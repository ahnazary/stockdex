"""The MCP server must fail clearly, without touching stdout, when the extra is absent."""

import builtins

from stockdex.claude_mcp import main


def test_optional_mcp_missing(monkeypatch, capsys):
    original = builtins.__import__

    def without_mcp(name, *args, **kwargs):
        if name == "mcp" or name.startswith("mcp."):
            raise ModuleNotFoundError("MCP intentionally unavailable", name="mcp")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_mcp)
    assert main() == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert ".[mcp]" in captured.err
