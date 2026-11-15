"""浏览器基础设施测试：临时目录不可写时的启动重试（不启动真实浏览器）。"""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import Error as PlaywrightError

from linnea_agent.shared import browser


class _FakeBrowser:
    def close(self) -> None:
        pass


class _FakeChromium:
    def __init__(self, error: Exception | None = None) -> None:
        self._error = error
        self.browser = _FakeBrowser()

    def launch(self, **kwargs):
        if self._error is not None:
            raise self._error
        return self.browser


class _FakePlaywright:
    def __init__(self, error: Exception | None = None) -> None:
        self.chromium = _FakeChromium(error)
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True


class _Starter:
    """模拟 sync_playwright()，按顺序返回预置的 Playwright 实例并记录启动时的 TEMP。"""

    def __init__(self, instances: list[_FakePlaywright]) -> None:
        self._instances = instances
        self._index = 0
        self.seen_temp: list[str | None] = []

    def start(self) -> _FakePlaywright:
        instance = self._instances[self._index]
        self._index += 1
        self.seen_temp.append(os.environ.get("TEMP"))
        return instance


def test_is_temp_error():
    assert browser._is_temp_error(
        PlaywrightError("BrowserType.launch: EPERM: operation not permitted, mkdtemp 'C:\\Temp\\x'")
    )
    assert not browser._is_temp_error(PlaywrightError("Executable doesn't exist"))


def test_launch_retries_with_project_temp(monkeypatch, tmp_path):
    fallback = tmp_path / "playwright-temp"
    monkeypatch.setattr(browser, "FALLBACK_TEMP", fallback)

    first = _FakePlaywright(PlaywrightError("BrowserType.launch: EPERM: mkdtemp 'C:\\Temp\\x'"))
    second = _FakePlaywright()
    starter = _Starter([first, second])
    monkeypatch.setattr(browser, "sync_playwright", lambda: starter)

    original = {key: os.environ.get(key) for key in browser._TEMP_KEYS}
    try:
        pw, launched = browser._launch()
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    assert pw is second
    assert launched is second.chromium.browser
    assert first.stopped
    assert fallback.is_dir()
    # 第二次启动驱动时 TEMP 指向兜底目录，启动后环境恢复
    assert starter.seen_temp[1] == str(fallback)
    assert {key: os.environ.get(key) for key in browser._TEMP_KEYS} == original


def test_launch_does_not_retry_other_errors(monkeypatch):
    first = _FakePlaywright(PlaywrightError("Executable doesn't exist"))
    starter = _Starter([first])
    monkeypatch.setattr(browser, "sync_playwright", lambda: starter)

    with pytest.raises(PlaywrightError):
        browser._launch()
    assert first.stopped
    assert starter._index == 1


def test_shutdown_swallows_close_and_stop_errors(monkeypatch):
    class _BadBrowser:
        def close(self) -> None:
            raise RuntimeError("cannot switch to a different thread")

    class _BadPlaywright:
        def stop(self) -> None:
            raise RuntimeError("greenlet already exited")

    monkeypatch.setattr(browser, "_registry", [(_BadPlaywright(), _BadBrowser())])

    browser.shutdown_browsers()  # 不应抛异常

    assert browser._registry == []
