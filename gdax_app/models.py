from django.db import models
from common.models import AbstractMarket, \
    AbstractTicker, AbstractOrderBook, AbstractOrder
# Create your models here.


class Market(AbstractMarket):
    # used to get a certain orderbook
    base_min_size = models.FloatField()
    base_max_size = models.FloatField()
    limit_only = models.BooleanField()
    margin_enabled = models.BooleanField()

    def market(self):
        return (self.tkr + '-' + self.quote).upper()


class Ticker(AbstractTicker):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)

    price = models.FloatField()
    open_24h = models.FloatField()
    volume_30d = models.FloatField()
    volume_24h = models.FloatField()
    low_24h = models.FloatField()
    high_24h = models.FloatField()
    best_bid = models.FloatField()
    best_ask = models.FloatField()


class OrderBook(AbstractOrderBook):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    sequence = models.BigIntegerField() # gdax does not use TCIP, and thus returns a sequence number
                                     # for users to verify if they are on the correct orderbook


class Order(AbstractOrder):
    orderbook = models.ForeignKey(OrderBook, on_delete=models.CASCADE)
    hash_id = models.CharField(max_length=100)