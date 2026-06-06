"""Content for Part 2 (user perspective): lessons 04-07."""

# ---------------------------------------------------------------------------
LESSON_04 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
进入"用户视角"，我们从最小的积木开始：<strong>消息（Message）</strong>。在 LangChain 里，
一段对话不是一坨字符串，而是<strong>一串结构化的消息对象</strong>。理解了消息，后面的模型、工具、Agent 全都顺了。
</p>

<div class="card analogy">
  <div class="tag">💬 生活类比</div>
  把对话想象成<strong>群聊记录</strong>：每条消息都标着"谁发的"。你发的标"用户"，
  机器人回的标"助手"，系统设定标"系统"，而某个被 @ 的工具返回结果标"工具"。
  LangChain 把这个"谁发的 + 发了什么"固化成不同的<strong>消息类</strong>。
</div>

<h2>四种核心消息</h2>
<p>99% 的场景你只会用到这四种。记住它们各自代表"谁在说话"：</p>

<table class="t">
  <tr><th>消息类</th><th>代表谁</th><th>典型内容</th></tr>
  <tr><td class="mono">SystemMessage</td><td>系统设定</td><td>"你是一个友好的助手"</td></tr>
  <tr><td class="mono">HumanMessage</td><td>用户（你）</td><td>"北京天气怎么样？"</td></tr>
  <tr><td class="mono">AIMessage</td><td>模型</td><td>回复正文 + 可能的工具调用</td></tr>
  <tr><td class="mono">ToolMessage</td><td>工具结果</td><td>"北京 晴 25°C"</td></tr>
</table>

<h2>它们的家谱：都继承自 BaseMessage</h2>
<p>所有消息类都从同一个基类派生。看懂这张继承图，你就知道"为什么它们用法这么一致"：</p>

<div class="flow" style="flex-direction:column;gap:.7rem">
  <div class="node hl" style="flex:0 0 auto">BaseMessage<br><span style="font-weight:400;font-size:.76rem;color:var(--muted)">公共字段：content（内容）+ 角色标识</span></div>
  <div class="arrow" style="transform:rotate(90deg)">→</div>
  <div style="display:flex;gap:.6rem;width:100%">
    <div class="node">SystemMessage</div>
    <div class="node">HumanMessage</div>
    <div class="node">AIMessage</div>
    <div class="node">ToolMessage</div>
  </div>
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  每个消息类都在 <span class="mono">langchain-core</span> 的 <span class="mono">messages/</span> 目录下一个独立文件里：
  <table class="t" style="margin-top:.6rem">
    <tr><th>类</th><th>文件</th></tr>
    <tr><td class="mono">BaseMessage</td><td class="mono">messages/base.py</td></tr>
    <tr><td class="mono">HumanMessage</td><td class="mono">messages/human.py</td></tr>
    <tr><td class="mono">AIMessage</td><td class="mono">messages/ai.py</td></tr>
    <tr><td class="mono">SystemMessage</td><td class="mono">messages/system.py</td></tr>
    <tr><td class="mono">ToolMessage / ToolCall</td><td class="mono">messages/tool.py</td></tr>
  </table>
</div>

<h2>AIMessage：信息量最大的一条</h2>
<p>模型的回复 <span class="inline">AIMessage</span> 不只是一段文字。它还可能携带<strong>工具调用请求</strong>和
<strong>token 用量</strong>。这正是它能驱动 Agent 的关键：</p>

