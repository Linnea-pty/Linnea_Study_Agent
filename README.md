# Linnea_Study_Agent

一个基于 Python 的多模型个人 Agent 学习与实战项目，采用领域驱动设计（DDD）进行模块划分。目标是构建能处理复杂学术问题、检索网络学术信息、识别网页题目并提供学习辅助的多模型 Agent，同时具备清晰的工程化演进路径。

> **使用边界**：网页题目识别与解题辅助功能仅用于个人学习、思路启发与代码调试。使用者需自行遵守刷题平台服务条款、robots 协议及所在学校学术诚信规范。本项目不提供自动提交、绕过登录/验证码、批量抓题或代考代做能力。

## 版本演进

### v0.4.1（当前）

相比 v0.4.0 的修复：

- **解题行为**：系统提示词明确“读题后必须作答”；用户说“做这个题 / 生成代码”时用 `full` 模式直接给出可提交代码，不再复述题面或只给步骤。`read_problem` 的默认模式改为 `full`。
- **PTA 真实页面适配**：支持 `div.rendered-markdown` 题面与 CodeMirror 样例（`div[data-code]` / `.cm-line`），修正标题带站点后缀、题干混入样例、限制字段为空的问题；题干中的代码块（如数字拼音对照表）会保留。
- **完整答案默认开启**：`ALLOW_FULL_ANSWER` 默认 `true`（个人学习用途），可设为 `false` 强制只给提示/分步；“不自动提交”等合规约束不变。
- **Web 界面反馈**：Gradio 改为流式回显，先显示“正在思考…”再替换为回答；单轮异常转为可见错误信息，避免看起来“没有反应”。
- **Windows 代理兼容**：启动 Web 前清理 `NO_PROXY` 中 httpx 无法解析的 `[::1]`，避免 Gradio 导入时报 `Invalid port: ':1]'`。
- **健壮性**：模型返回多模态 `content` 时统一拼接为文本；退出时忽略浏览器跨线程回收异常；新增 8 例测试，总计 54 例（含 3 个 PTA 真实页面端到端验证）。

### v0.4.0

相比 v0.3.0 的改进：

- **网页题目识别 MVP**：新增 `web_tutor/` 领域，通过 URL 或本机 CDP 读取当前刷题页面，用标准库 `html.parser` 做零依赖 DOM 解析，结构化提取题干、样例、限制、标签、图片与表格。
- **站点适配器与类型识别**：`ProblemAdapter` 协议 + PTA 适配器 + 通用回退适配器，自动识别编程题 / 选择题 / 填空题。
- **三种作答模式与学术诚信**：提示 / 分步解析 / 完整答案三档输出，完整答案默认关闭（`ALLOW_FULL_ANSWER`），并附带"不自动提交"合规约束。
- **工具接入**：`build_tools` 新增只读工具 `read_problem`，可通过 `ENABLE_WEB_TUTOR_TOOL` 开关；新增 10 例离线测试（不启动浏览器），测试由 36 例增至 46 例。
- **浏览器启动容错**：系统临时目录不可写（Windows 受控文件夹访问、企业策略、沙箱）导致 Playwright `mkdtemp` 报 EPERM 时，自动改用项目内 `.tmp/playwright` 重启驱动并重试一次；若浏览器装在项目内 `.playwright/browsers`，启动时自动识别该路径，无需手动设置环境变量。
- **修复**：`read_webpage` 去掉对 `aria_snapshot()` 文本的二次 JSON 序列化，避免转义噪声。

### v0.3.0

相比 v0.2.0 的改进：

- **降低耦合、消除冗余**：模型档位 `Tier` 下沉为 `shared/tier.py` 共享枚举，消除跨层字符串魔法值；模型提供方抽象为 `Provider` 数据类，`ModelPool` 数据驱动去除 if-else；拆分职责混杂的 `chat/models.py`（关键词归入路由、角色映射归入历史持久化），删除冗余的 `ROLE_MAP`/`role_of`/`PERSIST_ROLES`。
- **可观测性与成本控制**：新增 `observability/` 领域，通过 LangChain 回调自动累计每次调用的 token 与成本，支持预算熔断（`BUDGET_LIMIT`）。
- **模型调用韧性**：`ModelPool` 增加超时（`MODEL_TIMEOUT`）与重试（`MODEL_MAX_RETRIES`）配置，缺 Key 自动降级（balanced → fast）。
- **学术检索能力落地**：新增 `academic/` 领域，接入 arXiv / Semantic Scholar / OpenAlex 三个数据源，多源聚合去重排序，支持 GB/T 7714、APA、MLA 引用生成，并以 `search_papers` 工具暴露给 Agent。
- **评估体系与集成测试**：新增 `evaluation/` 离线路由评估集，补充 ChatService 编排集成测试，测试由 22 例增至 36 例。

