from common.bot import AbstractObserverBot
from bittrex_app.models import Market, OrderBook, Ticker
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
                    quote=i['BaseCurrency'],
                    min_trade_size=i['MinTradeSize'],
                    tkr=i['MarketCurrency'],
                    verbose=i['MarketCurrencyLong'],
                )
            )
        Market.objects.bulk_create(coins)
        self.coins = coins

    def update_markets(self):
        new_coins = []
        self.coins = Market.objects.all()
        for i in self.api.get_markets()['result']:
            if not self.coins.filter(tkr=i['MarketCurrency']).filter(quote=i['BaseCurrency']).exists():
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
        self.coins = Market.objects.all()

    def cast_orderbooks(self, res,  time):
        obs = []
        for ob in res:
            # sometimes a retried api call still failed
            if not ob['result']:
                logger.error(ob['message'])
                continue

            for i in ob['result']['buy']:
                obs.append(
                    OrderBook(
                        buy=True,
                        quantity=i['Quantity'],
                        rate=i['Rate'],
                        time=time,
                        market=ob['result']['market']
                    ),
                )

            for x in ob['result']['sell']:
                obs.append(
                    OrderBook(
                        buy=False,
                        quantity=x['Quantity'],
                        rate=x['Rate'],
                        time=time,
                        market=ob['result']['market'],
                    )
                )
        return obs

    def cast_tickers(self, tks, time):
        casted_tks = []
        for tk in tks:
            if not tk['success']:
                logger.error(tk['message'])
                continue
            casted_tks.append(
                Ticker(
                    bid=tk['result']['Bid'],
                    ask=tk['result']['Ask'],
                    last=tk['result']['Last'],
                    time=time,
                    market=tk['result']['market']
                )
            )
        return casted_tks

    def refresh_markets_orderbooks(self, time):
        orderbooks_json = self.api.orderbooks(self.coins)
        orderbooks = self.cast_orderbooks(orderbooks_json, time)
        OrderBook.objects.bulk_create(orderbooks)
        # used for testing
        return orderbooks

    def refresh_tickers(self, time):
        tks_json = self.api.tickers(self.coins)
        tks = self.cast_tickers(tks_json, time)
        Ticker.objects.bulk_create(tks)
        # used for testing
        return tks

    def run(self, single=False):
        # basic startup procedure
        if Market.objects.all().count() == 0:
            self.create_markets()
        else:
            self.update_markets()

        while True:
            start_time = datetime.datetime.now(tz=timezone.utc)
            obs = self.refresh_markets_orderbooks(start_time)
            tks = self.refresh_tickers(start_time)

            if single:
                return obs, tks
            else:
                # in general a refresh run takes 15 s.
                time.sleep(self.setting['REFRESH_RATE'] - (datetime.datetime.now().second - start_time.second))




