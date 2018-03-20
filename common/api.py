from common.exceptions import NotImplemented

not_implemented = NotImplemented('Method has not been implemented')


class AbstractRestApi:
    def tickers(self, markets):
        raise not_implemented

    def get_markets(self):
        raise not_implemented


class AbstractWssApi:

    def get_markets(self):
        raise not_implemented

    def subscribe_tickers(self, markets):
        raise not_implemented

    def subscribe_orderbooks(self, markets):
        raise not_implemented

    def extract_tickers(self, markets, time):
        raise not_implemented

    def extract_orderbook(self, markets, time):
        raise not_implemented
