"""系统代理环境变量清理。

Windows 的代理例外列表常包含 ``[::1]``，httpx 会把它当成非法端口
（``Invalid port: ':1]'``）。任何通过 httpx 发起请求的入口都应先调用本函数。
"""

from __future__ import annotations

import os
import urllib.request


def sanitize_proxy_bypass() -> None:
    """移除 NO_PROXY 中的 IPv6 方括号项，并统一大小写变量。"""
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
