"""API 层测试：健康检查与 SSE 事件格式。"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from linnea_agent.api.app import create_app
from linnea_agent.chat.history import HistoryRepository
from linnea_agent.chat.service import ChatService, TurnResult
from linnea_agent.shared.tier import Tier


class FakeService(ChatService):
    def __init__(self) -> None:  # noqa: D401 - 测试替身，无需真实依赖
        pass

    def run_turn(self, task: str, session_id: str) -> TurnResult:
        if task == "boom":
            raise RuntimeError("模型调用失败")
        return TurnResult(reply=f"回显：{task}", tier=Tier.FAST)


def _client(tmp_path: Path) -> TestClient:
    return TestClient(
        create_app(service=FakeService(), repo=HistoryRepository(tmp_path / "histories"))
    )


def test_health(tmp_path: Path) -> None:
    response = _client(tmp_path).get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_stream_returns_status_and_done(tmp_path: Path) -> None:
    response = _client(tmp_path).post(
        "/api/chat/stream", json={"message": "你好", "session_id": "web"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: status" in response.text
    assert "event: done" in response.text
    assert "回显：你好" in response.text


def test_chat_stream_reports_error_event(tmp_path: Path) -> None:
    response = _client(tmp_path).post(
        "/api/chat/stream", json={"message": "boom", "session_id": "web"}
    )
    assert response.status_code == 200
    assert "event: error" in response.text
    assert "模型调用失败" in response.text


def test_chat_stream_rejects_invalid_session_id(tmp_path: Path) -> None:
    response = _client(tmp_path).post(
        "/api/chat/stream", json={"message": "你好", "session_id": "../escape"}
    )
    assert response.status_code == 422
