"""Content for Part 6 (appendix / 番外篇):
- lesson 21 — LangChain vs AutoGen (横向对比)
- lesson 22 — AI 全栈坐标系 (Agent 编排层细分 + 7 层全栈图)
- lesson 23 — 隔壁层学习地图 (L5 推理服务 + L6 向量检索)
"""

LESSON_CMP = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
学完 LangChain，跳出来看看<strong>另一条技术路线</strong>——微软的 <strong>AutoGen</strong>。
对照才能真正看清 LangChain 的设计取舍：两者解决的是同一类问题，路径却截然不同。
</p>

<div class="card macro">
  <div class="tag">ℹ️ 先说现状</div>
  AutoGen <strong>自 2025 年起</strong>进入<strong>维护模式</strong>（不再加新功能），微软推荐新项目用其继任者
  <strong>Microsoft Agent Framework</strong>。但 AutoGen 的<strong>设计思想</strong>非常有代表性，
  作为"另一种范式"来对照学习，价值依旧很高。
</div>

<div class="card analogy">
  <div class="tag">🏗️ 一句话类比</div>
  如果说 <strong>LangChain</strong> 像<strong>"搭流水线 + 配一个会用工具的工人"</strong>（数据顺着管道流，路线你定）；
  那么 <strong>AutoGen</strong> 更像<strong>"召集一屋子专家开会"</strong>——多个智能体<strong>互相对话</strong>，
  谁先发言、何时结束由"会议规则"决定。
</div>

<h2>先认识 AutoGen 的分层</h2>
<p>和 LangChain 一样，AutoGen 也是 monorepo 分层，但层次的<strong>重心不同</strong>：</p>
<div class="layers">
  <div class="layer l-part">
    <div class="lh"><span class="badge">高层</span><span class="name">autogen-agentchat</span></div>
    <div class="ld">面向用户的<strong>对话智能体与团队</strong>：<span class="mono">AssistantAgent</span>、
      <span class="mono">RoundRobinGroupChat</span>/<span class="mono">SelectorGroupChat</span>/<span class="mono">Swarm</span>、终止条件。</div>
  </div>
  <div class="layer l-main">
    <div class="lh"><span class="badge">集成</span><span class="name">autogen-ext</span></div>
    <div class="ld">模型客户端（<span class="mono">OpenAIChatCompletionClient</span>）、工具、代码执行器、
      <strong>分布式运行时</strong>（<span class="mono">GrpcWorkerAgentRuntime</span>）。</div>
  </div>
  <div class="layer l-core">
    <div class="lh"><span class="badge">内核</span><span class="name">autogen-core</span></div>
    <div class="ld"><strong>事件驱动的 actor 运行时</strong>：<span class="mono">Agent</span>（含 <span class="mono">on_message</span>）、
      <span class="mono">@message_handler</span> 路由、<strong>Topic/Subscription 发布订阅</strong>、可跨语言（.NET）。</div>
  </div>
</div>

<h2>核心心智模型：管道/图 vs actor/对话</h2>
<p>这是两者<strong>最根本</strong>的差异——记住这一条，其它差异都能推导出来：</p>
<div class="cols">
  <div class="col">
    <h4>🟢 LangChain：可组合的"图"</h4>
    <p>一切是 <span class="mono">Runnable</span>，用 <span class="mono">|</span> 组装管道；Agent 是一张
      <strong>LangGraph 状态图</strong>（节点 + 条件边）。数据<strong>顺着你定义的路线</strong>流动——<strong>确定、可控</strong>。</p>
  </div>
  <div class="col">
    <h4>🟣 AutoGen：自治的"actor"</h4>
    <p>每个 Agent 是一个<strong>自治 actor</strong>，通过<strong>消息</strong>互相沟通；运行时按
      <strong>发布订阅</strong>投递消息。多个 Agent <strong>对话协作</strong>，行为更<strong>自治、涌现</strong>。</p>
  </div>
</div>

<h2>同一件事，两种写法</h2>

<h3>① 一个会用工具的 Agent</h3>
<div class="split">
  <div class="mockup">
    <div class="mockup-header">LangChain</div>
    <div class="mockup-body">
<pre class="code"><span class="kw">from</span> langchain.agents <span class="kw">import</span> create_agent

agent = create_agent(<span class="st">"openai:gpt-5.1"</span>, tools=[get_weather])
agent.invoke({<span class="st">"messages"</span>: [{<span class="st">"role"</span>:<span class="st">"user"</span>,
              <span class="st">"content"</span>:<span class="st">"北京天气？"</span>}]})</pre>
    </div>
  </div>
  <div class="mockup">
    <div class="mockup-header">AutoGen</div>
    <div class="mockup-body">
<pre class="code"><span class="kw">from</span> autogen_agentchat.agents <span class="kw">import</span> AssistantAgent
<span class="kw">from</span> autogen_ext.models.openai <span class="kw">import</span> OpenAIChatCompletionClient

