"""C-level Part 4: LangGraph mental model."""

import shell


def _p(text):
    return f"<p>{text}</p>"


def _h3(title, text):
    return f"<h3>{title}</h3>" + _p(text)


def _points(items):
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<div class="card keypoints"><div class="tag">✅ 本课要点</div><ul>{lis}</ul></div>'


def _analogy(text):
    return f'<div class="card analogy"><div class="tag">🧩 生活类比</div>{text}</div>'


LESSON_17_GRAPH_WHY = (
    r"""
<p class="lead">如果说 LCEL 链把 prompt、model、parser 接成一条可组合的管道，那么 LangGraph 解决的是另一类问题：流程会分岔，会把中间结果写入共享状态，会因为工具结果重新回到模型，还必须知道什么时候停止。本课建立第一张 LangGraph 心智地图：图不是漂亮 UI，而是一种可执行的状态机；节点不是随便改全局变量，而是接收 state、返回 partial state；编译后的图仍然是 Runnable，可以像链一样 invoke、stream、batch，却比直线链多了循环、路由和持久运行的能力。</p>
"""
    + _analogy("把 LCEL 想成一条地铁线路：站点固定、方向明确、从起点到终点不回头。LangGraph 更像城市公交调度中心：乘客的当前位置、换乘记录、目的地和路况都在状态里，车辆可以按规则改道、回到中转站、等待工具车送来信息，再决定下一站。调度图不是墙上的路线图好看而已，它是实际发车、记录、转弯和停运的规则。")
    + shell.lesson_map(
        "本课地图：为什么从链升级到状态图",
        [
            ("链的边界", "LCEL 擅长直线和 DAG 组合，但循环、长期状态、动态路由会变得别扭", "before"),
            ("图的承诺", "StateGraph 用节点、边、共享状态表达可执行流程", "now"),
            ("Agent 循环", "messages 进入模型，按 tool_calls 条件分支到工具，再回到模型", "now"),
            ("Runnable 兼容", "CompiledStateGraph 仍能被 LangChain 当作 Runnable 调用", "source"),
            ("下一课", "把 State schema 当成整张图的契约来读", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>本课的源码证据只使用文件 + 符号名，不写行号，因为 LangGraph 版本迭代时行号会移动，而类名、函数名和模块边界更适合作为阅读锚点。建议按“状态图 → 消息 reducer → Pregel 运行时 → LangChain Agent 入口”的顺序读。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/graph/state.py", "symbol": "StateGraph", "role": "有状态图建造者，要求每个节点围绕共享 state 读写 partial update", "direction": "用户定义 schema、节点和边后调用 compile"},
            {"file": "langgraph/graph/message.py", "symbol": "add_messages", "role": "消息列表 reducer，按消息 id 替换或追加，支撑聊天历史合并", "direction": "State key 标注后在运行时合并模型和工具消息"},
            {"file": "langgraph/pregel/main.py", "symbol": "Pregel", "role": "编译图的底层执行模型，按步骤调度节点、通道和更新", "direction": "Compiled graph 作为 Pregel/Runnable 被 invoke 或 stream"},
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "LangChain 高层 Agent 工厂，把易用 API 建在 LangGraph 能力之上", "direction": "用户调用 create_agent，内部组装/编译 LangGraph agent"},
        ]
    )
    + r"""
<h2>调用图：从一次聊天请求到工具循环</h2>
<p>一个最小工具型聊天机器人可以这样想：输入先写入 <span class="mono">messages</span>；模型节点读取消息并生成 AIMessage；如果 AIMessage 带 tool_calls，条件边把控制权交给工具节点；工具节点执行外部函数并写回 ToolMessage；边再把流程导回模型，让模型基于工具结果继续回答；如果模型不再请求工具，条件边走向 END。这个“可能回到模型”的动作，就是链和图最醒目的差别。</p>
"""
    + shell.state_flow(
        [
            ("输入进入状态", "用户问题被包装成 HumanMessage，写入 state['messages']。状态不是全局变量，而是本次运行的可合并数据。", "messages=[HumanMessage('北京天气?')]"),
            ("模型节点运行", "model 节点读取完整消息历史，调用聊天模型，返回 {'messages': [AIMessage(...)]} 这样的部分状态。", "model(state) -> {'messages': [AIMessage(tool_calls=[...])]}"),
            ("条件边路由", "route_tools 检查最后一条 AIMessage 是否有 tool_calls；有就去 tools，没有就去 END。", "route_tools(state) -> 'tools' | END"),
            ("工具节点写回", "tools 节点执行天气工具，把 ToolMessage 作为增量返回，由 add_messages 合并进消息列表。", "tools(state) -> {'messages': [ToolMessage(...)]}"),
            ("回到模型或结束", "工具结果可见后再次进入 model；当模型产出最终回答且不再调用工具，图到达 END。", "tools -> model -> END"),
        ]
    )
    + r"""
<h2>Trace：同一条 messages 如何跨节点流动</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. invoke", "input": "{'messages': [HumanMessage('查订单 42')]} ", "action": "CompiledStateGraph 接收输入，初始化通道和运行配置", "output": "messages 通道有一条用户消息"},
            {"step": "2. model", "input": "messages=用户问题", "action": "模型判断需要调用 search_order 工具", "output": "partial={'messages': [AIMessage(tool_calls=[...])]}"},
            {"step": "3. route", "input": "最后一条 AIMessage 有 tool_calls", "action": "条件边返回 tools 节点名", "output": "下一步调度 tools"},
            {"step": "4. tools", "input": "tool_calls + 旧 messages", "action": "执行工具，把结果包装成 ToolMessage", "output": "partial={'messages': [ToolMessage('已发货')]}"},
            {"step": "5. model again", "input": "用户消息 + AI 工具请求 + ToolMessage", "action": "模型生成自然语言答复，不再调用工具", "output": "END，最终 state 含完整消息轨迹"},
        ]
    )
    + r"""
<h2>简化源码走读：图不是链的语法糖</h2>
"""
    + shell.code_walkthrough(
        "langgraph/graph/state.py",
        "StateGraph",
        """class StateGraph:
    def __init__(self, state_schema, *, context_schema=None):
        self.schema = state_schema
        self.channels = _get_channels(state_schema)

    def add_node(self, name, action):
        # action: State -> partial State
        self.nodes[name] = action

    def compile(self):
        self.validate()
        return CompiledStateGraph(...)
""",
        "教学版只保留关键形状：StateGraph 维护节点、边、schema 和 channel；compile 之后才得到可运行对象。真实实现还会处理输入输出 schema、checkpointer、interrupt、retry 和 Pregel 节点包装。",
    )
    + r"""
<h2>图和链的根本差别</h2>
"""
    + _h3("一、链强调一段输出接下一段输入", "LCEL 的直觉是“把一组 Runnable 按数据依赖拼起来”。Prompt 产出消息，模型产出 AIMessage，parser 产出业务对象；每段只看上游输出，整体像一条表达式。这个模型非常适合无环处理：检索上下文、格式化提示词、调用模型、解析结果。它也能表达并行和简单分支，但一旦流程需要反复回到同一个模型节点，链就会变成手写 while 循环加很多外部变量。")
    + _h3("二、图强调状态在节点之间持续存在", "LangGraph 的核心不是“把边画出来”，而是“把状态作为第一等公民”。节点拿到同一份逻辑 state 的快照，返回自己负责的增量；底层通道和 reducer 决定这些增量怎样合并。于是模型节点不需要知道工具节点怎样存结果，工具节点也不需要负责改写整份历史，它们只对自己产出的 key 负责。共享状态让循环不再依赖隐藏闭包，也让 trace、checkpoint 和恢复都有明确对象。")
    + _h3("三、图允许控制流回到旧节点", "Agent 最典型的行为不是一次模型调用，而是“模型思考、发现需要工具、调用工具、观察结果、继续思考”。这是一条带反馈的控制流。用链表达时，你要在链外写循环、判断 tool_calls、维护消息列表；用图表达时，循环就是边，消息列表就是 state，判断就是条件边。图没有让问题消失，但把隐式控制流变成显式结构。")
    + _h3("四、编译图仍然是 Runnable", "这点很容易被忽略：LangGraph 不是和 LangChain 断裂的另一套世界。编译后的图可以被当成 Runnable 使用，因此上层仍能调用 invoke、stream、batch，也能带 RunnableConfig、回调和 metadata。差别在于这个 Runnable 的内部不是线性序列，而是 Pregel 风格的图运行时。你可以把它嵌回更大的 LangChain 应用，也可以让 create_agent 帮你生成这样的图。")
    + _h3("五、LangChain Agent 建在 LangGraph 上", "高层 Agent API 追求好用：给模型、工具和系统提示，得到一个能对话、调工具、stream 的对象。底层 LangGraph 追求可控：状态 schema、节点、边、checkpoint、interrupt、路由都能被明确表达。create_agent 把这两层接起来，所以“我只是用了 LangChain Agent”并不等于没有 LangGraph；相反，很多 v1 Agent 能力正是依赖 LangGraph 的循环状态机。")
    + _h3("六、状态不是随手可改的全局 dict", "节点收到的 state 应当被理解为一次运行步骤的输入快照。正确姿势是返回 partial update，让 reducer 合并。把它当成全局 dict 原地修改，短期看似方便，长期会破坏并行语义、checkpoint 可复现性和调试透明度。图运行时需要知道“哪个节点写了哪个 key”，这样才能处理冲突、记录更新和恢复。")
    + _h3("七、分支不是 if 语句散落在业务里", "条件边把“根据状态去哪”提升成图结构的一部分。route_tools 这样的函数只负责观察状态并返回目的节点名或 END。这样 trace 可以看到为什么走 tools，不会把路由逻辑藏在模型节点内部。越复杂的 Agent 越需要这种分离：模型节点产出内容，路由函数做决策，工具节点处理副作用，边负责控制流。")
    + _h3("八、循环必须有终止条件", "图能表达环，不代表应该无限绕。每个环都要回答：什么状态表示任务完成？什么状态表示工具失败？最多允许几次工具调用？是否需要 recursion_limit 兜底？如果没有这些问题的答案，LangGraph 只会让无限循环更容易发生。工程上常见做法是让路由函数识别无 tool_calls、达到最大步数、出现不可恢复错误或用户中断，然后走 END 或错误处理节点。")
    + _h3("九、图不是 UI，而是执行语义", "很多人看到 Graph 就想到可视化拖拽。LangGraph 的图当然可以被可视化，但它首先是运行时契约：节点怎样被调度，状态怎样合并，边怎样选择，什么时候保存 checkpoint，异常怎样传播。把它误解成 UI，会低估 schema、reducer 和 Pregel 执行模型的重要性。图的价值不是画出来好看，而是运行出来可解释、可恢复、可组合。")
    + _h3("十、读源码时先找稳定抽象", "本课 source map 里的 StateGraph、add_messages、Pregel、create_agent 分别代表建图层、状态合并、运行引擎和高层入口。不要一开始就陷入某个具体工具节点或 provider 适配器。先建立“入口到运行时”的纵向路径，再回头读细节，会更容易判断某个行为属于图语义、状态 reducer、还是 LangChain Agent 的封装。")
    + _h3("十一、从链迁移到图的判断题", "如果你的流程只有“取输入、格式化、调用模型、解析输出”，链更清楚。如果你开始写 while、把 message history 放在外部变量、根据模型输出选择工具、需要中断恢复、需要多节点共享状态，就该考虑图。判断标准不是代码行数，而是控制流是否已经变成状态机。状态机用图表达，通常比把状态藏在链外更诚实。")
    + _h3("十二、调试视角的变化", "调试链时，你常问“上一段输出是什么，下一段为什么不接收”。调试图时，你要问“当前 state 是什么，哪个节点写了哪个 partial，reducer 怎样合并，路由函数为什么选了这个节点，循环为什么还没结束”。问题从线性数据形状扩展到状态演化和控制流演化。这个视角转变，是学习 LangGraph 的第一道门槛。")
    + _h3("十三、最小心智模型", "把 LangGraph 记成一句话：一张编译后可运行的状态图，节点读取 state 并返回 partial state，边决定下一步，reducer 合并同一 key 的更新，Pregel 风格运行时负责按步骤调度。只要这句话站稳，后面 State schema、节点边、reducer、compile/runtime 都是对其中某个名词的展开。")
    + r"""
<h2>扩展复盘：从链到图的迁移判断</h2>
<p>判断一个流程是否应该迁移到 LangGraph，可以先看三个信号。第一，业务代码里是否已经出现手写循环，例如反复调用模型直到没有工具请求；第二，是否有多个步骤都要读写同一份历史，例如消息、工具结果、审计记录、草稿答案；第三，是否需要在失败、中断、人工确认后恢复到某个中间状态。如果三个信号都没有，LCEL 链往往更短、更透明；如果信号越来越多，继续把循环和状态藏在链外，就会让控制流分散在普通 Python 代码里，trace 也只能看到零散调用，看不到完整状态机。</p>
<p>迁移时不要把原链整体塞进一个巨大的节点。更好的做法是按责任拆分：模型判断是一个节点，工具执行是一个节点，质量检查是一个节点，人工确认是一个节点；共享数据进入 state，去向选择进入条件边，状态合并交给 reducer。这样拆分后，每个节点都能单独测试，每条边都能画出原因，每次运行都能回答“为什么走到这里”。图的收益来自显式结构，而不是把所有旧代码包进一个新容器。</p>
<p>另一个判断维度是团队协作。直线链通常由一个人就能完整理解；状态图往往会服务多个角色：模型工程师关心 prompt 和工具调用，后端工程师关心状态、持久化和权限，产品或运营关心人工审核与失败分支。图把这些关切放到同一张结构里，减少口头约定。只要节点命名和 state key 命名清楚，新成员能从图结构读出系统意图，而不必先追踪一整段嵌套 while/if 代码。</p>
<p>图也不是越细越好。如果每个字符串处理函数都变成节点，运行图会过度碎片化，trace 充满无意义步骤。一个节点应该代表一次业务上可命名、可观察、可失败、可重试的动作。比如“调用模型生成工具请求”值得成为节点，“把字符串去掉空格”通常不值得。合适粒度的标准是：当这一步失败时，你是否希望在 trace 中单独看到它；当它需要替换实现时，是否能不影响其他节点。</p>
<p>最终要记住，LangGraph 给你的不是自动智能，而是组织复杂性的工具。它不会替你设计正确工具，不会替你写终止条件，也不会让坏 schema 变好。它提供的是显式状态、显式路由、显式合并和可运行的图结构。把这些显式性用好，复杂 Agent 才能被调试、被复盘、被安全地演进。</p>
<h2>案例推演：把“查订单并可能升级人工”画成图</h2>
<p>假设原来有一条链：把用户问题填进 prompt，模型回答，如果回答里提到订单号就手动调用查询接口，再把结果塞回 prompt。这个写法在 demo 阶段能跑，但一到生产就会出现很多隐含状态：订单号是否已识别，查询工具是否成功，用户是否要求退款，是否需要人工确认，模型是否已经看过工具结果。用 LangGraph 重写时，第一步不是写节点，而是把这些隐含状态摊开：messages 记录对话，order_id 记录识别结果，tool_attempts 记录工具次数，needs_human 记录升级条件。</p>
<p>图结构可以从最小闭环开始：START 到 model，model 后接 route_tools，有 tool_calls 去 tools，没有工具调用则去 finalize 或 END，tools 再回 model。随后再加风险分支：如果工具返回订单异常或退款金额过高，route_after_tools 可以去 human_review；如果工具失败次数超过上限，可以去 error_handler；如果模型已经给出清晰答复，则去 END。每增加一条边，都要能说清楚对应的业务状态，而不是因为“可能有用”就随手加分支。</p>
<p>这个案例里，LCEL 仍然有位置。model 节点内部可以是一条 prompt | model 的小链，finalize 节点内部可以是一条格式化和解析链，error_handler 也可以复用 Runnable。LangGraph 负责外层状态机，LCEL 负责节点内部的局部数据流。把两者对立起来是误解；更好的分工是：无环的小步骤用链，跨步骤的循环和路由用图。</p>
<p>调试时，最有价值的不是最终答案，而是每一步 state 的变化。第一次 model 为什么请求 query_order？tools 返回了什么 ToolMessage？第二次 model 为什么没有继续调用工具？needs_human 为什么保持 False？如果图设计得好，这些问题都能从 trace 和 state update 中回答。若只能从一大段日志里猜测，说明节点、边或 state key 还不够显式。</p>
<p>安全性也来自显式图结构。退款、发邮件、创建工单等副作用可以集中在少数工具节点，并配合 human_review 或 approval 节点。模型节点只提出意图，不直接执行高风险动作；路由函数只决定去向，不偷偷做副作用；工具节点返回可审计结果。这样产品规则、权限控制和工程实现能在同一张图里对齐。</p>
<p>最后，用图之后仍要保持克制。不要为了展示 LangGraph 把每个 if 都变成节点，也不要让一个 route 函数承担所有业务判断。图应该让复杂性变得可见，而不是把简单问题复杂化。一个健康的订单图，读者能在一分钟内说出主循环、异常分支和终止条件；如果读者只看到满屏节点却说不出状态如何流动，说明抽象粒度需要回调。</p>
<h2>迁移判断：什么时候从 LCEL 链升级到 LangGraph</h2>
<p>第一条判断线是循环是否已经成为业务规则，而不只是临时控制代码。如果你在链外写 while，反复让模型判断是否还要调用工具，再手动把工具结果塞回下一次 prompt，那么真正的系统已经不是直线链，而是一个状态机。迁移到 LangGraph 时，循环要有明确终止：无 tool_calls、达到最大轮数、工具重复返回同样信息、出现不可恢复错误、用户取消或进入人工审核。没有终止条件的图只是把隐形无限循环换成显形无限循环。</p>
<p>第二条判断线是审计是否重要。直线 LCEL 很适合看“输入经过哪些 Runnable 变成输出”；但复杂 Agent 更常问“第几轮模型为什么选择这个工具，工具返回了什么，路由为什么没有结束，最终答案基于哪些观察”。LangGraph 把节点、边和 state update 暴露成可追踪结构，便于事后复盘和问题定位。如果系统涉及订单、退款、医疗建议、合同草稿或高成本工具调用，审计能力通常不是锦上添花，而是上线前提。</p>
<p>第三条判断线是状态是否应该显式命名。LCEL 链可以把中间结果自然地从上一段传给下一段；一旦多个步骤都要读取和更新 messages、tool_attempts、draft_answer、needs_human、last_error 这样的共享数据，继续靠外部变量或闭包维护就会让责任模糊。LangGraph 要求你把这些数据放进 state，并让节点只返回 partial update。这样每个字段谁写、谁读、怎样合并、何时输出，都能被讨论和测试。</p>
<p>第四条判断线是未来是否需要人工介入。很多团队一开始只做自动工具循环，后来才发现退款、删除数据、发送邮件、合规回答都需要人审或确认。如果已经预见到这些节点，提前用图表达 human_review、approval、resume 分支会更稳。即使第一版不接真实人工界面，也可以先让路由把高风险状态导向一个占位节点，保持流程边界清楚，避免以后在链外硬塞暂停和恢复逻辑。</p>
<p>第五条判断线是图边界本身。不是所有小步骤都应该变成节点：字符串清洗、简单格式化、一次 prompt 模板填充，放在 LCEL 子链或普通函数里更清楚。适合作为图节点的是业务上可命名、可观察、可失败、可重试、可能影响下一跳的动作。一个健康设计通常是“外层 LangGraph 管状态机，节点内部继续使用 LCEL 处理局部无环数据流”。这样既不丢掉链的简洁，也不把循环和状态藏在链外。</p>
<p>因此，迁移不是因为 LangGraph 更高级，而是因为你的应用已经出现了状态机的事实。只要你能写出“哪些状态持续存在、哪些节点负责更新、哪些边决定去向、哪些条件让循环停止、哪些步骤需要审计或人工准备”，迁移就是自然的；如果这些问题还答不上来，先整理链外的隐含规则，再动手建图。</p>
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("Graph 主要是为了画可视化 UI", "图首先是可执行状态机；可视化只是理解和调试的附加收益。"),
            ("state 就是节点随便改的全局 dict", "节点应返回 partial state，由 channel/reducer 统一合并，才能保持可追踪和可并行。"),
            ("有环就一定更智能", "环只是表达能力，必须配合路由、终止条件和步数兜底，否则会无限循环。"),
            ("LangChain Agent 和 LangGraph 是两套无关实现", "v1 create_agent 的高层便利入口建立在 LangGraph 的状态图和运行时能力之上。"),
        ]
    )
    + r"""
<h2>小实验</h2>
"""
    + shell.lab_card(
        "把一条 LCEL 工具链改写成图",
        [
            "先写出原链：prompt -> model -> parser，并标出哪一步开始需要 tool_calls 判断。",
            "定义 state 至少包含 messages；把模型调用写成 model 节点，只返回 {'messages': [AIMessage(...)]}。",
            "写 route_tools：最后一条 AIMessage 有 tool_calls 返回 'tools'，否则返回 END。",
            "给 tools 节点返回 ToolMessage，并画出 tools -> model 的回边；再写出最多循环次数或无工具调用的终止条件。",
        ],
    )
    + shell.version_note("本课以 LangChain v1 与当前 LangGraph 的源码结构为锚点。文件名和模块层次可能随发布调整，但 StateGraph、add_messages、Pregel、create_agent 这些符号分别对应状态建模、消息合并、运行时内核和高层 Agent 入口，是阅读新版源码时更稳定的路标。")
    + _points([
        "LCEL 链适合无环数据流；LangGraph 适合循环、分支、共享状态和可恢复运行。",
        "节点的核心契约是 state -> partial state，不是原地改全局对象。",
        "聊天工具循环可以看成 messages 状态在 model、route、tools、model 之间流动。",
        "CompiledStateGraph 仍是 Runnable，所以能接入 LangChain 的 invoke/stream/batch 生态。",
        "LangChain 高层 Agent 的很多能力来自 LangGraph；图不是 UI，而是执行语义。",
    ])
)


