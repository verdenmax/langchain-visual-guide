"""Content for Part 1 (macro overview): lessons 01-03."""

# ---------------------------------------------------------------------------
LESSON_01 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
LangChain 是一个用 Python（和 JS）写的<strong>开源框架</strong>，帮你把"大语言模型（LLM）"
接进真实的应用里。它不替你训练模型，而是负责模型<strong>周边的所有管道</strong>。
</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把大语言模型（如 GPT、Claude）想成一台<strong>很强但很孤立的发动机</strong>。它能输出文字，
  但不知道你的数据库、不会自己调用工具、不同品牌发动机接口还都不一样。
  LangChain 就是那套<strong>标准化的"传动系统 + 仪表盘 + 配件接口"</strong>：
  让你用同一套代码驱动任何品牌的发动机，并把它接到油箱、轮子和导航上。
</div>

<h2>它到底解决什么问题？</h2>
<p>直接调用某个厂商的 API（比如 OpenAI 的 SDK）当然能用，但真实应用里你很快会遇到四类麻烦，
这正是 LangChain 要替你抹平的：</p>

<table class="t">
  <tr><th>痛点</th><th>没有框架时</th><th>LangChain 的做法</th></tr>
  <tr><td><strong>厂商锁定</strong></td><td>换模型要重写一大片调用代码</td><td>统一接口 <span class="mono">invoke()</span>，换模型只改一行</td></tr>
  <tr><td><strong>对话拼装</strong></td><td>手动拼 role/content 的字典</td><td>结构化<strong>消息对象</strong>（Human/AI/Tool）</td></tr>
  <tr><td><strong>调用工具</strong></td><td>自己解析模型要调哪个函数、传什么参</td><td><strong>工具(Tool)</strong> + 自动生成 schema + 解析</td></tr>
  <tr><td><strong>多步推理</strong></td><td>手写"想—做—再想"的循环</td><td><strong>Agent</strong> 帮你编排循环</td></tr>
</table>

<p class="acc-intro" style="color:var(--muted);font-size:.92rem">
👇 想深入理解每一类麻烦？点开下面的折叠卡片，每张都给你：<strong>① 示例代码 · ② 为什么必要 · ③ LangChain 的做法与优点 · ④ 还有什么其他方案</strong>。
</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 厂商锁定 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">直接用各家 SDK，方法名、参数、返回结构都不一样：
<pre class="code"><span class="cm"># OpenAI SDK</span>
<span class="kw">from</span> openai <span class="kw">import</span> OpenAI
text = OpenAI().chat.completions.create(
    model=<span class="st">"gpt-5.1"</span>, messages=[...]
).choices[0].message.content

<span class="cm"># Anthropic SDK —— 形状完全不同</span>
<span class="kw">from</span> anthropic <span class="kw">import</span> Anthropic
text = Anthropic().messages.create(
    model=<span class="st">"claude-sonnet-4-5"</span>, max_tokens=1024, messages=[...]
).content[0].text

<span class="cm"># LangChain —— 换厂商只改字符串</span>
text = init_chat_model(<span class="st">"openai:gpt-5.1"</span>).invoke(<span class="st">"..."</span>).content</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">真实项目常需在厂商间切换：A/B 对比效果、主力模型故障时降级到备用、按成本或延迟选型。
        一旦调用代码与某家 SDK 深度耦合，每次切换都要重写一大片——这就是"厂商锁定"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ LangChain 的做法与优点</div>
      <div class="a">用统一的 <strong>BaseChatModel</strong> 接口包裹所有厂商，一律 <span class="inline">invoke/stream/batch</span>；
        换模型只改 <span class="inline">"openai:..."</span> → <span class="inline">"anthropic:..."</span> 一个字符串，
        还顺带统一了<strong>重试、缓存、回调追踪</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>自己写一层适配器</strong>（灵活但要自己维护、自己跟进各厂商更新）；
        <strong>LiteLLM</strong>（专注"统一调用 API"这一件事，更轻量）；
        <strong>直接绑定单一厂商</strong>（最省事，但放弃了可移植性）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 对话拼装（role / content） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">手拼字典 vs 结构化消息对象：
<pre class="code"><span class="cm"># 手动拼 dict：key 和 role 容易拼错、字段容易漏</span>
messages = [
    {<span class="st">"role"</span>: <span class="st">"system"</span>, <span class="st">"content"</span>: <span class="st">"你是助手"</span>},
    {<span class="st">"role"</span>: <span class="st">"user"</span>,   <span class="st">"content"</span>: <span class="st">"你好"</span>},
]

