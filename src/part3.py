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

<h2>谁是 Runnable？（几乎全员）</h2>
<p>下面这些你已经用过的东西，<strong>本质都是 Runnable</strong>，所以都能 invoke、都能用 <span class="inline">|</span> 拼接：</p>
<table class="t">
  <tr><th>组件</th><th>输入 → 输出</th></tr>
  <tr><td class="mono">ChatModel</td><td>消息列表 → AIMessage</td></tr>
  <tr><td class="mono">PromptTemplate</td><td>变量 dict → 提示词 / 消息</td></tr>
  <tr><td class="mono">OutputParser</td><td>AIMessage → 结构化数据</td></tr>
  <tr><td class="mono">Tool</td><td>参数 dict → 工具结果</td></tr>
  <tr><td class="mono">RunnableSequence / Parallel</td><td>组合本身也是 Runnable</td></tr>
  <tr><td class="mono">create_agent 的产物</td><td>状态 → 状态（也是 Runnable！）</td></tr>
</table>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入三个关键设计。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 只实现 invoke，为什么就"免费"获得 stream / batch <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 默认实现的思路</div>
      <div class="a">
<pre class="code"><span class="cm"># 基类 Runnable 里（概念示意）：</span>
<span class="kw">def</span> <span class="fn">batch</span>(self, inputs):
    <span class="kw">return</span> [self.invoke(x) <span class="kw">for</span> x <span class="kw">in</span> inputs]   <span class="cm"># 用线程池并发</span>

<span class="kw">def</span> <span class="fn">stream</span>(self, input):
    <span class="kw">yield</span> self.invoke(input)   <span class="cm"># 退化：一次性产出一块</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这样设计</div>
      <div class="a">子类<strong>只需实现一个</strong> <span class="mono">invoke</span>，就立刻拥有可用的 batch / stream。
        想要更好的体验（如真正逐 token 流式），子类可以<strong>重写</strong> <span class="mono">stream</span>（聊天模型就是这么做的）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">降低实现新组件的门槛（最少只写一个方法），又保留按需优化的空间——这是"默认实现 + 可重写"的经典模板设计。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> a | b 背后：__or__ 到底返回了什么 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 等价写法</div>
      <div class="a">
<pre class="code">chain = prompt | model | parser
<span class="cm"># 等价于：</span>
chain = prompt.pipe(model).pipe(parser)
<span class="cm"># 两者都得到一个 RunnableSequence（第 9 课详解）</span>
<span class="kw">type</span>(chain)   <span class="cm"># RunnableSequence</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么用运算符重载</div>
      <div class="a">Python 的 <span class="mono">__or__</span> 让你能像 Unix 管道 <span class="mono">cmd1 | cmd2</span> 那样表达数据流，
        读起来就是"从左流到右"，比嵌套函数调用直观得多。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">声明式、可读性强；而且产物仍是 Runnable，可继续 <span class="mono">|</span> 下去，无限组合。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> config 参数：贯穿整条链的"上下文信封" <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 RunnableConfig 携带什么</div>
      <div class="a">
<pre class="code">chain.invoke(x, config={
    <span class="st">"callbacks"</span>: [...],       <span class="cm"># 回调/追踪（第 14 课）</span>
    <span class="st">"tags"</span>: [<span class="st">"prod"</span>],         <span class="cm"># 给这次运行打标签</span>
    <span class="st">"metadata"</span>: {<span class="st">"uid"</span>: 1},   <span class="cm"># 自定义元数据</span>
    <span class="st">"max_concurrency"</span>: 5,    <span class="cm"># 并发上限</span>
})</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">链里有很多步，你需要一种方式把"回调、标签、并发度"等<strong>一次性传到每一步</strong>，
        而不是层层手动透传。<span class="mono">config</span> 就是这个自动随调用流动的信封。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">定义在 <span class="mono">runnables/config.py</span> 的 <span class="mono">RunnableConfig</span>，对所有 Runnable 通用；
        追踪、限流、命名一处设置、全链生效。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 运行时重配置：configurable_fields / configurable_alternatives <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 把参数/组件变成"调用时可换"</div>
      <div class="a">
<pre class="code"><span class="cm"># 把某个字段标成可在 config 里覆盖</span>
model = ChatModel(...).configurable_fields(
    temperature=ConfigurableField(id=<span class="st">"temp"</span>))
model.invoke(x, config={<span class="st">"configurable"</span>: {<span class="st">"temp"</span>: 0.9}})   <span class="cm"># 本次调用临时改</span>

<span class="cm"># 或整个组件提供备选，运行时切换</span>
chain.configurable_alternatives(ConfigurableField(<span class="st">"llm"</span>), default_key=<span class="st">"gpt"</span>, claude=other)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 它解决什么</div>
      <div class="a">同一条链，<strong>不重建</strong>就能按 <span class="mono">config["configurable"]</span> 切换模型/温度/提示等——
        多租户、A/B 实验、按请求选模型的核心手段。<span class="mono">init_chat_model(configurable_fields=...)</span> 也基于此。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">configurable_fields</span>（<span class="mono">runnables/base.py:2792</span>）/
        <span class="mono">configurable_alternatives</span>（<span class="mono">:2850</span>）；实现类在 <span class="mono">runnables/configurable.py</span>。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>只写 invoke，就免费得 stream/batch/async</strong>：默认实现 + 可重写的经典模板。</li>
    <li><strong>组合的产物还是 Runnable</strong>：所以能无限套娃，且整体自动具备全部能力。</li>
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

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入两个常见实战问题。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 一个 RAG 链如何用顺序 + 并行拼出来 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 经典 RAG 形状</div>
      <div class="a">
