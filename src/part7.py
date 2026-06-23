"""Content for Part 7 (deep dive): LangGraph 的实现细节.

- lesson 24 — LangGraph 是什么：图 / 状态 / 节点 / 边（心智模型）
- lesson 25 — 执行引擎：Pregel 与超步（actors + channels）
- lesson 26 — 持久化、中断与控制流：checkpointer / interrupt / Send / Command

源码引用对照官方仓库 langchain-ai/langgraph（libs/langgraph/langgraph/...）。
"""

LESSON_LG1 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 15 课你看到：<span class="inline">create_agent</span> 把 Agent 循环<strong>编译成一张 LangGraph 状态图</strong>。
这一部分（3 课）我们把这张图的<strong>引擎彻底拆开</strong>。先从最基本的问题开始：
<strong>LangGraph 到底是什么、为什么需要它。</strong>
</p>

<div class="card analogy">
  <div class="tag">🚆 一句话类比</div>
  你在第 10/11 课学的 <strong>LCEL（<span class="mono">Runnable |</span>）像一条直的传送带</strong>——东西一头进、一头出，绝不回头。
  而 <strong>LangGraph 像一整套带道岔和环线的铁路网 + 一个调度塔</strong>：列车能<strong>转圈、并行、
  中途停车存档、改天从原地继续</strong>。
</div>

<h2>为什么 LCEL 不够：DAG vs 状态图</h2>
<p>LCEL 把程序表达成一条<strong>有向无环图（DAG）</strong>——非常适合"prompt → model → parser"这种<strong>直线链</strong>。
但 Agent 天生不是直线：</p>
<div class="cols">
  <div class="col">
    <h4>🟦 LCEL：有向无环图（DAG）</h4>
    <p>一头流到另一头，<strong>不能转圈</strong>、不能暂停存档。适合<strong>确定的线性管道</strong>。</p>
  </div>
  <div class="col">
    <h4>🟩 LangGraph：有状态的图（状态机）</h4>
    <p>补上 <strong>环（cycle）+ 共享状态（state）+ 持久化 + 人在回路</strong>。适合<strong>会循环、会分支</strong>的 Agent。</p>
  </div>
</div>
<div class="card detail">
  <div class="tag">🔬 关键差别</div>
  Agent 的本质是"<strong>循环 + 分支</strong>"：反复"想 → 调工具 → 把结果回灌 → 再想"，直到完成。
  用 DAG <strong>表达不了"绕回去"</strong>；而图天然能画出"从 tools 节点连一条边<strong>回到</strong> model 节点"的环。
</div>

<h2>四件套：State / Node / Edge / compile</h2>
<p>LangGraph 的全部心智，就是这四个词。官方 <span class="mono">StateGraph</span> 的文档一句话点透：
<strong>"一张图，其节点通过读写一份共享状态来通信；每个节点的签名是 <span class="mono">State → 部分 State</span>"</strong>。</p>

<div class="layers">
  <div class="layer l-core">
    <div class="lh"><span class="badge">State</span><span class="name">共享状态</span></div>
    <div class="ld">一个数据字典（如 <span class="mono">{"messages": [...]}</span>），在图里流动。<strong>每个键可标注一个 reducer</strong>（归并函数 <span class="mono">(旧, 新) → 新</span>），决定多个节点的写如何合并。</div>
  </div>
  <div class="layer l-main">
    <div class="lh"><span class="badge">Node</span><span class="name">节点</span></div>
    <div class="ld">一个<strong>普通函数</strong>：读 <span class="mono">state</span> → 返回一份<strong>部分更新</strong>（如 <span class="mono">{"messages": [ai]}</span>）。"调模型""执行工具"各是一个节点。</div>
  </div>
  <div class="layer l-part">
    <div class="lh"><span class="badge">Edge</span><span class="name">边</span></div>
    <div class="ld"><strong>普通边</strong> <span class="mono">A→B</span>；<strong>条件边</strong>按一个路由函数<strong>动态</strong>选下一站；特殊节点 <span class="mono">START</span> / <span class="mono">END</span> 是入口与出口。</div>
  </div>
  <div class="layer l-app">
    <div class="lh"><span class="badge">compile</span><span class="name">编译</span></div>
    <div class="ld"><span class="mono">StateGraph</span> 只是<strong>建造者</strong>，不能直接跑；<span class="mono">.compile()</span> 出一个 <strong>CompiledStateGraph</strong>（可执行，<strong>本身就是 Runnable</strong>）。</div>
  </div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">你的代码</span><span class="ln">最小可跑的 StateGraph（真实 API）</span></div>
