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

    buy = models.BooleanField()
    quantity = models.FloatField()
    rate = models.FloatField()
    time = models.DateTimeField()





