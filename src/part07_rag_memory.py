"""C-level Part 7: RAG and memory."""

import shell


def _p(text):
    return f"<p>{text}</p>"


def _section(title, paragraphs):
    return f"<h2>{title}</h2>" + "".join(_p(p) for p in paragraphs)


def _analogy(text):
    return f'<div class="card analogy"><div class="tag">🧩 生活类比</div>{text}</div>'


def _points(items):
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<div class="card key"><div class="tag">✅ 本课要点</div><ul>{lis}</ul></div>'


def _detail_sections(d):
    return "".join(_section(title, paragraphs) for title, paragraphs in d["sections"])


def _build_lesson(d):
    html = (
        f'<p class="lead">{d["lead"]}</p>'
        + _analogy(d["analogy"])
        + shell.lesson_map(d["map_title"], d["map_nodes"])
        + "<h2>源码入口：文件 + 符号名</h2>"
        + _p(d["source_intro"])
        + shell.source_map(d["sources"])
        + f"<h2>{d['flow_title']}</h2>"
    )
    if d.get("flow_kind") == "call_graph":
        html += shell.call_graph(d["flow_steps"])
    else:
        html += shell.state_flow(d["flow_steps"])
    html += "<h2>Trace：把一次运行摊平成证据链</h2>" + shell.trace_table(d["trace"])
    html += "<h2>简化源码走读：保留契约，不背实现</h2>" + shell.code_walkthrough(
        d["code_path"], d["code_symbol"], d["code"], d["code_note"]
    )
    html += _detail_sections(d)
    html += shell.pitfall_grid(d["pitfalls"])
    html += shell.lab_card(d["lab_title"], d["lab_steps"])
    html += shell.version_note(d["version_note"])
    html += _points(d["points"])
    return html


