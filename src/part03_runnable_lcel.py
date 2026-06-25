"""C-level Part 3: Runnable and LCEL internals."""

import shell


LESSON_12_RUNNABLE_PROTOCOL = (
    r"""
<p class="lead">Runnable 是 LangChain 在应用层最重要的“标准插座”：提示词、模型、解析器、检索器、工具包装器、LCEL 链，甚至 LangGraph 编译后的图，都可以用同一套 <span class="mono">invoke / ainvoke / stream / astream / batch / abatch</span> 协议运行。本课不把 Runnable 当成“会被管道连接的对象”这么简单，而是把它拆成执行入口、输入输出契约、序列化边界、配置传播和回调追踪五层来看。理解这一层，后面的 LCEL、并行、分支、重试、Fallback 才不会像语法糖，而会像一套可组合的运行时。</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  把 Runnable 想成<strong>通用电源插座和电器铭牌</strong>：插座规定电压、插头形状和接地规则，电器可以是台灯、电脑、充电器；LangChain 规定调用方法、配置传递和事件上报，组件可以是 prompt、model、parser。你不需要知道每个电器内部怎么把电变成光或计算，只要它遵守插座协议，就能接进同一条排插。真正重要的不是“每个电器都一样”，而是“每个电器的连接方式一致”。</div>
"""
    + shell.lesson_map(
        "本课地图：从统一入口到可观测运行",
        [
            ("标准入口", "invoke 是同步核心；ainvoke、stream、batch 围绕它给出统一调用形状", "now"),
            ("数据契约", "每个 Runnable 明确接收什么输入、返回什么输出，链路靠这个契约首尾相接", "now"),
            ("配置传播", "RunnableConfig 携带 callbacks、tags、metadata、run_name 等横切信息", "now"),
            ("可序列化", "RunnableSerializable 让部分链可以保存、检查、传输或在 tracing 中展示结构", "source"),
            ("下一课", "LCEL 的 | 只是把这些标准插座按顺序接起来", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>读 Runnable 不要从某个模型 provider 开始，因为 provider 代码会把注意力带到网络请求、鉴权和返回格式上。更稳的路线是先看 <span class="mono">libs/core/langchain_core/runnables/</span>：这里定义了“所有可运行组件共同承诺什么”。下面这张源码地图把本课需要盯住的符号放在一起，后面每一段都围绕这些符号解释。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable", "role": "抽象基类，规定 invoke/ainvoke/stream/batch 等标准执行协议", "direction": "用户代码调用入口；子类实现核心行为"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "RunnableSerializable", "role": "可序列化 Runnable 的基类，支持 name、configurable 与结构导出", "direction": "链路保存、调试、LangSmith 展示时读取"},
            {"file": "libs/core/langchain_core/runnables/config.py", "symbol": "RunnableConfig", "role": "运行配置类型，承载 callbacks、tags、metadata、run_id、max_concurrency 等", "direction": "沿父子 Runnable 向下传播"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "RunnableBinding", "role": "把基础 Runnable 与 kwargs/config 绑定成新 Runnable", "direction": "外层包装调用内层，保留统一协议"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "RunnableEach", "role": "把单个输入协议提升到列表输入，逐项调用并收集结果", "direction": "批处理/映射场景复用底层 Runnable"},
        ]
    )
    + r"""
<h2>调用图：prompt / model / parser 为什么能串成一条链</h2>
<p>Runnable 协议的价值在“每一段都长得像可运行组件”。一个 prompt 接收字典，产出 PromptValue 或消息；模型接收消息，产出 AIMessage；parser 接收模型输出，产出业务对象。只要每段都通过同一入口调用，上层链就不用知道底层是模板渲染、HTTP 请求还是字符串解析。</p>
"""
    + shell.call_graph(
        [
            ("用户", "chain.invoke({'topic': '回调'})", True),
            ("Prompt Runnable", "校验变量，渲染消息或 PromptValue", False),
            ("ChatModel Runnable", "接收消息，调用 provider，返回 AIMessage", False),
            ("Parser Runnable", "读取文本或 message，解析成字符串、JSON 或 Pydantic 对象", False),
            ("调用者", "拿到最终业务输出，而不是中间消息", True),
        ]
    )
    + r"""
<h2>六个执行入口不是六套世界</h2>
<p><span class="mono">invoke</span> 是最容易理解的入口：给一个输入，得到一个输出。多数自定义 Runnable 只要把同步核心写清楚，就能先跑起来。<span class="mono">ainvoke</span> 是异步入口，但“异步”不等于自动并行，它只是允许事件循环在等待 I/O 时切走；如果底层仍是同步阻塞调用，框架可能只能把它放进线程池或仍然阻塞。<span class="mono">stream</span> 和 <span class="mono">astream</span> 关注“逐块产出”：模型 token、事件片段、解析器增量都可能作为 chunk 出现。chunk 的语义是“到目前为止的一段”，不是最终对象的保证。<span class="mono">batch</span> 和 <span class="mono">abatch</span> 关注“同一个 Runnable 处理多份输入”：它能利用并发限制、复用配置与错误收集，但每个元素仍要满足单次 invoke 的输入契约。</p>
<p>这六个入口背后有一个统一思想：框架尽量给出默认实现，让新组件的实现成本低；同时允许高性能组件覆盖默认行为。聊天模型可能原生支持 streaming，检索器可能能批量查询，解析器也许只能逐个处理。协议统一并不抹平差异，而是把差异藏在组件内部，把调用形状稳定地暴露给链路。</p>

<h2>输入输出契约：Runnable 不是“随便收、随便吐”</h2>
<p>很多链路错误不是 Runnable 本身错，而是你忘了每段都有清晰的输入输出边界。Prompt 通常期待一个包含模板变量的字典；ChatModel 通常期待消息列表、PromptValue 或字符串；parser 通常期待模型消息或文本。如果 parser 前面接了一个返回字典的并行分支，parser 就会报类型错误；如果 prompt 需要 <span class="mono">context</span> 和 <span class="mono">question</span>，上游却只返回 <span class="mono">input</span>，模板也会失败。Runnable 协议让“怎么调用”统一，但不替你保证“数据形状永远正确”。因此读 LCEL 链时，要像读函数签名一样读每段的输入输出。</p>

<h2>配置传播：RunnableConfig 是横切上下文，不是业务状态</h2>
<p><span class="mono">RunnableConfig</span> 携带的是运行时控制信息：callbacks 用于事件上报，tags 用于筛选运行，metadata 用于附加可观察上下文，run_name 和 run_id 用于追踪树，max_concurrency 用于批量并发限制。这些信息会从父 Runnable 传播到子 Runnable，并在进入子步骤时被 patch 或派生。它适合放“这次运行属于哪个实验、哪个页面、哪个租户标签、哪个 trace”，不适合放“购物车内容、用户余额、工具执行结果”。业务状态应该走 input/output 或图状态；配置是横切信号，不是数据管道本身。</p>
"""
    + shell.trace_table(
        [
            {"step": "1. 入口", "input": "{'topic': 'Runnable'} + config(tags=['demo'])", "action": "外层 RunnableSequence 接收 invoke 请求，标准化配置", "output": "父 run 创建，配置准备下传"},
            {"step": "2. prompt", "input": "变量字典", "action": "PromptTemplate.invoke 渲染模板，触发 prompt 子 run", "output": "PromptValue / messages"},
            {"step": "3. model", "input": "PromptValue / messages", "action": "ChatModel.invoke 调用 provider，回调记录 start/end/token", "output": "AIMessage(content='...')"},
            {"step": "4. parser", "input": "AIMessage 或文本", "action": "Parser.invoke 提取并校验结构", "output": "最终字符串、JSON 或业务对象"},
            {"step": "5. 返回", "input": "parser 输出", "action": "父 run 结束；trace 树闭合", "output": "chain.invoke 的返回值"},
        ]
    )
    + r"""
<h2>简化源码走读：默认实现把协议补齐</h2>
<p>真实源码有泛型、配置合并、回调管理、异常处理和并发控制。下面的伪代码只保留骨架：一个子类必须定义核心调用；基类围绕它提供异步、流式和批量的默认形状。源码重点不是逐行背诵，而是看出“最小实现面 + 统一外观”的框架设计。</p>
"""
    + shell.code_walkthrough(
        "libs/core/langchain_core/runnables/base.py",
        "Runnable",
        """class Runnable(Generic[Input, Output]):
    def invoke(self, input: Input, config: RunnableConfig | None = None) -> Output:
        raise NotImplementedError

    async def ainvoke(self, input: Input, config: RunnableConfig | None = None) -> Output:
        return await run_in_executor(self.invoke, input, config)

    def stream(self, input: Input, config: RunnableConfig | None = None):
        yield self.invoke(input, config)

    def batch(self, inputs: list[Input], config: RunnableConfig | None = None):
        return [self.invoke(item, config) for item in inputs]
""",
        "这是教学版骨架：真实实现会处理 callbacks、contextvars、max_concurrency、异常聚合和子 run。关键是看懂默认入口怎样围绕 invoke 建立统一协议。",
    )
    + r"""
<h2>序列化与绑定：链路能被看见，参数能被固定</h2>
<p><span class="mono">RunnableSerializable</span> 不是要求所有运行都能完全还原成 JSON；它表达的是“这个 Runnable 的结构、名称、可配置字段尽量可描述”。这对调试和可观察性很重要：当 LangSmith 或本地 trace 展示一条链时，你希望看到“PromptTemplate → ChatOpenAI → StrOutputParser”，而不是一团匿名函数。可序列化结构也让某些链可以保存、加载、对比或作为模板复用。</p>
<p><span class="mono">RunnableBinding</span> 则像给电器加一个固定转接头：同一个模型可以绑定 stop、temperature、tools 或默认 config，形成一个新 Runnable。调用者看到的仍是 invoke/stream/batch，但内部已经携带一组预设。绑定的好处是把重复参数从调用点挪到组件定义处；风险是过度绑定会让链路行为不透明，所以生产链要给绑定后的组件命名，方便 trace 中辨认。</p>

<h2>RunnableEach：列表输入不是随便 for 循环</h2>
<p><span class="mono">RunnableEach</span> 把“对一个输入可运行”的组件提升成“对一组输入可运行”的组件。它不是新业务逻辑，而是复用已有 Runnable 的契约：每个元素分别进入内层 Runnable，结果按顺序收集。这个设计的细节在于配置和并发：批量运行时 callbacks 仍要能区分每个子调用，max_concurrency 要限制同时飞出的请求，异常策略要说明是整体失败还是返回异常对象。也就是说，batch 不是“把 list 塞给模型就完了”，而是“在统一协议下组织多次单元调用”。</p>

<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("Runnable 只是为了使用 | 管道", "Runnable 首先是标准执行协议；LCEL 管道只是建立在协议之上的组合语法。"),
            ("ainvoke 会让任何代码自动并行", "异步只表示可等待；是否并行取决于底层 I/O、调度和 max_concurrency。"),
            ("stream 的每个 chunk 都是最终对象", "chunk 是增量片段，最终对象通常需要合并、解析或等待 end 事件。"),
            ("config 可以塞业务状态", "config 是 callbacks/tags/metadata 等横切配置；业务状态应走 input/output 或图状态。"),
        ]
    )
    + r"""
<h2>小结前的实验</h2>
"""
    + shell.lab_card(
        "手写最小 Runnable 心智模型",
        [
            "找一个 prompt | model | parser 示例，逐段写下每段的输入类型和输出类型。",
            "把同一条链分别用 invoke、stream、batch 运行，观察返回值形状与错误位置。",
            "给 config 加 tags 和 metadata，在回调或 LangSmith trace 中确认它们沿子 Runnable 传播。",
            "故意把 parser 接到一个返回 dict 的上游后面，记录错误信息，并说明是哪一段契约不匹配。",
        ],
    )
    + shell.version_note(
        "本课以 LangChain v1 时代的 langchain-core Runnable 设计为锚点。具体文件行号会随版本移动，但 libs/core/langchain_core/runnables/base.py 与 config.py 中的符号名是更稳定的阅读入口。"
    )
    + r"""

<h2>深入拆解：把 Runnable 当成运行时边界</h2>
<p>学习 Runnable 时，最容易低估的是“边界”二字。一个组件只要承诺自己是 Runnable，就等于承诺调用者可以用统一方式给它输入、拿它输出、给它配置、观察它运行、把它接入更大的组合。这个边界让上层代码不必关心内部是字符串模板、HTTP 模型、向量检索、工具适配器还是一整张图。边界越稳定，系统越能扩展；边界越含糊，链路越容易靠隐式约定维持。Runnable 的设计选择是把“执行”变成公共协议，把“实现细节”关在组件内部。</p>
<p>这也是为什么 input/output 契约必须被严肃对待。统一入口不会自动修复错误数据形状，只会让错误在清晰位置暴露。Prompt 报缺变量，说明上游没有提供模板需要的键；parser 报解析失败，说明模型输出没有满足解析器承诺；batch 中某个元素失败，说明那一项输入或外部依赖出现问题。把这些错误归咎于“Runnable 太抽象”是不准确的。抽象只负责把调用形状统一，真实的业务契约仍由每个组件定义和维护。</p>
<p>把 Runnable 和“普通 Python 函数”对照，更能看清它多做了什么。普通函数只有一种调用形态 f(x)，没有统一的异步、流式、批量入口，也没有内建的配置传播和回调观测；要把若干函数串成可观测、可重试、可并行的链路，你得自己发明一套约定。Runnable 把这套约定标准化：任何遵守协议的组件，调用者都能用同一心智模型 invoke/stream/batch，用同一 config 注入 callbacks 和 tags，用同一运行树结构定位问题。代价是组件作者要遵守协议、实现合理的默认行为；收益是整条链路成为可组合的标准件，而不是一堆只能在特定上下文里侥幸工作的临时函数。</p>
<h3>同步、异步、流式、批量的同构性</h3>
<p>Runnable 的多个执行入口看似复杂，其实是在回答同一个问题的四种运行形态：单次同步、单次异步、增量输出、多输入集合。它们同构的意思是：你不需要为 prompt 学一套 batch，为 model 学另一套 stream，为 parser 学第三套 async。只要组件遵守 Runnable，调用者就能先用统一心智模型尝试，再根据组件能力理解性能差异。默认 stream 可能只是 yield 最终结果，原生模型 stream 才会逐 token；默认 batch 可能只是并发多次 invoke，原生批量接口才可能合并请求。协议给你可预期的入口，不承诺每个实现都拥有同样优化。</p>
<p>在生产里，这种同构性直接影响工程组织。后端服务可以把任意链暴露成“单次调用接口”，前端可以在支持流式时切换到 stream，离线评测可以用 batch 跑样本集，异步 Web 框架可以使用 ainvoke 避免阻塞事件循环。你复用的是同一条链，而不是为四种运行方式各写一份业务流程。代价是必须理解默认实现的边界：如果底层 provider 不支持真正流式，你只能拿到一个最终 chunk；如果工具内部是阻塞 I/O，ainvoke 也不等于无限扩容。</p>
<h3>配置传播的正确姿势</h3>
<p>配置传播最常见的误用，是把它当成“隐藏参数通道”。例如把用户输入、会话历史、权限决策或购物车状态塞进 metadata，让下游 Runnable 自己从 config 里读。这样做短期省事，长期会破坏链路可读性：从函数签名看不出依赖，从 trace 看不出数据如何流动，复用组件时也不知道必须带哪些隐藏字段。更健康的做法是：业务必需的数据走 input；可观察、可调度、可筛选的数据走 config。只要某个值会改变模型答案或业务结果，它就应该显式出现在数据流里。</p>
<p>callbacks、tags、metadata 的继承也要有层次。父链可以打上产品线、环境、实验版本；子步骤可以补充自己的 run_name 和局部 metadata。不要让所有步骤都叫“RunnableLambda”，也不要让所有 metadata 都是一大坨不可搜索 JSON。好的 trace 像清晰的病例：能看到主诉、检查、诊断、用药和结果；坏的 trace 像一页杂乱聊天记录，信息很多却无法定位责任。</p>
<h3>自定义 Runnable 的判断标准</h3>
<p>什么时候需要写自定义 Runnable？如果你只是做轻量字段转换，用 RunnableLambda 足够；如果你要组合现有组件，用 LCEL 更清楚；如果你要表达复杂状态机，可能应该用 LangGraph。自定义 Runnable 适合那些有稳定输入输出契约、需要复用、需要独立命名、需要自定义 stream/batch 或需要封装外部系统的步骤。比如一个内部搜索服务适配器、一个带缓存的文档压缩器、一个公司统一审计包装器，都比匿名 lambda 更适合成为命名 Runnable。</p>
<p>写自定义 Runnable 时，先让 invoke 正确，再考虑 ainvoke、stream、batch。不要为了“看起来完整”复制一堆入口却实现不一致。每个入口都应遵守同一语义：同样输入在合理条件下返回等价结果；stream 的合并结果应能对应最终输出；batch 的每个元素应像独立 invoke；异常应保留足够上下文但不泄漏秘密。这样你的组件才能像标准零件一样进入 LangChain 生态，而不是只在某条链里侥幸可用。</p>


<h2>阅读源码时的三个检查点</h2>
<p>第一，看抽象方法和默认方法的分界。框架作者通常会把“必须由具体组件决定”的部分留成抽象，把“可以统一处理”的部分放进基类默认实现。Runnable 的设计正是如此：不同组件如何真正产生结果由自己负责，但同步、异步、批量、流式、配置、回调这些外观尽量统一。读源码时，如果你能指出哪些逻辑属于基类，哪些逻辑属于子类，就已经抓住了扩展点。</p>
<p>第二，看配置在哪里被复制、合并和派生。很多运行时问题来自配置没有传到子链，或子链覆盖了父链需要的字段。源码中的 ensure、patch、get_child 这类函数名都在提醒你：配置不是一个全局变量，而是在运行树中层层传递的对象。每进入一个子 Runnable，都要既继承父级观测信息，又给自己留下可识别的名字。这样错误发生时，trace 才能告诉你“哪一个子步骤在什么配置下失败”。</p>
<p>第三，看异常是否保持语义。一个好的 Runnable 不应该把所有异常都压成同一种“运行失败”，也不应该吞掉底层错误。模板缺变量、模型限流、解析失败、用户取消、批量中某项失败，含义完全不同。统一协议的价值是让这些异常沿同一调用路径冒出来，而不是抹平差异。你在实现自定义 Runnable 时，也应该保留异常类型和必要上下文，让上层 retry、fallback 或日志能做正确判断。</p>
<h2>和后续课程的连接</h2>
<p>本课其实是后面四课的地基。Sequence 需要 Runnable，因为只有统一入口才能把多个组件顺序接上；Parallel 需要 Runnable，因为只有统一入口才能把同一输入发给多个分支；Config 和 callbacks 需要 Runnable，因为只有每个节点都遵守配置协议，运行树才能完整；Retry 和 fallback 需要 Runnable，因为包装器要像普通组件一样继续被组合。换句话说，Runnable 不是某一课的局部知识，而是 LangChain 把模型应用工程化的共同底盘。</p>
<p>如果你以后读到某个新组件，不妨先问四个问题：它的 invoke 输入是什么？输出是什么？config 会如何影响它？它失败时抛什么异常？只要这四个问题回答清楚，你就能判断它能否接进现有链，能否并行，能否重试，能否被 trace。这个阅读习惯比记 API 更重要，因为版本会变，协议思维更稳定。</p>


<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Runnable 是统一执行协议，不只是 LCEL 管道里的一个节点。</li>
    <li>invoke、ainvoke、stream、astream、batch、abatch 是同一契约的不同运行形状。</li>
    <li>输入输出契约决定链能否首尾相接；协议统一不代表类型自动正确。</li>
    <li>RunnableConfig 传播 callbacks、tags、metadata 等横切信息，但不是业务状态容器。</li>
    <li>RunnableSerializable、RunnableBinding、RunnableEach 让链更可描述、可预设、可批量复用。</li>
  </ul>
</div>
"""
)


LESSON_13_LCEL_SEQUENCE = (
    r"""
<p class="lead">LCEL 的 <span class="mono">|</span> 看起来像把几个对象排成一行，实质是在构造 <span class="mono">RunnableSequence</span>：前一步输出成为后一步输入，整条链本身仍是 Runnable。本课的重点不是记住“prompt | model | parser”这句示例，而是掌握三件事：管道如何从左到右传递数据，已有 Runnable、普通 callable/generator-like 和 dict/mapping 如何被 <span class="mono">coerce_to_runnable</span> 变成可组合组件，以及为什么类型不匹配会让链在中途失败。注意，普通 list 不会被它自动提升；列表式批量输入属于 <span class="mono">batch</span> / <span class="mono">RunnableEach</span>，多步顺序组合则要显式串成 Sequence。</p>

<div class="card analogy">
  <div class="tag">🚚 生活类比</div>
  把 RunnableSequence 想成<strong>装配线</strong>：第一站把零件盒整理成半成品，第二站加工，第三站质检。传送带不是 shell 管道那种“字节流”，而是把上一站的完整产物交给下一站。上一站如果交出一箱螺丝，下一站却期待一块主板，传送带不会自动发明转接件；你必须显式加一个 RunnableLambda、Passthrough 或 parser 来改变形状。</div>
"""
    + shell.lesson_map(
        "本课地图：LCEL 顺序组合",
        [
            ("| 运算符", "Runnable.__or__ 把左右两侧合成 RunnableSequence", "now"),
            ("顺序数据流", "每一步的 output 直接作为下一步 input", "now"),
            ("自动提升", "Runnable、callable/generator-like、dict/mapping 通过 coerce_to_runnable 进入协议世界；plain list 不属于这里", "now"),
            ("胶水组件", "RunnableLambda 和 RunnablePassthrough 修补形状、保留原输入", "source"),
            ("后续扩展", "并行、分支、重试都依赖“组合结果仍是 Runnable”", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>LCEL 的入口在 Runnable 基类而不是某个独立 DSL 解释器里。原因很直接：只有 Runnable 自己知道如何保持“组合后仍是 Runnable”。看源码时，请把 <span class="mono">__or__</span>、<span class="mono">RunnableSequence</span> 和 <span class="mono">coerce_to_runnable</span> 连起来读。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable.__or__", "role": "重载 |，把左 Runnable 与右侧可运行对象组合", "direction": "用户写 a | b 时触发"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "RunnableSequence", "role": "顺序执行多个步骤，保存 first/middle/last 或 steps", "direction": "依次调用每个子 Runnable"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "coerce_to_runnable", "role": "把 callable、dict 等普通对象提升为 Runnable", "direction": "组合前标准化右侧对象"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "RunnableLambda", "role": "把普通 Python 函数包成 Runnable", "direction": "自定义转换逻辑进入链"},
            {"file": "libs/core/langchain_core/runnables/passthrough.py", "symbol": "RunnablePassthrough", "role": "原样透传输入，并可 assign 新字段", "direction": "在链中保留原始输入或补充字典键"},
        ]
    )
    + r"""
<h2>调用图：prompt | model | parser</h2>
<p>最经典的 LCEL 链不是为了炫耀语法短，而是把“数据从哪里来、经过哪些变形、最终到哪里去”画成一条可执行的左到右路径。每一段都只看自己的输入，返回自己的输出，外层 Sequence 负责把它们接起来。</p>
"""
    + shell.call_graph(
        [
            ("输入字典", "{'question': 'LCEL 是什么'}", True),
            ("prompt", "渲染系统提示和用户问题", False),
            ("model", "根据消息生成 AIMessage", False),
            ("parser", "提取 content 或校验 JSON", False),
            ("最终答案", "字符串或结构化对象", True),
        ]
    )
    + r"""
<h2>管道不是 shell pipe：传的是对象，不是文本流</h2>
<p>很多人第一次看到 <span class="mono">|</span> 会联想到 Unix shell：左边 stdout 的字节流喂给右边 stdin。LCEL 不一样。它传递的是 Python 对象，而且对象形状会随步骤变化。Prompt 输出可能是 PromptValue，模型输出可能是 AIMessage，parser 输出可能是字符串、字典或 Pydantic 对象。正因为传的是对象，LCEL 才能保留消息角色、tool_calls、response_metadata、usage_metadata 等结构化信息；也正因为传的是对象，类型不匹配会比纯文本管道更早、更明确地失败。</p>
<p>因此读 LCEL 链要做“接口对账”：左边产物是否正好是右边能吃的东西？如果不是，需要哪一种胶水？例如模型后面接 <span class="mono">StrOutputParser</span> 很自然，因为 parser 会从消息里取文本；检索器输出文档列表后面不能直接接普通 prompt，通常要先 format_docs；一个返回 <span class="mono">{'context': ..., 'question': ...}</span> 的并行结构可以接需要这两个变量的 prompt，但不能直接接只接受字符串的 parser。</p>

<h2>RunnableSequence 的闭包性：链本身还是链的一块积木</h2>
<p><span class="mono">prompt | model | parser</span> 的结果不是“立即执行后的答案”，而是一个新的 RunnableSequence。它拥有 invoke、stream、batch、with_config、with_retry 等同一套能力。这个闭包性是 LCEL 能规模化的关键：你可以把一条小链命名为 <span class="mono">answer_chain</span>，再把它放进更大的并行结构、分支结构或重试包装器里。没有闭包性，组合只能停留在一层；有了闭包性，复杂系统可以由多个小链分层拼装。</p>

<h2>coerce_to_runnable：为什么普通对象也能上管道</h2>
<p>LCEL 让右侧对象在组合时被提升为 Runnable。普通函数会变成 <span class="mono">RunnableLambda</span>，字典会变成并行映射（通常是 <span class="mono">RunnableParallel</span>），已经是 Runnable 的对象保持原样。这是便利，但也是常见坑的来源。你写 <span class="mono">chain | {'a': r1, 'b': r2}</span> 时，意思不是“把字典作为常量传给下游”，而是“同一个输入同时送入 r1 和 r2，再把两个结果合并成字典”。如果你真的需要常量字典，要用 lambda、RunnablePassthrough.assign 或 prompt partial 等更明确的方式。</p>
"""
    + shell.trace_table(
        [
            {"step": "1. 组合", "input": "prompt | model", "action": "Runnable.__or__ 调用 coerce_to_runnable(model)", "output": "RunnableSequence([prompt, model])"},
            {"step": "2. 再组合", "input": "sequence | parser", "action": "已有 Sequence 追加 parser，保持顺序结构", "output": "RunnableSequence([prompt, model, parser])"},
            {"step": "3. invoke", "input": "{'question': '...'}", "action": "Sequence 调 prompt.invoke", "output": "PromptValue"},
            {"step": "4. 中转", "input": "PromptValue", "action": "Sequence 把上一步输出原样交给 model.invoke", "output": "AIMessage"},
            {"step": "5. 结束", "input": "AIMessage", "action": "parser.invoke 解析 content", "output": "最终字符串或对象"},
        ]
    )
    + r"""
<h2>简化源码走读：| 如何变成 RunnableSequence</h2>
<p>真实实现还会处理反向管道、名称、输入输出 schema、流式 transform、回调和序列化。教学版只展示核心：组合时先把右侧变成 Runnable，再把步骤列表交给 Sequence；运行时逐步把当前值替换为下一步输出。</p>
"""
    + shell.code_walkthrough(
        "libs/core/langchain_core/runnables/base.py",
        "Runnable.__or__ / RunnableSequence",
        """class Runnable:
    def __or__(self, other):
        return RunnableSequence(self, coerce_to_runnable(other))

class RunnableSequence(Runnable):
    def invoke(self, input, config=None):
        value = input
        for step in self.steps:
            value = step.invoke(value, config=config)
        return value

def coerce_to_runnable(obj):
    if isinstance(obj, Runnable):
        return obj
    if callable(obj):
        return RunnableLambda(obj)
    if isinstance(obj, dict):
        return RunnableParallel(obj)
    raise TypeError("Expected a Runnable, callable or dict")
""",
        "这段伪代码刻意省略大量细节，但保留了 LCEL 的三个关键动作：重载 |、标准化右侧对象、顺序传递当前值。",
    )
    + r"""
<h2>RunnableLambda：胶水有用，但也会隐藏名字</h2>
<p><span class="mono">RunnableLambda</span> 是把普通 Python 函数塞回 Runnable 世界的桥。它适合做轻量转换：把文档列表格式化成字符串、从字典里取某个字段、把模型输出包装成业务对象。问题是 lambda 很容易变成“匿名黑盒”。在 trace 中，匿名 lambda 的名字不如一个明确命名的函数或带 run_name 的 Runnable 清楚；出错时，你也更难知道是哪一步在改形状。生产链里推荐给关键转换命名，或者用 <span class="mono">with_config(run_name='format_docs')</span> 标注。</p>

<h2>RunnablePassthrough：保留原输入，而不是复制粘贴变量</h2>
<p>顺序链有一个天然特性：下一步只看到上一步输出。若你既需要检索器的结果，又需要原始问题，就不能让检索器把问题“吃掉”后直接接 prompt。<span class="mono">RunnablePassthrough</span> 的作用是把原输入保留下来，或用 <span class="mono">assign</span> 在字典上补新字段。典型 RAG 链会把问题并行送给 retriever 生成 context，同时透传 question，最后 prompt 同时收到两者。这个模式会在下一课并行分支里展开。</p>

<h2>类型错位：LCEL 最常见的调试路径</h2>
<p>当链报错时，不要只看最后一行异常。先把整条链拆成步骤，逐段 invoke。第一步用真实输入跑 prompt，看输出是不是模型能接；第二步把 prompt 输出喂给 model，看模型返回的对象是不是 parser 能接；第三步把 parser 单独喂一个模拟 AIMessage，看解析失败是格式问题还是类型问题。LCEL 的优点是每段都是 Runnable，可以单独跑；不要把调试局限在整条链上。</p>

<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("LCEL 的 | 就是 shell pipe", "LCEL 传递 Python 对象和结构化消息，不是无类型字节流。"),
            ("字典在链里就是普通 dict 常量", "dict 会被提升为并行映射，同一个输入送到多个分支再合并。"),
            ("lambda 很方便，随便写就好", "匿名 lambda 会隐藏 trace 名称和职责，关键转换应命名或配置 run_name。"),
            ("parser 失败只影响最后一步", "Sequence 任一步失败都会让整条 chain.invoke 失败，除非显式重试、修复或 fallback。"),
        ]
    )
    + r"""
<h2>小结前的实验</h2>
"""
    + shell.lab_card(
        "拆开一条 LCEL 链调试",
        [
            "写下 prompt | model | parser 中每段的输入和输出形状。",
            "把一个普通函数接进链，观察它在 trace 中的名字，再用 with_config(run_name=...) 改名。",
            "把 {'context': retriever, 'question': RunnablePassthrough()} 接到 prompt 前，确认 dict 代表并行映射。",
            "故意让 prompt 需要 context，但上游不提供该键，记录错误并定位缺口。",
        ],
    )
    + shell.version_note(
        "LCEL 的核心符号仍在 langchain-core 的 runnables/base.py 与 passthrough.py。不同版本会调整内部字段名或流式实现，但 __or__、RunnableSequence、coerce_to_runnable 这条阅读主线稳定。"
    )
    + r"""

<h2>深入拆解：Sequence 的可读性来自显式数据流</h2>
<p>LCEL 的顺序组合最重要的收益是把数据流从嵌套调用里解放出来。命令式写法可能是 <span class="mono">parse(model(prompt(input)))</span>，短小但不容易插入观测、配置、重试和局部调试。LCEL 把每一步变成显式节点：prompt 负责渲染，model 负责生成，parser 负责校验。读者不需要猜哪一层调用了哪一层，顺着 <span class="mono">|</span> 从左到右就能看到执行路径。对教学链来说这是可读性；对生产链来说，这是可维护性和可观测性的基础。</p>
<p>不过，可读性不是“越长越好”。一条二十多个 <span class="mono">|</span> 的链同样会变成难读的长句。好的做法是按语义分段：把“检索并格式化”命名为 retrieval_chain，把“生成并解析”命名为 answer_chain，把“审计包装”放在外层。因为 Sequence 本身仍是 Runnable，分段不会失去组合能力。相反，命名后的子链在 trace 中更容易理解，也更容易单独测试。</p>
<h3>coercion 是便利，也是隐式复杂度</h3>
<p><span class="mono">coerce_to_runnable</span> 是 LCEL 好用的原因之一：你可以把普通函数、字典映射直接写进链里，不必手动 new 一堆包装类。但它也是需要警惕的隐式复杂度。一个 dict 在 Python 里通常表示“这个值就是一个字典”，在 LCEL 组合语境里却表示“并行映射”。一个 callable 在普通代码里只是函数，在 LCEL 里会被包装成 RunnableLambda，并进入配置和回调体系。理解语境很关键：同样的对象，在“作为输入值”和“作为组合右侧”时语义不同。</p>
<p>为了减少误会，团队可以形成约定：复杂的 dict 并行结构用变量名表达意图，例如 <span class="mono">rag_inputs = {'context': retriever | format_docs, 'question': RunnablePassthrough()}</span>；关键 callable 不写匿名 lambda，而写命名函数；需要常量时显式写 <span class="mono">lambda _: constant</span> 或使用 prompt partial。这样读者能一眼看出“这是并行分支”还是“这是常量值”，调试时也能在 trace 里看到更清楚的节点名。</p>
<h3>类型错位的四步排查</h3>
<p>LCEL 类型错位通常可以按四步排查。第一，列出每个节点的期望输入和实际输出，不要只看变量名。第二，单独 invoke 每个节点，用小样本确认形状。第三，在错位处加入最小转换，而不是在下游写复杂兼容逻辑。第四，给转换命名，防止以后维护者删掉它。比如 retriever 输出 Document 列表，prompt 需要字符串 context，正确补丁是添加 <span class="mono">format_docs</span>；不是让 prompt 模板自己理解 Document，也不是让 parser 猜测上游结构。</p>
<p>另一个常见问题是 parser 被放错位置。parser 应该解析模型输出，而不是解析 prompt 输出、并行 dict 或检索结果。如果你看到 parser 报“没有 content 字段”或“输入不是字符串”，先检查它前面是不是模型。LCEL 不会阻止你把任意 Runnable 接在一起，因为框架无法静态知道所有动态类型；它会在运行时按协议调用，然后让具体组件暴露契约错误。</p>
<h3>声明式链与手写函数的取舍</h3>
<p>不是所有逻辑都必须写成 LCEL。非常短、只在一个地方使用、没有流式和追踪需求的纯 Python 逻辑，用普通函数可能更直接。LCEL 的优势出现在组件化、可替换、可观测、可批量和可配置的场景：同一条链要接不同模型，要给每一步打 tags，要把并行和 fallback 放进结构里，要在 LangSmith 看运行树，要让评测脚本批量调用。此时声明式链把运行结构变成一等对象，手写函数则容易把结构藏进控制流。</p>
<p>健康的工程风格是混合使用。业务规则、字段转换、格式化函数可以保持普通 Python，但通过 RunnableLambda 或命名 Runnable 接入链；模型、prompt、parser、retriever 等可观测步骤用 LCEL 组合；复杂循环或状态机交给 LangGraph。这样既不把简单逻辑 DSL 化，也不把复杂编排埋在不可观察的函数里。</p>


<h2>组合前先写形状注释</h2>
<p>在团队项目里，建议在复杂 LCEL 链旁边保留简短的形状注释，不是解释语法，而是解释每一步的数据形状。例如：输入是 question 字典；检索后得到 context 和 question；prompt 后得到消息；model 后得到 AIMessage；parser 后得到 Answer。真正容易出错的是形状对不上，而不是大家不知道模型会生成答案。</p>
<p>形状注释还能帮助评审。评审者看到 dict 出现在链中，会立刻检查它是否表示并行映射；看到 lambda，会追问它是否应该命名；看到 parser，会检查它前面是不是模型输出；看到 passthrough，会确认原始输入是否真的需要保留。LCEL 的语法很短，短语法需要更强的结构意识，否则一行优雅代码可能隐藏很多隐式约定。</p>
<h2>把长链拆成可测试单元</h2>
<p>Sequence 的闭包性允许你把长链切成小 Runnable。每个小 Runnable 都能单独 invoke，这给测试带来很大便利。你可以用假 retriever 测 prompt 输入形状，用假 model 输出测 parser，用固定样本测 format_docs，而不必每次都真实调用 provider。这样测试更快、更稳定，也更容易定位失败。长链的端到端测试仍然需要，但不应该替代每段契约测试。</p>
<p>拆分的粒度可以按责任来定：一个子链负责把用户问题变成 prompt 变量，一个子链负责模型生成，一个子链负责解析和校验。不要按技术层机械拆成很多无意义步骤，也不要把多个责任塞进一个巨大 lambda。好的子链名字应该能回答“它把什么变成什么”。例如 build_rag_inputs、generate_answer_message、parse_answer 都比 step1、helper 清楚。</p>
<h2>LCEL 与普通 Python 的协作方式</h2>
<p>有些开发者担心 LCEL 会把 Python 代码变成难调试的 DSL。实际更健康的看法是：LCEL 负责描述可观察的运行结构，Python 函数负责表达局部确定性逻辑。格式化文档、裁剪字符串、转换字段、构造引用编号，这些都可以先写成普通函数并配单元测试，再通过 RunnableLambda 接进链。这样既保留 Python 的清晰和测试便利，又获得 Runnable 的配置、追踪和组合能力。</p>
<p>反过来，如果你把所有逻辑都塞进一个普通函数，外层只看到一个 RunnableLambda，那么 LangChain 的运行树就失去细节。trace 只能告诉你“lambda 失败了”，不知道是检索、模型、解析还是格式化失败。判断是否使用 LCEL 的标准不是“语法是否更短”，而是“这一步是否值得作为可观察、可替换、可配置的节点出现”。值得，就把它显式放进链；不值得，就留在普通函数里。</p>

<h2>链路演进：从一行示例到生产结构</h2>
<p>教程里常写 <span class="mono">prompt | model | parser</span>，但生产里这行代码通常会演进出更多显式边界。prompt 前面会有输入清洗、权限过滤、检索上下文、历史裁剪；model 外面会有超时、重试、fallback、成本标记；parser 后面会有 schema 校验、业务规则检查、审计记录。LCEL 的价值不是让所有东西挤在一行，而是让这些边界都能保持 Runnable 形状，按需要组合、命名和测试。</p>
<p>因此看到一条链时，要同时问“现在的数据从哪里来”和“以后可能在哪插入能力”。如果你把关键转换藏在普通函数内部，将来加 trace 和 fallback 会困难；如果你把每个微小表达式都拆成 Runnable，当前代码又会过度复杂。好的 LCEL 结构像清楚的段落：每段有主题，段与段之间顺序明确，必要时可以单独引用。</p>

<h2>调试时保留中间值</h2>
<p>LCEL 鼓励把链看成整体，但调试时要敢于拆开。把 prompt 输出打印成消息，把模型输出保留成 AIMessage，把 parser 输入单独保存成样本，可以让你区分“提示词没给够信息”“模型没按格式答”“解析器过严”三类问题。很多新手只盯最终异常，结果不断改 prompt，却没有发现 parser 前面拿到的根本不是模型消息。</p>
<p>保留中间值也有助于回归测试。一次线上失败后，可以把脱敏后的 prompt 输出和模型输出变成固定样本，加入 parser 或格式化函数测试。这样下次改链时，即使不调用真实模型，也能验证曾经失败的形状不会再次破坏。LCEL 的每段 Runnable 都可单独 invoke，正是这种测试方式成立的原因。</p>
<p>最后要记住，顺序链的“优雅”来自边界清楚，而不是代码最短。必要的命名、注释、校验和分段不会削弱 LCEL，反而让它从演示代码变成可靠工程结构。</p>

<h2>最后的判断标准</h2>
<p>一条好的 Sequence 应该让读者不用运行代码，也能说清每一步把什么变成什么。如果读者必须跳进函数内部才能知道数据形状，说明链的边界还不够清楚。保持短链可读、长链分段、转换命名、错误可定位，是 LCEL 在生产里长期可维护的关键。</p>
<p>如果链需要交给别人维护，请把每个子链的名字写得像接口说明，而不是临时变量。名字、形状、测试三者对齐，后续替换模型、增加 parser、插入 fallback 时才不会牵一发动全身。LCEL 的真正优势，是让这些改动发生在清晰节点之间。</p>
<p>最后，别把 LCEL 当成只能展示在文档里的短语法。它的价值在于把运行结构变成可复用对象，让评测、观测、重试、并行和分支都能围绕同一条链工作。</p>
<p>因此，写链时请先保证形状清楚，再追求语法漂亮。清晰的链会让后来者敢改，也知道改完该测哪里：先看契约，再看组合；先定位边界，再讨论优化。只要每个节点的职责、名字和输入输出都明确，LCEL 就不是难懂的 DSL，而是一张能运行、能追踪、能测试的数据流图。</p>
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>LCEL 的 | 构造 RunnableSequence，不是立刻执行。</li>
    <li>Sequence 从左到右把上一步输出交给下一步输入，类型契约必须对齐。</li>
    <li>coerce_to_runnable 会把 callable、dict 等提升为 Runnable，其中 dict 表示并行映射。</li>
    <li>RunnableLambda 和 RunnablePassthrough 是修补数据形状的胶水，但要保持 trace 可读。</li>
    <li>链本身仍是 Runnable，所以可以继续并行、分支、重试、fallback 和追踪。</li>
  </ul>
</div>
"""
)


