from tinydb import TinyDB, Query


class PriceDB:
    db = TinyDB('db/price_db.json')
    price_query = Query()

    def insert_to_db(self, name, price, time):
        if self.db.get(self.price_query.coin_name == name) is None:
            return self.db.insert({'coin_name': name, 'last_price': price, 'time': time})
        else:
            return self.db.update({'coin_name': name, 'last_price': price, 'time': time}, self.price_query.coin_name == name)

    def read_all_coins(self):
        return self.db.all()

    def get_coin_by_name(self, name):
        coin = self.db.get(self.price_query.coin_name == name)
        return coin