"""Content for Part 3 (internals): lessons 08-13."""

# ---------------------------------------------------------------------------
LESSON_08 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
现在掀开盖子。LangChain 内部有一个统一的抽象——<strong>Runnable</strong>。
模型、提示词、工具、解析器……几乎一切都是 Runnable。理解它，你就拿到了读懂整个源码的<strong>万能钥匙</strong>。
</p>

<div class="card analogy">
  <div class="tag">🔋 生活类比</div>
  Runnable 就像<strong>USB 标准接口</strong>：鼠标、键盘、硬盘内部天差地别，但都提供同一个 USB 插头。
  于是你能把它们<strong>随意串联到一个集线器上</strong>。LangChain 里每个组件都"长着 Runnable 这个插头"，
  所以才能用一个 <span class="mono">|</span> 把它们拼成链。
</div>

<h2>统一接口：每个 Runnable 都有这几招</h2>
<p>不管底层是什么，只要是 Runnable，就一定具备这套方法。你在第 5 课用过的 invoke/stream/batch，
其实就来自这里：</p>

<table class="t">
  <tr><th>方法</th><th>作用</th><th>异步版</th></tr>
  <tr><td class="mono">invoke(input)</td><td>单个输入 → 单个输出</td><td class="mono">ainvoke</td></tr>
  <tr><td class="mono">stream(input)</td><td>流式逐块产出</td><td class="mono">astream</td></tr>
  <tr><td class="mono">batch(inputs)</td><td>批量并发处理</td><td class="mono">abatch</td></tr>
</table>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/runnables/base.py</span><span class="ln">class Runnable</span></div>
<pre><span class="kw">class</span> <span class="fn">Runnable</span>(ABC, Generic[Input, Output]):
    <span class="cm"># 子类必须实现 invoke（抽象方法）</span>
    <span class="kw">def</span> <span class="fn">invoke</span>(self, input: Input, config=None) -> Output: ...
    <span class="kw">def</span> <span class="fn">stream</span>(self, input, config=None): ...
    <span class="kw">def</span> <span class="fn">batch</span>(self, inputs, config=None): ...
    <span class="cm"># ↓ 组合的关键：重载 | 运算符</span>
    <span class="kw">def</span> <span class="fn">__or__</span>(self, other): ...   <span class="cm"># a | b</span>
    <span class="kw">def</span> <span class="fn">pipe</span>(self, *others): ...     <span class="cm"># a.pipe(b)</span>
</pre>
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  在 <span class="mono">runnables/base.py</span> 里（行号会随版本变动，按方法名定位最稳）：
  <ul>
    <li><span class="mono">class Runnable(ABC, Generic[Input, Output])</span> —— 泛型基类，规定"输入类型→输出类型"。</li>
    <li><span class="mono">invoke</span> 是<strong>抽象方法</strong>：每个具体组件必须自己实现"输入怎么变输出"。</li>
    <li><span class="mono">__or__</span> 与 <span class="mono">pipe</span> 实现了 <span class="mono">|</span> 拼接（下一课详解）。</li>
    <li><span class="mono">stream</span> / <span class="mono">batch</span> 有<strong>默认实现</strong>：即使组件只写了 <span class="mono">invoke</span>，也能"免费"获得批量与（退化的）流式能力。</li>
  </ul>
</div>

<h2>LCEL：用 | 把组件拼成链</h2>
<p>因为人人都是 Runnable，你可以像 Unix 管道一样用 <span class="inline">|</span> 把它们串起来。
这套语法叫 <strong>LCEL（LangChain Expression Language）</strong>：</p>

<pre class="code"><span class="cm"># 提示词 → 模型 → 输出解析器，全是 Runnable，用 | 串起来</span>
chain = prompt | model | parser
result = chain.invoke({<span class="st">"city"</span>: <span class="st">"北京"</span>})
</pre>

