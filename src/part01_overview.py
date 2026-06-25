"""C-level Part 1: global map for the expanded LangChain visual guide."""

import shell


LESSON_01 = "".join([
r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
LangChain 是什么？一句话：它是把大语言模型接进应用的<strong>编排层</strong>。它帮你统一消息、模型、工具、回调、Agent 循环和图执行，但它不是模型本身，不负责训练，不负责底层推理，也不是向量数据库。第一课先把边界画清楚：知道它做什么，也知道它不做什么，后面读源码才不会把每一层的责任混在一起。
</p>

<div class="card analogy">
  <div class="tag">🧭 生活类比 · 机场调度塔</div>
  把模型想成飞机，向量库想成仓库，工具想成地勤车辆，业务系统想成城市交通。LangChain 像机场调度塔和标准跑道：它不制造飞机，也不替飞机发动机燃烧燃料；它规定无线电格式、排队规则、降落流程和地勤交接方式，让不同航空公司、不同机型、不同地勤系统能在同一套秩序下协作。调度塔强大，但它的权力边界也清楚：跑道上怎么编排归它，飞机怎么训练飞行员、发动机如何推力、仓库如何索引货物，则属于别的层。
</div>

<h2>先定边界：它是编排，不是底层能力</h2>
<p>学习框架最容易犯的错，是把所有“看起来和 AI 有关”的东西都塞到一个名字下面。LangChain 的定位要拆成两句话：第一，它提供<strong>统一接口</strong>，让你用相同的调用方式使用不同模型、工具和运行时；第二，它提供<strong>组合与编排</strong>，把一次模型调用扩展成可以追踪、可以重试、可以调用工具、可以形成 Agent 循环的应用流程。它不训练参数，不部署推理内核，不实现 HNSW 或 IVF 索引，也不替数据库做持久化查询优化。</p>
<p>这条边界非常重要。调试时如果模型回答差，可能是 prompt、检索材料、模型能力或温度参数的问题，不要第一反应怪 LangChain；如果接口换厂商后字段不一致，才更可能落在 provider adapter；如果 Agent 循环无法暂停恢复，就要看 LangGraph 的状态图与 checkpointer。边界越清楚，排错越快。</p>
""",
shell.lesson_map("第一部分的学习路线", [
    ("框架边界", "确认 LangChain 只做应用编排与集成，不替代模型、训练、推理和数据库", "now"),
    ("核心协议", "用 Runnable、BaseMessage、ChatModel、Tool 这些协议统一上层心智", "source"),
    ("调用链", "把一次 invoke 拆成消息标准化、配置合并、回调、provider payload、AIMessage", "after"),
    ("Agent 与图", "理解 create_agent 为什么交给 LangGraph 执行循环、分支、持久化", "after"),
    ("实验方法", "用 fake model 和可观测 trace 训练稳定的源码阅读习惯", "after"),
]),
r"""
<h2>一张调用图：从业务请求到模型、工具和图</h2>
<p>下面的图不是完整源码调用栈，而是你以后读所有章节时都要套用的宏观骨架。用户输入先变成标准消息，模型被统一成 Runnable，工具以 schema 暴露给模型，Agent 循环则由 LangGraph 的状态图管理。每一层都只拥有自己的职责，越界就会导致设计混乱。</p>
""",
shell.call_graph([
    ("你的业务代码", "描述任务、选择模型、绑定工具", True),
    ("LangChain 接口", "Runnable / BaseMessage / init_chat_model", True),
    ("Provider 适配器", "把标准消息翻译成厂商 payload", False),
    ("模型服务", "生成文本或 tool_calls", False),
    ("LangGraph 循环", "有工具请求就执行并回灌，再次调用模型", True),
]),
r"""
<div class="card detail">
  <div class="tag">🔬 源码入口 · 文件 + 符号名</div>
  读源码时不要从搜索“LangChain 是什么”开始，而要从稳定协议进入：谁定义统一形状，谁负责便捷构造，谁负责编排循环。下表给出第一课需要记住的最小入口。
</div>
""",
shell.source_map([
    {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable", "role": "所有可调用组件的统一协议，规定 invoke、stream、batch、config 等行为。", "direction": "上层链、模型、图都依赖它。"},
    {"file": "libs/core/langchain_core/messages/base.py", "symbol": "BaseMessage", "role": "所有 System/Human/AI/Tool 消息的公共基类，承载 content、metadata、id。", "direction": "模型输入输出围绕它标准化。"},
    {"file": "libs/langchain_v1/langchain/chat_models/base.py", "symbol": "init_chat_model", "role": "便捷工厂，根据 provider:model 字符串实例化聊天模型。", "direction": "用户入口向 partner 包分发。"},
    {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "把模型、工具、中间件组装成 Agent 图。", "direction": "高层 API 调用 LangGraph。"},
    {"file": "langchain-ai/langgraph/libs/langgraph/langgraph/graph/state.py", "symbol": "StateGraph", "role": "定义共享状态、节点、边并 compile 成可执行图。", "direction": "Agent 循环的执行底座。"},
]),
r"""
<h2>代码走读：手写模型 + 工具循环</h2>
<p>为了理解 LangChain 在自动化什么，先看一个极简手写循环。它和真实源码不逐行相同，但职责顺序一致：模型先看消息，若返回 tool_calls，程序执行工具，把结果追加为 ToolMessage，再让模型继续。LangChain 的价值不是“发明循环”，而是把循环里的类型转换、schema、回调、错误处理、并行工具、持久化都标准化。</p>
""",
shell.code_walkthrough(
    "conceptual_agent_loop.py",
    "model_tool_loop",
    '''def model_tool_loop(user_text):
    messages = [HumanMessage(user_text)]
    model = init_chat_model("openai:gpt-5.1").bind_tools([get_order_status])

    while True:
        ai = model.invoke(messages)          # 标准消息进入统一模型接口
        messages.append(ai)                  # AIMessage 可能包含 tool_calls
        if not ai.tool_calls:
            return ai.content                # 没有工具请求，循环结束

        for call in ai.tool_calls:
            result = run_tool(call["name"], call["args"])
            messages.append(ToolMessage(result, tool_call_id=call["id"]))''',
    "真实 create_agent 会把这段 while 循环编译成 LangGraph 状态图；这里保留骨架，帮助你看清职责边界。",
),
r"""
<h2>例子追踪：查询订单状态</h2>
<p>假设用户问“订单 A100 现在到哪了”。这个例子小，但包含完整边界：语言理解交给模型，真实订单状态交给业务工具，循环调度交给框架，最终话术仍由模型组织。只看最终输出会误以为模型“知道订单”；看 trace 才知道它只是请求了工具。</p>
""",
shell.trace_table([
    {"step": "1 用户输入", "input": "订单 A100 现在到哪了？", "action": "框架把字符串包装成 HumanMessage，并放入 messages 状态。", "output": "[HumanMessage]"},
    {"step": "2 第一次模型调用", "input": "messages + tool schema", "action": "模型判断需要查业务系统，返回带 get_order_status 的 AIMessage.tool_calls。", "output": "AIMessage(tool_calls=[...])"},
    {"step": "3 工具执行", "input": "order_id=A100", "action": "程序而不是模型调用订单 API，拿到“已到上海分拨中心”。", "output": "ToolMessage"},
    {"step": "4 回灌观察", "input": "原消息 + AIMessage + ToolMessage", "action": "循环把工具结果加入上下文，再次调用模型。", "output": "更新后的 messages"},
    {"step": "5 最终回复", "input": "模型看到工具结果", "action": "模型组织自然语言回答，并且不再请求工具。", "output": "AIMessage(content=...)"},
]),
r"""
<h2>三个边界判断</h2>
<p><strong>第一，模型能力边界。</strong>模型负责语言生成、意图判断和工具选择，但它不能凭空访问你的订单库。凡是涉及真实世界状态、账户余额、库存、文件系统，都必须通过工具或检索系统显式接入。框架提供接口，不提供事实本身。</p>
<p><strong>第二，训练/推理边界。</strong>训练数据、权重更新、GPU kernel、KV cache、量化、张量并行属于模型服务或推理框架。LangChain 最多把请求发过去、把响应拿回来，并在外围做重试、缓存、回调和结构化。</p>
<p><strong>第三，存储/检索边界。</strong>向量数据库负责向量索引、过滤、召回和持久化；LangChain 可以包装 retriever、把文档塞进 prompt、把结果变成上下文，但不等于它本身就是数据库。</p>

<div class="card macro">
  <div class="tag">🧱 抽象的收益与代价</div>
  收益是统一、可替换、可组合和可观测：同一套 Runnable 接口能串模型、解析器、图和工具；同一套消息协议让 provider 差异被隔离。代价是多了一层间接：报错栈更长，默认行为更多，版本变化需要查文档和源码。因此本教程的策略不是“相信抽象”，而是“使用抽象，同时知道抽象背后每一层归谁负责”。
</div>

<h2>从 C 级视角看“框架边界”</h2>
<p>所谓 C-level，不是堆更多 API 名字，而是要求你能把一个问题放回系统边界里解释。比如“订单状态回答错了”这件事，C 级分析不会只说“模型幻觉”，而会先问：订单状态是否来自工具？工具参数是否正确？工具返回是否进入了消息列表？模型是否看到了 ToolMessage？最终回答是否只是对工具结果的语言包装？这些问题把一个模糊输出拆成可定位的层。LangChain 在这里承担的是把层连接起来并留下可观察痕迹，而不是保证底层事实正确。</p>
<p>再比如“换成另一个模型后工具调用格式变了”。如果你知道 LangChain 的边界，就会去查 provider wrapper 如何把标准 tool schema 翻译成厂商格式，而不是修改业务工具本身；如果你知道 LangGraph 的边界，就会区分“模型没有提出工具请求”和“图路由没有执行工具节点”。这种判断力就是本教程后面反复训练的能力：先分层，再追踪，再读源码。</p>
<p>LangChain 的抽象并不意味着你可以不理解底层。恰恰相反，抽象越强，越需要知道它在哪些地方收口，哪些地方故意开放。<span class="mono">Runnable</span> 收口的是调用形状，但不收口业务语义；<span class="mono">BaseMessage</span> 收口的是对话数据结构，但不保证内容真实；<span class="mono">create_agent</span> 收口的是循环编排，但不替你设计安全工具；<span class="mono">StateGraph</span> 收口的是状态更新和节点调度，但不替你决定状态 schema 是否合理。</p>

<h2>什么时候不要先上 LangChain</h2>
<p>边界清楚也意味着知道什么时候不用。一次性脚本只调用一个固定 provider、没有工具、没有 trace、没有模型切换需求时，直接用厂商 SDK 可能更简单。LangChain 适合的是复杂度已经出现或即将出现的地方：多模型切换、消息结构化、工具 schema、回调追踪、流式输出、批量调用、Agent 循环、LangGraph 持久化。不要为了“用了框架”而购买抽象；要在重复胶水代码、可替换性和可观测性开始变得重要时使用它。</p>
<p>反过来，一旦应用进入生产，完全手写胶水也会变贵。你要维护重试、超时、日志、token 统计、工具参数校验、错误转消息、流式 chunk 合并、不同 provider 的 payload 差异。这些代码看起来都不难，但每个都有边界条件，叠在一起就是框架存在的理由。学习 LangChain 的价值不是崇拜框架，而是把这些工程问题系统化。</p>

<h2>本课的阅读姿势</h2>
<p>读后续课程时，请把每个概念都问三遍：它统一了什么？它不负责什么？出了问题应该向上查使用方式，还是向下查实现细节？例如 <span class="mono">init_chat_model</span> 统一的是构造入口，不负责 provider 服务可用性；<span class="mono">@tool</span> 统一的是函数到 schema 的转换，不负责真实副作用安全；callback 统一的是事件观察，不应该承载核心业务决策。能回答这三问，说明你已经从“会用 API”进入“会读系统”。</p>

<h2>边界排错清单</h2>
<p>当一个 LangChain 应用表现异常时，可以按固定清单排查。先看输入边界：用户输入有没有被转换成正确消息，系统消息有没有被误当成人类消息，工具结果有没有以工具消息形式回到上下文。再看模型边界：模型是否真的支持你绑定的工具、结构化输出或多模态块，温度和停止词是否让输出提前结束。然后看工具边界：工具描述是否清楚，参数 schema 是否能表达必填字段，真实执行是否被权限、网络或数据质量影响。最后看图边界：状态是否被 reducer 正确合并，条件边是否把流程送到预期节点，checkpoint 是否使用了正确 thread id。</p>
<p>这份清单的价值在于避免“把所有问题都归因于模型”。模型当然可能回答差，但框架应用更多失败来自边界错配：工具返回了字符串却没有作为 ToolMessage 回灌，retriever 找到了无关文档，config 没把回调传下去，provider wrapper 不支持某个参数，或者业务代码把状态覆盖了。边界排错让每个猜测都能落到一个可验证位置。</p>
<p>从学习角度看，第一课并不是要求你马上读懂所有源码，而是给后续各课提供坐标。遇到消息，想 BaseMessage；遇到模型，想 BaseChatModel 和 provider wrapper；遇到组合，想 Runnable；遇到循环，想 StateGraph；遇到可观测性，想 callbacks 和 config。坐标越稳，新 API 越不容易让你迷路。</p>
<p>最终你要形成一种工程直觉：LangChain 最擅长管理“连接处”。模型与业务工具的连接、统一消息与厂商格式的连接、同步调用与流式事件的连接、一次调用与多步状态图的连接。连接处最容易出错，也最值得框架标准化。把连接处看清楚，你就能判断什么时候应该相信框架默认，什么时候应该下探源码，什么时候应该在自己的业务层再加一道边界。</p>
<p>还有一个很实用的判断：凡是需要长期维护、多人协作、跨环境运行的代码，都应该优先选择清晰边界；凡是一次性、单人、可丢弃的脚本，则可以接受更直接的写法。LangChain 的抽象在前一种场景里价值更大，因为它让不同开发者围绕同一套消息、工具、配置和追踪语言交流。团队里有人负责工具安全，有人负责模型选择，有人负责图状态，有人负责业务体验，如果没有共同协议，每个人都会发明自己的中间格式，系统很快分裂。框架的作用之一，就是给团队提供共同词汇和共同接口。</p>
<p>因此，本课的核心不是让你记住所有名词，而是建立“谁拥有哪一层”的判断。模型拥有生成能力，工具拥有真实动作，业务代码拥有目标和约束，LangChain 拥有编排和标准化，LangGraph 拥有状态图执行。每当你想修改一段代码，先问它属于哪一层；每当你想解释一个 bug，先问证据停在哪一层。这个习惯会贯穿整本教程。</p>
<h2>边界语言训练</h2>
<p>你可以用一句模板训练自己：“某对象负责某种连接，不负责某种底层能力。”例如 LangChain 负责把模型、工具和状态连接起来，不负责训练权重；Runnable 负责统一调用形状，不负责业务正确性；BaseMessage 负责统一对话结构，不负责内容真实性；StateGraph 负责状态流转，不负责节点函数本身是否安全。把这类句子写熟，以后遇到新概念就能快速定位。</p>
<p>这套语言还能减少团队沟通成本。讨论问题时，如果大家都能说清“这是 provider 翻译问题”“这是工具副作用问题”“这是图状态合并问题”，会议就不会停留在“AI 不稳定”。框架学习的成熟标志，是能把模糊抱怨改写成层次明确的工程问题。</p>

<h2>边界不是推卸责任，而是定位责任</h2>
<p>强调 LangChain 不负责训练、推理和数据库，并不是说框架出了问题可以一概外推。相反，边界语言要求你更精确地承担责任：如果 provider payload 被翻译错，责任就在适配层；如果 ToolMessage 没有进入下一轮消息，责任就在编排或业务 glue；如果工具本身返回过期库存，责任在业务数据源；如果模型看到正确工具结果却仍然总结错误，才回到模型生成能力和 prompt 约束。这样的归因比“框架不行”或“模型不行”都更有行动价值。</p>
<p>实际项目中可以把一次故障复盘写成边界表：现象是什么，证据停在哪一层，上一层传入了什么，下一层产出了什么，哪个符号或工具能证明。比如客服 Agent 回复旧订单状态，先看 trace 里是否存在 get_order_status 的 tool call；再看工具参数是不是 A100；再看 ToolMessage 内容是不是旧值；最后才判断模型是否误读工具结果。每一步都有证据，修复也会更小。</p>
<p>这个习惯还能帮助设计安全策略。凡是会产生副作用的动作，例如退款、发邮件、写数据库，都不应只靠模型文字决定。模型可以提出请求，LangChain 可以把请求标准化，业务层仍要做权限、幂等、审计和人工确认。把“建议”和“执行”分成不同边界，是 Agent 系统从 demo 走向生产的关键。</p>
<p>判断是否该引入框架时，也可以用边界数量衡量：只有一个输入和一个输出，直接调用 SDK 往往足够；一旦出现多种消息类型、多种模型、工具副作用、回调审计和状态恢复，边界数量上升，框架提供的统一协议就开始抵消间接层成本。</p>
<p>如果边界数量已经上升，却仍然把所有逻辑写在一个函数里，后续排错会变成猜谜：不知道参数何时被改写，不知道工具是否真的执行，也不知道最终文本来自事实还是补全。先把连接处命名，再决定是否用框架，是比先选技术栈更稳的设计顺序。</p>


<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("LangChain 是一个模型，所以换它就能提升智商。", "它是编排框架；模型能力来自底层 provider，框架只能改善接入、组合和控制。"),
    ("用了 Agent，模型就可以直接执行任何函数。", "模型只提出 tool_calls；真实执行由你的程序控制，这是安全边界。"),
    ("Runnable 只是链式语法糖。", "Runnable 是统一协议，覆盖同步、异步、流式、批量、配置和回调传播。"),
    ("LangGraph 是 LangChain 的另一个名字。", "LangGraph 是图执行与状态管理层；LangChain 的 create_agent 会使用它，但两者职责不同。"),
    ("抽象越多越高级，越少越落后。", "抽象要按复杂度购买；一次简单 API 调用未必需要完整 Agent。"),
]),
r"""
<h2>小实验：亲手分层一个最小客服 Agent</h2>
""",
shell.lab_card("订单状态问答的层归属", [
    "写出用户问题、模型、订单查询函数、最终回复四个元素。",
    "标注哪一项由模型负责，哪一项由业务系统负责，哪一项由 LangChain 编排。",
    "把工具返回改成“订单不存在”，观察应该由工具、循环还是模型负责处理错误。",
    "尝试不用 Agent 手写 while 循环，再对比 create_agent 帮你省下哪些边界代码。",
]),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>LangChain 的核心定位是<strong>应用编排与集成</strong>，不是模型、训练框架、推理服务或向量数据库。</li>
    <li><span class="mono">Runnable</span> 和 <span class="mono">BaseMessage</span> 是统一协议；<span class="mono">init_chat_model</span> 是便捷入口；<span class="mono">create_agent</span> 把循环交给 <span class="mono">StateGraph</span>。</li>
    <li>模型只提出工具请求，真实执行和副作用控制属于你的程序。</li>
    <li>读源码时先找“文件 + 符号名”，再沿调用方向向下追，不要把所有层混成一团。</li>
  </ul>
