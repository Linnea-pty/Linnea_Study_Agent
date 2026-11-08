"""模型档位枚举：横跨路由、中间件与模型池的共享概念。"""

from enum import StrEnum


class Tier(StrEnum):
    FAST = "fast"
    BALANCED = "balanced"
