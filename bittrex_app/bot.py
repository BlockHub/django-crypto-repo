from common.bot import AbstractObserverBot
from bittrex_app.models import Market, OrderBook, Ticker, Order
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
                        quote=i['BaseCurrency'],
                        min_trade_size=i['MinTradeSize'],
                        tkr=i['MarketCurrency'],
                        verbose=i['MarketCurrencyLong'],
                    )
                )

        if new_coins:
            Market.objects.bulk_create(new_coins)
        self.coins = Market.objects.all()

    def cast_orderbooks(self, orderbooks, time):
        orders = []
        for book in orderbooks:
            # sometimes a retried api call still failed
            if not book['result']:
                logger.error(book['message'])
                continue

            new_orderbook = OrderBook.objects.create(
                market=book['result']['market'],
                time=time,
            )
            new_orderbook.save()

            try:
                for order in book['result']['buy']:
                    orders.append(
                        Order(
                            buy=True,
                            quantity=order['Quantity'],
                            rate=order['Rate'],
                            orderbook=new_orderbook,
                        ),
                    )
            except TypeError:
                pass

            try:
                for order in book['result']['sell']:
                    orders.append(
                        Order(
                            buy=False,
                            quantity=order['Quantity'],
                            rate=order['Rate'],
                            orderbook=new_orderbook,
                        ),
                    )
            except TypeError:
                pass

        return orders

    def cast_tickers(self, tks, time):
        casted_tks = []
        for tk in tks:
            try:
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
            except TypeError:
                pass
        return casted_tks

    def refresh_markets_orderbooks(self, time):
        orderbooks_json = self.api.orderbooks(self.coins)
        orders = self.cast_orderbooks(orderbooks_json, time)
        Order.objects.bulk_create(orders)
        # used for testing
        return orders

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




