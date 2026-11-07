"""聊天编排：加载历史 -> 路由 -> 调用 Agent -> 落盘。"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from linnea_agent.agent.middleware import AgentContext
from linnea_agent.chat.repository import HistoryRepository
from linnea_agent.chat.router import decide_tier


class ChatService:
    """编排单轮对话，并持久化会话历史。"""

    def __init__(self, agent, repo: HistoryRepository):
        self.agent = agent
        self.repo = repo

    def run_turn(self, task: str, session_id: str) -> tuple[str, str]:
        messages = self.repo.load(session_id)
        messages.append(HumanMessage(content=task))
        tier = decide_tier(task)

        result = self.agent.invoke(
            {"messages": messages},
            context=AgentContext(tier=tier.value),
        )
        reply = result["messages"][-1].content

        messages.append(AIMessage(content=reply))
        self.repo.save(session_id, messages)
        return reply, tier.value
