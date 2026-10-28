"""Keep the plugin skill's metric reference in sync with stockdex.config."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "plugins" / "stockdex" / "skills" / "stockdex"


def load_generator():
    path = ROOT / "scripts" / "generate_skill_metrics.py"
    spec = importlib.util.spec_from_file_location("generate_skill_metrics", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_metrics_reference_is_current():
    expected = load_generator().render()
    actual = (SKILL / "reference" / "metrics.md").read_text()
    assert actual == expected, "run: python scripts/generate_skill_metrics.py"


def test_skill_frontmatter():
    text = (SKILL / "SKILL.md").read_text()
    assert text.startswith("---\nname: stockdex\ndescription: ")
    assert "disable-model-invocation" not in text


def test_skill_default_metrics_match_adapter():
    from stockdex.claude_adapter import DEFAULT_METRICS

    text = (SKILL / "SKILL.md").read_text()
    for statement, metrics in DEFAULT_METRICS.items():
        line = next(
            row for row in text.splitlines() if row.startswith(f"- `{statement}`")
        )
        assert all(f"`{m}`" in line for m in metrics)
