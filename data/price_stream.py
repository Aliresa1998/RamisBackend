import os
import django
import sys

# Add your project to the PYTHONPATH
sys.path.append('/home/RamisBackend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RamisBackend.settings')
django.setup()
import yliveticker
from data.sketch import price_changed
import logging

logger = logging.getLogger(__name__)


def on_new_msg(ws, msg):
    print(msg['id'], msg['price'])
    logger.info(f"price get")
    price_changed(msg['id'], msg['price'])


# we should fetch the prices which we have open trades for
yliveticker.YLiveTicker(on_ticker=on_new_msg, ticker_names=[
    "BTC-USD", "ETH-USD", "DOGE-USD", "LTC-USD", "XRP-USD", "ADA-USD", 
    "DOT1-USD", "UNI3-USD", "LINK-USD", "BCH-USD", "XLM-USD", "USDT-USD", 
    "WBTC-USD", "AAVE-USD", "USDC-USD", "EOS-USD", "TRX-USD", "FIL-USD",
    "XTZ-USD", "NEO-USD", "ATOM1-USD", "BSV-USD", "MKR-USD", "COMP-USD", 
    "DASH-USD", "ETC-USD", "ZEC-USD", "OMG-USD", "SUSHI-USD", "YFI-USD", 
    "SNX-USD", "UMA-USD", "REN-USD", "CRV-USD"])
