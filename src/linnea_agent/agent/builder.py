"""Agent 组装：模型池 + 工具 + 档位路由中间件。"""

from __future__ import annotations

from langchain.agents import create_agent

from linnea_agent.agent.middleware import AgentContext, build_tier_middleware
from linnea_agent.config import Settings
from linnea_agent.shared.llm import ModelPool
from linnea_agent.tools import build_tools

SYSTEM_PROMPT = "你是一名Linnea的个人学习助手，请使用简体中文简洁作答。"


def build_agent(settings: Settings):
    """构建带工具与档位路由的 Agent（模型由中间件按 tier 动态替换）。"""
    pool = ModelPool(settings)
    return create_agent(
        model=pool.get("balanced"),
        tools=build_tools(settings),
        system_prompt=SYSTEM_PROMPT,
        middleware=[build_tier_middleware(pool)],
        context_schema=AgentContext,
    )
