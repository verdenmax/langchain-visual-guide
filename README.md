# LangChain 图解教程 · 从零理解整个项目

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lessons](https://img.shields.io/badge/lessons-19-blue.svg)
![Parts](https://img.shields.io/badge/parts-5-9cf.svg)
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

## 📚 教程结构（5 部分 · 19 课）

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

## 🎨 每页包含

- 🌍 **宏观理解** — 大局观，为什么这样设计
- 🔬 **细节 / 代码对应** — 指向真实源码文件（如 `runnables/base.py`、`chat_models.py`）
- 🧩 **生活类比** — 用日常事物帮助理解抽象概念
- ✅ **关键要点** — 每课小结
- 顶部进度条 + 上一课 / 下一课导航

## 📁 项目结构

```
langchain-visual-guide/
├── index.html              ← 入口（目录页），从这里开始
├── lessons/                ← 19 课图解页面
│   ├── 01-what-is-langchain.html
│   ├── 02-monorepo.html
│   └── …  19-runtime-context.html
├── src/                    ← 无依赖的 Python 生成器（可重建全部 HTML）
│   ├── shell.py            共享外壳：CSS 设计系统、导航、index 页
│   ├── part1.py … part4.py 各部分课程内容
│   └── build.py            构建脚本
├── README.md
└── LICENSE
```

## 🛠️ 重新生成

所有 HTML 由 `src/` 下的 Python 生成器产出，无第三方依赖（仅需 Python 3）：

```bash
cd src
python build.py
```

构建脚本会把 `index.html` 写到项目根目录，19 课写入 `lessons/`。
页面之间用相对链接互联，因此整体可直接拷贝、部署到任意静态服务器或 GitHub Pages。

## 📄 许可

本项目以 [MIT License](./LICENSE) 开源，可自由使用、修改与分发。

LangChain 为 LangChain, Inc. 的项目，相关名称与商标归其所有，详见其
[官方仓库](https://github.com/langchain-ai/langchain) 与文档。本教程为独立的第三方学习材料，与官方无隶属关系。