<pre class="code"><span class="cm"># 并行：同时"检索上下文"和"透传原问题"</span>
setup = RunnableParallel(
    context=retriever,                  <span class="cm"># 检索分支</span>
    question=RunnablePassthrough(),     <span class="cm"># 原样透传问题</span>
)
<span class="cm"># 顺序：把上一步的 dict 灌进 prompt → model → parser</span>
rag_chain = setup | prompt | model | parser</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么要并行那一步</div>
      <div class="a">prompt 需要<strong>两样东西</strong>：检索到的上下文 + 用户原问题。
        用 <span class="mono">RunnableParallel</span> 同时备齐这两者并打包成 dict，正好喂给下一步的 prompt。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">整条 RAG 用几个基础 Runnable 声明式拼出，无需手写胶水；检索与透传<strong>并发</strong>执行，更快。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> RunnableLambda vs RunnablePassthrough，别搞混 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 区别</div>
      <div class="a">
<pre class="code">RunnableLambda(f)            <span class="cm"># 把输入"变形"：output = f(input)</span>
RunnablePassthrough()        <span class="cm"># 原样透传：output = input</span>
RunnablePassthrough.assign(  <span class="cm"># 保留原 dict，再"旁加"一个新字段</span>
    extra=some_runnable)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 各自解决什么</div>
      <div class="a"><span class="mono">Lambda</span> 用于"我要对数据做个小处理再往下传"；
        <span class="mono">Passthrough</span> 用于"这一步我啥也不改，只是占位/保留"；
        <span class="mono">assign</span> 用于"保留已有字段的同时再算一个新字段"（RAG 里常见）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 记忆法</div>
      <div class="a">Lambda=变；Passthrough=不变；assign=加。三个胶水覆盖了链里 90% 的"数据搬运"需求。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> RunnableBranch：链里的 if / else 条件路由 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 按条件走不同分支</div>
      <div class="a">前面的组合都是"固定流程"。要根据输入<strong>动态选路</strong>，用 <span class="mono">RunnableBranch</span>：
<pre class="code"><span class="kw">from</span> langchain_core.runnables <span class="kw">import</span> RunnableBranch

