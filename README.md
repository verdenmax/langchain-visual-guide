# LangChain 图解教程 · 从零理解整个项目

[![📖 在线阅读](https://img.shields.io/badge/%F0%9F%93%96%20%E5%9C%A8%E7%BA%BF%E9%98%85%E8%AF%BB-Read%20Online-1a7f64?style=for-the-badge)](https://verdenmax.github.io/langchain-visual-guide/)
[![📄 下载 PDF](https://img.shields.io/badge/%F0%9F%93%84%20%E4%B8%8B%E8%BD%BD%20PDF-Download-b4690e?style=for-the-badge)](https://github.com/verdenmax/langchain-visual-guide/releases/latest/download/langchain-visual-guide.pdf)

> 🌐 **在线阅读**：<https://verdenmax.github.io/langchain-visual-guide/>　·　📄 **下载 PDF（全 46 课）**：[langchain-visual-guide.pdf](https://github.com/verdenmax/langchain-visual-guide/releases/latest/download/langchain-visual-guide.pdf)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lessons](https://img.shields.io/badge/lessons-expanding_to_45--55-blue.svg)
![Parts](https://img.shields.io/badge/parts-11-9cf.svg)
![Built with](https://img.shields.io/badge/built%20with-Python%203-3776AB.svg?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)
![Language](https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87-orange.svg)

> ✅ **C 级成书化版本**：本教程已从旧版 27 课重编为 **9 个 Part、46 课**的中文成书级深挖版本，强调更多图、worked-example trace、真实源码入口、简化伪代码和自测练习。九个 Part 全部为 C 级：全局地图、用户 API 基础、Runnable 与 LCEL、LangGraph 心智模型、LangGraph 执行引擎、Agent 内部、RAG 与记忆、工程化与实战、生态与速查。

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

## 📚 教程结构（C 级成书版 · 9 个 Part · 46 课）

> 当前站点有 46 个 HTML 课程页面（9 个 Part 全部为新版 C 级批次），并保留兼容旧链接的文件名；后续可在 45-55 课目标内继续按需加深。

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

### 第四部分 · LangGraph 心智模型（M4，新版 C 级）
17. `24-langgraph-mental-model.html` **为什么需要 LangGraph** — LCEL 边界 · 有状态图 · Agent 循环
18. `28-langgraph-state-schema.html` **State 与 Schema** — `TypedDict` / Pydantic · `context_schema` · state keys
19. `29-langgraph-nodes-edges.html` **Node、Edge 与路由** — `add_node` · `add_edge` · 条件边 · START / END
20. `30-langgraph-reducers-channels.html` **Reducer 与 Channel** — `Annotated` reducer · `add_messages` · channel 语义
21. `31-langgraph-compile-runtime.html` **compile 与 Runtime** — `CompiledStateGraph` · runtime / context · Runnable 兼容

### 第五部分 · LangGraph 执行引擎（M5，当前 C 级）
22. `25-langgraph-pregel-engine.html` **Pregel 与超步** — Plan / Execution / Update · 本步写入下步可见
23. `32-langgraph-tasks-channels.html` **Tasks、Channels 与调度** — `PregelTask` · channel 写入 · fan-in / fan-out
24. `26-langgraph-persistence-control.html` **Checkpoint 与持久化** — `thread_id` · checkpointer · resume / update_state
25. `33-langgraph-interrupt-command.html` **interrupt、Command 与人在回路** — 暂停 · 审批 · resume / goto / update
26. `34-langgraph-time-travel-debug.html` **时间旅行、回放与调试** — `StateSnapshot` · history · replay / fork

### 第六部分 · Agent 内部（M6，当前 C 级）
27. `07-agents-intro.html` **Agent 循环心智模型** — model node · tools node · tool_calls · loop termination
28. `13-agent-internals.html` **create_agent 构图内部** — StateGraph · 条件边 · ToolNode
29. `18-custom-middleware.html` **Middleware 生命周期** — `AgentMiddleware` · before/after/wrap hooks · dynamic prompt
30. `19-runtime-context.html` **Runtime Context 与结构化响应** — `context_schema` · runtime context · structured response
31. `35-agent-control-errors.html` **控制边界、递归限制与错误恢复** — `recursion_limit` · tool errors · fallback/retry

### 第七部分 · RAG 与记忆（M7，当前 C 级）
32. `17-rag.html` **RAG 全链路** — 问题 → Retriever → Document → context → 带引用回答
33. `36-documents-splitters.html` **Document、Loader 与 Splitter** — `Document` · metadata · 切块策略
34. `37-embeddings-vectorstores.html` **Embeddings 与 VectorStore** — 向量化 · 索引 · 相似度搜索
35. `38-retrievers-rerankers.html` **Retriever、压缩与 Rerank** — 召回 / 精排 / Contextual Compression
36. `39-memory-conversation-state.html` **记忆、会话历史与状态** — chat history · summary memory · LangGraph state

### 第八部分 · 工程化与实战（M8，当前 C 级）
37. `15-contributing.html` **本地开发、源码调试与贡献** — editable 环境 · 聚焦测试 · 小 PR 循环
38. `40-testing-debugging.html` **测试、Fake 模型与回归** — Fake 模型 · 确定性工具 · trace 断言
39. `41-observability-ci.html` **观测、CI、PDF 与发布** — callbacks · run tree · 构建检查 · Pages/PDF
40. `20-capstone.html` **端到端客服 Agent 工程化** — prompts + RAG + 工具 + 中间件 + 可回归发布

### 第九部分 · 生态与速查（M9，新版 C 级）
41. `11-chat-internals.html` **ChatModel Provider 内部** — `BaseChatModel` · provider adapter · payload/response 归一化
42. `12-tool-internals.html` **Tool Schema 与执行内部** — `BaseTool` · `args_schema` · `convert_to_openai_tool` · `ToolMessage`
43. `21-langchain-vs-autogen.html` **LangChain、LangGraph 与多 Agent 生态** — 图/管道 vs 多 Agent 对话
44. `22-ai-stack.html` **AI 全栈、MCP 与 A2A** — Agent 编排流派 · AI 全栈分层 · MCP/A2A
45. `23-learning-map.html` **后续学习地图** — L5 推理 · L6 向量检索 · 进阶路线
46. `27-glossary.html` **术语表与源码索引** — 全书术语一句话查 + 源码定位

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
├── lessons/                ← 46 课图解页面（C 级成书版 · 9 个 Part）
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
│   ├── 25-langgraph-pregel-engine.html    新版 C 级 M5：Pregel 与超步
│   ├── 32-langgraph-tasks-channels.html   新版 C 级 M5：Tasks、Channels 与调度
│   ├── 26-langgraph-persistence-control.html 新版 C 级 M5：Checkpoint 与持久化
│   ├── 33-langgraph-interrupt-command.html 新版 C 级 M5：interrupt、Command 与人在回路
│   ├── 34-langgraph-time-travel-debug.html 新版 C 级 M5：时间旅行、回放与调试
│   ├── 07-agents-intro.html          新版 C 级 M6：Agent 循环心智模型
│   ├── 13-agent-internals.html       新版 C 级 M6：create_agent 构图内部
│   ├── 18-custom-middleware.html     新版 C 级 M6：Middleware 生命周期
│   ├── 19-runtime-context.html       新版 C 级 M6：Runtime Context 与结构化响应
│   ├── 35-agent-control-errors.html  新版 C 级 M6：控制边界、递归限制与错误恢复
│   ├── 17-rag.html                   新版 C 级 M7：RAG 全链路
│   ├── 36-documents-splitters.html   新版 C 级 M7：Document、Loader 与 Splitter
│   ├── 37-embeddings-vectorstores.html 新版 C 级 M7：Embeddings 与 VectorStore
│   ├── 38-retrievers-rerankers.html  新版 C 级 M7：Retriever、压缩与 Rerank
│   ├── 39-memory-conversation-state.html 新版 C 级 M7：记忆、会话历史与状态
│   ├── 15-contributing.html           新版 C 级 M8：本地开发、源码调试与贡献
│   ├── 40-testing-debugging.html      新版 C 级 M8：测试、Fake 模型与回归
│   ├── 41-observability-ci.html       新版 C 级 M8：观测、CI、PDF 与发布
│   ├── 20-capstone.html               新版 C 级 M8：端到端客服 Agent 工程化
│   ├── …
│   └── 27-glossary.html
├── src/                    ← 无依赖的 Python 生成器（可重建全部 HTML / PDF）
│   ├── shell.py            共享外壳：CSS 设计系统、导航、index 页
│   ├── part01_overview.py  新版 Part 1（M0/M1 全局地图）
│   ├── part02_user_api.py  新版 Part 2（M2 用户 API 基础）
│   ├── part03_runnable_lcel.py  新版 Part 3（M3 Runnable 与 LCEL）
│   ├── part04_langgraph_model.py  新版 Part 4（M4 LangGraph 心智模型）
│   ├── part05_langgraph_engine.py  新版 Part 5（M5 LangGraph 执行引擎）
│   ├── part06_agent_internals.py  新版 Part 6（M6 Agent 内部）
│   ├── part07_rag_memory.py  新版 Part 7（M7 RAG 与记忆）
│   ├── part08_engineering.py  新版 Part 8（M8 工程化与实战）
│   ├── part09_ecosystem_reference.py  新版 Part 9（M9 生态与速查）
│   ├── part1.py … part7.py 旧版（保留兼容，registry 已不再引用）
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

`print.html` 把全部 46 课合成单页文档（折叠卡片全部展开、自动分页）。用任意无头浏览器打 PDF，例如：

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
