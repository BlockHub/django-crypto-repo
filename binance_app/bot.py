from common.bot import AbstractObserverBot
from binance_app.models import Market, OrderBook, Ticker, Order
from binance_app.api import BinanceRestApi
import datetime
import time
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class ObserverBot(AbstractObserverBot):

    def __init__(self, exchange, key='', secret='', ):
        self.api = BinanceRestApi(key=key, secret=secret, conn_timout=None, read_timeout=None)
        super().__init__(exchange=exchange)

    # ran the first time when setting up the bot
    def create_markets(self):
        coins = []
        for i in self.api.get_markets()['symbols']:

            if i['status'] == 'TRADING':
                status = True
            else:
                status = False
            min_trade = i['filters'][1].get('minQty')

            coins.append(
                Market(
                    is_active=status,
                    quote=i['quoteAsset'],
                    min_trade_size=min_trade,
                    tkr=i['baseAsset'],
                    # binance does not offer verbose names with their api
                    verbose=None,
                    ice_berg_allowed=i['icebergAllowed']
                )
            )
        Market.objects.bulk_create(coins)
        self.coins = coins

    def update_markets(self):
        new_coins = []
        self.coins = Market.objects.all()
        for i in self.api.get_markets()['symbols']:
            if not self.coins.filter(tkr=i['baseAsset']).filter(quote=i['quoteAsset']).exists():
                if i['status'] == 'TRADING':
                    status = True
                else:
                    status = False

                min_trade = i['filters'].get('LOT_SIZE')['minQty']

                new_coins.append(
                    Market(
                        is_active=status,
                        quote=i['quoteAsset'],
                        min_trade_size=min_trade,
                        tkr=i['baseAsset'],
                        # binance does not offer verbose names with their api
                        verbose=None,
                        ice_berg_allowed=i['icebergAllowed']
                    )
                )
        if new_coins:
            Market.objects.bulk_create(new_coins)

    def cast_orderbooks(self, orderbooks,  time):

        orders = []
        for orderbook in orderbooks:
            # if Orderbook is None, we had an api timouterror. Better luck next time!
            if not orderbook:
                continue
            # sometimes a retried api call still failed
            if not orderbook['bids'] or not orderbook['market']:
                logger.error(orderbook)
                continue

            ob = OrderBook.objects.create(
                market=orderbook['market'],
                last_updated=orderbook['lastUpdateId'],
                time=time,
            )
            ob.save()

            for i in orderbook['bids']:
                orders.append(
                    Order(
                        buy=True,
                        quantity=i[1],
                        rate=i[0],
                        orderbook=ob,
                    )
                )

            for x in orderbook['asks']:
                orders.append(
                    Order(
                        buy=False,
                        quantity=x[1],
                        rate=x[0],
                        orderbook=ob,
                    )
                )
        return orders

    def cast_tickers(self, res, time):
        tks = []
        for tk in res:
            # if tk is None, the api had a timouterror
            if not tk:
                continue
            if not tk['volume']:
                logger.error(tk)
                continue
            tks.append(
                Ticker(
                    price_change=tk['priceChange'],
                    w_a_price=tk['weightedAvgPrice'],
                    prev_close_price=tk['prevClosePrice'],
                    last_price=tk['lastPrice'],
                    bid_price=tk['bidPrice'],
                    ask_price=tk['askPrice'],
                    open_price=tk['openPrice'],
                    high_price=tk['highPrice'],
                    low_price=tk['lowPrice'],
                    volume=tk['volume'],
                    trade_count=tk['count'],
                    time=time,
                    market=tk['market'],
                )
            )
        return tks

    def refresh_markets_orderbooks(self, time):
        orderbooks_json = self.api.orderbooks(self.coins)
        orders = self.cast_orderbooks(orderbooks_json, time)
        Order.objects.bulk_create(orders)
        # used for testing
        return orders

    def refresh_tickers(self, time):
        tks_json = self.api.tickers(self.coins)
        tks = self.cast_tickers(res=tks_json, time=time)
        Ticker.objects.bulk_create(tks)

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