<pre><span class="kw">from</span> typing_extensions <span class="kw">import</span> TypedDict, Annotated
<span class="kw">from</span> langgraph.graph <span class="kw">import</span> StateGraph, START, END
<span class="kw">import</span> operator

<span class="kw">class</span> <span class="fn">State</span>(TypedDict):
    count: Annotated[int, operator.add]   <span class="cm"># 给 count 标个 reducer：累加</span>

<span class="kw">def</span> <span class="fn">step</span>(state):                       <span class="cm"># 节点：state → 部分 state</span>
    <span class="kw">return</span> {<span class="st">"count"</span>: 1}

g = StateGraph(State)
g.add_node(<span class="st">"step"</span>, step)
g.add_edge(START, <span class="st">"step"</span>)               <span class="cm"># 入口 → step</span>
g.add_edge(<span class="st">"step"</span>, END)                 <span class="cm"># step → 出口</span>
app = g.compile()                         <span class="cm"># 得到可执行图（也是 Runnable）</span>

<span class="nb">print</span>(app.invoke({<span class="st">"count"</span>: 0}))       <span class="cm"># {'count': 1}（reducer 把 0 和 1 累加）</span>
</pre>
</div>

<div class="card detail">
  <div class="tag">🔬 代码对应（langgraph 仓库）</div>
  <table class="t" style="margin-top:.6rem">
    <tr><th>概念</th><th>位置</th></tr>
    <tr><td class="mono">StateGraph / add_node / add_edge / add_conditional_edges / compile</td><td class="mono">graph/state.py</td></tr>
    <tr><td class="mono">CompiledStateGraph（compile 的产物）</td><td class="mono">graph/state.py · 继承 Pregel</td></tr>
    <tr><td class="mono">START / END</td><td class="mono">constants.py（值是 "__start__" / "__end__"）</td></tr>
    <tr><td>reducer（如 add_messages）</td><td class="mono">graph/message.py · 第 27 课详解</td></tr>
  </table>
</div>

<h2>和 LangChain 的关系（回顾 + 定位）</h2>
<div class="cols">
  <div class="col">
    <h4>LangChain（你一直在学）</h4>
    <p><strong>高层便利</strong>：<span class="mono">create_agent</span> 帮你把这张图<strong>搭好</strong>，你不用碰节点和边。</p>
  </div>
  <div class="col">
    <h4>LangGraph（这一部分）</h4>
    <p><strong>底层引擎</strong>：真正<strong>运行</strong>这张图。它是<strong>另一个独立仓库</strong> <span class="mono">langchain-ai/langgraph</span>，<span class="mono">langchain</span> 依赖它；你也能<strong>单独用</strong>它从零搭图。</p>
  </div>
