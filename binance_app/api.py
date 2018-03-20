from common.api import AbstractRestApi
from aiobinance.client import Client
from binance.websockets import BinanceSocketManager
from binance.client import Client as SyncClient
from binance.depthcache import DepthCacheManager
from concurrent.futures._base import TimeoutError
import asyncio


class BinanceRestApi(AbstractRestApi):

    def __init__(self, key=None, secret=None, conn_timout=600, read_timeout=60):

        self.key = key
        self.secret = secret
        self.client = Client(self.key, self.secret, conn_timeout=conn_timout, read_timout=read_timeout)
        self.loop = asyncio.get_event_loop()

    # def tickers(self, market):
    #     return self.__api_call(self.v1.get_orderbook, market, BOTH_ORDERBOOK)

    async def get_orderbook(self, market):
        try:
            res = await self.client.get_order_book(symbol=market.market())

            # a single retry if the api fails
            if not res['bids']:
                res = await self.client.get_order_book(symbol=market.market())

            # our loop might return the orderbooks unordered. This way our FK relations are correct.
            if res['bids']:
                res.update({
                    'market': market})
            return res
        except TimeoutError:
            pass

    def orderbooks(self, markets):
        tasks = [self.get_orderbook(i) for i in markets]
        obs = self.loop.run_until_complete(asyncio.gather(*tasks))
        return obs

    async def get_ticker(self, market):
        try:
            res = await self.client.get_ticker(symbol=market.market())

            # apparently this endpoint might return a list cointaining one dict
            if type(res) == list:
                res = res[0]
            # a single retry if the api fails, no success param, so we check for a different one
            if not res['volume']:
                res = await self.client.get_ticker(symbol=market.market())

            # our loop might return the orderbooks unordered. This way our FK relations are correct.
            if res['volume']:
                res.update({
                    'market': market})
            return res
        except TimeoutError:
            pass

    def tickers(self, markets):
        tasks = [self.get_ticker(i) for i in markets]
        tks = self.loop.run_until_complete(asyncio.gather(*tasks))
        return tks

    def get_markets(self):
        task = [self.client.get_exchange_info()]
        return self.loop.run_until_complete(asyncio.gather(*task))[0]


class BinanceWS:
    def __init__(self, on_ticker, on_orderbook, key=None, secret=None,):
        self.client = SyncClient(key, secret)
        self.ws = BinanceSocketManager(self.client)
        self.on_ticker = on_ticker
        self.on_orderbook = on_orderbook
        self.orderbooks = {}

    def subscribe_tickers(self, markets):
        for i in markets:
            self.ws.start_symbol_ticker_socket(i.market(), self.on_ticker)
        self.ws.start()

    def subscribe_orderbook(self, markets):
        print(len(markets))
        for i in markets:
            dcm = DepthCacheManager(self.client, i.market())
            self.orderbooks.update({i: dcm})
            print('created orderbook: {}'.format(i.market()))

    def extract_orderbooks(self):
        res = {}
        for i in self.orderbooks:
            res.update({i: self.orderbooks[i].get_depth_cache()})
        return res

