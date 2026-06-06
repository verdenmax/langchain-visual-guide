"""Shared HTML shell (CSS design system + navigation) for the LangChain tutorial."""

# Ordered list of all pages: (filename, short title, part label)
PAGES = [
    ("01-what-is-langchain.html", "LangChain 是什么", "第一部分 · 宏观全景"),
    ("02-monorepo.html", "Monorepo 全景", "第一部分 · 宏观全景"),
    ("03-lifecycle.html", "一次调用的生命周期", "第一部分 · 宏观全景"),
    ("04-messages.html", "消息系统", "第二部分 · 用户视角"),
    ("05-chat-models.html", "聊天模型", "第二部分 · 用户视角"),
    ("06-tools.html", "工具 Tools", "第二部分 · 用户视角"),
    ("07-agents-intro.html", "Agent 入门", "第二部分 · 用户视角"),
    ("08-runnable.html", "Runnable 万物之基", "第三部分 · 内部源码"),
    ("09-runnable-compose.html", "Runnable 如何组合", "第三部分 · 内部源码"),
    ("10-output-parsers.html", "输出解析器 Output Parsers", "第三部分 · 内部源码"),
    ("11-chat-internals.html", "聊天模型内部", "第三部分 · 内部源码"),
    ("12-tool-internals.html", "工具调用内部", "第三部分 · 内部源码"),
    ("13-agent-internals.html", "Agent 内部", "第三部分 · 内部源码"),
    ("14-streaming-callbacks.html", "Streaming 与 Callbacks", "第三部分 · 内部源码"),
    ("15-contributing.html", "读源码 / 调试 / 测试 / 贡献", "第四部分 · 进阶"),
    ("16-prompts.html", "提示词 Prompts", "第五部分 · 自己动手做 Agent"),
    ("17-rag.html", "RAG 检索增强", "第五部分 · 自己动手做 Agent"),
    ("18-custom-middleware.html", "写自己的中间件", "第五部分 · 自己动手做 Agent"),
    ("19-runtime-context.html", "运行时上下文与健壮性", "第五部分 · 自己动手做 Agent"),
]

INDEX_FILE = "index.html"

