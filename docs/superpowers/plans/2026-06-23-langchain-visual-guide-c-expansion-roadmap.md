# LangChain Visual Guide C Expansion Roadmap

> **For agentic workers:** This is a milestone roadmap. Each future milestone needs its own detailed implementation plan before execution.

**Goal:** Track the Part-by-Part expansion from the legacy 27-lesson guide to a Chinese-first, source-verified, 45-55 lesson C-level guide.

| Milestone | Scope | Status | Detailed plan |
| --- | --- | --- | --- |
| M0-M1 | Shared components, density checks, rewritten Part 1 global map | Done | `2026-06-23-langchain-visual-guide-c-expansion-m0-m1.md` |
| M2 | Part 2 user API basics: messages, chat models, tools, prompts, parsers, streaming | Done | `2026-06-23-langchain-visual-guide-c-expansion-m2-user-api.md` |
| M3 | Part 3 Runnable and LCEL | Done | `2026-06-23-langchain-visual-guide-c-expansion-m3-runnable-lcel.md` |
| M4 | Part 4 LangGraph mental model | Done | `2026-06-23-langchain-visual-guide-c-expansion-m4-langgraph-model.md` |
| M5 | Part 5 LangGraph execution engine | Done | `2026-06-23-langchain-visual-guide-c-expansion-m5-langgraph-engine.md` |
| M6 | Part 6 Agent internals | Done | `2026-06-24-langchain-visual-guide-c-expansion-m6-agent-internals.md` |
| M7 | Part 7 RAG and memory | Done | `2026-06-24-langchain-visual-guide-c-expansion-m7-rag-memory.md` |
| M8 | Part 8 engineering, testing, debugging, contribution, migration | In review | `2026-06-24-langchain-visual-guide-c-expansion-m8-engineering.md` |
| M9 | Part 9 ecosystem comparison, glossary, print/PDF/README final polish, including remaining legacy 27-lesson references and final PDF/README count polish | Not started | Plan pending after M8 review |

## Per-milestone rule

Every future milestone must verify current LangChain/LangGraph source entry points, keep generated HTML in sync with `src/`, pass all Python checks, and run the required two-stage review: spec-compliance review followed by code-quality review.
