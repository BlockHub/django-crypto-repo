from common.exceptions import NotImplemented

not_implemented = NotImplemented('Method has not been implemented')
from django.conf import settings


class AbstractObserverBot:
    def __init__(self, exchange):
        # exchange needs to be capitalized as it is a key in the settings.BOTS dict
        self.setting = settings.BOTS[exchange]
        self.coins = None

    def create_markets(self):
        raise not_implemented

    def update_markets(self):
        raise not_implemented

    def run(self):
        raise not_implemented