LESSON_14_PARALLEL_BRANCH = (
    r"""
<p class="lead">顺序链解决“先做 A 再做 B”，但真实应用常常需要“同一个输入同时走几条路，再汇合”，或“根据输入选择一条路”。RunnableParallel、RunnableBranch、RunnablePassthrough、RunnableMap / RunnableEach 共同负责这些形状。本课把它们放在 RAG 场景里理解：问题一边送去检索得到 context，一边原样保留为 question，二者合并成 prompt 需要的字典；如果问题类型不同，还可以用 Branch 路由到不同链。</p>

<div class="card analogy">
  <div class="tag">🛣️ 生活类比</div>
  把并行和分支想成<strong>机场行李系统</strong>：同一件行李进入系统后，可以同时被扫描重量、识别目的地、检查安检标签，最后这些结果汇总到登机口；如果标签显示“超大件”，它会被分流到特殊通道。并行不是大家抢同一个箱子乱改，而是每条通道拿到自己的输入副本；分支也不是随便猜路，而是根据清晰、便宜、可重复的规则选择通道。</div>
"""
    + shell.lesson_map(
        "本课地图：扇出、路由、汇合",
        [
            ("Parallel", "同一个输入扇出到多个 Runnable，输出按键汇合成字典", "now"),
            ("Branch", "按谓词选择第一个匹配分支，或走默认分支", "now"),
            ("Passthrough/assign", "保留原输入并在字典上补充字段", "now"),
            ("Map/Each", "把同一 Runnable 应用于列表中的每个元素，理解 batch/map 语义", "source"),
            ("RAG 模式", "retriever + question 并行，prompt 接收 context/question", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>并行和分支都在 Runnable 协议内部实现，因此它们也能 invoke、stream、batch、with_config。源码阅读要注意两个方向：Parallel 是“同输入多输出再合并”，Branch 是“多候选只执行一个”。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "RunnableParallel", "role": "同一输入并发调用多个步骤，结果以字典键汇合", "direction": "上游输入扇出到各子 Runnable"},
            {"file": "libs/core/langchain_core/runnables/branch.py", "symbol": "RunnableBranch", "role": "按条件谓词选择匹配分支，支持默认分支", "direction": "输入先给谓词，再给被选中的 Runnable"},
            {"file": "libs/core/langchain_core/runnables/passthrough.py", "symbol": "RunnablePassthrough", "role": "原样返回输入，并可 assign 新字段", "direction": "保留 question 或原始 dict"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "RunnableMap", "role": "RunnableParallel 的映射形态，强调键到 Runnable 的映射", "direction": "把分支结果收集成 dict"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "RunnableEach", "role": "把单输入 Runnable 应用于输入列表的每一项", "direction": "列表输入逐项调用并收集"},
        ]
    )
    + r"""
<h2>状态流：RAG 中的并行扇出与汇合</h2>
<p>一个典型 RAG chain 需要 prompt 同时拿到 <span class="mono">context</span> 和 <span class="mono">question</span>。检索器会把 question 变成文档列表，Passthrough 会保留原问题。Parallel 把两路汇合成字典，prompt 再按模板变量读取。</p>
"""
    + shell.state_flow(
        [
            ("用户问题进入", "输入是一句自然语言问题，尚未包含 context。", "question = 'RunnableConfig 是什么？'"),
            ("并行扇出", "同一 question 同时送给 retriever 和 passthrough；两边不共享可变状态。", "{'context': retriever, 'question': passthrough}"),
            ("检索分支", "retriever 返回相关文档，通常还要 format_docs 成 prompt 可读文本。", "context = '文档片段...'"),
            ("透传分支", "RunnablePassthrough 返回原 question，避免检索器输出覆盖问题。", "question = 原输入"),
            ("字典汇合", "Parallel 用键名合并结果，prompt 收到完整变量字典。", "{'context': ..., 'question': ...}"),
        ]
    )
    + r"""
<h2>Parallel：并发是实现细节，数据形状才是 API</h2>
<p><span class="mono">RunnableParallel</span> 的公开语义是“同一个输入喂给多个分支，输出组成字典”。它可能用线程、协程或 executor 并发执行，也可能因配置、环境或子组件限制而表现得不完全并行。应用代码不应该依赖“必然同时开始”这种细节，而应该依赖稳定的数据形状：每个键对应一个分支结果，下游 prompt 或函数按键读取。换句话说，Parallel 的 API 是 fan-out/fan-in，不是共享内存并发库。</p>
<p>Parallel 的另一个重要边界是错误传播。任何分支失败，默认会让整个并行结构失败，因为下游需要完整字典。如果检索分支超时而 question 分支成功，prompt 仍然缺少 context。生产系统要么给检索分支加重试或 fallback，要么让分支返回一个明确的空 context 和错误标记，再让下游 prompt 或业务层处理降级。</p>

<h2>Branch：条件路由应便宜、确定、可解释</h2>
<p><span class="mono">RunnableBranch</span> 把 if/elif/else 做成 Runnable。每个候选通常由“谓词 + 目标 Runnable”组成，输入先给谓词，匹配后只执行对应目标。谓词最好是便宜且确定的：例如检查输入字段、语言、用户选择、是否带附件。不要让谓词本身调用昂贵模型又产生随机判断，否则你会把路由变成新的不稳定依赖。Branch 的好 trace 应该能回答：为什么走这条路？哪些条件没有匹配？默认分支是什么？</p>
<p>分支还有一个容易忽略的契约：所有分支最好返回相同输出 schema。如果“中文问题分支”返回字符串，“代码问题分支”返回 dict，“默认分支”返回消息对象，下游就必须写大量类型判断，链的可组合性会下降。分支可以改变执行路径，但不应该让后续步骤无法预测输入形状。</p>

<h2>Passthrough 与 assign：保留输入，再补字段</h2>
<p>顺序链会不断替换当前值，因此保留原始输入是一件需要显式表达的事。<span class="mono">RunnablePassthrough</span> 原样返回输入；<span class="mono">assign</span> 常用于在已有字典上增加新键。例如输入已经是 <span class="mono">{'question': '...'}</span>，你可以 assign 一个 <span class="mono">context</span> 字段，而不是重建整个字典。这个风格让链路更局部：每一步只声明“我要新增什么”，不必复制所有旧字段。</p>
"""
    + shell.trace_table(
        [
            {"step": "1. 输入", "input": "'如何配置 callbacks？'", "action": "Parallel 接收单个 question", "output": "准备扇出"},
            {"step": "2. context 分支", "input": "同一 question", "action": "retriever.invoke 查询文档，format_docs 拼接片段", "output": "context 文本"},
            {"step": "3. question 分支", "input": "同一 question", "action": "RunnablePassthrough.invoke 原样返回", "output": "question 文本"},
            {"step": "4. 汇合", "input": "两个分支结果", "action": "RunnableParallel 按键构造 dict", "output": "{'context': ..., 'question': ...}"},
            {"step": "5. 下游", "input": "完整 dict", "action": "prompt.invoke 读取 context/question 变量", "output": "可发送给模型的消息"},
        ]
    )
    + r"""
<h2>简化源码走读：Parallel 和 Branch 的执行形状</h2>
<p>下面的伪代码把并发调度简化成循环，把回调省略掉。真实实现会处理异步、配置 patch、错误聚合和 streaming。教学重点是：Parallel 执行全部步骤并合并；Branch 只执行第一个匹配目标。</p>
"""
    + shell.code_walkthrough(
        "libs/core/langchain_core/runnables/base.py / branch.py",
        "RunnableParallel / RunnableBranch",
        """class RunnableParallel(Runnable):
    def invoke(self, input, config=None):
        result = {}
        for key, step in self.steps.items():
            result[key] = step.invoke(input, config=config)
        return result

class RunnableBranch(Runnable):
    def invoke(self, input, config=None):
        for predicate, runnable in self.branches:
            if predicate.invoke(input, config=config):
                return runnable.invoke(input, config=config)
        return self.default.invoke(input, config=config)
""",
        "Parallel 的抽象输出是 dict；Branch 的抽象输出来自被选中的单个分支。二者都保持 Runnable 外观，所以能继续接 prompt、model、parser 或 retry。",
    )
    + r"""
<h2>RunnableMap / RunnableEach：映射语义与 batch 语义</h2>
<p><span class="mono">RunnableMap</span> 在很多语境中就是强调“键到 Runnable 的映射”，实际心智模型与 RunnableParallel 接近：同输入、多分支、字典输出。<span class="mono">RunnableEach</span> 则把一个 Runnable 应用于列表里的每个元素。它们都容易被误解成“Python map 一定惰性”或“batch 一定合并成单个 provider 请求”。在 LangChain 里，关键仍是协议：列表中的每个元素都按单次输入契约运行，配置和回调要能区分子调用，结果顺序要能对应输入顺序。</p>
<p>如果每个元素会触发外部副作用，例如写数据库、扣费、发邮件，就不要只因为 RunnableEach 很方便就并发跑。并行适合独立、可重复、无共享可变状态的任务；涉及副作用时，要明确幂等键、事务边界和失败补偿。</p>

<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("parallel 就能共享并修改同一个状态", "Parallel 的心智模型是同输入扇出、结果汇合；共享可变状态会制造竞态。"),
            ("branch 谓词可以很重、很随机", "路由谓词应便宜、确定、可解释，昂贵模型判断要谨慎包装。"),
            ("下游 prompt 会自动补缺失键", "Prompt 需要的 context/question 缺一不可，缺键会在下游模板处失败。"),
            ("所有分支可以返回任意形状", "分支输出 schema 应尽量一致，否则后续链会变成类型判断迷宫。"),
        ]
    )
    + r"""
<h2>小结前的实验</h2>
"""
    + shell.lab_card(
        "设计 RAG 扇出链",
        [
            "画出 {'context': retriever | format_docs, 'question': RunnablePassthrough()} 的输入输出。",
            "让 prompt 故意引用 missing_key，观察错误发生在汇合后还是 prompt 渲染时。",
            "写一个 Branch：如果问题包含代码块走代码解释链，否则走普通问答链，并保证输出 schema 一致。",
            "用 batch 跑三个问题，记录每个子 run 的 tags 或 run_name，确认 trace 能区分它们。",
        ],
    )
    + shell.version_note(
        "RunnableParallel 与 RunnableBranch 的公开语义比内部调度细节更稳定。阅读源码时以 base.py、branch.py、passthrough.py 中的符号为锚点，不要把某一版 executor 实现当成 API 承诺。"
    )
    + r"""

<h2>深入拆解：并行的核心是独立性</h2>
<p>RunnableParallel 让链看起来像“同时做很多事”，但真正决定它是否可靠的不是同时，而是独立。每个分支都应能在不修改共享可变状态的情况下，根据同一输入计算自己的结果。检索分支读取向量库，透传分支保留问题，分类分支判断语言，这些都相对独立；如果两个分支同时写同一张订单表、同时更新同一个缓存键、同时修改同一个 Python 对象，就会把 LCEL 的声明式并行变成竞态条件。并行组合的第一条审查规则就是：分支之间是否有隐式依赖？</p>
<p>独立性还关系到错误处理。一个分支失败是否应该让整体失败？如果 prompt 必须同时拥有 context 和 question，context 缺失就应该失败；如果某个分支只是附加推荐信息，失败也许可以返回空列表并记录降级。RunnableParallel 默认更偏严格，因为下游通常期待完整 dict。生产链可以在单个分支内部做 fallback，把失败局部化，而不是让整个并行结构吞掉错误。</p>
<h3>扇出和汇合的命名设计</h3>
<p>Parallel 输出是 dict，因此键名就是下游契约。键名不要随意取。<span class="mono">context</span>、<span class="mono">question</span>、<span class="mono">language</span>、<span class="mono">citations</span> 这种名字能表达业务含义；<span class="mono">a</span>、<span class="mono">result1</span>、<span class="mono">tmp</span> 会让 prompt 模板和调试信息难读。键名一旦被 prompt、parser 或后续函数依赖，就相当于公共接口，改名需要同步修改下游。</p>
<p>汇合后最好尽快进入一个明确消费这些键的组件，例如 prompt 或命名函数。不要让一个巨大 dict 在很多步骤之间漂流，每一步都偷偷读写几个键。那会让链退化成弱类型状态包，和“config 当业务状态”一样难维护。如果确实需要长时间携带多字段状态，考虑用 LangGraph 的显式 state schema，而不是把 Parallel 输出无限传下去。</p>
<h3>Branch 的谓词设计</h3>
<p>Branch 谓词是路由逻辑，不是业务主体。它应该快、确定、可测试。快，意味着不要每次路由都调用昂贵模型，除非你明确接受成本；确定，意味着同一输入在同一条件下应走同一路径；可测试，意味着你能列出样例验证每个分支会被选中。基于字段存在、用户选择、文件类型、语言标签、模型置信度阈值的谓词通常比较适合。基于自由文本模型判断的谓词也能用，但要给它单独的观测、缓存和失败策略。</p>
<p>Branch 的默认分支不能随便写。没有默认分支时，未匹配输入可能抛出难懂错误；默认分支太宽时，又可能掩盖路由配置错误。推荐把默认分支设计成明确的安全路径：要么返回可解释的“不支持该类型”，要么走保守通用链，并在 metadata 或输出中标注“未命中特定路由”。这样既不让系统无声失败，也不给用户一个看似正常但完全错误的答案。</p>
<h3>RAG fan-out 的完整责任链</h3>
<p>RAG 中的并行结构通常不止两条线。最小版本是 question 透传和 context 检索；稍复杂时还会并行生成查询改写、语言检测、用户画像摘要、权限过滤参数。每加一条分支，都要回答三个问题：它读取什么输入？它输出哪个键？下游如果缺少这个键会怎样？不能回答这些问题，就说明分支边界还没设计清楚。</p>
<p>检索分支尤其需要注意权限和格式。retriever 返回的文档不一定都能直接进入 prompt，可能还要做权限过滤、去重、截断、排序和引用编号。format_docs 不只是把 Document 变成字符串，它也是把检索世界翻译成 prompt 世界的边界。这个边界出错，下游模型可能看到过长、重复、无权限或缺少来源的上下文。把 format_docs 命名为独立 Runnable 或函数，会比把它藏在 lambda 里更容易审查。</p>


<h2>并行结构的测试策略</h2>
<p>测试 RunnableParallel 时，不要只测最终答案。先测汇合字典是否包含下游需要的全部键，再测每个键的值是否符合契约。对于 RAG，至少要断言 context 是字符串或文档列表的约定格式，question 没有被检索器覆盖，引用编号和文档 ID 能对应。很多线上错误不是模型答错，而是 prompt 收到的变量缺失、为空或格式不对。并行汇合处是最适合加测试的边界。</p>
<p>Branch 的测试则要覆盖每个谓词路径和默认路径。每个样例都应说明为什么会走这条路，而不是只断言返回结果。比如“包含代码块的问题走代码解释链”“带 image 字段的输入走多模态链”“都不匹配时走通用问答链”。如果谓词依赖模型分类，就要用假分类器或固定输出测试路由，不要让测试被真实模型随机性影响。路由逻辑越清晰，生产问题越容易复现。</p>
<h2>性能与并发的现实边界</h2>
<p>Parallel 能降低延迟，但不是免费午餐。多个分支可能同时占用模型额度、数据库连接、向量库 QPS、线程池和内存。max_concurrency 可以限制批量和并行压力，但你仍然需要理解外部系统的容量。一个本地 demo 中并行三路很快，到了生产多租户流量下可能触发限流。设计并行链时，要把“理论并发”翻译成“实际依赖能承受的并发”。</p>
<p>并发还会影响观测。多个分支日志交错出现，如果没有 run_id、parent_run_id 和清晰 run_name，就很难拼回时间线。使用 Parallel 时更应该给关键分支命名，例如 retrieve_context、pass_question、classify_intent。这样当某个分支慢或失败时，trace 能直接显示责任，而不是让你在一堆匿名 Runnable 中猜测。</p>
<h2>从 LCEL 过渡到 LangGraph 的信号</h2>
<p>Parallel 和 Branch 能表达很多数据流，但当你开始需要循环、长期状态、多轮人工审批、复杂重入、节点间条件跳转和持久化时，LCEL 可能不再是最合适的层。一个信号是：你开始把一个巨大 dict 当状态在很多 Runnable 之间传来传去，并不断 assign 新字段；另一个信号是：分支结果还要回到前面步骤形成循环。此时 LangGraph 的显式状态、节点和边会更清楚。</p>
<p>这并不意味着 Parallel 和 Branch 只适合简单场景。它们是链式编排中非常重要的中层抽象：比手写并发和 if/else 更可观察，比完整图更轻量。关键是选择合适复杂度。确定的 RAG fan-out、简单意图路由、独立特征并行计算，用 LCEL 很合适；需要可恢复状态机时，再升级到图。好的架构不是只用一种工具，而是在复杂度上逐层递进。</p>

<h2>缺键失败的真实来源</h2>
<p>并行汇合后的缺键错误经常不是 prompt 写错，而是上游约定漂移。检索分支原来叫 context，后来有人改成 documents；透传分支原来返回 question，后来输入变成了包含 question 的 dict，却忘了取字段；assign 原来在字典上补键，后来输入变成字符串，导致无法补。解决这类问题不能只在 prompt 处捕获异常，而要回到汇合边界，给每个键建立清楚契约。</p>
<p>一个实用习惯是在并行结构后加一个轻量校验步骤，确认必要键存在、类型正确、空值可接受。这个步骤可以是命名 RunnableLambda，也可以是业务层校验函数。它不会让模型更聪明，却能让错误更早、更清楚地发生。对 RAG 来说，“没有检索到文档”与“检索分支根本没返回 context”是两种不同情况，前者可以降级回答，后者说明链路坏了。</p>

<h2>并行输出也需要版本意识</h2>
<p>当并行结构被多个 prompt 或下游服务复用时，它的输出字典就像一个小型 API。API 会演进，字段会新增、废弃或改名，因此也需要版本意识。可以在 metadata 中记录链版本，在代码中把构造输入的 Runnable 命名为 build_rag_inputs_v2，或者在校验步骤里明确兼容哪些字段。这样当下游 prompt 仍期待旧字段时，错误会更容易定位。</p>
<p>不要把“再加一个 assign”当成无成本操作。字段越多，下游越可能依赖隐式状态；字段来源越分散，越难判断谁负责生成。对于核心字段，例如 context、question、citations、user_scope，最好集中在一个清晰的构造边界完成，并配上测试。对于临时调试字段，则不要长期留在业务输入里，避免它们被后续步骤误用。</p>
<p>Branch 也有版本问题。新增一个更靠前的谓词，可能会截走原来走默认分支的流量；修改默认分支，可能改变所有未匹配输入的行为。每次调整路由，都应该用一组代表性样本跑一遍，确认路径变化是预期的，而不是悄悄改变产品体验。</p>

<h2>最后的判断标准</h2>
<p>并行和分支的好坏，不看语法是否漂亮，而看输入是否独立、输出是否稳定、失败是否可解释。只要每个分支职责清楚、键名可靠、路由样例覆盖充分，Parallel 和 Branch 就能让复杂数据流保持清晰。</p>
<p>当你不确定该用 Parallel 还是普通函数时，问一句：这些分支是否值得被分别观察、限流、重试和命名？如果值得，就用并行结构；如果只是局部计算，普通函数更简单。</p>
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>RunnableParallel 表达 fan-out/fan-in：同输入多分支，结果按键汇合。</li>
    <li>RunnableBranch 表达条件路由：谓词选择路径，未匹配走默认分支。</li>
    <li>Passthrough 和 assign 用来保留原输入、给字典补字段，是 RAG 链常用胶水。</li>
    <li>并行不是共享可变状态；分支也不应该破坏下游输出 schema。</li>
    <li>RunnableMap / RunnableEach 延续 Runnable 协议，重点是列表与映射的输入输出契约。</li>
  </ul>
</div>
"""
)


LESSON_15_CONFIG_CALLBACKS = (
    r"""
<p class="lead">如果 Runnable 是“怎么执行”的协议，RunnableConfig 和 callbacks 就是“这次执行如何被观察、标记和约束”的协议。一个父 chain 调 prompt、model、parser 时，不只是数据往下传，配置也会往下传：tags、metadata、callbacks、run_name、run_id、max_concurrency 等被标准化、patch、派生成子运行。理解这一课，你就能读懂 LangSmith trace 为什么是一棵树，也能知道哪些信息应该进入 metadata，哪些绝不能写进观测系统。</p>

<div class="card analogy">
  <div class="tag">🎫 生活类比</div>
  把 RunnableConfig 想成<strong>演唱会后台通行证</strong>：通行证上有场次标签、工作人员备注、摄像机编号和进出记录。歌手唱什么歌是业务数据；通行证只决定这场演出如何被记录、谁能跟拍、归到哪个活动。callbacks 就像摄像和场记，负责记录开场、换场、结束和事故，但不应该冲上舞台替歌手改歌词。</div>
"""
    + shell.lesson_map(
        "本课地图：配置、事件、运行树",
        [
            ("ensure_config", "把 None、局部 dict、继承配置标准化成完整 RunnableConfig", "source"),
            ("patch_config", "进入子 Runnable 时追加 run_name、callbacks、tags、metadata 等", "source"),
            ("CallbackManager", "管理 on_chain_start/on_llm_end/on_chain_error 等事件", "now"),
            ("BaseTracer", "把事件组织成 run tree，可被 LangSmith 或本地 tracer 消费", "now"),
            ("观测边界", "callbacks 观察运行，不应承载业务状态或秘密", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>配置和回调的代码分散在 config、callbacks、tracers 与 Runnable 基类之间。请把它们当成一条横切链路：入口标准化配置，父运行创建 callback manager，子 Runnable 派生 child callbacks，tracer 记录 run tree。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/core/langchain_core/runnables/config.py", "symbol": "ensure_config", "role": "补齐默认配置并合并上下文配置", "direction": "Runnable.invoke 开始时调用"},
            {"file": "libs/core/langchain_core/runnables/config.py", "symbol": "patch_config", "role": "为子步骤派生/覆盖 callbacks、tags、metadata、run_name 等", "direction": "父 Runnable 调用子 Runnable 前使用"},
            {"file": "libs/core/langchain_core/callbacks/manager.py", "symbol": "CallbackManager", "role": "分发 start/stream/end/error 等回调事件", "direction": "Runnable 运行时触发事件"},
            {"file": "libs/core/langchain_core/tracers/base.py", "symbol": "BaseTracer", "role": "把回调事件转换成可查询的运行记录与父子关系", "direction": "CallbackManager 调用 tracer 钩子"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable.invoke", "role": "标准执行入口，围绕子类逻辑创建 run 与配置传播", "direction": "用户调用与子 Runnable 嵌套调用"},
        ]
    )
    + r"""
<h2>运行树：父 chain 与三个子 run</h2>
<p>一条 <span class="mono">prompt | model | parser</span> 链在 trace 里通常不是一条扁平日志，而是一棵树。父 run 表示整条链，子 run 表示 prompt、model、parser。这个结构让你能回答“整条请求耗时多少”“模型耗时多少”“解析失败是不是发生在最后一步”“哪些 tags 从父级传下来了”。</p>
"""
    + shell.call_graph(
        [
            ("Parent Chain Run", "run_id=A，tags=['prod','rag']", True),
            ("Prompt Child", "parent=A，渲染模板，记录输入变量", False),
            ("Model Child", "parent=A，记录 token、provider、响应元数据", False),
            ("Parser Child", "parent=A，解析文本，成功或抛出错误", False),
            ("Trace Tree", "BaseTracer 汇总父子关系、时间、错误", True),
        ]
    )
    + r"""
<h2>RunnableConfig 里到底放什么</h2>
<p><span class="mono">RunnableConfig</span> 常见字段包括 callbacks、tags、metadata、run_name、run_id、max_concurrency、recursion_limit、configurable 等。它们的共同特征是“影响运行方式或观测方式”，而不是“成为模型输入的一部分”。tags 适合放 <span class="mono">['prod', 'checkout', 'experiment-a']</span> 这种低敏标记，metadata 适合放请求来源、版本、非敏感业务 ID、模型路由策略等。run_name 让 trace 中步骤更可读，run_id 用于关联一次明确运行。max_concurrency 影响 batch/parallel 调度，recursion_limit 防止递归链或图无限展开。</p>
<p>反过来，用户密码、完整 system prompt、私有文档原文、信用卡号、访问 token 都不应该随手进 metadata。metadata 很容易被发送到日志、tracer、LangSmith 或公司内部观测平台；一旦记录，就会进入更长的保留周期和更广的访问面。观测数据要采用白名单，而不是“把所有上下文都 dump 进去”。</p>

<h2>ensure_config 与 patch_config：父子配置如何连续</h2>
<p><span class="mono">ensure_config</span> 做的是入口标准化：如果用户没传 config，就给一个空但结构完整的配置；如果当前上下文已有配置，就合并；如果字段缺失，就补默认值。这样后续代码不用到处判断 None。<span class="mono">patch_config</span> 做的是局部改写：进入 prompt 子步骤时可以设置 run_name 为 prompt；进入 model 子步骤时可以派生 child callback manager；某一步也可以追加 tags 或 metadata。二者配合，让配置既能继承父级，又能在子级显示自己的身份。</p>

<h2>callbacks：观察事件，而不是改业务数据</h2>
<p>CallbackManager 负责把运行事件分发给 handler。典型事件包括 chain start/end/error、LLM start/new_token/end/error、tool start/end/error、retriever start/end 等。handler 可以打印日志、更新进度条、把事件发送到 LangSmith、统计 token、度量耗时。它们应当是“旁路观察者”：看到输入输出、记录必要信息、在错误时留下证据。不要把关键业务逻辑写在 callback 里，例如“on_chain_end 时扣库存”或“on_llm_new_token 时修改订单状态”。回调可能被禁用、替换、采样或因观测系统故障而失败，业务正确性不能依赖它。</p>
"""
    + shell.trace_table(
        [
            {"step": "1. 父入口", "input": "chain.invoke(input, config={'tags':['demo']})", "action": "ensure_config 标准化配置，CallbackManager 创建父 run", "output": "parent run_id=A"},
            {"step": "2. prompt 子 run", "input": "父 config + run_name='prompt'", "action": "patch_config 派生 child callbacks，触发 on_chain_start/end", "output": "child run parent=A"},
            {"step": "3. model 子 run", "input": "消息 + 继承 tags/metadata", "action": "on_llm_start、on_llm_end 记录模型事件（streaming 时才有 on_llm_new_token）", "output": "AIMessage + token/metadata"},
            {"step": "4. parser 子 run", "input": "AIMessage", "action": "解析成功触发 end；失败触发 error", "output": "结构化结果或异常"},
            {"step": "5. tracer 汇总", "input": "所有事件", "action": "BaseTracer 保存父子关系、时间线、错误", "output": "LangSmith / 本地 trace 中的 run tree"},
        ]
    )
    + r"""
<h2>简化源码走读：配置进入、子配置派生、事件上报</h2>
<p>真实 Runnable.invoke 的实现会比这里复杂得多，尤其要处理泛型、contextvars、schema、streaming、异步和异常。伪代码只保留可观察性主线：标准化配置、创建 manager、触发 start/end/error、给子步骤派生 callbacks。</p>
"""
    + shell.code_walkthrough(
        "libs/core/langchain_core/runnables/base.py + config.py",
        "Runnable.invoke with config/callbacks",
        """def invoke(self, input, config=None):
    config = ensure_config(config)
    manager = CallbackManager.configure(
        config.get("callbacks"),
        tags=config.get("tags"),
        metadata=config.get("metadata"),
    )
    run = manager.on_chain_start(name=self.get_name(), inputs=input)
    try:
        child_config = patch_config(config, callbacks=run.get_child())
        output = self._call_with_config(input, child_config)
    except Exception as exc:
        run.on_chain_error(exc)
        raise
    run.on_chain_end(output)
    return output
""",
        "教学版把许多细节合并了。重点是父 run 与 child callbacks 的关系：子 Runnable 不是另起炉灶，而是挂在同一棵运行树下。",
    )
    + r"""
<h2>LangSmith 与本地日志：边界不同，责任相同</h2>
<p>LangSmith 可以把 run tree、输入输出、token、错误、metadata 可视化，是调试复杂链路的强工具。但是否使用 LangSmith，不改变 callbacks 的边界：观测层收集证据，业务层决定结果。对于生产系统，建议先定义观测白名单：哪些输入可以记录，哪些字段必须脱敏，哪些环境禁用完整 payload，哪些 tags 用于筛选，保留周期多长。否则“为了方便调试”很容易演变成“把所有用户数据永久写到日志”。</p>
<p>本地开发时，callbacks 也要保持克制。打印整个 prompt 可能泄漏系统提示；打印检索文档可能泄漏私有知识库；打印 metadata 可能包含内部账号。更安全的做法是记录哈希、长度、文档 ID、非敏感类别、模型名称、耗时和错误类型。需要复现问题时，再通过受控权限查看原始数据。</p>

<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("config 是业务状态容器", "config 承载运行与观测信息；业务数据应走 input/output、图 state 或数据库。"),
            ("tags 可以当认证权限", "tags 只是观测标签，不能替代鉴权、租户隔离或访问控制。"),
            ("metadata 随便放，反正只给自己看", "metadata 常进入日志和 LangSmith，必须避免秘密与隐私泄漏。"),
            ("callbacks 可以顺便改业务结果", "callbacks 应观察和记录，业务变更应在显式 Runnable、工具或服务层完成。"),
        ]
    )
    + r"""
<h2>小结前的实验</h2>
"""
    + shell.lab_card(
        "画出你的运行树",
        [
            "给 prompt | model | parser 设置 run_name、tags、metadata，运行后在 trace 中确认父子关系。",
            "写一个只记录事件名和耗时的 callback handler，不记录原始 prompt 或用户输入。",
            "故意让 parser 抛错，确认父 run 和子 run 的 error 事件都能定位到解析步骤。",
            "列出 metadata 白名单和禁止字段，解释为什么 tags 不能用于权限判断。",
        ],
    )
    + shell.version_note(
        "RunnableConfig、CallbackManager、BaseTracer 的字段和 handler 细节会随版本演进，但父子 run、配置传播、事件观察这三个概念是 LangChain 可观测性的稳定骨架。"
    )
    + r"""

<h2>深入拆解：可观测性不是事后打印日志</h2>
<p>很多系统在出问题后才补日志，结果只能看到“最终失败”，看不到哪一步失败、输入形状是什么、哪次 fallback 被触发、模型耗时多少。LangChain 把 callbacks 和 run tree 放进 Runnable 协议，是为了让可观测性从一开始就是运行结构的一部分。父链、prompt、model、parser、retriever、tool 都能形成父子 run，事件顺序和耗时天然保留下来。调试复杂链时，这比散落的 print 更可靠。</p>
<p>但可观测性不是越多越好。记录完整 prompt、完整用户输入、完整检索文档确实方便复现，却也可能泄漏系统提示、用户隐私和公司知识库。成熟系统会把观测分成层级：默认记录结构化摘要、耗时、状态码、模型名、token 数、文档 ID；在受控调试环境中临时打开更详细 payload；对生产敏感字段做脱敏、哈希或完全不记录。callbacks 提供能力，治理规则决定用到什么程度。</p>
<h3>run tree 如何帮助定位问题</h3>
<p>一棵好的运行树能把“链失败了”拆成具体证据。prompt 子 run 失败，常见是变量缺失或模板格式错误；model 子 run 失败，可能是 provider、限流、鉴权、上下文过长；parser 子 run 失败，通常是输出格式不符合 schema；retriever 子 run 慢，说明检索后端或网络有瓶颈。没有 run tree，你只能看到外层异常；有 run tree，你能把责任定位到步骤，甚至比较同类步骤在不同请求中的耗时分布。</p>
<p>run tree 还支持产品层面的分析。tags 可以标记环境、功能、实验组；metadata 可以记录非敏感版本号、路由策略、文档集合 ID；run_name 可以让仪表盘按步骤聚合。这样你能问：“实验 A 是否让 parser 错误率上升？”“某个文档集合是否导致检索变慢？”“备用模型被触发的比例是多少？”这些问题不是单次调试，而是持续运营。</p>
<h3>配置传播的边界审查</h3>
<p>每当你准备往 config 里放一个字段，先问：如果这个字段消失，业务结果是否应该变化？如果会变化，它可能不是 config，而是 input 或 state。如果它只是帮助观察、筛选、调度、限制并发，那么 config 合适。这个简单问题能避免很多隐藏依赖。比如 <span class="mono">tenant_id</span> 如果用于权限过滤，就应该进入业务输入并由服务层验证；如果只是用于 trace 聚合，并且已经完成鉴权，可以作为脱敏 metadata 记录。</p>
<p>tags 也要避免语义过载。它们适合做低基数标签，如 <span class="mono">prod</span>、<span class="mono">eval</span>、<span class="mono">rag</span>、<span class="mono">fallback</span>。不要把每个用户 ID、每个订单号都塞进 tags，否则筛选维度会爆炸，还可能造成隐私问题。高基数字段如果确实需要记录，应进入受控 metadata，并经过脱敏或访问控制。</p>
<h3>callbacks 不应改变业务事实</h3>
<p>把业务副作用写进 callback 是一个诱人的捷径：模型结束后顺手写数据库，工具结束后顺手发通知，解析失败后顺手改状态。问题是 callback 的生命周期服务于观测，不服务于事务。它可能因为配置不同而不注册，可能在测试中被替换，可能在观测后端故障时被禁用，也可能被采样。业务事实必须由显式链路步骤、工具或服务层负责，callback 最多记录“某事发生了”。</p>
<p>如果你确实需要根据运行事件触发外部动作，应该把它设计成明确的 Runnable 或业务服务调用，并让它的输入输出、重试、错误处理和权限都可见。然后 callbacks 记录这个动作是否发生，而不是替代动作本身。这个边界能让测试更稳定，也能让审计更清楚：业务代码改变业务，观测代码观察业务。</p>


<h2>观测数据的最小披露原则</h2>
<p>配置和回调最容易在“为了调试”时越界。最小披露原则要求你只记录完成观测目标所需的信息。如果目标是统计延迟，不需要记录完整 prompt；如果目标是分析检索质量，可能只需要文档 ID、分数和集合名；如果目标是排查 parser 错误，可以记录 schema 名称、错误字段和输出长度，而不是完整用户内容。每多记录一个字段，就多一个泄漏面、多一份合规责任、多一个未来需要清理的数据副本。</p>
<p>实践中可以把 metadata 分成三类。第一类是安全低敏字段，例如环境、功能名、版本、模型名、非敏感实验组。第二类是受控字段，例如内部请求 ID、租户哈希、文档集合 ID，需要访问权限和保留周期。第三类是禁止字段，例如密钥、token、密码、完整身份证件、完整私有文档、系统提示原文。把分类写进团队规范，比依赖每个开发者临时判断更可靠。</p>
<h2>回调失败时业务应该怎样</h2>
<p>观测系统也会失败：网络断开、LangSmith 不可用、日志服务限流、handler 自己抛异常。业务链不应该因为非关键观测失败而错误扣款或返回错误答案；但也不应该完全无视观测失败。常见做法是把观测 handler 做成尽量不抛出业务异常的旁路，失败时记录本地告警或指标，同时不改变主链输出。对于强审计场景，则应把审计写入设计成显式业务步骤，而不是普通 callback。</p>
<p>这再次说明 callbacks 的边界：它们适合观察，不适合承诺业务事实。如果某个行业要求“没有审计记录就不能完成交易”，那审计写入必须是交易流程的一部分，有明确输入、输出、重试和失败策略。然后 callback 可以观察审计步骤是否成功。不要把合规要求隐藏在可选 handler 里。</p>
<h2>让 trace 服务于学习和协作</h2>
<p>好的 run tree 不只是排障工具，也是团队沟通工具。新人可以通过 trace 理解一条链包含哪些步骤；产品经理可以看到一次请求为什么慢；安全同学可以检查 metadata 是否越界；评测同学可以对比不同实验组的错误率。为了让 trace 可读，开发者需要主动命名关键节点，保持 tags 体系稳定，避免匿名 lambda 泛滥，避免把无结构大文本塞进 metadata。</p>
<p>在课程学习中，你可以把每条链都当成“会生成运行树的程序”。写完链后，不只看最终答案，还要看 trace 是否解释得清楚：父子关系是否正确，prompt、model、parser 是否分别出现，错误是否落在预期节点，tags 是否继承，metadata 是否安全。如果 trace 自己都看不懂，说明链的结构或命名还需要整理。</p>

<h2>从 trace 反推配置质量</h2>
<p>检查配置设计是否健康，一个简单方法是看 trace。打开一次运行，如果你能从父 run 的 tags 看出环境和功能，从子 run 的名字看出 prompt、model、parser，从 metadata 看出非敏感版本信息和路由策略，说明配置服务了理解。如果 trace 里全是匿名步骤、重复标签、大段不可搜索文本和可疑秘密，说明配置正在变成垃圾抽屉。可观测性需要设计，不是自动发生的。</p>
<p>配置还应支持对比。今天的模型版本、prompt 版本、检索集合、实验组如果没有进入安全 metadata，明天答案质量变化时就很难追溯。相反，如果把每次请求的完整用户资料都写入 metadata，虽然看似更全，却会造成隐私和噪声问题。好的 metadata 是“足以解释运行差异，但不足以泄漏敏感内容”。</p>

<h2>把配置规范写成团队契约</h2>
<p>如果每个开发者随意发明 tags 和 metadata，观测很快会失去可聚合性。今天有人用 prod，明天有人用 production；今天模型版本写 model，明天写 llm；同一个含义多个名字，仪表盘就会变得不可信。团队应该约定固定标签集合、metadata 字段名、脱敏方式和禁止字段，并在代码评审中检查。</p>
<p>配置规范还要考虑环境差异。开发环境可以记录更详细样本，但仍不能记录真实秘密；测试环境应使用假数据验证 trace 形状；生产环境默认最小披露，只在授权排障窗口打开更详细记录。LangChain 提供的是配置通道，具体治理必须由应用团队负责。</p>
<p>当你把这些规范落实后，callbacks 的价值会明显提升。它不再只是“打印点东西”，而是形成稳定的运行证据：哪条链、哪个版本、哪个模型、哪个分支、哪个错误、耗时多少。这样的证据能支持调试、评测、成本控制和安全审计。</p>

<h2>最后的判断标准</h2>
<p>配置和回调的好坏，不看记录了多少字段，而看能否在不泄漏秘密的前提下解释运行。一次失败发生后，你应该能从 trace 看出父子步骤、耗时、错误位置、模型版本和安全 metadata；同时看不到密码、token、完整隐私文本和不该外传的系统提示。达到这个平衡，观测才真正服务工程，而不是制造新风险。</p>
<p>对大型团队来说，可观测字段还应有生命周期：谁能新增字段，谁能查看字段，字段保留多久，何时删除。没有生命周期的日志会越积越多，既增加成本，也增加泄漏风险。把这些规则和 RunnableConfig 一起设计，才能让 tracing 在项目变大后仍然可信。</p>
<p>如果某个字段既影响权限又进入 metadata，要特别小心：权限判断必须在业务层完成，metadata 只能记录已脱敏、已授权的观测副本。把同一个值的业务用途和观测用途分开，是避免越权和泄漏的基本习惯。配置设计越早规范，后期排查和合规成本越低。</p>
<p>安全的观测永远是选择性记录，而不是完整复制运行现场。记录越克制，证据越可信；字段越规范，协作越轻松。观测要帮助定位问题，也要尊重数据边界和用户信任：少记秘密，多记结构，问题才好查。安全观测不是一次性整理，而是长期纪律，它同时保护用户数据、团队效率和系统可信度。</p>
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>RunnableConfig 传播运行控制与观测信息，不承载业务状态。</li>
    <li>ensure_config 标准化入口配置，patch_config 为子 Runnable 派生局部配置。</li>
    <li>callbacks 通过 CallbackManager 分发事件，tracer 把事件组织成 run tree。</li>
    <li>LangSmith 展示的是观测证据，不应成为业务正确性的依赖。</li>
    <li>tags、metadata 要遵守最小披露原则，避免把秘密写进日志和 trace。</li>
  </ul>
</div>
"""
)


