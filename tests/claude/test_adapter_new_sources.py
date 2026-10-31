"""Offline tests for the justETF, Digrin and Macrotrends revenue adapter paths."""

import pandas as pd
import pytest

from stockdex.claude_adapter import StockdexAdapter, _digrin_amount


class FakeRevenue:
    def __init__(self, frame):
        self.frame = frame
        self.calls = []

    def macrotrends_revenue(self, frequency="annual"):
        self.calls.append(frequency)
        return self.frame


def test_macrotrends_revenue_annual():
    provider = FakeRevenue(
        pd.DataFrame(
            {
                "Amazon Annual Revenue (Millions of US $)": [2023, 2024],
                "Amazon Annual Revenue (Millions of US $).1": ["$574,785", "$637,959"],
            }
        )
    )
    warnings = []
    out = StockdexAdapter._macrotrends_revenue(provider, "annual", warnings)
    assert provider.calls == ["annual"]
    assert out.to_dict("records") == [
        {"fiscal_year": 2024, "revenue_millions": 637959.0},
        {"fiscal_year": 2023, "revenue_millions": 574785.0},
    ]
    assert "millions" in warnings[0]


def test_macrotrends_revenue_quarterly():
    provider = FakeRevenue(
        pd.DataFrame(
            {
                "Amazon Quarterly Revenue (Millions of US $)": [
                    "2025-03-31",
                    "2025-06-30",
                ],
                "Amazon Quarterly Revenue (Millions of US $).1": [
                    "$155,667",
                    "$167,702",
                ],
            }
        )
    )
    out = StockdexAdapter._macrotrends_revenue(provider, "quarterly", [])
    assert out.to_dict("records")[0] == {
        "period_end": "2025-06-30",
        "revenue_millions": 167702.0,
    }


@pytest.mark.parametrize("value", ["?", "N/A", "-", None])
def test_digrin_missing_markers_are_null(value):
    assert _digrin_amount(value) is None


def test_digrin_amount_units():
    assert _digrin_amount("383.3 billion") == 383_300_000_000.0


def test_empty_etf_basics_is_returned_empty():
    class Provider:
        justetf_basics = pd.DataFrame()

    out = StockdexAdapter._etf_profile(Provider(), {"dataset": "basics"}, [])
    assert out.empty
