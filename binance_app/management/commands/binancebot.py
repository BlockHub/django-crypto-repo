from django.core.management.base import BaseCommand, CommandError
from binance_app.bot import ObserverBot
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            self.stdout.write('starting Binance Observerbot')
            ObserverBot('BINANCE').run()
        except Exception:
            logger.exception('Failure in binancebot')
            raise