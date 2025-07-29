import yfinance as yf

spy = yf.Ticker("SPY").funds_data
print(spy.description)
