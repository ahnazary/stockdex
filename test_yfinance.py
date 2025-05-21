# import yfinance as yf

# spy = yf.Ticker('SPY').funds_data

# print(spy.description)
# print(spy.top_holdings)

from stockdex import Ticker

ticker = Ticker(ticker="AAPL")
price = ticker.yahoo_api_price(range="1d", dataGranularity="1d")
