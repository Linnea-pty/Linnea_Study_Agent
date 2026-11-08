"""对外接口适配：封装 Gradio 与 CLI 所需的调用签名。"""

from __future__ import annotations

from linnea_agent.chat.service import ChatService


class ChatController:
    """将 ChatService 适配为 Web / CLI 可直接调用的处理函数。"""

    def __init__(self, service: ChatService):
        self.service = service

    def handle_chat(self, message: str, history: list, session_id: str = "web"):
        if not message.strip():
            return history, ""
        result = self.service.run_turn(message, session_id)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": result.reply})
        return history, f"本轮路由：**{result.tier.value}**"

    def handle_cli(self, task: str) -> None:
        result = self.service.run_turn(task, session_id="cli")
        print(f"\n[路由档位: {result.tier.value}]\n{result.reply}")
