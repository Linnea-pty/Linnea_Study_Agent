"""网页题目领域的结构化模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ProblemKind(StrEnum):
    """题目类型（基于页面文本的启发式识别）。"""

    PROGRAMMING = "编程题"
    CHOICE = "选择题"
    FILL_BLANK = "填空题"
    UNKNOWN = "未知"


@dataclass(frozen=True, slots=True)
class Sample:
    """一组样例输入/输出。"""

    input: str = ""
    output: str = ""


@dataclass(frozen=True, slots=True)
class Problem:
    """从网页中提取出的规范化题目。"""

    title: str
    statement: str
    url: str = ""
    source: str = "generic"
    kind: ProblemKind = ProblemKind.UNKNOWN
    samples: tuple[Sample, ...] = ()
    constraints: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    images: tuple[str, ...] = ()
    tables: tuple[str, ...] = ()
    warnings: tuple[str, ...] = field(default_factory=tuple)
