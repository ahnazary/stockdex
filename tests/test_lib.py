"""
Test the lib module
"""

import os
import threading
import time

import pytest

from stockdex.lib import plot_multiple_categories
from stockdex.ticker import Ticker

skip_test = bool(os.getenv("SKIP_TEST", False))


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("BAC"), ("CAT"), ("ASML"), ("MSFT"), ("PLTR"), ("DHL.DE")],
)
def test_complex_digrin_plot(ticker):
    """
    Test that builds multiple figures and plots them together in one dashboard
    """

    ticker = Ticker(ticker=ticker)
    figures = [
        ticker.plot_digrin_shares_outstanding(show_plot=False),
        ticker.plot_digrin_price(show_plot=False),
        ticker.plot_digrin_dividend(show_plot=False),
        ticker.plot_digrin_assets_vs_liabilities(show_plot=False),
        ticker.plot_digrin_free_cash_flow(show_plot=False),
        ticker.plot_digrin_net_income(show_plot=False),
        ticker.plot_digrin_cash_and_debt(show_plot=False),
        ticker.plot_digrin_expenses(show_plot=False),
        ticker.plot_digrin_cost_of_revenue(show_plot=False),
    ]

    # Function to run the Dash app
    def run_dash_app():
        plot_multiple_categories(ticker=ticker.ticker, figures=figures)

    # Start the Dash app in a separate thread
    dash_thread = threading.Thread(target=run_dash_app)
    dash_thread.daemon = True
    dash_thread.start()

    # Allow the Dash app to run for a short duration (e.g., 5 seconds)
    print("Waiting for Dash app to run for 10 seconds")
    time.sleep(10)


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("BAC"), ("CAT"), ("ASML"), ("MSFT"), ("PLTR"), ("DHL.DE")],
)
def test_complex_yahoo_api_plot(ticker):
    """
    Test that builds multiple figures and plots them together in dash
    """

    ticker = Ticker(ticker=ticker)
    figures = [
        ticker.plot_yahoo_api_income_statement(show_plot=False),
        ticker.plot_yahoo_api_cash_flow(show_plot=False),
        ticker.plot_yahoo_api_balance_sheet(show_plot=False),
        ticker.plot_yahoo_api_financials(show_plot=False),
    ]

    # Function to run the Dash app
    def run_dash_app():
        plot_multiple_categories(ticker=ticker.ticker, figures=figures)

    # Start the Dash app in a separate thread
    dash_thread = threading.Thread(target=run_dash_app)
    dash_thread.daemon = True
    dash_thread.start()

    # Allow the Dash app to run for a short duration (e.g., 5 seconds)
    print("Waiting for Dash app to run for 10 seconds")
    time.sleep(10)


@pytest.mark.skipif(skip_test, reason="Skipping in GH action as it is visual")
@pytest.mark.parametrize(
    "ticker",
    [("AAPL"), ("BAC"), ("CAT"), ("ASML"), ("MSFT"), ("PLTR"), ("DHL.DE")],
)
def test_complex_macrotrends_plot(ticker):
    """
    Test that builds multiple figures and plots them together in dash
    """

    ticker = Ticker(ticker=ticker)
    figures = [
        ticker.plot_macrotrends_income_statement(show_plot=False),
        ticker.plot_macrotrends_balance_sheet(show_plot=False),
        ticker.plot_macrotrends_cash_flow(show_plot=False),
    ]

    # Function to run the Dash app
    def run_dash_app():
        plot_multiple_categories(ticker=ticker.ticker, figures=figures)

    # Start the Dash app in a separate thread
    dash_thread = threading.Thread(target=run_dash_app)
    dash_thread.daemon = True
    dash_thread.start()

    # Allow the Dash app to run for a short duration (e.g., 5 seconds)
    print("Waiting for Dash app to run for 10 seconds")
    time.sleep(10)
