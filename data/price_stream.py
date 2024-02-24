from django.core.management.base import BaseCommand
import yliveticker
from .models import Trade




def on_new_msg(ws, msg):
    print(msg['id'], msg['price'])
    update_trades(msg['id'], msg['price'])


# we should fetch the prices which we have open trades for
yliveticker.YLiveTicker(on_ticker=on_new_msg, ticker_names=[
    "BTC-USD", "ETH-USD", "DOGE-USD", "LTC-USD", "XRP-USD", "ADA-USD", 
    "DOT1-USD", "UNI3-USD", "LINK-USD", "BCH-USD", "XLM-USD", "USDT-USD", 
    "WBTC-USD", "AAVE-USD", "USDC-USD", "EOS-USD", "TRX-USD", "FIL-USD",
    "XTZ-USD", "NEO-USD", "ATOM1-USD", "BSV-USD", "MKR-USD", "COMP-USD", 
    "DASH-USD", "ETC-USD", "ZEC-USD", "OMG-USD", "SUSHI-USD", "YFI-USD", 
    "SNX-USD", "UMA-USD", "REN-USD", "CRV-USD"])

def update_trades(symbol, price):
    # Filter trades with the given symbol
    trades = Trade.objects.filter(symbol=symbol, trade_status='OPEN')
    
    for trade in trades:
        print(trade)