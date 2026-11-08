"""路由准确率离线评估：golden 问答对。"""

from __future__ import annotations

from dataclasses import dataclass

from linnea_agent.chat.router import decide_tier
from linnea_agent.shared.tier import Tier


@dataclass(frozen=True, slots=True)
class EvalCase:
    query: str
    expected: Tier


EVAL_CASES: list[EvalCase] = [
    EvalCase("帮我写个 Python 函数", Tier.BALANCED),
    EvalCase("这段代码有 bug 帮我调试", Tier.BALANCED),
    EvalCase("写个 SQL 查询", Tier.BALANCED),
    EvalCase("分析一下为什么这么设计", Tier.BALANCED),
    EvalCase("比较这两种方案的权衡", Tier.BALANCED),
    EvalCase("你好", Tier.FAST),
    EvalCase("今天几号", Tier.FAST),
    EvalCase("1+1 等于几", Tier.FAST),
]


def evaluate_router() -> tuple[float, list[EvalCase]]:
    """返回路由准确率与预测错误的用例。"""
    errors = [case for case in EVAL_CASES if decide_tier(case.query) is not case.expected]
    accuracy = 1 - len(errors) / len(EVAL_CASES)
    return accuracy, errors
