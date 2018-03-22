from django.db import models
from common.models import AbstractOrderBook, AbstractTicker, AbstractMarket, AbstractOrder
# Create your models here.


class Market(AbstractMarket):
    # used to get a certain orderbook
    is_active = models.BooleanField(default=True)
    min_trade_size = models.FloatField()
    ice_berg_allowed = models.BooleanField()

    def market(self):
        return self.tkr + self.quote


class Ticker(AbstractTicker):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    price_change = models.FloatField()
    w_a_price = models.FloatField()
    prev_close_price = models.FloatField()
    last_price = models.FloatField()
    bid_price = models.FloatField()
    ask_price = models.FloatField()
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    volume = models.FloatField()
    trade_count = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['last_price']),
            models.Index(fields=['bid_price']),
            models.Index(fields=['ask_price']),
            models.Index(fields=['volume']),
        ]

class OrderBook(AbstractOrderBook):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    last_updated = models.BigIntegerField()


class Order(AbstractOrder):
    orderbook = models.ForeignKey(OrderBook, on_delete=models.CASCADE)