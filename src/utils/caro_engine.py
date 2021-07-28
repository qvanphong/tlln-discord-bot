from src.model.caro_board import CaroBoard
import re
import numpy as np


class CaroEngine:
    corner_left_top = "╔"
    corner_right_top = "╗"
    corner_left_bot = "╚"
    corner_right_bot = "╝"
    corner_straight = "═"
    corner_up = "╩"
    corner_down = "╦"
    corner_left = "╠"
    corner_middle = "╬"
    corner_right = "╣"
    box_width = 3

    def get_board_drawer(self, caro: CaroBoard):
        column_print = ""
        for y in range(0, caro.height * 2 + 1):
            for x in range(0, caro.width):
                if y == 0:
                    column_print += " {} ".format(" " + str(x + 1) if x < 10 else x + 1)
                elif y == 1:
                    column_print += "{}{}{}".format(
                        self.corner_left_top if x == 0 else self.corner_down if x != caro.width else self.corner_right_top,
                        self.corner_straight * self.box_width,
                        self.corner_right_top if x == caro.width - 1 else "")
                elif y % 2 == 0:
                    column_print += "║ {} {}".format(
                        " " if caro.board[int((y - 1) / 2)][x] == caro.blank_character else
                        caro.board[int((y - 1) / 2)][x],
                        # Current y must /2 (since I multiply 2 on above range()) and + 65 as 'A' character
                        "║ {}".format(chr(int((y - 1) / 2 + 65))) if x == caro.width - 1 else ""
                    )
                else:
                    column_print += "{}{}{}".format(
                        self.corner_left if x == 0 else self.corner_middle if x != caro.width else self.corner_right,
                        self.corner_straight * self.box_width,
                        self.corner_right if x == caro.width - 1 else "")

            column_print += "\n"
            if y == caro.height * 2:
                for x in range(0, caro.width):
                    column_print += "{}{}{}".format(
                        self.corner_left_bot if x == 0 else self.corner_up if x != caro.width else self.corner_right_bot,
                        self.corner_straight * self.box_width,
                        self.corner_right_bot if x == caro.width - 1 else "")

        return column_print

    # This will return int number, we treat it as status
    # 1: current player won
    # 0: No one is winning
    # -1: Go on existed cell
    def make_turn(self, x, y, caro: CaroBoard):
        if caro.width > x >= 0 and caro.height > y >= 0:
            if caro.board[y][x] == caro.blank_character:
                caro.insert_to_board(x, y)
                self.turn_check(x, y, caro)

                if caro.victory is True:
                    return 1
                else:
                    caro.change_turn()
                    return 0
            else:
                return -1

    def turn_check(self, x, y, caro: CaroBoard):
        caro.victory = self.check_horizontal(y, caro.board, caro.streak_to_win) or \
                       self.check_vertical(x, caro.board, caro.streak_to_win) or\
                       self.check_diagonal(x, y, caro, caro.streak_to_win)

    def check_horizontal(self, y, board, streak_to_win):
        streak_regex = r"(O{" + re.escape(str(streak_to_win) + "," + str(streak_to_win)) + r"}|X{" + \
                       re.escape(str(streak_to_win) + "," + str(streak_to_win)) + "})"
        row = "".join(board[y])
        if re.search(pattern=streak_regex, string=row) is not None:
            return True
        return False

    def check_vertical(self, x, board, streak_to_win):
        streak_regex = r"(O{" + re.escape(str(streak_to_win) + "," + str(streak_to_win)) + r"}|X{" + \
                       re.escape(str(streak_to_win) + "," + str(streak_to_win)) + "})"
        temp_board = np.array(board).T
        row = "".join(temp_board[x])
        if re.search(pattern=streak_regex, string=row) is not None:
            return True
        return False

    def check_diagonal(self, x, y, caro: CaroBoard, streak_to_win):
        streak_regex = r"(O{" + re.escape(str(streak_to_win) + "," + str(streak_to_win)) + r"}|X{" + \
                       re.escape(str(streak_to_win) + "," + str(streak_to_win)) + "})"
        # Check left to right diagonal ( \ )
        ltr_bound = x - y
        ltr = ""
        # Check right to lef diagonal ( / )
        rtl_bound = x + y
        rtl = ""

        for row_index in range(0, caro.height):
            if caro.height > ltr_bound + row_index >= 0:
                ltr += str(caro.board[row_index][ltr_bound + row_index])
            if caro.height > rtl_bound - row_index >= 0:
                rtl += str(caro.board[row_index][rtl_bound - row_index])
        if re.search(streak_regex, ltr) is not None:
            return True
        else:
            if re.search(streak_regex, rtl) is not None:
                return True
            return False
