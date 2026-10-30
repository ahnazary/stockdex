API reference
=============

Every public method is available on :class:`stockdex.Ticker`. The classes
below are the mixins it is built from, one per data source.

.. code-block:: python

   from stockdex import Ticker

   stock = Ticker(ticker="AAPL")
   etf = Ticker(isin="IE00B4L5Y983", security_type="etf")

Ticker
------

.. autoclass:: stockdex.Ticker
   :no-members:

Yahoo Finance
-------------

.. autoclass:: stockdex.yahoo_api_interface.YahooAPI
   :members:
   :exclude-members: get_response

Digrin
------

.. autoclass:: stockdex.digrin_interface.DigrinInterface
   :members:

Macrotrends
-----------

.. autoclass:: stockdex.macrotrends_interface.MacrotrendsInterface
   :members:

Finviz
------

.. autoclass:: stockdex.finviz_interface.FinvizInterface
   :members:

justETF
-------

.. autoclass:: stockdex.justetf_interface.JustETF
   :members:

Charts
------

.. autoclass:: stockdex.sankey_charts.SankeyCharts
   :members:

.. autofunction:: stockdex.lib.plot_dataframe

Exceptions
----------

.. automodule:: stockdex.exceptions
   :members:
