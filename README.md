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
pip install stockdex -U
``` 

# Supported Data Sources

As of now, the package supports the following data sources:

- Yahoo Finance API
- Yahoo Finance Website
- Digrin Website
- Macrotrends Website
- JustETF Website (for EU ETFs)

# Usage

To access main functions, use the `Ticker` class. Below is an example of how to create a `Ticker` object.
```python
from stockdex import Ticker

ticker = Ticker(ticker="AAPL")
```

Using the `Ticker` object, you can access financial data related to the stock in the form of a pandas DataFrame through ticker object's functions. each function is prefixed with the source of the data. For example functions with `yahoo_api_<function_name>` pattern are used to access data from Yahoo Finance API and functions with `yahoo_web_<function_name>` pattern are used to access data from Yahoo Finance website. Below are some examples of how to access data from different sources.

## Data from `Yahoo Finance` API (fast queries through Yahoo Finance API):
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


## Data from `Yahoo Finance` website (web scraping):
```python
from stockdex import Ticker

ticker = Ticker(ticker="AAPL")

# Summary including general financial information
summary = ticker.yahoo_web_summary

# Financial data as it is seen in the yahoo finance website
income_stmt = ticker.yahoo_web_income_stmt
balance_sheet = ticker.yahoo_web_balance_sheet
cash_flow = ticker.yahoo_web_cashflow

# Analysts and estimates
analysis = ticker.yahoo_web_analysis

# Data about options
calls = ticker.yahoo_web_calls
puts = ticker.yahoo_web_puts

# Profile data 
key_executives = ticker.yahoo_web_key_executives
description = ticker.yahoo_web_description
corporate_governance = ticker.yahoo_web_corporate_governance

# Data about shareholders
major_holders = ticker.yahoo_web_major_holders
top_institutional_holders = ticker.yahoo_web_top_institutional_holders
top_mutual_fund_holders = ticker.yahoo_web_top_mutual_fund_holders

# Statistics
valuation_measures = ticker.yahoo_web_valuation_measures
financial_highlights = ticker.yahoo_web_financial_highlights
trading_information = ticker.yahoo_web_trading_information
```

<!-- ## NASDAQ data from `NASDAQ` website (web scraping):

Data on NASDAQ website gets updated more frequently than Yahoo Finance data. Below are some of the data that can be retrieved from the NASDAQ website.

```python
# Data about quarterly and yearly earnings, updated on the same day as the earnings release (yahoo finance data is updated after a few days)

quarterly_earnings_surprise = ticker.quarterly_earnings_surprise
yearly_earnings_forecast = ticker.yearly_earnings_forecast
quarterly_earnings_forecast = ticker.quarterly_earnings_forecast

price_to_earnings_ratio = ticker.price_to_earnings_ratio
forecast_price_to_earnings__growth_rates = ticker.forecast_peg_rate
``` -->

## Stocks data from `Digrin` (web scraping):

Data on Digrin website includes all historical data of the stock in certain categories, unlike Yahoo Finance which only provides the last 5 years of data at most.

```python
from stockdex import Ticker

ticker = Ticker(ticker="AAPL")

# Complete historical data of the stock in certain categories
dividend = ticker.digrin_dividend
payout_ratio = ticker.digrin_payout_ratio
stock_splits = ticker.digrin_stock_splits
price = ticker.digrin_price

# Non-historical data
assets_vs_liabilities = ticker.digrin_assets_vs_liabilities
free_cash_flow = ticker.digrin_free_cash_flow
net_income = ticker.digrin_net_income
cash_and_debt = ticker.digrin_cash_and_debt
shares_outstanding = ticker.digrin_shares_outstanding
expenses = ticker.digrin_expenses
cost_of_revenue = ticker.digrin_cost_of_revenue
upcoming_estimated_earnings = ticker.digrin_upcoming_estimated_earnings

# Dividend data
dividend = ticker.digrin_dividend
dgr3 = ticker.digrin_dgr3
dgr5 = ticker.digrin_dgr5
dgr10 = ticker.digrin_dgr10
```

## Stocks data from ``macrotrends`` (web scraping):

Data on Macrotrends website includes historical data in a span years. Below are some of the data that can be retrieved from the Macrotrends website.

```python
from stockdex import Ticker

ticker = Ticker(ticker="AAPL")

# Financial data
income_statement = ticker.macrotrends_income_statement
balance_sheet = ticker.macrotrends_balance_sheet
cash_flow = ticker.macrotrends_cash_flow
key_financial_ratios = ticker.macrotrends_key_financial_ratios

# Margins
gross_margin = ticker.macrotrends_gross_margin
operating_margin = ticker.macrotrends_operating_margin
ebitda_margin = ticker.macrotrends_ebitda_margin
pre_tax_margin = ticker.macrotrends_pre_tax_margin
net_margin = ticker.macrotrends_net_margin
```

## EU ETF data from `justETF` (web scraping):

For EU ETFS, the `isin` and `security_type` should be passed to the `Ticker` object. The `isin` is the International Securities Identification Number of the ETF and the `security_type` should be set to `etf`.

```python
from stockdex import Ticker

etf = Ticker(isin="IE00B4L5Y983", security_type="etf")

etf_general_info = etf.justetf_general_info
etf_wkn = etf.justetf_wkn
etf_description = etf.justetf_description

# Basic data about the ETF
etf_basics = etf.justetf_basics

# Holdings of the ETF by company, country and sector
etf_holdings_companies = etf.justetf_holdings_companies
etf_holdings_countries = etf.justetf_holdings_countries
etf_holdings_sectors = etf.justetf_holdings_sectors
```

<br />

---

Check out sphinx documentation [here](https://ahnazary.github.io/stockdex/) for more information about the package.