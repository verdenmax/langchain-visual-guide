# LangChain Visual Guide C Expansion Roadmap

> **For agentic workers:** This is a milestone roadmap. Each future milestone needs its own detailed implementation plan before execution.

**Goal:** Track the Part-by-Part expansion from the legacy 27-lesson guide to a Chinese-first, source-verified, 45-55 lesson C-level guide.

| Milestone | Scope | Status | Detailed plan |
| --- | --- | --- | --- |
| M0-M1 | Shared components, density checks, rewritten Part 1 global map | In progress | `2026-06-23-langchain-visual-guide-c-expansion-m0-m1.md` |
| M2 | Part 2 user API basics: messages, chat models, tools, prompts, parsers, streaming | Not started | Plan pending after M0-M1 review |
| M3 | Part 3 Runnable and LCEL | Not started | Plan pending after M2 review |
| M4 | Part 4 LangGraph mental model | Not started | Plan pending after M3 review |
| M5 | Part 5 LangGraph execution engine | Not started | Plan pending after M4 review |
| M6 | Part 6 Agent internals | Not started | Plan pending after M5 review |
| M7 | Part 7 RAG and memory | Not started | Plan pending after M6 review |
| M8 | Part 8 engineering, testing, debugging, contribution, migration | Not started | Plan pending after M7 review |
| M9 | Part 9 ecosystem comparison, glossary, print/PDF/README final polish, including PDF/current-state 27-lesson references | Not started | Plan pending after M8 review |

## Per-milestone rule

Every future milestone must verify current LangChain/LangGraph source entry points, keep generated HTML in sync with `src/`, pass all Python checks, and run the required two-stage review: spec-compliance review followed by code-quality review.