<pre class="code"><span class="cm"># 一个 AIMessage 里可能有什么</span>
AIMessage(
    content=<span class="st">""</span>,                       <span class="cm"># 正文（要调工具时常为空）</span>
    tool_calls=[                       <span class="cm"># ★ 模型"想调用"的工具</span>
        {<span class="st">"name"</span>: <span class="st">"get_weather"</span>,
         <span class="st">"args"</span>: {<span class="st">"city"</span>: <span class="st">"北京"</span>},
         <span class="st">"id"</span>: <span class="st">"call_abc"</span>}
    ],
    usage_metadata={<span class="st">"input_tokens"</span>: 12,  <span class="cm"># token 统计</span>
                    <span class="st">"output_tokens"</span>: 8},
)
</pre>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <ul>
    <li><strong>消息是"通用货币"</strong>：模型的输入是 <span class="mono">list[BaseMessage]</span>，输出是一条 <span class="mono">AIMessage</span>。
      无论 OpenAI 还是 Anthropic，进出都是这套统一格式。</li>
    <li><strong>tool_calls 是 Agent 的引擎</strong>：模型不直接执行工具，而是在 AIMessage 里"请求"调用，
      由你的程序去执行，再把结果包成 ToolMessage 喂回去。这就是 Agent 循环的本质（第 7、12 课）。</li>
    <li><strong>content 可以是多模态</strong>：除了文本，还能放图片等内容块（定义在 <span class="mono">messages/content.py</span>）。</li>
  </ul>
</div>

<h2>动手：构造一段对话</h2>
<pre class="code"><span class="kw">from</span> langchain_core.messages <span class="kw">import</span> SystemMessage, HumanMessage

conversation = [
    SystemMessage(<span class="st">"你是一个简洁的天气助手。"</span>),
    HumanMessage(<span class="st">"北京天气怎么样？"</span>),
]
<span class="cm"># 把这串消息交给模型，它会还你一条 AIMessage（下一课）</span>
</pre>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>对话 = <strong>一串结构化消息</strong>，四种核心：System / Human / AI / Tool，全部继承 <span class="mono">BaseMessage</span>。</li>
    <li><span class="mono">AIMessage</span> 除了正文，还能带 <span class="mono">tool_calls</span> 和 <span class="mono">usage_metadata</span>。</li>
    <li><span class="mono">tool_calls</span> 是连接"模型"与"工具"的桥梁，也是 Agent 自动循环的起点。</li>
    <li>下一课：把这串消息真正喂给<strong>聊天模型</strong>。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_05 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
聊天模型（Chat Model）是你<strong>最常打交道的对象</strong>：喂给它一串消息，它还你一条 <span class="inline">AIMessage</span>。
LangChain 的杀手锏是——<strong>所有厂商的模型，用法一模一样</strong>。
</p>

<div class="card analogy">
  <div class="tag">🔁 生活类比</div>
  就像<strong>万能遥控器</strong>：电视、空调、音响牌子各不相同，但遥控器上的"开机/音量+"按钮是统一的。
  <span class="mono">init_chat_model</span> 就是这只万能遥控器，按钮（<span class="mono">invoke</span>/<span class="mono">stream</span>）永远一样，
  换设备只改一个型号字符串。
</div>

<h2>一行代码拿到任意模型</h2>
<p>核心入口是 <span class="inline">init_chat_model</span>，用 <span class="inline">"厂商:型号"</span> 的字符串指定模型：</p>

<pre class="code"><span class="kw">from</span> langchain.chat_models <span class="kw">import</span> init_chat_model

model = init_chat_model(<span class="st">"openai:gpt-5.1"</span>)        <span class="cm"># OpenAI</span>
<span class="cm"># model = init_chat_model("anthropic:claude-sonnet-4-5")  # 换厂商只改这里</span>
</pre>

<table class="t">
  <tr><th>前缀写法</th><th>实际用到的集成包</th></tr>
  <tr><td class="mono">"openai:gpt-5.1"</td><td class="mono">langchain-openai</td></tr>
  <tr><td class="mono">"anthropic:claude-sonnet-4-5"</td><td class="mono">langchain-anthropic</td></tr>
  <tr><td class="mono">"ollama:llama3"</td><td class="mono">langchain-ollama</td></tr>
</table>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  <ul>
    <li><span class="mono">init_chat_model</span> 在 <span class="mono">langchain_v1/langchain/chat_models/base.py</span>。
      它解析前缀、按需导入对应 partner 包、返回一个 <span class="mono">BaseChatModel</span> 实例。</li>
    <li>返回的对象类型（如 <span class="mono">ChatOpenAI</span>）来自<strong>集成层</strong>，但都实现了<strong>地基层</strong>
      <span class="mono">core/language_models/chat_models.py</span> 里的 <span class="mono">BaseChatModel</span> 接口。</li>
  </ul>
</div>

