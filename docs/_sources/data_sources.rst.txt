Data Sources
============

Each data source returns pandas DataFrames. Every method name starts with
its source, e.g. ``yahoo_api_income_statement`` or ``finviz_revenue_by_segment``.

.. list-table::
   :header-rows: 1
   :widths: 18 18 64

   * - Source
     - Prefix
     - Best for
   * - Yahoo Finance
     - ``yahoo_api_``
     - Prices, statements, valuation, profile, analyst estimates, ownership,
       SEC filings, ETF and fund data, options and search
   * - Digrin
     - ``digrin_``
     - Full dividend history, payout ratio, dividend growth rate and
       long-term fundamentals
   * - Macrotrends
     - ``macrotrends_``
     - Up to 15 years of statements, margins, ratios and revenue
   * - Finviz
     - ``finviz_``
     - Insider trades, revenue by segment, region and product, earnings
       history and revisions
   * - justETF
     - ``justetf_``
     - European ETFs by ISIN (needs Chrome, uses Selenium)

.. note::
   The ``yahoo_web_*`` methods are deprecated. Each still works but emits a
   ``DeprecationWarning`` and returns data from its ``yahoo_api_*``
   replacement. They will be removed in 2.0; see the :doc:`changelog`.

.. toctree::
   :maxdepth: 1

   readme_files/raw_dataframes/yahoo_api_doc
   readme_files/raw_dataframes/finviz_doc
   readme_files/raw_dataframes/digrin_doc
   readme_files/raw_dataframes/macrotrends_doc
   readme_files/raw_dataframes/justetf_doc