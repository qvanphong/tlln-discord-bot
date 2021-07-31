import json
from typing import Optional

import discord

import definition
from src.model.caro_board import CaroBoard
from src.repository import caro_repository
from src.utils.caro_engine import CaroEngine


class CaroGame:
    games = []
    engine = CaroEngine()
    responses = []
    client = None

    def __init__(self, client: discord.Client):
        f = open(definition.get_path('assets/caro_responses.json'), encoding="utf8")
        self.responses = json.load(f)
        f.close()

        self.client = client

    async def create_and_start(self, message, player1, player2, width, height, point_to_win, block_rule):
        if width < point_to_win or height < point_to_win or point_to_win <= 1:
            await self.send_message(message, "win_point_lower")
        elif 1 > width > 26 or 1 > height > 26:
            await self.send_message(message, "out_of_range")
        elif player2 == player1:
            await self.send_message(message, "play_alone")
        elif self.is_in_game(player1) is False and self.is_in_game(player2) is False:
            caro_game = CaroBoard(player1, player2, width, height, point_to_win, block_rule)
            self.games.append(caro_game)

            await self.send_message(message, "game_created", player1.id, player2.id)

            await self.announce_turn_with_info(message, caro_game)
        else:
            await self.send_message(message, "in_other_game")

    async def stop(self, message, player):
        player_game = self.get_game(player)
        if player_game is not None and player_game.creator == player:
            self.games.remove(player_game)
            await self.send_message(message, "game_stopped", player_game.match_id)
        else:
            await self.send_message(message, "not_in_any_game")

    async def rematch(self, message, player):
        player_game = self.get_game(player)
        if player_game is not None and player_game.creator == player:
            self.games.remove(player_game)
            await self.create_and_start(message,
                                        player_game.first_player,
                                        player_game.second_player,
                                        player_game.width,
                                        player_game.height,
                                        player_game.streak_to_win,
                                        player_game.block_rule)

    async def surrender(self, message, player):
        player_game = self.get_game(player)
        if player_game is not None:
            if player_game.current_player_turn == player:
                await self.send_message(message, "surrender",
                                        player.id,
                                        player_game.first_player.id if player_game.second_player == player else player_game.second_player.id
                                        )
                await self.save_score(
                    player_game.first_player if player_game.first_player != player_game.current_player_turn else player_game.second_player,
                    player_game.current_player_turn)

                self.games.remove(player_game)
            else:
                await self.send_message(message, "not_your_turn", player.id)

    async def move(self, message, player, x, y):
        player_game = self.get_game(player)
        if player_game is not None and player == player_game.current_player_turn:
            status = self.engine.make_turn(x, y, player_game)
            if status == 1:
                await self.send_board(message, player_game)
                await self.send_message(message, "win", player_game.current_player_turn.id)
                await self.save_score(player_game.current_player_turn,
                                      player_game.first_player if player_game.first_player != player_game.current_player_turn else player_game.second_player)

                self.games.remove(player_game)
            elif status == 0:
                if player_game.is_board_full():
                    await self.send_message(message, "board_full")
                    self.games.remove(player_game)
                else:
                    await self.announce_turn(message, player_game)
            else:
                await self.send_message(message, "invalid_turn")
        else:
            await self.send_message(message, "not_your_turn", player.id)

    async def admin_set_score(self, message, winner, loser):
        await self.save_score(winner, loser)
        await self.send_message(message, "win", winner.id)

    async def print_board(self, message, player):
        player_game = self.get_game(player)
        if player_game is not None:
            await self.announce_turn_with_info(message, player_game)
        pass

    def is_in_game(self, player):
        for index, game in enumerate(self.games):
            if game.first_player == player or game.second_player == player:
                return True
        return False

    def is_creator(self, player):
        for index, game in enumerate(self.games):
            if game.creator == player:
                return True
        return False

    def is_player_turn(self, player):
        for index, game in enumerate(self.games):
            if game.current_player_turn == player:
                return True
        return False

    def get_game(self, player) -> Optional[CaroBoard]:
        for index, game in enumerate(self.games):
            if game.first_player == player or game.second_player == player:
                return game
        return None

    async def send_board(self, message, caro_game):
        await message.channel.send(file=self.engine.get_board_drawer(caro_game))

    async def announce_turn(self, message, caro_game):
        await self.send_board(message, caro_game)
        await self.send_message(message, "player_turn",
                                caro_game.current_player_turn.id,
                                caro_game.get_current_mark())

    async def announce_turn_with_info(self, message, caro_game):
        await self.send_board(message, caro_game)
        await self.send_message(message, "board_info",
                                caro_game.match_id,
                                caro_game.width,
                                caro_game.height,
                                caro_game.streak_to_win,
                                "Không" if caro_game.block_rule is False else "Có")
        await self.send_message(message, "player_turn",
                                caro_game.current_player_turn.id,
                                caro_game.get_current_mark())

    async def send_message(self, message, key, *args):
        if len(args) == 0:
            await message.channel.send(">>> " + self.responses[key])
        else:
            await message.channel.send(">>> " + self.responses[key].format(*args))

    async def leader_board(self, message):
        all_record = caro_repository.get_all_score()
        pre_text = "W: {win:<5} L: {lose:<5} {icon:<3} {name:<16} \n"
        leader_board = ""
        leader_board += "CARO LEADERBOARD\n"
        for index, player in enumerate(all_record):
            icon = "🏆" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else str(index) + ". "
            leader_board += pre_text.format(name=player["name"], win=player["win"], lose=player["lose"], icon=icon)

        await message.channel.send(">>> ```CSS\n{}```".format(leader_board))

    async def save_score(self, winner, loser):
        caro_repository.save_score(winner, "win")
        caro_repository.save_score(loser, "lose")
