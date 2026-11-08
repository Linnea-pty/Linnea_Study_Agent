"""学术检索领域：多源检索、聚合去重与引用生成。"""

from linnea_agent.academic.citation import format_citation
from linnea_agent.academic.schemas import Paper

__all__ = ["Paper", "format_citation"]