</div>
""",
shell.version_note("本教程按 LangChain 1.x 时代的包结构和 LangGraph Agent 运行时讲解。0.x 时代的 Chain、AgentExecutor、旧 import 路径仍可能在历史文章中出现；遇到差异时，以当前源码的 Runnable、create_agent、StateGraph 路线为准。"),
])


LESSON_02 = "".join([
r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
LangChain 不是一个单包巨石，而是一组按稳定性和变更速度拆开的包：<span class="mono">langchain-core</span> 放协议地基，<span class="mono">langchain</span> 放高层入口和默认组合，<span class="mono">langgraph</span> 放状态图运行时，<span class="mono">langchain-community</span> 放社区集成，厂商 partner 包放 OpenAI、Anthropic 等易变适配。第二课的目标，是让你看到“为什么包要这样分”，以及换 provider 时爆炸半径为什么能被压小。
</p>

<div class="card analogy">
  <div class="tag">🏙️ 生活类比 · 城市分区</div>
  一座城市不会把宪法、公交调度、临街小店和临时展会都写进同一本规章。宪法稳定，公交调度常更新，商店每天换促销，展会更是随来随走。LangChain 的包结构也是这种分区：核心协议像宪法，主包像市政服务，LangGraph 像交通调度中心，community 和 partner 像各种店铺与外部公司。分区的意义不是让名字变多，而是让变化只发生在该变化的街区。
</div>

<h2>五类包各管一层</h2>
<p>先看层次图。越靠下越稳定，越靠上越贴近使用体验或厂商变化。一个健康的依赖方向应当是上层依赖下层，边缘依赖核心；不能让核心反过来 import 某个具体厂商，否则地基会被边缘拖着走。</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">core</span><span class="name">langchain-core</span></div><div class="ld">协议、基类、消息、Runnable、工具抽象、配置和回调接口。它追求稳定、轻依赖、可被所有包引用。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">main</span><span class="name">langchain</span></div><div class="ld">面向用户的高层入口与默认组合，例如 init_chat_model、create_agent、常用 chains。它依赖 core，并把复杂组合包装成好用 API。</div></div>
  <div class="layer l-graph"><div class="lh"><span class="badge">graph</span><span class="name">langgraph</span></div><div class="ld">有状态图、节点、边、Pregel 执行、checkpoint、中断与人审。Agent 循环越来越多地落在这一层。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">community</span><span class="name">langchain-community</span></div><div class="ld">社区维护或长尾集成，覆盖加载器、工具、向量库、第三方服务。它变化快，不应污染核心地基。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">partners</span><span class="name">langchain-openai / anthropic / ...</span></div><div class="ld">厂商 SDK 适配层，负责认证、参数翻译、payload 组装和响应解析。某个 SDK 升级时，影响应尽量限制在该 partner 包。</div></div>
</div>
""",
shell.lesson_map("本课地图：从包名看责任", [
    ("core", "先识别稳定协议：Runnable、BaseMessage、RunnableConfig、Callback 接口", "now"),
    ("langchain", "再找高层入口：init_chat_model、create_agent 等用户 API", "now"),
    ("langgraph", "理解 Agent 循环为什么需要图执行与状态持久化", "after"),
    ("community", "把长尾集成与核心发布节奏隔离", "source"),
    ("partners", "把厂商 SDK 的变化控制在单独包里", "source"),
]),
r"""
<h2>源码地图：包根就是第一层线索</h2>
<p>读大型仓库时，目录名本身就是架构文档。下面的源码入口不是让你背路径，而是训练一个习惯：看到一个 import，先判断它属于“协议地基、主包便利、图运行时、社区集成、厂商适配”哪一类，再决定应该往上读使用者，还是往下读实现者。</p>
""",
shell.source_map([
    {"file": "libs/core/langchain_core/", "symbol": "package root", "role": "核心协议、消息、Runnable、工具抽象、配置、回调。", "direction": "被 langchain、langgraph、partners 依赖；不应依赖具体厂商。"},
    {"file": "libs/langchain_v1/langchain/", "symbol": "package root", "role": "高层用户 API 与默认组合，例如 chat_models、agents。", "direction": "向下依赖 core、partners、langgraph。"},
    {"file": "langchain-ai/langgraph/libs/langgraph/langgraph/", "symbol": "package root", "role": "状态图、Pregel、checkpoint、中断、控制流。", "direction": "依赖 core 协议，对外提供可执行图。"},
    {"file": "langchain-ai/langchain-community/libs/community/langchain_community/", "symbol": "package root", "role": "社区和长尾集成，范围广、变化快。", "direction": "依赖 core；稳定性弱于 core。"},
    {"file": "libs/partners/openai/langchain_openai/", "symbol": "package root", "role": "OpenAI SDK 适配，参数与响应格式翻译。", "direction": "依赖 core；不应让 core 反向知道它。"},
    {"file": "libs/partners/anthropic/langchain_anthropic/", "symbol": "package root", "role": "Anthropic SDK 适配，处理该厂商的消息和工具调用差异。", "direction": "与其他 partner 平级隔离。"},
]),
r"""
<h2>依赖方向：地基不能认识住户</h2>
<p>包拆分的关键不是“文件夹漂亮”，而是依赖方向可控。一个简单判断：如果删除 OpenAI partner 包，<span class="mono">langchain-core</span> 仍应能被导入；如果删除 core，所有上层都应该崩。这说明 core 是地基，partner 是可替换边缘。</p>
""",
shell.code_walkthrough(
    "architecture_rules.py",
    "dependency_direction",
    '''# 允许：上层依赖稳定地基
langchain -> langchain_core
langchain_openai -> langchain_core
langchain_anthropic -> langchain_core
langchain -> langgraph

# 谨慎：高层可选择性调用具体 partner，但要通过工厂或可选依赖隔离
init_chat_model("openai:gpt-5.1") -> langchain_openai.ChatOpenAI

# 禁止：地基反向依赖边缘
langchain_core -X-> langchain_openai
langchain_core -X-> langchain_community''',
    "真正的依赖声明要读 pyproject.toml；这段伪代码只表达方向原则：稳定层不认识易变层。",
),
r"""
<div class="card detail">
  <div class="tag">🔬 为什么 core 要特别稳定</div>
  <p><span class="mono">langchain-core</span> 里放的是公共契约。契约一旦破坏，受影响的不是一个功能，而是所有实现该契约的模型、工具、retriever、parser、图和用户代码。因此 core 的设计会偏保守：少依赖、少魔法、重向后兼容。相反，partner 包必须跟着厂商 SDK 快速迭代，参数名、认证方式、响应字段都可能变化；把它们拆出去，是为了让“变化快的东西”不要拖垮“变化慢的地基”。</p>
</div>

<h2>Provider 切换追踪</h2>
<p>假设你把模型字符串从 <span class="mono">openai:gpt-5.1</span> 改成 <span class="mono">anthropic:claude-sonnet-4-5</span>。业务代码仍然调用 <span class="mono">model.invoke(messages)</span>，但底层导入、payload 和响应解析会换到另一个 partner 包。下面的 trace 展示爆炸半径如何被限制。</p>
""",
shell.trace_table([
    {"step": "1 用户改配置", "input": "provider:model 字符串", "action": "init_chat_model 解析 provider 前缀。", "output": "选择 openai 或 anthropic adapter"},
    {"step": "2 构造模型", "input": "统一参数 temperature、model、api_key", "action": "主包加载对应 partner 类，如 ChatOpenAI 或 ChatAnthropic。", "output": "BaseChatModel 子类实例"},
    {"step": "3 调用统一接口", "input": "BaseMessage 列表", "action": "上层仍调用 invoke；config、callbacks、stream 等接口不变。", "output": "进入 provider wrapper"},
    {"step": "4 翻译 payload", "input": "标准消息和工具 schema", "action": "partner 包把消息翻译成该厂商 SDK 需要的字段。", "output": "OpenAI/Anthropic 专用请求"},
    {"step": "5 响应归一", "input": "厂商原始响应", "action": "partner 包解析 content、tool_calls、usage，再包装成 AIMessage。", "output": "上层拿到同一种 AIMessage"},
]),
r"""
<h2>community 与 partners 的区别</h2>
<p>很多学习者会把 <span class="mono">langchain-community</span> 和 partner 包混在一起。粗略说，community 是“广而杂”的集成集合，适合长尾工具、加载器、向量库、非核心服务；partner 是“厂商主线适配”，通常围绕某个重要 provider 独立发版、独立依赖、独立维护。两者都属于边缘层，但隔离粒度不同。</p>
<p>为什么不把所有东西都放进 community？因为高频厂商的 SDK 变化会非常频繁，独立 partner 包可以单独升级、单独 pin 版本、单独修 bug。为什么不把所有长尾集成都拆成 partner？因为拆太细会增加维护成本和发现成本。工程设计永远是在稳定性、维护成本、安装体积、发布节奏之间做取舍。</p>

<h2>包边界如何影响日常开发</h2>
<p>包结构不是维护者的内部趣味，它会直接影响你写应用的方式。导入 <span class="mono">langchain_core.messages</span> 的代码，通常是在表达稳定数据契约；导入 <span class="mono">langchain_openai</span> 的代码，通常是在表达“这里接受 OpenAI 的厂商特性”；导入 <span class="mono">langchain_community</span> 的代码，通常要额外关注依赖质量、发布节奏和生产风险。读 import 就能看到耦合边界，这是大型项目里非常实用的信号。</p>
<p>如果你的业务层到处散落 <span class="mono">from openai import OpenAI</span>，换 provider 时就会到处改；如果业务层只接触 <span class="mono">BaseMessage</span>、<span class="mono">Runnable</span> 或你自己封装的薄接口，provider 变化就集中在 adapter。LangChain 的拆包给了你一个参考：稳定契约向内收，易变适配向外放。你自己的项目也可以照这个模式拆分，例如把“客服问答业务规则”与“具体模型供应商”分开。</p>

<h2>读 pyproject.toml 的价值</h2>
<p>架构图可能过期，口头描述可能简化，真实依赖最终要看包声明。<span class="mono">pyproject.toml</span> 告诉你一个包直接依赖谁、哪些依赖是 optional、哪些 extra 会拉入额外 provider。比如用户只安装 core 时，不应被迫安装所有厂商 SDK；安装 <span class="mono">langchain-openai</span> 时，才合理拉入 OpenAI 相关依赖。理解这一点，能解释为什么有时 import 报错并不是框架坏了，而是你没有安装对应 integration 包。</p>
<p>optional dependency 也是控制爆炸半径的工具。一个向量库集成需要某个重依赖，如果它被塞进核心依赖，所有用户都会为少数功能付出安装成本；如果它作为 community 或 extra 存在，只用该功能的人才承担成本。这种取舍背后是“默认路径轻、扩展路径可选”的设计哲学。</p>

<h2>Provider 切换的真实难点</h2>
<p>“换模型只改一行”是目标，不是魔法。统一接口能隐藏大部分调用形状，但不能让所有厂商能力完全相同。有的 provider 支持某种工具调用格式，有的支持多模态内容块，有的 usage 字段更细，有的 streaming chunk 结构不同。partner 包的职责，是尽量把这些差异投影到统一的 <span class="mono">AIMessage</span>、<span class="mono">tool_calls</span>、<span class="mono">response_metadata</span> 上；投影不了的独特能力，则要通过 provider-specific 参数暴露。</p>
<p>因此，写可移植应用时要分清“通用能力”和“厂商专有能力”。通用能力可以依赖 LangChain 抽象，例如消息、工具 schema、invoke/stream；专有能力要隔离在一小块代码里，例如只在构造某个 provider 模型时传特殊参数。这样即使未来切换 provider，你也知道哪些部分可直接迁移，哪些部分需要重新设计。</p>

<h2>community 集成的生产策略</h2>
<p>使用 community 集成并不等于不可靠，但需要更明确的边界。生产项目里可以把 community loader、tool 或 retriever 包在自己的接口后面，固定版本，写最小回归测试，并记录替代方案。这样即使上游集成变动，你的业务层也不会直接暴露在变化下。换句话说，LangChain 用包边界管理生态变化，你的项目也要用模块边界管理上游变化。</p>

<h2>安装体积也是架构问题</h2>
<p>很多初学者只从代码组织理解拆包，却忽略安装体积。一个 AI 应用可能只用 OpenAI 聊天模型，却完全不需要几十个向量库、文档加载器、云服务 SDK 和数据库驱动。如果所有集成都作为默认依赖安装，环境会更慢、更脆弱，也更容易出现版本冲突。拆成 core、main、community、partners 后，用户可以按需安装，生产镜像也更小，依赖审计更容易。</p>
<p>依赖冲突在 AI 生态里尤其常见。某个向量库需要新版 numpy，另一个加载器依赖旧版 pydantic，某个云 SDK 又限制 http 客户端版本。如果这些都绑在核心包上，任何小功能都可能被无关依赖拖垮。把长尾集成放在 community，把主流厂商放在 partner，是把冲突限制在使用者真正选择的功能范围内。</p>

<h2>版本发布节奏的分离</h2>
<p>核心协议的发布节奏应该慢，因为它要保护所有实现者；厂商适配的发布节奏必须快，因为 provider API 会不断增加参数、调整响应、修复流式边界。拆包让这两种节奏可以同时存在。OpenAI wrapper 修一个参数兼容问题，不应要求所有只用 Anthropic 的用户升级；core 增加一个协议字段，也不应被某个厂商 SDK 的临时 bug 阻塞。</p>
<p>这种节奏分离也帮助维护者分工。熟悉某个 provider 的维护者可以专注 partner 包，熟悉图执行的维护者可以专注 LangGraph，熟悉基础协议的维护者可以审慎维护 core。生态越大，越不能靠一个巨型包和一个统一发布节奏解决所有问题。</p>

<h2>从 import 看风险等级</h2>
<p>你可以把 import 当成风险提示。导入 core 类型通常风险较低，因为这些符号是稳定契约；导入 langchain 高层入口风险中等，因为它包装便利但可能随推荐用法演进；导入 community 集成要看维护活跃度和依赖；导入 partner 包要关注对应厂商 SDK 版本。不是说某类 import 好或坏，而是每类 import 暗示不同的升级策略。</p>
<p>在团队项目里，可以制定简单规则：领域层尽量只依赖自己的接口或 core 数据结构；基础设施层负责 partner/community 适配；配置层决定 provider；测试覆盖 adapter 行为。这样项目内部也形成和 LangChain 类似的稳定核心与易变边缘。框架的包结构不仅是被学习对象，也是一种可迁移的工程模式。</p>

<h2>读包结构时常问的四个问题</h2>
<p>第一，这个包定义契约还是实现契约？第二，它的用户是谁，是应用开发者、其他包维护者，还是某个 provider wrapper？第三，它的变化频率应该快还是慢？第四，如果它坏了，影响范围有多大？用这四个问题审视 <span class="mono">langchain-core</span>、<span class="mono">langchain</span>、<span class="mono">langgraph</span>、<span class="mono">community</span> 和 partners，你会发现拆分不是任意命名，而是围绕稳定性和爆炸半径设计的。</p>
<p>这四个问题也能帮助你读提交记录。修改 core 的提交通常需要更谨慎的兼容说明和更广泛的测试；修改 partner 的提交更关注对应厂商行为；修改 community 的提交要看依赖和维护状态；修改 LangGraph 的提交则可能影响 Agent 执行语义。看到变更在哪个包，你就能预估审查重点。大型项目的维护不是平均用力，而是按层级风险分配注意力。</p>
<p>在自己的应用里，建议也保留类似分层。可以有一个稳定的 domain 包定义订单、用户、消息等业务协议；有一个 application 包组织用例；有一个 infrastructure 包放 LangChain、provider、数据库、检索器适配；有一个 experiments 包放临时验证。这样 provider SDK 升级不会穿透到领域层，实验代码也不会污染生产路径。你学 LangChain 包结构，最终是为了把这种边界意识迁移到自己的项目。</p>
<p>最后记住：拆包不是为了让 import 变长，而是为了让责任变短。一个包如果既定义协议、又接真实厂商、又管理图执行、又包含长尾社区工具，它的责任就太长，任何变化都可能牵动全身。LangChain 的多包结构牺牲了一点发现成本，换来安装可选、发布独立、依赖清晰和风险可控。这是工程上非常典型的取舍。</p>
<h2>包结构是一种沟通协议</h2>
<p>仓库维护者用包名向使用者传递预期：core 表示这里应当可靠且通用；partner 表示这里贴近某个厂商；community 表示这里覆盖广但需要使用者判断成熟度；langgraph 表示这里处理图状态和执行。读者尊重这些预期，代码就会更稳。反过来，如果把 partner 的原始响应到处传递，等于绕过了包边界，未来升级时自然痛苦。</p>
<p>学习时也可以把每个 import 标颜色：绿色是稳定协议，蓝色是高层便利，紫色是图运行时，橙色是边缘集成，红色是直接厂商 SDK。颜色越靠边缘，越需要封装和版本固定。这个简单练习能很快暴露项目中不必要的耦合。</p>

<h2>源码路径也要区分仓库与发行包</h2>
<p>读第一部分的 source map 时，要注意“包名”和“源码所在仓库”不是同一个维度。<span class="mono">langchain-core</span>、<span class="mono">langchain</span> 和 partner 包可能在同一主仓中以不同目录存在；<span class="mono">langchain-community</span> 可以作为独立社区来源理解；LangGraph 也有自己的源码路径和发布节奏。引用路径时写清仓库或包来源，是为了避免把一个包里的符号误当成另一个包的内部文件。</p>
<p>这种区分在排查版本问题时特别重要。你本地安装的是 wheel，源码阅读可能看的是 main 分支，文档链接又可能指向某个 tag；三者只要版本不一致，路径和行为就可能出现细微差异。稳妥做法是先记录发行包版本，再找到对应源码 tag，最后用文件 + 符号名描述职责。教学里使用路径是为了建立地图，不是鼓励照抄某个分支的内部实现。</p>
<p>对 community 集成还要多问一个问题：这个集成是核心维护路径，还是长尾贡献路径？如果它只是把第三方服务包装成 loader 或 tool，生产中最好再套一层自己的 adapter。这样未来 community 路径迁移、依赖升级或维护状态变化时，业务代码仍然面对稳定接口。包结构给你的是风险信号，项目结构要把这个信号转化为隔离措施。</p>
<p>团队维护依赖清单时，可以按包层级设置不同升级策略：core 升级前跑协议回归，partner 升级前跑对应 provider 的 payload 和解析测试，community 升级前检查第三方依赖树，LangGraph 升级前跑状态图和 checkpoint 用例。分层不是目录知识，而是升级流程。</p>
<p>如果升级计划无法说明影响哪一层，通常说明边界还没有读清楚，应先补 source map 和最小回归再动版本。</p>
<p>这也解释了为什么课程要写清 source qualifier：同样叫“集成”，来自主仓、community 仓库、partner 包或 LangGraph 仓库，维护节奏和风险完全不同。路径越明确，升级讨论越不容易把多个来源混在一起。</p>

<h2>边界复盘</h2>
<p>本课看似讲仓库目录，实际讲的是变化管理。稳定协议要少变，易变适配要隔离，可选集成要按需安装，图运行时要独立演进。只要记住“谁变化快，谁就不该住在地基里”，很多包结构决策都会变得自然。</p>
<p>再补一个检查：如果一个改动需要同时修改 core、partner、community 和业务代码，通常说明边界设计有问题；理想情况是协议变化才动 core，厂商变化只动 partner，长尾集成变化只动 community，业务需求变化只动应用层。用影响范围反推包边界，是判断架构是否健康的简单方法。</p>

<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("包越少越简单，最好所有集成都进 langchain。", "单包会导致依赖膨胀和发布耦合；拆包是为了控制安装体积与变更半径。"),
    ("core 代码少，所以不重要。", "core 少而关键，它定义所有上层共享的稳定协议。"),
    ("partner 包只是换个 import 名字。", "partner 负责认证、payload、工具调用、流式 chunk、usage 等厂商差异。"),
    ("community 不稳定就不能用。", "community 表示集成范围更广、变化更快；生产中可以 pin 版本并封装边界。"),
    ("依赖方向只是架构图好看。", "依赖方向决定变更传播路径，违反方向会让底层被上层细节污染。"),
]),
r"""
<h2>小实验：画出你项目的包边界</h2>
""",
shell.lab_card("provider SDK 爆炸半径", [
    "选择一个使用 OpenAI 或 Anthropic 的小项目，列出直接 import 厂商 SDK 的文件。",
    "把这些文件按 core/main/provider/business 四类标注，检查业务层是否直接依赖厂商响应字段。",
    "设计一个最薄的 adapter，让业务层只接收统一的 AIMessage-like 数据。",
    "假设厂商 SDK 下周改字段名，写下会受影响的文件清单；目标是只影响 adapter。",
]),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">langchain-core</span> 是稳定协议层；<span class="mono">langchain</span> 是高层入口；<span class="mono">langgraph</span> 是图执行；<span class="mono">community</span> 和 partner 包承接边缘变化。</li>
    <li>依赖方向应从高层到地基、从边缘到核心，不能让 core import 具体 provider。</li>
    <li>provider 切换时，上层仍面对 Runnable 和 AIMessage，变化被压在 partner wrapper 内。</li>
    <li>读大型仓库时，先从包根判断责任，再看 pyproject.toml 确认真实依赖。</li>
  </ul>
</div>
""",
])


