"""Single source of truth: ordered map of output filename -> lesson HTML content.

Both the site build (build.py) and the print/PDF build (build_print.py) import
this so the lesson set stays in sync.
"""
import part01_overview
import part02_user_api
import part03_runnable_lcel
import part2
import part3
import part4
import part5
import part6
import part7
import glossary

# Ordered to match shell.PAGES. Filename -> content HTML string.
CONTENT = {
    "01-what-is-langchain.html": part01_overview.LESSON_01,
    "02-monorepo.html": part01_overview.LESSON_02,
    "03-lifecycle.html": part01_overview.LESSON_03,
    "04-source-reading-map.html": part01_overview.LESSON_04,
    "05-learning-path.html": part01_overview.LESSON_05,
    "04-messages.html": part02_user_api.LESSON_06_MESSAGES,
    "05-chat-models.html": part02_user_api.LESSON_07_CHAT_MODELS,
    "06-tools.html": part02_user_api.LESSON_08_TOOLS,
    "16-prompts.html": part02_user_api.LESSON_09_PROMPTS,
    "10-output-parsers.html": part02_user_api.LESSON_10_OUTPUT_PARSERS,
    "14-streaming-callbacks.html": part02_user_api.LESSON_11_STREAMING,
    "08-runnable.html": part03_runnable_lcel.LESSON_12_RUNNABLE_PROTOCOL,
    "09-runnable-compose.html": part03_runnable_lcel.LESSON_13_LCEL_SEQUENCE,
    "12-runnable-parallel-branch.html": part03_runnable_lcel.LESSON_14_PARALLEL_BRANCH,
    "13-runnable-config-callbacks.html": part03_runnable_lcel.LESSON_15_CONFIG_CALLBACKS,
    "15-runnable-retry-fallback.html": part03_runnable_lcel.LESSON_16_RETRY_FALLBACK,
    "07-agents-intro.html": part2.LESSON_07,
    "11-chat-internals.html": part3.LESSON_10,
    "12-tool-internals.html": part3.LESSON_11,
    "13-agent-internals.html": part3.LESSON_12,
    "15-contributing.html": part4.LESSON_14,
    "17-rag.html": part5.LESSON_16,
    "18-custom-middleware.html": part5.LESSON_17,
    "19-runtime-context.html": part5.LESSON_18,
    "20-capstone.html": part5.LESSON_CAP,
    "21-langchain-vs-autogen.html": part6.LESSON_CMP,
    "22-ai-stack.html": part6.LESSON_STACK,
    "23-learning-map.html": part6.LESSON_LEARN,
    "24-langgraph-mental-model.html": part7.LESSON_LG1,
    "25-langgraph-pregel-engine.html": part7.LESSON_LG2,
    "26-langgraph-persistence-control.html": part7.LESSON_LG3,
    "27-glossary.html": glossary.LESSON_GLOSSARY,
}
