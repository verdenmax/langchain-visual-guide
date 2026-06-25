# LangChain Visual Guide C Expansion M3 Runnable and LCEL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the Runnable/LCEL core as C-level lessons covering the Runnable protocol, LCEL sequence composition, parallel/branch/map composition, config/callback propagation, and retry/fallback robustness.

**Architecture:** M3 creates `src/part03_runnable_lcel.py`, maps two existing Runnable filenames plus three new filenames into a contiguous Part 3 block, extends the raw-body density checker, replaces matching quizzes, and regenerates HTML. Legacy source-internals pages remain in the guide under transitional sections until later milestones migrate them.

**Tech Stack:** Python 3 standard library; existing static HTML generator; shared C-level helpers in `src/shell.py`; validation via `build.py`, `build_print.py`, `check_html.py`, `check_links.py`, and `check_content_density.py`.

---

## File structure

- Create `src/part03_runnable_lcel.py` with five constants:
  - `LESSON_12_RUNNABLE_PROTOCOL`
  - `LESSON_13_LCEL_SEQUENCE`
  - `LESSON_14_PARALLEL_BRANCH`
  - `LESSON_15_CONFIG_CALLBACKS`
  - `LESSON_16_RETRY_FALLBACK`
- Modify `src/shell.py` to place five M3 pages after the M2 block and update `SUBTITLES`.
- Modify `src/registry.py` to import `part03_runnable_lcel` and map M3 filenames to it.
- Modify `src/check_content_density.py` to include the five M3 pages.
- Modify `src/quizzes.py` to add/replace quizzes for the five M3 pages.
- Generated: `index.html`, changed `lessons/*.html`, ignored `print.html`.

---

### Task 1: Register the M3 page set and density gates

**Files:**
- Create: `src/part03_runnable_lcel.py`
- Modify: `src/shell.py`
- Modify: `src/registry.py`
- Modify: `src/check_content_density.py`

- [ ] **Step 1: Create module skeleton**

Create `src/part03_runnable_lcel.py` with temporary strings:

```python
"""C-level Part 3: Runnable and LCEL internals."""

import shell

LESSON_12_RUNNABLE_PROTOCOL = r"""<p class="lead">M3 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_13_LCEL_SEQUENCE = r"""<p class="lead">M3 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_14_PARALLEL_BRANCH = r"""<p class="lead">M3 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_15_CONFIG_CALLBACKS = r"""<p class="lead">M3 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_16_RETRY_FALLBACK = r"""<p class="lead">M3 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
```

- [ ] **Step 2: Add M3 pages after the M2 block in `shell.PAGES`**

Use these entries and keep legacy pages after them:

```python
    ("08-runnable.html", "Runnable 协议", "第三部分 · Runnable 与 LCEL"),
    ("09-runnable-compose.html", "LCEL 管道与 Sequence", "第三部分 · Runnable 与 LCEL"),
    ("12-runnable-parallel-branch.html", "并行、分支与映射", "第三部分 · Runnable 与 LCEL"),
    ("13-runnable-config-callbacks.html", "配置、回调与运行树", "第三部分 · Runnable 与 LCEL"),
    ("15-runnable-retry-fallback.html", "重试、Fallback 与健壮链", "第三部分 · Runnable 与 LCEL"),
```

Legacy `07-agents-intro.html`, `11-chat-internals.html`, `12-tool-internals.html`, `13-agent-internals.html`, `15-contributing.html`, and later pages remain after the M3 block under transitional or existing labels.

- [ ] **Step 3: Update `SUBTITLES`**

```python
    "08-runnable.html": "RunnableSerializable · invoke/ainvoke/stream/batch · 标准协议",
    "09-runnable-compose.html": "LCEL `|` · RunnableSequence · 输入输出契约",
    "12-runnable-parallel-branch.html": "RunnableParallel · RunnableBranch · assign/map/passthrough",
    "13-runnable-config-callbacks.html": "RunnableConfig · ensure_config · callbacks/tags/metadata",
    "15-runnable-retry-fallback.html": "with_retry · with_fallbacks · RunnableWithFallbacks",
```

- [ ] **Step 4: Update `registry.py`**

Add:

```python
import part03_runnable_lcel
```

Map:

```python
    "08-runnable.html": part03_runnable_lcel.LESSON_12_RUNNABLE_PROTOCOL,
    "09-runnable-compose.html": part03_runnable_lcel.LESSON_13_LCEL_SEQUENCE,
    "12-runnable-parallel-branch.html": part03_runnable_lcel.LESSON_14_PARALLEL_BRANCH,
    "13-runnable-config-callbacks.html": part03_runnable_lcel.LESSON_15_CONFIG_CALLBACKS,
    "15-runnable-retry-fallback.html": part03_runnable_lcel.LESSON_16_RETRY_FALLBACK,
```

Keep non-M3 legacy mappings unchanged.

- [ ] **Step 5: Extend density gates**

Add the five M3 pages to `C_LEVEL_PAGES` with `{"min_cjk": 4500, "min_visual": 5}`.

- [ ] **Step 6: Verify expected temporary failure and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1/src
python3 build.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
```

Expected: build/html/link checks pass; density fails only for five temporary M3 pages.

Commit:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1
git add src/shell.py src/registry.py src/check_content_density.py src/part03_runnable_lcel.py index.html lessons
git commit -m "Register M3 Runnable and LCEL lesson set" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Write five C-level M3 lessons and quizzes

**Files:**
- Modify: `src/part03_runnable_lcel.py`
- Modify: `src/quizzes.py`
- Generated: M3 lesson HTML files

Each lesson must include `lead`, `lesson_map`, `source_map`, `call_graph` or `state_flow`, `trace_table`, `code_walkthrough`, `pitfall_grid`, `lab_card`, `version_note`, `card analogy`, and `本课要点`. Each raw body must have at least 4500 CJK chars.

- [ ] **Step 1: Write `LESSON_12_RUNNABLE_PROTOCOL` for `08-runnable.html`**

Must cover:
- Runnable as LangChain’s standard execution protocol.
- Source rows:
  - `libs/core/langchain_core/runnables/base.py :: Runnable`
  - `libs/core/langchain_core/runnables/base.py :: RunnableSerializable`
  - `libs/core/langchain_core/runnables/config.py :: RunnableConfig`
  - `libs/core/langchain_core/runnables/base.py :: RunnableBinding`
  - `libs/core/langchain_core/runnables/base.py :: RunnableEach`
- Explain `invoke`, `ainvoke`, `stream`, `astream`, `batch`, `abatch`, schema-ish input/output contracts, serialization, config propagation.
- Trace: one prompt/model/parser chain calling `invoke`.
- Pitfalls: Runnable is not just `|`, async is not magic parallelism, streaming chunks are not final objects, config is not business state.

- [ ] **Step 2: Write `LESSON_13_LCEL_SEQUENCE` for `09-runnable-compose.html`**

Must cover:
- LCEL pipe operator and `RunnableSequence`.
- Source rows:
  - `libs/core/langchain_core/runnables/base.py :: Runnable.__or__`
  - `libs/core/langchain_core/runnables/base.py :: RunnableSequence`
  - `libs/core/langchain_core/runnables/base.py :: coerce_to_runnable`
  - `libs/core/langchain_core/runnables/base.py :: RunnableLambda`
  - `libs/core/langchain_core/runnables/passthrough.py :: RunnablePassthrough`
- Explain how output of one step becomes input of next, how dict/list/callable are coerced, where type mismatches appear.
- Trace: `prompt | model | parser`.
- Pitfalls: pipe is not shell pipe, dict means parallel mapping in LCEL, lambda hides trace names, parser failure is chain failure.

- [ ] **Step 3: Write `LESSON_14_PARALLEL_BRANCH` for `12-runnable-parallel-branch.html`**

Must cover:
- Parallel fan-out, branching, passthrough/assign/map patterns.
- Source rows:
  - `libs/core/langchain_core/runnables/base.py :: RunnableParallel`
  - `libs/core/langchain_core/runnables/branch.py :: RunnableBranch`
  - `libs/core/langchain_core/runnables/passthrough.py :: RunnablePassthrough`
  - `libs/core/langchain_core/runnables/base.py :: RunnableMap`
  - `libs/core/langchain_core/runnables/base.py :: RunnableEach`
- Explain fan-out/fan-in, conditional branch selection, `assign`, retriever+question RAG pattern, batch map semantics.
- Trace: question goes to retriever and passthrough in parallel, then prompt receives dict.
- Pitfalls: parallel is about independent branches, not shared mutable state; branch predicates must be cheap and deterministic; missing keys break downstream prompt.

- [ ] **Step 4: Write `LESSON_15_CONFIG_CALLBACKS` for `13-runnable-config-callbacks.html`**

Must cover:
- `RunnableConfig`, callbacks, tags, metadata, run IDs, run tree.
- Source rows:
  - `libs/core/langchain_core/runnables/config.py :: ensure_config`
  - `libs/core/langchain_core/runnables/config.py :: patch_config`
  - `libs/core/langchain_core/callbacks/manager.py :: CallbackManager`
  - `libs/core/langchain_core/tracers/base.py :: BaseTracer`
  - `libs/core/langchain_core/runnables/base.py :: Runnable.invoke`
- Explain config propagation through nested runnables, child callbacks, tracing, LangSmith, observability boundaries.
- Trace: parent chain run -> prompt child -> model child -> parser child.
- Pitfalls: config is not state, tags are not auth, metadata can leak secrets, callbacks observe but should not mutate business data.

- [ ] **Step 5: Write `LESSON_16_RETRY_FALLBACK` for `15-runnable-retry-fallback.html`**

Must cover:
- `with_retry`, `with_fallbacks`, exception flow, robust chains.
- Source rows:
  - `libs/core/langchain_core/runnables/base.py :: Runnable.with_retry`
  - `libs/core/langchain_core/runnables/retry.py :: RunnableRetry`
  - `libs/core/langchain_core/runnables/base.py :: Runnable.with_fallbacks`
  - `libs/core/langchain_core/runnables/fallbacks.py :: RunnableWithFallbacks`
  - `libs/core/langchain_core/runnables/config.py :: RunnableConfig`
- Explain retryable vs non-retryable failures, fallback input shape, exception-key mode, provider fallback, parser repair vs fallback.
- Trace: primary model fails, fallback model succeeds, parser returns typed result.
- Pitfalls: retrying non-idempotent tools, swallowing errors, fallback changing output schema, infinite retry expectations.

- [ ] **Step 6: Replace quizzes for five M3 pages**

Each page must have 3 MCQ + 2 open prompts:

| Page | MCQ themes | Open prompt themes |
| --- | --- | --- |
| `08-runnable.html` | protocol value; config vs state; stream/batch semantics | trace invoke path; decide when to create custom Runnable |
| `09-runnable-compose.html` | sequence input/output; coercion; dict-as-parallel | debug type mismatch; compare LCEL vs manual function |
| `12-runnable-parallel-branch.html` | parallel fan-out; branch predicate; passthrough/assign | design RAG fan-out; detect missing-key failure |
| `13-runnable-config-callbacks.html` | callback propagation; tags/metadata; run tree | design tracing plan; avoid secret leakage |
| `15-runnable-retry-fallback.html` | retry vs fallback; idempotency; schema consistency | design robust chain; decide retry/fallback/repair |

Balance correct answer source indexes across 0/1/2/3.

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
for fname in ["08-runnable.html","09-runnable-compose.html","12-runnable-parallel-branch.html","13-runnable-config-callbacks.html","15-runnable-retry-fallback.html"]:
    print(fname, len(re.findall(r"[\u4e00-\u9fff]", registry.CONTENT[fname])))
PY
```

