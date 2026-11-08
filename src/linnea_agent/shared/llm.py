"""模型池：按档位（Tier）惰性构建 ChatOpenAI，缺 key 自动降级，支持超时与重试。"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from linnea_agent.config import Settings
from linnea_agent.shared.tier import Tier

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Provider:
    """模型提供方配置。"""

    name: str
    api_key: str
    model: str
    base_url: str


@dataclass
class ModelPool:
    """按档位缓存并管理 ChatOpenAI 模型实例。"""

    settings: Settings
    _cache: dict[Tier, ChatOpenAI] = field(default_factory=dict, init=False)

    # 降级顺序：目标档位缺 key 时按此顺序回退
    _FALLBACK_ORDER: tuple[Tier, ...] = (Tier.BALANCED, Tier.FAST)

    def get(self, tier: Tier) -> ChatOpenAI:
        if tier in self._cache:
            return self._cache[tier]
        model = self._build(tier)
        if model is None:
            model = self._first_available()
            if model is None:
                raise RuntimeError(
                    "未配置任何可用的模型 API Key，请在 .env 中设置 "
                    "DEEPSEEK_API_KEY 或 QWEN_API_KEY"
                )
        self._cache[tier] = model
        return model

    def _build(self, tier: Tier) -> ChatOpenAI | None:
        provider = self._provider(tier)
        if not provider.api_key:
            return None
        return ChatOpenAI(
            model=provider.model,
            base_url=provider.base_url,
            api_key=SecretStr(provider.api_key),
            temperature=0,
            timeout=self.settings.model_timeout,
            max_retries=self.settings.model_max_retries,
        )

    def _first_available(self) -> ChatOpenAI | None:
        for tier in self._FALLBACK_ORDER:
            model = self._build(tier)
            if model is not None:
                log.warning("目标档位缺少 API Key，已降级使用 %s", tier.value)
                return model
        return None

    def _provider(self, tier: Tier) -> Provider:
        settings = self.settings
        providers = {
            Tier.BALANCED: Provider(
                "deepseek",
                settings.deepseek_api_key,
                settings.deepseek_model,
                settings.deepseek_base_url,
            ),
            Tier.FAST: Provider(
                "qwen",
                settings.qwen_api_key,
                settings.qwen_model,
                settings.qwen_base_url,
            ),
        }
        return providers[tier]
