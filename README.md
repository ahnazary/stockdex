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

## price data:
Pass the range and interval (by default, range is '1d' and interval is '1m') to get a dataframe of the stock's historical price data including open, high, low, close, and volume on each timestamp.

```python
price = ticker.price(range='1y', dataGranularity='1d')
```

## Trading periods:
Get the current trading period of the stock (pre-market, regular, post-market).
```python
current_trading_period = ticker.current_trading_period
```

## Fundamental data:
```python
# Summary including general financial information
summary = ticker.summary

# Financial data
income_stmt = ticker.income_stmt 
balance_sheet = ticker.balance_sheet
cash_flow = ticker.cash_flow

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

History of dividends paid by the company.

```python
dividend = ticker.dividend
```

<br />

---

Check out sphinx documentation [here](https://ahnazary.github.io/stockdex/) for more information about the package.