CSS = r"""
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #f6f7f9; --panel: #ffffff; --panel-2: #f0f2f5; --ink: #1d2129;
  --muted: #5b6470; --faint: #8a939f; --line: #e1e5ea;
  --accent: #1a7f64; --accent-soft: #e4f3ee; --accent-ink: #0f5c48;
  --blue: #2563eb; --blue-soft: #e7efff; --amber: #b4690e; --amber-soft: #fdf1dd;
  --purple: #7c3aed; --purple-soft: #f0e9ff; --red: #d23f3f; --red-soft: #fbe6e6;
  --code-bg: #0f172a; --code-ink: #e2e8f0; --code-line: #1e293b;
  --shadow: 0 1px 2px rgba(16,24,40,.06), 0 8px 24px rgba(16,24,40,.06);
  --radius: 14px;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0e1116; --panel: #161b22; --panel-2: #1c232c; --ink: #e6edf3;
    --muted: #9aa6b2; --faint: #6e7a86; --line: #2a323c;
    --accent: #3fb892; --accent-soft: #14302a; --accent-ink: #8ee0c6;
    --blue: #6ea8fe; --blue-soft: #16243f; --amber: #e0a44a; --amber-soft: #33270f;
    --purple: #b794f6; --purple-soft: #271a40; --red: #f08080; --red-soft: #3a1a1a;
    --code-bg: #0a0f1a; --code-ink: #d8e2f0; --code-line: #14202f;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 10px 30px rgba(0,0,0,.35);
  }
}
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC",
    "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  background: var(--bg); color: var(--ink); line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: none; }
code, .mono { font-family: "SF Mono", "JetBrains Mono", "Fira Code", ui-monospace, Menlo, Consolas, monospace; }

/* ---- top progress bar ---- */
.topbar {
  position: sticky; top: 0; z-index: 50; background: var(--panel);
  border-bottom: 1px solid var(--line); backdrop-filter: blur(8px);
}
.topbar-inner {
  max-width: 960px; margin: 0 auto; padding: .7rem 1.25rem;
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
}
.topbar .home { font-size: .82rem; color: var(--muted); font-weight: 600; display:flex; gap:.5rem; align-items:center; }
.topbar .home b { color: var(--accent); }
.topbar .pill { font-size: .72rem; color: var(--muted); background: var(--panel-2);
  padding: .2rem .6rem; border-radius: 999px; border: 1px solid var(--line); white-space: nowrap; }
.progress { height: 3px; background: var(--panel-2); }
.progress > span { display: block; height: 100%; background: linear-gradient(90deg, var(--accent), var(--blue)); }

.wrap { max-width: 820px; margin: 0 auto; padding: 2.4rem 1.25rem 5rem; }

/* ---- hero ---- */
.hero { margin-bottom: 2rem; }
.hero .part { font-size: .76rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--accent); font-weight: 700; margin-bottom: .55rem; }
.hero h1 { font-size: 2.05rem; line-height: 1.2; letter-spacing: -.01em; font-weight: 750; }
.hero .lead { margin-top: .9rem; font-size: 1.06rem; color: var(--muted); }

h2 { font-size: 1.32rem; margin: 2.4rem 0 .9rem; letter-spacing: -.01em;
  display: flex; align-items: center; gap: .55rem; }
h2::before { content: ""; width: 4px; height: 1.05em; background: var(--accent); border-radius: 3px; display: inline-block; }
h3 { font-size: 1.05rem; margin: 1.4rem 0 .5rem; }
p { margin: .7rem 0; }
ul, ol { margin: .6rem 0 .6rem 1.3rem; }
li { margin: .3rem 0; }
strong { color: var(--ink); font-weight: 680; }
.inline { background: var(--panel-2); border: 1px solid var(--line); border-radius: 6px;
  padding: .08em .4em; font-size: .9em; color: var(--accent-ink); }

/* ---- callout cards ---- */
.card { border-radius: var(--radius); padding: 1.05rem 1.2rem; margin: 1.2rem 0;
  border: 1px solid var(--line); background: var(--panel); box-shadow: var(--shadow); }
.card .tag { font-size: .72rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase;
  display: inline-flex; align-items: center; gap: .4rem; margin-bottom: .5rem; }
.card.macro { border-left: 4px solid var(--blue); }
.card.macro .tag { color: var(--blue); }
.card.detail { border-left: 4px solid var(--purple); }
.card.detail .tag { color: var(--purple); }
.card.analogy { border-left: 4px solid var(--amber); background: var(--amber-soft); }
.card.analogy .tag { color: var(--amber); }
.card.key { border-left: 4px solid var(--accent); background: var(--accent-soft); }
.card.key .tag { color: var(--accent-ink); }
.card.warn { border-left: 4px solid var(--red); background: var(--red-soft); }
.card.warn .tag { color: var(--red); }
.card.spark { border-left: 4px solid #e0a000;
  background: linear-gradient(100deg, rgba(224,160,0,.12), transparent 70%); }
.card.spark .tag { color: #c98a00; }
@media (prefers-color-scheme: dark) { .card.spark .tag { color: #f0c050; } }

/* ---- code file callout ---- */
.codefile { margin: 1.2rem 0; border-radius: 12px; overflow: hidden; border: 1px solid var(--line);
  box-shadow: var(--shadow); }
.codefile .cf-head { display: flex; align-items: center; gap: .55rem; padding: .5rem .85rem;
  background: var(--panel-2); border-bottom: 1px solid var(--line); font-size: .8rem; }
.codefile .cf-head .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--accent); flex-shrink:0; }
.codefile .cf-head .path { font-family: ui-monospace, monospace; color: var(--ink); font-weight: 600; }
.codefile .cf-head .ln { margin-left: auto; color: var(--faint); font-size: .72rem; }
.codefile pre { background: var(--code-bg); color: var(--code-ink); padding: .9rem 1rem;
  overflow-x: auto; font-size: .82rem; line-height: 1.6; }
.codefile pre .cm { color: #7d8aa3; }
.codefile pre .kw { color: #c792ea; }
.codefile pre .fn { color: #82aaff; }
.codefile pre .st { color: #c3e88d; }
.codefile pre .nb { color: #f78c6c; }

pre.code { background: var(--code-bg); color: var(--code-ink); padding: .9rem 1rem; border-radius: 12px;
  overflow-x: auto; font-size: .83rem; line-height: 1.6; margin: 1.1rem 0; box-shadow: var(--shadow); }
pre.code .cm { color: #7d8aa3; } pre.code .kw { color: #c792ea; }
pre.code .fn { color: #82aaff; } pre.code .st { color: #c3e88d; } pre.code .nb { color: #f78c6c; }

/* ---- collapsible accordion (details/summary) ---- */
.accordion { border: 1px solid var(--line); border-radius: 12px; background: var(--panel);
  margin: .7rem 0; box-shadow: var(--shadow); overflow: hidden; }
.accordion > summary { cursor: pointer; padding: .85rem 1.1rem; font-weight: 650; font-size: .96rem;
  list-style: none; display: flex; align-items: center; gap: .6rem; user-select: none; }
.accordion > summary::-webkit-details-marker { display: none; }
.accordion > summary::after { content: "▶"; font-size: .68rem; color: var(--accent);
  margin-left: auto; transition: transform .15s ease; }
.accordion[open] > summary::after { transform: rotate(90deg); }
.accordion > summary:hover { background: var(--panel-2); }
.accordion[open] > summary { border-bottom: 1px solid var(--line); }
.accordion .badge-num { background: var(--accent-soft); color: var(--accent-ink);
  width: 1.6rem; height: 1.6rem; border-radius: 7px; display: inline-flex; align-items: center;
  justify-content: center; font-size: .82rem; font-weight: 700; flex-shrink: 0; }
.accordion .hint { font-size: .72rem; color: var(--faint); font-weight: 400; }
.acc-body { padding: .9rem 1.1rem 1.1rem; }
.acc-intro { color: var(--muted); font-size: .9rem; margin: .2rem 0 .4rem; }
.qa { margin: 1rem 0; }
.qa:first-child { margin-top: .3rem; }
.qa .q { font-weight: 680; font-size: .9rem; display: flex; gap: .45rem; align-items: center; margin-bottom: .3rem; }
.qa .a { color: var(--muted); font-size: .9rem; }
.qa .a strong { color: var(--ink); }
.qa pre.code { margin: .5rem 0 0; font-size: .78rem; }

/* ---- flow diagram ---- */
.flow { display: flex; align-items: stretch; gap: 0; flex-wrap: wrap; margin: 1.3rem 0;
  background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 1.2rem 1rem; box-shadow: var(--shadow); }
.flow .node { flex: 1 1 0; min-width: 110px; text-align: center; padding: .7rem .5rem;
  border-radius: 10px; background: var(--panel-2); border: 1px solid var(--line); }
.flow .node .nt { font-weight: 700; font-size: .92rem; }
.flow .node .nd { font-size: .76rem; color: var(--muted); margin-top: .2rem; }
.flow .node.hl { background: var(--accent-soft); border-color: var(--accent); }
.flow .arrow { align-self: center; color: var(--faint); font-size: 1.3rem; padding: 0 .35rem; }

/* vertical flow */
.vflow { margin: 1.3rem 0; }
.vflow .step { display: flex; gap: .9rem; position: relative; padding-bottom: 1.1rem; }
.vflow .step:not(:last-child)::before { content:""; position:absolute; left: 15px; top: 34px; bottom: -2px;
  width: 2px; background: var(--line); }
.vflow .num { width: 32px; height: 32px; border-radius: 50%; background: var(--accent); color: #fff;
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .85rem; flex-shrink: 0; z-index:1; }
.vflow .sc h4 { margin: .25rem 0 .2rem; font-size: 1rem; }
.vflow .sc p { margin: .15rem 0; font-size: .92rem; color: var(--muted); }
.vflow .sc .mono { font-size: .8rem; color: var(--accent-ink); }

/* layered architecture */
.layers { margin: 1.3rem 0; display: flex; flex-direction: column; gap: .55rem; }
.layer { border-radius: 12px; padding: .85rem 1.1rem; border: 1px solid var(--line); background: var(--panel);
  box-shadow: var(--shadow); }
.layer .lh { display: flex; align-items: center; gap: .6rem; }
.layer .lh .badge { font-size: .7rem; font-weight: 700; padding: .12rem .5rem; border-radius: 999px; }
.layer .lh .name { font-weight: 700; font-family: ui-monospace, monospace; }
.layer .ld { font-size: .85rem; color: var(--muted); margin-top: .35rem; }
.layer.l-core { border-left: 4px solid var(--accent); } .layer.l-core .badge { background: var(--accent-soft); color: var(--accent-ink); }
.layer.l-main { border-left: 4px solid var(--blue); } .layer.l-main .badge { background: var(--blue-soft); color: var(--blue); }
.layer.l-part { border-left: 4px solid var(--purple); } .layer.l-part .badge { background: var(--purple-soft); color: var(--purple); }
.layer.l-app { border-left: 4px solid var(--amber); } .layer.l-app .badge { background: var(--amber-soft); color: var(--amber); }

/* two-column compare */
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.2rem 0; }
@media (max-width: 640px) { .cols { grid-template-columns: 1fr; } }
.col { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 1rem 1.1rem; box-shadow: var(--shadow); }
.col h4 { margin: 0 0 .4rem; font-size: .95rem; }

table.t { width: 100%; border-collapse: collapse; margin: 1.1rem 0; font-size: .9rem;
  background: var(--panel); border-radius: 12px; overflow: hidden; box-shadow: var(--shadow); }
table.t th, table.t td { padding: .6rem .8rem; text-align: left; border-bottom: 1px solid var(--line); }
table.t th { background: var(--panel-2); font-size: .8rem; letter-spacing: .02em; }
table.t tr:last-child td { border-bottom: none; }
table.t td.mono, table.t td .mono { font-family: ui-monospace, monospace; font-size: .82rem; color: var(--accent-ink); }

/* footer nav */
.footnav { display: flex; justify-content: space-between; gap: 1rem; margin-top: 3rem;
  padding-top: 1.4rem; border-top: 1px solid var(--line); }
.footnav a { flex: 1; padding: .85rem 1.1rem; border-radius: 12px; border: 1px solid var(--line);
  background: var(--panel); box-shadow: var(--shadow); transition: .15s; }
.footnav a:hover { border-color: var(--accent); transform: translateY(-1px); }
.footnav a.next { text-align: right; }
.footnav .dir { font-size: .72rem; color: var(--faint); text-transform: uppercase; letter-spacing: .05em; }
.footnav .ttl { font-weight: 700; color: var(--ink); margin-top: .15rem; }
.footnav a.disabled { opacity: .35; pointer-events: none; }

/* index page */
.toc { display: grid; gap: .7rem; margin-top: 1.6rem; }
.toc-part { font-size: .78rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  color: var(--accent); margin: 1.4rem 0 .2rem; }
.toc a { display: flex; align-items: center; gap: .9rem; padding: .85rem 1.05rem; border-radius: 12px;
  background: var(--panel); border: 1px solid var(--line); box-shadow: var(--shadow); transition: .15s; }
.toc a:hover { border-color: var(--accent); transform: translateX(3px); }
.toc .n { width: 30px; height: 30px; border-radius: 8px; background: var(--accent-soft); color: var(--accent-ink);
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: .85rem; flex-shrink: 0; }
.toc .tt { font-weight: 650; color: var(--ink); }
.toc .ts { font-size: .8rem; color: var(--muted); margin-left: auto; text-align: right; }
.hero.index h1 { font-size: 2.3rem; }
.legend { display:flex; gap:1.2rem; flex-wrap:wrap; margin-top:1rem; font-size:.8rem; color:var(--muted); }
.legend span { display:flex; align-items:center; gap:.4rem; }
.legend i { width:12px; height:12px; border-radius:3px; display:inline-block; }
"""

