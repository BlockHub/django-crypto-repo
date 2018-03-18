from django.db import models

# Create your models here.


class AbstractMarket(models.Model):
    verbose = models.CharField(null=True, max_length=100)
    tkr = models.CharField(max_length=100)
    base_currency = models.CharField(max_length=10)

    class Meta:
        abstract = True
        unique_together = ('tkr', 'base_currency')


class AbstractTicker(models.Model):
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['time']),
            ]

    bid_btc = models.FloatField(null=True)
    ask_btc = models.FloatField(null=True)
    bid_usd = models.FloatField(null=True)
    ask_usd = models.FloatField(null=True)
    bid_eur = models.FloatField(null=True)
    ask_eur = models.FloatField(null=True)

    # bittrex api does not support depth a.t.m
    volume = models.FloatField(null=True)
    time = models.DateTimeField(auto_now=True)


class AbstractOrderBook(models.Model):
    class Meta:
        abstract = True

    buy = models.BooleanField()
    quantity = models.FloatField()
    rate = models.FloatField()
    time = models.DateTimeField()





