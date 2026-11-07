"""本地文件读取工具：绑定沙箱根目录，供 Agent 调用。"""

from __future__ import annotations

from langchain_core.tools import tool

from linnea_agent.config import Settings
from linnea_agent.shared.sandbox import SandboxViolation, safe_read_text


def build_read_local_file_tool(settings: Settings):
    root = settings.file_root

    @tool
    def read_local_file(path: str) -> str:
        """读取沙箱目录内的文本文件。path 可为沙箱内相对路径或绝对路径。"""
        try:
            return safe_read_text(path, root=root)
        except SandboxViolation as exc:
            return f"读取失败：{exc}"
        except FileNotFoundError:
            return "读取失败：文件不存在"
        except Exception as exc:  # noqa: BLE001 - 工具需兜底返回错误信息
            return f"读取失败：{exc}"

    return read_local_file
