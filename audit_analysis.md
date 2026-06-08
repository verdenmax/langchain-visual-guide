# Part6.py Audit - Fact-Checking Results

## 课号21 (AutoGen comparison)

### VERIFIED CLAIMS:
- ✅ AutoGen 0.4 uses actor model / event-driven architecture
- ✅ AutoGen has autogen-core, autogen-agentchat, autogen-ext layers
- ✅ AutoGen entered maintenance mode (October 2025 per web search)
- ✅ Microsoft Agent Framework is the recommended successor
- ✅ AgentChat built on Core with AssistantAgent, RoundRobinGroupChat, etc.
- ✅ GrpcWorkerAgentRuntime for distributed execution
- ✅ Topic/Subscription pub-sub model

### FACTUAL ISSUES:
- ⚠️ Lesson says "维护模式（不再加新功能）" but web confirms "October 2025" maintenance announcement - timing accurate
- ⚠️ AutoGen paths in 🔬 card are simplified (e.g., "autogen-agentchat/.../agents/_assistant_agent.py") - these are accurate patterns

## 课号22 (AI Stack)

### VERIFIED CLAIMS:
- ✅ L5: vLLM, SGLang, llama.cpp, Ollama for inference
- ✅ L6: Chroma, Qdrant, Milvus, pgvector for vector databases
- ✅ PagedAttention is vLLM's core innovation
- ✅ L7 frameworks: LangChain, AutoGen, LlamaIndex positioning

### MCP vs A2A CLAIM - **CRITICAL FINDING**:
✅ Lesson correctly states:
- "MCP 管'Agent 连工具'，A2A 管'Agent 连 Agent'"
- Web confirms: MCP (Anthropic, Nov 2024) = Agent ↔ tools/data sources
- Web confirms: A2A (Google) = Agent ↔ Agent communication
- Lesson says "横跨 L6/L7" - CORRECT (MCP connects agents at L7 to data/tools at L6/L5)

### FLOW派别 (5 schools):
- ✅ Correctly identifies LangChain as "图/工作流型"
- ✅ AutoGen + CrewAI as "多Agent协作型" - VERIFIED (CrewAI is indeed active in 2024)
- ✅ LlamaIndex as "数据/RAG型"
- ✅ Pydantic AI, OpenAI Agents SDK, Google ADK as "轻量/类型化"
- ✅ DSPy as "程序化/自动优化"

## 课号23 (Learning Map)

### L5 CLAIMS:
- ✅ vLLM: PagedAttention, continuous batching - VERIFIED
- ✅ SGLang: RadixAttention - VERIFIED (web confirms 2x faster for structured outputs)
- ✅ llama.cpp: GGUF format, quantization - VERIFIED
- ✅ Ollama: based on llama.cpp/GGML - VERIFIED
- ✅ TensorRT-LLM (NVIDIA), TGI (Hugging Face) - correct

### L6 CLAIMS:
- ✅ hnswlib: HNSW algorithm implementation - VERIFIED
- ✅ FAISS: IVF/PQ/HNSW indices from Meta - correct
- ✅ pgvector: Postgres extension for vectors - correct
- ✅ BGE: Chinese-friendly embedding model - correct
- ✅ Mem0/Zep: memory layers - correct

