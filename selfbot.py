from random import randint

import discord
import env
from channel_permission import ChannelPermission
from binance_price import BinancePriceWs
from command_sender import CommandSender


class MyClient(discord.Client):
    binance_ws = None
    command_sender = None
    channel_permission = ChannelPermission()

    # Khởi chạy Binance websocket để cập nhật giá
    async def on_ready(self):
        print('Logged on as', self.user)

        self.command_sender = CommandSender(client)
        self.binance_ws = BinancePriceWs(client)
        await self.binance_ws.start()

    async def on_message(self, message):
        # Loại log lỗi do message ko rõ tới từ server/channel nào
        # Chỉ nhận tin nhắn và phản hồi nếu server là TLLN và channel ark
        if message.author is not None and message.guild is not None and message.channel is not None and hasattr(
                message.author, 'guild'):
            if message.author.guild.id == env.SERVER_ID:

                # Kiểm tra channel này có quyền sử dụng các lệnh của bot không
                channel_name = message.channel.name

                # commands
                if len(message.content) > 0 and message.content[0] == self.command_sender.prefix:
                    # stoic quote
                    if message.content.lower() == '!stoic':
                        if self.channel_permission.can_use_command(channel_name, "!stoic"):
                            await self.command_sender.send_stoic_quote(message)
                            return

                    elif message.content.lower() == '!carljung':
                        if self.channel_permission.can_use_command(channel_name, "!carljung"):
                            await self.command_sender.send_carl_jung_quote(message)
                            return

                    # BTC Dominance
                    elif message.content == "!dmn":
                        if self.channel_permission.can_use_command(channel_name, "!dmn"):
                            await self.command_sender.btc_dominance(message)
                            return
                    # an com command
                    elif message.content == "!ancom":
                        if self.channel_permission.can_use_command(channel_name, "!ancom"):
                            await self.command_sender.send_response_message("ancom", message)
                            return

                    # simp command
                    elif message.content == '!simp':
                        if self.channel_permission.can_use_command(channel_name, "!simp"):
                            await self.command_sender.send_response_message("simp", message, link=True)
                            return

                    # help command
                    elif message.content == '!help':
                        if self.channel_permission.can_use_command(channel_name, "!help"):
                            await self.command_sender.send_response_message("help", message, True)
                            return

                    # no horny command
                    elif message.content == "!horny":
                        if self.channel_permission.can_use_command(channel_name, "!horny"):
                            await self.command_sender.send_response_message("no_horny", message, link=True)
                            return

                    # bonk command
                    elif message.content == "!bonk":
                        if self.channel_permission.can_use_command(channel_name, "!bonk"):
                            await self.command_sender.send_response_message("bonk", message, link=True)
                            return

                    elif message.content == "!dh":
                        if self.channel_permission.can_use_command(channel_name, "!dh"):
                            await self.command_sender.send_response_message("dh", message)
                            return

                    elif message.content == "!chaybobinhoi":
                        if self.channel_permission.can_use_command(channel_name, "chaybo"):
                            await self.command_sender.send_response_message("chaybo", message)
                            return

                    elif "!chaybo " in message.content:
                        if self.channel_permission.can_use_command(channel_name, "chaybo"):
                            if len(message.mentions) > 0:
                                message_str = "{} vừa rủ **{}** đi chạy bộ.\nhttps://cdn.discordapp.com/attachments/829403779513974824/861139558250709002/chaybobinhoi.gif"
                                tagged_users = []
                                for index in range(0, len(message.mentions)):
                                    tagged_users.append(message.mentions[index].display_name)

                                await message.channel.send(
                                    ">>> " + message_str.format(message.author.name, ', '.join(tagged_users)))

                    # xoa command
                    elif "!xoa" in message.content:
                        if self.channel_permission.can_use_command(channel_name, "!xoa"):
                            await self.command_sender.create_pet_pet(message)

                    # pick command
                    elif '!pick' in message.content:
                        if self.channel_permission.can_use_command(channel_name, "!pick") \
                                and self.command_sender.is_regex_match(message.content,
                                                                       self.command_sender.pick_regex):
                            answers = message.content.split('!pick ')[1:][0].split(',')
                            await message.channel.send(
                                '> {}'.format(answers[randint(0, len(answers) - 1)].lstrip()))
                            return

                    elif '!fap' in message.content:
                        if self.channel_permission.can_use_command(channel_name, "!fap"):
                            await self.command_sender.send_fap_content(message)

                    # get emoji
                    elif '!e' in message.content:
                        if self.channel_permission.can_use_command(channel_name, "!e") \
                                and self.command_sender.is_regex_match(message.content,
                                                                       self.command_sender.emoji_regex):
                            emoji_format = ".gif" if message.content.split(':')[0] == '<a' else ".png"
                            emoji_id = message.content.split(':')[2][:-1]
                            if id is not None:
                                await message.channel.send(
                                    'https://cdn.discordapp.com/emojis/{}{}'.format(emoji_id, emoji_format))
                                return

                    # Lấy avatar
                    elif '!ava' in message.content:
                        if self.channel_permission.can_use_command(channel_name, "!ava"):
                            if message.content.lower() == "!ava tao":
                                avatar_url = await self.command_sender.get_avatar_url(message.author.id)
                                await message.add_reaction(self.command_sender.emoji_check)
                                await message.channel.send(avatar_url)
                            elif message.content.lower() == "!ava may" or message.content.lower() == "!ava mày":
                                await message.add_reaction(self.command_sender.emoji_check)
                                await message.channel.send(client.user.avatar_url)
                            elif len(message.mentions) > 0:
                                await self.command_sender.send_tagged_user_avatar(message)
                            return

                    # Sleep/wake command
                    elif "!sleep" in message.content or "!wake" in message.content:
                        if self.channel_permission.can_use_command(channel_name, "!sleep"):
                            await self.command_sender.send_sleep_time(message, "!wake" in message.content)
                            return

                # check giá coin
                if self.channel_permission.can_use_command(channel_name, "price"):
                    # lấy giá coin theo yêu cầu
                    if len(message.content) > 0 and message.content[0] == '?':
                        await self.command_sender.send_coin_price(message)
                    #  so sánh giá trị giữa 2 coin
                    if self.command_sender.is_regex_match(message.content, self.command_sender.compare_regex):
                        await self.command_sender.send_coins_compare(message)
                        return

                # Trade, Margin, Future
                if self.channel_permission.can_use_command(channel_name, "other"):
                    #  Nếu có message hỏi "Khi nào xxx 30"
                    if 'khi nào' in message.content.lower():
                        if self.command_sender.is_regex_match(message.content, self.command_sender.ask_when_regex):
                            await self.command_sender.send_response_message('ask_price', message)
                            return

                    await self.command_sender.bad_behaviour(message)

                    # Đập Bắn Đấm
                    if 'đập' in message.content.lower():
                        await self.command_sender.send_response_message("dap", message, link=True)
                        return
                    elif 'bắn' in message.content.lower():
                        await self.command_sender.send_response_message("ban", message, link=True)
                        return
                    elif 'đấm' in message.content.lower():
                        await self.command_sender.send_response_message("dam", message, link=True)
                        return


client = MyClient()
client.run(env.TOKEN)
