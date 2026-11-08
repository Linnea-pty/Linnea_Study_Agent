"""arXiv 数据源解析测试（离线，构造 XML 样例）。"""

import xml.etree.ElementTree as ET

from linnea_agent.academic.sources.arxiv import ArxivSource

_ENTRY = """
<entry xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
    <title>Test Paper</title>
    <author><name>Alice</name></author>
    <author><name>Bob</name></author>
    <published>2023-05-01T00:00:00Z</published>
    <id>http://arxiv.org/abs/2301.00001</id>
    <summary>Abstract text</summary>
    <arxiv:doi>10.1/test</arxiv:doi>
</entry>
"""


def test_parse_entry():
    source = ArxivSource()
    entry = ET.fromstring(_ENTRY)
    paper = source._parse(entry)

    assert paper.title == "Test Paper"
    assert paper.authors == ["Alice", "Bob"]
    assert paper.year == 2023
    assert paper.doi == "10.1/test"
    assert paper.abstract == "Abstract text"
