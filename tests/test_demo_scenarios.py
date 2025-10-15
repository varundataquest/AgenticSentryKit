from __future__ import annotations

import pytest

from demo_app.scenarios import SCENARIOS, build_run_and_policy
from sentrykit import GuardEngine


@pytest.mark.parametrize(
    "scenario,variant",
    [
        pytest.param(scenario, variant, id=f"{scenario.id}:{variant.key}")
        for scenario in SCENARIOS
        for variant in scenario.variants
        if variant.expected_blocked is not None
    ],
)
def test_demo_variants_align_with_expectations(scenario, variant) -> None:
    run_input, policy = build_run_and_policy(scenario, variant)
    verdict = GuardEngine(policy).evaluate(run_input)
    assert verdict.blocked == variant.expected_blocked
