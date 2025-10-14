from __future__ import annotations

import pytest

from sentrykit.adapters.langchain import SentryKitCallback
from sentrykit.errors import PolicyViolationError
from sentrykit import GuardEngine, Policy


def test_langchain_callback_blocks_goal_drift() -> None:
    policy = Policy(block_on={"goal_drift"}, min_pay_threshold=5000)
    engine = GuardEngine(policy)
    callback = SentryKitCallback(policy, engine)
    callback.on_chain_start({}, {"goal": "Find Austin internship paying $5,000", "constraints": ["Austin only"]})
    with pytest.raises(PolicyViolationError):
        callback.on_chain_end({"output_text": "Here is a Dallas internship paying $5,500"})
