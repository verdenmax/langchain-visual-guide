"""C-level Part 6: Agent internals."""

import shell


def _p(text):
    return f"<p>{text}</p>"


def _section(title, paragraphs):
    return f"<h2>{title}</h2>" + "".join(_p(p) for p in paragraphs)


def _analogy(text):
    return f'<div class="card analogy"><div class="tag">🧩 生活类比</div>{text}</div>'


def _points(items):
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<div class="card keypoints"><div class="tag">✅ 本课要点</div><ul>{lis}</ul></div>'


LESSON_27_AGENT_LOOP = (
    r"""
<p class="lead">Agent 循环的最小骨架不是“模型会自己调用函数”，而是一条很朴素的状态机：用户消息先进入 model 节点，模型返回 <span class="mono">AIMessage</span>；如果这条消息带有 <span class="mono">tool_calls</span>，图就转到 tools 节点；工具执行后把结果包装成 <span class="mono">ToolMessage</span> 追加回消息历史；model 再读到这条观察结果并决定继续调用工具还是给出最终回答。本课把这个 model/tool loop 拆成可追踪的节点、消息和终止条件，重点看 <span class="mono">create_agent</span>、<span class="mono">ToolNode</span>、<span class="mono">tools_condition</span>、<span class="mono">AIMessage.tool_calls</span> 与 <span class="mono">ToolMessage</span> 如何配合。</p>
"""
    + _analogy("把 Agent 想成一个接线员，而工具像仓库、订单系统和日历。用户问“我的包裹什么时候到”，接线员先听问题，发现自己没有实时物流数据，于是写一张工单：调用查物流工具，参数是订单号。仓库同事处理工单并把结果贴回工单系统，这张回执就是 ToolMessage。接线员重新阅读完整工单记录，才能回答用户。真正的循环不是接线员脑内神秘发生的，而是“提出工具请求、收到工具回执、再判断是否足够回答”的外部化流程。")
    + shell.lesson_map(
        "本课地图：Agent 循环如何在消息上前进",
        [
            ("用户输入", "HumanMessage 进入 messages 状态，成为 model 节点本轮可见的上下文", "before"),
            ("模型节点", "模型读取历史、系统提示和工具说明，输出 AIMessage；是否继续由 tool_calls 决定", "now"),
            ("条件边", "tools_condition 检查最新 AIMessage.tool_calls，决定跳到 tools 还是结束", "now"),
            ("工具节点", "ToolNode 按 tool_calls 找到工具、执行参数、生成 ToolMessage 观察结果", "source"),
            ("回到模型", "ToolMessage 追加进 messages，模型用观察结果组织最终回答或继续调用工具", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>读 Agent 循环时要先抓住源码入口，而不是从任意示例开始猜。下面的 source map 使用“文件 + 符号名”作为可复查锚点：高层入口在哪里造图，条件边在哪里判断，工具节点在哪里把请求变成观察，消息对象如何保存请求与回执。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "高层 Agent 工厂，把模型、工具、提示、中间件和上下文组装成可运行图", "direction": "用户调用入口，内部把循环交给 LangGraph 编排"},
            {"file": "libs/langgraph/langgraph/prebuilt/tool_node.py", "symbol": "ToolNode", "role": "预置工具节点，读取 AIMessage.tool_calls，执行匹配工具并返回 ToolMessage", "direction": "位于 model -> tools -> model 的 tools 阶段"},
            {"file": "libs/langgraph/langgraph/prebuilt/tool_node.py", "symbol": "tools_condition", "role": "条件路由函数，检查最新 AIMessage 是否还有工具调用", "direction": "model 节点之后决定下一跳是 tools 还是 END"},
            {"file": "libs/core/langchain_core/messages/ai.py", "symbol": "AIMessage.tool_calls", "role": "模型请求调用工具的结构化字段，包含 name、args、id 等信息", "direction": "由模型节点写入，供条件边和 ToolNode 读取"},
            {"file": "libs/core/langchain_core/messages/tool.py", "symbol": "ToolMessage", "role": "工具执行结果消息，用 tool_call_id 与原始请求配对", "direction": "由 ToolNode 写回 messages，下一轮 model 读取"},
        ]
    )
    + r"""
<h2>状态流：一次 model/tool loop</h2>
"""
    + shell.state_flow(
        [
            ("用户问题进入 messages", "用户问“北京明天会下雨吗，顺便给我一句出门建议”。状态里只有 HumanMessage，模型还没有事实数据。", "messages=[HumanMessage(...)]"),
            ("model 节点产出工具请求", "模型看到可用天气工具，返回 AIMessage(content='', tool_calls=[{name:'get_weather', args:{city:'北京', date:'明天'}, id:'call_1'}])。", "AIMessage.tool_calls -> call_1"),
            ("tools_condition 选择 tools", "条件边只看最新 AIMessage 是否有 tool_calls；有就跳到 tools 节点，没有就结束。", "route='tools'"),
            ("ToolNode 执行并写回观察", "ToolNode 根据 name 找到 get_weather，传入 args，得到天气数据，并构造 ToolMessage(tool_call_id='call_1', content='小雨，12℃')。", "messages += ToolMessage"),
            ("model 再读观察并终止", "模型读到 ToolMessage 后组织自然语言回答；这次 AIMessage 没有 tool_calls，条件边路由到 END。", "AIMessage(content='明天小雨...')"),
        ]
    )
    + r"""
<h2>Trace：用户问题到最终回答</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. user question", "input": "HumanMessage: 查订单 42 的物流并告诉我是否需要联系仓库", "action": "图把消息追加到 messages，唤醒 model 节点", "output": "messages 包含用户问题"},
            {"step": "2. model node", "input": "messages + 工具说明 search_order(order_id)", "action": "模型没有直接编造物流，而是产出 AIMessage.tool_calls=[search_order({'order_id':'42'})]", "output": "最新 AIMessage 带 tool_calls"},
            {"step": "3. condition", "input": "latest AIMessage.tool_calls 非空", "action": "tools_condition 返回 tools 分支", "output": "下一步执行 ToolNode"},
            {"step": "4. tools node", "input": "tool_call id=call_order_42, name=search_order, args={'order_id':'42'}", "action": "ToolNode 查找工具、执行函数、捕获结果", "output": "ToolMessage(tool_call_id='call_order_42', content='已出库，预计明天到')"},
            {"step": "5. final model", "input": "完整历史：用户问题 + 工具请求 + 工具结果", "action": "模型综合观察，返回不含 tool_calls 的最终 AIMessage", "output": "条件边结束，用户收到回答"},
        ]
    )
    + r"""
<h2>简化源码走读：循环不是 while，而是条件图</h2>
"""
    + shell.code_walkthrough(
        "libs/langchain_v1/langchain/agents/factory.py",
        "create_agent / model -> tools",
        """state = {"messages": [user_message]}

while True:  # 教学版；真实实现是 StateGraph 条件边
    ai = model.invoke(state["messages"], tools=tool_schemas)
    state["messages"] = add_messages(state["messages"], [ai])

    if not ai.tool_calls:
        return ai

    tool_messages = ToolNode(tools).invoke({"messages": state["messages"]})
    state["messages"] = add_messages(state["messages"], tool_messages)
""",
        "真实 create_agent 不一定写成 Python while；它把 model 节点、tools 节点和条件边编进 StateGraph。教学版保留了核心语义：AIMessage.tool_calls 是请求，ToolMessage 是观察，messages reducer 负责把每轮增量接回历史。",
    )
    + _section(
        "为什么终止条件要落在消息字段上",
        [
            "很多初学者以为 Agent 循环的停止依赖“模型觉得完成了”这种不可见判断。框架真正使用的是更可审计的结构化信号：最新 AIMessage 的 tool_calls 是否为空。模型当然参与了决定，因为它选择是否输出工具调用；但一旦输出变成消息对象，控制流就由确定的字段驱动。这样做让 trace 很好读：看最新消息有没有工具请求，就知道下一步为什么跑 tools 或为什么结束。",
            "把终止条件放在消息字段上还有一个工程收益：它自然支持多工具和并行工具。AIMessage.tool_calls 可以是列表，ToolNode 可以逐个或并行执行，返回的每个 ToolMessage 再用 tool_call_id 配对。若终止条件只是解析自然语言里的“我需要调用工具”，就很难可靠地区分一个工具、三个工具、工具失败后是否需要重试。结构化字段把控制流从文字猜测中解放出来。",
            "这也解释了为什么 ToolMessage 不是普通 AIMessage 或 HumanMessage。它代表工具观察，是模型上一轮请求的结果，必须用 tool_call_id 回连原请求。没有这个连接键，模型下一轮虽然能看到一段文字，却不知道它对应哪个工具、哪组参数、哪个失败或重试。Agent 循环靠消息历史维持因果链，ToolMessage 是这条链上最容易被低估的一环。",
        ],
    )
    + _section(
        "模型负责选择，图负责守纪律",
        [
            "Agent 的“智能”主要发生在 model 节点：模型读系统提示、用户消息、工具说明和工具观察，决定下一步是否调用工具、调用哪个工具、填什么参数。图运行时不理解业务问题，也不会判断天气答案是否正确。它只负责把模型输出的结构化动作执行出来，并把结果按规则放回状态。这样的分工让框架既能支持开放式问题，又能保持执行层可预测。",
            "如果把工具执行也交给模型自由描述，系统会变得不可控：模型可能拼错工具名、漏参数、把敏感参数放进自然语言、把多个工具结果混成一段文本。ToolNode 的价值就在于把工具调用收束到一套可验证路径：按 name 找工具，按 schema 传 args，按 id 生成 ToolMessage，失败时按策略抛错或回填错误消息。模型可以选择动作，但动作必须经过工具节点的契约。",
            "在生产里，这个分工尤其重要。你可以在模型前后加 middleware、在工具节点前做人审、给图加 recursion_limit、给模型调用加 retry/fallback，但核心循环仍然是同一条消息驱动路径。系统越复杂，越需要一个简单稳定的骨架。否则每个业务场景都会手写一套循环，调试和审计成本会迅速失控。",
        ],
    )
    + _section(
        "常见误解与边界情况",
        [
            "Agent 循环很短，但误解很多。最常见的是把 tool_calls 当成工具执行结果。tool_calls 只是模型发出的请求，相当于“我要查订单 42”；ToolMessage 才是执行后的观察，相当于“订单 42 已出库”。请求和结果混淆后，日志会看起来像模型已经知道事实，实际只是模型提出了一个待执行动作。",
            "另一个边界是终止。没有 tool_calls 不代表答案一定正确，只代表模型没有继续请求工具。模型可能因为提示不清、工具描述不好或上下文太长而提前停止。框架只能保证控制流停下，不能保证业务事实一定足够。因此关键业务应配合评测、后置校验或人审，而不是把“无 tool_calls”误读成“任务成功”。",
        ],
    )

    + _section(
        "工程复盘：把循环 trace 变成排障证据",
        [
            "真正上线后，Agent 循环的问题很少表现为“完全不能跑”，更多表现为偶发编造、重复查工具、工具结果被模型忽略、最终回答没有引用刚拿到的观察。排查时不要先改 prompt，而要先把一次运行拆成消息序列：第几条是 HumanMessage，第几条是 AIMessage，第几条带 tool_calls，第几条是 ToolMessage，最后一条 AIMessage 是否仍有工具请求。只要消息序列清楚，控制流就不再神秘。",
            "建议把每个工具调用记录成四列：tool_call_id、工具名、参数摘要、ToolMessage 摘要。模型请求阶段和工具观察阶段必须能一一配对。如果日志里只有工具名没有 id，并行工具一多就会混乱；如果只有 ToolMessage 文本没有原始参数，后来很难判断模型到底查了哪个订单、哪个城市或哪个用户。id 是调试工具循环的主键，不是可选装饰。",
            "当模型拿到工具结果却继续重复调用同一个工具时，先检查 ToolMessage 内容是否对模型可用。很多工具返回的是内部 JSON、错误码或缩写字段，程序员看得懂，模型不一定能把它转成完成条件。工具观察应该简洁、明确、包含模型下一步需要的事实，例如“订单已出库，预计明天到，无需联系仓库”，而不是只返回 status=3。",
            "当模型过早结束时，先看工具说明和系统提示是否让它知道什么时候必须查工具。模型没有 tool_calls 并不说明工具不可用，也不说明事实足够；它可能认为用户问题是常识题，或者工具描述没有覆盖这个场景。此时应改工具 docstring、系统提示和少量评测样例，而不是在外层强行调用工具。强行调用会破坏 Agent 自主决策边界。",
            "工具边界的设计也会影响循环稳定性。一个工具如果既查询订单、又判断是否联系仓库、又生成回复，模型会失去中间观察，后续很难纠错。更好的边界是让工具返回可信事实，把策略判断留给模型或后置规则。反过来，支付、退款、发邮件这类副作用工具不应只返回模糊文本，必须返回业务 id、状态和是否可重试。",
            "多工具场景要额外关注顺序和独立性。天气查询和日历查询可能并行；先查用户权限再退款则不能并行。AIMessage.tool_calls 只是模型提出多个请求，不代表这些请求都安全并发。框架能执行并行工具，但业务仍要定义哪些工具无副作用、哪些工具必须串行、哪些工具需要中间件审批。",
            "如果你在 UI 上展示 Agent 运行过程，建议展示“模型正在思考”不如展示“模型请求查询订单”“工具返回已出库”“模型生成最终建议”这样的阶段化信息。用户不需要看内部类名，但需要知道系统是否真的查了数据。把 tool_calls 和 ToolMessage 映射成可读事件，会显著提升用户信任，也方便客服或开发排查。",
            "最后要把循环测试写成消息级断言，而不是只断言最终文本包含某个词。一个健壮测试可以检查第一轮模型必须产生 search_order 工具请求，ToolMessage 的 id 必须配对，第二轮模型不得再请求同一工具，并且最终回答引用工具事实。这样测试锁定的是 Agent 结构行为，而不是某个随机措辞。",
        ],
    )
    + shell.pitfall_grid(
        [
            ("tool_calls 就是工具返回值", "tool_calls 是模型请求；ToolMessage 才是工具返回值，二者靠 id 配对。"),
            ("Agent 循环是模型内部自动完成", "循环由图运行时执行，模型只输出下一步动作或最终回答。"),
            ("没有 tool_calls 就说明业务完成", "它只说明控制流终止；事实正确性还要靠观察、校验和评测。"),
            ("工具节点只负责调用函数", "ToolNode 还负责参数绑定、消息包装、错误策略和与消息历史的因果连接。"),
        ]
    )

    + _section(
        "源码阅读练习：用五个问题定位循环",
        [
            "第一问：最新消息是谁写的？如果最新消息是 HumanMessage，下一步通常应进 model；如果最新消息是带 tool_calls 的 AIMessage，下一步应进 tools；如果最新消息是不带 tool_calls 的 AIMessage，循环应结束；如果最新消息是 ToolMessage，下一步应回 model。这个判断比阅读一大段日志更快。",
            "第二问：工具请求和工具结果是否配对？检查 AIMessage.tool_calls 里的 id，确认 ToolMessage.tool_call_id 完全一致。配对失败时，模型下一轮可能看见一条观察，却无法可靠知道它对应哪个请求。并行工具、重试工具和工具错误都会放大这个问题。",
            "第三问：工具参数是否来自模型应该负责的范围？城市、日期、订单号通常可以让模型填；user_id、tenant、权限范围不应由模型填。把业务参数和安全参数分开，是后面 Runtime Context 课程的基础，也能减少提示注入风险。",
            "第四问：ToolMessage 内容是否足以让模型停止？如果工具只返回机器码，模型可能继续查；如果工具明确返回事实、缺失原因和下一步建议，模型更容易形成最终回答。工具输出不是给人类后端看的日志，而是给下一轮模型读的观察。",
            "第五问：如果循环继续，继续的理由是什么？有时继续是合理的，例如先查订单再查仓库；有时继续是失控，例如同一参数反复查同一工具。把每轮继续的原因写下来，就能区分正常多步推理和 runaway loop。",
        ],
    )
    + shell.lab_card(
        "手工追踪一次工具循环",
        [
            "写下一个用户问题，并列出模型可用的两个工具名称、参数和用途。",
            "手写第一轮 AIMessage：content 可以为空，但必须包含 tool_calls 的 name、args、id。",
            "根据工具执行结果写一个 ToolMessage，确认 tool_call_id 与上一步 id 完全一致。",
            "再写第二轮 AIMessage：如果还需要工具，解释为什么；如果结束，确认 tool_calls 为空。",
            "检查每一步是否只依赖 messages 中已经出现的事实，不允许模型凭空知道工具结果。",
        ],
    )

    + _section(
        '课堂检查清单：确认你真的理解 Agent 循环',
        [
'能不用框架名解释循环：模型先读消息，输出工具请求；工具节点执行请求，写回工具观察；模型再读观察，直到不再请求工具。',
'能指出每轮循环的最新消息类型，并据此判断下一步应该进模型、进工具还是结束，而不是凭最终文本猜运行路径。',
'能说明工具请求不是工具结果。请求由模型写在 AIMessage.tool_calls，结果由工具节点写成 ToolMessage，二者职责不同。',
'能解释为什么 tool_call_id 必须保留。没有它，并行工具、失败重试和审计日志都会失去因果连接。',
'能区分控制流终止和业务成功。没有 tool_calls 只表示模型没有继续请求工具，不表示事实已经充分或回答一定正确。',
'能判断一个工具是否应该被模型调用。需要实时数据、外部状态或副作用时应走工具；常识解释和文本整理不一定需要工具。',
'能读懂 trace 中的空 content AIMessage。很多模型在请求工具时正文为空，这不是错误，真正动作在 tool_calls 字段。',
'能说明 ToolNode 的价值不只是调用函数，还包括参数绑定、错误处理、结果包装和消息历史回填。',
'能为一个多工具问题判断哪些工具可并行，哪些必须等待前一个工具结果，哪些需要人审。',
'能用消息级测试验证循环，而不是只断言最终回答包含某个关键词。',
'能在模型重复调用同一工具时，检查工具观察是否足够明确、提示是否要求继续、recursion_limit 是否只是兜底。',
'能把 UI 里的进度提示映射到内部阶段，让用户知道系统正在请求工具、等待结果还是生成最终回答。'
        ],
    )

    + _section(
        '复盘提问：循环课后自检',
        [
'如果你只能保留一个调试习惯，请保留消息时间线。把每轮输入输出按顺序写成用户消息、模型消息、工具请求、工具结果、最终模型消息，就能看见控制流的真实形状。很多看似模型能力不足的问题，其实是工具结果没有回到消息历史，或者工具请求和工具结果没有配对。',
'学习本课不要只记住两个类名，而要记住请求和观察的分离。请求表示模型想做什么，观察表示外部世界实际返回了什么。只有把二者分开，系统才能审计、重试、并行和恢复，也才能让模型在下一轮基于事实而不是想象继续推理。',
'设计工具时也要服务循环。工具名称要像动作，参数要像业务输入，返回要像清晰观察。含糊的工具名会让模型误选，含糊的参数会让工具失败，含糊的返回会让模型继续追问或编造。一个好工具不是函数能跑，而是能让循环向结束前进。',
'最终回答出现问题时，先问模型有没有机会看到正确观察。如果 ToolMessage 不存在，模型是在猜；如果 ToolMessage 太晚写入，模型本轮看不到；如果 ToolMessage 内容缺事实，模型只能补脑。沿着这条线检查，往往比继续调整温度和模型名称更有效。'
        ],
    )

    + _section(
        "最后一遍：把概念落到维护动作",
        [
            "维护课程里的 Agent 页面时，不能只追求术语完整，还要让读者知道下一次出问题该打开哪个文件、看哪个符号、读哪条消息、改哪个边界。源码课的价值正在这里：把抽象概念变成可复查证据，把运行现象变成可解释路径，把设计取舍变成团队可以讨论和测试的维护动作。",
            "学习者如果能在没有导师提示的情况下完成三件事，就说明本课达标：第一，画出运行时数据从入口到节点再到结果的路径；第二，指出哪个结构化字段决定下一步控制流；第三，为一个失败案例选择合理的日志、测试和修复位置。记住名词只是开始，能用名词定位问题才是 C 级源码课的目标。",
        ],
    )

    + _section(
        "收束提醒",
        [
            "读完本课后，请把源码符号、运行 trace、错误策略和测试样例连成一条线。只会说概念说明理解还停在表层；能用概念解释一次真实调用为什么进入这个节点、为什么写入这个消息、为什么选择这个错误边界，才算把 Agent 内部机制转化成工程能力。",
        ],
    )

    + _section(
        "定位口诀",
        [
            "先看入口，再看状态；先看结构化字段，再看自然语言；先看边界，再看实现。这个顺序能避免把构图问题误判成模型问题，把权限问题误判成提示问题，把可恢复错误误判成系统崩溃。",
        ],
    )
    + shell.version_note("本课按 LangChain v1 Agent 与 LangGraph prebuilt ToolNode 的心智模型讲解。具体模块行号会随版本移动，但 create_agent、ToolNode、tools_condition、AIMessage.tool_calls、ToolMessage 这组源码锚点是阅读 Agent 循环的稳定入口。")
    + _points(
        [
            "Agent loop 的核心是 model 节点、tools 条件分支、ToolNode 和回到 model 的消息闭环。",
            "AIMessage.tool_calls 表示工具请求，ToolMessage 表示工具观察，不能混为一谈。",
            "终止条件是最新 AIMessage 没有 tool_calls；这只说明循环结束，不等于业务一定正确。",
            "图运行时守控制流纪律，模型负责选择下一步动作，工具节点负责把动作变成可审计结果。",
        ]
    )
)


LESSON_28_CREATE_AGENT = (
    r"""
<p class="lead"><span class="mono">create_agent</span> 看起来是一行 API，内部却在做一件很工程化的事：把用户声明的 model、tools、system_prompt、middleware、context_schema、response_format 等参数，转成一张 <span class="mono">StateGraph</span>。这张图至少包含 model 节点、可选 tools 节点、条件边、messages 状态和 <span class="mono">add_messages</span> reducer；更复杂时还会插入 middleware 节点、人审边界、结构化输出节点和运行时上下文。本课从参数流入图构件的角度读 <span class="mono">create_agent</span> 与 <span class="mono">_AgentBuilder</span>，理解为什么“高层声明式 API”最终要落到 LangGraph 的状态图。</p>
"""
    + _analogy("create_agent 像旅行社的打包行程。你告诉它目的地、预算、想去的景点、是否需要导游、是否要保险；旅行社不会让你自己排每天路线，而是把这些偏好编成一张行程图：第一天集合，某些景点需要门票，遇到天气就改线，晚上回酒店。你传入的是参数，得到的是可执行流程。_AgentBuilder 就像后台行程规划师，把每个参数放到正确位置，确保车、票、导游和应急方案能接起来。")
    + shell.lesson_map(
        "本课地图：参数如何变成 StateGraph",
        [
            ("声明入口", "create_agent 接收模型、工具、提示、schema、middleware、response_format 等用户意图", "before"),
            ("构建器", "_AgentBuilder 归一化参数，判断需要哪些节点、边和状态键", "now"),
            ("状态图", "StateGraph 定义 messages 等 state，并用 add_messages 描述消息如何增量合并", "source"),
            ("节点与边", "model 节点负责模型调用，ToolNode 负责工具执行，条件边负责循环或结束", "now"),
            ("编译运行", "图编译后成为 Runnable，继承 LangGraph 的 stream、checkpoint、interrupt 和 recursion_limit", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>源码阅读建议从工厂函数进入，再看构建器如何把参数放进图。不要只读最终返回对象；关键在“参数 -> 状态 -> 节点 -> 边 -> 编译图”的转换链。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "公开工厂函数，暴露声明式 Agent 配置入口", "direction": "用户参数从这里进入构图流程"},
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "_AgentBuilder", "role": "内部构建器，归一化工具、模型、middleware、response_format 并决定图形状", "direction": "把高层参数映射成 StateGraph 组件"},
            {"file": "libs/langgraph/langgraph/graph/state.py", "symbol": "StateGraph", "role": "状态图构建器，注册 state schema、节点、普通边、条件边和编译步骤", "direction": "承接 _AgentBuilder 产出的节点与边"},
            {"file": "libs/langgraph/langgraph/prebuilt/tool_node.py", "symbol": "ToolNode", "role": "当 tools 非空时加入图，负责执行模型发出的 tool_calls", "direction": "由条件边从 model 节点路由进入"},
            {"file": "libs/langgraph/langgraph/graph/message.py", "symbol": "add_messages", "role": "messages 状态的 reducer，把每个节点返回的新消息追加或按 id 合并", "direction": "让 model 和 tools 节点只返回增量消息"},
        ]
    )
    + r"""
<h2>调用图：create_agent 的构图路径</h2>
"""
    + shell.call_graph(
        [
            ("create_agent(...) ", "接收 model、tools、system_prompt、middleware、context_schema、response_format", True),
            ("normalize inputs", "把模型标识解析为 chat model，把工具转成 BaseTool/ToolNode 可用形式", False),
            ("_AgentBuilder", "计算 state schema、节点列表、middleware hook、条件边和输出格式策略", True),
            ("StateGraph", "add_node('model')、可选 add_node('tools')、add_conditional_edges(...)、messages reducer", True),
            ("compile", "返回可 invoke/stream 的编译图，运行时由 LangGraph 调度", False),
        ]
    )
    + r"""
<h2>Trace：参数进入图构件</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. model 参数", "input": "model='anthropic:claude...' 或 BaseChatModel 实例", "action": "create_agent 归一化为可调用模型，并准备 bind_tools 或工具 schema", "output": "model node 的核心 runnable"},
            {"step": "2. tools 参数", "input": "tools=[search_order, refund_order]", "action": "工具被验证、命名、生成 schema；若非空则构造 ToolNode", "output": "tools 节点 + model 后条件边"},
            {"step": "3. messages state", "input": "用户传入 messages 或 input", "action": "StateGraph 使用包含 messages 的 state schema，并为 messages 绑定 add_messages reducer", "output": "节点可返回 {'messages':[new_message]}"},
            {"step": "4. middleware 参数", "input": "middleware=[limit, hitl, custom_guard]", "action": "_AgentBuilder 插入 before/after 节点或包裹 model/tool 调用", "output": "图形状和调用链被扩展"},
            {"step": "5. response_format", "input": "response_format=AnswerSchema", "action": "构建结构化输出路径，必要时让模型 with_structured_output", "output": "最终 state 可含 structured_response"},
        ]
    )
    + r"""
<h2>简化源码走读：从声明到图</h2>
"""
    + shell.code_walkthrough(
        "libs/langchain_v1/langchain/agents/factory.py",
        "create_agent / _AgentBuilder",
        """def create_agent(model, tools=None, middleware=(), response_format=None, **opts):
    builder = _AgentBuilder(
        model=init_or_use_model(model),
        tools=normalize_tools(tools or []),
        middleware=list(middleware),
        response_format=response_format,
        context_schema=opts.get("context_schema"),
    )

    graph = StateGraph(builder.state_schema)
    graph.add_node("model", builder.model_node)
    if builder.tools:
        graph.add_node("tools", ToolNode(builder.tools))
        graph.add_conditional_edges("model", tools_condition)
        graph.add_edge("tools", "model")
    graph.set_entry_point(builder.entry_node)
    return graph.compile()
""",
        "教学版省略了动态模型选择、中间件链、结构化输出、interrupt 和 store/checkpointer 等细节，但保留了 create_agent 的关键角色：不是直接执行一次模型，而是声明并编译一张可重复运行的图。",
    )
    + _section(
        "为什么不是手写 while 循环",
        [
            "手写 while 循环可以完成最简单的 model/tool/model，但一旦需求增长，就会不断补洞：怎么保存中间状态，怎么流式输出每个节点，工具并行怎么合并，工具前人审怎么暂停，模型失败怎么重试，超过多少步算失控，最终结构化结果放在哪里。StateGraph 已经为这些问题提供统一运行时，create_agent 的价值就是把 Agent 的常见形状编到这套运行时里。",
            "图还有一个重要收益：可观察。节点名、边、状态 key、每步写入都能被 stream/debug/checkpoint 展示。手写循环的日志通常是开发者随手 print，格式不稳定，也很难恢复执行。Agent 一旦进入生产，可恢复、可追踪、可中断往往比少写几行代码更重要。",
            "不过，create_agent 并不是所有场景的唯一答案。如果你的控制流有非常强的业务确定性，例如必须先检索、再审批、再发邮件、最后写数据库，直接用 StateGraph 手工建图可能更清晰。create_agent 适合“模型可自主决定是否调工具”的通用 Agent；手工图适合“业务流程本身就是主角”的工作流。",
        ],
    )
    + _section(
        "add_messages 为什么是关键小零件",
        [
            "messages 是 Agent 状态中最重要的时间线。model 节点产出 AIMessage，tools 节点产出 ToolMessage，中间件也可能追加 SystemMessage 或修改消息。若每个节点都返回完整历史，节点之间会强耦合：任何节点都要知道前面所有消息怎么合并、是否去重、是否替换同 id 消息。add_messages reducer 把合并规则集中起来，节点只返回“我新增了什么”。",
            "增量返回也和 checkpoint 配合得更好。每一轮写入可以被记录为一个小的状态更新，而不是反复保存一份越来越大的完整列表。调试时你能看到“本步新增了一个 ToolMessage”，而不是只能比较两份大历史差异。对并行工具调用，reducer 还能把多个 ToolMessage 合并到同一 messages key，保持消息因果链完整。",
            "这就是 StateGraph 思维和普通 dict 思维的区别。普通 dict.update 会让后写覆盖先写；Agent messages 需要的是追加、按 id 替换和保留顺序。把这个语义显式写成 reducer，图运行时才能安全地处理多个节点对同一个 state key 的写入。",
        ],
    )
    + _section(
        "常见误解与边界情况",
        [
            "误解一是把 create_agent 当成一个“更聪明的模型调用”。实际上它返回的是图，图可以 stream、checkpoint、配置 recursion_limit，也能插入 middleware。把它当模型调用会忽略状态、边和运行时能力，调试时只盯着 prompt，很容易漏掉工具节点或 reducer 的问题。",
            "误解二是以为传入 tools 后模型一定会调用工具。create_agent 只是把工具说明和执行路径接好；是否调用仍由模型输出 tool_calls 决定。工具描述不清、系统提示禁止调用、模型认为已有答案，都可能导致工具节点完全不跑。排查时要看 AIMessage.tool_calls，而不是只看工具列表是否存在。",
        ],
    )

    + _section(
        "工程复盘：从参数表反推图形状",
        [
            "阅读或评审一个 create_agent 调用时，最有效的方法是先做参数表。第一列写参数名，第二列写它影响的图组件，第三列写运行时可观察结果。model 影响 model 节点；tools 影响 ToolNode 和条件边；middleware 影响额外节点或 wrapper 链；context_schema 影响 Runtime.context；response_format 影响最终 structured_response。参数表一旦完整，图形状基本就能推出来。",
            "不要把所有参数都理解成 prompt 配置。system_prompt 确实会改变模型看到的内容，但 tools 会改变模型可发出的动作空间，middleware 会改变调用边界，checkpointer 会改变恢复能力，context_schema 会改变工具可用的可信环境。这些参数属于不同层次。把它们都塞进“提示词优化”框里，会导致你用错排查手段。",
            "_AgentBuilder 的价值在于归一化。用户可能传字符串模型名、模型实例、普通函数工具、BaseTool、不同形式的 response_format；构建器要把这些变成图运行时能理解的统一组件。源码里很多分支看似繁琐，其实是在维护公共 API 的宽入口和内部图的窄契约。读源码时要区分“兼容用户输入”的代码和“决定运行语义”的代码。",
            "StateGraph 的 state schema 是 Agent 的长期骨架。messages 几乎总在里面，structured_response 可能在里面，某些中间件还会增加额外状态。评审时要问每个 state key 谁写、谁读、合并规则是什么。一个无人负责的 state key 会变成调试噪声；一个无 reducer 却被多个节点写的 key 会在并行场景产生冲突。",
            "ToolNode 是否出现由工具集合决定，但工具集合为空并不代表 Agent 没有价值。无工具 Agent 仍可以用 middleware、context 和 response_format 做结构化问答。相反，有工具也不代表每轮都会进入 ToolNode；条件边仍要看 AIMessage.tool_calls。这个区分能避免很多“我明明传了工具为什么没跑”的误判。",
            "add_messages 让图采用增量写入思维。model 节点不需要复制完整历史，tools 节点也不需要知道前面有多少消息；它们只返回新增消息。运行时用 reducer 统一合并。这个设计降低节点复杂度，也让 checkpoint 可以记录每一步新增内容。若手写循环每次都重建完整 messages，短期简单，长期难以观察和恢复。",
            "response_format 会改变最终阶段，而不是替代中间工具观察。模型仍可能先调用工具，再基于 ToolMessage 生成结构化响应。评审时要确认 schema 字段能被工具事实支撑：如果 schema 要求 order_count，但没有任何工具返回订单列表或数量，模型只能猜。结构化格式约束形状，不会凭空创造可靠事实来源。",
            "如果需要超出 create_agent 默认形状的流程，不要硬塞参数。比如必须先审批再允许模型看某些数据，或者必须按固定流程依次调用三个系统，手写 StateGraph 更清晰。create_agent 是通用 Agent 的快捷入口，不是替代所有工作流建模的银弹。判断标准是：控制权主要属于模型，还是主要属于业务流程。",
        ],
    )
    + shell.pitfall_grid(
        [
            ("create_agent 直接执行 Agent", "它构造并返回可运行图；真正执行发生在 invoke/stream 时。"),
            ("StateGraph 只是实现细节，不影响用法", "图决定状态、节点、边、流式事件、checkpoint 和 recursion_limit，是可观察行为的一部分。"),
            ("messages 可以普通 list append", "在图里应通过 add_messages reducer 合并增量，避免覆盖和并行冲突。"),
            ("ToolNode 总是存在", "只有传入工具且图需要工具阶段时才加入；无工具 Agent 可以只有模型路径。"),
        ]
    )

    + _section(
        "源码阅读练习：检查构图结果而非只看入口",
        [
            "第一步，确认 create_agent 返回的对象按 Runnable 使用，而不是在工厂函数里直接完成业务。很多困惑来自把“构建阶段”和“运行阶段”混在一起：构建阶段决定节点和边，运行阶段才读取用户消息、调用模型和执行工具。",
            "第二步，列出图的入口节点。普通 Agent 往往从 model 或 before_agent/before_model 之类中间件节点进入。入口错了，后续工具和结构化响应都可能看起来正常注册，却永远没有机会运行。",
            "第三步，列出 model 后的条件边。没有工具时，model 可以直接结束；有工具时，条件边必须能根据 AIMessage.tool_calls 跳到 ToolNode。条件边是 Agent 循环从“一次模型调用”变成“多轮工具交互”的关键。",
            "第四步，检查 state schema。messages 是否使用 add_messages，structured_response 是否有明确写入者，中间件新增字段是否有读者。图的状态越清楚，后面 checkpoint、stream 和 debug 才越有意义。",
            "第五步，把参数和节点一一对应。某个 middleware 没生效时，不要只看它是否传进列表，还要看它覆盖了哪个 hook，这个 hook 是否会生成节点或 wrapper。某个 response_format 没生效时，要看最终模型路径是否真的走结构化输出。",
            "最后，判断是否应该退出 create_agent。若图里出现大量固定业务步骤、复杂条件审批和多个必须串行的外部系统，手写 StateGraph 可能比继续堆参数更清楚。高层 API 的价值是覆盖常见形状，不是隐藏所有流程设计。",
        ],
    )
    + shell.lab_card(
        "把一组参数画成图",
        [
            "选择一个 create_agent 调用，列出 model、tools、middleware、context_schema、response_format 五类参数。",
            "画出至少两个节点：model 与 tools；如果没有工具，说明为什么 tools 节点可以省略。",
            "标出 messages state，并写明 model 和 tools 各自返回的增量消息类型。",
            "在 model 节点后写条件边：AIMessage.tool_calls 非空去 tools，否则结束。",
            "给每个 middleware 标注它会变成图节点、调用 wrapper，还是只改变模型/工具请求。",
        ],
    )

    + _section(
        '课堂检查清单：确认你真的理解 create_agent 构图',
        [
'能把 create_agent 看成构图函数，而不是一次模型调用。它接收声明式参数，返回可 invoke 和 stream 的编译图。',
'能根据 tools 是否为空判断图里是否需要 ToolNode，并知道有 ToolNode 也不代表每轮一定执行工具。',
'能说明 model 节点之后为什么需要条件边。循环轮数取决于运行时 AIMessage.tool_calls，编译期无法固定。',
'能解释 add_messages 的作用：节点返回新增消息，reducer 负责追加、替换和合并，而不是让节点复制完整历史。',
'能把 middleware 分成状态钩子和 wrapper，并指出它们会改变图节点还是调用链。',
'能说明 response_format 影响最终输出契约，而不是替代中间 ToolMessage 或工具事实来源。',
'能检查 state schema 中每个 key 的读者、写者和 reducer，避免无主字段或并行写冲突。',
'能区分用户传入参数的宽入口和图内部组件的窄契约，理解 _AgentBuilder 为什么要做大量归一化。',
'能说明为什么图比 while 循环更适合 checkpoint、interrupt、stream、debug 和并行工具。',
'能判断什么时候不该用 create_agent，而应手写 StateGraph 表达固定业务流程。',
'能从一次运行 trace 反推图路径：入口节点、model、条件边、tools、再回 model 或 END。',
'能把构图阶段的错误和运行阶段的错误分开排查，避免在 prompt 上修一个其实是图形状的问题。',
'能说明 checkpointer、store、context_schema 等参数为什么属于运行时能力，而不是模型提示词的一部分。',
'能在代码评审中要求作者画出参数到图组件的映射表，让隐式构图变成团队可讨论的设计。'
        ],
    )

    + _section(
        '复盘提问：构图课后自检',
        [
'create_agent 的学习难点在于它把很多工程能力藏在一个友好入口后面。你看到的是一行函数调用，运行时看到的是节点、边、状态、reducer、wrapper、runtime 和编译图。每当行为不符合预期，都应从这张隐藏图还原路径，而不是只盯着入口参数。',
'参数越多，越要分类。模型参数决定谁来思考，工具参数决定模型可以采取哪些外部动作，中间件决定调用边界如何被保护，上下文决定代码能读取什么可信环境，输出格式决定最终结果如何被应用消费。分类清楚，排查时才不会把所有问题都归因于提示词。',
'构图思维还能帮助团队沟通。产品说要加人工审批，工程上不是在 prompt 里写一句请谨慎，而是要在敏感工具前加入中间件或图节点。产品说要结构化结果，工程上不是让模型多写几行，而是要定义 response_format 并验证字段来源。',
'当 create_agent 的默认图形状不再适合时，主动切到 StateGraph 是成熟选择。高层 API 让常见 Agent 变快，手写图让特殊流程变清楚。两者不是竞争关系，而是同一运行时上的两个入口。关键是知道自己需要模型自主循环，还是需要业务确定流程。',
'读源码时要容忍工厂函数里的复杂分支。公共 API 为了好用，必须接受多种输入形式；内部图为了可靠，必须收束到少数稳定组件。看懂这层转换，就能理解为什么源码不是简单 while 循环，也能判断哪些复杂度是必要的兼容成本。'
        ],
    )

    + _section(
        "最后一遍：把概念落到维护动作",
        [
            "维护课程里的 Agent 页面时，不能只追求术语完整，还要让读者知道下一次出问题该打开哪个文件、看哪个符号、读哪条消息、改哪个边界。源码课的价值正在这里：把抽象概念变成可复查证据，把运行现象变成可解释路径，把设计取舍变成团队可以讨论和测试的维护动作。",
            "学习者如果能在没有导师提示的情况下完成三件事，就说明本课达标：第一，画出运行时数据从入口到节点再到结果的路径；第二，指出哪个结构化字段决定下一步控制流；第三，为一个失败案例选择合理的日志、测试和修复位置。记住名词只是开始，能用名词定位问题才是 C 级源码课的目标。",
        ],
    )

    + _section(
        "收束提醒",
        [
            "读完本课后，请把源码符号、运行 trace、错误策略和测试样例连成一条线。只会说概念说明理解还停在表层；能用概念解释一次真实调用为什么进入这个节点、为什么写入这个消息、为什么选择这个错误边界，才算把 Agent 内部机制转化成工程能力。",
        ],
    )

    + _section(
        "定位口诀",
        [
            "先看入口，再看状态；先看结构化字段，再看自然语言；先看边界，再看实现。这个顺序能避免把构图问题误判成模型问题，把权限问题误判成提示问题，把可恢复错误误判成系统崩溃。",
        ],
    )

    + _section(
        "构图口令",
        [
            "把参数映射成节点和边，是理解本页最重要的练习。遇到 create_agent 行为异常时，先画图，再读 trace，最后才改提示。只要能画出入口、model、ToolNode、条件边、messages reducer 和最终 structured_response，构图结果就从黑盒变成了可维护设计。",
        ],
    )
    + shell.version_note("本课聚焦 LangChain v1 的 create_agent 构图模型。_AgentBuilder 是内部符号，细节可能随版本重构；但 create_agent 把参数映射到 StateGraph、ToolNode、add_messages 和条件边的思路，是读 Agent 源码时最稳定的主线。")
    + _points(
        [
            "create_agent 是声明式工厂，核心工作是把参数编成 StateGraph。",
            "_AgentBuilder 负责归一化输入并决定 state、节点、边、middleware 与输出格式路径。",
            "add_messages 让节点返回增量消息，图运行时负责合并消息历史。",
            "ToolNode 与 tools_condition 构成 model/tool loop；是否进入工具由 AIMessage.tool_calls 决定。",
        ]
    )
)


