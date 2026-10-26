Use with Claude
===============

Stockdex includes a local, read-only `Model Context Protocol
<https://modelcontextprotocol.io>`_ (MCP) server, so Claude can look up stock
data for you. It provides three tools:

* ``get_prices``: historical daily OHLCV bars from Yahoo Finance
* ``get_financial_statement``: income statement, cash flow and balance sheet
  metrics from Yahoo Finance
* ``get_dividends``: dividend history from Digrin

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
``error.code`` is one of ``invalid_input``, ``busy``, ``rate_limited``,
``network_error``, ``no_data``, ``provider_schema_error`` or
``provider_error``.

* Statement values are raw provider numbers with **unknown currency and units**.
* ``null`` means the value is missing, not zero.
* Only one provider request runs at a time. Respect provider rate limits and
  terms of use.
* The data isn't guaranteed to be accurate and is not investment advice.