NAV_SCRIPT = """
(function(){
  var onDisk = location.protocol === 'file:';
  document.querySelectorAll('[data-nav]').forEach(function(a){
    var n = a.getAttribute('data-nav');
    a.setAttribute('href', onDisk ? n : '/files/' + n);
  });
})();
"""


def page(filename, content, standalone=False, home_href=None):
    """Wrap lesson content in the full HTML shell with nav.

    When ``standalone`` is True, navigation uses plain relative ``href`` links
    (works via file:// and any static server). Otherwise it uses ``data-nav``
    plus a script that targets the brainstorm companion's ``/files/`` route.

    ``home_href`` overrides the link back to the index (use ``"../index.html"``
    when lesson pages live in a subdirectory). Sibling lesson links always use
    bare filenames, so lessons must share one directory.
    """
    idx = next(i for i, p in enumerate(PAGES) if p[0] == filename)
    fname, title, part = PAGES[idx]
    total = len(PAGES)
    pct = int((idx + 1) / total * 100)
    home = home_href or INDEX_FILE

    prev_link = (
        f'<a class="prev" data-nav="{PAGES[idx-1][0]}"><div class="dir">← 上一课</div>'
        f'<div class="ttl">{PAGES[idx-1][1]}</div></a>'
        if idx > 0 else
        f'<a class="prev" data-nav="{home}"><div class="dir">← 返回</div>'
        f'<div class="ttl">目录</div></a>'
    )
    next_link = (
        f'<a class="next" data-nav="{PAGES[idx+1][0]}"><div class="dir">下一课 →</div>'
        f'<div class="ttl">{PAGES[idx+1][1]}</div></a>'
        if idx + 1 < total else
        f'<a class="next" data-nav="{home}"><div class="dir">完成 →</div>'
        f'<div class="ttl">返回目录</div></a>'
    )

    script_tag = "" if standalone else f"<script>{NAV_SCRIPT}</script>"
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{idx+1:02d} · {title} — LangChain 图解教程</title>
<style>{CSS}</style>
</head><body>
<div class="topbar">
  <div class="topbar-inner">
    <a class="home" data-nav="{home}">📘 LangChain 图解教程 · <b>目录</b></a>
    <span class="pill">{part}</span>
    <span class="pill">{idx+1:02d} / {total:02d}</span>
  </div>
  <div class="progress"><span style="width:{pct}%"></span></div>
