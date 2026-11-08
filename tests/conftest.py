"""测试共享 fixture。"""

from __future__ import annotations

from pathlib import Path

import pytest

from linnea_agent.config import Settings


@pytest.fixture
def make_settings():
    """返回一个可定制模型密钥的 Settings 工厂。"""

    def _make(deepseek_key: str = "sk-d", qwen_key: str = "sk-q") -> Settings:
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
            enable_academic_tool=False,
            model_timeout=60.0,
            model_max_retries=2,
            budget_limit=0.0,
            file_root=Path("sandbox"),
            history_dir=Path("histories"),
        )

    return _make
