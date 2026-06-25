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
  <strong>提示词模板本身也是 Runnable</strong>（第 10 课）。所以它能用 <span class="inline">|</span> 直接接到模型后面，
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
        正好衔接第 6 课的"上下文管理"——你裁剪/摘要后的历史，就从这里放进去。</div>
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

<h2>🔬 实现细节与亮点</h2>
<p>看清提示词模板在源码里是怎么把"变量 + 模板"变成"一串消息"的，以及它聪明在哪。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/prompts/chat.py</span><span class="ln">invoke → format_prompt → ChatPromptValue</span></div>
<pre><span class="kw">class</span> <span class="fn">ChatPromptTemplate</span>(BaseChatPromptTemplate):   <span class="cm"># ← 它是 Runnable</span>
    <span class="kw">def</span> <span class="fn">format_messages</span>(self, **kwargs) -> list[BaseMessage]:
        result = []
        <span class="kw">for</span> part <span class="kw">in</span> self.messages:        <span class="cm"># 逐个模板片段</span>
            <span class="kw">if</span> isinstance(part, MessagesPlaceholder):
                result.extend(kwargs[part.variable_name])  <span class="cm"># 展开成"一串消息"</span>
            <span class="kw">else</span>:
                result.append(part.format(**kwargs))        <span class="cm"># 填变量→一条消息</span>
        <span class="kw">return</span> result
    <span class="kw">def</span> <span class="fn">format_prompt</span>(self, **kwargs) -> ChatPromptValue:
        <span class="kw">return</span> ChatPromptValue(messages=self.format_messages(**kwargs))
</pre>
</div>

<div class="card detail">
  <div class="tag">🔬 实现流程</div>
  <ol>
    <li><span class="mono">invoke(vars)</span> → <span class="mono">format_prompt</span> → 返回一个 <strong>PromptValue</strong>（<span class="mono">ChatPromptValue</span>）。</li>
    <li><span class="mono">format_messages</span> 遍历每个模板片段：普通片段<strong>填变量得一条消息</strong>，
      <span class="mono">MessagesPlaceholder</span> 则把变量里的<strong>一串消息整段展开</strong>。</li>
    <li><span class="mono">from_messages([(role, tmpl), ...])</span> 在构建时由 <span class="mono">_convert_to_message_template</span>
      把 <span class="mono">("system","…")</span> 这类元组解析成对应的<strong>消息模板对象</strong>。</li>
  </ol>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>提示词是 Runnable</strong>：所以能直接 <span class="mono">prompt | model</span> 拼链——又一次复用第 10 课的统一抽象，无需任何"胶水"。</li>
    <li><strong>PromptValue 作中间层</strong>：同一份模板既能 <span class="mono">.to_messages()</span>（喂聊天模型）又能 <span class="mono">.to_string()</span>（喂纯文本 LLM），<strong>一套模板适配两类模型</strong>。</li>
    <li><strong>占位符是一等公民</strong>：<span class="mono">MessagesPlaceholder</span> 让"插入任意长度历史"成为模板语法的一部分，把第 6 课的上下文管理与提示词结构干净地解耦。</li>
  </ul>
</div>

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
<div class="card warn">
  <div class="tag">⚠️ 这是骨架示意</div>
  下面 <span class="mono">docs</span> / <span class="mono">embeddings</span> / <span class="mono">SomeVectorStore</span> 是<strong>占位</strong>，
  请替换成真实对象（下方"深入理解"里有<strong>可直接运行</strong>的完整版）。
</div>
<pre class="code"><span class="kw">from</span> langchain_text_splitters <span class="kw">import</span> RecursiveCharacterTextSplitter

<span class="cm"># 0) docs：上一步加载好的文档 list[Document]；embeddings = OpenAIEmbeddings() 之类</span>
<span class="cm"># 1~2) 文档 → 切块</span>
splits = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)

<span class="cm"># 3~4) 嵌入 + 存入向量库（SomeVectorStore 换成真实实现，如 InMemoryVectorStore / Chroma）</span>
vectorstore = SomeVectorStore.from_documents(splits, embedding=embeddings)

<span class="cm"># 5) 得到一个检索器</span>
retriever = vectorstore.as_retriever(search_kwargs={<span class="st">"k"</span>: 4})

hits = retriever.invoke(<span class="st">"北京的退货政策是什么？"</span>)   <span class="cm"># → list[Document]，最相关的 4 块</span>
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

<details class="accordion">
  <summary><span class="badge-num">4</span> 上手不用装库：InMemoryVectorStore + 增量索引 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 零依赖向量库（教学/测试首选）</div>
      <div class="a">不想先装一个向量数据库？core 自带一个纯内存实现，几行就能跑通整条 RAG：
