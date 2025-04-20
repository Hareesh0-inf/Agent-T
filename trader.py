import os
from datetime import datetime
from timedelta import Timedelta
from lumibot.strategies.strategy import Strategy
from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.traders import Trader
from dotenv import load_dotenv
from alpaca_trade_api import REST
from sentiment import estimate_sentiment


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
        self.api = REST(key_id=API_KEY, secret_key=API_SECRET, base_url=BASE_URL)
        self.sleeptime = "12H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk

    def get_dates(self):
        today = self.get_datetime()
        four_days_prior = today - Timedelta(days=4)
        return today.strftime("%Y-%m-%d"), four_days_prior.strftime("%Y-%m-%d")
    
    def get_sentiment(self):
        end, start = self.get_dates()
        response = self.api.get_news(symbol=self.symbol, start=start, end=end);
        news = [ev.__dict__["_raw"]["headline"] for ev in response]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()
        if cash > last_price:
            if probability > 0.98 and sentiment == "positive":
                if self.last_trade == "sell":
                    self.sell_all()
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
            if probability > 0.98 and sentiment == "negative":
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    asset=self.symbol,
                    quantity=quantity,
                    side="sell",
                    order_type="bracket",
                    take_profit_price=last_price * 0.8,
                    stop_loss_price=last_price * 1.05
                )
                self.submit_order(order)
                self.last_trade = "sell"

start_date = datetime(2024,1,1)
end_date = datetime(2024,1,15)
broker = Alpaca(ALPACA_CRED)
strategy = MYTrader(name = 'mybot', broker=broker, parameters={"symbol": 'SPY', "cash_at_risk": 0.5})
strategy.backtest(YahooDataBacktesting,
                  start_date,
                  end_date,
                  parameters={"symbol": 'SPY', "cash_at_risk": 0.5})