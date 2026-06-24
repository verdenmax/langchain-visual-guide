"""Single source of truth: ordered map of output filename -> lesson HTML content.

Both the site build (build.py) and the print/PDF build (build_print.py) import
this so the lesson set stays in sync.
"""
import part01_overview
import part02_user_api
import part03_runnable_lcel
import part04_langgraph_model
import part05_langgraph_engine
import part06_agent_internals
import part07_rag_memory
import part08_engineering
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
    "24-langgraph-mental-model.html": part04_langgraph_model.LESSON_17_GRAPH_WHY,
    "28-langgraph-state-schema.html": part04_langgraph_model.LESSON_18_STATE_SCHEMA,
    "29-langgraph-nodes-edges.html": part04_langgraph_model.LESSON_19_NODES_EDGES,
    "30-langgraph-reducers-channels.html": part04_langgraph_model.LESSON_20_REDUCERS_CHANNELS,
    "31-langgraph-compile-runtime.html": part04_langgraph_model.LESSON_21_COMPILE_RUNTIME,
    "25-langgraph-pregel-engine.html": part05_langgraph_engine.LESSON_22_PREGEL,
    "32-langgraph-tasks-channels.html": part05_langgraph_engine.LESSON_23_TASKS_CHANNELS,
    "26-langgraph-persistence-control.html": part05_langgraph_engine.LESSON_24_CHECKPOINTS,
    "33-langgraph-interrupt-command.html": part05_langgraph_engine.LESSON_25_INTERRUPT_COMMAND,
    "34-langgraph-time-travel-debug.html": part05_langgraph_engine.LESSON_26_TIME_TRAVEL,
    "07-agents-intro.html": part06_agent_internals.LESSON_27_AGENT_LOOP,
    "13-agent-internals.html": part06_agent_internals.LESSON_28_CREATE_AGENT,
    "18-custom-middleware.html": part06_agent_internals.LESSON_29_MIDDLEWARE,
    "19-runtime-context.html": part06_agent_internals.LESSON_30_RUNTIME_CONTEXT,
    "35-agent-control-errors.html": part06_agent_internals.LESSON_31_CONTROL_ERRORS,
    "17-rag.html": part07_rag_memory.LESSON_32_RAG_FLOW,
    "36-documents-splitters.html": part07_rag_memory.LESSON_33_DOCUMENTS_SPLITTERS,
    "37-embeddings-vectorstores.html": part07_rag_memory.LESSON_34_EMBEDDINGS_VECTORSTORES,
    "38-retrievers-rerankers.html": part07_rag_memory.LESSON_35_RETRIEVERS_RERANKERS,
    "39-memory-conversation-state.html": part07_rag_memory.LESSON_36_MEMORY_STATE,
    "15-contributing.html": part08_engineering.LESSON_37_LOCAL_DEV,
    "40-testing-debugging.html": part08_engineering.LESSON_38_TESTING_DEBUGGING,
    "41-observability-ci.html": part08_engineering.LESSON_39_OBSERVABILITY_CI,
    "20-capstone.html": part08_engineering.LESSON_40_CAPSTONE,
    "11-chat-internals.html": part3.LESSON_10,
    "12-tool-internals.html": part3.LESSON_11,
    "21-langchain-vs-autogen.html": part6.LESSON_CMP,
    "22-ai-stack.html": part6.LESSON_STACK,
    "23-learning-map.html": part6.LESSON_LEARN,
    "27-glossary.html": glossary.LESSON_GLOSSARY,
}
