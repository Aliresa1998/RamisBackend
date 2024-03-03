import decimal, logging
from datetime import datetime
from celery import shared_task
from .models import Trade, Wallet, AccountGrowth, Order, Challange
from django.contrib.auth.models import User
import yfinance as yf

logger = logging.getLogger(__name__)


def get_active_challenges():
    try:
        challenges = Challange.objects.filter(status='active')
        logger.info("Fetched active challenges successfully.")
        return challenges
    except Exception as e:
        logger.error(f"Error fetching active challenges: {e}")
        return None


def calculate_trade_balance(user):
    try:
        trades = Trade.objects.filter(user=user, trade_status='OPEN')
        trade_balance = sum(trade.pnl for trade in trades)
        logger.info(f"Calculated trade balance for user {user}: {trade_balance}")
        return trade_balance
    except Exception as e:
        logger.error(f"Error calculating trade balance for user {user}: {e}")
        return 0


def calculate_order_balance(user):
    try:
        orders = Order.objects.filter(user=user, is_done=True)
        order_balance = 0
        for order in orders:
            if order.order_type in ['BUY_LIMIT', 'BUY_STOP']:
                order_balance -= order.price * order.amount
            elif order.order_type in ['SELL_LIMIT', 'SELL_STOP']:
                order_balance += order.price * order.amount
        logger.info(f"Calculated order balance for user {user}: {order_balance}")
        return order_balance
    except Exception as e:
        logger.error(f"Error calculating order balance for user {user}: {e}")
        return 0


def get_wallet_balance(user):
    try:
        wallet = Wallet.objects.get(user=user)
        logger.info(f"Fetched wallet balance for user {user}: {wallet.balance}")
        return wallet.balance
    except Exception as e:
        logger.error(f"Error fetching wallet balance for user {user}: {e}")
        return 0


def create_account_growth_entry(user, total_balance):
    try:
        AccountGrowth.objects.create(user=user, balance=total_balance)
        logger.info(f"Created account growth entry for user {user}.")
    except Exception as e:
        logger.error(f"Error creating account growth entry for user {user}: {e}")


def check_challenge_date():
    challenges = Challange.objects.all(status='active')
    for challenge in challenges:
        if challenge.created_at + challenge.duration < datetime.now():
            challenge.status = 'expired'
            challenge.save()
    

@shared_task
def get_user_total_balance():
    challenges = get_active_challenges()
    if challenges:
        for challenge in challenges:
            try:
                trade_balance = calculate_trade_balance(challenge.user)
                order_balance = calculate_order_balance(challenge.user)
                wallet_balance = get_wallet_balance(challenge.user)
                total_balance = trade_balance + order_balance + wallet_balance
                create_account_growth_entry(challenge.user, total_balance)
            except Exception as e:
                logger.error(f"Error processing challenge for user {challenge.user}: {e}")
    else:
        logger.info("No active challenges found.")



def save_daily_balance():
    users = User.objects.all()
    for user in users:
        wallet = Wallet.objects.get(user=user)
        AccountGrowth.objects.create(user=user, balance=wallet.balance)


def calculate_pnl(trade, exit_price):
    if exit_price <= trade.stop_loss:
        pnl = (exit_price - trade.entry_price) * trade.amount
    elif exit_price >= trade.take_profit:
        pnl = (trade.take_profit - trade.entry_price) * trade.amount
    else:
        pnl = (exit_price - trade.entry_price) * trade.amount
    return pnl


@shared_task
def five_minute_long():
    trades = Trade.objects.filter(status=True, direction="LONG")
    for trade in trades:
        exit_price = yf.Ticker(trade.symbol).history()['Close'][-1]
        exit_price = decimal.Decimal(exit_price)
        pnl = calculate_pnl(trade, exit_price)
        Trade.objects.filter(id=trade.id).update(
            exit_price=exit_price,
            pnl=pnl,
            close_time=datetime.now(),
            status=False,
            )
        wallet_balance = Wallet.objects.get(user=trade.user).balance
        new_wallet_balance = wallet_balance + pnl
        Wallet.objects.filter(user=trade.user).update(balance=new_wallet_balance)


def calculate_pnl_short(trade, exit_price):
    if exit_price >= trade.stop_loss:
        pnl = (trade.entry_price - exit_price) * trade.amount
    elif exit_price <= trade.take_profit:
        pnl = (trade.entry_price - trade.take_profit) * trade.amount
    else:
        pnl = (trade.entry_price - exit_price) * trade.amount
    return pnl


