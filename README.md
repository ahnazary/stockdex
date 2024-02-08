# Stockdex

Stockdex is a Python package that provides a simple interface to access financial data from Yahoo Finance.

# Installation 

Install the package using pip:

```bash
pip install stockdex
``` 

# Usage

```python
from stockdex import Ticker

ticker = Ticker('AAPL')

summary = ticker.summary()
statistics = ticker.statistics()
income_stmt = ticker.income_stmt()
balance_sheet = ticker.balance_sheet()
cash_flow = ticker.cash_flow()
analysis = ticker.analysis()
```
