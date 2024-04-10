from django.db import models
from datetime import datetime
from users.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import Trade, Wallet, Order, Challange, AccountGrowth, WalletSnapShot


def get_user_wallet(user):
    try:
        wallet = Wallet.objects.get(user=user)
        return wallet
    except Wallet.DoesNotExist:
        return None


def update_user_wallet(wallet, value):

    wallet.balance += value
    wallet.save()



def create_wallet_snapshot(user):
    wallet = get_user_wallet(user)
    WalletSnapShot.objects.create(user=user, balance=wallet.balance)


@receiver(post_save, sender=Trade)
def update_wallet(sender, instance, created, **kwargs):
    if created:
        # instance.value = instance.amount * instance.entry_price * instance.leverage
        instance.value = instance.amount * Decimal(instance.entry_price) * Decimal(instance.leverage)
        instance.liquidation_amount = instance.amount * Decimal(instance.entry_price)
        # instance.liquidation_amount = instance.amount * instance.entry_price
        instance.save()

    if instance.trade_status == 'CLOSED':
        # instance.close_time = datetime.now()
        wallet = get_user_wallet(instance.user)
        update_user_wallet(wallet, instance.value)
        create_wallet_snapshot(instance.user)


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    if instance.is_done:
        create_wallet_snapshot(instance.user)


@receiver(post_save, sender=Wallet)
def check_wallet_balance(sender, instance, created, **kwargs):
    if instance.balance < 0:
        instance.balance = 0
        instance.save()


def get_user_challenge(user):
    try:
        challenge = Challange.objects.get(user=user)
        return challenge
    except Challange.DoesNotExist:
        return None


def get_user_account_growth(user):
    try:
        account_growth = AccountGrowth.objects.filter(user=user).latest('date')
        return account_growth
    except AccountGrowth.DoesNotExist:
        return None


def get_user_total_balance(user):
    wallet = get_user_wallet(user)
    trades = Trade.objects.filter(user=user, trade_status='OPEN')
    orders = Order.objects.filter(user=user, is_delete=False)
    total_balance = wallet.balance
    for trade in trades:
        total_balance += trade.value
    for order in orders:
        try:
            if order.is_done:
                total_balance += order.value
            else:
                total_balance += order.amount * order.price
        except:
            pass
    return total_balance


def challenge_failed(user):
    challenge = get_user_challenge(user)
    challenge.status = 'failed'
    challenge.save()
    wallet = get_user_wallet(user)
    wallet.delete()
    custom_user = CustomUser.objects.get(user=user)
    custom_user.plan = None
    custom_user.save()


def check_daily_drawdown(user, daily_drawdown):
    if abs(daily_drawdown) > 15:
        challenge_failed(user)


def check_total_profit_loss(user, challenge, profit_loss):
    if challenge.challange_level == '1':
        if profit_loss > 8:
            challenge.challange_level = '2'
            challenge.save()
        if profit_loss < -12:
            challenge_failed(user)
            # challenge.status = 'failed'
            # challenge.save()

# daily draw down is 5

def check_daily_profit_loss(user, challenge, account_growth, total_balance):
    daily_profit_loss = (total_balance - account_growth.balance) /\
                    challenge.start_day_assets * 100
    if daily_profit_loss <= -5:
        challenge_failed(user)
        # challenge.status = 'failed'
        # challenge.save()


@receiver(post_save, sender=Wallet)
def check_challenge(sender, instance, created, **kwargs):
    if not created:
        user = instance.user
        challenge = get_user_challenge(user)
        if not challenge:
            return
        
        total_balance = get_user_total_balance(user)
        account_growth = get_user_account_growth(user)
        
        if account_growth and challenge.challange_level != '3':
            check_daily_profit_loss(user, challenge, account_growth, total_balance)
        
        # calulate total profit loss    
        total_profit_loss = (total_balance - challenge.start_day_assets) /\
                        challenge.start_day_assets * 100
        check_total_profit_loss(user, challenge, total_profit_loss)

    