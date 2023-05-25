from datetime import datetime
from celery import shared_task
from .models import Trade, Wallet, AccountGrowth
from django.contrib.auth.models import User
import yfinance as yf
import decimal


# @shared_task
# def five_minute_long():
#     trades = Trade.objects.filter(status=True)
#     for trade in trades:
#         exit_price = yf.Ticker(trade.symbol).history()['Close'][-1]
#         exit_price = decimal.Decimal(exit_price)
#         if exit_price >= trade.take_profit or exit_price <= trade.exit_price:
#             pnl = (exit_price - trade.entry_price) * trade.amount
#             Trade.objects.filter(id=trade.id).update(exit_price=exit_price, pnl=pnl, close_time=datetime.now(),
#                                                      status=False, )
#             wallet_balance = Wallet.objects.get(user=trade.user).balance
#             new_wallet_balance = wallet_balance + pnl
#             Wallet.objects.filter(user=trade.user).update(balance=new_wallet_balance)
#

@shared_task
def TwentyFourHours():
    users = User.objects.all()
    for user in users:
        (balance, created) = Wallet.objects.get_or_create(user_id=user.id)
        AccountGrowth.objects.create(user_id=user.id, balance=balance.balance)
