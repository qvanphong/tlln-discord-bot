from price_db import PriceDB
import tornado.websocket
import json
import env
import discord_utils

try:
    import thread
except ImportError:
    import _thread as thread


class BinancePriceWs:
    discord_client = None
    price_db = PriceDB()

    gas_price = None
    neo_price = None
    ark_price = None
    firo_price = None
    btc_price = None
    zen_price = None
    dash_price = None
    temp_btc = {'coin_name': 'btc', 'last_price': '', 'time': ''}

    difference_percentage = 5

    def __init__(self, client):
        self.discord_client = client

    async def on_message(self, message):
        json_message = json.loads(message)

        if json_message["data"]["s"] == "NEOUSDT":
            self.neo_price = await self.alert_pump_or_dump("neo", self.neo_price, json_message)
        if json_message["data"]["s"] == "FIROUSDT":
            self.firo_price = await self.alert_pump_or_dump("firo", self.firo_price, json_message)
        if json_message["data"]["s"] == "BTCUSDT":
            self.btc_price = await self.alert_pump_or_dump("btc", self.btc_price, json_message)
        if json_message["data"]["s"] == "ZENUSDT":
            self.zen_price = await self.alert_pump_or_dump("zen", self.zen_price, json_message)
        if json_message["data"]["s"] == "DASHUSDT":
            self.dash_price = await self.alert_pump_or_dump("dash", self.dash_price, json_message)
        if json_message["data"]["s"] == "GASBTC":
            self.gas_price = await self.alert_pump_or_dump("gas", self.gas_price, json_message, currency='BTC')
        if json_message["data"]["s"] == "ARKBTC":
            self.ark_price = await self.alert_pump_or_dump("ark", self.ark_price, json_message, currency='BTC')

    def has_big_price_change(self, old_price, current_price):
        if old_price < current_price:
            difference = current_price - old_price
            difference_percentage = difference * 100 / old_price
            if difference_percentage >= self.difference_percentage:
                return 1
        elif old_price > current_price:
            difference = old_price - current_price
            difference_percentage = difference * 100 / current_price
            if difference_percentage >= self.difference_percentage:
                return -1
        return 0

    async def alert_pump_or_dump(self, coin_name, old_price_data, current_price_data, currency='USD'):
        current_price = current_price_data["data"]["c"]
        time = current_price_data["data"]["E"]

        # save btc price every second for convert USD
        if coin_name == 'btc':
            self.temp_btc['last_price'] = current_price
            self.temp_btc['time'] = time

        if old_price_data is None:
            self.price_db.insert_to_db(coin_name, current_price, time)
            old_price_data = self.price_db.get_coin_by_name(coin_name)

        if currency == 'BTC':
            if self.btc_price is not None:
                old_price_usd = float(old_price_data["last_price"]) * float(self.btc_price["last_price"])
                new_price_usd = float(current_price) * float(self.btc_price["last_price"])

                price_changed = self.has_big_price_change(old_price_usd, new_price_usd)
            else:
                return
        else:
            price_changed = self.has_big_price_change(float(old_price_data["last_price"]), float(current_price))

        if price_changed != 0:
            message = ">>> {icon} **{}** vừa {signal} {:.2f}% trên sàn Binance. Từ **{:{prec}} USD** {up_down} **{:{prec}} USD**" \
                .format(coin_name.upper(),
                        self.difference_percentage,
                        float(old_price_data["last_price"]) if currency == 'USD' else old_price_usd,
                        float(current_price) if currency == 'USD' else new_price_usd,
                        icon="📈" if price_changed == 1 else "📉",
                        signal="tăng" if price_changed == 1 else "giảm",
                        up_down="lên" if price_changed == 1 else "xuống",
                        prec=".2f")

            await self.discord_client \
                .get_guild(discord_utils.get_server_tlln_id()) \
                .get_channel(discord_utils.get_channel_id(coin_name)) \
                .send(message)

            await self.discord_client \
                .get_guild(discord_utils.get_server_tlln_id()) \
                .get_channel(discord_utils.get_spam_bot_channel_id()) \
                .send(message)

            self.price_db.insert_to_db(coin_name, current_price, time)
            return {'coin_name': coin_name, 'last_price': current_price, 'time': time}

        return old_price_data

    def load_old_price(self):
        self.gas_price = self.price_db.get_coin_by_name("gas")
        self.neo_price = self.price_db.get_coin_by_name("neo")
        self.ark_price = self.price_db.get_coin_by_name("ark")
        self.firo_price = self.price_db.get_coin_by_name("firo")
        self.btc_price = self.price_db.get_coin_by_name("btc")
        self.zen_price = self.price_db.get_coin_by_name("zen")
        self.dash_price = self.price_db.get_coin_by_name("dash")

    # Start binance websocket, đồng thời load lại các dữ liệu giá cữ trước khi chạy
    async def start(self):

        self.load_old_price()

        client = await tornado.websocket.websocket_connect(url=env.BINANCE_WS_URL)
        while True:
            message = await client.read_message()

            await self.on_message(message)
