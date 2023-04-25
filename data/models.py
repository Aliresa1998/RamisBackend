from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Crypto(models.Model):
    name = models.CharField(max_length=15)
    image_url = models.ImageField(null=True, blank=True)


DIRECTION_CHOICES = (
    ('LONG', 'Long'),
    ('SHORT', 'Short')
)


class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    entry_price = models.DecimalField(max_digits=20, decimal_places=8)
    exit_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    take_profit = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    status = models.BooleanField(default=True)
    pnl = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True, blank=True)
