"""OpenAlex 数据源（REST API）。"""

from __future__ import annotations

from typing import Any

from linnea_agent.academic.schemas import Paper
from linnea_agent.shared.http import get_json

_API_URL = "https://api.openalex.org/works"


class OpenAlexSource:
    name = "openalex"

    def search(self, query: str, max_results: int = 5) -> list[Paper]:
        data = get_json(_API_URL, params={"search": query, "per-page": str(max_results)})
        return [self._parse(item) for item in data.get("results", [])]

    def _parse(self, item: dict[str, Any]) -> Paper:
        source = (item.get("primary_location") or {}).get("source") or {}
        doi = item.get("doi") or ""
        return Paper(
            title=item.get("title") or "",
            authors=[
                (authorship.get("author") or {}).get("display_name") or ""
                for authorship in item.get("authorships", [])
            ],
            year=item.get("publication_year"),
            source=self.name,
            source_id=item.get("id") or "",
            url=doi,
            abstract=_reconstruct_abstract(item.get("abstract_inverted_index")),
            venue=source.get("display_name") or "",
            doi=doi.removeprefix("https://doi.org/"),
        )


def _reconstruct_abstract(inverted: dict[str, list[int]] | None) -> str:
    """将 OpenAlex 的倒排索引还原为摘要文本。"""
    if not inverted:
        return ""
    positions = [(idx, word) for word, indices in inverted.items() for idx in indices]
    return " ".join(word for _, word in sorted(positions))
