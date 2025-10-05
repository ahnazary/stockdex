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

- **Various data sources**: ``Stockdex`` provides data from Yahoo Finance and other sources like Digrin, Finviz, Macrotrends, and JustETF (for EU ETFs).

- **Historical data**: ``Stockdex`` provides a wide time range of data.  
  For example, Digrin and Macrotrends sources provide historical data over many years.

- **Numerous data categories**: ``Stockdex`` provides financial criteria including financial statements, earnings, dividends, stock splits, list of key executives, major shareholders, and more.

- **Plotting capabilities (new feature)**:  
  ``Stockdex`` provides plotting of financial data using bar, line, and Sankey plots.  
  Multiple plots can be combined into an interactive Dash app.

Installation
------------

Install the package using pip:

.. code-block:: bash

   pip install stockdex -U

Documentation
-------------

## Installation

Install the package using pip:

```bash
pip install stockdex -U
```

Usage
-----

Details of available data sources and their usage can be found in :doc:`data_sources`. Also documentation of Plotly plotting functions can be found in :doc:`plots_and_figures`.