</div>
<div class="card detail">
  <div class="tag">🔬 一个会反复用到的事实</div>
  <span class="mono">CompiledStateGraph</span> <strong>本身就是一个 Runnable</strong>，所以第 10 课关于 Runnable 的一切
  （<span class="mono">invoke</span>/<span class="mono">stream</span>/<span class="mono">batch</span>、<span class="mono">config</span>、回调）对整张图都成立。
  在第 24 课的全栈图里，LangChain 与 LangGraph 都在 <strong>L7 编排层</strong>。
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，抠三个常被问到的细节。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 条件边的路由函数到底返回什么 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 返回值</div>
      <div class="a"><span class="mono">add_conditional_edges(源节点, path, path_map=None)</span>：<span class="mono">path</span> 是一个看 state 的函数，
        返回<strong>下一个节点名</strong>（或名字列表，甚至 <span class="mono">Send</span>）；返回 <span class="mono">"END"</span> 就结束。
        可选的 <span class="mono">path_map</span> 把返回值映射到节点名。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 小坑</div>
      <div class="a">官方建议给 <span class="mono">path</span> 的返回值<strong>加类型注解</strong>（如 <span class="mono">-&gt; Literal["tools", "__end__"]</span>），
        否则画图工具无法得知这条条件边有哪些可能目标。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 为什么必须 compile() <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 两个阶段</div>
      <div class="a"><span class="mono">StateGraph</span> 只是<strong>建造者</strong>，存着"节点 + 边"的图纸，不能执行。
        <span class="mono">compile()</span> 会<strong>校验图</strong>（节点是否连通、键是否合法）并把图纸编成一个可执行的 <span class="mono">Pregel</span>（即 <span class="mono">CompiledStateGraph</span>）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 顺带的好处</div>
      <div class="a">产物是 <strong>Runnable</strong>，于是 <span class="mono">invoke/stream/batch</span>、回调、<span class="mono">config</span> 全部免费获得（第 10 课）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> reducer 的签名与默认行为 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 签名</div>
      <div class="a">reducer 是 <span class="mono">(旧值, 新值) → 新值</span>。键<strong>不标</strong> reducer 时默认是 <span class="mono">LastValue</span>——<strong>后写覆盖前值</strong>；
        标了（如 <span class="mono">operator.add</span> / <span class="mono">add_messages</span>）就按你的函数<strong>合并</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 它在哪生效</div>
      <div class="a">第 27 课会看到：编译时<strong>每个键变成一个 channel</strong>，reducer 就是那个 channel 的"更新函数"。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点：把"图"当成一等公民</div>
  一旦把程序建模成"<strong>状态 + 节点 + 边</strong>"，那些最难的能力——<strong>循环、分支、并行、持久化、人审、时间旅行</strong>——
  就都变成<strong>图引擎的通用能力</strong>，而不必每个 Agent 各写一遍。这正是 LangGraph 存在的理由，下一课我们看它怎么"跑"。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>LCEL 是 <strong>DAG（不能转圈）</strong>；LangGraph 是<strong>有状态的图</strong>，补上环 / 状态 / 持久化 / 人审。</li>
    <li>四件套：<strong>State</strong>（共享状态，键可带 reducer）、<strong>Node</strong>（<span class="mono">state → 部分 state</span>）、<strong>Edge</strong>（普通/条件，<span class="mono">START/END</span>）、<strong>compile()</strong>（产出可执行的 <span class="mono">CompiledStateGraph</span>）。</li>
    <li><span class="mono">CompiledStateGraph</span> 是 Runnable；LangGraph 是<strong>独立仓库</strong>，<span class="mono">create_agent</span> 依赖它、也能单独用。</li>
    <li>下一课：编译产物到底怎么"跑"——揭开 <strong>Pregel 引擎</strong>。</li>
  </ul>
