from crypto_repo.common.bot import AbstractObserverBot
from crypto_repo.bittrex.models import Coin, OrderBook
from crypto_repo.bittrex.api import BittrexApi
import datetime


class ObserverBot(AbstractObserverBot):

    def __init__(self, key, secret):
        self.api = BittrexApi(key=key, secret=secret)

    # ran the first time when setting up the bot
    def create_markets(self):
        coins = []
        for i in self.api.get_markets():
            coins.append(
                Coin(
                    market_name=i['MarketName'],
                    is_active=i['IsActive'],
                    base_currency=i['BaseCurrency'],
                    min_trade_size=i['MinTradeSize'],
                    tkr=i['MarketCurrency'],
                    verbose=i['MarketCurrencyLong'],
                )
            )
        Coin.objects.bulk_create(coins)
        return coins

    def update_markets(self):
        coins = Coin.objects.all()
        new_coins = []
        for i in self.api.get_markets():
            if coins.filter(market_name=i['MarketName']).exists():
                new_coins.append(
                    Coin(
                        market_name=i['MarketName'],
                        is_active=i['IsActive'],
                        base_currency=i['BaseCurrency'],
                        min_trade_size=i['MinTradeSize'],
                        tkr=i['MarketCurrency'],
                        verbose=i['MarketCurrencyLong'],
                    )
                )

        if new_coins:
            Coin.objects.bulk_create(new_coins)

    def __get_orderbook(self, market, time):
        res = self.api.ticker(market)
        obs = []

        for i in res['buy']:
            obs.append(
                OrderBook(
                    buy=True,
                    quantity=i['Quantity'],
                    rate=i['rate'],
                    time=time,
                )
            )

        for x in res['sell']:
            obs.append(
                OrderBook(
                    buy=False,
                    quantity=x['Quantity'],
                    rate=x['rate'],
                    time=time
                )
            )

    def get_market_orderbooks(self, coins, time):
        obs = []
        for coin in coins:
            obs.append(self.__get_orderbook(coin.market_name, time))

    def run(self):
        coins = Coin.objects.all()

        # basic startup procedure
        if coins.count() == 0:
            coins = self.create_markets()

        else:
            self.update_markets()
            coins = Coin.objects.all()

        while True:
            time = datetime.datetime.now()
            OrderBook.objects.bulk_create(self.get_market_orderbooks(coins, time))