LESSON_16_RETRY_FALLBACK = (
    r"""
<p class="lead">生产链路不能假设模型、网络、解析器和 provider 永远成功。LangChain 把健壮性也做成 Runnable 包装：<span class="mono">with_retry</span> 在同一路径上有限重试，<span class="mono">with_fallbacks</span> 在失败后切换到备用 Runnable。本课关注异常如何流动、哪些错误值得重试、fallback 的输入输出形状如何保持一致，以及为什么“修解析器输出”和“换模型 fallback”是两类不同策略。</p>

<div class="card analogy">
  <div class="tag">🧯 生活类比</div>
  把 retry 和 fallback 想成<strong>出行预案</strong>：叫车软件第一次下单失败，可以等几秒重试一次，这是 retry；如果这个平台一直无车，改用地铁或另一个平台，这是 fallback。你不会无限重试一个已经停运的车站，也不会把“地铁票”当成“网约车订单”交给后续报销系统。重试要有限、幂等；备用路线要保持到达目的地的承诺一致。</div>
"""
    + shell.lesson_map(
        "本课地图：从失败到可控降级",
        [
            ("with_retry", "包装 RunnableRetry，对指定异常做有限次数重试", "now"),
            ("with_fallbacks", "包装 RunnableWithFallbacks，主链失败后尝试备用链", "now"),
            ("异常流", "区分可重试、不可重试、应修复、应降级的错误", "now"),
            ("输入输出形状", "fallback 必须能接同样输入，并返回下游可接受的 schema", "source"),
            ("稳健链设计", "provider fallback、parser repair、超时与观测组合", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>重试和 fallback 不是散落在用户代码外面的 try/except，而是 Runnable 自身的包装能力。源码阅读从 Runnable 的方法入口开始，再跳到 retry/fallback 的包装类，看它们如何保持同一协议。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable.with_retry", "role": "返回带重试策略的新 Runnable", "direction": "用户在任意 Runnable 或链上调用"},
            {"file": "libs/core/langchain_core/runnables/retry.py", "symbol": "RunnableRetry", "role": "捕获指定异常，按 stop/wait 策略重复调用 bound Runnable", "direction": "外层包装内层 Runnable.invoke"},
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable.with_fallbacks", "role": "返回带 fallback 列表的新 Runnable", "direction": "主 Runnable 失败后切到备用"},
            {"file": "libs/core/langchain_core/runnables/fallbacks.py", "symbol": "RunnableWithFallbacks", "role": "按顺序尝试主链和 fallback，可把异常注入 exception_key", "direction": "错误驱动下一候选 Runnable"},
            {"file": "libs/core/langchain_core/runnables/config.py", "symbol": "RunnableConfig", "role": "重试/fallback 中继续传播 callbacks、tags、metadata、run_id 等", "direction": "每次尝试仍在可观察运行树中"},
        ]
    )
    + r"""
<h2>状态流：主模型失败，备用模型成功</h2>
<p>稳健链不是把错误藏起来，而是把错误变成可观察、有限、结构一致的流程。下面的例子中，主模型因 provider 超时失败，fallback 模型接收同一输入成功，parser 最终仍返回同一 schema。</p>
"""
    + shell.state_flow(
        [
            ("输入进入稳健链", "用户问题和 config 进入 primary_chain.with_fallbacks([...])。", "input + config"),
            ("主模型尝试", "prompt 成功，primary model 调用 provider 超时并抛出异常。", "TimeoutError"),
            ("异常被记录", "RunnableWithFallbacks 捕获允许处理的异常，callbacks 记录 primary error。", "error event"),
            ("备用模型尝试", "fallback model 用同样 prompt 输入生成 AIMessage。", "AIMessage"),
            ("解析并返回", "parser 校验输出 schema，通过后整条链返回 typed result。", "TypedResult"),
        ]
    )
    + r"""
<h2>Retry：适合短暂、可重复、有限的失败</h2>
<p><span class="mono">with_retry</span> 的核心问题不是“能不能再试一次”，而是“再试一次是否安全且有意义”。网络抖动、429 限流、临时 5xx、provider 短暂超时，通常适合有限退避重试。模板变量缺失、schema 设计错误、权限不足、用户输入不合法，重试一百次也不会变好。工具调用如果会写外部状态，重试前必须确认幂等：同一个请求 ID 重复扣款、重复发邮件、重复创建工单，都是灾难。</p>
<p>好的 retry 策略要有上限、等待策略和异常白名单。上限防止无限等待，等待策略避免立即打爆服务，异常白名单防止把编程错误伪装成暂时失败。重试仍应进入 trace：每次尝试耗时多少、失败原因是什么、最终第几次成功，这些信息对生产排障很关键。</p>

<h2>Fallback：换路线，但不能换契约</h2>
<p><span class="mono">with_fallbacks</span> 表示主 Runnable 失败后按顺序尝试备用 Runnable。最常见是 provider fallback：主模型走 A 厂商，失败后走 B 厂商；也可以是能力降级：结构化输出失败后改用更简单 parser，或高级检索失败后使用缓存摘要。无论哪种，fallback 都必须能接收兼容输入，并返回下游能接受的输出 schema。如果主链返回 <span class="mono">AnswerWithCitations</span>，fallback 只返回纯字符串，下游渲染引用就会崩。稳健性不是“只要有返回就行”，而是“在降级后仍守住契约”。</p>
<p>fallback 也不应该吞掉所有错误。调用者需要知道这次是否走了备用路径，观测系统需要记录主路径失败原因，业务也可能需要在响应中降低置信度或提示“当前使用备用模型”。静默 fallback 会让系统表面成功、内部腐烂：成本、质量和延迟变化都没人知道。</p>

<h2>exception_key 模式：把异常交给备用链</h2>
<p>某些 fallback 需要知道主链为什么失败。<span class="mono">exception_key</span> 模式会把异常对象或异常信息注入输入字典的某个键，让备用 Runnable 根据错误修复。例如 parser 失败后，把原始文本和解析错误交给 repair prompt，让模型按 schema 重写；或者检索失败后，把错误类型写入 metadata，让 fallback 使用缓存。这个模式要求输入必须是字典，因为异常要被加成一个字段；同时要小心不要把完整异常里的秘密、URL、token 或私有内容交给模型。</p>
"""
    + shell.trace_table(
        [
            {"step": "1. primary", "input": "prompt 输出消息", "action": "主模型 invoke，provider 返回 503", "output": "抛出 ServiceUnavailable"},
            {"step": "2. retry 判断", "input": "异常类型", "action": "如果配置了 with_retry 且异常可重试，按退避再试", "output": "成功或最后一次异常"},
            {"step": "3. fallback 捕获", "input": "最后异常", "action": "RunnableWithFallbacks 记录错误，选择第一个备用模型", "output": "备用 run 开始"},
            {"step": "4. fallback 成功", "input": "同一业务输入", "action": "备用模型生成满足 parser 的文本", "output": "AIMessage"},
            {"step": "5. parser", "input": "AIMessage", "action": "校验 schema，返回 typed result", "output": "AnswerWithCitations"},
        ]
    )
    + r"""
<h2>简化源码走读：包装器保持 Runnable 外观</h2>
<p>真实实现使用 tenacity、异步版本、配置 patch、回调 run 和异常过滤。教学版只展示形状：retry 多次调用同一个 bound Runnable；fallback 按候选列表尝试，成功就返回，全部失败才抛出。</p>
"""
    + shell.code_walkthrough(
        "libs/core/langchain_core/runnables/retry.py / fallbacks.py",
        "RunnableRetry / RunnableWithFallbacks",
        """class RunnableRetry(Runnable):
    def invoke(self, input, config=None):
        last_error = None
        for attempt in self.retry_policy:
            try:
                return self.bound.invoke(input, config=config)
            except self.retry_exceptions as exc:
                last_error = exc
                attempt.sleep_before_next_try()
        raise last_error

class RunnableWithFallbacks(Runnable):
    def invoke(self, input, config=None):
        errors = []
        for runnable in [self.primary, *self.fallbacks]:
            try:
                return runnable.invoke(input, config=config)
            except self.exceptions_to_handle as exc:
                errors.append(exc)
                input = self.maybe_add_exception(input, exc)
        raise errors[0]  # 真实实现抛首个被捕获的异常 first_error
""",
        "包装器自己也是 Runnable，所以可以包单个模型、包 parser、包整条 chain，并继续被外层 LCEL 组合。",
    )
    + r"""
<h2>Parser repair 与 provider fallback：别混成一类</h2>
<p>模型调用失败和解析失败是两类问题。Provider 失败时，换模型或重试网络可能有效；解析失败时，provider 其实已经返回了内容，只是内容不满足 schema。此时常见策略是 repair：把原始输出、schema 要求和错误信息交给一个修复链，让它重写为合法结构。repair 仍要有限次数，且要保留 raw output 以便审计。不要把 parser 错误一概交给 provider fallback，否则你可能换了三个模型，却没有告诉模型“具体哪里不符合 schema”。</p>
<p>同样，不要把所有失败都包在最外层 fallback。越靠近失败点，补救策略越精确：模型超时可以包模型，parser 格式错可以包 parser 或 parser 前的修复链，检索超时可以包 retriever。整条链 fallback 适合“大路线切换”，但会牺牲定位精度。</p>

<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("非幂等工具失败就直接 retry", "写外部状态的工具必须有幂等键或补偿机制，否则重试会重复副作用。"),
            ("fallback 成功就不用记录主错误", "主错误必须进入 trace，否则质量、成本和稳定性问题会被静默掩盖。"),
            ("fallback 可以返回任意更简单结果", "备用链也要保持下游需要的输出 schema，降级不能破坏契约。"),
            ("with_retry 会一直试到成功", "重试必须有限、有异常白名单和退避策略，永远成功不是现实承诺。"),
        ]
    )
    + r"""
<h2>小结前的实验</h2>
"""
    + shell.lab_card(
        "为一条链设计失败策略",
        [
            "列出链中可能失败的点：retriever、model、parser、tool，并标注可重试/不可重试。",
            "给模型层设置有限 retry，再给 provider 设置 fallback，确认 trace 中能看到每次尝试。",
            "让 parser 故意失败，比较 parser repair 与 provider fallback 哪个更精确。",
            "检查 fallback 输出 schema 是否与主链完全兼容，并写出不兼容时下游会在哪里崩。",
        ],
    )
    + shell.version_note(
        "with_retry、RunnableRetry、with_fallbacks、RunnableWithFallbacks 的内部策略对象可能随版本变化，但“包装器仍是 Runnable”“失败可观察”“契约不变”是稳定设计原则。"
    )
    + r"""

<h2>深入拆解：失败策略要按失败类型分层</h2>
<p>稳健链的第一步不是加 retry，而是列失败类型。网络超时、限流、provider 5xx 属于临时外部失败；模板变量缺失、schema 不一致、代码 bug 属于确定性内部失败；模型输出格式不对属于可修复但不一定可重试的生成失败；工具副作用失败则要看是否幂等。不同失败类型需要不同策略。把所有异常都交给同一个 retry 包装器，会让临时问题和设计问题混在一起，既浪费时间，也掩盖真正 bug。</p>
<p>分层策略通常更清楚：retriever 自己处理检索超时和缓存降级；model 自己处理 provider retry 和备用模型；parser 自己处理 repair loop；整条 chain 外层只处理少数全局降级。这样 trace 能显示“哪一层做了补救”，而不是只看到最外层兜底成功。越靠近失败点，补救越精确；越靠外层，补救越粗，但覆盖面更广。</p>
<h3>幂等性是 retry 的安全底线</h3>
<p>读操作通常比较适合 retry，因为重复查询最多增加成本和延迟。写操作必须谨慎：创建订单、扣款、发送邮件、写入 CRM、调用真实世界设备，都可能因为重试造成重复副作用。安全 retry 需要幂等键、去重表、事务状态机或外部 API 的幂等支持。例如扣款请求应带 request_id，服务端保证同一 request_id 只扣一次；邮件发送应记录消息 ID，重复尝试只查询或补偿，而不是盲发。</p>
<p>LLM 应用里，工具调用经常被包装成 Runnable 或 Agent tool，因此更容易被统一 retry 误伤。不要在整条 agent chain 外层粗暴 retry 所有异常，否则模型已经成功调用一次工具后，外层重试可能让它再次调用。更安全的做法是对纯模型请求、纯检索请求、纯解析请求分别加策略；对有副作用的工具，设计业务级幂等与确认机制。</p>
<h3>Fallback 的质量与 schema 双重约束</h3>
<p>备用模型或备用链不只是“能返回东西”。它必须在两个维度上兼容主链：质量边界和 schema 边界。质量边界指备用路径是否仍能满足业务承诺，例如是否支持相同语言、上下文长度、工具调用、结构化输出能力；schema 边界指它返回的对象字段、类型、错误语义是否和主链一致。一个便宜小模型也许能回答普通文本，却不能稳定生成带引用的 JSON；把它作为 fallback 前，就要加 parser repair、schema 校验或降低产品承诺。</p>
<p>Fallback 顺序也应表达偏好。第一备用可能是同能力不同 provider，第二备用可能是同 provider 小模型，第三备用可能是缓存摘要或人工转接。每一层降级都应在 trace 和必要的业务输出中留下标记。用户不一定需要看到内部模型名，但系统至少要知道这次答案来自备用路径，后续评估才能解释质量波动。</p>
<h3>Parser repair 是受控再生成</h3>
<p>解析失败时，最差做法是吞掉异常返回空对象；次差做法是无限让同一模型“再试试”。更好的 repair loop 会给出明确反馈：原始输出是什么，schema 要求是什么，错误字段是什么，只允许输出修正后的结构，最多尝试几次。repair 的目标不是让模型重新思考业务答案，而是把已有答案改写为合法格式。因此 repair prompt 应尽量窄，避免引入新的事实或改变含义。</p>
<p>repair 也要保留证据。原始输出、解析错误、修复尝试次数、最终结果都应在安全范围内记录。这样当结构化结果出现问题时，你能判断是主模型理解错、repair 改错，还是 schema 本身不合理。没有这些证据，parser repair 会变成新的黑盒：表面上错误率下降，实际上可能制造静默数据污染。</p>
<h3>不要让稳健性掩盖产品决策</h3>
<p>技术上可以 retry、fallback、repair、降级，但产品上不一定都应该做。有些场景宁愿明确失败，也不应给低置信答案：法律建议、医疗建议、财务交易、权限判断。稳健链的目标不是“永不报错”，而是“在可接受边界内尽量恢复，在不可接受时清楚失败”。因此每个 fallback 都应对应一条产品决策：用户看到什么、系统记录什么、是否需要人工介入、是否允许继续自动执行。</p>
<p>最终，健壮性是一套可解释流程，而不是一个万能装饰器。好的链会告诉你：失败发生在哪里，为什么选择重试，为什么切换备用，备用是否保持 schema，是否影响质量，是否泄漏敏感信息。只要这些问题能回答，with_retry 和 with_fallbacks 就不再是魔法，而是工程化可靠性的积木。</p>


<h2>设计稳健链的检查清单</h2>
<p>第一，列失败点：输入校验、prompt 渲染、retriever、model、parser、tool、数据库、外部 API。第二，给每个失败点分类：临时失败、确定失败、格式失败、权限失败、副作用失败。第三，为每类失败选择策略：有限 retry、provider fallback、parser repair、缓存降级、人工接管或直接失败。第四，定义观测：每次尝试如何命名，错误如何记录，fallback 是否打 tag，最终响应是否标注降级。这个清单比先写 with_retry 更重要。</p>
<p>第五，检查契约：重试前后输出是否等价，fallback 输出是否和主链同 schema，repair 是否会改变业务语义。第六，检查安全：异常信息是否包含密钥或私有内容，exception_key 是否会把敏感堆栈交给模型，metadata 是否记录了不该记录的字段。第七，检查上限：最大重试次数、总超时、最大 repair 次数、fallback 层级都应有限。没有上限的“稳健性”其实是另一种不可控。</p>
<h2>把错误暴露给谁</h2>
<p>同一个错误对不同对象有不同表达。开发者需要完整异常类型和 trace；用户需要可理解的降级说明；业务系统需要结构化状态码；安全审计需要知道是否涉及敏感数据；评测系统需要标记这次样本是否走了 fallback。不要把 provider 的原始堆栈直接展示给用户，也不要只给开发者一个“抱歉失败”。稳健链应该把内部错误翻译成多个层级的输出，各层拿到自己需要的信息。</p>
<p>例如主模型超时、备用模型成功时，用户可以正常得到答案，界面不必显示内部故障；但 metadata 或响应头可以带一个非敏感的 degraded 标记，trace 中记录 primary timeout 和 fallback model。parser repair 成功时，用户看到结构化结果，开发者能看到 raw output 和 repair 次数。全部 fallback 失败时，用户得到明确失败消息，系统保留完整诊断证据。这样既不恐吓用户，也不欺骗自己。</p>
<h2>何时不要 fallback</h2>
<p>不是所有失败都应该 fallback。权限不足不应 fallback 到“无权限也回答”的链；安全策略拦截不应 fallback 到更宽松模型；schema 代表强业务约束时，不应 fallback 到无校验字符串；用户输入缺必填字段时，不应让模型猜。Fallback 的前提是备用路径仍在业务允许范围内。如果备用路径降低了安全、合规或事实要求，就应该明确失败或请求人工处理。</p>
<p>这点在 Agent 和工具场景尤其重要。模型调用失败可以换 provider，但工具权限失败不能换一个绕过权限的工具；解析失败可以 repair，但不能把校验字段删掉；检索失败可以用缓存，但不能返回用户无权访问的缓存内容。稳健性必须服从业务边界。工程上能恢复，不代表产品和安全上允许恢复。</p>

<h2>把稳健性纳入评测</h2>
<p>重试和 fallback 不能只靠线上祈祷，应该进入评测样本。你可以准备 provider 超时、429、parser 非法 JSON、检索空结果、备用模型格式偏差等场景，用假 Runnable 或 monkey patch 模拟失败。评测不只断言最终是否有答案，还要断言尝试次数、fallback 顺序、错误记录和输出 schema。这样才能防止一次重构把稳健策略悄悄绕开。</p>
<p>评测还要覆盖“不可恢复”的场景。权限失败、输入缺必填字段、schema 重大不兼容时，正确行为可能是明确失败，而不是 fallback 成功。把这些样本写进测试，能保护业务边界不被“追求成功率”的代码破坏。稳健链的指标不只是成功率，还包括错误透明度、降级可解释性和安全边界。</p>

<h2>稳健性与用户体验</h2>
<p>用户不关心你用了几次 retry 或哪个 provider fallback，但会感受到延迟、答案质量和失败提示。过多重试可能让页面长时间转圈；过宽 fallback 可能给出质量明显下降的答案；过度暴露错误又会让用户困惑。因此稳健策略要和体验一起设计：什么时候快速失败，什么时候静默降级，什么时候提示“正在使用备用路径”，什么时候转人工。</p>
<p>一个实用做法是给每条链设定总时间预算。预算内可以进行一次短退避重试和一次同能力 fallback；超出预算就返回明确降级结果或请求稍后再试。这样系统不会为了追求成功而无限消耗用户耐心。trace 中记录预算消耗，也能帮助你判断是模型慢、检索慢，还是 fallback 过多。</p>
<p>稳健链最终服务的是可信度。用户可以接受系统偶尔失败，但很难接受系统悄悄给出不可靠结果。有限补救、清晰降级、保持 schema、保留证据，才是 retry 和 fallback 真正要达成的目标。</p>
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>with_retry 适合短暂、可重复、有限的失败，不适合编程错误或非幂等副作用。</li>
    <li>with_fallbacks 是路线切换，备用 Runnable 必须接收兼容输入并返回兼容 schema。</li>
    <li>exception_key 可把异常交给备用链，但要避免泄漏秘密和隐私。</li>
    <li>provider fallback、parser repair、retriever 降级应按失败点精确设计。</li>
    <li>稳健链不是吞错，而是有限补救、清晰观测、可解释降级。</li>
  </ul>
</div>
"""
)
