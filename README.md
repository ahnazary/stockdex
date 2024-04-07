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

Create `Ticker` object by passing the ticker symbol. Ticker objects are the main interface to retrieve stock data.

```python
from stockdex import Ticker

# Pick arbitrary ticker
ticker = Ticker('AAPL')
```

## Fundamental data from `Yahoo Finance` API (fast queries through Yahoo Finance API):
```python

# Price data (use range and dataGranularity to make range and granularity more specific)
price = ticker.price(range='1y', dataGranularity='1d')

# Current trading period of the stock (pre-market, regular, post-market trading periods)
current_trading_period = ticker.current_trading_period

# Fundamental data (use frequency, format, period1 and period2 to fine-tune the returned data)
income_statement = ticker.income_statement(frequency='quarterly')
cash_flow = ticker.cash_flow(format='raw')
balance_sheet = ticker.balance_sheet(period1=datetime(2020, 1, 1))
financials = ticker.financials(period1=datetime(2022, 1, 1), period2=datetime.today())
```


## Fundamental data with criteria from `Yahoo Finance` website (web scraping):
```python
# Summary including general financial information
summary = ticker.summary

# Financial data as it is seen in the yahoo finance website
income_stmt = ticker.income_stmt 
balance_sheet = ticker.balance_sheet_web
cash_flow = ticker.cashflow_web

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

## ETF data from justETF website:
```python

# build the ETF object, make sure to pass the ETF ISIN and use security_type to "etf"
etf = Ticker(isin='IE00B4L5Y983', security_type='etf')

etf_general_info = etf.etf_general_info
etf_wkn = etf.etf_wkn
etf_description = etf.etf_description

# Basic data about the ETF
etf_basics = etf.etf_basics

# Holdings of the ETF by company, country and sector
etf_holdings_companies = etf.etf_holdings_companies
etf_holdings_countries = etf.etf_holdings_countries
etf_holdings_sectors = etf.etf_holdings_sectors
```


## Historical dividends data

All dividends paid by the company returned as a pandas DataFrame.

```python
dividend = ticker.dividend
```

<br />

---

Check out sphinx documentation [here](https://ahnazary.github.io/stockdex/) for more information about the package.