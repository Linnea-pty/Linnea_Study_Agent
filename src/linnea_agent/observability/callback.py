"""LangChain 回调：在模型调用结束时记录 token 用量。"""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from linnea_agent.observability.usage import UsageTracker


class UsageCallbackHandler(BaseCallbackHandler):
    """从 LLMResult 提取 token 用量并写入 UsageTracker。"""

    def __init__(self, tracker: UsageTracker):
        self.tracker = tracker

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:  # noqa: ARG002
        info = response.llm_output or {}
        usage = info.get("token_usage") or {}
        if not usage:
            return
        self.tracker.record(
            model=str(info.get("model_name") or "unknown"),
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
        )
