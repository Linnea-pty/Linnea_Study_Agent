"""网页读取工具：通过 Playwright 获取 ARIA 快照。"""

from __future__ import annotations

from langchain_core.tools import tool

from linnea_agent.shared.browser import get_browser, install_hint


@tool
def read_webpage(url: str) -> str:
    """读取网页内容，返回 ARIA 快照。适合 SPA 与动态渲染页面。"""
    context = None
    try:
        browser = get_browser()
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:  # noqa: BLE001 - 等待网络空闲超时并非致命错误
            pass
        # aria_snapshot() 本身返回 YAML 文本，直接返回即可，避免二次 JSON 转义
        snapshot = page.locator("body").aria_snapshot()
        return snapshot[:8000]
    except Exception as exc:  # noqa: BLE001 - 网页读取失败返回文本
        text = str(exc)
        if "Executable doesn't exist" in text or "playwright install" in text:
            return f"网页读取失败：{install_hint()}"
        return f"网页读取失败：{text}"
    finally:
        if context is not None:
            context.close()
