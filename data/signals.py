from django.db import models
from users.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import Trade



@receiver(post_save, sender=Trade)
def calculate_and_check_margin(sender, instance, created, **kwargs):
    if created:
        instance.value = instance.amount * instance.entry_price * instance.leverage
        instance.liquidation_amount = instance.amount * instance.entry_price
        instance.save()