"""聊天域模型：档位枚举、路由关键词与消息角色映射。"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

CODING_KEYWORDS = ("代码", "函数", "写个", "实现", "bug", "调试", "python", "sql")
REASONING_KEYWORDS = ("分析", "推理", "比较", "权衡", "为什么", "设计")

ROLE_MAP: list[tuple[type[BaseMessage], str]] = [
    (HumanMessage, "user"),
    (SystemMessage, "system"),
    (ToolMessage, "tool"),
    (AIMessage, "assistant"),
]
PERSIST_ROLES = frozenset({"user", "assistant"})
ROLE_TO_CLS: dict[str, type[BaseMessage]] = {"user": HumanMessage, "assistant": AIMessage}


class Tier(StrEnum):
    FAST = "fast"
    BALANCED = "balanced"


def role_of(message: Any) -> str | None:
    for cls, role in ROLE_MAP:
        if isinstance(message, cls):
            return role
    return None
