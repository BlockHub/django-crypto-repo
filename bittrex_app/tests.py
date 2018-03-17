from django.test import TestCase
from bittrex_app.bot import ObserverBot
import time
# Create your tests here.


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('%s function took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap


class TestBot(TestCase):

    def test_init(self):
        bot = ObserverBot()
        self.assertTrue(bot)

    def test_create_markets(self):
        from bittrex_app.models import Market
        bot = ObserverBot()
        bot.create_markets()
        self.assertTrue(Market.objects.all())

    def test_update_markets(self):
        from bittrex_app.models import Market
        bot = ObserverBot()
        bot.create_markets()

        def delete_market():
            Market.objects.all().first().delete()

        len_markets = Market.objects.all().count()
        delete_market()
        len_markets_minus = Market.objects.all().count()

        self.assertTrue(len_markets - len_markets_minus == 1)
        bot.update_markets()

        len_markets_updated = Market.objects.all().count()
        self.assertEqual(len_markets, len_markets_updated)

    def test_run(self):
        from bittrex_app.models import Market
        bot = ObserverBot()

        bot.create_markets()
        obs = bot.run(single=True)

        self.assertTrue(len(obs) > Market.objects.all().count())