<div class="flow">
  <div class="node">输入 dict</div>
  <div class="arrow">→</div>
  <div class="node hl">prompt</div>
  <div class="arrow">→</div>
  <div class="node hl">model</div>
  <div class="arrow">→</div>
  <div class="node hl">parser</div>
  <div class="arrow">→</div>
  <div class="node">输出 str</div>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解：为什么这个抽象如此强大？</div>
  <ul>
    <li><strong>统一</strong>：学一次 invoke/stream/batch，所有组件都会用。</li>
    <li><strong>可组合</strong>：任意 Runnable 用 <span class="mono">|</span> 拼接，拼出来的链<strong>本身还是一个 Runnable</strong>（可继续拼）。</li>
    <li><strong>能力免费继承</strong>：你拼出的链<strong>自动获得</strong>流式、批量、异步、回调追踪——不用一行额外代码。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Runnable 是 LangChain 的<strong>统一抽象</strong>：模型/提示/工具/解析器都是它。</li>
    <li>统一接口 = <span class="mono">invoke / stream / batch</span>（+ 异步版）；<span class="mono">invoke</span> 是抽象方法，其余有默认实现。</li>
    <li><span class="mono">|</span>（<span class="mono">__or__</span>）把组件拼成链，这套语法叫 <strong>LCEL</strong>；链本身也是 Runnable。</li>
    <li>下一课：看 <span class="mono">|</span> 拼出来的到底是什么对象，以及顺序/并行两种组合。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_09 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
上一课我们用 <span class="inline">a | b | c</span> 拼了链。那么——<strong>拼出来的到底是什么？</strong>
答案是一个 <span class="inline">RunnableSequence</span> 对象。这一课拆解"顺序"与"并行"两种核心组合，
以及几个最常用的"胶水" Runnable。
</p>

<div class="card analogy">
  <div class="tag">🏭 生活类比</div>
  <strong>顺序组合</strong>像<strong>流水线</strong>：上一站的产出是下一站的原料，一站接一站。
  <strong>并行组合</strong>像<strong>多个窗口同时办理</strong>：同一份输入分发给几条线<strong>同时</strong>处理，最后把各自结果汇总成一张表。
</div>

<h2>顺序组合：RunnableSequence</h2>
<p>当你写 <span class="inline">a | b | c</span>，<span class="inline">__or__</span> 会把它们打包成一个
<span class="inline">RunnableSequence</span>。它的 <span class="inline">invoke</span> 做的事极其朴素——<strong>依次调用、首尾相接</strong>：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/runnables/base.py</span><span class="ln">class RunnableSequence</span></div>
<pre><span class="kw">class</span> <span class="fn">RunnableSequence</span>(RunnableSerializable):
    <span class="kw">def</span> <span class="fn">invoke</span>(self, input, config=None):
        <span class="kw">for</span> step <span class="kw">in</span> self.steps:        <span class="cm"># 依次跑每一步</span>
            input = step.invoke(input)   <span class="cm"># 上一步输出 = 下一步输入</span>
        <span class="kw">return</span> input
</pre>
</div>

<div class="flow">
  <div class="node">input</div><div class="arrow">→</div>
  <div class="node hl">step1</div><div class="arrow">→</div>
  <div class="node hl">step2</div><div class="arrow">→</div>
  <div class="node hl">step3</div><div class="arrow">→</div>
  <div class="node">output</div>
</div>

<h2>并行组合：RunnableParallel</h2>
<p>当你把<strong>一个字典</strong>放进链里（值都是 Runnable），就得到 <span class="inline">RunnableParallel</span>：
同一份输入<strong>同时</strong>喂给每个分支，结果合并成一个字典。</p>

<pre class="code"><span class="kw">from</span> langchain_core.runnables <span class="kw">import</span> RunnableParallel

parallel = RunnableParallel(
    weather=get_weather_chain,   <span class="cm"># 分支 1</span>
    news=get_news_chain,         <span class="cm"># 分支 2</span>
)
parallel.invoke(<span class="st">"北京"</span>)
<span class="cm"># → {"weather": ..., "news": ...}  两条分支并发执行</span>
</pre>

