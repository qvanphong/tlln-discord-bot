from random import randint

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from pycoingecko import CoinGeckoAPI
import discord
import re
import http.client
import json
import requests
import io
import math
import env
from binance_price import BinancePriceWs


class MyClient(discord.Client):
    prefix = '!'
    pick_regex = r'^\!pick (.*,)*(.*){1}$'
    pick_avatar_regex = r'^\!ava <@[!]?[0-9]*>$'
    coin_price_check_regex = r'^\?[a-zA-Z]*$'
    emoji_regex = r"!e <:.*:[0-9]*>"
    compare_regex = r"^[0-9]* [a-zA-Z]* = (\?|bn) [a-zA-Z]*$"
    ask_when_regex = r"khi nào .* [0-9]*"

    coin_gecko = None  # coingecko instance
    coin_gecko_map = None  # coingecko coins list
    responses = None  # list of commands response
    stoic_quotes = None  # list of stoic quotes
    carl_jung_quotes = None  # list of Carl Jung quotes
    url = 'https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': env.CMC_KEY,
    }

    binance_ws = None
    session = Session()
    session.headers.update(headers)

    def __init__(self, coin_gecko_map, coin_gecko, responses=None, stoic_quotes=None, carl_jung_quotes=None, **options):
        super().__init__(**options)
        self.coin_gecko_map = coin_gecko_map
        self.coin_gecko = coin_gecko
        self.responses = responses
        self.stoic_quotes = stoic_quotes
        self.carl_jung_quotes = carl_jung_quotes

    # Khởi chạy Binance websocket để cập nhật giá
    async def on_ready(self):
        print('Logged on as', self.user)
        self.binance_ws = BinancePriceWs(client)
        await self.binance_ws.start()

    async def on_message(self, message):
        # Loại log lỗi do message ko rõ tới từ server/channel nào
        # Chỉ nhận tin nhắn và phản hồi nếu server là TLLN và channel ark
        if message.author is not None and message.guild is not None and message.channel is not None and hasattr(
                message.author, 'guild'):
            if message.author.guild.id == env.SERVER_ID and message.channel.name == 'spam-bot':

                # ! commands
                if len(message.content) > 0 and message.content[0] == self.prefix:
                    # Lấy avatar
                    if message.content.lower() == "!ava tao":
                        await self.send_user_avatar(message)
                        return
                    if message.content.lower() == "!ava may" or message.content.lower() == "!ava mày":
                        await message.channel.send(self.user.avatar_url)
                        return
                    # stoic quote
                    elif message.content.lower() == '!stoic':
                        await self.send_stoic_quote(message)
                        return
                    elif message.content.lower() == '!carljung':
                        await self.send_carl_jung_quote(message)
                        return
                    # BTC Dominance
                    elif message.content == "!dmn":
                        await self.btc_dominance(message)
                        return
                    # an com
                    elif message.content == "!ancom":
                        await self.send_response_message("ancom", message)
                        return
                    # simp
                    elif message.content == '!simp':
                        await self.send_response_message("simp", message)
                        return
                    elif message.content == '!help':
                        await self.send_response_message("help", message, True)
                        return
                    elif message.content == "!horny":
                        await self.send_response_message("no_horny", message, link=True)
                        return
                    elif message.content == "!bonk":
                        await self.send_response_message("bonk", message, link=True)
                        return
                    elif "!xoa" in message.content:
                        await self.create_pet_pet(message)
                    elif '!pick' in message.content:
                        # pick command
                        pick_command_matcher = re.search(self.pick_regex, message.content, re.IGNORECASE)
                        if pick_command_matcher:
                            answers = pick_command_matcher.group().split('!pick ')[1:][0].split(',')
                            await message.channel.send(answers[randint(0, len(answers) - 1)].lstrip())
                            return
                    elif '!e' in message.content:
                        # get emoji
                        emoji_matcher = re.search(self.emoji_regex, message.content, re.IGNORECASE)
                        if emoji_matcher:
                            print(emoji_matcher.group().split(':'))
                            id = emoji_matcher.group().split(':')[2][:-1]
                            if id is not None:
                                await message.channel.send('https://cdn.discordapp.com/emojis/' + id)
                                return
                    elif '!ava ' in message.content:
                        avatar_command_matches = re.search(self.pick_avatar_regex, message.content, re.IGNORECASE)
                        if avatar_command_matches:
                            print('Avatar, content: ' + message.content)
                            await self.send_tagged_user_avatar(message)
                            return
                    elif "!sleep" in message.content or "!wake" in message.content:
                        await self.send_sleep_time(message, "!wake" in message.content)

                #  Nếu có message hỏi "Khi nào xxx 30"
                if 'khi nào' in message.content.lower():
                    ask_matches = re.search(self.ask_when_regex, message.content, re.IGNORECASE)
                    if ask_matches:
                        await self.send_response_message('ask_price', message)
                        return

                # check giá coin
                if len(message.content) > 0 and message.content[0] == '?':
                    await self.send_coin_price(message)

                #  so sanh gia coin
                price_compare_matcher = re.search(self.compare_regex, message.content, re.IGNORECASE)
                if price_compare_matcher:
                    await self.send_coins_compare(message)
                    return
                # Trade, Margin, Future
                await self.bad_behaviour(message)

                # Đập Bắn Đấm
                if 'đập' in message.content.lower():
                    await self.send_response_message("dap", message, link=True)
                    return
                elif 'bắn' in message.content.lower():
                    await self.send_response_message("ban", message, link=True)
                    return
                elif 'đấm' in message.content.lower():
                    await self.send_response_message("dam", message, link=True)
                    return

    # Lấy avatar của người yêu cầu
    async def send_user_avatar(self, message):
        avatar_url = await self.get_avatar_url(message.author.id)
        await message.channel.send(avatar_url)

    async def send_tagged_user_avatar(self, message):
        rawId = message.content.split('!ava ')[1]
        if rawId[2] == "!":
            tagged_id = rawId[3:-1]
        else:
            tagged_id = rawId[2:-1]
        avatar_url = await self.get_avatar_url(tagged_id)
        await message.channel.send(avatar_url)

    # Lấy avatar URL của người dùng bằng id
    async def get_avatar_url(self, id):
        print('fetching user\'s avatar: ' + str(id))
        data = await client.http.get_user_profile(id)
        return 'https://cdn.discordapp.com/avatars/{}/{}.png?size=1024'.format(str(id), data['user']['avatar'])

    async def bad_behaviour(self, message):
        # Bỏ bản thân mình ra ko thôi bị loop tới chết
        if message.author != self.user:
            if 'trade' in message.content.lower():
                await self.send_response_message("trade", message)

            if 'future' in message.content.lower() or 'futures' in message.content.lower():
                await self.send_response_message("future", message)

            if 'margin' in message.content.lower():
                await self.send_response_message("margin", message)

            if 'swap' in message.content.lower():
                await self.send_response_message("swap", message)

            if 'soap' in message.content.lower():
                await self.send_response_message("soap", message)

            if 'vào ark' in message.content.lower() or 'mua ark' in message.content.lower() or 'hốt ark' in message.content.lower():
                await self.send_response_message("buy_ark", message)

            if 'vào ark không' in message.content.lower() or 'vào ark ko' in message.content.lower():
                await self.send_response_message("buy_ark_2", message)

    # Gửi ngẫu nhiên 1 câu thoại stoic
    async def send_stoic_quote(self, message):
        if self.stoic_quotes is not None:
            selected_quote = self.stoic_quotes[randint(0, len(self.stoic_quotes) - 1)]
            await message.channel.send('> **"{quote}"** \n'
                                       '- *{author},{source}*'.format(quote=selected_quote["quote"],
                                                                      author=selected_quote["author"],
                                                                      source=selected_quote["source"]))

    # Gửi ngẫu nhiên 1 câu thoại của carl jung
    async def send_carl_jung_quote(self, message):
        if self.carl_jung_quotes is not None:
            if self.carl_jung_quotes is not None:
                selected_quote = self.carl_jung_quotes[randint(0, len(self.carl_jung_quotes) - 1)]
                await message.channel.send('> **"{quote}"**'.format(quote=selected_quote))

    async def send_coin_price(self, message):
        if message.content.lower() == '?tim':
            await message.channel.send('Coin tim là điều vô giá. Hãy yêu coin tim <:thatim:827892798518460417>')
        else:
            coin_price_command_matches = re.search(self.coin_price_check_regex, message.content, re.IGNORECASE)
            if coin_price_command_matches:
                coin_name = coin_price_command_matches.group().split('?')[1].lower()
                if coin_name in self.coin_gecko_map:
                    print('fetching coin ' + coin_name + ' price')
                    coin_key = self.coin_gecko_map[coin_name]
                    coin_price_json = self.coin_gecko.get_price(ids=coin_key, vs_currencies='usd')
                    await message.channel.send('> ' +
                                               coin_name.upper() + ' = **' + str(
                        coin_price_json[coin_key]['usd']) + '** USD ')

    async def send_coins_compare(self, message):
        split = message.content.split(' ')
        coin_a = self.coin_gecko_map[split[1].lower()]
        coin_b = self.coin_gecko_map[split[4].lower()]

        if coin_a is not None and coin_b is not None:
            result = coin_gecko.get_price(ids=[coin_a, coin_b], vs_currencies='usd')
            price = result[coin_a]['usd'] / result[coin_b]['usd'] * float(split[0])

            await message.channel.send(
                '> ' + message.content.replace("?", "{:.2f}".format(price)).replace("bn", "{:.2f}".format(price)))
        else:
            if coin_a is None:
                await message.channel.send('Không tìm thấy coin' + split[1].upper())
            else:
                await message.channel.send('Không tìm thấy coin' + split[4].upper())

    async def send_sleep_time(self, message, isWake):
        #     !sleep 21:00
        if isWake:
            time = message.content.split('!wake')[1]
        else:
            time = message.content.split('!sleep')[1]

        if time:
            time = time.split(':')
            if len(time) == 2:
                hour = time[0]
                minute = time[1]

                if hour.isnumeric() is False or minute.isnumeric() is False:
                    hour = int(hour)
                    minute = int(minute)

                    if 23 >= hour >= 0 and 0 <= minute <= 59:
                        result = ''
                        for cycle in range(6, 0, -1):
                            if cycle == 5 or cycle == 6:
                                result += self.calulate_sleep_cycle(hour, minute, cycle, isWake) + " 👍\n"
                            else:
                                result += self.calulate_sleep_cycle(hour, minute, cycle, isWake) + "\n"

                        if isWake:
                            await message.channel.send(
                                ">>> Thời gian đi ngủ tối ưu nhất để thức dậy vào lúc {:02d}:{:02d}: \n{}" \
                                .format(hour, minute, result))
                        else:
                            await message.channel.send(
                                ">>> Thời gian thức dậy tối ưu nhất khi đi ngủ vào lúc {:02d}:{:02d}: \n{}" \
                                .format(hour, minute, result))
                        return

        await message.channel.send('> Thời gian nhập vào không hợp lệ')

    def calulate_sleep_cycle(self, hour, minute, cycles, wake=False):
        time = (hour * 60) + minute
        time_cycles = 90 * cycles

        if wake:
            if time - time_cycles < 0:
                result = 1440 + (time - time_cycles)
            else:
                result = time - time_cycles
            result -= 15

        else:
            if time + time_cycles > 1440:
                result = time + time_cycles - 1440
            else:
                result = time + time_cycles
            result += 15

        hour = math.trunc(result / 60)
        minute = result % 60
        return "** {:02d}:{:02d} **".format(hour, minute)

    async def btc_dominance(self, message):
        try:
            print('fetching btc dominance')
            response = self.session.get(self.url)
            data = json.loads(response.text)
            await message.channel.send(
                '> BTC Dominance: **' + "{:.2f}".format(data['data']['btc_dominance']) + '%**')
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            await message.channel.send('> Lấy ứ đc bạn tôi ơi')

    async def create_pet_pet(self, message):
        rawId = message.content.split('!xoa ')[1]
        if rawId[2] == "!":
            tagged_id = rawId[3:-1]
        else:
            tagged_id = rawId[2:-1]
        avatar_url = await self.get_avatar_url(tagged_id)
        pet_response = requests.get('http://localhost:3000?url=' + avatar_url)

        if pet_response.status_code == 200:
            pet_pet = discord.File(io.BytesIO(pet_response.content), filename='pet.gif')
            await message.channel.send(file=pet_pet)

    async def send_response_message(self, command, message, send_all_responses=False, link=False):
        if self.responses is not None:
            responses = self.responses[command]
            if responses is not None and len(responses) > 0:
                if send_all_responses:
                    response = ''.join(responses)
                    await message.channel.send(('>>> ' if link is False else '') + response)
                else:
                    await message.channel.send(
                        ('>>> ' if link is False else '') + responses[randint(0, len(responses) - 1)])


#
# Load coingecko coin list và chuyển về dict. Vì một số coin tìm theo tên sẽ không ra do id khác nhau.
coin_gecko = CoinGeckoAPI()
cg_map = {}
for coin in coin_gecko.get_coins_list():
    cg_map[coin['symbol']] = coin['id']

# Open json and load responses
f = open('responses.json', encoding="utf8")
commands = json.load(f)
f.close()

f = open('stoic.json', encoding='utf8')
quotes = json.load(f)
f.close()

f = open('carljung.json', encoding='utf8')
carl_jung_quotes = json.load(f)
f.close()

client = MyClient(coin_gecko_map=cg_map,
                  coin_gecko=coin_gecko,
                  responses=commands,
                  stoic_quotes=quotes,
                  carl_jung_quotes=carl_jung_quotes)
client.run(env.TOKEN)
