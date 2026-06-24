# LangChain Visual Guide C Expansion M5 LangGraph Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the LangGraph execution-engine layer as C-level lessons covering Pregel supersteps, channels/tasks, checkpoints, interrupts/Command, and time-travel debugging.

**Architecture:** M5 creates `src/part05_langgraph_engine.py`, reuses legacy `25-langgraph-pregel-engine.html` and `26-langgraph-persistence-control.html`, adds three new execution-engine pages, places the block after M4, extends raw-body density checks, replaces matching quizzes, and updates README/roadmap. Later Agent/RAG/engineering pages remain in transitional legacy groups.

**Tech Stack:** Python 3 standard library; existing static HTML generator; shared C-level helpers in `src/shell.py`; validation via `build.py`, `build_print.py`, `check_html.py`, `check_links.py`, and `check_content_density.py`.

---

## M5 page set

- `25-langgraph-pregel-engine.html` — Pregel 与超步
- `32-langgraph-tasks-channels.html` — Tasks、Channels 与调度
- `26-langgraph-persistence-control.html` — Checkpoint 与持久化
- `33-langgraph-interrupt-command.html` — interrupt、Command 与人在回路
- `34-langgraph-time-travel-debug.html` — 时间旅行、回放与调试

---

### Task 1: Register M5 page set

**Files:**
- Create: `src/part05_langgraph_engine.py`
- Modify: `src/shell.py`
- Modify: `src/registry.py`
- Modify: `src/check_content_density.py`

- [ ] **Step 1: Create module skeleton**

```python
"""C-level Part 5: LangGraph execution engine."""

import shell

LESSON_22_PREGEL = r"""<p class="lead">M5 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_23_TASKS_CHANNELS = r"""<p class="lead">M5 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_24_CHECKPOINTS = r"""<p class="lead">M5 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_25_INTERRUPT_COMMAND = r"""<p class="lead">M5 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_26_TIME_TRAVEL = r"""<p class="lead">M5 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
```

- [ ] **Step 2: Add M5 pages after the M4 block in `shell.PAGES`**

```python
    ("25-langgraph-pregel-engine.html", "Pregel 与超步", "第五部分 · LangGraph 执行引擎"),
    ("32-langgraph-tasks-channels.html", "Tasks、Channels 与调度", "第五部分 · LangGraph 执行引擎"),
    ("26-langgraph-persistence-control.html", "Checkpoint 与持久化", "第五部分 · LangGraph 执行引擎"),
    ("33-langgraph-interrupt-command.html", "interrupt、Command 与人在回路", "第五部分 · LangGraph 执行引擎"),
    ("34-langgraph-time-travel-debug.html", "时间旅行、回放与调试", "第五部分 · LangGraph 执行引擎"),
```

- [ ] **Step 3: Update `SUBTITLES`**

```python
    "25-langgraph-pregel-engine.html": "Pregel · superstep · Plan/Execution/Update",
    "32-langgraph-tasks-channels.html": "PregelTask · channels · writes · fan-in/fan-out",
    "26-langgraph-persistence-control.html": "Checkpoint · checkpointer · thread_id · resume",
    "33-langgraph-interrupt-command.html": "interrupt · Command · human-in-the-loop · goto/update",
    "34-langgraph-time-travel-debug.html": "StateSnapshot · get_state_history · replay · debug workflow",
```

- [ ] **Step 4: Update registry**

Import `part05_langgraph_engine` and map:

```python
    "25-langgraph-pregel-engine.html": part05_langgraph_engine.LESSON_22_PREGEL,
    "32-langgraph-tasks-channels.html": part05_langgraph_engine.LESSON_23_TASKS_CHANNELS,
    "26-langgraph-persistence-control.html": part05_langgraph_engine.LESSON_24_CHECKPOINTS,
    "33-langgraph-interrupt-command.html": part05_langgraph_engine.LESSON_25_INTERRUPT_COMMAND,
    "34-langgraph-time-travel-debug.html": part05_langgraph_engine.LESSON_26_TIME_TRAVEL,
```

- [ ] **Step 5: Extend density gates**

Add all five M5 pages to `C_LEVEL_PAGES` with `{"min_cjk": 4500, "min_visual": 5}`.

- [ ] **Step 6: Verify expected temporary failure and commit**

Run build/html/link/density. Density should fail only for five M5 temporary pages. Commit:

```bash
git add src/shell.py src/registry.py src/check_content_density.py src/part05_langgraph_engine.py index.html lessons
git commit -m "Register M5 LangGraph engine lesson set" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Write five C-level M5 lessons and quizzes

**Files:**
- Modify: `src/part05_langgraph_engine.py`
- Modify: `src/quizzes.py`
- Generated: M5 lesson HTML files

Every lesson must include `lead`, `lesson_map`, `source_map`, `state_flow` or `call_graph`, `trace_table`, `code_walkthrough`, `pitfall_grid`, `lab_card`, `version_note`, `card analogy`, and `本课要点`. Each raw body must have at least 4500 CJK chars.

- [ ] **Step 1: Write `LESSON_22_PREGEL`**

Cover Pregel/BSP supersteps and Plan/Execution/Update. Source rows:
- `langgraph/pregel/main.py :: Pregel`
- `langgraph/pregel/algo.py :: prepare_next_tasks`
- `langgraph/pregel/algo.py :: apply_writes`
- `langgraph/pregel/_runner.py :: PregelRunner`
- `langgraph/pregel/debug.py :: print_step_*`

Trace one graph step: subscribed channels select tasks, tasks run, writes are buffered, update phase applies writes.

- [ ] **Step 2: Write `LESSON_23_TASKS_CHANNELS`**

Cover `PregelTask`, channels, writes, fan-in/fan-out, and how reducers/channel updates bridge graph state and execution. Source rows:
- `langgraph/types.py :: PregelTask`
- `langgraph/channels/base.py :: BaseChannel`
- `langgraph/pregel/algo.py :: local_read`
- `langgraph/pregel/write.py :: ChannelWrite`
- `langgraph/pregel/read.py :: PregelNode`

Trace two parallel tasks writing to different/same channels.

- [ ] **Step 3: Write `LESSON_24_CHECKPOINTS`**

Cover checkpoint structure, checkpointer, `thread_id`, checkpoint namespace, resume. Source rows:
- `langgraph/checkpoint/base/__init__.py :: Checkpoint`
- `langgraph/checkpoint/base/__init__.py :: BaseCheckpointSaver`
- `langgraph/checkpoint/memory/__init__.py :: InMemorySaver`
- `langgraph/pregel/main.py :: Pregel.get_state`
- `langgraph/pregel/main.py :: Pregel.update_state`

Trace invoke with `configurable.thread_id`, checkpoint write, resume from next call.

- [ ] **Step 4: Write `LESSON_25_INTERRUPT_COMMAND`**

Cover `interrupt`, `Command`, human-in-the-loop, `goto`, update/resume. Source rows:
- `langgraph/types.py :: interrupt`
- `langgraph/types.py :: Command`
- `langgraph/errors.py :: GraphInterrupt`
- `langgraph/pregel/main.py :: Pregel.stream`
- `langgraph/graph/state.py :: CompiledStateGraph`

Trace approval workflow: node interrupts, caller returns `Command(resume={"approved": True, "comment": "ok"})`, graph continues.

- [ ] **Step 5: Write `LESSON_26_TIME_TRAVEL`**

Cover `StateSnapshot`, history, replay, debugging, fork from checkpoint. Source rows:
- `langgraph/types.py :: StateSnapshot`
- `langgraph/pregel/main.py :: Pregel.get_state_history`
- `langgraph/pregel/main.py :: Pregel.bulk_update_state`
- `langgraph/checkpoint/base/__init__.py :: CheckpointMetadata`
- `langgraph/pregel/debug.py :: map_debug_tasks`

Trace bad answer investigation: inspect history, pick checkpoint, fork/replay with changed input.

- [ ] **Step 6: Replace quizzes**

Each page has 3 MCQ + 2 open prompts:

| Page | MCQ themes | Open prompt themes |
| --- | --- | --- |
| `25-langgraph-pregel-engine.html` | superstep phases; buffered writes; task selection | trace one superstep; identify why updates are delayed |
| `32-langgraph-tasks-channels.html` | task vs node; channel write; fan-in | design channel writes; debug conflicting updates |
| `26-langgraph-persistence-control.html` | checkpoint/thread_id; resume; update_state | choose checkpoint config; debug lost conversation state |
| `33-langgraph-interrupt-command.html` | interrupt vs exception; Command resume/update/goto; HITL | design approval flow; reason about resume payload |
| `34-langgraph-time-travel-debug.html` | StateSnapshot; history; replay/fork | debug bad step; choose replay checkpoint |

Balance answer indexes.

- [ ] **Step 7: Validate and commit**

Run full checks and raw CJK count. Expected: density passes for 26 C-level pages. Commit:

```bash
git add src/part05_langgraph_engine.py src/quizzes.py index.html lessons
git commit -m "Rewrite Part 5 LangGraph engine lessons to C-level" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Update README and roadmap for M5

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md`

Set M4 status to `Done`, M5 status to `In review`, and M5 detailed plan to this file. Update README to say 第一到第五部分 are C-level, add `part05_langgraph_engine.py`, mention current site has 39 lesson pages after M5, and list the five M5 current C-level pages. Run full checks and commit:

```bash
git add README.md docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md
git commit -m "Document M5 LangGraph engine expansion" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Final handoff

After Task 3 passes review, report:

- M5 commits created.
- Five M5 C-level pages migrated.
- Total C-level pages checked by density checker.
- Next plan to write: M6 “Agent 内部”.
