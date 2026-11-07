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
    # 沙箱与历史目录
    file_root: Path
    history_dir: Path

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
                "QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),

            tavily_api_key=_env("TAVILY_API_KEY"),
            enable_webpage_tool=_as_bool(_env("ENABLE_WEBPAGE_TOOL", "true")),
            enable_search_tool=_as_bool(_env("ENABLE_SEARCH_TOOL", "true")),

            file_root=Path(_env("AGENT_FILE_ROOT", str(PROJECT_ROOT / "sandbox"))),
            history_dir=Path(_env("AGENT_HISTORY_DIR", str(PROJECT_ROOT / "histories"))),
        )


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
