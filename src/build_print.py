"""Build a single print-ready HTML (all 20 lessons, accordions expanded).

Output: ``print.html`` at the project root. Render it to PDF with headless
Chromium, e.g.:

    chromium --headless=new --no-sandbox --no-pdf-header-footer \
        --print-to-pdf=langchain-visual-guide.pdf \
        --virtual-time-budget=15000 file://$PWD/print.html

This module has no third-party dependencies.
"""
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import shell  # noqa: E402
from registry import CONTENT  # noqa: E402
import quizzes  # noqa: E402

PRINT_CSS = r"""
/* ===== print / PDF overrides ===== */
@page { size: A4; margin: 15mm 14mm 16mm; }
html, body { height: auto !important; overflow: visible !important; background: #fff; }
.wrap { max-width: 100%; padding: 0; }
.hint { display: none !important; }
.accordion > summary { cursor: default; }
.accordion > summary::after { display: none; }
.accordion[open] > summary { border-bottom: 1px solid var(--line); }
/* keep blocks from splitting awkwardly across pages */
.card, .codefile, pre.code, table.t, .flow, .vflow .step, .layer,
.accordion, .qa, .cols, .mockup { break-inside: avoid; }
h2, h3, h4 { break-after: avoid; }

.print-cover { break-after: page; min-height: 90vh; display: flex; flex-direction: column;
  justify-content: center; text-align: center; }
.print-cover .emoji { font-size: 3.2rem; }
.print-cover h1 { font-size: 2.4rem; margin: 1rem 0 .4rem; border: none; }
.print-cover .sub { color: var(--muted); font-size: 1.05rem; }
.print-cover .meta { margin-top: 2rem; color: var(--faint); font-size: .9rem; }

.print-toc { break-after: page; }
.print-toc h2 { margin-top: 0; }
.print-toc .tp { font-size: .82rem; font-weight: 700; letter-spacing: .05em;
  color: var(--accent); margin: 1.1rem 0 .3rem; }
.print-toc ol { margin: 0; padding-left: 1.4rem; }
.print-toc li { margin: .2rem 0; }

.print-lesson { break-before: page; padding-top: .2rem; }
.lesson-head { border-bottom: 2px solid var(--accent); padding-bottom: .5rem; margin-bottom: 1.2rem; }
.lesson-head .lp { font-size: .72rem; letter-spacing: .08em; text-transform: uppercase;
  color: var(--accent); font-weight: 700; }
.lesson-head h1 { font-size: 1.7rem; margin: .25rem 0 0; border: none; }
.lesson-head .ln { color: var(--faint); font-weight: 600; }
"""


def _toc_html():
    parts, order = {}, []
    for i, (fname, title, part) in enumerate(shell.PAGES):
        parts.setdefault(part, [])
        if part not in order:
            order.append(part)
        parts[part].append((i + 1, title))
    blocks = ['<h2>目录</h2>']
    for part in order:
        blocks.append(f'<div class="tp">{part}</div>')
        blocks.append('<ol>')
        for num, title in parts[part]:
            blocks.append(f'<li value="{num}">{title}</li>')
        blocks.append('</ol>')
    return "\n".join(blocks)


def build_print():
    today = datetime.date.today().isoformat()
    lessons = []
    for idx, (fname, title, part) in enumerate(shell.PAGES):
        content = (CONTENT[fname] + quizzes.render(fname)).replace(
            '<details class="accordion">', '<details class="accordion" open>'
        )
        lessons.append(
            f'<section class="print-lesson"><div class="wrap">'
            f'<div class="lesson-head"><div class="lp">{part}</div>'
            f'<h1><span class="ln">{idx+1:02d} ·</span> {title}</h1></div>'
            f'{content}</div></section>'
        )
    body = "\n".join(lessons)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<title>LangChain 图解教程</title>
<style>{shell.CSS}{PRINT_CSS}</style>
</head><body>
<section class="print-cover">
  <div class="emoji">📘</div>
  <h1>LangChain 图解教程</h1>
  <div class="sub">从零理解整个项目 · 宏观 → 用法 → 源码 → 自己动手做 Agent</div>
  <div class="meta">共 {len(shell.PAGES)} 课 · {len({p[2] for p in shell.PAGES})} 个部分 · 每课配真实代码对应与设计亮点<br>
    生成日期 {today} · MIT License</div>
</section>
<section class="print-toc"><div class="wrap">{_toc_html()}</div></section>
{body}
</body></html>"""

    out = os.path.join(ROOT, "print.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


if __name__ == "__main__":
    path = build_print()
    print("Wrote", path, f"({len(shell.PAGES)} lessons, accordions expanded)")
