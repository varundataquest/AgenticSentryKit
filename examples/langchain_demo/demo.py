"""Offline LangChain callback demonstration."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from sentrykit import GuardEngine, Policy
from sentrykit.adapters.langchain import SentryKitCallback
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


def load_demo_goal() -> dict:
    return load_goal(COMMON / "sample_goal.yaml")


def run_demo() -> None:
    goal = load_demo_goal()
    policy = Policy(
        allowed_tool_names={"job_scraper"},
        allowed_url_domains={"file"},
        block_on={"goal_drift", "hallucination", "context_poisoning"},
        min_pay_threshold=5000,
        min_company_size=50,
    )
    engine = GuardEngine(policy)
    callback = SentryKitCallback(policy, engine)

    # simulate retriever output
    with open(HTML_DIR / "company_austin_job.html", "r", encoding="utf-8") as handle:
        html = handle.read()
    callback.on_retriever_end([type("Doc", (), {"metadata": {"source": "listing"}, "page_content": html})()])

    claim = Claim(
        statement="MetroTech Austin internship pays $5,500 per month",
        evidence_urls=[f"file://{HTML_DIR / 'company_austin_job.html'}"],
        extraction=Extraction(kind="contains", pattern="Compensation", must_include="$5,500"),
    )

    outputs = {"output_text": "Found MetroTech Austin internship with $5,500 monthly pay.", "claims": [claim]}
    callback.on_chain_start({}, {"goal": goal["goal"], "constraints": goal["constraints"]})
    callback.on_chain_end(outputs)

    verdict = engine.evaluate(
        RunInput(
            goal=goal["goal"],
            constraints=list(goal["constraints"]),
            messages=[("user", goal["goal"])],
            contexts=[ContextChunk(source="listing", text=html)],
            tool_calls=[ToolCall(name="job_scraper", args={"url": str(HTML_DIR / 'company_austin_job.html')})],
            output=RunOutput(text=outputs["output_text"], claims=[claim]),
        )
    )
    runs_dir = resolve_runs_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S_langchain")
    out_dir = runs_dir / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    if verdict.report:
        verdict.report.to_html(str(out_dir / "report.html"))
    print("LangChain demo verdict:", verdict.reason, verdict.score)


if __name__ == "__main__":
    run_demo()
