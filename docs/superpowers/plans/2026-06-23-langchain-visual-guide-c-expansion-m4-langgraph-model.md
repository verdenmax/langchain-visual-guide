# LangChain Visual Guide C Expansion M4 LangGraph Mental Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the LangGraph mental-model layer as C-level lessons covering why graphs are needed, state/schema, nodes/edges/routing, reducers/channels, and compile/runtime.

**Architecture:** M4 creates `src/part04_langgraph_model.py`, reuses `24-langgraph-mental-model.html`, adds four new LangGraph model pages, places the block after M3, extends raw-body density checks, replaces matching quizzes, and updates README/roadmap. Pregel/checkpoint/interrupt pages remain legacy for M5.

**Tech Stack:** Python 3 standard library; existing static HTML generator; shared C-level helpers in `src/shell.py`; validation via `build.py`, `build_print.py`, `check_html.py`, `check_links.py`, and `check_content_density.py`.

---

## M4 page set

- `24-langgraph-mental-model.html` — 为什么需要 LangGraph
- `28-langgraph-state-schema.html` — State 与 Schema
- `29-langgraph-nodes-edges.html` — Node、Edge 与路由
- `30-langgraph-reducers-channels.html` — Reducer 与 Channel
- `31-langgraph-compile-runtime.html` — compile 与 Runtime

---

### Task 1: Register M4 page set

**Files:**
- Create: `src/part04_langgraph_model.py`
- Modify: `src/shell.py`
- Modify: `src/registry.py`
- Modify: `src/check_content_density.py`

- [ ] **Step 1: Create module skeleton**

```python
"""C-level Part 4: LangGraph mental model."""

import shell

LESSON_17_GRAPH_WHY = r"""<p class="lead">M4 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_18_STATE_SCHEMA = r"""<p class="lead">M4 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_19_NODES_EDGES = r"""<p class="lead">M4 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_20_REDUCERS_CHANNELS = r"""<p class="lead">M4 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_21_COMPILE_RUNTIME = r"""<p class="lead">M4 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
```

- [ ] **Step 2: Add M4 pages after the M3 block in `shell.PAGES`**

```python
    ("24-langgraph-mental-model.html", "为什么需要 LangGraph", "第四部分 · LangGraph 心智模型"),
    ("28-langgraph-state-schema.html", "State 与 Schema", "第四部分 · LangGraph 心智模型"),
    ("29-langgraph-nodes-edges.html", "Node、Edge 与路由", "第四部分 · LangGraph 心智模型"),
    ("30-langgraph-reducers-channels.html", "Reducer 与 Channel", "第四部分 · LangGraph 心智模型"),
    ("31-langgraph-compile-runtime.html", "compile 与 Runtime", "第四部分 · LangGraph 心智模型"),
```

Move legacy `25-langgraph-pregel-engine.html` and `26-langgraph-persistence-control.html` to a non-colliding transitional label, `迁移中 · LangGraph 引擎旧版`.

- [ ] **Step 3: Update `SUBTITLES`**

```python
    "24-langgraph-mental-model.html": "为什么 LCEL 不够 · 有状态图 · Pregel 之前的心智模型",
    "28-langgraph-state-schema.html": "TypedDict/Pydantic state · context_schema · state keys",
    "29-langgraph-nodes-edges.html": "add_node · add_edge · conditional edges · START/END",
    "30-langgraph-reducers-channels.html": "Annotated reducer · add_messages · LastValue/Topic/Aggregate",
    "31-langgraph-compile-runtime.html": "compile() · CompiledStateGraph · runtime/context · Runnable",
```

- [ ] **Step 4: Update `registry.py`**

```python
import part04_langgraph_model
```

Map:

```python
    "24-langgraph-mental-model.html": part04_langgraph_model.LESSON_17_GRAPH_WHY,
    "28-langgraph-state-schema.html": part04_langgraph_model.LESSON_18_STATE_SCHEMA,
    "29-langgraph-nodes-edges.html": part04_langgraph_model.LESSON_19_NODES_EDGES,
    "30-langgraph-reducers-channels.html": part04_langgraph_model.LESSON_20_REDUCERS_CHANNELS,
    "31-langgraph-compile-runtime.html": part04_langgraph_model.LESSON_21_COMPILE_RUNTIME,
```

Keep `25-langgraph-pregel-engine.html` and `26-langgraph-persistence-control.html` mapped to legacy `part7`.

- [ ] **Step 5: Extend density gates**

Add all five M4 pages to `C_LEVEL_PAGES` with `{"min_cjk": 4500, "min_visual": 5}`.

- [ ] **Step 6: Verify expected temporary failure and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1/src
python3 build.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
```

Expected: build/html/link pass; density fails only for five temporary M4 pages.

Commit:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1
git add src/shell.py src/registry.py src/check_content_density.py src/part04_langgraph_model.py index.html lessons
git commit -m "Register M4 LangGraph mental model lesson set" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Write five C-level M4 lessons and quizzes

**Files:**
- Modify: `src/part04_langgraph_model.py`
- Modify: `src/quizzes.py`
- Generated: M4 lesson HTML files

Every lesson must include `lead`, `lesson_map`, `source_map`, `state_flow` or `call_graph`, `trace_table`, `code_walkthrough`, `pitfall_grid`, `lab_card`, `version_note`, `card analogy`, and `本课要点`. Each raw body must have at least 4500 CJK chars.

- [ ] **Step 1: Write `LESSON_17_GRAPH_WHY`**

Must cover:
- Why LCEL chains are not enough for cyclic/stateful/branching workflows.
- Source rows:
  - `langgraph/graph/state.py :: StateGraph`
  - `langgraph/graph/message.py :: add_messages`
  - `langgraph/pregel/main.py :: Pregel`
  - `libs/langchain_v1/langchain/agents/factory.py :: create_agent`
- Explain graph vs chain, shared state, node returns partial state, compile result as Runnable.
- Trace: chatbot state with messages, model node, conditional tool edge, tool node, loop back.
- Pitfalls: graph is not visual UI, state is not global mutable dict, cycles need termination, LangChain Agent is built on LangGraph.

- [ ] **Step 2: Write `LESSON_18_STATE_SCHEMA`**

Must cover:
- State schema as graph contract: keys, value types, reducers.
- Source rows:
  - `langgraph/graph/state.py :: StateGraph.__init__`
  - `langgraph/graph/state.py :: _get_channels`
  - `langgraph/graph/state.py :: _get_channel`
  - `langgraph/runtime.py :: Runtime`
  - `langgraph/graph/message.py :: add_messages`
- Explain `TypedDict`, Pydantic/dataclass style schemas, `context_schema`, input/output/private state, partial updates.
- Trace: node receives state, returns `{"messages": [AIMessage("ok")]}`, reducer merges.
- Pitfalls: mutating state in place, returning whole state unnecessarily, confusing context with state, missing reducer for list accumulation.

- [ ] **Step 3: Write `LESSON_19_NODES_EDGES`**

Must cover:
- Nodes as state -> partial state functions, edges as routing.
- Source rows:
  - `langgraph/graph/state.py :: StateGraph.add_node`
  - `langgraph/graph/state.py :: StateGraph.add_edge`
  - `langgraph/graph/state.py :: StateGraph.add_conditional_edges`
  - `langgraph/constants.py :: START`
  - `langgraph/constants.py :: END`
- Explain normal edges, conditional edges, routing functions, START/END, node naming, tool loop route.
- Trace: `START -> model -> route_tools -> tools or END -> model`.
- Pitfalls: route returns wrong node name, node returns non-dict update, edge creates unbounded loop, side effects in route function.

- [ ] **Step 4: Write `LESSON_20_REDUCERS_CHANNELS`**

Must cover:
- Reducers and channels as merge semantics below state keys.
- Source rows:
  - `langgraph/graph/message.py :: add_messages`
  - `langgraph/channels/last_value.py :: LastValue`
  - `langgraph/channels/topic.py :: Topic`
  - `langgraph/channels/binop.py :: BinaryOperatorAggregate`
  - `langgraph/graph/state.py :: _get_channel`
- Explain default overwrite, `Annotated[list[AnyMessage], reducer]`, message ID replacement/append, fan-in updates, why reducers matter for parallel branches.
- Trace: two nodes update same key; LastValue conflict vs reducer merge.
- Pitfalls: expecting list append without reducer, duplicate message IDs, non-commutative reducers, reducers doing I/O.

- [ ] **Step 5: Write `LESSON_21_COMPILE_RUNTIME`**

Must cover:
- `compile()` turns graph builder into a Runnable runtime.
- Source rows:
  - `langgraph/graph/state.py :: StateGraph.compile`
  - `langgraph/graph/state.py :: CompiledStateGraph`
  - `langgraph/pregel/main.py :: Pregel`
  - `langgraph/runtime.py :: Runtime`
  - `langgraph/checkpoint/base/__init__.py :: BaseCheckpointSaver`
- Explain validation, channel creation, node wrapping, runtime context, checkpointer hook, result can invoke/stream/batch.
- Trace: build graph -> compile -> invoke -> run nodes -> produce state.
- Pitfalls: thinking compile executes graph, changing builder after compile, missing `thread_id` when using checkpointer, runtime context vs state.

- [ ] **Step 6: Replace quizzes for five M4 pages**

Each page must have 3 MCQ + 2 open prompts:

| Page | MCQ themes | Open prompt themes |
| --- | --- | --- |
| `24-langgraph-mental-model.html` | graph vs chain; partial state; Agent on LangGraph | design graph from chain; identify loop termination |
| `28-langgraph-state-schema.html` | state vs context; reducer need; partial update | choose state keys; debug in-place mutation |
| `29-langgraph-nodes-edges.html` | node contract; conditional edge return; START/END | design route function; find infinite loop |
| `30-langgraph-reducers-channels.html` | LastValue vs reducer; add_messages; parallel fan-in | select reducer; reason about message IDs |
| `31-langgraph-compile-runtime.html` | compile vs invoke; runtime context; checkpointer | compile/run trace; choose checkpoint config |

Balance correct answer indexes across 0/1/2/3.

- [ ] **Step 7: Validate and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1/src
python3 build.py
python3 build_print.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
python3 - <<'PY'
import re, registry
for fname in ["24-langgraph-mental-model.html","28-langgraph-state-schema.html","29-langgraph-nodes-edges.html","30-langgraph-reducers-channels.html","31-langgraph-compile-runtime.html"]:
    print(fname, len(re.findall(r"[\u4e00-\u9fff]", registry.CONTENT[fname])))
PY
```

Expected: all checks pass; density passes for 21 C-level pages; each count >=4500.

Commit:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1
git add src/part04_langgraph_model.py src/quizzes.py index.html lessons
git commit -m "Rewrite Part 4 LangGraph mental model lessons to C-level" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Update README and roadmap for M4

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md`

- [ ] **Step 1: Update roadmap**

Set:
- M3 status to `Done`.
- M4 status to `In review`.
- M4 detailed plan to `` `2026-06-23-langchain-visual-guide-c-expansion-m4-langgraph-model.md` ``.

- [ ] **Step 2: Update README**

State that 第一到第四部分 are C-level batches. Add `part04_langgraph_model.py` to the project tree. Mention current site has 36 lesson pages after M4. Mark the five M4 pages as current C-level pages.

- [ ] **Step 3: Validate and commit**

Run full checks. Commit:

```bash
git add README.md docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md
git commit -m "Document M4 LangGraph mental model expansion" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Final handoff

After Task 3 passes review, report:

- M4 commits created.
- Five M4 C-level pages migrated.
- Total C-level pages checked by density checker.
- Next plan to write: M5 “LangGraph 执行引擎”.
