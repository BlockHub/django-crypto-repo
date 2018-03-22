from django.core.management.base import BaseCommand, CommandError
import logging
from locks.models import Lock
import warnings
warnings.simplefilter('once')

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        for x in Lock.objects.all():
            x.locked = False
            x.save()