<div class="flow" style="flex-direction:column;gap:.6rem;align-items:center">
  <div class="node hl" style="flex:0 0 auto">同一份 input</div>
  <div class="arrow" style="transform:rotate(90deg)">→</div>
  <div style="display:flex;gap:1rem">
    <div class="node">分支 weather</div>
    <div class="node">分支 news</div>
  </div>
  <div class="arrow" style="transform:rotate(90deg)">→</div>
  <div class="node hl" style="flex:0 0 auto">合并成 {weather, news}</div>
</div>

<h2>两个最常用的"胶水"</h2>
<div class="cols">
  <div class="col">
    <h4>RunnableLambda</h4>
    <p>把<strong>任意普通函数</strong>变成 Runnable，好塞进链里。</p>
    <pre class="code" style="margin:.4rem 0"><span class="kw">from</span> langchain_core.runnables <span class="kw">import</span> RunnableLambda
upper = RunnableLambda(<span class="kw">lambda</span> x: x.upper())
chain = upper | model</pre>
  </div>
  <div class="col">
    <h4>RunnablePassthrough</h4>
    <p>原样透传输入，常用于"<strong>保留原值 + 旁加一个新字段</strong>"。</p>
    <pre class="code" style="margin:.4rem 0"><span class="kw">from</span> langchain_core.runnables <span class="kw">import</span> RunnablePassthrough
RunnablePassthrough.assign(
  weather=get_weather_chain)</pre>
  </div>
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  全部在 <span class="mono">core/langchain_core/runnables/</span> 下：
  <table class="t" style="margin-top:.6rem">
    <tr><th>类</th><th>文件</th><th>作用</th></tr>
    <tr><td class="mono">RunnableSequence</td><td class="mono">base.py</td><td>顺序（<span class="mono">|</span> 的产物）</td></tr>
    <tr><td class="mono">RunnableParallel</td><td class="mono">base.py</td><td>并行（别名 <span class="mono">RunnableMap</span>）</td></tr>
    <tr><td class="mono">RunnableLambda</td><td class="mono">base.py</td><td>包装函数</td></tr>
    <tr><td class="mono">RunnablePassthrough</td><td class="mono">passthrough.py</td><td>透传 / assign</td></tr>
  </table>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  所有复杂的"链"，本质都是这几种基础 Runnable 的<strong>嵌套套娃</strong>：
  顺序里套并行、并行的分支里又是顺序……因为<strong>组合的产物还是 Runnable</strong>，
  所以可以无限拼下去，且整体永远支持 invoke/stream/batch。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">a | b | c</span> 的产物是 <span class="mono">RunnableSequence</span>，invoke = 依次调用、首尾相接。</li>
    <li>字典形式得到 <span class="mono">RunnableParallel</span>：同输入并发多分支，输出合并为字典。</li>
    <li><span class="mono">RunnableLambda</span>（包函数）和 <span class="mono">RunnablePassthrough</span>（透传/assign）是最常用胶水。</li>
    <li>下一课：深入聊天模型的 <span class="mono">invoke</span> 内部，看那条完整调用链。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_10 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 3 课我们鸟瞰过"一次调用的生命周期"。现在放大到<strong>聊天模型内部</strong>，
逐方法追踪 <span class="inline">model.invoke(...)</span> 真正经过的调用链——这是理解"统一接口 + 厂商实现"分工的关键。
</p>

<div class="card analogy">
  <div class="tag">🏛️ 生活类比</div>
  把 <span class="mono">BaseChatModel</span> 想成<strong>政务大厅的标准办事流程</strong>：取号、填表、缓存查重、记录档案——
  这些<strong>通用步骤对所有窗口都一样</strong>（写在地基层）。只有最后"具体盖哪个部门的章"
  （<span class="mono">_generate</span>）才由各窗口（各厂商）自己实现。
</div>