<span class="cm"># LangChain 消息对象：类型安全、可补全、可携带 tool_calls 等</span>
<span class="kw">from</span> langchain_core.messages <span class="kw">import</span> SystemMessage, HumanMessage
messages = [SystemMessage(<span class="st">"你是助手"</span>), HumanMessage(<span class="st">"你好"</span>)]</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么 role / content 必须存在</div>
      <div class="a">聊天类 LLM 是按<strong>多轮对话格式</strong>训练的：模型靠 <span class="inline">role</span> 区分"谁在说话"——
        <strong>system</strong>（最高优先级的设定）、<strong>user</strong>（你的输入）、<strong>assistant</strong>（模型的历史回复）；
        靠 <span class="inline">content</span> 承载具体内容。缺了 role，模型就无法分辨"系统指令"和"用户提问"，
        语义会错乱；这是 Chat Completions API 的<strong>硬性契约</strong>，漏字段会直接报错。</div>
    </div>
    <div class="qa">
      <div class="q">✅ LangChain 的做法与优点</div>
      <div class="a">用<strong>消息类</strong>代替裸字典：防拼写错误、IDE 自动补全、可承载结构化字段
        （<span class="inline">tool_calls</span>、<span class="inline">usage_metadata</span>、多模态内容块），
        并能在不同厂商间<strong>自动翻译</strong>成各自要求的 role/content 格式。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>继续手拼 dict</strong>（最简单，但易错、无补全）；
        <strong>自定义 TypedDict / pydantic 模型</strong>（类型安全，但要自己实现序列化与厂商适配）；
        <strong>用厂商 SDK 自带的消息类型</strong>（又回到厂商锁定）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 调用工具 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">手写 JSON Schema + 手动解析 vs 一个装饰器：
<pre class="code"><span class="cm"># 手动：自己写 schema，还要手动解析模型返回的调用请求</span>
tools = [{
    <span class="st">"type"</span>: <span class="st">"function"</span>,
    <span class="st">"function"</span>: {
        <span class="st">"name"</span>: <span class="st">"get_weather"</span>,
        <span class="st">"description"</span>: <span class="st">"查询天气"</span>,
        <span class="st">"parameters"</span>: {<span class="st">"type"</span>: <span class="st">"object"</span>,
            <span class="st">"properties"</span>: {<span class="st">"city"</span>: {<span class="st">"type"</span>: <span class="st">"string"</span>}},
            <span class="st">"required"</span>: [<span class="st">"city"</span>]}}}]
<span class="cm"># 模型返回后，还要自己 json.loads(arguments) → 调函数 → 拼回去</span>

<span class="cm"># LangChain：一个装饰器，schema 自动从签名生成</span>
<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">get_weather</span>(city: str) -> str:
    <span class="st">&quot;&quot;&quot;查询天气&quot;&quot;&quot;</span>
    ...</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">模型本身<strong>不会执行代码</strong>，它只能输出一个"我想调用某函数、参数是这些"的结构化请求。
        要真正用上工具，必须：① 用 JSON Schema 把工具<strong>描述</strong>给模型；② <strong>解析</strong>模型返回的调用请求；
        ③ <strong>执行</strong>并把结果回传。手写这三步繁琐且易错（参数校验、JSON 解析尤甚）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ LangChain 的做法与优点</div>
      <div class="a"><span class="inline">@tool</span> 从<strong>函数签名 + 类型注解 + docstring</strong> 自动生成 schema；
        自动把模型返回解析成结构化的 <span class="inline">tool_calls</span>；用 pydantic 校验参数。你只写一个普通函数。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>手写 JSON Schema + 手动解析</strong>（完全可控，但样板代码多）；
        <strong>用厂商 SDK 的 function calling 原语</strong>（仍要自己写 schema）；
        <strong>自己用 pydantic 生成 schema</strong> 再喂给厂商（接近 LangChain 的思路，但要自己拼装）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">4</span> 多步推理（Agent 循环） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">手写"想—做—再想"循环 vs 一行 create_agent：
<pre class="code"><span class="cm"># 手写循环：调模型 → 看有无 tool_calls → 执行 → 回灌 → 再调…</span>
<span class="kw">while</span> True:
    ai = model_with_tools.invoke(messages)
    messages.append(ai)
    <span class="kw">if</span> <span class="kw">not</span> ai.tool_calls:
        <span class="kw">break</span>
    <span class="kw">for</span> call <span class="kw">in</span> ai.tool_calls:
        result = run_tool(call)
        messages.append(ToolMessage(result, tool_call_id=call[<span class="st">"id"</span>]))

