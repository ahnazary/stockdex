<!-- [![Publish Python Package to PyPI](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml/badge.svg)](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml) -->
[![PyPI version](https://badge.fury.io/py/stockdex.svg)](https://badge.fury.io/py/stockdex)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Code style: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)
![flake8](https://img.shields.io/badge/flake8-checked-blue)
![ruff](https://img.shields.io/badge/ruff-checked-brightgreen)

<!-- <p align="center">
  <img src="docs/images/stockdex_logo.png" alt="Stockdex Logo" width="300" height="300" style="width: 300px; height: 300px; border-radius: 50%; object-fit: cover;">
</p> -->

For full documentation, visit [here](https://ahnazary.github.io/stockdex/)

# Stock Data Extractor (Stockdex)

Stockdex is a Python package that provides a simple interface to get financial data from various sources in pandas DataFrames and Plotly figures.

<br />


## Advantages of `Stockdex` over similar packages

- **Various data sources**: `Stockdex` provides data from Yahoo Finance and other sources like Digrin, Finviz, Macrotrends and JustETF (for EU ETFs).

- **Historical data**: `Stockdex` provides a wide time range of data, e.g. Digrin and Macrotrends sources provide historical data in a span of years.

- **Numerous data categories**: `Stockdex` provides financials criteria including financial statements, earnings, dividends, stock splits, list of key executives, major shareholders and more.

- <span style="font-size: 17px; font-weight: bold; animation: rainbow 1.8s infinite; background: linear-gradient(90deg, orange, green, blue, indigo, violet); background-size: 1300%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">**plotting capabilities (new feature)**</span>: `Stockdex` provides plotting financial data using bar, line, and sankey plots. Multiple plots can be combined in dash app.

<br />

## Installation

Install the package using pip:

```bash
pip install stockdex -U
```

do a simple test to verify the package is installed correctly:

```python
from stockdex import Ticker

ticker = Ticker(ticker="NVDA")
result = ticker.yahoo_api_income_statement(frequency='quarterly')
```

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Stockdex is an open-source project, and contributions of **any kind** are welcome and appreciated!  
Whether you want to report a bug, suggest a new feature, improve documentation, or submit code — every contribution helps.

### How to contribute

- **Issues**  
  Found a bug or have an idea for an improvement? Please open an issue on GitHub and describe it clearly.

- **Pull Requests (PRs)**  
  If you’d like to fix something directly, fork the repository and open a PR.  
  Please include a short description of the change and reference any related issues.

## Guidelines

There are no Guidelines as of now :)

---

<p align="center">
  ❤️ <b>Thank you in advance for your contribution!</b> ❤️
</p>