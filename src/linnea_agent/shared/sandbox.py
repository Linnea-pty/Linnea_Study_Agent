"""沙箱安全文件读取：限制根目录与后缀，阻断符号链接逃逸。"""

from __future__ import annotations

from pathlib import Path

ALLOWED_SUFFIXES = frozenset({".txt", ".md", ".json", ".csv", ".log", ".py"})
DEFAULT_MAX_BYTES = 8000


class SandboxViolation(ValueError):
    """沙箱访问违规。"""


def safe_read_text(path: str, root: Path, max_bytes: int = DEFAULT_MAX_BYTES) -> str:
    """在沙箱根目录内安全读取文本文件。

    - 相对路径按沙箱根解析，绝对路径必须位于根目录内；
    - 通过 resolve 解析符号链接，阻断目录逃逸；
    - 仅允许白名单后缀，并截断到 max_bytes。
    """
    root = Path(root).expanduser().resolve()
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    real = candidate.resolve(strict=True)

    if not real.is_relative_to(root):
        raise SandboxViolation(f"路径不在允许目录内：{path}")
    if real.suffix.lower() not in ALLOWED_SUFFIXES:
        raise SandboxViolation(f"不支持的文件类型：{real.suffix}")
    return real.read_text(encoding="utf-8", errors="ignore")[:max_bytes]
