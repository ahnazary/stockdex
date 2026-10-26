import asyncio
import json
import os
import sys
import threading
from pathlib import Path

import pytest

pytest.importorskip("mcp")
import anyio  # noqa: E402
from mcp import ClientSession  # noqa: E402
from mcp.client.stdio import StdioServerParameters, stdio_client  # noqa: E402


def test_stdio_tools(tmp_path):
    async def exercise():
        root = Path(__file__).resolve().parents[2]
        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(root / "tests" / "claude" / "stdio_fixture_server.py")],
            cwd=tmp_path,
            env={**os.environ, "PYTHONPATH": str(root)},
        )
        with anyio.fail_after(45):
            async with stdio_client(parameters) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    listing = await session.list_tools()
                    assert {t.name for t in listing.tools} == {
                        "get_prices",
                        "get_financial_statement",
                        "get_dividends",
                    }
                    for tool in listing.tools:
                        assert tool.annotations.read_only_hint is True
                        assert tool.annotations.destructive_hint is False
                        limit_schema = tool.input_schema["properties"]["limit"]
                        assert limit_schema["minimum"] == 1
                        assert limit_schema["maximum"] == 500
                    for name in (
                        "get_prices",
                        "get_financial_statement",
                        "get_dividends",
                    ):
                        result = await session.call_tool(name, {"ticker": "AAPL"})
                        assert not result.is_error
                        assert result.structured_content["ok"]
                        assert (
                            json.loads(result.content[0].text)
                            == result.structured_content
                        )
                    error = await session.call_tool(
                        "get_prices", {"ticker": "https://bad"}
                    )
                    assert error.is_error
                    assert error.structured_content["error"]["code"] == "invalid_input"

    anyio.run(exercise)


def test_overlap_is_rejected_without_queuing():
    from stockdex.claude_mcp import create_server

    started, release = threading.Event(), threading.Event()

    class SlowAdapter:
        def get_prices(self, **kwargs):
            started.set()
            assert release.wait(timeout=10)
            return {"ok": True, "records": []}

    async def exercise():
        server = create_server(SlowAdapter())
        results = []

        async def first():
            results.append(await server.call_tool("get_prices", {"ticker": "AAPL"}))

        with anyio.fail_after(15):
            async with anyio.create_task_group() as group:
                group.start_soon(first)
                try:
                    while not started.is_set():
                        await anyio.sleep(0.01)
                    busy = await server.call_tool("get_prices", {"ticker": "AAPL"})
                    assert busy.is_error
                    assert busy.structured_content["error"]["code"] == "busy"
                finally:
                    release.set()
            assert not results[0].is_error

    anyio.run(exercise)


def test_legacy_stdio_handshake(tmp_path):
    """Check wire compatibility with Desktop clients using the 2025 revision."""

    async def exercise():
        root = Path(__file__).resolve().parents[2]
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(root / "tests" / "claude" / "stdio_fixture_server.py"),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            cwd=tmp_path,
            env={**os.environ, "PYTHONPATH": str(root)},
        )

        async def send(message):
            process.stdin.write((json.dumps(message) + "\n").encode())
            await process.stdin.drain()

        async def receive(request_id):
            while True:
                line = await asyncio.wait_for(process.stdout.readline(), timeout=15)
                assert line, "MCP server exited before responding"
                # Every stdout line must be protocol JSON, never diagnostics.
                message = json.loads(line)
                if message.get("id") == request_id:
                    return message

        try:
            await send(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "offline-test", "version": "1.0"},
                    },
                }
            )
            initialized = await receive(1)
            assert initialized["result"]["protocolVersion"] == "2025-11-25"
            await send({"jsonrpc": "2.0", "method": "notifications/initialized"})
            await send(
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
            )
            assert len((await receive(2))["result"]["tools"]) == 3
            await send(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "get_prices",
                        "arguments": {"ticker": "AAPL"},
                    },
                }
            )
            result = (await receive(3))["result"]
            assert not result.get("isError", False)
            assert result["structuredContent"]["ok"]
        finally:
            process.stdin.close()
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()

    asyncio.run(exercise())
