import os

import pytest

from stockdex.ticker import Ticker

skip_test = bool(os.getenv("SKIP_TEST", False))


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker, frequency, period_ago",
    [
        ("AAPL", "annual", 0),
        ("AAPL", "quarterly", 4),
        ("NVDA", "annual", 0),
        ("BAC", "quarterly", 0),
        ("TSLA", "annual", 0),
        ("PLTR", "quarterly", 0),
    ],
)
def test_plot_sankey_chart(ticker, frequency, period_ago):
    ticker = Ticker(ticker=ticker)
    ticker.plot_sankey_chart(frequency=frequency, period_ago=period_ago)
