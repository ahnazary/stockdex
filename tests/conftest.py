"""
Conftest for test serialization.

Ensures tests run one at a time to avoid rate limiting from external APIs
(digrin, justetf, macrotrends, yahoo, finviz, nasdaq).
"""

import threading

import pytest

# Semaphore to limit concurrent tests to 8 at a time across all test files
_test_semaphore = threading.Semaphore(8)


@pytest.fixture(autouse=True)
def serialize_tests():
    """
    Autouse fixture that acquires a semaphore before each test and releases it after.
    This limits concurrency to at most 8 tests at a time to avoid API rate limiting.
    """
    with _test_semaphore:
        yield
