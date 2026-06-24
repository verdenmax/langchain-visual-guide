"""Content for the glossary / concept index page (lesson 27, Part 8 速查).

A flat, searchable reference: every key term across the 26 lessons gets a
one-line definition plus a link to the lesson where it's taught — doubling as a
"where is X explained?" concept index.
"""

LESSON_GLOSSARY = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
全教程术语很多。这一页把它们<strong>一网打尽</strong>：每个术语<strong>一句话</strong>说清，并<strong>点一下就跳到</strong>讲它的那一课。
它也是<strong>"概念索引"</strong>——忘了某个东西在哪讲，从这里查最快。
</p>

<div class="card detail">
  <div class="tag">🔎 用法</div>
  想找某个词？用浏览器的 <strong>Ctrl/⌘ + F</strong> 在本页内搜索；点"<strong>见课</strong>"列的链接直接跳到对应课。
  术语按 <strong>① LangChain 核心 → ② LangGraph 引擎 → ③ 生态与全栈</strong> 分三组。
</div>

<h2>① LangChain 核心</h2>
<table class="t">
  <tr><th>术语</th><th>一句话</th><th>见课</th></tr>
  <tr><td class="mono">Runnable</td><td>统一接口（invoke/stream/batch），LangChain 万物之基</td><td><a href="08-runnable.html">Runnable 协议</a></td></tr>
  <tr><td class="mono">LCEL（| 管道）</td><td>用 <span class="mono">|</span> 把多个 Runnable 串成一条链</td><td><a href="09-runnable-compose.html">LCEL 管道与 Sequence</a></td></tr>
  <tr><td class="mono">invoke / stream / batch</td><td>一问一答 / 流式 / 批量，三种调用方式（含异步 a*）</td><td><a href="05-chat-models.html">聊天模型</a></td></tr>
  <tr><td class="mono">init_chat_model</td><td>一行代码拿到任意厂商的聊天模型</td><td><a href="05-chat-models.html">聊天模型</a></td></tr>
  <tr><td class="mono">BaseChatModel</td><td>所有聊天模型的基类，定义调用链</td><td><a href="11-chat-internals.html">聊天模型内部</a></td></tr>
  <tr><td class="mono">Message（Human/AI/Tool/System）</td><td>四种标准消息类型</td><td><a href="04-messages.html">消息系统</a></td></tr>
  <tr><td class="mono">AIMessage.tool_calls</td><td>模型输出里"想调用的工具"——Agent 循环的引擎</td><td><a href="04-messages.html">消息系统</a> · <a href="06-tools.html">工具 Tools</a></td></tr>
  <tr><td class="mono">ToolMessage</td><td>工具执行结果，靠 <span class="mono">tool_call_id</span> 与请求配对</td><td><a href="06-tools.html">工具 Tools</a></td></tr>
  <tr><td class="mono">@tool</td><td>把普通函数变成工具（自动生成 schema）</td><td><a href="06-tools.html">工具 Tools</a> · <a href="12-tool-internals.html">工具调用内部</a></td></tr>
  <tr><td class="mono">bind_tools</td><td>告诉模型"你有哪些工具可用"</td><td><a href="06-tools.html">工具 Tools</a></td></tr>
  <tr><td class="mono">create_agent</td><td>一行造 Agent——内部编译成一张 LangGraph 状态图</td><td><a href="07-agents-intro.html">Agent 入门</a> · <a href="13-agent-internals.html">Agent 内部</a></td></tr>
  <tr><td class="mono">middleware / AgentMiddleware</td><td>Agent 的扩展点：在循环关键处插钩子</td><td><a href="18-custom-middleware.html">写自己的中间件</a></td></tr>
  <tr><td>七个钩子（before_model / wrap_model_call …）</td><td>中间件可覆盖的生命周期钩子</td><td><a href="18-custom-middleware.html">写自己的中间件</a></td></tr>
  <tr><td class="mono">Output Parser</td><td>把模型的文本输出解析成结构化数据</td><td><a href="10-output-parsers.html">输出解析器 Output Parsers</a></td></tr>
  <tr><td>结构化输出（with_structured_output）</td><td>强制模型直接吐出符合 schema 的对象</td><td><a href="06-tools.html">工具 Tools</a></td></tr>
  <tr><td class="mono">ChatPromptTemplate / MessagesPlaceholder</td><td>提示词模板与"历史插槽"</td><td><a href="16-prompts.html">提示词 Prompts</a></td></tr>
  <tr><td class="mono">RAG</td><td>检索增强生成：先查知识、再让模型作答</td><td><a href="17-rag.html">RAG 检索增强</a></td></tr>
  <tr><td class="mono">Document / VectorStore / Retriever / Embeddings</td><td>RAG 的四个核心零件</td><td><a href="17-rag.html">RAG 检索增强</a></td></tr>
  <tr><td class="mono">Runtime / context_schema</td><td>运行时上下文：把 user_id / db 等注入节点</td><td><a href="19-runtime-context.html">运行时上下文与健壮性</a></td></tr>
  <tr><td class="mono">with_retry / with_fallbacks</td><td>调用级重试 / 主模型失败切备用</td><td><a href="19-runtime-context.html">运行时上下文与健壮性</a></td></tr>
  <tr><td class="mono">Callbacks / BaseCallbackHandler</td><td>在生命周期关键点挂钩子（追踪、日志）</td><td><a href="14-streaming-callbacks.html">Streaming 与 Callbacks</a></td></tr>
  <tr><td class="mono">Run / run 树 / LangSmith</td><td>一次执行的记录树，上报 LangSmith 可视化</td><td><a href="14-streaming-callbacks.html">Streaming 与 Callbacks</a></td></tr>
  <tr><td class="mono">streaming / stream_mode</td><td>边生成边返回；updates/values/messages 几种模式</td><td><a href="14-streaming-callbacks.html">Streaming 与 Callbacks</a> · <a href="19-runtime-context.html">运行时上下文与健壮性</a></td></tr>
