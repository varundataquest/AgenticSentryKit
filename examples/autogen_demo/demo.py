"""Offline AutoGen integration demo."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from sentrykit import GuardEngine, Policy
from sentrykit.adapters.autogen import register_reply
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


class DummyAgent:
    def __init__(self, message: str) -> None:
        self.message = message
        self.goal = "Offline AutoGen demo"
        self.context = ""
        self.tool_calls = [{"name": "job_scraper", "args": {"url": "https://example.com"}}]

    def reply(self, *args, **kwargs):
        return {"content": self.message}


def run_demo() -> None:
    goal = load_demo_goal()
    policy = Policy(
        allowed_tool_names={"job_scraper"},
        allowed_url_domains={"example.com"},
        block_on={"goal_drift", "context_poisoning"},
        min_pay_threshold=5000,
    )
    engine = GuardEngine(policy)
    agent = DummyAgent("Here is a Dallas listing paying $4,000 per month.")

    register_reply(agent, policy, engine)
    try:
        agent.reply()
    except Exception as exc:
        print("AutoGen demo blocked:", exc)

    agent_good = DummyAgent("Austin internship paying $5,500 per month in Summer 2026.")
    agent_good.tool_calls = [{"name": "job_scraper", "args": {"url": "https://example.com"}}]
    register_reply(agent_good, policy, engine)
    result = agent_good.reply()
    run = RunInput(
        goal=goal["goal"],
        constraints=list(goal["constraints"]),
        messages=[("assistant", result["content"])],
        contexts=[ContextChunk(source="autogen", text="")],
        tool_calls=[ToolCall(name="job_scraper", args={"url": "https://example.com"})],
        output=RunOutput(text=result["content"]),
    )
    verdict = engine.evaluate(run)
    runs_dir = resolve_runs_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S_autogen")
    out_dir = runs_dir / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    if verdict.report:
        verdict.report.to_html(str(out_dir / "report.html"))
    print("AutoGen demo verdict:", verdict.reason, verdict.score)


if __name__ == "__main__":
    run_demo()