</div>
"""


LESSON_LG2 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
上一课的 <span class="inline">compile()</span> 产物到底怎么"跑"？答案藏在一个名字里：<strong>Pregel</strong>。
你编译出来的图，<strong>本质上就是一个 <span class="mono">Pregel</span> 对象</strong>。这是整个第七部分<strong>最硬核</strong>的一课。
</p>

<div class="card analogy">
  <div class="tag">♟️ 一句话类比：回合制</div>
  把图的运行想成<strong>回合制游戏</strong>：每一<strong>回合（超步 super-step）</strong>里，所有"该动的"节点<strong>同时行动</strong>，
  各自把要写的东西<strong>先攒着</strong>；回合一结束，<strong>统一结算</strong>到共享状态，再开下一回合——直到没有节点要动。
</div>

<h2>编译产物 = 一个 Pregel</h2>
<p>官方源码 <span class="mono">pregel/main.py</span> 里 <span class="mono">Pregel</span> 类的文档说得很直白（这里翻译关键句）：</p>
<div class="card detail">
  <div class="tag">🔬 Pregel 类文档（直译）</div>
  <p>"<strong>Pregel 把 actors（行动者）和 channels（通道）组合成一个应用。</strong>
  Actors 从 channels 读数据、往 channels 写数据。Pregel 把执行组织成<strong>多个步骤</strong>，
  遵循 <strong>Pregel 算法 / Bulk Synchronous Parallel（BSP，整体同步并行）模型</strong>。"</p>
  <ul>
    <li><strong>actor = 一个 <span class="mono">PregelNode</span></strong>（它也实现了 LangChain 的 <span class="mono">Runnable</span>）。</li>
    <li>"Graph API（<span class="mono">StateGraph</span>）/ Functional API 都会在底层<strong>编译成 Pregel</strong>。"——你的图就是这么跑的。</li>
  </ul>
</div>
<p style="color:var(--muted);font-size:.9rem">＊ Pregel 是 Google 2010 年提出的大规模图计算模型，LangGraph 把这套"消息传递 + 逐步推进"的成熟范式搬来跑 LLM 应用。</p>

<h2>一个"超步"的三阶段：Plan → Execution → Update</h2>
<p>每一个超步（step）都严格走三步（直接来自 Pregel 类文档）：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>Plan（计划）：选出本步要执行的节点</h4>
    <p>挑出"<strong>订阅了『上一步被更新的 channel』</strong>"的那些 actor。第一步则选订阅<strong>输入通道</strong>的节点。</p>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>Execution（执行）：并行跑选中的节点</h4>
    <p>选中的 actor <strong>并行执行</strong>。<strong>关键</strong>：本步产生的 channel 写入，<strong>对本步的 actor 不可见</strong>——要到下一步才生效。</p>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>Update（更新）：把写入统一应用到 channels</h4>
    <p>把本步所有节点写的值，<strong>一次性</strong>结算进 channels。然后回到 Plan，开下一超步——直到没有节点被触发，或到达步数上限。</p>
  </div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 确定性从哪来 + 代码对应</div>
  <p>"<strong>本步的写下一步才可见</strong>"是整个模型的灵魂：它让<strong>并行节点不会看到彼此的半成品</strong>，
  于是同样输入 → 同样结果，可复现、可持久化。</p>
  <ul>
    <li>超步循环：<span class="mono">pregel/_loop.py · PregelLoop.tick()</span>——里面先 <span class="mono">prepare_next_tasks(...)</span>（Plan），执行后 <span class="mono">apply_writes(...)</span>（Update）。</li>
    <li>步数上限：<span class="mono">tick()</span> 开头检查 <span class="mono">step &gt; stop</span> → 置 <span class="mono">out_of_steps</span>。这就是第 9 课 <span class="mono">recursion_limit</span> 的<strong>兜底实现</strong>。</li>
  </ul>
</div>

<h2>channels：状态到底怎么存与合并</h2>
<p>"状态的每个键"在底层其实是一个 <strong>channel（通道）</strong>。每个 channel 有<strong>值类型 + 更新函数（reducer）</strong>。
LangGraph 内置了几种（来自 Pregel 文档）：</p>
<table class="t">
  <tr><th>Channel</th><th>行为</th><th>用途</th></tr>
  <tr><td class="mono">LastValue</td><td><strong>默认</strong>：只存"最后写入的值"</td><td>键没标 reducer 时；在步与步之间传值</td></tr>
  <tr><td class="mono">BinaryOperatorAggregate</td><td>用<strong>二元运算</strong>把每次写入累积进去（如 <span class="mono">operator.add</span>）</td><td>需要"累加/合并"的键（reducer 的真身）</td></tr>
  <tr><td class="mono">Topic</td><td>可配置的 <strong>PubSub</strong>，能累积 / 去重</td><td>多个 actor 之间多值传递</td></tr>
  <tr><td class="mono">EphemeralValue / Context</td><td>只活一步的临时值 / 暴露上下文管理器</td><td>临时数据 / 外部资源生命周期</td></tr>
</table>

<div class="card detail">
  <div class="tag">🔬 reducer 的真身 = channel 的更新函数</div>
  <p>第 15 课你见过 <span class="mono">messages: Annotated[list[AnyMessage], add_messages]</span>。现在能说清它的实现了：
  <strong>编译时，这个标注让 "messages" 键变成一个『以 <span class="mono">add_messages</span> 为更新函数』的 channel</strong>。
  节点写 <span class="mono">{"messages": [ai]}</span> 时，channel 用 <span class="mono">add_messages</span> 把新值<strong>归并</strong>进旧值——这就是"追加而非覆盖"。</p>
  <ul>
    <li><span class="mono">add_messages</span>（<span class="mono">graph/message.py</span>）默认<strong>"append-only"</strong>：按 <span class="mono">id</span> 合并（同 id 替换、不同 id 追加），还支持 <span class="mono">RemoveMessage</span> 删除。</li>
    <li>你自定义的 reducer 也一样：标 <span class="mono">Annotated[T, 你的函数]</span>，编译时就接到对应 channel 上。</li>
  </ul>
</div>

<h2>回到 Agent：model / tools 两节点怎么在超步里转</h2>
<p>把上面这套套回第 15 课那张图，"Agent 循环"就清清楚楚是<strong>一串超步</strong>：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>超步 A</h4><p><span class="mono">model</span> 节点执行 → 往 <span class="mono">messages</span> channel 写一条 <span class="mono">AIMessage</span>。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>超步 B</h4><p><span class="mono">model</span> 的<strong>条件边</strong>据 <span class="mono">tool_calls</span> 选定下一站为 <span class="mono">tools</span> → 这一步执行 <span class="mono">tools</span> 节点 → 写回 <span class="mono">ToolMessage</span>。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>超步 C…</h4><p>又选中 <span class="mono">model</span>……如此往复，<strong>直到某次 AIMessage 没有 <span class="mono">tool_calls</span></strong> → 路由到 <span class="mono">END</span>，循环停。</p></div></div>
</div>
<div class="card detail">
  <div class="tag">🔬 多个工具如何"同一超步并行"</div>
  当一条 AIMessage 里有<strong>多个 <span class="mono">tool_calls</span></strong>，路由会用 <span class="mono">Send</span> 把它们<strong>同时</strong>扇给 <span class="mono">tools</span> 节点，
  于是它们在<strong>同一个超步内并发执行</strong>、再一起结算。<span class="mono">Send</span> 的细节留到第 28 课。
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入超步引擎的三个细节。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> Plan 阶段怎么"选中"要跑的节点 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 订阅机制</div>
      <div class="a">每个节点<strong>订阅</strong>若干 channel。一个超步结束后，引擎看<strong>哪些 channel 被更新了</strong>，
        就在下一步<strong>触发订阅了它们的节点</strong>（源码里叫 <span class="mono">trigger_to_nodes</span>）。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 套到 Agent</div>
      <div class="a"><span class="mono">model</span> 节点写了 <span class="mono">messages</span>，其<strong>条件边</strong>据 <span class="mono">tool_calls</span> 选定下一站 → 下一超步执行 <span class="mono">tools</span>（或走 <span class="mono">END</span>）。没有任何节点被触发时，图自然停下。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 除了 LastValue / Aggregate 还有哪些 channel <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 常见几种</div>
      <div class="a"><span class="mono">Topic</span>（PubSub，可累积/去重，多节点多值传递）、<span class="mono">EphemeralValue</span>（只活一个超步的临时值）、
        <span class="mono">Context</span>（暴露上下文管理器，管外部资源生命周期）等。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 实际上</div>
      <div class="a">用 <span class="mono">StateGraph</span> 时你几乎只碰两种：<strong>不标 reducer 的键 = LastValue</strong>，<strong>标了 reducer 的键 = 聚合通道</strong>。其余是底层在用。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 超步与流式：stream_mode 看到的是什么 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 对应关系</div>
      <div class="a"><span class="mono">stream_mode="updates"</span>：每个超步吐出<strong>被更新节点的输出</strong>；
        <span class="mono">"values"</span>：每步吐出<strong>整份状态</strong>；<span class="mono">"messages"</span>：逐 token。呼应第 16、21 课。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么能逐步流</div>
      <div class="a">正因为执行被切成<strong>一个个离散超步</strong>，引擎才能在<strong>每步边界</strong>把进展推给你——这是"边想边显示 Agent 过程"的基础。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点：借一套 20 年的成熟模型来跑 Agent</div>
  LangGraph 没有自己发明轮子，而是把 Google <strong>Pregel（大规模图计算）</strong>的 <strong>BSP 超步模型</strong>搬过来——
  "actors 读写 channels、逐超步推进、写入延迟到下一步可见"。这套范式天生<strong>确定、可并行、可在任意一步存档</strong>，
  正好满足 Agent 对"可控 + 可持久化"的需求。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>你 <span class="mono">compile()</span> 出的图<strong>就是一个 <span class="mono">Pregel</span></strong>（<span class="mono">CompiledStateGraph</span> 继承 Pregel）。</li>
    <li>运行 = 一串<strong>超步</strong>，每步三阶段 <strong>Plan → Execution → Update</strong>；"<strong>本步写、下步见</strong>"保证确定性。</li>
    <li>状态的每个键是一个 <strong>channel</strong>；<strong>reducer 就是 channel 的更新函数</strong>（<span class="mono">add_messages</span> = "messages" 通道的更新函数）。</li>
    <li>Agent 循环 = model/tools 两节点在超步间往复，靠 <span class="mono">tool_calls</span> 决定继续还是 <span class="mono">END</span>。</li>
    <li>下一课：每个超步存档之后，<strong>持久化、时间旅行、人审、跳转</strong>如何水到渠成。</li>
  </ul>
</div>
"""


