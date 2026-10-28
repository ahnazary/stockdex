# Stockdex plugin for Claude

Read-only public stock market data for Claude, powered by the
[Stockdex](https://github.com/ahnazary/stockdex) Python package. The plugin adds
a local MCP server with three tools and a skill that tells Claude when to use
them.

| Tool | What it returns | Source |
|---|---|---|
| `get_prices` | Daily open, high, low, close and volume for one ticker, up to 1 year | Yahoo Finance |
| `get_financial_statement` | Annual or quarterly income statement, cash flow or balance sheet figures, up to 5 years | Yahoo Finance |
| `get_dividends` | Ex-dividend date, payable date, amount and currency | Digrin |

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

## What the plugin runs, sends and stores

- **Runs:** the MCP server starts locally with
  `uvx --from "stockdex[mcp]==1.3.1" stockdex-mcp`, which installs the pinned
  Stockdex release from PyPI.
- **Sends:** only the ticker symbol and request parameters (date range,
  statement type, metric names, row limit) to Yahoo Finance
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
