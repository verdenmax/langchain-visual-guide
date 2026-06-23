# LangChain Visual Guide C Expansion M0-M1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the C-level expansion foundation and rewrite the first Part as the template batch for the future 45-55 lesson LangChain visual guide.

**Architecture:** This plan covers only M0-M1 because the approved C-level spec is too large for one execution pass. M0 adds reusable visual/source/trace components and a strict content-density checker; M1 rewrites the first Part (“全局地图”) as five source-verified C-level lessons. Later Parts must each get their own plan after this template batch is reviewed.

**Tech Stack:** Python 3 standard library; self-contained HTML/CSS/JS; existing `src/build.py`, `src/build_print.py`, `src/check_html.py`, `src/check_links.py`; GitHub Actions CI.

---

## Scope split

This plan implements:

1. **M0 Foundation:** shared component helpers, print rules, density checker, and CI wiring.
2. **M1 Template Part:** five rewritten Part 1 lessons that establish the C-level content and visual standard.
3. **Handoff artifacts:** README update and roadmap for later M2-M9 plans.

Out of scope:

- Rewriting Parts 2-9.
- Full English bilingual lesson bodies.
- Switching to a third-party static site generator.
- Copying upstream LangChain/LangGraph source code into this repository.

## File structure

- Modify `src/shell.py`: add escaping helpers, component helpers, component CSS, module-level `SUBTITLES`, and new Part 1 page order.
- Modify `src/build_print.py`: add print keep-together rules for the new components.
- Create `src/check_content_density.py`: enforce the C-level standard only for migrated pages.
- Create `src/part01_overview.py`: new Part 1 content module exporting `LESSON_01` through `LESSON_05`.
- Modify `src/registry.py`: map M1 pages to `part01_overview`.
- Modify `src/quizzes.py`: add/rewrite quizzes for M1 pages.
- Modify `src/check_html.py`: add stale-text guards for old 27-lesson framing.
- Modify `.github/workflows/ci.yml`: run the density checker in CI after M1 passes locally.
- Modify `README.md`: document C-level expansion status.
- Create `docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md`: milestone roadmap.
- Regenerate and commit `index.html` and changed `lessons/*.html`.

---

### Task 1: Add C-level shared lesson components

**Files:**
- Modify: `src/shell.py`

- [ ] **Step 1: Add escaping helpers**

Add after `import base64`:

```python
import html as _html
```

Add after `head_meta()`:

```python
def esc(s):
    """Escape plain text for HTML text/attribute contexts."""
    return _html.escape(str(s), quote=True)


def _attrs(**kwargs):
    """Build a safe HTML attribute string from keyword arguments."""
    parts = []
    for key, value in kwargs.items():
        if value is None or value is False:
            continue
        name = key.rstrip("_").replace("_", "-")
        if value is True:
            parts.append(name)
        else:
            parts.append(f'{name}="{esc(value)}"')
    return (" " + " ".join(parts)) if parts else ""
```

- [ ] **Step 2: Add component helpers**

Add these functions below `_attrs()`:

```python
def lesson_map(title, nodes):
    items = []
    for label, desc, kind in nodes:
        items.append(
            f'<div class="map-node {esc(kind)}">'
            f'<div class="mn-label">{esc(label)}</div>'
            f'<div class="mn-desc">{esc(desc)}</div>'
            f'</div>'
        )
    return (
        '<div class="lesson-map">'
        f'<div class="lm-title">🗺️ {esc(title)}</div>'
        f'<div class="lm-grid">{"".join(items)}</div>'
        '</div>'
    )


def source_map(rows):
    body = []
    for row in rows:
        body.append(
            '<tr>'
            f'<td class="mono">{esc(row["file"])}</td>'
            f'<td class="mono">{esc(row["symbol"])}</td>'
            f'<td>{esc(row["role"])}</td>'
            f'<td>{esc(row["direction"])}</td>'
            '</tr>'
        )
    return (
        '<table class="t source-map">'
        '<tr><th>文件</th><th>符号</th><th>职责</th><th>调用方向</th></tr>'
        f'{"".join(body)}'
        '</table>'
    )


def call_graph(steps):
    parts = []
    for i, (title, detail, highlight) in enumerate(steps):
        cls = "node hl" if highlight else "node"
        parts.append(
            f'<div class="{cls}"><div class="nt">{esc(title)}</div>'
            f'<div class="nd">{esc(detail)}</div></div>'
        )
        if i + 1 < len(steps):
            parts.append('<div class="arrow">-&gt;</div>')
    return f'<div class="flow call-graph">{"".join(parts)}</div>'


def state_flow(steps):
    parts = []
    for idx, (title, detail, code_label) in enumerate(steps, 1):
        code = f'<div class="mono">{esc(code_label)}</div>' if code_label else ""
        parts.append(
            '<div class="step">'
            f'<div class="num">{idx}</div>'
            f'<div class="sc"><h4>{esc(title)}</h4><p>{esc(detail)}</p>{code}</div>'
            '</div>'
        )
    return f'<div class="vflow state-flow">{"".join(parts)}</div>'


def trace_table(rows):
    body = []
    for row in rows:
        body.append(
            '<tr>'
            f'<td>{esc(row["step"])}</td>'
            f'<td>{esc(row["input"])}</td>'
            f'<td>{esc(row["action"])}</td>'
            f'<td>{esc(row["output"])}</td>'
            '</tr>'
        )
    return (
        '<table class="t trace-table">'
        '<tr><th>步骤</th><th>输入/状态</th><th>发生了什么</th><th>输出/新状态</th></tr>'
        f'{"".join(body)}'
        '</table>'
    )


def code_walkthrough(path, symbol, code, note):
    return (
        '<div class="codefile code-walkthrough">'
        '<div class="cf-head"><span class="dot"></span>'
        f'<span class="path">{esc(path)} :: {esc(symbol)}</span>'
        '<span class="ln">简化版</span></div>'
        f'<pre>{esc(code)}</pre>'
        f'<div class="cw-note">{esc(note)}</div>'
        '</div>'
    )


def pitfall_grid(items):
    cards = []
    for wrong, correct in items:
        cards.append(
            '<div class="pitfall">'
            f'<div class="pf-wrong">误解：{esc(wrong)}</div>'
            f'<div class="pf-correct">正确：{esc(correct)}</div>'
            '</div>'
        )
    return f'<div class="pitfall-grid">{"".join(cards)}</div>'


def lab_card(title, steps):
    lis = "".join(f'<li>{esc(step)}</li>' for step in steps)
    return (
        '<div class="card lab">'
        f'<div class="tag">🧪 小实验 · {esc(title)}</div>'
        f'<ol>{lis}</ol>'
        '</div>'
    )


def version_note(text):
    return (
        '<div class="card version">'
        '<div class="tag">📌 版本锚点</div>'
        f'{esc(text)}'
        '</div>'
    )


def svg_diagram(title, svg_body):
    return (
        '<figure class="svg-diagram">'
        f'<figcaption>{esc(title)}</figcaption>'
        f'{svg_body}'
        '</figure>'
    )
```

- [ ] **Step 3: Add component CSS**

Append this inside the existing raw `CSS` string before its closing triple quote:

```css

/* ---- C-level expansion components ---- */
.lesson-map { border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel);
  box-shadow: var(--shadow); padding: 1rem 1.1rem; margin: 1.25rem 0; }
.lesson-map .lm-title { font-weight: 750; color: var(--accent-ink); margin-bottom: .75rem; }
.lm-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .65rem; }
@media (max-width: 760px) { .lm-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 520px) { .lm-grid { grid-template-columns: 1fr; } }
.map-node { border: 1px solid var(--line); border-radius: 11px; padding: .7rem .75rem; background: var(--panel-2); }
.map-node.now { border-color: var(--accent); background: var(--accent-soft); }
.map-node.before { border-left: 4px solid var(--blue); }
.map-node.after { border-left: 4px solid var(--purple); }
.map-node.source { border-left: 4px solid var(--amber); }
.mn-label { font-weight: 720; font-size: .9rem; }
.mn-desc { color: var(--muted); font-size: .78rem; margin-top: .2rem; }
.source-map td:first-child, .source-map td:nth-child(2) { white-space: nowrap; }
.trace-table td:first-child { font-weight: 700; color: var(--accent-ink); white-space: nowrap; }
.code-walkthrough .cw-note { padding: .55rem .85rem; background: var(--panel-2); border-top: 1px solid var(--line);
  color: var(--muted); font-size: .82rem; }
.pitfall-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .8rem; margin: 1.1rem 0; }
@media (max-width: 640px) { .pitfall-grid { grid-template-columns: 1fr; } }
.pitfall { border: 1px solid var(--line); border-radius: 12px; background: var(--panel); box-shadow: var(--shadow); overflow: hidden; }
.pf-wrong { padding: .65rem .8rem; background: var(--red-soft); color: var(--red); font-weight: 680; }
.pf-correct { padding: .65rem .8rem; color: var(--muted); }
.card.lab { border-left: 4px solid var(--blue); background: var(--blue-soft); }
.card.lab .tag { color: var(--blue); }
.card.version { border-left: 4px solid var(--purple); background: var(--purple-soft); }
.card.version .tag { color: var(--purple); }
.svg-diagram { border: 1px solid var(--line); border-radius: var(--radius); background: var(--panel);
  box-shadow: var(--shadow); padding: 1rem; margin: 1.3rem 0; overflow-x: auto; }
.svg-diagram figcaption { font-weight: 720; color: var(--accent-ink); margin-bottom: .6rem; }
.svg-diagram svg { max-width: 100%; height: auto; display: block; }
```

- [ ] **Step 4: Verify and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide
python3 -m py_compile src/shell.py
git add src/shell.py
git commit -m "Add C-level lesson component helpers" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

Expected: `py_compile` exits 0 and the commit succeeds.

---

### Task 2: Add the C-level content density checker

**Files:**
- Create: `src/check_content_density.py`

- [ ] **Step 1: Create the checker**

Create `src/check_content_density.py` with this complete content:

```python
"""C-level lesson content-density checks.

Only pages listed in C_LEVEL_PAGES are checked so the guide can migrate
Part-by-Part. Migrated pages must meet the new standard; legacy pages are
ignored until their Part is rewritten.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
LESSONS = os.path.join(ROOT, "lessons")

C_LEVEL_PAGES = {
    "01-what-is-langchain.html": {"min_cjk": 4500, "min_visual": 5},
    "02-monorepo.html": {"min_cjk": 4500, "min_visual": 5},
    "03-lifecycle.html": {"min_cjk": 4500, "min_visual": 5},
    "04-source-reading-map.html": {"min_cjk": 4500, "min_visual": 5},
    "05-learning-path.html": {"min_cjk": 4200, "min_visual": 4},
}

RE_SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.I | re.S)
RE_PRE = re.compile(r"<pre\b.*?</pre>", re.I | re.S)
RE_TAG = re.compile(r"<[^>]+>")


def _class_count(html, class_name):
    return len(
        re.findall(
            rf'class="[^"]*(?:^|\s){re.escape(class_name)}(?:\s|$)[^"]*"',
            html,
            re.I,
        )
    )


def cjk_count(html):
    stripped = RE_SCRIPT_STYLE.sub("", html)
    stripped = RE_PRE.sub("", stripped)
    text = RE_TAG.sub(" ", stripped)
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def visual_count(html):
    classes = [
        "lesson-map",
        "source-map",
        "call-graph",
        "state-flow",
        "trace-table",
        "svg-diagram",
        "flow",
        "vflow",
        "cols",
    ]
    return sum(_class_count(html, cls) for cls in classes) + len(
        re.findall(r"<table\b", html, re.I)
    )


def check_page(fname, rules):
    path = os.path.join(LESSONS, fname)
    if not os.path.exists(path):
        return [f"{fname}: missing generated lesson file; run python build.py"]

    html = open(path, encoding="utf-8").read()
    errors = []

    cjk = cjk_count(html)
    if cjk < rules["min_cjk"]:
        errors.append(f"{fname}: only {cjk} CJK chars; want >= {rules['min_cjk']}")

    visuals = visual_count(html)
    if visuals < rules["min_visual"]:
        errors.append(f"{fname}: only {visuals} visual/trace/table blocks; want >= {rules['min_visual']}")

    required_classes = {
        "lesson-map": "lesson map",
        "source-map": "source map",
        "trace-table": "worked-example trace table",
        "code-walkthrough": "simplified source/pseudocode walkthrough",
        "pitfall-grid": "common pitfall grid",
        "lab": "exercise/lab card",
    }
    for cls, label in required_classes.items():
        if _class_count(html, cls) == 0:
            errors.append(f"{fname}: missing {label} ({cls})")

    if "文件 + 符号名" not in html and "源码入口" not in html:
        errors.append(f"{fname}: missing source-reference wording")

    if "常见误解" not in html and "边界情况" not in html:
        errors.append(f"{fname}: missing misconception/boundary section")

    return errors


def main():
    errors = []
    for fname, rules in C_LEVEL_PAGES.items():
        errors.extend(check_page(fname, rules))

    if errors:
        print(f"✗ C-level content density check failed: {len(errors)} issue(s)")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"✓ C-level content density passed for {len(C_LEVEL_PAGES)} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify the checker catches the current gap**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/src
python3 check_content_density.py
```

Expected: FAIL with missing-page errors for `04-source-reading-map.html` and `05-learning-path.html`, plus low-density errors for old lessons 01-03.

- [ ] **Step 3: Verify existing checks still pass and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/src
python3 build.py
python3 check_html.py
python3 check_links.py
cd /home/verden/course/langchain-visual-guide
git add src/check_content_density.py
git commit -m "Add C-level content density checker" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

Expected: existing checks exit 0; density checker is not in CI yet.

---

### Task 3: Refactor subtitles and print styling

**Files:**
- Modify: `src/shell.py`
- Modify: `src/build_print.py`

- [ ] **Step 1: Move subtitles to module scope**

Add `SUBTITLES` after `PAGES` in `src/shell.py`:

```python
SUBTITLES = {
    "01-what-is-langchain.html": "LangChain / LangGraph / 生态边界 · 全书路线",
    "02-monorepo.html": "langchain-core / langchain / langgraph / partners",
    "03-lifecycle.html": "从用户代码到 provider API 的完整调用链",
    "04-source-reading-map.html": "读源码先看哪些文件、类、函数和调用方向",
    "05-learning-path.html": "如何按主线学习、调试、做实验和复习",
    "04-messages.html": "Human / AI / Tool / System 消息",
    "05-chat-models.html": "init_chat_model · invoke / stream / batch",
    "06-tools.html": "@tool 装饰器 · 工具调用",
    "07-agents-intro.html": "create_agent · Agent 循环",
    "08-runnable.html": "invoke/stream/batch · LCEL 管道 |",
    "09-runnable-compose.html": "Sequence / Parallel / Branch 组合",
    "10-output-parsers.html": "StrOutputParser · JsonOutputParser · 闭环",
    "11-chat-internals.html": "BaseChatModel 调用链",
    "12-tool-internals.html": "函数 → JSON Schema → tool_calls",
    "13-agent-internals.html": "LangGraph 状态图 · Send/Command · add_messages reducer",
    "14-streaming-callbacks.html": "流式输出与回调追踪",
    "15-contributing.html": "uv · 测试 · 调试 · 贡献",
    "16-prompts.html": "ChatPromptTemplate · MessagesPlaceholder · few-shot",
    "17-rag.html": "Document → 切块 → Embeddings → VectorStore → Retriever",
    "18-custom-middleware.html": "AgentMiddleware 钩子 · before/after/wrap",
    "19-runtime-context.html": "context_schema · with_fallbacks · stream_mode",
    "20-capstone.html": "把所有零件拼成一个完整可跑的 Agent",
    "21-langchain-vs-autogen.html": "两种范式对照：图/管道 vs 多 Agent 对话",
    "22-ai-stack.html": "Agent 编排 5 流派 · AI 全栈 7 层 · 你在哪",
    "23-learning-map.html": "vLLM/llama.cpp/Ollama · hnswlib/pgvector/Qdrant",
    "24-langgraph-mental-model.html": "为什么 LCEL 不够 · State/Node/Edge/compile",
    "25-langgraph-pregel-engine.html": "Pregel/BSP 超步 · Plan→Execution→Update · channels",
    "26-langgraph-persistence-control.html": "Checkpoint/StateSnapshot · interrupt · Send/Command",
    "27-glossary.html": "全书术语一句话查 + 点链接跳到对应课",
}
```

