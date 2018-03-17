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

    def orderbooks(self, markets):
        tasks = [self.v1.get_orderbook(i.market, BOTH_ORDERBOOK) for i in markets]
        return self.loop.run_until_complete(asyncio.gather(*tasks))

    def get_markets(self):
        task = [self.v1.get_markets()]
        return self.loop.run_until_complete(asyncio.gather(*task))[0]






