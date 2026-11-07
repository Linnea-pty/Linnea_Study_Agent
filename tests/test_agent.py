"""Agent 组装冒烟测试。"""

from pathlib import Path

from linnea_agent.agent.builder import build_agent
from linnea_agent.config import Settings


def _settings() -> Settings:
    return Settings(
        deepseek_api_key="sk-d",
        deepseek_model="deepseek-chat",
        deepseek_base_url="https://api.deepseek.com",
        qwen_api_key="sk-q",
        qwen_model="qwen-flash",
        qwen_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        tavily_api_key="",
        enable_webpage_tool=False,
        enable_search_tool=False,
        file_root=Path("sandbox"),
        history_dir=Path("histories"),
    )


def test_build_agent_returns_graph():
    agent = build_agent(_settings())
    # 编译后的图应具备 invoke 方法
    assert hasattr(agent, "invoke")
