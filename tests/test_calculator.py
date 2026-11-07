"""安全计算工具测试。"""

from linnea_agent.tools.math_tool import calculator


def test_basic_arithmetic():
    assert calculator.invoke({"expression": "3*(4+2)"}) == "18"


def test_unsafe_input_rejected():
    result = calculator.invoke({"expression": "__import__('os')"})
    assert result.startswith("计算失败")


def test_power():
    assert calculator.invoke({"expression": "2 ** 10"}) == "1024"
