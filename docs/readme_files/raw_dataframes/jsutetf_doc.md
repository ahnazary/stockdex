# justETF

For EU ETFS, the `isin` and `security_type` should be passed to the `Ticker` object. The `isin` is the International Securities Identification Number of the ETF and the `security_type` should be set to `etf`.

```python
from stockdex import Ticker

etf = Ticker(isin="IE00B4L5Y983", security_type="etf")

etf_general_info = etf.justetf_general_info
etf_wkn = etf.justetf_wkn
etf_description = etf.justetf_description

# Price data and changes
etf_price = etf.justetf_price

# Basic data about the ETF
etf_basics = etf.justetf_basics

# Holdings of the ETF by company, country and sector
etf_holdings_companies = etf.justetf_holdings_companies
etf_holdings_countries = etf.justetf_holdings_countries
etf_holdings_sectors = etf.justetf_holdings_sectors
```