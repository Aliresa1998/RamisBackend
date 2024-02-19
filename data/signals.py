from django.db import models
from users.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import Trade



@receiver(post_save, sender=Trade)
def calculate_and_check_margin(sender, instance, created, **kwargs):
    if created:  # Only proceed if a new trade is being created
        total_trade_value = instance.amount  # Assuming 'amount' is the leveraged amount
        leverage = instance.leverage
        initial_margin = total_trade_value / Decimal(leverage)

        # Update the trade's margin
        instance.margin = initial_margin
        instance.save()

        # Check if the trader has enough balance
        account, created = CustomUser.objects.get_or_create(user=instance.user)
        if account.balance >= initial_margin:
            print("Sufficient balance available.")
            # Optionally, you can deduct the margin from the account balance here
            # and save the account to reflect the margin lock.
        else:
            print("Insufficient balance. Trade cannot be executed.")
            # Here, you should handle the insufficient balance case.
            # You might want to mark the trade as invalid or send a notification to the user.