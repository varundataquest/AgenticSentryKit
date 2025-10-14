"""Offline CrewAI integration demo."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from sentrykit import GuardEngine, Policy
from sentrykit.adapters.crewai import run_with_guard
from sentrykit.models import ContextChunk, RunInput, RunOutput, ToolCall
from examples.common import load_goal

BASE_DIR = Path(__file__).resolve().parent.parent
COMMON = BASE_DIR / "common"
DEFAULT_RUNS_DIR = Path(__file__).resolve().parent / "runs"


def resolve_runs_dir() -> Path:
    env_value = os.environ.get("SENTRYKIT_DEMO_RUNS_DIR")
    if env_value:
        path = Path(env_value).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path
    DEFAULT_RUNS_DIR.mkdir(exist_ok=True)
    return DEFAULT_RUNS_DIR


def load_demo_goal() -> dict:
    return load_goal(COMMON / "sample_goal.yaml")


class DummyCrew:
    def __init__(self, output: str) -> None:
        self.output = output
        self.goal = "Offline CrewAI demo"
        self.constraints = []
        self.history = []
        self.tool_calls = [{"name": "job_scraper", "args": {"url": "https://example.com"}}]
        self.contexts = [{"source": "crew", "text": "Austin references"}]

    def run(self, *args, **kwargs):
        self.history.append({"role": "assistant", "content": self.output})
        return {"output": self.output}


def run_demo() -> None:
    goal = load_demo_goal()
    policy = Policy(
        allowed_tool_names={"job_scraper"},
        allowed_url_domains={"example.com"},
        block_on={"goal_drift", "context_poisoning"},
        min_pay_threshold=5000,
    )
    engine = GuardEngine(policy)

    blocked_crew = DummyCrew("Dallas internship paying $4,000")
    try:
        run_with_guard(blocked_crew, policy, engine)
    except Exception as exc:
        print("CrewAI demo blocked:", exc)

    allowed_crew = DummyCrew("Austin internship paying $5,500 per month in Summer 2026 with 200 employees.")
    result = run_with_guard(allowed_crew, policy, engine)

    run = RunInput(
        goal=goal["goal"],
        constraints=list(goal["constraints"]),
        messages=allowed_crew.history,
        contexts=[ContextChunk(source=ctx["source"], text=ctx["text"]) for ctx in allowed_crew.contexts],
        tool_calls=[ToolCall(name=call["name"], args=call["args"]) for call in allowed_crew.tool_calls],
        output=RunOutput(text=result.get("output", "")),
    )
    verdict = engine.evaluate(run)
    runs_dir = resolve_runs_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S_crewai")
    out_dir = runs_dir / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    if verdict.report:
        verdict.report.to_html(str(out_dir / "report.html"))
    print("CrewAI demo verdict:", verdict.reason, verdict.score)


if __name__ == "__main__":
    run_demo()
