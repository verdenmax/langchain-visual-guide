"""C-level lesson content-density checks.

Only pages listed in C_LEVEL_PAGES are checked so the guide can migrate
Part-by-Part. Migrated pages must meet the new standard; legacy pages are
ignored until their Part is rewritten.
"""

import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
LESSONS = os.path.join(ROOT, "lessons")

from registry import CONTENT

C_LEVEL_PAGES = {
    "01-what-is-langchain.html": {"min_cjk": 4500, "min_visual": 5},
    "02-monorepo.html": {"min_cjk": 4500, "min_visual": 5},
    "03-lifecycle.html": {"min_cjk": 4500, "min_visual": 5},
    "04-source-reading-map.html": {"min_cjk": 4500, "min_visual": 5},
    "05-learning-path.html": {"min_cjk": 4200, "min_visual": 4},
    "04-messages.html": {"min_cjk": 4500, "min_visual": 5},
    "05-chat-models.html": {"min_cjk": 4500, "min_visual": 5},
    "06-tools.html": {"min_cjk": 4500, "min_visual": 5},
    "16-prompts.html": {"min_cjk": 4500, "min_visual": 5},
    "10-output-parsers.html": {"min_cjk": 4500, "min_visual": 5},
    "14-streaming-callbacks.html": {"min_cjk": 4500, "min_visual": 5},
    "08-runnable.html": {"min_cjk": 4500, "min_visual": 5},
    "09-runnable-compose.html": {"min_cjk": 4500, "min_visual": 5},
    "12-runnable-parallel-branch.html": {"min_cjk": 4500, "min_visual": 5},
    "13-runnable-config-callbacks.html": {"min_cjk": 4500, "min_visual": 5},
    "15-runnable-retry-fallback.html": {"min_cjk": 4500, "min_visual": 5},
}

RE_SCRIPT_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.I | re.S)
RE_PRE = re.compile(r"<pre\b.*?</pre>", re.I | re.S)
RE_TAG = re.compile(r"<[^>]+>")

SEMANTIC_VISUAL_CLASSES = {
    "lesson-map",
    "source-map",
    "call-graph",
    "state-flow",
    "trace-table",
    "svg-diagram",
    "code-walkthrough",
    "pitfall-grid",
    "lab",
}

GENERIC_VISUAL_WRAPPER_CLASSES = {
    # Legacy/current lessons count these generic layout helpers as standalone
    # visual blocks. C-level authors should not wrap semantic C-level
    # components (lesson-map, source-map, etc.) inside counted generic wrappers;
    # use non-counted markup or a dedicated semantic component when layout is
    # needed around semantic visuals.
    "flow",
    "vflow",
    "cols",
}

COUNTED_VISUAL_CLASSES = SEMANTIC_VISUAL_CLASSES | GENERIC_VISUAL_WRAPPER_CLASSES

VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class _DensityHTMLParser(HTMLParser):
    """Count top-level visual blocks in raw lesson body HTML.

    Any element with a counted visual class, including generic wrappers
    ``flow``, ``vflow``, and ``cols``, counts as one standalone visual block in
    legacy/current components. Once a visual block is counted, descendants are
    suppressed to avoid double counting nested semantic components or tables.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.class_counts = Counter()
        self.visual_blocks = 0
        self._open_tags = []
        self._visual_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        classes = _classes_from_attrs(attrs)
        self.class_counts.update(classes)

        has_counted_class = bool(classes & COUNTED_VISUAL_CLASSES)
        is_plain_table = tag == "table" and not has_counted_class
        is_counted_visual = has_counted_class or is_plain_table

        if is_counted_visual and self._visual_depth == 0:
            self.visual_blocks += 1

        if tag not in VOID_TAGS:
            if is_counted_visual:
                self._visual_depth += 1
            self._open_tags.append(
                {
                    "tag": tag,
                    "is_counted_visual": is_counted_visual,
                }
            )

    def handle_endtag(self, tag):
        tag = tag.lower()
        matching_index = next(
            (
                index
                for index in range(len(self._open_tags) - 1, -1, -1)
                if self._open_tags[index]["tag"] == tag
            ),
            None,
        )
        if matching_index is None:
            return

        while len(self._open_tags) > matching_index:
            open_tag = self._open_tags.pop()
            if open_tag["is_counted_visual"]:
                self._visual_depth -= 1


def _classes_from_attrs(attrs):
    classes = set()
    for name, value in attrs:
        if name.lower() == "class" and value:
            classes.update(value.split())
    return classes


def _parse_density(html):
    parser = _DensityHTMLParser()
    parser.feed(html)
    parser.close()
    return parser


def _class_count(html, class_name):
    return _parse_density(html).class_counts[class_name]


def cjk_count(html):
    stripped = RE_SCRIPT_STYLE.sub("", html)
    stripped = RE_PRE.sub("", stripped)
    text = RE_TAG.sub(" ", stripped)
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def visual_count(html):
    return _parse_density(html).visual_blocks


def check_page(fname, rules):
    path = os.path.join(LESSONS, fname)
    if not os.path.exists(path):
        return [f"{fname}: missing generated lesson file; run python build.py"]

    html = CONTENT.get(fname)
    if html is None:
        return [f"{fname}: missing raw lesson body in registry.CONTENT"]

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
