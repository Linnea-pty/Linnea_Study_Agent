"""统一入口：启动 Gradio Web 或 CLI。"""

from __future__ import annotations

import logging
import os
import sys
import urllib.request

from linnea_agent.agent.builder import build_agent
from linnea_agent.chat.controller import ChatController
from linnea_agent.chat.history import HistoryRepository
from linnea_agent.chat.service import ChatService
from linnea_agent.config import Settings
from linnea_agent.observability.usage import UsageTracker


def build_controller(settings: Settings | None = None) -> ChatController:
    """组装依赖：配置 -> Agent -> 仓库 -> 服务 -> 控制器。"""
    settings = settings or Settings.from_env()
    agent = build_agent(settings)
    repo = HistoryRepository(settings.history_dir)
    tracker = UsageTracker(settings.budget_limit)
    return ChatController(ChatService(agent, repo, tracker))


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def _sanitize_proxy_bypass() -> None:
    """清理 NO_PROXY 中 httpx 无法解析的 IPv6 方括号项，避免 Gradio 导入失败。

    Windows 系统代理例外列表常含 ``[::1]``，httpx 会把它当成非法端口
    （``Invalid port: ':1]'``），导致 ``import gradio`` 直接抛错。
    """
    raw = os.environ.get("NO_PROXY") or os.environ.get("no_proxy")
    if not raw:
        raw = str(urllib.request.getproxies().get("no", ""))
    entries = [
        item.strip()
        for item in raw.split(",")
        if item.strip() and not item.strip().startswith("[")
    ]
    value = ",".join(entries)
    os.environ["NO_PROXY"] = value
    os.environ["no_proxy"] = value


def run_web() -> None:
    _sanitize_proxy_bypass()
    import gradio as gr

    _configure_logging()
    controller = build_controller()

    with gr.Blocks(title="多模型Agent") as demo:
        gr.Markdown("# Linnea 的多模型个人 Agent")
        chatbot = gr.Chatbot(height=620)
        msg = gr.Textbox(placeholder="输入你的问题...", label="消息")
        tier_md = gr.Markdown()
        clear = gr.Button("清空会话")

        msg.submit(controller.handle_chat_stream, [msg, chatbot], [chatbot, tier_md])
        msg.submit(lambda: "", None, msg)
        clear.click(lambda: ([], "", ""), None, [chatbot, msg, tier_md])

    demo.queue()
    demo.launch()


def run_cli() -> None:
    _configure_logging()
    controller = build_controller()
    print("Linnea的个人Agent（输入 exit/quit 退出）")
    while True:
        task = input("\n> ").strip()
        if task.lower() in ("exit", "quit"):
            break
        if not task:
            continue
        controller.handle_cli(task)


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_web()
