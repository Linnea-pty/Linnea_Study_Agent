"""沙箱文件读取测试。"""

import pytest

from linnea_agent.shared.sandbox import SandboxViolation, safe_read_text


def test_read_relative_path(tmp_path):
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    assert safe_read_text("a.txt", root=tmp_path) == "hello"


def test_read_absolute_path(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello", encoding="utf-8")
    assert safe_read_text(str(f), root=tmp_path) == "hello"


def test_rejects_escape(tmp_path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    with pytest.raises(SandboxViolation):
        safe_read_text("../outside.txt", root=tmp_path)


def test_rejects_unsupported_suffix(tmp_path):
    (tmp_path / "a.exe").write_text("x", encoding="utf-8")
    with pytest.raises(SandboxViolation):
        safe_read_text("a.exe", root=tmp_path)


def test_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        safe_read_text("missing.txt", root=tmp_path)
