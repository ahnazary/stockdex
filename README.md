<!-- [![Publish Python Package to PyPI](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml/badge.svg)](https://github.com/ahnazary/stockdex/actions/workflows/publish-package.yaml) -->
[![PyPI version](https://badge.fury.io/py/stockdex.svg)](https://badge.fury.io/py/stockdex)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![Code style: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)
![flake8](https://img.shields.io/badge/flake8-checked-blue)
![ruff](https://img.shields.io/badge/ruff-checked-brightgreen)

<p align="center">
  <img src="docs/images/stockdex_logo.png" alt="Stockdex logo with three ascending candlesticks" width="300" height="300">
</p>

Full documentation: [ahnazary.github.io/stockdex](https://ahnazary.github.io/stockdex/)

# Stock Data Extractor (Stockdex)

Stockdex is a Python package that provides a simple interface to get financial data from various sources in pandas DataFrames and Plotly figures.

<br />


## Advantages of `Stockdex` over similar packages

- **Various data sources**: `Stockdex` provides data from Yahoo Finance and other sources like Digrin, Finviz, Macrotrends and JustETF (for EU ETFs).

- **Historical data**: `Stockdex` provides a wide time range of data, e.g. Digrin and Macrotrends sources provide historical data in a span of years.

- **Numerous data categories**: `Stockdex` provides financials criteria including financial statements, earnings, dividends, stock splits, list of key executives, major shareholders and more.

- **Plotting**: `Stockdex` plots financial data as bar, line and Sankey charts, and multiple plots can be combined in a Dash app.

<br />

## Installation

Install the package using pip:

```bash
pip install stockdex -U
```

A quick check that the package works:

```python
from stockdex import Ticker

ticker = Ticker(ticker="NVDA")
result = ticker.yahoo_api_income_statement(frequency='quarterly')
```

## Use with Claude

Stockdex ships a local, read-only MCP server so Claude can fetch prices, financial statements and dividends for you.

- **Claude Desktop**: download `stockdex.mcpb` from the [latest release](https://github.com/ahnazary/stockdex/releases/latest) and double-click it.
- **Claude Code**: install the plugin, which requires [uv](https://docs.astral.sh/uv/):

  ```text
  /plugin marketplace add ahnazary/stockdex
  /plugin install stockdex@stockdex
  ```

- **Other MCP clients**: run `uvx --from "stockdex[mcp]" stockdex-mcp`.

See [Use with Claude](https://ahnazary.github.io/stockdex/claude.html) for arguments, limits and output format.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Stockdex is an open-source project, and contributions of **any kind** are welcome and appreciated!  
Whether you want to report a bug, suggest a new feature, improve documentation, or submit code via **Pull Requests** or **Issues** — every contribution helps.

## Guidelines

There are no Guidelines as of now :)

---

<p align="center">
  ❤️ <b>Thank you in advance for your contribution!</b> ❤️
</p>