"""站点适配器：从页面 DOM 中提取结构化题目。

通用适配器负责大多数页面；站点适配器只提供更精确的内容根选择器。
所有解析均基于标准库 html.parser，便于离线测试。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from linnea_agent.web_tutor.dom import (
    NOISE_TAGS,
    Node,
    css_key,
    has_block_children,
    iter_nodes,
    parse_html,
    raw_text,
    text_of,
)
from linnea_agent.web_tutor.schemas import Problem, ProblemKind, Sample

_HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")
_BLOCK_TAGS = (*_HEADINGS, "p", "li", "td", "th", "dd", "dt", "blockquote", "figcaption")
_NOISE_KEY = re.compile(
    r"(^|[\s_-])(nav|menu|breadcrumb|sidebar|comment|recommend|related|login|footer|"
    r"toolbar|pagination)([\s_-]|$)"
)
_CONTENT_KEY = re.compile(
    r"(problem|question|subject|statement|description|article|markdown|题目|题干|content)"
)
_SAMPLE_INPUT = re.compile(r"(输入样例|样例输入|输入示例|sample\s*input|^输入$)", re.IGNORECASE)
_SAMPLE_OUTPUT = re.compile(r"(输出样例|样例输出|输出示例|sample\s*output|^输出$)", re.IGNORECASE)
_SAMPLE_MARK = re.compile(
    r"(输入样例|样例输入|输入示例|输出样例|样例输出|输出示例|sample\s*(input|output))",
    re.IGNORECASE,
)
_EMPTY_SAMPLE = {"无", "无输入", "无输出", "none", "n/a", "-"}
_CONSTRAINT = re.compile(r"(时间限制|内存限制|时限|内存|限制|time\s*limit|memory\s*limit)", re.I)
_CHOICE = re.compile(r"(单选题|多选题|以下.{0,12}正确|A[\.．、].{0,40}B[\.．、])", re.S)
_FILL = re.compile(r"(填空题|____|_{3,})")
_PROGRAMMING = re.compile(r"(输入格式|输出格式|输入描述|输出描述|编程题|代码题)")


class ProblemAdapter(Protocol):
    """站点适配器接口。"""

    name: str

    def matches(self, url: str) -> bool: ...

    def extract(self, html: str, url: str = "") -> Problem: ...


@dataclass(frozen=True, slots=True)
class _Block:
    tag: str
    text: str


@dataclass(frozen=True, slots=True)
class _Pre:
    text: str
    context: tuple[str, ...] = ()
    css: str = ""


class GenericProblemAdapter:
    """基于内容根与文本块启发式的通用适配器。"""

    name = "generic"
    content_selectors: tuple[str, ...] = ()

    def matches(self, url: str) -> bool:
        return True

    def extract(self, html: str, url: str = "") -> Problem:
        root, doc_title = parse_html(html)
        content = _select_content_root(root, self.content_selectors)
        blocks, pres = _collect(content)

        title = _pick_title(blocks, doc_title)
        samples = _pair_samples(pres)
        statement = _build_statement(blocks, title)
        constraints = _pick_constraints(blocks)
        tags = _pick_tags(content)
        images = _pick_images(content)
        tables = _pick_tables(content)

        return Problem(
            title=title,
            statement=statement,
            url=url,
            source=self.name,
            kind=_classify(title, statement, samples, tags),
            samples=tuple(samples),
            constraints=tuple(constraints),
            tags=tuple(tags),
            images=tuple(images),
            tables=tuple(tables),
        )


class PTAAdapter(GenericProblemAdapter):
    """PTA（pintia.cn）站点适配器。

    PTA 的题面在 ``div.rendered-markdown`` 中，样例代码位于 CodeMirror
    （``div[data-code][data-lang=in|out]`` 内的 ``.cm-line``），
    通用启发式无法稳定读取，因此单独处理。
    """

    name = "pta"
    content_selectors = (
        ".rendered-markdown",
        ".problem-content",
        ".problemContent",
        "#problem-content",
        ".subject-content",
        ".question-content",
        "[class*=problem]",
        "[class*=subject]",
    )

    def matches(self, url: str) -> bool:
        return "pintia.cn" in url.lower()

    def extract(self, html: str, url: str = "") -> Problem:
        root, doc_title = parse_html(html)
        content = _find_rendered_markdown(root)
        if content is None:
            return super().extract(html, url)

        blocks, samples = _pta_blocks(content)
        title = _clean_title(doc_title) or _pick_title(blocks, "")
        statement = _build_statement(blocks, title)

        return Problem(
            title=title,
            statement=statement,
            url=url,
            source=self.name,
            kind=_classify(title, statement, samples, []),
            samples=tuple(samples),
            constraints=tuple(_scan_constraints(root)),
            tags=tuple(_pick_tags(content)),
            images=tuple(_pick_images(content)),
            tables=tuple(_pick_tables(content)),
        )


def _find_rendered_markdown(root: Node) -> Node | None:
    candidates = [
        node
        for node in iter_nodes(root)
        if "rendered-markdown" in node.attrs.get("class", "").split()
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda node: len(raw_text(node)))


def _clean_title(doc_title: str) -> str:
    """去掉站点后缀（如「- 拼题A…」）并合并多余空白。"""
    title = re.split(r"\s+[-–—|]\s+", doc_title.strip(), maxsplit=1)[0]
    return re.sub(r"\s+", " ", title).strip()


def _is_code_container(node: Node) -> bool:
    return node.tag == "pre" or "data-code" in node.attrs


def _inside_code(node: Node) -> bool:
    current = node.parent
    while current is not None:
        if _is_code_container(current):
            return True
        current = current.parent
    return False


def _code_text(node: Node) -> str:
    """读取代码块文本；兼容 CodeMirror 的 .cm-line 行结构与普通 pre。"""
    lines = [
        text_of(item)
        for item in iter_nodes(node)
        if "cm-line" in item.attrs.get("class", "").split()
    ]
    lines = [line for line in lines if line]
    if lines:
        return "\n".join(lines)

    pres = [raw_text(item) for item in iter_nodes(node) if item.tag == "pre"]
    if pres:
        return "\n".join(part.strip("\n") for part in pres).strip("\n")
    return raw_text(node).strip("\n")


def _clean_sample(text: str) -> str:
    stripped = text.strip()
    return "" if stripped.lower() in _EMPTY_SAMPLE else stripped


def _pta_blocks(content: Node) -> tuple[list[_Block], list[Sample]]:
    """按「题干 -> 输入样例 -> 输出样例」顺序读取 PTA 题面。"""
    blocks: list[_Block] = []
    samples: list[Sample] = []
    pending: str | None = None
    mode: str | None = None
    in_samples = False

    for node in iter_nodes(content):
        if _inside_code(node):
            continue
        if node.tag in _HEADINGS:
            text = text_of(node)
            if not text:
                continue
            if _SAMPLE_INPUT.search(text):
                mode, in_samples = "in", True
                continue
            if _SAMPLE_OUTPUT.search(text):
                mode, in_samples = "out", True
                continue
            if not in_samples:
                blocks.append(_Block(node.tag, text))
            continue
        if _is_code_container(node):
            text = _code_text(node)
            if mode == "in":
                pending, mode = _clean_sample(text), None
            elif mode == "out":
                samples.append(Sample(pending or "", _clean_sample(text)))
                pending, mode = None, None
            elif not in_samples:
                # 题干中的代码块（如数字拼音对照表）保留在题干里
                blocks.append(_Block("pre", text))
            continue
        if in_samples or node.tag not in ("p", "li", "td", "th", "blockquote"):
            continue
        if has_block_children(node):
            continue
        text = text_of(node)
        if text:
            blocks.append(_Block(node.tag, text))

    if pending is not None:
        samples.append(Sample(pending, ""))
    return blocks, samples


_LIMIT_RE = re.compile(
    r"(代码长度限制|时间限制|内存限制|栈限制|运行时间限制)\s*"
    r"([0-9]+(?:\.[0-9]+)?\s*(?:KB|MB|GB|ms|s|秒))",
    re.IGNORECASE,
)


def _scan_constraints(root: Node) -> list[str]:
    """按「标签 + 数值」读取限制，避免把整段题面误当限制。"""
    text = raw_text(root)
    found: list[str] = []
    for label, value in _LIMIT_RE.findall(text):
        entry = f"{label} {value}"
        if entry not in found:
            found.append(entry)
    return found[:8]


def build_adapters() -> list[ProblemAdapter]:
    """返回按优先级排列的适配器。"""
    return [PTAAdapter(), GenericProblemAdapter()]


def _select_content_root(root: Node, selectors: tuple[str, ...]) -> Node:
    if selectors:
        selected = _match_selectors(root, selectors)
        if selected is not None:
            return selected

    matches = [
        node
        for node in _walk_nodes(root)
        if _CONTENT_KEY.search(css_key(node)) and not _is_noise(node)
    ]
    if matches:
        return max(matches, key=lambda node: len(raw_text(node)))
    for tag in ("main", "article", "body"):
        node = _find_tag(root, tag)
        if node is not None:
            return node
    return root


def _match_selectors(root: Node, selectors: tuple[str, ...]) -> Node | None:
    for selector in selectors:
        token = selector.lstrip(".#").replace("*", "").lower()
        for node in _walk_nodes(root):
            key = css_key(node)
            if selector.startswith(".") and token in key.split():
                return node
            if selector.startswith("#") and node.attrs.get("id", "").lower() == token:
                return node
            if selector.startswith("[") and token and token in key:
                return node
    return None


def _walk_nodes(node: Node):
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from _walk_nodes(child)


def _find_tag(root: Node, tag: str) -> Node | None:
    for node in _walk_nodes(root):
        if node.tag == tag:
            return node
    return None


def _is_noise(node: Node) -> bool:
    if node.tag in NOISE_TAGS:
        return True
    return bool(_NOISE_KEY.search(css_key(node)))


def _collect(root: Node) -> tuple[list[_Block], list[_Pre]]:
    blocks: list[_Block] = []
    pres: list[_Pre] = []

    def walk(node: Node) -> None:
        for child in node.children:
            if isinstance(child, str):
                continue
            if _is_noise(child):
                continue
            if _is_code_container(child):
                context = tuple(block.text for block in blocks[-2:])
                pres.append(_Pre(_code_text(child), context, css_key(child)))
                continue
            if (
                child.tag in _BLOCK_TAGS
                and not has_block_children(child)
                and not _has_pre(child)
            ):
                text = text_of(child)
                if text:
                    blocks.append(_Block(child.tag, text))
                continue
            walk(child)

    walk(root)
    return blocks, pres


def _has_pre(node: Node) -> bool:
    return any(
        isinstance(child, Node) and (child.tag == "pre" or _has_pre(child))
        for child in node.children
    )


def _pick_title(blocks: list[_Block], doc_title: str) -> str:
    for block in blocks:
        if block.tag in ("h1", "h2") and block.text:
            return block.text
    if doc_title:
        return doc_title
    for block in blocks:
        if block.text:
            return block.text[:120]
    return "未命名题目"


def _pair_samples(pres: list[_Pre]) -> list[Sample]:
    samples: list[Sample] = []
    pending: str | None = None

    for pre in pres:
        label_context = " ".join((*pre.context, pre.css))
        if _SAMPLE_OUTPUT.search(label_context):
            samples.append(Sample(pending or "", pre.text))
            pending = None
            continue
        if _SAMPLE_INPUT.search(label_context):
            if pending is not None:
                samples.append(Sample(pending, ""))
            pending = pre.text
            continue
        if pending is None:
            pending = pre.text
        else:
            samples.append(Sample(pending, pre.text))
            pending = None

    if pending is not None:
        samples.append(Sample(pending, ""))
    return samples


def _build_statement(blocks: list[_Block], title: str) -> str:
    lines: list[str] = []
    for block in blocks:
        text = block.text
        if not text or text == title:
            continue
        # 样例标题之后的内容属于样例区，不再并入题干
        if _SAMPLE_MARK.search(text):
            break
        lines.append(text)
    seen: list[str] = []
    for line in lines:
        if not seen or seen[-1] != line:
            seen.append(line)
    return "\n".join(seen)


def _pick_constraints(blocks: list[_Block]) -> list[str]:
    found: list[str] = []
    for block in blocks:
        for line in block.text.splitlines():
            line = line.strip()
            if line and len(line) <= 120 and _CONSTRAINT.search(line):
                if line not in found:
                    found.append(line)
    return found[:8]


def _pick_tags(root: Node) -> list[str]:
    tags: list[str] = []
    for node in _walk_nodes(root):
        key = css_key(node)
        if not any(token in key for token in ("tag", "label", "badge", "chip")):
            continue
        text = text_of(node)
        if text and len(text) <= 16 and text not in tags:
            tags.append(text)
        if len(tags) >= 8:
            break
    return tags


def _pick_images(root: Node) -> list[str]:
    images: list[str] = []
    for node in _walk_nodes(root):
        if node.tag != "img":
            continue
        src = (node.attrs.get("src") or node.attrs.get("data-src") or "").strip()
        if src and src not in images:
            images.append(src)
    return images[:10]


def _pick_tables(root: Node) -> list[str]:
    tables: list[str] = []
    for node in _walk_nodes(root):
        if node.tag != "table":
            continue
        rows: list[str] = []
        for row in _walk_nodes(node):
            if row.tag != "tr":
                continue
            cells = [text_of(cell) for cell in row.children if isinstance(cell, Node)]
            cells = [cell for cell in cells if cell]
            if cells:
                rows.append(" | ".join(cells))
        if rows:
            tables.append("\n".join(rows))
    return tables[:5]


def _classify(
    title: str, statement: str, samples: list[Sample], tags: list[str]
) -> ProblemKind:
    blob = " ".join((title, statement, " ".join(tags)))
    if _CHOICE.search(blob):
        return ProblemKind.CHOICE
    if _FILL.search(blob):
        return ProblemKind.FILL_BLANK
    if samples or _PROGRAMMING.search(blob):
        return ProblemKind.PROGRAMMING
    return ProblemKind.UNKNOWN
