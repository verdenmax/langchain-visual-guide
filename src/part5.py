"""Content for Part 5 (build your own agent): lessons 15-18."""

# ---------------------------------------------------------------------------
LESSON_15 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
前面我们用一个 <span class="inline">system_prompt</span> 字符串就把 Agent 的"人设"定了。
但真实应用里，提示词往往需要<strong>带变量、插入对话历史、给模型示范</strong>——这就要用到
LangChain 的<strong>提示词模板（Prompt Template）</strong>系统。
</p>

<div class="card analogy">
  <div class="tag">✉️ 生活类比</div>
  提示词模板就像<strong>邮件模板 / 填空题</strong>：你预先写好骨架，留几个空
  （<span class="mono">{name}</span>、<span class="mono">{question}</span>），用的时候把变量填进去，
  就生成一封"具体的信"。它把"提示词的结构"和"每次的具体内容"分开了。
</div>

<h2>从字符串到模板</h2>
<p>最常用的是 <span class="inline">ChatPromptTemplate</span>，它用一组"角色 + 模板字符串"构建一串消息：</p>

<pre class="code"><span class="kw">from</span> langchain_core.prompts <span class="kw">import</span> ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    (<span class="st">"system"</span>, <span class="st">"你是 {domain} 领域的助手，回答要简洁。"</span>),
    MessagesPlaceholder(<span class="st">"history"</span>),     <span class="cm"># ← 这里会插入整段对话历史</span>
    (<span class="st">"human"</span>, <span class="st">"{question}"</span>),
])

messages = prompt.invoke({
    <span class="st">"domain"</span>: <span class="st">"天气"</span>,
    <span class="st">"history"</span>: [],
    <span class="st">"question"</span>: <span class="st">"北京今天热吗？"</span>,
})
<span class="cm"># 得到一串标准消息，可直接喂给模型</span>
</pre>

<div class="card key">
  <div class="tag">🔑 核心认知</div>
  <strong>提示词模板本身也是 Runnable</strong>（第 8 课）。所以它能用 <span class="inline">|</span> 直接接到模型后面，
  组成最经典的链：<span class="inline">prompt | model | parser</span>。
</div>

<div class="flow">
  <div class="node">变量 dict</div><div class="arrow">→</div>
  <div class="node hl">prompt<br><span style="font-weight:400;font-size:.76rem;color:var(--muted)">填空→消息</span></div><div class="arrow">→</div>
  <div class="node hl">model</div><div class="arrow">→</div>
  <div class="node">AIMessage</div>
</div>

<div class="card detail">
  <div class="tag">🔬 代码对应</div>
  <ul>
    <li><span class="mono">ChatPromptTemplate</span> / <span class="mono">MessagesPlaceholder</span> → <span class="mono">core/prompts/chat.py</span></li>
    <li><span class="mono">PromptTemplate</span>（纯字符串提示，给非聊天模型用）→ <span class="mono">core/prompts/prompt.py</span></li>
  </ul>
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，逐个吃透模板的三个能力。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 变量填充：让提示词随输入变化 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">模板里 <span class="mono">{xxx}</span> 是占位符，<span class="mono">invoke</span> 时用 dict 填：
<pre class="code">tpl = ChatPromptTemplate.from_messages([
    (<span class="st">"system"</span>, <span class="st">"用 {style} 的风格回答"</span>),
    (<span class="st">"human"</span>, <span class="st">"{q}"</span>),
])
tpl.invoke({<span class="st">"style"</span>: <span class="st">"幽默"</span>, <span class="st">"q"</span>: <span class="st">"什么是 LLM？"</span>})</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么不直接用 f-string 拼字符串</div>
      <div class="a">模板能<strong>校验缺漏变量</strong>、支持<strong>部分填充</strong>、能和其它 Runnable 组合、还能被序列化/复用。
        手写 f-string 在复杂场景（多角色、插历史、few-shot）会很快失控。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">提示词成为<strong>可复用、可测试、可组合</strong>的组件，而不是散落在代码里的字符串拼接。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> MessagesPlaceholder：把对话历史插进模板 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 它占的是"一串消息"的位置</div>
      <div class="a">普通 <span class="mono">{var}</span> 填的是一段文本；而 <span class="mono">MessagesPlaceholder("history")</span>
        填的是<strong>一整串消息</strong>（之前的多轮对话）：
