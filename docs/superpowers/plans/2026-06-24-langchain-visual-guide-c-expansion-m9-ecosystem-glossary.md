# LangChain Visual Guide C Expansion M9 Ecosystem and Glossary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the C-level expansion by migrating the remaining legacy internals/ecosystem/reference pages: chat internals, tool internals, ecosystem comparisons, learning map, and glossary.

**Architecture:** M9 creates `src/part09_ecosystem_reference.py`, maps the six remaining legacy filenames to it, places them as Part 9/Appendix content, extends density checks so every published lesson page is C-level, updates quizzes, and performs final README/roadmap cleanup. This milestone should leave no migrated/legacy lesson pages outside density coverage.

**Tech Stack:** Python 3 standard library; existing static HTML generator; shared C-level helpers in `src/shell.py`; validation via `build.py`, `build_print.py`, `check_html.py`, `check_links.py`, and `check_content_density.py`.

---

## M9 page set

- `11-chat-internals.html` — ChatModel Provider 内部
- `12-tool-internals.html` — Tool Schema 与执行内部
- `21-langchain-vs-autogen.html` — LangChain、LangGraph 与多 Agent 生态
- `22-ai-stack.html` — AI 全栈、MCP 与 A2A
- `23-learning-map.html` — 后续学习地图
- `27-glossary.html` — 术语表与源码索引

---

### Task 1: Register M9 page set

**Files:**
- Create: `src/part09_ecosystem_reference.py`
- Modify: `src/shell.py`
- Modify: `src/registry.py`
- Modify: `src/check_content_density.py`

- [ ] **Step 1: Create skeleton**

```python
"""C-level Part 9: ecosystem and reference."""

import shell

LESSON_41_CHAT_INTERNALS = r"""<p class="lead">M9 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_42_TOOL_INTERNALS = r"""<p class="lead">M9 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_43_ECOSYSTEM_COMPARE = r"""<p class="lead">M9 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_44_AI_STACK_PROTOCOLS = r"""<p class="lead">M9 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_45_LEARNING_MAP = r"""<p class="lead">M9 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_46_GLOSSARY = r"""<p class="lead">M9 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
```

- [ ] **Step 2: Put M9 pages after M8 in `shell.PAGES`**

```python
    ("11-chat-internals.html", "ChatModel Provider 内部", "第九部分 · 生态与速查"),
    ("12-tool-internals.html", "Tool Schema 与执行内部", "第九部分 · 生态与速查"),
    ("21-langchain-vs-autogen.html", "LangChain、LangGraph 与多 Agent 生态", "第九部分 · 生态与速查"),
    ("22-ai-stack.html", "AI 全栈、MCP 与 A2A", "第九部分 · 生态与速查"),
    ("23-learning-map.html", "后续学习地图", "第九部分 · 生态与速查"),
    ("27-glossary.html", "术语表与源码索引", "第九部分 · 生态与速查"),
```

- [ ] **Step 3: Update `SUBTITLES`**

```python
    "11-chat-internals.html": "BaseChatModel · provider adapter · payload/response normalization",
    "12-tool-internals.html": "BaseTool · args_schema · convert_to_openai_tool · ToolMessage",
    "21-langchain-vs-autogen.html": "LangGraph vs actor/pubsub frameworks · handoff · orchestration styles",
    "22-ai-stack.html": "hardware→inference→retrieval→orchestration · MCP/A2A protocol boundaries",
    "23-learning-map.html": "inference engines · vector databases · eval/observability · next repositories",
    "27-glossary.html": "concept index · source anchors · where to read next",
```

- [ ] **Step 4: Update registry**

Import `part09_ecosystem_reference` and map the six pages to it.

- [ ] **Step 5: Extend density gates to all six pages**

Add all six pages to `C_LEVEL_PAGES` with `{"min_cjk": 4500, "min_visual": 5}`. After M9, every page in `shell.PAGES` must be in `C_LEVEL_PAGES`.

- [ ] **Step 6: Verify expected temporary failure and commit**

Run build/html/link/density. Density should fail only for six M9 temporary pages. Commit:

