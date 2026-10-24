"""Keep the Claude Code plugin manifest consistent with the Python package."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return json.loads((ROOT / path).read_text())


def test_plugin_manifest():
    plugin = load(".claude-plugin/plugin.json")
    assert plugin["name"] == "stockdex"
    assert plugin["license"] == "MIT"


def test_marketplace_lists_this_plugin():
    plugin = load(".claude-plugin/plugin.json")
    marketplace = load(".claude-plugin/marketplace.json")
    entries = {entry["name"]: entry for entry in marketplace["plugins"]}
    assert entries[plugin["name"]]["source"] == "./"


def test_mcp_server_launches_published_entry_point():
    plugin = load(".claude-plugin/plugin.json")
    server = load(".mcp.json")["mcpServers"]["stockdex"]
    assert server["command"] == "uvx"
    # The plugin requires a stockdex release that ships the MCP server.
    assert server["args"] == [
        "--from",
        f"stockdex[mcp]>={plugin['version']}",
        "stockdex-mcp",
    ]