mc = OpenAIChatCompletionClient(model=<span class="st">"gpt-5.1"</span>)
agent = AssistantAgent(<span class="st">"assistant"</span>, model_client=mc, tools=[get_weather])
<span class="kw">await</span> agent.run(task=<span class="st">"北京天气？"</span>)   <span class="cm"># 注意：异步</span></pre>
    </div>
  </div>
</div>
<p style="font-size:.9rem;color:var(--muted)">单 Agent 两者都很简洁。差别在<strong>异步</strong>（AutoGen 全异步）与<strong>模型客户端</strong>显式程度。</p>

<h3>② 多个 Agent 协作（这才是分水岭）</h3>
<div class="split">
  <div class="mockup">
    <div class="mockup-header">LangChain（LangGraph 手搭）</div>
    <div class="mockup-body">
<pre class="code"><span class="cm"># 多 Agent 要自己用 LangGraph 编排：</span>
<span class="cm"># 定义各 Agent 节点、handoff 边、共享状态、</span>
<span class="cm"># 路由谁下一个发言…… 可控但偏手动。</span>
graph = StateGraph(...)
graph.add_node(<span class="st">"writer"</span>, ...)
graph.add_node(<span class="st">"critic"</span>, ...)
graph.add_conditional_edges(...)   <span class="cm"># 自定义路由</span></pre>
    </div>
  </div>
  <div class="mockup">
    <div class="mockup-header">AutoGen（一等公民）</div>
    <div class="mockup-body">
<pre class="code"><span class="kw">from</span> autogen_agentchat.teams <span class="kw">import</span> RoundRobinGroupChat
<span class="kw">from</span> autogen_agentchat.conditions <span class="kw">import</span> MaxMessageTermination

writer = AssistantAgent(<span class="st">"writer"</span>, model_client=mc, system_message=<span class="st">"负责写"</span>)
critic = AssistantAgent(<span class="st">"critic"</span>, model_client=mc, system_message=<span class="st">"负责评审"</span>)
team = RoundRobinGroupChat([writer, critic],
        termination_condition=MaxMessageTermination(6))
<span class="kw">await</span> team.run(task=<span class="st">"写一首关于秋天的诗"</span>)   <span class="cm"># 几行就组好一支队伍</span></pre>
    </div>
  </div>
</div>
<p style="font-size:.9rem;color:var(--muted)"><strong>这就是 AutoGen 的主场</strong>：多 Agent 团队是内置抽象，
还能换 <span class="mono">SelectorGroupChat</span>（让 LLM 选下一个发言人）、<span class="mono">Swarm</span>（基于 handoff）、
<span class="mono">MagenticOneGroupChat</span> 等编排策略。</p>

<h2>逐维度对比</h2>
<table class="t">
  <tr><th>维度</th><th>🟢 LangChain</th><th>🟣 AutoGen</th></tr>
  <tr><td>核心抽象</td><td>Runnable（可组合）+ LangGraph 状态图</td><td>Agent actor + 消息传递 + 发布订阅</td></tr>
  <tr><td>主单元</td><td>链 / 单个工具 Agent</td><td>多个 Agent 的<strong>对话</strong></td></tr>
  <tr><td>多智能体</td><td>靠 LangGraph 搭图 / handoff（偏手动）</td><td><strong>一等公民</strong>：Team（GroupChat）</td></tr>
  <tr><td>编排方式</td><td>LCEL 管道、图节点/边、middleware</td><td>团队 + 发言人选择 + 终止条件（可组合 &/|）</td></tr>
  <tr><td>执行模型</td><td><span class="mono">invoke/stream</span> 跑一张图</td><td>事件驱动<strong>异步 actor</strong>，可<strong>分布式(gRPC)</strong>、<strong>跨语言(.NET)</strong></td></tr>
  <tr><td>集成生态</td><td><strong>巨大</strong>（partners、向量库、RAG…）</td><td>模型客户端 + 工具 + 代码执行（生态较小）</td></tr>
  <tr><td>状态 / 记忆</td><td>消息列表 + checkpointer</td><td>model_context / memory / 团队 state 存取</td></tr>
  <tr><td>语言支持</td><td>Python + JavaScript</td><td>Python + .NET</td></tr>
  <tr><td>现状</td><td>活跃，v1</td><td>维护模式 → Microsoft Agent Framework</td></tr>
</table>

