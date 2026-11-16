"""统一入口：启动 Vue Web（FastAPI）或 CLI。"""

from __future__ import annotations

import logging
import sys

from linnea_agent.agent.builder import build_agent
from linnea_agent.chat.history import HistoryRepository
from linnea_agent.chat.service import ChatService
from linnea_agent.config import Settings
from linnea_agent.observability.usage import UsageTracker
from linnea_agent.shared.proxy import sanitize_proxy_bypass


def build_service(settings: Settings | None = None) -> ChatService:
    """组装依赖：配置 -> Agent -> 仓库 -> 服务。"""
    settings = settings or Settings.from_env()
    agent = build_agent(settings)
    repo = HistoryRepository(settings.history_dir)
    tracker = UsageTracker(settings.budget_limit)
    return ChatService(agent, repo, tracker)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


def _sanitize_proxy_bypass() -> None:
    """兼容旧调用点：清理 NO_PROXY 中 httpx 无法解析的 IPv6 方括号项。"""
    sanitize_proxy_bypass()


def run_web() -> None:
    """默认入口：启动 FastAPI，并托管 web/dist 中的 Vue 前端。"""
    from linnea_agent.api.app import run

    run()


def run_cli() -> None:
    _configure_logging()
    service = build_service()
    print("Linnea的个人Agent（输入 exit/quit 退出）")
    while True:
        task = input("\n> ").strip()
        if task.lower() in ("exit", "quit"):
            break
        if not task:
            continue
        result = service.run_turn(task, session_id="cli")
        print(f"\n[路由档位: {result.tier.value}]\n{result.reply}")


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_web()
