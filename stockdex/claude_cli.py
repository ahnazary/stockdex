"""JSON command-line entry point for local Claude Code Skills."""

import argparse
import sys

from stockdex.claude_adapter import (
    PRICE_RANGES,
    STATEMENTS,
    StockdexAdapter,
    encode_json,
)


def main(argv=None, adapter=None):
    parser = argparse.ArgumentParser(
        description="Read-only local Stockdex tools; results are JSON."
    )
    commands = parser.add_subparsers(dest="operation", required=True)
    for name in ("prices", "financial-statement", "dividends"):
        command = commands.add_parser(name)
        command.add_argument("ticker", help="Stock symbol, e.g. AAPL or BMW.DE")
        command.add_argument(
            "--limit", type=int, default=20, help="1–500 rows, newest first"
        )
        if name == "prices":
            command.add_argument("--range", choices=PRICE_RANGES, default="1mo")
        if name == "financial-statement":
            command.add_argument(
                "--statement", choices=STATEMENTS, default="income_statement"
            )
            command.add_argument(
                "--frequency", choices=("annual", "quarterly"), default="annual"
            )
            command.add_argument("--start-date")
            command.add_argument("--end-date")
            command.add_argument(
                "--metrics", nargs="+", help="Up to 20 unprefixed provider metric names"
            )
    arguments = vars(parser.parse_args(argv))
    operation = arguments.pop("operation")
    adapter = adapter or StockdexAdapter()
    methods = {
        "prices": adapter.get_prices,
        "financial-statement": adapter.get_financial_statement,
        "dividends": adapter.get_dividends,
    }
    result = methods[operation](**arguments)
    print(encode_json(result))
    if not result["ok"]:
        print(result["error"]["message"], file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
