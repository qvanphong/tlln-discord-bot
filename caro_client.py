import discord
import re

from src.utils.caro_game import CaroGame
from src.utils import env


class CaroClient(discord.Client):
    caro = CaroGame()
    caro_with_custom_regex = r"^\!caro <@[!]?[0-9]*> \d+ \d+ \d+$"
    caro_default_regex = r"^\!caro <@[!]?[0-9]*>$"
    caro_move_regex = r"^\!caro [a-z]\d{1,2}$"

    async def on_ready(self):
        print("Caro bot on ready")

    async def on_message(self, message):
        if message.author is not None and message.guild is not None and message.channel is not None and hasattr(
                message.author, 'guild') and message.guild.id == env.SERVER_ID:
            message_content = message.content.lower()

            if "!caro surrender" == message_content:
                await self.caro.surrender(message, message.author.id)

            elif "!caro stop" == message_content:
                await self.caro.stop(message, message.author.id)

            elif "!caro board" == message_content:
                await self.caro.print_board(message, message.author.id)

            elif "!caro huongdan" == message_content:
                await self.caro.send_message(message, "tutorial")

            elif "!caro" in message_content:
                # Create game finder
                if re.search(self.caro_with_custom_regex, message_content, re.IGNORECASE) and len(message.mentions) == 1:
                    split = message_content.split()
                    width = int(split[2])
                    height = int(split[3])
                    win_point = int(split[4])

                    await self.caro.create_and_start(message, message.author.id, message.mentions[0].id, width, height,
                                                     win_point)
                elif re.search(self.caro_default_regex, message_content, re.IGNORECASE):
                    await self.caro.create_and_start(message, message.author.id, message.mentions[0].id, 7, 7, 5)
                elif re.search(self.caro_move_regex, message_content, re.IGNORECASE):
                    raw_move = message_content.split()[1]
                    y = ord(raw_move[0]) - 97
                    x = int(raw_move[1:len(raw_move)]) - 1

                    await self.caro.move(message, message.author.id, x, y)





caro = CaroClient().run(env.TOKEN)
# caro.show_board()
# while True:
#     print("Hay nhap x:")
#     x = int(input())
#     print("Hay nhap y:")
#     y = int(input())
#     caro.make_turn(x - 1, y - 1)
