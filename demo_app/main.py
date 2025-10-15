"""
FastAPI application that powers the interactive SentryKit demo UI.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from sentrykit import GuardEngine

from .scenarios import SCENARIOS, Scenario, build_run_and_policy, scenario_index

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = Path(os.environ.get("SENTRYKIT_DEMO_REPORTS_DIR", BASE_DIR / "generated_reports"))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SentryKit Demo", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class EvaluateRequest(BaseModel):
    scenario_id: str
    variant_key: str


def _get_scenario(scenario_id: str) -> Scenario:
    for scenario in SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    raise HTTPException(status_code=404, detail=f"Unknown scenario '{scenario_id}'")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render landing page with scenario cards."""

    context = {
        "request": request,
        "scenario_index": json.dumps(scenario_index()),
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/evaluate")
async def evaluate(request: EvaluateRequest) -> JSONResponse:
    """Evaluate a scenario variant and return guard verdict metadata."""

    scenario = _get_scenario(request.scenario_id)
    try:
        variant = scenario.variant(request.variant_key)
    except KeyError as exc:  # pragma: no cover - validated in tests
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    run_input, policy = build_run_and_policy(scenario, variant)
    engine = GuardEngine(policy)
    verdict = engine.evaluate(run_input)

    report_id = uuid4().hex
    report_path = REPORTS_DIR / f"{report_id}.html"
    if verdict.report:
        report_path.write_text(verdict.report.html, encoding="utf-8")
    else:  # pragma: no cover - engine always sets report, defensive
        report_path.write_text("<p>No report available.</p>", encoding="utf-8")

    findings = [
        {
            "kind": finding.kind,
            "severity": finding.severity,
            "details": finding.details,
            "evidence": finding.evidence,
        }
        for finding in verdict.findings
    ]
    response: Dict[str, Any] = {
        "blocked": verdict.blocked,
        "reason": verdict.reason,
        "score": verdict.score,
        "findings": findings,
        "report_url": f"/reports/{report_id}.html",
        "scenario": {"id": scenario.id, "title": scenario.title, "variant": variant.label},
    }
    if variant.expected_blocked is not None:
        response["expected_blocked"] = variant.expected_blocked
    return JSONResponse(response)


@app.get("/reports/{report_name}")
async def get_report(report_name: str) -> FileResponse:
    """Serve rendered HTML reports."""

    safe_name = report_name if report_name.endswith(".html") else f"{report_name}.html"
    report_path = REPORTS_DIR / safe_name
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report_path)