<h2>三种调用方式：invoke / stream / batch</h2>
<p>拿到模型后，有三种跑法。它们其实来自更底层的 <strong>Runnable 接口</strong>（第 8 课会揭晓）：</p>

<div class="cols">
  <div class="col">
    <h4>🟢 invoke：一问一答</h4>
    <pre class="code" style="margin:.4rem 0">resp = model.invoke(
  <span class="st">"北京天气怎么样？"</span>
)
print(resp.content)
<span class="cm"># 返回一条完整 AIMessage</span></pre>
  </div>
  <div class="col">
    <h4>🔵 stream：逐字流式</h4>
    <pre class="code" style="margin:.4rem 0"><span class="kw">for</span> chunk <span class="kw">in</span> model.stream(
    <span class="st">"讲个故事"</span>):
  print(chunk.content, end=<span class="st">""</span>)
<span class="cm"># 一块块吐 AIMessageChunk</span></pre>
  </div>
</div>
<pre class="code"><span class="cm"># batch：一次并发跑多个输入</span>
answers = model.batch([<span class="st">"北京天气？"</span>, <span class="st">"上海天气？"</span>, <span class="st">"广州天气？"</span>])
</pre>

<div class="card macro">
  <div class="tag">🌍 宏观理解：输入很灵活，输出很统一</div>
  <ul>
    <li><strong>输入</strong>可以偷懒：传<strong>字符串</strong>（自动当成 HumanMessage）、传<strong>消息列表</strong>、
      或传 <span class="mono">[("system","..."),("human","...")]</span> 这样的元组列表。</li>
    <li><strong>输出</strong>永远统一：<span class="mono">invoke</span> → 一条 <span class="mono">AIMessage</span>；
      <span class="mono">stream</span> → 一串 <span class="mono">AIMessageChunk</span>。</li>
    <li><strong>异步版</strong>同样齐全：<span class="mono">ainvoke</span> / <span class="mono">astream</span> / <span class="mono">abatch</span>。</li>
  </ul>
</div>

<h2>给模型装上工具：bind_tools</h2>
<p>聊天模型本身不会执行工具，但可以被告知"你有哪些工具可用"。这一步叫 <span class="inline">bind_tools</span>，
是通往 Agent 的关键一跳：</p>
<pre class="code">model_with_tools = model.bind_tools([get_weather])
resp = model_with_tools.invoke(<span class="st">"北京天气怎么样？"</span>)
print(resp.tool_calls)   <span class="cm"># 模型会在这里"请求"调用 get_weather</span>
</pre>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">init_chat_model("厂商:型号")</span> 一行拿到任意厂商模型，用法完全统一。</li>
    <li>三种跑法：<strong>invoke</strong>（一次）/<strong>stream</strong>（流式）/<strong>batch</strong>（批量），均有 async 版。</li>
    <li>输入灵活（字符串/消息/元组），输出统一（AIMessage / AIMessageChunk）。</li>
    <li><span class="mono">bind_tools</span> 让模型"知道"有哪些工具——下一课正式认识工具。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_06 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
工具（Tool）让模型<strong>突破"只会聊天"的边界</strong>——查数据库、调 API、做计算。
神奇之处在于：你只写一个<strong>普通 Python 函数</strong>，LangChain 自动把它变成模型能理解、能"请求调用"的工具。
</p>

<div class="card analogy">
  <div class="tag">🧰 生活类比</div>
  模型像个<strong>聪明但被关在房间里的顾问</strong>：它知识渊博，却拿不到实时信息、碰不到外部系统。
  工具就是你递进房间的一部部<strong>专用电话</strong>——一部打给天气台、一部打给数据库。
  你贴上"这部电话能干嘛、要拨什么号"的说明（schema），顾问就会在需要时<strong>请你帮他拨号</strong>。
</div>

<h2>把函数变成工具：@tool</h2>
<p>最常用的方式是 <span class="inline">@tool</span> 装饰器。它会自动从你的函数里<strong>提取三样东西</strong>：</p>

<pre class="code"><span class="kw">from</span> langchain_core.tools <span class="kw">import</span> tool

