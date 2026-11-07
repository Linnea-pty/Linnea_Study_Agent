"""会话历史持久化测试。"""

from langchain_core.messages import AIMessage, HumanMessage

from linnea_agent.chat.repository import HistoryRepository


def test_round_trip(tmp_path):
    repo = HistoryRepository(tmp_path)
    repo.save("web", [HumanMessage(content="你好"), AIMessage(content="你好！")])

    loaded = repo.load("web")
    assert [m.content for m in loaded] == ["你好", "你好！"]
    assert isinstance(loaded[0], HumanMessage)
    assert isinstance(loaded[1], AIMessage)


def test_load_missing_returns_empty(tmp_path):
    repo = HistoryRepository(tmp_path)
    assert repo.load("nonexistent") == []


def test_load_corrupted_resets(tmp_path):
    repo = HistoryRepository(tmp_path)
    (tmp_path / "web.json").write_text("{ not valid json", encoding="utf-8")
    assert repo.load("web") == []