<pre class="code">prompt.invoke({
    <span class="st">"history"</span>: [HumanMessage(<span class="st">"上一轮问题"</span>), AIMessage(<span class="st">"上一轮回答"</span>)],
    <span class="st">"question"</span>: <span class="st">"接着问"</span>,
})</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a">多轮对话要把"历史消息"原样塞进提示词的中间位置。占位符让你能<strong>动态注入任意长度的历史</strong>，
        正好衔接第 4 课的"上下文管理"——你裁剪/摘要后的历史，就从这里放进去。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">把"系统设定 + 历史 + 当前问题"清晰分层，历史的拼装与裁剪逻辑和提示词结构解耦。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> few-shot：用示范教模型怎么答 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 思路</div>
      <div class="a">在提示词里塞几组"输入→理想输出"的<strong>范例</strong>，模型会照着学：
<pre class="code">examples = [
    (<span class="st">"human"</span>, <span class="st">"2+2"</span>), (<span class="st">"ai"</span>, <span class="st">"4"</span>),
    (<span class="st">"human"</span>, <span class="st">"3+5"</span>), (<span class="st">"ai"</span>, <span class="st">"8"</span>),
]
prompt = ChatPromptTemplate.from_messages([
    (<span class="st">"system"</span>, <span class="st">"只输出数字结果"</span>), *examples, (<span class="st">"human"</span>, <span class="st">"{q}"</span>),
])</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么有效</div>
      <div class="a">大模型擅长<strong>模仿示范</strong>。给几个例子（few-shot），常比写一大段规则更能稳定输出格式与风格——
        这是"提示工程"里性价比最高的技巧之一。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 进阶</div>
      <div class="a">LangChain 还有 <span class="mono">FewShotChatMessagePromptTemplate</span> 与"示例选择器"，能按当前问题<strong>动态挑最相关的范例</strong>。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>提示词模板把"结构"与"具体内容"分离：<span class="mono">ChatPromptTemplate.from_messages([...])</span>。</li>
    <li><span class="mono">{var}</span> 填文本，<span class="mono">MessagesPlaceholder</span> 填一整串历史消息。</li>
    <li>模板是 <strong>Runnable</strong>，可直接 <span class="mono">prompt | model | parser</span>。</li>
    <li>few-shot（给范例）是稳定输出格式的利器。</li>
    <li>下一课：给 Agent 接一个它没学过的<strong>知识库</strong>——RAG。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_16 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
模型只懂它训练时见过的东西，<strong>不知道你的私有文档、公司知识库、最新资料</strong>。
RAG（检索增强生成）解决这个问题：<strong>先去知识库里检索相关片段，再把它塞进提示词让模型据此回答</strong>。
这是绝大多数真实 Agent 的标配。
</p>

<div class="card analogy">
  <div class="tag">📖 生活类比</div>
  RAG 就是把"闭卷考试"变成"<strong>开卷考试</strong>"：不靠模型死记硬背，而是每次答题前
  先翻书找到相关那几页（检索），再照着这几页作答（生成）。模型负责"会读会写"，知识库负责"提供资料"。
</div>

<h2>RAG 的五个零件 + 一条流水线</h2>
<p>把文档变成"可被检索的知识"，再到"喂给模型"，要经过五个零件。记住这条流水线，RAG 就不神秘了：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Document：装载文档</h4>
    <p>把原始资料读成 <span class="mono">Document</span>（含 <span class="mono">page_content</span> + <span class="mono">metadata</span>）。</p>
    <p class="mono">core/documents/base.py</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Splitter：切成小块</h4>
    <p>长文档切成若干小片（chunk），便于精准检索与控制 token。</p>
    <p class="mono">langchain_text_splitters</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Embeddings：变成向量</h4>
    <p>把每个文本块编码成一串数字（向量），<strong>语义相近 → 向量相近</strong>。</p>
    <p class="mono">core/embeddings/embeddings.py</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>VectorStore：存入向量库</h4>
    <p>把"文本块 + 向量"存起来，支持按相似度快速搜索。</p>
    <p class="mono">core/vectorstores/base.py</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Retriever：按问题召回</h4>
    <p>把用户问题也编码成向量，找出<strong>最相近的几个文本块</strong>返回。</p>
    <p class="mono">core/retrievers.py</p></div></div>