LESSON_29_MIDDLEWARE = (
    r"""
<p class="lead">AgentMiddleware 是 Agent 循环的“横切扩展层”：你不必改 create_agent 的核心 model/tool loop，就能在模型调用前改状态、在模型调用外包一层重试或路由、在模型调用后检查结果、在工具调用外做人审或限流，并在 Agent 结束后做审计。本课聚焦 <span class="mono">AgentMiddleware</span>、<span class="mono">_chain_model_call_handlers</span>、<span class="mono">_chain_tool_call_wrappers</span>、<span class="mono">ModelCallLimitMiddleware</span> 与 <span class="mono">HumanInTheLoopMiddleware</span>，读懂 before/after/wrap 三类钩子为什么要用不同机制实现。</p>
"""
    + _analogy("把中间件想成机场安检和登机流程。旅客主线是值机、安检、登机、起飞；航空公司不想每增加一条规则就重写机场。于是液体检查、优先登机、人工复核、超售处理都作为可插拔环节放在主线周围。有些环节改变旅客状态，比如盖章放行；有些环节包住一次动作，比如安检员可以让你重新过机或转人工。AgentMiddleware 也是如此：状态钩子像流程站点，wrap 钩子像包住一次模型或工具调用的检查员。")
    + shell.lesson_map(
        "本课地图：Middleware 在循环哪里插手",
        [
            ("before_agent / before_model", "在模型前读取或改写 state，例如注入系统消息、做预算检查", "before"),
            ("wrap_model_call", "包住模型调用，可重试、替换模型、短路、记录耗时", "now"),
            ("after_model", "模型返回后检查 AIMessage，例如审查 tool_calls 或结构化输出", "now"),
            ("wrap_tool_call", "包住单次工具调用，可做人审、权限、脱敏、错误转换", "source"),
            ("after_agent", "循环结束后做审计、指标、最终状态整理", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>中间件源码要分两条线读：第一条是抽象基类定义有哪些钩子，第二条是 create_agent 构图时如何把钩子串起来。状态钩子常被编成图节点；wrap 钩子常被组合成洋葱式 handler。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/langchain_v1/langchain/agents/middleware/types.py", "symbol": "AgentMiddleware", "role": "中间件基类，定义 before_agent、before_model、wrap_model_call、after_model、wrap_tool_call、after_agent 等扩展点", "direction": "用户自定义中间件从这里继承或实现"},
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "_chain_model_call_handlers", "role": "把多个 wrap_model_call 组合成嵌套 handler 链", "direction": "model 节点内部调用模型前后经过这条链"},
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "_chain_tool_call_wrappers", "role": "把多个 wrap_tool_call 组合到 ToolNode/工具执行路径周围", "direction": "每次工具调用会经过 wrapper 栈"},
            {"file": "libs/langchain_v1/langchain/agents/middleware/model_call_limit.py", "symbol": "ModelCallLimitMiddleware", "role": "内置模型调用次数限制，用软上限保护 Agent 不无限思考", "direction": "通常在模型调用前后统计并阻止超限"},
            {"file": "libs/langchain_v1/langchain/agents/middleware/human_in_the_loop.py", "symbol": "HumanInTheLoopMiddleware", "role": "内置人在回路中间件，在敏感工具或动作前 interrupt 等待人工批准", "direction": "常包住工具调用或在工具前插入审批边界"},
        ]
    )
    + r"""
<h2>调用图：洋葱式 wrapper 与图节点并存</h2>
"""
    + shell.call_graph(
        [
            ("State hook", "before_model/after_model 可作为图节点读写 state，运行痕迹进入 checkpoint", True),
            ("Wrapper outer", "第一个 wrap_model_call 拿到 handler，可决定是否调用下一层", False),
            ("Wrapper inner", "下一个 wrapper 继续包住 handler，形成洋葱式顺序", False),
            ("Actual call", "最终模型或工具调用在最内层执行", True),
            ("Unwind", "结果从内到外返回，每层可记录、修改、抛错或转换", False),
        ]
    )
    + r"""
<h2>Trace：五类钩子的执行位置</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. before_model", "input": "state.messages + runtime.context", "action": "GuardMiddleware 检查用户身份、追加安全提示或阻止模型调用", "output": "更新后的 state 进入 model 节点"},
            {"step": "2. wrap_model_call", "input": "ModelRequest + handler", "action": "Limit/Retry/Router wrapper 记录次数，必要时换模型或重试 handler", "output": "AIMessage 或异常"},
            {"step": "3. after_model", "input": "AIMessage(tool_calls=...)", "action": "检查工具调用是否越权、是否需要把某些 tool_calls 改走人工审批", "output": "保留或修改后的模型结果"},
            {"step": "4. wrap_tool_call", "input": "ToolCall(name='refund', args=...) + handler", "action": "HumanInTheLoopMiddleware interrupt 等待批准；通过后才调用真实工具", "output": "ToolMessage 或拒绝消息"},
            {"step": "5. after_agent", "input": "最终 state 和 structured_response", "action": "写审计日志、统计 token、记录最终状态摘要", "output": "调用结束后的可观察副作用"},
        ]
    )
    + r"""
