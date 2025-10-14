"""Lightweight parsers for offline demos."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def load_goal(path: Path) -> Dict[str, Any]:
    """Parse the sample goal YAML without requiring external dependencies."""
    goal: str | None = None
    constraints: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("goal:"):
            goal = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("-"):
            constraints.append(stripped.split("-", 1)[1].strip())
    if goal is None:
        raise ValueError(f"Goal file {path} missing goal line")
    return {"goal": goal, "constraints": constraints}


__all__ = ["load_goal"]
