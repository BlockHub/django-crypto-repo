from django.core.management.base import BaseCommand, CommandError
from bittrex_app.bot import ObserverBot
import logging
from locks.decorators import lock_and_log

import warnings
warnings.simplefilter('once')

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):
        @lock_and_log(logger, 'BITTREX')
        def run():
            try:
                self.stdout.write('starting Bittrex Observerbot')
                ObserverBot('BITTREX').run()
            except Exception:
                logger.exception('Failure in bittrexbot')
        run()
