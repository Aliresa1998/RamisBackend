from django.core.management.base import BaseCommand
from data.tasks import get_user_total_balance

class Command(BaseCommand):
    help = 'Updates user total balances'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting update balances task...')
        get_user_total_balance()
        self.stdout.write('Finished update balances task.')
