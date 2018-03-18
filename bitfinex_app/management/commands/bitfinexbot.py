from django.core.management.base import BaseCommand, CommandError
from bitfinex_app.bot import ObserverBot


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('starting Bitfinex Observerbot')
        ObserverBot('BINANCE').run()