</div>

<h2>代码：十几行搭一个 RAG</h2>
<pre class="code"><span class="kw">from</span> langchain_text_splitters <span class="kw">import</span> RecursiveCharacterTextSplitter

<span class="cm"># 1~2) 文档 → 切块</span>
splits = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)

<span class="cm"># 3~4) 嵌入 + 存入向量库（embeddings 来自某个 partner，如 OpenAIEmbeddings）</span>
vectorstore = SomeVectorStore.from_documents(splits, embedding=embeddings)

<span class="cm"># 5) 得到一个检索器</span>
retriever = vectorstore.as_retriever(search_kwargs={<span class="st">"k"</span>: 4})

docs = retriever.invoke(<span class="st">"北京的退货政策是什么？"</span>)   <span class="cm"># → list[Document]，最相关的 4 块</span>
</pre>

<div class="card key">
  <div class="tag">🔑 核心认知</div>
  <strong>Retriever 本身就是一个 Runnable</strong>（<span class="mono">retriever.invoke(query)</span>）。
  所以它能像积木一样：① 直接拼进 LCEL 链（<span class="mono">{"context": retriever, ...} | prompt | model</span>），
  或 ② 包成一个<strong>工具</strong>交给 Agent，让 Agent 自己决定"何时该查知识库"。
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，吃透 RAG 的关键细节。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么要"切块"和"嵌入" <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">❓ 为什么要切块（chunking）</div>
      <div class="a">整篇文档太长，既塞不进上下文，也让检索不精准。切成小块后，能<strong>只召回真正相关的那几段</strong>，
        省 token 又更准。<span class="mono">chunk_overlap</span> 让相邻块有重叠，避免把一句话从中间切断丢失语义。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 嵌入(Embeddings)到底在做什么</div>
      <div class="a">把文本映射成向量，使<strong>语义相近的文本向量也相近</strong>。于是"检索相关内容"就变成了
        "在向量空间里找最近邻"——这叫<strong>语义检索</strong>，比关键词匹配能理解"意思相近但用词不同"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">Embeddings</span> 抽象（<span class="mono">embed_query</span> / <span class="mono">embed_documents</span>）在
        <span class="mono">core/embeddings/embeddings.py</span>；具体实现（如 <span class="mono">OpenAIEmbeddings</span>）在对应 partner 包。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 两种用法：拼进链 vs 当作工具 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 用法 A：固定的 RAG 链（每次都先检索）</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> langchain_core.runnables <span class="kw">import</span> RunnablePassthrough
rag = (
    {<span class="st">"context"</span>: retriever, <span class="st">"question"</span>: RunnablePassthrough()}
    | prompt | model | parser
)
rag.invoke(<span class="st">"退货政策？"</span>)   <span class="cm"># 一定会先检索再回答</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">🧪 用法 B：把检索器变成工具，交给 Agent</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> langchain_core.tools <span class="kw">import</span> tool
<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">search_kb</span>(query: str) -> str:
    <span class="st">&quot;&quot;&quot;在公司知识库中检索相关资料。&quot;&quot;&quot;</span>
    <span class="kw">return</span> <span class="st">"\n"</span>.join(d.page_content <span class="kw">for</span> d <span class="kw">in</span> retriever.invoke(query))

