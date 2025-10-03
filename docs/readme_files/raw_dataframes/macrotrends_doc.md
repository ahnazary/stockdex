# macrotrends

Data on Macrotrends website includes historical data in a span years. Below are some of the data that can be retrieved from the Macrotrends website.

## Raw data:

Following functions will return the data extracted from Macrotrends website in the form of a pandas DataFrame:

```python
from stockdex import Ticker

ticker = Ticker(ticker="AAPL")

# Financial data
income_statement = ticker.macrotrends_income_statement(frequency="quarterly")
balance_sheet = ticker.macrotrends_balance_sheet(frequency="quarterly")
cash_flow = ticker.macrotrends_cash_flow(frequency="annual")
key_financial_ratios = ticker.macrotrends_key_financial_ratios

# Margins
gross_margin = ticker.macrotrends_gross_margin
operating_margin = ticker.macrotrends_operating_margin
ebitda_margin = ticker.macrotrends_ebitda_margin
pre_tax_margin = ticker.macrotrends_pre_tax_margin
net_margin = ticker.macrotrends_net_margin
```

## Plotting data:

Following functions will plot the data extracted from Macrotrends website using the `plotly` library:

```python

from stockdex import Ticker

ticker = Ticker(ticker="GOOGL")

ticker.plot_macrotrends_income_statement()
ticker.plot_macrotrends_balance_sheet()
ticker.plot_macrotrends_cash_flow()

```

Running each function will open a tab in default browser showing the plot. Below the output for `ticker.plot_macrotrends_income_statement()` is illustrated for `GOOGL` stock:

![Income Statement for GOOGL stock](../../images/plot_macrotrends_income_statement_googl.png)