<h2>调用链：从 invoke 到厂商实现</h2>
<p>一条 <span class="inline">invoke</span> 会层层下钻，最终落到每个厂商<strong>各自实现的</strong> <span class="inline">_generate</span>：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>invoke()</h4>
    <p>统一入口。把你的输入规整成消息，调用 <span class="mono">generate_prompt</span>。</p>
    <p class="mono">BaseChatModel.invoke</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>generate_prompt() → generate()</h4>
    <p>组织本次调用：准备回调管理器、合并参数。<span class="mono">generate</span> 是处理一批输入的模板方法。</p>
    <p class="mono">generate_prompt → generate</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>_generate_with_cache()</h4>
    <p>缓存包装层：先查缓存，命中就直接返回；未命中才真正请求，拿到结果后写入缓存。</p>
    <p class="mono">_generate_with_cache</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>_generate()　← 厂商在这里实现</h4>
    <p><strong>抽象方法</strong>。<span class="mono">ChatOpenAI</span> / <span class="mono">ChatAnthropic</span> 各自实现：
      翻译成厂商格式、发 HTTP、把响应转回 <span class="mono">ChatResult</span>（内含 AIMessage）。</p>
    <p class="mono">ChatOpenAI._generate（集成层）</p></div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/language_models/chat_models.py</span><span class="ln">分工示意</span></div>
<pre><span class="kw">class</span> <span class="fn">BaseChatModel</span>(BaseLanguageModel, ABC):
    <span class="kw">def</span> <span class="fn">invoke</span>(self, input, config=None) -> AIMessage:
        <span class="cm"># 规整输入 → generate_prompt → generate</span>
        ...
    <span class="kw">def</span> <span class="fn">_generate_with_cache</span>(self, messages, ...) -> ChatResult:
        <span class="cm"># 查缓存；未命中则调用下面的 _generate</span>
        ...
    <span class="nb">@abstractmethod</span>
    <span class="kw">def</span> <span class="fn">_generate</span>(self, messages, ...) -> ChatResult:
        <span class="cm"># ★ 由每个厂商子类实现（OpenAI / Anthropic / ...）</span>
        ...
</pre>
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  全部位于地基层 <span class="mono">core/language_models/chat_models.py</span>（用方法名定位）：
  <table class="t" style="margin-top:.6rem">
    <tr><th>方法</th><th>角色</th></tr>
    <tr><td class="mono">invoke</td><td>统一入口，返回单条 AIMessage</td></tr>
    <tr><td class="mono">generate_prompt / generate</td><td>模板流程：回调、批处理、参数合并</td></tr>
    <tr><td class="mono">_generate_with_cache</td><td>缓存层（命中即返回）</td></tr>
    <tr><td class="mono">_generate（abstract）</td><td>厂商各自实现，真正发请求</td></tr>
  </table>
  返回值类型 <span class="mono">ChatResult</span> 来自 <span class="mono">core/outputs/</span>，里面包着 AIMessage。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解：模板方法模式</div>
  这是经典的<strong>"模板方法"设计模式</strong>：地基层把<strong>不变的流程</strong>
  （缓存、回调、重试、批处理）写死成模板，把<strong>会变的那一步</strong>（怎么和具体厂商对话）
  留成抽象方法 <span class="mono">_generate</span> 交给子类。<br>
  这正是<strong>第 2 课"三层架构"在方法级别的体现</strong>：要支持新厂商，只需在集成层实现一个 <span class="mono">_generate</span>。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>调用链：<span class="mono">invoke → generate_prompt → generate → _generate_with_cache → _generate</span>。</li>
    <li>前几步是<strong>所有厂商共享</strong>的模板（缓存/回调/重试）；只有 <span class="mono">_generate</span> 由厂商各自实现。</li>
    <li>这是"模板方法模式"，也是三层架构在代码里的落点。</li>
    <li>下一课：工具调用在内部如何完成"函数 → schema → tool_calls → 执行"。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_11 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 6 课你学会了用 <span class="inline">@tool</span>。这一课深入源码，看清楚两件"魔法"到底怎么发生：
