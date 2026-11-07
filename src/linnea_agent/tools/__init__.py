"""工具注册：build_tools 工厂按配置组装工具，避免 import 期副作用。"""

from __future__ import annotations

import logging

from langchain_core.tools import BaseTool

from linnea_agent.config import Settings
from linnea_agent.tools.file_tool import build_read_local_file_tool
from linnea_agent.tools.math_tool import calculator
from linnea_agent.tools.time_tool import current_time
from linnea_agent.tools.web_tool import read_webpage

log = logging.getLogger(__name__)

__all__ = ["build_tools"]


def build_tools(settings: Settings) -> list[BaseTool]:
    """按配置组装工具集合。"""
    tools: list[BaseTool] = [
        calculator,
        current_time,
        build_read_local_file_tool(settings),
    ]

    if settings.enable_webpage_tool:
        tools.append(read_webpage)
    else:
        log.info("read_webpage 工具已按配置禁用")

    if settings.enable_search_tool and settings.tavily_api_key:
        from langchain_tavily import TavilySearch

        tools.append(TavilySearch(max_results=2))
    else:
        log.info("TavilySearch 未启用（缺少 TAVILY_API_KEY 或已禁用）")

    log.info("已启用工具: %s", [t.name for t in tools])
    return tools
