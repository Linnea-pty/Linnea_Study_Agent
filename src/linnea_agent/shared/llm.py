"""模型池：按档位（tier）惰性构建 ChatOpenAI，缺 key 时自动降级。"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from linnea_agent.config import Settings

log = logging.getLogger(__name__)

# 降级顺序：目标档位缺 key 时按此顺序回退
_FALLBACK_ORDER = ("balanced", "fast")


@dataclass
class ModelPool:
    """按档位缓存并管理 ChatOpenAI 模型实例。"""

    settings: Settings
    _cache: dict[str, ChatOpenAI] = field(default_factory=dict, init=False)

    def get(self, tier: str) -> ChatOpenAI:
        """返回指定档位的模型；该档位缺 key 时降级到可用档位。"""
        if tier in self._cache:
            return self._cache[tier]
        model = self._build(tier)
        if model is None:
            model = self._build_first_available()
            if model is None:
                raise RuntimeError(
                    "未配置任何可用的模型 API Key，请在 .env 中设置 "
                    "DEEPSEEK_API_KEY 或 QWEN_API_KEY"
                )
        self._cache[tier] = model
        return model

    def _build(self, tier: str) -> ChatOpenAI | None:
        key, model, base_url = self._provider(tier)
        if not key:
            return None
        return ChatOpenAI(model=model, base_url=base_url, api_key=SecretStr(key), temperature=0)

    def _build_first_available(self) -> ChatOpenAI | None:
        for tier in _FALLBACK_ORDER:
            model = self._build(tier)
            if model is not None:
                log.warning("目标档位缺少 API Key，已降级使用 %s", tier)
                return model
        return None

    def _provider(self, tier: str) -> tuple[str, str, str]:
        if tier == "fast":
            return (
                self.settings.qwen_api_key,
                self.settings.qwen_model,
                self.settings.qwen_base_url,
            )
        return (
            self.settings.deepseek_api_key,
            self.settings.deepseek_model,
            self.settings.deepseek_base_url,
        )
