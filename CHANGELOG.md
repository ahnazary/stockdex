# Changelog

## Unreleased

### Added

- `yahoo_api_company_name`: the company's full name from the Yahoo Finance API.

### Deprecated

- All `yahoo_web_*` attributes. The Yahoo Finance website scraper has been removed because every dataset it returned is available from the Yahoo Finance API. The old names still work for now: each emits a `DeprecationWarning` and returns the data from its `yahoo_api_*` replacement, with the API's column layout. They will be removed in 2.0.

  | Deprecated | Replacement |
  |---|---|
  | `yahoo_web_income_stmt`, `yahoo_web_balance_sheet`, `yahoo_web_cashflow` | `yahoo_api_income_statement()`, `yahoo_api_balance_sheet()`, `yahoo_api_cash_flow()` |
  | `yahoo_web_calls`, `yahoo_web_puts` | `yahoo_api_options_chain(option_type="calls" / "puts")` |
  | `yahoo_web_description`, `yahoo_web_corporate_governance` | `yahoo_api_profile()` |
  | `yahoo_web_key_executives` | `yahoo_api_officers()` |
  | `yahoo_web_major_holders`, `yahoo_web_top_institutional_holders`, `yahoo_web_top_mutual_fund_holders` | `yahoo_api_major_holders()`, `yahoo_api_institutional_holders()`, `yahoo_api_fund_holders()` |
  | `yahoo_web_summary` | `yahoo_api_summary_detail()` |
  | `yahoo_web_valuation_measures` | `yahoo_api_valuation_measures()` |
  | `yahoo_web_financial_highlights`, `yahoo_web_trading_information` | `yahoo_api_financial_data()`, `yahoo_api_key_statistics()` |
  | `yahoo_web_earnings_estimate`, `yahoo_web_revenue_estimate`, `yahoo_web_eps_trend`, `yahoo_web_eps_revisions`, `yahoo_web_growth_estimates` | `yahoo_api_earnings_trend()` |
  | `yahoo_web_earnings_history` | `yahoo_api_earnings_history()` |
  | `yahoo_web_full_name` | `yahoo_api_company_name()` |

### Removed

- The `stockdex.yahoo_web_interface` module and the `YahooWeb` class.
- `"yahoo_web"` from `VALID_DATA_SOURCES` and the unused `YAHOO_WEB_BASE_URL` setting.
- The "Yahoo Finance (Website)" docs page.

### Changed

- Macrotrends looks up the company name through the Yahoo Finance API instead of scraping the Yahoo website.
- Docs: new landing page with install tabs and data-source cards, an API reference generated from the docstrings, a changelog page, a Finviz plots page, and the missing `justetf_price`, `justetf_holdings_countries`, `plot_dataframe` and `plot_finviz_*` entries. The justETF page URL is now `justetf_doc.html` (was `jsutetf_doc.html`).
- Docs are rebuilt and published on every merge to `main`, and checked on pull requests that touch them. Sphinx warnings now fail the build.

## 1.4.0

### Added

- Yahoo Finance API: `yahoo_api_dividends`, `yahoo_api_splits` and `yahoo_api_capital_gains` from the chart endpoint's corporate-action events.
- Yahoo Finance API: `yahoo_api_valuation_measures` with market cap, enterprise value, P/E, forward P/E, PEG, P/S, P/B and EV ratios over time (annual, quarterly or trailing).
- Yahoo Finance API: `yahoo_api_quote_summary(modules)` to fetch any quoteSummary module, plus methods built on it:
  - company and market data: `yahoo_api_profile`, `yahoo_api_officers`, `yahoo_api_market_price`, `yahoo_api_summary_detail`, `yahoo_api_key_statistics`, `yahoo_api_financial_data`, `yahoo_api_calendar_events`
  - analyst and earnings: `yahoo_api_earnings_history`, `yahoo_api_earnings_trend`, `yahoo_api_recommendation_trend`, `yahoo_api_upgrades_downgrades`
  - ownership and filings: `yahoo_api_institutional_holders`, `yahoo_api_fund_holders`, `yahoo_api_major_holders`, `yahoo_api_insider_holders`, `yahoo_api_insider_transactions`, `yahoo_api_insider_purchase_activity`, `yahoo_api_sec_filings`
  - ETFs and mutual funds: `yahoo_api_fund_top_holdings`, `yahoo_api_fund_sector_weightings`, `yahoo_api_fund_asset_allocation`, `yahoo_api_fund_profile`, `yahoo_api_fund_performance`
