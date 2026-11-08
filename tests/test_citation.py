"""引用格式化测试。"""

import pytest

from linnea_agent.academic.citation import format_citation
from linnea_agent.academic.schemas import Paper


def _paper() -> Paper:
    return Paper(
        title="Attention Is All You Need",
        authors=["Vaswani", "Shazeer", "Parmar"],
        year=2017,
        source="arxiv",
        source_id="1706.03762",
        url="https://arxiv.org/abs/1706.03762",
        abstract="...",
        venue="NeurIPS",
        doi="",
    )


def test_gb7714_contains_title_and_year():
    text = format_citation(_paper())
    assert "Attention Is All You Need" in text
    assert "2017" in text


def test_apa_contains_year_in_parens():
    text = format_citation(_paper(), style="apa")
    assert "(2017)" in text


def test_unknown_style_raises():
    with pytest.raises(ValueError):
        format_citation(_paper(), style="unknown")