LESSON_LG3 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
有了"超步"引擎，LangGraph 最强的能力就<strong>水到渠成</strong>了：把<strong>每个超步存档</strong>（持久化 / 时间旅行 / 人审），
以及用<strong>原语控制图的走向</strong>（并行 / 跳转 / 多 Agent 交接）。这一课把它们的实现一次讲透。
</p>

<div class="card analogy">
  <div class="tag">💾 一句话类比：游戏存档</div>
  因为引擎<strong>每个超步都自动存了一个档（checkpoint）</strong>，你才能：<strong>关机改天接着玩</strong>（续跑）、
  <strong>读任意旧档重来</strong>（时间旅行）、<strong>在剧情关键点暂停等你决定</strong>（人审）。
</div>

<h2>持久化：每个超步存一个 checkpoint</h2>
<p>挂上一个 <strong>checkpointer</strong> 后，引擎会在<strong>每个超步后</strong>把状态存成一个 <span class="mono">Checkpoint</span>。</p>
<div class="card detail">
  <div class="tag">🔬 存的是什么（checkpoint/base.py）</div>
  <ul>
    <li><span class="mono">Checkpoint</span> 里有 <span class="mono">channel_values</span>（<strong>所有 channel 的当前值＝状态快照</strong>）、<span class="mono">channel_versions</span>、<span class="mono">versions_seen</span>。</li>
    <li><span class="mono">BaseCheckpointSaver</span> 是<strong>存储接口</strong>：开发用 <span class="mono">InMemorySaver</span>，生产换 <span class="mono">Postgres</span> / <span class="mono">SQLite</span> 版，<strong>代码不变</strong>。</li>
    <li>对外读状态是 <span class="mono">StateSnapshot</span>（<span class="mono">types.py</span>）：<span class="mono">values</span>（当前状态）、<span class="mono">next</span>（下一步要执行的节点）、<span class="mono">config</span>、<span class="mono">tasks</span>、<span class="mono">interrupts</span> 等——<span class="mono">graph.get_state(config)</span> 返回它。</li>
  </ul>
