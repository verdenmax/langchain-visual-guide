# LangChain Visual Guide C Expansion M2 User API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the user-facing LangChain API lessons as C-level, source-verified lessons that teach messages, chat models, tools, prompts, output parsers, and streaming/callbacks.

**Architecture:** M2 builds on M0-M1 without changing the site generator architecture. It creates a new `part02_user_api.py` content module, maps existing user-API filenames into a contiguous Part 2 block in `shell.PAGES`, extends the raw-body density checker to these pages, updates quizzes, and regenerates HTML. Legacy pages that are not part of M2 remain in the guide for later milestones.

**Tech Stack:** Python 3 standard library; existing static HTML generator; shared C-level helpers in `src/shell.py`; validation via `build.py`, `build_print.py`, `check_html.py`, `check_links.py`, and `check_content_density.py`.

---

## File structure

- Create `src/part02_user_api.py`
  - Exports `LESSON_06_MESSAGES`, `LESSON_07_CHAT_MODELS`, `LESSON_08_TOOLS`, `LESSON_09_PROMPTS`, `LESSON_10_OUTPUT_PARSERS`, `LESSON_11_STREAMING`.
  - Uses shared helpers from `shell.py`.

- Modify `src/shell.py`
  - Reorder `PAGES` so the M2 pages appear immediately after the five Part 1 pages.
  - Update `SUBTITLES` for these pages.

- Modify `src/registry.py`
  - Import `part02_user_api`.
  - Map the six M2 filenames to the new module.
  - Keep legacy non-M2 pages mapped to their existing modules.

- Modify `src/quizzes.py`
  - Replace quizzes for the six M2 filenames with C-level design questions.

- Modify `src/check_content_density.py`
  - Add the six M2 pages to `C_LEVEL_PAGES`.

- Generated: `index.html`, changed `lessons/*.html`, and ignored `print.html`.

---

### Task 1: Register the M2 page set and density gates

**Files:**
- Modify: `src/shell.py`
- Modify: `src/registry.py`
- Modify: `src/check_content_density.py`
- Create: `src/part02_user_api.py`

- [ ] **Step 1: Create the new module skeleton**

Create `src/part02_user_api.py` with:

```python
"""C-level Part 2: user-facing LangChain API basics."""

import shell


LESSON_06_MESSAGES = r"""
<p class="lead">M2 临时页面：Task 2 会把这里替换为完整 C-level lesson。</p>
"""

LESSON_07_CHAT_MODELS = r"""
<p class="lead">M2 临时页面：Task 2 会把这里替换为完整 C-level lesson。</p>
"""

LESSON_08_TOOLS = r"""
<p class="lead">M2 临时页面：Task 2 会把这里替换为完整 C-level lesson。</p>
"""

LESSON_09_PROMPTS = r"""
<p class="lead">M2 临时页面：Task 2 会把这里替换为完整 C-level lesson。</p>
"""

LESSON_10_OUTPUT_PARSERS = r"""
<p class="lead">M2 临时页面：Task 2 会把这里替换为完整 C-level lesson。</p>
"""

LESSON_11_STREAMING = r"""
<p class="lead">M2 临时页面：Task 2 会把这里替换为完整 C-level lesson。</p>
"""
```

- [ ] **Step 2: Reorder `shell.PAGES`**

In `src/shell.py`, after the five Part 1 entries, place these six Part 2 entries in this order:

```python
    ("04-messages.html", "消息系统", "第二部分 · 用户 API 基础"),
    ("05-chat-models.html", "聊天模型", "第二部分 · 用户 API 基础"),
    ("06-tools.html", "工具 Tools", "第二部分 · 用户 API 基础"),
    ("16-prompts.html", "提示词 Prompts", "第二部分 · 用户 API 基础"),
    ("10-output-parsers.html", "输出解析器 Output Parsers", "第二部分 · 用户 API 基础"),
    ("14-streaming-callbacks.html", "Streaming 与 Callbacks", "第二部分 · 用户 API 基础"),
```

Keep all remaining legacy pages after this M2 block. Do not delete legacy files in this task.

- [ ] **Step 3: Update `SUBTITLES` for M2**

Set these subtitles in `src/shell.py`:

```python
    "04-messages.html": "BaseMessage · Human/AI/System/Tool · tool_calls · usage_metadata",
    "05-chat-models.html": "init_chat_model · BaseChatModel.invoke · provider wrapper",
    "06-tools.html": "@tool · BaseTool · schema 生成 · ToolMessage 回填",
    "16-prompts.html": "ChatPromptTemplate · MessagesPlaceholder · PromptValue · partial",
    "10-output-parsers.html": "StrOutputParser · JsonOutputParser · structured output · repair loop",
    "14-streaming-callbacks.html": "stream/astream_events · callback manager · run tree",
```

