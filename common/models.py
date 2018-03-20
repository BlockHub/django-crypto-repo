from django.db import models

# Create your models here.


class AbstractMarket(models.Model):
    verbose = models.CharField(null=True, max_length=100)
    tkr = models.CharField(max_length=100)
    quote = models.CharField(max_length=10)

    class Meta:
        abstract = True
        unique_together = ('tkr', 'quote')


class AbstractTicker(models.Model):
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['time']),
            ]

    # bittrex api does not support depth a.t.m
    time = models.DateTimeField()


class AbstractOrderBook(models.Model):
    class Meta:
        abstract = True
        get_latest_by = 'time'

    time = models.DateTimeField()


class AbstractOrder(models.Model):
    class Meta:
        abstract = True
        get_latest_by = 'time'
    # only null if orderbooks use a special type to remove orders, i.e. bitfinex
    buy = models.NullBooleanField()
    quantity = models.FloatField()
    rate = models.FloatField()

