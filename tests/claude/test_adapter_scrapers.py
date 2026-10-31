"""The MCP adapter makes bot-protected sites fail fast."""

from stockdex.claude_adapter import (
    FORBIDDEN_RETRIES,
    FORBIDDEN_RETRY_DELAY,
    StockdexAdapter,
)
from stockdex.ticker_base import TickerBase
from tests.claude.conftest import FakeTicker


class Provider(FakeTicker):
    forbidden_retries = TickerBase.forbidden_retries
    forbidden_retry_delay = TickerBase.forbidden_retry_delay


def test_adapter_shortens_forbidden_retries_per_instance():
    made = []

    def factory(**kwargs):
        made.append(Provider(kwargs["ticker"]))
        return made[-1]

    assert StockdexAdapter(ticker_factory=factory).get_prices("AAPL")["ok"]
    assert made[0].forbidden_retries == FORBIDDEN_RETRIES
    assert made[0].forbidden_retry_delay == FORBIDDEN_RETRY_DELAY
    # The library default is untouched for normal users.
    assert TickerBase.forbidden_retries == 5
    assert TickerBase.forbidden_retry_delay == 10.0


def test_fake_providers_without_the_setting_still_work(adapter):
    assert adapter.get_prices("AAPL")["ok"]
