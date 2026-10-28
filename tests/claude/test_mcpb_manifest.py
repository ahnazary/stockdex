"""Keep the Claude Desktop extension (.mcpb) manifest consistent."""

import ast
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "mcpb"


def manifest():
    return json.loads((BUNDLE / "manifest.json").read_text())


def pyproject_value(key):
    text = (BUNDLE / "pyproject.toml").read_text()
    return re.search(rf"^{key} = (.+)$", text, re.MULTILINE).group(1)


def test_uv_server_points_at_entry_point():
    server = manifest()["server"]
    assert server["type"] == "uv"
    assert (BUNDLE / server["entry_point"]).is_file()
    assert server["entry_point"] in server["mcp_config"]["args"]


def test_versions_are_in_sync():
    version = manifest()["version"]
    plugin = json.loads(
        (ROOT / "plugins" / "stockdex" / ".claude-plugin" / "plugin.json").read_text()
    )
    assert plugin["version"] == version
    assert ast.literal_eval(pyproject_value("version")) == version
    assert f'"stockdex[mcp]=={version}"' in (BUNDLE / "pyproject.toml").read_text()


def test_declared_tools_match_server():
    pytest.importorskip("mcp")
    import anyio

    from stockdex.claude_mcp import create_server

    declared = {tool["name"] for tool in manifest()["tools"]}
    registered = {tool.name for tool in anyio.run(create_server().list_tools)}
    assert declared == registered


def test_icon_exists():
    assert (BUNDLE / manifest()["icon"]).read_bytes().startswith(b"\x89PNG")
