[![Publish Python Package to PyPI](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml/badge.svg)](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml)
[![PyPI version](https://badge.fury.io/py/stockdex.svg)](https://badge.fury.io/py/stockdex)

![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Code style: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)
![flake8](https://img.shields.io/badge/flake8-checked-blue)

[![Documentation Status](https://readthedocs.org/projects/stockdex/badge/?version=latest)](https://ahnazary.github.io/stockdex/)

# Stockdex

Stockdex is a Python package that provides a simple interface to access financial data from Yahoo Finance. Data is returned as a pandas DataFrame.

# Installation 

Install the package using pip:

```bash
pip install stockdex
``` 

# Usage

Create a `Ticker` object by passing the ticker symbol. Ticker objects are the main interface to retrieve stock data.

```python
from stockdex import Ticker

# Pick arbitrary ticker
ticker = Ticker('AAPL')
```

## Fundamental data from `Yahoo Finance` API (fast queries):
```python

# Price data
price = ticker.price(range='1y', dataGranularity='1d')

# Current trading period of the stock (pre-market, regular, post-market)
current_trading_period = ticker.current_trading_period

income_statement = ticker.income_statement()
cash_flow = ticker.cash_flow()
balance_sheet = ticker.balance_sheet()
financials = ticker.financials()
```


## Fundamental data that is seen in the `Yahoo Finance` website:
```python
# Summary including general financial information
summary = ticker.summary

# Financial data as it is seen in the yahoo finance website
income_stmt = ticker.income_stmt 
balance_sheet = ticker.balance_sheet_web
cash_flow = ticker.cash_flow_web

# Analysts and estimates
analysis = ticker.analysis

# Data about options
calls = ticker.calls
puts = ticker.puts

# Profile data 
key_executives = ticker.key_executives
description = ticker.description
corporate_governance = ticker.corporate_governance

# Data about shareholders
major_holders = ticker.major_holders
top_institutional_holders = ticker.top_institutional_holders
top_mutual_fund_holders = ticker.top_mutual_fund_holders

# Main statistics
statistics = ticker.statistics 
```

## Dividends data from `Digrin` Webstite:

All dividends paid by the company are returned as a pandas DataFrame. 

```python
dividend = ticker.dividend
```

<br />

---

Check out sphinx documentation [here](https://ahnazary.github.io/stockdex/) for more information about the package.