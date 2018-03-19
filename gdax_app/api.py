import gdax
from collections import deque
from common.api import AbstractWssApi

class DataBin:

    def __init__(self):
        self.ticker = deque()

    def store_ticker(self, x):
        self.ticker.append(x)

    def dump_ticker(self):
        res = []
        print(self.ticker)
        while self.ticker:
            res.append(self.ticker.popleft())

        return res


class WebsocketClient(gdax.WebsocketClient):
    def __init__(self, settings, handle_ticks=None):
        self.settings = settings
        self.ws_url = settings['WS_ENDPOINT']
        self.handle_ticks = handle_ticks
        self.gdax = gdax.PublicClient()
        self.bin = DataBin()
        self.type = 'ticker'
        self.products = [m['id'] for m in self.gdax.get_products()]
        self.orderbooks = {}
        super().__init__(url=self.ws_url, products=self.products, channels=['ticker'])
        # since gdax has so few products, this takes almost no time. Can be optimized though

    def get_markets(self):
        return [m for m in self.gdax.get_products()]

    def on_message(self, msg):
        if msg['type'] == 'ticker':
            print(msg)
            if self.handle_ticks:
                self.handle_ticks(msg)
            else:
                self.bin.store_ticker(msg)

    # if not handling the on_message, use this to retrieve the ticker deque
    def extract_ticker(self, time):
        return {
            'time': time,
            'data': self.bin.dump_ticker()
        }

    def start_orderbooks(self):
        for market in self.products:
            self.orderbooks.update({market: gdax.OrderBook(market)})

        for market in self.orderbooks:
            self.orderbooks[market].start()

    def dump_orderbooks(self):
        res = {}
        for market in self.orderbooks:
            res.update({market: self.orderbooks[market].get_current_book()})
        return res