Inside `index_page()`, delete the local `subtitles` dictionary and replace `subtitles.get(fname, "")` with `SUBTITLES.get(fname, "")`.

- [ ] **Step 2: Add print keep-together rules**

In `src/build_print.py`, replace the `break-inside: avoid` selector with:

```css
.card, .codefile, pre.code, table.t, .flow, .vflow .step, .layer,
.accordion, .qa, .cols, .mockup, .lesson-map, .map-node, .svg-diagram,
.pitfall, .trace-table, .source-map { break-inside: avoid; }
```

- [ ] **Step 3: Rebuild, verify, and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/src
python3 build.py
python3 build_print.py
python3 check_html.py
python3 check_links.py
cd /home/verden/course/langchain-visual-guide
git add src/shell.py src/build_print.py index.html lessons
git commit -m "Refactor subtitles and print rules for C-level expansion" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

Expected: all commands exit 0.

---

### Task 4: Rewrite Part 1 as five C-level lessons

**Files:**
- Modify: `src/shell.py`
- Modify: `src/registry.py`
- Create: `src/part01_overview.py`
- Modify: `src/quizzes.py`
- Generated: `index.html`, `lessons/01-what-is-langchain.html`, `lessons/02-monorepo.html`, `lessons/03-lifecycle.html`, `lessons/04-source-reading-map.html`, `lessons/05-learning-path.html`

- [ ] **Step 1: Update `shell.PAGES`**

Replace the first three `PAGES` entries with:

```python
    ("01-what-is-langchain.html", "LangChain 是什么", "第一部分 · 全局地图"),
    ("02-monorepo.html", "项目与包结构", "第一部分 · 全局地图"),
    ("03-lifecycle.html", "一次调用的全链路", "第一部分 · 全局地图"),
    ("04-source-reading-map.html", "源码阅读地图", "第一部分 · 全局地图"),
    ("05-learning-path.html", "学习路径与实验方法", "第一部分 · 全局地图"),
```

Keep existing legacy pages after these entries.

- [ ] **Step 2: Create `part01_overview.py` and write the five lessons**

Create `src/part01_overview.py`:

```python
"""C-level Part 1: global map for the expanded LangChain visual guide."""

import shell
```

Then author five complete constants: `LESSON_01`, `LESSON_02`, `LESSON_03`, `LESSON_04`, and `LESSON_05`. Each constant must be a complete HTML string with a `<p class="lead">` opening paragraph, all required shared components, and the lesson-specific sections from the brief below. Do not commit any lesson that contains only a starter paragraph or skeletal section headings.

Use these exact lesson briefs:

| Lesson | Required content |
| --- | --- |
| 01 LangChain 是什么 | Explain boundaries: LangChain is orchestration, not model/training/inference/vector DB. Include `lesson_map`, `call_graph`, `source_map` rows for `Runnable`, `BaseMessage`, `init_chat_model`, `create_agent`, `StateGraph`; include code walkthrough of model+tool loop; trace order-status example; pitfall grid; lab; version note. |
| 02 项目与包结构 | Explain package split: `langchain-core`, `langchain`, `langgraph`, `community`, `partners`. Include layer diagram, source map for package roots, dependency-direction pseudocode, provider-switch trace, pitfall grid, lab. |
| 03 一次调用的全链路 | Trace `model.invoke("写一句欢迎语")`: input normalization, message conversion, config merge, callbacks, provider payload, response parsing, `AIMessage`. Include state flow, source map for `BaseChatModel.invoke`, `convert_to_messages`, `ensure_config`, callback manager, provider wrapper; include simplified invoke pseudocode and trace table. |
| 04 源码阅读地图 | Teach source-reading route: public API, protocol/base class, concrete implementation, tests/examples. Include source map for `init_chat_model`, `Runnable`, `tool`, `create_agent`, `StateGraph`, `Pregel`; include source-reading algorithm pseudocode, `@tool` trace, pitfall grid, lab. |
| 05 学习路径与实验方法 | Explain how to use the expanded guide: concept, trace, source, experiment, glossary. Include state flow, source map for `GenericFakeChatModel`, `InMemorySaver`, `RunnableConfig`, tracers; include deterministic fake-model experiment, trace table, pitfall grid, lab. |

Each lesson must include all required classes checked by `check_content_density.py`: `lesson-map`, `source-map`, `trace-table`, `code-walkthrough`, `pitfall-grid`, and `lab`. Lessons 01-04 must have at least 4500 CJK chars; lesson 05 must have at least 4200 CJK chars.

- [ ] **Step 3: Update `registry.py`**

Add:

```python
import part01_overview
```

Update the first `CONTENT` mappings:

```python
CONTENT = {
    "01-what-is-langchain.html": part01_overview.LESSON_01,
    "02-monorepo.html": part01_overview.LESSON_02,
    "03-lifecycle.html": part01_overview.LESSON_03,
    "04-source-reading-map.html": part01_overview.LESSON_04,
    "05-learning-path.html": part01_overview.LESSON_05,
    "04-messages.html": part2.LESSON_04,
```

Keep remaining legacy mappings after `04-messages.html`.

- [ ] **Step 4: Update quizzes**

In `src/quizzes.py`, replace entries for `01-what-is-langchain.html`, `02-monorepo.html`, and `03-lifecycle.html`, and add entries for `04-source-reading-map.html` and `05-learning-path.html`.

Each entry must contain 3 `mcq` questions and 2 `open` prompts. Required quiz themes:

| Lesson | Required MCQ themes | Required open prompt themes |
| --- | --- | --- |
| 01 | framework boundary; Runnable as protocol; LangGraph vs LangChain | abstraction tradeoff; layer ownership |
| 02 | core stability; partner-package isolation; dependency direction | package boundary; provider SDK blast radius |
| 03 | message normalization; config propagation; callback lifecycle | trace one invoke; streaming path difference |
| 04 | happy-path source reading; file+symbol citation; tests as examples | build a source map; locate provider differences |
| 05 | concept→trace→source→experiment order; fake components; observing state | safe experiment design; why output-only debugging is weak |

- [ ] **Step 5: Build, verify, and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/src
python3 build.py
python3 build_print.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
cd /home/verden/course/langchain-visual-guide
git add src/shell.py src/registry.py src/part01_overview.py src/quizzes.py index.html lessons
git commit -m "Rewrite Part 1 as C-level overview lessons" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

Expected: all checks exit 0; the site has 29 generated lesson pages in transitional order.

---

### Task 5: Wire C-level checks into CI and stale guards

**Files:**
- Modify: `src/check_html.py`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Add stale-text guards**

Add to `STALE` in `src/check_html.py`:

