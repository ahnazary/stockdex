"""Anthropic directory policy checks for the MCP tools.

The Software Directory Policy requires every tool to declare its title,
readOnlyHint and destructiveHint, keep names under 64 characters, and
describe exactly what it does.
"""

import pytest

pytest.importorskip("mcp")

import anyio  # noqa: E402

from stockdex.claude_mcp import create_server  # noqa: E402


@pytest.fixture(scope="module")
def tools():
    return anyio.run(create_server().list_tools)


def test_every_tool_declares_required_annotations(tools):
    assert len(tools) == 3
    for tool in tools:
        assert tool.title, tool.name
        assert tool.annotations.title == tool.title
        assert tool.annotations.read_only_hint is True
        assert tool.annotations.destructive_hint is False
        assert tool.annotations.open_world_hint is True


def test_tool_names_and_descriptions(tools):
    for tool in tools:
        assert len(tool.name) <= 64
        assert 40 <= len(tool.description) <= 600, tool.name
        # Each description names its data source.
        assert "Yahoo Finance" in tool.description or "Digrin" in tool.description
