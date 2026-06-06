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

<h2>进阶：消息的两个"另一面"</h2>
<p>除了四种基础消息，还有两点在真实项目里很常见，值得先有个印象：</p>

<div class="cols">
  <div class="col">
    <h4>① 流式块 Message Chunk</h4>
    <p>流式输出时，模型不是一次给完整 <span class="inline">AIMessage</span>，而是一串
      <span class="inline">AIMessageChunk</span>。它们能用 <span class="inline">+</span> 累加成完整消息（第 13 课详解）。</p>
    <p class="mono" style="font-size:.8rem;color:var(--muted)">messages/ai.py · AIMessageChunk</p>
  </div>
  <div class="col">
    <h4>② 多模态内容块</h4>
    <p><span class="inline">content</span> 不只是字符串，也可以是<strong>内容块列表</strong>
      （文本 + 图片等），用于多模态输入。</p>
    <p class="mono" style="font-size:.8rem;color:var(--muted)">messages/content.py</p>
  </div>
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入三个常见疑问。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 四种之外还有哪些消息类型 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 其它消息类</div>
      <div class="a">日常很少用，但读源码会遇到：
<pre class="code"><span class="cm"># messages/ 目录下还有：</span>
ChatMessage      <span class="cm"># 自定义任意 role（非标准角色时用）</span>
FunctionMessage  <span class="cm"># 旧版函数调用结果（已被 ToolMessage 取代）</span>
RemoveMessage    <span class="cm"># 一个"修饰符"，用于从历史中删除某条消息</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么保留这些</div>
      <div class="a"><span class="mono">FunctionMessage</span> 是历史遗留（OpenAI 早期的 function calling），为兼容而保留；
        <span class="mono">RemoveMessage</span> 在管理长对话 / Agent 状态时用来裁剪历史。99% 场景你只需四种核心消息。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 怎么记</div>
      <div class="a">记住主线即可：<strong>System / Human / AI / Tool</strong>。其余都是边角或历史兼容，遇到再查。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> content 为什么有时是字符串、有时是列表 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 两种形态</div>
      <div class="a">
<pre class="code"><span class="cm"># 纯文本：content 就是字符串</span>
HumanMessage(<span class="st">"你好"</span>)

<span class="cm"># 多模态：content 是内容块列表（文本 + 图片）</span>
HumanMessage(content=[
    {<span class="st">"type"</span>: <span class="st">"text"</span>, <span class="st">"text"</span>: <span class="st">"这张图里是什么？"</span>},
    {<span class="st">"type"</span>: <span class="st">"image"</span>, <span class="st">"source_type"</span>: <span class="st">"url"</span>, <span class="st">"url"</span>: <span class="st">"https://..."</span>},
])</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">现代模型支持图片、音频等多模态输入。一个纯字符串无法表达"文字 + 图片"的组合，
        所以 <span class="mono">content</span> 允许是<strong>结构化内容块列表</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">同一个 <span class="mono">HumanMessage</span> 类既能装纯文本也能装多模态，且各 partner 会把这些标准内容块
        翻译成自家厂商的多模态格式——你无需关心差异。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> tool_calls 与 ToolMessage 是怎么配对的 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 靠 id 配对（像快递单号）</div>
      <div class="a">
<pre class="code"><span class="cm"># 模型请求里每个 tool_call 带一个 id</span>
AIMessage(tool_calls=[{<span class="st">"name"</span>: <span class="st">"get_weather"</span>,
                      <span class="st">"args"</span>: {<span class="st">"city"</span>: <span class="st">"北京"</span>},
                      <span class="st">"id"</span>: <span class="st">"call_abc"</span>}])
