from common.bot import AbstractObserverBot
from bitfinex_app.models import Market, OrderBook, Ticker, Order
from bitfinex_app.api import BitfinexApi
import datetime
import time
from django.utils import timezone
import logging
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


class ObserverBot(AbstractObserverBot):

    def __init__(self, exchange):
        self.api = BitfinexApi()
        super().__init__(exchange=exchange)

    # ran the first time when setting up the bot
    def create_markets(self):
        symbols = self.api.get_markets()
        markets = []
        for symbol in symbols:
            markets.append(
                Market(
                    quote=symbol[-3:],
                    tkr=symbol[:3]
                )
            )
        Market.objects.bulk_create(markets)
        self.coins = markets

    def update_markets(self):
        new_markets = []
        self.coins = Market.objects.all()
        for symbol in self.api.get_markets():
            if not self.coins.filter(tkr=symbol[:3]).filter(quote=symbol[-3:]).exists():
                new_markets.append(
                        Market(
                            quote=symbol[-3:],
                            tkr=symbol[:3]
                        )
                    )
        if new_markets:
            Market.objects.bulk_create(new_markets)

    def subscribe(self):
        self.api.subscribe_orderbooks(self.coins)
        self.api.subscribe_tickers(self.coins)

        # subscribing takes a bit
        time.sleep(5)

    def get_tickers(self, time):
        return self.api.extract_tickers(self.coins, time)

    def get_orderbook(self, time):
        return self.api.extract_orderbook(self.coins, time)

    def cast_tickers(self, tickers):
        tks = []
        for market in tickers['data']:
            for i in tickers['data'][market]:
                tks.append(
                    Ticker(
                        time=tickers['time'],
                        market=market,
                        actual_time=i[1],
                        bid=i[0][0][0],
                        bid_size=i[0][0][1],
                        ask=i[0][0][2],
                        ask_size=i[0][0][3],
                        daily_change=i[0][0][4],
                        daily_change_percentage=i[0][0][5],
                        last_price=i[0][0][6],
                        volume=i[0][0][7],
                        high=i[0][0][8],
                        low=i[0][0][9],
                    )
                )
        return tks

    def cast_orderbook(self, orderbooks):
        orders = []
        for market in orderbooks['data']:
            try:
                current_book = market.orderbook_set.latest()
            except ObjectDoesNotExist:
                # we should only get this error on our first run
                current_book = OrderBook.objects.create(
                    market=market,
                    time=orderbooks['time'],
                )

            for data in orderbooks['data'][market]:
                book = data[0][0]
                # if we disconnect& reconnect or on startup, we receive a completely new orderbook
                if len(book) > 3:
                    new_book = OrderBook.objects.create(
                        market=market,
                        time=orderbooks['time'],
                    )
                    new_book.save()

                    for i in book:
                        if i[0]>0:
                            buy = True
                        elif i[0]<0:
                            buy = False
                        else:
                            buy=None

                        orders.append(
                            Order(
                                buy=buy,
                                orderbook=new_book,
                                rate=i[0],
                                count=i[1],
                                quantity=i[2],
                                last_updated=data[1],
                                time=orderbooks['time'],
                            )
                        )
                else:
                    orders.append(
                        Order(
                            # if current_book is referenced before assignment,
                            # something has gone wrong with our initial creation
                            # of an orderbook
                            orderbook=current_book,
                            rate=book[0],
                            count=book[1],
                            quantity=book[2],
                            last_updated=data[1],
                            time=orderbooks['time'],
                        )
                    )
        return orders

    def refresh_ticker(self, time):
        tks = self.get_tickers(time)
        casted_tks = self.cast_tickers(tks)
        Ticker.objects.bulk_create(casted_tks)
        return casted_tks

    def refresh_orderbook(self, time):
        orderbooks = self.get_orderbook(time)
        orders = self.cast_orderbook(orderbooks)
        Order.objects.bulk_create(orders)
        return orders

    def run(self, single=False):
        # basic startup procedure
        if Market.objects.all().count() == 0:
            self.create_markets()
        else:
            self.update_markets()

        self.subscribe()

        # subscriptions need to connect
        time.sleep(5)
        while True:
            start_time = datetime.datetime.now(tz=timezone.utc)
            tks = self.refresh_ticker(start_time)
            obs = self.refresh_orderbook(start_time)

            if single:
                return tks, obs

            time.sleep(self.setting['REFRESH_RATE'] - (datetime.datetime.now().second - start_time.second))