### v0.2.0

- 修复 import 混乱与缺失模块，实现 `build_agent`、`ModelPool`、`Settings`，统一包内绝对导入与依赖注入，补充首批单元测试。

## 项目状态

- 当前版本：v0.4.1
- 状态：开发中 / 实验性项目
- 适用场景：学习与实践大模型 Agent 的底层架构、工具调用与路由机制，服务于学生学术实践与刷题学习辅助场景。

## 核心特性

- **动态模型路由**：按输入意图（代码 / 推理 / 简单问答）自动路由至 DeepSeek、Qwen 等模型，平衡成本与效果。
- **丰富的工具生态**：内置数学计算、时间查询、Tavily 联网搜索、Playwright 网页抓取、沙箱文件读取、学术论文检索等能力。
- **完善的会话记忆**：Web 端与 CLI 端独立历史记录，支持多轮对话并持久化到本地。
- **双端启动**：同时提供 Gradio Web 界面与 CLI 命令行交互。
- **安全优先**：在计算、文件读取、网页抓取等环节内置沙箱与防护机制。
- **可观测性与成本控制**：自动累计每次调用的 token 与成本，支持预算熔断。
- **学术检索与引用**：多源检索（arXiv / Semantic Scholar / OpenAlex）聚合去重，支持 GB/T 7714、APA、MLA 引用生成。
- **网页题目识别与解题辅助**：可读取当前刷题页面，结构化识别题干、样例、图片与公式，按"提示 / 分步解析 / 完整答案"模式给出学习辅助；编程题支持参考代码生成与本地样例验证，但不自动提交。

## 功能清单
标注说明: 

- [x] 表示已经实现
### 模型与路由
- [x] 多模型接入（DeepSeek、Qwen 等）
- [x] 基于意图的动态模型路由（代码 / 推理 / 简单问答）
- [x] 模型 fallback 与自动降级机制
- [ ] 学术场景细粒度路由（文献检索 / 数据分析 / 论文写作 / 公式推导）

### 学术信息检索与文献管理
- [x] 通用联网搜索（Tavily）
- [x] 学术数据库检索（arXiv、Semantic Scholar、OpenAlex；CrossRef、PubMed 待接入）
- [x] 多源结果聚合、去重、排序
- [ ] 引文滚雪球与可复现检索记录导出
- [ ] 文献元数据规范化、个人文献库与标签管理
- [ ] PDF 全文解析、多模态阅读与深度笔记沉淀

### 学术写作辅助
- [ ] 选题分析、大纲规划、段落草稿与润色
- [x] 参考文献自动生成（GB/T 7714、APA、MLA）
- [ ] 引用一致性检查
- [ ] DOI 核验与引用真伪检查

### 复杂问题推理与知识组织
- [ ] Agentic RAG（多步推理、自适应检索、自我修正）
- [ ] 学术知识图谱构建与推理
- [ ] 多模态证据整合与长文档分层理解

### 学习与教学辅助
- [ ] 概念分层讲解、纠正性学习反馈
- [ ] 自动测验生成与错题追踪、个性化学习路径
- [ ] 代码复现辅助

### 网页题目识别与解题辅助（PTA 等刷题平台）
- [x] 基础网页抓取能力（Playwright）
- [x] 当前页面题目区域结构化提取（题干、样例、限制、标签）
- [ ] 题目图片 / 公式 / 表格 / 附件识别解析
- [x] 站点适配器机制、题目类型识别
- [x] 提示 / 分步解析 / 完整答案三种输出模式
- [ ] 编程题参考代码生成与本地沙箱样例验证
- [ ] 复杂度分析、答案可信度标注
- [ ] 用户授权与隐私控制、学术诚信模式、平台合规适配

### 学术规范与安全
- [x] 沙箱文件读取（限制后缀与根目录，阻断符号链接逃逸）
- [x] 安全数学计算（AST 白名单，杜绝 eval）
- [ ] 学术诚信护栏、敏感内容过滤与提示词注入防护
- [ ] 操作审计日志

### 工程化与可观测性
- [x] 多端支持（Gradio Web + CLI）、会话历史持久化与原子写入
- [x] token / 成本用量追踪与预算熔断
- [x] 路由准确率离线评估集
- [ ] 全链路 Trace（Langfuse / OpenTelemetry）
- [ ] 多租户隔离、MCP / A2A 协议支持

## 技术栈