<span class="cm"># 回传结果时用同一个 id 标明"这是哪个请求的答案"</span>
ToolMessage(content=<span class="st">"北京 晴 25°C"</span>, tool_call_id=<span class="st">"call_abc"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">模型一次可能<strong>请求多个工具</strong>。没有 id，回传时就分不清"哪个结果对应哪个请求"，
        模型会张冠李戴。<span class="mono">tool_call_id</span> 就是那张对账单号。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">支持<strong>并行多工具</strong>调用且结果不错乱；整套机制纯靠结构化消息运转，无需额外状态——再次印证"消息是通用货币"。</div>
    </div>
  </div>
</details>

<h2>🧠 上下文管理：对话历史就是"上下文"</h2>
<p>这是本课最重要的进阶主题。先建立一个关键认知——它会贯穿你之后所有的开发：</p>

<div class="card key">
  <div class="tag">🔑 核心认知</div>
  大语言模型<strong>没有记忆、是无状态的</strong>。它每次被调用时，"记得"的全部内容，
  就是你这一次<strong>传进去的那串消息</strong>。所以——
  <strong>这串消息列表 = 模型的上下文(context)</strong>，而"管理对话/记忆"本质上就是
  <strong>管理这个消息列表</strong>：往里加什么、保留什么、删掉什么、压缩什么。
</div>

<div class="card analogy">
  <div class="tag">📋 生活类比</div>
  模型像一个<strong>每次都失忆的专家</strong>：你每次找他都得把"之前聊到哪了"重新讲一遍（那叠消息）。
  对话越长，这叠纸越厚——但他桌子（<strong>上下文窗口</strong>）只放得下有限张纸。
  于是你必须决定：哪些旧纸该<strong>扔掉</strong>、哪些该<strong>缩写成摘要</strong>、哪些必须<strong>留着</strong>。
</div>

<h3>为什么必须管理它</h3>
<ul>
  <li><strong>窗口有限</strong>：每个模型有 token 上限，历史无限增长迟早<strong>超限报错</strong>。</li>
  <li><strong>又贵又慢</strong>：每轮都把全部历史发过去，token 越多<strong>越费钱、延迟越高</strong>。</li>
  <li><strong>噪声干扰</strong>：太多无关旧消息会<strong>稀释重点</strong>，让模型抓不住当前任务。</li>
</ul>

<h3>LangChain 的"上下文工具箱"</h3>
<p>core 提供了一组现成的纯函数来加工消息列表（都在 <span class="inline">langchain_core.messages</span>）：</p>
<table class="t">
  <tr><th>工具</th><th>作用</th><th>位置</th></tr>
  <tr><td class="mono">trim_messages</td><td>按 <strong>token 预算</strong>裁剪历史（保留最近/最早）</td><td class="mono">messages/utils.py</td></tr>
  <tr><td class="mono">filter_messages</td><td>按<strong>类型 / 名字 / id</strong> 保留或剔除消息</td><td class="mono">messages/utils.py</td></tr>
  <tr><td class="mono">merge_message_runs</td><td>合并<strong>连续同角色</strong>的消息，减少碎片</td><td class="mono">messages/utils.py</td></tr>
  <tr><td class="mono">count_tokens_approximately</td><td><strong>估算</strong>一串消息的 token 数</td><td class="mono">messages/utils.py</td></tr>
  <tr><td class="mono">RemoveMessage</td><td>一个修饰符，从状态历史中<strong>删除</strong>指定消息</td><td class="mono">messages/modifier.py</td></tr>
</table>

<h3>四种主流"管理策略"</h3>
<p>把上面的工具组合起来，常见有四种策略。真实项目里经常<strong>混用</strong>：</p>
<div class="cols">
  <div class="col">
    <h4>① 滑动窗口（Trimming）</h4>
    <p>只保留<strong>最近 N 条 / N 个 token</strong>，旧的直接丢。最简单、最常用。</p>
    <p class="mono" style="font-size:.8rem;color:var(--muted)">trim_messages</p>
  </div>
  <div class="col">
    <h4>② 摘要压缩（Summarization）</h4>
    <p>把久远历史<strong>让模型缩写成一段摘要</strong>，用摘要替代原始长历史。</p>
    <p class="mono" style="font-size:.8rem;color:var(--muted)">SummarizationMiddleware</p>
  </div>
  <div class="col">
    <h4>③ 检索召回（RAG）</h4>
    <p>历史存外部库，每轮<strong>只检索相关片段</strong>放进上下文，而非全带。</p>
    <p class="mono" style="font-size:.8rem;color:var(--muted)">retriever + 消息拼装</p>
  </div>
  <div class="col">
    <h4>④ 持久化（Persistence）</h4>
    <p>把对话状态<strong>存档</strong>，跨请求/会话恢复，实现"长期记忆"。</p>
    <p class="mono" style="font-size:.8rem;color:var(--muted)">LangGraph checkpointer</p>
  </div>
</div>

<h2>🔍 上下文管理 · 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，逐个吃透每种管理方式。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> trim_messages：按 token 预算裁剪历史 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> langchain_core.messages <span class="kw">import</span> trim_messages, count_tokens_approximately

trimmed = trim_messages(
    messages,
    max_tokens=4000,                        <span class="cm"># token 预算</span>
    token_counter=count_tokens_approximately,
    strategy=<span class="st">"last"</span>,                       <span class="cm"># 保留最近的（最常用）</span>
    include_system=<span class="kw">True</span>,                   <span class="cm"># 始终保住开头的 SystemMessage</span>
    start_on=<span class="st">"human"</span>,                       <span class="cm"># 裁剪后从一条 Human 开始，保持对话完整</span>
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么有这些参数</div>
      <div class="a"><span class="mono">include_system=True</span> 保证"人设/规则"不会被一起裁掉；
        <span class="mono">start_on="human"</span> 避免裁剪后历史从一条孤立的 AI 回复或 ToolMessage 开头（那会让模型困惑）。
        这些细节就是"裁剪历史"里最容易踩的坑。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点 & 🔀 其他方案</div>
      <div class="a">优点：实现简单、可预测、零额外模型调用。代价：被裁掉的早期信息<strong>彻底丢失</strong>。
        想保住要点又省 token → 用策略 ②摘要；想按需召回 → 用策略 ③检索。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> filter / merge / RemoveMessage：精修历史 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 三种精修</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> langchain_core.messages <span class="kw">import</span> filter_messages, merge_message_runs, RemoveMessage

<span class="cm"># 只保留 human + ai，剔除工具噪声</span>
clean = filter_messages(messages, include_types=[<span class="st">"human"</span>, <span class="st">"ai"</span>])

<span class="cm"># 合并连续同角色消息，减少碎片</span>
merged = merge_message_runs(messages)

<span class="cm"># 在 Agent 状态里删掉某条消息（按 id）</span>
update = [RemoveMessage(id=<span class="st">"msg_123"</span>)]</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 各自解决什么</div>
      <div class="a"><span class="mono">filter_messages</span>：把无关消息（如调试用的 ToolMessage）挡在上下文外；
        <span class="mono">merge_message_runs</span>：某些厂商不接受连续两条同角色消息，合并可避免报错；
        <span class="mono">RemoveMessage</span>：在 LangGraph 状态里精准删除（如撤回一次错误的工具调用）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">它们都是<strong>纯函数</strong>（输入消息列表 → 输出消息列表），可随意组合进任何链或 Agent 前处理，互不耦合。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 在 Agent 里：持久化 + 摘要 + 上下文编辑 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 三种 Agent 级手段</div>
      <div class="a">
<pre class="code"><span class="cm"># A) 持久化记忆：给 Agent 一个 checkpointer，自动存取对话状态</span>
agent = create_agent(model, tools, checkpointer=saver)
agent.invoke(input, config={<span class="st">"configurable"</span>: {<span class="st">"thread_id"</span>: <span class="st">"u1"</span>}})

<span class="cm"># B) 自动摘要：历史过长时把旧消息压成摘要</span>
<span class="kw">from</span> langchain.agents.middleware <span class="kw">import</span> SummarizationMiddleware

<span class="cm"># C) 上下文编辑：按规则裁剪/编辑进入模型的上下文</span>
<span class="kw">from</span> langchain.agents.middleware <span class="kw">import</span> ContextEditingMiddleware
agent = create_agent(model, tools, middleware=[SummarizationMiddleware(model)])</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么放在 Agent / 中间件层</div>
      <div class="a">Agent 会自动循环、消息<strong>持续增长</strong>，最需要上下文治理。
        <span class="mono">checkpointer</span> 解决"跨请求记忆"（线程 id 区分用户）；
        <span class="mono">SummarizationMiddleware</span> / <span class="mono">ContextEditingMiddleware</span> 在每轮模型调用前自动治理上下文，
        无需你手写裁剪逻辑。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">SummarizationMiddleware</span> → <span class="mono">agents/middleware/summarization.py</span>；
        <span class="mono">ContextEditingMiddleware</span> → <span class="mono">agents/middleware/context_editing.py</span>；
        <span class="mono">checkpointer</span> 是 <span class="mono">create_agent</span> 的参数（持久化由 LangGraph 提供，第 12 课）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 给普通链加"记忆"：RunnableWithMessageHistory <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 用途</div>
      <div class="a">如果你用的是<strong>普通链</strong>（不是 Agent），可以用它把"按会话 id 存取历史"包到链外面：
<pre class="code"><span class="kw">from</span> langchain_core.runnables.history <span class="kw">import</span> RunnableWithMessageHistory

chat = RunnableWithMessageHistory(
    chain,
    get_session_history,           <span class="cm"># 按 session_id 取/存历史的函数</span>
    input_messages_key=<span class="st">"input"</span>,
    history_messages_key=<span class="st">"history"</span>,
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 它和 Agent 的 checkpointer 区别</div>
      <div class="a"><span class="mono">RunnableWithMessageHistory</span> 是给 <strong>LCEL 链</strong>加历史的经典方式（偏底层、手动）；
        而 Agent 用 LangGraph <span class="mono">checkpointer</span> 做状态持久化，更适合复杂、有状态的多步流程。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 怎么选</div>
      <div class="a">简单问答链 + 要记住上一轮 → <span class="mono">RunnableWithMessageHistory</span>；
        多步工具、需要断点续跑/人审 → 用 Agent + checkpointer。</div>
    </div>
  </div>
</details>

<div class="card macro">
  <div class="tag">🌍 宏观理解：一句话收束</div>
  <strong>"管理对话" = "管理那串喂给模型的消息列表"</strong>。
  无论裁剪、筛选、合并、摘要、检索还是持久化，本质都是在回答同一个问题：
  <strong>这一次调用，到底该把哪些消息放进上下文？</strong> 想透这一点，你就掌握了所有 LLM 应用的命脉。
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>对话 = <strong>一串结构化消息</strong>，四种核心：System / Human / AI / Tool，全部继承 <span class="mono">BaseMessage</span>。</li>
    <li><span class="mono">AIMessage</span> 除了正文，还能带 <span class="mono">tool_calls</span> 和 <span class="mono">usage_metadata</span>。</li>
    <li><span class="mono">tool_calls</span> 是连接"模型"与"工具"的桥梁，也是 Agent 自动循环的起点。</li>
    <li><strong>上下文 = 你传进去的消息列表</strong>；管理对话就是裁剪/筛选/合并/摘要/检索/持久化这串消息。</li>
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

<h2>进阶：让模型直接吐出"结构化数据"</h2>
<p>除了自由文本，你常常想让模型返回<strong>固定结构的数据</strong>（如 JSON / 对象）。
用 <span class="inline">with_structured_output</span> 绑定一个 schema，模型输出就会被解析成该类型：</p>
<pre class="code"><span class="kw">from</span> pydantic <span class="kw">import</span> BaseModel

<span class="kw">class</span> <span class="fn">Weather</span>(BaseModel):
    city: str
    temp_c: float

structured = model.with_structured_output(Weather)
result = structured.invoke(<span class="st">"北京现在 25 度"</span>)
<span class="cm"># result 直接是 Weather(city="北京", temp_c=25.0)，不是字符串</span>
</pre>
<div class="card detail">
  <div class="tag">🔬 代码对应</div>
  <span class="mono">with_structured_output</span> 定义在 <span class="mono">core/language_models/chat_models.py</span>，
  与 <span class="mono">bind_tools</span> 相邻。它底层常借助"工具调用 / JSON 模式"来强制模型产出符合 schema 的结果。
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入三个常见疑问。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> invoke / stream / batch 该用哪个 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 场景对照</div>
      <div class="a">
<pre class="code">invoke  → 一问一答，要完整结果（最常用）
stream  → 聊天 UI 打字机效果，边生成边显示
batch   → 一批互不相关的输入，并发处理省时间
a*      → 上面三个的异步版（FastAPI 等异步框架里用）</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么有这么多</div>
      <div class="a">不同场景对"延迟感受"和"吞吐"诉求不同：用户等单个回答看重<strong>首字延迟</strong>（stream），
        后台批处理看重<strong>总吞吐</strong>（batch）。一套接口覆盖全部，省得你换 API。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">它们其实都来自底层 <strong>Runnable</strong> 接口（第 8 课），所以<strong>任何</strong> LangChain 组件
        （链、Agent）都自带这四类跑法，学一次处处通用。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> init_chat_model 的"厂商:型号"是怎么解析的 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 两种等价写法</div>
      <div class="a">
<pre class="code"><span class="cm"># 写法 1：前缀内联</span>
init_chat_model(<span class="st">"anthropic:claude-sonnet-4-5"</span>)

<span class="cm"># 写法 2：分开传（适合 provider 来自配置/环境变量）</span>
init_chat_model(<span class="st">"claude-sonnet-4-5"</span>, model_provider=<span class="st">"anthropic"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 它在背后做了什么</div>
      <div class="a">解析前缀 → 推断 provider → <strong>按需导入</strong>对应 partner 包（如 <span class="mono">langchain-anthropic</span>）→
        实例化具体模型类（<span class="mono">ChatAnthropic</span>）→ 返回一个 <span class="mono">BaseChatModel</span>。
        所以你<strong>必须先安装</strong>对应 partner 包。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点 & 🔀 其他方案</div>
      <div class="a">优点：一行切换厂商、provider 可动态化。其他方案：直接 <span class="mono">from langchain_openai import ChatOpenAI</span>
        手动实例化（更显式，但换厂商要改 import）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 自由文本 vs 结构化输出，何时用哪个 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 对比</div>
      <div class="a">需要"念给人听"的回答 → 用普通 <span class="mono">invoke</span>（拿 <span class="mono">.content</span>）；
        需要"喂给程序"的数据（写库、调用下游 API）→ 用 <span class="mono">with_structured_output</span> 拿到对象。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">直接让模型"输出 JSON"很脆——它可能多写解释、少个引号导致解析失败。
        <span class="mono">with_structured_output</span> 用 schema 约束 + 自动解析，把这种不确定性收敛掉。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点 & 🔀 其他方案</div>
      <div class="a">优点：拿到的是已校验的强类型对象，省去手写解析与容错。
        其他方案：自己写 prompt 要求输出 JSON + <span class="mono">json.loads</span>（易碎）；或用 output parser 手动解析。</div>
    </div>
  </div>
</details>

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

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入三个进阶用法。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> @tool 的几种写法与定制 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="cm"># 1) 最简：函数名=工具名，docstring=描述</span>
<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">get_weather</span>(city: str) -> str:
    <span class="st">&quot;&quot;&quot;查询天气&quot;&quot;&quot;</span>
    ...

<span class="cm"># 2) 自定义名字 + 直接返回（不再回模型）</span>
<span class="nb">@tool</span>(<span class="st">"weather"</span>, return_direct=True)
<span class="kw">def</span> <span class="fn">get_weather</span>(city: str) -> str: ...

<span class="cm"># 3) 用 pydantic 显式定义参数 schema</span>
<span class="nb">@tool</span>(args_schema=WeatherInput)
<span class="kw">def</span> <span class="fn">get_weather</span>(city: str) -> str: ...</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ return_direct 是什么</div>
      <div class="a">默认工具结果会<strong>回传给模型</strong>再让它总结。设 <span class="mono">return_direct=True</span> 后，
        工具一旦执行，其结果<strong>直接作为最终输出</strong>返回给用户，不再多走一轮模型——省时省 token，适合"查到即答"的工具。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">同一个装饰器覆盖从"零配置"到"精细控制"的全谱：能自动推断时省心，需要时又能完全接管 name/description/schema。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> ToolMessage 不只是文本：content / artifact / status <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 字段一览</div>
      <div class="a">
<pre class="code">ToolMessage(
    content=<span class="st">"北京 晴 25°C"</span>,        <span class="cm"># 给模型看的文本结果</span>
    tool_call_id=<span class="st">"call_abc"</span>,       <span class="cm"># 与请求配对的 id</span>
    artifact={<span class="st">"raw"</span>: {...}},       <span class="cm"># 不给模型、留给程序用的原始数据</span>
    status=<span class="st">"success"</span>,            <span class="cm"># success / error</span>
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ artifact 有什么用</div>
      <div class="a">有时工具返回的"完整原始数据"（如一张图、一个大 JSON）<strong>不适合塞给模型</strong>（费 token 又没必要），
        但你的程序后续要用。<span class="mono">artifact</span> 就是"<strong>给程序、不给模型</strong>"的那一份，
        靠 <span class="mono">response_format="content_and_artifact"</span> 启用。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">把"给模型的摘要"和"给程序的原始数据"分离，既省上下文又不丢信息；<span class="mono">status</span> 还能让 Agent 感知工具失败。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 写好工具的关键：类型注解 + docstring <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 好 vs 差</div>
      <div class="a">
<pre class="code"><span class="cm"># ✅ 好：类型清晰、描述明确，模型才知道何时/如何调用</span>
<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">search_orders</span>(user_id: str, status: str) -> list:
    <span class="st">&quot;&quot;&quot;按用户 id 和订单状态查询订单。status 可选: paid/shipped。&quot;&quot;&quot;</span>

<span class="cm"># ❌ 差：无注解、无说明，模型只能瞎猜</span>
<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">f</span>(a, b): ...</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">模型<strong>看不到函数体</strong>，它只能根据"工具名 + 描述 + 参数 schema"决定要不要调、传什么参。
        注解和 docstring 直接变成模型看到的"说明书"，写得含糊，模型就用得糟。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 经验法则</div>
      <div class="a">每个参数都加类型注解；docstring 一句话说清"做什么 + 关键参数取值范围"；
        工具名用动词短语（<span class="mono">get_weather</span> 而非 <span class="mono">gw</span>）。</div>
    </div>
  </div>
</details>

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

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入 create_agent 的三个常用能力。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> system_prompt：怎么给 Agent 定"人设"和规则 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code">agent = create_agent(
    model, tools=[get_weather],
    system_prompt=<span class="st">"你是严谨的天气助手。只用工具返回的数据，不要编造。"</span>,
)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">它会作为对话最前面的 <span class="mono">SystemMessage</span> 注入，约束 Agent 的<strong>语气、边界、调用工具的策略</strong>。
        没有它，模型只能凭默认行为发挥，容易跑偏或乱编。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">一个字符串就能统一规范整个 Agent 的行为，无需在每条用户消息里重复叮嘱。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> response_format：让 Agent 最终输出结构化数据 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> pydantic <span class="kw">import</span> BaseModel
<span class="kw">class</span> <span class="fn">Answer</span>(BaseModel):
    city: str
    temp_c: float

agent = create_agent(model, tools=[get_weather], response_format=Answer)
<span class="cm"># Agent 跑完循环后，给你一个 Answer 对象，而不只是文本</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 与 with_structured_output 的区别</div>
      <div class="a">第 5 课的 <span class="mono">with_structured_output</span> 约束<strong>单次模型调用</strong>的输出；
        这里的 <span class="mono">response_format</span> 约束<strong>整个 Agent 循环跑完后</strong>的最终结果——适合"先用工具查、最后给结构化答案"的场景。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">Agent 既能多步用工具，又能把最终结论交成强类型对象，直接对接下游程序。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> middleware：在循环里插钩子（预告第 12 课） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 用途举例</div>
      <div class="a"><span class="mono">create_agent(..., middleware=[...])</span> 可以在"调用模型前后""执行工具前后"插入逻辑：
        <strong>改写请求、人审(human-in-the-loop)、日志、限流、敏感词过滤</strong>等。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">真实产品需要在 Agent 的标准循环里加"非功能性"逻辑。若没有扩展点，就只能去改核心循环代码——既危险又难维护。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点 & 🔀 其他方案</div>
      <div class="a">优点：行为可插拔，核心循环保持稳定（第 12 课看它如何映射到 LangGraph 节点）。
        其他方案：用回调（callbacks，第 13 课）做观测，但 middleware 能真正<strong>改变</strong>流程，回调主要用于<strong>观察</strong>。</div>
    </div>
  </div>
</details>

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
