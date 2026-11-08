"""用量追踪测试。"""

import pytest

from linnea_agent.observability.usage import BudgetExceeded, UsageTracker


def test_usage_accumulation():
    tracker = UsageTracker()
    tracker.record("deepseek-chat", 1000, 100)
    tracker.record("deepseek-chat", 2000, 200)

    assert tracker.calls == 2
    assert tracker.total_input_tokens == 3000
    assert tracker.total_output_tokens == 300
    assert tracker.total_cost > 0


def test_budget_not_exceeded_by_default():
    tracker = UsageTracker()
    tracker.record("deepseek-chat", 1000, 100)
    assert tracker.over_budget is False
    tracker.ensure_within_budget()  # 不应抛异常


def test_budget_exceeded():
    tracker = UsageTracker(budget_limit=0.0001)
    tracker.record("qwen-max", 1_000_000, 1_000_000)
    assert tracker.over_budget is True
    with pytest.raises(BudgetExceeded):
        tracker.ensure_within_budget()


def test_snapshot():
    tracker = UsageTracker()
    tracker.record("deepseek-chat", 1000, 100)
    snapshot = tracker.snapshot()
    assert snapshot["calls"] == 1
    assert snapshot["input_tokens"] == 1000
