"""意图路由：按关键词将输入映射到模型档位。"""

from __future__ import annotations

from functools import lru_cache

from linnea_agent.shared.tier import Tier

_CODING_KEYWORDS = ("代码", "函数", "写个", "实现", "bug", "调试", "python", "sql")
_REASONING_KEYWORDS = ("分析", "推理", "比较", "权衡", "为什么", "设计")


@lru_cache(maxsize=256)
def decide_tier(task: str) -> Tier:
    """根据输入内容决定使用的模型档位。"""
    text = task.strip().lower()
    if any(keyword in text for keyword in _CODING_KEYWORDS):
        return Tier.BALANCED
    if any(keyword in text for keyword in _REASONING_KEYWORDS):
        return Tier.BALANCED
    return Tier.FAST
