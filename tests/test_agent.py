"""Agent 组装冒烟测试。"""

from linnea_agent.agent.builder import build_agent


def test_build_agent_returns_graph(make_settings):
    agent = build_agent(make_settings())
    assert hasattr(agent, "invoke")
