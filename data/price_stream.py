import yliveticker


from .models import Trade

def on_new_msg(ws, msg):
    print(msg)
    # filter all the trades with the symbol of the message
    # run some checks asynchronously

# i think this is better to fetch all the prices
yliveticker.YLiveTicker(on_ticker=on_new_msg, ticker_names=[
    "BTC=X", "BTC-USD", "ETH-USD", "DOGE-USD", "LTC-USD", "XRP-USD", "ADA-USD", 
    "DOT1-USD", "UNI3-USD", "LINK-USD", "BCH-USD", "XLM-USD", "USDT-USD", 
    "WBTC-USD", "AAVE-USD", "USDC-USD", "EOS-USD", "TRX-USD", "FIL-USD",
    "XTZ-USD", "NEO-USD", "ATOM1-USD", "BSV-USD", "MKR-USD", "COMP-USD", 
    "DASH-USD", "ETC-USD", "ZEC-USD", "OMG-USD", "SUSHI-USD", "YFI-USD", 
    "SNX-USD", "UMA-USD", "REN-USD", "CRV-USD"])

# we can write a post save method for the trades to calculate the wallet balance