from django.db import models
from common.models import AbstractTicker, AbstractMarket, AbstractOrderBook
# Create your models here.


class Market(AbstractMarket):
    # used to get a certain orderbook
    is_active = models.BooleanField(default=True)
    base_currency = models.CharField(max_length=10)
    min_trade_size = models.FloatField()


class Ticker(AbstractTicker):
    pass


class OrderBook(AbstractOrderBook):
    coin = models.ForeignKey(Market, on_delete=models.CASCADE)

