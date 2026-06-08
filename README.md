# LangChain 图解教程 · 从零理解整个项目

[![📖 在线阅读](https://img.shields.io/badge/%F0%9F%93%96%20%E5%9C%A8%E7%BA%BF%E9%98%85%E8%AF%BB-Read%20Online-1a7f64?style=for-the-badge)](https://verdenmax.github.io/langchain-visual-guide/)
[![📄 下载 PDF](https://img.shields.io/badge/%F0%9F%93%84%20%E4%B8%8B%E8%BD%BD%20PDF-Download-b4690e?style=for-the-badge)](https://github.com/verdenmax/langchain-visual-guide/releases/latest/download/langchain-visual-guide.pdf)

> 🌐 **在线阅读**：<https://verdenmax.github.io/langchain-visual-guide/>　·　📄 **下载 PDF（全 26 课）**：[langchain-visual-guide.pdf](https://github.com/verdenmax/langchain-visual-guide/releases/latest/download/langchain-visual-guide.pdf)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lessons](https://img.shields.io/badge/lessons-26-blue.svg)
![Parts](https://img.shields.io/badge/parts-7-9cf.svg)
![Built with](https://img.shields.io/badge/built%20with-Python%203-3776AB.svg?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)
![Language](https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87-orange.svg)

一套面向**完全新手**的可视化（HTML 图解）教程，带你从零开始理解
[LangChain](https://github.com/langchain-ai/langchain) 这个项目——既有**宏观全景**，也有**细节源码**，
每一课都配有**真实代码文件对应**。

> 本教程在 Copilot CLI 中借助 superpowers 的 *brainstorming visual companion* 生成，
> 内容对照 LangChain 仓库真实源码核实。

## 👤 作者与适用人群

- **作者**：kws
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

## 📚 教程结构（7 部分 · 26 课）

### 第一部分 · 宏观全景
1. **LangChain 是什么** — 解决什么问题 · 核心心智模型
2. **Monorepo 全景** — `core` / `langchain` / `partners` 三层架构
3. **一次调用的生命周期** — 从你的代码到 LLM 的完整数据流

### 第二部分 · 用户视角
4. **消息系统** — Human / AI / Tool / System 消息
5. **聊天模型** — `init_chat_model` · invoke / stream / batch
6. **工具 Tools** — `@tool` 装饰器 · 工具调用
7. **Agent 入门** — `create_agent` · Agent 循环

### 第三部分 · 内部源码
8. **Runnable 万物之基** — invoke/stream/batch · LCEL 管道 `|`
9. **Runnable 如何组合** — Sequence / Parallel / Branch 组合
10. **输出解析器 Output Parsers** — `StrOutputParser` · `JsonOutputParser` · 闭环
11. **聊天模型内部** — `BaseChatModel` 调用链
12. **工具调用内部** — 函数 → JSON Schema → `tool_calls`
13. **Agent 内部** — LangGraph 状态图 + middleware
14. **Streaming 与 Callbacks** — 流式输出与回调追踪

### 第四部分 · 进阶实战
15. **读源码 / 调试 / 测试 / 贡献** — `uv` · 测试 · 调试 · 贡献规范

### 第五部分 · 自己动手做 Agent
16. **提示词 Prompts** — `ChatPromptTemplate` · `MessagesPlaceholder` · few-shot
17. **RAG 检索增强** — `Document` → 切块 → `Embeddings` → `VectorStore` → `Retriever`
18. **写自己的中间件** — `AgentMiddleware` 钩子（before/after/wrap）· `dynamic_prompt`
19. **运行时上下文与健壮性** — `context_schema` · `with_fallbacks` · `stream_mode`
20. **端到端实战：拼一个客服 Agent** — prompts + RAG + 工具 + 中间件 + 上下文 全拼起来

### 第六部分 · 番外篇
21. **横向对比：LangChain vs AutoGen** — 两种范式对照：图/管道 vs 多 Agent 对话
22. **全栈坐标系：从 LangChain 缩放到整个生态** — Agent 编排 5 流派 · AI 全栈 7 层 · 你在哪
23. **隔壁层学习地图：L5 推理 · L6 向量检索** — vLLM/llama.cpp/Ollama · hnswlib/pgvector/Qdrant

### 第七部分 · 深入 LangGraph
24. **深入 LangGraph：图 / 状态 / 节点 / 边** — 为什么 LCEL 不够 · State/Node/Edge/compile · 和 LangChain 的关系
25. **执行引擎：Pregel 与超步** — Pregel/BSP · Plan→Execution→Update · channels 与 reducer
26. **持久化 · 中断 · 控制流** — Checkpoint/StateSnapshot · 时间旅行 · interrupt · Send/Command

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
├── lessons/                ← 26 课图解页面
│   ├── 01-what-is-langchain.html
│   ├── 02-monorepo.html
│   └── …  26-langgraph-persistence-control.html
├── src/                    ← 无依赖的 Python 生成器（可重建全部 HTML / PDF）
│   ├── shell.py            共享外壳：CSS 设计系统、导航、index 页
│   ├── part1.py … part6.py 各部分课程内容
│   ├── registry.py         课程 → 内容 的统一映射
│   ├── build.py            站点构建（→ index.html + lessons/）
│   └── build_print.py      PDF 构建（→ print.html，折叠全展开）
├── .github/workflows/
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

`print.html` 把全部 26 课合成单页文档（折叠卡片全部展开、自动分页）。用任意无头浏览器打 PDF，例如：

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

另有 `.github/workflows/ci.yml`（每次 push / PR 触发）做**防回归**：① 重新运行 `build.py` 并校验提交的 HTML 与 `src/` **没有漂移**；② 运行 `check_links.py` 确保**内部链接无死链**。

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