<h2>简化源码走读：middleware 链如何包住模型</h2>
"""
    + shell.code_walkthrough(
        "libs/langchain_v1/langchain/agents/factory.py",
        "_chain_model_call_handlers",
        """def _chain_model_call_handlers(middleware, base_handler):
    handler = base_handler
    for mw in reversed(middleware):
        if not has_wrap_model_call(mw):
            continue
        next_handler = handler

        def handler(request, runtime, mw=mw, next_handler=next_handler):
            return mw.wrap_model_call(request, runtime, next_handler)

    return handler
""",
        "真实实现要处理同步/异步、类型化请求、响应对象和错误传播。核心思想是 wrapper 拿到 next_handler，所以它可以先做检查，再调用内层，也可以重试多次、替换请求、短路返回或把异常转换成更友好的错误。",
    )
    + _section(
        "为什么 before/after 和 wrap 不是同一种东西",
        [
            "before_model、after_model 这类钩子更像状态转换：读当前 state，返回一段 state 更新。它们适合放进图，因为图能记录节点输入输出、进入 checkpoint、被 stream 展示，也能和其他状态更新按 reducer 合并。比如 before_model 追加一条系统提示，after_model 记录模型输出审查结果，这些都属于“状态里发生了什么”。",
            "wrap_model_call 和 wrap_tool_call 则是控制一次调用的边界。它们需要拿到 handler，才能决定要不要调用内层、调用几次、是否换参数、是否捕获异常。重试、fallback、限流、缓存、熔断、人审短路，本质都不是简单 state update，而是“控制是否以及如何执行这个调用”。洋葱式 wrapper 正好表达这种控制权。",
            "两种机制并存不是设计不统一，而是语义不同。强行把所有中间件都做成图节点，重试会很别扭，因为节点只能产生状态更新，不能自然地重复调用内层模型。强行把所有中间件都做成 wrapper，状态变更又不容易被图持久化和可视化。AgentMiddleware 的成熟之处在于按语义选择工具。",
        ],
    )
    + _section(
        "顺序为什么必须可解释",
        [
            "多个中间件叠加时，顺序是第一调试线索。外层 wrapper 先看到请求，最后看到响应；内层 wrapper 离真实调用更近。假设外层是审计，内层是重试，那么审计可能只看到一次“整体调用”；如果外层是重试，内层是审计，审计可能记录每一次尝试。两种都合理，但语义完全不同。团队必须把顺序当成 API 设计，而不是列表偶然顺序。",
            "状态钩子也有顺序问题。一个 before_model 先注入租户信息，另一个 before_model 再做权限检查，和反过来执行可能结果不同。健康做法是让每个中间件职责单一，并在配置旁写清楚依赖：某某 guard 必须在 prompt 注入之后，某某审计必须包在 retry 外部。复杂 Agent 不是不能用很多中间件，而是不能让顺序变成隐形规则。",
            "HumanInTheLoopMiddleware 是理解顺序的好例子。它通常应该靠近敏感工具调用边界，而不是只在最终回答后提醒人审。因为真正需要批准的是“是否执行退款、发邮件、改数据库”这些副作用动作。如果人审放错位置，模型可能已经调用了工具，审批就从预防变成事后通知，安全语义完全变了。",
        ],
    )
    + _section(
        "常见误解与边界情况",
        [
            "误解一是以为 middleware 越多越安全。实际上每层中间件都会增加顺序、延迟和失败模式。安全系统需要最少但明确的护栏：哪些规则在模型前检查，哪些规则在工具前检查，哪些错误要中断，哪些错误要回填给模型。堆叠没有边界的中间件，只会把主循环变成新的黑盒。",
            "误解二是把 wrapper 当成普通回调。普通回调通常只能观察 start/end/error；wrapper 拥有控制权，可以不调用 handler、调用多次、换请求、捕获异常。这个能力很强，也很危险。写 wrapper 时要明确幂等性，尤其包住有副作用工具时，重试可能导致重复扣款或重复发邮件。",
        ],
    )

    + _section(
        "工程复盘：把中间件当成安全边界设计",
        [
            "中间件最容易被滥用成“哪里都放一点逻辑”。成熟做法是先给每个中间件写一句边界说明：它保护什么风险，读取哪些 state/context，可能修改什么，失败时抛错还是返回消息。没有边界说明的中间件，会在几轮迭代后变成隐形业务层，核心循环虽然没改，系统复杂度却被搬到了更难看见的地方。",
            "before_model 适合做输入侧准备和轻量阻断，例如注入非敏感租户摘要、检查消息长度、确认用户是否具备基本访问权限。它不适合执行有副作用动作，也不适合读取工具结果后做复杂补偿，因为此时工具还没有运行。把阶段放错，会让中间件依赖不存在的状态，或者在模型前做了本该在工具前做的安全检查。",
            "after_model 适合检查模型输出的结构化动作。比如模型请求 refund_order，可以在 after_model 检查 tool_calls 是否包含高风险工具、参数是否明显越界、是否需要打上审批标记。但 after_model 仍未执行工具，它更像动作审查员，不是副作用执行者。真正阻止执行通常还要在 wrap_tool_call 或 HITL 边界落地。",
            "wrap_model_call 的风险在于它能重复调用模型。对无副作用模型调用来说，重试通常安全；但每次重试都会消耗 token，并可能产生不同 tool_calls。外层如果没有记录尝试次数、原错误和最终选择，排查时只会看到一个结果，丢失了为什么改走 fallback 的证据。重试不是透明的，应该被观测。",
            "wrap_tool_call 的风险更高，因为工具可能改变外部世界。任何包住工具的 retry、timeout、fallback、人审，都必须先知道工具是否幂等。查询库存可以重试，创建订单不能盲目重试，除非工具支持幂等键并能查询前一次结果。把模型调用的可靠性模式原样套到工具上，是 Agent 系统常见事故来源。",
            "HumanInTheLoopMiddleware 的用户体验也要设计。interrupt 只说“是否批准”往往不够，审批人需要看到工具名、参数摘要、用户身份、租户、风险原因和可选操作。批准后还要把决定写入可追踪状态，避免恢复执行时看不出是谁批准了什么。人审不是暂停按钮，而是一条审计链。",
            "多个中间件之间的依赖应显式排序。可以用命名约定或配置分组：观测类最外层，预算类靠外，fallback/retry 包住模型，权限类靠近工具，HITL 紧贴副作用工具。顺序不是审美问题，而是语义问题。每次新增中间件都要问它应该看见原始请求、每次重试，还是最终结果。",
            "测试中间件时，不要只测“最终能返回”。应构造一个假 handler，记录被调用次数、收到的 request、抛出的错误和返回路径。这样能验证 wrapper 是否真的短路、是否重复调用、是否按预期修改请求。对状态钩子，则要检查它返回的 state 更新是否能被 reducer 合并，而不是在原地偷偷修改输入 dict。",
        ],
    )
    + shell.pitfall_grid(
        [
            ("before_model 可以实现所有护栏", "模型前只能检查当前 state；真正的副作用权限通常要在 wrap_tool_call 里守。"),
            ("wrapper 只是日志回调", "wrapper 控制内层 handler，能重试、短路、替换请求，也必须承担副作用风险。"),
            ("中间件顺序无所谓", "外层/内层顺序会改变审计粒度、重试范围和人审语义。"),
            ("HumanInTheLoop 只是在回答前问人", "HITL 的关键是在敏感动作执行前 interrupt，而不是事后确认。"),
        ]
    )

    + _section(
        "源码阅读练习：调试 wrapper 顺序",
        [
            "先画洋葱图。把 middleware 列表从外到内写出来，再在最内层写真实模型或工具调用。外层最先接触 request，最晚拿到 response；内层最接近真实调用。只要画出这个方向，很多顺序争论就会从抽象讨论变成具体语义。",
            "再标注每层是否可能短路。权限检查可能不调用 handler，缓存可能直接返回旧结果，HITL 可能 interrupt，retry 可能多次调用 handler。能短路的层放在不同位置，会决定哪些审计和计费记录能看见这次尝试。",
            "然后标注每层是否会重复调用。retry 放在审计外面，审计可能只记录一次整体调用；retry 放在审计里面，审计可能记录每次尝试。两种设计都可能正确，但必须符合团队希望的观测粒度。",
            "工具 wrapper 还要标注副作用阶段。权限、人审、幂等检查应在真实工具执行之前；审计可以同时记录执行前请求和执行后结果；错误转换应知道工具是否已经产生副作用。把这些阶段混在一个 wrapper 里，会让失败恢复很难写清楚。",
            "状态钩子的调试则要看图事件。before_model 是否真的产生 state update，after_model 是否看到了模型输出，after_agent 是否只在循环结束后执行。不要用 wrapper 的直觉读状态钩子，它们不是内外层函数，而是图上的步骤。",
            "最后写一个最小假 handler 测试顺序：handler 每次被调用就把名字写入列表，中间件也写入列表。断言列表顺序，比看最终回答可靠得多。中间件系统的正确性首先是执行顺序正确，其次才是业务逻辑正确。",
        ],
    )
    + shell.lab_card(
        "设计一个工具权限中间件",
        [
            "列出一个敏感工具，例如 refund_order(amount, order_id)，说明它的副作用。",
            "写出 before_model 只做什么：读取 context 中的 user_id/role，不把密钥放进消息。",
            "写出 wrap_tool_call 做什么：检查工具名、金额上限、租户范围，必要时触发人工审批。",
            "决定错误策略：权限不足抛异常，还是返回带 tool_call_id 的拒绝 ToolMessage 给模型解释。",
            "说明 middleware 在列表中的顺序：应在 retry 内侧还是外侧，为什么。",
        ],
    )

    + _section(
        '课堂检查清单：确认你真的理解 middleware',
        [
'能说明中间件是横切能力，不是把业务主流程藏到插件里。每个中间件都应有清晰风险边界。',
'能区分 before_model、after_model 与 wrap_model_call 的语义：前两者偏状态更新，后者控制一次调用。',
'能区分 after_model 与 wrap_tool_call：前者审查模型提出的动作，后者守住真实工具执行边界。',
'能解释为什么 wrapper 拿到 handler 就能实现重试、fallback、短路、缓存和熔断。',
'能画出多个 wrapper 的洋葱顺序，并预测外层和内层交换后日志、重试次数和错误传播会怎样变化。',
'能指出哪些中间件应靠近模型，哪些应靠近工具，哪些应最外层记录审计指标。',
'能说明 HumanInTheLoop 的关键是副作用前审批，而不是最终回答后让人看一眼。',
'能为敏感工具列出审批信息：工具名、参数摘要、租户、用户、风险原因、批准人和恢复状态。',
'能避免在 wrapper 中盲目重试有副作用工具，除非工具支持幂等键和状态查询。',
'能测试一个 wrapper 是否真的调用内层几次、是否短路、是否修改 request、是否正确传播异常。',
'能测试状态钩子返回的是增量 state update，而不是偷偷原地修改输入对象。',
'能在中间件列表旁写出顺序理由，让后来维护者知道为什么审计在外、权限在内或相反。',
'能识别中间件过多带来的新黑盒，并通过职责拆分、命名和观测减少复杂度。'
        ],
    )

    + _section(
        '复盘提问：中间件课后自检',
        [
'中间件的强大来自不改核心循环，但危险也来自不改核心循环。逻辑被放在循环旁边后，调用者可能看不出它已经改变了模型请求、工具执行或错误传播。因此每个中间件都应该有名字、边界、顺序说明和测试，不能只靠作者记忆。',
'状态钩子和调用包裹的差异要反复练习。状态钩子像图上的站点，适合留下可持久化的状态变化；调用包裹像围住一次动作的守门员，适合控制是否执行、执行几次、失败如何处理。把二者混用，会让代码既不好观察，也不好恢复。',
'顺序是中间件系统的第二 API。列表前后不是格式问题，而是安全和观测语义。权限检查在重试外还是内，审计记录整体调用还是每次尝试，人审发生在参数改写前还是后，都会改变生产行为。任何顺序变化都应像代码变更一样被评审。',
'中间件尤其适合承载横切关注点，例如预算、限流、审计、人审、脱敏、模型路由和错误转换。但业务主流程如果完全藏进中间件，图会变得表面简单、实际难懂。健康边界是主流程仍能从图上读出，中间件只负责跨流程的一致规则。',
'测试中间件时，最终答案通过并不够。要测试 handler 调用次数、异常是否传播、短路是否发生、请求是否被修改、状态更新是否合并。中间件的错误常常不改变 happy path，却会在失败、重试和副作用场景制造事故。'
        ],
    )

    + _section(
        "最后一遍：把概念落到维护动作",
        [
            "维护课程里的 Agent 页面时，不能只追求术语完整，还要让读者知道下一次出问题该打开哪个文件、看哪个符号、读哪条消息、改哪个边界。源码课的价值正在这里：把抽象概念变成可复查证据，把运行现象变成可解释路径，把设计取舍变成团队可以讨论和测试的维护动作。",
            "学习者如果能在没有导师提示的情况下完成三件事，就说明本课达标：第一，画出运行时数据从入口到节点再到结果的路径；第二，指出哪个结构化字段决定下一步控制流；第三，为一个失败案例选择合理的日志、测试和修复位置。记住名词只是开始，能用名词定位问题才是 C 级源码课的目标。",
        ],
    )

    + _section(
        "收束提醒",
        [
            "读完本课后，请把源码符号、运行 trace、错误策略和测试样例连成一条线。只会说概念说明理解还停在表层；能用概念解释一次真实调用为什么进入这个节点、为什么写入这个消息、为什么选择这个错误边界，才算把 Agent 内部机制转化成工程能力。",
        ],
    )

    + _section(
        "定位口诀",
        [
            "先看入口，再看状态；先看结构化字段，再看自然语言；先看边界，再看实现。这个顺序能避免把构图问题误判成模型问题，把权限问题误判成提示问题，把可恢复错误误判成系统崩溃。",
        ],
    )
    + shell.version_note("本课使用 LangChain v1 AgentMiddleware 的概念性源码锚点。具体内置中间件名称和文件可能随版本扩展，但状态钩子编进图、wrap 钩子组合 handler、HITL 守副作用边界，是阅读 middleware 系统的稳定心智模型。")
    + _points(
        [
            "AgentMiddleware 让护栏、审计、重试、人审等横切能力不污染核心 Agent 循环。",
            "before/after 钩子偏状态更新，适合成为图节点；wrap 钩子偏调用控制，适合洋葱式 handler。",
            "中间件顺序会改变语义，必须显式设计和测试。",
            "HITL 应放在敏感副作用发生前，尤其是工具调用边界。",
        ]
    )
)


LESSON_30_RUNTIME_CONTEXT = (
    r"""