chain = RunnableBranch(
    (<span class="kw">lambda</span> x: <span class="st">"代码"</span> <span class="kw">in</span> x[<span class="st">"q"</span>], code_chain),    <span class="cm"># 条件 → 分支</span>
    (<span class="kw">lambda</span> x: <span class="st">"翻译"</span> <span class="kw">in</span> x[<span class="st">"q"</span>], translate_chain),
    default_chain,                                  <span class="cm"># 都不满足 → 兜底</span>
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 它解决什么</div>
      <div class="a">同一个入口，按内容<strong>分流到不同子链</strong>（如"问代码走代码链、问翻译走翻译链"）。
        每个 <span class="mono">(条件, 分支)</span> 依次判断，命中即走该分支；都不中走 <span class="mono">default</span>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">RunnableBranch</span> 在 <span class="mono">core/runnables/branch.py:42</span>，本身也是 Runnable——
        所以条件路由也能无缝拼进更大的链。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li>再复杂的链都只是几种基础 Runnable 的<strong>套娃</strong>：顺序里套并行、并行里套顺序、再加条件路由。</li>
    <li>因为产物仍是 Runnable，<strong>组合没有尽头</strong>，invoke/stream/batch 永远可用。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">a | b | c</span> 的产物是 <span class="mono">RunnableSequence</span>，invoke = 依次调用、首尾相接。</li>
    <li>字典形式得到 <span class="mono">RunnableParallel</span>：同输入并发多分支，输出合并为字典。</li>
    <li><span class="mono">RunnableLambda</span>（包函数）和 <span class="mono">RunnablePassthrough</span>（透传/assign）是最常用胶水；<span class="mono">RunnableBranch</span> 做条件路由。</li>
    <li>下一课：补上 LCEL 的第三块拼图——<strong>输出解析器</strong>，把模型输出变成程序能用的数据。</li>
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

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入两个内部细节。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 缓存命中时，整条链路怎么"抄近道" <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 命中 vs 未命中</div>
      <div class="a">
<pre class="code">_generate_with_cache(messages):
    key = hash(messages + 参数)
    <span class="kw">if</span> 缓存有 key:
        <span class="kw">return</span> 缓存值        <span class="cm"># ← 命中：根本不调 _generate、不发 HTTP</span>
    result = self._generate(...)  <span class="cm"># 未命中：才真正请求厂商</span>
    缓存[key] = result
    <span class="kw">return</span> result</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么放在这一层</div>
      <div class="a">缓存逻辑对所有厂商一致，放在 <span class="mono">_generate</span> 的<strong>外面一层</strong>，
        就能让任何 partner 自动获得缓存能力，partner 作者无需关心。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">重复问题零成本、零延迟返回；开/关缓存只是给模型传一个 <span class="mono">cache</span>，业务代码不变。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 回调是在调用链的哪些点触发的 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 触发时机</div>
      <div class="a">
<pre class="code">generate:
    on_llm_start(...)            <span class="cm"># 调用前</span>
    try:
        result = _generate_with_cache(...)
    except e:
        on_llm_error(e)          <span class="cm"># 出错时</span>
    on_llm_end(result)           <span class="cm"># 调用后（含 token 用量）</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么由模板层统一触发</div>
      <div class="a">这样无论哪个厂商、无论命中缓存与否，<strong>事件序列都一致</strong>，
        LangSmith 等追踪工具才能可靠地记录每一次模型调用（第 14 课）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">观测能力对所有模型一视同仁；partner 只管发请求，"何时上报"由通用流程负责。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>模板方法模式</strong>：通用流程（缓存/回调/重试）写一次、所有厂商共享，只留 <span class="mono">_generate</span> 抽象。</li>
    <li>这正是三层架构在<strong>方法级</strong>的落点——加新厂商只需实现一个方法。</li>
  </ul>
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

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入两个内部机制。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 类型注解是怎么变成 JSON Schema 的 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 映射关系</div>
      <div class="a"><span class="mono">create_schema_from_function</span> 读取签名，把 Python 类型映射成 JSON Schema 类型：
<pre class="code">city: str         → {<span class="st">"type"</span>: <span class="st">"string"</span>}
count: int        → {<span class="st">"type"</span>: <span class="st">"integer"</span>}
ratio: float      → {<span class="st">"type"</span>: <span class="st">"number"</span>}
tags: list[str]   → {<span class="st">"type"</span>: <span class="st">"array"</span>, <span class="st">"items"</span>: {<span class="st">"type"</span>: <span class="st">"string"</span>}}
<span class="cm"># 没有默认值的参数 → required；docstring → description</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么用 pydantic 当中间层</div>
      <div class="a">pydantic 既能<strong>生成</strong> JSON Schema（给模型看），又能在执行时<strong>校验</strong>模型传回的参数
        （类型不对就报错）。一举两得，避免脏参数进入你的函数。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">你只写普通类型注解，schema 生成与参数校验全自动；想更精细时再用显式 <span class="mono">args_schema</span>。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 流式下工具参数是"碎着来"的：ToolCallChunk <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 为什么会有 ToolCallChunk</div>
      <div class="a">流式输出时，模型生成的工具参数 JSON 是<strong>一段段</strong>吐出来的（如 <span class="mono">{"ci</span> … <span class="mono">ty": "北</span> … <span class="mono">京"}</span>）。
        每一段是一个 <span class="mono">ToolCallChunk</span>，累加后才拼成完整的 <span class="mono">ToolCall</span>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">要在 UI 上"边生成边显示工具调用"，就不能等参数全部到齐。分块 + 累加让你能实时呈现，
        最终再得到可执行的完整调用。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">ToolCall</span> 与 <span class="mono">ToolCallChunk</span> 都在 <span class="mono">messages/tool.py</span>；
        chunk 的累加规则与第 14 课的 <span class="mono">AIMessageChunk</span> 相加是同一套思路。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 参数校验失败会怎样：错误如何"回灌"给模型 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 失败路径</div>
      <div class="a">模型偶尔会传回<strong>不合法的参数</strong>（类型不对、缺必填项）。pydantic 校验不过 → 抛
        <span class="mono">ValidationError</span>。默认情况下 <span class="mono">ToolNode</span>（<span class="mono">handle_tool_errors</span> 默认开启）会<strong>捕获</strong>它，
        把错误信息包成一条 <span class="mono">ToolMessage</span>（<span class="mono">status="error"</span>）追加回对话——<strong>而不是让程序崩溃</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 然后呢：模型会自我纠正</div>
      <div class="a">这条错误 <span class="mono">ToolMessage</span> 回灌后，Agent 循环把它当作新的"观察"喂给模型，
        模型通常会<strong>读懂报错、改对参数再调一次</strong>——这正是 Agent "试错 → 纠正"能力的来源。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 可配置 / 可加固</div>
      <div class="a">行为由 <span class="mono">ToolNode(handle_tool_errors=...)</span> 控制（<span class="mono">langgraph.prebuilt</span>）：可用默认提示、自定义错误文案，或关掉直接抛。
        还有现成的 <span class="mono">ToolRetryMiddleware</span> 能在工具抖动时自动重试（见第 7 课）。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>两段翻译 + id 配对</strong>：函数 ↔ JSON 全自动，pydantic 既生成 schema 又校验参数。</li>
    <li><strong>ToolCallChunk 可累加</strong>：流式下工具参数碎着来，也能拼回完整调用。</li>
  </ul>
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
    <li>Agent 引擎来自<strong>独立库 LangGraph</strong>——它是<strong>另一个仓库</strong>（<span class="mono">langchain-ai/langgraph</span>），
      <strong>不在</strong>你一直读的 langchain monorepo 的 <span class="mono">libs/</span> 里；<span class="mono">langchain</span> 主力包<strong>依赖</strong>它。
      <span class="mono">StateGraph</span>、<span class="mono">ToolNode</span> 等都从 <span class="mono">langgraph</span> 导入。</li>
    <li><span class="mono">create_agent</span> 在 <span class="mono">agents/factory.py</span>：定义 <span class="mono">model_node</span>，加 <span class="mono">"model"</span>/<span class="mono">"tools"</span> 两节点，
      用 <span class="mono">add_conditional_edges</span> 接好循环，最后 <span class="mono">compile()</span>。</li>
    <li>返回的 <span class="mono">CompiledStateGraph</span> <strong>本身也是一个 Runnable</strong>——所以你能对它
      <span class="mono">invoke</span>/<span class="mono">stream</span>（呼应第 8 课）。</li>
  </ul>
</div>

<h2>create_agent 用到的 LangGraph 零件清单</h2>
<p>你问"LangGraph 的代码细节到底用了哪些"——这张表一次说清。<span class="mono">factory.py</span> 顶部就 import 了它们：</p>
<table class="t">
  <tr><th>LangGraph 零件</th><th>作用</th><th>教程位置</th></tr>
  <tr><td class="mono">StateGraph / CompiledStateGraph</td><td>定义并编译整张 Agent 图</td><td>本课</td></tr>
  <tr><td class="mono">START / END</td><td>图的入口与出口</td><td>本课流程图</td></tr>
  <tr><td class="mono">add_conditional_edges</td><td>"去 tools 还是结束"的条件路由</td><td>本课 · 深入 ①</td></tr>
  <tr><td class="mono">ToolNode</td><td>执行工具、产出 ToolMessage 的节点</td><td>第 12 课</td></tr>
  <tr><td class="mono">add_messages（reducer）</td><td>messages 的<strong>合并规则</strong>（按 id 追加/替换）</td><td>下方 ⤵</td></tr>
  <tr><td class="mono">Send</td><td><strong>并行扇出</strong>多个工具调用</td><td>本课 · 进阶 ④</td></tr>
  <tr><td class="mono">Command</td><td>状态更新 + 跳转（多 Agent <strong>handoff</strong> 的底座）</td><td>本课 · 进阶 ④ · 第 21 课</td></tr>
  <tr><td class="mono">Checkpointer / Store</td><td>持久化会话 / 长期记忆</td><td>本课 · 进阶 ①③</td></tr>
  <tr><td class="mono">interrupt</td><td>中断等人审批（HITL）</td><td>本课 · 进阶 ② · 第 7 课</td></tr>
  <tr><td class="mono">Runtime</td><td>运行时上下文（依赖注入）</td><td>第 19 课</td></tr>
</table>
<p style="color:var(--muted);font-size:.9rem">想把这些零件<strong>逐个拆到引擎层</strong>（Pregel 超步、channels、checkpoint、Send/Command 的实现）？见 <strong>第七部分 · 深入 LangGraph</strong>。</p>

<h2>状态：在节点间流动的是什么？</h2>
<p>图里流动的不是裸消息，而是 <span class="inline">AgentState</span>——一个至少含 <span class="inline">messages</span> 键的状态字典。
每个节点读取它、产出新消息追加进去：</p>
<pre class="code"><span class="cm"># 你 invoke 的就是这个 state</span>
{<span class="st">"messages"</span>: [HumanMessage(...), AIMessage(...), ToolMessage(...), ...]}
<span class="cm"># model 节点追加 AIMessage；tools 节点追加 ToolMessage</span>
</pre>

<div class="card detail">
  <div class="tag">🔬 关键细节：messages 为什么是"追加"而非"覆盖"</div>
  <p>真实定义是 <span class="mono">messages: Annotated[list[AnyMessage], add_messages]</span>（<span class="mono">agents/middleware/types.py</span>）。
  这个 <span class="mono">add_messages</span> 是 LangGraph 的 <strong>reducer（归并函数）</strong>：当节点/中间件返回
  <span class="mono">{"messages": [...]}</span> 时，框架<strong>不是覆盖</strong>旧列表，而是用它把新消息<strong>按 id 合并</strong>进去（id 相同则替换、不同则追加）。</p>
  <ul>
    <li>所以 <span class="mono">"model"</span> 节点只要 <span class="mono">return {"messages": [ai]}</span> 就能"追加一条"，不必自己拼回整段历史。</li>
    <li>想<strong>删 / 改</strong>历史？返回<strong>相同 id</strong> 的消息可替换，或用 <span class="mono">RemoveMessage</span> 删除——直接塞一个新列表是<strong>删不掉</strong>的（只会被合并进去）。</li>
    <li>这也解释了第 18 课中间件改消息为何要小心：你返回的是会被 reducer <strong>归并</strong>的"更新"，而不是整份状态。</li>
  </ul>
</div>

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

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入 Agent 内部的三个机制。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 条件边是怎么决定"去 tools 还是结束"的 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 路由函数</div>
      <div class="a">"model"节点之后挂了一个条件边，本质是一个看状态的小函数：
<pre class="code"><span class="kw">def</span> <span class="fn">should_continue</span>(state):
    last = state[<span class="st">"messages"</span>][-1]
    <span class="kw">if</span> last.tool_calls:        <span class="cm"># 模型请求了工具</span>
        <span class="kw">return</span> <span class="st">"tools"</span>         <span class="cm"># → 去 tools 节点</span>
    <span class="kw">return</span> END                <span class="cm"># → 否则结束</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么用"条件边"而不是写死</div>
      <div class="a">是否继续循环取决于<strong>运行时</strong>模型的输出，不是编译期能定的。
        条件边（<span class="mono">add_conditional_edges</span>）让图能根据当前状态<strong>动态选择</strong>下一个节点。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">循环的终止条件被清晰地表达为一条边，逻辑集中、可读；要改循环行为只需改这个路由函数。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 为什么用"图(Graph)"而不是简单 while 循环 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">❓ 图能给你什么，while 给不了</div>
      <div class="a"><strong>持久化 / 断点续跑</strong>（checkpointer：跑一半存档，之后从断点恢复）、
        <strong>中断与人审</strong>（在某节点暂停等人确认）、<strong>并行分支</strong>、<strong>可视化</strong>、
        <strong>细粒度流式</strong>（按节点输出事件）。这些用裸 while 自己实现会非常复杂。</div>
    </div>
    <div class="qa">
      <div class="q">🧪 体现在签名里</div>
      <div class="a"><span class="mono">create_agent</span> 的 <span class="mono">checkpointer</span>、<span class="mono">interrupt_before/after</span>、
        <span class="mono">store</span> 等参数，正是这些图能力的开关。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点 & 🔀 其他方案</div>
      <div class="a">优点：把"有状态、可中断、可恢复的循环"标准化。其他方案：自己写 while（小场景够用，但要自己实现状态管理与持久化）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> AgentState 里除了 messages 还能放什么 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 自定义状态</div>
      <div class="a">默认状态至少含 <span class="mono">messages</span>，但你可以用 <span class="mono">state_schema</span> 扩展，
        让节点之间传递更多字段（如已检索文档、剩余预算、用户画像等）。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么需要</div>
      <div class="a">复杂 Agent 的节点常要共享"对话之外"的数据。把它们放进状态，
        就能在 model / tools / middleware 各节点间安全传递，而不必塞进消息里污染对话。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">AgentState</span> 由 <span class="mono">agents/middleware/types.py</span> 定义并从 <span class="mono">langchain.agents</span> 导出；
        <span class="mono">state_schema</span> 是 <span class="mono">create_agent</span> 的参数之一。</div>
    </div>
  </div>
</details>

<h2>🗺️ 进阶专题：状态图的高级能力</h2>
<p>create_agent 编译出的 LangGraph 图，远不止"循环"。正因为底层是<strong>图</strong>而非裸 while，
它还自带<strong>持久化、中断恢复、并行、长期记忆</strong>等生产级能力——大多通过 <span class="inline">create_agent</span> 的参数开启。</p>

<table class="t">
  <tr><th>能力</th><th>开关 / 机制</th></tr>
  <tr><td>跨请求记忆、多会话隔离</td><td class="mono">checkpointer + thread_id</td></tr>
  <tr><td>暂停 / 断点续跑（人审）</td><td class="mono">interrupt_before / interrupt_after</td></tr>
  <tr><td>跨会话的长期存储</td><td class="mono">store</td></tr>
  <tr><td>并发分支 / 子图</td><td class="mono">LangGraph 图能力</td></tr>
</table>

<h2>🔍 状态图进阶 · 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，逐个吃透高级能力。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 持久化与多会话：checkpointer + thread_id <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> langgraph.checkpoint.memory <span class="kw">import</span> InMemorySaver

agent = create_agent(model, tools, checkpointer=InMemorySaver())
<span class="cm"># 用 thread_id 区分不同用户/会话，各自的历史自动保存与恢复</span>
agent.invoke({<span class="st">"messages"</span>: [...]}, config={<span class="st">"configurable"</span>: {<span class="st">"thread_id"</span>: <span class="st">"user-1"</span>}})
agent.invoke({<span class="st">"messages"</span>: [...]}, config={<span class="st">"configurable"</span>: {<span class="st">"thread_id"</span>: <span class="st">"user-1"</span>}})  <span class="cm"># 记得上一轮</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 它解决什么</div>
      <div class="a">默认每次 <span class="mono">invoke</span> 都是<strong>全新一局</strong>。挂上 <span class="mono">checkpointer</span> 后，
        图会在每步<strong>存档状态</strong>，相同 <span class="mono">thread_id</span> 的后续调用自动<strong>接着上次</strong>跑——这就是 Agent 的"记忆"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">记忆能力是"配置项"而非手写：开发用 <span class="mono">InMemorySaver</span>，生产换成数据库版（如 Postgres），代码不变。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 中断与恢复：让图在中途暂停等人 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 机制</div>
      <div class="a"><span class="mono">interrupt_before=["tools"]</span> 让图在执行工具节点<strong>前暂停</strong>并存档，
        把控制权交还给你的程序；人确认后再 <span class="mono">invoke(None, config=...)</span> <strong>从断点继续</strong>。
        第 7 课的 <span class="mono">HumanInTheLoopMiddleware</span> 正是基于这套机制。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么只有"图"能做到</div>
      <div class="a">暂停 / 恢复要求把"执行到哪、状态是什么"完整存下来，之后精确还原。
        这正是<strong>状态图 + checkpointer</strong> 的拿手好戏；裸 while 循环很难优雅实现"跑一半存档、改天再续"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">支撑人审、审批流、超长任务分段执行等真实场景；中断期间不占用任何运行资源。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 并行、子图与长期记忆 store <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 三种进阶形态</div>
      <div class="a">
<pre class="code"><span class="cm"># 并行：图可让多个分支节点并发执行，再汇合（如同时查多个数据源）</span>
<span class="cm"># 子图：把一个编译好的 Agent 当作另一张图里的一个节点（多智能体协作）</span>
<span class="cm"># 长期记忆：store 跨会话保存知识（区别于 checkpointer 的"单会话状态"）</span>
agent = create_agent(model, tools, store=my_store)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ checkpointer 与 store 区别</div>
      <div class="a"><span class="mono">checkpointer</span> 存的是<strong>单个会话(thread)的过程状态</strong>（用于续跑/记住本轮对话）；
        <span class="mono">store</span> 存的是<strong>跨会话、跨用户的长期知识</strong>（如"这个用户的偏好"），两者互补。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点 & 🌍 收束</div>
      <div class="a">正因为 Agent 是一张<strong>可组合的图</strong>，单 Agent 能升级成<strong>多 Agent 系统</strong>（子图）、
        能并发、能记长期记忆。这就是"用图运行"相比"裸循环"的真正威力。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 控制流原语：Send（并行扇出）与 Command（跳转 / handoff） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 Send：一次请求多个工具，怎么并行</div>
      <div class="a">当一条 AIMessage 里有<strong>多个 tool_calls</strong> 时，路由不是简单返回 <span class="mono">"tools"</span>，而是给每个调用发一个 <span class="mono">Send</span>：
<pre class="code"><span class="cm"># factory.py：把 N 个工具调用并行扇出到 tools 节点</span>
<span class="kw">return</span> [Send(<span class="st">"tools"</span>, [tc]) <span class="kw">for</span> tc <span class="kw">in</span> pending_tool_calls]</pre>
        这就是"<strong>并行工具调用</strong>"的真实机制：<span class="mono">Send(node, payload)</span> 让同一个节点<strong>被并发触发多次</strong>，各跑各的、再汇合回 model。</div>
    </div>
    <div class="qa">
      <div class="q">🧪 Command：状态更新 + 跳转（多 Agent handoff）</div>
      <div class="a">普通节点返回一个 <span class="mono">dict</span> 只更新状态；返回 <span class="mono">Command</span> 则能<strong>同时</strong>"改状态 + 指定下一步去哪"：
<pre class="code"><span class="kw">from</span> langgraph.types <span class="kw">import</span> Command
<span class="kw">return</span> Command(update={<span class="st">"messages"</span>: [...]}, goto=<span class="st">"researcher"</span>)  <span class="cm"># 改状态并跳到另一个 agent</span></pre>
        多 Agent <strong>handoff</strong>（第 21 课对照 AutoGen 时提到的"交接"）正是用 <span class="mono">Command(goto=...)</span> 实现的——一个 Agent 把任务<strong>交棒</strong>给另一个。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 一句话记</div>
      <div class="a"><span class="mono">Send</span> = <strong>"分身并行"</strong>（fan-out，如多工具）；<span class="mono">Command</span> = <strong>"改状态 + 改去向"</strong>（含 handoff）。
        二者都来自 <span class="mono">langgraph.types</span>，是 LangGraph 控制流的两块基石。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>Agent 就是一张图</strong>：节点 + 条件边 = 循环；"组装(LangChain)"与"运行(LangGraph)"彻底分离。</li>
    <li>编译产物<strong>仍是 Runnable</strong>，所以 Agent 自动获得 stream/批处理/回调，还能持久化与中断。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
    <li>两个节点：<span class="mono">"model"</span>（调模型）、<span class="mono">"tools"</span>（ToolNode 执行工具）；条件边按 <span class="mono">tool_calls</span> 决定走向。</li>
    <li>流动的状态是 <span class="mono">AgentState</span>（含 <span class="mono">messages</span>，靠 <span class="mono">add_messages</span> reducer <strong>合并</strong>而非覆盖）；<span class="mono">middleware</span> 可在循环中插钩子。</li>
    <li>它<strong>直接复用 LangGraph 的零件</strong>：<span class="mono">StateGraph / ToolNode / Send（并行）/ Command（handoff）/ checkpointer / interrupt</span>——LangChain 组装、LangGraph 运行。</li>
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

<div class="card detail">
  <div class="tag">🔬 自己写一个回调处理器（10 行）</div>
  <p>不止能用官方追踪——继承 <span class="mono">BaseCallbackHandler</span>，只重写你关心的钩子即可：</p>
<pre class="code"><span class="kw">from</span> langchain_core.callbacks <span class="kw">import</span> BaseCallbackHandler

<span class="kw">class</span> <span class="fn">MyHandler</span>(BaseCallbackHandler):
    <span class="kw">def</span> <span class="fn">on_llm_start</span>(self, serialized, prompts, **kw):
        <span class="nb">print</span>(<span class="st">"→ 模型开始，prompt:"</span>, prompts[0][:30])
    <span class="kw">def</span> <span class="fn">on_llm_end</span>(self, response, **kw):
        <span class="nb">print</span>(<span class="st">"← 模型结束，用量:"</span>, response.llm_output)

<span class="cm"># 用法见下方 config={"callbacks": [MyHandler()]}</span></pre>
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

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入三个进阶话题。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> stream 与 astream_events 有什么区别 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 两种粒度</div>
      <div class="a">
<pre class="code"><span class="cm"># stream：只拿"最终输出"的逐块结果</span>
<span class="kw">for</span> chunk <span class="kw">in</span> chain.stream(x):
    ...   <span class="cm"># 通常是最后一步 parser/model 的输出块</span>

<span class="cm"># astream_events：拿"链中每一步"的事件（开始/结束/token…）</span>
<span class="kw">async</span> <span class="kw">for</span> ev <span class="kw">in</span> chain.astream_events(x):
    ev[<span class="st">"event"</span>]   <span class="cm"># on_chat_model_stream / on_tool_end / ...</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 各自用在哪</div>
      <div class="a"><span class="mono">stream</span> 够做"打字机"效果；而要展示 <strong>Agent 的思考过程</strong>
        （正在调哪个工具、检索到什么），就需要 <span class="mono">astream_events</span> 这种<strong>逐步骤</strong>事件流。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a">两者都在 <span class="mono">runnables/base.py</span>；<span class="mono">astream_events</span> 是构建复杂实时 UI 的基础。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> callbacks 与 middleware 到底有什么不同 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 一句话区分</div>
      <div class="a"><strong>callbacks = 观察</strong>（被动收到事件，做日志/追踪，不改流程）；
        <strong>middleware = 干预</strong>（主动改写请求、拦截、加节点，<strong>会改变</strong>流程，第 13 课）。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 何时用哪个</div>
      <div class="a">要"记录 / 上报 / 监控" → 用 callbacks；要"修改行为 / 加人审 / 限流" → 用 middleware。
        两者可同时存在，各司其职。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">观察与干预分离，职责清晰：观测代码不会意外改变业务流程，反之亦然。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> chunk 相加的"+"到底合并了什么 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 合并的不只是文本</div>
      <div class="a"><span class="mono">AIMessageChunk + AIMessageChunk</span> 会把<strong>正文拼接</strong>、
        <strong>工具调用片段(ToolCallChunk)拼接</strong>、<strong>token 用量累加</strong>，
        最终等价于一次性 <span class="mono">invoke</span> 拿到的完整 <span class="mono">AIMessage</span>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么要可相加</div>
      <div class="a">流式天然是"碎片化"的。让 chunk 支持 <span class="mono">+</span>，你就能一边实时显示、一边在循环里
        累加出"完整结果"，无需第二次请求。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a">由 <span class="mono">BaseMessageChunk.__add__</span>（<span class="mono">messages/ai.py</span> 等）实现；
        辅助函数 <span class="mono">generate_from_stream</span> 把整串 chunk 归并成最终结果。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> astream_events 的事件长什么样（v2 结构） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 每个事件是一个统一结构的字典</div>
      <div class="a">
<pre class="code">{
  <span class="st">"event"</span>: <span class="st">"on_chat_model_stream"</span>,   <span class="cm"># 事件类型：on_*_start/stream/end</span>
  <span class="st">"name"</span>: <span class="st">"ChatOpenAI"</span>,             <span class="cm"># 哪个组件</span>
  <span class="st">"run_id"</span>: <span class="st">"..."</span>,                  <span class="cm"># 本次运行 id（可关联父子）</span>
  <span class="st">"tags"</span>: [], <span class="st">"metadata"</span>: {},
  <span class="st">"data"</span>: {<span class="st">"chunk"</span>: AIMessageChunk(...)}  <span class="cm"># 负载（input/chunk/output）</span>
}</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么 UI 开发者需要它</div>
      <div class="a">要在界面上显示"正在调用哪个工具、模型在逐字输出什么"，就得订阅这些<strong>带类型的逐步骤事件</strong>。
        按 <span class="mono">event</span> 类型和 <span class="mono">name</span> 过滤，即可驱动"Agent 思考过程"可视化。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">StreamEvent</span> / <span class="mono">EventData</span> 在 <span class="mono">runnables/schema.py</span>（<span class="mono">StreamEvent</span> 约 :188、<span class="mono">EventData</span> :13）；
        v2 实现 <span class="mono">tracers/event_stream.py</span>。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 谁在背后上报：CallbackManager 与 LangChainTracer <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">❓ 什么是"Run / run 树"</div>
      <div class="a">每次 <span class="mono">invoke</span> 都会生成一个 <strong>Run</strong> 对象（一次可观测的执行记录）；
        链式的父子调用（链 → 模型 → 工具）层层嵌套，就形成一棵 <strong>run 树</strong>——
        也就是你在 <strong>LangSmith</strong> 里看到的那棵可展开的调用树。</div>
    </div>
    <div class="qa">
      <div class="q">🧪 事件的分发与上报链路</div>
      <div class="a">
<pre class="code">组件触发事件 → CallbackManager 把事件 fan-out 给所有已注册 handler
                              ├─ 你的日志 handler
                              └─ LangChainTracer → 上报 LangSmith（构建 run 树）</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 各自职责</div>
      <div class="a"><span class="mono">CallbackManager</span>（<span class="mono">callbacks/manager.py:1343</span>）负责"把一次事件<strong>广播</strong>给所有处理器"；
        <span class="mono">LangChainTracer</span>（<span class="mono">tracers/langchain.py:134</span>）是其中一个处理器，专门把运行树<strong>上报 LangSmith</strong>——
        这就是全书反复说的"LangSmith 追踪"的落地实现。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 进阶</div>
      <div class="a"><span class="mono">dispatch_custom_event</span>（<span class="mono">callbacks/manager.py:2705</span>）让你在自己的工具/链里<strong>发自定义事件</strong>，
        一并出现在 <span class="mono">astream_events</span> 流里。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>chunk 可相加（__add__）</strong>：流式天然碎片化，相加即还原成完整消息。</li>
    <li>Streaming/Callbacks 是<strong>横切能力</strong>，对所有 Runnable 一视同仁；<span class="mono">config</span> 是随调用流动的信封。</li>
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

# ---------------------------------------------------------------------------
LESSON_OP = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 8、9 课你反复见到 <span class="inline">prompt | model | parser</span> 这条链，但 <strong>parser（输出解析器）</strong>一直没讲。
它负责把模型吐出的"一段文本"变成<strong>程序能直接用的结构化数据</strong>——这是 LCEL 链里缺失的第三块拼图。
</p>

<div class="card analogy">
  <div class="tag">🧾 生活类比</div>
  模型像一位<strong>口述答案的专家</strong>：它说得很好，但说出来的是"一段话"。
  输出解析器就是旁边的<strong>速记员</strong>：把这段口述<strong>整理成表格/卡片/JSON</strong>，让后面的程序能直接录入、计算、入库。
</div>

<h2>为什么需要它</h2>
<p>模型 <span class="inline">invoke</span> 返回的是 <span class="inline">AIMessage</span>，其 <span class="inline">.content</span> 是<strong>字符串</strong>。
但你的程序往往需要的是 <strong>纯文本 / 字典 / 强类型对象</strong>。解析器就站在链的末尾，完成这"最后一步翻译"。</p>

<div class="flow">
  <div class="node">prompt</div><div class="arrow">→</div>
  <div class="node">model</div><div class="arrow">→</div>
  <div class="node">AIMessage<br><span style="font-weight:400;font-size:.76rem;color:var(--muted)">.content 是字符串</span></div>
  <div class="arrow">→</div>
  <div class="node hl">parser<br><span style="font-weight:400;font-size:.76rem;color:var(--muted)">→ str / dict / 对象</span></div>
</div>

<h2>三个最常用的解析器</h2>
<table class="t">
  <tr><th>解析器</th><th>把输出变成</th><th>典型场景</th></tr>
  <tr><td class="mono">StrOutputParser</td><td>纯字符串（取 <span class="mono">.content</span>）</td><td>几乎每条链的结尾</td></tr>
  <tr><td class="mono">JsonOutputParser</td><td>dict（支持流式增量）</td><td>要 JSON 结果</td></tr>
  <tr><td class="mono">PydanticOutputParser</td><td>pydantic 对象 + 校验</td><td>强类型结构化数据</td></tr>
</table>

<pre class="code"><span class="kw">from</span> langchain_core.output_parsers <span class="kw">import</span> StrOutputParser

chain = prompt | model | StrOutputParser()
text: str = chain.invoke({<span class="st">"q"</span>: <span class="st">"你好"</span>})   <span class="cm"># 直接拿到字符串，而不是 AIMessage</span>
</pre>

<div class="card key">
  <div class="tag">🔑 核心认知</div>
  <strong>解析器也是 Runnable</strong>（第 8 课）。所以它能用 <span class="inline">|</span> 接在 model 后面，
  成为链的最后一环——这就是 <span class="inline">prompt | model | parser</span> 三段式的由来。
</div>

<h2>闭环技巧：get_format_instructions</h2>
<p>解析器还能<strong>反过来生成提示</strong>：告诉模型"请按这个格式输出"，再由它自己解析回来，形成闭环：</p>
<pre class="code"><span class="kw">from</span> langchain_core.output_parsers <span class="kw">import</span> PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=Weather)

