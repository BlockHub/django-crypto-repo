from common.api import AbstractMarketApi
from aiobittrex.bittrex import Bittrex, API_V2_0, API_V1_1, BOTH_ORDERBOOK
import asyncio
from common.exceptions import ProgrammingError


class BittrexApi(AbstractMarketApi):

    def __init__(self, key=None, secret=None, v1=False, v2=False):

        if not v1 and not v2:
            raise ProgrammingError('specify v1 and/or v2')

        self.key = key
        self.secret = secret

        if v1:
            self.v1 = Bittrex(
                api_key=self.key,
                api_secret=self.secret,
                api_version=API_V1_1
            )

        if v2:
            self.v2 = Bittrex(
                api_key=self.key,
                api_secret=self.secret,
                api_version=API_V2_0
            )
        self.loop = asyncio.get_event_loop()

    # def tickers(self, market):
    #     return self.__api_call(self.v1.get_orderbook, market, BOTH_ORDERBOOK)

    async def get_orderbook(self, market):
        res = await self.v1.get_orderbook(market.market(), BOTH_ORDERBOOK)

        # a single retry if the api fails
        if not res['success']:
            res = await self.v1.get_orderbook(market.market(), BOTH_ORDERBOOK)

        # our loop might return the orderbooks unordered. This way our FK relations are correct.
        if res['result']:
            res['result'].update({
                'market': market
            })
        return res

    def orderbooks(self, markets):
        tasks = [self.get_orderbook(i) for i in markets]
        obs = self.loop.run_until_complete(asyncio.gather(*tasks))
        return obs

    def get_markets(self):
        task = [self.v1.get_markets()]
        return self.loop.run_until_complete(asyncio.gather(*task))[0]

    async def get_ticker(self, market):
        res = await self.v1.get_ticker(market.market())

        # a single retry if the api fails
        if not res['success']:
            res = await self.v1.get_ticker(market.market())

        # our loop might return the orderbooks unordered. This way our FK relations are correct.
        if res['result']:
            res['result'].update({
                'market': market
            })
        return res

    def tickers(self, markets):
        tasks = [self.get_ticker(i) for i in markets]
        tks = self.loop.run_until_complete(asyncio.gather(*tasks))
        return tks