LESSON_03 = "".join([
r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
本课只追一行代码：<span class="mono">model.invoke("写一句欢迎语")</span>。看似是一句同步调用，内部会经历输入标准化、消息转换、配置合并、回调生命周期、provider payload 组装、网络请求、响应解析，最后回到一条 <span class="mono">AIMessage</span>。理解这条链路，你以后遇到 streaming、batch、tool calling、Agent trace，都能判断当前卡在第几层。
</p>

<div class="card analogy">
  <div class="tag">📮 生活类比 · 寄一封跨国快递</div>
  你把一句中文写在纸上交给快递员，不代表它原样飞到对方手里。快递公司会把它装进标准信封、贴面单、合并运输配置、扫描揽收和转运节点、交给国际承运商、到目的国再拆包投递。<span class="mono">invoke</span> 也是这样：用户输入只是寄件动作，真正的系统会一路做包装、登记、转运、解析和回执。调试时不能只问“最后回了什么”，还要看每个扫描点是否正常。
</div>
""",
shell.lesson_map("一次 invoke 的六个检查点", [
    ("输入", "字符串、PromptValue、消息列表都先进入统一入口", "now"),
    ("消息", "convert_to_messages 把输入收敛为 BaseMessage 列表", "now"),
    ("配置", "ensure_config 合并 tags、metadata、callbacks、run_id", "source"),
    ("回调", "on_chat_model_start → on_llm_end / on_llm_error 形成可观测生命周期", "source"),
    ("provider", "wrapper 翻译 payload 并调用厂商 SDK", "after"),
    ("输出", "原始响应被解析回 AIMessage", "after"),
]),
r"""
<h2>状态流：同一份请求如何变形</h2>
<p>下面的 state flow 把“写一句欢迎语”沿着调用链拆开。重点不是背函数名，而是记住每一步的输入输出类型。类型一旦错位，错误位置通常也就暴露了：字符串无法变消息，说明卡在标准化；callbacks 没触发，说明 config 或 manager 没传下去；usage 缺失，说明 provider 响应解析没收集到。</p>
""",
shell.state_flow([
    ("用户输入", "你的代码传入一个普通字符串。入口宽，允许字符串、消息、PromptValue。", '"写一句欢迎语"'),
    ("消息标准化", "字符串被包装为 HumanMessage，消息列表成为模型统一输入。", '[HumanMessage(content="写一句欢迎语")]'),
    ("配置合并", "运行时 config 与默认 config 合并，tags、metadata、callbacks、run_name 继续向下传。", 'RunnableConfig'),
    ("回调启动", "CallbackManager 记录一次 chat model run，追踪器、日志器、LangSmith 都可挂在这里。", 'on_chat_model_start'),
    ("厂商请求", "provider wrapper 把标准消息翻译成 OpenAI、Anthropic 或本地模型需要的 payload。", '{messages: ..., model: ...}'),
    ("响应归一", "厂商原始响应被解析成 AIMessage，内容、tool_calls、usage_metadata 回到统一结构。", 'AIMessage(content=...)'),
]),
r"""
<div class="card detail">
  <div class="tag">🔬 源码入口 · 文件 + 符号名</div>
  追 <span class="mono">invoke</span> 时，先从基类看公共流程，再跳到具体 provider 看差异。不要一开始就陷进某个 SDK 的参数海里；先确认统一入口做了哪些事情，哪些事情才交给子类实现。
</div>
""",
shell.source_map([
    {"file": "libs/core/langchain_core/language_models/chat_models.py", "symbol": "BaseChatModel.invoke", "role": "聊天模型统一同步入口，负责把输入收敛到 chat prompt/messages 并调用生成流程。", "direction": "用户调用进入基类公共流程。"},
    {"file": "libs/core/langchain_core/messages/utils.py", "symbol": "convert_to_messages", "role": "把字符串、元组、dict、BaseMessage 等输入转换成标准消息列表。", "direction": "入口标准化依赖它。"},
    {"file": "libs/core/langchain_core/runnables/config.py", "symbol": "ensure_config", "role": "合并和补齐 RunnableConfig，确保 callbacks、tags、metadata 等字段存在。", "direction": "Runnable 调用链向下传播配置。"},
    {"file": "libs/core/langchain_core/callbacks/manager.py", "symbol": "CallbackManagerForLLMRun", "role": "管理 on_llm_new_token / on_llm_end / on_llm_error 等生命周期事件（on_chat_model_start 由 CallbackManager 触发）。", "direction": "模型执行时向观察者发事件。"},
    {"file": "libs/partners/openai/langchain_openai/chat_models/base.py", "symbol": "ChatOpenAI._generate", "role": "OpenAI provider wrapper，把标准消息转 payload 并解析响应。", "direction": "基类模板方法下沉到具体厂商。"},
    {"file": "libs/partners/anthropic/langchain_anthropic/chat_models.py", "symbol": "ChatAnthropic._generate", "role": "Anthropic provider wrapper，处理该厂商的消息块、工具和流式差异。", "direction": "与 OpenAI wrapper 平级替换。"},
]),
r"""
<h2>简化伪代码：invoke 的骨架</h2>
<p>真实源码要处理更多分支：缓存、rate limiter、stream fallback、stop words、structured output、错误包装、异步版本等。这里压缩成一条骨架，帮助你看到“公共流程在基类，厂商差异在子类”的模板方法模式。</p>
""",
shell.code_walkthrough(
    "langchain_core/language_models/chat_models.py",
    "BaseChatModel.invoke",
    '''def invoke(self, input, config=None, *, stop=None, **kwargs):
    config = ensure_config(config)
    messages = convert_to_messages(input)
    callback_manager = CallbackManager.configure(
        inheritable_callbacks=config.get("callbacks"),
        inheritable_tags=config.get("tags"),
        inheritable_metadata=config.get("metadata"),
    )
    run_manager = callback_manager.on_chat_model_start(
        serialized=self.to_json(), messages=[messages]
    )
    try:
        result = self._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
    except BaseException as error:
        run_manager.on_llm_error(error)
        raise
    run_manager.on_llm_end(result)
    return result.generations[0].message  # AIMessage''',
    "这是概念化骨架：函数名与职责对应源码，细节以当前版本实现为准。重点是公共生命周期包住 provider-specific _generate。",
),
r"""
<h2>逐步追踪表：写一句欢迎语</h2>
""",
shell.trace_table([
    {"step": "1 invoke 入口", "input": "字符串", "action": "BaseChatModel 接收 LanguageModelInput，不要求你手写 HumanMessage。", "output": "待标准化输入"},
    {"step": "2 消息转换", "input": "写一句欢迎语", "action": "convert_to_messages/PromptValue 路径把它转成 HumanMessage。", "output": "[HumanMessage]"},
    {"step": "3 配置传播", "input": "config=None 或传入 tags", "action": "ensure_config 补默认值并合并父级 Runnable 配置。", "output": "RunnableConfig"},
    {"step": "4 回调 start", "input": "模型序列化信息 + messages", "action": "CallbackManager 创建 run，通知 tracer。", "output": "run_id / run_manager"},
    {"step": "5 Provider payload", "input": "标准消息", "action": "ChatOpenAI 等 wrapper 转成厂商 role/content、工具、参数字段。", "output": "SDK 请求对象"},
    {"step": "6 响应解析", "input": "厂商原始 JSON/对象", "action": "提取文本、tool_calls、usage、finish_reason。", "output": "ChatGeneration(message=AIMessage)"},
    {"step": "7 回调 end", "input": "LLMResult", "action": "on_llm_end 记录完成；异常时走 on_llm_error。", "output": "可观测 trace"},
    {"step": "8 返回给你", "input": "ChatGeneration", "action": "取第一条 generation.message。", "output": "AIMessage(content='欢迎...')"},
]),
r"""
<h2>为什么先标准化消息，而不是直接发给厂商</h2>
<p>如果上层每个组件都直接理解 OpenAI、Anthropic、本地模型各自的 payload，组合会迅速变成 N×M 的适配矩阵：Prompt 要懂所有厂商，Tool 要懂所有厂商，Agent 要懂所有厂商，Tracer 也要懂所有厂商。LangChain 的做法是先引入标准中间表示：<span class="mono">BaseMessage</span>、<span class="mono">AIMessage</span>、<span class="mono">ToolMessage</span>。上层只认标准消息，provider wrapper 只负责“标准 ↔ 自家格式”的翻译，复杂度从 N×M 降到 N+M。</p>
<p>这也解释了为什么输出统一成 <span class="mono">AIMessage</span>。即使厂商返回结构完全不同，你的下游 parser、Agent、memory、trace table 都可以稳定读取 <span class="mono">content</span>、<span class="mono">tool_calls</span>、<span class="mono">response_metadata</span>。统一输出是可组合性的地基。</p>

<h2>回调生命周期：可观测性从这里插入</h2>
<p>回调不是装饰品。一次模型调用通常至少有 start、end、error 三个关键事件，streaming 时还会有 token/chunk 事件。LangSmith 追踪、日志、计费统计、进度条、调试面板都依赖这些事件。更重要的是，config 里的 callbacks、tags、metadata 必须沿 Runnable 调用链向下传播；如果中间某个自定义 Runnable 吞掉 config，下游 trace 就会断裂。</p>
<p>因此读源码时要特别注意两件事：一是 <span class="mono">ensure_config</span> 和相关 helper 如何合并父子配置；二是每个执行分支是否在异常时调用 error 回调。没有 error 事件的失败很难排查，因为 trace 只显示“开始了”，却不知道在哪里消失。</p>

<h2>Streaming 路径有什么不同</h2>
<p>本课主线是 <span class="mono">invoke</span>，但 streaming 不是“invoke 多次”。流式路径会尽早把 provider 的增量 chunk 转成 <span class="mono">AIMessageChunk</span> 或类似结构，并在每个 token/chunk 到达时触发回调。最终可能再把多个 chunk 合并成完整消息。也就是说，标准化、config 和 callbacks 仍然存在，但响应解析从“一次性解析完整响应”变成“持续解析增量响应”。这就是为什么同一个 provider wrapper 通常既有 <span class="mono">_generate</span> 也有 <span class="mono">_stream</span> 或相关分支。</p>

<h2>用类型判断问题位置</h2>
<p>调用链里每一步都有相对清楚的类型边界。你的输入可以很宽，可能是字符串、消息、PromptValue；进入模型前应该收敛成消息列表；provider 请求前应该变成厂商 payload；返回上层前应该重新包装成 <span class="mono">AIMessage</span>。调试时如果你能写出“当前手里是什么类型、下一步期望什么类型”，就已经完成了一半定位。类型不只是给 IDE 看，它是理解框架边界的最短路径。</p>
<p>例如你在自定义 Runnable 中返回了普通 dict，下游却期待 <span class="mono">BaseMessage</span>，错误可能在组合链中段暴露；如果 provider 原始响应里有 usage，但最终 <span class="mono">AIMessage.usage_metadata</span> 为空，就要查响应解析；如果传了 tags 但 tracer 看不到，就要查 config 是否被中间层丢弃。每个症状都对应一个类型或事件边界。</p>

<h2>Config 不是参数垃圾桶</h2>
<p><span class="mono">RunnableConfig</span> 经常被初学者误解成“随便塞参数的 dict”。更准确地说，它是运行时控制面：tags 用于分类 trace，metadata 用于附加上下文，callbacks 用于观察事件，configurable 用于把可配置字段传给下游，run_name/run_id 用于追踪结构。业务输入仍应放在 input 里，模型参数应放在模型构造或调用 kwargs 中。把所有东西都塞进 config，会让调用边界变得混乱。</p>
<p>配置传播还有继承关系。一个父 Runnable 给了 tags，下游模型调用通常应带着这些 tags；某个子节点可以追加自己的 tags，但不应该无意中清空父级信息。LangChain 的很多 helper 都在处理这种合并语义。读源码时看到 <span class="mono">ensure_config</span>、<span class="mono">merge_configs</span> 或 callback manager configure，要意识到它们维护的是整条调用链的可观测上下文。</p>

<h2>异常路径和正常路径同样重要</h2>
<p>只读成功路径会让你误以为调用链很简单：start、请求、end、返回。真实系统里更关键的是异常路径。provider 网络失败、认证失败、参数非法、工具 schema 不支持、stream 中途断开，都应该触发 error 回调并把异常向上抛出或按策略包装。没有 error 事件，调用就像在黑洞里消失；吞掉异常只返回空文本，更会让上层误判为模型正常回答。</p>
<p>因此实现自定义模型或自定义 Runnable 时，不能只让 happy path 可运行，还要保证 config 和 callbacks 在失败时也被正确处理。最小原则是：开始了就要结束或报错；创建了 run_manager，就要在成功时 on_end，在失败时 on_error。这样 trace 才是一条闭合链路。</p>

<h2>Provider payload 是最后一道翻译</h2>
<p>上层统一消息不代表 provider payload 毫无差异。OpenAI、Anthropic、本地服务对 system message、多模态块、tool choice、response format、stream usage 的表达都可能不同。provider wrapper 负责把统一结构尽量翻译过去，也负责把厂商响应翻译回来。你需要厂商专属能力时，应该在这一层附近寻找参数入口，而不是破坏上层消息协议。</p>
<p>这也是为什么读调用链要从基类到子类。基类回答“所有聊天模型共同经历什么”，子类回答“这个厂商特殊在哪里”。如果直接从子类开始，很容易把厂商细节误当成 LangChain 通用规则；如果只读基类，又会忽略真实 payload 的限制。</p>

<h2>同步、异步、批量的共同骨架</h2>
<p>虽然本课追的是同步 <span class="mono">invoke</span>，但同一套心智也适用于 <span class="mono">ainvoke</span>、<span class="mono">batch</span> 和 <span class="mono">abatch</span>。差别主要在调度方式：异步路径用 await 让事件循环管理并发，批量路径为多个输入重复或优化执行公共流程。输入仍要标准化，config 仍要传播，回调仍要标记每个 run，provider 响应仍要回到统一消息。理解共同骨架后，新方法名只是执行语义的变化，而不是全新的世界观。</p>
<p>这对调试很有帮助。如果单次 invoke 正常、batch 异常，就重点看批量输入和每项 config 是否对齐；如果 invoke 正常、ainvoke 异常，就看异步 provider wrapper 或事件循环；如果 invoke 正常、stream 异常，就看 chunk 解析和 streaming callbacks。先确认共同骨架，再定位分支差异，比盲目重写业务代码更可靠。</p>

<h2>响应解析不只是取 content</h2>
<p>聊天模型返回的 <span class="mono">AIMessage</span> 包含多种信息：自然语言内容、工具调用请求、响应元数据、usage 统计、可能还有安全过滤或 finish reason。很多 demo 只打印 <span class="mono">result.content</span>，容易让人误以为其他字段不重要。Agent 是否继续循环，往往取决于 <span class="mono">tool_calls</span>；成本统计依赖 usage；调试 provider 行为需要 response_metadata。取 content 是展示层动作，不是完整语义。</p>
<p>因此写应用时，建议在边界层保留完整消息对象，只有到最终 UI 或日志摘要时再取 content。过早把 AIMessage 转成字符串，会丢失工具请求、token 用量和 provider 元数据，下游就无法判断模型为什么这样回答。LangChain 统一输出为 AIMessage，正是为了让这些结构化信息继续流动。</p>

<h2>最小 trace 如何手工记录</h2>
<p>即使没有 LangSmith，也可以手工记录一次 invoke：输入类型、标准消息、config tags、provider 名称、是否触发 start、payload 关键字段、原始响应摘要、AIMessage 字段、是否触发 end。记录一两次后，你会发现调用链不再神秘。以后遇到错误，只要看哪一列为空或异常，就能迅速缩小范围。</p>
<p>这张手工 trace 还可以变成团队调试模板。新同事报告“模型不工作”时，不要只要截图；让他填写输入、消息、config、provider、回调、响应字段。模板迫使问题从模糊感受变成结构化事实，也让你能远程判断是环境、配置、provider 还是业务逻辑问题。</p>

<h2>调用链中的所有权</h2>
<p>用户代码拥有业务输入和业务解释，LangChain 基类拥有标准流程，provider wrapper 拥有厂商翻译，callback manager 拥有事件分发，模型服务拥有生成结果。所有权清楚，修改才有方向。想改变业务问题，就改 prompt 或工具；想改变可观测标签，就改 config；想支持厂商新参数，就看 wrapper；想改变 Agent 循环，就看 LangGraph。不要在错误层做补丁。</p>
<p>所有权还决定测试方式。测试业务逻辑时，可以用 fake model 固定输出，避免真实模型干扰；测试 provider wrapper 时，要关注 payload 和响应解析；测试 callback 时，要断言事件顺序和 metadata；测试 streaming 时，要断言 chunk 合并和错误传播。把测试写在正确层，才能避免脆弱测试。比如为了验证欢迎语文案，不应该真的调用 OpenAI；为了验证 OpenAI payload，又不应该只看最终中文回答。</p>
<p>一次 invoke 看似短，实际上是多个所有者协作的结果。输入归一化保护上层体验，配置合并保护组合能力，回调保护可观测性，provider 翻译保护可替换性，AIMessage 保护下游结构化处理。任何一步被绕过，系统仍可能“看起来能跑”，但会丢失某种工程能力。最常见的例子是把模型输出立即转成字符串：短期方便，长期失去工具调用、usage 和元数据。</p>
<p>所以本课不只是背调用顺序，而是训练一种审查习惯：一个自定义组件是否接收并传递 config？是否保留消息对象？是否在异常时触发回调？是否把厂商细节隔离在边界层？这些问题比“代码能不能跑一次”更接近生产质量。</p>
<h2>把 invoke 当成可审计流程</h2>
<p>生产系统里的每次模型调用都应该能回答几个审计问题：谁发起了调用，输入消息是什么，使用了哪个模型和参数，携带哪些标签，是否调用了工具，花费多少 token，失败时错误是什么。LangChain 的消息、config、callbacks 和 AIMessage 字段正是为了让这些问题有位置可放。忽略这些结构，只保存最终文本，会让审计、计费和复盘都变困难。</p>
<p>因此，写模型封装时不要过早隐藏底层信息。可以给业务层提供简洁函数，但内部仍应保留完整消息、metadata、usage 和 trace id。简洁 API 与完整可观测性并不矛盾，关键是把展示层的简洁和运行层的结构化分开。</p>

<h2>读 trace 时先分正常证据和缺失证据</h2>
<p>一次 invoke 的 trace 不只是按时间排序的日志，它还是证据清单。正常证据说明链路经过了某一层，例如出现 on_chat_model_start 说明回调启动了，AIMessage 里有 usage_metadata 说明响应解析至少收到了用量信息；缺失证据同样重要，例如没有 provider payload 记录、没有 error 事件、没有 tool_calls 字段，都在提示某个观察点没有覆盖或某个分支没有执行。调试时要同时看“出现了什么”和“应该出现却没出现什么”。</p>
<p>缺失证据不能立即等同于 bug，也可能只是你没有打开对应 tracer、provider 不返回该字段、或当前路径不是 streaming。比较稳的步骤是先确认观察方式，再确认协议是否承诺该字段，最后才读具体实现。比如某个模型没有 usage，不一定是 LangChain 丢失；可能是 provider 响应本来没有，或 wrapper 只在非流式路径填充。把“没有看到”拆成“没产生、没传递、没记录”三种可能，定位会更准确。</p>
<p>在团队里复盘调用链时，建议把 trace 表和源码入口放在一起。trace 告诉你事实顺序，源码告诉你责任位置。只有 trace 没有源码，容易停留在现象；只有源码没有 trace，容易证明了一条没有实际发生的路径。两者配合，才知道当前请求到底走过哪条分支。</p>
<p>还有一个边界技巧：先记录框架标准对象，再记录厂商对象。前者回答 LangChain 看到了什么，后者回答 provider 收到了什么。两者不一致，问题在翻译层；两者一致但输出异常，才继续查模型服务或业务约束。</p>
<p>记录 trace 时也要避免只保存成功摘要。把失败输入、异常类型、回调事件和最后一个已知状态一起留下，下一次复现时才能比较差异。没有失败证据的“偶发问题”，通常会退化成重复试 prompt。</p>

<h2>链路复盘</h2>
<p>一次调用的每个环节都在保护一种工程能力：消息标准化保护可替换性，配置合并保护组合性，回调保护可观测性，provider 翻译保护生态适配，AIMessage 保护下游结构化处理。少看任何一环，都会低估 invoke 的设计含义。</p>
<p>再补一个检查：如果你无法说清某个字段是在输入标准化、配置传播、回调事件、provider payload 还是响应解析中产生的，就不要急着修。先把字段放回链路位置，再看它由谁创建、谁读取、谁应该保持稳定。链路定位先于代码修改。</p><p>最后确认：一次调用必须能解释输入、配置、事件、请求、响应五类证据，缺一类就补观察点。</p>

<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("invoke 只是把字符串直接发给 API。", "它先标准化输入、合并配置、启动回调，再进入 provider wrapper。"),
    ("config 只影响当前函数，不会继续传。", "RunnableConfig 的价值就在于 tags、metadata、callbacks 能沿组合链传播。"),
    ("回调只用于打印日志。", "回调承载 tracing、计费、调试、stream token、错误生命周期等可观测能力。"),
    ("输出 content 是字符串，所以返回值就是字符串。", "聊天模型返回 AIMessage；content 只是其中一个字段，tool_calls 和 metadata 同样重要。"),
    ("所有 provider 的 invoke 源码都一样。", "公共骨架相似，payload 翻译、流式 chunk、工具调用解析在 wrapper 中不同。"),
]),
r"""
<h2>小实验：给 invoke 加一个可观测标签</h2>
""",
shell.lab_card("追踪一次欢迎语调用", [
    "调用 model.invoke('写一句欢迎语', config={'tags': ['lesson03'], 'metadata': {'case': 'welcome'}})。",
    "在 tracer 或日志里确认 start 事件能看到输入消息和 tags。",
    "故意传入错误 API key 或非法模型名，观察 error 事件是否记录异常。",
    "把 invoke 改成 stream，比较 end 事件之前是否多了 chunk/token 事件。",
]),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">model.invoke("写一句欢迎语")</span> 会经历输入标准化、消息转换、config 合并、callbacks、provider payload、响应解析。</li>
    <li>标准消息是中间表示，让上层逻辑不依赖具体厂商字段。</li>
    <li>回调生命周期是可观测性的插入口，config 传播断裂会导致 trace 断裂。</li>
    <li>streaming 与 invoke 共用很多前置步骤，但响应解析和回调事件变成增量式。</li>
  </ul>
