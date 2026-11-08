"""多源结果聚合测试。"""

from linnea_agent.academic.aggregator import aggregate
from linnea_agent.academic.schemas import Paper


def _paper(title: str, doi: str = "", year: int = 2020, abstract: str = "") -> Paper:
    return Paper(
        title=title,
        authors=["A"],
        year=year,
        source="test",
        source_id=title,
        url="",
        abstract=abstract,
        doi=doi,
    )


def test_dedup_by_doi():
    first = _paper("T", doi="10.1/x", year=2020)
    dup = _paper("T (dup)", doi="10.1/x", year=2021)
    assert len(aggregate([first, dup])) == 1


def test_sorted_by_year_desc():
    old = _paper("old", year=2000)
    new = _paper("new", year=2024)
    result = aggregate([old, new])
    assert result[0].title == "new"


def test_prefer_richer_abstract():
    bare = _paper("T", year=2020)
    rich = _paper("T", year=2020, abstract="full text")
    assert aggregate([bare, rich])[0].abstract == "full text"