<p class="lead">Runtime Context 解决的是一个很具体的问题：Agent 运行时需要知道当前用户、租户、权限、连接、请求 id、地区等信息，但这些信息不一定应该进入对话消息，也不应该让模型随意看到。LangChain v1 的 <span class="mono">context_schema</span>、LangGraph 的 <span class="mono">Runtime</span>、工具侧的 <span class="mono">ToolRuntime</span>，把“给代码用的运行时上下文”和“给模型看的消息状态”分开；<span class="mono">response_format</span> 与 <span class="mono">with_structured_output</span> 则把最终回答收束为结构化结果。本课追踪 <span class="mono">context={'user_id':'u_123','tenant':'acme'}</span> 如何进入 prompt、工具和结构化响应。</p>
"""
    + _analogy("把 Runtime Context 想成餐厅后厨的订单小票背面信息。顾客菜单上写的是“少辣牛肉面”，这是给厨师理解需求的内容；收银系统还知道会员号、门店、优惠券、过敏记录和支付渠道，这些不是都要念给顾客听，也不该贴在菜名里。服务员需要这些信息来查会员价，后厨需要过敏信息来避免花生，经理需要订单号做追踪。context_schema 就是规定小票背面有哪些字段、谁能读、字段类型是什么。")
    + shell.lesson_map(
        "本课地图：context、state 与 structured response 的边界",
        [
            ("context_schema", "声明运行时上下文字段，例如 user_id、tenant、role、request_id", "before"),
            ("Runtime", "图运行时携带 context、store、stream_writer、config 等执行环境", "source"),
            ("ToolRuntime", "工具函数通过运行时对象读取上下文，而不是让模型把秘密填进参数", "now"),
            ("prompt 注入", "只有确实需要模型知道的非敏感摘要才进入系统提示或 messages", "now"),
            ("response_format", "最终回答可通过 with_structured_output 变成可校验结构", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>运行时上下文要同时看 LangChain Agent 工厂、LangGraph runtime 和工具 runtime。读源码时重点问：context 从 invoke 入口保存在哪里，模型节点怎么拿到它，工具调用怎么拿到它，结构化响应最终写到哪个 state key。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "接收 context_schema 和 response_format，把它们纳入 Agent 图与模型调用策略", "direction": "用户声明上下文类型与最终输出类型"},
            {"file": "libs/langgraph/langgraph/runtime.py", "symbol": "Runtime", "role": "图执行期间的运行时对象，携带 context、store、stream_writer、config 等环境", "direction": "节点和中间件可读取当前调用上下文"},
            {"file": "libs/core/langchain_core/tools/base.py", "symbol": "ToolRuntime", "role": "工具侧运行时注入对象，让工具安全读取 context、config 或 store", "direction": "工具执行时避免让模型传入敏感运行时字段"},
            {"file": "libs/core/langchain_core/language_models/chat_models.py", "symbol": "with_structured_output", "role": "把聊天模型包装成按 schema 返回结构化对象的 runnable", "direction": "response_format 需要结构化最终结果时使用"},
            {"file": "libs/langgraph/langgraph/graph/state.py", "symbol": "StateGraph", "role": "承载 messages、structured_response 等 state，并把 runtime context 传入节点", "direction": "Agent 图把上下文与状态分开管理"},
        ]
    )
    + r"""
