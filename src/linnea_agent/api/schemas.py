"""API 请求 / 响应模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field

_SESSION_PATTERN = r"^[A-Za-z0-9_-]{1,64}$"


class ChatRequest(BaseModel):
    """一轮对话请求。"""

    message: str = Field(min_length=1, max_length=20_000)
    session_id: str = Field(default="web", pattern=_SESSION_PATTERN)


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
