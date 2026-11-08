"""tier 路由中间件：按运行期 context 的档位动态切换模型。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call

from linnea_agent.shared.llm import ModelPool
from linnea_agent.shared.tier import Tier


@dataclass(frozen=True, slots=True)
class AgentContext:
    """单次运行的上下文，携带模型档位。"""

    tier: Tier = Tier.BALANCED


def build_tier_middleware(pool: ModelPool):
    """构建按档位切换模型的中间件。"""

    @wrap_model_call
    def inject_model_by_tier(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        tier = _tier_of(request)
        if tier is None:
            return handler(request)
        return handler(request.override(model=pool.get(tier)))

    return inject_model_by_tier


def _tier_of(request: ModelRequest) -> Tier | None:
    runtime = getattr(request, "runtime", None)
    ctx = getattr(runtime, "context", None) if runtime is not None else None
    return ctx.tier if isinstance(ctx, AgentContext) else None
