from crypto_repo.common.api import AbstractMarketApi
from bittrex.bittrex import Bittrex, API_V2_0, API_V1_1, BOTH_ORDERBOOK
from crypto_repo.common.exceptions import ApiResponseError


class BittrexApi(AbstractMarketApi):
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret
        self.v1 = Bittrex(
            api_key=self.key,
            api_secret=self.secret,
            api_version=API_V1_1
        )
        self.v2 = Bittrex(
            api_key=self.key,
            api_secret=self.secret,
            api_version=API_V2_0
        )

    def __api_call(self, method, *args):
        res = method(*args)
        if not res['success']:
            raise ApiResponseError(res['message'])
        return res['result']

    def ticker(self, market):
        return self.__api_call(self.v1.get_orderbook, market, BOTH_ORDERBOOK)

    def get_markets(self):
        return self.__api_call(self.v1.get_markets())



