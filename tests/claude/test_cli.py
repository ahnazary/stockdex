"""Offline tests for the JSON CLI used by the Claude Code Skill."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from stockdex.claude_cli import main


@pytest.mark.parametrize(
    "command,method",
    [
        ("prices", "get_prices"),
        ("financial-statement", "get_financial_statement"),
        ("dividends", "get_dividends"),
    ],
)
def test_cli_matches_adapter(adapter, capsys, command, method):
    assert main([command, "AAPL"], adapter=adapter) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == getattr(adapter, method)("AAPL")
    assert not captured.err


def test_cli_error(adapter, capsys):
    assert main(["prices", "../AAPL"], adapter=adapter) == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)["error"]["code"] == "invalid_input"
    assert captured.err


def test_cli_parse_error(adapter, capsys):
    with pytest.raises(SystemExit) as error:
        main(["prices", "AAPL", "--range", "max"], adapter=adapter)
    assert error.value.code == 2
    assert not capsys.readouterr().out


def test_help_subprocess_outside_checkout(tmp_path):
    root = Path(__file__).resolve().parents[2]
    process = subprocess.run(
        [sys.executable, "-m", "stockdex.claude_cli", "--help"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(root)},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert process.returncode == 0
    assert "financial-statement" in process.stdout
