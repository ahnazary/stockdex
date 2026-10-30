"""Bounded, read-only local operations shared by the CLI and MCP server.

No shell, arbitrary URLs, browser tools, or MCP dependency in this module.
"""

import json
import math
import re
import threading
from datetime import date, datetime, timezone
from decimal import Decimal

import numpy as np
import pandas as pd
from curl_cffi.requests.exceptions import RequestException

from stockdex import Ticker, config
from stockdex.exceptions import (
    LayoutChangedError,
    NoDataError,
    ProviderBlockedError,
    RateLimitError,
)

MAX_BYTES = 256 * 1024
MAX_ROWS = 500
PRICE_RANGES = ("1mo", "3mo", "6mo", "1y")
STATEMENTS = ("income_statement", "cash_flow", "balance_sheet")
STATEMENT_SOURCES = ("yahoo", "macrotrends")
VALUATION_FREQUENCIES = ("annual", "quarterly", "trailing")
DIVIDEND_SOURCES = ("digrin", "yahoo", "auto")
OPTION_TYPES = ("calls", "puts", "both")
MAX_QUOTE_SYMBOLS = 20
DEFAULT_METRICS = {
    "income_statement": ["TotalRevenue", "NetIncome", "BasicEPS"],
    "cash_flow": ["OperatingCashFlow", "FreeCashFlow", "CapitalExpenditure"],
    "balance_sheet": [
        "TotalAssets",
        "TotalLiabilitiesNetMinorityInterest",
        "StockholdersEquity",
    ],
}
# Macrotrends row names differ from Yahoo's; these defaults match the
# statement pages and the Stockdex plot defaults.
MACROTRENDS_DEFAULT_METRICS = {
    "income_statement": ["Revenue", "Net Income", "EPS - Earnings Per Share"],
    "cash_flow": [
        "Cash Flow From Operating Activities",
        "Net Change In Property, Plant, And Equipment",
        "Common Stock Dividends Paid",
    ],
    "balance_sheet": ["Total Assets", "Total Liabilities", "Share Holder Equity"],
}
_MACROTRENDS_METRIC = re.compile(r"[\w .,&'/()%+-]{1,80}")
# Macrotrends margin and ratio pages exposed by get_margins_and_ratios.
# "margin" pages are TTM tables with a Date column; "ratios" is field x date.
MACROTRENDS_DATASETS = {
    "gross_margin": "macrotrends_gross_margin",
    "operating_margin": "macrotrends_operating_margin",
    "ebitda_margin": "macrotrends_ebitda_margin",
    "pre_tax_margin": "macrotrends_pre_tax_margin",
    "net_margin": "macrotrends_net_margin",
    "key_ratios": "macrotrends_key_financial_ratios",
}
_PROVIDER_LOCK = threading.Lock()
_SOURCES = {"dividends": "digrin", "margins": "macrotrends"}
_SOURCES.update(
    revenue_breakdown="finviz", insiders="finviz", earnings_reaction="finviz"
)
# Dividend metrics: dataset -> (source, method). Digrin projections are
# estimates of future dividends at a fixed growth rate, not history.
DIVIDEND_METRICS = {
    "payout_ratio": ("digrin", "digrin_payout_ratio"),
    "growth_3y": ("digrin", "digrin_dgr3"),
    "growth_5y": ("digrin", "digrin_dgr5"),
    "growth_10y": ("digrin", "digrin_dgr10"),
    "annual": ("finviz", "finviz_dividends_annual_data"),
    "summary": ("finviz", "finviz_overall_dividend"),
}
_QUARTER = re.compile(r"(?P<year>\d{4})Q(?P<quarter>[1-4])")
_FISCAL_YEAR = re.compile(r"(?P<year>\d{4})FY")
_CURRENCY_AMOUNT = re.compile(r"(?P<amount>-?[\d,]*\.?\d+)\s*(?P<currency>[A-Z]{3})")
# Finviz revenue breakdowns: dataset -> FinvizInterface method
REVENUE_BREAKDOWNS = {
    "segment": "finviz_revenue_by_segment",
    "region": "finviz_revenue_by_regions",
    "product": "finviz_revenue_by_products_and_services",
}
EARNINGS_REACTION_DATASETS = ("price_reaction", "surprises", "revisions")
# Finviz price-reaction keys, in time order, and the column names we use.
_REACTION_WINDOWS = (
    ("minus_1_day", "day_before_pct"),
    ("open", "open_pct"),
    ("close", "day_after_close_pct"),
    ("plus_1_week", "one_week_pct"),
    ("plus_1_month", "one_month_pct"),
)
_FINVIZ_DATE = re.compile(r"(?P<mon>[A-Z][a-z]{2}) (?P<day>\d{2}) '(?P<year>\d{2})")
# Finviz estimate types: E = EPS (adjusted), R = EPS as reported (GAAP),
# S = sales (revenue).
_REVISION_TYPES = {"E": "eps", "R": "eps_reported", "S": "revenue"}
# The MCP should answer quickly; give bot-protected sites one short retry
# instead of the library default of five ten-second waits.
FORBIDDEN_RETRIES = 1
FORBIDDEN_RETRY_DELAY = 2.0
# Optional "^" prefix for indices (^GSPC) and "=" for futures/FX (GC=F, EURUSD=X).
_SYMBOL = re.compile(r"\^?[A-Z0-9]+(?:[.=-][A-Z0-9]+)*", re.ASCII)
# Placeholder Yahoo parsers emit when a field is absent from the response.
_UNAVAILABLE = "Data Not Available"
# Company names and partial tickers accepted by search: letters, digits,
# spaces and common punctuation in names, no URLs or control characters.
_SEARCH_QUERY = re.compile(r"[\w .,&'^=()/-]{1,64}")
MAX_SEARCH_RESULTS = 25
# Yahoo datasets exposed through StockdexAdapter.get_dataset.
# "record" methods return one value per field; "table" methods return rows.
YAHOO_DATASETS = {
    "profile": ("yahoo_api_profile", "record"),
    "officers": ("yahoo_api_officers", "table"),
    "market_price": ("yahoo_api_market_price", "record"),
    "summary": ("yahoo_api_summary_detail", "record"),
    "key_statistics": ("yahoo_api_key_statistics", "record"),
    "financial_data": ("yahoo_api_financial_data", "record"),
    "earnings_calendar": ("yahoo_api_calendar_events", "record"),
    "earnings_history": ("yahoo_api_earnings_history", "table"),
    "estimates": ("yahoo_api_earnings_trend", "table"),
    "recommendations": ("yahoo_api_recommendation_trend", "table"),
    "upgrades_downgrades": ("yahoo_api_upgrades_downgrades", "table"),
    "institutional_holders": ("yahoo_api_institutional_holders", "table"),
    "fund_holders": ("yahoo_api_fund_holders", "table"),
    "ownership_breakdown": ("yahoo_api_major_holders", "record"),
    "insiders": ("yahoo_api_insider_holders", "table"),
    "insider_transactions": ("yahoo_api_insider_transactions", "table"),
    "insider_activity": ("yahoo_api_insider_purchase_activity", "record"),
    "sec_filings": ("yahoo_api_sec_filings", "table"),
    "fund_top_holdings": ("yahoo_api_fund_top_holdings", "table"),
    "fund_sectors": ("yahoo_api_fund_sector_weightings", "table"),
    "fund_asset_allocation": ("yahoo_api_fund_asset_allocation", "record"),
    "fund_profile": ("yahoo_api_fund_profile", "record"),
    "fund_performance": ("yahoo_api_fund_performance", "table"),
    "similar_symbols": ("yahoo_api_similar_symbols", "table"),
}
_AMOUNT = re.compile(
    r"(?P<amount>[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)"
    r"\s+(?P<currency>[A-Z]{3})(?:\s*\([+-]?\d+(?:\.\d+)?%\))?"
)


