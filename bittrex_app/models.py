from django.db import models
from common.models import AbstractTicker, AbstractMarket, AbstractOrderBook, AbstractOrder
# Create your models here.


class Market(AbstractMarket):
    # used to get a certain orderbook
    is_active = models.BooleanField(default=True)
    min_trade_size = models.FloatField()

    def market(self):
        return self.quote + '-' + self.tkr


class Ticker(AbstractTicker):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    bid = models.FloatField()
    ask = models.FloatField()
    last = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['bid']),
            models.Index(fields=['ask']),
            models.Index(fields=['last']),
        ]

class OrderBook(AbstractOrderBook):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)


class Order(AbstractOrder):
    orderbook = models.ForeignKey(OrderBook, on_delete=models.CASCADE)
