.. image:: https://badge.fury.io/py/stockdex.svg
   :target: https://badge.fury.io/py/stockdex
   :alt: PyPI version

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :alt: Code style: black

.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
   :alt: Code style: isort

.. image:: https://img.shields.io/badge/flake8-checked-blue
   :alt: flake8

.. image:: https://img.shields.io/badge/ruff-checked-brightgreen
   :alt: ruff

Stock Data Extractor (Stockdex)
===============================

Stockdex is a Python package that provides a simple interface to get financial data from various sources in pandas DataFrames and Plotly figures.

Advantages of ``Stockdex`` over similar packages
------------------------------------------------

- **Various data sources**: Data from various sources like Yahoo Finance, Digrin, Finviz, Macrotrends and JustETF (for EU ETFs).

- **Historical data**: A wide time range of historical data is available.
  For example, Digrin and Macrotrends sources provide historical data over many years.

- **Numerous data categories**: Various financial criteria including financial statements, earnings, dividends, stock splits, list of key executives, major shareholders, and more are available.

- **Plotting capabilities**:  
  Plotting financial data using bar, line, and Sankey plots is supported to some extent.
  Multiple plots can be combined into an interactive Dash app.



Installation
------------

Install the package using pip:

.. code-block:: bash

   pip install stockdex -U


Walkthrough
----------------

This documentation provides a walkthrough of the main features of the package. 

You can check out :doc:`data_sources` section for details on available data sources and their functionalities with examples.

You can also check out :doc:`plots_and_figures` section for details on plotting functions with examples.


