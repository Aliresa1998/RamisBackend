from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from data.models import AccountGrowth, Wallet

class Command(BaseCommand):
    help = 'Records the daily balance of each user'

    def handle(self, *args, **options):
        for user in User.objects.all():
            try:
                wallet = Wallet.objects.get(user=user)
                AccountGrowth.objects.create(
                    user=user,
                    balance=wallet.balance
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Recorded daily balance for user: {user.username}'))
            except Wallet.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'No wallet found for user: {user.username}'))
