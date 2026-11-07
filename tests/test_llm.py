"""模型池测试。"""

from pathlib import Path

import pytest
from langchain_openai import ChatOpenAI

from linnea_agent.config import Settings
from linnea_agent.shared.llm import ModelPool


def _settings(deepseek_key: str = "sk-d", qwen_key: str = "sk-q") -> Settings:
    return Settings(
        deepseek_api_key=deepseek_key,
        deepseek_model="deepseek-chat",
        deepseek_base_url="https://api.deepseek.com",
        qwen_api_key=qwen_key,
        qwen_model="qwen-flash",
        qwen_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        tavily_api_key="",
        enable_webpage_tool=False,
        enable_search_tool=False,
        file_root=Path("sandbox"),
        history_dir=Path("histories"),
    )


def test_get_builds_model():
    pool = ModelPool(_settings())
    model = pool.get("balanced")
    assert isinstance(model, ChatOpenAI)
    assert model.model_name == "deepseek-chat"


def test_get_caches_instance():
    pool = ModelPool(_settings())
    assert pool.get("fast") is pool.get("fast")


def test_fallback_when_target_missing():
    pool = ModelPool(_settings(deepseek_key=""))
    model = pool.get("balanced")
    assert model.model_name == "qwen-flash"


def test_raises_without_any_key():
    pool = ModelPool(_settings(deepseek_key="", qwen_key=""))
    with pytest.raises(RuntimeError):
        pool.get("balanced")