LESSON_18_STATE_SCHEMA = (
    r"""
<p class="lead">State schema 是 LangGraph 图的合同：它声明哪些 key 可以进入状态、每个 key 的类型是什么、哪个 key 需要 reducer、哪些数据属于运行时 context 而不是可变 state。本课把 schema 当成“多人协作写同一本账”的制度来看：节点只能按合同读写，返回 partial update；运行时根据 schema 建 channel；list 这类会累积的 key 必须声明合并规则，否则默认覆盖会让历史消失。</p>
"""
    + _analogy("把 State schema 想成共享病历的表格模板：姓名、过敏史、检查结果、医嘱、备注分别有固定栏位。医生不能把化验单塞进姓名栏，也不应该直接涂改整本病历；每次只提交自己新增的记录，由病历系统按规则追加或覆盖。context_schema 则像医院科室、值班医生、权限范围，是这次看诊的环境，不是病人病情本身。")
    + shell.lesson_map(
        "本课地图：State schema 如何约束整张图",
        [
            ("状态合同", "TypedDict/Pydantic/dataclass 都是在声明图运行时可以看到的 key", "now"),
            ("通道生成", "_get_channels/_get_channel 把字段类型和 Annotated reducer 变成 channel", "source"),
            ("上下文分离", "context_schema 放运行环境，state 放会随节点演化的数据", "now"),
            ("部分更新", "节点返回 {'messages': [...]}，reducer 决定和旧值怎样合并", "now"),
            ("下一课", "节点和边会围绕这个状态合同工作", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>读 schema 相关源码时，重点不是背某个 TypedDict 示例，而是追踪“类型声明怎样变成运行时通道”。下面这些文件 + 符号名覆盖了建造者入口、字段解析、运行时上下文和消息 reducer。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/graph/state.py", "symbol": "StateGraph.__init__", "role": "接收 state_schema、context_schema、input_schema、output_schema 等图级合同", "direction": "用户定义图时调用，初始化 schemas 与 channels"},
            {"file": "langgraph/graph/state.py", "symbol": "_get_channels", "role": "扫描 schema 字段，决定每个 key 对应什么 channel 或 managed value", "direction": "compile 前把类型信息转成运行时合并规则"},
            {"file": "langgraph/graph/state.py", "symbol": "_get_channel", "role": "读取单个字段的 Annotated 元数据，识别 reducer、LastValue 或其他通道", "direction": "字段级类型标注进入底层 channel"},
            {"file": "langgraph/runtime.py", "symbol": "Runtime", "role": "向节点暴露运行时 context、store、stream_writer 等环境能力", "direction": "节点可读 context，但不应把它当作 state 更新"},
            {"file": "langgraph/graph/message.py", "symbol": "add_messages", "role": "消息列表常用 reducer，追加新消息或按 id 替换旧消息", "direction": "Annotated[list[AnyMessage], add_messages] 驱动 messages 合并"},
        ]
    )
    + r"""
<h2>状态流：节点返回一条 AIMessage 后发生什么</h2>
"""
    + shell.state_flow(
        [
            ("schema 声明", "State 声明 messages 字段，并用 Annotated 绑定 add_messages。", "messages: Annotated[list[AnyMessage], add_messages]"),
            ("节点接收快照", "model 节点拿到当前 state，其中 messages 已包含用户消息和之前的工具结果。", "state['messages'] -> list[AnyMessage]"),
            ("节点返回增量", "节点不返回整份 state，只返回自己新增的一条 AIMessage。", "return {'messages': [AIMessage('ok')]}"),
            ("reducer 合并", "add_messages 读取旧 messages 和新增列表，按 id 替换或追加。", "old + new -> merged messages"),
            ("下一节点可见", "合并后的 state 进入下一步路由或节点。", "state['messages'] includes AIMessage('ok')"),
        ]
    )
    + r"""
<h2>Trace：partial update 与 reducer 的分工</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. 初始输入", "input": "{'messages': [HumanMessage('hi')]} ", "action": "输入 schema 校验/规范化后写入 messages channel", "output": "state.messages 有一条用户消息"},
            {"step": "2. model 节点", "input": "完整 state 快照", "action": "节点调用模型并返回 {'messages': [AIMessage('ok')]} ", "output": "一份 partial update，而不是整份 state"},
            {"step": "3. channel update", "input": "旧 messages + 新 AIMessage", "action": "add_messages 作为 reducer 处理列表合并", "output": "messages=[HumanMessage('hi'), AIMessage('ok')]"},
            {"step": "4. context 读取", "input": "runtime.context={'user_id': 'u1'}", "action": "节点可用 context 选择权限或租户配置", "output": "context 不写入 state，除非显式返回某个 state key"},
            {"step": "5. 输出过滤", "input": "最终内部 state", "action": "output_schema 可限制最终暴露哪些 key", "output": "调用者只看到约定输出"},
        ]
    )
    + r"""
<h2>简化源码走读：schema 怎样变成 channel</h2>
"""
    + shell.code_walkthrough(
        "langgraph/graph/state.py",
        "_get_channel",
        """def _get_channel(name, annotation):
    if has_reducer(annotation):
        return BinaryOperatorAggregate(annotation, reducer)
    if is_managed_value(annotation):
        return ManagedValueSpec(...)
    return LastValue(annotation)

class StateGraph:
    def __init__(self, state_schema, *, context_schema=None):
        self.schemas[state_schema] = _get_channels(state_schema)
        self.context_schema = context_schema
""",
        "教学版把真实分支压缩成三类：字段带 reducer 就用聚合通道；特殊管理值走 managed value；普通字段默认 LastValue 覆盖。这个转换解释了为什么 schema 不是注释，而是运行时合并语义。",
    )
    + r"""
<h2>Schema 是图的公共合同</h2>
"""
    + _h3("一、TypedDict、Pydantic、dataclass 都是在声明形状", "LangGraph 不要求你只用一种 Python 类型来描述 state。TypedDict 轻量、直观，适合教程和多数业务图；Pydantic 适合需要字段校验、默认值和更强结构约束的场景；dataclass 适合已有面向对象数据模型的项目。选择哪一种不是审美问题，而是团队希望在类型检查、运行时校验和可读性之间怎样取舍。关键是：schema 必须让节点作者知道可以读写哪些 key。")
    + _h3("二、State 和 context 的边界", "state 是会随节点执行而演化的数据，例如 messages、draft、tool_results、risk_score、需要人工确认的字段。context 是一次运行的环境，例如 user_id、tenant_id、权限、模型配置、数据库连接提示或实验分组。context 可以影响节点怎么做，但它不是图的业务历史。把 context 塞进 state 会污染 checkpoint；把 state 塞进 context 会让数据流不可见。")
    + _h3("三、input/output/private state", "一个图内部可能维护很多 key，但调用者不一定都要提供或看到。input_schema 可以收窄入口需要的数据，output_schema 可以限制最终返回的视图，内部私有 state key 则服务于中间节点协作。这样设计能避免把内部实现暴露成公共 API。例如客服图内部有 retrieved_docs、tool_attempts、moderation_notes，最终输出可能只需要 messages 和 final_answer。")
    + _h3("四、partial update 是节点协作的最小单位", "节点返回 partial state，有两个收益。第一，节点只声明自己改变了什么，读起来更像事件日志；第二，运行时可以精确知道哪些 key 有更新，从而让 reducer、checkpoint、并行冲突处理都有依据。返回整份 state 会掩盖真正变化，还可能把旧值误写回去。尤其在并行分支里，整份 state 返回常常制造难以解释的覆盖。")
    + _h3("五、默认覆盖不是追加", "如果一个字段没有 reducer，通常语义是 LastValue：新值覆盖旧值。这对 draft、current_step、final_answer 这类单值字段很合理；对 messages、logs、documents 这类累积字段就危险。很多初学者以为返回 {'messages': [AIMessage('ok')]} 会自动追加到旧列表；实际是否追加取决于 schema 是否绑定 add_messages 或其他 reducer。")
    + _h3("六、add_messages 不是普通 list.extend", "add_messages 的特别之处在于消息 id。没有相同 id 时，它表现得像追加；有相同 id 时，它会替换旧消息。这让工具调用、消息修正和流式合并更可控。把它理解成简单 append 会漏掉“按 id 更新”的能力，也会在重复 tool_call_id 或手动构造消息 id 时踩坑。")
    + _h3("七、schema 也是调试文档", "一个清楚的 State schema 能让后来的人不用读所有节点也知道图在维护什么。messages 表示对话历史，next_action 表示路由意图，tool_results 表示工具产物，needs_human 表示是否中断给人审。命名越接近业务含义，trace 越容易读。反过来，如果 state 里全是 data、result、temp，就算图能跑，调试也会像猜谜。")
    + _h3("八、不要原地修改 state", "节点里写 state['messages'].append(...) 看似和返回 {'messages': [...]} 等价，但它绕开了更新记录和 reducer。运行时无法可靠知道这是一次有意写入，还是你临时改了输入对象。更糟的是，在并行、重试或 checkpoint 场景中，原地修改会让状态快照失真。把 state 当只读输入，把返回值当唯一写入，是最稳的工程纪律。")
    + _h3("九、schema 控制的是图状态，不是所有函数参数", "节点仍然可以接受 runtime、config 或通过闭包捕获模型和工具。schema 不负责描述模型对象或数据库连接对象；它负责描述会进入图状态、被 checkpoint、被节点共享的业务数据。这个边界能防止把不可序列化对象写入状态，也让持久化只保存真正需要恢复的内容。")
    + _h3("十、运行时上下文要显式命名", "context_schema 的好处是让节点依赖的环境数据也有合同。比如 Runtime[Context] 中的 context 可以包含 user_id 和 permissions。节点读 runtime.context['user_id'] 时，读者知道这是运行上下文，而不是 messages 里的一条业务消息。这样的显式分离也方便测试：同一份 state 可以在不同 context 下跑出不同授权行为。")
    + _h3("十一、私有 key 不等于乱放临时变量", "内部状态 key 可以不暴露给图的最终输出，但仍然应被 schema 管理。临时草稿、检索候选、评估分数都可以是私有 state；它们依旧要有类型、合并语义和命名。私有只表示 API 不公开，不表示可以绕过状态系统。")
    + _h3("十二、schema 设计先于节点实现", "写图之前先列 state keys，能迫使你思考数据生命周期：谁创建，谁读取，谁更新，是否累积，是否需要出现在最终输出，是否应该 checkpoint。很多 LangGraph 设计问题，其实在 schema 阶段就能发现。例如两个节点都要写同一个 list，却没有 reducer；路由函数需要 step_count，却没有任何节点维护它。")
    + _h3("十三、最小心智模型", "State schema 是图的类型合同和合并合同。类型告诉节点“有什么”；reducer 告诉运行时“同一个 key 的多次更新怎么合并”；context_schema 告诉节点“这次运行在什么环境里”；input/output schema 告诉外部调用者“入口和出口长什么样”。把这四层分清，状态图才不会退化成一堆共享变量。")
    + r"""
<h2>扩展复盘：如何设计一份耐用的 State schema</h2>
<p>设计 state 时，先不要写代码，而是列数据生命周期。每个 key 都问四个问题：谁创建它，谁读取它，谁更新它，什么时候它不再需要。messages 由入口和模型、工具节点持续追加，几乎贯穿全图；retrieved_docs 可能只在检索和回答之间短暂存在；final_answer 只在最后覆盖一次；needs_human 可能由风险节点设置，再由人工节点清除。把生命周期写清楚，schema 的类型、reducer 和输出边界自然会清楚。</p>
<p>第二步是区分“事实”和“过程”。订单号、用户问题、工具结果属于业务事实；tool_attempts、last_error、route_reason 属于过程记录。事实常常需要进入最终回答或 checkpoint；过程记录主要服务调试、限流、重试和人工审核。两类数据都可以是 state，但命名要让读者知道它的用途。不要把所有中间变量都叫 result，也不要把过程控制藏在 messages 的自然语言文本里。</p>
<p>第三步是给累积字段选择合并策略。messages 用 add_messages，因为它有消息 id 和工具调用语义；audit_events 可能需要 append 并带时间和来源；retrieved_docs 可能需要按 document_id 去重；risk_scores 可能需要取最大值或保留按来源分组的 dict。每个策略都反映业务含义。最糟糕的做法是看到 list 就统一 operator.add，短期解决报错，长期制造重复、乱序和难以解释的状态。</p>
<p>第四步是决定哪些 key 属于输入、输出和私有内部状态。外部调用者不应该被迫提供内部重试计数，也不一定需要看到检索候选和评分细节。input_schema 可以让入口更窄，output_schema 可以让返回值更稳定，内部 schema 则保留实现自由。这样以后你更换检索策略、增加风控节点或调整工具重试，不会破坏调用方契约。</p>
<p>最后要把 context_schema 当成环境合同来审查。只要某个值描述“这次运行在哪个租户、哪个用户、什么权限、什么实验配置下发生”，它通常属于 context；只要某个值是节点产物、业务历史或后续节点要合并的内容，它属于 state。这个边界清楚后，checkpoint 才不会保存不该保存的环境对象，测试也能用同一份 state 搭配不同 context 验证授权和个性化行为。</p>
<p>耐用 schema 的目标不是把所有可能字段一次性设计完，而是让当前字段有清楚语义，并为后续扩展留下边界。新增 key 时，先写一句说明：为什么需要它，谁写它，谁读它，是否累积，是否输出。这个习惯比复杂类型技巧更重要，因为 LangGraph 的很多线上问题，根源不是 Python 类型写错，而是团队没人说清楚某个 key 代表什么。</p>
<h2>案例推演：客服 Agent 的 schema 评审</h2>
<p>假设你要设计订单客服图，第一次评审 schema 时可以把白板分成四栏：入口、内部、输出、上下文。入口可能只有 messages 和可选 order_id；内部包括 retrieved_docs、tool_attempts、last_tool_error、risk_flags、draft_answer；输出包括 messages、final_answer、needs_human；上下文包括 user_id、tenant_id、locale、permissions。这样一分，团队立刻能看出哪些数据来自调用方，哪些数据只是图内部协作，哪些数据会暴露给外部。</p>
<p>接着审查每个 key 的更新者。messages 会被入口、model、tools 写；tool_attempts 会被工具节点写；risk_flags 由风控节点写；draft_answer 由模型节点覆盖；final_answer 由 finalize 节点覆盖。一个 key 如果没有明确写入者，可能是多余的；如果有太多写入者，可能需要拆分或增加 reducer。schema 评审的目标不是追求字段越少越好，而是让每个字段都有主人和生命周期。</p>
<p>第三步审查合并语义。messages 用 add_messages，tool_attempts 可以按工具调用 id 去重追加，risk_flags 可以用集合并集，draft_answer 和 final_answer 用 LastValue，last_tool_error 也可以覆盖。retrieved_docs 则要看业务：如果多个检索节点并行，可能按 document_id 去重并按分数排序；如果只有一个检索节点，每次覆盖当前候选就足够。合并语义必须来自业务，而不是来自字段类型。</p>
<p>第四步审查 checkpoint 价值。哪些 key 是恢复时必须保留的？messages、tool_attempts、needs_human 通常需要；临时 prompt 片段、模型对象、数据库连接不应该进入 state。这个问题能帮助你把不可序列化对象排除出去，也能减少 checkpoint 体积。记住：能写进 state 的，不一定都应该长期保存；应该保存的，必须有清晰类型和语义。</p>
<p>第五步审查隐私和权限。user_id 放 context 并不表示它不重要，而是它描述运行环境。订单详情、用户输入、工具结果如果进入 state，就可能被 checkpoint 保存，需要考虑脱敏、保留周期和访问控制。schema 设计不是纯技术细节，它决定哪些数据会出现在 trace、存档和调试页面。越早明确，越少后续合规返工。</p>
<p>最后，把 schema 当成团队接口文档。节点作者按它返回 partial update，测试作者按它构造状态，运维排障按它读 checkpoint，产品讨论按它理解流程。一个好的 State schema 不需要很花哨，但必须命名稳定、合并语义明确、context/state 边界清楚。只要这份合同稳，图的节点可以逐步演进；合同含糊，节点越多越难维护。</p>
<h2>进一步练习：用 schema 反推节点设计</h2>
<p>拿到一份 schema 后，可以反过来检查节点是否合理。每个节点最多应关注少数几个输入 key，并只写自己承诺的输出 key。如果一个节点读取几乎所有 state，又写回许多无关字段，说明它可能承担了多个职责。把这种节点拆开，通常会让 reducer 选择更简单，路由条件也更清楚。schema 不是写完就放着的类型声明，它是评审节点边界的工具。</p>
<p>还可以用 schema 设计测试夹具。为 messages 构造最小历史，为 retrieved_docs 构造空列表、重复文档和高分文档，为 needs_human 构造 True/False 两种状态。节点测试不需要真实跑完整图，只要给定这些状态样本，检查 partial update 是否符合合同。这样测试能直接保护 schema 语义，而不是只验证最终页面有没有文本。</p>
<p>当需求变化时，先改 schema 说明再改节点。比如新增“用户情绪”能力，不要直接在某个节点里塞一个 sentiment 临时字段；先决定它是当前值还是历史，谁负责写，是否输出，是否影响路由，是否需要 checkpoint。这个顺序能避免临时字段扩散成隐形公共接口。很多长期维护成本，都是从一个没有评审的临时 key 开始的。</p>
<p>最后，把 schema 文档和源码引用放在一起复查。StateGraph.__init__ 告诉你图接收哪些 schema，_get_channel 告诉你字段会落到什么通道，Runtime 告诉你 context 怎样进入节点，add_messages 告诉你消息列表怎样合并。只要这四个证据能支撑你的设计，schema 就不是凭感觉写出来的，而是和运行时机制对齐的合同。</p>
<p>补充检查：schema 合同要覆盖“初始、运行中、结束后”三个状态。初始 state 里哪些 key 可缺省，运行中哪些 key 只能由内部节点写，结束后 output_schema 暴露哪些 key，都应写清楚。否则同一个字段可能在入口被调用方误传，在中途被节点覆盖，最后又被外部依赖，合同边界会迅速失控。</p>
<p>context/state 边界也要反复复查。user_id、tenant_id、permissions、实验开关描述运行环境，适合随 Runtime context 注入；messages、retrieved_docs、needs_human、final_answer 描述业务演化，适合进入 state。把环境写进 state 会污染 checkpoint，把业务历史藏进 context 会让 trace 看不见关键变化。边界清楚，恢复、测试和权限审查才有共同语言。</p>
<p>状态演进要像版本化 API 一样对待。新增 key 时说明默认值、写入者、读取者、合并语义和输出可见性；删除或改名 key 时检查旧 checkpoint、旧测试夹具和下游调用者。LangGraph 的 state 不是临时 dict，而是节点之间的公共合同。合同越稳定，图越容易迭代。</p>
<p>本课可以用一句话收束：schema 先定义工程边界，再允许模型在边界内产生不确定输出。模型文本可能变化，但 state key 的含义、context 的来源、partial update 的目标和 reducer 的选择必须稳定。把这份合同写清，后续节点、边和运行时才有可靠基础。</p>
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("节点可以直接 append state['messages']", "把 state 当只读输入；返回 partial update，让 add_messages 记录和合并更新。"),
            ("返回整份 state 更保险", "返回整份 state 会制造覆盖和噪声；节点应只返回自己产生的 key。"),
            ("context 和 state 都是 dict，随便放", "context 是运行环境，state 是业务演化数据；混用会破坏 checkpoint 和可读性。"),
            ("list 字段天然会累积", "没有 reducer 的字段默认通常是 LastValue 覆盖；累积列表要显式声明 reducer。"),
        ]
    )
    + r"""
<h2>小实验</h2>
"""
    + shell.lab_card(
        "为客服图设计 State schema",
        [
            "列出入口需要的 key：用户问题、已有 messages、可能的订单号。",
            "列出内部 key：retrieved_docs、tool_attempts、needs_human、draft_answer，并标注哪些只在内部使用。",
            "判断每个 key 的合并语义：messages 用 add_messages，tool_attempts 可以累加，final_answer 用覆盖。",
            "把 user_id、tenant_id、permissions 放入 context_schema，再解释为什么它们不应作为普通 state 历史保存。",
        ],
    )
    + shell.version_note("本课使用的 StateGraph.__init__、_get_channels、_get_channel、Runtime、add_messages 是理解 v1 时代 LangGraph state contract 的稳定入口。具体 schema 参数名可能演进，但 state/context 分离、partial update 和 reducer 合并这三条规则应优先记住。")
    + _points([
        "State schema 是图的合同，定义 state key、类型和合并语义。",
        "TypedDict、Pydantic、dataclass 都可表达 schema，选择取决于校验和可读性需求。",
        "context_schema 描述运行环境，不应和会 checkpoint 的业务 state 混淆。",
        "节点返回 partial update；list 累积必须显式声明 reducer，例如 add_messages。",
        "原地修改 state 和返回整份 state 都会削弱可追踪、可并行和可恢复能力。",
    ])
)