<span class="cm"># LangChain：一行</span>
agent = create_agent(model, tools)
agent.invoke({<span class="st">"messages"</span>: [...]})</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这件事必要</div>
      <div class="a">复杂任务要让模型<strong>边想边做</strong>：查一次不够还要再查、根据中间结果调整方向。
        这需要一个循环——调用→判断→执行工具→把结果回灌→再调用。手写时还要处理
        <strong>终止条件、错误重试、并行工具调用、消息累积、状态管理</strong>，很快就会失控。</div>
    </div>
    <div class="qa">
      <div class="q">✅ LangChain 的做法与优点</div>
      <div class="a"><span class="inline">create_agent</span> 用 <strong>LangGraph</strong> 把这个循环编译成一张状态图，
        自带终止判断、并行工具、流式输出、持久化 / 中断、以及 <strong>middleware</strong> 扩展点——
        无需你手搓循环（细节见第 7、12 课）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 还有什么其他方案</div>
      <div class="a"><strong>手写 while 循环</strong>（小场景够用，复杂场景易失控）；
        <strong>其他 Agent 框架</strong>（如 LlamaIndex、AutoGen、CrewAI，各有侧重）；
        <strong>直接用 LangGraph 自己搭图</strong>（最大灵活度，但要自己定义节点和边）。</div>
    </div>
  </div>
</details>

<h2>核心心智模型：四个名词</h2>
<p>整个框架你只要先记住<strong>四个概念</strong>，后面所有内容都是它们的展开。下面这张图是你之后
反复会用到的"骨架图"：</p>

<div class="flow">
  <div class="node hl"><div class="nt">Messages</div><div class="nd">对话的"原子"<br>谁说了什么</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Chat Model</div><div class="nd">包裹 LLM<br>输入/输出都是消息</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Tools</div><div class="nd">模型能调用的<br>外部能力</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">Agent</div><div class="nd">把上面三者<br>编成自动循环</div></div>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <ul>
    <li><strong>Messages（消息）</strong>：对话由一条条消息组成。你说的是 <span class="inline">HumanMessage</span>，
      模型回的是 <span class="inline">AIMessage</span>，工具返回的是 <span class="inline">ToolMessage</span>。</li>
    <li><strong>Chat Model（聊天模型）</strong>：对 LLM 的<strong>统一封装</strong>。喂给它一串消息，它吐回一条 AI 消息。
      无论底层是 OpenAI 还是 Anthropic，用法完全一样。</li>
    <li><strong>Tools（工具）</strong>：你写的普通 Python 函数，包装后模型就能"请求调用"它（查天气、查数据库……）。</li>
    <li><strong>Agent（智能体）</strong>：让模型在"思考 → 调用工具 → 看结果 → 再思考"之间自动循环，直到完成任务。</li>
  </ul>
</div>

<h2>最小可运行例子</h2>
<p>先不用懂细节，感受一下"四个名词"在代码里长什么样。这段代码就是后面所有课的浓缩：</p>

<pre class="code"><span class="kw">from</span> langchain.chat_models <span class="kw">import</span> init_chat_model
<span class="kw">from</span> langchain.agents <span class="kw">import</span> create_agent

<span class="cm"># 1) 一个工具：就是普通函数</span>
<span class="kw">def</span> <span class="fn">get_weather</span>(city: str) -> str:
    <span class="st">&quot;&quot;&quot;查询某城市的天气。&quot;&quot;&quot;</span>
    <span class="kw">return</span> <span class="st">f"{city} 今天晴，25°C"</span>

<span class="cm"># 2) 一个聊天模型：换厂商只改这一行字符串</span>
model = init_chat_model(<span class="st">"openai:gpt-5.1"</span>)

<span class="cm"># 3) 一个 Agent：把模型 + 工具编成自动循环</span>
agent = create_agent(model, tools=[get_weather])

<span class="cm"># 4) 跑起来：底层就是一串 Messages 在流动</span>
result = agent.invoke({<span class="st">"messages"</span>: [{<span class="st">"role"</span>: <span class="st">"user"</span>, <span class="st">"content"</span>: <span class="st">"北京天气怎么样？"</span>}]})
</pre>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应</div>
  这三个入口函数你会在后面反复见到，记住它们来自哪里：
  <table class="t" style="margin-top:.6rem">
    <tr><th>函数</th><th>来源包</th><th>文件</th></tr>
    <tr><td class="mono">init_chat_model</td><td>langchain</td><td class="mono">chat_models/base.py</td></tr>
    <tr><td class="mono">create_agent</td><td>langchain</td><td class="mono">agents/factory.py</td></tr>
    <tr><td class="mono">@tool / 普通函数</td><td>langchain-core</td><td class="mono">tools/convert.py</td></tr>
  </table>
