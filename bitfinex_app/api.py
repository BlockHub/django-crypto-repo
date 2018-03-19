from btfxwss import BtfxWss
from bitfinex.client import Client
import time
from common.api import AbstractRestApi


class BitfinexApi(AbstractRestApi):

    def __init__(self, key=None, secret=None):

        self.wss = BtfxWss()
        self.wss.start()
        self.client = Client()

        while not self.wss.conn.connected.is_set():
            time.sleep(1)

    def get_markets(self):
        return self.client.symbols()

    def subscribe_tickers(self, markets):
        for market in markets:
            self.wss.subscribe_to_ticker(market.market())

    def subscribe_orderbooks(self, markets):
        for market in markets:
            self.wss.subscribe_to_order_book(market.market())

    def extract_tickers(self, markets, time):
        res = {'time': time, 'data': {}}
        for market in markets:
            queue = self.wss.tickers(market.market())
            subres = []
            while not queue.empty():
                subres.append(queue.get())
            res['data'].update({
                market: subres
            })
        return res

    def extract_orderbook(self, markets, time):
        res = {'time': time, 'data': {}}
        for market in markets:
            queue = self.wss.books(market.market())
            subres = []
            while not queue.empty():
                subres.append(queue.get())
            res['data'].update({
                market: subres
            })
        return res