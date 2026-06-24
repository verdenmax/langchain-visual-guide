# LangChain Visual Guide C Expansion M6 Agent Internals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the Agent layer as C-level lessons covering the model/tool loop, `create_agent`, middleware hooks, runtime context, and agent control/error boundaries.

**Architecture:** M6 creates `src/part06_agent_internals.py`, reuses legacy Agent-related filenames, adds one new control/error page, places the block after M5, extends raw-body density checks, replaces matching quizzes, and updates README/roadmap. Later RAG/memory/engineering/ecosystem pages remain transitional.

**Tech Stack:** Python 3 standard library; existing static HTML generator; shared C-level helpers in `src/shell.py`; validation via `build.py`, `build_print.py`, `check_html.py`, `check_links.py`, and `check_content_density.py`.

---

## M6 page set

- `07-agents-intro.html` — Agent 循环心智模型
- `13-agent-internals.html` — create_agent 构图内部
- `18-custom-middleware.html` — Middleware 生命周期
- `19-runtime-context.html` — Runtime Context 与结构化响应
- `35-agent-control-errors.html` — 控制边界、递归限制与错误恢复

---

### Task 1: Register M6 page set

**Files:**
- Create: `src/part06_agent_internals.py`
- Modify: `src/shell.py`
- Modify: `src/registry.py`
- Modify: `src/check_content_density.py`

- [ ] **Step 1: Create skeleton**

```python
"""C-level Part 6: Agent internals."""

import shell

LESSON_27_AGENT_LOOP = r"""<p class="lead">M6 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_28_CREATE_AGENT = r"""<p class="lead">M6 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_29_MIDDLEWARE = r"""<p class="lead">M6 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_30_RUNTIME_CONTEXT = r"""<p class="lead">M6 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_31_CONTROL_ERRORS = r"""<p class="lead">M6 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
```

- [ ] **Step 2: Add M6 pages after M5 block in `shell.PAGES`**

```python
    ("07-agents-intro.html", "Agent 循环心智模型", "第六部分 · Agent 内部"),
    ("13-agent-internals.html", "create_agent 构图内部", "第六部分 · Agent 内部"),
    ("18-custom-middleware.html", "Middleware 生命周期", "第六部分 · Agent 内部"),
    ("19-runtime-context.html", "Runtime Context 与结构化响应", "第六部分 · Agent 内部"),
    ("35-agent-control-errors.html", "控制边界、递归限制与错误恢复", "第六部分 · Agent 内部"),
```

Move any remaining legacy Agent/RAG group labels to non-colliding migration labels.

- [ ] **Step 3: Update `SUBTITLES`**

```python
    "07-agents-intro.html": "model node · tools node · tool_calls · loop termination",
    "13-agent-internals.html": "create_agent · StateGraph · tools_condition · ToolNode",
    "18-custom-middleware.html": "AgentMiddleware · before/after/wrap hooks · dynamic prompt",
    "19-runtime-context.html": "context_schema · Runtime · response_format · structured response",
    "35-agent-control-errors.html": "recursion_limit · tool errors · fallback/retry · safe control",
```

- [ ] **Step 4: Update registry**

Import `part06_agent_internals` and map:

```python
    "07-agents-intro.html": part06_agent_internals.LESSON_27_AGENT_LOOP,
    "13-agent-internals.html": part06_agent_internals.LESSON_28_CREATE_AGENT,
    "18-custom-middleware.html": part06_agent_internals.LESSON_29_MIDDLEWARE,
    "19-runtime-context.html": part06_agent_internals.LESSON_30_RUNTIME_CONTEXT,
    "35-agent-control-errors.html": part06_agent_internals.LESSON_31_CONTROL_ERRORS,
```

- [ ] **Step 5: Extend density gates**

Add the five M6 pages to `C_LEVEL_PAGES` with `{"min_cjk": 4500, "min_visual": 5}`.

- [ ] **Step 6: Verify expected temporary failure and commit**

Run build/html/link/density. Density should fail only for five M6 temporary pages. Commit:

```bash
git add src/shell.py src/registry.py src/check_content_density.py src/part06_agent_internals.py index.html lessons
git commit -m "Register M6 Agent internals lesson set" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Write five C-level M6 lessons and quizzes

**Files:**
- Modify: `src/part06_agent_internals.py`
- Modify: `src/quizzes.py`
- Generated: M6 lesson HTML files

Every lesson must include `lead`, `lesson_map`, `source_map`, `state_flow` or `call_graph`, `trace_table`, `code_walkthrough`, `pitfall_grid`, `lab_card`, `version_note`, `card analogy`, and `本课要点`. Each raw body must have at least 4500 CJK chars.

- [ ] **Step 1: Write `LESSON_27_AGENT_LOOP`**

Cover model/tool loop. Source rows:
- `libs/langchain_v1/langchain/agents/factory.py :: create_agent`
- `libs/langgraph/langgraph/prebuilt/tool_node.py :: ToolNode`
- `libs/langgraph/langgraph/prebuilt/tool_node.py :: tools_condition`
- `libs/core/langchain_core/messages/ai.py :: AIMessage.tool_calls`
- `libs/core/langchain_core/messages/tool.py :: ToolMessage`

Trace user question -> model node -> tool_calls -> tools node -> ToolMessage -> model final.

- [ ] **Step 2: Write `LESSON_28_CREATE_AGENT`**

Cover `create_agent` building StateGraph. Source rows:
- `libs/langchain_v1/langchain/agents/factory.py :: create_agent`
- `libs/langchain_v1/langchain/agents/factory.py :: _AgentBuilder`
- `libs/langgraph/langgraph/graph/state.py :: StateGraph`
- `libs/langgraph/langgraph/prebuilt/tool_node.py :: ToolNode`
- `libs/langgraph/langgraph/graph/message.py :: add_messages`

Trace parameters into model/tools/middleware/response_format/checkpointer graph pieces.

- [ ] **Step 3: Write `LESSON_29_MIDDLEWARE`**

Cover `AgentMiddleware` hooks and wrapping. Source rows:
- `libs/langchain_v1/langchain/agents/middleware/types.py :: AgentMiddleware`
- `libs/langchain_v1/langchain/agents/factory.py :: _chain_model_call_handlers`
- `libs/langchain_v1/langchain/agents/factory.py :: _chain_tool_call_wrappers`
- `libs/langchain_v1/langchain/agents/middleware/model_call_limit.py :: ModelCallLimitMiddleware`
- `libs/langchain_v1/langchain/agents/middleware/human_in_the_loop.py :: HumanInTheLoopMiddleware`

Trace before_model, wrap_model_call, after_model, wrap_tool_call, after_agent.

- [ ] **Step 4: Write `LESSON_30_RUNTIME_CONTEXT`**

Cover `context_schema`, Runtime, response_format/structured response. Source rows:
- `libs/langchain_v1/langchain/agents/factory.py :: create_agent`
- `libs/langgraph/langgraph/runtime.py :: Runtime`
- `libs/langchain_v1/langchain/tools/tool_node.py :: ToolRuntime`
- `libs/core/langchain_core/language_models/chat_models.py :: with_structured_output`
- `libs/langgraph/langgraph/graph/state.py :: StateGraph`

Trace `context={"user_id": ...}` into prompt/tool node and structured final response.

- [ ] **Step 5: Write `LESSON_31_CONTROL_ERRORS`**

Cover recursion limits, tool/model errors, fallback/retry, safe side effects. Source rows:
- `libs/langgraph/langgraph/errors.py :: GraphRecursionError`
- `libs/langgraph/langgraph/pregel/main.py :: Pregel.stream`
- `libs/core/langchain_core/runnables/retry.py :: RunnableRetry`
- `libs/core/langchain_core/runnables/fallbacks.py :: RunnableWithFallbacks`
- `libs/langgraph/langgraph/prebuilt/tool_node.py :: ToolNode`

Trace runaway tool loop stopped by recursion_limit; tool error surfaced vs converted to ToolMessage.

- [ ] **Step 6: Replace quizzes**

Each page gets 3 MCQ + 2 open prompts:

| Page | MCQ themes | Open prompt themes |
| --- | --- | --- |
| `07-agents-intro.html` | loop phases; tool_calls vs ToolMessage; termination | trace loop; decide tool boundary |
| `13-agent-internals.html` | create_agent graph pieces; add_messages; ToolNode | map params to graph; inspect graph path |
| `18-custom-middleware.html` | before/after/wrap; middleware order; HITL middleware | design guard middleware; debug wrapper order |
| `19-runtime-context.html` | context vs state; structured response; ToolRuntime | design context schema; avoid leaking secrets |
| `35-agent-control-errors.html` | recursion_limit; retry/fallback; tool error policy | design safe loop; classify errors |

Balance answer indexes.

- [ ] **Step 7: Validate and commit**

Run full checks and raw CJK count. Expected: density passes for 31 C-level pages. Commit:

```bash
git add src/part06_agent_internals.py src/quizzes.py index.html lessons
git commit -m "Rewrite Part 6 Agent internals lessons to C-level" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Update README and roadmap for M6

Set M5 status to `Done`, M6 to `In review`, link this plan. Update README to say 第一到第六部分 are C-level, add `part06_agent_internals.py`, mention current site has 40 lesson pages after M6, and list the five M6 current pages. Run full checks and commit:

```bash
git add README.md docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md
git commit -m "Document M6 Agent internals expansion" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Final handoff

After Task 3 passes review, report:

- M6 commits created.
- Five M6 C-level pages migrated.
- Total C-level pages checked by density checker.
- Next plan to write: M7 “RAG 与记忆”.
