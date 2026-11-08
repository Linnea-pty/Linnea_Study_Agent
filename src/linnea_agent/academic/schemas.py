"""学术检索领域模型。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Paper:
    """一篇学术论文的规范化元数据。"""

    title: str
    authors: list[str]
    year: int | None
    source: str
    source_id: str
    url: str
    abstract: str = ""
    venue: str = ""
    doi: str = ""

    def key(self) -> str:
        """去重用归一化键：优先 DOI，其次标题小写。"""
        if self.doi:
            return f"doi:{self.doi.lower()}"
        return f"title:{self.title.strip().lower()}"