LESSON_19_NODES_EDGES = (
    r"""
<p class="lead">节点和边是 LangGraph 最像“图”的部分，但它们真正表达的是两种责任：节点负责把当前 state 转成 partial state，边负责决定下一步去哪。普通边给出固定顺序，条件边把路由函数纳入图结构，START 和 END 则标出入口与终点。本课用工具循环拆解 add_node、add_edge、add_conditional_edges 的心智模型，重点不是记 API，而是知道业务逻辑、路由逻辑和副作用应该分别放在哪里。</p>
"""
    + _analogy("把节点想成工厂里的工位，工人拿到半成品和工单，只完成自己那一步并贴上一张新标签；边像传送带，决定半成品下一站送到哪里。普通传送带永远通向固定工位，分拣传送带会读标签后选择路线。START 是收货口，END 是出货口。最危险的工厂，是工人一边加工一边偷偷改传送带规则，最后谁也不知道货为什么绕圈。")
    + shell.lesson_map(
        "本课地图：节点做事，边选路",
        [
            ("节点契约", "add_node 注册 state -> partial state 的可运行步骤", "now"),
            ("普通边", "add_edge 表达固定后继关系，例如 START -> model", "now"),
            ("条件边", "add_conditional_edges 用路由函数把 state 映射到节点名或 END", "source"),
            ("工具循环", "model -> route_tools -> tools 或 END；tools 再回 model", "now"),
            ("下一课", "多个节点写同一 key 时要靠 reducer/channel 合并", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>节点边相关源码适合按“注册节点、连接边、动态路由、特殊端点”的顺序读。下面的文件 + 符号名就是本课所有结论的证据锚点。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/graph/state.py", "symbol": "StateGraph.add_node", "role": "把函数、Runnable 或节点规格注册进状态图，并绑定节点名", "direction": "用户定义业务步骤，compile 时被包装成 Pregel 节点"},
            {"file": "langgraph/graph/state.py", "symbol": "StateGraph.add_edge", "role": "声明一个固定后继关系，当前节点完成后调度目标节点", "direction": "START、普通节点和 END 之间建立静态路径"},
            {"file": "langgraph/graph/state.py", "symbol": "StateGraph.add_conditional_edges", "role": "注册路由函数和可选路径映射，让 state 决定下一跳", "direction": "运行时调用 route 函数，返回节点名、END 或映射键"},
            {"file": "langgraph/constants.py", "symbol": "START", "role": "虚拟入口常量，供 add_edge 等图结构 API 标记初始边界", "direction": "START -> first_node，运行时从入口边接收初始 state"},
            {"file": "langgraph/constants.py", "symbol": "END", "role": "虚拟终点常量，供普通边或条件边标记运行完成", "direction": "route 返回 END 或边指向 END 后结束本次图运行"},
        ]
    )
    + r"""
<h2>调用图：工具循环的节点和边</h2>
"""
    + shell.call_graph(
        [
            ("START", "入口把初始 messages 写入 state", True),
            ("model", "节点读取 state，返回 AIMessage partial update", False),
            ("route_tools", "条件边函数检查最后一条消息", False),
            ("tools 或 END", "有 tool_calls 去 tools；否则结束", True),
            ("tools -> model", "工具写回 ToolMessage，再把控制权交还模型", False),
        ]
    )
    + r"""
<h2>Trace：START -> model -> route_tools -> tools or END -> model</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. START", "input": "初始 {'messages': [HumanMessage(...)]}", "action": "虚拟入口把输入交给第一条边", "output": "下一节点 model"},
            {"step": "2. model", "input": "state.messages", "action": "模型节点生成 AIMessage，可能包含 tool_calls", "output": "partial messages 更新"},
            {"step": "3. route_tools", "input": "最后一条 AIMessage", "action": "条件边函数返回 'tools' 或 END", "output": "选择下一跳"},
            {"step": "4a. tools", "input": "tool_calls", "action": "工具节点执行副作用并返回 ToolMessage", "output": "tools -> model 回边"},
            {"step": "4b. END", "input": "无 tool_calls 的 AIMessage", "action": "图运行结束", "output": "最终 state 返回调用者"},
        ]
    )
    + r"""
<h2>简化源码走读：注册和路由</h2>
"""
    + shell.code_walkthrough(
        "langgraph/graph/state.py",
        "StateGraph.add_conditional_edges",
        """builder.add_node('model', call_model)
builder.add_node('tools', tool_node)
builder.add_edge(START, 'model')
builder.add_conditional_edges('model', route_tools, {'tools': 'tools', END: END})
builder.add_edge('tools', 'model')

def route_tools(state):
    last = state['messages'][-1]
    return 'tools' if last.tool_calls else END
""",
        "教学版把 API 用法和路由函数放在一起：节点产生消息，条件边只做去向判断，工具节点完成后用普通边回到模型。真实源码会校验节点名、路径映射和图连通性。",
    )
    + r"""
<h2>节点：state -> partial state</h2>
"""
    + _h3("一、节点不是任意回调", "一个 LangGraph 节点最重要的签名是读取当前 state，返回 partial state。它可以内部调用模型、检索器、工具、数据库或另一个 Runnable，但对图运行时暴露的是统一形状：这一步根据 state 产生了哪些更新。只要节点遵守这个形状，它的内部实现就可以替换，测试时也可以用 fake model 或 fake tool。")
    + _h3("二、节点命名是公共接口", "add_node 的名字不只是调试标签，还是边和路由返回值会引用的目的地。名字应该稳定、语义明确，例如 model、tools、retrieve、grade、human_review，而不是 node1、tmp、lambda。条件边返回错名字时，图不是“猜一下你想去哪”，而是应该在校验或运行时失败。好的命名会让 trace 像流程图，坏命名会让 trace 像乱码。")
    + _h3("三、节点可以是函数也可以是 Runnable", "StateGraph.add_node 常见输入是普通函数，但 LangGraph 也能包装 Runnable 或更复杂的节点规格。这让前面学过的 LangChain 组件可以进入图：一个 LCEL 子链可以成为节点，一个模型绑定可以成为节点，一个工具集合可以成为节点。图不是抛弃 Runnable，而是把 Runnable 放进有状态控制流里。")
    + _h3("四、普通边表达确定顺序", "add_edge 适合没有条件的路径：START 后总是 model，tools 后总是 model，retrieve 后总是 grade。普通边越多，流程越稳定；条件边越多，流程越动态。不要为了显得灵活把所有边都写成条件边，如果下一步永远相同，普通边更清楚，也更容易被编译期校验。")
    + _h3("五、条件边表达路由，不表达业务副作用", "路由函数应该尽量纯：观察 state，返回下一跳。它不应调用外部 API，不应写数据库，不应修改 state，不应偷偷发送邮件。原因很简单：路由函数可能被重试、被调试、被可视化假设为无副作用；如果它里面藏了副作用，图的行为就很难复现。业务动作放节点，去向判断放条件边。")
    + _h3("六、START 和 END 是边界符号", "START 不是一个你实现的函数，而是图的虚拟入口；END 不是普通节点，而是运行完成的标记。把它们当作边界符号，可以避免给入口和出口写多余节点。START 的后继通常是第一个业务节点，END 通常由条件边返回或普通边指向。看到 START/END，就知道图的生命周期从哪里开始、在哪里闭合。")
    + _h3("七、工具循环为什么适合条件边", "模型是否调用工具，是运行时才知道的事。prompt、用户问题、模型能力、工具结果都会影响最后一条 AIMessage。条件边把这个运行时决策显式化：route_tools 只看最后消息，有 tool_calls 去 tools，没有就 END。这样模型节点不用知道工具节点怎么连，工具节点也不用知道什么时候结束。")
    + _h3("八、无限循环通常来自边而不是模型", "模型可能不断请求工具，但真正让图无限跑的是边允许它一直回到 model，且路由没有终止策略。解决办法不是只骂模型，而是给图加结构约束：最大工具轮数、错误计数、已调用同一工具同一参数的检测、无新信息时 END、人审节点或 recursion_limit。循环是图能力，终止是图责任。")
    + _h3("九、路由返回值要和路径映射一致", "add_conditional_edges 可以让 route 返回真实节点名，也可以通过 path_map 把业务标签映射到节点。无论哪种方式，返回值都必须可解析。常见错误是 route 返回 'tool'，实际节点叫 'tools'；或者返回 True/False，却没有提供 {True: 'tools', False: END} 映射。把路由返回类型写窄、测试覆盖每个分支，能减少这类低级错误。")
    + _h3("十、节点返回非 dict 的问题", "StateGraph 节点应返回符合 state 更新语义的 mapping。返回字符串、AIMessage 本体、list 或 None，通常会让运行时不知道写哪个 state key。即使只有一个 messages 字段，也要返回 {'messages': [message]}。这种冗余是有价值的，因为它让写入目标显式，reducer 也能按 key 工作。")
    + _h3("十一、边把架构意图写出来", "从代码审查角度看，边比节点更能暴露系统设计。节点里是一段实现，边展示实现之间的控制关系。START -> model -> route -> tools -> model 说明这是工具 Agent；retrieve -> grade -> answer/rewriter 说明这是带质量评估的 RAG；human_review -> approve/reject 说明有人审分支。读图先读边，往往比先读节点内部更快理解系统。")
    + _h3("十二、测试节点和路由要分开", "节点测试关注给定 state 时返回什么 partial update；路由测试关注给定 state 时返回哪个节点名或 END。不要把模型调用、工具执行和路由判断混在一个黑盒测试里，否则失败时不知道是模型输出、工具副作用还是路由拼写错。把责任拆开，是 LangGraph 可测试性的主要来源。")
    + _h3("十三、最小心智模型", "节点是工位，边是传送带，条件边是分拣器，START/END 是收发货口。工位只贴自己新增的标签，分拣器只读标签决定方向，传送带不加工货物。只要这三个责任不混，复杂图也能保持清楚；一旦节点开始偷偷路由、路由开始偷偷写状态，图就会失去可解释性。")
    + r"""
<h2>扩展复盘：节点边界与路由纪律</h2>
<p>设计节点时，可以用“输入、动作、输出、失败”四栏检查。输入是它读取哪些 state key 和 context；动作是它调用模型、工具还是纯计算；输出是它返回哪些 partial update；失败是异常、重试或错误状态如何表达。一个节点如果读了十几个 key、调用三个外部系统、同时决定下一跳，通常已经太大。把它拆成多个节点后，边会多一些，但每一步的责任更清楚。</p>
<p>路由函数则要用另一套标准：它应该短、纯、可枚举。短，是因为路由只决定去向，不承载业务处理；纯，是因为同样 state 应该得到同样目的地，不应有随机数、网络请求或数据库写入；可枚举，是因为每个返回值都应能在测试里覆盖到。一个好的 route_tools 测试，至少包含有工具调用、无工具调用、消息为空、超过最大轮数、工具错误需要人审这几类状态。</p>
<p>节点名和路由返回值最好形成小型词汇表。比如 model、tools、human_review、finalize、error_handler，这些名字一眼能看出流程。不要让 route 返回模型生成的自然语言句子，再用字符串匹配猜下一跳；也不要把业务标签和节点名混在一起而没有 path_map。图的控制流应该尽量像有限状态机：状态集合明确，转移条件明确，非法转移能尽早失败。</p>
<p>START/END 的使用也能暴露设计质量。一个图如果有多个实际入口，可能需要先用一个 classify_input 节点把不同输入规范化，而不是从 START 直接连到很多复杂分支。一个图如果迟迟到不了 END，说明完成条件没有被建模。END 不是失败，而是“本次运行已经给出足够结果”。有时错误也应该走到一个 error_handler 节点整理消息后 END，而不是让异常在半路把用户体验炸掉。</p>
<p>副作用节点要特别谨慎。工具节点可能发邮件、扣款、查库、写工单。它们应该有幂等键、错误返回和可审计输出。路由函数绝不应该藏这些动作，因为路由在读图时会被当成判断逻辑。把副作用集中在节点，能让 checkpoint、重试和人工审核更可控；也能让代码审查者快速找到所有真正影响外部世界的地方。</p>
<p>当图变大时，先读边再读节点。边告诉你系统允许哪些状态转移，节点告诉你每个转移前后发生什么。一个边很复杂、返回值很多的条件路由，可能暗示应该拆出中间节点；一个节点有很多普通后继，可能暗示它其实在同时做分类和处理。用这套眼光复盘图结构，LangGraph 代码会越来越像清晰的流程规范，而不是另一种形式的意大利面。</p>
<h2>案例推演：把路由函数从“聪明”改成“可靠”</h2>
<p>很多初学者会把 route_tools 写得很“聪明”：让它重新调用模型判断要不要工具，查数据库确认工具是否可用，顺手记录一条审计日志，最后返回某个字符串。这样的函数短期看似集中，长期会变成不可测试的黑盒。可靠的路由函数应该更笨：只看当前 state 中已经存在的信息，例如最后一条消息、tool_rounds、last_tool_error、needs_human，然后返回有限集合里的一个目的地。</p>
<p>以工具循环为例，route_tools 可以先处理保护条件：如果 messages 为空，返回 END 或 error_handler；如果 tool_rounds 超过上限，返回 human_review；如果最后消息不是 AIMessage，返回 END；如果最后 AIMessage 没有 tool_calls，返回 END；否则返回 tools。这个顺序把异常形状、终止条件和正常工具分支分开，测试也能一一覆盖。路由不需要解释业务答案，它只需要做稳定转移。</p>
<p>节点和路由分离后，错误定位会简单很多。模型没有产生 tool_calls，是 model 节点的问题；tool_calls 参数不合法，是工具节点或模型提示的问题；route 返回了不存在的节点，是路由拼写或 path_map 问题；tools 执行失败后仍然回到 model，是错误分支缺失。每类问题都有明确责任，而不是全部混在一个“Agent 不工作”的症状里。</p>
<p>条件边的 path_map 可以让路由返回业务标签，而不是直接暴露节点名。例如 route 返回 'need_tool'、'done'、'blocked'，path_map 再映射到 tools、END、human_review。这样业务判断和图节点命名可以适度解耦。但无论是否使用 path_map，返回集合都应清楚、有限、可测试。不要让 route 返回任意模型文本，再靠模糊匹配决定下一跳。</p>
<p>当一个 route 函数分支越来越多时，可能说明图需要分层。先用 classify 节点写入 next_action，再用简单条件边根据 next_action 跳转；或把错误处理、人审处理、工具处理拆成多个局部路由。复杂路由不是罪，但它必须有结构。把所有 if 都堆在一个函数里，会让图表面清楚、内部混乱。</p>
<p>最后，边也需要测试。很多项目只测节点输出，不测 route 返回值，结果线上因为 'tool' 和 'tools' 这种拼写差异失败。给每个条件边写一组状态样本，是成本最低的保险。节点测试证明“这一步产出什么”，路由测试证明“产出之后去哪”，两者合起来才证明图能按预期流动。</p>
<h2>进一步练习：把边画成状态转移表</h2>
<p>除了画流程图，还可以把每条条件边写成状态转移表。表头写“当前节点、观察的 state、条件、下一节点、理由”。例如当前节点 model，观察最后一条 AIMessage；有 tool_calls 且 tool_rounds 小于 3，下一节点 tools；无 tool_calls，下一节点 END；tool_rounds 达上限，下一节点 human_review。转移表能暴露遗漏分支，也方便产品和后端一起评审。</p>
<p>转移表还能帮助你发现不该存在的边。如果某条边的理由写不清，只能说“可能以后会用”，最好先不要加。每条边都会扩大图的状态空间，也会增加测试组合。LangGraph 的灵活性很强，但工程上要控制可达路径数量。路径越多，越需要明确状态字段和终止条件，否则 trace 虽然完整，人却读不懂。</p>
<p>对工具循环，还要单独写失败转移。工具参数缺失、工具超时、工具返回权限错误、工具结果为空，这些状态不应该全部回到 model 让模型猜。可以让工具节点写 last_tool_error 和 tool_attempts，再由条件边选择 retry、human_review、error_handler 或 END。失败路径越显式，用户体验越稳定，副作用也越可控。</p>
<p>最后，用 START/END 检查整图连通性。每个业务节点都应该能从 START 到达，也应该在合理条件下走向 END 或错误终点。如果一个节点只能进入不能退出，通常是漏边；如果一个节点永远不可达，通常是旧设计残留。把这项检查放进代码评审，比等运行时发现“某分支永远没触发”更省成本。</p>
<p>补充检查：每个条件边都应有一组最小样本状态，能证明所有返回值都可达且合法。样本不需要真实模型输出，可以手写 AIMessage、ToolMessage 或错误标记。这样做的好处是把路由从模型不确定性中解耦出来：即使模型偶尔输出奇怪内容，图的控制层仍然有可预测的保护分支和终止路径。</p>
<p>路由可靠性的核心，是返回值集合要小而稳定。route_tools 不应返回模型自然语言，也不应把布尔、节点名和业务标签混着用。要么直接返回 tools、END、human_review 这样的合法目的地，要么返回 need_tool、done、blocked 这样的业务标签并用 path_map 明确映射。每个返回值都应能在代码审查中被追到一条边。</p>
<p>测试路由函数时，不要依赖真实模型刚好生成某种 tool_calls。构造最小 state：空 messages、最后消息无工具、最后消息有工具、工具轮数超限、工具错误需要人工。对每个样本断言返回值和 path_map 都合法。这样即使节点内部 prompt 后来改变，控制层仍然能保证不会跳到不存在的节点或漏掉终止条件。</p>
<p>节点和边的收束原则是：节点负责产出事实，路由负责根据事实选择去向。只要 route 函数保持纯、短、可枚举，复杂 Agent 的控制流就能被单独理解和验证。反之，如果路由一边调用模型一边写审计再返回任意字符串，图看起来有结构，实际仍然是不可测试的黑盒。</p>
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("route 返回随便一个字符串，图会自动找到", "返回值必须是有效节点名、END，或能被 path_map 映射的键。"),
            ("节点可以直接返回 AIMessage", "StateGraph 节点应返回 dict partial update，例如 {'messages': [AIMessage(...)]}。"),
            ("tools -> model 回边天然安全", "任何回边都需要终止条件、计数或错误分支，避免无界循环。"),
            ("路由函数里顺手调工具", "路由应尽量无副作用；外部调用放节点，路由只决定下一跳。"),
        ]
    )
    + r"""
<h2>小实验</h2>
"""
    + shell.lab_card(
        "设计 route_tools 函数",
        [
            "写三个测试状态：最后消息有 tool_calls、没有 tool_calls、messages 为空或最后消息不是 AIMessage。",
            "让 route_tools 对有工具调用返回 'tools'，对无工具调用返回 END，对异常形状返回 END 或错误节点。",
            "故意把节点名写成 'tool'，观察校验或运行时错误，再改回 'tools'。",
            "给 state 增加 tool_rounds，并让 route 在超过 3 次时返回 END 或 human_review。",
        ],
    )
    + shell.version_note("本课锚定 StateGraph.add_node、StateGraph.add_edge、StateGraph.add_conditional_edges、START、END。未来 API 可能增加更丰富的控制流原语，但“节点做状态更新，边做控制转移”的边界仍是读图的第一原则。")
    + _points([
        "节点是 state -> partial state 的可测试步骤；边是节点之间的控制关系。",
        "普通边适合固定顺序，条件边适合运行时路由。",
        "START/END 是虚拟边界，标出图的入口和终点。",
        "工具循环的核心路径是 START -> model -> route_tools -> tools 或 END，tools 再回 model。",
        "路由函数应避免副作用，返回值必须匹配节点名或 path_map。",
    ])
)


