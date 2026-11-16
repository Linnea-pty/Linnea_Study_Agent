"""聊天接口：健康检查、SSE 流式对话、历史读取。"""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from linnea_agent import __version__
from linnea_agent.api.schemas import ChatRequest, HealthResponse
from linnea_agent.chat.history import HistoryRepository

log = logging.getLogger(__name__)
router = APIRouter()


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    """以 SSE 返回一轮对话：status -> done | error。"""
    service = request.app.state.service

    async def generate():
        yield _sse("status", {"phase": "thinking"})
        try:
            result = await asyncio.to_thread(
                service.run_turn, payload.message, payload.session_id
            )
        except Exception as exc:  # noqa: BLE001 - 单轮失败要作为事件返回给前端
            log.exception("API 对话失败")
            yield _sse("error", {"message": str(exc)})
            return
        yield _sse(
            "done",
            {
                "reply": result.reply,
                "tier": result.tier.value,
                "session_id": payload.session_id,
            },
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/history/{session_id}")
async def history(session_id: str, request: Request) -> dict:
    repo: HistoryRepository = request.app.state.repo
    messages = repo.load(session_id)
    return {
        "session_id": session_id,
        "messages": [
            {"role": "assistant" if msg.type == "ai" else "user", "content": msg.content}
            for msg in messages
        ],
    }
