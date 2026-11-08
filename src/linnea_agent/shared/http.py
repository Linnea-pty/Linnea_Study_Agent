"""轻量 HTTP 客户端：学术检索数据源共用，带超时与统一错误。"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

_USER_AGENT = "LinneaAgent/0.3 (academic-search)"


class HttpError(RuntimeError):
    """HTTP 请求失败。"""


def get_text(url: str, params: dict[str, str] | None = None, timeout: float = 15.0) -> str:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise HttpError(f"请求失败：{url}（{exc}）") from exc


def get_json(url: str, params: dict[str, str] | None = None, timeout: float = 15.0) -> Any:
    return json.loads(get_text(url, params=params, timeout=timeout))
