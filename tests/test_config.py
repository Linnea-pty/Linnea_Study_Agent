"""配置加载测试。"""

from pathlib import Path

from linnea_agent.config import Settings, _as_bool


def test_as_bool():
    assert _as_bool("true") is True
    assert _as_bool("1") is True
    assert _as_bool("no") is False
    assert _as_bool("false") is False


def test_from_env_reads_env_values(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-test")
    monkeypatch.setenv("QWEN_MODEL", "qwen-test")
    monkeypatch.setenv("ENABLE_WEBPAGE_TOOL", "false")
    settings = Settings.from_env()

    assert settings.deepseek_model == "deepseek-test"
    assert settings.qwen_model == "qwen-test"
    assert settings.enable_webpage_tool is False
    assert isinstance(settings.file_root, Path)
    assert isinstance(settings.history_dir, Path)


def test_from_env_defaults(monkeypatch):
    for name in ("MODEL_TIMEOUT", "MODEL_MAX_RETRIES", "BUDGET_LIMIT", "ENABLE_ACADEMIC_TOOL"):
        monkeypatch.delenv(name, raising=False)
    settings = Settings.from_env()

    assert settings.model_timeout == 60.0
    assert settings.model_max_retries == 2
    assert settings.budget_limit == 0.0
    assert settings.enable_academic_tool is True