<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">get_weather</span>(city: str) -> str:
    <span class="st">&quot;&quot;&quot;查询某城市的当前天气。&quot;&quot;&quot;</span>
    <span class="kw">return</span> <span class="st">f"{city} 晴，25°C"</span>
</pre>

<div class="flow">
  <div class="node hl"><div class="nt">函数名</div><div class="nd">get_weather<br>→ 工具名</div></div>
  <div class="arrow">+</div>
  <div class="node hl"><div class="nt">docstring</div><div class="nd">"查询天气"<br>→ 工具描述</div></div>
  <div class="arrow">+</div>
  <div class="node hl"><div class="nt">类型注解</div><div class="nd">city: str<br>→ 参数 schema</div></div>
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  <ul>
    <li><span class="mono">@tool</span> 定义在 <span class="mono">core/tools/convert.py</span>，把函数包装成一个 <span class="mono">BaseTool</span>。</li>
    <li>实际生成的是 <span class="mono">StructuredTool</span>（<span class="mono">core/tools/structured.py</span>），
      它用 <span class="mono">create_schema_from_function</span> 从函数签名<strong>自动推断出 pydantic 参数 schema</strong>。</li>
    <li>所以"写好类型注解 + docstring"很重要——它们直接决定模型看到的工具说明。</li>
  </ul>
</div>

<h2>工具自己也能被调用</h2>
<p>包装后的工具是个对象，有 <span class="inline">name</span>、<span class="inline">description</span>、
<span class="inline">args_schema</span>，并且可以像函数一样 <span class="inline">invoke</span>：</p>
<pre class="code">print(get_weather.name)         <span class="cm"># "get_weather"</span>
print(get_weather.description)  <span class="cm"># "查询某城市的当前天气。"</span>
print(get_weather.invoke({<span class="st">"city"</span>: <span class="st">"北京"</span>}))  <span class="cm"># "北京 晴，25°C"</span>
</pre>

<h2>模型如何"使用"工具：完整往返</h2>
<p>关键认知：<strong>模型不会自己执行工具</strong>，它只会"请求"。真正的执行由你的程序（或 Agent）完成。
这一来一回是整个工具机制的核心：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>绑定</h4><p><span class="mono">model.bind_tools([get_weather])</span>：把工具的 schema 告诉模型。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>请求</h4><p>模型回一条 <span class="mono">AIMessage</span>，其中 <span class="mono">tool_calls=[{name, args, id}]</span>——"我想调 get_weather('北京')"。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>执行</h4><p>你的程序按请求真正运行 <span class="mono">get_weather.invoke(args)</span>，拿到结果。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>回传</h4><p>把结果包成 <span class="mono">ToolMessage</span>（带上对应的 <span class="mono">tool_call_id</span>）追加到消息列表。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>再问</h4><p>把更新后的消息再喂给模型，它据此给出最终自然语言回答。</p></div></div>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  这套"请求 → 执行 → 回传 → 再问"的循环，<strong>手写也能实现，但很繁琐</strong>。
  第 7 课的 <span class="mono">create_agent</span> 就是把这整个循环<strong>自动化</strong>。
  也就是说：<strong>工具 + 这个循环 = Agent</strong>。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">@tool</span> 把普通函数变成工具，自动提取<strong>名字 / 描述(docstring) / 参数 schema(类型注解)</strong>。</li>
    <li>底层是 <span class="mono">StructuredTool</span>，用 pydantic 从函数签名推断 schema。</li>
    <li>模型只<strong>请求</strong>调用（写在 <span class="mono">AIMessage.tool_calls</span>），<strong>执行靠你的程序</strong>，结果用 <span class="mono">ToolMessage</span> 回传。</li>
    <li>把这个往返自动化，就得到了 Agent —— 下一课登场。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_07 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
把前三课（消息 + 模型 + 工具）<strong>组装并自动化</strong>，就是 Agent。
一个函数 <span class="inline">create_agent</span> 帮你编排"思考 → 调工具 → 看结果 → 再思考"的循环，直到任务完成。
</p>

