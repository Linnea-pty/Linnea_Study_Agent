"""入口辅助函数测试：代理例外列表清理（不启动 Gradio）。"""

from __future__ import annotations

import os

from linnea_agent.main import _sanitize_proxy_bypass


def test_sanitize_proxy_bypass_drops_bracketed_ipv6(monkeypatch):
    monkeypatch.setenv("NO_PROXY", "localhost,127.0.0.1,[::1],10.0.0.0/8")
    monkeypatch.setenv("no_proxy", "localhost,127.0.0.1,[::1],10.0.0.0/8")

    _sanitize_proxy_bypass()

    assert os.environ["NO_PROXY"] == "localhost,127.0.0.1,10.0.0.0/8"
    assert os.environ["no_proxy"] == "localhost,127.0.0.1,10.0.0.0/8"
