import atexit
import os
import threading
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[3]
# 系统临时目录不可写时的兜底目录（Windows 受控文件夹访问 / 企业策略 / 沙箱限制）
FALLBACK_TEMP = PROJECT_ROOT / ".tmp" / "playwright"
# 项目内安装的浏览器目录；系统默认目录不可写时使用
LOCAL_BROWSERS = PROJECT_ROOT / ".playwright" / "browsers"
_TEMP_KEYS = ("TEMP", "TMP", "TMPDIR")

_local = threading.local()
_registry: list[tuple] = []
_lock = threading.Lock()


def install_hint() -> str:
    """返回项目内安装 Chromium 的可操作命令。"""
    return (
        "未找到 Chromium 浏览器。请先安装（系统目录不可写时用项目内目录）：\n"
        f'  $env:PLAYWRIGHT_BROWSERS_PATH="{LOCAL_BROWSERS}"\n'
        "  uv run playwright install chromium"
    )


def _ensure_browsers_path() -> None:
    """若项目内已安装浏览器且用户未显式指定路径，则自动启用。"""
    if os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        return
    if LOCAL_BROWSERS.is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(LOCAL_BROWSERS)


def _is_temp_error(exc: BaseException) -> bool:
    """判断异常是否由临时目录不可写（mkdtemp EPERM）引起。"""
    text = str(exc)
    return "mkdtemp" in text and ("EPERM" in text or "Permission denied" in text)


def _launch():
    """启动 Playwright 与 Chromium；系统临时目录不可写时自动改用项目内目录重试。"""
    _ensure_browsers_path()
    pw = sync_playwright().start()
    try:
        return pw, pw.chromium.launch(headless=True)
    except PlaywrightError as exc:
        pw.stop()
        if not _is_temp_error(exc):
            raise

    FALLBACK_TEMP.mkdir(parents=True, exist_ok=True)
    saved = {key: os.environ.get(key) for key in _TEMP_KEYS}
    try:
        # Playwright 驱动（Node）在启动时继承环境变量，因此只需在 start() 期间切换
        for key in _TEMP_KEYS:
            os.environ[key] = str(FALLBACK_TEMP)
        pw = sync_playwright().start()
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    try:
        browser = pw.chromium.launch(headless=True)
    except Exception:
        pw.stop()
        raise
    return pw, browser


def get_browser():
    b = getattr(_local, "browser", None)
    if b is not None and b.is_connected():
        return b
    pw, b = _launch()
    _local.pw, _local.browser = pw, b
    with _lock:
        _registry.append((pw, b))
    return b


@atexit.register
def shutdown_browsers() -> None:
    """进程退出时尽力回收浏览器；任何异常都不应污染退出流程。"""
    with _lock:
        items = list(_registry)
        _registry.clear()
    for pw, browser in items:
        try:
            browser.close()
        except Exception:  # noqa: BLE001 - 退出阶段无法恢复，忽略即可
            pass
        try:
            pw.stop()
        except Exception:  # noqa: BLE001 - greenlet 跨线程停止会报错，忽略
            pass
