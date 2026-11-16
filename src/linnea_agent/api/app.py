"""FastAPI 应用工厂：SSE 聊天接口 + 静态前端托管。"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from linnea_agent import __version__
from linnea_agent.agent.builder import build_agent
from linnea_agent.api.routes import chat
from linnea_agent.chat.history import HistoryRepository
from linnea_agent.chat.service import ChatService
from linnea_agent.config import Settings
from linnea_agent.observability.usage import UsageTracker
from linnea_agent.shared.proxy import sanitize_proxy_bypass

log = logging.getLogger(__name__)
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_WEB_DIST = _PROJECT_ROOT / "web" / "dist"


def create_app(
    service: ChatService | None = None,
    repo: HistoryRepository | None = None,
) -> FastAPI:
    """构建应用。测试可注入 `service` / `repo`，避免真实模型调用。"""
    sanitize_proxy_bypass()
    if service is None or repo is None:
        settings = Settings.from_env()
        if repo is None:
            repo = HistoryRepository(settings.history_dir)
        if service is None:
            service = ChatService(
                agent=build_agent(settings),
                repo=repo,
                tracker=UsageTracker(settings.budget_limit),
            )

    app = FastAPI(title="Linnea Agent API", version=__version__)
    app.state.service = service
    app.state.repo = repo

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat.router, prefix="/api")

    if _WEB_DIST.is_dir():
        app.mount("/", StaticFiles(directory=str(_WEB_DIST), html=True), name="web")
    return app


def run() -> None:
    """生产启动：`linnea-agent-api`。"""
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    run()
