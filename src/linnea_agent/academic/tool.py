"""学术检索工具：聚合多源结果并格式化输出。"""

from __future__ import annotations

import logging

from langchain_core.tools import tool

from linnea_agent.academic.aggregator import aggregate
from linnea_agent.academic.citation import format_citation
from linnea_agent.academic.sources import build_sources
from linnea_agent.shared.http import HttpError

log = logging.getLogger(__name__)


@tool
def search_papers(query: str, max_results: int = 5) -> str:
    """检索学术论文，返回聚合去重后的结果（含 GB/T 7714 引用）。"""
    papers = []
    for source in build_sources():
        try:
            papers.extend(source.search(query, max_results=max_results))
        except HttpError as exc:
            log.warning("数据源 %s 检索失败：%s", source.name, exc)

    if not papers:
        return "未检索到相关论文。"

    lines = [f"共检索到 {len(papers)} 篇（已聚合去重，按年份排序）："]
    lines.extend(f"- {format_citation(paper)}" for paper in aggregate(papers))
    return "\n".join(lines)
