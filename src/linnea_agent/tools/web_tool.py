"""网页读取工具：通过 Playwright 获取 ARIA 快照。"""

from __future__ import annotations

import json

from langchain_core.tools import tool

from linnea_agent.shared.browser import get_browser


@tool
def read_webpage(url: str) -> str:
    """读取网页内容，返回 ARIA 快照。适合 SPA 与动态渲染页面。"""
    browser = get_browser()
    context = browser.new_context()
    page = context.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:  # noqa: BLE001 - 等待网络空闲超时并非致命错误
            pass
        snapshot = page.locator("body").aria_snapshot()
        return json.dumps(snapshot, ensure_ascii=False)[:8000]
    except Exception as exc:  # noqa: BLE001 - 网页读取失败返回文本
        return f"网页读取失败：{exc}"
    finally:
        context.close()
