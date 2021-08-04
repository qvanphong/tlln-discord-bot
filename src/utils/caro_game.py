import json
from typing import Optional

import discord
from gomoku_ai import GomokuAI

import definition
from src.model.caro_board import CaroBoard
from src.repository import caro_repository
from src.utils.caro_engine import CaroEngine


class AIMockDiscordUser:
    def __init__(self):
        self.id = 6666
        self.name = "🤖 Siêu CáRô"


class CaroGame:
    games = []
    engine = CaroEngine()
    responses = []
    client = None
    ai_engine = None
    ai_player = None

    def __init__(self, client: discord.Client):
        f = open(definition.get_path('assets/caro_responses.json'), encoding="utf8")
        self.responses = json.load(f)
        f.close()

        self.client = client

        self.ai_engine = GomokuAI()
        self.ai_player = AIMockDiscordUser()

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

    async def create_and_start_ai(self, message, player, human_first=False):
        if not self.is_in_game(player):
            if human_first:
                caro_game = CaroBoard(player, self.ai_player, 15, 15, 5, False)
            else:
                caro_game = CaroBoard(self.ai_player, player, 15, 15, 5, False)
            self.games.append(caro_game)
            self.ai_engine.start_game(caro_game.match_id, human_first)

            await self.send_message(message, "game_created_ai", self.ai_player.name, player.id)

            await self.announce_turn_with_info(message, caro_game)

            if not human_first:
                x, y = self.ai_engine.get_ai_move(caro_game.match_id, None)
                await self.move_ai(message, caro_game, x, y)
        else:
            await self.send_message(message, "in_other_game")

    async def stop(self, message, player):
        player_game = self.get_game(player)
        if player_game is not None and player_game.creator == player:
            self.games.remove(player_game)
            if self.is_ai_game(player_game):
                self.ai_engine.end_game(player_game.match_id)

            await self.send_message(message, "game_stopped", player_game.match_id)
        else:
            await self.send_message(message, "not_in_any_game")

    async def rematch(self, message, player):
        player_game = self.get_game(player)
        if player_game is not None and player_game.creator == player:
            if self.is_ai_game(player_game):
                # TODO: unsupported for now to avoid complexity
                return

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
                if self.is_ai_game(player_game):
                    await self.send_message(message, "surrender_ai", player.id, self.ai_player.name)
                else:
                    await self.send_message(message, "surrender",
                                            player.id,
                                            player_game.first_player.id if player_game.second_player == player else player_game.second_player.id
                                            )
                await self.save_score(
                    player_game.first_player if player_game.first_player != player_game.current_player_turn else player_game.second_player,
                    player_game.current_player_turn)

                self.games.remove(player_game)
                if self.is_ai_game(player_game):
                    self.ai_engine.end_game(player_game.match_id)
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
                if self.is_ai_game(player_game):
                    self.ai_engine.end_game(player_game.match_id)
            elif status == 0:
                if player_game.is_board_full():
                    await self.send_message(message, "board_full")
                    self.games.remove(player_game)
                    if self.is_ai_game(player_game):
                        self.ai_engine.end_game(player_game.match_id)
                else:
                    await self.announce_turn(message, player_game)
                    if self.is_ai_game(player_game):
                        x, y = self.ai_engine.get_ai_move(player_game.match_id, [x, y])
                        await self.move_ai(message, player_game, x, y)
            else:
                await self.send_message(message, "invalid_turn")
        else:
            await self.send_message(message, "not_your_turn", player.id)

    async def move_ai(self, message, caro_game, x, y):
        status = self.engine.make_turn(x, y, caro_game)
        await self.send_message(message, "ai_move", self.ai_player.name, chr(ord("A") + y), x + 1)
        if status == 1:
            player = caro_game.first_player if caro_game.second_player is self.ai_player else caro_game.second_player
            await self.send_board(message, caro_game)
            await self.send_message(message, "lose_ai", player.id, self.ai_player.name)
            await self.save_score(self.ai_player, player)

            self.games.remove(caro_game)
            self.ai_engine.end_game(caro_game.match_id)
        elif status == 0:
            if caro_game.is_board_full():
                await self.send_message(message, "board_full")
                self.games.remove(caro_game)
                self.ai_engine.end_game(caro_game.match_id)
            else:
                await self.announce_turn(message, caro_game)

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

    def is_ai_game(self, caro_game):
        if caro_game.first_player is self.ai_player or caro_game.second_player is self.ai_player:
            return True
        else:
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
        if caro_game.current_player_turn is self.ai_player:
            await self.send_message(message, "ai_turn",
                                    self.ai_player.name,
                                    caro_game.get_current_mark())
        else:
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
        if caro_game.current_player_turn is self.ai_player:
            await self.send_message(message, "ai_turn",
                                    self.ai_player.name,
                                    caro_game.get_current_mark())
        else:
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
            icon = "🏆" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else str(index + 1) + ". "
            if index > 2 and index < 9:
                icon += " "
            leader_board += pre_text.format(name=player["name"], win=player["win"], lose=player["lose"], icon=icon)

        await message.channel.send(">>> ```CSS\n{}```".format(leader_board))

    async def save_score(self, winner, loser):
        caro_repository.save_score(winner, "win")
        caro_repository.save_score(loser, "lose")
