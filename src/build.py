"""Build the LangChain visual guide as a standalone static site.

Generates all 14 lesson pages plus index.html into the project root,
using plain relative links so the pages work via file:// or any static
HTTP server (no companion required).

Usage:
    cd src && python build.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, ".."))  # project root
sys.path.insert(0, HERE)

import shell  # noqa: E402

CONTENT = {}


def register(module_name, mapping):
    mod = __import__(module_name)
    for fname, attr in mapping.items():
        CONTENT[fname] = getattr(mod, attr)


def build():
    written = []
    for fname, _title, _part in shell.PAGES:
        html = shell.page(fname, CONTENT[fname], standalone=True)
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write(html)
        written.append(fname)
    with open(os.path.join(OUT, shell.INDEX_FILE), "w", encoding="utf-8") as f:
        f.write(shell.index_page(standalone=True))
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
    done = build()
    print("Wrote", len(done), "files to", OUT)
    for f in done:
        print("  -", f)
