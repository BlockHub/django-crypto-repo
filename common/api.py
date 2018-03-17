from common.exceptions import NotImplemented

not_implemented = NotImplemented('Method has not been implemented')


class AbstractMarketApi:
    def tickers(self):
        raise not_implemented

    def get_markets(self):
        raise not_implemented