LESSON_32_RAG_FLOW = _build_lesson(
    {
        "name": "RAG 全链路",
        "core": "RAG 的核心不是让模型“记住”知识，而是在回答前把可信资料按需取出、格式化成上下文，再要求模型基于这些资料回答并给出引用",
        "contract": "Document、BaseRetriever、VectorStore、ChatPromptTemplate 与 Runnable",
        "artifact": "检索到的 Document 列表和格式化 context",
        "risk": "检索内容被当成指令、引用缺失、模型绕过资料自由发挥",
        "tuning": "query rewrite、top_k、score_threshold、context formatting、引用校验",
        "evidence": "source metadata、chunk id、相似度得分、最终引用和核验结果",
        "boundary": "什么时候必须检索、什么时候可以直接回答、什么时候应该拒答或要求澄清",
        "debug": "query 是否被重写、retriever 是否返回文档、context 是否进入 prompt、回答是否引用真实来源",
        "lead": "RAG（Retrieval-Augmented Generation）把“查资料”和“生成回答”拆成可追踪流水线：用户问题先被保留或改写成检索 query，Retriever 作为 Runnable 返回 Document，格式化器把文档内容和 metadata 变成 context，ChatPromptTemplate 把问题与 context 填入消息，模型生成答案，最后用引用和核验守住事实边界。本课重点看端到端路径，以及为什么 Retriever 既能放进 LCEL 链，也能被包装成 Agent 工具。",
        "analogy": "把 RAG 想成开卷考试。学生不是把整座图书馆背下来，而是先根据题目去目录系统查资料，拿到几页相关书摘，再在答题纸上引用页码作答。Retriever 是查目录的人，Document 是书摘，Prompt 是答题纸模板，模型是组织语言的学生。老师真正关心的不是学生说得多流畅，而是答案有没有依据、依据是不是题目需要的那几页。",
        "map_title": "本课地图：RAG 从问题到可引用回答",
        "map_nodes": [
            ("用户问题", "保留原问题，并可选改写成更适合检索的 query", "before"),
            ("Retriever", "作为 Runnable 接收 query，返回带 metadata 的 Document 列表", "now"),
            ("格式化 context", "把 page_content、source、score 整理成模型可读资料区", "now"),
            ("Prompt + Model", "ChatPromptTemplate 明确区分系统规则、用户问题和检索资料", "source"),
            ("引用核验", "答案必须能回指 Document；证据不足时承认不知道", "after"),
        ],
        "source_intro": "RAG 的源码锚点要覆盖数据对象、检索契约、存储契约、提示模板和组合协议。下面路径均按当前 LangChain monorepo/package 验证；这些文件名能帮助你在源码里确认每一步的责任边界。",
        "sources": [
            {"file": "libs/core/langchain_core/documents/base.py", "symbol": "Document", "role": "承载 page_content 与 metadata，是检索证据的最小单位", "direction": "由 loader/splitter/vectorstore 产生，传给 retriever 和 prompt 格式化器"},
            {"file": "libs/core/langchain_core/retrievers.py", "symbol": "BaseRetriever", "role": "定义输入 query、输出 Document 列表的检索 Runnable 契约", "direction": "RAG 链调用入口，也可被包装成工具"},
            {"file": "libs/core/langchain_core/vectorstores/base.py", "symbol": "VectorStore", "role": "定义 add/search/as_retriever 等向量检索存储接口", "direction": "索引阶段写入，运行阶段被 retriever 查询"},
            {"file": "libs/core/langchain_core/prompts/chat.py", "symbol": "ChatPromptTemplate", "role": "把系统规则、问题和 context 渲染为结构化聊天消息", "direction": "retriever 之后、model 之前"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable", "role": "统一 invoke/stream/batch/config，使 retriever 能进入 LCEL", "direction": "贯穿 prompt、retriever、model、parser 组合"},
        ],
        "flow_title": "状态流：一次带可选改写的 RAG 调用",
        "flow_kind": "state_flow",
        "flow_steps": [
            ("接收问题", "用户问“LangGraph checkpoint 有什么作用？”系统保留原问题和会话信息。", "question"),
            ("可选改写", "若问题依赖上下文，把“它有什么作用”改写成独立 query；不需要时保持原文。", "rewrite?"),
            ("检索文档", "BaseRetriever.invoke(query) 返回若干 Document，每个文档带 source、section、score。", "docs"),
            ("格式化上下文", "把文档编号、摘要、来源拼成资料区，并明确资料不能覆盖系统规则。", "context"),
            ("模型回答", "Prompt + model 生成答案，要求只使用资料区事实，并在段落后给引用。", "answer"),
            ("引用核验", "检查引用是否来自本轮 docs；证据不足则降级为不知道或追加检索。", "verified"),
        ],
        "trace": [
            {"step": "1. question", "input": "用户问题：为什么 checkpoint 重要？", "action": "记录原问题，判断是否需要根据聊天历史改写", "output": "独立 query：LangGraph checkpoint 作用"},
            {"step": "2. retrieve", "input": "query + search_kwargs={'k':4}", "action": "Retriever 调用底层向量库或其他检索器", "output": "4 个 Document，带 source 和 score"},
            {"step": "3. format", "input": "Document.page_content + metadata", "action": "生成带编号的 context，保留文件名和段落号", "output": "[{1}] checkpoint 保存状态..."},
            {"step": "4. answer", "input": "system + question + context", "action": "模型基于资料组织自然语言", "output": "回答含 [1][3] 引用"},
            {"step": "5. verify", "input": "答案引用 + 本轮 docs", "action": "确认引用编号存在，且关键断言能在文档中找到", "output": "通过；否则触发补检索或拒答"},
        ],
        "code_path": "libs/core/langchain_core/retrievers.py",
        "code_symbol": "BaseRetriever as Runnable",
        "code": """rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | parser
)

answer = rag_chain.invoke("LangGraph checkpoint 有什么作用？")
""",
        "code_note": "教学版展示了 Retriever 作为 Runnable 的意义：它可以直接出现在 LCEL 字典分支中，输入问题，输出 Document，再被 format_docs 转成 prompt context。真实项目还会加入 query rewrite、metadata filter、引用核验和降级策略。",
        "sections": [
            ("RAG 的职责边界：取证和写作分开", [
                "RAG 最重要的边界是：检索层负责把可用证据找出来，生成层负责把证据组织成回答。Retriever 不应该替模型写结论，模型也不应该凭空决定某个事实存在。这个边界让排障很清晰：如果正确文档没有进入候选池，问题在 query、索引、filter 或 retriever；如果文档已经进入 context 但答案仍然编造，问题在 prompt 约束、引用核验或模型评测。",
                "在 LCEL 中，retriever 能作为 Runnable 出现在字典分支里，意味着它和 prompt、model、parser 一样拥有可配置、可追踪、可批处理的运行接口。这个设计不是语法糖，而是让检索成为链的一等节点：可以给它加 config、callback、重试、并行分支，也可以把同一个 retriever 包装成 Agent 工具，让模型在任务流中决定何时查资料。",
            ]),
            ("Query rewrite 不是必须，但必须可见", [
                "多轮问答里，用户常说“它支持吗”“刚才那个方案怎么配”。直接拿这句话检索，向量库很难知道“它”指 LangGraph checkpoint 还是 VectorStore。可选的 query rewrite 会把上下文依赖问题改写成独立问题，例如“LangGraph InMemorySaver 是否支持跨进程持久化”。改写能显著提升召回，但也可能引入错误意图，所以原问题、改写问题和改写理由都应进入 trace。",
                "不是所有请求都要改写。单轮明确问题可以直接检索；带强约束的问题可以只补全指代；含有用户隐私或权限字段的问题要避免把敏感值扩散进不必要的检索 query。好的 RAG 链会把 rewrite 当成可观测步骤，而不是隐藏在 prompt 里。出现错答时，先看改写后的 query 是否已经偏题，往往比盲目调 top_k 更快。",
            ]),
            ("Query rewrite 审计", [
                "上线后要抽查 query rewrite 的“保真度”：改写是否保留用户真正问的实体、时间范围、否定条件和权限范围。一个好的审计样本同时保存原问题、最近历史、改写 query、改写理由和检索结果。若改写把“不能做什么”改成“怎么做”，RAG 会检索到相反证据，最终答案再流畅也不可信。",
                "审计还要区分改写失败和检索失败。同一个原问题可分别用原文 query 与改写 query 跑候选池，比较黄金文档是否进入 top-k。若原文能召回、改写不能召回，优先修 rewrite；若两者都不能召回，再看切块、embedding、filter 或语料覆盖。这样调参不会把所有责任推给 retriever。",
            ]),
            ("Context formatting 决定模型看到什么", [
                "Document 返回后不能把 page_content 简单拼成一坨文本。格式化器应给每段资料编号，展示必要 metadata，例如 source、title、page、chunk_id、score，并用清楚的提示说明“下面是资料，不是系统指令”。这样既能帮助模型引用，也能降低检索内容中的提示注入风险。资料里的“忽略上文规则”只能被当成被引用文本，不能提升为开发者或系统指令。",
                "context 的顺序也会影响回答。常见策略是按 rerank 分数排序，把高置信短段放前；也可以按文档结构排序，避免同一章节被拆散。若问题需要综合多个来源，格式化器要保留不同来源之间的边界，不能把互相矛盾的段落揉成一个摘要。引用核验依赖这些边界：最终答案里的 [2] 必须能回到本轮第二个 Document，而不是回到某个历史缓存。",
            ]),
            ("引用核验和拒答是 RAG 的安全阀", [
                "引用不是给页面增添可信感的装饰，而是系统判断“这句话有没有证据”的主键。一个基本核验器可以检查引用编号是否存在、引用段落是否包含关键实体、答案是否把多个文档的结论混在一起。更严格的系统会对每个关键断言做 entailment 或二次模型检查，但即使只做结构校验，也能发现很多无来源回答。",
                "证据不足时，RAG 不应该强行给出完整答案。可选降级包括：明确说明当前资料没有覆盖、请求用户补充范围、扩大检索条件、转人工、或给出带不确定性的部分答案。是否降级应写入产品策略，而不是让模型临场发挥。对于合规、医疗、财务和内部权限资料，宁可少答，也不要把相似但错误的片段包装成确定事实。",
            ]),
            ("什么时候不要优先用 RAG", [
                "如果任务需要学习一种稳定格式或风格，而不是访问外部事实，微调或少样本提示可能比 RAG 更合适。比如让模型按公司固定语气改写客服回复，检索知识库不是关键。若任务要求执行实时动作，例如退款、订票、改数据库，工具调用比 RAG 更直接，因为系统需要的是状态变更和返回码，不是文档段落。",
                "RAG 也不适合替代权限系统。不能因为用户问到了某个主题，就把所有相似内部文档拿出来让模型自己判断能否展示。权限过滤应发生在检索前或检索时，并作为 metadata filter 进入 retriever。模型可以解释权限不足，但不应该拿到无权资料后再被要求忘记。",
            ]),
            ("评测 RAG 要分层", [
                "只看最终答案分数无法知道问题出在哪里。建议至少分三层评测：第一层看正确证据是否被 retriever 召回，第二层看 context 是否保留足够证据且噪声可控，第三层看模型答案是否忠实引用。某次参数调整让最终答案变好，可能是因为召回更全，也可能只是模型运气更好；分层指标才能指导下一步改动。",
                "日志也要对应分层指标。记录 query、filter、top_k、doc ids、scores、context 字符数、引用编号和核验结果。上线后用户反馈“答案不准”时，团队可以直接定位：是没有查到、查到了没放进 prompt、放进 prompt 但没引用，还是引用了过期文档。这样的证据链比反复改一句 prompt 更可靠。",
            ]),
            ("常见误解与边界情况：RAG 不是万能知识外挂", [
                "常见误解是“只要接了知识库，模型就会自动只说真话”。事实上 RAG 只能把候选证据送到模型面前，不能保证候选一定完整，也不能保证模型一定忠实使用。问题可能出在 query 改写、切块、向量空间、权限过滤、context 排序、prompt 边界或最终核验。把所有问题都归因于模型，会掩盖检索链路里的真实缺陷。",
                "另一个边界是资料冲突。两个 Document 可能来自不同版本、不同租户或不同发布时间，并给出相反结论。格式化 context 时应保留版本和日期，让模型知道哪份资料更新；必要时直接告诉用户资料冲突并列出来源，而不是让模型自行合成一个看似确定的答案。冲突处理是产品策略，不是语言润色。",
            ]),
            ("源码排障清单：从 Runnable 到 Document", [
                "排查 RAG 时先确认 retriever.invoke 的输入是不是预期 query，再确认返回值是否真的是 Document 列表。若返回空列表，查看 search_kwargs、filter、向量库命名空间和 embedding 版本；若返回文档但没有 source，回到 loader 和 splitter；若文档有 source 但答案不引用，检查 prompt 模板和输出格式约束。",
                "Runnable 的好处是每个节点都可以单独 invoke。不要一开始就运行整条链；先单测 rewrite，单测 retriever，单测 format_docs，再把 prompt 渲染出来人工检查。只有每个节点输出可信，整条链的问题才会收敛。LCEL 让组件组合很短，但排障仍要按组件边界拆开。",
            ]),
            ("引用格式设计：让用户和工程都能读", [
                "面向用户的引用应简短，例如 [政策手册 §3.2] 或 [source#chunk]；面向工程的引用应包含 doc_id、chunk_id、score、version 和检索时间。两者可以从同一 metadata 生成，只是展示层不同。不要把工程 id 直接扔给普通用户，也不要为了界面简洁而丢掉工程 id。",
                "引用还应覆盖“不引用”的情况。若答案是基于系统规则、工具观察或用户本轮输入，而不是检索资料，引用格式应能区分。否则所有回答都强行挂知识库来源，用户会误以为资料支持了模型的推理。证据类型越清楚，RAG 越容易被信任。",
            ]),
            ("Agent 中的 RAG 工具", [
                "当 retriever 被包装成工具交给 Agent，检索不再每轮必做，而变成模型可选择的动作。此时工具描述要清楚说明适用范围：查内部政策、查产品文档、查历史工单，还是查公开网页。描述太宽，模型会频繁检索增加成本；描述太窄，模型可能在需要证据时直接回答。",
                "Agent RAG 还要记录“为什么查”。固定链只需说明每次都会检索；Agent 需要知道模型为什么决定调用 retriever，使用了什么 query，是否把结果用于最终回答。若模型查了资料却忽略结果，可能是工具返回格式不适合模型阅读；若模型不查资料就答，可能是系统提示没有明确证据要求。",
            ]),
            ("RAG 与微调的配合", [
                "微调适合改变稳定行为，例如输出风格、领域术语格式、工具调用习惯；RAG 适合注入变化快、私有或需要引用的事实。二者不是互斥：可以用微调让模型更会遵守引用格式和拒答策略，同时用 RAG 提供最新资料。把事实硬塞进微调会导致更新慢，把行为全交给 RAG 又会让提示很重。",
                "选择时问三个问题：知识是否频繁变化，是否需要逐条引用，是否受权限控制。三个答案越偏是，越应优先 RAG；如果知识稳定且更多是表达习惯，微调或模板更合适。这个判断也应写进架构文档，避免团队在每个需求里重复争论。",
            ]),
            ("上线观测：不要只看满意度", [
                "RAG 上线后至少监控无结果率、低分结果率、引用缺失率、引用冲突率、平均 context token、检索延迟和拒答率。用户满意度下降时，这些结构指标能告诉你是资料没覆盖、检索太慢、还是模型引用不稳定。没有结构指标，团队只会看到“回答不好”这一团雾。",
                "还要抽样保存失败案例，但要注意脱敏和权限。失败样例应包含 query、候选 doc id、最终 context、答案和用户反馈，不应随意保存完整私密文档。评测集来自真实失败，真实失败又受隐私约束；这正是 RAG 工程需要治理而不只是写链的原因。",
            ]),
            ("端到端测试：不要只断最终文本", [
                "RAG 测试最好把链路拆成结构断言。给定一个问题，先断言 rewrite 输出是否保留关键实体；再断言 retriever 至少召回某个 doc_id；再断言 context 含 source 和 chunk_id；最后才断言答案包含引用。这样模型措辞变化不会让测试脆弱，但证据链断裂会被及时发现。",
                "还要测试负例。准备一个知识库没有覆盖的问题，期望系统拒答或要求澄清；准备一个带提示注入的文档，期望系统把它当资料而不是指令；准备两个版本冲突的文档，期望系统指出冲突或选择最新版本。负例能证明 RAG 边界真的被执行。",
            ]),
            ("上下文窗口的预算分配", [
                "RAG context 不是越长越安全。系统提示、开发者规则、用户问题、聊天历史、工具观察、检索资料和输出空间都争夺同一个窗口。若检索资料占满窗口，模型可能丢掉用户本轮限定；若历史占太多，正确资料进不来。预算应按任务显式分配。",
                "一种实用策略是先给系统规则和用户问题保底，再给最近历史和检索 context 设置上限。超过上限时，优先保留高分且来源多样的资料，而不是保留同一文档的重复块。预算分配也应写进 trace，让调参时能看到谁挤掉了谁。",
            ]),
            ("权限过滤的确定性", [
                "权限过滤必须发生在 retriever 或 vector store 查询阶段，而不是最终回答阶段。模型不应该先看到无权文档再被要求不要泄漏，因为 prompt 注入、摘要或日志都可能让内容外溢。tenant、role、document_acl 等字段应作为 filter 进入检索调用，并在 trace 中记录。",
                "权限和相关性有时冲突：最相似的文档可能无权访问，第二相似的文档才可用。系统应先过滤权限再排序，或在向量库支持的情况下把 filter 下推。若先全局排序再过滤，top-k 名额可能被无权文档占掉，导致可用结果不足。",
            ]),
            ("从 RAG 到可运营知识库", [
                "课程里的 RAG 链只是运行时一半，另一半是知识库运营。资料谁负责更新，多久同步一次，删除如何生效，错误引用谁修，评测集如何扩充，这些流程决定系统能否长期可信。没有运营流程，第一次 demo 准确不代表一个月后仍准确。",
                "建议把每次用户反馈映射到知识库动作：缺资料就补 source，资料过期就更新版本，召回错就调切块或 metadata，回答乱编就加强核验。RAG 的迭代对象不只是 prompt，而是资料、索引、检索和生成共同组成的闭环。",
            ]),
        ],
        "pitfalls": [
            ("RAG 会自动保证答案正确", "RAG 只提供证据通道；仍需召回评测、prompt 约束和引用核验。"),
            ("Retriever 只能在固定链里用", "BaseRetriever 是 Runnable，也能转换成工具供 Agent 自主调用。"),
            ("context 越多越好", "过多上下文会增加噪声、成本和注入风险，应按质量与证据覆盖调参。"),
            ("引用只是 UI 装饰", "引用是事实核验入口，应能回指本轮 Document 的 source 与 chunk。"),
        ],
        "lab_title": "手工追踪一条 RAG 证据链",
        "lab_steps": [
            "选一个问题，写下原问题和可选改写后的检索 query。",
            "列出 3 个模拟 Document：每个包含 page_content、source、chunk_id、score。",
            "把 Document 格式化成 context，给每段编号，保留来源。",
            "写一个只允许使用 context 的 prompt，并生成带引用的短答案。",
            "检查答案里的每个事实能否在编号文档中找到，不能找到的句子必须删除或标成不确定。",
        ],
        "version_note": "当前 LangChain 中 BaseRetriever 位于 langchain_core.retrievers，并继承 RunnableSerializable；这就是 retriever 可以进入 LCEL 的原因。旧教程可能把 RAG 只讲成 chain 类型，本课按 Runnable 时代的组合方式理解。",
        "points": [
            "RAG 的本质是运行时取证，不是重新训练模型。",
            "Retriever 输入 query、输出 Document，是可组合 Runnable。",
            "Document 的 metadata 是引用、权限和排障的关键，不是附属字段。",
            "Prompt 必须区分系统规则、用户问题和检索资料，防止资料覆盖指令。",
            "生产 RAG 要有引用核验和证据不足时的降级策略。",
        ],
    }
)


LESSON_33_DOCUMENTS_SPLITTERS = _build_lesson(
    {
        "name": "Document、Loader 与 Splitter",
        "core": "文档摄取阶段把网页、PDF、Markdown、数据库记录等原始材料统一变成 Document，再按语义和 token 预算切成可检索 chunk",
        "contract": "Document、BaseLoader、TextSplitter 与 RecursiveCharacterTextSplitter",
        "artifact": "带 page_content 和 metadata 的 chunk Document",
        "risk": "切块后丢失 source、页码、标题层级或权限 metadata，导致回答无法引用或越权",
        "tuning": "chunk_size、chunk_overlap、separator 优先级、metadata 复制和 source_id 策略",
        "evidence": "source、page、section、chunk_index、parent_id、loader 名称和文档版本",
        "boundary": "loader 负责读取与初始 metadata，splitter 负责切分，不应在切分器里偷偷做业务清洗或权限判断",
        "debug": "原始页面是否正确加载、Document 是否有 metadata、chunk 是否重叠合理、子块是否继承父文档来源",
        "lead": "RAG 的质量从 ingestion 开始。Document 是 LangChain 里承载文本和 metadata 的统一容器；Loader 把外部来源读成 Document；TextSplitter 把长文档切成适合嵌入和检索的 chunk；chunk_overlap 用少量重复保护跨段语义。本课追踪 raw page → Document → chunks → metadata propagation，重点理解为什么“切块策略”和“metadata 传播”决定后续检索能不能引用、能不能过滤、能不能排错。",
        "analogy": "把文档处理想成给一本厚书做资料卡。Loader 像馆员，负责把书拿进系统并贴上书名、版本、页码；Splitter 像做卡片的人，把章节裁成可检索小卡，同时在每张卡背后抄上书名和页码。卡片太大，查到后要读很多无关内容；卡片太小，定义和例子分家；卡片没有页码，就算答案正确也无法引用。",
        "map_title": "本课地图：从原始资料到可检索 chunk",
        "map_nodes": [
            ("Raw source", "网页、文件、数据库行或 API 响应仍是外部格式", "before"),
            ("BaseLoader", "读取原始内容，构造初始 Document 与 metadata", "now"),
            ("Document", "page_content 存文本，metadata 存来源、权限、版本和结构", "now"),
            ("TextSplitter", "按长度、分隔符和 overlap 生成子 Document", "source"),
            ("Chunks", "每个 chunk 继承并补充 metadata，进入 embedding/indexing", "after"),
        ],
        "source_intro": "计划里的 community BaseLoader 路径已过期；当前核心抽象在 langchain_core.document_loaders.base。text-splitters 是独立包，源码仍在 monorepo 的 libs/text-splitters 下。",
        "sources": [
            {"file": "libs/core/langchain_core/documents/base.py", "symbol": "Document", "role": "统一文本和 metadata 的数据容器", "direction": "loader 创建，splitter 复制/拆分，retriever 返回"},
            {"file": "libs/core/langchain_core/document_loaders/base.py", "symbol": "BaseLoader", "role": "定义 load/lazy_load/alazy_load 等加载契约", "direction": "外部资料进入 LangChain 的入口"},
            {"file": "libs/text-splitters/langchain_text_splitters/base.py", "symbol": "TextSplitter", "role": "定义按长度和 overlap 创建子 Document 的基础逻辑", "direction": "Document 进入索引前的切分阶段"},
            {"file": "libs/text-splitters/langchain_text_splitters/character.py", "symbol": "RecursiveCharacterTextSplitter", "role": "按分隔符优先级递归切分，尽量保留段落/句子边界", "direction": "常用默认 splitter，可按语言和文本结构调节"},
            {"file": "libs/text-splitters/langchain_text_splitters/base.py", "symbol": "TextSplitter.split_documents", "role": "把父 Document 拆成子 Document，并传播 metadata", "direction": "切分阶段输出可索引 chunks"},
        ],
        "flow_title": "状态流：raw page 到 chunks",
        "flow_kind": "state_flow",
        "flow_steps": [
            ("读取原始页面", "Loader 从 URL 或文件读取标题、正文、页码和更新时间。", "raw"),
            ("构造 Document", "把正文放入 page_content，把 source、title、page、version 放入 metadata。", "Document"),
            ("选择 splitter", "根据文本类型设置 chunk_size、chunk_overlap 和 separators。", "splitter"),
            ("生成 chunks", "每个 chunk 是新的 Document，文本变短，metadata 复制并补充 chunk_index。", "chunks"),
            ("交给索引", "chunks 进入 embedding 和 vector store；source 字段继续服务引用和过滤。", "index"),
        ],
        "trace": [
            {"step": "1. raw page", "input": "HTML 页面含标题、正文、导航和更新时间", "action": "Loader 清理正文并记录 URL", "output": "Document(page_content, metadata={'source':url})"},
            {"step": "2. metadata", "input": "Document + loader metadata", "action": "补充 title、section、version、tenant", "output": "可过滤、可引用的父 Document"},
            {"step": "3. split", "input": "长 page_content", "action": "RecursiveCharacterTextSplitter 按段落/句子/字符递归切分", "output": "多个 chunk Document"},
            {"step": "4. overlap", "input": "相邻 chunk", "action": "保留少量重叠，避免定义和例子被硬切开", "output": "chunk_i 与 chunk_i+1 共享边界文本"},
            {"step": "5. propagate", "input": "父 metadata", "action": "复制 source/page/权限，并加入 chunk_index", "output": "可进入索引的 chunks"},
        ],
        "code_path": "libs/text-splitters/langchain_text_splitters/base.py",
        "code_symbol": "TextSplitter.split_documents",
        "code": """docs = loader.load()
chunks = splitter.split_documents(docs)

# 每个子块仍是 Document
for i, chunk in enumerate(chunks):
    assert chunk.page_content
    assert chunk.metadata["source"] == docs[0].metadata["source"]
    chunk.metadata["chunk_index"] = i
""",
        "code_note": "教学版强调 metadata 传播：splitter 不只是返回字符串列表，而是返回新的 Document 列表。每个子 Document 的 source、page、权限和版本必须继续存在，否则后续检索无法引用或过滤。",
        "sections": [
            ("Document 是摄取阶段的事实边界", [
                "Document 的 page_content 只回答“这段文本是什么”，metadata 才回答“它来自哪里、属于谁、何时有效、能否展示”。很多 RAG 质量问题不是 embedding 不好，而是 Document 一开始就缺少 source、title、page、section、tenant、version 等字段。后续无论向量库多强，都无法凭空恢复这些治理信息。",
                "Loader 的责任是把外部格式转成这个统一边界。PDF、网页、Markdown、数据库行的原始结构不同，但进入链路后都应成为 Document。BaseLoader 的 load/lazy_load 让大文件或批量来源可以逐步产出文档；懒加载特别适合长列表和流式摄取，避免一次性把所有资料读进内存。",
            ]),
            ("切块不是字符数学，而是语义工程", [
                "chunk_size 决定检索粒度，separator 决定优先保留哪些自然边界。RecursiveCharacterTextSplitter 会按分隔符优先级递归尝试，通常先保段落，再保句子，最后才退到字符级。对代码文档，函数和类边界比普通段落更重要；对表格文档，行列标题必须和数值留在同一个块里。",
                "chunk_overlap 解决的是边界附近语义断裂，而不是为了提高命中率无限复制。定义在上一段、例子在下一段时，少量 overlap 能让任意一个 chunk 都有足够上下文。若 overlap 过大，同一事实会重复进入索引，top-k 里可能出现一堆近似块，挤掉真正互补的资料。",
            ]),
            ("metadata propagation 是引用能力的根", [
                "split_documents 应返回子 Document，而不是裸字符串，因为每个子块都要继承父文档的治理字段。常见做法是复制父 metadata，再补充 chunk_index、chunk_start、parent_id 或 content_hash。这样最终引用可以指向“某文档第几页第几个块”，也能在源文档更新时定位哪些 chunk 需要重建。",
                "权限字段同样必须传播。若父文档属于 tenant A，但切块后丢掉 tenant，向量检索时就无法用 metadata filter 限制访问。不要指望 prompt 让模型“不要泄漏”；模型不应该拿到无权内容。权限和版本过滤属于检索前或检索时的确定性逻辑，metadata 是这条逻辑的载体。",
            ]),
            ("Loader 清洗要有边界", [
                "网页 loader 常需要去掉导航、页脚、广告和脚本；PDF loader 可能要处理页眉、断行、页码；Markdown loader 可能要保留标题层级。清洗的目标是让 page_content 更接近人类正文，但不应在 loader 中偷偷做业务摘要或改写事实。摘要属于后续转换，原始可引用文本应尽量保留。",
                "同一来源多次加载时，要有稳定 source_id 或 checksum。否则文档更新会被当成新文档追加，旧 chunk 继续被检索命中。摄取阶段最好记录 loader 名称、加载时间、原始 URI、内容哈希和解析版本。解析器升级后，如果 chunk 边界变化，也能知道哪些索引记录来自旧解析逻辑。",
            ]),
            ("父子结构能兼顾召回和阅读", [
                "有些系统会使用 parent-child retrieval：小 chunk 用来做 embedding 和相似度召回，大 parent 文档或段落用来提供给模型阅读。这样既保留细粒度召回，又避免模型只看到碎片。实现这个策略时，子 chunk metadata 必须有 parent_id，检索后再根据 parent_id 取回较完整上下文。",
                "父子结构也适合长表格、FAQ 和代码说明。问题可能只命中一行术语，但回答需要相邻说明、参数表或异常说明。若只返回命中的短句，模型容易误读；若整篇文档都返回，token 成本又过高。父子索引把“如何找”和“给模型读什么”拆开，是切块设计的高级取舍。",
            ]),
            ("调试切块要看样例，不只看平均长度", [
                "统计平均 chunk 长度只能发现极端异常，不能说明语义是否完整。更可靠的方法是抽样展示原文、chunk 边界、metadata 和 overlap。看每个 chunk 是否有标题语境，是否把否定条件切掉，是否把代码块或表格切坏，是否保留引用字段。",
                "还要准备反例样本：很短的公告、很长的 API 文档、嵌套列表、中文无空格段落、包含表格的页面、带权限的内部文档。每次调整 splitter 都重新检查这些样本。切块是离线阶段的小改动，但会改变所有后续检索结果，因此必须像模型参数一样被评测和版本化。",
            ]),
            ("常见误解与边界情况：切块不是越细越好", [
                "常见误解是把 chunk_size 调小就一定更精准。过小的 chunk 会失去标题、限定条件和上下文，检索命中后模型只看到一句碎片，容易把局部事实当成完整规则。过大的 chunk 又会带来噪声和 token 成本。真正的目标不是长度数字漂亮，而是每个 chunk 能独立说明一个可回答事实，并能回到原文。",
                "边界情况包括表格、代码块和项目符号列表。表格如果按普通段落切，列名和数值可能分离；代码块如果按字符硬切，函数签名和异常说明可能断开；列表如果每项太短，模型看不到总标题。不同文档类型应有不同 splitter 配置，不能全站共用一个默认字符切分器。",
            ]),
            ("源码排障清单：loader 到 splitter", [
                "如果检索命中内容但引用丢失，先打印 loader.load() 的第一个 Document，确认 metadata 是否已经有 source、page 和 title。如果 loader 阶段就没有，splitter 不可能变出来；如果 loader 有但 chunk 没有，检查 split_documents 是否复制 metadata，是否被后续清洗函数覆盖。",
                "如果 chunk 文本出现乱码、重复导航或页脚，问题通常在 loader 或正文抽取，而不是 splitter。先修清洗，再谈切块。若 chunk 边界总是把定义和例子切开，才调整 separators、chunk_size 和 overlap。按阶段定位可以避免把所有摄取问题都归咎于切分器。",
            ]),
            ("metadata schema 要提前定", [
                "metadata 不应随每个 loader 自由发挥。建议统一 source_id、uri、title、section_path、page、chunk_index、version、tenant、acl、content_hash、created_at、updated_at 等字段。字段名稳定，向量库 filter、引用组件和排障脚本才能复用。字段名混乱时，一个 loader 写 url，另一个写 source，最终引用层会不断写特例。",
                "metadata 也要控制大小。把整篇原文、完整 ACL 列表或大对象塞进 metadata 会增加存储和传输成本。metadata 应保存可过滤、可引用、可追踪的摘要字段；大对象放在外部存储，用 id 关联。这个边界能让 chunk 轻量，同时保留回源能力。",
            ]),
            ("语义边界与语言差异", [
                "中文文本没有天然空格，英文文档常用段落和句号，代码文档有缩进和符号，Markdown 有标题层级。RecursiveCharacterTextSplitter 的 separator 列表应反映这些差异。例如中文可加入。！？和换行，Markdown 要保留 # 标题，代码要尽量按函数或类边界切。",
                "多语言知识库还要考虑同一文档的不同语言版本。metadata 应记录 language，retriever 可按用户语言过滤或优先同语言。若把中英文 chunk 混在同一候选池，embedding 可能召回跨语言相似内容，但最终回答引用的语言和用户预期不一致。语言策略也是摄取设计的一部分。",
            ]),
            ("去重与版本", [
                "网页抓取常会得到重复内容：列表页、打印页、移动页、带参数 URL 都可能包含同一正文。摄取阶段应通过 canonical URL 或 content_hash 去重，否则检索 top-k 会被重复块占满。重复不是无害的，它会让模型误以为某个事实被多个来源支持。",
                "版本字段决定旧资料如何退出。政策更新后，旧版本可能需要保留但不能默认检索；API 文档旧版本可能仍对老客户有效。metadata 中的 version、effective_date 和 deprecated 标记让检索器能按场景选择。没有版本治理，RAG 会在新旧知识之间摇摆。",
            ]),
            ("摄取评测样本", [
                "为 splitter 准备样本时，不要只选干净文章。要包含扫描 PDF、长表格、嵌套标题、FAQ、代码块、短公告、重复页脚和权限文档。每个样本都定义期望 chunk：哪些字段必须保留，哪些边界不能切开，哪些噪声必须删除。",
                "每次改 loader 或 splitter 后，重新生成样本 chunk 并做文本 diff。看平均长度不够，要看具体边界。摄取阶段一旦变化，向量 id、chunk_index 和召回结果都会变化，因此它应进入版本控制和评测流程，而不是脚本角落里的临时参数。",
            ]),
            ("加载失败与部分成功", [
                "真实 loader 经常遇到部分失败：某些网页 403，某些 PDF 页损坏，某些数据库行缺字段。摄取管道应记录每个 source 的状态，而不是整个批次一失败就静默跳过。部分成功时，索引应知道哪些来源更新了，哪些仍保持旧版本，哪些需要重试。",
                "错误信息也应成为运维数据。记录 loader 名称、异常类型、source_id、重试次数和最后成功时间。用户问到缺失资料时，团队可以判断是资料本身没有、权限抓取失败、还是解析失败。没有这些记录，知识库覆盖率只能靠猜。",
            ]),
            ("结构化文档的特殊处理", [
                "表格文档不能简单按字符切。表头、单位、行名和脚注共同决定数值含义，切散后模型可能引用一个数字却不知道它是金额、日期还是百分比。处理表格时可以把每行转成带表头的文本，或按小表整体保留，再用 metadata 记录表名和页码。",
                "代码和 API 文档也需要结构感。函数签名、参数说明、返回值和异常通常应在同一块或父子块中关联。若只按固定长度切，检索可能命中参数名但漏掉类型约束。对这类资料，基于 Markdown 标题、代码 fence 或 AST 的切分往往比纯字符切分更可靠。",
            ]),
            ("Chunk id 与重建稳定性", [
                "chunk_index 简单直观，但原文前面插入一段后，所有后续 index 都会变化，导致旧 id 大量失效。content_hash 稳定但无法表达顺序。生产系统常组合 source_id、版本、局部 hash 和顺序号，在稳定性与可读性之间取舍。这个选择会影响 upsert、引用链接和缓存。",
                "重建索引时要知道哪些 chunk 真变了。若只因解析器升级导致边界变化，应记录 parser_version；若内容没变但 chunk id 变了，要避免把评测误判为知识变化。摄取工程的细节会直接影响向量库成本和引用稳定性。",
            ]),
            ("引用稳定性演练", [
                "发布前可以做一次小型引用稳定性演练：选取几条真实问答，把答案引用的 source_id、page、chunk_id 和原文片段保存下来；随后模拟文档前部插入一段、标题改名、解析器升级，再重新切块和索引。理想结果不是 chunk_index 永远不变，而是系统能把旧引用映射到新位置，或明确标记旧引用已失效。",
                "这个演练能暴露很多隐藏假设。若引用只依赖顺序号，轻微改版就会全线断链；若只依赖 content_hash，格式清洗变化也可能导致误删；若没有 parent_id，用户点引用时只能看到孤立碎片。稳定引用通常需要组合 source_id、版本、父级范围和局部定位，而不是押注单个字段。",
            ]),
            ("人工抽检界面", [
                "好的 splitter 配置需要人工看样例。一个简单抽检界面可以展示原文、chunk 边界、metadata、overlap 和预计 token 数，让编辑者标记“边界错误”“metadata 缺失”“噪声太多”。这些标记再进入评测集，帮助后续自动回归。",
                "抽检不需要覆盖所有文档，但要覆盖不同模板和高价值来源。内部政策、法律条款、计费说明、API 参考比普通博客更值得抽检。RAG 的可信度常由少数关键文档决定，摄取阶段应把人工精力放在这些高风险资料上。",
            ]),
            ("权限文档的摄取约束", [
                "内部知识库往往按部门、项目、客户或数据级别授权。Loader 读取时就应拿到这些权限字段，splitter 必须逐块传播。若权限只存在外部系统而不进入 metadata，检索阶段就无法下推过滤，只能在返回后补救，这会增加泄漏风险。",
                "权限还会随时间变化。某个用户今天能看项目文档，明天离开项目后就不应再检索到。metadata 应保存可验证的权限引用或 ACL 版本，索引同步要能更新这些字段。不要把权限当成一次性摄取信息，它和正文一样需要治理。",
            ]),
            ("Chunk 质量的自动信号", [
                "除了人工抽检，也可以计算自动信号：chunk 是否过短、是否重复、是否包含过多导航词、是否没有标点、metadata 是否缺 source、相邻 chunk overlap 是否异常。信号不能替代人工判断，但能在大规模摄取时快速发现坏批次。",
                "这些信号应在 build 或 ingestion 报告中展示。比如某次 loader 改动后，平均 chunk 数突然翻倍、缺 source 比例上升、重复 hash 增多，就应阻止索引发布。摄取质量门禁越早，后续 RAG 排障越少。",
            ]),
            ("发布前的摄取审查", [
                "知识库发布前应抽查生成后的 chunk，而不是只看原始文件是否存在。审查清单包括：每个高价值来源是否有 chunk，chunk 是否保留标题和来源，页码是否正确，权限字段是否存在，版本是否最新，重复块是否过多。只有这些检查通过，后续 embedding 才值得执行。",
                "如果摄取管道支持增量发布，还应比较新旧 chunk 数量和 source 覆盖率。某个 loader 改动让 chunk 数量突然减少，可能是解析失败；数量突然增加，可能是噪声没有清理。把这些指标写入发布报告，可以在索引污染前发现问题。",
            ]),
            ("从失败样例反推切块", [
                "当某个问题答错时，把命中的 chunk 和理想原文并排看。若理想原文在同一父文档但没有被命中，可能是 chunk 太大或 query 词被噪声稀释；若命中片段缺少限定条件，可能是 chunk 太小或 overlap 不足。失败样例比抽象参数更能说明该怎么改。",
                "每次修切块后，都要重建受影响来源的索引并复跑失败样例。只改 splitter 代码但不重建向量，线上不会变化；只重建部分来源但没有 cleanup，旧坏块可能继续出现。摄取、索引和验证必须一起执行。",
                "如果失败样例来自图片表格或扫描件，还要检查 OCR 质量。OCR 把列名识别错、把页码混进正文、把负号漏掉，都会让 splitter 得到看似正常但事实错误的文本。此时调 chunk_size 没用，应先修解析和质量标记。",
            ]),
        ],
        "pitfalls": [
            ("切块只影响速度", "切块决定召回粒度、上下文噪声和引用能力，是质量核心旋钮。"),
            ("metadata 可有可无", "metadata 承载来源、权限、版本和父子关系，丢失后很难排错。"),
            ("overlap 越大越好", "过大 overlap 会制造重复和成本，应只保护跨边界语义。"),
            ("Loader 应该完成所有清洗", "Loader 负责读取和初始结构；复杂清洗、去重、权限治理应有独立阶段。"),
        ],
        "lab_title": "设计一个不会丢引用的 splitter",
        "lab_steps": [
            "选一段包含标题、定义、列表和例子的长文本，写成一个父 Document。",
            "给父 Document 添加 source、section、page、version、tenant metadata。",
            "手工切成 3 个 chunk，并为每个 chunk 保留父 metadata。",
            "观察相邻 chunk 是否需要 overlap；如果定义和例子分离，调整边界。",
            "写下最终 chunk_index 和 parent_id，说明用户追问引用时如何回到原文。",
        ],
        "version_note": "BaseLoader 当前可在 langchain_core.document_loaders.base 找到；旧的 langchain_community.document_loaders.base 路径在当前 master 中不再存在。TextSplitter 来自独立 langchain-text-splitters 包，源码路径是 libs/text-splitters/langchain_text_splitters。",
        "points": [
            "Document 是文本和 metadata 的统一证据容器。",
            "Loader 负责把外部格式读入 Document，不应吞掉来源字段。",
            "Splitter 返回子 Document，必须传播并补充 metadata。",
            "chunk_size 和 overlap 是召回质量、token 成本和语义完整性的权衡。",
            "丢失 metadata 的 RAG 很难引用、过滤和排障。",
        ],
    }
)


LESSON_34_EMBEDDINGS_VECTORSTORES = _build_lesson(
    {
        "name": "Embeddings 与 VectorStore",
        "core": "Embedding 把文本映射成向量，VectorStore 保存向量与 Document，并用相似度搜索把 query 找回相关 chunk",
        "contract": "Embeddings、VectorStore、VectorStoreRetriever 与 indexing.index",
        "artifact": "embedding vector、向量索引记录、相似度结果 Document",
        "risk": "索引版本过期、重复写入、embedding 模型不一致、upsert 没有稳定 id",
        "tuning": "embedding 模型、距离度量、top_k、score_threshold、upsert key 和 cleanup 策略",
        "evidence": "document id、source_id、embedding model、index timestamp、similarity score 和索引命名空间",
        "boundary": "Embeddings 只负责向量化，VectorStore 负责存取和搜索，业务去重与权限过滤不能只靠相似度",
        "debug": "chunks 是否已嵌入、向量维度是否匹配、add_documents 是否返回 id、similarity_search 是否使用同一 embedding 模型",
        "lead": "Embeddings 与 VectorStore 是 RAG 的检索引擎层。Embedding 模型把 chunk 文本变成数字向量；VectorStore 保存向量、原始 Document 和 metadata；similarity_search 或 VectorStoreRetriever 根据 query 向量找回相似文档；indexing.index 则提供更系统的增量索引、去重和清理语义。本课追踪 chunks → vectors → add_documents → similarity_search → docs，并把 indexing/upsert 的版本问题讲清楚。",
        "analogy": "把向量库想成一座按“意思”而不是按字母排序的仓库。Embedding 模型给每张资料卡一个空间坐标，意思接近的卡片放得近。用户提问时，系统也给问题一个坐标，然后找附近卡片。仓库管理员 VectorStore 不负责判断答案，只负责把卡片、坐标、标签和编号存好，并在查询时按距离交出候选。",
        "map_title": "本课地图：从 chunk 到相似文档",
        "map_nodes": [
            ("Chunks", "splitter 产出的 Document 列表，带 source 和 chunk id", "before"),
            ("Embeddings", "embed_documents / embed_query 把文本映射为同维向量", "now"),
            ("VectorStore", "保存向量、Document、metadata 和外部 id", "now"),
            ("Retriever", "as_retriever 暴露 Runnable 检索接口", "source"),
            ("Docs", "similarity_search 返回候选文档，进入 context 格式化", "after"),
        ],
        "source_intro": "FAISS 的真实实现位于独立 langchain-community 包的 langchain_community.vectorstores.faiss；monorepo 中的 libs/langchain/langchain_classic/vectorstores/faiss.py 是弃用期 re-export shim，不是实现文件。本课因此把 core 的 InMemoryVectorStore 作为 source-verified concrete anchor，用它说明 VectorStore 契约，再提醒生产可替换为专用向量库。",
        "sources": [
            {"file": "libs/core/langchain_core/embeddings/embeddings.py", "symbol": "Embeddings", "role": "定义 embed_documents 和 embed_query 的向量化契约", "direction": "索引阶段和查询阶段都必须使用兼容模型"},
            {"file": "libs/core/langchain_core/vectorstores/base.py", "symbol": "VectorStore", "role": "定义 add_documents、similarity_search、as_retriever 等接口", "direction": "连接索引写入和运行时检索"},
            {"file": "libs/core/langchain_core/vectorstores/base.py", "symbol": "VectorStoreRetriever", "role": "把 VectorStore 包装成 BaseRetriever/Runnable", "direction": "RAG 链运行时调用"},
            {"file": "libs/core/langchain_core/indexing/api.py", "symbol": "index", "role": "提供基于 record manager 的增量索引、去重和 cleanup 流程", "direction": "构建/更新知识库时使用"},
            {"file": "libs/core/langchain_core/vectorstores/in_memory.py", "symbol": "InMemoryVectorStore", "role": "核心包内可验证的具体向量库实现，适合教学和小规模实验", "direction": "实现 VectorStore 契约，可替换为生产向量库"},
        ],
        "flow_title": "调用图：索引写入与相似搜索",
        "flow_kind": "call_graph",
        "flow_steps": [
            ("chunks", "Document 列表携带 chunk 文本和 metadata", False),
            ("embed_documents", "Embedding 模型批量生成向量", True),
            ("add_documents", "VectorStore 保存向量、文本、metadata、id", True),
            ("embed_query", "运行时把用户 query 变成同空间向量", True),
            ("similarity_search", "按距离/相似度返回 top-k Document", True),
            ("context", "候选文档被格式化进 RAG prompt", False),
        ],
        "trace": [
            {"step": "1. chunks", "input": "5 个 chunk Document", "action": "读取 page_content 和 metadata", "output": "待嵌入文本批次"},
            {"step": "2. vectors", "input": "文本批次 + embedding model", "action": "embed_documents 生成同维向量", "output": "vectors shape = n × d"},
            {"step": "3. add", "input": "Document + vector + stable id", "action": "VectorStore 写入索引和 docstore", "output": "返回 ids 或更新已有记录"},
            {"step": "4. query", "input": "用户问题", "action": "embed_query 使用同一 embedding 空间", "output": "query vector"},
            {"step": "5. search", "input": "query vector + k/filter", "action": "similarity_search 找近邻并取回 Document", "output": "top-k docs with metadata"},
        ],
        "code_path": "libs/core/langchain_core/vectorstores/base.py",
        "code_symbol": "VectorStore.as_retriever",
        "code": """vectorstore.add_documents(chunks, ids=[chunk.metadata["chunk_id"] for chunk in chunks])
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

docs = retriever.invoke("如何配置 checkpoint？")
for doc in docs:
    print(doc.metadata["source"], doc.page_content[:80])
""",
        "code_note": "教学版保留两个关键点：写入时使用稳定 id，查询时通过 as_retriever 暴露 Runnable 检索接口。真实系统还要记录 embedding 模型版本、命名空间、权限过滤和 cleanup 策略。",
        "sections": [
            ("Embedding 契约：同一空间才可比较", [
                "Embeddings 的核心约束是文档向量和查询向量必须来自兼容模型、相同维度和相同归一化约定。换模型、换服务版本、换预处理方式，都可能让向量空间改变。旧向量和新查询看似都是数字列表，但距离已经没有业务意义。因此索引记录应保存 embedding_model、dimension、normalize 约定和生成时间。",
                "距离指标也会改变排序。cosine 更关注方向，dot product 可能受向量长度影响，L2 关注欧氏距离；有些向量库会在内部做归一化，有些要求调用方先处理。课程不要求记公式，但要知道 metric 是索引配置的一部分。线上发现相似度异常时，要检查模型、维度、归一化和 metric 是否一致，而不是只调 top_k。",
                "上线后还要把 embedding 版本当成索引版本管理。模型供应商静默升级、清洗规则改变或标题拼接策略调整，都会造成 embedding drift；发现召回突然变差时，不要只调阈值，应先比对固定评测集里新旧 query 的邻居、分数分布和命中版本，再决定全量重嵌入、双索引灰度还是回滚旧 namespace。若 metadata filter 同时变化，要分开记录，否则会把模型漂移误判成过滤过严。",
            ]),
            ("VectorStore 保存的不只是向量", [
                "一个有用的 VectorStore 至少要同时保存四类信息：向量、原始文本、metadata、外部 id。向量用于近邻搜索，文本用于返回给模型，metadata 用于过滤和引用，id 用于更新和删除。若只保存向量，检索命中后还要去别处找正文；若没有 id，同一文档更新时只能追加，无法可靠 upsert。",
                "InMemoryVectorStore 适合教学、测试和小规模临时检索，因为它让契约可见且无需外部服务。生产环境常换成 FAISS、pgvector、Milvus、Pinecone、Elasticsearch hybrid 或云厂商向量检索。只要业务依赖 VectorStore/VectorStoreRetriever 契约，上层 RAG 链不应关心底层索引文件、连接池或分片细节。",
            ]),
            ("indexing.index 解决增量同步问题", [
                "简单 add_documents 适合一次性实验，生产知识库更关心增量：某个 source 更新了，旧 chunk 是否删除；某个 source 消失了，索引是否 cleanup；同一内容重复摄取，是否跳过。langchain_core.indexing.api.index 的设计目标就是把 loader 输出、record manager 和 vector store 写入连接起来，记录哪些文档已经索引过。",
                "理解 index 时要抓住 source_id 和 cleanup。source_id 把多个 chunk 归到同一原始来源；record manager 记录每个 chunk 的写入状态；cleanup 决定全量或增量同步后如何处理旧记录。没有这些信息，向量库会越用越脏，用户问到已经删除或更新的政策时，系统仍可能返回旧 chunk。",
            ]),
            ("Upsert 策略要先于写入设计", [
                "稳定 id 可以来自 source_id + chunk_index，也可以来自内容哈希 + 版本。前者便于覆盖同一位置的更新，后者便于识别内容是否变化。选择哪种取决于业务：政策文档常需要按版本替换，审计场景可能要保留历史版本并在 metadata 中标注有效期。无论哪种，都不应让向量库随机生成唯一 id 后就失去来源关系。",
                "写入失败也要定义行为。若 embedding 批次中途失败，已经写入的部分是否回滚？若向量库写入成功但 record manager 记录失败，下次同步会不会重复写入？这些问题在小 demo 中看不到，但生产索引必须处理。至少要有幂等 id、批次日志和可重跑流程。",
            ]),
            ("过滤、混合检索和重排", [
                "向量相似度只说明语义接近，不说明权限正确、时间有效或类型匹配。metadata filter 应在搜索时限制 tenant、language、doc_type、version 或 effective_date。过滤太晚会浪费候选名额，甚至把无权内容交给后续模型。过滤太严则可能漏召回，所以要用评测集观察每个 filter 的影响。",
                "纯向量检索对数字、代码符号、专有名词和精确短语不总是稳定。很多系统会加入 BM25 或关键词过滤形成 hybrid retrieval，再用 reranker 精排。VectorStoreRetriever 提供的是统一入口，不意味着底层只能做单一向量近邻。课程把这一层放在第 7 部分（RAG 与记忆），是为了让你看到 embeddings 是基础，但不是检索质量的全部。",
            ]),
            ("排查 stale index 的顺序", [
                "当用户看到旧答案，先确认返回 Document 的 metadata：source_id 是谁，version 是不是最新，embedding_model 是否当前，index_time 是否晚于文档更新时间。再检查查询是否命中旧命名空间，是否有缓存，cleanup 是否真的删除旧 ids。很多 stale 问题不是模型幻觉，而是索引里确实还躺着旧块。",
                "如果相似度分数异常低或排序怪异，检查维度和 metric；如果同一来源重复出现，检查 chunk id 和 upsert；如果权限错误，检查 metadata filter 是否进入 retriever；如果新文档完全搜不到，检查 loader 是否产出 Document、embedding 是否成功、add_documents 是否返回 id。按阶段排查，比直接重建全库更节省时间。",
            ]),
            ("常见误解与边界情况：相似不等于正确", [
                "常见误解是把最高相似度当成答案依据。向量相似度只说明 query 和 chunk 在 embedding 空间里接近，不说明 chunk 最新、不说明用户有权访问、不说明足以回答完整问题。一个段落可能和问题语义很像，却来自旧版本或只覆盖部分条件。最终 context 应结合 score、metadata、版本和可回答性判断。",
                "边界情况包括数字、代码符号、产品型号和否定语句。Embedding 对“支持”和“不支持”有时距离很近，对 v1 和 v2 这种短符号也不一定敏感。遇到这类资料，单纯向量检索风险较高，应加入关键词过滤、结构化 metadata filter 或 reranker。",
            ]),
            ("源码排障清单：embedding 到 search", [
                "如果所有查询都返回奇怪结果，先检查文档向量和查询向量维度是否一致、是否使用同一 embedding 模型、是否同一 normalize 设置。若只有某类问题失败，检查这些问题是否包含精确术语、数字或权限条件。不要一开始就怀疑模型回答，先确认向量空间本身可比较。",
                "如果新写入文档搜不到，检查 add_documents 是否被调用、ids 是否唯一、向量库命名空间是否正确、metadata filter 是否过严。若写入后立刻查询仍旧返回旧版本，检查缓存、record manager 和 cleanup。向量库问题通常可以通过列出 ids 和 metadata 直接验证。",
            ]),
            ("距离指标与归一化", [
                "cosine similarity 常用于比较方向，适合很多文本 embedding；dot product 可能受向量长度影响；L2 距离在某些索引实现中更自然。不同 provider 和向量库对 metric 的默认值不同，有的会自动归一化，有的不会。迁移向量库时必须确认 metric，不然相同向量会得到不同排序。",
                "归一化还影响阈值。一个在 cosine 下合理的 score_threshold，换成 dot product 后可能完全失效。阈值不是可随意复制的魔法数字，必须和模型、metric、索引库、语料分布一起评估。上线前应从验证集统计正负样本分数分布，再决定阈值。",
            ]),
            ("indexing.index 的实际价值", [
                "indexing.index 不是为了让 demo 更复杂，而是为了解决“知识库持续变化”这个生产问题。它通过 record manager 记录哪些来源和 chunk 已经写入，帮助跳过未变化内容，并在 cleanup 时删除不再存在的记录。没有这层记录，向量库只知道一堆向量，不知道它们对应的源文档生命周期。",
                "使用 index 时要设计 source_id。一个 PDF 的多个 chunk 共享同一 source_id；网页更新后仍然是同一 source_id 的新版本；复制到另一个租户则可能是不同命名空间。source_id 设计错误会导致 cleanup 删除不该删的内容，或保留应该删除的旧内容。",
            ]),
            ("向量库选择", [
                "InMemoryVectorStore 让学生看清契约，但它不适合多进程持久化和大规模检索。FAISS 适合本地高性能实验，但权限过滤和分布式运维要自己处理；pgvector 适合已有 PostgreSQL 团队，事务和权限集成方便；托管向量库提供扩展和运维能力，但成本、锁定和数据合规要评估。",
                "选择时不要只问“哪个更准”。准确率更多来自 embedding、切块、过滤和 rerank；向量库主要影响规模、延迟、过滤能力、持久化、运维和成本。先定义数据量、更新频率、权限模型和部署环境，再选择实现。VectorStore 契约让早期可以从简单实现开始，后续再替换。",
            ]),
            ("Hybrid retrieval 与 rerank", [
                "很多真实知识库需要混合检索。关键词检索擅长精确符号、编号、错误码和短语；向量检索擅长语义近似和同义表达。混合检索先扩大候选，再用 reranker 合并排序，常比单一路线稳定。课程把向量库作为主线，但不应误解成只能用向量。",
                "混合结果需要统一去重和记录来源。一个 chunk 可能同时被 BM25 和向量检索命中，最终候选应合并分数而不是重复出现。日志里应标记命中通道，方便判断某类问题到底依赖关键词还是向量。这样的信息能指导后续优化索引和查询改写。",
            ]),
            ("批量嵌入的工程细节", [
                "Embedding 服务通常有批量大小、速率限制和超时。批量太小成本高，批量太大容易超时或触发限流。索引管道应把 chunk 分批，记录每批输入数量、失败重试和 provider 响应。若某批失败，不应让整个知识库处于半更新但无记录的状态。",
                "还要处理空文本和极短文本。空 chunk 不应嵌入；只有标题或导航的短 chunk 可能产生噪声向量。摄取阶段可以过滤低质量 chunk，或把短标题和正文合并。向量库里的垃圾数据越少，后续 retriever 和 reranker 越轻松。",
            ]),
            ("命名空间与多租户", [
                "多租户系统不能只靠 metadata 约定，最好在向量库层使用 namespace、collection 或索引分区隔离。metadata filter 是重要防线，但命名空间能降低误配置时的影响范围。不同租户使用不同 embedding 模型或不同数据保留策略时，命名空间也能表达这些差异。",
                "命名空间设计要和 source_id 配合。同一个公共文档可能被多个租户共享，也可能按租户复制并带不同权限。共享能省存储，但权限和删除更复杂；复制更隔离，但更新成本高。VectorStore 抽象不替你做这个决定，架构层必须明确。",
            ]),
            ("分数阈值的校准", [
                "score_threshold 只有经过校准才有意义。不同 embedding 模型、不同 metric、不同语料规模会产生不同分数分布。一个项目里 0.78 可能很高，另一个项目里只是普通相似。用少量人工标注的正负样本统计分数区间，比照搬教程阈值可靠。",
                "阈值还会影响拒答率。阈值过高，系统经常说没资料；阈值过低，噪声进入 prompt。可以按文档类型设置阈值，也可以把低分结果标记为“低置信”交给后续 reranker 或模型核验。关键是让阈值变化有评测记录。",
            ]),
            ("索引回滚与迁移", [
                "换 embedding 模型或向量库时，不要在原索引上直接覆盖。更安全的做法是建立新 namespace，双写或离线重建，然后用评测集比较新旧召回，再切流量。若新模型表现变差，可以快速回滚到旧 namespace。",
                "迁移还要考虑引用稳定性。用户收藏的引用链接、评测集里的 doc_id、缓存里的 chunk_id 是否仍有效？如果 chunk 边界变化，旧引用可能需要映射到新 chunk。索引迁移不只是数据复制，也影响用户可见证据。",
            ]),
            ("向量维度与存储成本", [
                "向量维度越高，单条记录占用越多，索引构建和搜索成本也可能增加。更高维不自动意味着更准，模型训练数据、任务匹配度和检索策略同样重要。选择 embedding 模型时要同时看质量、维度、价格、吞吐、语言覆盖和数据合规。",
                "成本还来自重复 chunk 和多版本索引。若摄取阶段没有去重，向量库存储会被重复页面放大；若迁移模型时长期双写，也要计划旧索引下线。VectorStore 运维不是只加机器，还包括数据生命周期管理。",
            ]),
            ("相似度结果的解释", [
                "向量库返回的 score 要解释给工程团队，而不一定直接展示给用户。用户需要看到来源和关键片段，工程需要看到分数、metric、rank 和 filter。若把原始分数直接展示为“可信度”，可能误导用户，因为相似度不等于事实可信度。",
                "更好的解释是组合信号：来源是否权威、版本是否最新、是否多来源支持、reranker 是否高分、引用核验是否通过。Embedding score 是候选排序信号之一，不应被包装成最终答案置信度。",
            ]),
            ("删除与合规", [
                "向量库删除必须能从业务对象追溯到所有 chunk id。用户要求删除某份文档或某个租户数据时，系统不能只删除原始文件，还要删除向量、docstore 文本、record manager 记录和相关缓存。若没有 source_id 到 chunk ids 的映射，删除会变成全库扫描。",
                "合规场景还要证明删除已经发生。记录删除请求、匹配的 ids、执行时间、失败重试和验证查询结果。VectorStore 抽象提供接口，但删除策略和审计属于应用责任。没有删除闭环，RAG 知识库会积累无法治理的历史数据。",
            ]),
            ("查询向量也要观察", [
                "很多排障只看文档索引，却忘了 query embedding。用户问题如果被改写得过长、夹带无关历史或混入多个意图，query vector 会偏离目标。记录原问题、改写 query 和相似结果，可以判断问题在查询侧还是文档侧。",
                "对于多意图问题，可以拆成多个 query 分别检索，再合并候选。一个向量同时代表两个问题时，可能两个方向都不够近。拆 query 增加成本，但能显著改善复杂问答的召回覆盖。",
                "查询侧还要避免把历史摘要无脑拼进去。摘要能补充指代，但过长摘要会把 query vector 拉向旧话题。更稳妥的做法是先用对话上下文生成独立查询，再只把独立查询送入 embed_query，并把两者都清晰记录到 trace。",
            ]),
        ],
        "pitfalls": [
            ("换 embedding 模型不用重建索引", "向量空间变了，旧向量不可比较，通常需要重嵌入。"),
            ("add_documents 永远只是追加", "生产索引要考虑 upsert、去重、删除过期和 source_id 稳定性。"),
            ("相似度最高就一定正确", "相似不等于可回答；仍需 metadata、rerank、引用核验和拒答策略。"),
            ("VectorStore 负责所有权限", "权限字段可用于过滤，但策略和租户边界应由业务层明确传入。"),
        ],
        "lab_title": "排查一个 stale index",
        "lab_steps": [
            "列出一个文档的 source_id、chunk_id、version 和 embedding_model。",
            "模拟第一次 add_documents，记录返回 id 和索引时间。",
            "修改原文后再次索引，决定是 upsert 同 id、写新版本还是删除旧版本。",
            "执行一次 similarity_search，检查返回结果是否来自最新 version。",
            "写下如果旧结果仍出现，你会检查 record manager、cleanup、命名空间还是缓存。",
        ],
        "version_note": "当前 core 包提供 langchain_core.vectorstores.in_memory.InMemoryVectorStore；FAISS 的真实实现位于独立 langchain-community 包 langchain_community.vectorstores.faiss。monorepo 中 libs/langchain/langchain_classic/vectorstores/faiss.py 只是 deprecation re-export shim，不是实现文件。课程用 core InMemoryVectorStore 作可验证主锚点。",
        "points": [
            "Embeddings 必须保证文档和查询进入同一向量空间。",
            "VectorStore 保存向量、文档和 metadata，不只是一个距离计算器。",
            "VectorStoreRetriever 把向量库包装成 Runnable 检索器。",
            "稳定 id、source_id 和版本是 upsert/cleanup 的基础。",
            "相似度搜索需要配合过滤、rerank、引用核验和评测。",
        ],
    }
)


LESSON_35_RETRIEVERS_RERANKERS = _build_lesson(
    {
        "name": "Retriever、压缩与 Rerank",
        "core": "Retriever 先扩大召回，压缩器或 reranker 再缩小上下文，把更少但更相关的材料交给模型",
        "contract": "BaseRetriever、VectorStoreRetriever、ContextualCompressionRetriever 与 BaseDocumentCompressor",
        "artifact": "候选 Document、压缩后 Document、rerank 分数和最终 top-k context",
        "risk": "过早过滤导致漏召回，过晚过滤导致噪声和成本，压缩后丢引用 metadata",
        "tuning": "base top_k、metadata filter、compressor 策略、rerank_k、score threshold 和多路召回权重",
        "evidence": "原始排名、压缩前后文本、rerank score、保留下来的 source 和过滤原因",
        "boundary": "Retriever 负责找候选，Compressor/Reranker 负责重排或裁剪，不应让模型在无证据时补事实",
        "debug": "base retriever 是否召回正确文档、search_kwargs 是否生效、compressor 是否保留关键句、reranker 是否改变排序",
        "lead": "检索不是一次 top-k 就结束。高召回 retriever 可以先取更多候选，ContextualCompressionRetriever 用 compressor 或 reranker 按当前 query 压缩、过滤、重排，再把更小的 top-k context 交给模型。这样能在召回率和精确率之间做分层取舍：第一层宁可多拿，第二层再去噪。本课追踪 query → broad retriever → compressor/reranker → top-k context，并说明 search_kwargs、contextual compression、recall/precision 如何一起调。",
        "analogy": "把检索想成招聘。第一轮简历筛选要高召回，宁可多放进一些可能合适的人；第二轮面试官或测评系统再精排，找出最匹配岗位的几位。如果第一轮太严格，真正合适的人进不了池子；如果第二轮没有精排，面试官会被一堆弱相关简历淹没。Retriever 是初筛，reranker 是复核，context 是最终给决策者看的短名单。",
        "map_title": "本课地图：先召回，再压缩，再精排",
        "map_nodes": [
            ("Query", "用户问题或改写后的检索语句", "before"),
            ("Broad retriever", "用较大 k 和过滤条件扩大候选池", "now"),
            ("Compressor", "按 query 删除无关句、截短或过滤 Document", "now"),
            ("Reranker", "用交叉编码器或模型重排候选，优化精确率", "source"),
            ("Top-k context", "只把最有用且可引用的材料交给 prompt", "after"),
        ],
        "source_intro": "当前 contextual compression 位于 langchain_classic retrievers；BaseDocumentCompressor 的核心抽象在 langchain_core.documents.compressor，classic compressor pipeline 会导入这个核心抽象。计划中的 langchain.retrievers 路径已过期。",
        "sources": [
            {"file": "libs/core/langchain_core/retrievers.py", "symbol": "BaseRetriever", "role": "检索器基础契约，输入 query 输出 Document 列表", "direction": "候选召回入口"},
            {"file": "libs/core/langchain_core/vectorstores/base.py", "symbol": "VectorStoreRetriever", "role": "向量库检索器，支持 search_kwargs 控制 k、filter、search_type", "direction": "常见 broad retriever 实现"},
            {"file": "libs/langchain/langchain_classic/retrievers/contextual_compression.py", "symbol": "ContextualCompressionRetriever", "role": "包装 base_retriever 和 base_compressor，对候选做上下文压缩", "direction": "base retriever 之后、prompt 之前"},
            {"file": "libs/core/langchain_core/documents/compressor.py", "symbol": "BaseDocumentCompressor", "role": "定义 compress_documents 的压缩/过滤契约", "direction": "reranker、extractor、filter 等后处理组件的抽象"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable", "role": "让 retriever 及其包装器能进入 LCEL 与配置系统", "direction": "组合、回调和 trace 的统一协议"},
        ],
        "flow_title": "调用图：从宽召回到窄上下文",
        "flow_kind": "call_graph",
        "flow_steps": [
            ("query", "问题进入检索层", False),
            ("base retriever", "k=20 扩大召回，带权限 filter", True),
            ("compressor", "按 query 提取相关句或过滤无关块", True),
            ("reranker", "重新计算相关性并排序", True),
            ("top-k", "保留 4 段可引用上下文", True),
            ("prompt", "模型只阅读短名单", False),
        ],
        "trace": [
            {"step": "1. query", "input": "用户问：如何减少 RAG 幻觉？", "action": "生成检索 query，保留租户过滤", "output": "query + filter"},
            {"step": "2. broad", "input": "k=20", "action": "VectorStoreRetriever 找到候选块", "output": "20 个 Document，召回较全但有噪声"},
            {"step": "3. compress", "input": "20 docs + query", "action": "BaseDocumentCompressor 删除无关句或整块", "output": "10 个更短 Document"},
            {"step": "4. rerank", "input": "压缩后 docs", "action": "reranker 重新打分排序", "output": "按相关性和可回答性排序"},
            {"step": "5. context", "input": "top 4", "action": "格式化 context，保留 source 和 score", "output": "给模型的短名单"},
        ],
        "code_path": "libs/langchain/langchain_classic/retrievers/contextual_compression.py",
        "code_symbol": "ContextualCompressionRetriever",
        "code": """base = vectorstore.as_retriever(search_kwargs={"k": 20, "filter": {"tenant": tenant}})
retriever = ContextualCompressionRetriever(
    base_retriever=base,
    base_compressor=reranker_or_extractor,
)

docs = retriever.invoke("如何减少 RAG 幻觉？")
context = format_docs(docs[:4])
""",
        "code_note": "教学版把第一层召回和第二层压缩分开。base retriever 追求不漏，compressor/reranker 追求少而准；二者都必须保留 Document metadata，避免最终引用断链。",
        "sections": [
            ("Recall 与 precision 要分开优化", [
                "第一层 retriever 的任务是让正确证据有机会进入候选池，所以它通常偏向 recall。k 设得太小、filter 太严、query 改写偏题，都会让正确文档在第一步消失。第二层 compressor 或 reranker 才偏向 precision，把弱相关、重复或过长的内容压下去。把两层目标混在一起，会导致参数调优互相打架。",
                "评测时也要分开看。候选池 recall 衡量黄金证据是否在 top-20；rerank precision 衡量黄金证据是否进 top-4；最终答案忠实度衡量模型有没有引用这些证据。若 top-20 没有正确块，应该改 query、切块、embedding 或 filter；若 top-20 有但 top-4 没有，才重点看 reranker 和压缩器。",
            ]),
            ("检索评测切片", [
                "不要只维护一个总分。把评测集按问题类型切片：定义型、步骤型、比较型、故障排查、权限受限和资料缺失。每个切片分别看候选池召回、rerank 后 top-k 和最终引用完整性。这样某次改动若让平均分上升，但权限受限问题开始漏过滤，也能被及时发现。",
                "切片还帮助选择 search profile。定义型问题可能小 k 加高阈值就足够；比较型问题需要多来源和 MMR；故障排查问题要混合代码符号、错误日志和文档。评测报告应显示每个 profile 的失败样例，而不只是一个漂亮平均数。",
            ]),
            ("search_kwargs 是检索器的控制面", [
                "VectorStoreRetriever 的 search_kwargs 不是随手传的字典，而是运行时检索策略的控制面。常见字段包括 k、filter、score_threshold、fetch_k、lambda_mult 或 search_type。不同向量库支持的字段不同，因此业务代码最好把这些参数集中配置，并在 trace 中记录本次实际使用的值。",
                "MMR 是常见 search_type，用最大边际相关性在相关性和多样性之间取平衡。它适合问题可能需要多个方面证据的场景，避免 top-k 全是同一段的近重复。相反，如果用户只问一个精确定义，普通 similarity search 加较小 k 可能更合适。检索策略要匹配问题类型，而不是全站一个默认值。",
            ]),
            ("ContextualCompressionRetriever 的组合方式", [
                "ContextualCompressionRetriever 把 base_retriever 和 base_compressor 接起来：先 retrieve_documents，再 compress_documents。这个顺序说明 compressor 不是替代检索器，而是后处理候选。BaseDocumentCompressor 的契约接收 documents、query 和 callbacks，返回新的 Document 序列；返回值仍应保留 metadata。",
                "compressor 可以是抽取器、过滤器、重排器或 pipeline。抽取器按 query 从长块中摘出相关句；过滤器删除低相关块；reranker 重新打分排序；DocumentCompressorPipeline 可以把多个步骤串起来。不同组件的失败模式不同：抽取器可能删掉引用上下文，过滤器可能过度保守，reranker 可能偏向措辞相似而不是事实可回答。",
            ]),
            ("Reranker 的几种形态", [
                "交叉编码器 reranker 会同时读取 query 和候选文本，通常比向量相似度更精确，但延迟和成本更高。LLM judge reranker 可以根据复杂指令判断“是否能回答问题”，但输出更不稳定，需要结构化分数和超时策略。轻量 embedding filter 速度快，适合先做粗过滤。选择哪种 reranker，要看候选数量、延迟预算和错误成本。",
                "Rerank 后不要只保留文本。原始 rank、原始 score、新 score、过滤原因和 source 都应进入日志。这样才能解释为什么某个文档从第 12 名升到第 2 名，或为什么某个含关键词的块被删掉。没有这些字段，reranker 会变成另一个黑盒，排障时只能猜它“觉得不相关”。",
            ]),
            ("压缩不能破坏引用", [
                "很多 compressor 会返回更短的 Document.page_content。缩短文本没问题，但 metadata 必须保留，最好再补充 compression_method、original_chunk_id 和 span 信息。否则最终答案引用的是压缩后的临时片段，却无法回到原文。对合规场景，压缩内容还要能证明没有改变原意。",
                "如果压缩器使用 LLM 抽取句子，要警惕它把多个来源改写成新句子。抽取应尽量保留原文片段；若做摘要式压缩，就要标明这是生成摘要，不应当作逐字引用。最终 prompt 可以同时给摘要和 source，但引用核验需要知道摘要背后的原始 Document。",
            ]),
            ("调参顺序：先候选，后精排", [
                "遇到回答漏条件，先看 broad retriever 的候选列表。正确证据不在候选里，就扩大 k、调整 query rewrite、检查 chunk、放宽 filter 或加入关键词检索。正确证据在候选但排名低，再看 reranker；正确证据在 top-k 但模型没用，再看 context 格式和 prompt。这个顺序能避免把所有问题都甩给 reranker。",
                "上线时建议为每次检索保存候选池快照，至少包括 doc id、score、rank、filter、压缩后长度和最终是否入选。A/B 调参时比较这些结构字段，比只比较最终回答更稳定。最终用户只看到答案，工程团队必须看到每层检索决策。",
            ]),
            ("常见误解与边界情况：rerank 不是召回魔法", [
                "常见误解是“加 reranker 就会变准”。如果 base retriever 没有召回正确文档，reranker 没有机会看到它；如果切块把关键条件拆散，reranker 也只能在残缺文本里排序。Rerank 改善的是候选池内部的精确率，不是替代 ingestion、embedding 和 filter。",
                "边界情况是高召回带来的成本。base k 从 5 提到 50 可能提高覆盖，但 compressor 和 reranker 的延迟、费用和失败率也会上升。生产系统要为不同问题类型设置不同候选规模，例如 FAQ 可小 k，复杂政策问答可大 k 加精排。",
            ]),
            ("源码排障清单：候选池先于精排", [
                "排查时先打印 base retriever 的原始候选，包括 rank、score、source、filter 和文本摘要。正确证据不在候选池时，不要看 reranker；先检查 query、filter、chunk、embedding 和 hybrid 检索。正确证据在候选但排很后，再检查 reranker 输入长度、模型限制和排序分数。",
                "ContextualCompressionRetriever 的 trace 应同时保存压缩前和压缩后。若压缩后丢了关键句，查看 compressor 提示或阈值；若压缩后 metadata 丢失，修 compressor 返回 Document 的逻辑；若压缩结果为空，定义回退策略，是使用原始候选、扩大检索，还是告诉用户证据不足。",
            ]),
            ("Compressor 类型与失败模式", [
                "抽取式 compressor 从长 Document 中摘出相关句，优点是省 token，风险是删掉限定条件。过滤式 compressor 删除不相关文档，优点是简单，风险是阈值过高漏证据。重排式 compressor 改变顺序，优点是提高 top-k 质量，风险是引入模型偏见。Pipeline 能组合多步，但每步都要记录输入输出。",
                "LLMChainExtractor 这类模型抽取器适合长文档，但要防止生成式改写；EmbeddingsFilter 速度快，但仍受 embedding 空间限制；交叉编码器 reranker 准确但成本高。不要把这些组件统称“压缩”后就忽略差异。选择组件时要明确问题类型、延迟预算和错误代价。",
            ]),
            ("Precision 也可能过高", [
                "过度追求精确率会让系统只返回一个看似最相关段落，却漏掉限制条件、例外条款或必要步骤。用户问“如何申请退款并保留会员权益”时，答案可能需要退款政策和会员政策两个来源。若 reranker 只保留退款段落，最终回答会不完整。",
                "因此 top-k context 应兼顾相关性和覆盖面。可以按主题去重，确保不同 source 或 section 都有代表；也可以用 MMR 增加多样性，再用 reranker 保证可回答性。精确不是越窄越好，而是让模型看到足够且不过量的证据集合。",
            ]),
            ("Search kwargs 的治理", [
                "search_kwargs 不应散落在业务代码各处。建议按场景定义 profile：快速 FAQ、深度政策、代码文档、审计查询。每个 profile 明确 k、fetch_k、filter、search_type、rerank_k 和超时。这样调参有版本记录，也能在评测中比较 profile，而不是追踪几十个调用点。",
                "用户输入不应直接控制所有 search_kwargs。允许用户选择范围或时间可以，但 tenant、acl、最大 k、命名空间等安全参数必须由系统注入。否则提示注入或恶意请求可能扩大检索范围，拿到本不该进入候选池的资料。检索参数也是安全边界。",
            ]),
            ("上下文预算分配", [
                "压缩和 rerank 的最终目标是给模型分配有限上下文。预算不只包括文档，还包括系统提示、用户问题、历史、工具观察和输出空间。若把所有预算给检索资料，多轮问题会丢掉用户刚才的澄清；若历史占太多，检索证据又不够。RAG 与 memory 同时使用时更要显式分配预算。",
                "一种实用做法是为每类上下文设上限：最近消息最多多少 token，检索 context 最多多少 token，每个 source 最多多少段。超过上限时由 reranker 或摘要器裁剪，并在 trace 中记录裁剪原因。这样模型看到的上下文可解释，成本也可控。",
            ]),
            ("多路召回的合并", [
                "复杂系统常同时使用向量检索、关键词检索、结构化过滤和手工规则候选。合并时要去重同一 chunk，保留每个通道的 rank 和 score，并定义融合策略。简单拼接会让先执行的通道占优势；只按一个分数排序又会丢掉其他通道的信号。",
                "融合结果应让 reranker 看到来源通道。某个候选既被关键词命中又被向量命中，通常比只被一个通道命中更值得保留。相反，只有关键词但语义很偏的候选可被降权。多路召回的目标是覆盖不同问题类型，而不是把多个黑盒叠在一起。",
            ]),
            ("Rerank 评测的标注方式", [
                "评测 reranker 需要给 query-document 对标注相关性等级，例如不可用、部分相关、可回答、关键证据。只有二分类会丢掉“有点相关但不够回答”的差异。排序指标可以看 MRR、nDCG 或 top-k 命中，但课程实践中至少要人工看 top-5 是否包含关键证据。",
                "标注时要保留 query 意图。一个文档对“如何配置”相关，对“为什么失败”可能不相关。Reranker 读的是 query 和候选配对，因此评测样本也应按配对构造。只给文档打全局好坏分，无法衡量上下文相关性。",
            ]),
            ("压缩器的回退策略", [
                "Compressor 可能超时、返回空列表或生成无效文本。生产链路应有回退：使用原始 top-k、降低压缩强度、跳过 rerank、或返回证据不足。不同回退会影响质量和成本，不能让异常冒泡成用户看不懂的错误。",
                "回退也要记录。若某天 reranker 服务降级，最终答案质量可能下降；日志应能显示本轮是否使用了压缩、是否回退、回退原因是什么。否则团队看到答案变差，却不知道是模型问题还是检索后处理失效。",
            ]),
            ("长文档压缩的引用跨度", [
                "从长 Document 中抽取几句话时，最好记录原文跨度或行号。这样最终引用可以跳到原文位置，而不是只引用压缩后的临时文本。没有跨度，用户无法核对上下文，工程也无法判断抽取是否漏掉前后限定。",
                "若压缩器生成摘要而非抽取，引用语义更复杂。摘要可帮助模型理解，但不应作为逐字证据。最终回答引用时应指向摘要背后的原始 Document，必要时把摘要标注为“系统生成的阅读笔记”。这个区分能减少伪引用。",
            ]),
            ("查询分类与检索策略", [
                "并非所有问题都需要同一套 retriever。定义型问题适合小 k 和高精度；比较型问题需要多来源和多样性；故障排查问题需要代码、错误日志和文档混合；合规问题需要严格版本和权限过滤。先识别问题类型，再选择检索 profile，质量会比一个默认 k 更稳定。",
                "查询分类可以由规则、轻量模型或上游 Agent 完成，但结果必须可观测。trace 中记录本轮选择了哪个 profile、为什么选择、用了哪些 search_kwargs。分类错了时，团队才能知道是分类器问题，不是 retriever 本身差。",
            ]),
            ("重复候选的处理", [
                "向量库常返回同一父文档的相邻 chunk，尤其 overlap 较大时。若 top-k 全是同一段附近的重复信息，模型缺少互补证据。可以按 parent_id 或 source 去重，限制每个 source 的最大段数，再把名额留给其他来源。",
                "去重不能太粗。一本手册的不同章节可能都相关，按 source 只留一个会漏掉重要条件。更好的策略是按 parent_id、section_path 或语义簇去重，并保留必要的相邻块。去重本身也是检索策略，应被评测。",
            ]),
            ("Reranker 输出的稳定性", [
                "模型式 reranker 可能受提示、候选顺序和截断影响。为了稳定，应固定输入格式、限制候选长度、要求结构化分数，并在超时时回退。若 reranker 输出解释，也要把解释当调试信息而不是用户事实。",
                "A/B 测试 reranker 时，要比较同一候选池上的排序变化。否则 base retriever 候选变了，无法判断 reranker 是否更好。把候选池快照保存下来，可以离线反复跑不同 reranker，这是优化检索栈的有效方法。",
            ]),
            ("最终 context 的组装", [
                "检索栈的输出不是简单 docs[:k]。组装 context 时要决定排序、分组、来源标题、分数是否展示、长段如何截断、重复 source 如何合并。这个步骤会影响模型阅读顺序，也影响用户引用体验。Rerank 分数高的块不一定应该单独出现，可能需要相邻块补充定义。",
                "组装器还应保留被丢弃候选的摘要。上线排障时，只看最终 context 不够，还要知道哪些候选被压缩、过滤或去重。尤其当用户指出答案漏了某个条件时，团队需要判断条件是从未召回、被 reranker 降权、还是在 context 组装时被截断。",
            ]),
            ("用户可见的检索解释", [
                "有些产品会向用户展示“已检索 6 份资料，采用其中 3 份”。这种解释不必暴露内部分数，但应说明来源范围和时间。用户知道系统真的查了资料，也能发现来源不对时及时反馈。",
                "解释不能替代真实引用。若系统说使用了公司政策库，答案里仍应标出具体段落。泛泛的“我查了资料”无法支持事实核验，也无法帮助工程定位错误。用户解释和工程 trace 应来自同一候选与引用数据。",
                "当检索没有找到足够证据时，也应该解释边界：是资料库没有覆盖、权限范围不包含、还是结果分数太低。这样的说明能引导用户补充范围或联系资料维护者，而不是让用户误以为系统故障。",
            ]),
        ],
        "pitfalls": [
            ("top_k 越小越精准", "太小会漏召回；常见做法是先大 k 召回，再压缩或 rerank。"),
            ("rerank 可以修复所有索引问题", "如果正确文档第一层没召回，reranker 没机会看见。"),
            ("压缩后 metadata 不重要", "压缩后的 Document 仍要能引用原 source、page 和 chunk。"),
            ("召回率和精确率只看最终答案", "应分别评测候选池召回、rerank 排序和最终回答引用。"),
        ],
        "lab_title": "调一个两阶段检索栈",
        "lab_steps": [
            "为一个问题写出理想答案所需的 3 个证据块。",
            "设置 base retriever k=20，检查理想证据是否都出现在候选池。",
            "设计 compressor：保留含关键术语和定义的句子，删除导航和广告。",
            "设计 rerank 输出：记录每个候选的新分数和排序变化。",
            "把 top_k 从 3、5、8 分别跑一遍，比较引用完整性、噪声和 token 成本。",
        ],
        "version_note": "当前 master 中 ContextualCompressionRetriever 位于 libs/langchain/langchain_classic/retrievers/contextual_compression.py；BaseDocumentCompressor 位于 libs/core/langchain_core/documents/compressor.py。旧的 libs/langchain/langchain/retrievers/... 路径需要更新。",
        "points": [
            "高质量检索常用两阶段：先高召回，再压缩/精排。",
            "search_kwargs 是检索行为的重要入口，包括 k、filter 和 search_type。",
            "ContextualCompressionRetriever 包装 base retriever 与 compressor。",
            "reranker 只能重排已召回候选，不能凭空找回漏掉文档。",
            "压缩和重排后仍必须保留 source、score 和 chunk metadata。",
        ],
    }
)


LESSON_36_MEMORY_STATE = _build_lesson(
    {
        "name": "记忆、会话历史与状态",
        "core": "会话记忆把多轮消息、摘要、检查点和长期偏好组织成下一轮可用上下文，但每类记忆都有不同生命周期和隐私边界",
        "contract": "BaseChatMessageHistory、InMemoryChatMessageHistory、add_messages、InMemorySaver 与 create_agent",
        "artifact": "messages 状态、checkpoint、summary memory、长期记忆记录和下一轮 prompt context",
        "risk": "把敏感信息长期保存、把过期偏好当事实、历史裁剪后丢工具因果、摘要覆盖原始证据",
        "tuning": "最近窗口大小、摘要触发阈值、checkpoint namespace、长期记忆写入策略和删除策略",
        "evidence": "message id、thread_id、checkpoint_id、summary 版本、memory source、写入原因和过期时间",
        "boundary": "短期消息服务当前任务，checkpoint 服务可恢复执行，长期记忆服务跨会话偏好；三者不能混用",
        "debug": "本轮消息是否 append、checkpoint 是否按 thread 保存、summary 是否进入 prompt、长期记忆是否经过同意和过滤",
        "lead": "Memory 不是一个单一对象，而是一组围绕会话状态的策略：ChatMessageHistory 保存多轮 Human/AI/Tool 消息；LangGraph 的 add_messages reducer 把增量消息合并进 state；checkpoint saver 让线程可恢复、可 time travel；summary memory 把长历史压缩成短上下文；长期记忆则保存跨会话偏好或事实。本课追踪 conversation turn → append messages → checkpoint/state → retrieval or summary memory → next turn context，重点区分 short-term、long-term 与 LangGraph state。",
        "analogy": "把对话系统想成医生接诊。病历本里的本次问诊记录是短期历史，能解释刚才问了什么、做了什么检查；医院系统的存档 checkpoint 能让医生中断后恢复；病人长期档案记录过敏史和长期偏好，但写入需要谨慎、可删除、可追溯。不能把一次闲聊当永久病史，也不能在下一次问诊时忘掉刚刚开的检查单。",
        "map_title": "本课地图：一轮对话如何变成下一轮上下文",
        "map_nodes": [
            ("Turn input", "用户新消息进入线程，带 thread_id/context", "before"),
            ("Chat history", "HumanMessage、AIMessage、ToolMessage 追加到 messages", "now"),
            ("Checkpoint", "state 按线程保存，可恢复、回放和调试", "now"),
            ("Memory policy", "选择最近窗口、摘要、长期检索或拒绝写入", "source"),
            ("Next context", "下一轮 prompt 读取合适的历史、摘要和长期记忆", "after"),
        ],
        "source_intro": "当前 chat history 核心抽象和内存实现均可在 langchain_core.chat_history 验证；旧 community in_memory 路径在当前 master 中变成 classic re-export。LangGraph 消息合并与内存 checkpoint 仍是理解 Agent state 的关键。",
        "sources": [
            {"file": "libs/core/langchain_core/chat_history.py", "symbol": "BaseChatMessageHistory", "role": "定义 add/get/clear 消息历史接口", "direction": "会话历史存储抽象"},
            {"file": "libs/core/langchain_core/chat_history.py", "symbol": "InMemoryChatMessageHistory", "role": "核心包内可验证的内存消息历史实现", "direction": "教学、小规模或测试场景使用"},
            {"file": "langgraph/graph/message.py", "symbol": "add_messages", "role": "LangGraph 常用 messages reducer，按 id 合并消息列表", "direction": "图节点返回增量消息后写回 state"},
            {"file": "langgraph/checkpoint/memory/__init__.py", "symbol": "InMemorySaver", "role": "内存 checkpoint saver，保存线程状态快照", "direction": "图编译和运行时持久化入口"},
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "高层 Agent 工厂，使用图状态、messages 和 checkpoint 组织循环", "direction": "用户 API 到 LangGraph state 的桥"},
        ],
        "flow_title": "状态流：一次会话回合进入记忆",
        "flow_kind": "state_flow",
        "flow_steps": [
            ("用户发言", "HumanMessage 进入当前 thread，运行时知道 user_id 和 thread_id。", "input"),
            ("追加消息", "add_messages 把 HumanMessage、AIMessage、ToolMessage 增量合并到 state['messages']。", "messages"),
            ("保存 checkpoint", "InMemorySaver 或生产 saver 按 thread_id 保存状态快照。", "checkpoint"),
            ("执行记忆策略", "短历史保留最近窗口；长历史生成摘要；长期偏好经过过滤和同意后写入 store。", "policy"),
            ("下一轮上下文", "Prompt 读取最近消息、摘要和检索到的长期记忆，但不泄漏无关隐私。", "context"),
        ],
        "trace": [
            {"step": "1. turn", "input": "用户：以后回答尽量用中文，并记住我在学 LangGraph", "action": "创建 HumanMessage，附 thread/user context", "output": "messages 增量"},
            {"step": "2. append", "input": "旧 messages + 新 HumanMessage", "action": "add_messages 按 id 合并", "output": "state['messages'] 增长"},
            {"step": "3. checkpoint", "input": "完整 state", "action": "saver.put 写入 thread 快照", "output": "checkpoint_id 可恢复"},
            {"step": "4. memory", "input": "本轮内容", "action": "判断“中文偏好”可长期保存，“正在学 LangGraph”可短期或带过期保存", "output": "summary/long-term records"},
            {"step": "5. next", "input": "下一轮问题", "action": "读取最近窗口 + 摘要 + 相关长期偏好", "output": "模型获得合适上下文"},
        ],
        "code_path": "langgraph/graph/message.py + langgraph/checkpoint/memory/__init__.py",
        "code_symbol": "add_messages + InMemorySaver",
        "code": """class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    summary: str

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

app.invoke(
    {"messages": [HumanMessage("请记住我偏好中文解释")]},
    config={"configurable": {"thread_id": "u1-thread"}},
)
""",
        "code_note": "教学版展示 state、messages reducer 和 checkpoint 的分工：add_messages 决定如何合并消息，checkpointer 决定如何按线程保存状态。长期记忆是否写入，需要额外策略，不应默认把所有历史永久保存。",
        "sections": [
            ("短期历史、状态和长期记忆不是一回事", [
                "Chat history 关注对话消息序列，解决“刚才说了什么”。LangGraph state 关注图运行时的业务状态，除 messages 外还可以有 summary、当前任务、工具结果、审批标记。Checkpoint 关注某个 thread 的状态快照，解决中断恢复、time travel 和调试。长期记忆关注跨会话可复用信息，例如稳定偏好或用户授权保存的事实。",
                "这四层生命周期不同。最近消息可能几分钟后就没必要进入 prompt；checkpoint 可能按线程保留用于恢复；长期偏好可能跨月有效但必须可删除；摘要可能只是为了压缩窗口而生成。把它们都叫 memory 会导致错误设计：把 checkpoint 当画像、把临时任务当偏好、把摘要当原始证据。",
            ]),
            ("add_messages 的合并语义", [
                "LangGraph 的 add_messages reducer 让节点只返回增量消息，运行时负责把它们合并到 state['messages']。它不仅是 list append；消息有 id 时可以按 id 覆盖，配合工具调用、人工修改和重放更稳定。理解 reducer 的意义，才能解释为什么多个节点可以共同写 messages，而不是每个节点手工复制整段历史。",
                "新版本消息合并还支持删除哨兵一类的控制语义，例如用特殊消息表达移除历史中的某条记录。即使具体 API 会随版本演进，原则不变：消息状态不是随便拼接字符串，而是带角色、id、tool_call_id 和元数据的结构化列表。裁剪历史时要保持工具请求和 ToolMessage 的因果配对，不能只删中间一半。",
            ]),
            ("Checkpoint 负责可恢复，不负责画像", [
                "InMemorySaver 适合教学，因为它把 checkpoint 概念变得很轻：给 graph.compile 传入 checkpointer，再用 thread_id 调用，运行时就能保存状态快照。生产 saver 可能写数据库或对象存储，但核心问题一样：按哪个 thread 命名，什么时候保存，如何列出历史，如何恢复到某个 checkpoint。",
                "checkpoint 记录的是执行状态，不等于同意长期记住。用户在一次任务里提供的地址、验证码、身份证号，可能会出现在 checkpoint 中用于恢复本次流程，但不应自动写入长期 memory store。隐私治理需要定义 checkpoint 保留期、访问权限和删除策略；长期记忆还要额外经过写入判断和用户可控删除。",
            ]),
            ("Summary memory 是压缩，不是事实来源", [
                "摘要解决上下文窗口问题：历史太长时，把早期对话压缩成短说明，再保留最近几轮原始消息。摘要应该标注生成时间和覆盖范围，最好保留可回溯的 checkpoint 或消息范围。模型下一轮可以读摘要理解背景，但关键事实、工具结果和承诺仍应能回到原始消息。",
                "摘要会丢细节，也可能引入偏差。比如用户说“不要记住我的手机号，只用于本次验证”，摘要若写成“用户手机号是...”就造成隐私泄漏。生成摘要时要有规则：敏感信息脱敏，临时信息不进入长期摘要，用户纠正后的事实覆盖旧事实，过期任务从摘要中移除。",
            ]),
            ("长期记忆更像可检索资料库", [
                "长期记忆可以存用户偏好、项目背景、稳定身份信息或跨会话任务进展，但它应该像小型知识库一样有 schema：key、value、source、reason、created_at、updated_at、expires_at、confidence、delete_policy。没有这些字段，系统无法解释为什么记住、何时该忘、用户要求删除时删哪条。",
                "长期记忆的读取也应按相关性和权限过滤，而不是每轮全部塞进 prompt。用户问代码问题时，读取“偏好中文解释”有用；读取上周一次性订单号没有用。长期记忆越多，越需要 retriever 或规则选择当前相关记录。否则 memory 会变成噪声源，甚至把旧偏好压过用户本轮明确指令。",
            ]),
            ("记忆系统的隐私排障", [
                "当用户发现系统记住了不该记的内容，要沿写入路径排查：原始 HumanMessage 是否进入 chat history，summary 是否复制了敏感字段，long-term store 是否写入，checkpoint 是否仍保留旧状态，日志或评测样例是否另存一份。只删一个表往往不够，需要明确哪些存储属于产品记忆，哪些属于审计或调试记录。",
                "设计记忆策略时最好把每条信息分成四类：本轮任务必要、短期会话有用、长期偏好可保存、禁止保存。用户说“以后都用中文”通常可保存；用户上传合同要求本次总结，合同内容不应变成长期记忆；用户纠正“我现在不是 A 项目成员”应更新或删除旧记录。记忆的智能不在于多记，而在于只记该记的。",
            ]),
            ("常见误解与边界情况：记得越多不等于越智能", [
                "常见误解是把所有历史都保存并塞回 prompt。这样会迅速带来 token 成本、隐私风险和上下文噪声。用户当前问题可能只需要最近两轮和一个长期偏好，没必要读取半年前的闲聊。记忆系统的质量体现在筛选和遗忘，而不是无限追加。",
                "边界情况是用户纠正自己或改变偏好。长期记忆里旧偏好必须能被更新或废弃；摘要里也要反映最新纠正。若系统同时读到“用户喜欢英文回答”和“用户现在要求中文”，应优先本轮明确指令，并考虑更新长期记录。记忆不是不可变事实，而是带来源和时间的记录。",
            ]),
            ("源码排障清单：messages、checkpoint、store", [
                "如果模型忘记上一轮工具结果，先查看 state['messages'] 是否包含对应 ToolMessage，tool_call_id 是否和 AIMessage.tool_calls 配对。若消息存在但 prompt 没看到，检查 MessagesPlaceholder 或 state 到 prompt 的映射。若消息根本没进 state，检查节点返回值和 add_messages reducer。",
                "如果线程恢复失败，检查 config 中 thread_id 是否稳定、checkpointer 是否传入 graph.compile、checkpoint saver 是否持久化到预期位置。若跨会话偏好没有出现，检查长期 store 的写入策略和读取 retriever，而不是只看 checkpoint。短期恢复和长期画像是两条路径。",
            ]),
            ("RemoveMessage 与历史裁剪", [
                "长对话必须裁剪，但裁剪不能破坏消息因果。工具请求 AIMessage 和对应 ToolMessage 应成对保留或成对移除；否则模型可能看到工具结果却不知道它回答哪个请求，或看到请求却没有观察结果。支持删除消息的 reducer 语义让系统可以显式移除旧消息，而不是粗暴截断列表。",
                "裁剪策略应优先保留系统规则、最近用户目标、未完成工具链和关键决策。早期寒暄、重复确认和过期工具观察可以摘要或删除。每次裁剪最好记录原因和覆盖范围，这样用户追问“你为什么忘了”时，工程团队能解释是窗口策略而非随机丢失。",
            ]),
            ("Checkpoint 写入与中断恢复", [
                "LangGraph checkpoint 不只是最后状态快照；执行过程中还可能记录中间 writes，用于恢复并发节点、interrupt 和 time travel。理解 put 与 put_writes 的差异有助于排查“节点执行了但状态没恢复”的问题。教学页不展开底层存储实现，但要知道 checkpoint 是图运行时的一部分。",
                "人审 interrupt 场景尤其依赖 checkpoint。模型准备执行敏感工具时，图中断并保存当前 state；人工批准后，系统从同一 thread 的 checkpoint 继续，而不是重新让模型生成一次请求。若没有稳定 checkpoint，审批前后的消息和工具调用 id 可能对不上。",
            ]),
            ("BaseStore 与长期记忆", [
                "长期记忆更接近 key-value 或文档 store，而不是 checkpointer。它按用户、命名空间或主题保存可检索记录，并在下一轮根据相关性读取。LangGraph 生态常把 checkpointer 用于 short-term thread state，把 store 用于跨线程 long-term memory；这个分工能避免把所有线程快照当成用户画像。",
                "写长期 store 前应有 memory policy：哪些信息自动保存，哪些需要确认，哪些禁止保存，哪些带过期时间。读取时也要按 namespace 和用户权限过滤。否则一个用户的偏好可能泄漏到另一个用户，或临时任务信息在未来无关对话中被模型误用。",
            ]),
            ("摘要策略与事实校验", [
                "摘要 memory 应把长历史压缩成当前任务需要的背景，而不是改写成永久事实。摘要中出现的事实最好保留来源消息范围，例如“来自第 3-8 轮”。当用户纠正摘要内容时，系统应更新摘要并保留修正依据。没有来源的摘要会变成另一个不可解释的模型输出。",
                "摘要还要处理工具结果。工具观察通常比模型自然语言更接近事实，不能在摘要中被随意弱化或改写。若工具返回“余额不足，交易失败”，摘要不能写成“用户完成了支付”。对关键业务状态，宁可保留结构化字段，也不要只依赖自然语言摘要。",
            ]),
            ("隐私删除的实际范围", [
                "用户要求删除记忆时，要区分产品长期记忆、当前线程历史、checkpoint、日志、备份和评测样本。产品承诺应明确哪些会立即删除，哪些因审计或安全需要按策略保留，哪些会在备份周期后消失。技术实现上，要能根据 user_id 和 memory id 找到相关记录。",
                "不要把删除请求交给模型解释后就结束。模型可以生成确认话术，但真正删除必须由确定性代码执行，并返回可审计结果。对于敏感信息，最好在写入前就阻止进入长期 memory，降低后续删除复杂度。记忆系统越克制，隐私治理越简单。",
            ]),
            ("删除策略演练", [
                "设计 memory 功能时，应提前演练一次删除请求。给定 user_id 和 memory_id，列出要清理的长期 store 记录、索引记录、摘要片段、活跃 thread checkpoint、可搜索缓存和评测样本；再标出哪些属于产品可立即删除，哪些属于审计日志按保留期处理。演练输出应是确定性清单，而不是“让模型忘记”。",
                "删除后还要验证读取路径。下一轮 prompt 不应再出现该记忆，长期记忆 retriever 不应命中相关记录，摘要若曾包含敏感片段也要重写或作废。若系统支持多设备或多线程，会话缓存也要失效。删除策略只有覆盖写入、读取、缓存和审计边界，用户的“忘记我说过”才真正可信。",
            ]),
            ("多线程会话与身份", [
                "同一个用户可能同时有多个 thread：学习课程、处理订单、调试代码。thread_id 决定短期状态隔离，user_id 决定长期记忆归属。把二者混用会造成串话：一个线程的工具结果进入另一个线程，或一个用户的偏好被另一个用户读取。",
                "运行时 config 应稳定传入 thread_id、user_id 和必要权限上下文。模型不应自己填写这些安全字段。记忆读取和写入都要使用系统侧身份，而不是用户消息里的自称。这样才能防止提示注入要求“把我当成另一个用户”。",
            ]),
            ("工具消息与记忆", [
                "ToolMessage 通常包含外部系统事实，例如订单状态、搜索结果或执行错误。它适合短期对话和 checkpoint，但不一定适合长期记忆。一次订单查询结果过几天可能过期，长期保存会误导未来回答。记忆策略要按事实有效期决定是否保存。",
                "有些工具结果可以提炼成长期偏好，例如用户每次都选择中文文档；有些只能作为本次任务证据，例如支付失败原因。模型可以建议写入，但最终应由确定性策略判断。不要把工具返回 JSON 原样塞进长期 store。",
            ]),
            ("摘要触发时机", [
                "摘要不应每轮都重写，否则成本高且容易累积漂移。常见触发条件包括消息 token 超过阈值、完成一个任务阶段、工具链结束或用户显式切换主题。触发时要把最近未总结消息和旧摘要一起生成新摘要，并记录摘要版本。",
                "摘要更新后，最近窗口仍要保留若干原始消息，尤其是用户最新目标和未完成工具结果。只保留摘要会让模型失去语气、约束和细节。摘要是压缩层，不是当前上下文的唯一来源。",
            ]),
            ("记忆评测", [
                "记忆系统也需要评测样例。例一：用户要求以后中文回答，下一轮应使用中文；例二：用户提供一次性验证码，下一轮不应复述；例三：用户纠正偏好，旧偏好应被覆盖；例四：另一个 thread 不应看到当前任务细节。",
                "评测断言应检查结构记录，而不只是最终回答。长期 store 是否新增正确 key，敏感信息是否未写入，checkpoint 是否按 thread 隔离，summary 是否脱敏，删除请求后记录是否消失。结构断言能防止记忆功能表面可用、底层泄漏。",
            ]),
            ("记忆与 RAG 的交界", [
                "长期记忆可以被看作一类私有 RAG 数据源：它有记录、有 metadata、有写入来源，也需要检索和引用。区别在于记忆往往更敏感、更个人化、更容易过期。读取长期记忆时应像检索文档一样记录命中的 memory id 和使用原因。",
                "当记忆和外部文档冲突时，本轮用户指令和权威资料通常优先于旧记忆。例如长期记忆说用户在学旧版本 API，但本轮用户明确说切到 v1 新文档，系统应更新或忽略旧记忆。优先级规则能减少“越记越固执”的问题。",
                "每条长期记忆还应能解释来源、时间和用途。用户问“你为什么知道这个偏好”时，系统应能回到某次明确授权或可保存事件，而不是只说历史里出现过。可解释性让记忆从神秘画像变成可审计记录。",
            ]),
        ],
        "pitfalls": [
            ("Memory 就是把所有历史塞进 prompt", "历史需要窗口、摘要、检索和隐私策略，否则成本高且容易泄漏。"),
            ("checkpoint 等于长期记忆", "checkpoint 是线程状态快照，长期记忆是跨会话可检索记录，生命周期不同。"),
            ("摘要可以完全替代原始消息", "摘要会丢细节和证据；关键工具结果和可审计消息仍要保留。"),
            ("用户说记住就必须永久保存", "长期写入要考虑同意、敏感信息、过期、可删除和最小化原则。"),
        ],
        "lab_title": "制定一条安全记忆策略",
        "lab_steps": [
            "写 5 条用户发言：偏好、临时任务、敏感信息、事实纠正和闲聊。",
            "分别判断每条进入最近窗口、摘要、长期记忆、还是拒绝保存。",
            "为长期记忆记录写 source、reason、created_at、expires_at 和 delete 方式。",
            "设计下一轮 prompt：哪些历史直接放入，哪些通过检索放入，哪些不能放入。",
            "模拟用户要求删除记忆，写出应该清理的长期记录和 checkpoint/日志边界。",
        ],
        "version_note": "当前可验证路径中 InMemoryChatMessageHistory 位于 langchain_core.chat_history；langchain_classic/memory/chat_message_histories/in_memory.py 只是 re-export。学习时优先理解 core 抽象和 LangGraph state/checkpoint，而不是旧 Memory 类名。",
        "points": [
            "短期历史、checkpoint、摘要和长期记忆是不同层，不应混用。",
            "add_messages 负责把节点产出的消息增量合并进 state。",
            "checkpoint 让线程可恢复和可调试，但不等于用户长期画像。",
            "长期记忆要有写入理由、隐私过滤、过期和删除机制。",
            "下一轮上下文应只读取相关且允许使用的记忆。",
        ],
    }
)
