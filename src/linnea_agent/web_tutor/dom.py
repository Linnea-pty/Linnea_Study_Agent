"""极简 DOM 工具：仅用标准库 html.parser 解析页面，供题目结构化提取使用。

不引入 BeautifulSoup 等额外依赖，保持 README 技术栈（标准库 + Playwright）。
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from html.parser import HTMLParser

VOID_TAGS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source",
     "track", "wbr"}
)
# 这些标签允许在新标签出现时隐式闭合
_AUTO_CLOSE = frozenset({"p", "li", "tr", "td", "th", "option", "dt", "dd"})
_BLOCK_START = frozenset(
    {"address", "article", "div", "dl", "fieldset", "form", "h1", "h2", "h3", "h4", "h5",
     "h6", "hr", "main", "ol", "p", "pre", "section", "table", "ul"}
)
NOISE_TAGS = frozenset(
    {"script", "style", "noscript", "nav", "header", "footer", "aside", "button", "select",
     "textarea", "svg", "canvas", "iframe", "form"}
)
_WS = re.compile(r"[ \t\r\f\v]+")
_BLANK_LINES = re.compile(r"\n{3,}")

class Node:
    """轻量 DOM 节点。"""

    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag: str, attrs: dict[str, str] | None = None, parent: Node | None = None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children: list[Node | str] = []
        self.parent = parent

    def __repr__(self) -> str:  # pragma: no cover - 调试辅助
        return f"<Node {self.tag} children={len(self.children)}>"


class _Builder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#document")
        self.stack: list[Node] = [self.root]
        self.title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self._auto_close(tag)
        node = Node(tag, {key.lower(): (value or "") for key, value in attrs}, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag == "title":
            self._in_title = True
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def _auto_close(self, tag: str) -> None:
        """处理常见的可选闭合标签，避免畸形 HTML 造成深层错位。"""
        while len(self.stack) > 1:
            top = self.stack[-1].tag
            if top == tag and tag in _AUTO_CLOSE:
                self.stack.pop()
            elif top == "p" and tag in _BLOCK_START:
                self.stack.pop()
            elif top in {"td", "th"} and tag in {"td", "th", "tr"}:
                self.stack.pop()
            elif top == "tr" and tag in {"tr", "td", "th"}:
                self.stack.pop()
            else:
                break

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if not data.strip():
            return
        self.stack[-1].children.append(data)


def parse_html(html: str) -> tuple[Node, str]:
    """解析 HTML，返回 (根节点, <title> 文本)。"""
    builder = _Builder()
    builder.feed(html)
    builder.close()
    return builder.root, "".join(builder.title_parts).strip()


def iter_nodes(node: Node) -> Iterator[Node]:
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from iter_nodes(child)


def raw_text(node: Node) -> str:
    """保留换行的纯文本。"""
    parts: list[str] = []

    def walk(current: Node) -> None:
        for child in current.children:
            if isinstance(child, str):
                parts.append(child)
            elif child.tag in {"br"}:
                parts.append("\n")
            elif child.tag in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "pre"}:
                parts.append("\n")
                walk(child)
                parts.append("\n")
            else:
                walk(child)

    walk(node)
    return _normalize("".join(parts))


def text_of(node: Node) -> str:
    """折叠空白后的单行文本。"""
    return _WS.sub(" ", raw_text(node)).strip()


def _normalize(text: str) -> str:
    lines = [_WS.sub(" ", line).strip() for line in text.splitlines()]
    normalized = "\n".join(line for line in lines if line)
    return _BLANK_LINES.sub("\n\n", normalized).strip()


def css_key(node: Node) -> str:
    """class 与 id 的小写拼接，用于选择器启发式。"""
    return f"{node.attrs.get('class', '')} {node.attrs.get('id', '')}".lower()


def has_block_children(node: Node) -> bool:
    return any(
        isinstance(child, Node) and child.tag in {"p", "div", "li", "table", "ul", "ol", "pre"}
        for child in node.children
    )


def find_nodes(root: Node, predicate) -> list[Node]:
    return [node for node in iter_nodes(root) if predicate(node)]
