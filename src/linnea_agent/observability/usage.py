"""用量追踪：累计 token 与成本，支持预算熔断。"""

from __future__ import annotations

from dataclasses import dataclass

from linnea_agent.observability.costs import estimate_cost


@dataclass(frozen=True, slots=True)
class Usage:
    """单次模型调用的用量快照。"""

    model: str
    input_tokens: int
    output_tokens: int
    cost: float


class BudgetExceeded(RuntimeError):
    """成本超出预算上限。"""


class UsageTracker:
    """累计并查询模型用量与成本。"""

    def __init__(self, budget_limit: float = 0.0):
        self.budget_limit = budget_limit
        self._records: list[Usage] = []

    def record(self, model: str, input_tokens: int, output_tokens: int) -> Usage:
        usage = Usage(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=estimate_cost(model, input_tokens, output_tokens),
        )
        self._records.append(usage)
        return usage

    @property
    def calls(self) -> int:
        return len(self._records)

    @property
    def total_input_tokens(self) -> int:
        return sum(usage.input_tokens for usage in self._records)

    @property
    def total_output_tokens(self) -> int:
        return sum(usage.output_tokens for usage in self._records)

    @property
    def total_cost(self) -> float:
        return sum(usage.cost for usage in self._records)

    @property
    def over_budget(self) -> bool:
        return self.budget_limit > 0 and self.total_cost >= self.budget_limit

    def ensure_within_budget(self) -> None:
        if self.over_budget:
            raise BudgetExceeded(
                f"累计成本 {self.total_cost:.4f} 已超过预算上限 {self.budget_limit:.4f}"
            )

    def snapshot(self) -> dict[str, float | int]:
        return {
            "calls": self.calls,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cost": round(self.total_cost, 6),
        }
