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