<h2>优缺点</h2>
<div class="cols">
  <div class="col">
    <h4>🟢 LangChain</h4>
    <div class="pros-cons">
      <div class="pros"><h4>优点</h4><ul>
        <li>生态/集成<strong>最大</strong>，RAG/数据原语丰富</li>
        <li>统一 <span class="mono">Runnable</span> 抽象，组合力强</li>
        <li>LangGraph 提供<strong>可控、有状态</strong>的工作流</li>
        <li>流式、追踪（LangSmith）成熟</li>
      </ul></div>
      <div class="cons"><h4>缺点</h4><ul>
        <li>抽象多，上手概念负担重</li>
        <li>多 Agent 需自己搭图，较手动</li>
        <li>体系庞大，"小事也要懂不少"</li>
      </ul></div>
    </div>
  </div>
  <div class="col">
    <h4>🟣 AutoGen</h4>
    <div class="pros-cons">
      <div class="pros"><h4>优点</h4><ul>
        <li>多 Agent 对话<strong>一等公民</strong>，组队几行搞定</li>
        <li>干净的 <strong>actor 模型</strong> + 发言人选择策略</li>
        <li><strong>分布式 / 跨语言</strong>运行时</li>
        <li>适合智能体协作 / 研究 / 快速原型</li>
      </ul></div>
      <div class="cons"><h4>缺点</h4><ul>
        <li>已进入<strong>维护模式</strong>（迁移风险）</li>
        <li>集成生态较小，RAG/数据工具少</li>
        <li>对话式编排<strong>可控性/可预测性</strong>偏弱</li>
        <li>事件驱动 actor 有学习曲线</li>
      </ul></div>
    </div>
  </div>
</div>

<h2>互相可以学什么</h2>
<div class="cols">
  <div class="col">
    <h4>LangChain ← 向 AutoGen 学</h4>
    <ul>
      <li>把<strong>"多 Agent 团队"做成更高层的一等抽象</strong>（RoundRobin/Selector/Swarm 那种几行组队的体验），而不必每次手搭 LangGraph。</li>
      <li><strong>发言人选择</strong>与<strong>对话式编排</strong>的现成模式。</li>
      <li><strong>分布式 / 跨语言</strong> actor 运行时的设计。</li>
    </ul>
  </div>
  <div class="col">
    <h4>AutoGen ← 向 LangChain 学</h4>
    <ul>
      <li>更丰富的<strong>集成生态</strong>与 <strong>RAG/数据</strong>原语。</li>
      <li>统一<strong>可组合抽象</strong>（Runnable / LCEL）带来的复用性。</li>
      <li>用<strong>显式状态图</strong>（LangGraph）换取更强的<strong>可控性与可预测性</strong>。</li>
      <li>长期<strong>稳定性与版本治理</strong>。</li>
    </ul>
  </div>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点：两种哲学，没有银弹</div>
  <ul>
    <li><strong>LangChain = "数据流/图"优先</strong>：确定、可控、可组合，集成生态最大——适合 <strong>RAG、工作流、可控的工具 Agent</strong>。</li>
    <li><strong>AutoGen = "对话/actor"优先</strong>：自治、涌现、组队快——适合<strong>多 Agent 协作与研究</strong>（其能力现由 Microsoft Agent Framework 延续）。</li>
    <li><strong>边界在模糊</strong>：LangChain 用 LangGraph 也能做多 Agent（子图/handoff），AutoGen 也能跑单 Agent；差别在<strong>"默认重心"</strong>，而非能不能。</li>
  </ul>
</div>

<div class="card detail">
  <div class="tag">🔬 代码对应（AutoGen 侧，便于你去读源码）</div>
  <table class="t" style="margin-top:.6rem">
    <tr><th>概念</th><th>位置（autogen 仓库）</th></tr>
    <tr><td class="mono">Agent / on_message</td><td class="mono">autogen-core/.../_agent.py</td></tr>
    <tr><td class="mono">@message_handler / RoutedAgent</td><td class="mono">autogen-core/.../_routed_agent.py</td></tr>
    <tr><td class="mono">Topic / Subscription（发布订阅）</td><td class="mono">autogen-core/.../_subscription.py</td></tr>
    <tr><td class="mono">AssistantAgent</td><td class="mono">autogen-agentchat/.../agents/_assistant_agent.py</td></tr>
    <tr><td class="mono">RoundRobin/Selector/Swarm</td><td class="mono">autogen-agentchat/.../teams/_group_chat/</td></tr>
    <tr><td class="mono">OpenAIChatCompletionClient</td><td class="mono">autogen-ext/.../models/openai/_openai_client.py</td></tr>
    <tr><td class="mono">GrpcWorkerAgentRuntime（分布式）</td><td class="mono">autogen-ext/.../runtimes/grpc/</td></tr>
  </table>
</div>

