from django.db import models
from common.models import AbstractTicker, AbstractCoin, AbstractOrderBook
# Create your models here.


class Coin(AbstractCoin):
    # used to get a certain orderbook
    market_name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    base_currency = models.CharField(max_length=10)
    min_trade_size = models.FloatField()


class Ticker(AbstractTicker):
    pass


class OrderBook(AbstractOrderBook):
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)