</div>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">你的代码</span><span class="ln">checkpointer + thread_id（承接第 15 课，这里看实现）</span></div>
<pre><span class="kw">from</span> langgraph.checkpoint.memory <span class="kw">import</span> InMemorySaver

app = g.compile(checkpointer=InMemorySaver())
cfg = {<span class="st">"configurable"</span>: {<span class="st">"thread_id"</span>: <span class="st">"user-1"</span>}}

app.invoke({<span class="st">"messages"</span>: [...]}, cfg)   <span class="cm"># 每个超步后存一个 checkpoint（绑 thread_id）</span>
app.invoke({<span class="st">"messages"</span>: [...]}, cfg)   <span class="cm"># 同 thread：从最后的 checkpoint 恢复状态继续</span>

snap = app.get_state(cfg)              <span class="cm"># StateSnapshot：看当前状态 / 下一步</span>
</pre>
</div>

<h2>时间旅行（time-travel）</h2>
<p>因为<strong>每一步的状态都存了</strong>，"回到第 N 步、换个选择重来"就成了可能——这是调试 Agent 的利器。</p>
<div class="card detail">
  <div class="tag">🔬 怎么做</div>
  <span class="mono">graph.get_state_history(cfg)</span> 返回一串历史 <span class="mono">StateSnapshot</span>（每个超步一个）。
  挑中某个旧 snapshot，把它的 <span class="mono">config</span>（含该 checkpoint 的 id）传回 <span class="mono">invoke</span>，图就会<strong>从那个点 fork 出去重跑</strong>，
  让你"在岔路口换条路走"。
