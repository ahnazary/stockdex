Digrin
=======

Data on the Digrin website includes all historical data of the stock in certain categories, unlike Yahoo Finance which only provides the last 5 years or last 4 quarters of data at most.  

Below are some examples of the data that can be retrieved from Digrin through Stockdex.

.. important::
   In each result dataframe, only the first 5 rows of the DataFrame are shown at most to keep the documentation concise. The actual DataFrame returned by each function may contain more rows.
   
.. note::
   Be aware that some digrin dataframes may require additional data cleaning. In certain cases digrin's API payload may send back additional hidden data (e.g., spaces or trailing characters) that will need to be handled correctly. For example, digrin's Payout Ratio data the Date field has trailing spaces that will impact your ability to convert to a pandas datetime object.


Dividend data
~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="AAPL")
   result = ticker.digrin_dividend


Results:

+----+-------------------+---------------+----------------------------------------------------------------------------------------------------------+-----------------+--------------+
|    | Ex-dividend date  | Payable date  | Dividend amount (change)                                                                                 | Adjusted Price  | Close Price  |
+====+===================+===============+==========================================================================================================+=================+==============+
|  0 | 2025-08-11        | 2025-08-14    | 0.2600 USD                                                                                               | 202.38 USD      | 202.38 USD   |
+----+-------------------+---------------+----------------------------------------------------------------------------------------------------------+-----------------+--------------+
|  1 | 2025-05-12        | 2025-05-15    | 0.2600 USD (4%)                                                                                          | 205.35 USD      | 205.35 USD   |
+----+-------------------+---------------+----------------------------------------------------------------------------------------------------------+-----------------+--------------+
|  2 | 2025-02-10        | 2025-02-13    | 0.2500 USD                                                                                               | 234.32 USD      | 234.32 USD   |
+----+-------------------+---------------+----------------------------------------------------------------------------------------------------------+-----------------+--------------+
|  3 | 2024-11-08        | 2024-11-14    | 0.2500 USD                                                                                               | 222.91 USD      | 222.91 USD   |
+----+-------------------+---------------+----------------------------------------------------------------------------------------------------------+-----------------+--------------+
|  4 | 2024-08-12        | 2024-08-15    | 0.2500 USD                                                                                               | 219.86 USD      | 219.86 USD   |
+----+-------------------+---------------+----------------------------------------------------------------------------------------------------------+-----------------+--------------+


Payout Ratio data
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="MSFT")
   result = ticker.digrin_payout_ratio


Results:

+----+---------+---------------+-----------+
|    | Date    | Payout ratio  | PE ratio  |
+====+=========+===============+===========+
|  0 | 2025Q4  | 22.65%        | 33.94     |
+----+---------+---------------+-----------+
|  1 | 2025Q3  | 23.89%        | 27.02     |
+----+---------+---------------+-----------+
|  2 | 2025Q2  | 25.59%        | 32.50     |
+----+---------+---------------+-----------+
|  3 | 2025Q1  | 22.60%        | 32.42     |
+----+---------+---------------+-----------+
|  4 | 2024Q4  | 25.29%        | 38.52     |
+----+---------+---------------+-----------+


Price
~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="TSLA")
   result = ticker.digrin_price


Results:

+----+----------------+-----------------+-------------+
|    | Date           | Adjusted price  | Real price  |
+====+================+=================+=============+
|  0 | October 2025   | $459.46         | $459.46     |
+----+----------------+-----------------+-------------+
|  1 | September 2025 | $444.72         | $444.72     |
+----+----------------+-----------------+-------------+
|  2 | August 2025    | $333.87         | $333.87     |
+----+----------------+-----------------+-------------+
|  3 | July 2025      | $308.27         | $308.27     |
+----+----------------+-----------------+-------------+
|  4 | June 2025      | $317.66         | $317.66     |
+----+----------------+-----------------+-------------+


Stock splits
~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="TSLA")
   result = ticker.digrin_stock_splits


Results:

+----+------------+--------------+
|    | Date       | Split Ratio  |
+====+============+==============+
|  0 | 2022-08-25 | 3            |
+----+------------+--------------+
|  1 | 2020-08-31 | 5            |
+----+------------+--------------+


