"""网页题目识别工具：读取页面 -> 结构化提取 -> 按模式输出。"""

from __future__ import annotations

from langchain_core.tools import tool

from linnea_agent.config import Settings
from linnea_agent.web_tutor.extractor import extract_problem
from linnea_agent.web_tutor.formatter import format_problem
from linnea_agent.web_tutor.page import PageReadError, fetch_page_html
from linnea_agent.web_tutor.schemas import ProblemKind


def build_read_problem_tool(settings: Settings):
    """构建只读的题目识别工具（绑定配置）。"""

    @tool
    def read_problem(url: str = "", mode: str = "full") -> str:
        """读取刷题页面的题目并结构化输出。

        url 留空时通过本机 CDP 读取当前活动标签页。
        mode：full（默认，完整解答与参考代码）、steps（分步解析）、hint（只给提示）。
        仅读取可见内容，不点击、不提交、不绕过登录。
        """
        try:
            html = fetch_page_html(url, cdp_url=settings.web_tutor_cdp_url)
        except PageReadError as exc:
            return f"题目读取失败：{exc}"

        problem = extract_problem(html, url)
        if problem.kind is ProblemKind.UNKNOWN and not problem.statement.strip():
            return "未能从页面中识别出题目内容，请确认已打开题目页，或直接传入题目 URL。"

        max_chars = settings.web_tutor_max_chars
        text = format_problem(
            problem,
            mode=mode,
            allow_full=settings.allow_full_answer,
            max_chars=max_chars,
        )
        return f"{text}\n\n【重要】请直接基于以上题目作答，不要复述题目原文。"

    return read_problem