- [ ] **Step 4: Update `registry.py`**

Add:

```python
import part02_user_api
```

Map the six M2 pages:

```python
    "04-messages.html": part02_user_api.LESSON_06_MESSAGES,
    "05-chat-models.html": part02_user_api.LESSON_07_CHAT_MODELS,
    "06-tools.html": part02_user_api.LESSON_08_TOOLS,
    "16-prompts.html": part02_user_api.LESSON_09_PROMPTS,
    "10-output-parsers.html": part02_user_api.LESSON_10_OUTPUT_PARSERS,
    "14-streaming-callbacks.html": part02_user_api.LESSON_11_STREAMING,
```

Keep `07-agents-intro.html` mapped to `part2.LESSON_07` and all non-M2 legacy pages mapped as before.

- [ ] **Step 5: Extend `check_content_density.py`**

Add these pages to `C_LEVEL_PAGES`:

```python
    "04-messages.html": {"min_cjk": 4500, "min_visual": 5},
    "05-chat-models.html": {"min_cjk": 4500, "min_visual": 5},
    "06-tools.html": {"min_cjk": 4500, "min_visual": 5},
    "16-prompts.html": {"min_cjk": 4500, "min_visual": 5},
    "10-output-parsers.html": {"min_cjk": 4500, "min_visual": 5},
    "14-streaming-callbacks.html": {"min_cjk": 4500, "min_visual": 5},
```

