# Finviz

Following functions will plot the data extracted from Finviz website using the `plotly` library:

```python
from stockdex import Ticker

ticker = Ticker(ticker="AAPL")

ticker.plot_finviz_revenue_by_products_and_services(log_scale=True)
ticker.plot_finviz_revenue_by_segment(log_scale=False)
ticker.plot_finviz_revenue_by_regions(log_scale=True)
```

Below the chart for `AAPL` revenue by products and services is shown in logarithmic scale:

![AAPL Finviz Revenue by Products and Services](../../images/plot_finviz_aapl_service_and_product.png)