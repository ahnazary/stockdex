"""Bounded, read-only local operations shared by the CLI and MCP server.

No shell, arbitrary URLs, browser tools, or MCP dependency in this module.
"""

import json
import math
import re
import threading
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
from curl_cffi.requests.exceptions import RequestException

from stockdex import Ticker, config
from stockdex.exceptions import NoDataError, RateLimitError

MAX_BYTES = 256 * 1024
MAX_ROWS = 500
PRICE_RANGES = ("1mo", "3mo", "6mo", "1y")
STATEMENTS = ("income_statement", "cash_flow", "balance_sheet")
DEFAULT_METRICS = {
    "income_statement": ["TotalRevenue", "NetIncome", "BasicEPS"],
    "cash_flow": ["OperatingCashFlow", "FreeCashFlow", "CapitalExpenditure"],
    "balance_sheet": [
        "TotalAssets",
        "TotalLiabilitiesNetMinorityInterest",
        "StockholdersEquity",
    ],
}
_PROVIDER_LOCK = threading.Lock()
# Optional "^" prefix for indices (^GSPC) and "=" for futures/FX (GC=F, EURUSD=X).
_SYMBOL = re.compile(r"\^?[A-Z0-9]+(?:[.=-][A-Z0-9]+)*", re.ASCII)
# Placeholder Yahoo parsers emit when a field is absent from the response.
_UNAVAILABLE = "Data Not Available"
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


class StockdexAdapter:
    def __init__(self, ticker_factory=Ticker, clock=None):
        self._ticker_factory = ticker_factory
        self._clock = clock or (lambda: datetime.now(timezone.utc))

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
    ):
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
            },
        )

    def get_dividends(self, ticker, limit=20):
        return self._request("dividends", ticker, {"limit": limit})

    def _validate(self, operation, ticker, parameters):
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
        if (
            type(parameters["limit"]) is not int
            or not 1 <= parameters["limit"] <= MAX_ROWS
        ):
            raise InputError("limit must be an integer from 1 to 500.")
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

    def _request(self, operation, ticker, parameters):
        result = {
            "schema_version": "1.0",
            "ok": False,
            "operation": operation,
            "ticker": None,
            "source": "digrin" if operation == "dividends" else "yahoo_api",
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
            symbol = self._validate(operation, ticker, parameters)
            result.update(ticker=symbol, parameters=parameters)
            # Nonblocking admission prevents an unbounded queue of waiting requests.
            if not _PROVIDER_LOCK.acquire(blocking=False):
                result["error"] = {
                    "code": "busy",
                    "message": "Another local request is running; try again after it finishes.",
                }
                return result
            try:
                provider = self._ticker_factory(ticker=symbol)
                frame = self._fetch(provider, operation, parameters, result["warnings"])
            finally:
                _PROVIDER_LOCK.release()
            result["retrieved_at"] = self._clock().isoformat()
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
        return self._dividends(provider.digrin_dividend, warnings)

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