- [ ] **Step 6: Verify this task intentionally fails density**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1/src
python3 build.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
```

Expected: `build.py`, `check_html.py`, and `check_links.py` pass. `check_content_density.py` fails for the six placeholder M2 pages. That failure is expected until Task 2 writes the complete lessons.

- [ ] **Step 7: Commit**

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1
git add src/shell.py src/registry.py src/check_content_density.py src/part02_user_api.py index.html lessons
git commit -m "Register M2 user API lesson set" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Write the six C-level M2 lessons

**Files:**
- Modify: `src/part02_user_api.py`
- Generated: six M2 lesson HTML files

- [ ] **Step 1: Replace `LESSON_06_MESSAGES`**

Write a complete C-level lesson for `04-messages.html`. It must contain:

- `lead`: messages are LangChain’s normalized conversation/data contract.
- `lesson_map`: user text, `BaseMessage`, provider payload, Agent state.
- `source_map` rows:
  - `libs/core/langchain_core/messages/base.py :: BaseMessage`
  - `libs/core/langchain_core/messages/human.py :: HumanMessage`
  - `libs/core/langchain_core/messages/ai.py :: AIMessage`
  - `libs/core/langchain_core/messages/tool.py :: ToolMessage`
  - `libs/core/langchain_core/messages/utils.py :: convert_to_messages`
- `call_graph`: string/list/dict input -> message objects -> provider adapter -> AIMessage/tool_calls -> downstream Runnable/Agent.
- `code_walkthrough`: simplified message normalization pseudocode.
- `trace_table`: one input “查订单 123” becomes `HumanMessage`, model response becomes `AIMessage` with a tool-calls list, tool result becomes `ToolMessage`, final answer becomes `AIMessage`.
- Sections explaining `role/content`, `additional_kwargs`, `tool_calls`, `usage_metadata`, message IDs, and why `ToolMessage.tool_call_id` matters.
- `pitfall_grid`: dict vs message object, `AIMessage.tool_calls` vs executed tool result, `ToolMessage` without matching ID, token usage metadata as tracing not business state.
- `lab_card`: inspect a message list before/after one fake tool round.
- `version_note`: cite LangChain v1 / langchain-core source anchor.
- `card analogy` and a `本课要点` section.
- Raw CJK count at least 4500.

- [ ] **Step 2: Replace `LESSON_07_CHAT_MODELS`**

Write a complete lesson for `05-chat-models.html`. It must contain:

- `lead`: chat models wrap provider APIs behind `BaseChatModel`.
- `lesson_map`: `init_chat_model`, provider string, `BaseChatModel`, provider wrapper, `AIMessage`.
- `source_map` rows:
  - `libs/langchain_v1/langchain/chat_models/base.py :: init_chat_model`
  - `libs/core/langchain_core/language_models/chat_models.py :: BaseChatModel`
  - `libs/core/langchain_core/runnables/config.py :: RunnableConfig`
  - `libs/partners/openai/langchain_openai/chat_models/base.py :: ChatOpenAI`
  - `libs/partners/anthropic/langchain_anthropic/chat_models.py :: ChatAnthropic`
- `state_flow`: model string -> provider package lookup -> wrapper init -> message conversion -> provider request -> `AIMessage`.
- `code_walkthrough`: simplified `init_chat_model` + `invoke` path.
- `trace_table`: switch `openai:gpt-5.1` to `anthropic:claude-sonnet-4-5` while messages and downstream code stay stable.
- Explain invoke/stream/batch, async variants, `bind_tools`, model kwargs, retry/fallback hooks.
- `pitfall_grid`: model object vs provider client, `invoke` result type, `batch` vs parallel tools, provider-specific kwargs leakage.
- `lab_card`: print model class and result metadata with a fake or deterministic model.
- `card analogy`, `本课要点`, raw CJK >= 4500.

- [ ] **Step 3: Replace `LESSON_08_TOOLS`**

Write a complete lesson for `06-tools.html`. It must contain:

- `lead`: tools are the bridge from model intention to real code execution.
- `lesson_map`: Python function, JSON schema, model tool call, tool execution, `ToolMessage`.
- `source_map` rows:
  - `libs/core/langchain_core/tools/convert.py :: tool`
  - `libs/core/langchain_core/tools/base.py :: BaseTool`
  - `libs/core/langchain_core/utils/function_calling.py :: convert_to_openai_tool`
  - `libs/langchain_v1/langchain/agents/factory.py :: create_agent`
  - `libs/core/langchain_core/messages/tool.py :: ToolMessage`
- `call_graph`: function -> schema -> bound model -> `AIMessage.tool_calls` -> execute -> `ToolMessage`.
- `code_walkthrough`: simplified `@tool` decorator and schema extraction.
- `trace_table`: weather/order lookup tool call with `id`, arguments, execution result, `ToolMessage`.
- Explain docstring quality, type annotations, pydantic args schema, injected state/runtime, error surfaces.
- `pitfall_grid`: schema is not execution, docstring is prompt contract, unsafe side effects, missing `tool_call_id`, broad exception swallowing.
- `lab_card`: write one pure tool and inspect `.args_schema` / `.name` / `.description`.
- `card analogy`, `本课要点`, raw CJK >= 4500.

- [ ] **Step 4: Replace `LESSON_09_PROMPTS`**

Write a complete lesson for `16-prompts.html`. It must contain:

- `lead`: prompts are structured message factories, not just string templates.
- `lesson_map`: variables, `ChatPromptTemplate`, `MessagesPlaceholder`, `PromptValue`, model input.
- `source_map` rows:
  - `libs/core/langchain_core/prompts/chat.py :: ChatPromptTemplate`
  - `libs/core/langchain_core/prompts/chat.py :: MessagesPlaceholder`
  - `libs/core/langchain_core/prompt_values.py :: ChatPromptValue`
  - `libs/core/langchain_core/runnables/base.py :: Runnable`
  - `libs/core/langchain_core/prompts/base.py :: BasePromptTemplate`
- `state_flow`: template declaration -> variable validation -> partial binding -> format -> messages -> model.
- `code_walkthrough`: simplified `ChatPromptTemplate.invoke`.
- `trace_table`: template with `{role}`, `{question}`, history placeholder becomes concrete messages.
- Explain system/human/history separation, partial variables, optional placeholders, few-shot placement, prompt as Runnable.
- `pitfall_grid`: string prompt vs chat prompt, history as one string vs messages, missing variables, overstuffed system prompt, prompt injection boundary.
- `lab_card`: format a prompt with and without history and compare message list.
- `card analogy`, `本课要点`, raw CJK >= 4500.

- [ ] **Step 5: Replace `LESSON_10_OUTPUT_PARSERS`**

Write a complete lesson for `10-output-parsers.html`. It must contain:

- `lead`: parsers turn model text/messages into application data contracts.
- `lesson_map`: model output, parser, typed data, error/repair loop, downstream app.
- `source_map` rows:
  - `libs/core/langchain_core/output_parsers/string.py :: StrOutputParser`
  - `libs/core/langchain_core/output_parsers/json.py :: JsonOutputParser`
  - `libs/core/langchain_core/output_parsers/base.py :: BaseOutputParser`
  - `libs/core/langchain_core/language_models/chat_models.py :: with_structured_output`
  - `libs/core/langchain_core/runnables/base.py :: RunnableSequence`
- `call_graph`: prompt -> model -> parser -> typed result -> validation/repair.
- `code_walkthrough`: simplified parser `invoke` and JSON parsing path.
- `trace_table`: raw model output with JSON text -> parser -> dict -> validation error -> repair prompt.
- Explain parser vs structured output, Pydantic schemas, partial/streaming parse, failure handling.
- `pitfall_grid`: regex-only parsing, trusting malformed JSON, parser vs tool call, swallowing parse errors, schema as documentation only.
- `lab_card`: intentionally break JSON and observe parser error.
- `card analogy`, `本课要点`, raw CJK >= 4500.

- [ ] **Step 6: Replace `LESSON_11_STREAMING`**

Write a complete lesson for `14-streaming-callbacks.html`. It must contain:

- `lead`: streaming and callbacks reveal the run while it is happening.
- `lesson_map`: stream chunks, callback events, run tree, LangSmith/tracing, user UI.
- `source_map` rows:
  - `libs/core/langchain_core/language_models/chat_models.py :: BaseChatModel.stream`
  - `libs/core/langchain_core/runnables/base.py :: astream_events`
  - `libs/core/langchain_core/callbacks/manager.py :: CallbackManager`
  - `libs/core/langchain_core/callbacks/base.py :: BaseCallbackHandler`
  - `libs/core/langchain_core/tracers/base.py :: BaseTracer`
- `state_flow`: run start -> model start -> token/chunk events -> tool/chain events -> run end/error.
- `code_walkthrough`: simplified callback lifecycle with `on_chat_model_start`, `on_llm_new_token`, `on_llm_end`, `on_llm_error`.
- `trace_table`: one streaming answer emits chunks and run events, then final message.
- Explain `stream`, `astream`, `astream_events`, callback handlers, tags/metadata, run IDs, LangSmith, UI backpressure.
- `pitfall_grid`: streaming as faster total latency, chunks as final messages, callbacks as middleware, logging secrets, ignoring error events.
- `lab_card`: print chunks and event names for one small chain.
- `card analogy`, `本课要点`, raw CJK >= 4500.

- [ ] **Step 7: Verify raw body density**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1/src
python3 - <<'PY'
import re, registry
for fname in [
    "04-messages.html", "05-chat-models.html", "06-tools.html",
    "16-prompts.html", "10-output-parsers.html", "14-streaming-callbacks.html",
]:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", registry.CONTENT[fname]))
    print(fname, cjk)
PY
```