Assets vs Liabilities
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="TSLA")
   result = ticker.digrin_assets_vs_liabilities

Results:

+---+----------------+---------------+--------------+
|   | Date           | Assets        | Liabilities  |
+===+================+===============+==============+
| 0 | June 30, 2025  | 128.6 billion | 50.5 billion |
+---+----------------+---------------+--------------+
| 1 | March 31, 2025 | 125.1 billion | 49.7 billion |
+---+----------------+---------------+--------------+
| 2 | Dec. 31, 2024  | 122.1 billion | 48.4 billion |
+---+----------------+---------------+--------------+
| 3 | Sept. 30, 2024 | 119.9 billion | 49.1 billion |
+---+----------------+---------------+--------------+


Free Cash Flow
~~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="TSLA")
   result = ticker.digrin_free_cash_flow

Results:

+---+----------------+----------------+--------------------------+
|   | Date           | Free Cash Flow | Stock based compensation |
+===+================+================+==========================+
| 0 | June 30, 2025  | 146.0 million  | 635.0 million            |
+---+----------------+----------------+--------------------------+
| 1 | March 31, 2025 | 664.0 million  | 573.0 million            |
+---+----------------+----------------+--------------------------+
| 2 | Dec. 31, 2024  | 2.0 billion    | 579.0 million            |
+---+----------------+----------------+--------------------------+
| 3 | Sept. 30, 2024 | 2.7 billion    | 457.0 million            |
+---+----------------+----------------+--------------------------+



Net Income
~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="GOOG")
   result = ticker.digrin_net_income

Results:

+---+----------------+--------------+
|   | Date           | Net Income   |
+===+================+==============+
| 0 | June 30, 2025  | 28.2 billion |
+---+----------------+--------------+
| 1 | March 31, 2025 | 34.5 billion |
+---+----------------+--------------+
| 2 | Dec. 31, 2024  | 26.5 billion |
+---+----------------+--------------+
| 3 | Sept. 30, 2024 | 26.3 billion |
+---+----------------+--------------+


Cash and Debt
~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="GOOG")
   result = ticker.digrin_cash_and_debt

Results:

+---+----------------+--------------+--------------+---------------+
|   | Date           | Cash         | Debt         | Capital Lease |
+===+================+==============+==============+===============+
| 0 | June 30, 2025  | 95.1 billion | 35.6 billion | 12.0 billion  |
+---+----------------+--------------+--------------+---------------+
| 1 | March 31, 2025 | 95.3 billion | 22.6 billion | 11.7 billion  |
+---+----------------+--------------+--------------+---------------+
| 2 | Dec. 31, 2024  | 95.7 billion | 22.6 billion | 14.6 billion  |
+---+----------------+--------------+--------------+---------------+
| 3 | Sept. 30, 2024 | 93.2 billion | 24.0 billion | 16.0 billion  |
+---+----------------+--------------+--------------+---------------+



Shares Outstanding
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="GOOG")
   result = ticker.digrin_shares_outstanding

Results:

+---+----------------+--------------------+
|   | Date           | Shares Outstanding |
+===+================+====================+
| 0 | June 30, 2025  | 12.2 billion       |
+---+----------------+--------------------+
| 1 | March 31, 2025 | 12.3 billion       |
+---+----------------+--------------------+
| 2 | Dec. 31, 2024  | 12.3 billion       |
+---+----------------+--------------------+
| 3 | Sept. 30, 2024 | 12.4 billion       |
+---+----------------+--------------------+


Expenses
~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="GOOG")
   result = ticker.digrin_expenses

Results:

+---+----------------+--------------+--------------+--------------+-------------+
|   | Date           | Capex        | R&D          | G&A          | S&M         |
+===+================+==============+==============+==============+=============+
| 0 | June 30, 2025  | 22.4 billion | 13.8 billion | 12.3 billion | 7.1 billion |
+---+----------------+--------------+--------------+--------------+-------------+
| 1 | March 31, 2025 | 17.2 billion | 13.6 billion | 9.7 billion  | 6.2 billion |
+---+----------------+--------------+--------------+--------------+-------------+
| 2 | Dec. 31, 2024  | 14.3 billion | 13.1 billion | 11.8 billion | 7.4 billion |
+---+----------------+--------------+--------------+--------------+-------------+
| 3 | Sept. 30, 2024 | 13.1 billion | 12.4 billion | 10.8 billion | 7.2 billion |
+---+----------------+--------------+--------------+--------------+-------------+