**当前**：uv（环境管理）、LangChain / LangGraph（核心框架）、ChatOpenAI（兼容 DeepSeek、通义千问）、Gradio（前端）、Playwright / langchain-tavily（网页解析与搜索）、arXiv / Semantic Scholar / OpenAlex API（学术检索）、标准库 urllib（HTTP 客户端，零额外依赖）。

**面向后续能力的推荐补充**：

| 领域 | 推荐技术 | 用途 |
|---|---|---|
| 学术检索扩展 | CrossRef / PubMed API | 更多数据源与 DOI 核验 |
| PDF 解析 | PyMuPDF、pdfplumber、Unstructured | 全文结构化提取 |
| 多模态理解 | VLM（如 Qwen-VL） | 图表、公式、表格识别 |
| 知识图谱 | Neo4j / NetworkX + LLM | 实体关系抽取与推理 |
| 向量检索 | Weaviate / Qdrant / pgvector | 语义检索与 RAG |
| 引用管理 | CrossRef API、citeproc | DOI 核验与参考文献格式化 |
| 页面接入 | Playwright / CDP、浏览器扩展 / 书签脚本 | 手动读取当前活动页面 DOM 与截图 |
| 代码题验证 | Docker / gVisor 沙箱 + 本地判题 | 隔离运行参考代码，不接触提交接口 |
| 可观测性 | Langfuse / OpenTelemetry | 全链路 Trace、评估 |

## 目录结构

项目采用 src 布局，源码位于 `src/linnea_agent/`，按领域分包并通过依赖注入组装：

```
src/linnea_agent/
├── __init__.py        # 公共 API 导出（Settings / ModelPool / build_agent / Tier）
├── config.py          # Settings 集中配置（从环境变量加载）
├── main.py            # 组合根与统一入口（启动 Web 或 CLI）
├── agent/             # Agent 领域：组装模型、中间件与工具
│   ├── builder.py         # build_agent 组装
│   └── middleware.py      # 档位路由中间件
├── chat/              # 聊天领域：路由、历史、编排、接口适配
├── academic/          # 学术检索领域：多源检索、聚合去重、引用生成
│   └── sources/           # arXiv / Semantic Scholar / OpenAlex 数据源
├── web_tutor/         # 网页题目识别：页面读取、DOM 解析、站点适配、模式输出
├── observability/     # 可观测性：用量追踪、成本估算、回调埋点
├── evaluation/        # 离线评估体系：路由准确率等
├── tools/             # 工具领域：计算、时间、文件、网页、检索
└── shared/            # 共享基础设施：模型池、档位枚举、HTTP、沙箱、浏览器

tests/                 # 单元 + 集成测试
```

建议后续新增领域包：`knowledge/`（知识图谱与 RAG）。

## 安装与配置

```bash
# 1. 克隆并安装依赖（需先安装 uv）
git clone https://github.com/Linnea-pty/Linnea_Agent_Study.git
cd Linnea_Agent_Study
uv sync

# 2. 安装 Playwright Chromium 内核
uv run playwright install chromium

# 若 Windows 系统目录不可写（报 EPERM: mkdir ...ms-playwright），改装到项目内：
# PowerShell:
#   $env:TEMP = "$PWD\.tmp"; $env:TMP = $env:TEMP
#   $env:PLAYWRIGHT_BROWSERS_PATH = "$PWD\.playwright\browsers"
#   uv run playwright install chromium
# 程序启动时会自动识别 .playwright/browsers，无需额外配置。
```

复制根目录 `.env.example` 为 `.env` 并填入 API Key：

```bash
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
QWEN_API_KEY=sk-xxx
QWEN_MODEL=qwen-flash
TAVILY_API_KEY=tvly-xxx

# 可选：工具开关与本地目录（均有默认值）
ENABLE_WEBPAGE_TOOL=true
ENABLE_SEARCH_TOOL=true
ENABLE_ACADEMIC_TOOL=true
AGENT_FILE_ROOT=./sandbox
AGENT_HISTORY_DIR=./histories

# 可选：模型韧性与成本控制
MODEL_TIMEOUT=60
MODEL_MAX_RETRIES=2
BUDGET_LIMIT=0

# 可选：网页题目识别（只读，不自动提交）
ENABLE_WEB_TUTOR_TOOL=true
WEB_TUTOR_CDP_URL=http://127.0.0.1:9222
WEB_TUTOR_MAX_CHARS=6000
ALLOW_FULL_ANSWER=true
```

## 使用指南

```bash
uv run linnea-agent        # 启动 Gradio Web（默认 http://127.0.0.1:7860）
uv run linnea-agent-cli    # 启动 CLI 终端模式
```