@shared_task
def five_minute_short():
    trades = Trade.objects.filter(status=True, direction="SHORT")
    for trade in trades:
        exit_price = yf.Ticker(trade.symbol).history()['Close'][-1]
        exit_price = decimal.Decimal(exit_price)
        pnl = calculate_pnl_short(trade, exit_price)
        Trade.objects.filter(id=trade.id).update(
            exit_price=exit_price,
            pnl=pnl,
            close_time=datetime.now(),
            status=False,
        )
        wallet_balance = Wallet.objects.get(user=trade.user).balance
        new_wallet_balance = wallet_balance + pnl
        Wallet.objects.filter(user=trade.user).update(balance=new_wallet_balance)


@shared_task
def TwentyFourHours():
    users = User.objects.all()
    for user in users:
        (balance, created) = Wallet.objects.get_or_create(user_id=user.id)
        AccountGrowth.objects.create(user_id=user.id, balance=balance.balance)


ORDER_TYPES = (
    ('BUY_LIMIT', 'Buy Limit'),
    ('BUY_STOP', 'Buy Stop'),
    ('SELL_LIMIT', 'Sell Limit'),
    ('SELL_STOP', 'Sell Stop'),
)


@shared_task
def buy_stop():
    orders = Order.objects.filter(order_type='BUY_STOP', is_done=False)
    for order in orders:
        entry_price = float(yf.Ticker(order.symbol).history()['Close'][-1])
        if order.price <= entry_price:
            Trade.objects.create(user=order.user, symbol=order.symbol, amount=order.amount, direction="LONG",
                                 entry_price=entry_price)


@shared_task
def buy_limit():
    orders = Order.objects.filter(order_type='BUY_LIMIT', is_done=False)
    for order in orders:
        entry_price = float(yf.Ticker(order.symbol).history()['Close'][-1])
        if order.price >= entry_price:
            Trade.objects.create(
                user=order.user, symbol=order.symbol, amount=order.amount, direction="LONG",
                                 entry_price=entry_price)


@shared_task
def sell_limit():
    orders = Order.objects.filter(order_type='SELL_LIMIT', is_done=False)
    for order in orders:
        entry_price = float(yf.Ticker(order.symbol).history()['Close'][-1])
        if order.price <= entry_price:
            Trade.objects.create(
                user=order.user, symbol=order.symbol, amount=order.amount, direction="SHORT",
                                 entry_price=entry_price)


@shared_task
def sell_stop():
    orders = Order.objects.filter(order_type='SELL_STOP', is_done=False)
    for order in orders:
        entry_price = float(yf.Ticker(order.symbol).history()['Close'][-1])
        if order.price >= entry_price:
            Trade.objects.create(
                user=order.user, symbol=order.symbol, amount=order.amount, direction="SHORT",
                                 entry_price=entry_price)


@shared_task
def initial_start_day_assets():
    chalengs = Challange.objects.all()
    for chaleng in chalengs:
        start_day_assets = 0
        user = chaleng.user
        walet_balance = Wallet.objects.get(user=user)
        start_day_assets += walet_balance.balance
        trades = Trade.objects.filter(user=user, status=True)
        for trade in trades:
            start_day_assets = + yf.Ticker(trade.symbol).history()['Close'][-1] * trade.amount
        chaleng.start_day_assets = start_day_assets
        chaleng.save()


@shared_task
def check_daily_loss():
    chalengs = Challange.objects.all()
    for chaleng in chalengs:
        now_assets = 0
        user = chaleng.user
        walet_balance = Wallet.objects.get(user=user)
        now_assets += walet_balance.balance
        trades = Trade.objects.filter(user=user, status=True)
        for trade in trades:
            now_assets = + yf.Ticker(trade.symbol).history()['Close'][-1] * trade.amount
        persents = int(((now_assets / chaleng.start_day_assets) - 1) * 100)
        if persents <= -5:
            if chaleng.challange_level == "1":
                walet_balance.balance = 0
                chaleng.delete()
                walet_balance.save()
            if chaleng.challenge_level == "2":
                chaleng.challange_level = '1'
                chaleng.created_at = datetime.now()
                chaleng.save()
            if chaleng.challenge_level == "3":
                chaleng.challange_level = '2'
                chaleng.created_at = datetime.now()
                chaleng.save()
