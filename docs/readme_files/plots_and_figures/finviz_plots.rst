Finviz Plots
============

Grouped bar charts of revenue broken down by product, segment or region,
from Finviz. Each takes ``logarithmic`` (bool) to use a log scale on the
y-axis, which helps when one category is much larger than the rest.

Revenue by Products and Services
--------------------------------

.. code-block:: python

    from stockdex import Ticker

    ticker = Ticker(ticker="AAPL")
    ticker.plot_finviz_revenue_by_products_and_services(logarithmic=False)

.. image:: ../../images/plot_finviz_aapl_service_and_product.png
   :alt: Apple revenue by products and services from Finviz
   :align: center
   :width: 80%
   :class: rounded

Revenue by Segments
-------------------

.. code-block:: python

    from stockdex import Ticker

    ticker = Ticker(ticker="AAPL")
    ticker.plot_finviz_revenue_by_segments(logarithmic=False)

Revenue by Regions
------------------

.. code-block:: python

    from stockdex import Ticker

    ticker = Ticker(ticker="NVDA")
    ticker.plot_finviz_revenue_by_regions(logarithmic=True)

.. image:: ../../images/plot_finviz_nvda_service_and_product.png
   :alt: NVIDIA revenue breakdown from Finviz
   :align: center
   :width: 80%
   :class: rounded
