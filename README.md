[![Publish Python Package to PyPI](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml/badge.svg)](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml)
[![PyPI version](https://badge.fury.io/py/stockdex.svg)](https://badge.fury.io/py/stockdex)

![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Code style: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)
![flake8](https://img.shields.io/badge/flake8-checked-blue)

[![Documentation Status](https://readthedocs.org/projects/stockdex/badge/?version=latest)](https://ahnazary.github.io/stockdex/)

<p align="center">
  <img src="docs/images/stockdex_logo.png" alt="Stockdex Logo" width="300" height="300" style="width: 300px; height: 300px; border-radius: 50%; object-fit: cover;">
</p>


# Stockdex

Stockdex is a Python package that provides a simple interface to access financial data from various soruces and plotting capabilities using Plotly.

<br />


# Advantages of `Stockdex` over similar packages

- **Various data sources**: `Stockdex` provides data from Yahoo Finance API and website, Digrin, Macrotrends, and JustETF (for EU ETFs).

- **Numerous data categories**: `Stockdex` provides various data including financial statements, earnings, dividends, stock splits, list of key executives, major shareholders, and many more.

- **Historical data**: `Stockdex` provides a wide time range of data, e.g. Digrin and Macrotrends sources, which provide data ranging from 4 years to historical data.

- <span style="font-size: 17px; font-weight: bold; animation: rainbow 1.8s infinite; background: linear-gradient(90deg, orange, green, blue, indigo, violet); background-size: 1300%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">plotting capabilities (new feature)</span>: `Stockdex` provides plotting financial data using bar, line, and sanky plots. Multiple plots can be combined in dash app.

<!-- <style>
@keyframes rainbow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
</style> -->

<br />

# Installation 

Install the package using pip:

```bash
pip install stockdex -U
``` 
<br />

# Usage

For detailed info about usage of the package and its functions including plotting and dash app, check out the [this part of the readme](./stockdex/USAGE.md).

In general, to access main functions, The `Ticker` object should be created with the ticker of the stock as an argument. An example of creating a `Ticker` object is shown below:

```python
from stockdex import Ticker

ticker = Ticker(ticker="AAPL")
```

## Data from `Yahoo Finance`, `Digrin`, and `Macrotrends`:

The `Ticker` object provides data from Yahoo Finance API and website, Digrin, and Macrotrends. Below are some of the data that can be retrieved from these sources (more detailed info with output can be found [here](./stockdex/USAGE.md)).

### Raw data:
```python
from stockdex import Ticker
from datetime import datetime

ticker = Ticker(ticker="AAPL")

# Price data (use range and dataGranularity to make range and granularity more specific) from Yahoo Finance API
price = ticker.yahoo_api_price(range='1y', dataGranularity='1d')

# plot financial data using Plotly
ticker = Ticker(ticker="MSFT")
ticker.plot_yahoo_api_financials(group_by="field")

# Summary including general financial information from Yahoo Finance website
summary = ticker.yahoo_web_summary#

# Complete historical data of the stock in certain categories from digrin website
dividend = ticker.digrin_dividend


# Financial data from macrotrends website
income_statement = ticker.macrotrends_income_statement
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

## EU ETF data from `justETF` (web scraping):

For EU ETFS, the `isin` and `security_type` should be passed to the `Ticker` object. The `isin` is the International Securities Identification Number of the ETF and the `security_type` should be set to `etf`.

```python
from stockdex import Ticker

etf = Ticker(isin="IE00B4L5Y983", security_type="etf")

etf_general_info = etf.justetf_general_info
```
<br />

---

Check out sphinx documentation [here](https://ahnazary.github.io/stockdex/) for more information about the package.