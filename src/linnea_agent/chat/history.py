"""会话历史持久化：显式角色映射 + 临时文件原子写入。"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

log = logging.getLogger(__name__)

# 仅持久化 user / assistant 两类消息
_ROLE_TO_CLS: dict[str, type[BaseMessage]] = {"user": HumanMessage, "assistant": AIMessage}
_CLS_TO_ROLE: dict[type[BaseMessage], str] = {cls: role for role, cls in _ROLE_TO_CLS.items()}


class HistoryRepository:
    """按会话 ID 读写消息历史，落盘为 JSON。"""

    def __init__(self, base_dir: str | Path):
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def load(self, session_id: str) -> list[BaseMessage]:
        path = self._path(session_id)
        if not path.exists():
            return []
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []
        try:
            raw = json.loads(content)
        except json.JSONDecodeError:
            log.warning("历史文件 %s 损坏，已重置为空历史", path.name)
            return []

        messages: list[BaseMessage] = []
        for item in raw:
            cls = _ROLE_TO_CLS.get(item.get("role"))
            if cls is not None:
                messages.append(cls(content=item.get("content", "")))
        return messages

    def save(self, session_id: str, messages: list[BaseMessage]) -> None:
        serializable = []
        for message in messages:
            role = _CLS_TO_ROLE.get(type(message))
            if role is None:
                log.warning("不持久化的消息类型 %s，已跳过", type(message).__name__)
                continue
            serializable.append({"role": role, "content": message.content})

        path = self._path(session_id)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)

    def _path(self, session_id: str) -> Path:
        return self.base / f"{session_id}.json"
