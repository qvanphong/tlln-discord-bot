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

    async def create_and_start(self, message, player1_id, player2_id, width, height, point_to_win, block_rule):
        if width - 1 < point_to_win or height - 1 < point_to_win:
            await self.send_message(message, "win_point_lower")
        elif 1 > width > 14 or 1 > height > 14 or width + height > 28:
            await self.send_message(message, "out_of_range")
        elif player2_id == player1_id:
            await self.send_message(message, "play_alone")
        elif self.is_in_game(player1_id) is False and self.is_in_game(player2_id) is False:
            caro_game = CaroBoard(player1_id, player2_id, width, height, point_to_win, block_rule)
            self.games.append(caro_game)

            await self.send_message(message, "game_created", player1_id, player2_id)

            await self.announce_turn_with_info(message, caro_game)
        else:
            await self.send_message(message, "in_other_game")

    async def stop(self, message, player_id):
        player_game = self.get_game(player_id)
        if player_game is not None and player_game.creator == player_id:
            self.games.remove(player_game)
            await self.send_message(message, "game_stopped", player_game.match_id)
        else:
            await self.send_message(message, "not_in_any_game")

    async def rematch(self, message, player_id):
        player_game = self.get_game(player_id)
        if player_game is not None and player_game.creator == player_id:
            self.games.remove(player_game)
            await self.create_and_start(message,
                                        player_game.first_player,
                                        player_game.second_player,
                                        player_game.width,
                                        player_game.height,
                                        player_game.streak_to_win,
                                        player_game.block_rule)

    async def surrender(self, message, player_id):
        player_game = self.get_game(player_id)
        if player_game is not None:
            await self.send_message(message, "surrender",
                                    player_id,
                                    player_game.first_player if player_game.second_player == player_id else player_game.second_player
                                    )
            await self.save_score(
                player_game.first_player if player_game.first_player != player_game.current_player_turn else player_game.second_player,
                player_game.current_player_turn)

            self.games.remove(player_game)

    async def move(self, message, player_id, x, y):
        player_game = self.get_game(player_id)
        if player_game is not None and player_id == player_game.current_player_turn:
            status = self.engine.make_turn(x, y, player_game)
            if status == 1:
                await self.send_message(message, "win", player_game.current_player_turn)
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
            await self.send_message(message, "not_your_turn", player_id)

    async def admin_set_score(self, message, winner_id, loser_id):
        await self.save_score(winner_id, loser_id)
        await self.send_message(message, "win", winner_id)

    async def print_board(self, message, player_id):
        player_game = self.get_game(player_id)
        if player_game is not None:
            await self.announce_turn_with_info(message, player_game)
        pass

    def is_in_game(self, player_id):
        for index, game in enumerate(self.games):
            if game.first_player == player_id or game.second_player == player_id:
                return True
        return False

    def is_creator(self, player_id):
        for index, game in enumerate(self.games):
            if game.creator == player_id:
                return True
        return False

    def is_player_turn(self, player_id):
        for index, game in enumerate(self.games):
            if game.current_player_turn == player_id:
                return True
        return False

    def get_game(self, player_id) -> Optional[CaroBoard]:
        for index, game in enumerate(self.games):
            if game.first_player == player_id or game.second_player == player_id:
                return game
        return None

    async def announce_turn(self, message, caro_game):
        await message.channel.send(file=self.engine.get_board_drawer(caro_game))
        await self.send_message(message, "player_turn", caro_game.current_player_turn)

    async def announce_turn_with_info(self, message, caro_game):
        await message.channel.send(file=self.engine.get_board_drawer(caro_game))
        await self.send_message(message, "board_info",
                                caro_game.match_id,
                                caro_game.width,
                                caro_game.height,
                                caro_game.streak_to_win,
                                "Không" if caro_game.block_rule is False else "Có")
        await self.send_message(message, "player_turn", caro_game.current_player_turn)

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

    async def save_score(self, winner_id, loser_id):
        winner = await self.client.fetch_user_profile(winner_id)
        loser = await self.client.fetch_user_profile(loser_id)
        caro_repository.save_score(winner.user, "win")
        caro_repository.save_score(loser.user, "lose")
