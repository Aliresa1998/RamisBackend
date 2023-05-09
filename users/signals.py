from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from data.models import Challange

@receiver(post_save, sender=User)
def CreateChallange(sender, instance, created, **kwargs):
    if created:
        user = instance
        print(user)
        print(created)
        Challange.objects.create(user=user)