agent = create_agent(model, tools=[search_kb])   <span class="cm"># Agent 自己决定要不要查</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 怎么选</div>
      <div class="a">问答场景"每次都该查" → 用<strong>固定 RAG 链</strong>（简单、可控）；
        通用 Agent"有时要查、有时不用" → 把检索<strong>做成工具</strong>，让模型按需调用，更灵活。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> Retriever 不止向量库 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 统一抽象 BaseRetriever</div>
      <div class="a"><span class="mono">BaseRetriever</span>（<span class="mono">core/retrievers.py</span>）只规定一件事：
        "给一个查询，返回一串 <span class="mono">Document</span>"。向量库检索只是它最常见的一种实现。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 还能是什么</div>
      <div class="a">关键词检索（BM25）、数据库查询、搜索引擎 API、甚至混合检索（向量 + 关键词），
        都能包装成同一个 <span class="mono">Retriever</span> 接口。对上层而言，"怎么检索的"被隐藏了。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">因为 <span class="mono">BaseRetriever</span> 是 Runnable，任何检索来源都能无缝接进链或做成工具——又一次体现统一抽象的威力。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>RAG = <strong>先检索、再生成</strong>：把私有/最新知识喂给模型，突破"只懂训练数据"的局限。</li>
    <li>流水线五件套：<span class="mono">Document → Splitter → Embeddings → VectorStore → Retriever</span>。</li>
    <li>切块控制精度与 token；嵌入实现<strong>语义检索</strong>（按意思找，不只按词）。</li>
    <li><span class="mono">Retriever</span> 是 Runnable：可拼进链，也可包成工具交给 Agent。</li>
    <li>下一课：当内置中间件不够用，<strong>写你自己的中间件</strong>来定制 Agent。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_17 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 7、12 课我们<strong>用</strong>过内置中间件（限流、人审、重试…）。当它们不够用时，
定制自己 Agent 的<strong>核心钥匙</strong>就是——<strong>写你自己的中间件</strong>。这是 Agent 最强大的扩展点。
</p>

<div class="card analogy">
  <div class="tag">🧅 生活类比</div>
  中间件就像<strong>洋葱的一层层皮</strong>，也像 Web 框架的 middleware：每次请求都<strong>从外向里穿过每一层</strong>，
  再<strong>从里向外穿回来</strong>。每一层都能在"进去前"和"出来后"做点事——记录、改写、拦截、重试。
</div>

<h2>六个钩子：在循环的关键点插入逻辑</h2>
<p>一个中间件可以实现下面任意几个<strong>钩子方法</strong>，框架会在对应时机自动调用：</p>

<table class="t">
  <tr><th>钩子</th><th>触发时机</th><th>典型用途</th></tr>
  <tr><td class="mono">before_agent</td><td>整个 Agent 开始时（一次）</td><td>初始化、鉴权</td></tr>
  <tr><td class="mono">before_model</td><td>每次调用模型<strong>前</strong></td><td>裁剪历史、注入提示</td></tr>
  <tr><td class="mono">wrap_model_call</td><td><strong>包裹</strong>整个模型调用</td><td>改请求/响应、重试、降级</td></tr>
  <tr><td class="mono">after_model</td><td>每次调用模型<strong>后</strong></td><td>校验/改写模型输出</td></tr>
  <tr><td class="mono">wrap_tool_call</td><td><strong>包裹</strong>每次工具调用</td><td>工具级重试、审计</td></tr>
  <tr><td class="mono">after_agent</td><td>整个 Agent 结束时（一次）</td><td>收尾、记录指标</td></tr>
</table>

<div class="flow" style="flex-direction:column;gap:.5rem;align-items:stretch">
  <div style="text-align:center;color:var(--muted);font-size:.82rem">before_agent → 〔循环：before_model → (wrap_model_call) 模型 → after_model → (wrap_tool_call) 工具 〕→ after_agent</div>
</div>

<h2>两种写法</h2>
<div class="cols">
  <div class="col">
    <h4>① 装饰器（轻量）</h4>
    <pre class="code" style="margin:.4rem 0"><span class="kw">from</span> langchain.agents.middleware <span class="kw">import</span> before_model

<span class="nb">@before_model</span>
<span class="kw">def</span> <span class="fn">log_turns</span>(state, runtime):
    print(len(state[<span class="st">"messages"</span>]))
    <span class="kw">return</span> None   <span class="cm"># None = 不改状态</span></pre>
  </div>
  <div class="col">
    <h4>② 类（功能全）</h4>
    <pre class="code" style="margin:.4rem 0"><span class="kw">from</span> langchain.agents.middleware <span class="kw">import</span> AgentMiddleware