<h2>怎么选：三步决策</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>先看任务形态</h4>
    <p>是<strong>一条可控的流水线 / 工作流</strong>（含 RAG、审批、确定路线）？还是<strong>多个角色自由协作</strong>（头脑风暴、辩论、研究）？</p>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>再看你最在意什么</h4>
    <p>要<strong>可控、可预测、大集成生态、长期稳定</strong> → 倾向 LangChain；要<strong>多 Agent 组队快、行为涌现</strong> → 倾向 AutoGen 系。</p>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>给结论</h4>
    <p><strong>RAG / 可控工具 Agent / 工作流</strong> → <span class="mono">LangChain + LangGraph</span>；
      <strong>多 Agent 协作 / 研究原型</strong> → <span class="mono">AutoGen</span>（新项目用继任者 <span class="mono">Microsoft Agent Framework</span>）。</p>
    <p class="mono">边界模糊时：LangGraph 也能做多 Agent，按"默认重心"选即可。</p>
  </div></div>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>根本差异：<strong>LangChain = 可组合的图（数据流优先）</strong>；<strong>AutoGen = 自治 actor 的对话（多 Agent 优先）</strong>。</li>
    <li>单 Agent 两者都简洁；<strong>多 Agent 协作是 AutoGen 的主场</strong>（Team 一等公民），LangChain 则靠 LangGraph 手搭、换取可控性。</li>
    <li>选型：要<strong>RAG/可控工作流/大集成</strong>→ LangChain；要<strong>快速多 Agent 协作/研究</strong>→ AutoGen（或其继任 Agent Framework）。</li>
    <li>互相借鉴：LangChain 可学"团队一等抽象"，AutoGen 可学"集成生态 + 显式可控 + 稳定性"。</li>
    <li>🎉 看懂一个框架的最好方式，就是<strong>把它和另一个对照</strong>——你现在两种范式都有了坐标。<strong>下一课</strong>再把镜头拉远，看看这两个框架在<strong>整个 AI 全栈</strong>里站在哪一层。</li>
  </ul>