prompt = ChatPromptTemplate.from_messages([
    (<span class="st">"system"</span>, <span class="st">"{format_instructions}"</span>),   <span class="cm"># ← 把格式说明塞进提示</span>
    (<span class="st">"human"</span>, <span class="st">"{q}"</span>),
]).partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser   <span class="cm"># 模型按要求输出 → parser 解析成 Weather 对象</span>
</pre>

<h2>🔬 实现细节与亮点</h2>
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/output_parsers/base.py</span><span class="ln">BaseOutputParser 是 Runnable</span></div>
<pre><span class="kw">class</span> <span class="fn">BaseOutputParser</span>(..., Runnable[..., T]):
    <span class="kw">def</span> <span class="fn">invoke</span>(self, input, config=None):
        <span class="cm"># 取出 AIMessage.content，交给 parse()</span>
        <span class="kw">return</span> self.parse(input.content <span class="kw">if</span> isinstance(input, BaseMessage) <span class="kw">else</span> input)
    <span class="kw">def</span> <span class="fn">parse</span>(self, text: str) -> T: ...          <span class="cm"># 子类实现：文本 → 结构化</span>
    <span class="kw">def</span> <span class="fn">get_format_instructions</span>(self) -> str: ...  <span class="cm"># 反向：生成格式说明</span>
