"""Tests for shared HTTP behavior in TickerBase."""

from types import SimpleNamespace

import pytest

from stockdex.config import DIGRIN_BASE_URL
from stockdex.exceptions import RateLimitError
from stockdex.ticker_base import TickerBase


def test_get_response_aborts_immediately_on_rate_limit(monkeypatch):
    calls = []
    response = SimpleNamespace(
        status_code=429,
        headers={"Retry-After": "120"},
    )

    def fake_get(*args, **kwargs):
        calls.append((args, kwargs))
        return response

    monkeypatch.setattr(TickerBase, "session", SimpleNamespace(get=fake_get))
    monkeypatch.setattr(TickerBase, "_external_request_delay", 0)

    with pytest.raises(RateLimitError, match="Retry-After: 120") as error:
        TickerBase().get_response("https://example.com/rate-limited")

    assert error.value.retry_after == "120"
    assert len(calls) == 1


def test_digrin_responses_are_cached_for_the_test_session(
    monkeypatch, cache_live_digrin_requests
):
    calls = []
    response = SimpleNamespace(status_code=200, headers={})

    def fake_get(*args, **kwargs):
        calls.append((args, kwargs))
        return response

    cache_live_digrin_requests.clear()
    monkeypatch.setattr(TickerBase, "session", SimpleNamespace(get=fake_get))
    monkeypatch.setattr(TickerBase, "_external_request_delay", 0)
    url = f"{DIGRIN_BASE_URL}/CACHE/price"

    first = TickerBase().get_response(url)
    second = TickerBase().get_response(url)

    assert first is second
    assert len(calls) == 1