```python
    "全 27 课",
    "8 部分 · 27 课",
    "第八部分 · 速查",
```

- [ ] **Step 2: Add density checker to CI**

In `.github/workflows/ci.yml`, after “Check HTML structure & consistency”, add:

```yaml
      - name: Check C-level content density
        working-directory: src
        run: python check_content_density.py
```

- [ ] **Step 3: Verify and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/src
python3 build.py
python3 build_print.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
cd /home/verden/course/langchain-visual-guide
git add .github/workflows/ci.yml src/check_html.py index.html lessons
git commit -m "Add C-level density check to CI" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

Expected: all checks exit 0.

---

### Task 6: Update README and roadmap

**Files:**
- Modify: `README.md`
- Create: `docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md`

- [ ] **Step 1: Update README**

Replace the lesson-count badge:

```markdown
![Lessons](https://img.shields.io/badge/lessons-27-blue.svg)
```

with:

```markdown
![Lessons](https://img.shields.io/badge/lessons-expanding_to_45--55-blue.svg)
```

Add this paragraph near the top:

```markdown
> 🚧 **C 级扩充中**：本教程正在从旧版 27 课扩展为约 45-55 课的中文成书级深挖版本。新版本强调更多图、worked-example trace、真实源码入口、简化伪代码和自测练习。第一部分“全局地图”是新标准模板批次，后续部分会按 Part 分批迁移。
```

- [ ] **Step 2: Create roadmap**

Create `docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md`:

```markdown
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
| M9 | Part 9 ecosystem comparison, glossary, print/PDF/README final polish | Not started | Plan pending after M8 review |

## Per-milestone rule

Every future milestone must verify current LangChain/LangGraph source entry points, keep generated HTML in sync with `src/`, pass all Python checks, and run the required two-stage review: spec-compliance review followed by code-quality review.
```

- [ ] **Step 3: Verify and commit**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/src
python3 build.py
python3 build_print.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
cd /home/verden/course/langchain-visual-guide
git add README.md docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-roadmap.md index.html lessons
git commit -m "Document C-level expansion roadmap" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

Expected: all checks exit 0.

---

### Task 7: Run required reviews and final verification

**Files:**
- No planned source edits unless review finds a real issue.

- [ ] **Step 1: Run spec-compliance review subagent**

Dispatch a review subagent with `model: "gpt-5.5"`. Ask it to compare implementation against:

- `docs/superpowers/specs/2026-06-23-langchain-visual-guide-c-expansion-design.md`
- `docs/superpowers/plans/2026-06-23-langchain-visual-guide-c-expansion-m0-m1.md`
- Current branch diff from before M0-M1 work

Expected: reviewer reports whether M0-M1 satisfies the approved spec and this plan.

- [ ] **Step 2: Run code-quality review subagent**

Dispatch a second review subagent with `model: "gpt-5.5"`. Ask it to inspect escaping, helper APIs, generated HTML consistency, checker false-positive risk, CI workflow correctness, and content quality for the five M1 pages.

Expected: reviewer reports only meaningful issues. Fix confirmed issues and avoid style-only churn.

- [ ] **Step 3: Re-run full verification**

Run:

```bash
cd /home/verden/course/langchain-visual-guide/src
python3 build.py
python3 build_print.py
python3 check_html.py
python3 check_links.py
python3 check_content_density.py
cd /home/verden/course/langchain-visual-guide
git --no-pager status --short
git --no-pager log --oneline -5
```

Expected: all checks exit 0; status is clean or only intentional review fixes remain.

- [ ] **Step 4: Commit review fixes if needed**

If review fixes were made:

```bash
cd /home/verden/course/langchain-visual-guide
git add .
git commit -m "Address M0-M1 expansion review findings" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

If no review fixes were needed, do not create an empty commit.

---

## Final handoff

After Task 7 passes, summarize the M0-M1 commits, the five migrated C-level pages, the checks that passed, and the next milestone plan to write: M2 “用户 API 基础”.