```bash
git add src/shell.py src/registry.py src/check_content_density.py src/part09_ecosystem_reference.py index.html lessons
git commit -m "Register M9 ecosystem and glossary lesson set" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Write six C-level M9 lessons and quizzes

**Files:**
- Modify: `src/part09_ecosystem_reference.py`
- Modify: `src/quizzes.py`
- Generated: M9 lesson HTML files

Every lesson must include `lead`, `lesson_map`, `source_map`, `state_flow` or `call_graph`, `trace_table`, `code_walkthrough`, `pitfall_grid`, `lab_card`, `version_note`, `card analogy`, and `本课要点`. Each raw body must have at least 4500 CJK chars. Glossary may be table-heavy but still must include the checked components.

- [ ] **Step 1: Write `LESSON_41_CHAT_INTERNALS`**

Cover provider adapters below `BaseChatModel`. Source rows:
- `libs/core/langchain_core/language_models/chat_models.py :: BaseChatModel`
- `libs/core/langchain_core/messages/utils.py :: convert_to_messages`
- `libs/partners/openai/langchain_openai/chat_models/base.py :: ChatOpenAI`
- `libs/partners/anthropic/langchain_anthropic/chat_models.py :: ChatAnthropic`
- `libs/core/langchain_core/outputs/chat_generation.py :: ChatGeneration`

- [ ] **Step 2: Write `LESSON_42_TOOL_INTERNALS`**

Cover schema generation and execution below `@tool`. Source rows:
- `libs/core/langchain_core/tools/base.py :: BaseTool`
- `libs/core/langchain_core/tools/convert.py :: tool`
- `libs/core/langchain_core/utils/function_calling.py :: convert_to_openai_tool`
- `libs/core/langchain_core/messages/tool.py :: ToolMessage`
- `libs/prebuilt/langgraph/prebuilt/tool_node.py :: ToolNode`

- [ ] **Step 3: Write `LESSON_43_ECOSYSTEM_COMPARE`**

Cover LangChain/LangGraph vs AutoGen/CrewAI/LlamaIndex style ecosystems without overclaiming maintenance status. Source rows can cite local lessons and public package concepts; avoid unverifiable current claims unless source/path can be checked. Include paradigm comparison: graph/state, actor/pubsub, data/RAG, role-based crew.

- [ ] **Step 4: Write `LESSON_44_AI_STACK_PROTOCOLS`**

Cover AI stack layers and MCP/A2A boundaries. Source rows:
- Use course-local anchors for inference/vector/orchestration pages.
- Cite MCP/A2A as protocol concepts with version note that exact specs evolve; avoid hardcoded breaking claims.
- Compare tool protocol vs agent-to-agent protocol vs framework API.

- [ ] **Step 5: Write `LESSON_45_LEARNING_MAP`**

Cover what to study after this guide: inference engines, vector databases, eval/observability, agent protocols, contributing. Source rows should point to this course’s own sections and verified source anchors. Provide a staged reading plan.

- [ ] **Step 6: Write `LESSON_46_GLOSSARY`**

Rewrite glossary as C-level concept/source index:
- Group by Part 1-9.
- Include each current page title and key terms.
- Link terms to current pages with current titles.
- Include source anchor table for major symbols (`Runnable`, `BaseMessage`, `BaseChatModel`, `BaseTool`, `StateGraph`, `Pregel`, `create_agent`, `BaseRetriever`, `VectorStore`, `AgentMiddleware`).
- Avoid stale hard-coded old lesson numbers; use title/link wording.

- [ ] **Step 7: Replace quizzes**

Each M9 page has 3 MCQ + 2 open prompts. Balance answer indexes.

- [ ] **Step 8: Validate and commit**

Run full checks and raw CJK count. Expected: density passes for 46 C-level pages and `set(shell.PAGES) == set(C_LEVEL_PAGES)`. Commit:

```bash
git add src/part09_ecosystem_reference.py src/quizzes.py index.html lessons
git commit -m "Rewrite Part 9 ecosystem and glossary lessons to C-level" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Final docs, cleanup, and full review

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md`
- Optionally remove unused imports from `src/registry.py` after verifying no references.

- [ ] **Step 1: Update roadmap**

Set M8 status to `Done`, M9 status to `In review`, and M9 detailed plan to this file.

- [ ] **Step 2: Update README**

State that all nine parts are C-level, current site has 46 lessons, and no legacy pages remain. Add `part09_ecosystem_reference.py` to the project tree and update the final Part 9 list.

- [ ] **Step 3: Optional dead import cleanup**

Remove unused imports from `src/registry.py` only if `rg` confirms no `CONTENT` entries use those modules. Do not delete old part files in this plan.

- [ ] **Step 4: Validate and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1/src
python3 build.py
python3 build_print.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
python3 - <<'PY'
import shell
from check_content_density import C_LEVEL_PAGES
pages = {p[0] for p in shell.PAGES}
assert pages == set(C_LEVEL_PAGES), (pages - set(C_LEVEL_PAGES), set(C_LEVEL_PAGES) - pages)
print("all pages are C-level checked:", len(pages))
PY
```

Commit:

```bash
git add README.md docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md src/registry.py
git commit -m "Document completed C-level expansion" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Final handoff

After Task 3 passes review, report:

- M9 commits created.
- All 46 pages are C-level and covered by `check_content_density.py`.
- Full checks pass.
- Branch is ready for final overall review/merge workflow.
