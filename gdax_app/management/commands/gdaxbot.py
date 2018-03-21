from django.core.management.base import BaseCommand, CommandError
from gdax_app.bot import ObserverBot
import logging
from locks.decorators import lock_and_log

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):
        @lock_and_log(logger, 'GDAX')
        def run():
            try:
                self.stdout.write('starting Bittrex Observerbot')
                ObserverBot('GDAX').run()
            except Exception:
                logger.exception('Failure in gdaxbot')
        run()