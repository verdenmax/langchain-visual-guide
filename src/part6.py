"""Content for Part 6 (appendix): lesson 21 — LangChain vs AutoGen."""

LESSON_CMP = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
学完 LangChain，跳出来看看<strong>另一条技术路线</strong>——微软的 <strong>AutoGen</strong>。
对照才能真正看清 LangChain 的设计取舍：两者解决的是同一类问题，路径却截然不同。
</p>

<div class="card warn">
  <div class="tag">ℹ️ 先说现状</div>
  AutoGen 目前已进入<strong>维护模式</strong>（不再加新功能），微软推荐新项目用其继任者
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

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>根本差异：<strong>LangChain = 可组合的图（数据流优先）</strong>；<strong>AutoGen = 自治 actor 的对话（多 Agent 优先）</strong>。</li>
    <li>单 Agent 两者都简洁；<strong>多 Agent 协作是 AutoGen 的主场</strong>（Team 一等公民），LangChain 则靠 LangGraph 手搭、换取可控性。</li>
    <li>选型：要<strong>RAG/可控工作流/大集成</strong>→ LangChain；要<strong>快速多 Agent 协作/研究</strong>→ AutoGen（或其继任 Agent Framework）。</li>
    <li>互相借鉴：LangChain 可学"团队一等抽象"，AutoGen 可学"集成生态 + 显式可控 + 稳定性"。</li>
    <li>🎉 看懂一个框架的最好方式，就是<strong>把它和另一个对照</strong>——你现在两种范式都有了坐标。</li>
  </ul>
</div>
"""
