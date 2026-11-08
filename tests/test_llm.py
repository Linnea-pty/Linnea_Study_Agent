"""模型池测试。"""

import pytest
from langchain_openai import ChatOpenAI

from linnea_agent.shared.llm import ModelPool
from linnea_agent.shared.tier import Tier


def test_get_builds_model(make_settings):
    pool = ModelPool(make_settings())
    model = pool.get(Tier.BALANCED)
    assert isinstance(model, ChatOpenAI)
    assert model.model_name == "deepseek-chat"


def test_get_caches_instance(make_settings):
    pool = ModelPool(make_settings())
    assert pool.get(Tier.FAST) is pool.get(Tier.FAST)


def test_fallback_when_target_missing(make_settings):
    pool = ModelPool(make_settings(deepseek_key=""))
    model = pool.get(Tier.BALANCED)
    assert model.model_name == "qwen-flash"


def test_raises_without_any_key(make_settings):
    pool = ModelPool(make_settings(deepseek_key="", qwen_key=""))
    with pytest.raises(RuntimeError):
        pool.get(Tier.BALANCED)
