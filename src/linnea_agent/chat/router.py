"""意图路由：按关键词将输入映射到模型档位。"""

from __future__ import annotations

from functools import lru_cache

from linnea_agent.chat.models import CODING_KEYWORDS, REASONING_KEYWORDS, Tier


@lru_cache(maxsize=256)
def decide_tier(task: str) -> Tier:
    """根据输入内容决定使用的模型档位。"""
    text = task.strip().lower()
    if any(keyword in text for keyword in CODING_KEYWORDS):
        return Tier.BALANCED
    if any(keyword in text for keyword in REASONING_KEYWORDS):
        return Tier.BALANCED
    return Tier.FAST
