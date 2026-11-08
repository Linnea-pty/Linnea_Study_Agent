"""Semantic Scholar 数据源（Graph API）。"""

from __future__ import annotations

from typing import Any

from linnea_agent.academic.schemas import Paper
from linnea_agent.shared.http import get_json

_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


class SemanticScholarSource:
    name = "semantic_scholar"

    def search(self, query: str, max_results: int = 5) -> list[Paper]:
        data = get_json(
            _API_URL,
            params={
                "query": query,
                "limit": str(max_results),
                "fields": "title,authors,year,url,abstract,venue,externalIds",
            },
        )
        return [self._parse(item) for item in data.get("data", [])]

    def _parse(self, item: dict[str, Any]) -> Paper:
        external = item.get("externalIds") or {}
        return Paper(
            title=item.get("title") or "",
            authors=[author.get("name") or "" for author in item.get("authors", [])],
            year=item.get("year"),
            source=self.name,
            source_id=str(item.get("paperId") or ""),
            url=item.get("url") or "",
            abstract=item.get("abstract") or "",
            venue=item.get("venue") or "",
            doi=external.get("DOI") or "",
        )
