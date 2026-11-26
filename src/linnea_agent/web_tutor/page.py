"""页面读取：抓取指定 URL，或通过 CDP 读取用户手动打开的活动页面。"""

from __future__ import annotations

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from linnea_agent.shared.browser import get_browser, install_hint

DEFAULT_CDP_URL = "http://127.0.0.1:9222"


class PageReadError(RuntimeError):
    """页面读取失败。"""


def fetch_page_html(
    url: str = "",
    cdp_url: str = DEFAULT_CDP_URL,
    timeout_ms: int = 20_000,
) -> str:
    """返回页面 HTML。

    - 传 url：打开该页面读取（只读，不点击、不提交）；
    - 不传 url：连接本机 CDP，读取最后一个活动标签页。
    """
    if url:
        return _fetch_url(url, timeout_ms)
    return _fetch_active_page(cdp_url, timeout_ms)


def _fetch_url(url: str, timeout_ms: int) -> str:
    context = None
    try:
        browser = get_browser()
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        try:
            page.wait_for_load_state("networkidle", timeout=5_000)
        except PlaywrightError:
            pass
        return page.content()
    except PlaywrightError as exc:
        raise PageReadError(_describe(exc, url)) from exc
    finally:
        if context is not None:
            context.close()


def _fetch_active_page(cdp_url: str, timeout_ms: int) -> str:
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(cdp_url, timeout=timeout_ms)
            pages = [page for context in browser.contexts for page in context.pages]
            if not pages:
                raise PageReadError("CDP 已连接，但没有可读取的标签页。")
            return pages[-1].content()
    except PlaywrightError as exc:
        raise PageReadError(
            f"无法连接本机浏览器 CDP（{cdp_url}）：{exc}。"
            "请先用 --remote-debugging-port=9222 启动浏览器，或直接传入题目 URL。"
        ) from exc


def _describe(exc: PlaywrightError, url: str) -> str:
    """把 Playwright 的原始异常翻译成可操作的中文提示。"""
    text = str(exc)
    if "Executable doesn't exist" in text or "playwright install" in text:
        return install_hint()
    if "EPERM" in text and "mkdtemp" in text:
        return (
            "浏览器启动失败：系统临时目录不可写。"
            "请检查 Windows 受控文件夹访问/杀毒软件对 Temp 目录的限制，"
            "或清理项目下的 .tmp/playwright 后重试。"
        )
    return f"打开页面失败（{url}）：{text}"
