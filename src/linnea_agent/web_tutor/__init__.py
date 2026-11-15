"""网页题目识别与学习辅助领域（只读、不自动提交）。"""

from linnea_agent.web_tutor.extractor import extract_problem
from linnea_agent.web_tutor.formatter import format_problem, resolve_mode
from linnea_agent.web_tutor.schemas import Problem, ProblemKind, Sample

__all__ = [
    "Problem",
    "ProblemKind",
    "Sample",
    "extract_problem",
    "format_problem",
    "resolve_mode",
]
