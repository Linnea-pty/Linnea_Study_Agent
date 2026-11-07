"""意图路由测试。"""

from linnea_agent.chat.models import Tier
from linnea_agent.chat.router import decide_tier


def test_coding_goes_balanced():
    assert decide_tier("帮我写个 python 函数") is Tier.BALANCED


def test_reasoning_goes_balanced():
    assert decide_tier("分析一下这段代码为什么慢") is Tier.BALANCED


def test_simple_goes_fast():
    assert decide_tier("你好") is Tier.FAST


def test_case_insensitive():
    assert decide_tier("实现一个 SQL 查询") is Tier.BALANCED