<span class="kw">class</span> <span class="fn">Guard</span>(AgentMiddleware):
    <span class="kw">def</span> <span class="fn">before_model</span>(self, state, runtime):
        ...
    <span class="kw">def</span> <span class="fn">wrap_model_call</span>(self, request, handler):
        <span class="kw">return</span> handler(request)</pre>
  </div>
</div>
<pre class="code">agent = create_agent(model, tools, middleware=[Guard()])   <span class="cm"># 装上即生效</span></pre>

<div class="card detail">
  <div class="tag">🔬 代码对应</div>
  <ul>
    <li><span class="mono">AgentMiddleware</span> 基类与全部钩子 → <span class="mono">agents/middleware/types.py</span></li>
    <li>装饰器 <span class="mono">before_model / after_model / wrap_model_call / wrap_tool_call / before_agent / after_agent / dynamic_prompt</span>
      与 <span class="mono">ModelRequest / ModelResponse</span> → 从 <span class="mono">langchain.agents.middleware</span> 导出</li>
  </ul>
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，逐个吃透中间件机制。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 六个钩子分别在何时触发 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 执行顺序</div>
      <div class="a">
<pre class="code">before_agent                <span class="cm"># 仅一次</span>
└─ 循环开始
   before_model             <span class="cm"># 每轮模型调用前</span>
   wrap_model_call ─ 模型 ─┐ <span class="cm"># 包在模型调用外层</span>
   after_model  ◄──────────┘ <span class="cm"># 每轮模型调用后</span>
   wrap_tool_call ─ 工具      <span class="cm"># 每次工具调用外层</span>
└─ 循环结束
after_agent                 <span class="cm"># 仅一次</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ before_model vs wrap_model_call 区别</div>
      <div class="a"><span class="mono">before_model</span> 只能在调用<strong>前</strong>改状态（返回一个 state 更新）；
        <span class="mono">wrap_model_call</span> <strong>同时掌控前后</strong>：能改请求、决定是否调用、还能改/重试响应——更强但也更重。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 多个中间件怎么叠</div>
      <div class="a">多个中间件像洋葱<strong>层层包裹</strong>：靠前的在最外层。<span class="mono">wrap_*</span> 钩子可决定"是否、何时"调用内层（<span class="mono">handler</span>）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> wrap_model_call：拦截并改写模型调用 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 模式：改请求 → 调 handler → 改响应</div>
      <div class="a">
<pre class="code"><span class="kw">def</span> <span class="fn">wrap_model_call</span>(self, request, handler):
    <span class="cm"># request 里有 model / messages / tools / system_prompt / state / runtime</span>
    request.messages = trim(request.messages)   <span class="cm"># 改请求</span>
    response = handler(request)                  <span class="cm"># 真正调用模型（内层）</span>
    <span class="cm"># 这里可检查 response，必要时改写或用不同 request 重试</span>
    <span class="kw">return</span> response</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 它为什么这么关键</div>
      <div class="a">内置的 <span class="mono">ModelRetryMiddleware</span> / <span class="mono">ModelFallbackMiddleware</span>（第 7 课）
        正是基于 <span class="mono">wrap_model_call</span> 实现的——失败就换个 <span class="mono">request</span> 再调一次 <span class="mono">handler</span>。
        你也能用它做"动态换模型、按内容改提示、缓存"等任意定制。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">request</span> 是 <span class="mono">ModelRequest</span>（字段：model/messages/system_prompt/tools/tool_choice/state/runtime），
        定义在 <span class="mono">agents/middleware/types.py</span>。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> dynamic_prompt：让系统提示词随状态变化 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> langchain.agents.middleware <span class="kw">import</span> dynamic_prompt

<span class="nb">@dynamic_prompt</span>
<span class="kw">def</span> <span class="fn">make_prompt</span>(request):
    user = request.runtime.context.user_id
    <span class="kw">return</span> <span class="st">f"你在为用户 {user} 服务，回答要个性化。"</span>
