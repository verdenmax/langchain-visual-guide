"""Structural / consistency regression guard for the generated HTML.

Run after ``build.py``::

    cd src && python check_html.py

Exits non-zero if any ERROR-level issue is found (used by CI). WARN/INFO are
printed but do not fail the build. Checks performed on every lesson + index:

* balanced tags (div / details / table / pre / summary) and details<->summary
* exactly one <h1>, a <title>, and a meta description
* no unescaped '<' inside <pre> code blocks (would eat content)
* no out-of-range "第 N 课" cross-references
* nav prev/next chain matches shell.PAGES order
* no stale counts / wording (e.g. "全 20 课", "六个钩子")
* index TOC lists every page and shows the correct lesson/part counts
* every CSS class used in a page body has a rule in shell.CSS (guards silent
  style fallbacks, e.g. ``card keypoints`` when only ``.card.key`` is defined)
* (WARN only) every lesson has a "本课要点" and a "card analogy"
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import shell  # noqa: E402

PAGES = shell.PAGES
ORDER = [p[0] for p in PAGES]
TOTAL = len(PAGES)

# Substrings that must never appear in any generated HTML (stale counts/wording).
STALE = [
    "全 20 课", "全 23 课", "全 27 课", "共 20 课", "5 部分 20 课",
    "8 部分 · 27 课", "六个钩子", "第六部分 · 横向对比",
    "第八部分 · 速查",
]

# Inline tags allowed (unescaped) inside <pre> code blocks.
PRE_INLINE = ("span", "strong", "b", "em", "u", "a")

# Reference pages exempt from the "needs analogy / 本课要点" soft checks.
SOFT_EXEMPT = {"27-glossary.html"}

# CSS class names that have a rule in shell.CSS (e.g. ".foo", ".a.b"). The regex
# only matches a dot followed by a letter, so numeric fragments (".5rem", ".06")
# and pseudo-elements (no dot) are ignored.
DEFINED_CSS_CLASSES = set(re.findall(r"\.([A-Za-z][\w-]*)", shell.CSS))

# Classes intentionally used in HTML without their own CSS rule, because the
# element also carries a fully-styled base class (semantic markers) or the class
# is purely a JS/data hook. Add here ONLY with a clear reason — this whitelist is
# what lets the "undefined CSS class" guard catch real fallback bugs (a card
# variant that was never styled) while allowing deliberate markers.
ALLOWED_UNDEFINED_CLASSES = {
    "call-graph",  # always on a ".flow" element; semantic marker for density check
    "state-flow",  # always on a ".vflow" element; semantic marker
    "prev",        # footnav back-link; styled by ".footnav a" (only ".next" overrides)
}

issues = []  # (severity, file, message)


def add(sev, f, msg):
    issues.append((sev, f, msg))


def check_balance(name, html, tag):
    o = len(re.findall(rf"<{tag}[\s>]", html))
    c = len(re.findall(rf"</{tag}>", html))
    if o != c:
        add("ERR", name, f"<{tag}> unbalanced: {o} open / {c} close")


def check_stale(name, html):
    for bad in STALE:
        if bad in html:
            add("ERR", name, f"stale text: {bad!r}")


def check_classes(name, html):
    """Flag any class used in the page body that has no rule in shell.CSS.

    Guards against silent style fallbacks (e.g. ``card keypoints`` when only
    ``.card.key`` is defined). Only the body is scanned (the inlined <style> is
    skipped). Deliberate markers / JS hooks belong in ALLOWED_UNDEFINED_CLASSES.
    """
    body = html.split("</style>", 1)[-1]
    attrs = re.findall(r'class="([^"]*)"', body) + re.findall(r"class='([^']*)'", body)
    seen = set()
    for attr in attrs:
        for cls in attr.split():
            if cls in seen or cls in DEFINED_CSS_CLASSES or cls in ALLOWED_UNDEFINED_CLASSES:
                continue
            seen.add(cls)
            add("ERR", name, f"undefined CSS class .{cls} (used in HTML but no rule in "
                             "shell.CSS; add a rule or whitelist it in ALLOWED_UNDEFINED_CLASSES)")


def check_lesson(fname, html):
    for tag in ("div", "details", "table", "pre", "summary"):
        check_balance(fname, html, tag)
    nd = len(re.findall(r"<details", html))
    ns = len(re.findall(r"<summary", html))
    if nd != ns:
        add("ERR", fname, f"details({nd}) != summary({ns})")
    h1 = len(re.findall(r"<h1", html))
    if h1 != 1:
        add("WARN", fname, f"{h1} <h1> (expected 1)")
    if "<title>" not in html:
        add("ERR", fname, "missing <title>")
    if 'name="description"' not in html:
        add("ERR", fname, "missing meta description")
    if fname not in SOFT_EXEMPT:
        if "本课要点" not in html and "全书结业" not in html:
            add("WARN", fname, "no 本课要点 card")
        if "card analogy" not in html:
            add("WARN", fname, "no analogy card")

    check_stale(fname, html)
    check_classes(fname, html)

    # unescaped '<' inside <pre>
    for pre in re.findall(r"<pre[^>]*>(.*?)</pre>", html, re.S):
        cleaned = re.sub(r"</?(?:%s)\b[^>]*>" % "|".join(PRE_INLINE), "", pre)
        if re.search(r"<(?!/)", cleaned):
            m = re.search(r"<(?!/).{0,20}", cleaned)
            add("ERR", fname, f"unescaped '<' in <pre>: {m.group(0)!r}")
            break

    # out-of-range course references
    for m in re.finditer(r"第\s*([0-9、,，~\-－\s]+?)\s*课", html):
        nums = [int(x) for x in re.findall(r"[0-9]+", m.group(1))]
        over = [n for n in nums if n == 0 or n > TOTAL]
        if over:
            add("ERR", fname, f"course ref out of range: {m.group(0)!r} -> {over}")

    # nav chain
    if fname in ORDER:
        idx = ORDER.index(fname)
        if idx + 1 < TOTAL and f'href="{ORDER[idx + 1]}"' not in html:
            add("ERR", fname, f"next link missing -> {ORDER[idx + 1]}")
        if idx > 0 and f'href="{ORDER[idx - 1]}"' not in html:
            add("ERR", fname, f"prev link missing -> {ORDER[idx - 1]}")


def main():
    for fname, _title, _part in PAGES:
        path = os.path.join(ROOT, "lessons", fname)
        if not os.path.exists(path):
            add("ERR", fname, "lesson file missing (run build.py)")
            continue
        check_lesson(fname, open(path, encoding="utf-8").read())

    index_path = os.path.join(ROOT, shell.INDEX_FILE)
    idx = open(index_path, encoding="utf-8").read()
    check_stale("index.html", idx)
    check_classes("index.html", idx)
    for fname, title, _part in PAGES:
        if fname not in idx:
            add("ERR", "index.html", f"TOC missing entry {fname}")
        if title not in idx:
            add("WARN", "index.html", f"TOC missing title {title!r}")
    m = re.search(r"共 (\d+) 课 · (\d+) 个部分", idx)
    if m:
        if int(m.group(1)) != TOTAL:
            add("ERR", "index.html", f"count says {m.group(1)} 课 but PAGES has {TOTAL}")
        nparts = len({p[2] for p in PAGES})
        if int(m.group(2)) != nparts:
            add("ERR", "index.html", f"count says {m.group(2)} 部分 but PAGES has {nparts}")
    else:
        add("WARN", "index.html", "could not find '共 N 课 · N 个部分' pill")

    errs = [i for i in issues if i[0] == "ERR"]
    warns = [i for i in issues if i[0] == "WARN"]
    order = {"ERR": 0, "WARN": 1, "INFO": 2}
    for sev, f, msg in sorted(issues, key=lambda x: order[x[0]]):
        print(f"  [{sev}] {f}: {msg}")
    print(f"\nChecked {TOTAL} lessons + index — {len(errs)} error(s), {len(warns)} warning(s).")
    if errs:
        print("✗ structural check FAILED")
        return 1
    print("✓ structural check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
