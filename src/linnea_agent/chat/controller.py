"""对外接口适配：封装 Gradio 与 CLI 所需的调用签名。"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterator

from linnea_agent.chat.service import ChatService

log = logging.getLogger(__name__)

# Gradio 6.31 的 Prism 在渲染 ```c / ```cpp 代码块时会抛
# TypeError: Cannot set properties of undefined (setting 'class-name')，
# 前端因此永久停在“正在思考…”。展示时去掉语言标记，代码内容与排版不受影响。
_BROKEN_PRISM_LANGS = re.compile(
    r"```(?:c|cpp|c\+\+|cc|h|hpp)[ \t]*\r?\n", re.IGNORECASE
)


def _display_text(text: str) -> str:
    """返回适合 Gradio 展示的文本（仅影响前端，不改变持久化历史）。"""
    return _BROKEN_PRISM_LANGS.sub("```\n", text)


class ChatController:
    """将 ChatService 适配为 Web / CLI 可直接调用的处理函数。"""

    def __init__(self, service: ChatService):
        self.service = service

    def handle_chat(self, message: str, history: list, session_id: str = "web"):
        history = list(history or [])
        if not message.strip():
            return history, ""
        result = self.service.run_turn(message, session_id)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": _display_text(result.reply)})
        return history, f"本轮路由：**{result.tier.value}**"

    def handle_chat_stream(
        self, message: str, history: list, session_id: str = "web"
    ) -> Iterator[tuple[list, str]]:
        """先回显用户消息与“正在思考”，完成后再替换为该轮回答。"""
        history = list(history or [])
        if not message.strip():
            yield history, ""
            return

        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "正在思考…"})
        yield _snapshot(history), ""

        try:
            result = self.service.run_turn(message, session_id)
        except Exception as exc:  # noqa: BLE001 - 单轮失败不应让整个界面无响应
            log.exception("本轮对话失败")
            history[-1]["content"] = f"抱歉，这一轮出错了：{exc}"
            yield _snapshot(history), ""
            return

        history[-1]["content"] = _display_text(result.reply)
        yield _snapshot(history), f"本轮路由：**{result.tier.value}**"

    def handle_cli(self, task: str) -> None:
        result = self.service.run_turn(task, session_id="cli")
        print(f"\n[路由档位: {result.tier.value}]\n{result.reply}")


def _snapshot(history: list) -> list:
    """返回历史快照，避免 Gradio 因复用同一列表对象而漏刷。"""
    return [dict(item) if isinstance(item, dict) else item for item in history]
