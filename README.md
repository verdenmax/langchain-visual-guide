# LangChain 图解教程 · 从零理解整个项目

[![📖 在线阅读](https://img.shields.io/badge/%F0%9F%93%96%20%E5%9C%A8%E7%BA%BF%E9%98%85%E8%AF%BB-Read%20Online-1a7f64?style=for-the-badge)](https://verdenmax.github.io/langchain-visual-guide/)
[![📄 下载 PDF](https://img.shields.io/badge/%F0%9F%93%84%20%E4%B8%8B%E8%BD%BD%20PDF-Download-b4690e?style=for-the-badge)](https://github.com/verdenmax/langchain-visual-guide/releases/latest/download/langchain-visual-guide.pdf)

> 🌐 **在线阅读**：<https://verdenmax.github.io/langchain-visual-guide/>　·　📄 **下载 PDF（全 36 课）**：[langchain-visual-guide.pdf](https://github.com/verdenmax/langchain-visual-guide/releases/latest/download/langchain-visual-guide.pdf)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lessons](https://img.shields.io/badge/lessons-expanding_to_45--55-blue.svg)
![Parts](https://img.shields.io/badge/parts-11-9cf.svg)
![Built with](https://img.shields.io/badge/built%20with-Python%203-3776AB.svg?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)
![Language](https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87-orange.svg)

> 🚧 **C 级扩充中**：本教程正在从旧版 27 课扩展为约 45-55 课的中文成书级深挖版本。新版本强调更多图、worked-example trace、真实源码入口、简化伪代码和自测练习。第一到第四部分现在都是 C 级批次：全局地图、用户 API 基础、Runnable 与 LCEL、LangGraph 心智模型；后续部分会按 Part 分批迁移。

一套面向**完全新手**的可视化（HTML 图解）教程，带你从零开始理解
[LangChain](https://github.com/langchain-ai/langchain) 这个项目——既有**宏观全景**，也有**细节源码**，
每一课都配有**真实代码文件对应**。

> 本教程在 Copilot CLI 中借助 superpowers 的 *brainstorming visual companion* 生成，
> 内容对照 LangChain 仓库真实源码核实。

> 📌 **版本锚点**：对照 **LangChain v1（`langchain_v1`）** 与 **LangGraph** 源码讲解，最后核验于 **2026-06**。
> 源码引用以「**文件 + 符号名**」为主（行号会随上游更新而失效，故不写死）。

## 👤 适用人群

- **适用人群**：
  - 完全没接触过 LangChain、想从零入门的新手
  - 想先建立宏观认知、再深入内部源码的学习者
  - 准备阅读 / 调试 / 贡献 LangChain 源码的开发者
- **你将获得**：从"会用"到"懂原理"的完整路径，以及一份可随时查阅的源码导航地图

## 🚀 如何阅读

直接用浏览器打开 **`index.html`** 即可（双击或拖入浏览器）。页面是自包含的，
导航链接使用相对路径，支持 `file://` 直接打开，也支持任意静态服务器：

```bash
# 可选：用任意静态服务器本地预览
python -m http.server 8000
# 然后访问 http://localhost:8000/
```

## 📚 教程结构（C 级扩充中 · M1-M3 已完成 · M4 审阅中 · 当前 36 课）

> M4 后当前站点有 36 个 HTML 课程页面，并保留兼容旧链接的文件名，同时继续扩展到约 45-55 课。第一到第四部分都是新版 C 级批次；其余页面仍按旧版/迁移中结构保留。

### 第一部分 · 全局地图（M1，新版 C 级）
1. `01-what-is-langchain.html` **LangChain 是什么** — 解决什么问题 · 核心心智模型
2. `02-monorepo.html` **项目与包结构** — `core` / `langchain` / `partners` 三层架构
3. `03-lifecycle.html` **一次调用的全链路** — 从你的代码到 LLM 的完整数据流
4. `04-source-reading-map.html` **源码阅读地图** — 新手读源码的入口与路线
5. `05-learning-path.html` **学习路径与实验方法** — 如何边读边跑边验证

### 第二部分 · 用户 API 基础（M2，新版 C 级）
6. `04-messages.html` **消息系统** — Human / AI / Tool / System 消息
7. `05-chat-models.html` **聊天模型** — `init_chat_model` · invoke / stream / batch
8. `06-tools.html` **工具 Tools** — `@tool` 装饰器 · 工具调用
9. `16-prompts.html` **提示词 Prompts** — `ChatPromptTemplate` · `MessagesPlaceholder`
10. `10-output-parsers.html` **输出解析器 Output Parsers** — 文本到结构化数据
11. `14-streaming-callbacks.html` **Streaming 与 Callbacks** — 流式输出与回调追踪

### 第三部分 · Runnable 与 LCEL（M3，当前 C 级）
12. `08-runnable.html` **Runnable 协议** — invoke / ainvoke / stream / batch · 统一运行接口
13. `09-runnable-compose.html` **LCEL 管道与 Sequence** — `|` · `RunnableSequence` · 输入输出契约
14. `12-runnable-parallel-branch.html` **并行、分支与映射** — `RunnableParallel` · `RunnableBranch`
15. `13-runnable-config-callbacks.html` **配置、回调与运行树** — `RunnableConfig` · tags / metadata / callbacks
16. `15-runnable-retry-fallback.html` **重试、Fallback 与健壮链** — `with_retry` · `with_fallbacks`

### 第四部分 · LangGraph 心智模型（M4，当前 C 级）
17. `24-langgraph-mental-model.html` **为什么需要 LangGraph** — LCEL 边界 · 有状态图 · Agent 循环
18. `28-langgraph-state-schema.html` **State 与 Schema** — `TypedDict` / Pydantic · `context_schema` · state keys
19. `29-langgraph-nodes-edges.html` **Node、Edge 与路由** — `add_node` · `add_edge` · 条件边 · START / END
20. `30-langgraph-reducers-channels.html` **Reducer 与 Channel** — `Annotated` reducer · `add_messages` · channel 语义
21. `31-langgraph-compile-runtime.html` **compile 与 Runtime** — `CompiledStateGraph` · runtime / context · Runnable 兼容

### 旧版 / 迁移中页面
22. `07-agents-intro.html` **Agent 入门** — `create_agent` · Agent 循环
23. `11-chat-internals.html` **聊天模型内部** — `BaseChatModel` 调用链
24. `12-tool-internals.html` **工具调用内部** — 函数 → JSON Schema → `tool_calls`
25. `13-agent-internals.html` **Agent 内部** — LangGraph 状态图 + middleware
26. `15-contributing.html` **读源码 / 调试 / 测试 / 贡献** — `uv` · 测试 · 调试 · 贡献规范
27. `17-rag.html` **RAG 检索增强** — `Document` → 切块 → `Embeddings` → `VectorStore` → `Retriever`
28. `18-custom-middleware.html` **写自己的中间件** — `AgentMiddleware` 钩子与 `dynamic_prompt`
29. `19-runtime-context.html` **运行时上下文与健壮性** — `context_schema` · `with_fallbacks` · `stream_mode`
30. `20-capstone.html` **端到端实战：拼一个客服 Agent** — prompts + RAG + 工具 + 中间件
31. `21-langchain-vs-autogen.html` **LangChain vs AutoGen** — 图/管道 vs 多 Agent 对话
32. `22-ai-stack.html` **AI 全栈坐标系** — Agent 编排 5 流派 · AI 全栈 7 层
33. `23-learning-map.html` **隔壁层学习地图** — L5 推理 · L6 向量检索
34. `25-langgraph-pregel-engine.html` **执行引擎：Pregel 与超步**
35. `26-langgraph-persistence-control.html` **持久化 · 中断 · 控制流**
36. `27-glossary.html` **术语表 · 概念索引** — 全书术语一句话查

## 🎨 每页包含

- 🌍 **宏观理解** — 大局观，为什么这样设计
- 🔬 **细节 / 代码对应** — 指向真实源码文件（如 `runnables/base.py`、`chat_models.py`）
- 🧩 **生活类比** — 用日常事物帮助理解抽象概念
- ✅ **关键要点** — 每课小结
- 💡 **设计亮点** — 该课最精妙的设计思想
- 顶部进度条 + 上一课 / 下一课导航

## 📁 项目结构

```
langchain-visual-guide/
├── index.html              ← 入口（目录页），从这里开始
├── print.html              ← 生成的单页打印 / PDF 源（可由 build_print.py 重建）
├── lessons/                ← 36 课图解页面（C 级扩充中，M1-M3 已完成，M4 审阅中）
│   ├── 01-what-is-langchain.html
│   ├── 02-monorepo.html
│   ├── 03-lifecycle.html
│   ├── 04-source-reading-map.html   新版 C 级：源码阅读地图
│   ├── 05-learning-path.html        新版 C 级：学习路径
│   ├── 04-messages.html             新版 C 级 M2：消息系统
│   ├── 05-chat-models.html          新版 C 级 M2：聊天模型
│   ├── 06-tools.html                新版 C 级 M2：工具 Tools
│   ├── 16-prompts.html              新版 C 级 M2：提示词 Prompts
│   ├── 10-output-parsers.html       新版 C 级 M2：输出解析器
│   ├── 14-streaming-callbacks.html  新版 C 级 M2：Streaming / Callbacks
│   ├── 08-runnable.html             新版 C 级 M3：Runnable 协议
│   ├── 09-runnable-compose.html     新版 C 级 M3：LCEL 管道与 Sequence
│   ├── 12-runnable-parallel-branch.html  新版 C 级 M3：并行、分支与映射
│   ├── 13-runnable-config-callbacks.html 新版 C 级 M3：配置、回调与运行树
│   ├── 15-runnable-retry-fallback.html   新版 C 级 M3：重试、Fallback 与健壮链
│   ├── 24-langgraph-mental-model.html    新版 C 级 M4：为什么需要 LangGraph
│   ├── 28-langgraph-state-schema.html     新版 C 级 M4：State 与 Schema
│   ├── 29-langgraph-nodes-edges.html      新版 C 级 M4：Node、Edge 与路由
│   ├── 30-langgraph-reducers-channels.html 新版 C 级 M4：Reducer 与 Channel
│   ├── 31-langgraph-compile-runtime.html  新版 C 级 M4：compile 与 Runtime
│   ├── …
│   └── 27-glossary.html
├── src/                    ← 无依赖的 Python 生成器（可重建全部 HTML / PDF）
│   ├── shell.py            共享外壳：CSS 设计系统、导航、index 页
│   ├── part01_overview.py  新版 Part 1（M0/M1 全局地图）
│   ├── part02_user_api.py  新版 Part 2（M2 用户 API 基础）
│   ├── part03_runnable_lcel.py  新版 Part 3（M3 Runnable 与 LCEL）
│   ├── part04_langgraph_model.py  新版 Part 4（M4 LangGraph 心智模型）
│   ├── part2.py … part7.py 旧版 / 迁移中课程内容
│   ├── registry.py         课程 → 内容 的统一映射
│   ├── build.py            站点构建（→ index.html + lessons/）
│   ├── build_print.py      PDF 构建（→ print.html，折叠全展开）
│   ├── check_links.py      内部链接检查
│   ├── check_html.py       HTML 结构与一致性检查
│   └── check_content_density.py  内容密度质量检查
├── .github/workflows/
│   ├── ci.yml              CI：站点 + print HTML 构建 / 链接 / HTML 结构 / 内容密度防回归检查
│   └── deploy.yml          CI：自动部署 Pages + 生成 PDF
├── README.md
└── LICENSE
```

## 🛠️ 重新生成

所有 HTML 由 `src/` 下的 Python 生成器产出，无第三方依赖（仅需 Python 3）：

```bash
cd src
python build.py          # 生成 index.html + lessons/（站点）
python build_print.py    # 生成 print.html（用于打 PDF，折叠全部展开）
```

页面之间用相对链接互联，整体可直接拷贝、部署到任意静态服务器或 GitHub Pages。

### 本地导出 PDF

`print.html` 把全部 36 课合成单页文档（折叠卡片全部展开、自动分页）。用任意无头浏览器打 PDF，例如：

```bash
chromium --headless=new --no-pdf-header-footer \
  --print-to-pdf=langchain-visual-guide.pdf \
  --virtual-time-budget=20000 "file://$PWD/print.html"
```

## 🚀 自动化：GitHub Pages + PDF（CI）

仓库内置 `.github/workflows/deploy.yml`，**推送即自动**：
1. 重新构建站点与 `print.html`；
2. 用无头 Chrome 渲染出 **PDF**（CI 已安装 CJK/emoji 字体，中文正常）；
3. 把 `index.html`、`lessons/`、`langchain-visual-guide.pdf` 部署到 **GitHub Pages**；
4. PDF 同时作为构建产物上传；打 `v*` **标签**时还会自动发布 Release 并附带 PDF。

另有 `.github/workflows/ci.yml`（每次 push / PR 触发）做**防回归**：① 重新运行 `build.py` 并校验提交的站点 HTML 与 `src/` **没有漂移**；② 运行 `build_print.py` 校验 `print.html` 可重新构建；③ 运行 `check_links.py` 确保**内部链接无死链**；④ 运行 `check_html.py` 与 `check_content_density.py` 检查 **HTML 结构 / 一致性** 和 **C 级内容密度**。

**首次启用（一次性）：**
1. 在 GitHub 新建仓库并推送：
   ```bash
   git remote add origin git@github.com:<你的用户名>/langchain-visual-guide.git
   git push -u origin master
   ```
2. 仓库 **Settings → Pages → Build and deployment → Source** 选 **GitHub Actions**。
3. 之后每次 `push` 到 `master` 会自动部署，站点地址形如
   `https://<你的用户名>.github.io/langchain-visual-guide/`，PDF 在
   `https://<你的用户名>.github.io/langchain-visual-guide/langchain-visual-guide.pdf`。
4. 发布带 PDF 的版本：`git tag v1.0 && git push --tags`。


## 📄 许可

本项目以 [MIT License](./LICENSE) 开源，可自由使用、修改与分发。

LangChain 为 LangChain, Inc. 的项目，相关名称与商标归其所有，详见其
[官方仓库](https://github.com/langchain-ai/langchain) 与文档。本教程为独立的第三方学习材料，与官方无隶属关系。
