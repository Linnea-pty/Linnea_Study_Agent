"""聊天编排：预算检查 -> 加载历史 -> 路由 -> 调用 Agent -> 落盘。"""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage

from linnea_agent.agent.middleware import AgentContext
from linnea_agent.chat.history import HistoryRepository
from linnea_agent.chat.router import decide_tier
from linnea_agent.observability.callback import UsageCallbackHandler
from linnea_agent.observability.usage import UsageTracker
from linnea_agent.shared.tier import Tier


@dataclass(frozen=True, slots=True)
class TurnResult:
    """单轮对话结果。"""

    reply: str
    tier: Tier


class ChatService:
    """编排单轮对话，并持久化会话历史与用量。"""

    def __init__(self, agent, repo: HistoryRepository, tracker: UsageTracker | None = None):
        self.agent = agent
        self.repo = repo
        self.tracker = tracker

    def run_turn(self, task: str, session_id: str) -> TurnResult:
        if self.tracker is not None:
            self.tracker.ensure_within_budget()

        messages = self.repo.load(session_id)
        messages.append(HumanMessage(content=task))
        tier = decide_tier(task)

        config = {"callbacks": [UsageCallbackHandler(self.tracker)]} if self.tracker else None
        result = self.agent.invoke(
            {"messages": messages},
            context=AgentContext(tier=tier),
            config=config,
        )
        reply = _content_text(result["messages"][-1].content)
        if not reply:
            reply = "（模型没有返回内容，请重试。）"

        messages.append(AIMessage(content=reply))
        self.repo.save(session_id, messages)
        return TurnResult(reply=reply, tier=tier)


def _content_text(content: object) -> str:
    """把模型返回的 content（字符串或多模态块列表）统一成文本。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        return "".join(parts)
    return "" if content is None else str(content)
