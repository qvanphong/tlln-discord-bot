from random import randint

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from pycoingecko import CoinGeckoAPI
import discord
import re
import json
import requests
import io
import math
import env
import http.client


class CommandSender:
    # Commands Regex
    prefix = '!'
    pick_regex = r'^\!pick (.*,)*(.*){1}$'
    pick_avatar_regex = r'^\!ava <@[!]?[0-9]*>$'
    coin_price_check_regex = r'^\?\S*$'
    emoji_command_regex = r"!e <(a)?:\w*:[0-9]*>"
    emoji_regex = r"<(a)?:\w*:[0-9]*>"
    compare_regex = r"^[0-9]*(\.[0-9]*)? [a-zA-Z]* = (\?|bn) [a-zA-Z]*$"
    ask_when_regex = r"khi nào .* [0-9]*"

    # Instances
    coin_gecko = CoinGeckoAPI()  # coingecko instance
    coin_gecko_map = {}  # coingecko coins list
    responses = None  # list of commands response
    stoic_quotes = None  # list of stoic quotes
    carl_jung_quotes = None  # list of Carl Jung quotes
    url = 'https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': env.CMC_KEY,
    }
    client = None  # Discord Client

    # Emojis
    emoji_money = "💰"
    emoji_check = "✅"
    emoji_cross = "❎"

    session = Session()
    session.headers.update(headers)

    def __init__(self, client):
        # Load coingecko coin list và chuyển về dict. Vì một số coin tìm theo tên sẽ không ra do id khác nhau.
        for coin in self.coin_gecko.get_coins_list():
            self.coin_gecko_map[coin['symbol']] = coin['id']

        # Open json and load responses
        f = open('assets/responses.json', encoding="utf8")
        self.responses = json.load(f)
        f.close()

        f = open('assets/stoic.json', encoding='utf8')
        self.stoic_quotes = json.load(f)
        f.close()

        f = open('assets/carljung.json', encoding='utf8')
        self.carl_jung_quotes = json.load(f)
        f.close()

        self.client = client

    # Lấy avatar của người được tag
    async def send_tagged_user_avatar(self, message):
        tagged_id = message.mentions[0].id
        avatar_url = await self.get_avatar_url(tagged_id)
        await message.add_reaction(self.emoji_check)
        await message.channel.send(avatar_url)

    # Lấy avatar URL của người dùng bằng id
    async def get_avatar_url(self, id):
        data = await self.client.http.get_user_profile(id)
        return 'https://cdn.discordapp.com/avatars/{}/{}.png?size=1024'.format(str(id), data['user']['avatar'])

    async def bad_behaviour(self, message):
        # Bỏ bản thân mình ra ko thôi bị loop tới chết
        if message.author != self.client.user:
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
            await message.add_reaction(self.emoji_check)
            await message.channel.send('> **"{quote}"** \n'
                                       '- *{author},{source}*'.format(quote=selected_quote["quote"],
                                                                      author=selected_quote["author"],
                                                                      source=selected_quote["source"]))
        else:
            await message.add_reaction(self.emoji_cross)

    # Gửi ngẫu nhiên 1 câu thoại của carl jung
    async def send_carl_jung_quote(self, message):
        if self.carl_jung_quotes is not None:
            selected_quote = self.carl_jung_quotes[randint(0, len(self.carl_jung_quotes) - 1)]
            await message.add_reaction(self.emoji_check)
            await message.channel.send('> **"{quote}"**'.format(quote=selected_quote))
        else:
            await message.add_reaction(self.emoji_cross)

    async def send_coin_price(self, message):
        if message.content.lower() == '?tim':
            await message.add_reaction(self.emoji_money)
            await message.channel.send('Coin tim là điều vô giá. Hãy yêu coin tim <:thatim:827892798518460417>')
        else:
            coin_price_command_matches = re.search(self.coin_price_check_regex, message.content, re.IGNORECASE)
            if coin_price_command_matches:
                coin_name = coin_price_command_matches.group().split('?')[1].lower()
                if coin_name in self.coin_gecko_map:
                    coin_key = self.coin_gecko_map[coin_name]
                    coin_price_json = self.coin_gecko.get_price(ids=coin_key, vs_currencies='usd')
                    await message.add_reaction(self.emoji_money)
                    await message.channel.send('> ' +
                                               coin_name.upper() + ' = **' + str(
                        coin_price_json[coin_key]['usd']) + '** USD ')
                else:
                    await message.add_reaction(self.emoji_cross)

    async def send_coins_compare(self, message):
        split = message.content.split(' ')
        coin_a = self.coin_gecko_map[split[1].lower()] if split[1].lower() in self.coin_gecko_map else None
        coin_b = self.coin_gecko_map[split[4].lower()] if split[4].lower() in self.coin_gecko_map else None

        if coin_a is not None and coin_b is not None:
            result = self.coin_gecko.get_price(ids=[coin_a, coin_b], vs_currencies='usd')
            price = result[coin_a]['usd'] / result[coin_b]['usd'] * float(split[0])

            message_to_send = '> ' + message.content.replace("?", "{:.2f}".format(price)).replace("bn", "{:.2f}".format(
                price))
            await message.add_reaction(self.emoji_money)
            await message.channel.send(message_to_send.upper())
        else:
            await message.add_reaction(self.emoji_cross)
            if coin_a is None:
                await message.channel.send('Không tìm thấy coin {}'.format(split[1].upper()))
            else:
                await message.channel.send('Không tìm thấy coin {}'.format(split[4].upper()))

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

                        await message.add_reaction(self.emoji_check)
                        if isWake:
                            await message.channel.send(
                                ">>> Thời gian đi ngủ tối ưu nhất để thức dậy vào lúc {:02d}:{:02d}: \n{}" \
                                    .format(hour, minute, result))
                        else:
                            await message.channel.send(
                                ">>> Thời gian thức dậy tối ưu nhất khi đi ngủ vào lúc {:02d}:{:02d}: \n{}" \
                                    .format(hour, minute, result))
                        return

        await message.add_reaction(self.emoji_cross)
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
            response = self.session.get(self.url)
            data = json.loads(response.text)
            await message.add_reaction(self.emoji_check)
            await message.channel.send(
                '> BTC Dominance: **' + "{:.2f}".format(data['data']['btc_dominance']) + '%**')
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
            await message.add_reaction(self.emoji_cross)

    async def create_gif_emoji(self, message, type):
        if len(message.mentions) > 0:
            tagged_id = message.mentions[0].id
            avatar_url = await self.get_avatar_url(tagged_id)
            gif_emoji_response = requests.get('http://localhost:3000?url={}&type={}'.format(avatar_url, type))

            if gif_emoji_response.status_code == 200:
                pet_pet = discord.File(io.BytesIO(gif_emoji_response.content), filename='generated.gif')
                await message.add_reaction(self.emoji_check)
                await message.channel.send(file=pet_pet)
        else:
            await message.add_reaction(self.emoji_cross)

    async def send_response_message(self, command, message, send_all_responses=False, link=False):
        response_message = self.get_response_message(command, send_all_responses)
        if response_message is not None:
            await message.channel.send(('>>> ' if link is False else '') + response_message)

    async def send_fap_content(self, message):
        conn = http.client.HTTPSConnection("emergency.nofap.com")
        conn.request("GET", "/director.php?cat=em&religious=true")
        res = conn.getresponse()
        data = res.read()
        await message.add_reaction(self.emoji_check)
        await message.channel.send(data.decode("utf-8"))

    def is_regex_match(self, message_content, pattern):
        return re.search(pattern, message_content, re.IGNORECASE) is not None

    def get_response_message(self, command, get_all=False):
        if self.responses is not None:
            responses = self.responses[command]
            if responses is not None and len(responses) > 0:
                if get_all:
                    return ''.join(responses)
                return responses[randint(0, len(responses) - 1)]