<strong>① 你的函数怎么变成模型能读的 JSON Schema</strong>，<strong>② 模型返回的 tool_calls 怎么被解析和执行</strong>。
</p>

<div class="card analogy">
  <div class="tag">🌐 生活类比</div>
  你的 Python 函数说"中文"，大模型 API 只认"JSON 方言"。这中间需要一个<strong>翻译官</strong>：
  去程把函数签名翻成 JSON Schema 给模型看，回程把模型说的"我要调这个函数、参数是这些"翻回成你能执行的调用。
  这两段翻译，就是工具机制的核心。
</div>

<h2>去程：函数 → JSON Schema</h2>
<p>当你 <span class="inline">@tool</span> 一个函数，<span class="inline">StructuredTool</span> 会用
<span class="inline">create_schema_from_function</span> 读取<strong>函数签名 + 类型注解 + docstring</strong>，
自动生成一个 pydantic schema：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/tools/structured.py</span><span class="ln">推断 schema</span></div>
<pre><span class="kw">if</span> args_schema <span class="kw">is</span> None <span class="kw">and</span> infer_schema:
    <span class="cm"># 从函数签名自动推断参数 schema</span>
    args_schema = create_schema_from_function(name, func, ...)
</pre>
</div>

<div class="flow">
  <div class="node hl"><div class="nt">Python 函数</div><div class="nd">get_weather(city: str)</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">pydantic schema</div><div class="nd">推断参数类型</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">JSON Schema</div><div class="nd">{city: {type: string}}</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">发给模型</div><div class="nd">bind_tools</div></div>
</div>

<p><span class="inline">model.bind_tools([get_weather])</span> 就是把上面生成的 JSON Schema 塞进请求，
告诉模型"你有这么个工具可用"。</p>

<h2>回程：tool_calls → 执行 → ToolMessage</h2>
<p>模型决定用工具时，会在响应里返回结构化的工具调用。partner 把它解析成
<span class="inline">AIMessage.tool_calls</span>，其中每一项是一个 <span class="inline">ToolCall</span>：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/messages/tool.py</span><span class="ln">ToolCall 结构</span></div>
<pre><span class="kw">class</span> <span class="fn">ToolCall</span>(TypedDict):
    name: str               <span class="cm"># 要调用的工具名</span>
    args: dict[str, Any]    <span class="cm"># 参数（已是 Python dict）</span>
    id: str | None          <span class="cm"># 本次调用的唯一 id</span>
</pre>
</div>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>解析</h4><p>厂商响应中的工具调用被解析成 <span class="mono">AIMessage.tool_calls = [ToolCall, ...]</span>。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>匹配</h4><p>按 <span class="mono">name</span> 找到对应的工具对象。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>执行</h4><p><span class="mono">tool.invoke(tool_call["args"])</span> 真正运行你的函数。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>封装</h4><p>结果包成 <span class="mono">ToolMessage(content=..., tool_call_id=id)</span>，用 id 与请求一一对应。</p></div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  <ul>
    <li><span class="mono">@tool</span> → <span class="mono">tools/convert.py</span>；底层 <span class="mono">StructuredTool</span> → <span class="mono">tools/structured.py</span>。</li>
    <li><span class="mono">ToolCall</span> / <span class="mono">ToolCallChunk</span> → <span class="mono">messages/tool.py</span>；<span class="mono">ToolMessage</span> 同文件。</li>
    <li>在 Agent 里，这套"匹配 + 执行 + 封装"由 LangGraph 的 <span class="mono">ToolNode</span> 节点完成（下一课）。</li>
  </ul>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  工具机制 = <strong>两段翻译 + 一个 id 配对</strong>。<span class="mono">tool_call_id</span> 像快递单号，
  保证"哪个请求对应哪个结果"不会错乱（尤其当模型一次请求<strong>多个</strong>工具时）。
  这套机制纯靠<strong>结构化消息</strong>运转——又一次印证"消息是通用货币"。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>去程：函数签名 → <span class="mono">create_schema_from_function</span> → pydantic → JSON Schema → <span class="mono">bind_tools</span>。</li>
    <li>回程：<span class="mono">AIMessage.tool_calls</span>（ToolCall）→ 匹配 → 执行 → <span class="mono">ToolMessage</span>，靠 <span class="mono">id</span> 配对。</li>
    <li>类型注解和 docstring 直接决定模型看到的工具说明，<strong>务必写好</strong>。</li>
    <li>下一课：看 Agent 把这套循环编成一张 LangGraph 状态图。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_12 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 7 课的 <span class="inline">create_agent</span> 看起来像魔法。真相是：它<strong>构建并编译了一张
