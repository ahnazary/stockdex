"""
Conftest for test serialization.

Ensures tests run one at a time to avoid rate limiting from external APIs
(digrin, justetf, macrotrends, yahoo, finviz, nasdaq).
"""

import os
import threading

import pytest

from stockdex.config import DIGRIN_BASE_URL, MACROTRENDS_BASE_URL
from stockdex.exceptions import RateLimitError
from stockdex.ticker_base import TickerBase

# Semaphore to limit concurrent tests to 8 at a time across all test files
_test_semaphore = threading.Semaphore(8)


def pytest_addoption(parser):
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="run tests that make live requests to external websites",
    )


def pytest_collection_modifyitems(config, items):
    run_live = config.getoption("--run-live") or os.getenv("RUN_LIVE_TESTS") == "1"
    if run_live:
        return

    skip_live = pytest.mark.skip(reason="live test; pass --run-live to enable")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture(scope="session", autouse=True)
def cache_live_digrin_requests():
    """Cache Digrin responses and stop live requests after the first HTTP 429.

    Macrotrends requests are not cached, but the first HTTP 403 (bot
    protection) opens a circuit so later tests skip instead of each spending
    about a minute in the 403 retry loop.
    """

    original_get_response = TickerBase.get_response
    response_cache = {}
    circuit = {"rate_limit": None, "macrotrends_blocked": None}

    def cached_get_response(self, url):
        if url.startswith(MACROTRENDS_BASE_URL):
            if circuit["macrotrends_blocked"] is not None:
                pytest.skip(
                    f"Macrotrends blocked this test run: {circuit['macrotrends_blocked']}"
                )
            try:
                return original_get_response(self, url)
            except RuntimeError as error:
                if "status 403" not in str(error):
                    raise
                circuit["macrotrends_blocked"] = error
                pytest.skip(f"Macrotrends blocked this test run: {error}")

        if not url.startswith(DIGRIN_BASE_URL):
            return original_get_response(self, url)

        if circuit["rate_limit"] is not None:
            pytest.skip(f"Digrin rate-limit circuit is open: {circuit['rate_limit']}")

        if url in response_cache:
            return response_cache[url]

        try:
            response = original_get_response(self, url)
        except RateLimitError as error:
            circuit["rate_limit"] = error
            pytest.skip(f"Digrin rate limited this test run: {error}")

        response_cache[url] = response
        return response

    TickerBase.get_response = cached_get_response
    try:
        yield response_cache
    finally:
        TickerBase.get_response = original_get_response


@pytest.fixture(autouse=True)
def serialize_tests():
    """
    Autouse fixture that acquires a semaphore before each test and releases it after.
    This limits concurrency to at most 8 tests at a time to avoid API rate limiting.
    """
    with _test_semaphore:
        yield
