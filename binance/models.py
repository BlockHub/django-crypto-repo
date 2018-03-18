from django.db import models
from common.models import AbstractOrderBook, AbstractTicker, AbstractMarket
# Create your models here.


class Market(AbstractMarket):
    # used to get a certain orderbook
    is_active = models.BooleanField(default=True)
    min_trade_size = models.FloatField()
    ice_berg_allowed = models.BooleanField()

    def market(self):
        return self.tkr + self.quote


class Ticker(AbstractTicker):
    pass


class OrderBook(AbstractOrderBook):
    coin = models.ForeignKey(Market, on_delete=models.CASCADE)
    last_updated = models.IntegerField()