</div>
"""


LESSON_STACK = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
你已经把 <strong>LangChain 这"一个点"</strong>学透了。现在把镜头一路<strong>拉远</strong>——
先看它在"Agent 编排层"里的<strong>邻居</strong>，再看<strong>整个 AI 全栈 7 层</strong>，
最后回答一个最实用的问题：<strong>你，到底站在坐标系的哪里？</strong>
</p>

<div class="card analogy">
  <div class="tag">🗺️ 一句话类比：地图缩放</div>
  学一个框架就像盯着一条街看。本课做三次<strong>缩放（Zoom out）</strong>：
  <strong>某条街</strong>（LangChain）→ <strong>整个城区</strong>（Agent 编排层的几大流派）→
  <strong>整张城市地图</strong>（AI 全栈 7 层）。看清坐标，你就再也不会把一个名词"放错层"。
</div>

<div class="card warn">
  <div class="tag">⚠️ 先纠正一个常见误解</div>
  很多人以为 <strong>LangChain / AutoGen 是"最底层的框架"</strong>。<strong>不是。</strong>
  它们同处<strong>很上面的一层</strong>——<strong>Agent 编排 / 应用框架层（L7）</strong>。
  下面还压着模型、推理、训练、芯片好几层。看完这张图你就有体感了。
</div>

<h2>🔍 缩放 ①：Agent 编排层，内部还分 5 大流派</h2>
<p>LangChain 和 AutoGen 不是"上下级"，而是<strong>同一层的邻居</strong>。这一层（把模型变成"会用工具、能干活的 Agent"）内部，按<strong>"默认重心"</strong>大致分成 5 种流派：</p>

<table class="t">
  <tr><th>流派</th><th>核心心智</th><th>代表项目</th><th>什么时候选它</th></tr>
  <tr>
    <td><strong>① 图 / 工作流型</strong></td>
    <td>你画一张<strong>状态图</strong>，数据顺着你定的路线流——确定、可控</td>
    <td class="mono">LangChain + LangGraph</td>
    <td>RAG、可控工作流、带审批的工具 Agent</td>
  </tr>
  <tr>
    <td><strong>② 多 Agent 协作型</strong></td>
    <td>多个 Agent <strong>分工 / 对话</strong>协作，行为更自治、涌现</td>
    <td class="mono">AutoGen · CrewAI</td>
    <td>多角色协作、头脑风暴、研究类任务</td>
  </tr>
  <tr>
    <td><strong>③ 数据 / RAG 型</strong></td>
    <td>以<strong>"喂数据 / 建索引 / 查询"</strong>为一等公民</td>
    <td class="mono">LlamaIndex · Haystack</td>
    <td>重知识库、文档问答、企业检索</td>
  </tr>
  <tr>
    <td><strong>④ 轻量 / 类型化</strong></td>
    <td><strong>薄封装</strong>，贴近原生 API，靠类型系统约束</td>
    <td class="mono">Pydantic AI · OpenAI Agents SDK · Google ADK · Semantic Kernel*</td>
    <td>想要"少魔法、可控、好调试"的小而稳</td>
  </tr>
  <tr>
    <td><strong>⑤ 程序化 / 自动优化</strong></td>
    <td>把"写提示词"变成<strong>"编译 + 自动优化"</strong></td>
    <td class="mono">DSPy</td>
    <td>想让提示词/流程被数据自动调优，而非手写</td>
  </tr>
</table>
<p style="color:var(--faint);font-size:.8rem;margin-top:-.6rem">* Semantic Kernel（微软）偏<strong>企业级编排</strong>，比同组其他几个"重"一些；归到这里是因为它同样强调<strong>强类型 + 贴近原生 SDK</strong>。</p>

<div class="card detail">
  <div class="tag">🔬 别把"流派"当"壁垒"</div>
  这些边界是<strong>"默认重心"而非"能不能"</strong>：LangChain 用 LangGraph 也能做多 Agent；
  AutoGen 也能跑单 Agent；大家都能接 <strong>MCP</strong> 工具、都能做 RAG。
  它们也都<strong>建在更底层的东西之上</strong>（模型 SDK、协议、推理服务）——这正是下一次缩放要看的。
</div>

<h2>🔍 缩放 ②：整个 AI 全栈，7 层 + 1 条横切带</h2>
<p>把镜头拉到最远。从你点的"调用一次模型"往下追，会一路穿过 7 层。
<strong>越上层越接近用户，越下层越接近硅片</strong>：</p>

<div class="layers">
  <div class="layer l-app">
    <div class="lh"><span class="badge">L7</span><span class="name">编排 + 应用</span><span style="margin-left:auto;font-size:.78rem;font-weight:700;color:var(--accent-ink)">📍 你在这里</span></div>
    <div class="ld">把模型变成<strong>会用工具、能干活的产品</strong>。<span class="mono">LangChain/LangGraph · AutoGen · LlamaIndex</span>；低代码 <span class="mono">Dify/Coze</span>；以及各种最终 App。</div>
  </div>
  <div class="layer l-main">
    <div class="lh"><span class="badge">L6</span><span class="name">检索 / 记忆</span></div>
    <div class="ld">给模型补<strong>外部知识与长期记忆</strong>（RAG 的底座）。向量库 <span class="mono">Chroma/Qdrant/Milvus/pgvector</span>；嵌入 <span class="mono">BGE</span>；记忆 <span class="mono">Mem0/Zep</span>。</div>
  </div>
  <div class="layer l-main">
    <div class="lh"><span class="badge">L5</span><span class="name">推理 / 服务</span></div>
    <div class="ld">让训练好的模型<strong>高效跑起来、对外提供 API</strong>。<span class="mono">vLLM · SGLang · TensorRT-LLM · llama.cpp · Ollama</span>。</div>
  </div>
  <div class="layer l-part">
    <div class="lh"><span class="badge">L4</span><span class="name">模型（权重）</span></div>
    <div class="ld"><strong>智能本身</strong>。闭源 <span class="mono">GPT · Claude · Gemini</span>；开源 <span class="mono">Llama · Qwen · DeepSeek · Mistral</span>。</div>
  </div>
  <div class="layer l-part">
    <div class="lh"><span class="badge">L3</span><span class="name">训练 / 微调</span></div>
    <div class="ld">把<strong>数据 + 算力炼成模型</strong>。<span class="mono">Megatron-LM · DeepSpeed · FSDP</span>；微调 <span class="mono">LoRA/PEFT · TRL</span>。</div>
  </div>
  <div class="layer l-core">
    <div class="lh"><span class="badge">L2</span><span class="name">基础设施 / 算力框架</span></div>
    <div class="ld">把<strong>硬件变成可编程算力</strong>。<span class="mono">CUDA · PyTorch · JAX · Triton · Ray · Kubernetes</span>。</div>
  </div>
  <div class="layer l-core">
    <div class="lh"><span class="badge">L1</span><span class="name">硬件 / 芯片</span></div>
    <div class="ld"><strong>算力地基</strong>。<span class="mono">NVIDIA GPU(H100) · Google TPU · 华为昇腾 · AMD · 推理芯片 Groq</span>。</div>
  </div>
</div>
<p style="text-align:center;color:var(--faint);font-size:.82rem;margin-top:-.5rem">↑ 越上层越接近用户　·　越下层越接近硅片 ↓</p>

<table class="t">
  <tr><th>层</th><th>一句话作用</th><th>代表项目</th></tr>
  <tr><td><strong>L7 编排 + 应用</strong></td><td>把模型变成会用工具、能干活的产品</td><td class="mono">LangChain/LangGraph · AutoGen · LlamaIndex · Dify/Coze</td></tr>
  <tr><td><strong>L6 检索 / 记忆</strong></td><td>给模型补外部知识与记忆（RAG 底座）</td><td class="mono">向量库 Chroma/Qdrant/Milvus/pgvector · 嵌入 BGE · 记忆 Mem0/Zep</td></tr>
  <tr><td><strong>L5 推理 / 服务</strong></td><td>让模型高效跑起来、对外提供 API</td><td class="mono">vLLM · SGLang · TensorRT-LLM · llama.cpp · Ollama</td></tr>
  <tr><td><strong>L4 模型</strong></td><td>智能本身（一堆权重）</td><td class="mono">GPT/Claude/Gemini · Llama/Qwen/DeepSeek</td></tr>
  <tr><td><strong>L3 训练 / 微调</strong></td><td>把数据 + 算力炼成模型</td><td class="mono">Megatron-LM · DeepSpeed · LoRA/PEFT · TRL</td></tr>
  <tr><td><strong>L2 基础设施</strong></td><td>把硬件变成可编程算力</td><td class="mono">CUDA · PyTorch · JAX · Ray · K8s</td></tr>
  <tr><td><strong>L1 硬件</strong></td><td>算力地基</td><td class="mono">NVIDIA GPU · TPU · 昇腾 · AMD</td></tr>
  <tr><td><strong>┄ 横切带 ┄</strong><br><span style="color:var(--muted);font-weight:400">贯穿 L4–L7</span></td><td>评测 / 可观测 / 安全护栏</td><td class="mono">LangSmith · Langfuse · Ragas · Guardrails · OpenTelemetry</td></tr>
</table>

<div class="card spark">
  <div class="tag">💡 设计亮点：两条河 + 一个残酷事实</div>
  <ul>
    <li><strong>两条河</strong>：L1→L4 是<strong>"训练侧"</strong>（少数大厂把模型炼出来），L4→L7 是<strong>"应用侧"</strong>（所有人用模型造东西）。<strong>L4 模型是两条河的交汇口。</strong></li>
    <li><strong>残酷但解放人的事实</strong>：99% 的应用开发者，<strong>一辈子只在 L4 以上工作</strong>——你不需要自己训模型。但<strong>懂下面几层</strong>能帮你做对选型：为什么慢（L5）、为什么答不准（L6）、本地还是 API（L4/L5）。</li>
    <li><strong>没有银弹，只有坐标</strong>：每个火爆的新名词，先问一句"它在第几层？"——你就不会被营销词淹没。</li>
  </ul>
</div>

<div class="card detail">
  <div class="tag">🔬 顺手澄清两个被叫混的协议</div>
  <ul>
    <li><span class="mono">MCP</span> = <strong>Model Context Protocol</strong>（Anthropic，2024 年 11 月开源）：标准化"Agent ↔ 工具/数据源"的接法，横跨 L6/L7。<strong>不是</strong>"多 Agent 通信协议"。</li>
    <li><span class="mono">A2A</span> = <strong>Agent2Agent</strong>（Google，2025 年提出）：标准化"Agent ↔ Agent"的协作。</li>
    <li>一句话记：<strong>MCP 管"Agent 连工具"，A2A 管"Agent 连 Agent"。</strong></li>
  </ul>
</div>

<h2>🔍 缩放 ③：所以，你站在哪里？</h2>
<p>把这张图当"问诊表"。下面三个最实用的问题，帮你<strong>定位自己、定位瓶颈、定位下一步</strong>：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>我该自己训模型吗？</h4>
    <p><strong>基本不用。</strong>L3/L4 交给大厂（成本以百万美元计）。你的主场是 <strong>L5 以上</strong>：调用、检索、编排。</p>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>我的瓶颈在第几层？</h4>
    <p>响应<strong>慢 / 贵</strong> → 看 <strong>L5 推理</strong>；答<strong>不准 / 缺知识</strong> → 看 <strong>L6 检索</strong>；流程<strong>乱 / 不可控</strong> → 看 <strong>L7 编排</strong>（你已经在学）。</p>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>下一步往哪学？</h4>
    <p>从 L7 往下探<strong>紧挨着的两层</strong>投入产出比最高：<strong>L5 推理服务</strong> 与 <strong>L6 向量检索</strong>。
    具体读哪些项目、什么顺序 → <strong>下一课</strong>给你一张学习地图。</p>
    <p class="mono">下一课 · 隔壁层学习地图</p>
  </div></div>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>LangChain / AutoGen 都在 L7 编排层</strong>，不是"最底层"——它们之上是 App，之下还有 6 层。</li>
    <li>全栈 7 层（自上而下）：<strong>编排+应用 → 检索/记忆 → 推理/服务 → 模型 → 训练 → 基础设施 → 硬件</strong>，外加一条横切带（评测/可观测/安全）。</li>
    <li><strong>Megatron 在 L3（训练）</strong>，<strong>向量数据库在 L6（检索）</strong>——它们和 LangChain 隔着好几层，别再混为一谈。</li>
    <li>编排层内部还分 <strong>5 大流派</strong>（图/多Agent/RAG/轻量/程序化），LangChain 属"图/工作流型"。</li>
    <li>学会"缩放看坐标"：遇到任何新名词，先问 <strong>"它在第几层？"</strong></li>
  </ul>
</div>
"""


