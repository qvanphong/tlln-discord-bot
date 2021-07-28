from random import randint

import discord

from src.price_alert import PriceAlert
from src.utils import env, responder, advanced_random
from src.utils.channel_permission import ChannelPermission


class DiscordCommandClient(discord.Client):
    binance_ws = None
    responder = None
    permission = ChannelPermission()
    randomizer = advanced_random.AdvancedRandom()

    # Khởi chạy Binance websocket để cập nhật giá
    async def on_ready(self):
        print('Logged on as', self.user)

        self.responder = responder.Responder(client)

        # Comment if you don't want to use Binance price alert
        self.binance_ws = PriceAlert(client)
        await self.binance_ws.start()
        print('Started price alert')

    async def on_message(self, message):
        # Loại log lỗi do message ko rõ tới từ server/channel nào
        # Chỉ nhận tin nhắn và phản hồi nếu server là TLLN và channel ark
        if message.author is not None and message.guild is not None and message.channel is not None and hasattr(
                message.author, 'guild'):
            if message.author.guild.id == env.SERVER_ID:

                # Kiểm tra channel này có quyền sử dụng các lệnh của bot không
                channel_id = message.channel.id

                # commands
                if len(message.content) > 0 and message.content[0] == self.responder.prefix:
                    # stoic quote
                    if message.content.lower() == '!stoic':
                        if self.permission.can_use_command(channel_id, "!stoic"):
                            await self.responder.send_stoic_quote(message)
                            return

                    # seneca's letter
                    if '!seneca' in message.content.lower():
                        if self.permission.can_use_command(channel_id, "!seneca"):
                            await self.responder.send_seneca_letters(message)
                            return

                    # carl jung's quotes
                    elif message.content.lower() == '!carljung':
                        if self.permission.can_use_command(channel_id, "!carljung"):
                            await self.responder.send_carl_jung_quote(message)
                            return

                    # BTC Dominance
                    elif message.content == "!dmn":
                        if self.permission.can_use_command(channel_id, "!dmn"):
                            await self.responder.send_btc_dominance(message)
                            return
                    # an com command
                    elif message.content == "!ancom":
                        if self.permission.can_use_command(channel_id, "!ancom"):
                            await self.responder.send_response_message("ancom", message)
                            return

                    # simp command
                    elif message.content == '!simp':
                        if self.permission.can_use_command(channel_id, "!simp"):
                            await self.responder.send_response_message("simp", message, link=True)
                            return

                    # help command
                    elif message.content == '!help':
                        if self.permission.can_use_command(channel_id, "!help"):
                            await self.responder.send_response_message("help", message, True)
                            return

                    # no horny command
                    elif message.content == "!horny":
                        if self.permission.can_use_command(channel_id, "!horny"):
                            await self.responder.send_response_message("no_horny", message, link=True)
                            return

                    # bonk command
                    elif message.content == "!bonk":
                        if self.permission.can_use_command(channel_id, "!bonk"):
                            await self.responder.send_response_message("bonk", message, link=True)
                            return

                    elif message.content == "!dh":
                        if self.permission.can_use_command(channel_id, "!dh"):
                            await self.responder.send_response_message("dh", message)
                            return

                    elif message.content == "!tailieu":
                        if self.permission.can_use_command(channel_id, "!tailieu"):
                            await self.responder.send_response_message("tailieu", message)
                            return

                    elif message.content == "!noichu":
                        if self.permission.can_use_command(channel_id, "!noichu"):
                            await self.responder.send_response_message("noichu", message)
                            return

                    elif message.content == "!chaybobinhoi":
                        if self.permission.can_use_command(channel_id, "chaybo"):
                            await self.responder.send_response_message("chaybobinhoi", message)
                            await message.channel.send(
                                "https://cdn.discordapp.com/attachments/829403779513974824/861139558250709002/chaybobinhoi.gif")
                            return

                    elif "!chaybo " in message.content or "!chaytrongphong" in message.content:
                        if self.permission.can_use_command(channel_id, "chaybo"):
                            await self.responder.send_run_command(message)

                    # xoa command
                    elif "!xoa" in message.content:
                        if self.permission.can_use_command(channel_id, "!xoa"):
                            await self.responder.create_gif_emoji(message, "pet")

                    elif "!bonk" in message.content:
                        if self.permission.can_use_command(channel_id, "!bonk"):
                            await self.responder.create_gif_emoji(message, "bonk")

                    elif "!sort" in message.content:
                        # Free for all channel, since no one gonna use it... lol
                        await self.responder.send_sorted_users(message)

                    # pick command
                    elif '!pick' in message.content:
                        if self.permission.can_use_command(channel_id, "!pick") \
                                and responder.is_regex_match(message.content,
                                                             self.responder.pick_regex):
                            answers = message.content.split('!pick ')[1:][0].split(',')
                            await message.channel.send(
                                '> {}'.format(answers[randint(0, len(answers) - 1)].lstrip()))
                            return

                    elif '!fap' in message.content:
                        if self.permission.can_use_command(channel_id, "!fap"):
                            await self.responder.send_fap_content(message)

                    # get emoji
                    elif '!e' in message.content:
                        if self.permission.can_use_command(channel_id, "!e") \
                                and responder.is_regex_match(message.content,
                                                             self.responder.emoji_command_regex):
                            emoji_format = ".gif" if message.content.split(':')[0] == '<a' else ".png"
                            emoji_id = message.content.split(':')[2][:-1]
                            if id is not None:
                                await message.channel.send(
                                    'https://cdn.discordapp.com/emojis/{}{}'.format(emoji_id, emoji_format))
                                return

                    # Lấy avatar
                    elif '!ava' in message.content:
                        if self.permission.can_use_command(channel_id, "!ava"):
                            if message.content.lower() == "!ava tao":
                                avatar_url = await self.responder.get_avatar_url(message.author.id)
                                await message.add_reaction(self.responder.emoji_check)
                                await message.channel.send(avatar_url)
                            elif message.content.lower() == "!ava may" or message.content.lower() == "!ava mày":
                                await message.add_reaction(self.responder.emoji_check)
                                await message.channel.send(client.user.avatar_url)
                            elif len(message.mentions) > 0:
                                await self.responder.send_tagged_user_avatar(message)
                            return

                    # Sleep/wake command
                    elif "!sleep" in message.content or "!wake" in message.content:
                        if self.permission.can_use_command(channel_id, "!sleep"):
                            await self.responder.send_sleep_time(message, "!wake" in message.content)
                            return

                    # Random number command
                    elif "!random" in message.content.lower() and responder.is_regex_match(message.content.lower(),
                                                                                           self.responder.random_regex):

                        # profile = await self.fetch_user_profile(message.author.id)
                        profile = message.author
                        split_command = message.content.lower().split()
                        minimum = split_command[1]
                        maximum = split_command[2]

                        if minimum > maximum:
                            await message.channel.send(">>> Số đầu tiên phải bé hơn số phía sau")
                            return

                        if len(split_command) == 4 and split_command[3] == "exclude":
                            self.randomizer.add_random_session(minimum=minimum, maximum=maximum,
                                                               channel_id=message.channel.id, author=profile)
                            await message.channel.send(
                                ">>> Đã tạo phiên quay số không bị trùng, "
                                "gõ `!random` để bắt đầu quay số, gõ `!stoprandom` để xóa phiên quay số nếu không cần dùng nữa.")
                        else:
                            random_number = advanced_random.get_random_number(minimum, maximum)
                            await message.channel.send(">>> Số ngẫu nhiên: **{}**".format(random_number))

                    elif message.content.lower() == "!random":
                        number = self.randomizer.get_random_with_exclude(message.author)
                        if number is not None:
                            random_number = number[0]
                            excluded_number = number[1]
                            await message.channel.send(">>> Số ngẫu nhiên: **{}**".format(random_number))
                            await message.channel.send(">>> Các số đã ra trước đó: **{}**".format(excluded_number))

                    elif "!stoprandom" in message.content.lower():
                        if self.randomizer.remove_random_session(message.author):
                            await message.channel.send(">>> Đã xóa phiên quay số.")

                # check giá coin
                if self.permission.can_use_command(channel_id, "price"):
                    # lấy giá coin theo yêu cầu
                    if len(message.content) > 0 and message.content[0] == '?':
                        await self.responder.send_coin_price(message)
                    #  so sánh giá trị giữa 2 coin
                    if responder.is_regex_match(message.content, self.responder.compare_regex):
                        await self.responder.send_coins_compare(message)
                        return

                # Trade, Margin, Future
                if self.permission.can_use_command(channel_id, "other"):
                    #  Nếu có message hỏi "Khi nào xxx 30"
                    if 'khi nào' in message.content.lower():
                        if responder.is_regex_match(message.content, self.responder.ask_when_regex):
                            await self.responder.send_response_message('ask_price', message)
                            return

                    await self.responder.send_bad_behaviour(message)

                    # Đập Bắn Đấm
                    if 'đập' in message.content.lower():
                        await self.responder.send_response_message("dap", message, link=True)
                        return
                    elif 'bắn' in message.content.lower():
                        await self.responder.send_response_message("ban", message, link=True)
                        return
                    elif 'đấm' in message.content.lower():
                        await self.responder.send_response_message("dam", message, link=True)
                        return


client = DiscordCommandClient()
client.run(env.TOKEN)