<pre class="code"><span class="kw">from</span> langchain_core.vectorstores <span class="kw">import</span> InMemoryVectorStore

vs = InMemoryVectorStore.from_texts(["北京晴", "上海雨"], embedding=embeddings)
vs.similarity_search("北京天气", k=1)</pre>
        位置：<span class="mono">core/vectorstores/in_memory.py</span>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 真实项目：怎么避免每次全量重嵌入</div>
      <div class="a">文档会更新，但大部分没变。core 的<strong>索引 API</strong> 用一个 <span class="mono">RecordManager</span> 记录"哪些文档已入库"，
        <span class="mono">index()</span> 只对<strong>新增/变更</strong>的文档重新嵌入入库，并清理已删除的：
<pre class="code"><span class="kw">from</span> langchain_core.indexing <span class="kw">import</span> index   <span class="cm"># indexing/api.py</span>
index(docs, record_manager, vectorstore, cleanup=<span class="st">"incremental"</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">✅ 为什么重要</div>
      <div class="a">这正是"<strong>玩具 RAG</strong> ↔ <strong>可维护 RAG</strong>"的分水岭：避免重复嵌入（省钱省时）、自动去重、同步删除。
        <span class="mono">RecordManager</span> 在 <span class="mono">indexing/base.py</span>（含内存版 <span class="mono">InMemoryRecordManager</span>）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">5</span> 别手写：create_retriever_tool + 嵌入缓存 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 一行把检索器变成 Agent 工具</div>
      <div class="a">前面"用法 B"我们手写了 <span class="mono">@tool</span>，其实有现成助手：
<pre class="code"><span class="kw">from</span> langchain_core.tools <span class="kw">import</span> create_retriever_tool

kb_tool = create_retriever_tool(
    retriever, name=<span class="st">"search_kb"</span>, description=<span class="st">"检索公司知识库"</span>)
agent = create_agent(model, tools=[kb_tool])</pre>
        位置：<span class="mono">core/tools/retriever.py</span>。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 嵌入太贵？给它加缓存</div>
      <div class="a"><span class="mono">CacheBackedEmbeddings</span>（<span class="mono">langchain_classic/embeddings/cache.py</span>）
        把"文本 → 向量"的结果缓存起来，<strong>相同文本不再重复调用嵌入 API</strong>，显著省钱（尤其重复构建索引时）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 小结</div>
      <div class="a">真实 RAG 的"省心三件套"：<span class="mono">create_retriever_tool</span>（少写胶水）、
        嵌入缓存（省钱）、索引 API（增量更新）。</div>
    </div>
  </div>
</details>

<h2>🔬 实现细节与亮点</h2>
<p>RAG 的三个零件在源码里各有精巧之处——看 Retriever 如何"白嫖"Runnable 能力，以及切分器如何在语义边界下刀。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/retrievers.py</span><span class="ln">BaseRetriever.invoke（含回调）</span></div>
<pre><span class="kw">class</span> <span class="fn">BaseRetriever</span>(RunnableSerializable, ABC):   <span class="cm"># ← 检索器也是 Runnable</span>
    <span class="kw">def</span> <span class="fn">invoke</span>(self, input, config=None):
        run_manager = callback_manager.on_retriever_start(...)   <span class="cm"># 追踪开始</span>
        result = self._get_relevant_documents(input, ...)        <span class="cm"># ← 子类只实现这个</span>
        run_manager.on_retriever_end(result)                     <span class="cm"># 追踪结束</span>
        <span class="kw">return</span> result
</pre>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">text-splitters/langchain_text_splitters/character.py</span><span class="ln">递归切分</span></div>
<pre><span class="kw">class</span> <span class="fn">RecursiveCharacterTextSplitter</span>(TextSplitter):
    <span class="cm"># 默认分隔符：从"粗"到"细"</span>
    separators = [<span class="st">"\n\n"</span>, <span class="st">"\n"</span>, <span class="st">" "</span>, <span class="st">""</span>]   <span class="cm"># 段落 → 行 → 词 → 字符</span>
    <span class="kw">def</span> <span class="fn">_split_text</span>(self, text, separators):
        <span class="cm"># 先用最粗的分隔符切；某块仍太大，就用更细的分隔符"递归"再切</span>
        ... <span class="kw">then</span> _merge_splits(...)   <span class="cm"># 按 chunk_size 合并，相邻块留 overlap</span>
</pre>
</div>

<div class="card detail">
  <div class="tag">🔬 实现要点</div>
  <ul>
    <li><strong>Retriever</strong>：子类只需实现 <span class="mono">_get_relevant_documents</span>，<span class="mono">invoke</span> 自动包上回调/追踪/异步。</li>
    <li><strong>VectorStore.search</strong>（<span class="mono">vectorstores/base.py</span>）按 <span class="mono">search_type</span> 分发：
      <span class="mono">similarity</span> / <span class="mono">similarity_score_threshold</span> / <span class="mono">mmr</span>；
      <span class="mono">VectorStoreRetriever</span>（<span class="mono">同文件</span>）只是<strong>委托</strong>调用它。</li>
    <li><strong>切分器</strong>：递归用越来越细的分隔符切，再 <span class="mono">_merge_splits</span> 按 <span class="mono">chunk_size</span> 打包、留 <span class="mono">chunk_overlap</span>。</li>
  </ul>
</div>

<details class="accordion">
  <summary><span class="badge-num">6</span> 从"能跑"到"答得准"：RAG 调优清单 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 四个最该调的旋钮</div>
      <div class="a">
<pre class="code">chunk_size / chunk_overlap   <span class="cm"># 切太大→噪声多，切太小→语义碎；常见 300~800 字 + 10~15% 重叠</span>
k（检索条数）                <span class="cm"># 太少漏召回，太多塞爆上下文；常从 4~8 起调</span>
重排序 reranking            <span class="cm"># 先粗召回 ~20 条，再用 reranker 精排取前几条，准确率显著提升</span>
嵌入模型                    <span class="cm"># 中文优先 BGE / bge-m3；换更强的嵌入往往比改 prompt 更有效</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 怎么知道调好了：要评估</div>
      <div class="a">别凭感觉。准备一组"问题 → 应命中的文档"，量<strong>召回率</strong>（该召回的有没有召回）和
        <strong>答案正确率</strong>。工具如 <span class="mono">Ragas</span>（第 24 课"横切带"提到过）可自动打分。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 常见翻车点</div>
      <div class="a">① 文档没清洗（页眉页脚/乱码也进了向量）；② 切块把表格/代码拦腰斩断；
        ③ 只调 prompt 不调检索——<strong>RAG 的上限通常卡在"检索"而非"生成"</strong>。</div>
    </div>
  </div>
</details>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>检索器"白嫖"Runnable 能力</strong>：只写 <span class="mono">_get_relevant_documents</span> 一个方法，就免费获得回调追踪、异步、可拼链——典型的"模板方法 + 统一抽象"。</li>
    <li><strong>递归切分保语义</strong>：优先在<strong>段落</strong>边界下刀，不行才退到行、词、字符。尽量不把一句话拦腰斩断，这对检索质量至关重要。</li>
    <li><strong>召回策略可切换</strong>：<span class="mono">search_type="mmr"</span> 能在"相关"之外兼顾"<strong>多样性</strong>"（避免召回一堆near-重复片段），一个检索器多副面孔。</li>
  </ul>
</div>

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
第 9、15 课我们<strong>用</strong>过内置中间件（限流、人审、重试…）。当它们不够用时，
定制自己 Agent 的<strong>核心钥匙</strong>就是——<strong>写你自己的中间件</strong>。这是 Agent 最强大的扩展点。
</p>

<div class="card analogy">
  <div class="tag">🧅 生活类比</div>
  中间件就像<strong>洋葱的一层层皮</strong>，也像 Web 框架的 middleware：每次请求都<strong>从外向里穿过每一层</strong>，
  再<strong>从里向外穿回来</strong>。每一层都能在"进去前"和"出来后"做点事——记录、改写、拦截、重试。
</div>

<h2>七个钩子：在循环的关键点插入逻辑</h2>
<p>一个中间件可以实现下面任意几个<strong>钩子方法</strong>，框架会在对应时机自动调用：</p>

<table class="t">
  <tr><th>钩子</th><th>触发时机</th><th>典型用途</th></tr>
  <tr><td class="mono">before_agent</td><td>整个 Agent 开始时（一次）</td><td>初始化、鉴权</td></tr>
  <tr><td class="mono">before_model</td><td>每次调用模型<strong>前</strong></td><td>裁剪历史、注入提示</td></tr>
  <tr><td class="mono">dynamic_prompt</td><td>每次调用模型<strong>前</strong>（生成系统提示）</td><td>按状态切换 system prompt</td></tr>
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
  <summary><span class="badge-num">1</span> 七个钩子分别在何时触发 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 执行顺序</div>
      <div class="a">
<pre class="code">before_agent                <span class="cm"># 仅一次</span>
└─ 循环开始
   before_model             <span class="cm"># 每轮模型调用前</span>
   dynamic_prompt           <span class="cm"># 每轮模型调用前·按状态生成系统提示</span>
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
    <span class="cm"># request 里有 model / messages / tools / system_message / state / runtime</span>
    new_req = request.override(messages=trim(request.messages))  <span class="cm"># 改请求（用 override，别直接赋值）</span>
    response = handler(new_req)                   <span class="cm"># 真正调用模型（内层）</span>
    <span class="cm"># 这里可检查 response，必要时改写或用不同 request 重试</span>
    <span class="kw">return</span> response</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 它为什么这么关键</div>
      <div class="a">内置的 <span class="mono">ModelRetryMiddleware</span> / <span class="mono">ModelFallbackMiddleware</span>（第 9 课）
        正是基于 <span class="mono">wrap_model_call</span> 实现的——失败就换个 <span class="mono">request</span> 再调一次 <span class="mono">handler</span>。
        你也能用它做"动态换模型、按内容改提示、缓存"等任意定制。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 代码对应</div>
      <div class="a"><span class="mono">request</span> 是 <span class="mono">ModelRequest</span>（字段：model/messages/<strong>system_message</strong>/tools/tool_choice/state/runtime；
        <span class="mono">system_prompt</span> 是已废弃的别名），
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

<h2>三个真实场景：中间件到底能干什么</h2>
<p>光看钩子名字没体感，来看三个生产里最常写的中间件——全部基于 <span class="mono">wrap_model_call</span> / <span class="mono">override</span>：</p>
<details class="accordion">
  <summary><span class="badge-num">4</span> 案例库：PII 脱敏 / 成本限速 / A·B 切模型 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 ① PII 脱敏（wrap_model_call + override）</div>
      <div class="a">只把<strong>发给模型的那份副本</strong>脱敏（手机号/邮箱 → 占位符），原始对话历史<strong>原封不动</strong>：
<pre class="code"><span class="kw">class</span> <span class="fn">PIIRedaction</span>(AgentMiddleware):
    <span class="kw">def</span> <span class="fn">wrap_model_call</span>(self, request, handler):
        clean = request.override(messages=redact(request.messages))
        <span class="kw">return</span> handler(clean)        <span class="cm"># 敏感数据不出本地</span></pre></div>
    </div>
    <div class="qa">
      <div class="q">🧪 ② 成本 / 限速护栏（wrap_model_call）</div>
      <div class="a">累加每次调用的 token，超预算就<strong>短路</strong>或降级换更便宜的模型：
<pre class="code"><span class="kw">class</span> <span class="fn">Budget</span>(AgentMiddleware):
    <span class="kw">def</span> <span class="fn">wrap_model_call</span>(self, request, handler):
        <span class="kw">if</span> self.spent &gt; self.cap:
            <span class="kw">raise</span> RuntimeError(<span class="st">"预算用尽"</span>)      <span class="cm"># 或 override 换便宜模型</span>
        resp = handler(request)
        ai = resp.result[-1]                  <span class="cm"># 最新的 AIMessage</span>
        self.spent += (ai.usage_metadata <span class="kw">or</span> {}).get(<span class="st">"total_tokens"</span>, 0)
        <span class="kw">return</span> resp</pre></div>
    </div>
    <div class="qa">
      <div class="q">🧪 ③ A/B 切模型（wrap_model_call + override）</div>
      <div class="a">放一部分流量到候选模型，灰度对比效果——上线新模型的常用手法：
<pre class="code"><span class="kw">class</span> <span class="fn">ABModel</span>(AgentMiddleware):
    <span class="kw">def</span> <span class="fn">wrap_model_call</span>(self, request, handler):
        <span class="kw">if</span> random.random() &lt; 0.1:             <span class="cm"># 10% 流量走候选</span>
            request = request.override(model=candidate)
        <span class="kw">return</span> handler(request)</pre></div>
    </div>
    <div class="qa">
      <div class="q">✅ 共同套路</div>
      <div class="a"><strong>读改状态</strong>用 <span class="mono">before/after_model</span>（返回 state 更新）；
        <strong>拦截 / 改请求 / 重试 / 短路一次调用</strong>用 <span class="mono">wrap_model_call</span>——
        靠 <span class="mono">request.override(...)</span> 造新请求、靠 <span class="mono">handler(...)</span> 决定调不调、调几次。内置的 retry/fallback/限流就是这么写的。</div>
    </div>
  </div>
</details>

<h2>🔬 实现细节与亮点</h2>
<p>这是第五部分最值得深挖的一处：<strong>两类钩子用了两种完全不同的实现机制</strong>——这正是 middleware 既灵活又高效的秘密。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">langchain/agents/factory.py</span><span class="ln">机制一：before/after 钩子 → 真实图节点</span></div>
<pre><span class="cm"># 被覆盖的 before_model / after_model 会被编译成 LangGraph 的"节点"</span>
graph.add_node(f<span class="st">"{m.name}.before_model"</span>, before_node, ...)
graph.add_node(f<span class="st">"{m.name}.after_model"</span>,  after_node,  ...)
<span class="cm"># 再用边把它们按顺序串进循环：…before_model → model → after_model…</span>
</pre>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">langchain/agents/factory.py</span><span class="ln">机制二：wrap_* 钩子 → 洋葱式函数组合</span></div>
<pre><span class="kw">def</span> <span class="fn">_chain_model_call_handlers</span>(handlers):
    <span class="cm"># "第一个 middleware 成为最外层；每层拿到一个 handler 回调去执行内层"</span>
    <span class="cm"># 组合成嵌套函数：outer(req, handler=inner(req, handler=...真正调模型))</span>
    ...
</pre>
</div>

<div class="card detail">
  <div class="tag">🔬 两种机制</div>
  <ul>
    <li><strong>状态型钩子</strong>（<span class="mono">before_agent/before_model/after_model/after_agent</span>）：返回一个 state 更新，
      被编译成<strong>图里的真实节点</strong>，按顺序执行。</li>
    <li><strong>包裹型钩子</strong>（<span class="mono">wrap_model_call/wrap_tool_call</span>）：不是节点，而是被
      <span class="mono">_chain_model_call_handlers</span> 组合成<strong>层层嵌套的函数</strong>，每层拿到 <span class="mono">handler</span> 去调内层。（<span class="mono">dynamic_prompt</span> 本质上也属此类——包裹模型调用、生成 system prompt 的便捷写法。）</li>
    <li>哪些钩子被启用？框架检查<strong>子类是否覆盖了该方法</strong>（基类默认是 no-op，返回 <span class="mono">None</span>），没覆盖就<strong>不进图</strong>。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>两类钩子两种实现，各取所长</strong>：要"读改状态"的用图节点（清晰、可被 LangGraph 持久化）；要"包裹前后/决定是否调用"的用嵌套函数（能重试、能短路）。</li>
    <li><strong>洋葱组合解释了 retry/fallback</strong>：<span class="mono">wrap_model_call</span> 拿到 <span class="mono">handler</span> 回调，可<strong>重复调用</strong>内层——这就是 <span class="mono">ModelRetry/ModelFallback</span>"失败再调一次"的实现原理。第一个 middleware 在最外层。</li>
    <li><strong>零开销原则</strong>：没被覆盖的钩子<strong>根本不会进图</strong>，不写就没成本——既灵活又不拖慢循环。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>中间件是 Agent 的核心扩展点：七个钩子 <span class="mono">before_agent / before_model / dynamic_prompt / wrap_model_call / after_model / wrap_tool_call / after_agent</span>。</li>
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
<span class="kw">from</span> langchain_core.tools <span class="kw">import</span> tool
<span class="kw">from</span> langchain.tools <span class="kw">import</span> ToolRuntime
<span class="kw">from</span> langchain.chat_models <span class="kw">import</span> init_chat_model
<span class="kw">from</span> langchain.agents <span class="kw">import</span> create_agent

<span class="nb">@dataclass</span>
<span class="kw">class</span> <span class="fn">Context</span>:
    user_id: str

<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">my_orders</span>(runtime: ToolRuntime) -> str:
    <span class="st">&quot;&quot;&quot;查询当前用户的订单。&quot;&quot;&quot;</span>
    <span class="kw">return</span> db.query(runtime.context.user_id)   <span class="cm"># 工具读到 user_id，但模型看不到这个参数</span>

model = init_chat_model(<span class="st">"openai:gpt-5.1"</span>)
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
        （底层 <span class="mono">langgraph.prebuilt</span>）。对比第 8 课的 <span class="mono">InjectedState</span>（读对话状态）——context 读的是"运行时配置"。</div>
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
      <div class="a"><span class="mono">with_retry</span>（第 7 课）是"<strong>同一个</strong>选项重试几次"；
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
      <div class="a">这建立在第 16 课的流式与 <span class="mono">astream_events</span> 之上——Agent 是 Runnable，所以天然支持流式，只是多了"按节点"的粒度。</div>
    </div>
  </div>
</details>

<h2>🔬 实现细节与亮点</h2>
<p>看 context 如何作为"侧信道"独立于消息流动，以及 <span class="inline">with_fallbacks</span> 降级的真实实现。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">core/langchain_core/runnables/fallbacks.py</span><span class="ln">RunnableWithFallbacks.invoke</span></div>
<pre><span class="kw">class</span> <span class="fn">RunnableWithFallbacks</span>(RunnableSerializable):
    <span class="cm"># runnables = [主选项, 备用1, 备用2, ...]</span>
    exceptions_to_handle = (Exception,)        <span class="cm"># 只有这些异常才触发降级</span>
    <span class="kw">def</span> <span class="fn">invoke</span>(self, input, config=None):
        <span class="kw">for</span> runnable <span class="kw">in</span> self.runnables:    <span class="cm"># 依次尝试</span>
            <span class="kw">try</span>:
                <span class="kw">return</span> runnable.invoke(input, ...)   <span class="cm"># 首个成功即返回</span>
            <span class="kw">except</span> self.exceptions_to_handle <span class="kw">as</span> e:
                last_error = e                  <span class="cm"># 否则换下一个</span>
        <span class="kw">raise</span> last_error                        <span class="cm"># 全失败才抛出</span>
</pre>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">langchain/agents/factory.py</span><span class="ln">context 是独立通道</span></div>
<pre><span class="cm"># 运行时上下文不进 state/messages，而是图的一条独立"通道"</span>
graph = StateGraph(state_schema, context_schema=context_schema)
<span class="cm"># invoke(..., context={...}) 注入；工具经 ToolRuntime、中间件经 runtime.context 读取</span>
</pre>
</div>

<div class="card detail">
  <div class="tag">🔬 实现要点</div>
  <ul>
    <li><strong>fallbacks</strong>：<span class="mono">runnables</span> 是 <span class="mono">[主, 备1, 备2…]</span>，<span class="mono">invoke</span> 顺序尝试，
      只捕获 <span class="mono">exceptions_to_handle</span> 内的异常，首个成功即返回，全败则抛最后一个。</li>
    <li><strong>context</strong>：<span class="mono">context_schema</span> 传给 <span class="mono">StateGraph</span>，成为与 <span class="mono">state</span> 平行的
      <strong>独立通道</strong>；通过 <span class="mono">Runtime.context</span> 读取，<strong>从不进入消息列表</strong>。</li>
    <li><strong>stream_mode</strong>：编译出的图天然支持多模式流（<span class="mono">updates / messages / values</span>）。</li>
  </ul>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>context 是"侧信道"</strong>：与对话状态、消息<strong>物理隔离</strong>。既不耗 token、不被模型读到，也杜绝了"提示注入篡改 user_id"这类安全问题。</li>
    <li><strong>exceptions_to_handle 精准降级</strong>：默认只对 <span class="mono">Exception</span> 降级，但你能指定"<strong>只对超时/限流降级，对鉴权错误直接抛</strong>"——避免把真正的 bug 悄悄吞掉。</li>
    <li><strong>多粒度流式来自"图"</strong>：因为 Agent 是编译后的图，<span class="mono">stream</span> 能按"节点更新 / 逐 token / 完整快照"产出，<strong>同一个 Agent 适配不同 UI</strong>，无需改实现。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">context_schema</span> + <span class="mono">invoke(context=...)</span>：把 user_id 等运行时数据安全注入工具/中间件，<strong>不进消息</strong>。</li>
    <li><span class="mono">with_fallbacks</span>：任意 Runnable 的降级兜底；与 <span class="mono">with_retry</span> 配合更稳。</li>
    <li><span class="mono">stream_mode</span>（updates / messages / values）：给 Agent UI 选对的流式粒度。</li>
    <li>零件都齐了——<strong>下一课把它们拼成一个完整可跑的 Agent</strong>。</li>
  </ul>
</div>
"""


# ---------------------------------------------------------------------------
LESSON_CAP = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
前面 19 课，你学的都是<strong>一个个零件</strong>。这一课把它们<strong>拼成一台完整的机器</strong>：
一个能查知识库、查订单、按用户身份个性化、带护栏、给结构化答复的<strong>客服 Agent</strong>。
你会看到——每一块，都是前面学过的东西。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  之前是在认识<strong>螺丝、齿轮、电机</strong>；现在我们把它们<strong>组装成一台机器</strong>。
  神奇的是：组装过程几乎没有"新知识"，全是把学过的零件<strong>插到对的接口上</strong>——
  这正是 LangChain 统一抽象的最终回报。
</div>

<h2>零件 → 课程对照地图</h2>
<p>这个 Agent 用到的每一块，都能追溯到前面的某一课：</p>
<table class="t">
  <tr><th>零件</th><th>作用</th><th>来自</th></tr>
  <tr><td class="mono">init_chat_model</td><td>聊天模型</td><td>第 7 课</td></tr>
  <tr><td class="mono">@tool（查订单）</td><td>调用外部系统</td><td>第 8 课</td></tr>
  <tr><td class="mono">create_retriever_tool</td><td>RAG 知识库工具</td><td>第 19 课</td></tr>
  <tr><td class="mono">system_prompt</td><td>人设与规则</td><td>第 18 课</td></tr>
  <tr><td class="mono">AgentMiddleware</td><td>审计 / 护栏</td><td>第 20 课</td></tr>
  <tr><td class="mono">context_schema</td><td>注入 user_id</td><td>第 21 课</td></tr>
  <tr><td class="mono">response_format</td><td>结构化答复</td><td>第 7 课</td></tr>
  <tr><td class="mono">create_agent</td><td>把以上接成循环</td><td>第 9 / 15 课</td></tr>
</table>

<h2>完整代码：拼起来其实就这么短</h2>
<pre class="code"><span class="kw">from</span> dataclasses <span class="kw">import</span> dataclass
<span class="kw">from</span> pydantic <span class="kw">import</span> BaseModel
<span class="kw">from</span> langchain.chat_models <span class="kw">import</span> init_chat_model
<span class="kw">from</span> langchain.agents <span class="kw">import</span> create_agent
<span class="kw">from</span> langchain.agents.middleware <span class="kw">import</span> AgentMiddleware
<span class="kw">from</span> langchain_core.tools <span class="kw">import</span> tool, create_retriever_tool
<span class="kw">from</span> langchain.tools <span class="kw">import</span> ToolRuntime

<span class="cm"># ① 运行时上下文（第 21 课）：每次请求带 user_id，不进消息</span>
<span class="nb">@dataclass</span>
<span class="kw">class</span> <span class="fn">Ctx</span>:
    user_id: str

<span class="cm"># ② 工具（第 8 课）：查订单，用 runtime 读当前用户</span>
<span class="nb">@tool</span>
<span class="kw">def</span> <span class="fn">get_order_status</span>(order_id: str, runtime: ToolRuntime) -> str:
    <span class="st">&quot;&quot;&quot;查询订单状态。&quot;&quot;&quot;</span>
    <span class="kw">return</span> orders_db.status(runtime.context.user_id, order_id)

<span class="cm"># ③ RAG（第 19 课）：把知识库检索器变成一个工具</span>
kb_tool = create_retriever_tool(retriever, <span class="st">"search_kb"</span>, <span class="st">"检索退换货等政策"</span>)

<span class="cm"># ④ 自定义中间件（第 20 课）：每轮审计 + 护栏</span>
<span class="kw">class</span> <span class="fn">AuditMiddleware</span>(AgentMiddleware):
    <span class="kw">def</span> <span class="fn">before_model</span>(self, state, runtime):
        log.info(<span class="st">"user=%s turns=%d"</span>, runtime.context.user_id, len(state[<span class="st">"messages"</span>]))
        <span class="kw">return</span> None

<span class="cm"># ⑤ 结构化答复（第 7 课）</span>
<span class="kw">class</span> <span class="fn">Reply</span>(BaseModel):
    answer: str
    resolved: bool

<span class="cm"># ⑥ 组装（第 9、15 课）：一个 create_agent 把以上全部接起来</span>
agent = create_agent(
    model=init_chat_model(<span class="st">"openai:gpt-5.1"</span>),                <span class="cm"># 第 7 课</span>
    tools=[get_order_status, kb_tool],                       <span class="cm"># 第 8、19 课</span>
    system_prompt=<span class="st">"你是友好的客服，先查资料再回答，不要编造。"</span>,   <span class="cm"># 第 18 课</span>
    middleware=[AuditMiddleware()],                          <span class="cm"># 第 20 课</span>
    context_schema=Ctx,                                      <span class="cm"># 第 21 课</span>
    response_format=Reply,                                   <span class="cm"># 第 7 课</span>
)

<span class="cm"># ⑦ 跑起来：context 带身份，输出是结构化的 Reply</span>
result = agent.invoke(
    {<span class="st">"messages"</span>: [{<span class="st">"role"</span>: <span class="st">"user"</span>, <span class="st">"content"</span>: <span class="st">"我的订单 A123 到哪了？"</span>}]},
    context={<span class="st">"user_id"</span>: <span class="st">"u_42"</span>},
)
print(result[<span class="st">"structured_response"</span>])   <span class="cm"># Reply(answer=..., resolved=...)</span>
</pre>

<h2>一次真实请求，数据怎么流</h2>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>进入：带身份的请求</h4>
    <p>用户消息 + <span class="mono">context={"user_id": "u_42"}</span> 进入 Agent 图。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>中间件先跑</h4>
    <p><span class="mono">AuditMiddleware.before_model</span> 记录这一轮（读到 user_id，但不污染对话）。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>模型决定用哪个工具</h4>
    <p>模型看到"订单"→ 请求 <span class="mono">get_order_status("A123")</span>；若问政策则请求 <span class="mono">search_kb</span>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>工具执行（带上下文）</h4>
    <p><span class="mono">get_order_status</span> 通过 <span class="mono">runtime.context.user_id</span> 只查"这个用户"的订单，结果回灌为 ToolMessage。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>循环 + 结构化收尾</h4>
    <p>模型据工具结果作答；因设了 <span class="mono">response_format</span>，最终给出 <span class="mono">Reply(answer, resolved)</span>。</p></div></div>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>几乎没有"新代码"，全是拼装</strong>：每个零件都是前面学过的 Runnable / 抽象，插到 <span class="mono">create_agent</span> 的对应参数上即可。</li>
    <li><strong>关注点分离得很干净</strong>：身份走 context、护栏走 middleware、知识走 RAG 工具、格式走 response_format——彼此不纠缠，可单独替换/测试。</li>
    <li><strong>可平滑长大</strong>：要记忆就加 <span class="mono">checkpointer</span>，要人审就加 <span class="mono">HumanInTheLoopMiddleware</span>，要多 Agent 就把它当子图——都不用重写核心。</li>
  </ul>
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，看这个 Agent 如何继续长大与被测试。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 加记忆：让它记住多轮对话 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 一行加持久化</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> langgraph.checkpoint.memory <span class="kw">import</span> InMemorySaver
agent = create_agent(..., checkpointer=InMemorySaver())
agent.invoke(inp, config={<span class="st">"configurable"</span>: {<span class="st">"thread_id"</span>: <span class="st">"u_42"</span>}})  <span class="cm"># 同 thread 记住上下文</span></pre>
        （第 15 课）按 <span class="mono">thread_id</span> 区分会话，自动存取历史。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 配合上下文管理</div>
      <div class="a">历史变长时，叠加 <span class="mono">SummarizationMiddleware</span>（第 6 课）自动摘要，控制 token。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 给 UI 流式：显示"正在查订单…" <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 用 stream_mode</div>
      <div class="a">
<pre class="code"><span class="kw">for</span> ev <span class="kw">in</span> agent.stream(inp, context=ctx, stream_mode=<span class="st">"updates"</span>):
    ...  <span class="cm"># 每个节点的增量：模型/工具步骤，驱动进度提示</span></pre>
        要逐字打字机用 <span class="mono">"messages"</span>；要细到每一步事件用 <span class="mono">astream_events</span>（第 16 课）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 测试：不联网也能验证整个 Agent <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 用假模型替换真模型</div>
      <div class="a">
<pre class="code"><span class="kw">from</span> langchain_core.language_models.fake_chat_models <span class="kw">import</span> GenericFakeChatModel
test_agent = create_agent(model=GenericFakeChatModel(messages=iter([...])), tools=[...])
<span class="cm"># 断言它在该调工具时调了工具、最终结构化字段正确</span></pre>
        （第 17 课）单测禁网、用假模型，快速稳定地验证 Agent 的<strong>编排逻辑</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 分层测</div>
      <div class="a">工具单独测（纯函数）、链/Agent 用假模型测编排、真模型留给集成测试——三层各司其职。</div>
    </div>
  </div>
</details>

<div class="card key">
  <div class="tag">✅ 本课要点 & 全书结业</div>
  <ul>
    <li>一个真实 Agent = <strong>把学过的零件插到 <span class="mono">create_agent</span> 的对应参数上</strong>：model / tools / system_prompt / middleware / context_schema / response_format。</li>
    <li>身份走 <strong>context</strong>、护栏走 <strong>middleware</strong>、知识走 <strong>RAG 工具</strong>、格式走 <strong>response_format</strong>——关注点干净分离。</li>
    <li>要长大很平滑：<span class="mono">checkpointer</span> 加记忆、<span class="mono">stream_mode</span> 加 UI、假模型做测试。</li>
    <li>🎉 <strong>恭喜你走完 LangChain 主线！</strong>你已经把它从<strong>宏观结构</strong>、<strong>用户用法</strong>、<strong>内部源码</strong>到<strong>自己动手做 Agent</strong> 完整走了一遍。接下来是<strong>番外篇（3 课）</strong>：先把 LangChain 与微软 AutoGen 对照，再<strong>缩放看整个 AI 全栈坐标系</strong>，最后给你<strong>隔壁层（推理/向量检索）的学习地图</strong>。</li>
  </ul>
</div>
"""
