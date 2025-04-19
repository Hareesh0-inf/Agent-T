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
    def initialize(self, symbol:str = 'SPY', cash_at_risk:float = .5):
        self.symbol = symbol
        self.sleeptime = "12H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        order = self.create_order(
            asset=self.symbol,
            quantity=quantity,
            side="buy",
            order_type="bracket",
            take_profit_price=last_price * 1.15,
            stop_loss_price=last_price * 0.95
        )
        self.submit_order(order)
        self.last_trade = "buy"

start_date = datetime(2024,1,1)
end_date = datetime(2024,1,15)
broker = Alpaca(ALPACA_CRED)
strategy = MYTrader(name = 'mybot', broker=broker, parameters={"symbol": 'SPY', "cash_at_risk": 0.5})
strategy.backtest(YahooDataBacktesting,
                  start_date,
                  end_date,
                  parameters={"symbol": 'SPY', "cash_at_risk": 0.5})