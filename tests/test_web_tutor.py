"""网页题目识别测试（离线，全部基于固定 HTML，不启动浏览器）。"""

from __future__ import annotations

from dataclasses import replace

from linnea_agent.tools import build_tools
from linnea_agent.web_tutor.extractor import extract_problem
from linnea_agent.web_tutor.formatter import format_problem, resolve_mode
from linnea_agent.web_tutor.schemas import ProblemKind, Sample

_PTA_HTML = """
<html>
<head><title>7-1 两数之和</title></head>
<body>
  <nav>首页 / 题库</nav>
  <div class="problem-content">
    <h1>7-1 两数之和</h1>
    <div class="problem-body">
      <p>给定两个整数 a 和 b，输出它们的和。</p>
      <h2>输入格式</h2>
      <p>一行包含两个整数。</p>
      <h2>输出格式</h2>
      <p>输出一个整数。</p>
      <h2>输入样例</h2>
      <pre>1 2</pre>
      <h2>输出样例</h2>
      <pre>3</pre>
      <p>时间限制 400 ms</p>
      <p>内存限制 64 MB</p>
    </div>
    <span class="tag">基础</span>
    <span class="tag">数学</span>
    <img src="/images/fig1.png" alt="示意图">
  </div>
  <footer>版权所有</footer>
</body>
</html>
"""

_CHOICE_HTML = """
<html><head><title>练习</title></head>
<body>
  <main>
    <h2>第 3 题</h2>
    <p>以下关于 Python 列表的说法，正确的是？</p>
    <p>A. 列表不可变</p>
    <p>B. 列表可以包含不同类型元素</p>
    <p>C. 列表只能用整数索引以外的下标</p>
    <p>D. 列表长度固定</p>
  </main>
</body></html>
"""


def test_extract_pta_problem():
    problem = extract_problem(_PTA_HTML, "https://pintia.cn/problem-sets/1/problems/2")

    assert problem.source == "pta"
    assert problem.title == "7-1 两数之和"
    assert problem.kind is ProblemKind.PROGRAMMING
    assert "输出它们的和" in problem.statement
    assert problem.samples == (Sample("1 2", "3"),)
    assert any("时间限制" in item for item in problem.constraints)
    assert any("内存限制" in item for item in problem.constraints)
    assert "基础" in problem.tags
    assert "数学" in problem.tags
    assert problem.images == ("https://pintia.cn/images/fig1.png",)


def test_extract_generic_choice_problem():
    problem = extract_problem(_CHOICE_HTML, "https://example.com/quiz/3")

    assert problem.source == "generic"
    assert problem.kind is ProblemKind.CHOICE
    assert "列表" in problem.statement
    assert problem.samples == ()


def test_noise_is_excluded():
    problem = extract_problem(_PTA_HTML, "https://pintia.cn/problem-sets/1/problems/2")

    assert "首页 / 题库" not in problem.statement
    assert "版权所有" not in problem.statement


def test_mode_gating():
    assert resolve_mode("full", allow_full=False)[0] == "steps"
    assert "未开启" in resolve_mode("full", allow_full=False)[1]
    assert resolve_mode("full", allow_full=True) == ("full", "")
    assert resolve_mode("unknown", allow_full=False)[0] == "hint"


def test_formatter_contains_structure_and_compliance():
    problem = extract_problem(_PTA_HTML, "https://pintia.cn/problem-sets/1/problems/2")
    text = format_problem(problem, mode="hint")

    assert "【题目】7-1 两数之和" in text
    assert "【类型】编程题" in text
    assert "样例 1 输入" in text
    assert "【作答模式】提示" in text
    assert "不自动提交" in text

    gated = format_problem(problem, mode="full", allow_full=False)
    assert "【作答模式】分步解析" in gated
    assert "已回退" in gated


def test_truncates_long_statement():
    problem = extract_problem(_PTA_HTML, "https://pintia.cn/problem-sets/1/problems/2")
    text = format_problem(problem, max_chars=10)
    assert "已截断" in text


_PTA_CODEMIRROR_HTML = """
<html><head><title>L1-014 简单题 - 拼题A-程序设计类实验辅助教学平台</title></head>
<body>
  <div class="flex flex-col">
    <div class="rendered-markdown dark:rendered-markdown-invert">
      <p>这次真的没骗你 —— 这道超级简单的题目没有任何输入。</p>
      <p>你只需要在一行中输出事实：<code>This is a simple problem.</code> 就可以了。</p>
      <h3 id="输入样例：">输入样例：</h3>
      <div data-code="" data-lang="in">
        <div class="cm-editor"><div class="cm-line">无</div></div>
      </div>
      <h3 id="输出样例：">输出样例：</h3>
      <div data-code="" data-lang="out">
        <div class="cm-editor"><div class="cm-line">This is a simple problem.</div></div>
      </div>
    </div>
    <div class="text-lightest">代码长度限制 16 KB 时间限制 400 ms 内存限制 64 MB</div>
  </div>
</body></html>
"""


def test_extract_pta_codemirror_problem():
    problem = extract_problem(
        _PTA_CODEMIRROR_HTML,
        "https://pintia.cn/problem-sets/994805046380707840/exam/problems/type/7?problemSetProblemId=1",
    )

    assert problem.source == "pta"
    assert problem.title == "L1-014 简单题"
    assert problem.kind is ProblemKind.PROGRAMMING
    assert problem.samples == (Sample("", "This is a simple problem."),)
    assert "输入样例" not in problem.statement
    assert "输出样例" not in problem.statement
    assert any("400 ms" in item for item in problem.constraints)


def test_full_answer_mode_available():
    problem = extract_problem(_PTA_HTML, "https://pintia.cn/problem-sets/1/problems/2")
    text = format_problem(problem, mode="full", allow_full=True)

    assert "【作答模式】完整答案" in text
    assert "已回退" not in text


def test_read_problem_tool_registered(make_settings):
    names = [tool.name for tool in build_tools(make_settings())]
    assert "read_problem" in names

    disabled = replace(make_settings(), enable_web_tutor_tool=False)
    assert "read_problem" not in [tool.name for tool in build_tools(disabled)]
