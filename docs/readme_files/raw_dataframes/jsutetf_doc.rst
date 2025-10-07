justETF
=======


For EU ETFS, the ``isin`` and ``security_type`` should be passed to the ``Ticker`` object. The ``isin`` is the International Securities Identification Number of the ETF (e.g ``IE00B4L5Y983``) and the ``security_type`` should be set to ``etf``.
Below are examples of available methods from JustETF source.

.. important::
   In each result dataframe, only the first 5 rows of the DataFrame are shown at most to keep the documentation concise. The actual DataFrame returned by each function may contain more rows.


General Info
~~~~~~~~~~~~

Gives general info about the ETF. This is the data shown in the overview tab on JustETF website.

.. code-block:: python

    from stockdex import Ticker

    etf = Ticker(isin="IE00B4L5Y983", security_type="etf")
    result = etf.justetf_general_info

**Results:**

+---+------------+--------------------+-------------+----------------+-------------------+----------+
|   | TER        | Distributionpolicy | Replication | Fundsize       | InceptionDate     | Holdings |
+===+============+====================+=============+================+===================+==========+
| 0 | 0.20% p.a. | Accumulating       | Physical    | EUR 102,811  m | 25 September 2009 | 1,319    |
+---+------------+--------------------+-------------+----------------+-------------------+----------+


justetf_wkn
~~~~~~~~~~~~

Gives the WKN (Wertpapierkennnummer) of the ETF.

.. code-block:: python

    from stockdex import Ticker

    etf = Ticker(isin="IE00B4L5Y983", security_type="etf")
    result = etf.justetf_wkn

**Results:**

.. code-block:: text

    A0RPWH

Description
~~~~~~~~~~~

.. code-block:: python

    from stockdex import Ticker

    etf = Ticker(isin="IE00B4L5Y983", security_type="etf")
    result = etf.justetf_description

**Results:**

.. code-block:: text
    
    The iShares Core MSCI World UCITS ETF USD (Acc) seeks to track the MSCI World index. The MSCI World index tracks stocks from 23 developed countries worldwide.      The ETF's TER (total expense ratio) amounts to 0.20% p.a..   The iShares Core MSCI World UCITS ETF USD (Acc) is the largest ETF that tracks the MSCI World index.   The ETF replicates the performance of the underlying index by sampling technique (buying a selection of the most relevant index constituents).     The dividends in the ETF  are accumulated and reinvested in the ETF.            The iShares Core MSCI World UCITS ETF USD (Acc) is a very large ETF with 102,811m Euro assets under management.    The ETF was launched on 25 September 2009  and is domiciled in Ireland.


Share of companies in the ETF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Show the companies who have the highest share in the ETF.

.. code-block:: python

    from stockdex import Ticker

    etf = Ticker(isin="IE00B4L5Y983", security_type="etf")
    result = etf.justetf_holdings_companies

**Results:**

+--------------------+-----------------------+
| company name       | shares in percent     |
+====================+=======================+
| NVIDIA Corp.       | 5.42%                 |
+--------------------+-----------------------+
| Microsoft          | 4.56%                 |
+--------------------+-----------------------+
| Apple              | 4.42%                 |
+--------------------+-----------------------+
| Amazon.com, Inc.   | 2.79%                 |
+--------------------+-----------------------+
| Meta Platforms     | 2.05%                 |
+--------------------+-----------------------+


Share of countries in the ETF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Show the countries who have the highest share in the ETF.

.. code-block:: python

    from stockdex import Ticker

    etf = Ticker(isin="IE00B4L5Y983", security_type="etf")
    result = etf.justetf_holdings_sectors

**Results:**

+------------------+-----------------------+
| country name     | shares in percent     |
+==================+=======================+
| United States    | 68.47%                |
+------------------+-----------------------+
| Japan            | 5.47%                 |
+------------------+-----------------------+
| United Kingdom   | 3.51%                 |
+------------------+-----------------------+
| Canada           | 2.89%                 |
+------------------+-----------------------+
| Other            | 19.66%                |
+------------------+-----------------------+


Share of sectors in the ETF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Show the sectors who have the highest share in the ETF.

.. code-block:: python

    from stockdex import Ticker

    etf = Ticker(isin="IE00B4L5Y983", security_type="etf")
    result = etf.justetf_holdings_sectors

**Results:**

+--------------------------+-----------------------+
| sector name              | shares in percent     |
+==========================+=======================+
| Technology               | 27.93%                |
+--------------------------+-----------------------+
| Financials               | 14.70%                |
+--------------------------+-----------------------+
| Consumer Discretionary   | 10.40%                |
+--------------------------+-----------------------+
| Industrials              | 10.29%                |
+--------------------------+-----------------------+
| Other                    | 36.68%                |
+--------------------------+-----------------------+

Basics
~~~~~~~~~~~~~~~~~~~~~~

Gives basic data about the ETF. Returned fields include:

  - Index
  - Investment focus
  - Fund size
  - Total expense ratio
  - Replication
  - Legal structure
  - Strategy risk
  - Sustainability
  - Fund currency
  - Currency risk
  - Volatility 1 year (in EUR)
  - Inception/ Listing Date
  - Distribution policy
  - Distribution frequency
  - Fund domicile
  - Fund Provider

.. code-block:: python

    from stockdex import Ticker

    etf = Ticker(isin="IE00B4L5Y983", security_type="etf")
    result = etf.justetf_basics


**Results:**

+---+------------+------------------+---------------+---------------------+-------------------------------+-----------------+---------------+----------------+---------------+-------------------+----------------------------+-------------------------+---------------------+------------------------+---------------+---------------+
|   | Index      | Investment focus | Fund size     | Total expense ratio | Replication                   | Legal structure | Strategy risk | Sustainability | Fund currency | Currency risk     | Volatility 1 year (in EUR) | Inception/ Listing Date | Distribution policy | Distribution frequency | Fund domicile | Fund Provider |
+===+============+==================+===============+=====================+===============================+=================+===============+================+===============+===================+============================+=========================+=====================+========================+===============+===============+
| 0 | MSCI World | Equity, World    | EUR 102,811 m | 0.20% p.a.          | Physical (Optimized sampling) | ETF             | Long-only     | No             | USD           | Currency unhedged | 16.07%                     | 25 September 2009       | Accumulating        | -                      | Ireland       | iShares       |
+---+------------+------------------+---------------+---------------------+-------------------------------+-----------------+---------------+----------------+---------------+-------------------+----------------------------+-------------------------+---------------------+------------------------+---------------+---------------+