</div>
<div class="wrap">
  <div class="hero">
    <div class="part">{part}</div>
    <h1>{title}</h1>
  </div>
  {content}
  <div class="footnav">{prev_link}{next_link}</div>
</div>
{script_tag}
</body></html>"""
    if standalone:
        html = html.replace('data-nav="', 'href="')
    return html


def index_page(standalone=False, lesson_prefix=""):
    parts = {}
    order = []
    for i, (fname, title, part) in enumerate(PAGES):
        parts.setdefault(part, [])
        if part not in order:
            order.append(part)
        parts[part].append((i + 1, fname, title))

    blocks = []
    subtitles = {
        "01-what-is-langchain.html": "解决什么问题 · 核心心智模型",
        "02-monorepo.html": "core / langchain / partners 三层",
        "03-lifecycle.html": "从你的代码到 LLM 的完整数据流",
        "04-messages.html": "Human / AI / Tool / System 消息",
        "05-chat-models.html": "init_chat_model · invoke / stream / batch",
        "06-tools.html": "@tool 装饰器 · 工具调用",
        "07-agents-intro.html": "create_agent · Agent 循环",
        "08-runnable.html": "invoke/stream/batch · LCEL 管道 |",
        "09-runnable-compose.html": "Sequence / Parallel / Branch 组合",
        "10-output-parsers.html": "StrOutputParser · JsonOutputParser · 闭环",
        "11-chat-internals.html": "BaseChatModel 调用链",
        "12-tool-internals.html": "函数 → JSON Schema → tool_calls",
        "13-agent-internals.html": "LangGraph 状态图 + middleware",
        "14-streaming-callbacks.html": "流式输出与回调追踪",
        "15-contributing.html": "uv · 测试 · 调试 · 贡献",
        "16-prompts.html": "ChatPromptTemplate · MessagesPlaceholder · few-shot",
        "17-rag.html": "Document → 切块 → Embeddings → VectorStore → Retriever",
        "18-custom-middleware.html": "AgentMiddleware 钩子 · before/after/wrap",
        "19-runtime-context.html": "context_schema · with_fallbacks · stream_mode",
    }
    for part in order:
        blocks.append(f'<div class="toc-part">{part}</div>')
        for num, fname, title in parts[part]:
            sub = subtitles.get(fname, "")
            blocks.append(
                f'<a data-nav="{lesson_prefix}{fname}"><span class="n">{num:02d}</span>'
                f'<span class="tt">{title}</span>'
                f'<span class="ts">{sub}</span></a>'
            )
    toc = "\n".join(blocks)

    script_tag = "" if standalone else f"<script>{NAV_SCRIPT}</script>"
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LangChain 图解教程 · 从零理解整个项目</title>
<style>{CSS}</style>
</head><body>
<div class="topbar">
  <div class="topbar-inner">
    <span class="home">📘 LangChain 图解教程</span>
    <span class="pill">共 {len(PAGES)} 课 · 4 个部分</span>
  </div>
  <div class="progress"><span style="width:100%"></span></div>
</div>
<div class="wrap">
  <div class="hero index">
    <div class="part">从零开始 · 面向完全新手</div>
    <h1>用图解理解整个 LangChain 项目</h1>
    <p class="lead">这套教程分四步带你走：先建立<strong>宏观全景</strong>，再从<strong>用户视角</strong>学会使用，
    然后深入<strong>内部源码</strong>看它如何实现，最后教你<strong>读源码与贡献</strong>。
    每一课都配有真实的代码文件对应，既有宏观理解，也有细节拆解。</p>
    <div class="legend">
      <span><i style="background:var(--blue)"></i>宏观理解</span>
      <span><i style="background:var(--purple)"></i>细节 / 源码</span>
      <span><i style="background:var(--amber)"></i>生活类比</span>
      <span><i style="background:var(--accent)"></i>关键要点</span>
    </div>
  </div>
  <div class="toc">{toc}</div>
</div>
{script_tag}
</body></html>"""
    if standalone:
        html = html.replace('data-nav="', 'href="')
    return html
