import numpy as np
from nanoid import generate

class CaroBoard:
    match_id = None
    width = 7
    height = 7
    streak_to_win = 5
    creator = None
    first_player = None
    second_player = None
    first_player_mark = "0"
    second_player_mark = "×"
    blank_character = '_'
    turns = None
    current_player_turn = None
    is_game_started = False
    board = None
    victory = None
    block_rule = None

    def __init__(self, player_1, player_2, width, height, point_to_win, block_rule):
        self.match_id = generate()
        self.width = width
        self.height = height
        self.streak_to_win = point_to_win
        self.creator = player_1
        self.first_player = player_1
        self.second_player = player_2
        self.current_player_turn = player_1
        self.victory = None
        self.is_game_started = False
        self.board = np.full((height, width), self.blank_character)
        self.block_rule = block_rule
        self.turns = 0

    def is_first_player(self):
        if self.current_player_turn == self.first_player:
            return True
        return False

    def insert_to_board(self, x, y):
        self.board[y][x] = self.get_current_mark()
        self.turns += 1

    def get_current_mark(self):
        return self.first_player_mark if self.is_first_player() else self.second_player_mark

    def change_turn(self):
        if self.is_first_player():
            self.current_player_turn = self.second_player
        else:
            self.current_player_turn = self.first_player

    def is_board_full(self):
        return self.turns == self.width * self.height
