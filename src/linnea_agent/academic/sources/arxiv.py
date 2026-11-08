"""arXiv 数据源（Atom XML API）。"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from linnea_agent.academic.schemas import Paper
from linnea_agent.shared.http import get_text

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}
_API_URL = "http://export.arxiv.org/api/query"


class ArxivSource:
    name = "arxiv"

    def search(self, query: str, max_results: int = 5) -> list[Paper]:
        raw = get_text(
            _API_URL, params={"search_query": f"all:{query}", "max_results": str(max_results)}
        )
        root = ET.fromstring(raw)
        return [self._parse(entry) for entry in root.findall("atom:entry", _NS)]

    def _parse(self, entry: ET.Element) -> Paper:
        authors = [
            _author_name(node) for node in entry.findall("atom:author", _NS) if _author_name(node)
        ]
        published = _text(entry, "atom:published")
        return Paper(
            title=_text(entry, "atom:title"),
            authors=authors,
            year=int(published[:4]) if published else None,
            source=self.name,
            source_id=_text(entry, "atom:id"),
            url=_text(entry, "atom:id"),
            abstract=_text(entry, "atom:summary"),
            doi=_text(entry, "arxiv:doi"),
        )


def _author_name(author: ET.Element) -> str:
    name = author.find("atom:name", _NS)
    return (name.text or "").strip() if name is not None else ""


def _text(entry: ET.Element, path: str) -> str:
    node = entry.find(path, _NS)
    return (node.text or "").strip() if node is not None else ""
