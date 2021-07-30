import discord
import re

from src.utils.caro_game import CaroGame
from src.utils import env


class CaroClient(discord.Client):
    caro = None
    caro_with_custom_regex = r"^\!caro <@[!]?[0-9]*> \d+ \d+ \d+( yes)?$"
    caro_default_regex = r"^\!caro <@[!]?[0-9]*>$"
    caro_move_regex = r"^\!caro [a-z]\d{1,2}$"
    caro_set_win_regex = r"^\!caro win <@[!]?[0-9]*> <@[!]?[0-9]*>$"

    async def on_ready(self):
        self.caro = CaroGame(self)
        print("Caro bot on ready")

    async def on_message(self, message):
        if message.author is not None and message.guild is not None and message.channel is not None and hasattr(
                message.author, 'guild') and message.guild.id == env.SERVER_ID:
            message_content = message.content.lower()

            if "!caro gg" == message_content:
                await self.caro.surrender(message, message.author)

            elif "!caro stop" == message_content:
                await self.caro.stop(message, message.author)

            elif "!caro board" == message_content:
                await self.caro.print_board(message, message.author)

            elif "!caro huongdan" == message_content:
                await self.caro.send_message(message, "tutorial")

            elif "!caro rematch" == message_content:
                await self.caro.rematch(message, message.author)

            elif "!caro leaderboard" == message_content:
                await self.caro.leader_board(message)

            elif "!caro" in message_content:
                # Create game finder
                if re.search(self.caro_with_custom_regex, message_content, re.IGNORECASE) and len(
                        message.mentions) == 1:
                    split = message_content.split()
                    width = int(split[2])
                    height = int(split[3])
                    win_point = int(split[4])

                    if len(split) == 6 and split[5].strip() == "yes":
                        block_rule = True
                    else:
                        block_rule = False
                    await self.caro.create_and_start(message,
                                                     message.author,
                                                     message.mentions[0],
                                                     width,
                                                     height,
                                                     win_point,
                                                     block_rule)
                elif re.search(self.caro_default_regex, message_content, re.IGNORECASE):
                    await self.caro.create_and_start(message, message.author, message.mentions[0], 7, 7, 3, True)
                # Move
                elif re.search(self.caro_move_regex, message_content, re.IGNORECASE):
                    raw_move = message_content.split()[1]
                    y = ord(raw_move[0]) - 97
                    x = int(raw_move[1:len(raw_move)]) - 1

                    await self.caro.move(message, message.author, x, y)
                # Set win
                elif message.author.id == 437090685309681705 or message.author.id == 403040446118363138 and \
                        re.search(self.caro_set_win_regex, message_content, re.IGNORECASE):
                    await self.caro.admin_set_score(message, message.mentions[0], message.mentions[1])


caro = CaroClient().run(env.TOKEN)
