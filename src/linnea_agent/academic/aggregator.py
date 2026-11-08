"""多源结果聚合：去重并排序。"""

from __future__ import annotations

from linnea_agent.academic.schemas import Paper


def aggregate(papers: list[Paper]) -> list[Paper]:
    """去重（DOI 优先）并按年份降序排序。"""
    deduped: dict[str, Paper] = {}
    for paper in papers:
        key = paper.key()
        existing = deduped.get(key)
        if existing is None or _richer(paper, existing):
            deduped[key] = paper
    return sorted(deduped.values(), key=lambda p: p.year or 0, reverse=True)


def _richer(candidate: Paper, current: Paper) -> bool:
    """候选记录信息更全（有摘要或 DOI）则优先保留。"""
    return (not current.abstract and bool(candidate.abstract)) or (
        not current.doi and bool(candidate.doi)
    )