LESSON_20_REDUCERS_CHANNELS = (
    r"""
<p class="lead">Reducer 和 channel 是 LangGraph 状态系统的地下管道：上层看到的是 state key，底层真正决定“多个更新怎样合并”的是 channel。普通字段默认像 LastValue，新值覆盖旧值；消息列表常用 Annotated[list[AnyMessage], add_messages]，让新消息追加或按 id 替换；并行分支同时写同一 key 时，是否冲突、能否合并、顺序是否重要，都取决于 reducer。本课把 reducer 当成状态键的合并法律来读。</p>
"""
    + _analogy("把每个 state key 想成一条收件通道。LastValue 像白板，后来的人擦掉前面的字；Topic 像公告栏，可以收集多张便签；BinaryOperatorAggregate 像会计账本，每笔收入按加法汇总；add_messages 像聊天记录管理员，看到新 id 就追加，看到旧 id 就更新那条记录。你不能只说“我要写 messages”，还要说“这条通道收到多份更新时按什么规矩办”。")
    + shell.lesson_map(
        "本课地图：state key 下面的合并语义",
        [
            ("默认覆盖", "没有 reducer 的普通字段通常落到 LastValue，新值覆盖旧值", "now"),
            ("显式 reducer", "Annotated[list[AnyMessage], add_messages] 把字段变成消息合并通道", "source"),
            ("并行 fan-in", "两个节点同一轮写同一 key 时，channel 决定冲突还是合并", "now"),
            ("通道类型", "LastValue、Topic、BinaryOperatorAggregate 分别代表不同更新语义", "source"),
            ("下一课", "compile 会把 schema、channel、节点包装成可运行 Pregel 图", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>Reducer 不只是 Python 函数，它会通过 schema 解析落到底层 channel。下面这些文件 + 符号名把 add_messages、LastValue、Topic、BinaryOperatorAggregate 和 _get_channel 串成一条证据链。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/graph/message.py", "symbol": "add_messages", "role": "消息列表 reducer，按消息 id 替换或追加，适合 chat history", "direction": "State 字段 Annotated 后被 channel 调用"},
            {"file": "langgraph/channels/last_value.py", "symbol": "LastValue", "role": "默认单值通道，通常每轮只接受一个最终值，新值覆盖旧值", "direction": "普通 state key 未声明 reducer 时使用"},
            {"file": "langgraph/channels/topic.py", "symbol": "Topic", "role": "收集多条更新的发布/订阅式通道，可用于多值 fan-in", "direction": "多个节点写入后按通道规则聚合"},
            {"file": "langgraph/channels/binop.py", "symbol": "BinaryOperatorAggregate", "role": "用二元操作把多次更新折叠成一个值，例如加法或列表拼接", "direction": "Annotated reducer 常被落实成聚合通道"},
            {"file": "langgraph/graph/state.py", "symbol": "_get_channel", "role": "从字段注解中识别 reducer 或默认通道类型", "direction": "schema 层合并声明进入运行时 channel"},
        ]
    )
    + r"""
<h2>状态流：两个节点同时写同一个 key</h2>
"""
    + shell.state_flow(
        [
            ("并行分支产生更新", "node_a 和 node_b 在同一轮都返回 {'notes': [...]} 或 {'score': ...}。", "A -> {'notes': ['a']} / B -> {'notes': ['b']}"),
            ("LastValue 场景", "如果 key 是默认 LastValue，同一轮多个值可能冲突，因为通道不知道怎样安全合并。", "notes: LastValue[list[str]] -> conflict/overwrite risk"),
            ("Reducer 场景", "如果 key 声明了 reducer，运行时按 reducer 折叠多份更新。", "notes: Annotated[list[str], operator.add]"),
            ("消息场景", "messages 使用 add_messages，新 id 追加，重复 id 替换。", "add_messages(old, [AIMessage(id='1')])"),
            ("下一步可见", "合并结果在下一轮对下游节点可见，而不是让并行节点互相读半成品。", "merged state for next step"),
        ]
    )
    + r"""
<h2>Trace：LastValue 冲突 vs reducer merge</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. fan-out", "input": "state={'query': '退款'}", "action": "两个分析节点并行运行", "output": "risk_node 和 policy_node 各自产生更新"},
            {"step": "2. LastValue", "input": "risk_node -> {'notes': ['高风险']}；policy_node -> {'notes': ['需人工']} ", "action": "notes 没有 reducer，通道无法表达安全追加", "output": "冲突或最后值覆盖，历史可能丢失"},
            {"step": "3. reducer", "input": "notes: Annotated[list[str], operator.add]", "action": "BinaryOperatorAggregate 折叠两份 list", "output": "notes=['高风险', '需人工']"},
            {"step": "4. add_messages", "input": "old=[AIMessage(id='a')] new=[AIMessage(id='a', content='修正')]", "action": "按 id 替换旧消息", "output": "只有 id='a' 的新版本"},
            {"step": "5. 下游", "input": "合并后的 notes/messages", "action": "answer 节点读取稳定结果", "output": "可解释、可复现的下一步 state"},
        ]
    )
    + r"""
<h2>简化源码走读：Annotated reducer 落到 channel</h2>
"""
    + shell.code_walkthrough(
        "langgraph/graph/state.py",
        "_get_channel",
        """class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    answer: str

# compile/build channels
channels = {
    'messages': BinaryOperatorAggregate(list[AnyMessage], add_messages),
    'answer': LastValue(str),
}

# update step
channels['messages'].update([[AIMessage(id='m1', content='ok')]])
channels['answer'].update(['最终答案'])
""",
        "教学版展示字段到通道的映射：messages 因 Annotated reducer 变成聚合语义；answer 没有 reducer，所以是覆盖语义。真实实现还会处理 managed value、类型校验和多轮更新。",
    )
    + r"""
<h2>Reducer 是每个 key 的合并法律</h2>
"""
    + _h3("一、默认覆盖适合单值事实", "LastValue 并不是坏设计。很多 state key 的正确语义就是“当前值”：final_answer、current_node_label、selected_tool、approval_status、error_message。对这些字段，追加历史反而会让下游困惑。默认覆盖的价值是简单、明确、节省存储。问题出在你把需要累积的字段也交给默认覆盖。")
    + _h3("二、列表不会因为是列表就自动追加", "Python 类型是 list 只说明值的形状，不说明更新语义。一个 list 字段可能表示“当前候选文档列表”，每次检索都覆盖；也可能表示“所有已执行工具记录”，每次都追加。只有业务知道哪个语义正确，所以 schema 必须通过 Annotated reducer 讲清楚。不要期待运行时从 list 推断你想 append。")
    + _h3("三、add_messages 的 id 语义", "聊天历史不是简单字符串数组。AIMessage、HumanMessage、ToolMessage 可能带 id、tool_call_id、metadata、usage。add_messages 让新消息在 id 不重复时追加，在 id 重复时替换旧消息。这支持流式修正、工具结果回填和消息去重。代价是你必须小心手动设置 id：重复 id 会被认为是更新而非新消息。")
    + _h3("四、并行分支让 reducer 变得必要", "在单线流程里，覆盖和追加的差异已经重要；在并行 fan-in 里，它会变成正确性问题。两个节点同一轮写同一个 key，如果没有合并法律，运行时不能凭空决定谁赢。你要么让它们写不同 key，要么为共享 key 声明交换律、结合律良好的 reducer，要么改图结构避免同轮冲突。")
    + _h3("五、BinaryOperatorAggregate 的直觉", "二元聚合通道像 reduce：拿旧值和新值，用一个函数合成更新后的值。operator.add 可以拼 list 或加数字，自定义函数可以合并 dict、去重文档、取最大分数。选择 reducer 时要问：多次更新的顺序是否影响结果？重复执行是否安全？空值是什么？错误输入怎样处理？这些问题决定图是否可复现。")
    + _h3("六、Topic 适合多生产者收集", "Topic 可以理解为一个收集多条更新的通道，适合发布/订阅或多分支产物汇集的场景。它和 LastValue 的差别在于：LastValue 关注最终单值，Topic 关注一批更新。实际使用时仍要看具体 API 和配置，但心智上可以把它放在“多值通道”这一格。")
    + _h3("七、Reducer 要纯，不要做 I/O", "Reducer 可能在运行时合并多个节点更新，也可能在重放、恢复、测试中被调用。它应该是纯函数：给定旧值和新值，返回合并值。不要在 reducer 里写数据库、发请求、读时钟、生成随机数或记录业务审计。副作用属于节点；reducer 属于状态合并法律。法律不能每次执行都变。")
    + _h3("八、非交换 reducer 的风险", "并行更新时，顺序可能由运行时调度、节点名或实现细节决定。如果 reducer 不满足交换律，例如字符串拼接、列表拼接带顺序语义、按先后选择赢家，你就要确认这个顺序是否被框架保证，是否对业务重要。风险高的做法是让并行分支产出带排序键的结构，下游再按规则排序，而不是让 reducer 隐式依赖调度顺序。")
    + _h3("九、去重和替换要写进语义", "很多业务列表不是单纯追加，而是“按文档 id 去重”“按工具调用 id 替换”“按最高分保留”。add_messages 给聊天消息提供了现成 id 语义；其他领域你可能需要自定义 reducer。自定义时不要只考虑 happy path，也要考虑重复更新、失败重试、同一节点重跑和 checkpoint 恢复后再次合并。")
    + _h3("十、channel 是 reducer 的运行时形态", "上层写 Annotated reducer，底层用 channel 存储当前值、接收更新、决定可见性。理解 channel 能帮助你解释为什么本轮并行节点看不到彼此刚写的值，为什么合并结果下一轮才稳定可见，为什么 compile 阶段要根据 schema 创建通道。Reducer 是语义，channel 是执行容器。")
    + _h3("十一、冲突不总是坏事", "如果两个并行节点同时写 final_answer，报冲突可能比随机覆盖更好。冲突暴露了设计不清：到底谁有权决定最终答案？是否应该先写 candidate_answers，再由 judge 节点选择？不要为了让检查通过给所有 key 都加 list append reducer。正确的 reducer 应反映业务语义，不是消音器。")
    + _h3("十二、设计 reducer 的问题清单", "每个 state key 都问五个问题：这个值是当前值还是历史？多个节点会不会同轮写？重复更新应该追加、替换、去重还是覆盖？顺序是否重要？重试和恢复会不会导致重复？如果回答不出来，先不要写复杂图。Reducer 设计是状态图可靠性的核心。")
    + _h3("十三、最小心智模型", "State key 只是门牌号，channel 才是收件规则。LastValue 擦白板，Topic 收便签，BinaryOperatorAggregate 做折叠，add_messages 管聊天记录。节点只负责投递 partial update；通道负责按法律收件。法律选错，图看起来能跑，状态却会悄悄丢失、重复或乱序。")
    + r"""
<h2>扩展复盘：为每个 key 写合并说明</h2>
<p>Reducer 设计最实用的文档方式，是在 schema 旁边为每个 key 写一句合并说明。final_answer：后写覆盖前写，因为只有一个最终答案。messages：用 add_messages，因为聊天历史要追加，同时允许按 id 修正。retrieved_docs：按文档 id 去重并保留最高分，因为多个检索分支可能找到同一篇文档。audit_events：只追加不可修改，因为审计记录要保留事实。这样的说明能让后来的人知道 reducer 不是随手选的。</p>
<p>并行 fan-in 是检验 reducer 的压力测试。顺序执行时，很多错误会被最后一次覆盖掩盖；并行执行时，两个更新同时到来，通道必须做出明确裁决。没有 reducer 的共享 key 可能报冲突；不合适的 reducer 可能悄悄吞掉一个分支；依赖顺序的 reducer 可能在不同运行中产生不同结果。设计图时，凡是看到两个节点可能同轮写同一 key，就应该停下来讨论合并法律。</p>
<p>幂等性也很重要。节点失败重试、人工恢复、checkpoint 重放都可能让同一逻辑更新再次出现。add_messages 通过 id 替换减少重复；自定义 reducer 也可以用 event_id、document_id、tool_call_id 去重。如果 reducer 只是盲目 list 拼接，恢复一次就多一条审计，重试一次就多一个候选文档，下游会越来越难判断真实状态。</p>
<p>有些 key 不该被合并，而应该被拆开。比如两个并行节点都想写 final_answer，这不是缺少 reducer，而是职责冲突。更好的设计是让它们写 candidate_answers，随后由 judge 节点选择 final_answer。Reducer 不是万能胶；它只能表达合理的合并语义，不能弥补架构上“谁负责最终决定”没有说清的问题。</p>
<p>非交换、非结合的 reducer 不是不能用，但要非常显式。列表拼接如果只是为了展示日志，顺序也许不关键；如果顺序影响模型答案，就应该给每条记录带 rank、source、created_step，然后由下游排序。字符串拼接、取第一个、取最后一个这类 reducer 在并行场景尤其危险，因为读者很难从业务上解释为什么某个分支赢了。</p>
<p>最后，reducer 的纯度直接影响可复现性。合并函数如果读当前时间、查数据库、调用模型，就会让同样一组更新得到不同状态。图运行时依赖步骤边界和 channel 合并来实现 trace、checkpoint 和恢复；reducer 越像数学函数，这些能力越可靠。任何需要外部世界的信息，都应该先由节点读取并写成 update，再由 reducer 纯粹合并。</p>
<h2>案例推演：并行检索结果如何安全汇总</h2>
<p>假设一个 RAG 图有三个并行检索节点：向量检索、关键词检索、知识库工具检索。它们都想把候选文档写入 retrieved_docs。如果 retrieved_docs 没有 reducer，最后可能只剩一个分支的结果，或者运行时报冲突。正确做法不是让每个节点返回整份 state，而是先决定合并语义：按 document_id 去重，保留最高 score，记录来源 sources，最后按 score 排序截断前 N 条。</p>
<p>这个合并语义可以由自定义 reducer 表达，也可以让三个分支分别写 vector_docs、keyword_docs、tool_docs，再由 merge_docs 节点统一处理。前者让 fan-in 更直接，后者让排序、去重和解释更可控。选择哪种方式取决于复杂度：如果合并规则简单、纯粹、无副作用，reducer 很合适；如果合并需要较多业务逻辑、日志或模型判断，单独节点更清楚。</p>
<p>消息合并也有类似权衡。messages 用 add_messages 是因为聊天消息的追加和按 id 替换是通用语义，适合作为 reducer。若你要做“只保留最近十轮”“压缩旧消息”“根据 token 数摘要历史”，就不一定应该全塞进 reducer。摘要需要模型或复杂策略时，更适合一个 memory_compaction 节点，先读取 messages，再返回压缩后的明确更新。</p>
<p>审计事件通常要求不可变追加。audit_events 的 reducer 可以按 event_id 去重追加，但不应替换旧内容，因为审计记录代表发生过的事实。相反，current_risk_level 可以覆盖，因为它代表当前判断。把这两类 key 混用会出事故：如果审计用 LastValue，会丢历史；如果当前风险用盲目 append，下游又要猜哪个才是最新。</p>
<p>并行分支还要求 reducer 的结果可解释。下游 answer 节点看到 retrieved_docs 时，最好知道每条文档来自哪个分支、分数是多少、是否被去重合并。一个只返回纯字符串列表的 reducer，可能让模型能回答，却让排障人员不知道为什么某文档被选中。合并后的数据结构应服务下游模型，也服务人类调试。</p>
<p>最后，不要为了避免冲突给所有 key 都加“列表追加”。冲突有时是设计给你的提醒：两个节点同时写同一个最终值，说明责任不清。健康的 reducer 设计，会区分“可以自然合并的多值产物”和“必须由某个裁决节点选择的单值决策”。这个区分，是复杂图能长期维护的关键。</p>
<h2>进一步练习：为 reducer 写反例测试</h2>
<p>好的 reducer 不只测 happy path，还要测反例。messages 要测相同 id 替换、不同 id 追加、空更新保持不变；文档 reducer 要测重复 document_id、分数更高的版本、来源合并、排序稳定；审计事件 reducer 要测重复 event_id 不重复追加。反例测试能防止 reducer 在重试、恢复和并行 fan-in 时悄悄制造重复数据。</p>
<p>还要测试 reducer 的顺序敏感性。把同两份更新按 A/B 和 B/A 两种顺序输入，结果是否等价？如果不等价，业务是否允许？如果允许，是否在注释里说明顺序来源？如果不允许，就需要改 reducer 或改图结构。并行图最怕隐藏顺序假设，因为它们在小样本测试里不明显，到了真实并发才会出现难复现差异。</p>
<p>对于 LastValue 字段，也要写“同时写入”的设计测试或结构评审。比如 final_answer 不应该被两个并行节点同时写；如果确实可能出现，就让它们写 candidate_answers，再由 judge 节点写 final_answer。这个测试不是为了让 LastValue 通过，而是为了证明图结构避免了冲突。冲突被提前发现，说明 channel 设计在保护你。</p>
<p>最后，给 reducer 写一句人类可读的业务解释。比如“risk_scores 按来源合并，因为每个评估器代表不同维度”“audit_events 按 event_id 去重追加，因为重试不应制造假审计”“messages 按 id 替换，因为流式或工具回填可能修正旧消息”。这些解释能帮助未来维护者判断是否可以改 reducer，而不是只看到一个神秘函数名。</p>
<p>补充检查：为每个 reducer 写出“旧值、新值、结果”的三列表格，至少覆盖空旧值、正常追加、重复更新、并行两份更新和错误输入。表格比文字更容易暴露歧义：同一个文档重复出现是替换还是保留两份，同一个审计事件重试出现是忽略还是追加，同一个风险分数来源重复出现是取最大还是取最新，都应该在实现前说清。</p>
<p>Reducer 的收束点是合并法律，而不是数据类型技巧。一个好法律要说明是否满足交换律、结合律和幂等性；如果不满足，就要说明运行时顺序从哪里来，业务是否接受。并行 fan-in 里，无法解释顺序的 reducer 会让同样输入在不同调度下产生不同状态，这比显式冲突更危险。</p>
<p>消息列表还要特别记住 id 语义。add_messages 不是无脑 append：新 id 追加，相同 id 替换。这个能力让流式修正和工具回填更自然，也让手写 message id 变成风险点。测试里要同时覆盖“不同 id 追加”和“相同 id 替换”，否则你可能把修正消息误当成新消息，或把新消息误覆盖掉。</p>
<p>选择 reducer 时，先问业务再写代码：final_answer 是当前值，通常覆盖；audit_events 是事实历史，通常追加且不可改；retrieved_docs 可能要按 document_id 去重并排序；risk_scores 可能按来源合并。把这些语义写在 schema 旁边，fan-in 才能可复现，checkpoint 重放才不会制造重复或丢失。</p>
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("list 字段默认 append", "默认通常是 LastValue 覆盖；需要累积就用 Annotated 声明 reducer。"),
            ("重复 message id 会生成两条消息", "add_messages 会按 id 替换旧消息，重复 id 表示更新。"),
            ("任何 reducer 都适合并行", "并行 fan-in 更偏好交换律、结合律清晰的 reducer，否则顺序会影响结果。"),
            ("reducer 里可以顺手写日志或查库", "reducer 应是纯合并函数；I/O 和副作用放到节点。"),
        ]
    )
    + r"""
<h2>小实验</h2>
"""
    + shell.lab_card(
        "为并行分支选择 reducer",
        [
            "设计两个并行节点：risk_node 返回风险标签，policy_node 返回政策标签。先让它们都写 notes 且不声明 reducer，观察冲突或覆盖。",
            "把 notes 改成 Annotated[list[str], operator.add]，确认两个标签都进入下游 state。",
            "给 messages 构造两个相同 id 的 AIMessage，观察 add_messages 替换而不是追加。",
            "讨论如果 notes 顺序有业务意义，是否应该让节点返回带 source 和 rank 的对象，再由下游排序。",
        ],
    )
    + shell.version_note("本课以 add_messages、LastValue、Topic、BinaryOperatorAggregate、_get_channel 为版本锚点。随着 LangGraph channel 实现演进，具体类路径可能调整，但“schema 标注 reducer，compile 创建 channel，运行时按 channel 合并”的结构仍是阅读主线。")
    + _points([
        "Reducer/channel 决定同一个 state key 多次更新时怎样合并。",
        "普通字段默认覆盖适合单值；累积列表必须显式声明 reducer。",
        "add_messages 会追加新消息，也会按消息 id 替换旧消息。",
        "并行 fan-in 中 reducer 的交换性、结合性和幂等性会影响可复现性。",
        "Reducer 应保持纯函数；副作用和 I/O 应放在节点里。",
    ])
)


