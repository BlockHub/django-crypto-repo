from django.db import models

# Create your models here.
from django.db import models
from common.models import AbstractOrderBook, AbstractTicker, AbstractMarket, AbstractOrder
# Create your models here.


class Market(AbstractMarket):
    # used to get a certain orderbook

    def market(self):
        return (self.tkr + self.quote).upper()


class Ticker(AbstractTicker):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    actual_time = models.IntegerField() # websocket returned timestamp

    bid	= models.FloatField() # Price of last highest bid
    bid_size = models.FloatField() # Size of the last highest bid
    ask = models.FloatField() #	Price of last lowest ask
    ask_size = models.FloatField() # Size of the last lowest ask
    daily_change = models.FloatField() # Amount that the last price has changed since yesterday
    daily_change_percentage	=models.FloatField() # Amount that the price has changed expressed in percentage terms
    last_price = models.FloatField() # Price of the last trade.
    volume = models.FloatField() # Daily volume
    high = models.FloatField() # Daily high
    low = models.FloatField() # Daily low


class OrderBook(AbstractOrderBook):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)

    precision = models.CharField(default='P0', max_length=2, null=True)  # string Level of price aggregation (P0, P1, P2, P3). The default is P0.
    frequency = models.CharField(default='F0', max_length=2, null=True)  # string Frequency of updates (F0, F1). F0=realtime / F1=2sec. The default is F0.
    length = models.CharField(max_length=3, default="25")	 # string Number of price points ("25", "100") [default="25"]


class Order(AbstractOrder):
    orderbook = models.ForeignKey(OrderBook, on_delete=models.CASCADE)
    count = models.IntegerField()  # int	Number of orders at that price level.
                                   # quantity is the total number available
    last_updated = models.IntegerField()
    time=models.DateTimeField()