</div>

<h2>中断与恢复：interrupt 的真实机制</h2>
<p>人在回路（HITL）不是什么黑魔法，就是<strong>"存档 + 重放"</strong>的直接产物。官方 <span class="mono">interrupt()</span> 文档说得很清楚：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>暂停</h4><p>在节点里调 <span class="mono">interrupt(value)</span> → <strong>第一次会抛出 <span class="mono">GraphInterrupt</span></strong>，执行停住，<span class="mono">value</span> 被交给客户端（如"请审批这笔转账"）。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>等待</h4><p>状态已存档，<strong>不占用任何运行资源</strong>；可以等几秒，也可以等几天。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>恢复</h4><p>客户端用 <span class="mono">Command(resume=值)</span> 继续；<strong>图会从该节点的开头<u>重新执行</u></strong>，这次 <span class="mono">interrupt()</span> 直接返回你给的值。需要 <strong>checkpointer</strong>。</p></div></div>
</div>
<div class="card warn">
  <div class="tag">⚠️ 真实的坑：恢复是"从节点头重跑"</div>
  因为恢复会<strong>重新执行整个节点</strong>，所以 <span class="mono">interrupt()</span> <strong>之前</strong>的副作用（比如"已经发了邮件""已经扣了款"）会<strong>再执行一遍</strong>。
  原则：<strong>把副作用放在 <span class="mono">interrupt()</span> 之后</strong>，或做幂等。第 9 课的 <span class="mono">HumanInTheLoopMiddleware</span> 正是基于这套机制。
</div>

<h2>控制流原语：Send 与 Command（实现细节）</h2>
<p>第 15 课点过名，这里看它们在 <span class="mono">types.py</span> 里到底是什么、能干什么。</p>
<div class="cols">
  <div class="col">
    <h4><span class="mono">Send</span>：动态扇出（map-reduce）</h4>
    <p>文档原话：<strong>"在条件边里用来动态调用一个节点，并可携带与主 state 不同的自定义 state"</strong>。
    典型就是 map-reduce / 并行：</p>
<pre class="code"><span class="cm"># 给每个 subject 派发一个并行任务</span>
<span class="kw">return</span> [Send(<span class="st">"gen_joke"</span>, {<span class="st">"subject"</span>: s})
        <span class="kw">for</span> s <span class="kw">in</span> state[<span class="st">"subjects"</span>]]</pre>
    <p>Agent 的<strong>并行工具调用</strong>就是用它把多个 <span class="mono">tool_call</span> 扇给 <span class="mono">tools</span> 节点。</p>
  </div>
  <div class="col">
    <h4><span class="mono">Command</span>：改状态 + 改去向</h4>
    <p>一个节点返回普通 <span class="mono">dict</span> 只能<strong>改状态</strong>；返回 <span class="mono">Command</span> 能<strong>同时</strong>改状态<strong>并指定下一步</strong>：</p>
<pre class="code"><span class="kw">from</span> langgraph.types <span class="kw">import</span> Command

<span class="kw">return</span> Command(
    update={<span class="st">"messages"</span>: [...]},   <span class="cm"># 改状态</span>
    goto=<span class="st">"researcher"</span>,            <span class="cm"># 跳到另一个 agent</span>
)</pre>
    <p>字段：<span class="mono">update</span> / <span class="mono">goto</span>（节点名 / <span class="mono">Send</span> / 序列）/ <span class="mono">resume</span>（配合 interrupt）/ <span class="mono">graph</span>（当前或 <span class="mono">PARENT</span>）。</p>
  </div>
