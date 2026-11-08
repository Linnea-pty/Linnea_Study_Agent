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
        reply = result["messages"][-1].content

        messages.append(AIMessage(content=reply))
        self.repo.save(session_id, messages)
        return TurnResult(reply=reply, tier=tier)
