from common.bot import AbstractObserverBot
from bittrex_app.models import Market, OrderBook
from bittrex_app.api import BittrexApi
import datetime
import time
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class ObserverBot(AbstractObserverBot):

    def __init__(self, exchange, key=None, secret=None, ):
        self.api = BittrexApi(key=key, secret=secret, v1=True)
        super().__init__(exchange=exchange)

    # ran the first time when setting up the bot
    def create_markets(self):
        coins = []
        for i in self.api.get_markets()['result']:
            coins.append(
                Market(
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
            if not coins.filter(tkr=i['MarketCurrency']).filter(base_currency=i['BaseCurrency']).exists():
                new_coins.append(
                    Market(
                        is_active=i['IsActive'],
                        base_currency=i['BaseCurrency'],
                        min_trade_size=i['MinTradeSize'],
                        tkr=i['MarketCurrency'],
                        verbose=i['MarketCurrencyLong'],
                    )
                )

        if new_coins:
            Market.objects.bulk_create(new_coins)

    def cast_orderbooks(self, res,  time):

        obs = []
        for ob in res:
            # sometimes a retried api call still failed
            if not ob['result']:
                logger.error(ob['message'])
            for i in ob['result']['buy']:
                obs.append(
                    OrderBook(
                        buy=True,
                        quantity=i['Quantity'],
                        rate=i['Rate'],
                        time=time,
                        coin=ob['result']['market'],
                    )
                )

            for x in ob['result']['sell']:
                obs.append(
                    OrderBook(
                        buy=False,
                        quantity=x['Quantity'],
                        rate=x['Rate'],
                        time=time,
                        coin=ob['result']['market'],
                    )
                )
        return obs

    def refresh_markets_orderbooks(self, coins, time):
        orderbooks_json = self.api.orderbooks(coins)
        orderbooks = self.cast_orderbooks(orderbooks_json, time)
        OrderBook.objects.bulk_create(orderbooks)
        # used for testing
        return orderbooks

    def run(self, single=False, rate=30):
        coins = Market.objects.all()
        # basic startup procedure
        if coins.count() == 0:
            coins = self.create_markets()

        else:
            self.update_markets()
            coins = Market.objects.all()

        while True:
            start_time = datetime.datetime.now(tz=timezone.utc)
            obs = self.refresh_markets_orderbooks(coins, start_time)
            if single:
                return obs
            else:
                # in general a refresh run takes 15 s.
                time.sleep(self.setting['REFRESH_RATE'] - (datetime.datetime.now().second - start_time.second))





