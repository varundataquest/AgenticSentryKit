"""Offline OpenAI Agents style demonstration."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from sentrykit import GuardEngine, Policy
from sentrykit.models import Claim, ContextChunk, Extraction, RunInput, RunOutput, ToolCall
from examples.common import load_goal

BASE_DIR = Path(__file__).resolve().parent.parent
COMMON = BASE_DIR / "common"
HTML_DIR = COMMON / "sample_html"
DEFAULT_RUNS_DIR = Path(__file__).resolve().parent / "runs"


def resolve_runs_dir() -> Path:
    env_value = os.environ.get("SENTRYKIT_DEMO_RUNS_DIR")
    if env_value:
        path = Path(env_value).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path
    DEFAULT_RUNS_DIR.mkdir(exist_ok=True)
    return DEFAULT_RUNS_DIR


def load_demo_goal() -> Dict[str, Any]:
    return load_goal(COMMON / "sample_goal.yaml")


def load_context_poisoned() -> ContextChunk:
    with open(COMMON / "sample_context.txt", "r", encoding="utf-8") as handle:
        return ContextChunk(source="poisoned.txt", text=handle.read())


def pass_case(engine: GuardEngine) -> None:
    html_path = HTML_DIR / "company_austin_job.html"
    goal = load_demo_goal()
    with open(html_path, "r", encoding="utf-8") as handle:
        html = handle.read()
    claim = Claim(
        statement="MetroTech Austin internship pays $5,500 per month",
        evidence_urls=[f"file://{html_path}"],
        extraction=Extraction(kind="contains", pattern="Compensation", must_include="$5,500"),
    )
    run = RunInput(
        goal=goal["goal"],
        constraints=list(goal["constraints"]),
        messages=[("user", goal["goal"])],
        contexts=[ContextChunk(source="listing", text=html)],
        tool_calls=[ToolCall(name="job_scraper", args={"url": str(html_path)})],
        output=RunOutput(text="Found MetroTech Austin internship with $5,500 monthly pay.", claims=[claim]),
    )
    verdict = engine.evaluate(run)
    runs_dir = resolve_runs_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S_pass")
    out_dir = runs_dir / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    if verdict.report:
        verdict.report.to_html(str(out_dir / "report.html"))
    print("PASS verdict:", verdict.reason, verdict.score)


def block_case(engine: GuardEngine) -> None:
    goal = load_demo_goal()
    contexts = [load_context_poisoned()]
    run = RunInput(
        goal=goal["goal"],
        constraints=list(goal["constraints"]),
        messages=[("user", goal["goal"])],
        contexts=contexts,
        tool_calls=[ToolCall(name="job_scraper", args={"url": "https://example.com/dallas"})],
        output=RunOutput(text="Here is a Dallas internship paying $4,000 per month."),
    )
    verdict = engine.evaluate(run)
    runs_dir = resolve_runs_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S_block")
    out_dir = runs_dir / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    if verdict.report:
        verdict.report.to_html(str(out_dir / "report.html"))
    print("BLOCK verdict:", verdict.reason, verdict.score)


def main() -> None:
    policy = Policy(
        allowed_tool_names={"job_scraper"},
        allowed_url_domains={"file", "example.com"},
        block_on={"goal_drift", "hallucination", "context_poisoning", "tool_firewall", "data_leak"},
        min_pay_threshold=5000,
        min_company_size=50,
    )
    engine = GuardEngine(policy)
    pass_case(engine)
    block_case(engine)


if __name__ == "__main__":
    main()
