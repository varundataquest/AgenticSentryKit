import importlib
from pathlib import Path

import pytest


MODULES = [
    "examples.openai_agents_demo.demo",
    "examples.langchain_demo.demo",
    "examples.autogen_demo.demo",
    "examples.crewai_demo.demo",
    "examples.strands_demo.demo",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_demo_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, module_name: str) -> None:
    monkeypatch.setenv("SENTRYKIT_DEMO_RUNS_DIR", str(tmp_path))
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name: str, *args, **kwargs):  # type: ignore[override]
        if name in {"autogen", "crewai", "strands", "aws_strands"}:
            return object()
        return original_find_spec(name, *args, **kwargs)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    module = importlib.import_module(module_name)
    run_callable = getattr(module, "run_demo", None) or getattr(module, "main")
    run_callable()
    reports = list(Path(tmp_path).rglob("report.html"))
    assert reports, f"expected report written for {module_name}"
