from django.db import models

# Create your models here.


class AbstractCoin(models.Model):
    verbose = models.CharField(null=True, max_length=100)
    tkr = models.CharField(primary_key=True, max_length=100)

    class Meta:
        abstract = True


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
    buy = models.BooleanField()
    quantity = models.FloatField()
    rate = models.FloatField()
    time = models.DateTimeField()