</div>
""",
])


LESSON_04 = "".join([
r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
读 LangChain 源码不要从全仓搜索开始，也不要随机点进最深的 provider 实现。正确路线是四步：先找公共 API，确认用户从哪里进入；再找协议或基类，理解稳定契约；然后找一个具体实现，看变化点如何落地；最后读测试和示例，确认真实用法与边界条件。本课给你一张源码阅读地图，让你能带着“文件 + 符号名”的证据解释每个结论。
</p>

<div class="card analogy">
  <div class="tag">🕵️ 生活类比 · 查案卷宗</div>
  源码阅读像查案。公共 API 是报警电话，告诉你案件从哪里进入；基类和协议是法律条文，说明什么行为被允许；具体实现是现场记录，展示某个厂商如何执行；测试和示例是判例，告诉你维护者认为哪些情况必须成立。只看现场会迷路，只看法律会空泛，只看博客又缺证据。合格的源码结论必须能回到案卷：哪个文件、哪个符号、哪条测试支撑了它。
</div>
""",
shell.lesson_map("源码阅读四站法", [
    ("Public API", "从 init_chat_model、tool、create_agent 这种用户入口开始", "now"),
    ("Protocol/Base", "找 Runnable、BaseChatModel、BaseTool、StateGraph 等稳定契约", "now"),
    ("Concrete", "选一个 provider 或 graph 实现，看差异如何接入契约", "source"),
    ("Tests/Examples", "用测试确认边界、异常、兼容用法，而不是只相信直觉", "after"),
    ("Citation", "每个结论写成文件 + 符号名，方便复查和迁移", "after"),
]),
r"""
<h2>源码入口地图</h2>
<p>下面这张表是第一轮阅读最常用的导航。它覆盖高层入口、协议基类、工具装饰器、Agent 工厂、图构建器和执行引擎。不要把表当成死记硬背；把它当成“问路牌”：当你想知道某个功能为什么这样设计，就从对应符号进入，再顺着调用方向走。</p>
""",
shell.source_map([
    {"file": "libs/langchain_v1/langchain/chat_models/base.py", "symbol": "init_chat_model", "role": "聊天模型便捷工厂，解析 provider:model 并延迟/直接实例化模型。", "direction": "Public API -> partner implementation"},
    {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable", "role": "统一可运行协议，规定 invoke、stream、batch、with_config、pipe 等组合行为。", "direction": "Protocol -> every runnable component"},
    {"file": "libs/core/langchain_core/tools/convert.py", "symbol": "tool", "role": "把普通函数转换成 StructuredTool/BaseTool，生成 schema 与描述。", "direction": "Decorator -> tool object"},
    {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "高层 Agent 工厂，组装模型、工具、中间件并产出图。", "direction": "Public API -> LangGraph"},
    {"file": "langchain-ai/langgraph/libs/langgraph/langgraph/graph/state.py", "symbol": "StateGraph", "role": "状态图构建器，定义 schema、节点、边、reducer，并 compile。", "direction": "Graph builder -> compiled graph"},
    {"file": "langchain-ai/langgraph/libs/langgraph/langgraph/pregel/main.py", "symbol": "Pregel", "role": "执行引擎基类，负责按 superstep 调度节点、channel 更新和流式事件。", "direction": "Runtime engine -> node execution"},
]),
r"""
<h2>算法：带问题读源码，而不是漫游</h2>
<p>源码仓库很大，漫游式阅读会让你在 import 和类型分支里耗尽耐心。每次阅读都要先写一个问题，例如“@tool 如何从函数签名生成 schema？”或“create_agent 为什么返回 Runnable？”然后按固定算法收集证据。</p>
""",
shell.code_walkthrough(
    "reading_algorithm.md",
    "source_reading_route",
    '''question = "@tool 如何从函数签名生成 schema？"

entry = find_public_api(question)          # langchain_core.tools.tool
contract = find_protocol_or_base(entry)    # BaseTool / StructuredTool / Runnable
implementation = choose_concrete_path()    # from_function / pydantic schema creation
tests = search_tests_by_symbol("tool")    # tests show supported signatures and errors

notes = cite([
    ("libs/core/langchain_core/tools/convert.py", "tool"),
    ("libs/core/langchain_core/tools/structured.py", "StructuredTool.from_function"),
    ("libs/core/tests/unit_tests/test_tools.py", "test_*"),
])

answer = explain_with_boundaries(notes)''',
    "关键是先提出问题，再收集入口、契约、实现、测试四类证据；否则读到哪里都像重点。",
),
r"""
<div class="card detail">
  <div class="tag">🔬 文件 + 符号名的引用习惯</div>
  <p>不要写“源码里好像是这么做的”。写成“<span class="mono">libs/core/langchain_core/tools/convert.py :: tool</span> 负责装饰器入口；<span class="mono">StructuredTool.from_function</span> 负责从函数生成工具对象”。这种引用不需要行号也能复查，因为符号名比行号更稳定。只有在做代码审查或补丁时，才需要精确到行。</p>
</div>

<h2>@tool 走读：从函数到工具对象</h2>
<p>下面追踪一个最常见的路径。用户写普通函数，装饰器读取函数名、docstring、类型注解，生成 schema，最后得到一个可被模型看到、也可被程序执行的工具对象。这个例子体现了“公共 API → 协议对象 → 具体实现 → 测试边界”的完整路线。</p>
""",
shell.trace_table([
    {"step": "1 用户函数", "input": "def get_weather(city: str) -> str", "action": "函数名、签名、docstring 成为单一事实来源。", "output": "Python callable"},
    {"step": "2 装饰器入口", "input": "@tool", "action": "tool 判断是否直接装饰、是否传入 name/args_schema/infer_schema。", "output": "转换流程参数"},
    {"step": "3 schema 推断", "input": "类型注解与 docstring", "action": "从函数签名构建 pydantic/JSON Schema，供模型理解参数。", "output": "args_schema / JSON schema"},
    {"step": "4 工具对象", "input": "callable + schema + description", "action": "StructuredTool.from_function 封装执行入口与元数据。", "output": "BaseTool/StructuredTool"},
    {"step": "5 Agent 使用", "input": "tools=[get_weather]", "action": "create_agent/model binding 把 schema 暴露给模型，并在 tool_calls 出现时执行。", "output": "可调用工具链路"},
]),
r"""
<h2>@tool 简化代码</h2>
""",
shell.code_walkthrough(
    "langchain_core/tools/convert.py",
    "tool",
    '''def tool(name_or_callable=None, *, args_schema=None, infer_schema=True, ...):
    def _create_tool_factory(tool_name):
        def _tool_factory(dec_func):
            if infer_schema or args_schema is not None:
                return StructuredTool.from_function(
                    dec_func,
                    name=tool_name,
                    args_schema=args_schema,
                    infer_schema=infer_schema,
                    parse_docstring=parse_docstring,
                )
            return Tool(name=tool_name, func=dec_func, description=description)
        return _tool_factory

    if callable(name_or_callable):
        return _create_tool_factory(name_or_callable.__name__)(name_or_callable)
    return _create_tool_factory(name_or_callable)''',
    "这是压缩版路径：真实实现处理 async、response_format、错误提示等分支；阅读时先抓主干，再补边界。",
),
r"""
<h2>测试和示例为什么重要</h2>
<p>基类告诉你“应该怎样”，实现告诉你“某条路径怎样”，测试告诉你“维护者承诺哪些情况不能坏”。例如 <span class="mono">@tool</span> 的测试会覆盖无 docstring、显式 args_schema、解析 Google 风格 docstring、错误参数等情况。读这些测试比读随机博客可靠，因为它们随仓库一起演进，失败就会阻止合并。</p>
<p>示例则告诉你公共 API 希望怎样被使用。有时源码支持一个内部参数，并不代表它是推荐用法；示例和文档出现频繁的路径才是 happy path。读源码时要区分“技术上可行”和“维护者希望你这样用”。</p>

<h2>Provider 差异怎么定位</h2>
<p>当两个厂商行为不同，不要在业务代码里猜。先确认公共协议是否相同：都继承/实现同一类模型接口吗？然后比较 partner wrapper 的同名方法，例如 <span class="mono">_generate</span>、<span class="mono">_stream</span>、bind_tools 相关方法。最后找各自测试，尤其是 tool calling、stream usage、multimodal content 这些厂商差异高发点。这样你能把问题定位为“协议设计差异”“某个 provider adapter 缺功能”还是“业务使用了厂商专属字段”。</p>

<h2>公共 API 不是实现边界</h2>
<p>很多 public API 的目标是降低使用门槛，所以它会隐藏很多分支。<span class="mono">init_chat_model</span> 看起来只是解析一个字符串，背后却涉及 provider 推断、可选依赖、延迟初始化、具体模型类选择；<span class="mono">create_agent</span> 看起来只是接收 model 和 tools，背后会构造状态、节点、边、中间件和工具执行路径。读 public API 时要问：它为了用户体验隐藏了哪些复杂度？这些复杂度分别交给哪些下层符号？</p>
<p>因此，公共入口只回答“用户从哪里进来”，不能单独回答“系统如何工作”。下一步必须找协议或基类。协议告诉你哪些行为是所有实现必须满足的，例如 Runnable 必须能 invoke，BaseTool 必须有 name、description、args_schema 和执行入口，StateGraph 的节点要读写状态。协议层是判断实现是否合规的尺子。</p>

<h2>具体实现要选代表路径</h2>
<p>大型项目里同一协议可能有几十个实现。阅读时不要平均用力，而要选一条代表路径。学聊天模型，可以先选 OpenAI 或 fake model；学工具，可以先选 <span class="mono">StructuredTool.from_function</span>；学图执行，可以先选一个最小 StateGraph 编译到 Pregel 的路径。代表路径读通后，再比较第二个实现，差异会非常清楚。</p>
<p>比较实现时，最好使用同一问题。比如都问“它如何处理流式输出”，就分别看两个 provider 的 stream 分支；都问“它如何生成工具 schema”，就比较显式 args_schema 和类型推断路径。问题一致，差异才有意义。随机在两个文件之间跳，只会得到一堆不成体系的细节。</p>

<h2>测试能帮你发现隐藏边界</h2>
<p>源码里的 if 分支不一定都容易理解，但测试往往会告诉你为什么存在。一个错误提示测试说明维护者在乎用户如何失败；一个兼容旧输入格式的测试说明历史 API 仍需支持；一个 provider-specific 测试说明该厂商有独特行为。读测试时要特别关注名称、输入、断言和失败信息，它们合起来就是行为边界。</p>
<p>示例和集成测试还会展示组合方式。某个类也许有很多参数，但官方示例只使用其中少数几个，这通常暗示 happy path。教学和生产代码应优先沿 happy path 写，除非你明确需要扩展点。偏离 happy path 时，更要给自己的封装加测试，因为你已经走进维护者较少覆盖的区域。</p>

<h2>如何整理源码笔记</h2>
<p>建议每张源码笔记固定五栏：问题、公共入口、协议/基类、代表实现、测试/示例。每栏只写文件 + 符号名和一句职责，不要复制大段源码。复制源码会让笔记很快过期，职责说明和符号引用更容易迁移。遇到版本升级时，只要重新确认符号是否存在、职责是否变化即可。</p>
<p>最后给结论加边界词：通常、当前版本、对这个 provider、在这个测试覆盖下。边界词不是让结论变弱，而是让结论诚实。源码阅读的专业性不在于说得绝对，而在于知道证据支持到哪里。</p>

<h2>不要忽略反向阅读</h2>
<p>正向路线从 public API 往下走，反向路线从错误或测试往上走。遇到报错信息时，先搜索报错文本，找到抛出异常的符号，再向上看谁调用它；遇到一个测试失败，先读测试断言，再读被测函数，再回到 public API。反向阅读能帮助你定位边界条件，因为错误路径往往不会出现在 happy path 示例里。</p>
<p>例如工具 docstring 解析失败时，报错文本可能直接指向 schema 推断函数。此时没必要从 create_agent 重新读一遍，而应从异常源头向上追：谁要求 parse_docstring，谁传入函数签名，谁把错误展示给用户。正向和反向结合，源码阅读才完整。</p>

<h2>源码阅读中的版本意识</h2>
<p>LangChain 生态经历过多次 API 迁移，网上文章常常混杂旧路径。看到 <span class="mono">AgentExecutor</span>、旧 Chain 或旧 import 时，不要立即照抄，要先问当前版本推荐入口是什么。源码里的 deprecation message、迁移文档和新测试比旧博客更可信。用文件 + 符号名记录当前版本，能避免把历史实现误当成现在设计。</p>
<p>版本意识还包括分支意识。main 分支可能领先已发布版本，你本地安装的包可能落后。读源码解释本地行为时，最好确认包版本和源码版本是否一致。教学中引用符号名而非行号，也是为了在版本变化中保留可迁移的坐标。</p>

<h2>从文档跳到源码</h2>
<p>官方文档适合建立意图，源码适合确认机制。读文档时可以把每个关键名词圈出来：Runnable、tool、create_agent、StateGraph、checkpointer。然后在源码中搜索这些符号，确认它们是函数、类、协议还是配置项。这样文档和源码互相校验：文档告诉你为什么这样用，源码告诉你实际怎样执行。</p>
<p>如果文档和源码看起来不一致，先不要下结论。可能是版本不同，可能是文档省略了分支，也可能是你读到了内部 helper。用测试和示例做第三方证据：维护者真正保证的行为，一般会出现在测试中。三方证据一致时，结论才稳。</p>

<h2>给团队讲源码的方式</h2>
<p>向别人解释源码时，不要直播滚动文件。先画四站路线，再展示最少的符号。比如讲 <span class="mono">@tool</span>：入口是 convert.py :: tool，协议对象是 BaseTool/StructuredTool，实现关键是 from_function，测试覆盖签名和 docstring。每个符号只讲职责和调用方向。听众先获得地图，再决定是否下钻细节。</p>
<p>这种讲法也能提升代码审查质量。审查一个修改时，问它是否改变 public API、是否破坏协议、是否只影响某个实现、是否有测试覆盖边界。源码地图不只是学习工具，也是评估变更风险的工具。</p>
<p>源码阅读还要避免“把实现细节变成公共承诺”。某个内部 helper 当前这样写，不代表你应该依赖它；某个未文档化参数存在，不代表未来不会变化。判断一个符号的稳定性，要看它是否在 public API 中出现，是否被测试覆盖，是否在文档或示例中推荐，是否属于 core 协议。越靠内部、越少测试、越少文档，越应该把它当作实现细节而非契约。</p>
<p>反过来，真正的公共契约需要更严肃地阅读。Runnable、BaseMessage、BaseTool、StateGraph 这类符号影响范围广，它们的参数、返回值和错误语义值得细读。读这些符号时，不仅看代码，还要看注释、类型、测试和迁移说明。公共契约是框架给生态的承诺，理解承诺比记住某个 private 函数更重要。</p>
<p>当你能区分公共承诺和内部细节，就能更安全地扩展框架。需要定制时，优先使用公开扩展点，例如自定义 Runnable、自定义 BaseTool、Graph 节点、middleware、callbacks；不要复制内部函数再改。复制内部源码看似快，版本升级时最痛苦。沿公开扩展点写代码，才是源码阅读转化为工程能力的标志。</p>
<h2>源码阅读的最小交付物</h2>
<p>一次合格的源码阅读，最小交付物不是“我看完了”，而是一张小卡片。卡片包含问题、入口符号、协议符号、实现符号、测试符号、结论和限制。比如研究工具 schema，结论可以写“普通函数通过 tool 装饰器进入，StructuredTool.from_function 生成结构化工具，测试覆盖 docstring 和 args_schema；本结论不讨论 provider 如何展示 schema”。这种卡片短小但可复查。</p>
<p>长期积累后，这些卡片会形成你自己的源码索引。以后遇到新问题，可以先查卡片，再决定是否重新读源码。没有卡片，阅读成果会停留在短期记忆里；有卡片，知识才能在版本变化和项目迁移中复用。</p>

<h2>阅读复盘</h2>
<p>源码阅读最怕“细节淹没问题”。先写问题，再找入口，再找契约，再看实现，再用测试校验，这个顺序能把注意力锁在证据链上。你读到的每个符号都要回答一个问题：它是入口、协议、实现、测试，还是内部辅助？角色不同，稳定性和引用方式也不同。</p>
<p>如果一个结论无法写出文件和符号名，就暂时把它当成猜测；如果能写出符号却找不到测试，就给结论加上边界；如果测试和实现冲突，优先重新确认版本。这样的谨慎会让源码笔记更可靠。</p>
<p>再补一个检查：读源码时如果连续打开五个内部 helper 仍然说不出原始问题是什么，就应该停下来回到路线图。源码不是越深越好，而是证据越贴近问题越好。能用 public API 和测试解释的问题，不必强行钻到最底层。</p><p>最后确认：源码笔记要能服务未来维护。它不仅告诉你今天在哪里看，还要告诉你版本升级、测试失败、provider 差异出现时应该沿哪条证据链复查。这样的笔记才是真正的工程资产，而不是一次性阅读痕迹。</p><p>补充一句：如果阅读结果无法指导代码修改、测试补充或问题定位，就说明证据链还没有闭合，需要重新回到入口和测试。</p>

<h2>引用源码时保留不确定性</h2>
<p>源码阅读最容易过度自信：看到一个 helper 当前这样实现，就写成“LangChain 一定会这样”。更专业的表达是带上范围：“当前版本的某路径中，某符号负责某职责；这个结论由某测试或示例覆盖”。范围不是废话，它告诉未来的你什么时候需要复查。只要换了版本、换了 provider、换了执行模式，原结论就可能只剩一部分成立。</p>
<p>例如研究 <span class="mono">create_agent</span> 时，不要只引用工厂函数本身，还要说明它把循环交给 LangGraph 图执行；研究 <span class="mono">@tool</span> 时，不要只引用装饰器入口，还要说明 schema 推断的边界和测试覆盖。一个结论至少要有入口、契约、代表实现和边界条件，才适合写进团队文档。否则它更像临时笔记，不适合作为设计依据。</p>
<p>如果源码路径和文档路径不一致，也不要急着改代码。先确认是否是仓库重组、版本标签不同、包拆分或文档锚点更新。很多“路径不存在”的问题并不代表符号消失，而是来源仓库或目录名变化。用符号名和包名交叉确认，比只靠路径字符串更稳。</p>
<p>写给同事的源码结论最好包含一个复查动作，例如“升级后重新搜索这个符号并跑相关测试”。这样引用不会变成静态权威，而会变成可维护的索引。源码会变，复查动作让知识能跟着变。</p>
<p>做课程笔记时也一样：把路径、符号、职责、版本和限制放在同一行，未来看到测试失败就能从这一行开始复查，而不是重新在仓库里漫游。</p>
<p>当你引用 LangGraph 或 community 这类独立来源时，更要写出包或仓库名。否则读者可能在主包目录里搜索不到路径，误以为教程错误；明确来源能把“找不到文件”变成“去正确仓库复查”。</p>

<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("读源码就是从 main 分支随机打开文件。", "先提出具体问题，再按 API、协议、实现、测试路线走。"),
    ("只要看 public API 就够了。", "API 只能说明入口；真正边界要看基类契约和测试。"),
    ("行号是最好的引用。", "教学和笔记优先用文件 + 符号名，行号会随版本漂移。"),
    ("测试只是验证，不适合学习。", "测试是维护者写下的行为契约，尤其适合学习边界条件。"),
    ("某个 provider 行为不同，说明 LangChain 整体坏了。", "先比较 partner wrapper 和测试，很多差异来自厂商能力或 SDK 限制。"),
]),
r"""
<h2>小实验：为一个符号建立源码卡片</h2>
""",
shell.lab_card("从 create_agent 建一张 source map", [
    "选择 create_agent，记录 public API 文件和符号名。",
    "找它调用 LangGraph 的位置，记录 StateGraph 或 compiled graph 相关符号。",
    "搜索 tests/examples 中 create_agent 的 happy path，摘出最小用法。",
    "写三句话：它接收什么、返回什么、哪些差异交给 LangGraph 或 provider。",
]),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>源码阅读路线：Public API → Protocol/Base class → Concrete implementation → Tests/Examples。</li>
    <li>结论要用“文件 + 符号名”引用，避免只凭印象讲源码。</li>
    <li><span class="mono">@tool</span> 的主线是函数签名和 docstring → schema → StructuredTool → Agent 使用。</li>
    <li>定位 provider 差异时，比较同一协议下的不同 wrapper 和对应测试。</li>
  </ul>
</div>
""",
])