</div>

<h2>LangChain 不是什么</h2>
<div class="card warn">
  <div class="tag">⚠️ 常见误解</div>
  <ul>
    <li>它<strong>不训练、不托管模型</strong>——模型仍跑在 OpenAI / Anthropic 等厂商那里，LangChain 只是客户端。</li>
    <li>它<strong>不是只能做聊天机器人</strong>——它是通用的"LLM 应用编排层"，可做 RAG、数据抽取、工作流等。</li>
    <li>它<strong>不强制你用全部功能</strong>——可以只用聊天模型封装，也可以一路用到复杂 Agent。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>LangChain = LLM 的<strong>标准化管道与编排层</strong>，让你"换模型只改一行、调工具不写胶水、多步推理不手搓循环"。</li>
    <li>记住四个名词的<strong>流向</strong>：Messages → Chat Model → Tools → Agent。这是整套教程的骨架。</li>
    <li>下一课我们拉远镜头，看看这些概念在<strong>代码仓库的哪一层</strong>。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_02 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
LangChain 的代码不是一个大包，而是一个 <strong>monorepo（单仓库、多包）</strong>：
一个 Git 仓库里装着十几个<strong>各自独立发版</strong>的 Python 包。看懂这张"分层地图"，
你就再也不会在目录里迷路。
</p>

<div class="card analogy">
  <div class="tag">🏗️ 生活类比</div>
  把它想成一栋<strong>分层的大楼</strong>：地基层（core）定义所有"接口标准"，
  楼上的主套间（langchain）放你日常用的高级功能，
  而每个厂商（partners/openai、partners/anthropic）是<strong>可插拔的配件房间</strong>，
  都按地基层的标准接口来装修，所以能随意替换。
</div>

<h2>仓库的物理结构</h2>
<p>所有包都在 <span class="inline">libs/</span> 下。你现在只需认得这几个最重要的：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">langchain/libs/</span><span class="ln">目录结构</span></div>
<pre><span class="cm"># 在仓库根目录执行 ls libs/ 就能看到</span>
libs/
├── <span class="fn">core/</span>            <span class="cm"># langchain-core：地基，所有抽象与接口</span>
├── <span class="fn">langchain/</span>       <span class="cm"># langchain-classic：旧版（维护中，无新功能）</span>
├── <span class="fn">langchain_v1/</span>    <span class="cm"># langchain：当前主力包，你日常 import 的就是它</span>
├── <span class="fn">partners/</span>        <span class="cm"># 各厂商集成：openai / anthropic / ollama ...</span>
│   ├── openai/
│   ├── anthropic/
│   └── ...
├── <span class="fn">text-splitters/</span>  <span class="cm"># 文档切块工具</span>
├── <span class="fn">standard-tests/</span>  <span class="cm"># 给所有 partner 共用的标准测试套件</span>
└── <span class="fn">model-profiles/</span>  <span class="cm"># 模型能力档案（上下文长度、是否支持工具等）</span>
</pre>
</div>

<h2>核心三层：地基 / 主力 / 配件</h2>
<p>十几个包里，理解 LangChain 你<strong>主要只需盯住三层</strong>。它们的依赖方向<strong>永远从上往下</strong>
——上层依赖下层，下层<strong>绝不</strong>反过来依赖上层：</p>

