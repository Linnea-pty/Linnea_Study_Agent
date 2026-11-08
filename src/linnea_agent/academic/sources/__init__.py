"""学术数据源协议与工厂。"""

from __future__ import annotations

from typing import Protocol

from linnea_agent.academic.schemas import Paper


class Source(Protocol):
    """学术检索数据源接口。"""

    name: str

    def search(self, query: str, max_results: int) -> list[Paper]: ...


def build_sources() -> list[Source]:
    from linnea_agent.academic.sources.arxiv import ArxivSource
    from linnea_agent.academic.sources.openalex import OpenAlexSource
    from linnea_agent.academic.sources.semantic_scholar import SemanticScholarSource

    return [ArxivSource(), SemanticScholarSource(), OpenAlexSource()]
