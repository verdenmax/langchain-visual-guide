# LangChain 图解教程 · 从零理解整个项目

一套面向**完全新手**的可视化（HTML 图解）教程，带你从零开始理解
[LangChain](https://github.com/langchain-ai/langchain) 这个项目——既有**宏观全景**，也有**细节源码**，
每一课都配有**真实代码文件对应**。

> 本教程在 Copilot CLI 中借助 superpowers 的 *brainstorming visual companion* 生成，
> 内容对照 LangChain 仓库真实源码核实。

## 🚀 如何阅读

直接用浏览器打开 **`index.html`** 即可（双击或拖入浏览器）。页面是自包含的，
导航链接使用相对路径，支持 `file://` 直接打开，也支持任意静态服务器：

```bash
# 可选：用任意静态服务器本地预览
python -m http.server 8000
# 然后访问 http://localhost:8000/
```

## 📚 教程结构（4 部分 · 14 课）

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
9. **Runnable 如何组合** — Sequence / Parallel 组合
10. **聊天模型内部** — `BaseChatModel` 调用链
11. **工具调用内部** — 函数 → JSON Schema → `tool_calls`
12. **Agent 内部** — LangGraph 状态图 + middleware
13. **Streaming 与 Callbacks** — 流式输出与回调追踪

### 第四部分 · 进阶实战
14. **读源码 / 调试 / 测试 / 贡献** — `uv` · 测试 · 调试 · 贡献规范

## 🎨 每页包含

- 🌍 **宏观理解** — 大局观，为什么这样设计
- 🔬 **细节 / 代码对应** — 指向真实源码文件（如 `runnables/base.py`、`chat_models.py`）
- 🧩 **生活类比** — 用日常事物帮助理解抽象概念
- ✅ **关键要点** — 每课小结
- 顶部进度条 + 上一课 / 下一课导航

## 🛠️ 重新生成

所有 HTML 由 `src/` 下的 Python 生成器产出，无第三方依赖（仅需 Python 3）：

```bash
cd src
python build.py
```

- `src/shell.py` — 共享外壳：CSS 设计系统、导航、index 页
- `src/part1.py … part4.py` — 各部分课程内容
- `src/build.py` — 构建脚本，输出到项目根目录

## 📄 许可

教程内容供学习使用。LangChain 为 LangChain, Inc. 的项目，详见其
[官方仓库](https://github.com/langchain-ai/langchain) 与文档。
