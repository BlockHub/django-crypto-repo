from common.bot import AbstractObserverBot
from binance.models import Market, OrderBook
from binance.api import BinanceApi
import datetime
import time
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class ObserverBot(AbstractObserverBot):

    def __init__(self, exchange, key='', secret='', ):
        self.api = BinanceApi(key=key, secret=secret)
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

    def cast_orderbooks(self, res,  time):

        obs = []
        for ob in res:
            # sometimes a retried api call still failed
            if not ob['bids']:
                logger.error(ob)
                continue

            for i in ob['bids']:
                coin = self.coins.get(tkr=ob['tkr'], quote=ob['quote'])

                obs.append(
                    OrderBook(
                        buy=True,
                        quantity=i[1],
                        rate=i[0],
                        time=time,
                        coin=coin,
                        last_updated=ob['lastUpdateId'],
                    )
                )

            for x in ob['asks']:
                coin = self.coins.get(tkr=ob['tkr'], quote=ob['quote'])
                obs.append(
                    OrderBook(
                        buy=False,
                        quantity=x[1],
                        rate=x[0],
                        time=time,
                        coin=coin,
                        last_updated=ob['lastUpdateId'],
                    )
                )
        return obs

    def refresh_markets_orderbooks(self, time):
        orderbooks_json = self.api.orderbooks(self.coins)
        orderbooks = self.cast_orderbooks(orderbooks_json, time)
        OrderBook.objects.bulk_create(orderbooks)
        # used for testing
        return orderbooks

    def run(self, single=False):
        # basic startup procedure
        if Market.objects.all().count() == 0:
            self.create_markets()
        else:
            self.update_markets()

        while True:
            start_time = datetime.datetime.now(tz=timezone.utc)
            obs = self.refresh_markets_orderbooks(start_time)
            if single:
                return obs
            else:
                # in general a refresh run takes 15 s.
                time.sleep(self.setting['REFRESH_RATE'] - (datetime.datetime.now().second - start_time.second))