</div>
<div class="card detail">
  <div class="tag">🔬 这就是"多 Agent handoff"</div>
  第 23 课对照 AutoGen 时提到的"<strong>交接（handoff）</strong>"，落到 LangGraph 就是 <span class="mono">Command(goto="另一个 agent", update=...)</span>：
  一个 Agent <strong>改完共享状态、把控制权交棒</strong>给另一个。<span class="mono">Command</span> 还实现了 <span class="mono">ToolOutputMixin</span>——意味着<strong>工具直接返回 Command</strong> 也能驱动跳转。
  <table class="t" style="margin-top:.6rem">
    <tr><th>原语</th><th>位置</th></tr>
    <tr><td class="mono">Send / Command / interrupt() / Interrupt / StateSnapshot</td><td class="mono">types.py</td></tr>
    <tr><td class="mono">Checkpoint / BaseCheckpointSaver</td><td class="mono">checkpoint/base.py</td></tr>
  </table>
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，抠持久化与中断的三个细节。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> checkpoint 里的 versions_seen 是干嘛的 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 三个字段的分工</div>
      <div class="a"><span class="mono">channel_values</span> = 状态快照；<span class="mono">channel_versions</span> = 每个 channel 的<strong>当前版本号</strong>；
        <span class="mono">versions_seen</span> = "<strong>每个节点看过哪个版本</strong>"。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 有什么用</div>
      <div class="a">引擎对比"channel 现在的版本"和"某节点已看过的版本"，决定这个节点<strong>要不要（再）跑</strong>——
        避免对<strong>同一次更新</strong>重复处理，也让断点续跑能精确知道"还差哪些没做"。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> InMemorySaver 和生产用的 saver <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 同一个接口</div>
      <div class="a">都实现 <span class="mono">BaseCheckpointSaver</span>。开发/测试用 <span class="mono">InMemorySaver</span>（进程内）；
        生产换 <span class="mono">langgraph-checkpoint-postgres</span> / <span class="mono">-sqlite</span>，<strong>业务代码不用改</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 怎么选</div>
      <div class="a">要<strong>跨进程 / 重启后仍能续跑</strong>（真实用户会话、长任务）就用数据库版；只是本地跑通用内存版即可。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 一个节点里有多个 interrupt 怎么办 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 按顺序匹配</div>
      <div class="a">LangGraph 按 <span class="mono">interrupt()</span> 在节点里<strong>出现的顺序</strong>，把你给的 resume 值依次对上；
        这份 resume 值列表<strong>只属于当前这个 task</strong>，不跨任务共享。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 回顾那个坑</div>
      <div class="a">别忘了恢复是"<strong>从节点头重跑</strong>"：已经返回过值的 interrupt 会直接返回上次的 resume 值，但<strong>它们之间的普通代码会重新执行一遍</strong>。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点：一个设计的三个面</div>
  持久化、时间旅行、人审、可靠跳转——看似四件事，其实是<strong>同一个设计</strong>的不同侧面：
  <strong>因为状态被逐超步持久化</strong>，"续跑 / 回到过去 / 暂停等人 / 跨节点跳转"才统统成立。
  这就是"用图 + checkpoint 运行"相比"裸 while 循环"<strong>质的差距</strong>。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点 & 第七部分收尾</div>
  <ul>
    <li><strong>持久化</strong>：每个超步存一个 <span class="mono">Checkpoint</span>（<span class="mono">channel_values</span> = 状态快照）；<span class="mono">thread_id</span> 区分会话；<span class="mono">get_state</span> 返回 <span class="mono">StateSnapshot</span>。</li>
    <li><strong>时间旅行</strong>：<span class="mono">get_state_history</span> + 旧 checkpoint 的 config → 从任意一步 fork 重跑。</li>
    <li><strong>interrupt</strong>：抛 <span class="mono">GraphInterrupt</span> 暂停、<span class="mono">Command(resume=...)</span> 恢复，且<strong>从节点头重放</strong>（副作用要放在 interrupt 之后）。</li>
    <li><strong>控制流</strong>：<span class="mono">Send</span> = 动态扇出/并行；<span class="mono">Command</span> = 改状态 + 跳转（多 Agent handoff 的底座）。</li>
    <li>🎉 至此，<span class="mono">create_agent</span> 从"魔法"被彻底拆到了引擎层：<strong>一张状态图，跑在 Pregel 超步引擎上，靠 channel 合并状态、靠 checkpoint 持久化、靠 Send/Command 控制走向。</strong></li>
  </ul>
</div>
"""