LESSON_05 = "".join([
r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
前四课给了边界、包结构、调用链和源码路线。本课把它们合成一套学习方法：每个主题都按“概念 → trace → source → experiment → glossary”五步推进。先用概念建立地图，再用 trace 观察真实流动，再用 source 找到文件和符号，再用实验验证假设，最后回到术语表复习。这样学 LangChain，不会停留在“会跑 demo”，也不会陷入“读源码但不知道为什么”。
</p>

<div class="card analogy">
  <div class="tag">🧪 生活类比 · 科学课实验本</div>
  学框架像做实验课。概念是老师先画的模型，trace 是实验仪器记录的数据，source 是教材里的原理推导，experiment 是你改变量后复现实象，glossary 是期末复习卡片。只背概念会空，只有输出截图会玄，直接读源码会乱；五步连起来，才形成“能解释、能定位、能复现、能迁移”的学习闭环。
</div>
""",
shell.lesson_map("使用本教程的五步闭环", [
    ("Concept", "先用中文心智模型回答它是什么、边界在哪、为什么存在", "now"),
    ("Trace", "再用表格或回调观察输入、状态、输出如何变化", "now"),
    ("Source", "用文件 + 符号名把解释落到源码证据", "source"),
    ("Experiment", "用 fake model、in-memory saver、可控 config 做可复现实验", "after"),
    ("Glossary", "把术语回收到索引，建立跨章节链接", "after"),
]),
r"""
<h2>学习状态流：不要跳步</h2>
<p>很多人学 LangChain 的失败模式是跳步：刚看完概念就复制复杂 Agent；输出不对就调 prompt；调不动就随机搜 issue。更稳的流程是把每个主题都当成一个可观测系统，逐层增加证据。</p>
""",
shell.state_flow([
    ("概念", "用一句话定义本节对象，并写出它不负责什么。", "Runnable = 可调用协议，不是某个具体模型"),
    ("Trace", "构造最小输入，记录每一步状态如何变化。", "HumanMessage -> AIMessage -> ToolMessage"),
    ("Source", "找到公共入口、协议、具体实现和测试。", "file + symbol"),
    ("Experiment", "改变一个变量，预测 trace 会怎样变，再运行验证。", "temperature=0 / fake outputs"),
    ("Glossary", "把新术语写成可复习的一句话，并链接到相关课。", "Callback / Checkpoint / Reducer"),
]),
r"""
<div class="card detail">
  <div class="tag">🔬 源码入口 · 文件 + 符号名</div>
  本课关注“怎么做实验”。真实模型输出不稳定、网络和计费也会干扰学习，所以我们优先使用 fake model、内存 checkpointer、RunnableConfig 和 tracer，让实验可重复、可观察、低成本。
</div>
""",
shell.source_map([
    {"file": "libs/core/langchain_core/language_models/fake_chat_models.py", "symbol": "GenericFakeChatModel", "role": "用预设消息或生成器模拟聊天模型，避免真实 API 的随机性和费用。", "direction": "实验替身 -> BaseChatModel 协议"},
    {"file": "langchain-ai/langgraph/libs/checkpoint/langgraph/checkpoint/memory/__init__.py", "symbol": "InMemorySaver", "role": "内存 checkpoint，用于本地验证 LangGraph 状态保存和恢复。", "direction": "Graph runtime -> checkpoint storage"},
    {"file": "libs/core/langchain_core/runnables/config.py", "symbol": "RunnableConfig", "role": "传递 tags、metadata、callbacks、configurable 等运行时配置。", "direction": "调用者 -> Runnable 链路"},
    {"file": "libs/core/langchain_core/tracers/base.py", "symbol": "BaseTracer", "role": "收集 run、事件、输入输出和错误，支撑可观测调试。", "direction": "Callbacks -> trace records"},
    {"file": "libs/core/langchain_core/callbacks/manager.py", "symbol": "CallbackManager", "role": "把回调事件分发给 tracer、日志器或自定义 handler。", "direction": "Runnable execution -> observers"},
]),
r"""
<h2>确定性 fake-model 实验</h2>
<p>学习早期尽量不要依赖真实模型判断框架行为。真实模型会受 temperature、上下文、服务端版本和网络重试影响，同一个 prompt 可能得到不同结果。框架行为实验需要可重复，因此应该用 fake model 固定输出，再观察消息、工具、状态和回调是否按预期变化。</p>
""",
shell.code_walkthrough(
    "experiments/fake_agent_trace.py",
    "deterministic_fake_model",
    '''from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

fake = GenericFakeChatModel(messages=iter([
    AIMessage(content="欢迎来到课程！"),
]))

config = RunnableConfig(
    tags=["lesson05", "fake"],
    metadata={"case": "welcome"},
)

result = fake.invoke([HumanMessage(content="写一句欢迎语")], config=config)
assert result.content == "欢迎来到课程！"''',
    "这个实验不验证模型聪明不聪明，只验证 Runnable 输入、config 传播、AIMessage 输出这些框架行为。",
),
r"""
<h2>实验 trace 表</h2>
""",
shell.trace_table([
    {"step": "1 固定假输出", "input": "GenericFakeChatModel(messages=iter([...]))", "action": "预设模型下一次返回的 AIMessage。", "output": "确定性响应队列"},
    {"step": "2 构造输入", "input": "HumanMessage('写一句欢迎语')", "action": "使用标准消息而不是裸字符串，减少无关变量。", "output": "messages list"},
    {"step": "3 添加 config", "input": "tags + metadata", "action": "通过 RunnableConfig 传入观察标签。", "output": "可追踪 run"},
    {"step": "4 执行 invoke", "input": "fake + messages + config", "action": "走 BaseChatModel/Runnable 协议，但不访问网络。", "output": "AIMessage"},
    {"step": "5 断言行为", "input": "result.content", "action": "断言固定输出，并检查 trace 是否包含 tags。", "output": "实验可复现"},
]),
r"""
<h2>为什么 output-only 调试很弱</h2>
<p>只看最终输出，就像医生只看病人最后一句“我不舒服”。模型回答错，可能是输入消息不对、工具 schema 不对、retriever 返回了错误文档、config 没传、回调断了、图状态被覆盖、provider 参数被忽略，也可能只是模型随机性。最终输出把所有层压成一个字符串，信息量太低。</p>
<p>强调 trace 不是为了形式主义，而是为了把黑盒拆成可观察节点：输入是什么、状态是什么、调用了哪个工具、工具返回什么、下一步路由到哪里、最终消息如何形成。只有这样你才能提出可验证假设。例如“模型没调用工具”可以拆成：工具是否绑定？schema 是否出现在 provider payload？模型是否返回 tool_calls？Agent 是否执行 tool node？ToolMessage 是否回灌？每个问题都能被 trace 或源码回答。</p>

<h2>安全实验设计</h2>
<p>实验要小、确定、单变量、无副作用。小，意味着一次只验证一个概念，例如 config tags 是否传播，不要同时测试 RAG、工具、streaming 和 checkpoint。确定，意味着优先 fake model 或 temperature=0，并固定输入。单变量，意味着每轮只改一个参数，否则输出变化无法归因。无副作用，意味着真实数据库、付款、发邮件、删文件都要用 stub 或 sandbox 工具替代。</p>
<p>对 LangGraph 状态实验，<span class="mono">InMemorySaver</span> 很适合入门：它让你观察 checkpoint 和 thread_id 如何工作，而不需要先部署数据库。等理解状态保存、恢复、中断之后，再换 SQLite、Postgres 或生产级 checkpointer。学习顺序应该从可控到真实，而不是一开始就把所有复杂性打开。</p>

<h2>如何配合术语表</h2>
<p>术语表不是附录，而是学习闭环的“索引层”。每学完一个词，就用一句中文写出：它是什么、在哪一层、和相邻概念有什么区别。例如 Runnable 是协议，不是执行线程；Callback 是事件观察，不是业务逻辑；Checkpoint 是状态快照，不是聊天历史本身。写出区别，才说明你真的掌握边界。</p>
<p>复习时可以反向使用术语表：随机挑一个词，要求自己画出概念图、写出最小 trace、指出源码入口、设计一个小实验。如果四项中有一项说不清，就回到对应课程补证据。这种复习比重看视频或重跑 demo 更有效。</p>

<h2>从最小实验扩展到真实项目</h2>
<p>最小实验不是终点，而是通往真实项目的台阶。第一步用 fake model 固定输出，验证框架行为；第二步把 fake model 换成真实 provider，但仍保持工具和输入简单；第三步加入一个无副作用工具，例如查询内存字典；第四步加入 checkpointer，观察 thread_id 和状态恢复；第五步才接真实数据库、真实检索和真实外部 API。每一步只新增一种复杂性，出了问题能立刻回退到上一层。</p>
<p>这种扩展方式尤其适合 Agent。很多 Agent demo 一上来就包含网页搜索、数据库、文件读写、长上下文和真实模型随机性，输出失败时几乎无法归因。把它拆成层后，你可以先证明“模型会提出工具请求”，再证明“工具节点会执行”，再证明“ToolMessage 会回灌”，最后才证明“真实工具数据质量足够”。学习速度看似慢，其实避免了大量无效调参。</p>

<h2>实验记录应该写什么</h2>
<p>每次实验建议记录六项：目标、假设、固定条件、变量、观察方式、结论。目标回答你要验证什么；假设写出运行前的预测；固定条件列出 fake 输出、输入消息、版本和配置；变量只允许一个；观察方式说明看 trace、断言、日志还是源码；结论写“支持/不支持假设”而不是“感觉可以”。这样的记录能防止你被单次输出误导。</p>
<p>例如验证 callbacks 传播：目标是确认父链 tags 会传到模型；固定条件是 fake model 和同一条 HumanMessage；变量是给父 Runnable 增加 tags；观察方式是 tracer 记录；结论是模型 run 是否带有该 tag。这个实验不需要真实模型，却能可靠证明框架传播行为。</p>

<h2>版本变化时怎么复查</h2>
<p>LangChain 生态变化很快，学习笔记必须能应对版本漂移。不要只保存“某行代码这样写”，要保存符号和职责：<span class="mono">GenericFakeChatModel</span> 用于确定性模型实验，<span class="mono">RunnableConfig</span> 用于运行时配置，<span class="mono">InMemorySaver</span> 用于内存 checkpoint。版本升级后先确认这些符号是否仍在、职责是否变化、测试是否仍覆盖同一行为。这样你能快速更新认知，而不是整套笔记报废。</p>
<p>如果某个符号迁移了，也不要慌。先找 deprecation message，再看新路径是否保留相同协议。LangChain 的很多迁移都围绕“旧入口变薄，新协议更稳定”展开。理解协议比记住路径更抗变化，这也是前几课反复强调 Runnable、BaseMessage、StateGraph 的原因。</p>

<h2>把每一课变成可运行检查</h2>
<p>学习结束时，不要只问“我看懂了吗”，而要问“我能不能写一个最小检查”。消息课可以检查字符串如何变成 HumanMessage；模型课可以检查 fake model 返回 AIMessage；工具课可以检查 @tool 是否生成必填参数 schema；Agent 课可以检查 ToolMessage 是否回灌；LangGraph 课可以检查 checkpoint 是否保存状态。每个检查都很小，却能证明你掌握了一个机制。</p>
<p>这些检查可以积累成个人回归套件。以后版本升级，你运行这些小检查，就知道哪些认知仍然成立，哪些需要更新。相比收藏一堆链接，小检查更接近工程实践：它们能失败，能定位，能提醒你重新读源码。</p>

<h2>学习节奏：先窄后宽</h2>
<p>不要同时学习所有概念。先窄到一条链：HumanMessage 进入 fake model，返回 AIMessage。然后加 config 和 tracer。再加一个 tool。再把手写循环换成 create_agent。再把一次性状态换成 InMemorySaver。每次只增加一个维度，旧维度保持可验证。这样你的心智模型会像树一样长出分支，而不是像毛线团一样缠在一起。</p>
<p>先窄后宽并不意味着忽视全局。第一部分已经给了全局地图，后续每次下钻都要回到地图上定位：我现在学的是协议、provider、工具、图、状态、还是观察？知道自己站在哪一层，才不会把某个细节放大成整个框架。</p>

<h2>把失败当成学习材料</h2>
<p>实验失败不是坏事，前提是失败可观察。一个好的失败会告诉你哪条假设错了：tags 没传播，说明 config 处理有问题；工具没调用，说明 schema、模型能力或路由有问题；checkpoint 没恢复，说明 thread_id 或 saver 配置有问题。一个坏的失败只给你一个含糊输出，让你不知道该改哪里。</p>
<p>所以每个实验都要设计观察点。至少记录输入、状态、配置、事件和输出；涉及工具时记录 tool_calls 和 ToolMessage；涉及图时记录节点名和状态更新；涉及检索时记录召回文档。观察点越明确，失败越有价值。最终你会把调试从“试试这个 prompt”升级为“验证这个层的假设”。</p>
<p>学习路径的最后目标，是让你能独立处理新需求。面对一个教程没覆盖的新 provider、新工具或新 graph 模式，你不需要等待完整示例，而是按同一套流程行动：先写概念边界，再构造最小 trace，再找源码入口，再做确定性实验，再把新术语加入索引。流程稳定，未知内容就会变成可拆解任务。</p>
<p>这也是为什么本指南强调中文解释、源码证据和实验并重。中文解释帮助你建立直觉，源码证据防止直觉漂浮，实验让证据变成自己的经验。三者缺一不可：只有解释会变成口号，只有源码会变成细节堆积，只有实验会变成试错。闭环学习让你既能向别人讲清楚，也能在代码里验证。</p>
<p>从下一部分开始，每课都可以套用本课方法。看到消息系统，就问消息如何流动；看到聊天模型，就追 invoke；看到工具，就看 schema 和执行边界；看到 Agent，就观察状态图；看到 streaming，就记录 chunk 事件。你不是在学习零散章节，而是在反复练习同一套系统化方法。</p>
<h2>把术语变成行动</h2>
<p>术语只有能指导行动才有价值。知道 Runnable，就应该能决定一个组件是否能被 pipe、batch、stream；知道 Callback，就应该能设计观察点；知道 Checkpoint，就应该能解释恢复为什么需要 thread id；知道 FakeModel，就应该能设计无网络实验。每个词都连接一个动作，学习才不会停在背诵。</p>
<p>复习时可以用“术语到行动”的方式自测：随机抽一个词，写出它能帮助你做的一个调试动作、一个源码入口、一个实验。写不出来，就说明这个词仍然只是名词，没有进入工程直觉。</p>

<h2>把实验写成可重复配方</h2>
<p>好的学习实验应该像配方，而不是像回忆。配方要写清环境、输入、固定输出、变量、观察点和预期结果。比如验证 checkpoint 恢复，不要只写“试了一下能恢复”，而要写 thread_id 是什么、初始状态是什么、第一次运行停在哪个节点、恢复时传入什么 config、期望状态中哪些字段保持不变。这样别人才能复现，你未来升级版本时也能重跑。</p>
<p>配方还要明确哪些东西故意不测试。一个 fake model 实验不评价模型质量，一个内存 checkpointer 实验不评价数据库可靠性，一个单工具 Agent 实验不覆盖真实权限系统。写出“不测试什么”能防止读者把实验结论外推到生产。学习中的小实验是为了隔离机制，生产验证则需要在机制清楚后逐层增加真实依赖。</p>
<p>当实验失败时，先不要扩大变量。最常见的错误是同时换真实模型、加检索、改 prompt、开 streaming，最后不知道哪个变化导致结果不同。闭环学习要求你一次只移动一个旋钮；如果必须引入多个变化，就把它拆成几轮实验，每轮都保留上一轮的可运行检查。</p>
<p>最终，这些配方可以成为团队的入门手册。新人先跑确定性实验，理解消息、配置、工具和图状态，再接触真实模型和真实数据。这样训练出的不是“会复制 demo 的人”，而是能用证据解释系统行为的人。</p>
<p>当团队共用同一批配方，讨论也会更具体：大家可以指向同一个输入、同一个 trace、同一个源码符号，而不是各自描述一次不可复现的体验。</p>
<p>把配方保留下来还有一个好处：它会自然形成升级前检查清单。每次依赖升级后先跑这些小实验，若某一步失败，就按配方里的观察点回到对应源码，而不是在完整业务项目里寻找噪声。</p>

<h2>方法复盘</h2>
<p>概念、trace、source、experiment、glossary 不是五个独立动作，而是一条闭环。概念给方向，trace 给事实，source 给证据，experiment 给验证，glossary 给复用。任何一步缺失，学习都会偏：没有概念会乱，没有 trace 会黑盒，没有 source 会虚，没有 experiment 会不牢，没有 glossary 会遗忘。</p>
<p>再补一个检查：每做完一个实验，都要写下如果失败下一步看哪里。比如 fake model 输出不符看预设队列，trace 标签缺失看 config，checkpoint 缺失看 saver 和 thread id。提前写好失败路线，实验才真正可调试。</p><p>最后确认：学习闭环要能重复执行。每遇到新概念，都用同一套问题拆解、同一套 trace 观察、同一套实验验证。</p>

<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("教程应该从完整项目开始，越真实越好。", "学习框架机制时应从可控最小实验开始，再逐步加真实复杂度。"),
    ("fake model 不真实，所以没价值。", "fake model 用来验证框架行为，不用来评估模型能力；它能消除随机性。"),
    ("只要最终回答对，就说明链路正确。", "输出正确可能是偶然；没有 trace 无法证明工具、状态、config 都按预期工作。"),
    ("源码读懂一次就够了。", "版本会变，应该保留文件 + 符号名和实验，方便未来复查。"),
    ("实验变量越多越接近生产。", "多变量实验难以归因；生产复杂性应在机制理解后逐步引入。"),
]),
r"""
<h2>小实验：设计一个无副作用的 Agent 练习</h2>
""",
shell.lab_card("从概念到实验的闭环", [
    "选一个主题，例如 RunnableConfig 传播，用一句话写出概念和边界。",
    "用 fake model 或纯 Runnable 构造最小 trace，记录输入、config、输出。",
    "找到对应源码入口，例如 config.py :: RunnableConfig 和 ensure_config。",
    "只改变一个变量，例如新增 metadata，预测 trace 变化并运行验证。",
    "把 RunnableConfig、callbacks、tracer 三个词加入自己的术语卡片。",
]),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>本教程推荐“概念 → trace → source → experiment → glossary”的学习闭环。</li>
    <li>fake model、InMemorySaver、RunnableConfig、tracers 能让实验低成本、可重复、可观察。</li>
    <li>只看最终输出无法定位层次问题；trace 能把黑盒拆成可验证节点。</li>
    <li>安全实验要小、确定、单变量、无副作用，再逐步迁移到真实 provider 和生产存储。</li>
  </ul>
</div>
""",
])
