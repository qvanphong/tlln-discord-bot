import json

import definition
from src.model.caro_board import CaroBoard
from src.utils.caro_engine import CaroEngine


class CaroGame:
    games = []
    engine = CaroEngine()
    responses = []

    def __init__(self):
        f = open(definition.get_path('assets/caro_responses.json'), encoding="utf8")
        self.responses = json.load(f)
        f.close()

    async def create_and_start(self, message, player1_id, player2_id, width, height, point_to_win):
        if width - 1 < point_to_win or height - 1 < point_to_win:
            await self.send_message(message, "win_point_lower")
        elif 1 > width > 26 or 1 > height > 26:
            await self.send_message(message, "out_of_range")
        elif player2_id == player1_id:
            await self.send_message(message, "play_alone")
        elif self.is_in_game(player1_id) is False and self.is_in_game(player2_id) is False:
            caro_game = CaroBoard(player1_id, player2_id, width, height, point_to_win)
            self.games.append(caro_game)

            await self.send_message(message, "game_created", player1_id, player2_id)

            await self.announce_turn_with_info(message, caro_game)
        else:
            await self.send_message(message, "in_other_game")

    async def stop(self, message, player_id):
        player_game = self.get_game(player_id)
        if player_game is not None and player_game.creator == player_id:
            self.games.remove(player_game)
            await self.send_message(message, "game_stopped")
        else:
            await self.send_message(message, "not_in_any_game")

    async def surrender(self, message, player_id):
        player_game = self.get_game(player_id)
        if player_game is not None:
            await self.send_message(message, "surrender",
                                    player_id,
                                    player_game.first_player if player_game.second_player == player_id else player_game.second_player
                                    )
            self.games.remove(player_game)

    async def move(self, message, player_id, x, y):
        player_game = self.get_game(player_id)
        if player_game is not None and player_id == player_game.current_player_turn:
            status = self.engine.make_turn(x, y, player_game)
            await self.announce_turn(message, player_game)
            if status == 1:
                self.games.remove(player_game)
                await self.send_message(message, "win", player_game.current_player_turn)
            elif status == 0:
                if player_game.is_board_full():
                    await self.send_message(message, "board_full")
                    self.games.remove(player_game)
            else:
                await self.send_message(message, "invalid_turn")
        else:
            await self.send_message(message, "not_your_turn", player_id)

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

    def get_game(self, player_id):
        for index, game in enumerate(self.games):
            if game.first_player == player_id or game.second_player == player_id:
                return game
        return None

    async def announce_turn(self, message, caro_game):
        await message.channel.send("```CSS\n{}```".format(self.engine.get_board_drawer(caro_game)))
        await self.send_message(message, "player_turn", caro_game.current_player_turn)

    async def announce_turn_with_info(self, message, caro_game):
        await message.channel.send("```CSS\n{}```".format(self.engine.get_board_drawer(caro_game)))
        await self.send_message(message, "board_info", caro_game.width, caro_game.height, caro_game.streak_to_win)
        await self.send_message(message, "player_turn", caro_game.current_player_turn)

    async def send_message(self, message, key, *args):
        if len(args) == 0:
            await message.channel.send(">>> " + self.responses[key])
        else:
            await message.channel.send(">>> " + self.responses[key].format(*args))