LangGraph 状态图（StateGraph）</strong>。这一课拆开这张图，你会发现"Agent 循环"不过是图里的两个节点 + 几条边。
</p>

<div class="card analogy">
  <div class="tag">🗺️ 生活类比</div>
  把 Agent 想成<strong>地铁线路图</strong>：每个<strong>节点</strong>是一个站（"模型站"、"工具站"），
  <strong>边</strong>是轨道，而<strong>条件边</strong>是道岔——列车（消息状态）到了"模型站"后，
  道岔根据"有没有 tool_calls"决定开往"工具站"还是直接驶向终点。
</div>

<h2>create_agent 构建的图长这样</h2>
<p>核心就两个节点和一条会绕回去的边。请求带着 <strong>状态（messages）</strong>在图里流动：</p>

<div class="flow" style="flex-direction:column;gap:.7rem;align-items:center">
  <div class="node">START</div>
  <div class="arrow" style="transform:rotate(90deg)">→</div>
  <div class="node hl" style="min-width:220px">节点 "model"<br><span style="font-weight:400;font-size:.76rem;color:var(--muted)">调用聊天模型，产出 AIMessage</span></div>
  <div class="arrow" style="transform:rotate(90deg)">→ 条件判断 →</div>
  <div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap;justify-content:center">
    <div class="node" style="min-width:220px;border-color:var(--amber)">有 tool_calls → 节点 "tools"<br><span style="font-weight:400;font-size:.76rem;color:var(--muted)">ToolNode 执行工具 → 加 ToolMessage → <b>回到 "model"</b></span></div>
    <div class="node" style="min-width:140px;border-color:var(--accent)">无 → END</div>
  </div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">langchain_v1/langchain/agents/factory.py</span><span class="ln">构建状态图（节选）</span></div>
<pre><span class="kw">from</span> langgraph.graph.state <span class="kw">import</span> StateGraph
<span class="kw">from</span> langgraph.prebuilt.tool_node <span class="kw">import</span> ToolNode

graph = StateGraph(...)
graph.add_node(<span class="st">"model"</span>, model_node)        <span class="cm"># 模型节点</span>
graph.add_node(<span class="st">"tools"</span>, tool_node)        <span class="cm"># 工具节点（ToolNode）</span>
graph.add_edge(START, <span class="st">"model"</span>)             <span class="cm"># 入口 → model</span>
graph.add_conditional_edges(<span class="st">"model"</span>, ...)   <span class="cm"># model → tools 或 END</span>
graph.add_conditional_edges(<span class="st">"tools"</span>, ...)   <span class="cm"># tools → 回到 model（或退出）</span>
<span class="kw">return</span> graph.compile(...)               <span class="cm"># 编译成 CompiledStateGraph</span>
</pre>
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  <ul>
    <li>Agent 引擎来自<strong>独立库 LangGraph</strong>（<span class="mono">langchain</span> 主力包依赖它）。
      <span class="mono">StateGraph</span>、<span class="mono">ToolNode</span> 都从 <span class="mono">langgraph</span> 导入。</li>
    <li><span class="mono">create_agent</span> 在 <span class="mono">agents/factory.py</span>：定义 <span class="mono">model_node</span>，加 <span class="mono">"model"</span>/<span class="mono">"tools"</span> 两节点，
      用 <span class="mono">add_conditional_edges</span> 接好循环，最后 <span class="mono">compile()</span>。</li>
    <li>返回的 <span class="mono">CompiledStateGraph</span> <strong>本身也是一个 Runnable</strong>——所以你能对它
      <span class="mono">invoke</span>/<span class="mono">stream</span>（呼应第 8 课）。</li>
  </ul>
