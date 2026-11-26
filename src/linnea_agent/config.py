"""集中式应用配置：从环境变量加载，供各模块依赖注入使用。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录：src/linnea_agent/config.py -> parents[2] 即仓库根
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Settings:
    """运行配置。所有字段只读，避免运行期被意外修改。"""

    # DeepSeek（balanced 档位）
    deepseek_api_key: str
    deepseek_model: str
    deepseek_base_url: str
    # Qwen（fast 档位）
    qwen_api_key: str
    qwen_model: str
    qwen_base_url: str
    # Tavily 搜索
    tavily_api_key: str
    # 工具开关
    enable_webpage_tool: bool
    enable_search_tool: bool
    enable_academic_tool: bool
    # 模型调用韧性
    model_timeout: float
    model_max_retries: int
    # 成本预算（美元，0 表示不限）
    budget_limit: float
    # 沙箱与历史目录
    file_root: Path
    history_dir: Path
    # 网页题目识别（只读，不自动提交）
    enable_web_tutor_tool: bool = True
    web_tutor_cdp_url: str = "http://127.0.0.1:9222"
    web_tutor_max_chars: int = 6000
    # 完整答案：个人学习场景默认允许，可显式关闭以强制只给提示
    allow_full_answer: bool = True

    @classmethod
    def from_env(cls) -> Settings:
        """从环境变量构建配置，自动加载根目录 .env（不覆盖已存在变量）。"""
        load_dotenv()
        return cls(
            deepseek_api_key=_env("DEEPSEEK_API_KEY"),
            deepseek_model=_env("DEEPSEEK_MODEL", "deepseek-chat"),
            deepseek_base_url=_env("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            qwen_api_key=_env("QWEN_API_KEY"),
            qwen_model=_env("QWEN_MODEL", "qwen-flash"),
            qwen_base_url=_env(
                "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
            ),
            tavily_api_key=_env("TAVILY_API_KEY"),
            enable_webpage_tool=_as_bool(_env("ENABLE_WEBPAGE_TOOL", "true")),
            enable_search_tool=_as_bool(_env("ENABLE_SEARCH_TOOL", "true")),
            enable_academic_tool=_as_bool(_env("ENABLE_ACADEMIC_TOOL", "true")),
            model_timeout=float(_env("MODEL_TIMEOUT", "60")),
            model_max_retries=int(_env("MODEL_MAX_RETRIES", "2")),
            budget_limit=float(_env("BUDGET_LIMIT", "0")),
            file_root=Path(_env("AGENT_FILE_ROOT", str(PROJECT_ROOT / "sandbox"))),
            history_dir=Path(_env("AGENT_HISTORY_DIR", str(PROJECT_ROOT / "histories"))),
            enable_web_tutor_tool=_as_bool(_env("ENABLE_WEB_TUTOR_TOOL", "true")),
            web_tutor_cdp_url=_env("WEB_TUTOR_CDP_URL", "http://127.0.0.1:9222"),
            web_tutor_max_chars=int(_env("WEB_TUTOR_MAX_CHARS", "6000")),
            allow_full_answer=_as_bool(_env("ALLOW_FULL_ANSWER", "true")),
        )


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