LESSON_LEARN = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
学完编排层（L7），想往下探一层？最值得动手的是<strong>紧挨着你的两层</strong>：
<strong>L5 推理服务</strong>（让模型高效跑起来）和 <strong>L6 向量检索</strong>（RAG 的底座）。
这一课给你一张<strong>"该读哪些项目、按什么顺序"</strong>的实战地图。
</p>

<div class="card analogy">
  <div class="tag">🏭 一句话类比</div>
  如果 <strong>L7（你已会）</strong>是"一个会用工具的工人"，那么
  <strong>L5</strong> 是<strong>给工人配一台高效引擎</strong>（同样的活，更快更省）；
  <strong>L6</strong> 是<strong>给工人一个随手可查的资料库</strong>（不靠死记，靠查）。
</div>

<div class="card warn">
  <div class="tag">⚠️ 这是"地图"，不是"作业"</div>
  下面项目<strong>不用全学</strong>。每层我都标了一个 <strong>⭐ 主攻项目</strong>和一条<strong>推荐主线</strong>——
  先跟主线走通一条，建立体感，再按兴趣横向铺开。<strong>能跑 → 读核心 → 工程深度</strong>，三步走。
</div>

<h2>L5 · 推理 / 服务：让模型高效跑起来</h2>
<p>这层解决一件事：<strong>同一个模型，怎么更快、更省、更高并发地对外提供</strong>。
核心关键词：<span class="mono">KV-cache</span>、<span class="mono">PagedAttention</span>、
<span class="mono">continuous batching</span>、<span class="mono">量化(quantization)</span>。</p>

