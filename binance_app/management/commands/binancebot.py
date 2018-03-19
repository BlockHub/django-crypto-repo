from django.core.management.base import BaseCommand, CommandError
from binance.bot import ObserverBot


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('starting Binance Observerbot')
        ObserverBot('BINANCE').run()