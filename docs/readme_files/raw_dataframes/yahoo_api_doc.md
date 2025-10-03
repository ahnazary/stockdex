# Yahoo Finance (API)

## Raw data:

Following functions will return the data extracted from Yahoo Finance API in the form of a pandas DataFrame:

```python
from stockdex import Ticker
from datetime import datetime

ticker = Ticker(ticker="AAPL")

# Price data (use range and dataGranularity to make range and granularity more specific)
price = ticker.yahoo_api_price(range='1y', dataGranularity='1d')

# Current trading period of the stock (pre-market, regular, post-market trading periods)
current_trading_period = ticker.yahoo_api_current_trading_period

# Fundamental data (use frequency, format, period1 and period2 to fine-tune the returned data)
income_statement = ticker.yahoo_api_income_statement(frequency='quarterly')
cash_flow = ticker.yahoo_api_cash_flow(format='raw')
balance_sheet = ticker.yahoo_api_balance_sheet(period1=datetime(2020, 1, 1))
financials = ticker.yahoo_api_financials(period1=datetime(2022, 1, 1), period2=datetime.today())
```

## Plotting data:

Following functions will plot the data extracted from Yahoo Finance API using the `plotly` library:

```python

from stockdex import Ticker

ticker = Ticker(ticker="MSFT")

ticker.plot_yahoo_api_financials(group_by="field")
ticker.plot_yahoo_api_income_statement(group_by="timeframe")
ticker.plot_yahoo_api_cash_flow(freq="quarterly")
ticker.plot_yahoo_api_balance_sheet(freq="quarterly")
``` 

Running each function will open a tab in default browser showing the plot like below:

![MSFT Yahoo Finance Financials Annual](../../images/msft_financials_annual.png)