<table class="t">
  <tr><th>项目</th><th>语言</th><th>难度</th><th>读它能学到</th></tr>
  <tr><td class="mono">⭐ vLLM</td><td>Python/CUDA</td><td>中</td><td><strong>生产级推理引擎的范式</strong>：PagedAttention、continuous batching、OpenAI 兼容 server</td></tr>
  <tr><td class="mono">SGLang</td><td>Python</td><td>中</td><td>vLLM 之外的前沿：<strong>RadixAttention</strong>、结构化输出、超高并发</td></tr>
  <tr><td class="mono">llama.cpp</td><td>C/C++</td><td>中高</td><td>从底层吃透<strong>量化与推理</strong>：GGUF、纯 CPU 也能跑大模型</td></tr>
  <tr><td class="mono">Ollama</td><td>Go</td><td>低</td><td>本地<strong>一键起模型</strong>（底层基于 llama.cpp / GGML）——最快练手</td></tr>
  <tr><td class="mono">TensorRT-LLM · TGI</td><td>C++ · Rust</td><td>高</td><td>厂商级<strong>极致优化</strong>，进阶 / 特定硬件再看</td></tr>
</table>

<div class="card key">
  <div class="tag">✅ L5 推荐主线</div>
  <strong>① 用 Ollama 跑起来</strong>（10 分钟建立"模型在本地转"的直觉）→
  <strong>② 主攻 vLLM</strong>（读懂生产级推理怎么做高吞吐，这是行业事实标准）→
  <strong>③ 想深入底层再啃 llama.cpp</strong>（量化、算子）。
</div>

<div class="card detail">
  <div class="tag">🔬 vLLM 想先读哪几处</div>
  <ul>
    <li><strong>PagedAttention / KV-cache 管理</strong>——它最核心的创新，把"显存碎片"问题用"分页"解决。</li>
    <li><strong>Scheduler（continuous batching）</strong>——为什么它能把 GPU 利用率拉满。</li>
    <li><strong>OpenAI 兼容 server 入口</strong>——看"一个请求进来后怎么被排队、批处理、流式返回"。</li>
  </ul>
</div>

<h2>L6 · 检索 / 记忆：RAG 的底座</h2>
<p>你在<strong>第 19 课</strong>已经用过 <span class="mono">VectorStore / Retriever</span>——这层就是它们的<strong>"引擎室"</strong>。
核心关键词：<span class="mono">向量(embedding)</span>、<span class="mono">相似度</span>、
<span class="mono">ANN 近邻索引(HNSW / IVF)</span>。它分三小块：①向量索引/库　②嵌入模型　③长期记忆。</p>