</div>

<h2>状态：在节点间流动的是什么？</h2>
<p>图里流动的不是裸消息，而是 <span class="inline">AgentState</span>——一个至少含 <span class="inline">messages</span> 键的状态字典。
每个节点读取它、产出新消息追加进去：</p>
<pre class="code"><span class="cm"># 你 invoke 的就是这个 state</span>
{<span class="st">"messages"</span>: [HumanMessage(...), AIMessage(...), ToolMessage(...), ...]}
<span class="cm"># model 节点追加 AIMessage；tools 节点追加 ToolMessage</span>
</pre>

<h2>middleware：在循环里插钩子</h2>
<p>第 7 课签名里的 <span class="inline">middleware</span> 参数，就是往这张图里<strong>插入额外节点/包裹逻辑</strong>的机制——
可在"调用模型前后"做拦截（如改写请求、人审、日志）。它让 Agent 行为可扩展而无需改核心循环。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <ul>
    <li><strong>Agent 不是黑魔法，是一张图</strong>：节点("model"/"tools") + 条件边(看 tool_calls) = 自动循环。</li>
    <li>LangChain 负责<strong>"组装"</strong>这张图（把模型、工具、中间件接成节点和边），
      LangGraph 负责<strong>"运行"</strong>这张图（状态在节点间流转、支持持久化/中断）。</li>
    <li>因为编译产物是 Runnable，整个 Agent 自动获得 stream/批处理/回调等能力。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">create_agent</span> = 构建并编译一张 LangGraph <span class="mono">StateGraph</span>。</li>
    <li>两个节点：<span class="mono">"model"</span>（调模型）、<span class="mono">"tools"</span>（ToolNode 执行工具）；条件边按 <span class="mono">tool_calls</span> 决定走向。</li>
    <li>流动的状态是 <span class="mono">AgentState</span>（含 <span class="mono">messages</span>）；<span class="mono">middleware</span> 可在循环中插钩子。</li>
    <li>编译产物是 Runnable，所以能 invoke/stream。下一课：流式与回调系统。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_13 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
最后一块内部机制：<strong>流式输出（Streaming）</strong>与<strong>回调（Callbacks）</strong>。
前者让你"边生成边显示"，后者是 LangSmith 追踪、日志、监控的底层钩子。两者都贯穿前面所有组件。
</p>

<div class="card analogy">
  <div class="tag">📺 生活类比</div>
  <strong>Streaming</strong> 像<strong>直播</strong>：不必等整集拍完，画面一帧帧实时推送。
  <strong>Callbacks</strong> 像<strong>赛事解说</strong>：在"比赛开始 / 进球 / 结束"等关键时刻自动播报，
  你可以挂上任意多位解说员（处理器），各做各的记录。
</div>

<h2>Streaming：chunk 是可以相加的</h2>
<p><span class="inline">stream()</span> 不返回完整结果，而是不断 yield <span class="inline">AIMessageChunk</span>。
关键设计：<strong>这些 chunk 能用 <span class="mono">+</span> 累加</strong>，拼回一条完整消息：</p>

<pre class="code">full = None
<span class="kw">for</span> chunk <span class="kw">in</span> model.stream(<span class="st">"讲个故事"</span>):
    print(chunk.content, end=<span class="st">""</span>)   <span class="cm"># 实时显示</span>
    full = chunk <span class="kw">if</span> full <span class="kw">is</span> None <span class="kw">else</span> full + chunk  <span class="cm"># ★ chunk 相加</span>
