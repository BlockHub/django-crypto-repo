from common.bot import AbstractObserverBot
from bittrex_app.models import Market, OrderBook
from bittrex_app.api import BittrexApi
import asyncio
import datetime


class ObserverBot(AbstractObserverBot):

    def __init__(self, key=None, secret=None):
        self.api = BittrexApi(key=key, secret=secret, v1=True)

    # ran the first time when setting up the bot
    def create_markets(self):
        coins = []
        for i in self.api.get_markets()['result']:
            coins.append(
                Market(
                    market=i['MarketName'],
                    is_active=i['IsActive'],
                    base_currency=i['BaseCurrency'],
                    min_trade_size=i['MinTradeSize'],
                    tkr=i['MarketCurrency'],
                    verbose=i['MarketCurrencyLong'],
                )
            )
        Market.objects.bulk_create(coins)
        return coins

    def update_markets(self):
        coins = Market.objects.all()
        new_coins = []
        for i in self.api.get_markets()['result']:
            if not coins.filter(market=i['MarketName']).exists():
                new_coins.append(
                    Market(
                        market=i['MarketName'],
                        is_active=i['IsActive'],
                        base_currency=i['BaseCurrency'],
                        min_trade_size=i['MinTradeSize'],
                        tkr=i['MarketCurrency'],
                        verbose=i['MarketCurrencyLong'],
                    )
                )

        if new_coins:
            Market.objects.bulk_create(new_coins)

    def cast_orderbooks(self, res, coins, time):
        obs = []
        for ob, coin in zip(res, coins):
            for i in ob['result']['buy']:
                obs.append(
                    OrderBook(
                        buy=True,
                        quantity=i['Quantity'],
                        rate=i['Rate'],
                        time=time,
                        coin=coin,
                    )
                )

            for x in ob['result']['sell']:
                obs.append(
                    OrderBook(
                        buy=False,
                        quantity=x['Quantity'],
                        rate=x['Rate'],
                        time=time,
                        coin=coin,
                    )
                )
        return obs

    def refresh_markets_orderbooks(self, coins, time):
        orderbooks_json = self.api.orderbooks(coins)
        orderbooks = self.cast_orderbooks(orderbooks_json, coins, time)
        OrderBook.objects.bulk_create(orderbooks)
        # used for testing
        return orderbooks

    def run(self, single=False):
        coins = Market.objects.all()

        # basic startup procedure
        if coins.count() == 0:
            coins = self.create_markets()

        else:
            self.update_markets()
            coins = Market.objects.all()

        while True:
            time = datetime.datetime.now()
            obs = self.refresh_markets_orderbooks(coins, time)
            if single:
                return obs





