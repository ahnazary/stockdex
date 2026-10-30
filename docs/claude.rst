Use with Claude
===============

Stockdex includes a local, read-only `Model Context Protocol
<https://modelcontextprotocol.io>`_ (MCP) server, so Claude can look up stock
data for you. It provides 16 read-only tools:

* ``search_ticker``: find ticker symbols for a company name
* ``get_quotes``: current quotes for up to 20 symbols
* ``get_prices``: daily open, high, low, close and volume, up to 1 year
* ``get_financial_statement``: annual or quarterly income statement, cash flow or balance sheet, up to 5 years
* ``get_key_statistics``: market cap, P/E, beta, 52-week range, margins and analyst price targets
* ``get_valuation_history``: market cap, enterprise value and valuation ratios over time
* ``get_company_profile``: business summary, sector, executives and related tickers
* ``get_analyst_estimates``: EPS and revenue estimates, recommendations, rating changes and EPS surprises
* ``get_earnings_calendar``: next earnings date, estimates and dividend dates
* ``get_holders``: institutional and fund holders, ownership breakdown and insider transactions
* ``get_sec_filings``: recent SEC filings with links
* ``get_dividends``: dividend history (Digrin by default, Yahoo Finance as an alternative or fallback)
* ``get_splits``: stock split history
* ``get_options_chain``: calls and puts for one expiration date
* ``get_fund_holdings``: ETF and fund top holdings, sector weights and asset allocation
* ``get_fund_profile``: ETF and fund fees, category and performance vs category

All data comes from Yahoo Finance, except dividends, which come from
Digrin by default.

The server runs on your computer and needs no API key. Requests go to Yahoo
Finance and Digrin, and results you use in a conversation are sent to Claude.

Claude Desktop (one click)
--------------------------

1. Download ``stockdex.mcpb`` from the latest
   `GitHub release <https://github.com/ahnazary/stockdex/releases/latest>`_.
2. Double-click the file, or drag it into **Settings → Extensions** in Claude
   Desktop, and click **Install**.

Claude Desktop installs Python and the dependencies itself. You don't need a
terminal.

Claude Code (plugin)
--------------------

The plugin adds the MCP server and a skill that tells Claude when and how to
use it. It requires `uv <https://docs.astral.sh/uv/>`_.

.. code-block:: text

   /plugin marketplace add ahnazary/stockdex
   /plugin install stockdex@stockdex

Then ask, for example, *"How have Apple's revenue and net income changed over
the last five years?"*

Other MCP clients
-----------------

Any MCP client that can start a stdio server can run it with ``uvx``:

.. code-block:: json

   {
     "mcpServers": {
       "stockdex": {
         "command": "uvx",
         "args": ["--from", "stockdex[mcp]", "stockdex-mcp"]
       }
     }
   }

If you'd rather use pip, run ``pip install "stockdex[mcp]"`` and set
``command`` to ``stockdex-mcp``.

Command line
------------

The same operations are also available as a JSON command-line tool:

.. code-block:: sh

   pip install stockdex
   stockdex-claude prices AAPL --range 3mo --limit 5
   stockdex-claude financial-statement AAPL --statement cash_flow --frequency quarterly
   stockdex-claude dividends KO

Arguments and limits
--------------------

* **Tickers** use Yahoo symbols, e.g. ``AAPL``, ``BRK-B``, ``BMW.DE``,
  ``^GSPC`` or ``GC=F``.
* **limit** sets how many rows come back (1–500, default 20, newest first).
  Output is also capped at 256 KiB.
* **Datasets**: tools such as ``get_key_statistics`` and ``get_holders``
  take a ``dataset`` argument that selects one view; each tool lists its
  allowed values and default.
* **Dividends** use ``source`` ``digrin`` (default), ``yahoo`` or ``auto``
  (Digrin, falling back to Yahoo Finance).
* **Prices** use ``range`` ``1mo`` (default), ``3mo``, ``6mo`` or ``1y`` at a
  daily interval. These are historical bars, not real-time quotes.
* **Financial statements**:

  * ``statement`` is ``income_statement`` (default), ``cash_flow`` or
    ``balance_sheet``.
  * ``frequency`` is ``annual`` (default) or ``quarterly``.
  * ``start_date`` and ``end_date`` are ``YYYY-MM-DD``. The window can be at
    most five years, and the end date is exclusive.
  * ``metrics`` takes up to 20 names from ``stockdex/config.py``, without a
    prefix, e.g. ``TotalRevenue``. Output columns have an ``annual`` or
    ``quarterly`` prefix.

Reading results
---------------

Every call returns a JSON envelope. Check ``ok`` first, then use
``records`` and ``columns``. The envelope also includes ``source``,
``retrieved_at``, ``warnings`` and ``truncated``. When a call fails,
``error.code`` is one of:

* ``invalid_input``: an argument is out of range or malformed.
* ``busy``: another request is still running.
* ``rate_limited``: the provider asked to slow down.
* ``provider_blocked``: the website refused the request, usually because of
  bot protection. Try another ``source`` or try later.
* ``layout_changed``: a scraped page no longer has the expected structure.
  This says nothing about the value itself.
* ``network_error``, ``no_data``, ``provider_schema_error`` or
  ``provider_error``.

* Statement values are raw provider numbers with **unknown currency and units**.
* ``null`` means the value is missing, not zero.
* Fractions are not percentages: a yield or margin of ``0.031`` is 3.1%.
* Only one provider request runs at a time. Respect provider rate limits and
  terms of use.
* The data isn't guaranteed to be accurate and is not investment advice.
