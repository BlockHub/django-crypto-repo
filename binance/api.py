from common.api import AbstractMarketApi
from aiobinance.client import Client
import asyncio


class BinanceApi(AbstractMarketApi):

    def __init__(self, key=None, secret=None):

        self.key = key
        self.secret = secret
        self.client = Client(self.key, self.secret)
        self.loop = asyncio.get_event_loop()

    # def tickers(self, market):
    #     return self.__api_call(self.v1.get_orderbook, market, BOTH_ORDERBOOK)

    async def get_orderbook(self, market):
        res = await self.client.get_order_book(symbol=market.market())

        # a single retry if the api fails
        if not res['bids']:
            res = await self.client.get_order_book(symbol=market.market())

        # our loop might return the orderbooks unordered. This way our FK relations are correct.
        if res['bids']:
            res.update({
                'tkr': market.tkr,
                'quote': market.quote})
        return res

    def orderbooks(self, markets):
        tasks = [self.get_orderbook(i) for i in markets]
        obs = self.loop.run_until_complete(asyncio.gather(*tasks))
        return obs

    def get_markets(self):
        task = [self.client.get_exchange_info()]
        return self.loop.run_until_complete(asyncio.gather(*task))[0]