<h3>① 向量索引 / 数据库</h3>
<table class="t">
  <tr><th>项目</th><th>语言</th><th>难度</th><th>读它能学到</th></tr>
  <tr><td class="mono">⭐ hnswlib</td><td>C++/Python</td><td>中</td><td><strong>HNSW 算法本身</strong>（ANN 检索的核心）。代码极小，最适合读懂"向量检索到底怎么算"</td></tr>
  <tr><td class="mono">FAISS</td><td>C++/Python</td><td>中高</td><td>工业级<strong>索引大全</strong>（IVF / PQ / HNSW），Meta 出品</td></tr>
  <tr><td class="mono">pgvector</td><td>C</td><td>中</td><td>在 <strong>Postgres 里做向量检索</strong>——最贴近真实业务落地</td></tr>
  <tr><td class="mono">Qdrant</td><td>Rust</td><td>中</td><td>生产级向量数据库的<strong>完整工程</strong>（过滤 + payload + 分布式）</td></tr>
  <tr><td class="mono">Chroma</td><td>Python</td><td>低</td><td>最易上手，<strong>本地 RAG 原型</strong>首选（第 19 课就是它这类）</td></tr>
  <tr><td class="mono">Milvus · Weaviate</td><td>Go</td><td>高</td><td>大规模<strong>分布式</strong>向量库，海量数据再看</td></tr>
</table>

<h3>② 嵌入模型　③ 长期记忆</h3>
<table class="t">
  <tr><th>项目</th><th>属于</th><th>读它能学到</th></tr>
  <tr><td class="mono">BGE（bge-m3 等）</td><td>嵌入模型</td><td>把文本变向量，<strong>中文友好、开源</strong>，RAG 检索质量的关键一环</td></tr>
  <tr><td class="mono">sentence-transformers</td><td>库</td><td>跑 / 微调嵌入模型的<strong>标准库</strong></td></tr>
  <tr><td class="mono">Mem0 · Zep</td><td>记忆层</td><td>在向量库之上给 Agent 加<strong>"长期记忆"</strong>（跨会话记住用户）</td></tr>
</table>

<div class="card key">
  <div class="tag">✅ L6 推荐主线</div>
  <strong>① 读 hnswlib</strong>（2~3 个核心文件就能看懂 HNSW，从此"向量检索"不再是黑盒）→
  <strong>② 用 pgvector 或 Chroma 落地一个 RAG</strong>（把第 19 课的玩具升级成能用的东西）→
  <strong>③ 要工程深度再看 Qdrant / FAISS</strong>。嵌入选 <strong>BGE</strong>，要记忆看 <strong>Mem0 / Zep</strong>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点：为什么偏偏是这两层</div>
  <ul>
    <li>L5 和 L6 是<strong>"应用开发者最该下探的两层"</strong>——它们紧挨着你已会的 L7，学了立刻能用。</li>
    <li><strong>懂 L5</strong>：你能解释"为什么慢 / 为什么贵"，能判断<strong>本地 vs API</strong> 怎么选。</li>
    <li><strong>懂 L6</strong>：你的 RAG 才能从<strong>"能跑"进化到"答得准"</strong>（选对索引、选对嵌入、调对 chunk）。</li>
    <li>再往下（L3 训练 / L1 硬件）是<strong>另一条职业路线</strong>了——不是不好，而是投入产出比对应用开发者没这么高，按需再说。</li>
  </ul>
</div>

<div class="card detail">
  <div class="tag">🔬 术语速查：5 个高频词，一句话各拆一个</div>
  <table class="t" style="margin-top:.6rem">
    <tr><th>术语</th><th>一句话理解</th></tr>
    <tr><td class="mono">PagedAttention</td><td>把 KV-cache 像操作系统的<strong>虚拟内存"分页"</strong>来管，消除显存碎片 → 同一张卡能跑更多并发</td></tr>
    <tr><td class="mono">continuous batching</td><td>不等"整批"凑齐，谁先生成完就把<strong>新请求填进空位</strong> → GPU 不空转</td></tr>
    <tr><td>量化 <span class="mono">quantization</span></td><td>用更低精度（int8/int4）存权重，<strong>省显存、提速</strong>，精度略有损失</td></tr>
    <tr><td class="mono">HNSW</td><td>一种多层"跳表式"图索引，<strong>快速找到最近邻向量</strong>（hnswlib 就是它）</td></tr>
    <tr><td class="mono">ANN</td><td>近似最近邻：<strong>牺牲一点点精度，换巨大的速度</strong>——向量检索能上规模的关键</td></tr>
  </table>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>L5 主攻 vLLM</strong>（先 Ollama 起步，深入再读 llama.cpp）；关键词 <span class="mono">PagedAttention / continuous batching / 量化</span>。</li>
    <li><strong>L6 主攻 hnswlib</strong>（懂算法）+ <strong>pgvector / Chroma</strong>（会落地）；关键词 <span class="mono">HNSW / ANN / 嵌入</span>。</li>
    <li>嵌入选 <strong>BGE</strong>，长期记忆看 <strong>Mem0 / Zep</strong>。</li>
    <li>统一学习节奏：<strong>能跑 → 读核心 → 工程深度</strong>，先走通一条主线再横向铺开。</li>
    <li>🎉 番外到此为止——你已从"LangChain 一个点"，缩放到了"整个 AI 生态的坐标系"，并拿到了往下探的地图。祝你走得更远。</li>
  </ul>
</div>
"""
