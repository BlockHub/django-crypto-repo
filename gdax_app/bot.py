from common.bot import AbstractObserverBot
from gdax_app.models import Market, OrderBook, Ticker, Order
from gdax_app.api import WebsocketClient
import datetime
import time
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)


class ObserverBot(AbstractObserverBot):

    def __init__(self, exchange):
        self.api = WebsocketClient(
            handle_ticks=self.handle_ticker

        )
        super().__init__(exchange=exchange)

    # ran the first time when setting up the bot
    def create_markets(self):
        res = self.api.get_markets()
        markets = []
        for id in res:
            markets.append(
                Market(
                    quote=id['quote_currency'],
                    tkr=id['base_currency'],
                    base_min_size=id['base_min_size'],
                    base_max_size=id['base_max_size'],
                    margin_enabled=id['margin_enabled'],
                    limit_only=id['limit_only'],
                )
            )
        Market.objects.bulk_create(markets)
        self.coins = markets

    def update_markets(self):
        new_markets = []
        self.coins = Market.objects.all()
        for id in self.api.get_markets():
            if not self.coins.filter(tkr=id['base_currency']).filter(quote=id['quote_currency']).exists():
                new_markets.append(
                    Market(
                        quote=id['quote_currency'],
                        tkr=id['base_currency'],
                        base_min_size=id['base_min_size'],
                        base_max_size=id['base_max_size'],
                        margin_enabled=id['margin_enabled'],
                        limit_only=id['limit_only'],
                    )
                )
        if new_markets:
            Market.objects.bulk_create(new_markets)
        self.coins = Market.objects.all()

    def subscribe(self):
        # subscribes to all product tickers
        self.api.start()

    def start_orderbooks(self):
        self.api.start_orderbooks()

    def get_orderbooks(self):
        return self.api.dump_orderbooks()

    def handle_ticker(self, msg):
        Ticker.objects.create(
            market=self.coins.get(
                quote=msg['product_id'][-3:],
                tkr=msg['product_id'][:3]
            ),
            price=msg['price'],
            open_24h=msg['open_24h'],
            volume_24h=msg['volume_24h'],
            low_24h=msg['low_24h'],
            high_24h=msg['high_24h'],
            volume_30d=msg['volume_30d'],
            best_bid=msg['best_bid'],
            best_ask=msg['best_ask']
        ).save()

    def cast_orderbook(self, orderbooks, time):
        books = []
        for market_id in orderbooks:
            ob = OrderBook.objects.create(
                market=self.coins.get(
                    tkr=market_id[:3],
                    quote=market_id[-3:]
                ),
                sequence=orderbooks[market_id]['sequence'],
                time=time,
            )
            ob.save()
            for orders in orderbooks[market_id]['asks']:
                for order in orderbooks[market_id]['asks'][orders]:
                    books.append(
                        Order(
                            orderbook=order,
                            rate=orderbooks[market_id]['asks'][orders][order][0],
                            quantity=orderbooks[market_id]['asks'][orders][order][1],
                            hash_id=orderbooks[market_id]['asks'][orders][order][2],
                        )
                    )
            for orders in orderbooks[market_id]['bids']:
                for order in orderbooks[market_id]['bids'][orders]:
                    books.append(
                        Order(
                            orderbook=order,
                            rate=orderbooks[market_id]['bids'][orders][order][0],
                            quantity=orderbooks[market_id]['bids'][orders][order][1],
                            hash_id=orderbooks[market_id]['bids'][orders][order][2],
                        )
                    )
        return books

    def refresh_orderbook(self, time):
        obs = self.get_orderbooks()
        casted_obs = self.cast_orderbook(obs, time)
        print(casted_obs)
        Order.objects.bulk_create(casted_obs)
        return obs

    def run(self, single=False):
        # basic startup procedure
        if Market.objects.all().count() == 0:
            self.create_markets()
        else:
            self.update_markets()

        self.subscribe()

        # subscriptions need to connect
        time.sleep(5)
        self.api.start()
        self.start_orderbooks()

        while True:
            start_time = datetime.datetime.now(tz=timezone.utc)
            self.refresh_orderbook(start_time)
            time.sleep(self.setting['REFRESH_RATE'] - (datetime.datetime.now().second - start_time.second))