<h2>状态流：context 如何进入 prompt、工具和结果</h2>
"""
    + shell.state_flow(
        [
            ("调用入口带 context", "应用调用 agent.invoke({'messages':[... ]}, context={'user_id':'u_123','tenant':'acme'})。context 不等于 messages。", "Runtime.context={'user_id':'u_123','tenant':'acme'}"),
            ("before_model 读取上下文", "中间件或 prompt builder 读取 tenant，决定注入“你正在服务 acme 租户”这类非敏感提示；user_id 不直接展示给模型。", "system_prompt += tenant label"),
            ("模型提出业务工具请求", "模型只请求 get_orders(status='open')，不需要自己填 user_id 或 tenant，因为这些由工具 runtime 补齐。", "AIMessage.tool_calls"),
            ("工具通过 ToolRuntime 查上下文", "工具函数读取 runtime.context.user_id 和 tenant，按租户隔离查询数据库。模型从未看到连接串或内部权限。", "query tenant='acme', user_id='u_123'"),
            ("结构化最终响应", "response_format 要求最终输出 {answer, order_count, next_action}；模型通过 with_structured_output 或对应策略写回 structured_response。", "state.structured_response=Answer(...)"),
        ]
    )
    + r"""
<h2>Trace：u_123/acme 的一次调用</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. invoke", "input": "messages=用户问‘我还有哪些未处理订单？’，context={'user_id':'u_123','tenant':'acme'}", "action": "Runtime 保存 context，StateGraph 保存 messages", "output": "上下文和对话分轨"},
            {"step": "2. prompt", "input": "Runtime.context.tenant='acme'", "action": "before_model 只注入租户展示名和回答风格，不注入内部 token", "output": "模型知道服务 acme，但不知道数据库凭证"},
            {"step": "3. tool call", "input": "模型看到 get_orders(status) 工具", "action": "AIMessage.tool_calls=[get_orders({'status':'open'})]", "output": "工具参数不含 user_id/tenant"},
            {"step": "4. tool runtime", "input": "ToolRuntime.context + args.status", "action": "工具用 tenant 和 user_id 做权限过滤，再查询订单", "output": "ToolMessage: 3 个未处理订单"},
            {"step": "5. structured final", "input": "ToolMessage + response_format=OrderSummary", "action": "模型返回可校验结构化响应", "output": "structured_response.answer/order_count/next_action"},
        ]
    )
    + r"""
<h2>简化源码走读：context 不进 messages</h2>
"""
    + shell.code_walkthrough(
        "libs/langchain_v1/langchain/agents/factory.py",
        "context_schema / response_format",
        """class RequestContext(TypedDict):
    user_id: str
    tenant: str

agent = create_agent(
    model=model,
    tools=[get_orders],
    context_schema=RequestContext,
    response_format=OrderSummary,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "我有哪些未处理订单？"}]},
    context={"user_id": "u_123", "tenant": "acme"},
)

# tool(runtime: ToolRuntime) reads runtime.context["tenant"]
# final result may include result["structured_response"]
""",
        "教学版强调边界：messages 是模型要读的对话状态；context 是你的代码、工具和中间件读取的运行时环境；structured_response 是最终可校验业务结果。不要把三者混成一个大字典。",
    )
    + _section(
        "context 与 state 的边界",
        [
            "state 是图内部会被节点读写、被 reducer 合并、被 checkpoint 保存的业务状态。messages、structured_response、当前步骤标记、工具观察，都属于 state。context 则是调用这一次图时由外部注入的环境信息，通常不由节点随意修改，也不应该作为对话历史的一部分。把两者分开，可以让同一张图服务不同用户、租户和请求，而不污染可恢复的业务状态。",
            "安全是这个边界的第一理由。user_id、tenant、role 有时可以被模型知道一个脱敏摘要，但数据库连接、内部权限、访问 token、真实邮箱等敏感字段不应进入消息。只要进入 messages，它就可能被模型引用、被日志记录、被下游工具当成自然语言处理。context 让你的代码能用这些字段，同时默认不把它们暴露给模型。",
            "第二个理由是可测试。测试工具权限时，你可以固定 messages，只改变 context，观察工具查询范围是否正确；测试 prompt 时，你可以固定 context，只改变消息。若所有东西都塞进 messages，每个测试都要解析长 prompt，很难判断失败是模型没理解，还是上下文注入错。",
        ],
    )
    + _section(
        "结构化响应为什么属于最终契约",
        [
            "response_format 不是简单美化输出，而是把 Agent 最终结果变成应用可以依赖的契约。客服页面可能需要 answer 文本、confidence、next_action、ticket_id；后端需要明确字段，而不是从一段自然语言里再用正则提取。with_structured_output 或等价策略把“模型应该按 schema 回答”放进模型调用路径，并把结果写回 structured_response。",
            "结构化响应也能减少工具循环后的歧义。模型读完 ToolMessage 后，如果只写一段话，应用很难知道是否需要展示按钮、是否需要升级人工、是否应该写数据库。schema 让这些决策字段显式化。当然，schema 不会自动保证事实正确；它保证的是形状可校验，事实仍要靠工具结果和业务验证。",
            "要注意 response_format 和 ToolMessage 的职责不同。ToolMessage 是循环中间的工具观察，可能有很多条；structured_response 是循环结束后的最终产物，通常只有一个。前者帮助模型继续推理，后者帮助应用消费结果。混淆二者会导致工具结果被当成最终 API 响应，或者最终响应又被错误追加进工具观察。",
        ],
    )
    + _section(
        "常见误解与边界情况",
        [
            "误解一是“模型需要知道用户是谁，所以把全部 user profile 塞进 prompt”。更好的做法是分类：模型完成任务确实需要的偏好可以用脱敏摘要进入 prompt；权限、连接、审计 id、内部标签留在 context；工具查询时由 ToolRuntime 使用。这样既满足模型理解，又控制泄漏面。",
            "误解二是“context 不进消息，所以工具也拿不到”。工具拿上下文的正确方式不是让模型把 user_id 当参数填出来，而是通过 ToolRuntime 或运行时注入读取。让模型填安全字段会制造伪造风险：用户可以提示模型改成另一个 user_id；runtime context 则由应用层可信注入。",
        ],
    )

    + _section(
        "工程复盘：为上下文画数据分级表",
        [
            "设计 Runtime Context 前，先做数据分级。第一类是模型必须知道的任务语义，例如用户选择的语言、公开的公司名称、当前页面主题；第二类是工具和中间件需要但模型不该知道的安全字段，例如 user_id、tenant、role、auth_scope；第三类是绝不应进入普通日志的秘密，例如访问 token、数据库连接、内部风控标签。分级表比口头说“注意安全”有效得多。",
            "context_schema 的字段应尽量稳定而小。不要把整份用户画像、完整权限对象或任意 settings 字典塞进去。字段越大，越容易被误传进 prompt 或日志，也越难测试。更好的做法是传稳定标识和必要范围，由工具在可信后端查询详细信息，并在返回给模型前做脱敏和摘要。",
            "有些上下文确实需要让模型知道，但要以摘要形式进入消息。比如模型可以知道“当前用户是企业管理员，偏好中文回答”，不需要知道真实 user_id、邮箱、内部权限列表。before_model 或 prompt builder 的职责就是做这种选择性投影：从 Runtime.context 取可信字段，生成最小必要的模型可见信息。",
            "工具参数设计要避免让模型填安全边界字段。get_orders(status) 比 get_orders(user_id, tenant, status) 更安全，因为 user_id 和 tenant 来自 ToolRuntime。即使模型被用户提示“请把 tenant 改成 competitor”，工具也不会使用模型伪造的租户。安全字段从可信运行时进入工具，是多租户 Agent 的基本防线。",
            "structured_response 应只包含下游需要消费的字段。不要为了调试把 context 原样放进最终响应，也不要把工具内部原始返回全塞进去。最终结构应该面向产品契约：answer、items、next_action、needs_human、confidence_reason。内部审计信息走日志或 trace，用户响应走 schema，二者不要混用。",
            "日志策略要同时覆盖 messages、context 和 structured_response。messages 可能包含用户隐私，context 可能包含权限标识，structured_response 可能包含业务结果。生产系统至少要定义字段级脱敏、采样、保留周期和谁有权限查看。很多泄漏不是模型直接泄漏，而是调试日志把上下文和消息拼在一起。",
            "测试上下文边界时，可以写两个同样的用户消息，分别用 tenant=acme 和 tenant=beta 调用，断言工具查询只返回对应租户数据。还可以故意在用户消息里写“我的 user_id 是别人”，断言工具仍使用 Runtime.context 的 user_id。这样的测试能证明模型文本不能越过运行时边界。",
            "当 response_format 失败时，不要立刻把 schema 放宽。先看工具事实是否足够、模型是否看到了需要的字段、schema 是否过度嵌套、字段描述是否清楚。结构化输出失败往往暴露的是上游信息设计问题。把 schema 改成任意 dict 虽然能通过，但会失去应用契约。",
        ],
    )
    + shell.pitfall_grid(
        [
            ("context 就是另一种 state", "context 是每次调用的运行时环境；state 是图内可读写和可持久化的业务状态。"),
            ("把 user_id 放进工具参数最简单", "安全字段应由 ToolRuntime 从 context 读取，避免模型或用户伪造。"),
            ("structured_response 能保证答案正确", "它保证输出形状可校验；事实正确性仍依赖工具、校验和评测。"),
            ("所有上下文都不能给模型看", "非敏感、任务必要的摘要可以进入 prompt；秘密和权限留在 runtime context。"),
        ]
    )

    + _section(
        "源码阅读练习：追踪 context 的可见范围",
        [
            "从 invoke 入口开始，写下同一次调用里的三份数据：input state、context、config。input state 进入图状态，context 进入 Runtime，config 影响回调、标签、recursion_limit 等运行设置。三者常同时出现，但职责不同。",
            "接着检查模型可见内容。模型只能直接看到 messages、系统提示和工具 schema；它不会自动看到完整 context。若模型回答中出现了 user_id 或 tenant，说明某个 prompt builder 或 middleware 主动投影了这些字段，应该确认是否符合脱敏策略。",
            "然后检查工具可见内容。工具如果声明接收 ToolRuntime 或等价运行时对象，就能读取 context。工具参数里不应重复出现安全字段；一旦出现，就要判断这是业务参数还是模型可伪造的权限字段。",
            "再检查结构化响应。structured_response 应来自最终模型输出或结构化策略，不应把 context 原样复制进去。若下游确实需要 request_id 或 tenant 做追踪，也应由应用层在响应外包装，而不是让模型生成这些可信字段。",
            "调试多租户问题时，构造相同 messages、不同 context 的两次调用最有效。如果结果串租户，问题多半在工具没有使用 Runtime.context 过滤，或者某个中间件把租户摘要写错进 prompt。用这种对照，比人工读长 prompt 更快。",
            "最后检查日志和 trace。很多框架会记录 state，但 context 的记录策略要由应用谨慎决定。能记录字段名不代表能记录字段值。安全实践是默认脱敏 context，只在受控调试环境记录最小必要字段。",
        ],
    )
    + shell.lab_card(
        "设计一个安全 context_schema",
        [
            "列出应用需要的运行时字段：user_id、tenant、role、request_id、locale、auth_scope。",
            "把字段分三类：模型可见摘要、工具可见权限、只用于审计且不进入模型。",
            "为一个工具写参数列表，确认它不包含 user_id/tenant，而是从 ToolRuntime 读取。",
            "定义 response_format 字段，例如 answer、items、next_action、needs_human，并说明每个字段给哪个下游使用。",
            "检查日志策略：messages、context、structured_response 哪些能记录，哪些必须脱敏。",
        ],
    )

    + _section(
        '课堂检查清单：确认你真的理解 Runtime Context',
        [
'能一句话区分 context、state 和 config：context 是可信运行时环境，state 是图内业务状态，config 是执行配置和追踪信息。',
'能把 user_id、tenant、role、request_id 放进 context，而不是让模型从用户消息或工具参数里伪造。',
'能判断哪些上下文摘要可以给模型看，哪些只能给工具和中间件看，哪些连普通日志都不该出现。',
'能设计工具参数时排除安全字段，让工具通过 ToolRuntime 读取租户和身份，模型只填写业务查询条件。',
'能说明 context_schema 的价值是类型化和边界清晰，而不是随便传一个无限扩张的裸字典。',
'能解释 Runtime.context 不等于 messages，因此不会自动成为模型上下文，必须由代码选择性投影。',
'能说明 structured_response 是最终应用契约，和中间 ToolMessage 的工具观察不是同一层东西。',
'能检查 response_format 字段是否有事实来源，避免 schema 要求模型输出工具从未提供的信息。',
'能为日志制定脱敏策略，分别处理 messages、context、tool args、ToolMessage 和 structured_response。',
'能用相同 messages、不同 tenant 的测试证明工具查询按 Runtime.context 隔离数据。',
'能用用户伪造身份的提示注入测试证明工具不会相信消息里的 user_id，而只相信 context。',
'能把多语言、地区、展示名等非敏感偏好以摘要注入 prompt，同时把令牌和权限留在 runtime。',
'能在结构化输出失败时先排查事实来源、字段描述和模型路径，而不是直接放宽 schema 到任意字典。'
        ],
    )

    + _section(
        '复盘提问：运行时上下文课后自检',
        [
'Runtime Context 的核心价值是可信边界。用户消息是用户可控制的，模型输出是模型生成的，context 是应用注入的可信环境。权限、租户和身份必须站在可信环境一侧，否则提示注入就可能把安全边界变成一句可被改写的文本。',
'上下文不是越多越好。把大对象塞进 context 会诱惑后续代码随手投影到 prompt 或日志，也会让测试难以构造。小而稳定的字段更适合长期维护：标识、范围、角色、请求号、地区和必要偏好，详细资料让工具按需查询并脱敏返回。',
'模型可见信息应是最小必要摘要。模型需要知道回答语言、用户可见角色或业务场景时，可以从 context 投影一小段提示；模型不需要知道内部 id、令牌、连接、完整权限列表和风控标签。投影是主动选择，不是自动泄漏。',
'结构化响应让 Agent 成为应用组件，而不只是聊天机器人。下游界面、规则引擎和数据库写入都需要稳定字段。字段设计应围绕消费方，而不是围绕模型喜欢怎么说。只要下游要依赖某个字段，就应说明它来自哪条消息、哪个工具事实或哪条规则。',
'安全测试要故意攻击边界。让用户在消息里声称自己是管理员，要求模型切换租户，诱导工具使用别人的 user_id；正确系统应仍然使用 Runtime.context，并把越权尝试交给中间件或工具权限检查处理。'
        ],
    )

    + _section(
        "最后一遍：把概念落到维护动作",
        [
            "维护课程里的 Agent 页面时，不能只追求术语完整，还要让读者知道下一次出问题该打开哪个文件、看哪个符号、读哪条消息、改哪个边界。源码课的价值正在这里：把抽象概念变成可复查证据，把运行现象变成可解释路径，把设计取舍变成团队可以讨论和测试的维护动作。",
            "学习者如果能在没有导师提示的情况下完成三件事，就说明本课达标：第一，画出运行时数据从入口到节点再到结果的路径；第二，指出哪个结构化字段决定下一步控制流；第三，为一个失败案例选择合理的日志、测试和修复位置。记住名词只是开始，能用名词定位问题才是 C 级源码课的目标。",
        ],
    )

    + _section(
        "收束提醒",
        [
            "读完本课后，请把源码符号、运行 trace、错误策略和测试样例连成一条线。只会说概念说明理解还停在表层；能用概念解释一次真实调用为什么进入这个节点、为什么写入这个消息、为什么选择这个错误边界，才算把 Agent 内部机制转化成工程能力。",
        ],
    )

    + _section(
        "定位口诀",
        [
            "先看入口，再看状态；先看结构化字段，再看自然语言；先看边界，再看实现。这个顺序能避免把构图问题误判成模型问题，把权限问题误判成提示问题，把可恢复错误误判成系统崩溃。",
        ],
    )
    + shell.version_note("本课按 LangChain v1 Agent 的 context_schema/response_format 与 LangGraph Runtime 心智模型讲解。不同版本中 Runtime、ToolRuntime 的具体导入路径可能调整；但 context 与 state 分离、工具通过 runtime 读安全字段、最终响应用 schema 收束，是稳定设计原则。")
    + _points(
        [
            "context_schema 描述给代码用的运行时环境，不应默认进入 messages。",
            "Runtime/ToolRuntime 让节点、中间件和工具读取可信上下文，避免模型伪造安全字段。",
            "response_format/with_structured_output 把最终结果变成应用可校验契约。",
            "上下文、消息状态、工具观察、结构化响应各有职责，混在一起会带来泄漏和调试困难。",
        ]
    )
)