Expected: every page prints `>= 4500`.

- [ ] **Step 8: Commit**

Do not commit yet if density fails. Once the six lessons pass density, commit them after Task 3 updates quizzes and final checks, not here.

---

### Task 3: Update M2 quizzes and run full validation

**Files:**
- Modify: `src/quizzes.py`
- Generated: `index.html`, changed `lessons/*.html`

- [ ] **Step 1: Replace quizzes for the six M2 pages**

For each filename below, define 3 `mcq` entries and 2 `open` prompts. Use the existing quiz schema: each MCQ has `q`, `opts`, `answer`, `why`; each `answer` is a 0-based index.

Required themes:

| Filename | MCQ themes | Open prompt themes |
| --- | --- | --- |
| `04-messages.html` | message as contract; `tool_calls` vs `ToolMessage`; usage metadata | trace one message list; identify invalid tool result |
| `05-chat-models.html` | provider wrapper boundary; `invoke` return type; `bind_tools` effect | switch provider while preserving app code; inspect model config |
| `06-tools.html` | schema vs execution; docstring/type annotation; tool_call_id pairing | design a safe tool; handle tool error explicitly |
| `16-prompts.html` | prompt as Runnable; `MessagesPlaceholder`; partial variables | compare history string vs message list; prompt injection boundary |
| `10-output-parsers.html` | parser vs structured output; parse error handling; schema validation | design repair loop; decide parser vs tool call |
| `14-streaming-callbacks.html` | chunks vs final messages; callbacks vs middleware; event stream | build UI token stream; avoid logging secrets |

- [ ] **Step 2: Run full validation**

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

Expected:

- `build.py` writes current site pages.
- `build_print.py` writes print HTML.
- `check_html.py` reports 0 errors and 0 warnings.
- `check_links.py` resolves all links.
- `check_content_density.py` passes for 11 C-level pages: five M1 + six M2.
- `git status --short` shows only intentional source/generated changes.

- [ ] **Step 3: Commit M2**

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1
git add src/shell.py src/registry.py src/check_content_density.py src/part02_user_api.py src/quizzes.py index.html lessons
git commit -m "Rewrite Part 2 user API lessons to C-level" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 4: Update roadmap status and final M2 review

**Files:**
- Modify: `docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md`

- [ ] **Step 1: Update roadmap status**

In the roadmap table:

- Change M0-M1 status to `Done`.
- Change M2 status to `In review`.
- Set M2 detailed plan to `` `2026-06-23-langchain-visual-guide-c-expansion-m2-user-api.md` ``.

- [ ] **Step 2: Run final validation**

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

Expected: all checks pass. Only roadmap should be uncommitted.

- [ ] **Step 3: Commit roadmap**

```bash
cd /home/verden/course/langchain-visual-guide/.worktrees/c-expansion-m0-m1
git add docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md
git commit -m "Mark M2 user API expansion in roadmap" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Final handoff

After Task 4 passes review, report:

- M2 commits created.
- Six C-level M2 pages migrated.
- Total C-level pages checked by `check_content_density.py`.
- Next plan to write: M3 “Runnable 与 LCEL”.
