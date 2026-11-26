"""作答模式：提示 / 分步解析 / 完整答案，并落实学术诚信默认值。"""

from __future__ import annotations

from linnea_agent.web_tutor.schemas import Problem

MODES: dict[str, tuple[str, str]] = {
    "hint": ("提示", "只给方向性提示与关键突破口，不给出完整解答或代码。"),
    "steps": ("分步解析", "按步骤讲解思路、推导与关键实现，最后留出自行完成的空间。"),
    "full": ("完整答案", "给出完整解答；编程题附参考代码，但仅在本地验证样例，不自动提交。"),
}
DEFAULT_MODE = "hint"


def resolve_mode(mode: str, allow_full: bool = False) -> tuple[str, str]:
    """校验模式；未显式开启时禁止完整答案，降级为分步解析。"""
    requested = (mode or DEFAULT_MODE).strip().lower()
    if requested not in MODES:
        return DEFAULT_MODE, f"未知模式 {mode!r}，已回退为「提示」模式。"
    if requested == "full" and not allow_full:
        note = "完整答案未开启，已回退为「分步解析」模式（需显式设置 ALLOW_FULL_ANSWER=true）。"
        return "steps", note
    return requested, ""


def format_problem(
    problem: Problem,
    mode: str = DEFAULT_MODE,
    allow_full: bool = False,
    max_chars: int = 6000,
) -> str:
    """把结构化题目格式化为供 Agent 阅读的文本。"""
    resolved, note = resolve_mode(mode, allow_full)
    label, instruction = MODES[resolved]

    lines: list[str] = [
        f"【题目】{problem.title}",
        f"【类型】{problem.kind.value}",
        f"【来源】{problem.source}",
    ]
    if problem.url:
        lines.append(f"【链接】{problem.url}")

    body = problem.statement.strip()
    if len(body) > max_chars:
        body = body[:max_chars] + "\n…（题干过长，已截断）"
    lines.extend(["", "【题干】", body or "（未提取到题干）"])

    if problem.constraints:
        lines.extend(["", "【限制】", *problem.constraints])
    if problem.samples:
        lines.extend(["", "【样例】"])
        for index, sample in enumerate(problem.samples, start=1):
            lines.append(f"样例 {index} 输入：\n{sample.input or '（空）'}")
            lines.append(f"样例 {index} 输出：\n{sample.output or '（空）'}")
    if problem.tags:
        lines.extend(["", f"【标签】{' / '.join(problem.tags)}"])
    if problem.images:
        lines.extend(["", "【图片】", *problem.images])
    if problem.tables:
        lines.extend(["", "【表格】", *problem.tables])

    lines.extend(
        [
            "",
            f"【作答模式】{label}：{instruction}",
            "【合规约束】仅用于个人学习；不自动提交、不绕过登录/验证码、不批量抓取。",
        ]
    )
    if note:
        lines.append(f"【模式说明】{note}")
    return "\n".join(lines)
