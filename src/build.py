"""Build the LangChain visual guide as a standalone static site.

Layout produced (relative to the project root):

    index.html           entry point (table of contents)
    lessons/NN-*.html    the 14 lesson pages

Pages use relative links so the site works via file:// or any static HTTP
server. Index links to ``lessons/NN-*.html``; lesson pages link to siblings
by bare filename and back home via ``../index.html``.

Usage:
    cd src && python build.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))  # project root
LESSONS_DIR = os.path.join(ROOT, "lessons")
sys.path.insert(0, HERE)

import shell  # noqa: E402

CONTENT = {}


def register(module_name, mapping):
    mod = __import__(module_name)
    for fname, attr in mapping.items():
        CONTENT[fname] = getattr(mod, attr)


def build():
    os.makedirs(LESSONS_DIR, exist_ok=True)
    written = []
    for fname, _title, _part in shell.PAGES:
        html = shell.page(
            fname, CONTENT[fname], standalone=True, home_href="../index.html"
        )
        with open(os.path.join(LESSONS_DIR, fname), "w", encoding="utf-8") as f:
            f.write(html)
        written.append(os.path.join("lessons", fname))
    with open(os.path.join(ROOT, shell.INDEX_FILE), "w", encoding="utf-8") as f:
        f.write(shell.index_page(standalone=True, lesson_prefix="lessons/"))
    written.append(shell.INDEX_FILE)
    return written


if __name__ == "__main__":
    register("part1", {
        "01-what-is-langchain.html": "LESSON_01",
        "02-monorepo.html": "LESSON_02",
        "03-lifecycle.html": "LESSON_03",
    })
    register("part2", {
        "04-messages.html": "LESSON_04",
        "05-chat-models.html": "LESSON_05",
        "06-tools.html": "LESSON_06",
        "07-agents-intro.html": "LESSON_07",
    })
    register("part3", {
        "08-runnable.html": "LESSON_08",
        "09-runnable-compose.html": "LESSON_09",
        "10-chat-internals.html": "LESSON_10",
        "11-tool-internals.html": "LESSON_11",
        "12-agent-internals.html": "LESSON_12",
        "13-streaming-callbacks.html": "LESSON_13",
    })
    register("part4", {
        "14-contributing.html": "LESSON_14",
    })
    register("part5", {
        "15-prompts.html": "LESSON_15",
        "16-rag.html": "LESSON_16",
        "17-custom-middleware.html": "LESSON_17",
        "18-runtime-context.html": "LESSON_18",
    })
    done = build()
    print("Wrote", len(done), "files under", ROOT)
    for f in done:
        print("  -", f)
