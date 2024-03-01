from django.db import models
from users.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import Trade, Wallet, Order, Challange, AccountGrowth


def get_user_wallet(user):
    try:
        wallet = Wallet.objects.get(user=user)
        return wallet
    except Wallet.DoesNotExist:
        return None   


@receiver(post_save, sender=Trade)
def calculate_and_check_margin(sender, instance, created, **kwargs):
    if created:
        instance.value = instance.amount * instance.entry_price * instance.leverage
        instance.liquidation_amount = instance.amount * instance.entry_price
        instance.save()


@receiver(post_save, sender=Trade)
def update_wallet(sender, instance, created, **kwargs):
    if instance.trade_status == 'CLOSED':
        wallet = get_user_wallet(instance.user)
        wallet.balance += instance.value
        wallet.save()


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, **kwargs):
    if instance.is_done:
        handle_completed_order(instance)


def handle_completed_order(order):
    if not order.is_done or order.is_delete:
        return

    wallet = get_user_wallet(order.user)
    
    if order.order_type in ['BUY_LIMIT', 'BUY_STOP']:
        total_cost = order.price * order.amount
        wallet.balance -= total_cost
    elif order.order_type in ['SELL_LIMIT', 'SELL_STOP']:
        total_gain = order.price * order.amount
        wallet.balance += total_gain
    wallet.save()


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
    orders = Order.objects.filter(user=user, is_done=False, is_delete=False)
    total_balance = wallet.balance
    for trade in trades:
        total_balance += trade.value
    for order in orders:
        if order.order_type in ['BUY_LIMIT', 'BUY_STOP']:
            total_balance -= order.price * order.amount
        elif order.order_type in ['SELL_LIMIT', 'SELL_STOP']:
            total_balance += order.price * order.amount
    return total_balance


def check_daily_drawwon(user, daily_drawdown):
    if daily_drawdown > 15:
        # what you want to do when the user has exceeded the daily drawdown
        pass


def check_total_drawdown_profit(user, challenge, total_balance):
    total_drawdown = (
        challenge.start_day_assets - total_balance) / challenge.start_day_assets * 100
    if total_drawdown > 0 and total_drawdown > 15:
        # what you want to do when the user has exceeded the total drawdown
        pass
    elif total_drawdown < 0 and total_drawdown > -8 and challenge.challange_level == '1':
        # challenge 1 is completed
        challenge.challange_level = '2'
        challenge.save()
    elif total_drawdown < 0 and total_drawdown > -4 and challenge.challange_level == '2':
        # challenge 2 is completed
        challenge.challange_level = '3'
        challenge.save()


# when should we call this function? wallet_updated, trade_updated, order_updated
def check_challenge(user):

    # get the user's challenge
    challenge = get_user_challenge(user)
    if not challenge:
        return
    
    # get the users total balance = wallet balance + open trades + pending orders
    total_balance = get_user_total_balance(user)

    # get the user's account growth
    account_growth = get_user_account_growth(user)
    
    # calculate the daily drawdown percentage based on the user's account growth
    if account_growth:
        daily_drawdown = (
            account_growth.balance - account_growth.balance) /\
                challenge.start_day_assets * 100
        if challenge.challange_level != '3':
            check_daily_drawwon(user, daily_drawdown)
    else:
        daily_drawdown = 0

    # check the total drawdown and profit
    check_total_drawdown_profit(user, challenge, total_balance)

    