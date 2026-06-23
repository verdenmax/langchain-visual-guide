# LangChain Visual Guide C 级成书化扩充设计

## 背景

当前 `langchain-visual-guide` 已有 27 课，定位是面向新手的中文图解教程，HTML 由 `src/` 下的零依赖 Python 生成器构建。和 `../llama-cpp-visual-guide/` 对比后，当前项目在内容厚度、图形密度、worked-example 追踪、源码级解释、练习体系上都明显偏薄。

量化观察：

- 当前项目：27 个 lesson，平均正文约 4.2k 字符/页，平均图/表/流程组件约 2.3 个/页。
- 对照项目：40 个 lesson，平均正文约 28.5k 字符/页，平均图/表/流程组件约 6 个/页；同时包含更系统的源码解释、手绘图、worked-example trace、自测与 print 版本。

本设计目标是把当前教程升级为中文为主的“成书级深挖”版本，而不是只给现有页面补几段文字。

## 已确认决策

- 扩充强度：选择 C · 成书级深挖。
- 语言策略：保持中文为主，不做完整中英双语；优先把内容深度做到位。
- 实施节奏：按 Part 分批做，每批完成后审查和验收。
- 源码核验：强源码核验，每个核心机制都对应真实源码入口、调用链和简化伪代码。
- 页面/组件：允许统一升级页面模板和图形组件，新增图形、源码、trace、lab 等组件并重构页面结构。
- 课程结构：允许重新拆分目录，把现有 27 课扩成更多课。
- 目标规模：45-55 课，明显成书化但保持可控。
- 总体策略：采用“主线重编版”，按学习路径重新组织目录，而不是简单扩写旧目录。

## 课程架构

重编后采用约 9 个 Part、45-55 课的主线结构：

| Part | 主题 | 目标 |
| --- | --- | --- |
| Part 1 | 全局地图 | 建立 LangChain、LangGraph、生态边界、一次调用全景、源码阅读路线 |
| Part 2 | 用户 API 基础 | messages、chat models、tools、prompts、output parsers、streaming |
| Part 3 | Runnable 与 LCEL | Runnable 协议、invoke/stream/batch、sequence/parallel/branch、config/callbacks |
| Part 4 | LangGraph 心智模型 | state、node、edge、channel、reducer、compile、runtime |
| Part 5 | LangGraph 执行引擎 | Pregel、superstep、checkpoint、interrupt、Send/Command、time travel |
| Part 6 | Agent 内部 | create_agent、model/tool loop、middleware、runtime context、错误恢复 |
| Part 7 | RAG 与记忆 | document、splitter、embedding、vector store、retriever、rerank、memory |
| Part 8 | 实战与工程化 | 客服 Agent、可观测性、测试、调试、贡献、版本迁移 |
| Part 9 | 生态对比与速查 | AutoGen、LlamaIndex、CrewAI、MCP、A2A、AI stack、glossary |

每个 Part 的内部节奏：

1. 地图课：说明本 Part 的问题域、概念关系和源码入口。
2. 机制课：讲核心 API 或内部机制。
3. 源码课：追真实源码入口、调用链和关键对象。
4. worked-example 课：用一个具体输入逐步追踪状态变化。
5. 工程/边界课：总结常见坑、测试方法和设计取舍。

不是每个 Part 都必须完整包含这五类课，但每个 Part 至少要有地图、机制、源码和练习/边界内容。

## 单课模板

每课默认包含以下模块，并允许按主题裁剪：

1. **本课地图**
   - 一张图说明本课在全书中的位置。
   - 标出上游依赖、下游会用到的概念、对应源码区域。

2. **直觉解释**
   - 先用类比、小例子、问题场景解释概念。
   - 避免一上来堆类名、函数名和源码路径。

3. **运行轨迹图**
   - 展示一次输入如何经过对象、函数、状态、消息、配置。
   - 对 API 课使用调用链图；对 LangGraph/Agent 课使用状态流图；对 RAG 课使用数据流图。

4. **源码入口地图**
   - 列真实文件、类/函数、调用方向。
   - 以“文件 + 符号名”为主，不写死易随上游变化的行号。
   - 必须区分 LangChain、LangGraph、langchain-core、community/partners 等来源。

5. **简化源码/伪代码**
   - 从真实源码抽象为 20-60 行可读版本。
   - 只保留教学所需路径，明确说明省略了哪些错误处理、兼容层或 provider 细节。

6. **worked example trace**
   - 给一个具体输入，逐步追踪消息、state、config、tool call、retriever result 等变化。
   - 使用 trace table 或编号流程图。

7. **设计取舍**
   - 说明为什么这样设计。
   - 比较替代方案，例如简单函数调用 vs Runnable、链式调用 vs 图执行、普通 while loop vs Pregel/superstep。

8. **常见误解与边界情况**
   - 每课至少 3-5 个，适合解释新手容易混淆的点。
   - 例如 message 和 prompt 的区别、tool schema 和 tool result 的区别、state mutation 与 reducer 的区别。

9. **自测与练习**
   - 概念题：检查是否理解核心抽象。
   - 读源码题：指出要打开的文件/符号。
   - 小实验：给出最小代码或伪代码任务。