LESSON_21_COMPILE_RUNTIME = (
    r"""
<p class="lead">StateGraph 在 add_node、add_edge 阶段还只是建造者；compile 才把图纸变成可运行的 Runnable runtime。编译会校验图结构，创建 channel，包装节点，接入 runtime context 和 checkpointer，并产出 CompiledStateGraph。之后 invoke、stream、batch 才真正执行 Pregel 风格的节点调度。本课把 compile 和 invoke 分清：compile 不跑模型，不调工具；它像把剧本、舞台、灯光和安全规则装配好，演出发生在运行阶段。</p>
"""
    + _analogy("把 StateGraph.compile 想成剧院彩排前的舞台装配：剧本检查有没有缺场，演员入口出口是否连通，道具柜按清单摆好，灯光控制台接线完成，录像系统准备记录。装配完成后，剧院还没有演出；只有观众入场并调用 invoke，演员才按场次上台。checkpointer 像录像机，runtime context 像当天演出单，CompiledStateGraph 像已经装配好的整座舞台。")
    + shell.lesson_map(
        "本课地图：从 builder 到 Runnable runtime",
        [
            ("建造阶段", "StateGraph 收集 schema、节点、边和配置，但不执行节点", "before"),
            ("编译阶段", "compile 校验结构、创建 channel、包装节点、接入 checkpointer", "now"),
            ("运行阶段", "invoke/stream/batch 进入 Pregel runtime，按步骤调度节点", "now"),
            ("上下文", "Runtime 向节点提供 context、store、stream_writer 等环境能力", "source"),
            ("持久化", "BaseCheckpointSaver 在运行时保存和恢复 state snapshot", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>compile/runtime 的源码阅读要把“建图对象”和“运行对象”分开。下面的文件 + 符号名覆盖了编译入口、编译产物、Pregel 执行、运行时上下文和 checkpoint 接口。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/graph/state.py", "symbol": "StateGraph.compile", "role": "把 builder 校验并转换为 CompiledStateGraph，可传入 checkpointer、interrupt、debug 等选项", "direction": "用户完成节点边定义后调用"},
            {"file": "langgraph/graph/state.py", "symbol": "CompiledStateGraph", "role": "编译后的状态图，继承/组合 Pregel 能力并实现 Runnable 调用面", "direction": "调用者对它 invoke、stream、batch"},
            {"file": "langgraph/pregel/main.py", "symbol": "Pregel", "role": "底层图执行运行时，按步骤计划、执行节点、提交 channel 更新", "direction": "CompiledStateGraph 的运行核心"},
            {"file": "langgraph/runtime.py", "symbol": "Runtime", "role": "节点运行时对象，暴露 context、store、stream_writer 等非 state 能力", "direction": "运行阶段注入节点，不属于 compile 执行"},
            {"file": "langgraph/checkpoint/base/__init__.py", "symbol": "BaseCheckpointSaver", "role": "checkpoint 抽象接口，保存和读取线程/步骤状态", "direction": "invoke/stream 时通过 config 中 thread_id 等信息定位"},
        ]
    )
    + r"""
<h2>调用图：build graph -> compile -> invoke -> run nodes -> produce state</h2>
"""
    + shell.call_graph(
        [
            ("builder", "StateGraph(State) + add_node/add_edge", True),
            ("compile", "validate graph, create channels, wrap nodes", False),
            ("compiled", "CompiledStateGraph as Runnable", True),
            ("invoke/stream", "Pregel runtime schedules steps with Runtime context", False),
            ("final state", "channels merge updates, optional checkpoint saved", True),
        ]
    )
    + r"""
<h2>Trace：编译和运行各做什么</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. build", "input": "StateGraph(State)", "action": "注册 model/tools 节点，添加 START、条件边和回边", "output": "builder 持有图纸，不执行任何节点"},
            {"step": "2. compile", "input": "builder + checkpointer?", "action": "校验节点名和边，创建 channels，包装节点为运行时任务", "output": "CompiledStateGraph"},
            {"step": "3. invoke", "input": "{'messages': [...]} + config", "action": "Pregel 运行时初始化 state、runtime context、checkpoint 配置", "output": "第一个 step 准备调度"},
            {"step": "4. run nodes", "input": "当前可运行节点集合", "action": "执行节点，收集 partial updates，提交到 channel", "output": "下一步 state 可见"},
            {"step": "5. finish", "input": "到达 END 或无后继", "action": "保存 checkpoint，按 output_schema 整理结果", "output": "invoke 返回最终 state；stream 可逐步吐事件"},
        ]
    )
    + r"""
<h2>简化源码走读：compile 不等于执行</h2>
"""
    + shell.code_walkthrough(
        "langgraph/graph/state.py",
        "StateGraph.compile",
        """builder = StateGraph(State)
builder.add_node('model', call_model)
builder.add_edge(START, 'model')

compiled = builder.compile(checkpointer=saver)
# no model call has happened yet

result = compiled.invoke(
    {'messages': [HumanMessage('hi')]},
    config={'configurable': {'thread_id': 't1'}},
)
""",
        "教学版强调时间线：compile 返回可运行对象，但不会调用 call_model；invoke 才根据输入和 config 开始调度。checkpointer 也通常在运行时按 thread_id 读写，而不是 compile 时保存业务状态。",
    )
    + r"""
<h2>Compile 阶段的责任</h2>
"""
    + _h3("一、Builder 是可变图纸", "StateGraph builder 阶段适合逐步添加节点、边、schema、入口和条件路由。它像一张还在绘制的图纸，可以继续修改。这个阶段的对象不应该被拿去处理用户请求，因为它还没有完成校验、通道创建和运行时包装。把 builder 和 compiled graph 混用，是很多初学者理解混乱的来源。")
    + _h3("二、compile 做结构校验", "编译会检查边引用的节点是否存在、START/END 使用是否合理、条件路径是否可解析、schema/channel 是否能建立。校验不是形式主义，它把一部分错误从用户请求时提前到启动时。一个节点名拼错，如果等线上第一个请求走到该分支才爆炸，代价就太高。compile 的价值之一，就是让图尽早失败。")
    + _h3("三、compile 创建 channel", "State schema 中的每个 key 会在编译前后被解析为运行时 channel。普通字段可能是 LastValue，Annotated reducer 可能是 BinaryOperatorAggregate，消息字段可能使用 add_messages。没有 channel，节点返回的 partial update 就没有地方落地，也没有合并规则。compile 把类型合同变成运行容器。")
    + _h3("四、compile 包装节点", "用户写的函数、Runnable 或工具节点，需要被包装成运行时可以调度的任务。包装层负责传递 config、runtime、输入 state，收集返回值，处理错误和回调。你在节点函数里看到的是简单签名，Pregel 运行时看到的是可计划、可执行、可记录的节点任务。")
    + _h3("五、CompiledStateGraph 是 Runnable", "编译产物最重要的工程特性是可运行。它继承或实现 Runnable 调用面，所以可以 invoke、ainvoke、stream、astream、batch，也能被更外层 LangChain 组件组合。对调用者来说，它像一个组件；对内部来说，它是一整张状态图。这种外部统一、内部复杂的封装，是 LangChain/LangGraph 分层的关键。")
    + _h3("六、Pregel 运行时按步骤推进", "invoke 之后，Pregel 风格运行时会计划当前哪些节点可运行，执行它们，收集更新，提交到 channel，再进入下一步。并行节点本步写入通常下一步才稳定可见。这种步骤化模型让执行可复现，也让 checkpoint 可以在步骤边界保存状态。compile 只是准备这个运行机器，真正推进发生在 invoke/stream。")
    + _h3("七、Runtime context 不是 state", "Runtime 给节点提供 context、store、stream_writer 等能力。context 是本次运行的环境，例如用户、租户、权限；store 可能是外部长期存储；stream_writer 用于输出自定义流事件。它们帮助节点运行，但不自动成为 state。只有节点显式返回的 key 才进入 state 合并和 checkpoint。")
    + _h3("八、checkpointer 是运行时钩子", "BaseCheckpointSaver 抽象的是保存和读取状态快照的能力。编译时你可以把 checkpointer 接到图上，但真正保存哪条线程、哪一步状态，要等运行时 config 提供 thread_id 等可配置项。忘记 thread_id 时，checkpointer 可能不知道把状态归档到哪里；多个用户共享 thread_id 时，状态可能串线。")
    + _h3("九、compile 不会跑模型", "这句话值得重复：compile 不执行节点、不调用模型、不调工具、不产生业务答案。它最多验证节点存在、包装调用结构。任何“我 compile 了为什么没有结果”的疑问，都是把构建期和运行期混在一起。结果来自 compiled.invoke 或 compiled.stream，而不是 builder.compile。")
    + _h3("十、compile 后再改 builder 要小心", "编译产物是根据当时 builder 的图纸生成的。之后你再对 builder add_node/add_edge，旧 compiled graph 不一定会自动更新。正确做法是把图定义集中完成，再 compile 一次并把产物作为应用依赖注入；如果确实要改图，重新 compile 并替换运行对象。不要让线上请求同时使用多个你自己都分不清版本的 compiled graph。")
    + _h3("十一、stream 和 invoke 共用运行结构", "stream 不是另一套图，它只是以增量方式暴露运行过程或结果。底层仍然是编译后的图、同一组 channel、同一组节点和边。理解这一点能避免为流式输出写重复业务流程：先让 invoke 正确，再决定 stream_mode、事件粒度和前端消费方式。")
    + _h3("十二、batch 是多次运行，不是共享 state", "对 compiled graph batch 多个输入时，每个输入都应该有自己的运行配置和状态边界。除非你显式使用同一个 thread_id 或外部 store，否则不要期待 batch 元素共享同一份 state。把 batch 当成“并发处理多次 invoke”更安全；把它当成“一个大图同时处理所有用户”容易引发状态串扰。")
    + _h3("十三、最小心智模型", "build 阶段画图纸，compile 阶段装配机器，invoke/stream 阶段开机运行，checkpointer 在运行边界录像，Runtime context 提供当天环境。CompiledStateGraph 对外像 Runnable，对内像 Pregel 状态机。只要把这条时间线记住，compile、runtime、checkpoint 的多数坑都能提前避开。")
    + r"""
<h2>扩展复盘：把构建期和运行期分开管理</h2>
<p>在真实服务里，compile 通常发生在应用启动或依赖初始化阶段，而不是每个请求里。启动时构建 StateGraph，注册节点和边，注入模型、工具、checkpointer，调用 compile 得到可复用的 CompiledStateGraph。请求到来时，只调用 compiled.invoke 或 stream，并传入本次输入和 config。这样可以把结构错误提前暴露，也避免每次请求重复装配图。</p>
<p>运行期最重要的是隔离会话。带 checkpointer 的图必须认真设计 thread_id：它可以来自会话 id、用户 id 加业务会话 id、工单 id，或其他稳定且不串线的标识。不能用固定字符串 demo 处理所有用户，也不能把容易碰撞的临时值当线程标识。thread_id 的选择本质上是状态归属设计，错了就会出现用户看到别人历史、恢复到错误步骤等严重问题。</p>
<p>compile 后的对象应当被视为不可变运行资产。虽然 builder 可能还能继续 add_node，但旧 compiled graph 不会神奇吸收新图纸。团队协作中最好把图定义封装成一个工厂函数，返回 compiled graph；修改图结构后重新运行测试和构建，部署新产物。不要在请求处理过程中动态修改全局 builder，否则同一进程里可能同时存在多个结构版本，问题很难复现。</p>
<p>stream、invoke、batch 的选择属于运行接口选择，不应改变图的业务语义。先用 invoke 验证最终 state 正确，再打开 stream 观察中间事件；先用单个输入验证 thread_id 和 checkpoint，再用 batch 做评测或批处理。不要为了前端想看流式输出，就在节点里写另一套业务逻辑。编译图的价值之一，就是同一运行结构可以暴露多种调用形态。</p>
<p>Runtime context 也要在运行期清晰注入。用户权限、租户配置、实验开关这些值应该随请求传入，而不是硬编码在节点闭包里。这样同一个 compiled graph 可以服务多个用户和环境，测试也能构造不同 context 检查行为。相反，如果把这些运行信息写进全局变量，图看起来能跑，却失去了可复现和可隔离的基础。</p>
<p>最后，验证 compile/runtime 相关问题时，要按时间线排查：builder 是否含有正确节点边；compile 是否成功创建产物；invoke 输入是否符合 input_schema；config 是否含 thread_id；节点是否收到预期 context；checkpoint 是否在步骤边界保存；输出是否被 output_schema 过滤。按这条链路逐步定位，比盲目怀疑模型或工具可靠得多。</p>
<h2>案例推演：一次带 checkpoint 的运行时间线</h2>
<p>应用启动时，服务创建 StateGraph，注册 model、tools、human_review、finalize 等节点，添加边和条件边，然后调用 compile(checkpointer=saver)。这一步如果节点名拼错、边指向不存在的节点、schema reducer 无法解析，应该直接启动失败。此时没有任何用户消息进入图，也没有模型调用发生。compile 的输出是一个可复用的 compiled graph，可以放进应用容器供请求处理函数使用。</p>
<p>用户发来第一条消息时，请求处理函数构造输入 {'messages': [HumanMessage(...)]}，同时构造 config {'configurable': {'thread_id': session_id}}。session_id 必须能唯一代表这段对话或工单。compiled.invoke 接收输入后，Pregel runtime 初始化 channels，读取或创建该 thread 的 checkpoint，注入 runtime context，然后从 START 的后继节点开始执行。模型调用、工具调用、路由判断都发生在这个阶段。</p>
<p>每个 step 结束时，节点返回的 partial update 会提交到 channel，合并后的 state 可能被 checkpointer 保存。这样当工具调用后需要人审，图可以暂停；人类批准后，再用同一个 thread_id 恢复，运行时能找到之前的 messages、tool_attempts 和等待状态。没有 thread_id，checkpointer 就像录像机没有磁带标签，无法可靠知道该接哪一段。</p>
<p>如果服务改版增加了一个 fraud_check 节点，必须重新 compile 并部署新 compiled graph。旧 compiled graph 不会自动拥有新节点。对于已经存在的 checkpoint，还要考虑状态兼容：旧 checkpoint 里没有 fraud_flags，新 schema 是否提供默认值？路由是否能处理缺失 key？这说明 compile/runtime 不是孤立 API，而是和版本迁移、持久化兼容一起考虑的工程问题。</p>
<p>stream 模式下，时间线不变，只是运行过程中的事件或状态片段被逐步交给调用者。前端看到 token、节点事件或中间状态，不代表图用了另一套逻辑。为了避免前后端理解偏差，后端应该明确 stream_mode 输出的是消息、values、updates 还是自定义事件。否则前端可能把中间 update 当最终答案，或漏掉最后的 END 状态。</p>
<p>排查 checkpoint 问题时，按固定顺序看：config 是否带 thread_id；thread_id 是否对每个用户唯一；checkpointer 是否真的传给 compile；节点是否把需要恢复的数据写入 state 而不是 context；恢复时 input 是否和线程状态兼容；output_schema 是否隐藏了你想看的调试 key。按时间线排查，比反复修改节点逻辑更有效。</p>
<h2>进一步练习：运行时配置的安全清单</h2>
<p>上线前可以为 compiled graph 写一张运行时配置清单。第一项是 thread_id 来源：它是否稳定、唯一、不可被用户随意伪造，是否区分环境和租户。第二项是 context：user_id、tenant_id、permissions 是否每次请求都显式传入，节点是否避免从全局变量读取这些值。第三项是 checkpointer：保存位置、保留时间、加密和清理策略是否满足业务要求。</p>
<p>第二组清单关注调用方式。invoke 用于普通请求，stream 用于需要中间事件的交互，batch 用于评测或批处理。三者应共享同一个 compiled graph 和业务语义，只改变结果暴露方式。若你发现 stream 路径和 invoke 路径调用了不同节点或不同 prompt，就要警惕逻辑分叉。调用方式可以不同，状态机不应随意变成两套。</p>
<p>第三组清单关注版本。编译产物对应哪份图定义？部署后旧 checkpoint 是否还能被新 schema 读取？新增 key 是否有默认处理？删除节点后，是否还有旧线程停在那个节点附近？这些问题在无状态链里不明显，但在有 checkpoint 的图里非常重要。状态一旦持久化，图结构就和数据迁移产生了关系。</p>
<p>最后，运行时排障要保存足够但不过量的信息。trace 需要看到节点名、路由结果、state update 摘要、thread_id 和错误类型；不应随意泄漏密钥、完整隐私数据或不可公开的工具响应。Runtime context、RunnableConfig metadata、checkpoint 内容各有边界。边界清楚，既能调试，也能保护用户数据。</p>
<p>对 checkpointer 来说，<span class="mono">configurable</span> 不是随便放参数的杂物箱，而是运行时定位线程、命名空间和恢复点的合同。至少要明确 <span class="mono">thread_id</span> 从哪里来，是否还需要 <span class="mono">checkpoint_ns</span> 区分子图或业务域，恢复时是否沿用同一份 config。把这些字段当成 API 合同记录下来，才能让同一张 compiled graph 在多租户、批处理和人工恢复场景里稳定复用。</p>
<p>补充检查：compile/runtime 的测试最好包含一个“不会发生”的断言，例如只调用 compile 时节点计数器保持为零，只有 invoke 后计数器才增加。再加一个 checkpoint 配置测试：同一 thread_id 能恢复历史，不同 thread_id 彼此隔离，缺失 thread_id 时给出明确错误或退化策略。这样的测试能防止团队把构建期、运行期和持久化边界混在一起。</p>
<p>部署时还要记录 compiled graph 的版本。运行日志中保留图版本、thread_id、入口 schema 版本和关键路由结果，能帮助你把用户报告的问题对应到具体图结构。如果没有这些信息，checkpoint 里的状态可能来自旧图，当前代码却按新图解释，排查会非常困难。版本信息不是课程细节，而是有状态运行系统的基本卫生。</p>
<p>运营清单应按生命周期排列：构建期检查节点名、边、schema 和 reducer；编译期确认 checkpointer、interrupt 和 debug 配置；运行期确认 input、context、configurable.thread_id 和 stream_mode；恢复期确认 checkpoint 版本、state 兼容和输出过滤。按阶段排查，能避免把 thread_id 配错误判成模型问题，或把旧 compiled graph 误判成节点 bug。</p>
<p>本课最终要记住的是时间线：builder 只是图纸，compile 只是装配，invoke/stream 才运行，checkpoint 在运行步骤边界保存和恢复。每次上线前都应问四个问题：我部署的是哪份 compiled graph？每个请求的 thread_id 从哪里来？旧 checkpoint 是否还能被新 schema 解释？出现中断后由谁、用什么输入恢复？这些问题答清楚，LangGraph 才能从 demo 变成可运营系统。</p>
<p>还要把这个清单落实到团队流程里：代码评审检查图结构和 state 合同，启动日志记录编译产物版本，请求日志记录 thread_id 与关键路由，恢复工具能查看最近 checkpoint 摘要，回滚方案说明旧线程如何继续运行。compile/runtime 课程的重点不是背 API 名称，而是建立运维边界。谁负责构建，谁负责调用，谁负责保存，谁负责恢复，每一段都明确，线上故障才不会在模型、图、存储和前端之间来回甩锅。</p>
<p>最后给自己一个上线前口令：先确认图能编译，再确认一次 invoke 能结束，再确认同一 thread_id 能恢复，再确认不同 thread_id 不串线，再确认 stream 只改变输出形式而不改变业务路径。这个顺序能把构建、执行、持久化和观测分开验证，避免把所有风险压到真实用户请求上，也让排障记录能对应具体生命周期阶段和责任人，减少临场猜测即可。</p>
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("compile 会执行图并得到答案", "compile 只校验和装配；invoke/stream/batch 才运行节点。"),
            ("compile 后继续改 builder，旧 compiled graph 会自动变", "编译产物反映编译当刻的图；修改 builder 后应重新 compile 并替换产物。"),
            ("用了 checkpointer 不需要 thread_id", "运行时通常需要 config.configurable.thread_id 等信息定位会话状态。"),
            ("runtime context 就是 state 的另一个名字", "context 是环境输入，state 是可演化、可合并、可 checkpoint 的业务数据。"),
        ]
    )
    + r"""
<h2>小实验</h2>
"""
    + shell.lab_card(
        "观察 compile 和 invoke 的分界",
        [
            "写一个节点，在函数体第一行打印或记录 'model called'；只执行 builder.compile()，确认没有打印。",
            "对 compiled.invoke({'messages': [...]}) 运行一次，确认节点此时才执行。",
            "接入内存 checkpointer，先不传 thread_id 观察错误或不可恢复行为，再传 {'configurable': {'thread_id': 'demo'}}。",
            "compile 后给 builder 再添加一个节点，但不重新 compile，解释为什么旧 compiled graph 不会包含新节点。",
        ],
    )
    + shell.version_note("本课锚定 StateGraph.compile、CompiledStateGraph、Pregel、Runtime、BaseCheckpointSaver。不同版本可能调整 checkpointer 配置细节或 runtime 参数形状，但“builder/compile/runtime 三阶段”和“编译产物是 Runnable”是稳定心智模型。")
    + _points([
        "compile 把 StateGraph builder 转成可运行 CompiledStateGraph，但不执行节点。",
        "编译阶段负责校验、channel 创建、节点包装和 checkpointer/runtime 钩子装配。",
        "invoke/stream/batch 才进入 Pregel 运行时，按步骤执行节点并合并 state。",
        "Runtime context 是运行环境，不是会自动 checkpoint 的业务 state。",
        "使用 checkpointer 时要正确提供 thread_id 等配置；修改 builder 后应重新 compile。",
    ])
)
