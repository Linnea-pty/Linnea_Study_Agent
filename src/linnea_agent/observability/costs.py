"""模型单价表（美元 / 百万 tokens），仅用于估算成本，可按官方最新价格调整。"""

from __future__ import annotations

# (输入价格, 输出价格)，单位：美元 / 1M tokens
PRICING: dict[str, tuple[float, float]] = {
    "deepseek-chat": (0.27, 1.10),
    "deepseek-reasoner": (0.55, 2.19),
    "qwen-flash": (0.10, 0.40),
    "qwen-plus": (0.40, 1.20),
    "qwen-max": (1.60, 6.40),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """估算一次调用的成本（美元）。未知模型按 0 计。"""
    input_price, output_price = PRICING.get(model, (0.0, 0.0))
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000
