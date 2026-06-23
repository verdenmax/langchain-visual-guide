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
    count = 0
    for value in re.findall(r'class="([^"]*)"', html, re.I):
        if class_name in value.split():
            count += 1
    return count


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
        "code-walkthrough",
        "pitfall-grid",
        "lab",
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