<span class="cm"># 循环结束后，full 等价于一次性 invoke 的完整 AIMessage</span>
</pre>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  <ul>
    <li><span class="mono">stream</span> 定义在 <span class="mono">core/language_models/chat_models.py</span>；
      产出的 <span class="mono">AIMessageChunk</span> 在 <span class="mono">messages/ai.py</span>（继承 <span class="mono">BaseMessageChunk</span>）。</li>
    <li><span class="mono">+</span> 能相加，是因为 <span class="mono">BaseMessageChunk</span> 实现了 <span class="mono">__add__</span>（合并内容、工具调用片段、用量）。</li>
    <li>辅助函数 <span class="mono">generate_from_stream</span>（同文件）把一串 chunk 归并成最终 <span class="mono">ChatResult</span>。</li>
  </ul>
</div>

<h2>Callbacks：在生命周期关键点挂钩子</h2>
<p>还记得第 3 课"沿途触发回调"吗？回调系统在每次调用的关键时刻发出事件，
你可以注册处理器来响应。最常见的用途就是 <strong>LangSmith 追踪</strong>。</p>

<div class="flow">
  <div class="node hl"><div class="nt">on_llm_start</div><div class="nd">开始调用模型</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">on_llm_new_token</div><div class="nd">每来一个 token<br>（流式）</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">on_llm_end</div><div class="nd">调用结束<br>（含用量）</div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/callbacks/</span><span class="ln">BaseCallbackHandler（示意）</span></div>
<pre><span class="kw">class</span> <span class="fn">BaseCallbackHandler</span>:
    <span class="kw">def</span> <span class="fn">on_llm_start</span>(self, ...): ...        <span class="cm"># 模型开始</span>
    <span class="kw">def</span> <span class="fn">on_llm_new_token</span>(self, token, ...): ...  <span class="cm"># 流式逐 token</span>
    <span class="kw">def</span> <span class="fn">on_llm_end</span>(self, response, ...): ...     <span class="cm"># 模型结束</span>
    <span class="kw">def</span> <span class="fn">on_tool_start</span>/<span class="fn">on_tool_end</span>(self, ...): ...  <span class="cm"># 工具事件</span>
</pre>
</div>

<h2>config：回调/标签如何传进去</h2>
<p>回调、标签（tags）、元数据通过 <span class="inline">RunnableConfig</span> 这个配置字典在调用时一路传递。
这就是第 8 课 <span class="mono">invoke(input, config)</span> 里 <span class="inline">config</span> 参数的用途：</p>
<pre class="code">model.invoke(<span class="st">"你好"</span>, config={
    <span class="st">"callbacks"</span>: [MyHandler()],
    <span class="st">"tags"</span>: [<span class="st">"demo"</span>],
    <span class="st">"metadata"</span>: {<span class="st">"user"</span>: <span class="st">"alice"</span>},
})
</pre>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <ul>
    <li><strong>Streaming 与 Callbacks 是横切能力</strong>：因为一切都是 Runnable，它们对模型、链、Agent <strong>一视同仁</strong>地生效。</li>
    <li>更细粒度的 <span class="mono">astream_events</span>（<span class="mono">runnables/base.py</span>）能让你订阅<strong>链中每一步</strong>的事件流，是构建复杂 UI（如显示 Agent 思考过程）的基础。</li>
    <li><span class="mono">RunnableConfig</span> 是"随调用流动的上下文信封"，把回调/标签/并发度一路带到底层。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Streaming：<span class="mono">stream()</span> 产出可相加的 <span class="mono">AIMessageChunk</span>，累加即得完整消息。</li>
    <li>Callbacks：在 <span class="mono">on_llm_start / new_token / end</span> 等生命周期点触发，支撑追踪与监控。</li>
    <li>两者通过 <span class="mono">RunnableConfig</span> 注入，且对所有 Runnable 通用。</li>
    <li><strong>第三部分（内部源码）到此结束</strong>。最后一部分教你如何读源码、调试、测试与贡献。</li>
  </ul>
</div>
"""
