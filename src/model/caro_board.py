import numpy as np


class CaroBoard:
    width = 7
    height = 7
    streak_to_win = 5
    creator = None
    first_player = None
    second_player = None
    blank_character = '_'
    turns = None
    current_player_turn = None
    is_game_started = False
    board = None
    victory = None

    def __init__(self, player_1, player_2, width, height, point_to_win):
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
        self.turns = 0

    def is_first_player(self):
        if self.current_player_turn == self.first_player:
            return True
        return False

    def insert_to_board(self, x, y):
        self.board[y][x] = "O" if self.is_first_player() else "X"
        self.turns += 1

    def change_turn(self):
        if self.is_first_player():
            self.current_player_turn = self.second_player
        else:
            self.current_player_turn = self.first_player

    def is_board_full(self):
        return self.turns == self.width * self.height
