Stockdex
========

.. rst-class:: lead

   Financial data from Yahoo Finance, Digrin, Finviz, Macrotrends and justETF
   as pandas DataFrames and Plotly figures, in one ``Ticker`` object.

.. image:: https://badge.fury.io/py/stockdex.svg
   :target: https://pypi.org/project/stockdex/
   :alt: PyPI version

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :alt: Code style: black

.. image:: https://img.shields.io/badge/ruff-checked-brightgreen
   :alt: ruff

Install
-------

.. tab-set::

   .. tab-item:: pip

      .. code-block:: bash

         pip install -U stockdex

   .. tab-item:: Claude Desktop

      Download ``stockdex.mcpb`` from the
      `latest release <https://github.com/ahnazary/stockdex/releases/latest>`_
      and double-click it. See :doc:`claude`.

   .. tab-item:: Claude Code

      Requires `uv <https://docs.astral.sh/uv/>`_, which the plugin uses to
      start the MCP server.

      .. code-block:: text

         /plugin marketplace add ahnazary/stockdex
         /plugin install stockdex@stockdex

      See :ref:`claude-code-plugin` for the full setup.

Quick start
-----------

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="NVDA")

   income = ticker.yahoo_api_income_statement(frequency="quarterly")
   prices = ticker.yahoo_api_price(range="1y", dataGranularity="1d")
   dividends = ticker.digrin_dividend
   ticker.plot_yahoo_api_income_statement()

Every method name starts with its data source, e.g. ``yahoo_api_*`` or
``finviz_*``, so you always know where the numbers come from.

Data sources
------------

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: Yahoo Finance
      :link: readme_files/raw_dataframes/yahoo_api_doc
      :link-type: doc

      Prices, statements, valuation, profile, analyst estimates, holders,
      SEC filings, funds, options and search.

   .. grid-item-card:: Digrin
      :link: readme_files/raw_dataframes/digrin_doc
      :link-type: doc

      Long dividend history, payout ratio, dividend growth and fundamentals
      over many years.

   .. grid-item-card:: Macrotrends
      :link: readme_files/raw_dataframes/macrotrends_doc
      :link-type: doc

      Up to 15 years of statements, margins, ratios and revenue.

   .. grid-item-card:: Finviz
      :link: readme_files/raw_dataframes/finviz_doc
      :link-type: doc

      Insider trades, revenue by segment and region, earnings and revisions.

   .. grid-item-card:: justETF
      :link: readme_files/raw_dataframes/justetf_doc
      :link-type: doc

      European ETFs by ISIN: holdings, countries, sectors and fund basics.

   .. grid-item-card:: Use with Claude
      :link: claude
      :link-type: doc

      A local MCP server so Claude can look up stock data for you.

Plots
-----

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Charts
      :link: plots_and_figures
      :link-type: doc

      Bar and line charts for statements, dividends and cash flow, with
      ``show_plot=False`` to get the figure back.

   .. grid-item-card:: Sankey and dashboards
      :link: readme_files/plots_and_figures/sankey_charts
      :link-type: doc

      Cash-flow Sankey charts and multi-plot Dash apps.
