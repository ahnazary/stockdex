# Stockdex plugin for Claude

Read-only public stock market data for Claude, powered by the
[Stockdex](https://github.com/ahnazary/stockdex) Python package. The plugin adds
a local MCP server with 16 read-only tools and a skill that tells Claude
when to use them.

| Tool | What it returns | Source |
|---|---|---|
| `search_ticker` | Find ticker symbols for a company name | Yahoo Finance |
| `get_quotes` | Current quotes for up to 20 symbols | Yahoo Finance |
| `get_prices` | Daily open, high, low, close and volume, up to 1 year | Yahoo Finance |
| `get_financial_statement` | Annual or quarterly income statement, cash flow or balance sheet, up to 5 years | Yahoo Finance |
| `get_key_statistics` | Market cap, P/E, beta, 52-week range, margins and analyst price targets | Yahoo Finance |
| `get_valuation_history` | Market cap, enterprise value and valuation ratios over time | Yahoo Finance |
| `get_company_profile` | Business summary, sector, executives and related tickers | Yahoo Finance |
| `get_analyst_estimates` | EPS and revenue estimates, recommendations, rating changes and EPS surprises | Yahoo Finance |
| `get_earnings_calendar` | Next earnings date, estimates and dividend dates | Yahoo Finance |
| `get_holders` | Institutional and fund holders, ownership breakdown and insider transactions | Yahoo Finance |
| `get_sec_filings` | Recent SEC filings with links | Yahoo Finance |
| `get_dividends` | Dividend history (Digrin by default, Yahoo Finance as an alternative or fallback) | Digrin / Yahoo Finance |
| `get_splits` | Stock split history | Yahoo Finance |
| `get_options_chain` | Calls and puts for one expiration date | Yahoo Finance |
| `get_fund_holdings` | ETF and fund top holdings, sector weights and asset allocation | Yahoo Finance |
| `get_fund_profile` | ETF and fund fees, category and performance vs category | Yahoo Finance |

## Install

Requires [uv](https://docs.astral.sh/uv/). In Claude Code:

```text
/plugin marketplace add ahnazary/stockdex
/plugin install stockdex@stockdex
```

## Example prompts

- "How has Microsoft's stock price moved over the last 6 months?"
- "Show Apple's annual revenue, net income and EPS for the last five years."
- "Compare NVIDIA's quarterly free cash flow over the last two years."
- "What dividends has Coca-Cola (KO) paid recently?"
- "Who are the largest institutional holders of Tesla, and have insiders been selling?"
- "What do analysts expect for Apple's next quarter, and when does it report?"
- "Compare the expense ratio and top holdings of SPY and VOO."

## What the plugin runs, sends and stores

- **Runs:** the MCP server starts locally with
  `uvx --from "stockdex[mcp]==1.4.0" stockdex-mcp`, which installs the pinned
  Stockdex release from PyPI.
- **Sends:** only ticker symbols, search text and request parameters (date
  range, statement type, metric names, dataset, row limit) to Yahoo Finance
  (`finance.yahoo.com`, `query1.finance.yahoo.com`, `fc.yahoo.com`) and Digrin
  (`www.digrin.com`). No account, API key, personal data or conversation
  content is sent.
- **Stores:** nothing. There is no telemetry, logging of requests, or local
  cache beyond the process lifetime.

Provider privacy policies:
[Yahoo](https://legal.yahoo.com/us/en/yahoo/privacy/index.html),
[Digrin](https://www.digrin.com/privacy-policy).

## Troubleshooting

- **Tools don't appear:** check that `uvx` is on your `PATH` (`which uvx`) and
  restart Claude Code.
- **`rate_limited` or `provider_error`:** the provider throttled or blocked the
  request. Wait a few minutes before trying again.
- **`no_data`:** the provider returned nothing for that ticker or period. This
  does not mean the value is zero.

Full documentation: <https://ahnazary.github.io/stockdex/claude.html>.
Report issues: <https://github.com/ahnazary/stockdex/issues>.

Stockdex is not investment advice. Data comes from third-party providers and
may be delayed, incomplete or unavailable.
