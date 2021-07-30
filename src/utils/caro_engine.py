from src.model.caro_board import CaroBoard
import re
import numpy as np
import io
import cv2
import discord


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (255, 0, 0)
RED = (0, 0, 255)


class CaroEngine:
    margin = 10
    label_width = 20
    line_thickness = 1
    square_side_length = 30

    label_font = cv2.FONT_HERSHEY_SIMPLEX
    label_font_size = 0.5
    label_font_thickness = 1

    def get_board_drawer(self, caro: CaroBoard):
        if caro.board_image is None:
            caro.board_image = self.draw_new_board(caro)

        _, buffer = cv2.imencode(".jpg", caro.board_image)
        io_buf = io.BytesIO(buffer)
        return discord.File(io_buf, "board.jpg")

    def draw_new_board(self, caro: CaroBoard):
        # compute image width height
        image_width = self.margin * 2 + self.label_width + self.line_thickness \
            + caro.width * (self.square_side_length + self.line_thickness)
        image_height = self.margin * 2 + self.label_width + self.line_thickness \
            + caro.height * (self.square_side_length + self.line_thickness)

        # declare white image
        image = np.full([image_width, image_height, 3], 255, np.uint8)

        # draw rows/columns
        x1 = y1 = self.margin + self.line_thickness // 2
        x2 = image_width - self.margin - self.label_width \
            - self.line_thickness // 2 - 1
        y2 = image_height - self.margin - self.label_width \
            - self.line_thickness // 2 - 1
        for i in range(caro.width + 1):
            x = self.margin + self.line_thickness // 2 \
                + i * (self.square_side_length + self.line_thickness)
            cv2.line(image, (x, y1), (x, y2),
                     BLACK, self.line_thickness, cv2.LINE_AA)
        for i in range(caro.height + 1):
            y = self.margin + self.line_thickness // 2 \
                + i * (self.square_side_length + self.line_thickness)
            cv2.line(image, (x1, y), (x2, y),
                     BLACK, self.line_thickness, cv2.LINE_AA)

        # draw labels
        for i in range(caro.width):
            text_size, _ = cv2.getTextSize(
                f"{i + 1}", self.label_font,
                self.label_font_size, self.label_font_thickness)
            x = self.margin + self.line_thickness \
                + (self.square_side_length - text_size[0]) // 2 \
                + i * (self.square_side_length + self.line_thickness)
            y = image_height - self.margin - self.label_width + 8 + text_size[1]
            cv2.putText(image, f"{i + 1}", (x, y),
                        self.label_font, self.label_font_size, BLACK,
                        self.label_font_thickness, cv2.LINE_AA)
        x = image_width - self.margin - self.label_width + 8
        for i in range(caro.height):
            text_size, _ = cv2.getTextSize(
                chr(ord("A") + i), self.label_font,
                self.label_font_size, self.label_font_thickness)
            y = self.margin - (self.square_side_length - text_size[1]) // 2 \
                + (i + 1) * (self.square_side_length + self.line_thickness)
            cv2.putText(image, chr(ord("A") + i), (x, y),
                        self.label_font, self.label_font_size, BLACK,
                        self.label_font_thickness, cv2.LINE_AA)

        return image

    def draw_new_turn(self, x, y, caro: CaroBoard):
        image = caro.board_image

        if caro.is_first_player():
            xcenter = self.margin + self.line_thickness \
                + self.square_side_length // 2 \
                + x * (self.square_side_length + self.line_thickness)
            ycenter = self.margin + self.line_thickness \
                + self.square_side_length // 2 \
                + y * (self.square_side_length + self.line_thickness)
            cv2.circle(image, (xcenter, ycenter), 8, BLUE, 3, cv2.LINE_AA)
        else:
            x_size, _ = cv2.getTextSize("x", self.label_font, 1.3, 3)
            xleft = self.margin + self.line_thickness \
                + (self.square_side_length - x_size[0]) // 2 + 1 \
                + x * (self.square_side_length + self.line_thickness)
            ybottom = self.margin \
                - (self.square_side_length - x_size[1]) // 2 - 6 \
                + (y + 1) * (self.square_side_length + self.line_thickness)
            cv2.putText(image, "x", (xleft, ybottom),
                        self.label_font, 1.3, RED, 3, cv2.LINE_AA)

        return image

    # This will return int number, we treat it as status
    # 1: current player won
    # 0: No one is winning
    # -1: Go on existed cell
    def make_turn(self, x, y, caro: CaroBoard):
        if caro.width > x >= 0 and caro.height > y >= 0:
            if caro.board[y][x] == caro.blank_character:
                caro.insert_to_board(x, y)
                caro.board_image = self.draw_new_turn(x, y, caro)
                self.turn_check(x, y, caro)

                if caro.victory is True:
                    return 1
                else:
                    caro.change_turn()
                    return 0
            else:
                return -1

    def turn_check(self, x, y, caro: CaroBoard):
        caro.victory = \
            self.check_horizontal_vertical(x,
                                           y,
                                           caro.board,
                                           caro.streak_to_win,
                                           caro.block_rule,
                                           caro.get_current_mark()) or \
            self.check_diagonal(x,
                                y,
                                caro,
                                caro.streak_to_win,
                                caro.block_rule,
                                caro.get_current_mark())

    def check_horizontal_vertical(self, x, y, board, streak_to_win, block_rule, mark):
        # Check horizontal
        streak_regex = "{mark}{{{streak},{streak}}}".format(mark=mark, streak=streak_to_win)
        line = "".join(board[y])
        win_match = re.search(pattern=streak_regex, string=line)
        if win_match is not None:
            if block_rule is True:
                return self.check_head_block(line, win_match.group(), streak_to_win, mark)
            return True
        else:
            # check vertical
            temp_board = np.array(board).T
            line = "".join(temp_board[x])
            win_match = re.search(pattern=streak_regex, string=line)
            if win_match is not None:
                if block_rule is True:
                    return self.check_head_block(line, win_match.group(), streak_to_win, mark)
                return True
        return False

    # def check_vertical(self, x, board, streak_to_win, has_head_block, mark):
    #     streak_regex = "{mark}{{{streak},{streak}}}".format(mark=mark, streak=streak_to_win)
    #     temp_board = np.array(board).T
    #     line = "".join(temp_board[x])
    #     win_match = re.search(pattern=streak_regex, string=line)
    #     if win_match is not None:
    #         if has_head_block is True:
    #             return self.check_head_block(line, win_match, mark)
    #         return True
    #     return False

    def check_diagonal(self, x, y, caro: CaroBoard, streak_to_win, block_rule, mark):
        streak_regex = "{mark}{{{streak},{streak}}}".format(mark=mark, streak=streak_to_win)
        # Check left to right diagonal ( \ )
        ltr_bound = x - y
        ltr_line = ""
        # Check right to lef diagonal ( / )
        rtl_bound = x + y
        rtl_line = ""

        for row_index in range(0, caro.height):
            if caro.height > ltr_bound + row_index >= 0:
                ltr_line += str(caro.board[row_index][ltr_bound + row_index])
            if caro.height > rtl_bound - row_index >= 0:
                rtl_line += str(caro.board[row_index][rtl_bound - row_index])
        if re.search(streak_regex, ltr_line) is not None:
            return True
        else:
            win_match = re.search(pattern=streak_regex, string=rtl_line)
            if win_match is not None:
                if block_rule is True:
                    return self.check_head_block(rtl_line, win_match.group(), streak_to_win, mark)
                return True
            return False

    def check_head_block(self, line, win_match, win_streak, mark):
        win_index = line.index(win_match)
        if win_index == 0 or win_index + win_streak - 1 == len(line):
            return True
        else:
            left = line[win_index - 1]
            right = line[win_index + win_streak]
            other_mark = CaroBoard.second_player_mark if mark == CaroBoard.first_player_mark else CaroBoard.first_player_mark
            if left != other_mark and right != other_mark or \
                    left == other_mark and right != other_mark or \
                    left != other_mark and right == other_mark:
                return True
            else:
                return False
