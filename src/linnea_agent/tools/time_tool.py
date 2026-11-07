"""时间查询工具。"""

from __future__ import annotations

import datetime

from langchain_core.tools import tool


@tool
def current_time() -> str:
    """获取当前日期和时间。"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
