from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Crypto(models.Model):
    name = models.CharField(max_length=15)
    image_url = models.ImageField(null=True, blank=True)


DIRECTION_CHOICES = (
    ('LONG', 'Long'),
    ('SHORT', 'Short'),
)
TRANSACTION_CHOICES = (
    ('DEPOSIT', 'deposit'),
    ('WITHDRAW', 'withdraw'),
)


class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    symbol = models.CharField(max_length=20)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    entry_price = models.DecimalField(max_digits=20, decimal_places=2)
    exit_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    stop_loss = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    take_profit = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    status = models.BooleanField(default=True)
    pnl = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True, blank=True)
    leverage = models.IntegerField(default=1)

    class Meta:
        ordering = ['-time']


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.IntegerField(default=0)


class WalletHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_history')
    created = models.DateTimeField(auto_now=True)
    amount = models.IntegerField()
    transaction = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    wallet_destination = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        ordering = ['-created']


class Challange(models.Model):
    LEVEL_CHOICES = (
        ('1', 'Level One'),
        ('2', 'Level Two'),
        ('3', 'Level Three'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='challange')
    challange_level = models.CharField(
        max_length=1, choices=LEVEL_CHOICES, default='1')
    total_assets = models.IntegerField(default=0)
    percent = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    start_day_assets = models.IntegerField(default=0)


class AccountGrowth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    balance = models.IntegerField(default=0)


class Order(models.Model):
    ORDER_TYPES = (
        ('BUY_LIMIT', 'Buy Limit'),
        ('BUY_STOP', 'Buy Stop'),
        ('SELL_LIMIT', 'Sell Limit'),
        ('SELL_STOP', 'Sell Stop'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField()
    symbol = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