<div class="card analogy">
  <div class="tag">🕵️ 生活类比</div>
  Agent 就像一个<strong>会用工具的助理</strong>：你交代任务，他自己判断"需要先查个天气"，
  拿起工具电话拨号，看到结果后再决定"够了，可以回答了"还是"还得再查一个"。
  你不用一步步指挥——<strong>循环由他自己跑</strong>。
</div>

<h2>一行创建 Agent</h2>
<pre class="code"><span class="kw">from</span> langchain.agents <span class="kw">import</span> create_agent

agent = create_agent(
    model=<span class="st">"openai:gpt-5.1"</span>,        <span class="cm"># 模型（字符串或模型对象都行）</span>
    tools=[get_weather],            <span class="cm"># 一组工具</span>
    system_prompt=<span class="st">"你是天气助手"</span>,  <span class="cm"># 可选的系统设定</span>
)

result = agent.invoke(
    {<span class="st">"messages"</span>: [{<span class="st">"role"</span>: <span class="st">"user"</span>, <span class="st">"content"</span>: <span class="st">"北京和上海哪个更热？"</span>}]}
)
print(result[<span class="st">"messages"</span>][-1].content)   <span class="cm"># 最终答案</span>
</pre>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  <ul>
    <li><span class="mono">create_agent</span> 在 <span class="mono">langchain_v1/langchain/agents/factory.py</span>，
      由 <span class="mono">agents/__init__.py</span> 导出。</li>
    <li>它的输入/输出都是一个带 <span class="mono">"messages"</span> 键的状态字典——即 <span class="mono">AgentState</span>。</li>
    <li>核心签名（节选）：
      <pre class="code" style="margin:.5rem 0"><span class="kw">def</span> <span class="fn">create_agent</span>(
    model: str | BaseChatModel,
    tools=None,
    *,
    system_prompt=None,
    middleware=(),         <span class="cm"># 可插拔的中间件（第 12 课）</span>
    response_format=None,  <span class="cm"># 结构化输出</span>
    ...
)</pre></li>
  </ul>
</div>

<h2>Agent 循环：它到底在转什么？</h2>
<p>这张图是 Agent 的灵魂。注意它<strong>就是第 6 课那个工具往返，只是自动重复</strong>，
直到模型不再请求工具为止：</p>

<div class="flow" style="flex-direction:column;gap:.7rem;align-items:center">
  <div class="node hl" style="flex:0 0 auto;min-width:200px">① 模型思考<br><span style="font-weight:400;font-size:.76rem;color:var(--muted)">看当前消息，决定下一步</span></div>
  <div class="arrow" style="transform:rotate(90deg)">→</div>
  <div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap;justify-content:center">
    <div class="node" style="min-width:200px;border-color:var(--amber)">要调工具？→ ② 执行工具<br><span style="font-weight:400;font-size:.76rem;color:var(--muted)">运行后把 ToolMessage 加回消息，<b>回到 ①</b></span></div>
    <div class="node" style="min-width:160px;border-color:var(--accent)">不调工具？→ ③ 结束<br><span style="font-weight:400;font-size:.76rem;color:var(--muted)">返回最终 AIMessage</span></div>
  </div>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <ul>
    <li>Agent = <strong>模型 + 工具 + 一个自动循环</strong>。循环的"判断条件"很简单：
      <strong>模型回复里还有没有 <span class="mono">tool_calls</span></strong>？有就执行并继续，没有就结束。</li>
    <li>你只管<strong>声明</strong>"用哪个模型、给哪些工具、什么系统设定"，循环的编排交给框架。</li>
    <li>底层其实是一张 <strong>LangGraph 状态图</strong>（节点："model" 与 "tools"）——这是第 12 课的内容，现在只需理解它在转一个循环。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">create_agent(model, tools, system_prompt=...)</span> 一行得到一个会自动循环的 Agent。</li>
    <li>输入/输出都是 <span class="mono">{"messages": [...]}</span> 状态字典（<span class="mono">AgentState</span>）。</li>
    <li>循环判据：<strong>AIMessage 里还有没有 tool_calls</strong>。这把第 4–6 课串成了闭环。</li>
    <li><strong>第二部分（用户视角）到此结束</strong>。接下来掀开盖子，看这些便利背后的源码机制。</li>
  </ul>
</div>
"""