<div class="layers">
  <div class="layer l-part">
    <div class="lh"><span class="badge">集成层</span><span class="name">langchain-openai / langchain-anthropic …</span></div>
    <div class="ld">每个厂商一个独立包，把厂商 SDK 适配成 core 定义的标准接口。
      位置：<span class="mono">libs/partners/*/</span>。换厂商 = 换这一层的包。</div>
  </div>
  <div class="layer l-main">
    <div class="lh"><span class="badge">实现层</span><span class="name">langchain（主力包）</span></div>
    <div class="ld">面向用户的高级功能：<span class="mono">create_agent</span>、<span class="mono">init_chat_model</span>、中间件等。
      位置：<span class="mono">libs/langchain_v1/langchain/</span>。这是你日常写代码 import 的包。</div>
  </div>
  <div class="layer l-core">
    <div class="lh"><span class="badge">地基层</span><span class="name">langchain-core</span></div>
    <div class="ld">最底层抽象：<span class="mono">Runnable</span>、<span class="mono">BaseChatModel</span>、各种
      <span class="mono">Message</span>、<span class="mono">BaseTool</span>。位置：<span class="mono">libs/core/langchain_core/</span>。
      <strong>用户通常不直接 import 它</strong>，但所有东西都建在它之上。</div>
  </div>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解：为什么要分这么多包？</div>
  <ul>
    <li><strong>依赖隔离</strong>：你只装 OpenAI，就不会被迫装上 Anthropic 的 SDK。每个 partner 是独立包，按需安装。</li>
    <li><strong>独立发版</strong>：OpenAI 出了新功能，<span class="mono">langchain-openai</span> 可以自己发版，不用等整个框架。</li>
    <li><strong>稳定地基</strong>：<span class="mono">core</span> 很少变，给所有上层一个稳定的"接口契约"。</li>
  </ul>
</div>

<h2>用依赖关系验证这套分层</h2>
<p>不用记，<strong>看每个包的 <span class="inline">pyproject.toml</span> 就能验证</strong>谁依赖谁。下面是真实内容：</p>

<div class="cols">
  <div class="col">
    <h4>🟢 core 依赖谁？</h4>
    <pre class="code" style="margin:.4rem 0"><span class="cm"># libs/core/pyproject.toml</span>
dependencies = [
  <span class="st">"langsmith"</span>,    <span class="cm"># 追踪</span>
  <span class="st">"pydantic"</span>,     <span class="cm"># 数据校验</span>
  <span class="st">"tenacity"</span>,     <span class="cm"># 重试</span>
  ...
]</pre>
    <p style="font-size:.85rem;color:var(--muted)">没有任何 langchain 包——它是<strong>地基</strong>，谁都不依赖。</p>
  </div>
  <div class="col">
    <h4>🔵 主力包 / partner 依赖谁？</h4>
    <pre class="code" style="margin:.4rem 0"><span class="cm"># langchain_v1/pyproject.toml</span>
dependencies = [
  <span class="st">"langchain-core"</span>,  <span class="cm"># ↓ 依赖地基</span>
  <span class="st">"langgraph"</span>,       <span class="cm"># Agent 引擎</span>
]
<span class="cm"># partners/openai/pyproject.toml</span>
dependencies = [
  <span class="st">"langchain-core"</span>,  <span class="cm"># ↓ 依赖地基</span>
  <span class="st">"openai"</span>,          <span class="cm"># 厂商 SDK</span>
]</pre>
  </div>
</div>

<div class="card detail">
  <div class="tag">🔬 细节：开发工具栈</div>
  这个仓库用一套现代 Python 工具链，后面"贡献"那一课会细讲，先混个眼熟：
  <table class="t" style="margin-top:.6rem">
    <tr><th>工具</th><th>作用</th></tr>
    <tr><td class="mono">uv</td><td>装依赖 / 管理虚拟环境（比 pip 快）</td></tr>
    <tr><td class="mono">ruff</td><td>代码检查 + 格式化</td></tr>
    <tr><td class="mono">mypy</td><td>静态类型检查</td></tr>
    <tr><td class="mono">pytest</td><td>测试框架</td></tr>
    <tr><td class="mono">make</td><td>把上面命令打包成 <span class="mono">make test</span> / <span class="mono">make lint</span></td></tr>
  </table>
  每个包<strong>各自有一份</strong> <span class="mono">pyproject.toml</span> 和 <span class="mono">uv.lock</span>。
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入三个常见疑问。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么用 monorepo，而不是一个大包或彻底分成多个仓库 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 三种方案对比</div>
      <div class="a">
<pre class="code"><span class="cm"># 方案 A：一个大包（all-in-one）</span>
pip install langchain   <span class="cm"># 但会拖进所有厂商 SDK，臃肿</span>

<span class="cm"># 方案 B：彻底分仓库（每个包一个 repo）</span>
<span class="cm"># 跨包改动要开多个 PR，版本对不齐，难维护</span>

<span class="cm"># 方案 C：monorepo（LangChain 的选择）</span>
<span class="cm"># 一个 repo 多个包：按需安装、统一改动、独立发版</span>
pip install langchain langchain-openai   <span class="cm"># 只装你要的</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">LangChain 要同时服务"只用一个厂商的轻量用户"和"跨多包协同的核心开发者"。
        单一大包会让前者背上不必要的依赖；彻底分仓库会让后者的跨包改动（改 core 接口同时更新所有 partner）变成噩梦。</div>
    </div>
    <div class="qa">
      <div class="q">✅ monorepo 的优点</div>
      <div class="a"><strong>按需安装</strong>（只装用到的 partner）、<strong>跨包原子改动</strong>（一个 PR 同时改 core 与 partner）、
        <strong>独立发版</strong>（每个包有自己的版本号与 <span class="mono">pyproject.toml</span>）、<strong>共享工具链</strong>（统一 lint/test 配置）。</div>
    </div>
    <div class="qa">
      <div class="q">🔀 其他方案</div>
      <div class="a">很多项目用<strong>单包 + 可选依赖</strong>（<span class="mono">pip install pkg[openai]</span>）；
        或用 <strong>Nx / Turborepo</strong> 之类的 monorepo 工具。LangChain 用的是"<strong>uv workspace</strong> + 各包独立 <span class="mono">pyproject.toml</span>"的轻量组合。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 地基层 <code>core</code> 里到底有哪些"抽象" <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 目录速览</div>
      <div class="a"><span class="mono">libs/core/langchain_core/</span> 下的主要子目录，每个都是后面某一课的主角：
<pre class="code">langchain_core/
├── <span class="fn">runnables/</span>        <span class="cm"># Runnable 抽象（第 8、9 课）</span>
├── <span class="fn">language_models/</span>  <span class="cm"># BaseChatModel（第 10 课）</span>
├── <span class="fn">messages/</span>         <span class="cm"># Human/AI/Tool/System（第 4 课）</span>
├── <span class="fn">tools/</span>            <span class="cm"># BaseTool / @tool（第 6、11 课）</span>
├── <span class="fn">prompts/</span>          <span class="cm"># 提示词模板</span>
├── <span class="fn">outputs/</span>          <span class="cm"># ChatResult 等输出结构</span>
├── <span class="fn">callbacks/</span>        <span class="cm"># 回调系统（第 13 课）</span>
└── <span class="fn">output_parsers/</span>   <span class="cm"># 把模型输出解析成结构化数据</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这些要放在 core</div>
      <div class="a">它们是<strong>接口契约</strong>：定义"聊天模型长什么样、消息长什么样、工具长什么样"。
        所有上层（主力包、partner）都依赖这些契约，因此它们必须在最底层且<strong>极少变动</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 这样设计的好处</div>
      <div class="a">任何人想加一个新厂商，只要去 <span class="mono">partners/</span> 新建一个包、实现 core 的接口即可，
        <strong>无需改动 core 一行</strong>。这就是"对扩展开放、对修改封闭"。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 一个 partner 包是怎么"适配"厂商的 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 适配器模式</div>
      <div class="a"><span class="mono">langchain-openai</span> 里的 <span class="mono">ChatOpenAI</span> 继承 core 的 <span class="mono">BaseChatModel</span>，
        把"标准接口"翻译成"OpenAI SDK 调用"：
<pre class="code"><span class="cm"># 概念示意（partners/openai/...）</span>
<span class="kw">class</span> <span class="fn">ChatOpenAI</span>(BaseChatModel):
    <span class="kw">def</span> <span class="fn">_generate</span>(self, messages, ...):
        <span class="cm"># 1) 标准消息 → OpenAI 的 JSON 格式</span>
        <span class="cm"># 2) 调用 openai SDK 发请求</span>
        <span class="cm"># 3) OpenAI 响应 → 标准 AIMessage</span>
        ...</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">每个厂商的 API 形状不同。partner 包就是那层"翻译"，把差异<strong>封装在最外层</strong>，
        让上面所有代码都只看到统一的 <span class="mono">BaseChatModel</span>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点 & 🔀 其他方案</div>
      <div class="a">优点：新增 / 升级厂商只动一个独立包，互不影响（这正是第 10 课"模板方法模式"的落点）。
        其他方案：把适配逻辑塞进 core（会让 core 依赖所有厂商 SDK，违背分层）——LangChain 刻意避免了这点。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>一个 Git 仓库 = 多个独立发版的包，全在 <span class="mono">libs/</span> 下。</li>
    <li>盯住三层：<strong>core（地基）→ langchain（主力）→ partners（配件）</strong>，依赖永远从上往下。</li>
    <li>想验证依赖关系，直接读各包的 <span class="mono">pyproject.toml</span>，不用猜。</li>
    <li>下一课：跟着一次真实调用，看数据如何<strong>穿过这三层</strong>。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_03 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
现在把前两课接起来：当你写下 <span class="inline">model.invoke("你好")</span> 的那一刻，
数据具体<strong>穿过哪些层、变成什么形状、最后怎么回来</strong>？这一课用一张"生命周期图"讲透。
</p>

<div class="card analogy">
  <div class="tag">✉️ 生活类比</div>
  这趟旅程就像<strong>寄一封跨国信</strong>：你写中文信（字符串）→ 邮局装进标准信封并贴上规范地址（消息标准化）→
  翻译成目的国语言（厂商 API 格式）→ 寄出、对方回信 → 再翻译回中文 → 装进标准信封交还给你（AIMessage）。
  你只面对"中文信"，<strong>中间的翻译与信封都被框架藏起来了</strong>。
</div>

<h2>一次调用的完整生命周期</h2>
<p>下面每一步都标注了它发生在<strong>哪一层</strong>。重点是数据形状的三次变身：
<strong>字符串 → 标准消息 → 厂商格式 → 标准消息</strong>。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc">
    <h4>你的代码：传入字符串或消息</h4>
    <p>你调用 <span class="mono">model.invoke("北京天气怎么样？")</span>。输入可以是字符串、字典或消息对象。</p>
    <p class="mono">📍 实现层 langchain</p>
  </div></div>
  <div class="step"><div class="num">2</div><div class="sc">
    <h4>标准化：一切都变成 Messages</h4>
    <p>框架把你的输入统一转成一串<strong>标准消息对象</strong>（如 <span class="mono">[HumanMessage("北京天气怎么样？")]</span>）。
      从这里开始，内部只认消息，不认裸字符串。</p>
    <p class="mono">📍 地基层 langchain-core · messages/</p>
  </div></div>
  <div class="step"><div class="num">3</div><div class="sc">
    <h4>进入统一入口 invoke → generate</h4>
    <p><span class="mono">BaseChatModel.invoke()</span> 调用 <span class="mono">generate_prompt → generate</span>，
      这是<strong>所有厂商共享</strong>的模板流程（含缓存、回调、重试）。</p>
    <p class="mono">📍 地基层 · language_models/chat_models.py</p>
  </div></div>
  <div class="step"><div class="num">4</div><div class="sc">
    <h4>翻译成厂商格式并发请求</h4>
    <p>具体 partner（如 <span class="mono">ChatOpenAI._generate</span>）把标准消息<strong>翻译成 OpenAI 的 JSON</strong>，
      通过厂商 SDK 发出 HTTP 请求。</p>
    <p class="mono">📍 集成层 langchain-openai</p>
  </div></div>
  <div class="step"><div class="num">5</div><div class="sc">
    <h4>厂商返回 → 翻译回标准消息</h4>
    <p>OpenAI 返回原始 JSON，partner 把它<strong>翻译回</strong> <span class="mono">AIMessage</span>
      （含正文、可能的工具调用、token 用量等）。</p>
    <p class="mono">📍 集成层 → 地基层</p>
  </div></div>
  <div class="step"><div class="num">6</div><div class="sc">
    <h4>回调触发 + 缓存写入 + 返回给你</h4>
    <p>沿途的<strong>回调（callbacks）</strong>记录这次调用（用于 LangSmith 追踪），结果可能写入缓存，
      最后把 <span class="mono">AIMessage</span> 交还给你。</p>
    <p class="mono">📍 地基层 → 你的代码</p>
  </div></div>
</div>

<h2>用一张层级图再看一遍</h2>
<p>同样的旅程，换成"数据穿过三层"的视角。注意<strong>请求往下走、响应往上回</strong>，
core 提供的统一接口让你的代码<strong>完全不碰最右边的厂商细节</strong>：</p>

<div class="flow" style="flex-direction:column;gap:.6rem">
  <div style="display:flex;align-items:center;gap:.5rem;width:100%">
    <div class="node hl" style="flex:0 0 130px">你的代码</div>
    <div class="arrow">→</div>
    <div class="node" style="flex:1">字符串 / dict</div>
  </div>
  <div style="display:flex;align-items:center;gap:.5rem;width:100%">
    <div class="node hl" style="flex:0 0 130px">langchain (主力)</div>
    <div class="arrow">→</div>
    <div class="node" style="flex:1">标准化为 Messages</div>
  </div>
  <div style="display:flex;align-items:center;gap:.5rem;width:100%">
    <div class="node hl" style="flex:0 0 130px">core (地基)</div>
    <div class="arrow">→</div>
    <div class="node" style="flex:1">invoke → generate（缓存/回调/重试的通用模板）</div>
  </div>
  <div style="display:flex;align-items:center;gap:.5rem;width:100%">
    <div class="node hl" style="flex:0 0 130px">openai (配件)</div>
    <div class="arrow">→</div>
    <div class="node" style="flex:1">翻译成厂商 JSON → 发 HTTP → 翻译回 AIMessage</div>
  </div>
  <div style="text-align:center;color:var(--faint);font-size:.85rem">↑ 响应原路返回，每一层把数据"还原"成上一层认识的形状 ↑</div>
</div>

<div class="card detail">
  <div class="tag">🔬 细节 / 代码对应：关键调用链</div>
  这条链是第三部分"内部源码"的预告，记住这几个方法名即可：
  <table class="t" style="margin-top:.6rem">
    <tr><th>步骤</th><th>方法</th><th>文件</th></tr>
    <tr><td>统一入口</td><td class="mono">BaseChatModel.invoke</td><td class="mono">core · chat_models.py</td></tr>
    <tr><td>模板流程</td><td class="mono">generate_prompt → generate</td><td class="mono">core · chat_models.py</td></tr>
    <tr><td>缓存包装</td><td class="mono">_generate_with_cache</td><td class="mono">core · chat_models.py</td></tr>
    <tr><td>厂商实现</td><td class="mono">ChatOpenAI._generate</td><td class="mono">partners/openai/…</td></tr>
  </table>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解：为什么要这么多次"变身"？</div>
  每一次形状转换都对应一层的<strong>单一职责</strong>：主力层只管"把用户输入规整成消息"，
  地基层只管"通用流程（缓存/回调/重试）"，配件层只管"和某个厂商对话"。
  正因为职责被切干净，<strong>换厂商时只有最底层那一块需要替换</strong>，你上面的代码一行都不用动。
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入两个关键环节。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> "标准化"那一步到底做了什么 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例：同一个调用的多种输入写法</div>
      <div class="a">框架会把下面三种写法<strong>都规整成同一串标准消息</strong>，再往下走：
<pre class="code"><span class="cm"># 写法 1：裸字符串 → 自动当成一条 HumanMessage</span>
model.invoke(<span class="st">"北京天气怎么样？"</span>)

<span class="cm"># 写法 2：消息对象列表</span>
model.invoke([HumanMessage(<span class="st">"北京天气怎么样？"</span>)])

<span class="cm"># 写法 3：(role, content) 元组列表</span>
model.invoke([(<span class="st">"system"</span>, <span class="st">"你是助手"</span>), (<span class="st">"human"</span>, <span class="st">"北京天气？"</span>)])
<span class="cm"># ↑ 三者在内部都变成 list[BaseMessage]</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">让用户写得轻松（可以偷懒传字符串），同时让内部逻辑只需处理<strong>一种</strong>规整形式（消息列表）。
        这种"入口宽容、内部统一"的设计能大幅减少下游分支判断。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">输入灵活但内部干净；所有缓存、回调、厂商适配只需面向 <span class="mono">list[BaseMessage]</span> 编写，复杂度集中在一处。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 缓存、回调、重试是在"哪一层"统一处理的 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 这些"横切能力"的位置</div>
      <div class="a">它们都在<strong>地基层</strong>的通用流程里，<strong>不在</strong>各厂商的 <span class="mono">_generate</span> 里：
<pre class="code">invoke
└─ generate
   └─ _generate_with_cache   <span class="cm"># ← 缓存在这里（命中就不发请求）</span>
      └─ _generate           <span class="cm"># ← 厂商只负责"真正发请求"这一步</span>
<span class="cm"># 回调（on_llm_start/end）与重试也由通用流程统一触发</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这样分</div>
      <div class="a">缓存、回调、重试对<strong>所有厂商都一样</strong>，没必要每个 partner 各写一遍。
        把它们放在通用流程里，partner 作者就只需关心"怎么和我的厂商对话"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点 & 🔀 其他方案</div>
      <div class="a">优点：能力统一、partner 极简、行为一致（换厂商缓存策略不变）。
        其他方案：每个 partner 自行实现缓存/重试（重复、易不一致）——这正是 LangChain 用"模板方法"避免的（第 10 课详解）。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>一次调用 = 数据三次变身：<strong>字符串 → 标准消息 → 厂商格式 → 标准消息</strong>。</li>
    <li>请求往下穿三层、响应原路返回；你的代码只接触最上层的统一接口。</li>
    <li>"统一入口 + 厂商专属 <span class="mono">_generate</span>"是 LangChain 可替换性的核心机关。</li>
    <li>第一部分（宏观）到此结束。下一部分进入<strong>用户视角</strong>，从最小的"消息"开始动手。</li>
  </ul>
</div>
"""
