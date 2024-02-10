from abc import ABC, abstractmethod
import yliveticker
from .models import Trade


price_list = [
    "BTC=X", "BTC-USD", "ETH-USD", "DOGE-USD", "LTC-USD", "XRP-USD", "ADA-USD", 
    "DOT1-USD", "UNI3-USD", "LINK-USD", "BCH-USD", "XLM-USD", "USDT-USD", 
    "WBTC-USD", "AAVE-USD", "USDC-USD", "EOS-USD", "TRX-USD", "FIL-USD",
    "XTZ-USD", "NEO-USD", "ATOM1-USD", "BSV-USD", "MKR-USD", "COMP-USD", 
    "DASH-USD", "ETC-USD", "ZEC-USD", "OMG-USD", "SUSHI-USD", "YFI-USD", 
    "SNX-USD", "UMA-USD", "REN-USD", "CRV-USD"
    ]

# Define the common interface for all strategies
class PriceSourceStrategy(ABC):
    @abstractmethod
    def get_price(self, symbol):
        pass

# Concrete strategy: API
class ApiPriceSource(PriceSourceStrategy):
    def get_price(self, symbol):
        # Implement the logic to get the price from an API
        # This is just a placeholder
        return 100.00

# Concrete strategy: WebSocket
class WebSocketPriceSource(PriceSourceStrategy):
    def get_price(self, symbol):
        # Implement the logic to get the price from a WebSocket
        # This is just a placeholder
        return 200.00

# Concrete strategy: YLiveTicker
class YLiveTickerPriceSource(PriceSourceStrategy):
    def __init__(self, price_list):
        self.prices = {}
        yliveticker.YLiveTicker(on_ticker=self.on_new_msg, ticker_names=[price_list])

    def on_new_msg(self, ws, msg):
        symbol = msg['symbol']
        price = msg['price']
        self.prices[symbol] = price

    def get_price(self, symbol):
        return self.prices.get(symbol, None)


# Context
class PriceSource:
    def __init__(self, source: PriceSourceStrategy):
        self._source = source

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source: PriceSourceStrategy):
        self._source = source

    def get_price(self, symbol):
        return self._source.get_price(symbol)
    

price_source = PriceSource(YLiveTickerPriceSource(price_list))

# Use the PriceSource to get prices
btc_price = price_source.get_price("BTC-USD")
eth_price = price_source.get_price("ETH-USD")