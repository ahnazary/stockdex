"""Run setup.py in isolation and inspect the arguments it passes to setuptools."""

import builtins
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest
import setuptools

ROOT = Path(__file__).resolve().parents[2]


def run_setup(monkeypatch, tmp_path, release_version=None):
    original = builtins.__import__

    def version_import(name, *args, **kwargs):
        if name == "__version__" and release_version is None:
            raise ModuleNotFoundError(
                "No development version module", name="__version__"
            )
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", version_import)
    if release_version:
        module = ModuleType("__version__")
        module.VERSION = release_version
        monkeypatch.setitem(sys.modules, "__version__", module)
    captured = {}
    monkeypatch.setattr(setuptools, "setup", lambda **kw: captured.update(kw))
    # Run from another directory to prove paths resolve relative to setup.py.
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(ROOT / "setup.py"), run_name="__main__")
    return captured


@pytest.fixture
def setup_kwargs(monkeypatch, tmp_path):
    return run_setup(monkeypatch, tmp_path)


@pytest.mark.parametrize("release_version", [None, "9.8.7"])
def test_version_fallback(monkeypatch, tmp_path, release_version):
    captured = run_setup(monkeypatch, tmp_path, release_version)
    assert captured["version"] == (release_version or "0.0.0+local")


def test_python_floor_matches_pandas(setup_kwargs):
    assert setup_kwargs["python_requires"] == ">=3.9"


def test_file_reads_declare_utf8():
    # Windows defaults to cp1252, which cannot decode bytes in README.md, so
    # every read_text()/open() in setup.py must name the encoding explicitly.
    import ast

    tree = ast.parse((ROOT / "setup.py").read_text(encoding="utf-8"))
    reads = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and getattr(node.func, "attr", getattr(node.func, "id", None))
        in ("read_text", "open")
    ]
    assert reads
    for call in reads:
        encodings = [k.value.value for k in call.keywords if k.arg == "encoding"]
        assert encodings == ["utf-8"], ast.unparse(call)


def test_cli_entry_point(setup_kwargs):
    scripts = setup_kwargs["entry_points"]["console_scripts"]
    assert "stockdex-claude=stockdex.claude_cli:main" in scripts


def test_mcp_is_optional(setup_kwargs):
    scripts = setup_kwargs["entry_points"]["console_scripts"]
    assert "stockdex-mcp=stockdex.claude_mcp:main" in scripts
    assert setup_kwargs["extras_require"] == {"mcp": ["mcp>=2.3,<3"]}
    assert not any(r.startswith("mcp") for r in setup_kwargs["install_requires"])