网页题目识别：在对话中调用 `read_problem` 工具，`url` 留空时通过 CDP 读取当前活动标签页，也可直接传入题目 URL；`mode` 支持 `full`（默认，直接给出完整解答/代码）、`steps`、`hint`。只读可见内容，不点击、不提交；不需要完整答案时可设置 `ALLOW_FULL_ANSWER=false`。示例：

```text
https://pintia.cn/problem-sets/.../exam/problems/type/7?problemSetProblemId=...
做这个题，直接给代码
```

## 测试与代码质量

```bash
uv run pytest            # 运行单元测试
uv run ruff check .      # 代码风格与静态检查
uv run mypy src          # 类型检查
```

## 架构与安全设计

- **路由一致性**：通过 `context_schema=AgentContext` 与运行期 `context=AgentContext(tier=...)` 传递档位，中间件按档位动态切换模型，保证中间件执行与 UI 展示的模型档位一致；目标档位缺 API Key 时自动降级到可用档位。
- **模型韧性**：`ModelPool` 统一配置超时（`MODEL_TIMEOUT`）与重试（`MODEL_MAX_RETRIES`），惰性构建，缺 Key 按 balanced → fast 降级。
- **成本预算熔断**：通过 LangChain 回调自动累计每次调用的 token 与成本，超出 `BUDGET_LIMIT` 时在调用前熔断。
- **历史记录安全**：显式类型映射表解析消息，临时文件 `os.replace` 原子写，杜绝历史损坏与上下文污染。
- **沙箱隔离**：`read_local_file` 限制后缀与固定根目录，通过 resolve 阻断符号链接逃逸。
- **安全计算**：使用 `ast` 语法树白名单实现数学计算，杜绝 eval 代码注入。
- **多源学术检索**：arXiv / Semantic Scholar / OpenAlex 结果聚合去重（DOI 优先）并按年份排序，单数据源失败自动降级不影响整体。
- **高并发抓取**：基于 `threading.local` 与 `atexit` 实现 Playwright 浏览器线程级复用与统一回收。
- **页面读取最小权限**：题目识别仅在当前活动标签页手动触发，默认只读可见内容；不后台遍历、不批量抓取、不绕过登录与验证码。
- **不自动提交**：参考代码仅在本地沙箱运行样例，不调用平台提交接口。
- **学术诚信可配置**：默认允许完整答案（`ALLOW_FULL_ANSWER=true`），可设为 `false` 强制只给提示或分步解析。
- **数据脱敏与最小持久化**：题目原文、截图默认不落盘或仅短期缓存，可一键清除，敏感信息自动脱敏。

## 工程化演进路线

1. **学术检索与引用能力深化**：已完成 arXiv / Semantic Scholar / OpenAlex 检索与 GB/T 7714、APA、MLA 引用生成；后续补 CrossRef / PubMed、DOI 核验与 PDF 解析。
2. **网页题目识别 MVP**：已完成 URL / CDP 读取活动页面、题目结构化提取、站点适配与类型识别、三种输出模式；后续补公式 / 附件解析、参考代码沙箱验证与复杂度分析。
3. **可观测性与评估**：接入 Langfuse / OpenTelemetry，构建检索 / 引用 / 忠实度 / 代码通过率评估集。
4. **复杂推理与知识组织**：Agentic RAG、知识图谱、多模态文献阅读。
5. **安全与多租户**：学术诚信护栏、操作审计、多租户隔离。

## 常见问题（FAQ）

- **Missing credentials**：检查根目录 `.env` 是否存在且无多余空格或引号。
- **No module named 'app'**：在项目根目录执行 `uv run`，不要在 `src` 中单独运行脚本。
- **Executable doesn't exist**：运行 `uv run playwright install chromium`；若系统目录不可写，按上方「安装与配置」中的项目内安装命令处理，程序会自动识别 `.playwright/browsers`。
- **Playwright 报 EPERM / mkdtemp**：系统 Temp 目录不可写。程序会自动回退到项目内 `.tmp/playwright`；若仍失败，请检查 Windows「受控文件夹访问」或杀毒软件对 Temp 的限制，并确认项目目录可写。
- **如何识别当前 PTA 题目**：通过手动触发读取当前活动页面，仅提取可见内容，不后台抓取、不自动提交；使用前请确认符合平台条款与学校规范。
- **会直接给最终答案吗**：默认提示与分步解析模式，完整答案需显式开启，代码仅在本地沙箱运行样例。

## 贡献

欢迎提交 Issue 或 Pull Request；较大改动请先开 Issue 讨论。

## 许可证

本项目采用 MIT License 开源。
