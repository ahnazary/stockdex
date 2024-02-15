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

Create a `Ticker` object by passing the ticker symbol of the stock you want to access. Then, you can access the following data:

```python
from stockdex import Ticker

# Pick arbitrary ticker
ticker = Ticker('AAPL')
```

## Summary data:
```python
summary = ticker.summary
```

## Historical data:
```python
statistics = ticker.statistics
```

## Financial data:
```python
income_stmt = ticker.income_stmt
balance_sheet = ticker.balance_sheet
cash_flow = ticker.cash_flow
```

## Analyst data:
```python
analysis = ticker.analysis
```

## Option data:
```python
calls = ticker.calls
puts = ticker.puts
```

## Profile data:
```python
key_executives = ticker.key_executives
description = ticker.description
corporate_governance = ticker.corporate_governance
```
