from django.core.management.base import BaseCommand, CommandError
from bittrex_app.bot import ObserverBot
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            self.stdout.write('starting Bittrex Observerbot')
            ObserverBot('BITTREX').run()
        except Exception:
            logger.exception('Failure in bittrexbot')
