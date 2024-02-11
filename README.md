[![Publish Python Package to PyPI](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml/badge.svg)](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml)
[![PyPI version](https://badge.fury.io/py/stockdex.svg)](https://badge.fury.io/py/stockdex)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Code style: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)


# Stockdex

Stockdex is a Python package that provides a simple interface to access financial data from Yahoo Finance. Data is returned as a pandas DataFrame.

# Installation 

Install the package using pip:

```bash
pip install stockdex
``` 

# Usage

```python
from stockdex import Ticker

# Pick arbitrary ticker
ticker = Ticker('AAPL')

summary = ticker.summary
statistics = ticker.statistics
income_stmt = ticker.income_stmt
balance_sheet = ticker.balance_sheet
cash_flow = ticker.cash_flow
analysis = ticker.analysis

# Options
calls = ticker.calls
puts = ticker.puts
```
