# Yahoo Finance (Website)



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

