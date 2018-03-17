from django.core.management.base import BaseCommand, CommandError
from bittrex_app.bot import ObserverBot

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('starting Bittrex Observerbot')
        ObserverBot().run()