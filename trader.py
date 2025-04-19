import os
from datetime import datetime
from lumibot.strategies.strategy import Strategy
from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.traders import Trader
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
BASE_URL = os.getenv('BASE_URL')

ALPACA_CRED = {"API_KEY":API_KEY,
               "API_SECRET": API_SECRET,
               "PAPER": True}

class MYTrader(Strategy):
    def initialize(self, symbol:str = 'SPY'):
        self.symbol = symbol
        self.sleeptime = "12H"
        self.last_trade = None
    def on_trading_iteration(self):
        order = self.create_order(
            asset=self.symbol,
            quantity=10,
            side="buy",
            order_type="market"
        )
        self.submit_order(order)
        self.last_trade = "buy"

start_date = datetime(2024,1,1)
end_date = datetime(2024,1,15)
broker = Alpaca(ALPACA_CRED)
strategy = MYTrader(name = 'mybot', broker=broker, parameters={"symbol": 'SPY'})
strategy.backtest(YahooDataBacktesting,
                  start_date,
                  end_date,
                  parameters={"symbol": 'SPY'})