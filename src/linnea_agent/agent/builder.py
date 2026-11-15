"""Agent 组装：模型池 + 工具 + 档位路由中间件。"""

from __future__ import annotations

from langchain.agents import create_agent

from linnea_agent.agent.middleware import AgentContext, build_tier_middleware
from linnea_agent.config import Settings
from linnea_agent.shared.llm import ModelPool
from linnea_agent.shared.tier import Tier
from linnea_agent.tools import build_tools

SYSTEM_PROMPT = """你是 Linnea 的个人学习助手，使用简体中文简洁作答。

遇到刷题链接（如 pintia.cn）或题目内容时：
1. 先调用 read_problem 读取并结构化题目；用户要求读取当前浏览器标签页时 url 留空。
2. 用户说“做这个题 / 解题 / 直接生成代码 / 给答案”时，用 mode="full"，并直接给出可提交的
   完整代码（未指定语言默认 Python；只给一个语言版本，不要并列 C/C++/Python 多份），
   再补充 2-4 条关键点。
3. 用户只要“提示 / 思路”时用 mode="hint"；要“分步讲解”时用 mode="steps"。
4. 绝不要把工具返回的题目原文当作最终回答，也不要只回复“请自行完成”；必须基于题目实际作答。
5. 不自动提交、不绕过登录或验证码，也不要声称已经提交或通过。

其他问题直接回答；需要实时网页内容时用 read_webpage，需要论文时用 search_papers。"""


def build_agent(settings: Settings):
    """构建带工具与档位路由的 Agent（模型由中间件按 tier 动态替换）。"""
    pool = ModelPool(settings)
    return create_agent(
        model=pool.get(Tier.BALANCED),
        tools=build_tools(settings),
        system_prompt=SYSTEM_PROMPT,
        middleware=[build_tier_middleware(pool)],
        context_schema=AgentContext,
    )