LESSON_31_CONTROL_ERRORS = (
    r"""
<p class="lead">Agent 最危险的地方不是“它能调工具”，而是它可能一直调工具、重复调有副作用的工具、把工具错误吞掉、在模型失败时没有降级路径。LangGraph 用 <span class="mono">recursion_limit</span> 与 <span class="mono">GraphRecursionError</span> 给图执行加硬刹车，<span class="mono">Pregel.stream</span> 在步骤循环中推进并暴露错误边界；LangChain 的 <span class="mono">RunnableRetry</span>、<span class="mono">RunnableWithFallbacks</span> 提供调用级重试和降级；<span class="mono">ToolNode</span> 则决定工具异常是抛出、还是转换成带 tool_call_id 的 ToolMessage。本课把失控循环、工具错误、模型错误和安全副作用放到同一张控制图里。</p>
"""
    + _analogy("把 Agent 控制想成自动驾驶车。导航系统可以自己规划路线，但车必须有最高速度、刹车、碰撞传感器和人工接管。recursion_limit 是硬刹车：不管导航还想绕几圈，到步数上限必须停。retry 像短暂网络抖动后的重新请求，fallback 像主路封闭时改走备用路线。工具副作用则像真正踩油门或转账：不能因为上一脚没收到反馈就盲目再踩一次。安全系统不是让车更聪明，而是保证聪明系统失误时不会无限扩大损失。")
    + shell.lesson_map(
        "本课地图：Agent 控制与错误边界",
        [
            ("硬上限", "recursion_limit 限制图步骤，超过后抛 GraphRecursionError 防止无限循环", "before"),
            ("图执行", "Pregel.stream 按超步推进，错误、interrupt、stream 事件都从执行循环暴露", "source"),
            ("模型错误", "RunnableRetry 处理短暂失败，RunnableWithFallbacks 切备用模型或链", "now"),
            ("工具错误", "ToolNode 可让异常浮出，也可按策略转成 ToolMessage 交给模型恢复", "now"),
            ("副作用安全", "重试与 fallback 必须区分幂等工具和不可重复副作用", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>控制与错误要跨 LangGraph 执行引擎、LangChain Runnable 包装器和 ToolNode 三处阅读。source map 的问题不是“哪里抛异常”，而是“谁定义上限，谁推进步骤，谁决定重试，谁把工具错误变成消息”。</p>
"""
    + shell.source_map(
        [
            {"file": "libs/langgraph/langgraph/errors.py", "symbol": "GraphRecursionError", "role": "图超过 recursion_limit 时抛出的硬错误，表示循环未按预期收敛", "direction": "从执行引擎向调用方暴露"},
            {"file": "libs/langgraph/langgraph/pregel/main.py", "symbol": "Pregel.stream", "role": "编译图的流式执行入口，按步骤推进任务、检查限制、产出事件或错误", "direction": "Agent 图 invoke/stream 最终进入的执行循环"},
            {"file": "libs/core/langchain_core/runnables/retry.py", "symbol": "RunnableRetry", "role": "Runnable 级重试包装器，适合短暂网络、限流、可重试模型错误", "direction": "包住模型、链或其他 Runnable 调用"},
            {"file": "libs/core/langchain_core/runnables/fallbacks.py", "symbol": "RunnableWithFallbacks", "role": "Runnable 级 fallback 包装器，主组件失败时切换备用组件", "direction": "为模型或子链提供降级路径"},
            {"file": "libs/langgraph/langgraph/prebuilt/tool_node.py", "symbol": "ToolNode", "role": "工具执行错误边界，可按策略抛错或生成错误 ToolMessage", "direction": "位于工具调用阶段，决定模型能否看到错误观察"},
        ]
    )
    + r"""
<h2>状态流：失控工具循环如何被刹停</h2>
"""
    + shell.state_flow(
        [
            ("模型请求工具", "用户问一个需要查询的问题，模型调用 search 工具。", "step=1 model -> tool_calls"),
            ("工具返回不充分", "ToolNode 返回 ToolMessage，但内容模糊或模型误判，还想再查一次。", "step=2 tools -> ToolMessage"),
            ("循环重复", "model 继续产生相同或相近 tool_calls，tools 再执行，messages 变长但没有最终答案。", "model/tools/model/tools..."),
            ("recursion_limit 命中", "Pregel.stream 推进到配置上限，认为图没有收敛，抛 GraphRecursionError。", "raise GraphRecursionError"),
            ("调用方处理", "应用记录 trace，给用户友好提示，必要时展示部分状态或转人工；不要静默吞掉。", "fallback UI / human escalation"),
        ]
    )
    + r"""
<h2>Trace：工具错误是抛出还是回填</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. runaway loop", "input": "recursion_limit=6，模型反复调用 search_docs(query='same')", "action": "Pregel.stream 每步推进 model/tools，但最新 AIMessage 总有 tool_calls", "output": "第 6 步仍未 END"},
            {"step": "2. hard stop", "input": "下一步将超过上限", "action": "执行引擎抛 GraphRecursionError", "output": "调用方得到明确失败，而不是进程无限运行"},
            {"step": "3. tool raises", "input": "ToolNode 调用 refund_order，数据库超时", "action": "策略 A：让异常浮出，整次 Agent 失败", "output": "应用层捕获异常，可能触发 retry/fallback 或告警"},
            {"step": "4. tool message error", "input": "ToolNode 调用 search，外部 API 返回 404", "action": "策略 B：生成 ToolMessage(tool_call_id=..., content='工具错误：未找到')", "output": "模型下一轮可解释、改参或询问用户"},
            {"step": "5. side effect review", "input": "工具是 charge_card 或 send_email", "action": "不盲目 RunnableRetry；先检查幂等键、人审、事务状态", "output": "避免重复扣款或重复发送"},
        ]
    )
    + r"""
<h2>简化源码走读：三层防线</h2>
"""
    + shell.code_walkthrough(
        "libs/langgraph/langgraph/pregel/main.py",
        "Pregel.stream / recursion_limit",
        """for step in range(config.recursion_limit):
    tasks = prepare_next_tasks(state)
    if not tasks:
        return final_state

    for task in tasks:
        result = run_with_retry_or_fallback(task)
        collect_writes(result)

    apply_writes(state)

raise GraphRecursionError("graph did not finish before recursion_limit")
""",
        "教学版把控制压成三层：图层用 recursion_limit 防无限步骤；Runnable 层用 retry/fallback 处理可恢复调用失败；工具层决定异常浮出还是包装成 ToolMessage。真实系统还要处理 stream、interrupt、checkpoint、并发任务和取消。",
    )
    + _section(
        "recursion_limit 是保险丝，不是业务终止条件",
        [
            "recursion_limit 常被误解成“让 Agent 最多思考 N 轮”的正常控制手段。更准确地说，它是图执行的保险丝：当业务终止条件没有让图结束时，硬上限保证系统不会无限消耗 token、工具费用和外部资源。正常终止仍应来自模型不再输出 tool_calls，或你的图状态满足明确完成条件。",
            "保险丝触发时，不应该简单把上限调大。先看 trace：模型为什么一直调用同一个工具？工具结果是否缺少模型需要的信息？ToolMessage 是否丢了 tool_call_id？提示是否要求必须查到某个不存在的事实？中间件是否每轮都追加新消息导致模型误以为还没完成？把这些根因找出来，比盲目从 25 调到 100 更可靠。",
            "当然，业务可以有软上限。ModelCallLimitMiddleware 这类中间件可以在模型调用次数接近预算时引导模型总结当前信息、请求用户补充或转人工。软上限负责用户体验，recursion_limit 负责绝对安全。两者分层，才不会把友好收尾和硬失败混成一件事。",
        ],
    )
    + _section(
        "retry、fallback 与副作用的边界",
        [
            "RunnableRetry 适合处理短暂、可重试、无副作用或幂等的失败，例如模型 API 429、网络超时、临时 5xx。它不适合盲目包住所有工具。查询天气失败重试一次通常没问题；退款接口超时后重试可能造成重复退款，除非工具使用幂等键、事务状态查询或业务补偿。重试是可靠性工具，不是魔法橡皮。",
            "RunnableWithFallbacks 适合主模型不可用时切备用模型，或主解析链失败时切简化路径。fallback 的风险是掩盖主路径长期故障：用户看似还能用，实际上主模型一直失败。生产系统要把 fallback 事件打到指标和告警里，并在响应中保留必要的降级标记，避免维护者看不到问题。",
            "模型调用和工具调用的错误策略也不同。模型错误通常没有外部副作用，retry/fallback 较安全；工具错误可能已经改变外部世界，也可能只是查询失败。为每个工具标注幂等性、是否有副作用、失败后是否可安全重试，是 Agent 上生产前必须做的清单。",
        ],
    )
    + _section(
        "工具错误：抛出还是 ToolMessage",
        [
            "ToolNode 面对异常时有两种常见策略。第一种是让异常浮出，让整次 Agent 调用失败。这适合权限错误、程序 bug、数据一致性错误、危险副作用失败等不应由模型自行处理的问题。浮出异常能触发应用层告警、事务回滚或人工介入。",
            "第二种是把错误转成 ToolMessage，内容明确说明失败原因，并保留原 tool_call_id。这样模型下一轮能看到“工具执行失败”这个观察，可能改参数、换工具或向用户解释。适合用户输入错误、外部资源不存在、搜索无结果等可对话恢复的情况。关键是错误不能无声消失，否则模型会以为工具没有返回，继续空转或编造事实。",
            "选择策略时问三个问题：错误是否暴露敏感信息？模型是否有能力安全修复？工具是否已经产生副作用？如果错误包含内部栈或 token，不能原样塞进 ToolMessage；如果模型无法修复数据库写入失败，就应抛出；如果只是“订单号不存在”，ToolMessage 反而能让模型请用户核对订单号。",
        ],
    )
    + _section(
        "常见误解与边界情况",
        [
            "误解一是把所有错误都交给模型解释。模型擅长对用户解释可恢复问题，但不该处理权限绕过、内部异常、支付状态不一致这类系统级错误。安全边界必须由代码和中间件守住。",
            "误解二是认为 fallback 越多越稳。没有观测的 fallback 会让系统悄悄降级，成本、质量和合规风险都可能变化。每次 fallback 都应记录原错误、备用路径、用户影响和恢复指标。",
        ],
    )

    + _section(
        "工程复盘：错误策略要按风险分层",
        [
            "生产 Agent 的错误策略不能只写“失败就重试”。建议先按风险分层：模型调用失败、只读工具失败、可幂等写工具失败、不可幂等副作用失败、权限和合规失败。每一层的处理都不同。模型 429 可以 retry；搜索无结果可以 ToolMessage；退款超时要查事务状态；权限不足必须抛出或中断；合规风险可能需要人审。",
            "GraphRecursionError 出现时，最糟糕的处理是捕获后返回“系统繁忙”但不保留 trace。它是宝贵信号，说明图没有收敛。你应该记录 recursion_limit、最后几条 AIMessage.tool_calls、对应 ToolMessage、模型调用次数和工具参数摘要。没有这些证据，下一次只能猜 prompt、工具或条件边哪里出了问题。",
            "软上限和硬上限要配合。软上限可以由 middleware 在模型调用次数接近预算时插入提示，让模型总结已有事实或请求用户补充；硬上限由图运行时保证绝不无限跑。软上限追求体验，硬上限追求安全。只用硬上限，用户会突然失败；只用软上限，bug 仍可能绕过提示继续空转。",
            "工具错误回填给模型时，文案要为模型设计，而不是为后端工程师设计。合适的 ToolMessage 可以写“未找到订单，请用户核对订单号”，不应写完整栈、SQL、内部服务名或 token。模型需要的是可行动观察：改参数、换工具、询问用户、停止并解释。错误消息越像内部日志，泄漏和误导风险越高。",
            "副作用工具必须有调用记录。每次 charge_card、refund_order、send_email 都应生成业务幂等键或操作 id，并在 ToolMessage 或审计日志中保留状态。模型下一轮如果再次请求同一动作，中间件可以检测重复并阻止。没有操作 id，系统很难区分“第一次没成功所以重试”和“已经成功但模型没理解”。",
            "fallback 不是静默降级。主模型失败切备用模型后，响应质量、成本、合规区域和工具调用风格都可能变化。指标应记录 fallback 次数、主错误类型、备用组件、是否最终成功。告警不应只看用户失败率，也要看 fallback 率；否则主路径坏了很久，团队却因为用户暂时还能用而没有发现。",
            "对工具重试要区分传输失败和业务失败。网络超时可能可重试，参数非法不该重试，余额不足更不该换个工具继续尝试。ToolMessage 或异常类型应能表达错误分类，而不是所有失败都变成 Exception('failed')。错误分类越清楚，retry/fallback 策略越安全。",
            "最后，错误策略也要写进评测。构造一个模型反复请求同一工具的假场景，断言 recursion_limit 会触发；构造查询工具 404，断言模型收到脱敏 ToolMessage；构造退款工具超时，断言不会自动重复扣款；构造主模型 429，断言 retry 次数有限且 fallback 被记录。没有这些测试，控制策略只是文档愿望。",
        ],
    )
    + shell.pitfall_grid(
        [
            ("recursion_limit 是正常停止逻辑", "它是硬保险丝；正常停止应来自无 tool_calls 或业务完成条件。"),
            ("所有失败都应该 retry", "只有可重试且幂等的失败才适合自动重试；副作用工具必须谨慎。"),
            ("fallback 成功就不用管主错误", "fallback 事件必须可观测，否则主路径长期损坏会被掩盖。"),
            ("工具异常都转成 ToolMessage", "权限、内部 bug、危险副作用失败通常应抛出；可对话恢复的问题才适合回填。"),
        ]
    )

    + _section(
        "源码阅读练习：为失败路径建立表格",
        [
            "第一列写错误来源：模型、图执行、只读工具、写入工具、中间件、结构化输出。第二列写错误是否可恢复。第三列写是否有副作用。第四列写处理策略。这个表格能迫使你在写代码前区分 retry、fallback、ToolMessage 和抛异常。",
            "模型错误通常适合有限 retry 或 fallback，但也要区分错误类型。429 和超时可以重试，认证失败不该重试，schema 不匹配可能需要修 prompt 或结构化策略。把所有模型异常都包进同一个 retry，会浪费预算并掩盖配置错误。",
            "图执行错误如 GraphRecursionError 代表控制流问题。它不是让模型再试一次就能解决的普通异常。处理它需要保留运行轨迹、最后消息、步数和配置，并给用户一个安全收尾。自动重新运行同一个输入，往往只会再次消耗资源。",
            "只读工具错误可以更灵活。搜索无结果、订单不存在、用户输入格式错误，适合变成 ToolMessage 让模型解释或追问。外部搜索服务短暂超时，可以有限重试。内部权限错误或服务配置错误，则不应让模型继续猜。",
            "写入工具错误必须最保守。发邮件、扣款、退款、修改权限这类动作，在超时后无法仅凭异常判断是否已经执行。正确做法是用幂等键、操作状态查询和人工补偿，而不是简单 retry。Agent 系统的可靠性很大程度取决于这些副作用边界。",
            "结构化输出错误也要分类。如果模型事实充足但格式错，可以重试结构化生成；如果工具事实缺失，重试只会让模型编造；如果 schema 过严，应该调整字段说明或拆分任务。错误策略应服务事实可靠性，而不是只追求通过解析。",
        ],
    )
    + shell.lab_card(
        "为一个生产 Agent 写错误策略",
        [
            "列出每个工具：查询类、写入类、支付类、通知类，并标注是否幂等。",
            "为模型调用设置 retry 条件：只包含超时、429、临时 5xx，并限制最大次数。",
            "为 fallback 设计指标：记录主错误、备用模型、是否影响结构化响应质量。",
            "为工具错误分类：哪些抛出，哪些转 ToolMessage，ToolMessage 文案如何脱敏。",
            "设置 recursion_limit 和软模型调用上限，并写出触发后的用户提示和人工升级路径。",
        ],
    )

    + _section(
        '课堂检查清单：确认你真的理解控制与错误',
        [
'能说明 recursion_limit 是图步骤硬上限，不是正常业务完成条件。它触发时应调查为什么图没有收敛。',
'能把模型错误、图错误、只读工具错误、写入工具错误、权限错误分开，而不是统一写成失败重试。',
'能判断哪些错误适合 RunnableRetry：短暂网络、限流、可重试且无危险副作用的调用。',
'能判断哪些错误适合 fallback：主模型或主链不可用时切备用，并且必须记录降级指标和原始错误。',
'能判断哪些工具错误适合 ToolMessage：用户可修正、模型可解释、内容已脱敏、没有危险副作用。',
'能判断哪些工具错误必须抛出：权限不足、内部 bug、支付状态不一致、可能泄漏敏感信息。',
'能为每个副作用工具设计幂等键、操作状态查询、审计记录和重复调用拦截。',
'能说明自动重试退款或发邮件为什么危险：超时不代表动作没有发生，重复执行可能造成真实损失。',
'能在 GraphRecursionError 日志中保留最后几轮 tool_calls、ToolMessage、步数、配置和工具参数摘要。',
'能区分软上限和硬上限：软上限引导模型收尾或转人工，硬上限保证系统不会无限消耗资源。',
'能设计 fallback 告警，不只看最终成功率，还要看备用路径使用率、质量变化和成本变化。',
'能用失败路径测试覆盖循环失控、模型 429、查询无结果、工具权限不足和副作用超时。',
'能把错误文案写成模型可行动观察，而不是把内部栈、服务名、SQL 或密钥暴露给模型。'
        ],
    )

    + _section(
        '复盘提问：控制错误课后自检',
        [
'控制与错误处理的目标不是让 Agent 永远不失败，而是让失败有限、可见、可恢复且不扩大损失。无限循环要被硬上限截断，短暂错误要有限重试，主路径失败要可观测降级，危险副作用要宁可中断也不盲目重复。',
'每个错误策略都应写明适用条件。retry 需要可重试和幂等，fallback 需要备用路径和告警，ToolMessage 需要模型能安全处理，抛异常需要调用方能接住并给用户收尾。没有条件的统一策略，迟早会在边界场景出事故。',
'工具副作用是最高风险区域。模型可以多想几次，查询可以多试一次，但扣款、退款、发邮件、改权限都是真实世界动作。真实世界动作需要幂等键、事务、状态查询、人审和审计，而不是相信模型下一轮会自己小心。',
'GraphRecursionError 应被当成诊断入口。它告诉你图没有结束，却不告诉你根因。根因可能是工具结果不充分、模型提示要求继续、错误 ToolMessage 被误读、中间件每轮追加新任务，或者条件边设计错误。保留最后几轮 trace 是修复的前提。',
'错误消息也有产品设计。给用户的提示要诚实但不泄漏内部；给模型的 ToolMessage 要可行动但脱敏；给工程师的日志要包含足够上下文但受权限保护。三类读者不同，一段错误文本不应同时承担所有职责。'
        ],
    )

    + _section(
        "最后一遍：把概念落到维护动作",
        [
            "维护课程里的 Agent 页面时，不能只追求术语完整，还要让读者知道下一次出问题该打开哪个文件、看哪个符号、读哪条消息、改哪个边界。源码课的价值正在这里：把抽象概念变成可复查证据，把运行现象变成可解释路径，把设计取舍变成团队可以讨论和测试的维护动作。",
            "学习者如果能在没有导师提示的情况下完成三件事，就说明本课达标：第一，画出运行时数据从入口到节点再到结果的路径；第二，指出哪个结构化字段决定下一步控制流；第三，为一个失败案例选择合理的日志、测试和修复位置。记住名词只是开始，能用名词定位问题才是 C 级源码课的目标。",
        ],
    )

    + _section(
        "收束提醒",
        [
            "读完本课后，请把源码符号、运行 trace、错误策略和测试样例连成一条线。只会说概念说明理解还停在表层；能用概念解释一次真实调用为什么进入这个节点、为什么写入这个消息、为什么选择这个错误边界，才算把 Agent 内部机制转化成工程能力。",
        ],
    )

    + _section(
        "定位口诀",
        [
            "先看入口，再看状态；先看结构化字段，再看自然语言；先看边界，再看实现。这个顺序能避免把构图问题误判成模型问题，把权限问题误判成提示问题，把可恢复错误误判成系统崩溃。",
        ],
    )
    + shell.version_note("本课把 LangGraph 的 GraphRecursionError/Pregel.stream 与 LangChain Core 的 RunnableRetry/RunnableWithFallbacks、LangGraph prebuilt ToolNode 放在一起讲。不同版本的异常类路径和配置名可能微调；但硬上限、可恢复重试、可观测 fallback、工具错误策略和副作用幂等性，是生产 Agent 不变的控制原则。")
    + _points(
        [
            "recursion_limit 是防失控的硬保险丝，触发 GraphRecursionError 后要查根因。",
            "RunnableRetry 适合短暂且可安全重试的失败，RunnableWithFallbacks 适合可观测降级。",
            "ToolNode 的错误策略要区分抛异常和转 ToolMessage，不能无声吞错。",
            "有副作用工具必须设计幂等键、人审、事务状态和重复调用防线。",
        ]
    )
)