</pre>
</div>

<div class="card detail">
  <div class="tag">🔬 继承体系</div>
  <ul>
    <li><span class="mono">BaseOutputParser</span>（<span class="mono">base.py:136</span>）是 Runnable，<span class="mono">invoke</span> → <span class="mono">parse</span>。</li>
    <li><span class="mono">StrOutputParser</span>（<span class="mono">string.py:8</span>）最简单：直接返回文本。</li>
    <li><span class="mono">JsonOutputParser</span>（<span class="mono">json.py:31</span>）继承 <span class="mono">BaseCumulativeTransformOutputParser</span>——
      <strong>支持流式</strong>：边接收边解析出"部分 JSON"。</li>
    <li><span class="mono">PydanticOutputParser</span>（<span class="mono">pydantic.py:19</span>）在 Json 之上再做<strong>pydantic 校验</strong>。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>解析器是 Runnable</strong>：所以无缝拼进链，且自动获得 stream/batch/async——这是 <span class="mono">prompt|model|parser</span> 能成立的根基。</li>
    <li><strong>get_format_instructions 形成闭环</strong>：同一个 parser 既<strong>告诉模型怎么输出</strong>，又<strong>负责把输出解析回来</strong>，提示与解析两端由一个对象统一保证。</li>
    <li><strong>流式可增量解析</strong>：<span class="mono">JsonOutputParser</span> 能在 JSON 还没输出完时就给出"部分结果"，适合实时 UI。</li>
  </ul>
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，吃透解析器的取舍。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 输出解析器 vs with_structured_output，怎么选 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 两条路线</div>
      <div class="a"><strong>解析器路线</strong>：模型<strong>自由输出文本</strong> → 事后用 parser 解析（靠提示 + 解析，<strong>任何模型都能用</strong>）。
        <strong>with_structured_output 路线</strong>（第 5 课）：用工具调用 / JSON 模式<strong>强约束</strong>模型输出（更可靠，但需模型支持）。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 各自适合</div>
      <div class="a">模型不支持工具/JSON 模式，或想要更灵活的后处理 → 用<strong>解析器</strong>；
        要"几乎不会解析失败"的强保证、且模型支持 → 用 <span class="mono">with_structured_output</span>。
        二者背后都离不开 schema 约束的思想。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 关系</div>
      <div class="a">其实 <span class="mono">with_structured_output</span> 内部也用到 tool/JSON 解析器（第 11 课）。解析器是更底层、更通用的一层。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 为什么几乎每条链结尾都有 StrOutputParser <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">❓ 不加会怎样</div>
      <div class="a">不加，链的输出是 <span class="mono">AIMessage</span>（还要 <span class="mono">.content</span> 取文本）。
        加上 <span class="mono">StrOutputParser()</span>，链<strong>直接产出干净的字符串</strong>，下游（打印、拼接、再喂下一步）更顺手。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 还有一个好处</div>
      <div class="a"><span class="mono">StrOutputParser</span> 对<strong>流式</strong>友好：逐 token 产出纯文本块，正好做打字机效果（第 14 课）。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>输出解析器是 <span class="mono">prompt | model | parser</span> 的<strong>第三块拼图</strong>：把模型输出的文本变成 str / dict / 对象。</li>
    <li>三个常用：<span class="mono">StrOutputParser</span>（文本）/<span class="mono">JsonOutputParser</span>（dict，可流式）/<span class="mono">PydanticOutputParser</span>（强类型）。</li>
    <li>解析器<strong>也是 Runnable</strong>；<span class="mono">get_format_instructions</span> 让"提示↔解析"闭环。</li>
    <li>与 <span class="mono">with_structured_output</span> 互补：解析器更通用，结构化输出更强约束。</li>
    <li>下一课：深入<strong>聊天模型内部</strong>，看 <span class="mono">invoke</span> 的完整调用链。</li>
  </ul>
</div>
"""