</table>

<h2>② LangGraph 引擎</h2>
<table class="t">
  <tr><th>术语</th><th>一句话</th><th>见课</th></tr>
  <tr><td class="mono">LangGraph</td><td>独立的"有状态图"编排引擎，create_agent 建在它上</td><td><a href="24-langgraph-mental-model.html">为什么需要 LangGraph</a></td></tr>
  <tr><td class="mono">StateGraph / CompiledStateGraph</td><td>状态图的建造者 / 编译产物（是 Runnable，继承 Pregel）</td><td><a href="24-langgraph-mental-model.html">为什么需要 LangGraph</a></td></tr>
  <tr><td>State / Node / Edge</td><td>共享状态 / 节点（<span class="mono">state→部分 state</span>）/ 边</td><td><a href="24-langgraph-mental-model.html">为什么需要 LangGraph</a></td></tr>
  <tr><td class="mono">条件边（add_conditional_edges）</td><td>按路由函数动态选下一个节点</td><td><a href="13-agent-internals.html">Agent 内部</a> · <a href="24-langgraph-mental-model.html">为什么需要 LangGraph</a></td></tr>
  <tr><td class="mono">reducer / add_messages</td><td>状态某键的"合并函数"；add_messages 按 id 追加消息</td><td><a href="13-agent-internals.html">Agent 内部</a> · <a href="25-langgraph-pregel-engine.html">执行引擎：Pregel 与超步</a></td></tr>
  <tr><td class="mono">Pregel / 超步 / BSP</td><td>执行引擎：actors+channels，分超步 Plan→Execution→Update</td><td><a href="25-langgraph-pregel-engine.html">执行引擎：Pregel 与超步</a></td></tr>
  <tr><td class="mono">channel（LastValue/Topic/Aggregate）</td><td>状态的底层通道；reducer 就是它的更新函数</td><td><a href="25-langgraph-pregel-engine.html">执行引擎：Pregel 与超步</a></td></tr>
  <tr><td class="mono">checkpointer / Checkpoint / thread_id</td><td>每超步存档，按 thread_id 区分会话、可续跑</td><td><a href="13-agent-internals.html">Agent 内部</a> · <a href="26-langgraph-persistence-control.html">持久化 · 中断 · 控制流</a></td></tr>
  <tr><td class="mono">StateSnapshot / 时间旅行</td><td>某步的状态快照；可回到历史 checkpoint 重跑</td><td><a href="26-langgraph-persistence-control.html">持久化 · 中断 · 控制流</a></td></tr>
  <tr><td class="mono">interrupt / 人在回路（HITL）</td><td>在节点里暂停等人，Command(resume) 恢复</td><td><a href="07-agents-intro.html">Agent 入门</a> · <a href="26-langgraph-persistence-control.html">持久化 · 中断 · 控制流</a></td></tr>
  <tr><td class="mono">Send</td><td>动态扇出：把多个任务并行投给同一节点（并行工具）</td><td><a href="26-langgraph-persistence-control.html">持久化 · 中断 · 控制流</a></td></tr>
  <tr><td class="mono">Command</td><td>改状态 + 跳转（goto）；多 Agent handoff 的底座</td><td><a href="26-langgraph-persistence-control.html">持久化 · 中断 · 控制流</a></td></tr>
  <tr><td class="mono">recursion_limit</td><td>图执行步数的硬上限（防失控的兜底）</td><td><a href="07-agents-intro.html">Agent 入门</a> · <a href="25-langgraph-pregel-engine.html">执行引擎：Pregel 与超步</a></td></tr>
