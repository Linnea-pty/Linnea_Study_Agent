"""题目提取入口：按 URL 选择站点适配器，统一返回 Problem。"""

from __future__ import annotations

from urllib.parse import urljoin

from linnea_agent.web_tutor.adapters import GenericProblemAdapter, build_adapters
from linnea_agent.web_tutor.schemas import Problem


def extract_problem(html: str, url: str = "") -> Problem:
    """从页面 HTML 中提取题目；无匹配适配器时回退到通用适配器。"""
    adapter = next((item for item in build_adapters() if item.matches(url)), None)
    if adapter is None:
        adapter = GenericProblemAdapter()
    problem = adapter.extract(html, url)
    if url and problem.images:
        images = tuple(urljoin(url, src) for src in problem.images)
        problem = Problem(
            title=problem.title,
            statement=problem.statement,
            url=problem.url,
            source=problem.source,
            kind=problem.kind,
            samples=problem.samples,
            constraints=problem.constraints,
            tags=problem.tags,
            images=images,
            tables=problem.tables,
            warnings=problem.warnings,
        )
    return problem
