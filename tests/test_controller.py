"""ChatController 的流式回显与错误兜底测试。"""

from __future__ import annotations

from linnea_agent.chat.controller import ChatController
from linnea_agent.chat.service import TurnResult
from linnea_agent.shared.tier import Tier


class FakeService:
    def __init__(self, reply: str = "答案", error: Exception | None = None):
        self.reply = reply
        self.error = error

    def run_turn(self, task: str, session_id: str) -> TurnResult:
        if self.error is not None:
            raise self.error
        return TurnResult(reply=self.reply, tier=Tier.BALANCED)


def test_stream_shows_thinking_then_answer():
    controller = ChatController(FakeService(reply="```python\nprint(1)\n```"))
    frames = list(controller.handle_chat_stream("做题", []))

    assert len(frames) == 2
    first_history, _ = frames[0]
    assert first_history[-1] == {"role": "assistant", "content": "正在思考…"}
    final_history, tier = frames[1]
    assert final_history[-1]["content"].startswith("```python")
    assert "balanced" in tier


def test_stream_turns_exception_into_message():
    controller = ChatController(FakeService(error=RuntimeError("boom")))
    frames = list(controller.handle_chat_stream("做题", []))

    final_history, _ = frames[-1]
    assert "出错了" in final_history[-1]["content"]
    assert "boom" in final_history[-1]["content"]


def test_stream_ignores_blank_message():
    controller = ChatController(FakeService())
    frames = list(controller.handle_chat_stream("   ", []))

    assert frames == [([], "")]