## 页面与组件设计

保留现有卡片化、进度条、上一课/下一课导航风格，但新增更适合成书级内容的组件。

计划新增的共享组件：

- `lesson_map()`：本课位置图和概念依赖图。
- `source_map()`：源码入口地图，展示文件、符号、职责和调用方向。
- `call_graph()`：调用链图，用于 Runnable、ChatModel、Tool、Agent 等。
- `state_flow()`：状态流图，用于 LangGraph、Agent、RAG 和 memory。
- `trace_table()`：worked example 逐步追踪表。
- `code_walkthrough()`：简化源码/伪代码块，附省略说明。
- `pitfall_grid()`：常见误解、错误用法、边界情况。
- `lab_card()`：小实验或读源码练习。
- `version_note()`：版本锚点、上游变动风险、API 兼容提示。
- `svg_diagram()`：可复用 inline SVG 图容器，用于更复杂的结构图。

这些组件应在 `src/shell.py` 中实现，内容模块只传结构化参数或 HTML 片段，避免每课复制大量布局代码。

## 生成器与目录结构

继续保持当前项目的零依赖 Python 生成方式：

- `src/build.py` 生成 `index.html` 和 `lessons/*.html`。
- `src/build_print.py` 生成 print/PDF 所需页面。
- 生成后的 HTML 继续提交，确保 GitHub Pages 可直接部署。

建议重构为更清晰的内容模块：

```text
src/
  shell.py                       # CSS、布局、共享组件
  registry.py                    # 唯一目录顺序来源
  quizzes.py / glossary.py       # 题库和术语
  part01_overview.py
  part02_user_api.py
  part03_runnable_lcel.py
  part04_langgraph_model.py
  part05_langgraph_engine.py
  part06_agent_internals.py
  part07_rag_memory.py
  part08_engineering.py
  part09_ecosystem_reference.py
  build.py
  build_print.py
  check_html.py
  check_links.py
  check_content_density.py       # 新增：内容密度/组件覆盖检查
```

迁移时不需要一次性删除旧 `part1.py`...`part7.py`。可以按批次引入新模块，完成一个 Part 后再从 `registry.py` 切换对应页面。

## 分批实施策略

按 Part 分批，每批遵循同一流程：

1. 为该 Part 写详细目录和每课目标。
2. 核验 LangChain/LangGraph 当前源码入口和调用链。
3. 实现或扩展所需共享组件。
4. 编写该 Part 的内容模块。
5. 更新 `registry.py`、导航、index、print 输出。
6. 运行构建与检查。
7. 进行双重审查：spec-compliance subagent + code-quality subagent。
8. 批次验收通过后再进入下一 Part。

建议先做 Part 1 作为模板批次，因为它会确定全书的视觉语言、组件粒度、目录样式和源码引用规范。

## 验收标准

通用标准：

- 每课都有明确学习目标和本课地图。
- 每个核心机制都有源码入口地图。
- 每课至少 3 个核心图/trace/table 组件；特殊 glossary/索引页可豁免。
- 每课至少 1 个 worked example trace；纯索引页可豁免。
- 每课至少 1 组自测/练习。
- 核心解释必须包含“为什么这么设计”和“常见误解/边界情况”。
- 源码引用使用文件 + 符号名，不依赖易漂移行号。
- 页面内部链接、上一课/下一课、目录页、print 版本都必须同步。

构建与检查：

- `python3 build.py`
- `python3 build_print.py`
- `python3 check_html.py`
- `python3 check_links.py`
- `python3 check_content_density.py`（新增）

生成检查应确保：

- 提交的 HTML 与 `src/` 生成结果无漂移。
- 每课满足最低组件覆盖要求。
- 内部链接全部可解析。
- print/PDF 页面包含新目录和新内容。

## 风险与应对

| 风险 | 应对 |
| --- | --- |
| 范围过大导致一次 PR 难以完成 | 按 Part 分批，每批独立验收 |
| 源码上游变化导致内容过期 | 版本锚点 + 文件/符号引用 + version note |
| 页面变长后可读性下降 | 使用地图、折叠、trace table、lab card 分层阅读 |
| 组件过多导致内容模块难维护 | 组件集中在 `shell.py`，内容模块只调用语义组件 |
| 旧 lesson 与新 lesson 混杂期间导航不一致 | `registry.py` 作为唯一目录来源，逐批切换 |
| PDF/print 漂移 | 每批同时更新 `build_print.py` 并加入检查 |

## 非目标

- 不做完整中英双语正文。
- 不切换到第三方静态站点生成器。
- 不把所有上游源码复制进仓库。
- 不在第一批就一次性完成 45-55 课。
- 不追求逐行源码注释，而是追核心机制和调用链。

## 完成定义

整体 C 级扩充完成时，项目应具备：

- 约 45-55 课的重新编排目录。
- 中文为主、成书级深度的页面内容。
- 统一的图解组件系统。
- 每个核心机制都有源码入口、简化伪代码、运行轨迹和练习。
- 网页、print/PDF、README、CI 检查全部同步。
- 每个 Part 都经过构建验证和双重审查。
