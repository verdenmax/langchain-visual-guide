# LangChain Visual Guide C Expansion M7 RAG and Memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the RAG and memory layer as C-level lessons covering RAG flow, documents/splitting, embeddings/vector stores, retrievers/reranking, and conversation memory/state.

**Architecture:** M7 creates `src/part07_rag_memory.py`, reuses `17-rag.html`, adds four new RAG/memory pages, places the block after M6, extends raw-body density checks, replaces matching quizzes, and updates README/roadmap. Remaining engineering/ecosystem/glossary pages stay in transitional groups until M8/M9.

**Tech Stack:** Python 3 standard library; existing static HTML generator; shared C-level helpers in `src/shell.py`; validation via `build.py`, `build_print.py`, `check_html.py`, `check_links.py`, and `check_content_density.py`.

---

## M7 page set

- `17-rag.html` — RAG 全链路
- `36-documents-splitters.html` — Document、Loader 与 Splitter
- `37-embeddings-vectorstores.html` — Embeddings 与 VectorStore
- `38-retrievers-rerankers.html` — Retriever、压缩与 Rerank
- `39-memory-conversation-state.html` — 记忆、会话历史与状态

---

### Task 1: Register M7 page set

**Files:**
- Create: `src/part07_rag_memory.py`
- Modify: `src/shell.py`
- Modify: `src/registry.py`
- Modify: `src/check_content_density.py`

- [ ] **Step 1: Create skeleton**

```python
"""C-level Part 7: RAG and memory."""

import shell

LESSON_32_RAG_FLOW = r"""<p class="lead">M7 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_33_DOCUMENTS_SPLITTERS = r"""<p class="lead">M7 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_34_EMBEDDINGS_VECTORSTORES = r"""<p class="lead">M7 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_35_RETRIEVERS_RERANKERS = r"""<p class="lead">M7 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
LESSON_36_MEMORY_STATE = r"""<p class="lead">M7 临时页面：Task 2 会替换为完整 C-level lesson。</p>"""
```

- [ ] **Step 2: Add M7 pages after M6 block in `shell.PAGES`**

```python
    ("17-rag.html", "RAG 全链路", "第七部分 · RAG 与记忆"),
    ("36-documents-splitters.html", "Document、Loader 与 Splitter", "第七部分 · RAG 与记忆"),
    ("37-embeddings-vectorstores.html", "Embeddings 与 VectorStore", "第七部分 · RAG 与记忆"),
    ("38-retrievers-rerankers.html", "Retriever、压缩与 Rerank", "第七部分 · RAG 与记忆"),
    ("39-memory-conversation-state.html", "记忆、会话历史与状态", "第七部分 · RAG 与记忆"),
```

Move legacy `20-capstone.html` and remaining non-migrated practical pages to migration labels if needed to avoid duplicate ordinal groups.

- [ ] **Step 3: Update `SUBTITLES`**

```python
    "17-rag.html": "query -> retrieve -> stuff/map-rerank -> answer · Retriever as Runnable",
    "36-documents-splitters.html": "Document · metadata · TextSplitter · chunk overlap",
    "37-embeddings-vectorstores.html": "Embeddings · VectorStore · similarity search · indexing",
    "38-retrievers-rerankers.html": "BaseRetriever · contextual compression · rerank · recall/precision",
    "39-memory-conversation-state.html": "chat history · summary memory · LangGraph state · long-term memory",
```

- [ ] **Step 4: Update registry**

Import `part07_rag_memory` and map:

```python
    "17-rag.html": part07_rag_memory.LESSON_32_RAG_FLOW,
    "36-documents-splitters.html": part07_rag_memory.LESSON_33_DOCUMENTS_SPLITTERS,
    "37-embeddings-vectorstores.html": part07_rag_memory.LESSON_34_EMBEDDINGS_VECTORSTORES,
    "38-retrievers-rerankers.html": part07_rag_memory.LESSON_35_RETRIEVERS_RERANKERS,
    "39-memory-conversation-state.html": part07_rag_memory.LESSON_36_MEMORY_STATE,
```

- [ ] **Step 5: Extend density gates**

Add the five M7 pages to `C_LEVEL_PAGES` with `{"min_cjk": 4500, "min_visual": 5}`.

- [ ] **Step 6: Verify expected temporary failure and commit**

Run build/html/link/density. Density should fail only for five M7 temporary pages. Commit:

```bash
git add src/shell.py src/registry.py src/check_content_density.py src/part07_rag_memory.py index.html lessons
git commit -m "Register M7 RAG and memory lesson set" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Write five C-level M7 lessons and quizzes

**Files:**
- Modify: `src/part07_rag_memory.py`
- Modify: `src/quizzes.py`
- Generated: M7 lesson HTML files

Every lesson must include `lead`, `lesson_map`, `source_map`, `state_flow` or `call_graph`, `trace_table`, `code_walkthrough`, `pitfall_grid`, `lab_card`, `version_note`, `card analogy`, and `本课要点`. Each raw body must have at least 4500 CJK chars.

- [ ] **Step 1: Write `LESSON_32_RAG_FLOW`**

Cover the end-to-end RAG loop and Retriever as Runnable. Source rows:
- `libs/core/langchain_core/documents/base.py :: Document`
- `libs/core/langchain_core/retrievers.py :: BaseRetriever`
- `libs/core/langchain_core/vectorstores/base.py :: VectorStore`
- `libs/core/langchain_core/prompts/chat.py :: ChatPromptTemplate`
- `libs/core/langchain_core/runnables/base.py :: Runnable`

Trace: question -> rewrite optional -> retrieve docs -> format context -> model answer -> cite/verify.

- [ ] **Step 2: Write `LESSON_33_DOCUMENTS_SPLITTERS`**

Cover Document, metadata, loaders concept, splitting/chunk overlap. Source rows:
- `libs/core/langchain_core/documents/base.py :: Document`
- `libs/text-splitters/langchain_text_splitters/base.py :: TextSplitter`
- `libs/text-splitters/langchain_text_splitters/character.py :: RecursiveCharacterTextSplitter`
- `libs/community/langchain_community/document_loaders/base.py :: BaseLoader`
- `libs/core/langchain_core/document_loaders/base.py :: BaseLoader` if present; if current source differs, use the verified actual path and update plan before final review.

Trace: raw page -> Document -> chunks -> metadata propagation.

- [ ] **Step 3: Write `LESSON_34_EMBEDDINGS_VECTORSTORES`**

Cover embeddings, vector stores, similarity search, indexing/upserts. Source rows:
- `libs/core/langchain_core/embeddings/embeddings.py :: Embeddings`
- `libs/core/langchain_core/vectorstores/base.py :: VectorStore`
- `libs/core/langchain_core/vectorstores/base.py :: VectorStoreRetriever`
- `libs/core/langchain_core/indexing/api.py :: index`
- `libs/community/langchain_community/vectorstores/faiss.py :: FAISS` or another verified concrete vector store path.

Trace: chunks -> embedding vectors -> add_documents -> similarity_search -> docs.

- [ ] **Step 4: Write `LESSON_35_RETRIEVERS_RERANKERS`**

Cover BaseRetriever, search kwargs, contextual compression, rerank, recall/precision. Source rows:
- `libs/core/langchain_core/retrievers.py :: BaseRetriever`
- `libs/core/langchain_core/vectorstores/base.py :: VectorStoreRetriever`
- `libs/langchain/langchain/retrievers/contextual_compression.py :: ContextualCompressionRetriever` if current source exists; otherwise verify/update to current path.
- `libs/langchain/langchain/retrievers/document_compressors/base.py :: BaseDocumentCompressor` if current source exists; otherwise verify/update.
- `libs/core/langchain_core/runnables/base.py :: Runnable`

Trace: query -> broad retriever -> compressor/reranker -> top-k context.

- [ ] **Step 5: Write `LESSON_36_MEMORY_STATE`**

Cover chat history, summary memory, LangGraph state, short-term vs long-term memory. Source rows:
- `libs/core/langchain_core/chat_history.py :: BaseChatMessageHistory`
- `libs/community/langchain_community/chat_message_histories/in_memory.py :: ChatMessageHistory` or verified current path
- `langgraph/graph/message.py :: add_messages`
- `langgraph/checkpoint/memory/__init__.py :: InMemorySaver`
- `libs/langchain_v1/langchain/agents/factory.py :: create_agent`

Trace: conversation turn -> append messages -> checkpoint/state -> retrieval or summary memory -> next turn context.

- [ ] **Step 6: Replace quizzes**

Each page has 3 MCQ + 2 open prompts:

| Page | MCQ themes | Open prompt themes |
| --- | --- | --- |
| `17-rag.html` | RAG stages; Retriever as Runnable; context grounding | design RAG trace; decide when not to use RAG |
| `36-documents-splitters.html` | metadata propagation; chunk size/overlap; loader boundary | design splitter; debug lost citation |
| `37-embeddings-vectorstores.html` | embedding contract; vector store retriever; indexing/upsert | choose vector store; debug stale index |
| `38-retrievers-rerankers.html` | recall vs precision; compression; rerank | design retriever stack; tune top-k |
| `39-memory-conversation-state.html` | history vs memory; state vs long-term store; checkpoint | design memory policy; avoid privacy leak |

Balance answer indexes.

- [ ] **Step 7: Validate and commit**

Run full checks and raw CJK count. Expected: density passes for 36 C-level pages. Commit:

```bash
git add src/part07_rag_memory.py src/quizzes.py index.html lessons
git commit -m "Rewrite Part 7 RAG and memory lessons to C-level" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Update README and roadmap for M7

Set M6 status to `Done`, M7 to `In review`, link this plan. Update README to say 第一到第七部分 are C-level, add `part07_rag_memory.py`, mention current site has 44 lesson pages after M7, and list the five M7 current pages. Run full checks and commit:

```bash
git add README.md docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md
git commit -m "Document M7 RAG and memory expansion" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Final handoff

After Task 3 passes review, report:

- M7 commits created.
- Five M7 C-level pages migrated.
- Total C-level pages checked by density checker.
- Next plan to write: M8 “工程化与贡献”.