Expected: all checks pass; density passes for 16 C-level pages; each printed count is >= 4500.

Commit:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1
git add src/part03_runnable_lcel.py src/quizzes.py index.html lessons
git commit -m "Rewrite Part 3 Runnable and LCEL lessons to C-level" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Update roadmap and README for M3

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md`

- [ ] **Step 1: Update roadmap**

Set:
- M2 status to `Done`.
- M3 status to `In review`.
- M3 detailed plan to `` `2026-06-23-langchain-visual-guide-c-expansion-m3-runnable-lcel.md` ``.

- [ ] **Step 2: Update README**

Update expansion wording so it says 第一、第二、第三部分 are now C-level batches. Add `part03_runnable_lcel.py` to the project tree. Mention that current site has 32 lesson pages if the generated lesson count is 32 after M3.

- [ ] **Step 3: Validate and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1/src
python3 build.py
python3 build_print.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
cd ..
git --no-pager status --short
```

Expected: all checks pass and only docs are uncommitted.

Commit:

```bash
git add README.md docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md
git commit -m "Document M3 Runnable and LCEL expansion" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Final handoff

After Task 3 passes review, report:

- M3 commits created.
- Five M3 C-level pages migrated.
- Total C-level pages checked by density checker.
- Next plan to write: M4 “LangGraph 心智模型”.