class InputError(ValueError):
    """Invalid local tool arguments, safe to report to the caller."""


def encode_json(value):
    """One strict JSON representation for CLI and MCP text responses."""
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def _scalar(value):
    if isinstance(value, (list, tuple)):
        return [_scalar(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _scalar(item) for key, item in value.items()}
    if value is None or pd.isna(value):
        return None
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError("Unsupported provider value")


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise InputError("Dates must use YYYY-MM-DD.")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise InputError("Invalid calendar date.") from error


def _years_before(value, years):
    # February 29 maps to February 28 in non-leap years.
    try:
        return value.replace(year=value.year - years)
    except ValueError:
        return value.replace(year=value.year - years, day=28)


_MONEY = re.compile(r"(?P<sign>-)?\$?(?P<number>-?[\d,]*\.?\d+)(?P<unit>[KMBT])?")
_UNITS = {None: 0, "K": 3, "M": 6, "B": 9, "T": 12}


def _money(value):
    """'$416.16B' -> 416160000000.0, '-$1.2M' -> -1200000.0, '' -> None."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(" ", "")
    match = _MONEY.fullmatch(text)
    if not match:
        return None
    # Decimal keeps "$133.05B" exact (133050000000.0, not ...0.00002).
    number = float(
        Decimal(match["number"].replace(",", "")).scaleb(_UNITS[match["unit"]])
    )
    return -number if match["sign"] else number


def _percent(value):
    """'31.97%' -> 31.97, '' -> None."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().rstrip("%").replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def _macrotrends_number(column):
    """Statement and ratio cells are numeric strings or empty; '' -> null."""
    return pd.to_numeric(
        column.map(lambda v: None if v in ("", None) else str(v).replace(",", "")),
        errors="coerce",
    )


def _fiscal_year(value):
    """'2025FY' -> 2025; anything else means the layout changed."""
    match = _FISCAL_YEAR.fullmatch(str(value).strip())
    if not match:
        raise LayoutChangedError("Finviz", "fiscal period format changed")
    return int(match["year"])


_MONTHS = {
    m: i
    for i, m in enumerate(
        "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), start=1
    )
}


def _finviz_date(value):
    """ "Oct 27 '26" -> "2026-10-27"; unknown formats are a layout change."""
    match = _FINVIZ_DATE.fullmatch(str(value).strip())
    if not match or match["mon"] not in _MONTHS:
        raise LayoutChangedError("Finviz", "insider trade date format changed")
    return date(
        2000 + int(match["year"]), _MONTHS[match["mon"]], int(match["day"])
    ).isoformat()


class StockdexAdapter:
    def __init__(self, ticker_factory=Ticker, clock=None):
        self._ticker_factory = ticker_factory
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _provider(self, symbol):
        provider = self._ticker_factory(ticker=symbol)
        # Instance attributes only; library users keep the class defaults.
        if hasattr(provider, "forbidden_retries"):
            provider.forbidden_retries = FORBIDDEN_RETRIES
            provider.forbidden_retry_delay = FORBIDDEN_RETRY_DELAY
        return provider

    def get_prices(self, ticker, range="1mo", limit=20):
        return self._request("prices", ticker, {"range": range, "limit": limit})

    def get_financial_statement(
        self,
        ticker,
        statement="income_statement",
        frequency="annual",
        start_date=None,
        end_date=None,
        metrics=None,
        limit=20,
        source="yahoo",
    ):
        """
        Income statement, cash flow or balance sheet.

        ``source="yahoo"`` (default) covers up to five years and uses Yahoo
        metric names such as ``TotalRevenue``. ``source="macrotrends"`` covers
        up to about 15 years and uses Macrotrends row names such as
        ``Revenue``; values are in millions of the reporting currency.
        """
        return self._request(
            "financial_statement",
            ticker,
            {
                "statement": statement,
                "frequency": frequency,
                "start_date": start_date,
                "end_date": end_date,
                "metrics": metrics,
                "limit": limit,
                "source": source,
            },
        )

    def get_margins_and_ratios(self, ticker, dataset="operating_margin", limit=20):
        """Margins over time and key financial ratios from Macrotrends."""
        return self._request("margins", ticker, {"dataset": dataset, "limit": limit})

    def get_dividend_metrics(self, ticker, dataset="payout_ratio", limit=20):
        """
        Dividend payout, growth and annual history.

        Digrin: ``payout_ratio`` (quarterly payout and P/E) and
        ``growth_3y``/``growth_5y``/``growth_10y`` (dividends projected at the
        3/5/10-year average growth rate). Finviz: ``annual`` (amount, yield
        and payout per fiscal year, including analyst estimates) and
        ``summary`` (TTM dividend, next estimate and ex-date).
        """
        return self._request(
            "dividend_metrics", ticker, {"dataset": dataset, "limit": limit}
        )

    def get_revenue_breakdown(self, ticker, dataset="segment", limit=100):
        """Annual revenue by business segment, region or product from Finviz."""
        return self._request(
            "revenue_breakdown", ticker, {"dataset": dataset, "limit": limit}
        )

    def get_insider_trades(self, ticker, limit=20):
        """Recent insider buys and sales (SEC Form 4) from Finviz."""
        return self._request("insiders", ticker, {"limit": limit})

    def get_earnings_reaction(self, ticker, dataset="price_reaction", limit=12):
        """
        How the stock and estimates moved around earnings, from Finviz.

        ``price_reaction``: price change around each report vs the S&P 500.
        ``surprises``: actual vs estimated EPS and revenue per quarter.
        ``revisions``: latest analyst estimate and up/down revision counts
        per fiscal period.
        """
        return self._request(
            "earnings_reaction", ticker, {"dataset": dataset, "limit": limit}
        )

    def get_dividends(self, ticker, limit=20, source="digrin"):
        """
        Dividend history. ``source`` is "digrin" (default), "yahoo", or
        "auto" (Digrin first, Yahoo if Digrin is rate limited or unavailable).
        """
        return self._request("dividends", ticker, {"limit": limit, "source": source})

    def get_splits(self, ticker, limit=20):
        """Stock split history from Yahoo Finance, newest first."""
        return self._request("splits", ticker, {"limit": limit})

    def get_options_chain(self, ticker, expiration=None, option_type="both", limit=100):
        """Options chain for one expiration (nearest by default)."""
        return self._request(
            "options",
            ticker,
            {"expiration": expiration, "option_type": option_type, "limit": limit},
        )

    def get_quotes(self, symbols):
        """Current quotes for up to 20 symbols in one request."""
        return self._request("quotes", None, {"symbols": symbols})

    def get_valuation_history(self, ticker, frequency="quarterly", limit=20):
        """Market cap, enterprise value and valuation ratios over time."""
        return self._request(
            "valuation", ticker, {"frequency": frequency, "limit": limit}
        )

    def search(self, query, limit=10):
        """Find Yahoo Finance symbols for a company name or partial ticker."""
        return self._request("search", None, {"query": query, "limit": limit})

    def get_dataset(self, ticker, dataset, limit=None):
        """
        One Yahoo Finance dataset from YAHOO_DATASETS, e.g. "profile".

        Record datasets return ``field``/``value`` rows and by default every
        field; table datasets return their rows, 20 by default.
        """
        return self._request("dataset", ticker, {"dataset": dataset, "limit": limit})

    @staticmethod
    def _requested_source(operation, parameters, default):
        """The provider a request asks for, before its parameters are validated"""
        if operation == "financial_statement":
            return {"macrotrends": "macrotrends"}.get(parameters.get("source"), default)
        if operation == "dividend_metrics":
            dataset = parameters.get("dataset")
            if isinstance(dataset, str) and dataset in DIVIDEND_METRICS:
                return DIVIDEND_METRICS[dataset][0]
        return default

    def _validate(self, operation, ticker, parameters):
        if operation == "search":
            return self._validate_search(parameters)
        if operation == "quotes":
            return self._validate_quotes(parameters)
        if (
            not isinstance(ticker, str)
            or not ticker.isascii()
            or not 1 <= len(ticker) <= 20
        ):
            raise InputError("Ticker must be a stock symbol of 1–20 characters.")
        ticker = ticker.upper()
        if not _SYMBOL.fullmatch(ticker):
            raise InputError(
                "Use a ticker symbol, e.g. AAPL, BRK-B, BMW.DE, ^GSPC or GC=F; not a URL."
            )
        if operation == "dataset":
            if parameters["dataset"] not in YAHOO_DATASETS:
                raise InputError(
                    "dataset must be one of: " + ", ".join(sorted(YAHOO_DATASETS))
                )
            if parameters["limit"] is None:
                kind = YAHOO_DATASETS[parameters["dataset"]][1]
                parameters["limit"] = MAX_ROWS if kind == "record" else 20
        if operation == "margins" and parameters["dataset"] not in MACROTRENDS_DATASETS:
            raise InputError(
                "dataset must be one of: " + ", ".join(MACROTRENDS_DATASETS)
            )
        if (
            operation == "dividend_metrics"
            and parameters["dataset"] not in DIVIDEND_METRICS
        ):
            raise InputError("dataset must be one of: " + ", ".join(DIVIDEND_METRICS))
        if (
            operation == "revenue_breakdown"
            and parameters["dataset"] not in REVENUE_BREAKDOWNS
        ):
            raise InputError("dataset must be segment, region or product.")
        if (
            operation == "earnings_reaction"
            and parameters["dataset"] not in EARNINGS_REACTION_DATASETS
        ):
            raise InputError("dataset must be price_reaction, surprises or revisions.")
        if (
            type(parameters["limit"]) is not int
            or not 1 <= parameters["limit"] <= MAX_ROWS
        ):
            raise InputError("limit must be an integer from 1 to 500.")
        if operation == "dividends":
            if parameters.get("source", "digrin") not in DIVIDEND_SOURCES:
                raise InputError("source must be digrin, yahoo or auto.")
            parameters.setdefault("source", "digrin")
        if operation == "options":
            if parameters["option_type"] not in OPTION_TYPES:
                raise InputError("option_type must be calls, puts or both.")
            if parameters["expiration"] is not None:
                parameters["expiration"] = _date(parameters["expiration"]).isoformat()
        if operation == "valuation":
            if parameters["frequency"] not in VALUATION_FREQUENCIES:
                raise InputError("frequency must be annual, quarterly or trailing.")
        if operation == "prices":
            if parameters["range"] not in PRICE_RANGES:
                raise InputError("range must be 1mo, 3mo, 6mo or 1y.")
            parameters["interval"] = "1d"
        if operation == "financial_statement":
            statement = parameters["statement"]
            if statement not in STATEMENTS:
                raise InputError("Unsupported financial statement.")
            if parameters["frequency"] not in ("annual", "quarterly"):
                raise InputError("frequency must be annual or quarterly.")
            source = parameters.setdefault("source", "yahoo")
            if source not in STATEMENT_SOURCES:
                raise InputError("source must be yahoo or macrotrends.")
            if source == "macrotrends":
                self._validate_macrotrends_statement(parameters)
                return ticker
            today = self._clock().date()
            end = (
                _date(parameters["end_date"])
                if parameters["end_date"] is not None
                else today
            )
            if end.year <= 5:
                raise InputError("End date must allow a five-year lookback.")
            start = (
                _date(parameters["start_date"])
                if parameters["start_date"] is not None
                else _years_before(end, 5)
            )
            if end > today or not _years_before(end, 5) <= start < end:
                raise InputError(
                    "Use an increasing date window of at most five years, ending no later than today."
                )
            parameters.update(start_date=start.isoformat(), end_date=end.isoformat())
            metrics = parameters["metrics"]
            if metrics is None:
                metrics = DEFAULT_METRICS[statement][:]
            allowed = {
                "income_statement": config.INCOME_STATEMENT_COLUMNS,
                "cash_flow": config.CASH_FLOW_COLUMNS,
                "balance_sheet": config.BALANCE_SHEET_COLUMNS,
            }[statement]
            if (
                not isinstance(metrics, list)
                or not 1 <= len(metrics) <= 20
                or any(not isinstance(m, str) or m not in allowed for m in metrics)
            ):
                raise InputError(
                    "Select 1–20 metric names from the statement's Stockdex config columns (without a frequency prefix)."
                )
            if len(set(metrics)) != len(metrics):
                raise InputError("Metric names must be unique.")
            parameters["metrics"] = metrics
        return ticker

    @staticmethod
    def _validate_quotes(parameters):
        symbols = parameters["symbols"]
        if isinstance(symbols, str):
            symbols = [symbols]
        if not isinstance(symbols, list) or not 1 <= len(symbols) <= MAX_QUOTE_SYMBOLS:
            raise InputError(
                f"symbols must be a list of 1 to {MAX_QUOTE_SYMBOLS} ticker symbols."
            )
        cleaned = []
        for symbol in symbols:
            if (
                not isinstance(symbol, str)
                or not symbol.isascii()
                or not 1 <= len(symbol) <= 20
                or not _SYMBOL.fullmatch(symbol.upper())
            ):
                raise InputError(
                    "Each symbol must be a ticker such as AAPL, BMW.DE or ^GSPC."
                )
            if symbol.upper() not in cleaned:
                cleaned.append(symbol.upper())
        parameters["symbols"] = cleaned
        parameters["limit"] = len(cleaned)
        return None

    @staticmethod
    def _validate_search(parameters):
        query = parameters["query"]
        if (
            not isinstance(query, str)
            or "://" in query
            or any(not ch.isprintable() for ch in query)
            or not _SEARCH_QUERY.fullmatch(query.strip())
        ):
            raise InputError(
                "query must be a company name or ticker of 1–64 characters, not a URL."
            )
        parameters["query"] = " ".join(query.split())
        limit = parameters["limit"]
        if type(limit) is not int or not 1 <= limit <= MAX_SEARCH_RESULTS:
            raise InputError(
                f"limit must be an integer from 1 to {MAX_SEARCH_RESULTS}."
            )
        return None

    def _request(self, operation, ticker, parameters):
        result = {
            "schema_version": "1.0",
            "ok": False,
            "operation": operation,
            "ticker": None,
            "source": _SOURCES.get(operation, "yahoo_api"),
            "retrieved_at": None,
            "parameters": {},
            "columns": [],
            "records": [],
            "total_rows": 0,
            "returned_rows": 0,
            "truncated": False,
            "warnings": [],
            "error": None,
        }
        try:
            parameters = dict(parameters)
            # Report the requested provider even when validation rejects the call
            result["source"] = self._requested_source(
                operation, parameters, result["source"]
            )
            symbol = self._validate(operation, ticker, parameters)
            result.update(ticker=symbol, parameters=parameters)
            if operation == "financial_statement":
                result["source"] = {"macrotrends": "macrotrends"}.get(
                    parameters["source"], "yahoo_api"
                )
            if operation == "dividend_metrics":
                result["source"] = DIVIDEND_METRICS[parameters["dataset"]][0]
            # Nonblocking admission prevents an unbounded queue of waiting requests.
            if not _PROVIDER_LOCK.acquire(blocking=False):
                result["error"] = {
                    "code": "busy",
                    "message": "Another local request is running; try again after it finishes.",
                }
                return result
            try:
                if operation == "search":
                    frame = self._search(parameters)
                elif operation == "quotes":
                    frame = self._quotes(parameters)
                else:
                    provider = self._provider(symbol)
                    frame = self._fetch(
                        provider, operation, parameters, result["warnings"]
                    )
            finally:
                _PROVIDER_LOCK.release()
            result["retrieved_at"] = self._clock().isoformat()
            if operation in ("dividends", "financial_statement"):
                result["source"] = frame.attrs.get("source", result["source"])
            if frame.empty:
                raise NoDataError()
            if not frame.columns.is_unique:
                raise ValueError("Duplicate provider columns")
            result["total_rows"] = len(frame)
            result["columns"] = [str(c) for c in frame.columns]
            result["records"] = [
                {str(k): _scalar(v) for k, v in row.items()}
                for row in frame.head(parameters["limit"]).to_dict(orient="records")
            ]
            result["ok"] = True
            result["returned_rows"] = len(result["records"])
            result["truncated"] = result["returned_rows"] < result["total_rows"]
            while len(encode_json(result).encode("utf-8")) > MAX_BYTES:
                if not result["records"]:
                    raise ValueError("Provider metadata exceeds output budget")
                result["records"].pop()
                result["returned_rows"] -= 1
                result["truncated"] = True
            return result
        except InputError as error:
            code, message = "invalid_input", str(error)
        except RateLimitError:
            code, message = (
                "rate_limited",
                "Provider rate limit reached. Wait before trying again; do not retry in a loop.",
            )
        except ProviderBlockedError:
            code, message = (
                "provider_blocked",
                "The website refused the request, usually because of bot protection. "
                "Try another source or try again later; do not retry in a loop.",
            )
        except LayoutChangedError:
            code, message = (
                "layout_changed",
                "The website's page layout changed and Stockdex could not read it. "
                "This does not mean the value is zero; try another source.",
            )
        except NoDataError:
            code, message = (
                "no_data",
                "No data was returned for this symbol and request. This does not establish a zero value.",
            )
        except RequestException:
            code, message = "network_error", "The provider request failed or timed out."
        except (KeyError, IndexError, TypeError, ValueError, AttributeError):
            code, message = (
                "provider_schema_error",
                "The provider returned an unsupported data layout.",
            )
        except Exception:
            # Provider exceptions can contain cookies, crumbs, URLs or raw HTML.
            code, message = (
                "provider_error",
                "The provider could not complete the request.",
            )
        result.update(
            ok=False, columns=[], records=[], returned_rows=0, truncated=False
        )
        result["error"] = {"code": code, "message": message}
        return result

    def _fetch(self, provider, operation, parameters, warnings):
        if operation == "prices":
            frame = provider.yahoo_api_price(
                range=parameters["range"], dataGranularity="1d"
            ).copy()
            if frame.empty:
                return frame
            required = {
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "currency",
            }
            if not required.issubset(frame.columns):
                raise ValueError("Missing price columns")
            # Yahoo returns no timestamps for symbols without bars in the range.
            if frame["timestamp"].astype(str).eq(_UNAVAILABLE).all():
                raise NoDataError()
            frame["timestamp"] = pd.to_datetime(
                frame["timestamp"], utc=True, errors="coerce"
            )
            if frame["timestamp"].isna().any():
                raise ValueError("Missing price timestamps")
            for column in ("open", "high", "low", "close", "volume"):
                frame[column] = pd.to_numeric(frame[column], errors="raise")
            warnings.append(
                "Historical daily bars, not a real-time quote. Timestamps are UTC; exchange timezone metadata is separate."
            )
            return frame.sort_values("timestamp", ascending=False, kind="stable")
        if operation == "financial_statement":
            if parameters.get("source") == "macrotrends":
                return self._macrotrends_statement(provider, parameters, warnings)
            methods = {
                "income_statement": provider.yahoo_api_income_statement,
                "cash_flow": provider.yahoo_api_cash_flow,
                "balance_sheet": provider.yahoo_api_balance_sheet,
            }
            frame = methods[parameters["statement"]](
                frequency=parameters["frequency"],
                format="raw",
                period1=datetime.combine(
                    _date(parameters["start_date"]), datetime.min.time(), timezone.utc
                ),
                period2=datetime.combine(
                    _date(parameters["end_date"]), datetime.min.time(), timezone.utc
                ),
            ).copy()
            if frame.empty:
                return frame
            columns = [parameters["frequency"] + m for m in parameters["metrics"]]
            missing = [c for c in columns if c not in frame.columns]
            if len(missing) == len(columns):
                raise NoDataError()
            if missing:
                warnings.append(
                    "Unavailable metrics returned as null: " + ", ".join(missing)
                )
            frame = frame.reindex(columns=columns)
            for column in columns:
                frame[column] = pd.to_numeric(frame[column], errors="raise")
            dates = pd.to_datetime(frame.index, errors="raise")
            if dates.isna().any():
                raise ValueError("Missing statement dates")
            frame.insert(0, "date", dates.strftime("%Y-%m-%d"))
            frame = frame[
                (frame["date"] >= parameters["start_date"])
                & (frame["date"] < parameters["end_date"])
            ]
            warnings.append(
                "Raw provider values; currency/units are not supplied by this interface. Do not assume all metrics are monetary. End date is exclusive."
            )
            return frame.sort_values("date", ascending=False, kind="stable")
        if operation == "dataset":
            return self._dataset(provider, parameters["dataset"])
        if operation == "margins":
            return self._margins(provider, parameters["dataset"], warnings)
        if operation == "dividend_metrics":
            return self._dividend_metrics(provider, parameters["dataset"], warnings)
        if operation == "revenue_breakdown":
            return self._revenue_breakdown(provider, parameters["dataset"], warnings)
        if operation == "insiders":
            return self._insider_trades(provider, warnings)
        if operation == "earnings_reaction":
            return self._earnings_reaction(provider, parameters["dataset"], warnings)
        if operation == "splits":
            return self._events(provider.yahoo_api_splits(), "split_date")
        if operation == "options":
            return self._options(provider, parameters)
        if operation == "valuation":
            frame = provider.yahoo_api_valuation_measures(
                frequency=parameters["frequency"], format="raw"
            )
            if frame.empty:
                return frame
            prefix = parameters["frequency"]
            frame = frame.rename(
                columns=lambda c: c[len(prefix) :] if c.startswith(prefix) else c
            )
            frame = frame.apply(pd.to_numeric, errors="coerce")
            frame.insert(0, "date", pd.to_datetime(frame.index).strftime("%Y-%m-%d"))
            warnings.append(
                "Raw provider values. Market cap and enterprise value are in the "
                "trading currency; ratios are unitless."
            )
            return frame.sort_values("date", ascending=False).reset_index(drop=True)
        return self._dividends_with_source(provider, parameters, warnings)

    def _dividends_with_source(self, provider, parameters, warnings):
        source = parameters.get("source", "digrin")
        if source == "yahoo":
            return self._yahoo_dividends(provider)
        try:
            frame = self._dividends(provider.digrin_dividend, warnings)
        except (RateLimitError, RequestException, ValueError, RuntimeError):
            if source != "auto":
                raise
            frame = pd.DataFrame()
        if frame.empty and source == "auto":
            warnings.append(
                "Digrin was unavailable or empty; dividends come from Yahoo Finance."
            )
            return self._yahoo_dividends(provider)
        frame.attrs["source"] = "digrin"
        return frame

    def _yahoo_dividends(self, provider):
        frame = self._events(provider.yahoo_api_dividends(), "ex_dividend_date")
        frame.attrs["source"] = "yahoo_api"
        return frame

    @staticmethod
    def _events(frame, date_column):
        if frame.empty:
            return frame
        frame = frame.rename_axis(date_column).reset_index()
        frame[date_column] = pd.to_datetime(frame[date_column], utc=True).dt.strftime(
            "%Y-%m-%d"
        )
        return frame.sort_values(date_column, ascending=False).reset_index(drop=True)

    @staticmethod
    def _options(provider, parameters):
        frame = provider.yahoo_api_options_chain(
            expiration=parameters["expiration"],
            option_type=parameters["option_type"],
        )
        if frame.empty:
            return frame
        keep = [
            "optionType",
            "contractSymbol",
            "strike",
            "lastPrice",
            "bid",
            "ask",
            "change",
            "percentChange",
            "volume",
            "openInterest",
            "impliedVolatility",
            "inTheMoney",
            "expiration",
            "lastTradeDate",
            "currency",
        ]
        return frame[[c for c in keep if c in frame]].reset_index(drop=True)

    def _quotes(self, parameters):
        quotes = getattr(self._ticker_factory, "yahoo_api_quotes", None)
        if quotes is None:
            quotes = Ticker.yahoo_api_quotes
        frame = quotes(parameters["symbols"])
        if frame.empty:
            return frame
        keep = [
            "shortName",
            "quoteType",
            "currency",
            "exchange",
            "marketState",
            "regularMarketPrice",
            "regularMarketChange",
            "regularMarketChangePercent",
            "regularMarketVolume",
            "regularMarketTime",
            "marketCap",
            "fiftyTwoWeekLow",
            "fiftyTwoWeekHigh",
            "trailingPE",
            "forwardPE",
            "dividendYield",
        ]
        frame = frame[[c for c in keep if c in frame]]
        return frame.rename_axis("symbol").reset_index()

    def _search(self, parameters):
        search = getattr(self._ticker_factory, "yahoo_api_search", None)
        if search is None:
            search = Ticker.yahoo_api_search
        return search(parameters["query"], limit=parameters["limit"])

    @staticmethod
    def _dataset(provider, dataset):
        method, kind = YAHOO_DATASETS[dataset]
        frame = getattr(provider, method)()
        if frame.empty:
            return frame
        if kind == "record":
            frame = frame.iloc[:, :1].copy()
            frame.columns = ["value"]
            return frame.rename_axis("field").reset_index()
        if not isinstance(frame.index, pd.RangeIndex):
            name = frame.index.name or "key"
            frame = frame.rename_axis(name).reset_index()
        return frame.reset_index(drop=True)

    @staticmethod
    def _dividends(frame, warnings):
        if frame.empty:
            return frame
        rows = []
        incomplete = False
        for row in frame.to_dict(orient="records"):
            raw = _scalar(row["Dividend amount (change)"])
            text = " ".join(str(raw).split()) if raw is not None else ""
            match = _AMOUNT.fullmatch(text)
            normalized = {"amount_text": raw, "amount": None, "currency": None}
            if match:
                normalized.update(
                    amount=float(match["amount"].replace(",", "")),
                    currency=match["currency"],
                )
            else:
                incomplete = True
            for source, target in (
                ("Ex-dividend date", "ex_dividend_date"),
                ("Payable date", "payable_date"),
            ):
                value = _scalar(row[source])
                try:
                    normalized[target] = _date(str(value).strip()).isoformat()
                except InputError:
                    normalized[target] = None
                    incomplete = True
            rows.append(normalized)
        if incomplete:
            warnings.append(
                "Some dividend amounts, currencies or dates could not be parsed and are null; original amount text is retained."
            )
        return pd.DataFrame(rows).sort_values(
            "ex_dividend_date", ascending=False, na_position="last", kind="stable"
        )

    def _validate_macrotrends_statement(self, parameters):
        today = self._clock().date()
        for key in ("start_date", "end_date"):
            if parameters[key] is not None:
                parameters[key] = _date(parameters[key]).isoformat()
        end = parameters["end_date"]
        if end is not None and end > today.isoformat():
            raise InputError("end_date must not be in the future.")
        start = parameters["start_date"]
        if start is not None and end is not None and not start < end:
            raise InputError("start_date must be before end_date.")
        metrics = parameters["metrics"]
        if metrics is None:
            metrics = MACROTRENDS_DEFAULT_METRICS[parameters["statement"]][:]
        if (
            not isinstance(metrics, list)
            or not 1 <= len(metrics) <= 20
            or any(
                not isinstance(m, str) or not _MACROTRENDS_METRIC.fullmatch(m)
                for m in metrics
            )
        ):
            raise InputError(
                "Select 1–20 Macrotrends row names, e.g. Revenue or Net Income."
            )
        if len(set(metrics)) != len(metrics):
            raise InputError("Metric names must be unique.")
        parameters["metrics"] = metrics

    @staticmethod
    def _macrotrends_statement(provider, parameters, warnings):
        methods = {
            "income_statement": provider.macrotrends_income_statement,
            "cash_flow": provider.macrotrends_cash_flow,
            "balance_sheet": provider.macrotrends_balance_sheet,
        }
        frame = methods[parameters["statement"]](frequency=parameters["frequency"])
        if frame.empty:
            return frame
        # Field x period -> one row per period, matching the Yahoo layout.
        by_name = {str(name).strip().casefold(): name for name in frame.index}
        wanted = parameters["metrics"]
        found = [by_name.get(m.casefold()) for m in wanted]
        missing = [m for m, f in zip(wanted, found) if f is None]
        if missing:
            warnings.append(
                "Unavailable metrics returned as null: "
                + ", ".join(missing)
                + ". Available rows: "
                + ", ".join(str(n) for n in frame.index[:40])
            )
        if len(missing) == len(wanted):
            raise NoDataError()
        rows = frame.reindex([f for f in found if f is not None]).T
        rows.columns = [m for m, f in zip(wanted, found) if f is not None]
        rows = rows.reindex(columns=wanted)
        rows = rows.apply(_macrotrends_number)
        dates = pd.to_datetime(rows.index, errors="coerce")
        if dates.isna().all():
            raise LayoutChangedError("Macrotrends", "statement periods are not dates")
        rows = rows[~dates.isna()]
        rows.insert(0, "date", dates[~dates.isna()].strftime("%Y-%m-%d"))
        if parameters["start_date"]:
            rows = rows[rows["date"] >= parameters["start_date"]]
        if parameters["end_date"]:
            rows = rows[rows["date"] < parameters["end_date"]]
        warnings.append(
            "Macrotrends values are in millions of the reporting currency, except "
            "per-share figures and ratios. End date is exclusive."
        )
        rows = rows.sort_values("date", ascending=False, kind="stable")
        rows = rows.reset_index(drop=True)
        rows.attrs["source"] = "macrotrends"
        return rows

    @staticmethod
    def _dividend_metrics(provider, dataset, warnings):
        method = DIVIDEND_METRICS[dataset][1]
        attribute = getattr(provider, method)
        frame = attribute() if callable(attribute) else attribute
        if frame.empty:
            return frame
        frame = frame.rename(columns=lambda c: str(c).strip())
        if dataset == "payout_ratio":
            out = pd.DataFrame(
                {
                    "quarter": frame["Date"].map(lambda v: str(v).strip()),
                    "payout_ratio_pct": frame["Payout ratio"].map(_percent),
                    "pe_ratio": frame["PE ratio"].map(_percent),
                }
            )
            if not out["quarter"].map(lambda v: bool(_QUARTER.fullmatch(v))).all():
                raise LayoutChangedError("Digrin", "payout ratio periods changed")
            warnings.append(
                "Payout ratio is a percentage of earnings (56.9 means 56.9%)."
            )
            return out.sort_values("quarter", ascending=False).reset_index(drop=True)
        if dataset.startswith("growth_"):
            rows = []
            for row in frame.to_dict(orient="records"):
                year = str(row.get("Year", "")).strip()
                if not year.isdigit():
                    raise LayoutChangedError(
                        "Digrin", "growth projection years changed"
                    )
                match = _CURRENCY_AMOUNT.fullmatch(
                    str(row.get("Dividend", "")).replace(" ", "")
                )
                rows.append(
                    {
                        "year": int(year),
                        "projected_dividend": (
                            float(match["amount"].replace(",", "")) if match else None
                        ),
                        "currency": match["currency"] if match else None,
                        "yield_on_cost_pct": _percent(
                            row.get("Estimated Yield on Cost")
                        ),
                    }
                )
            years = dataset[len("growth_") : -1]
            warnings.append(
                "Projections, not history: future dividends assuming the "
                f"{years}-year average dividend growth rate continues. Yield on "
                "cost is a percentage of today's price."
            )
            return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)
        if dataset == "annual":
            out = pd.DataFrame(
                {
                    "fiscal_year": frame["FiscalPeriod"].map(_fiscal_year),
                    "amount": pd.to_numeric(frame["Amount"], errors="coerce"),
                    "yield_pct": pd.to_numeric(frame["Yield"], errors="coerce"),
                    "payout_pct": pd.to_numeric(frame["Payout"], errors="coerce"),
                    "estimate": frame["Estimate"].map(lambda v: v is True),
                }
            )
            warnings.append(
                "Per-share amounts in the trading currency; yield and payout are "
                "percentages. Rows with estimate=true are analyst forecasts."
            )
            return out.sort_values("fiscal_year", ascending=False).reset_index(
                drop=True
            )
        # summary: one record as field/value rows, like the Yahoo record datasets
        names = {
            "lastClose": "last_close",
            "dividendExDate": "next_ex_dividend_date",
            "dividendEstimate": "next_12m_dividend_estimate",
            "dividendTTM": "trailing_12m_dividend",
        }
        rows = []
        for key, value in frame.iloc[0].to_dict().items():
            if key == "dividendExDate" and isinstance(value, str):
                value = value[:10]
            rows.append({"field": names.get(key, key), "value": value})
        warnings.append("Per-share amounts in the trading currency.")
        return pd.DataFrame(rows)

    @staticmethod
    def _revenue_breakdown(provider, dataset, warnings):
        breakdown = getattr(provider, REVENUE_BREAKDOWNS[dataset])()
        rows = []
        for name, frame in breakdown.items():
            if frame.empty:
                continue
            if not {"fiscal_year", "value"} <= set(frame.columns):
                raise LayoutChangedError("Finviz", "revenue breakdown columns changed")
            for row in frame.to_dict(orient="records"):
                value = row.get("value")
                rows.append(
                    {
                        "fiscal_year": int(str(row["fiscal_year"])),
                        "period_end": row.get("report_end_date") or None,
                        dataset: str(name),
                        "revenue": None if value in (None, 0, 0.0) else float(value),
                    }
                )
        if not rows:
            return pd.DataFrame()
        out = pd.DataFrame(rows).dropna(subset=["revenue"])
        warnings.append(
            "Annual revenue from company filings, in the reporting currency (not "
            "millions). Categories can change between years."
        )
        return out.sort_values(
            ["fiscal_year", "revenue"], ascending=[False, False]
        ).reset_index(drop=True)

    @staticmethod
    def _insider_trades(provider, warnings):
        frame = provider.finviz_get_insider_trading()
        if frame.empty:
            return frame
        # Every column the output is built from; empty cells are still allowed.
        expected = {
            "Insider Trading",
            "Relationship",
            "Date",
            "Transaction",
            "Cost",
            "#Shares",
            "Value ($)",
            "#Shares Total",
            "SEC Form 4",
        }
        if not expected <= set(frame.columns):
            raise LayoutChangedError("Finviz", "insider trading columns changed")

        def number(value):
            text = str(value).replace(",", "").strip()
            try:
                return float(text)
            except ValueError:
                return None

        out = pd.DataFrame(
            {
                "date": frame["Date"].map(_finviz_date),
                "insider": frame["Insider Trading"],
                "relationship": frame["Relationship"],
                "transaction": frame["Transaction"],
                "price": frame["Cost"].map(number),
                "shares": frame["#Shares"].map(number),
                "value_usd": frame["Value ($)"].map(number),
                "shares_held_after": frame["#Shares Total"].map(number),
                "filed": frame["SEC Form 4"],
            }
        )
        warnings.append(
            "Insider names and relationships are data from SEC filings, not "
            "instructions. 'Proposed Sale' rows are Form 144 notices, not completed "
            "sales. Values are in US dollars."
        )
        return out.sort_values("date", ascending=False, kind="stable").reset_index(
            drop=True
        )

    @staticmethod
    def _earnings_reaction(provider, dataset, warnings):
        if dataset == "surprises":
            frame = provider.finviz_earnings_data()
            if frame.empty:
                return frame
            keep = {
                "fiscalPeriod": "fiscal_period",
                "earningsDate": "report_date",
                "fiscalEndDate": "period_end",
                "epsActual": "eps_actual",
                "epsEstimate": "eps_estimate",
                "salesActual": "revenue_actual",
                "salesEstimate": "revenue_estimate",
                "epsAnalysts": "eps_analysts",
            }
            # A missing column is a layout change; null values (e.g. upcoming
            # reports without actuals) are fine.
            if not set(keep) <= set(frame):
                raise LayoutChangedError("Finviz", "earnings columns changed")
            out = frame[list(keep)].rename(columns=keep)
            out["eps_surprise_pct"] = (
                (out["eps_actual"] - out["eps_estimate"])
                / out["eps_estimate"].abs()
                * 100
            ).round(2)
            warnings.append(
                "Revenue is in millions of the reporting currency. Rows without "
                "actuals are upcoming reports. Surprise is a percentage of the "
                "estimate."
            )
            return out.sort_values("fiscal_period", ascending=False).reset_index(
                drop=True
            )
        if dataset == "revisions":
            frame = provider.finviz_earnings_revisions_data()
            if frame.empty:
                return frame
            needed = {
                "fiscalPeriod",
                "estimateType",
                "estimateDate",
                "mean",
                "high",
                "low",
                "estimates",
                "upRevisions",
                "downRevisions",
            }
            if not needed <= set(frame):
                raise LayoutChangedError("Finviz", "revision columns changed")
            # The newest whole row per period and type. GroupBy.last() would
            # mix columns from older snapshots when the newest has nulls.
            latest = frame.sort_values("estimateDate", kind="stable").drop_duplicates(
                ["fiscalPeriod", "estimateType"], keep="last"
            )
            out = pd.DataFrame(
                {
                    "fiscal_period": latest["fiscalPeriod"],
                    "estimate": latest["estimateType"].map(
                        lambda t: _REVISION_TYPES.get(t, t)
                    ),
                    "as_of": latest["estimateDate"].str[:10],
                    "mean": latest["mean"],
                    "high": latest["high"],
                    "low": latest["low"],
                    "analysts": latest["estimates"],
                    "up_revisions": latest["upRevisions"],
                    "down_revisions": latest["downRevisions"],
                }
            )
            warnings.append(
                "Latest consensus per fiscal period. EPS is per share; revenue is "
                "in millions of the reporting currency."
            )
            return out.sort_values(
                ["fiscal_period", "estimate"], ascending=[False, True]
            ).reset_index(drop=True)
        frame = provider.finviz_price_reaction_to_earnings_report()
        if frame.empty:
            return frame
        if not {"reportDate", "fiscalPeriod", "reactions"} <= set(frame):
            raise LayoutChangedError("Finviz", "price reaction columns changed")
        rows = []
        for record in frame.to_dict(orient="records"):
            reactions = record["reactions"]
            if not isinstance(reactions, dict):
                raise LayoutChangedError("Finviz", "price reaction layout changed")
            row = {
                "fiscal_period": record["fiscalPeriod"],
                "report_date": str(record["reportDate"])[:10],
            }
            for key, column in _REACTION_WINDOWS:
                point = reactions.get(key) or {}
                change = point.get("priceDiff")
                spy = point.get("spyPriceDiff")
                row[column] = None if change is None else round(float(change), 2)
                row[column.replace("_pct", "_vs_spy_pct")] = (
                    None
                    if change is None or spy is None
                    else round(float(change) - float(spy), 2)
                )
            rows.append(row)
        warnings.append(
            "Percent price changes around each earnings report: day_before is the "
            "session before the report, open/day_after_close compare with the "
            "last close before the report, one_week/one_month with the previous "
            "point. *_vs_spy_pct subtracts the S&P 500 (SPY) move. Null means the "
            "window has not happened yet."
        )
        return (
            pd.DataFrame(rows)
            .sort_values("report_date", ascending=False)
            .reset_index(drop=True)
        )

    @staticmethod
    def _margins(provider, dataset, warnings):
        frame = getattr(provider, MACROTRENDS_DATASETS[dataset])
        if frame.empty:
            return frame
        if dataset == "key_ratios":
            # Field x date -> one row per date, ratios as numbers.
            frame = frame.T.apply(_macrotrends_number)
            dates = pd.to_datetime(frame.index, errors="coerce")
            frame = frame[~dates.isna()]
            frame.insert(0, "date", dates[~dates.isna()].strftime("%Y-%m-%d"))
            warnings.append(
                "Ratios are unitless except margins and returns, which are percentages "
                "(31.9 means 31.9%)."
            )
            return frame.sort_values("date", ascending=False).reset_index(drop=True)
        if "Date" not in frame.columns:
            raise LayoutChangedError(
                "Macrotrends", f"{dataset} table has no Date column"
            )
        dates = pd.to_datetime(frame["Date"], errors="coerce")
        frame = frame[~dates.isna()].reset_index(drop=True)
        out = pd.DataFrame({"date": dates.dropna().dt.strftime("%Y-%m-%d").values})
        for column in frame.columns:
            if column == "Date":
                continue
            name = re.sub(r"[^0-9a-z]+", "_", column.lower()).strip("_")
            if column.endswith("Margin"):
                out[name + "_pct"] = frame[column].map(_percent)
            else:
                out[name] = frame[column].map(_money)
        warnings.append(
            "Trailing-twelve-month values from Macrotrends. Amounts are in the "
            "reporting currency; *_pct columns are percentages (31.9 means 31.9%)."
        )
        return out.sort_values("date", ascending=False).reset_index(drop=True)