</table>

<h2>③ 生态与全栈</h2>
<table class="t">
  <tr><th>术语</th><th>一句话</th><th>见课</th></tr>
  <tr><td class="mono">AutoGen</td><td>微软的多 Agent 对话框架（与 LangChain 对照）</td><td><a href="21-langchain-vs-autogen.html">横向对比：LangChain vs AutoGen</a></td></tr>
  <tr><td class="mono">handoff（交接）</td><td>一个 Agent 把任务交棒给另一个</td><td><a href="21-langchain-vs-autogen.html">横向对比：LangChain vs AutoGen</a> · <a href="26-langgraph-persistence-control.html">持久化 · 中断 · 控制流</a></td></tr>
  <tr><td class="mono">MCP</td><td>Model Context Protocol（Anthropic）：标准化"Agent↔工具"</td><td><a href="22-ai-stack.html">全栈坐标系：从 LangChain 缩放到整个生态</a></td></tr>
  <tr><td class="mono">A2A</td><td>Agent2Agent（Google）：标准化"Agent↔Agent"</td><td><a href="22-ai-stack.html">全栈坐标系：从 LangChain 缩放到整个生态</a></td></tr>
  <tr><td>AI 全栈 7 层</td><td>硬件→基础设施→训练→模型→推理→检索→编排+应用</td><td><a href="22-ai-stack.html">全栈坐标系：从 LangChain 缩放到整个生态</a></td></tr>
  <tr><td class="mono">vLLM / PagedAttention</td><td>主流推理引擎 / 它的核心显存分页技术（L5）</td><td><a href="23-learning-map.html">隔壁层学习地图：L5 推理 · L6 向量检索</a></td></tr>
  <tr><td class="mono">continuous batching / 量化</td><td>推理提速的两大手段（吞吐 / 省显存）</td><td><a href="23-learning-map.html">隔壁层学习地图：L5 推理 · L6 向量检索</a></td></tr>
  <tr><td class="mono">HNSW / ANN</td><td>向量检索的近似最近邻算法（L6 底座）</td><td><a href="23-learning-map.html">隔壁层学习地图：L5 推理 · L6 向量检索</a></td></tr>
  <tr><td class="mono">嵌入 / BGE</td><td>把文本变向量；BGE 是中文友好的开源嵌入模型</td><td><a href="23-learning-map.html">隔壁层学习地图：L5 推理 · L6 向量检索</a></td></tr>
</table>

<div class="card key">
  <div class="tag">✅ 怎么用好这页</div>
  <ul>
    <li><strong>查词</strong>：忘了术语含义 → Ctrl/⌘ + F 搜本页，一行看懂。</li>
    <li><strong>跳课</strong>：想看细节 → 点"见课"链接直达讲解。</li>
    <li><strong>复习</strong>：通读三张表，就是一份全书<strong>概念地图</strong>。</li>
    <li>🎉 至此，从"LangChain 一个点"到"整个 AI 生态 + LangGraph 引擎"，你已经走完全程。</li>
  </ul>
</div>
"""