<span class="cm"># 每轮根据运行时上下文/状态，动态生成系统提示词</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 与固定 system_prompt 的区别</div>
      <div class="a">固定 <span class="mono">system_prompt</span> 是写死的字符串；<span class="mono">dynamic_prompt</span> 能在<strong>每次调用时</strong>
        根据当前状态/运行时上下文（如用户身份、检索结果）<strong>实时生成</strong>提示词。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">把"提示词工程"也变成可编程的中间件，适合多租户、个性化、A/B 实验等场景。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>中间件是 Agent 的核心扩展点：六个钩子 <span class="mono">before_agent / before_model / wrap_model_call / after_model / wrap_tool_call / after_agent</span>。</li>
    <li>两种写法：<strong>装饰器</strong>（轻量）与<strong>继承 AgentMiddleware</strong>（功能全）。</li>
    <li><span class="mono">wrap_model_call</span> 能改请求/响应、重试、降级——内置的 retry/fallback 都基于它。</li>
    <li><span class="mono">dynamic_prompt</span> 让系统提示词随运行时上下文动态生成。</li>
    <li>下一课：把运行时数据传进去（context）、加降级、把思考流式推给 UI。</li>
  </ul>
</div>
"""

# ---------------------------------------------------------------------------
LESSON_18 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
最后一公里，三件让 Agent 真正"上生产"的事：把每次运行的数据（如 <span class="inline">user_id</span>）
<strong>安全地传进去</strong>、给调用<strong>加降级兜底</strong>、把 Agent 的思考过程<strong>流式推给 UI</strong>。
</p>

<div class="card analogy">
  <div class="tag">🎒 生活类比</div>
  <strong>运行时上下文</strong>像随身工牌：每次进门（每次 invoke）出示，门里的人（工具/中间件）都能看到"你是谁"，
  但它<strong>不会被写进对话记录</strong>。<strong>降级</strong>像备用发电机；<strong>流式</strong>像现场直播进度。
</div>

<h2>① 运行时上下文：context_schema</h2>
<p>有些数据（用户 id、租户、权限）<strong>不该放进消息</strong>（会污染对话、还可能被模型乱用），
但工具和中间件又需要它。用 <span class="inline">context_schema</span> 声明，再在 invoke 时通过 <span class="inline">context=</span> 传入：</p>

<pre class="code"><span class="kw">from</span> dataclasses <span class="kw">import</span> dataclass
<span class="kw">from</span> langchain.tools <span class="kw">import</span> ToolRuntime

<span class="nb">@dataclass</span>
<span class="kw">class</span> <span class="fn">Context</span>:
    user_id: str

<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">my_orders</span>(runtime: ToolRuntime) -> str:
    <span class="st">&quot;&quot;&quot;查询当前用户的订单。&quot;&quot;&quot;</span>
    <span class="kw">return</span> db.query(runtime.context.user_id)   <span class="cm"># 工具读到 user_id，但模型看不到这个参数</span>

agent = create_agent(model, tools=[my_orders], context_schema=Context)
agent.invoke({<span class="st">"messages"</span>: [...]}, context={<span class="st">"user_id"</span>: <span class="st">"u1"</span>})   <span class="cm"># 每次运行传入</span>
</pre>

<h2>② 健壮性：with_fallbacks</h2>
<p>任何 Runnable 都能挂一条<strong>降级链</strong>：主选项失败时，自动依次尝试备用选项。</p>
<pre class="code">robust_model = primary_model.with_fallbacks([backup_model])
<span class="cm"># primary 报错 → 自动改用 backup，对调用方透明</span>
</pre>

<h2>③ 流式给 UI：stream_mode</h2>
<p>Agent 的 <span class="inline">stream</span> 可以选不同<strong>粒度</strong>，决定你能在界面上看到什么：</p>
<table class="t">
  <tr><th>stream_mode</th><th>你拿到什么</th><th>适合</th></tr>
  <tr><td class="mono">"updates"</td><td>每个节点产生的<strong>增量</strong>（哪步做了什么）</td><td>显示"正在调用工具…"</td></tr>
  <tr><td class="mono">"messages"</td><td>模型<strong>逐 token</strong> 的输出</td><td>打字机效果</td></tr>
  <tr><td class="mono">"values"</td><td>每步后的<strong>完整状态快照</strong></td><td>调试 / 全量同步</td></tr>
</table>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，吃透这三件事。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么运行时数据不放进消息，而走 context <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">❓ 放进消息会怎样</div>
      <div class="a">把 <span class="mono">user_id</span>、密钥之类塞进消息，会：① <strong>浪费 token</strong>；② <strong>被模型当成可改的内容</strong>
        （甚至被提示注入篡改）；③ 污染对话历史。这些数据是"<strong>给程序用的</strong>"，不是"给模型读的"。</div>
    </div>
    <div class="qa">
      <div class="q">🧪 谁能读到 context</div>
      <div class="a"><strong>工具</strong>通过注入的 <span class="mono">ToolRuntime</span>（<span class="mono">runtime.context</span>）读；
        <strong>中间件</strong>通过钩子里的 <span class="mono">runtime.context</span> 读。模型<strong>完全看不到</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">context_schema</span> 是 <span class="mono">create_agent</span> 参数；<span class="mono">ToolRuntime</span> 从 <span class="mono">langchain.tools</span> 导出
        （底层 <span class="mono">langgraph.prebuilt</span>）。对比第 6 课的 <span class="mono">InjectedState</span>（读对话状态）——context 读的是"运行时配置"。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> with_fallbacks：任意 Runnable 的降级兜底 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 不止用于模型</div>
      <div class="a">因为是 Runnable 通用能力，<strong>链、工具、解析器</strong>都能挂降级：
<pre class="code"><span class="cm"># 主模型贵但强，备用便宜；主挂了就降级</span>
model = strong.with_fallbacks([cheap])
<span class="cm"># 也可用于"主解析失败 → 退而求其次"的解析链</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 与 with_retry 的区别</div>
      <div class="a"><span class="mono">with_retry</span>（第 5 课）是"<strong>同一个</strong>选项重试几次"；
        <span class="mono">with_fallbacks</span> 是"主选项不行就<strong>换别的</strong>选项"。常组合使用：先重试，仍失败再降级。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">with_fallbacks</span> 定义在 <span class="mono">core/runnables/base.py</span>，产物是 <span class="mono">RunnableWithFallbacks</span>。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 给 Agent UI 选对的 stream_mode <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 示例</div>
      <div class="a">
<pre class="code"><span class="kw">for</span> chunk <span class="kw">in</span> agent.stream(input, stream_mode=<span class="st">"updates"</span>):
    <span class="cm"># 每个节点一步步的增量：可据此显示"思考中 / 调用工具中"</span>
    ...</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 三种模式怎么选</div>
      <div class="a">要展示"<strong>Agent 在做什么</strong>"（调了哪个工具）→ <span class="mono">"updates"</span>；
        要"<strong>打字机</strong>"逐字显示最终回答 → <span class="mono">"messages"</span>；
        要<strong>调试/全量</strong>状态 → <span class="mono">"values"</span>。三者可按需组合订阅。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 关联</div>
      <div class="a">这建立在第 13 课的流式与 <span class="mono">astream_events</span> 之上——Agent 是 Runnable，所以天然支持流式，只是多了"按节点"的粒度。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 本课要点 & 结业</div>
  <ul>
    <li><span class="mono">context_schema</span> + <span class="mono">invoke(context=...)</span>：把 user_id 等运行时数据安全注入工具/中间件，<strong>不进消息</strong>。</li>
    <li><span class="mono">with_fallbacks</span>：任意 Runnable 的降级兜底；与 <span class="mono">with_retry</span> 配合更稳。</li>
    <li><span class="mono">stream_mode</span>（updates / messages / values）：给 Agent UI 选对的流式粒度。</li>
    <li>🎉 <strong>恭喜！你已具备从零搭建并定制一个生产级 Agent 的全部知识地图。</strong>去把这些零件拼成你自己的 Agent 吧！</li>
  </ul>
</div>
"""

