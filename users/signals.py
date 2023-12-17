from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CustomUser, Ticket
from data.models import Challange, Wallet


@receiver(post_save, sender=User)
def CreateChallange(sender, instance, created, **kwargs):
    if created:
        user = instance
        Challange.objects.create(user=user)


@receiver(post_save, sender=User)
def CreateWallet(sender, instance, created, **kwargs):
    if created:
        user = instance
        Wallet.objects.create(user=user, balance=0)


@receiver(post_save, sender=User)
def CreateProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        CustomUser.objects.create(user=user)