- Yahoo Finance API: `yahoo_api_option_expirations`, `yahoo_api_options_chain`, `yahoo_api_quotes` (many symbols in one request), `yahoo_api_search` and `yahoo_api_similar_symbols`.
- MCP tools for Claude (13 new, 16 in total): `search_ticker`, `get_quotes`, `get_key_statistics`, `get_valuation_history`, `get_company_profile`, `get_analyst_estimates`, `get_earnings_calendar`, `get_holders`, `get_sec_filings`, `get_splits`, `get_options_chain`, `get_fund_holdings` and `get_fund_profile`, built on the Yahoo Finance API methods above.
- `get_dividends` accepts `source="yahoo"` or `source="auto"` (Digrin with Yahoo Finance fallback). The default is still Digrin.

### Changed

- The Claude skill, plugin README, docs and Desktop extension description cover the new tools.

## 1.3.1

### Changed

- MCP tools now declare a `title` and full annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`), and their descriptions state exactly what each tool returns and where the data comes from. This follows Anthropic's Software Directory Policy.
- The Claude Code plugin moved to `plugins/stockdex/`, with its own README and LICENSE, and pins `stockdex[mcp]==1.3.1` exactly. The install commands stay the same.
- The Claude Desktop extension pins `stockdex[mcp]==1.3.1` and adds a privacy disclosure and example prompts to its description.

## 1.3.0

### Added

- Local read-only MCP server (`stockdex-mcp`, install with `pip install "stockdex[mcp]"`) with `get_prices`, `get_financial_statement` and `get_dividends` tools.
- JSON command-line tool `stockdex-claude` for the same operations.
- Claude Code plugin and marketplace (`/plugin marketplace add ahnazary/stockdex`).
- Claude Desktop extension `stockdex.mcpb`, attached to GitHub releases.

### Fixed

- `digrin_dividend` raises a clear `ValueError` when Digrin's page layout changes, instead of an `AttributeError`. Rows that don't match the table header are skipped.
- `pip install -e .` now works from a fresh clone without `__version__.py`.

### Changed

- Minimum Python version is now 3.9, matching the existing `pandas>=2.2.3` requirement.

## 1.2.7

### Fixed

- Fixed `yahoo_api_financials` (and related income statement, balance sheet, cash flow methods) dropping recent years' data (2024, 2025) due to using the last column's date index when constructing the DataFrame.

## 1.2.6

### Fixed

- `yahoo_web_balance_sheet`, `yahoo_web_cashflow`, and `yahoo_web_income_stmt` now return **all rows** including expandable/hidden rows from Yahoo Finance by fetching data via the Yahoo timeseries API instead of only scraping the visible HTML rows.

## 1.0.8

### Added

- Added `macrotrends_revenue` method to fetch quarterly and annual revenue data from `macrotrends` website.

## 1.0.5

### Fixed

- Fixed bug with selenium driver path. 

## 1.0.4

### Added

- Added `justetf_price` method to fetch price data from `justetf` website.
- fix bugs in `yahoo_web` module.

## 1.0.2

### Added

- Added `ruff`as link to the project. 

### Fixed

- Fix path to chrome driver in selenium module.
- Fix yahoo web financials, balance sheet, and cash flow data.

### Changed

## 1.0.0

### Added

- Added `plotly` and `dash` modules to plot financial data and create dash app.

### Fixed

### Changed

## 0.7.0

### Added

- Added following properties to yahoo web module:
    - `yahoo_web_earnings_estimate` 
    - `yahoo_web_revenue_estimate`
    - `yahoo_web_earnings_history`
    - `yahoo_web_eps_trend`
    - `yahoo_web_eps_revisions`
    - `yahoo_web_growth_estimates`

### Fixed

### Changed


## 0.6.0

### Added

- Module for `´macrotrends` website to fetch data.
- methods for extracting basic and margin related data from `macrotrends` website.

### Fixed

### Changed

- Some log messages are changed.
- `TickerFactory` class is removed and `Ticker` class is used to create `Ticker` objects.

- `Ticker` class now is the main calss and `TickerFactory` class is removed.

## 0.5.0

### Added

-- `data_source` in the `TickerFactory` class to specify the source of the data.
-- `WrongSecurityType` exception class to raise an exception when the security type is not valid.

### Fixed

- Bug with `isin` field in all classes.

### Changed

- Removed `nasdaq` module as the website keeps changing its structure.
- Instead of `Ticker` class, `TickerFactory` class is used to create `Ticker` objects.

## 0.4.0

### Added

- More methods for fetching data from `NASDAQ` website.
- More methods for fetching data from `JustETF` website.
- Separate module for yahoo finance web related functions.

### Fixed

- Bug with `security_type` field in all classes.

### Changed

- `Ticker` class now accepts `isin` and `security_type` as arguments.
