# LangChain Visual Guide C Expansion M8 Engineering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the engineering/practice layer as C-level lessons covering local development, source debugging, testing/fakes, CI/release workflow, and an end-to-end customer-service Agent.

**Architecture:** M8 creates `src/part08_engineering.py`, reuses `15-contributing.html` and `20-capstone.html`, adds two new engineering pages, places the block after M7, extends raw-body density checks, replaces matching quizzes, and updates README/roadmap. M9 will finish ecosystem comparison and glossary polish.

**Tech Stack:** Python 3 standard library; existing static HTML generator; shared C-level helpers in `src/shell.py`; validation via `build.py`, `build_print.py`, `check_html.py`, `check_links.py`, and `check_content_density.py`.

---

## M8 page set

- `15-contributing.html` — 本地开发、源码调试与贡献
- `40-testing-debugging.html` — 测试、Fake 模型与回归
- `41-observability-ci.html` — 观测、CI、PDF 与发布
- `20-capstone.html` — 端到端客服 Agent 工程化

---

### Task 1: Register M8 page set

**Files:**
- Create: `src/part08_engineering.py`
- Modify: `src/shell.py`
- Modify: `src/registry.py`
- Modify: `src/check_content_density.py`

- [ ] **Step 1: Create skeleton**

```python
"""C-level Part 8: engineering, testing, and capstone."""

import shell

LESSON_37_LOCAL_DEV = r"""<p class="lead">M8 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_38_TESTING_DEBUGGING = r"""<p class="lead">M8 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_39_OBSERVABILITY_CI = r"""<p class="lead">M8 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_40_CAPSTONE = r"""<p class="lead">M8 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
```

- [ ] **Step 2: Add M8 pages after M7 block in `shell.PAGES`**

```python
    ("15-contributing.html", "本地开发、源码调试与贡献", "第八部分 · 工程化与实战"),
    ("40-testing-debugging.html", "测试、Fake 模型与回归", "第八部分 · 工程化与实战"),
    ("41-observability-ci.html", "观测、CI、PDF 与发布", "第八部分 · 工程化与实战"),
    ("20-capstone.html", "端到端客服 Agent 工程化", "第八部分 · 工程化与实战"),
```

- [ ] **Step 3: Update `SUBTITLES`**

```python
    "15-contributing.html": "uv/monorepo · editable install · source breakpoints · contribution loop",
    "40-testing-debugging.html": "fake models · deterministic tools · trace assertions · regression cases",
    "41-observability-ci.html": "callbacks · LangSmith/run tree · build checks · PDF/deploy workflow",
    "20-capstone.html": "prompts + tools + RAG + middleware + context + tests",
```

- [ ] **Step 4: Update registry**

Import `part08_engineering` and map the four pages to its constants. Keep non-M8 legacy mappings unchanged.

- [ ] **Step 5: Extend density gates**

Add all four M8 pages to `C_LEVEL_PAGES` with `{"min_cjk": 4500, "min_visual": 5}`.

- [ ] **Step 6: Verify expected temporary failure and commit**

Run build/html/link/density. Density should fail only for four M8 temporary pages. Commit:

```bash
git add src/shell.py src/registry.py src/check_content_density.py src/part08_engineering.py index.html lessons
git commit -m "Register M8 engineering lesson set" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Write four C-level M8 lessons and quizzes

**Files:**
- Modify: `src/part08_engineering.py`
- Modify: `src/quizzes.py`
- Generated: M8 lesson HTML files

Every lesson must include `lead`, `lesson_map`, `source_map`, `state_flow` or `call_graph`, `trace_table`, `code_walkthrough`, `pitfall_grid`, `lab_card`, `version_note`, `card analogy`, and `本课要点`. Each raw body must have at least 4500 CJK chars.

- [ ] **Step 1: Write `LESSON_37_LOCAL_DEV`**

Cover local development, source debugging, repo/package layout, editable install, and contribution loop. Source rows:
- `langchain/libs/langchain_v1/pyproject.toml :: [project] / [dependency-groups] / [tool.uv.sources]`
- `langchain/libs/core/pyproject.toml :: langchain-core package`
- `langgraph/libs/langgraph/pyproject.toml :: langgraph package`
- `src/build.py :: build`
- `src/check_html.py :: check_lesson / check_stale`
- `.github/workflows/ci.yml :: verify job`

Path correction: current LangChain master has no root `pyproject.toml`; package metadata is in package-level pyprojects. LangGraph is in the separate `langchain-ai/langgraph` repository, not `langchain/libs/langgraph`.

Trace: choose API -> find package -> create editable env -> run focused test -> open PR.

- [ ] **Step 2: Write `LESSON_38_TESTING_DEBUGGING`**

Cover fake models, deterministic tools, trace assertions, regression cases. Source rows:
- `langchain/libs/core/langchain_core/language_models/fake_chat_models.py :: GenericFakeChatModel`
- `langchain/libs/core/langchain_core/messages/ai.py :: AIMessage`
- `langchain/libs/core/langchain_core/runnables/base.py :: Runnable`
- `langgraph/libs/checkpoint/langgraph/checkpoint/memory/__init__.py :: InMemorySaver`
- `langchain/libs/langchain_v1/langchain/agents/factory.py :: create_agent`

Trace: one deterministic Agent test with fake model/tool/checkpointer.

- [ ] **Step 3: Write `LESSON_39_OBSERVABILITY_CI`**

Cover callbacks/run tree, LangSmith-style observability, local CI checks, generated HTML/PDF sync. Source rows:
- `langchain/libs/core/langchain_core/callbacks/base.py :: BaseCallbackHandler`
- `langchain/libs/core/langchain_core/tracers/base.py :: BaseTracer`
- `src/check_html.py :: main`
- `src/check_links.py :: check`
- `src/check_content_density.py :: main`
- `.github/workflows/ci.yml :: verify job`

Trace: code change -> build -> checks -> generated diff gate -> deploy/PDF.

- [ ] **Step 4: Write `LESSON_40_CAPSTONE`**

Cover an end-to-end customer-service Agent assembled from previous parts: prompt, tools, RAG, middleware, runtime context, structured response, tests. Source rows:
- `langchain/libs/langchain_v1/langchain/agents/factory.py :: create_agent`
- `langchain/libs/core/langchain_core/prompts/chat.py :: ChatPromptTemplate`
- `langchain/libs/core/langchain_core/tools/convert.py :: tool`
- `langchain/libs/core/langchain_core/retrievers.py :: BaseRetriever`
- `langchain/libs/langchain_v1/langchain/agents/middleware/types.py :: AgentMiddleware`

Trace: user issue -> prompt/context -> retrieve order docs -> tool action -> middleware guard -> structured response -> regression test.

- [ ] **Step 5: Replace quizzes**

Each page has 3 MCQ + 2 open prompts:

| Page | MCQ themes | Open prompt themes |
| --- | --- | --- |
| `15-contributing.html` | package boundary; focused test; source anchor | debug a failing API; plan a small PR |
| `40-testing-debugging.html` | fake model; deterministic tools; regression trace | design fake test; assert message state |
| `41-observability-ci.html` | callback vs middleware; generated drift; density gate | design CI gate; trace one run |
| `20-capstone.html` | component assembly; structured response; guard middleware | design customer agent; identify failure mode |

Balance answer indexes.

- [ ] **Step 6: Validate and commit**

Run full checks and raw CJK count. Expected: density passes for 40 C-level pages. Commit:

```bash
git add src/part08_engineering.py src/quizzes.py index.html lessons
git commit -m "Rewrite Part 8 engineering lessons to C-level" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Update README and roadmap for M8

Set M7 status to `Done`, M8 to `In review`, link this plan. Update README to say 第一到第八部分 are C-level, add `part08_engineering.py`, mention current site has 46 lesson pages after M8, and list four M8 current pages. Run full checks and commit:

```bash
git add README.md docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md
git commit -m "Document M8 engineering expansion" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Final handoff

After Task 3 passes review, report:

- M8 commits created.
- Four M8 C-level pages migrated.
- Total C-level pages checked by density checker.
- Next plan to write: M9 “生态对比与速查”.
