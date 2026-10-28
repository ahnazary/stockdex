"""Keep the Claude Code plugin consistent with the Python package and directory rules."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "stockdex"


def load(path):
    return json.loads(path.read_text())


def test_plugin_manifest():
    plugin = load(PLUGIN / ".claude-plugin" / "plugin.json")
    assert plugin["name"] == "stockdex"
    assert plugin["license"] == "MIT"


def test_marketplace_lists_this_plugin():
    plugin = load(PLUGIN / ".claude-plugin" / "plugin.json")
    marketplace = load(ROOT / ".claude-plugin" / "marketplace.json")
    entries = {entry["name"]: entry for entry in marketplace["plugins"]}
    assert entries[plugin["name"]]["source"] == "./plugins/stockdex"


def test_mcp_server_launches_exactly_pinned_release():
    # The plugin directory blocks package launchers that use a version range.
    plugin = load(PLUGIN / ".claude-plugin" / "plugin.json")
    server = load(PLUGIN / ".mcp.json")["mcpServers"]["stockdex"]
    assert server["command"] == "uvx"
    assert server["args"] == [
        "--from",
        f"stockdex[mcp]=={plugin['version']}",
        "stockdex-mcp",
    ]


def test_plugin_folder_is_self_contained():
    # People who install the plugin get only this folder.
    readme = (PLUGIN / "README.md").read_text()
    prose = re.sub(r"```.*?```", "", readme, flags=re.S)
    assert len(prose.split()) >= 40
    assert (PLUGIN / "LICENSE").read_text().startswith("MIT License")
    for path in PLUGIN.rglob("*"):
        assert path.name not in {".DS_Store", "Thumbs.db", "desktop.ini"}
        if path.is_file():
            assert path.stat().st_size < 256 * 1024, path
