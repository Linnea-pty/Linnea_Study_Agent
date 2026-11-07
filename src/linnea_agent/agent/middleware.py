"""tier 路由中间件：按运行期 context 的档位动态切换模型。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from urllib import request

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call

from linnea_agent.shared.llm import ModelPool


@dataclass(frozen=True, slots=True)
class AgentContext:
    """单次运行的上下文，携带模型档位。"""

    tier: str = "balanced"


def _tier_of(request: ModelRequest) -> str | None:
    runtime = getattr(request, "runtime", None)
    ctx = getattr(runtime, "context", None) if runtime is not None else None
    if ctx is None:
        return None
    if isinstance(ctx, dict):
        return ctx.get("tier")
    return getattr(ctx, "tier", None)


def build_tier_middleware(pool: ModelPool):
    """构建按档位切换模型的中间件。"""

    @wrap_model_call
    def inject_model_by_tier(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        tier = _tier_of(request)
        if not tier:
            return handler(request)
        return handler(request.override(model=pool.get(tier)))

    return inject_model_by_tier
