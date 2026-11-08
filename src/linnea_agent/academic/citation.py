"""引用格式化：GB/T 7714、APA、MLA。"""

from __future__ import annotations

from linnea_agent.academic.schemas import Paper

_STYLES = ("gb7714", "apa", "mla")


def format_citation(paper: Paper, style: str = "gb7714") -> str:
    """按指定格式生成参考文献条目。"""
    if style == "gb7714":
        return _gb7714(paper)
    if style == "apa":
        return _apa(paper)
    if style == "mla":
        return _mla(paper)
    raise ValueError(f"不支持的引用格式：{style}，可选 {_STYLES}")


def _gb7714(paper: Paper) -> str:
    authors = _authors_text(paper)
    year = str(paper.year) if paper.year else "n.d."
    venue = f"{paper.venue}." if paper.venue else "[EB/OL]."
    doi = f" DOI:{paper.doi}." if paper.doi else ""
    return f"{authors}. {paper.title}{venue} {year}{doi}"


def _apa(paper: Paper) -> str:
    authors = ", ".join(paper.authors or ["Anon."])
    year = f"({paper.year})." if paper.year else "(n.d.)."
    return f"{authors} {year} {paper.title}."


def _mla(paper: Paper) -> str:
    first = (paper.authors or ["Anon."])[0]
    year = str(paper.year) if paper.year else "n.d."
    return f'{first}. "{paper.title}." {paper.venue or "Web"}, {year}.'


def _authors_text(paper: Paper, max_authors: int = 3) -> str:
    authors = paper.authors or ["佚名"]
    if len(authors) <= max_authors:
        return ", ".join(authors)
    return f"{authors[0]} 等"