Cost of Revenue
~~~~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="GOOG")
   result = ticker.digrin_cost_of_revenue

Results:

+---+----------------+--------------+-----------------+
|   | Date           | Revenue      | Cost of Revenue |
+===+================+==============+=================+
| 0 | June 30, 2025  | 96.4 billion | 39.0 billion    |
+---+----------------+--------------+-----------------+
| 1 | March 31, 2025 | 90.2 billion | 36.4 billion    |
+---+----------------+--------------+-----------------+
| 2 | Dec. 31, 2024  | 96.5 billion | 40.6 billion    |
+---+----------------+--------------+-----------------+
| 3 | Sept. 30, 2024 | 88.3 billion | 36.5 billion    |
+---+----------------+--------------+-----------------+


Upcoming Estimated Earnings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="GOOG")
   result = ticker.digrin_upcoming_estimated_earnings

Results:

+---+---------------------------+------------------------+--------------+----------------------------+---------------+
|   | Date                      | Actual / Estimated EPS | Low Revenue  | Actual / Estimated Revenue | High Revenue  |
+===+===========================+========================+==============+============================+===============+
| 0 | Oct. 27, 2025 AfterMarket | - / -                  | 97.5 billion | - / 99.6 billion           | 107.7 billion |
+---+---------------------------+------------------------+--------------+----------------------------+---------------+


Dividend Growth Rate (3-Year Average)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="NVDA")
   result = ticker.digrin_dgr3


Results:

+---+------+----------+-------------------------+
|   | Year | Dividend | Estimated Yield on Cost |
+===+======+==========+=========================+
| 0 | 2035 | 0.396USD | 0.21%                   |
+---+------+----------+-------------------------+
| 1 | 2034 | 0.317USD | 0.17%                   |
+---+------+----------+-------------------------+
| 2 | 2033 | 0.253USD | 0.14%                   |
+---+------+----------+-------------------------+
| 3 | 2032 | 0.203USD | 0.11%                   |
+---+------+----------+-------------------------+
| 4 | 2031 | 0.162USD | 0.09%                   |
+---+------+----------+-------------------------+


Dividend Growth Rate (5-Year Average)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="AAPL")
   result = ticker.digrin_dgr5

Results:

+---+------+----------+-------------------------+
|   | Year | Dividend | Estimated Yield on Cost |
+===+======+==========+=========================+
| 0 | 2035 | 1.669USD | 0.65%                   |
+---+------+----------+-------------------------+
| 1 | 2034 | 1.591USD | 0.62%                   |
+---+------+----------+-------------------------+
| 2 | 2033 | 1.518USD | 0.59%                   |
+---+------+----------+-------------------------+
| 3 | 2032 | 1.447USD | 0.56%                   |
+---+------+----------+-------------------------+
| 4 | 2031 | 1.380USD | 0.53%                   |
+---+------+----------+-------------------------+



Dividend Growth Rate (10-Year Average)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from stockdex import Ticker

   ticker = Ticker(ticker="MSFT")
   result = ticker.digrin_dgr10

Results:

+---+------+----------+-------------------------+
|   | Year | Dividend | Estimated Yield on Cost |
+===+======+==========+=========================+
| 0 | 2035 | 8.991USD | 1.74%                   |
+---+------+----------+-------------------------+
| 1 | 2034 | 8.156USD | 1.58%                   |
+---+------+----------+-------------------------+
| 2 | 2033 | 7.399USD | 1.43%                   |
+---+------+----------+-------------------------+
| 3 | 2032 | 6.713USD | 1.30%                   |
+---+------+----------+-------------------------+
| 4 | 2031 | 6.090USD | 1.18%                   |
+---+------+----------+-------------------------+
