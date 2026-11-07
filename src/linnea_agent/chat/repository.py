"""会话历史持久化：显式角色映射 + 临时文件原子写入。"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from langchain_core.messages import BaseMessage

from linnea_agent.chat.models import PERSIST_ROLES, ROLE_TO_CLS, role_of

log = logging.getLogger(__name__)


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
            cls = ROLE_TO_CLS.get(item.get("role"))
            if cls is None:
                continue
            messages.append(cls(content=item.get("content", "")))
        return messages

    def save(self, session_id: str, messages: list[BaseMessage]) -> None:
        serializable = []
        for message in messages:
            role = role_of(message)
            if role not in PERSIST_ROLES:
                if role is None:
                    log.warning("未知消息类型 %s，已跳过", type(message).__name__)
                continue
            serializable.append({"role": role, "content": message.content})

        path = self._path(session_id)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)

    def _path(self, session_id: str) -> Path:
        return self.base / f"{session_id}.json"
