"""ChatService 编排集成测试（使用假 Agent，不联网）。"""

from langchain_core.messages import AIMessage, HumanMessage

from linnea_agent.chat.history import HistoryRepository
from linnea_agent.chat.service import ChatService
from linnea_agent.observability.usage import UsageTracker
from linnea_agent.shared.tier import Tier


class FakeAgent:
    def invoke(self, input, context=None, config=None):
        return {"messages": [HumanMessage(content="input"), AIMessage(content="你好！")]}


def test_run_turn_round_trip(tmp_path):
    service = ChatService(FakeAgent(), HistoryRepository(tmp_path), UsageTracker())
    result = service.run_turn("你好", "web")

    assert result.reply == "你好！"
    assert result.tier is Tier.FAST

    loaded = HistoryRepository(tmp_path).load("web")
    assert [message.content for message in loaded] == ["你好", "你好！"]


class ListContentAgent:
    def invoke(self, input, context=None, config=None):
        return {
            "messages": [
                AIMessage(
                    content=[
                        {"type": "text", "text": "第一段"},
                        {"type": "text", "text": "第二段"},
                    ]
                )
            ]
        }


def test_run_turn_flattens_content_blocks(tmp_path):
    service = ChatService(ListContentAgent(), HistoryRepository(tmp_path), UsageTracker())
    assert service.run_turn("你好", "web").reply == "第一段第二段"
