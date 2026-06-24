"""Per-lesson self-test (自测题): design-insight multiple-choice + open prompts.

Questions focus on *why a thing is designed the way it is* (设计亮点 / 取舍 /
引发思考), not rote syntax recall. Content lives here as data; ``render(fname)``
turns it into HTML that build.py / build_print.py append to the bottom of each
lesson (above the footnav). Data-driven => consistent markup (check_html stays
green) and one place to review/extend.

Schema per lesson::

    "NN-file.html": {
        "mcq": [{"q": "...", "opts": ["A 文本", ...], "answer": 1, "why": "..."}],
        "open": ["发散题 1", "发散题 2"],
    }

``answer`` is the 0-based index of the correct option (into ``opts`` as written).
At render time the options are deterministically shuffled per question so the
correct answer is spread across A/B/C/D (otherwise authors tend to always put it
first/second). Use <code>…</code> for inline code and single quotes inside it to
avoid escaping.
"""

import hashlib


def _shuffle(opts, answer, seed):
    """Deterministically permute ``opts`` (stable across builds) and return
    ``(new_opts, new_answer_index)`` so the correct option lands in a varied
    position instead of always being first/second."""
    order = sorted(
        range(len(opts)),
        key=lambda i: hashlib.md5(f"{seed}:{i}".encode("utf-8")).hexdigest(),
    )
    return [opts[i] for i in order], order.index(answer)

QUIZZES = {
    # ===== 第一部分 · 全局地图 =================================================
    "01-what-is-langchain.html": {
        "mcq": [
            {
                "q": "从框架边界看，LangChain 最准确的定位是什么？",
                "opts": [
                    "训练和部署大语言模型的底层系统",
                    "把模型、消息、工具、回调和 Agent 循环接成应用的编排层",
                    "专门存储向量并执行相似度检索的数据库",
                    "替代所有 provider SDK 的推理引擎",
                ],
                "answer": 1,
                "why": "LangChain 的边界是应用编排与集成：统一接口、组织流程、连接工具和图运行时；模型训练、推理内核、向量索引属于其他层。",
            },
            {
                "q": "为什么说 <code>Runnable</code> 更像协议，而不是某个具体功能？",
                "opts": [
                    "因为它只用于 prompt 模板",
                    "因为它规定 <code>invoke/stream/batch/config</code> 等统一行为，模型、链、解析器、图都能按这个契约组合",
                    "因为它只能同步执行",
                    "因为它绕过了所有回调",
                ],
                "answer": 1,
                "why": "Runnable 定义的是可运行组件的共同形状。具体实现可以是聊天模型、parser、LCEL 链或 LangGraph 编译图。",
            },
            {
                "q": "LangGraph 与 LangChain 在 Agent 场景中的关系，更准确的说法是？",
                "opts": [
                    "LangGraph 负责训练模型，LangChain 负责推理",
                    "LangChain 的 <code>create_agent</code> 提供高层入口，LangGraph 负责状态图、循环、分支、持久化等运行时能力",
                    "二者只是同一个包的两个名字",
                    "LangGraph 只能画图，不能执行",
                ],
                "answer": 1,
                "why": "LangGraph 是图执行与状态管理层；LangChain 可以把高层 Agent API 编译/组装到 LangGraph 上运行。",
            },
        ],
        "open": [
            "抽象会带来可替换性，也会带来隐藏细节的代价。结合 <code>Runnable</code> 或 <code>init_chat_model</code>，说明你愿意为了什么收益接受这层间接。",
            "把一次订单查询 Agent 分成模型、LangChain 编排、业务工具、存储/检索四层。每层分别拥有什么责任？哪一层不该越界？",
        ],
    },
    "02-monorepo.html": {
        "mcq": [
            {
                "q": "为什么 <code>langchain-core</code> 必须比 partner 包更稳定？",
                "opts": [
                    "因为 core 不包含任何代码",
                    "因为 core 定义所有上层共享的协议，破坏它会影响模型、工具、图和用户代码",
                    "因为 core 只服务 OpenAI",
                    "因为 core 不允许测试",
                ],
                "answer": 1,
                "why": "越底层、被依赖越广，变更成本越高。core 是公共契约层，所以要轻依赖、保守和向后兼容。",
            },
            {
                "q": "把 OpenAI、Anthropic 等适配拆成 partner 包，最主要隔离了什么？",
                "opts": [
                    "Python 语法差异",
                    "厂商 SDK、认证、payload、响应字段和发布节奏的变化",
                    "所有业务逻辑",
                    "LangGraph 的 checkpoint 数据",
                ],
                "answer": 1,
                "why": "partner 包承接高频厂商变化，某个 SDK 升级时不应迫使 core 或其他 provider 一起变化。",
            },
            {
                "q": "健康的包依赖方向应当是什么？",
                "opts": [
                    "<code>langchain-core</code> 反向 import 所有 partner，方便统一管理",
                    "上层和边缘依赖稳定核心，核心不依赖具体厂商或 community 集成",
                    "所有包相互 import，减少参数传递",
                    "业务代码直接读取每个 provider 的原始响应字段",
                ],
                "answer": 1,
                "why": "单向依赖能控制变更传播路径：稳定层不认识易变层，边缘变化不会污染地基。",
            },
        ],
        "open": [
            "为一个你熟悉的项目画出 core/main/community/partner 类似边界。哪些代码应该沉到稳定地基，哪些应该留在易变边缘？",
            "如果某 provider SDK 改了响应字段，直接依赖 SDK 的业务代码会有什么爆炸半径？用 adapter/partner 包如何缩小影响范围？",
        ],
    },
    "03-lifecycle.html": {
        "mcq": [
            {
                "q": "<code>model.invoke('写一句欢迎语')</code> 为什么要先做 message normalization？",
                "opts": [
                    "为了让字符串变长",
                    "为了把字符串、PromptValue、消息列表等输入统一成 <code>BaseMessage</code> 列表，隔离上层逻辑和厂商格式",
                    "因为 provider 只能接收 Python 对象，不能接收 JSON",
                    "为了跳过回调",
                ],
                "answer": 1,
                "why": "标准消息是中间表示。上层只处理 BaseMessage，provider wrapper 再负责翻译成自家 payload。",
            },
            {
                "q": "<code>RunnableConfig</code> 沿调用链传播的意义是什么？",
                "opts": [
                    "只用于改变最终文本内容",
                    "让 tags、metadata、callbacks、run_id 等运行时信息能穿过组合链，被下游模型、工具和 tracer 看到",
                    "强制所有调用都变成异步",
                    "替代 provider API key",
                ],
                "answer": 1,
                "why": "config 是跨 Runnable 传播的运行上下文。中间组件吞掉它，trace、metadata、回调就会断。",
            },
            {
                "q": "回调生命周期中 start/end/error 事件最直接支撑什么能力？",
                "opts": [
                    "自动提升模型质量",
                    "可观测性：追踪输入输出、耗时、错误、stream chunk 和调用层级",
                    "减少所有网络请求",
                    "把所有 AIMessage 转成字符串",
                ],
                "answer": 1,
                "why": "callbacks 是 tracing 和调试的插入口。它们记录调用何时开始、如何结束、哪里失败。",
            },
        ],
        "open": [
            "按输入标准化、config 合并、callback start、provider payload、响应解析、callback end 的顺序，追踪一次 <code>invoke</code>，写出每步输入和输出类型。",
            "把 <code>invoke</code> 改成 <code>stream</code> 后，哪些步骤仍然相同？哪些地方会变成 chunk/token 级事件？",
        ],
    },
    "04-source-reading-map.html": {
        "mcq": [
            {
                "q": "读一个新功能源码时，最稳的 happy-path 顺序是什么？",
                "opts": [
                    "随机搜索关键词，打开最长的文件",
                    "Public API → protocol/base class → concrete implementation → tests/examples",
                    "只读 README，不看测试",
                    "直接从 provider SDK 源码开始",
                ],
                "answer": 1,
                "why": "先找入口，再看契约，再看实现差异，最后用测试确认边界，这样不容易迷路。",
            },
            {
                "q": "为什么教程要求源码结论使用“文件 + 符号名”引用？",
                "opts": [
                    "为了避免写中文解释",
                    "因为符号名能让结论可复查、可迁移，比只说“源码里好像”可靠，也比行号更抗版本漂移",
                    "因为所有文件都没有行号",
                    "为了跳过具体实现",
                ],
                "answer": 1,
                "why": "文件 + 符号名是可验证证据。教学笔记中它比易漂移的行号更稳定。",
            },
            {
                "q": "为什么 tests/examples 适合作为源码阅读材料？",
                "opts": [
                    "它们只展示无关样式",
                    "测试记录维护者承诺的行为边界，示例展示推荐 happy path",
                    "它们永远不会随版本更新",
                    "它们可以替代所有源码",
                ],
                "answer": 1,
                "why": "测试和示例随仓库演进，能帮助判断哪些用法被支持、哪些边界不能破坏。",
            },
        ],
        "open": [
            "选择 <code>@tool</code> 或 <code>create_agent</code>，建立一张 source map：public API、base/protocol、concrete implementation、tests/examples 各写一个文件 + 符号名。",
            "如果 OpenAI 与 Anthropic 的 tool calling 行为不同，你会如何定位差异？请写出先比较哪些 wrapper 方法，再找哪些测试。",
        ],
    },
    "05-learning-path.html": {
        "mcq": [
            {
                "q": "本教程推荐的学习顺序是什么？",
                "opts": [
                    "先跑最大 demo，再看最终输出，最后凭感觉改 prompt",
                    "concept → trace → source → experiment → glossary",
                    "只读源码，不做实验",
                    "只背术语表，不运行代码",
                ],
                "answer": 1,
                "why": "五步闭环先建立心智，再观察流动，再找证据，再验证假设，最后沉淀术语。",
            },
            {
                "q": "<code>GenericFakeChatModel</code>、<code>InMemorySaver</code> 这类 fake/in-memory 组件最适合用来做什么？",
                "opts": [
                    "评估真实模型智商",
                    "消除网络、费用和随机性，验证框架行为、状态保存和 trace 是否按预期工作",
                    "替代所有生产数据库",
                    "绕过 Runnable 协议",
                ],
                "answer": 1,
                "why": "fake 组件用于机制实验，不用于模型能力评测；它们让实验可控、低成本、可重复。",
            },
            {
                "q": "观察 LangGraph 或 Runnable 状态时，最有价值的做法是什么？",
                "opts": [
                    "只保存最终字符串",
                    "记录输入、状态、config、回调事件、工具结果和输出的变化",
                    "每次同时改变五个变量",
                    "完全关闭 tracing",
                ],
                "answer": 1,
                "why": "状态观察把黑盒拆成节点，能定位到底是输入、工具、路由、config 还是 provider 出了问题。",
            },
        ],
        "open": [
            "设计一个安全实验验证 <code>RunnableConfig</code> 的 tags/metadata 是否传播：如何保证小、确定、单变量、无副作用？",
            "解释为什么 output-only debugging 很弱。请举例说明最终回答错误时，可能分别由消息、工具、retriever、config、provider 哪些层造成。",
        ],
    },

    # ===== 第二部分 · 用户视角 =================================================
    "04-messages.html": {
        "mcq": [
            {
                "q": "为什么说消息是“模型上下文的契约”，而不只是聊天记录文本？",
                "opts": [
                    "因为消息只负责让页面显示得更整齐",
                    "因为每条消息保留角色、内容、工具关系和元数据，下游组件能按结构理解一次运行",
                    "因为消息会自动执行所有工具",
                    "因为消息会把业务数据库状态也保存起来",
                ],
                "answer": 1,
                "why": "消息契约让模型、工具执行器、trace 和裁剪逻辑面对同一种结构；聊天记录字符串会丢失角色、tool_call_id 和 usage 等证据。",
            },
            {
                "q": "<code>AIMessage.tool_calls</code> 和 <code>ToolMessage</code> 的边界是什么？",
                "opts": [
                    "二者都是工具定义 schema，可以互换",
                    "<code>ToolMessage</code> 表示模型打算调用工具，但还没执行",
                    "<code>tool_calls</code> 是模型提出的调用请求，<code>ToolMessage</code> 是程序执行后的观察",
                    "<code>tool_calls</code> 保存工具返回值，<code>ToolMessage</code> 保存用户输入",
                ],
                "answer": 2,
                "why": "模型只提出意图；应用负责校验、执行并追加 ToolMessage。把结果误塞进 tool_calls 或普通文本，会破坏工具回合的证据链。",
            },
            {
                "q": "<code>usage_metadata</code> 最适合承担哪类责任？",
                "opts": [
                    "决定订单是否付款成功",
                    "替代 <code>tool_call_id</code> 做工具配对",
                    "保存用户权限和业务主状态",
                    "记录 token 用量、成本分析和调试观察",
                ],
                "answer": 3,
                "why": "usage_metadata 是观测数据，不是业务事实。它适合进日志、指标和 trace，不应驱动领域状态变更。",
            },
        ],
        "open": [
            "追踪一组消息列表：HumanMessage 提问、AIMessage 带两个 tool_calls、两个 ToolMessage 返回、最终 AIMessage 回复。写出每一步哪些字段必须保留。",
            "给出一个无效工具结果例子，并说明为什么它不能正确回灌给模型：缺 <code>tool_call_id</code>、id 不匹配、还是把结果放错了消息类型？",
        ],
    },
    "05-chat-models.html": {
        "mcq": [
            {
                "q": "聊天模型 wrapper 与 provider 原生 SDK 的边界，最准确的说法是？",
                "opts": [
                    "wrapper 实现 LangChain 的 Runnable/消息契约，内部才调用 provider SDK",
                    "wrapper 就是 provider SDK 的别名，不改变输入输出",
                    "业务代码应该读取 provider 原始 HTTP 响应来保持灵活",
                    "wrapper 只负责保存 API key，不处理消息转换",
                ],
                "answer": 0,
                "why": "边界在 wrapper：上层面对 BaseChatModel、RunnableConfig 和 AIMessage；provider SDK、payload 差异和响应解析应被隔离在适配层。",
            },
            {
                "q": "<code>model.invoke(...)</code> 的标准返回类型是什么？",
                "opts": [
                    "裸字符串，因为下游只需要文本",
                    "<code>AIMessage</code>，其中可能包含 content、tool_calls、usage_metadata 等字段",
                    "provider SDK 的原始响应对象",
                    "总是 JSON dict，和工具 schema 一样",
                ],
                "answer": 1,
                "why": "invoke 的统一输出是 AIMessage。想要字符串可再接 StrOutputParser；直接假设裸字符串会丢掉工具调用和元数据。",
            },
            {
                "q": "<code>bind_tools</code> 对聊天模型做了什么？",
                "opts": [
                    "立即调用所有工具并把结果写入数据库",
                    "把工具函数转换成 prompt 字符串后删除 schema",
                    "把工具 schema 绑定到模型请求上，让模型可以返回 tool_calls，但不执行工具",
                    "保证模型一定会调用某个工具",
                ],
                "answer": 2,
                "why": "bind_tools 改变的是模型可见的工具说明和 provider 请求格式；真实执行仍由 Agent、图节点或你的业务代码完成。",
            },
        ],
        "open": [
            "设计一次从 OpenAI 切到 Anthropic 的改动：哪些代码应该只改模型构造或配置，哪些业务链、parser、工具执行代码不应该跟着改？",
            "检查一个模型配置对象：列出通用参数、provider-specific 参数、RunnableConfig 中的 tags/metadata/callbacks，并说明各自应该在哪一层使用。",
        ],
    },
    "06-tools.html": {
        "mcq": [
            {
                "q": "工具的 schema 与工具执行之间的关系是什么？",
                "opts": [
                    "schema 一生成，工具就会自动执行",
                    "schema 只给人类看，模型不会读取",
                    "执行结果应该写回 schema，供下次复用",
                    "schema 告诉模型可填哪些参数；执行是应用校验参数后调用真实函数",
                ],
                "answer": 3,
                "why": "schema 是模型可见接口，执行是程序控制的副作用边界。把二者分开，才能审批、限流、记录和处理错误。",
            },
            {
                "q": "为什么工具函数的 docstring 和类型注解会影响模型调用质量？",
                "opts": [
                    "它们通常会变成工具名称、参数 schema 和描述，直接指导模型如何填参",
                    "它们只影响 Python 编辑器提示，不会进入工具 schema",
                    "它们能保证工具永远不会失败",
                    "它们会替代权限检查",
                ],
                "answer": 0,
                "why": "工具说明是模型的操作手册。含糊 docstring 或缺类型注解会让 schema 变窄、变错或难以让模型正确选择。",
            },
            {
                "q": "为什么 <code>ToolMessage.tool_call_id</code> 必须和原始 tool call id 配对？",
                "opts": [
                    "让工具名更短",
                    "让模型和 trace 知道哪条工具观察对应哪次请求，尤其支持并行、失败和重试",
                    "让 token 计费更便宜",
                    "让 ToolMessage 可以替代 AIMessage",
                ],
                "answer": 1,
                "why": "tool_call_id 是工具回合的连接键。缺它时，多工具场景中的观察结果会失去归属，错误恢复也难以审计。",
            },
        ],
        "open": [
            "设计一个安全工具：写出函数名、参数、docstring 应表达的约束，以及执行前需要做的权限、范围和速率检查。",
            "工具执行失败时，不要让错误无声消失。说明你会何时抛异常，何时构造带同一 <code>tool_call_id</code> 的 ToolMessage 把错误显式交给模型。",
        ],
    },
    "07-agents-intro.html": {
        "mcq": [
            {
                "q": "一次标准 Agent model/tool loop 的阶段顺序，哪一个最准确？",
                "opts": [
                    "用户问题 → model 节点直接执行 Python 函数 → 最终回答，不需要消息回填",
                    "用户问题 → tools 节点 → model 节点 → ToolMessage → tool_calls → 最终回答",
                    "用户问题 → ToolMessage → model 节点 → tools_condition → 最终回答",
                    "用户问题 → model 节点 → AIMessage.tool_calls → tools 节点 → ToolMessage → model 最终回答",
                ],
                "answer": 3,
                "why": "Agent 循环靠消息推进：模型先发出结构化工具请求，ToolNode 执行后写回 ToolMessage，模型再基于观察结果回答或继续请求工具。",
            },
            {
                "q": "<code>AIMessage.tool_calls</code> 与 <code>ToolMessage</code> 的区别是什么？",
                "opts": [
                    "二者都是工具结果，只是名字不同",
                    "<code>tool_calls</code> 是模型提出的工具请求；<code>ToolMessage</code> 是工具执行后的观察结果，并用 <code>tool_call_id</code> 配对",
                    "<code>ToolMessage</code> 只能由用户手写，不能由 ToolNode 产生",
                    "<code>tool_calls</code> 表示循环已经结束，<code>ToolMessage</code> 表示循环开始",
                ],
                "answer": 1,
                "why": "请求和观察必须分开。tool_calls 告诉运行时要执行什么；ToolMessage 把执行结果带回消息历史，供下一轮模型读取。",
            },
            {
                "q": "Agent 循环何时终止？",
                "opts": [
                    "只要工具返回了任意字符串就终止",
                    "只要达到一次模型调用就终止",
                    "最新 <code>AIMessage</code> 不再包含 <code>tool_calls</code>，条件边路由到结束",
                    "只要用户问题包含问号就终止",
                ],
                "answer": 2,
                "why": "终止信号是结构化字段，而不是自然语言猜测。没有 tool_calls 表示模型没有请求下一轮工具，图可以结束。",
            },
        ],
        "open": [
            "按“用户问题 → model → tool_calls → ToolNode → ToolMessage → final”的顺序，追踪一个查订单 Agent 的完整循环，并写出每一步消息类型。",
            "为一个业务动作判断工具边界：哪些信息应由模型直接回答，哪些必须通过工具查询或执行？说明你的依据。",
        ],
    },

    # ===== 第三部分 · Runnable 与 LCEL =========================================
    "08-runnable.html": {
        "mcq": [
            {
                "q": "Runnable 标准协议最核心的价值是什么？",
                "opts": [
                    "让所有组件都继承同一个具体模型类",
                    "让 prompt、model、parser、retriever 等用同一组执行入口调用并组合",
                    "让所有调用都自动变成流式输出",
                    "让业务状态自动保存在 config 里",
                ],
                "answer": 1,
                "why": "Runnable 统一的是执行协议和组合形状：invoke/stream/batch/config 等入口稳定，具体组件内部如何实现可以不同。",
            },
            {
                "q": "为什么说 <code>RunnableConfig</code> 不应该被当成业务状态？",
                "opts": [
                    "因为 config 只能在异步调用里使用",
                    "因为 config 会阻止 callbacks 运行",
                    "因为它承载 tags、metadata、callbacks 等横切运行信息，业务数据应走 input/output 或图状态",
                    "因为 config 不能传给子 Runnable",
                ],
                "answer": 2,
                "why": "config 是观测、调度和运行控制通道，不是隐藏业务参数通道。把业务状态塞进去会破坏数据流可读性。",
            },
            {
                "q": "关于 <code>stream</code> 与 <code>batch</code>，哪种理解更准确？",
                "opts": [
                    "stream 返回增量 chunk，batch 对多份输入组织多次调用；二者都仍受单次输入输出契约约束",
                    "stream 的每个 chunk 都必然是最终对象",
                    "batch 会把所有输入自动合并成一个模型请求",
                    "stream 和 batch 不会触发 callbacks",
                ],
                "answer": 0,
                "why": "流式和批量是运行形态，不改变组件契约。chunk 不是最终对象保证，batch 也不必然等于 provider 原生批量。",
            },
        ],
        "open": [
            "追踪一次 <code>prompt | model | parser</code> 的 <code>invoke</code>：写出每一步输入、输出、config/callback 如何传播。",
            "你要接入一个内部搜索服务时，会用 <code>RunnableLambda</code>、现有 retriever 适配，还是自定义 Runnable？说明判断标准。",
        ],
    },
    "09-runnable-compose.html": {
        "mcq": [
            {
                "q": "<code>prompt | model | parser</code> 的顺序数据流是什么？",
                "opts": [
                    "prompt 输出直接成为 model 输入，model 输出直接成为 parser 输入，整条 Sequence 返回 parser 结果",
                    "三个组件并行执行，最后随机选一个结果",
                    "parser 先检查用户输入，再决定是否调用 prompt",
                    "管道只传字符串，不保留消息对象",
                ],
                "answer": 0,
                "why": "RunnableSequence 的核心就是左到右传递当前值；每一步 output 变成下一步 input。",
            },
            {
                "q": "LCEL 中 <code>coerce_to_runnable</code> 的作用更接近哪一项？",
                "opts": [
                    "把所有输出都转成 JSON",
                    "把 config 转成业务输入",
                    "把所有异常吞掉并继续执行",
                    "把 callable、dict 等可组合对象提升为 Runnable，例如函数变 RunnableLambda、dict 变并行映射",
                ],
                "answer": 3,
                "why": "coercion 让普通 Python 对象进入 Runnable 协议，但也带来 dict-as-parallel 等需要理解的语义。",
            },
            {
                "q": "在 LCEL 组合右侧写 <code>{'context': retriever, 'question': RunnablePassthrough()}</code> 通常表示什么？",
                "opts": [
                    "把这个字典作为常量传给下游",
                    "同一输入并行送到两个分支，再把结果合并成包含 context/question 的字典",
                    "把 retriever 和 question 串行执行两次",
                    "让 parser 自动补齐缺失字段",
                ],
                "answer": 1,
                "why": "dict 在 LCEL 组合语境中会被提升为 RunnableParallel / RunnableMap，而不是普通常量 dict。",
            },
        ],
        "open": [
            "一条链报错：prompt 需要 <code>context</code>，但上游只返回字符串。你会如何逐段定位并修复类型/键不匹配？",
            "比较 LCEL 链和一个手写 Python 函数：在哪些场景 LCEL 的可观测、可替换、可批量能力更值得？",
        ],
    },
    "12-runnable-parallel-branch.html": {
        "mcq": [
            {
                "q": "<code>RunnableParallel</code> 的 fan-out/fan-in 语义是什么？",
                "opts": [
                    "每个分支依次修改同一个共享状态对象",
                    "只执行第一个最快返回的分支",
                    "同一输入送到多个分支，结果按键汇合成字典",
                    "把所有分支输出拼成一个字符串",
                ],
                "answer": 2,
                "why": "Parallel 的稳定语义是同输入、多分支、dict 汇合；是否真正并发是实现和配置细节。",
            },
            {
                "q": "<code>RunnableBranch</code> 的谓词最好具备什么特征？",
                "opts": [
                    "便宜、确定、可解释，能清楚说明为什么选择某条路径",
                    "越随机越好，避免固定路径",
                    "必须每次调用最贵的模型来判断",
                    "可以返回任意输出 schema",
                ],
                "answer": 0,
                "why": "路由谓词是控制流边界。便宜、确定、可测试的谓词能让分支行为稳定且可追踪。",
            },
            {
                "q": "RAG 链里 <code>RunnablePassthrough</code> / <code>assign</code> 常用来解决什么问题？",
                "opts": [
                    "自动提升模型准确率",
                    "禁用 retriever 的 callbacks",
                    "把所有字段写进 config",
                    "保留原问题，并在字典上补充 context 等下游 prompt 需要的键",
                ],
                "answer": 3,
                "why": "检索会把问题变成文档上下文，Passthrough/assign 用来保留或补齐 prompt 所需变量。",
            },
        ],
        "open": [
            "设计一个 RAG fan-out：问题如何同时进入 retriever 和 passthrough，format_docs 放在哪里，prompt 最终收到哪些键？",
            "下游 prompt 报缺少 <code>context</code>：你会检查 Parallel、assign、键名还是 prompt 模板？写出定位顺序。",
        ],
    },
    "13-runnable-config-callbacks.html": {
        "mcq": [
            {
                "q": "父 Runnable 调子 Runnable 时，callbacks 通常如何传播？",
                "opts": [
                    "子 Runnable 会完全丢弃父级 callbacks",
                    "父 run 派生 child callbacks，子 run 挂到同一棵运行树下",
                    "callbacks 只在 parser 中运行",
                    "callbacks 会把业务输入改写成 metadata",
                ],
                "answer": 1,
                "why": "CallbackManager / tracer 的关键就是维护父子 run 关系，让链、prompt、model、parser 形成可观察运行树。",
            },
            {
                "q": "tags 与 metadata 最适合承载哪类信息？",
                "opts": [
                    "环境、实验组、非敏感版本、路由策略等观测/筛选信息",
                    "用户密码和访问 token",
                    "购物车状态和订单明细",
                    "替代鉴权结果的权限标签",
                ],
                "answer": 0,
                "why": "tags/metadata 是观测字段，必须遵守最小披露原则，不能承载秘密、隐私或业务权限。",
            },
            {
                "q": "run tree 对排查 <code>prompt | model | parser</code> 失败有什么帮助？",
                "opts": [
                    "它会自动修复 parser 错误",
                    "它让所有子步骤合并成一条不可分日志",
                    "它显示父链和子步骤的 start/end/error、耗时与父子关系，能定位失败发生在哪一步",
                    "它会把 tags 当成认证系统",
                ],
                "answer": 2,
                "why": "运行树把复杂链路拆成可观察节点。你能看出是 prompt、model 还是 parser 失败，而不是只看到外层异常。",
            },
        ],
        "open": [
            "为一条 RAG chain 设计 tracing 方案：哪些 run_name、tags、metadata 必须有，哪些 payload 不记录？",
            "如果 metadata 里可能出现系统提示、用户隐私或 token，你会用白名单、脱敏、哈希还是禁记策略？说明规则。",
        ],
    },
    "15-runnable-retry-fallback.html": {
        "mcq": [
            {
                "q": "<code>with_retry</code> 与 <code>with_fallbacks</code> 的核心区别是什么？",
                "opts": [
                    "二者完全相同，只是名字不同",
                    "fallback 只能用于 parser，retry 只能用于 prompt",
                    "retry 在同一路径上有限再试；fallback 在失败后切换到备用 Runnable",
                    "retry 会改变输出 schema，fallback 不会运行 callbacks",
                ],
                "answer": 2,
                "why": "retry 是同路线重试，fallback 是换路线降级；二者都应保持可观察、有限且契约清楚。",
            },
            {
                "q": "为什么对非幂等工具调用盲目 retry 很危险？",
                "opts": [
                    "因为 retry 会禁用所有异常",
                    "因为重复执行可能重复扣款、发邮件、建单等外部副作用",
                    "因为工具不能作为 Runnable",
                    "因为 parser 会自动吞掉工具结果",
                ],
                "answer": 1,
                "why": "写外部状态的动作必须有幂等键、事务或补偿机制；否则重试会把一次失败变成多次副作用。",
            },
            {
                "q": "备用链的输出 schema 为什么必须与主链一致或兼容？",
                "opts": [
                    "为了让模型运行更快",
                    "为了隐藏主链错误",
                    "因为 config 只能保存同一种 schema",
                    "因为下游 prompt/parser/UI 依赖固定字段；fallback 改形状会把失败推迟到后面",
                ],
                "answer": 3,
                "why": "fallback 是降级，不是破坏契约。主链返回带引用对象，备用链也要满足下游需要的字段和类型。",
            },
        ],
        "open": [
            "为一个 RAG 答案链设计稳健策略：retriever、model、parser 分别哪些错误 retry、fallback、repair 或直接失败？",
            "遇到 parser 非法 JSON、provider 503、权限不足、扣款工具超时四种失败，分别选择 retry、fallback、repair 还是失败，并说明理由。",
        ],
    },
    "10-output-parsers.html": {
        "mcq": [
            {
                "q": "输出解析器和 <code>with_structured_output</code> 的核心区别是什么？",
                "opts": [
                    "解析器会执行工具，结构化输出只显示文本",
                    "二者完全相同，只是名字不同",
                    "解析器解析模型文本；结构化输出尽量让 provider/model 原生按 schema 产出",
                    "结构化输出只能处理 markdown，解析器只能处理图片",
                ],
                "answer": 2,
                "why": "parser 是下游解析与校验层；structured output 是模型调用策略。二者都服务结构化结果，但约束位置不同。",
            },
            {
                "q": "解析失败时，最健康的处理方式是什么？",
                "opts": [
                    "吞掉异常并返回空对象",
                    "把错误当作成功结果写入业务表",
                    "永远无限重试直到模型碰巧输出正确格式",
                    "显式捕获解析错误，保留原始输出和错误信息，再决定重试、修复或向用户降级",
                ],
                "answer": 3,
                "why": "parse error 是可观测边界。保留 raw output 与错误原因，才能做有限修复循环和审计，而不是制造静默脏数据。",
            },
            {
                "q": "为什么即使模型“看起来输出了 JSON”，仍需要 schema validation？",
                "opts": [
                    "因为 JSON 语法正确不代表字段齐全、类型正确或满足业务约束",
                    "因为 validation 会让模型更快",
                    "因为 validation 会自动调用外部工具",
                    "因为所有 provider 都禁止直接返回 JSON",
                ],
                "answer": 0,
                "why": "语法解析只证明形状像 JSON；schema validation 才检查字段、类型和约束，避免半正确结果进入下游。",
            },
        ],
        "open": [
            "设计一个有限 repair loop：第一次解析失败后给模型哪些错误信息、最多重试几次、何时返回降级结果，并说明如何记录 raw output。",
            "面对一个需要严格业务动作的场景，判断该用 parser 解析文本，还是让模型发 tool call / structured output。说明你的选择依据。",
        ],
    },
    "11-chat-internals.html": {
        "mcq": [
            {
                "q": "<code>invoke</code> 的调用链里，前几步所有厂商共享、只有 <code>_generate</code> 各自实现。这种“骨架共享、末端定制”是哪种模式、图什么？",
                "opts": [
                    "工厂模式；图省内存",
                    "模板方法模式；图把“缓存/回调/重试”等通用流程写一遍复用，厂商只填“真正调用”这一步",
                    "单例；图唯一性",
                    "装饰器；图加功能",
                ],
                "answer": 1,
                "why": "模板方法把“不变的流程”固化在基类、“会变的一步”留给子类。这正是第 3 课“统一入口 + 厂商 _generate”在代码里的落点。",
            },
            {
                "q": "缓存、回调、重试都放在“共享模板”里，而不是让每个厂商各自实现。这样避免了什么？",
                "opts": [
                    "代码太短",
                    "每个厂商重复实现这些横切逻辑、且实现不一致——放在模板里写一遍，所有厂商行为统一",
                    "厂商太多",
                    "缓存失效",
                ],
                "answer": 1,
                "why": "把通用能力上提到共享层，消除重复 + 保证一致。新增厂商自动获得缓存/回调/重试，不必也不该自己写。",
            },
            {
                "q": "为什么把“会因厂商而异的那一步”精确隔离成 <code>_generate</code> 一个抽象方法，而不是让厂商重写整个 invoke？",
                "opts": [
                    "让厂商多写代码",
                    "把“变化点”收敛到最小：厂商只关心自己独特的部分，其余流程不可能被写错或写偏",
                    "防止厂商创新",
                    "没有原因",
                ],
                "answer": 1,
                "why": "“识别变化点、把它隔离成最小扩展接口”是模板方法的精髓——扩展成本低、出错面小、流程一致。",
            },
            {
                "q": "顺着调用链读源码，能体会到“包边界与分层”在代码里的样子。这说明好的架构有什么特征？",
                "opts": [
                    "文件很多",
                    "宏观的分层思想能在微观的调用链里被一眼认出——结构是自洽、可追溯的",
                    "代码很长",
                    "没有特征",
                ],
                "answer": 1,
                "why": "当“宏观设计”和“微观实现”对得上（包边界 ↔ 调用链 ↔ 模板方法），系统就是可理解的。读一条链就能验证整套架构。",
            },
        ],
        "open": [
            "模板方法把“通用流程”写死在基类。如果某厂商需求恰好和“通用流程”冲突（比如缓存语义不同），这种设计会变成阻碍吗？框架一般怎么留口子？",
            "“把变化点隔离成最小接口”听起来简单，但难在“预判哪里会变”。如果变化点选错了（该变的地方写死了），会发生什么？",
        ],
    },
    "12-tool-internals.html": {
        "mcq": [
            {
                "q": "去程“函数签名 → schema → tool_calls”、回程“tool_calls → 执行 → ToolMessage”全自动。这“两段翻译”把什么复杂性挡在了你看不见的地方？",
                "opts": [
                    "没挡什么",
                    "“Python 世界 ↔ 模型的 JSON 世界”之间繁琐易错的格式转换与配对，你只写普通函数",
                    "模型推理",
                    "网络请求",
                ],
                "answer": 1,
                "why": "把“函数↔JSON”双向翻译自动化，你的工具就是普通 Python 函数。这层翻译是 Agent 能“调用代码”的桥，被刻意隐藏。",
            },
            {
                "q": "工具结果和请求靠 <code>id</code> 配对（tool_call_id）。为什么需要 id，而不是按顺序匹配？",
                "opts": [
                    "凑字段",
                    "一次可能并行发起多个工具调用，结果回来的顺序不定，用 id 才能可靠地把“结果”对回“请求”",
                    "id 更短",
                    "防止重复",
                ],
                "answer": 1,
                "why": "并行/乱序场景下，位置不可靠、id 才可靠。这个看似不起眼的 id，是支持“并行工具调用”的前提。",
            },
            {
                "q": "参数校验失败时默认不崩溃，而是把 <code>ValidationError</code> 包成 <code>ToolMessage(error)</code> 回灌给模型。这让 Agent 获得了什么？",
                "opts": [
                    "永不失败",
                    "自我纠正：模型读到报错→改对参数再试，错误成为新观察而非程序崩溃",
                    "隐藏错误",
                    "更快崩溃",
                ],
                "answer": 1,
                "why": "把“异常”翻译成“对话里的反馈”，闭环从崩溃变成纠正。这是 Agent 鲁棒性的来源，也呼应第 8 课的“错误转消息”。",
            },
            {
                "q": "类型注解和 docstring“直接决定模型看到的工具说明”。这把“写好注解/文档”从‘好习惯’变成了什么？",
                "opts": [
                    "可选项",
                    "影响模型能否正确调用工具的“功能性需求”——注解/文档写不好，模型就用不对工具",
                    "装饰",
                    "没影响",
                ],
                "answer": 1,
                "why": "当文档成了“喂给模型的说明书”，它就不再是给人看的可选注释，而是直接影响 Agent 行为的输入。",
            },
        ],
        "open": [
            "用 id 配对支持了“并行工具调用”。但并行也意味着多个工具可能同时改外部状态、互相干扰。你会怎么判断哪些工具适合并行、哪些必须串行？",
            "“把工具说明书交给类型注解和 docstring”很优雅，但模型表现就依赖你写得好不好。你会怎么测试“模型到底有没有看懂你的工具”？",
        ],
    },
    "13-agent-internals.html": {
        "mcq": [
            {
                "q": "<code>create_agent</code> 最核心的内部产物是什么？",
                "opts": [
                    "一段固定 prompt 字符串",
                    "只包含 provider SDK 的客户端对象",
                    "一张包含 model 节点、可选 ToolNode、条件边和 messages state 的 <code>StateGraph</code>",
                    "一个只能同步运行的 while 循环",
                ],
                "answer": 2,
                "why": "create_agent 的关键不是立即执行模型，而是把声明式参数编译成 LangGraph 状态图，运行时再由图调度。",
            },
            {
                "q": "为什么 Agent 的 <code>messages</code> 状态通常使用 <code>add_messages</code> reducer？",
                "opts": [
                    "让节点只返回新增消息，由 reducer 负责追加、按 id 合并和处理并行写入",
                    "让所有消息在每一轮都被删除",
                    "让工具不能返回 ToolMessage",
                    "让模型绕过系统提示",
                ],
                "answer": 0,
                "why": "model 和 tools 节点都只应表达自己的增量输出；合并历史的规则集中在 reducer，图才容易持久化和调试。",
            },
            {
                "q": "在 create_agent 构出的图里，<code>ToolNode</code> 的职责是什么？",
                "opts": [
                    "替代模型生成最终回答",
                    "检查最新 AIMessage 的 tool_calls，直接决定是否 END",
                    "执行模型请求的工具调用，并把结果包装为与请求 id 配对的 ToolMessage",
                    "保存用户密码和 API key",
                ],
                "answer": 2,
                "why": "ToolNode 是工具执行阶段：按 name/args 调用工具，并把观察结果写回消息历史，供下一轮 model 使用。",
            },
        ],
        "open": [
            "选择一个 create_agent 调用，把 model、tools、middleware、context_schema、response_format 分别映射到图里的节点、边、state 或 runtime 组件。",
            "给一条具体用户请求画出 graph path：从入口到 model，再到 tools 或 END，标出每一步哪个 state key 被读写。",
        ],
    },
    "14-streaming-callbacks.html": {
        "mcq": [
            {
                "q": "stream 中的 chunk 与最终 <code>AIMessage</code> 是什么关系？",
                "opts": [
                    "chunk 就是已经完成的最终消息，不能再合并",
                    "chunk 是增量片段，通常需要合并后才得到完整消息和最终元数据",
                    "chunk 只用于日志，不会给 UI 使用",
                    "最终消息会自动执行所有 chunk 中的工具",
                ],
                "answer": 1,
                "why": "流式输出让用户更早看到增量，但 chunk 边界不等于完整语义边界。最终消息仍是更稳定的结果对象。",
            },
            {
                "q": "callbacks 与 middleware 的边界更接近哪种描述？",
                "opts": [
                    "callbacks 负责业务权限，middleware 只能打印 token",
                    "二者都只能在页面层工作",
                    "callbacks 偏观察事件，middleware 偏改变或包裹运行行为",
                    "二者完全等价，没有设计边界",
                ],
                "answer": 2,
                "why": "callbacks 适合 tracing、日志和 token 事件；middleware 更适合拦截、限流、重试或注入策略。混用会模糊责任。",
            },
            {
                "q": "为什么需要 <code>astream_events</code> 这类事件流，而不只看最终文本？",
                "opts": [
                    "事件流会提高模型准确率",
                    "事件流会替代所有业务日志和数据库",
                    "事件流只包含最终答案，没有中间过程",
                    "事件流能展示链、模型、工具等内部步骤的 start/stream/end/error，支撑细粒度 UI 和排错",
                ],
                "answer": 3,
                "why": "复杂链路中，最终文本不足以解释发生了什么。事件流把内部运行过程变成可观察证据。",
            },
        ],
        "open": [
            "设计一个 UI token stream：前端如何接收 chunk、节流渲染、处理最终消息和错误状态，避免把半截 JSON 当成完成结果？",
            "如果 callbacks 要记录调试信息，如何避免把系统提示、用户隐私、工具返回的秘密写进日志？请写出脱敏或白名单策略。",
        ],
    },
    "15-contributing.html": {
        "mcq": [
            {
                "q": "调试 <code>create_agent</code> 行为时，为什么第一步要确认 package boundary，而不是直接改最长的内部文件？",
                "opts": [
                    "因为 import 路径、源码目录和发布包边界决定测试范围与兼容性风险",
                    "因为最长的文件通常没有任何逻辑",
                    "因为所有 Agent 代码都在同一个 Python 文件里",
                    "因为 CI 只检查 README，不检查源码",
                ],
                "answer": 0,
                "why": "先确认入口属于 langchain_v1、langchain-core 还是 LangGraph，才能选择正确源码锚点、测试命令和 PR 风险说明。",
            },
            {
                "q": "一个聚焦测试在贡献循环里最直接解决什么问题？",
                "opts": [
                    "先跑全量测试并根据最早失败猜测范围",
                    "只证明 reviewer 能读懂 PR，不验证行为",
                    "把失败缩到一个可解释行为，先红后绿，再扩大到相关检查",
                    "让生成 HTML 不需要提交",
                ],
                "answer": 2,
                "why": "聚焦测试给出明确因果：这个行为以前失败，修复后通过。之后再跑包级或 CI 级检查。",
            },
            {
                "q": "教程和 PR 说明为什么优先写“文件 + 符号名”而不是固定行号？",
                "opts": [
                    "因为符号名不能搜索",
                    "因为行号能跨版本保持不变",
                    "因为文件名不需要核验",
                    "因为符号锚点比行号更抗上游重排，reviewer 仍能复查结论",
                ],
                "answer": 3,
                "why": "行号会随着格式化和重构漂移；文件 + 符号名既可复查，又更适合长期教程和开源 PR。",
            },
        ],
        "open": [
            "某公开 API 在本地表现异常。请写出调试计划：如何确认导入的是 editable 源码、如何定位包边界、先跑哪个聚焦测试、再跑哪些 CI 同款检查？",
            "为一个小 PR 写提交前说明：问题、源码锚点、测试命令、生成物同步、兼容性风险分别怎么描述？",
        ],
    },

    "40-testing-debugging.html": {
        "mcq": [
            {
                "q": "在无工具绑定的模型单元测试中使用 <code>GenericFakeChatModel</code> 的主要目的是什么？",
                "opts": [
                    "评估真实模型的推理质量",
                    "用预设消息消除模型随机性，验证消息脚本、token callback 或无工具链路",
                    "自动替换所有工具实现",
                    "让 <code>create_agent(model, tools=[...])</code> 不再需要 <code>bind_tools</code>",
                ],
                "answer": 1,
                "why": "GenericFakeChatModel 不实现 bind_tools，适合 no-tool 模型输出、stream/token/callback 等测试；Agent 工具循环要用实现 bind_tools 的 fake。",
            },
            {
                "q": "测试 <code>create_agent(model, tools=[...])</code> 的工具循环时，fake 模型最关键要实现什么？",
                "opts": [
                    "实现 <code>bind_tools</code>，并能按脚本返回带 <code>tool_calls</code> 的 <code>AIMessage</code>",
                    "只返回普通字符串，不返回消息对象",
                    "直接执行生产数据库查询",
                    "跳过 <code>ToolMessage.tool_call_id</code> 配对",
                ],
                "answer": 0,
                "why": "create_agent 会把工具 schema 绑定到模型；fake 不支持 bind_tools 时，测试在进入 Agent 循环前就会失败。",
            },
            {
                "q": "确定性工具在测试中应该避免什么？",
                "opts": [
                    "真实网络、当前时间、随机数或生产副作用",
                    "明确的输入输出 fixture",
                    "受控错误分支",
                    "通过 <code>@tool</code> 暴露 schema",
                ],
                "answer": 0,
                "why": "这些因素会让测试慢且不可复现。单元测试工具应只依赖 fixtures，并把错误也做成确定分支。",
            },
            {
                "q": "回归 trace 断言比最终文本全文相等更稳，是因为它锁住了什么？",
                "opts": [
                    "模型回答的每个标点",
                    "真实 provider 的隐藏系统提示",
                    "CI 的运行机器型号",
                    "消息类型、工具名、参数、tool_call_id、结构化字段等行为骨架",
                ],
                "answer": 3,
                "why": "结构断言能定位 Agent 循环是否正确，同时避免同义措辞变化导致脆弱失败。",
            },
        ],
        "open": [
            "设计一个 fake Agent 测试：说明 ToolCallingFakeModel 如何实现 bind_tools，给出两条预设 AIMessage、一个确定性工具、一个 checkpointer，以及你会断言的消息状态。",
            "某测试最终答案正确但工具被调用了两次。请说明要怎样断言 messages 序列、tool_call_id 和 ToolMessage 内容来定位问题。",
        ],
    },

    "41-observability-ci.html": {
        "mcq": [
            {
                "q": "Callback/tracer 与 Agent middleware 的边界更准确的是？",
                "opts": [
                    "二者完全等价，只是名字不同",
                    "Callback 负责执行退款，middleware 只能打印日志",
                    "Callback 会自动修复所有 prompt 问题",
                    "Callback/tracer 偏观察运行事件，middleware 偏改变、包裹或拦截运行行为",
                ],
                "answer": 3,
                "why": "观察和干预要分开：trace 记录发生了什么，middleware 决定某些动作是否允许或如何包装。",
            },
            {
                "q": "CI 中的 generated drift gate 为什么要在重新 build 后运行 <code>git diff</code>？",
                "opts": [
                    "统计中文字符数量",
                    "删除没有链接的课程",
                    "确认提交的 HTML 与 src 重新生成结果一致，避免用户看到旧页面",
                    "替代所有人工 review",
                ],
                "answer": 2,
                "why": "源码生成型仓库必须防止 src 已变、lessons/index/print 未同步的情况；diff gate 把漂移变成失败。",
            },
            {
                "q": "<code>check_content_density.py</code> 的 density gate 主要防止什么退化？",
                "opts": [
                    "页面颜色不够鲜艳",
                    "C-level 课程缺少足够正文和 lesson_map/source_map/trace/lab 等语义组件",
                    "真实模型回答太短",
                    "GitHub Actions 机器太慢",
                ],
                "answer": 1,
                "why": "密度检查读取 raw lesson body，确保迁移页面不是空壳，也不缺少 C-level 必备教学结构。",
            },
        ],
        "open": [
            "为这个教程仓库设计一个 CI gate：写出生成、漂移检查、链接检查、结构检查、密度检查的顺序，以及每步失败说明什么。",
            "选择一次 Agent 运行，列出你会在 run tree 中记录的字段：run_id、父子关系、工具名、参数摘要、耗时、错误、脱敏策略。",
        ],
    },

    # ===== 第五部分 · 自己动手做 Agent =========================================
    "16-prompts.html": {
        "mcq": [
            {
                "q": "为什么说 prompt template 也是一个 <code>Runnable</code>？",
                "opts": [
                    "它能接收输入并产出 PromptValue / 消息，再和 model、parser 组成同一条管道",
                    "它会直接调用 provider SDK",
                    "它只能返回普通字符串，不能进入链",
                    "它会自动保存所有聊天历史",
                ],
                "answer": 0,
                "why": "Runnable 化让提示渲染成为链的一步：prompt | model | parser 可以共享 invoke、stream、config 等组合方式。",
            },
            {
                "q": "<code>MessagesPlaceholder</code> 相比把 history 拼成字符串，关键优势是什么？",
                "opts": [
                    "让历史永远不会超出上下文窗口",
                    "保留每条历史消息的角色、工具调用和元数据结构",
                    "把所有历史都改成 SystemMessage",
                    "让模型无法看到用户输入",
                ],
                "answer": 1,
                "why": "消息列表是结构化上下文。压平成字符串会丢失角色和 tool_call_id，影响多轮、工具回合和裁剪策略。",
            },
            {
                "q": "partial variables 最适合解决什么问题？",
                "opts": [
                    "让用户输入绕过模板校验",
                    "把模型输出提前写死",
                    "把稳定但重复的变量预先绑定到 prompt，调用时只传剩余动态输入",
                    "替代所有 runtime config",
                ],
                "answer": 2,
                "why": "partial 把固定上下文或格式说明预先填入模板，减少调用端重复，同时保留剩余变量的显式输入边界。",
            },
        ],
        "open": [
            "比较两种历史传入方式：一段 history 字符串 vs <code>MessagesPlaceholder</code> 消息列表。分别说明它们在角色保留、工具回合和裁剪上的后果。",
            "说明 prompt injection 的边界：系统提示、开发者模板、用户变量和检索内容各自应如何隔离，哪些内容不能被用户输入覆盖？",
        ],
    },
    "17-rag.html": {
        "mcq": [
            {
                "q": "RAG 端到端链路中，哪一步最直接负责把外部知识变成模型可读上下文？",
                "opts": [
                    "直接微调模型权重，让知识永久进入参数",
                    "只把用户问题原样发给模型，不做任何资料处理",
                    "让输出解析器随机选择一个引用编号",
                    "Retriever 返回 Document 后，由格式化步骤把 page_content 和 metadata 整理进 prompt context",
                ],
                "answer": 3,
                "why": "Retriever 只返回 Document；真正进入模型的是格式化后的 context，里面应保留 source、编号和边界说明。",
            },
            {
                "q": "为什么说 <code>BaseRetriever</code> 可以被放进 LCEL 链？",
                "opts": [
                    "因为它继承 Runnable 契约，能用 invoke/stream/config 等统一接口接收 query 并返回 Document",
                    "因为它只能返回字符串，不能返回 Document",
                    "因为它会自动调用所有工具",
                    "因为它负责训练 embedding 模型",
                ],
                "answer": 0,
                "why": "Retriever as Runnable 让检索成为链中的普通节点，也能被包装成 Agent 工具复用。",
            },
            {
                "q": "当 RAG 没检索到足够证据时，最稳妥的回答策略是什么？",
                "opts": [
                    "让模型凭常识补全缺失事实",
                    "删除所有 metadata，避免用户看到来源",
                    "承认证据不足、要求澄清或扩大检索，而不是编造带引用答案",
                    "把 top_k 调成 1，让答案更短",
                ],
                "answer": 2,
                "why": "RAG 的可信度来自证据链。证据不足时应降级或补检索，不能把流畅文本伪装成有来源的事实。",
            },
        ],
        "open": [
            "设计一条 RAG trace：从用户问题、可选 query rewrite、retriever 返回 Document、context 格式化到最终引用核验，说明每一步记录哪些字段。",
            "列出三个不适合优先使用 RAG 的场景，并说明这些场景更适合微调、规则系统、工具调用还是直接拒答。",
        ],
    },
    "36-documents-splitters.html": {
        "mcq": [
            {
                "q": "Document 的 metadata 在切块后为什么必须继续保留？",
                "opts": [
                    "metadata 只给前端美化使用，切块后可以删除",
                    "metadata 会让 embedding 维度自动变小",
                    "metadata 会替代 page_content 成为模型回答正文",
                    "metadata 保存 source、页码、权限和版本，决定后续能否引用、过滤和排障",
                ],
                "answer": 3,
                "why": "chunk 仍然要能回到父文档和权限边界；否则检索命中后无法引用，也可能越权。",
            },
            {
                "q": "chunk_overlap 的主要作用是什么？",
                "opts": [
                    "保护跨边界语义，避免定义、上下文或句子在硬切分时断裂",
                    "让所有 chunk 完全相同，便于缓存",
                    "强制 loader 跳过 metadata",
                    "把长文档直接交给模型而不做切分",
                ],
                "answer": 0,
                "why": "适量 overlap 能保住边界附近的语义；过大则会制造重复、成本和召回噪声。",
            },
            {
                "q": "Loader 与 Splitter 的责任边界哪项最准确？",
                "opts": [
                    "Splitter 负责连接数据库权限系统，Loader 只负责排序",
                    "Loader 必须决定最终 prompt 模板",
                    "二者没有区别，只是命名不同",
                    "Loader 负责读取外部来源并构造初始 Document；Splitter 负责把 Document 切成子 Document 并传播 metadata",
                ],
                "answer": 3,
                "why": "Loader 是摄取入口，Splitter 是索引前的粒度控制；二者都不能吞掉来源和权限字段。",
            },
        ],
        "open": [
            "给一篇包含标题、表格和步骤说明的文档设计 splitter：说明 chunk_size、overlap、separator 和 metadata 字段如何设置。",
            "调试一个丢引用问题：检索结果内容正确但没有 source/page。请按 raw page、Document、split_documents、add_documents 的顺序排查。",
        ],
    },
    "37-embeddings-vectorstores.html": {
        "mcq": [
            {
                "q": "Embeddings 契约中最关键的一致性要求是什么？",
                "opts": [
                    "每次查询都必须重新训练模型",
                    "文档和查询必须使用兼容的 embedding 模型与向量空间，否则相似度不可比较",
                    "metadata 必须为空，避免影响向量维度",
                    "VectorStore 只能保存一个文档",
                ],
                "answer": 1,
                "why": "换 embedding 模型通常意味着向量空间改变，旧索引需要重建或隔离命名空间。",
            },
            {
                "q": "<code>VectorStoreRetriever</code> 的价值是什么？",
                "opts": [
                    "把向量库包装成 BaseRetriever/Runnable，让 RAG 链按统一检索接口调用",
                    "把所有 Document 变成 SystemMessage",
                    "自动删除所有旧索引且无法关闭",
                    "替代 ChatPromptTemplate 生成最终答案",
                ],
                "answer": 0,
                "why": "as_retriever 暴露 query -> Document 的接口，屏蔽具体向量库实现，便于组合和替换。",
            },
            {
                "q": "为什么生产索引需要 stable id / source_id？",
                "opts": [
                    "为了让答案押韵",
                    "为了让模型跳过检索",
                    "为了支持 upsert、去重、cleanup 和排查 stale index",
                    "为了让 chunk_overlap 自动为 0",
                ],
                "answer": 2,
                "why": "没有稳定标识，更新同一来源时无法判断追加、覆盖还是删除旧版本，过期内容会长期留在检索结果里。",
            },
        ],
        "open": [
            "为一个小型知识库选择向量库：比较 InMemory、FAISS/本地库、托管向量库在规模、持久化、权限过滤和运维上的取舍。",
            "排查 stale index：用户问到旧政策，请设计检查顺序，包括 source_id、version、embedding_model、cleanup 和缓存。",
        ],
    },
    "38-retrievers-rerankers.html": {
        "mcq": [
            {
                "q": "两阶段检索中，第一层 broad retriever 通常追求什么？",
                "opts": [
                    "高召回，先把可能相关的候选尽量放进池子，再交给压缩或 rerank 精排",
                    "只返回一个最短 chunk，避免后续处理",
                    "直接生成最终自然语言答案",
                    "删除所有低分文档的 source 字段",
                ],
                "answer": 0,
                "why": "如果正确文档第一层没召回，后面的 reranker 没机会修复；所以第一层通常宁可多拿。",
            },
            {
                "q": "Contextual compression 的核心目的是什么？",
                "opts": [
                    "把用户问题永久写入向量库",
                    "让模型忽略所有引用",
                    "把检索到的候选按当前 query 裁剪、过滤或重排，减少无关上下文",
                    "替代 Loader 读取原始文件",
                ],
                "answer": 2,
                "why": "压缩器处理的是已召回 Document，目标是在保留证据的同时降低噪声和 token 成本。",
            },
            {
                "q": "为什么 reranker 不能解决所有检索失败？",
                "opts": [
                    "reranker 只能处理图片，不能处理文本",
                    "reranker 会强制关闭 metadata filter",
                    "reranker 的输出不能排序",
                    "reranker 只能重排或过滤候选；如果正确文档没有被 base retriever 召回，它根本看不见",
                ],
                "answer": 3,
                "why": "召回和精排是两层指标：先保证候选池覆盖，再优化排序和上下文精度。",
            },
        ],
        "open": [
            "设计一个 retriever stack：说明 base k、metadata filter、compressor、reranker、最终 top_k，以及每层记录哪些日志。",
            "针对“回答漏掉关键条件”的问题，说明如何调 top_k、score_threshold、rerank_k，并如何判断是召回问题还是压缩问题。",
        ],
    },
    "39-memory-conversation-state.html": {
        "mcq": [
            {
                "q": "Chat history、summary memory、checkpoint 的区别哪项最准确？",
                "opts": [
                    "三者完全相同，只是不同包的名字",
                    "Chat history 保存消息；summary 压缩长历史；checkpoint 保存线程状态快照以便恢复和调试",
                    "checkpoint 只能保存向量，不能保存消息",
                    "summary memory 必须永久保存所有敏感信息",
                ],
                "answer": 1,
                "why": "三者生命周期和用途不同：消息服务当前对话，摘要服务窗口压缩，checkpoint 服务状态恢复。",
            },
            {
                "q": "LangGraph 中 <code>add_messages</code> 常用于什么？",
                "opts": [
                    "把节点返回的消息增量合并进 state['messages']，并按消息 id 处理追加/覆盖",
                    "把所有用户偏好写入公开网页",
                    "把向量相似度改成余弦距离",
                    "把 retriever 自动变成 loader",
                ],
                "answer": 0,
                "why": "add_messages 是 messages 状态的 reducer，帮助多轮 Agent loop 保持结构化消息历史。",
            },
            {
                "q": "长期记忆写入最应该遵守哪条原则？",
                "opts": [
                    "只要用户说过就永久保存",
                    "为了个性化可以忽略删除请求",
                    "最小化、可解释、可删除，并过滤敏感或临时信息",
                    "把 checkpoint 当作公开知识库",
                ],
                "answer": 2,
                "why": "长期记忆涉及隐私和陈旧风险，必须有写入理由、过期/删除机制和使用边界。",
            },
        ],
        "open": [
            "为学习助手设计 memory policy：哪些内容进入最近窗口、摘要、长期偏好或拒绝保存？说明写入和删除规则。",
            "分析一次隐私泄漏风险：用户临时提供身份证号完成任务。系统在 chat history、checkpoint、summary、long-term memory 中应如何处理？",
        ],
    },
    "18-custom-middleware.html": {
        "mcq": [
            {
                "q": "哪一组最准确地区分了 AgentMiddleware 的 before/after 与 wrap 钩子？",
                "opts": [
                    "before/after 偏状态读写，wrap 偏包住一次模型或工具调用并控制是否调用内层 handler",
                    "before/after 只能用于工具，wrap 只能用于最终回答",
                    "before/after 会自动重试，wrap 只能打印日志",
                    "三者没有区别，只是命名不同",
                ],
                "answer": 0,
                "why": "状态钩子适合成为图节点；wrap 钩子拿到 handler，能重试、短路、替换请求或捕获异常。",
            },
            {
                "q": "多个 <code>wrap_model_call</code> 中间件叠加时，为什么顺序重要？",
                "opts": [
                    "顺序只影响代码格式，不影响行为",
                    "外层先看到请求、后看到响应；内外顺序会改变重试范围、审计粒度和错误处理语义",
                    "只有最后一个中间件会运行",
                    "顺序由模型随机决定",
                ],
                "answer": 1,
                "why": "洋葱式 wrapper 的外层/内层位置就是语义。审计包住重试和重试包住审计，记录结果会不同。",
            },
            {
                "q": "<code>HumanInTheLoopMiddleware</code> 最应该守住哪个边界？",
                "opts": [
                    "所有最终回答生成之后，再询问人类是否喜欢语气",
                    "模型第一次读取用户问题之前，阻止任何文本生成",
                    "敏感工具或有副作用动作执行之前，interrupt 等待人工批准",
                    "只在 build.py 生成 HTML 时运行",
                ],
                "answer": 2,
                "why": "HITL 的安全价值在于预防危险副作用，而不是事后通知。退款、发邮件、改数据库等动作应在执行前审批。",
            },
        ],
        "open": [
            "设计一个 guard middleware：说明哪些逻辑放 before_model，哪些放 wrap_tool_call，权限不足时抛异常还是生成 ToolMessage。",
            "调试一个 wrapper 顺序问题：审计、重试、fallback 三个中间件不同排序会产生哪些日志和行为差异？",
        ],
    },
    "19-runtime-context.html": {
        "mcq": [
            {
                "q": "<code>context</code> 与 Agent <code>state</code> 的核心区别是什么？",
                "opts": [
                    "二者完全相同，只是两个名字",
                    "context 只能保存 AIMessage，state 只能保存字符串",
                    "context 会自动展示给模型，state 永远不会",
                    "context 是每次调用注入的运行时环境，state 是图内可读写、可合并和可持久化的业务状态",
                ],
                "answer": 3,
                "why": "user_id、tenant、权限等适合放 context；messages、ToolMessage、structured_response 等属于图 state。分开才能安全和可测试。",
            },
            {
                "q": "<code>response_format</code> / 结构化输出策略的主要价值是什么？",
                "opts": [
                    "让模型输出更长的自然语言段落",
                    "跳过所有工具调用",
                    "把最终回答收束成应用可校验的结构化字段，而不是让下游解析自由文本",
                    "把 context 自动写入公开日志",
                ],
                "answer": 2,
                "why": "结构化响应是最终契约，方便 UI、后端和评测读取明确字段；它保证形状，不自动保证事实正确。",
            },
            {
                "q": "为什么工具应通过 <code>ToolRuntime</code> 读取 user_id/tenant，而不是让模型把这些字段作为工具参数填入？",
                "opts": [
                    "因为工具参数越多越慢",
                    "因为模型可能被用户诱导伪造安全字段；Runtime context 由应用可信注入，适合做权限和租户隔离",
                    "因为 ToolRuntime 会替代所有数据库查询",
                    "因为 structured_response 不能和工具同时使用",
                ],
                "answer": 1,
                "why": "安全上下文应来自可信运行时，而不是模型生成文本。模型只填业务参数，工具用 runtime 补齐身份与租户。",
            },
        ],
        "open": [
            "为一个多租户订单 Agent 设计 context_schema：列出字段、类型、谁能读取、哪些字段绝不进入 messages。",
            "说明如何避免泄漏 secrets：哪些信息可以脱敏后放 prompt，哪些只能留在 Runtime/ToolRuntime，日志又该如何脱敏？",
        ],
    },
    "20-capstone.html": {
        "mcq": [
            {
                "q": "客服 Agent capstone 中，哪组组件边界最健康？",
                "opts": [
                    "所有事实、权限和动作都写进一个巨大 prompt",
                    "RAG 直接执行退款，工具只负责解释政策",
                    "Prompt 定原则，RAG 给证据，工具做动作，middleware/context 守权限，response_format 收束结果",
                    "让模型从用户文本里生成 user_id 和 tenant",
                ],
                "answer": 2,
                "why": "端到端工程化强调关注点分离：每种能力放在最适合的机制里，才能测试、观测和演进。",
            },
            {
                "q": "结构化响应在客服 Agent 中最直接的收益是什么？",
                "opts": [
                    "保证所有事实都一定正确",
                    "让工具调用不再需要权限",
                    "自动替代 RAG 检索",
                    "把 answer、citations、next_action、needs_human 等字段变成 UI/后端可校验契约",
                ],
                "answer": 3,
                "why": "response_format 解决输出形状和下游读取问题；事实正确仍要靠资料、工具观察和校验。",
            },
            {
                "q": "Guard middleware 在高风险客服动作前最应该检查什么？",
                "opts": [
                    "最终回答是否足够长",
                    "页面是否包含类比卡",
                    "权限、金额/风险、工具类型、是否需要人审，以及安全字段是否来自 runtime context",
                    "模型 provider 的品牌名",
                ],
                "answer": 2,
                "why": "middleware 是横切护栏：它应拦截危险副作用、读取可信 context、记录审计，而不是只做文本润色。",
            },
        ],
        "open": [
            "设计一个最小客服 Agent：列出 prompt、两个工具、一个 retriever、一个 middleware、context_schema、response_format 和测试断言。",
            "识别一个失败模式：例如无证据仍退款、引用缺失、用户伪造身份、工具重复调用。说明 trace 中会看到什么，以及你会在哪个组件修复。",
        ],
    },
    "35-agent-control-errors.html": {
        "mcq": [
            {
                "q": "<code>recursion_limit</code> 在 Agent 图里的定位是什么？",
                "opts": [
                    "防止图无限推进的硬保险丝，超过后抛出 GraphRecursionError",
                    "让模型一定回答正确的质量评分",
                    "工具参数 schema 的字段数量限制",
                    "只影响 HTML 构建速度",
                ],
                "answer": 0,
                "why": "recursion_limit 限制的是图执行步数。触发它说明循环没有正常收敛，应查看 trace 找出模型为何一直请求工具。",
            },
            {
                "q": "<code>RunnableRetry</code> 与 <code>RunnableWithFallbacks</code> 的区别更准确的是？",
                "opts": [
                    "Retry 把失败交给用户，Fallback 删除错误日志",
                    "Retry 对同一路径做有限重试；Fallback 在主路径失败时切到备用 runnable，并且都需要可观测",
                    "二者只能用于 ToolMessage，不能用于模型",
                    "二者都会自动保证副作用幂等",
                ],
                "answer": 1,
                "why": "retry 解决短暂可恢复失败；fallback 解决主组件不可用。二者都不能替代幂等设计和告警。",
            },
            {
                "q": "工具执行失败时，什么时候更适合转成带 <code>tool_call_id</code> 的错误 <code>ToolMessage</code>？",
                "opts": [
                    "所有权限错误和内部栈都原样发给模型",
                    "支付扣款状态不一致时，让模型自行决定是否重试",
                    "任何有副作用工具超时时都自动重试并回填成功",
                    "用户输入导致的可恢复问题，例如订单号不存在、搜索无结果，且错误文案已脱敏",
                ],
                "answer": 3,
                "why": "可对话恢复的问题适合回填给模型；权限、内部 bug、危险副作用失败通常应抛出并交给应用层处理。",
            },
        ],
        "open": [
            "设计一个安全 Agent loop：写出软模型调用上限、recursion_limit、工具幂等策略和触发上限后的用户提示。",
            "把五类错误分类：模型 429、模型 schema 失败、查询工具 404、退款工具超时、权限不足。分别说明 retry、fallback、ToolMessage 或抛异常的策略。",
        ],
    },


    # ===== 第六部分 · 番外篇 ===================================================
    "21-langchain-vs-autogen.html": {
        "mcq": [
            {
                "q": "LangChain = 可组合的图（数据流优先），AutoGen = 自治 actor 的对话（多 Agent 优先）。这个“根本差异”告诉我们，看懂一个框架的关键是？",
                "opts": [
                    "记住它的 API",
                    "抓住它的“核心心智模型/默认重心”——其它差异大多能从这一条推导出来",
                    "比较谁的星多",
                    "看谁更新快",
                ],
                "answer": 1,
                "why": "框架的无数差异，往往源于一个根本的心智模型（图 vs actor）。抓住它，就能预测和理解其余设计——这是对照学习的价值。",
            },
            {
                "q": "课里强调两者的差别在“默认重心”而非“能不能”（LangChain 用 LangGraph 也能多 Agent）。为什么要区分“重心”和“能力”？",
                "opts": [
                    "咬文嚼字",
                    "几乎任何框架都“什么都能做”，真正决定体验的是“它让什么变容易”——选型应看默认重心而非功能清单",
                    "为了显得公平",
                    "没有意义",
                ],
                "answer": 1,
                "why": "“能不能”的对比常常无意义（都能），“默认让什么顺手”才决定开发体验。这是看待框架对比的成熟视角。",
            },
            {
                "q": "选型建议：要 RAG/可控工作流→LangChain，要快速多 Agent 协作→AutoGen。这种“按场景选”而非“谁更好”的态度说明？",
                "opts": [
                    "和稀泥",
                    "没有银弹：框架是为不同侧重设计的工具，“适合你的场景”才是唯一有意义的标准",
                    "两个都不行",
                    "随便选",
                ],
                "answer": 1,
                "why": "“哪个更好”是伪命题，“哪个更适合这个场景”才有答案。工程选型的本质是匹配需求与工具的默认重心。",
            },
            {
                "q": "课里说两者“边界在模糊”、可以互相借鉴。这对你理解技术生态有什么启发？",
                "opts": [
                    "框架都一样",
                    "好的设计会互相吸收（LangChain 学团队抽象、AutoGen 学集成/可控），框架在竞争中趋同又各有侧重",
                    "没必要学多个",
                    "越新越好",
                ],
                "answer": 1,
                "why": "生态里的框架既竞争又互鉴、边界流动。理解这点，你就不会“非此即彼”，而是从每个框架学它最擅长的设计。",
            },
        ],
        "open": [
            "“看框架先抓它的核心心智模型（图 vs actor）”。用这个方法，挑一个你最近接触的新框架/库，试着一句话说出它的“默认重心”。",
            "“没有银弹，只有适合的场景”。回想一次你的技术选型，当时是按“功能清单”还是“默认重心”选的？如果重来，你会怎么判断？",
        ],
    },
    "22-ai-stack.html": {
        "mcq": [
            {
                "q": "课里反复纠正“LangChain/AutoGen 不是最底层，它们在 L7 编排层”。把“认清自己在第几层”当成核心能力，图什么？",
                "opts": [
                    "显得有层次",
                    "坐标感：知道一个东西在哪一层，就知道它解决什么、依赖什么、和谁是邻居——不会把概念放错位置",
                    "记住更多名词",
                    "没用",
                ],
                "answer": 1,
                "why": "分层是一张“坐标系”。能给任何技术定位，你就能快速理解它的职责与边界——这比记住孤立名词有用得多。",
            },
            {
                "q": "课里教你遇到新名词“先问它在第几层”。这个习惯的价值是？",
                "opts": [
                    "装专业",
                    "用一个稳定的坐标系去消化层出不穷的新技术，避免被营销词淹没、能快速判断它和你的关系",
                    "让你显得懂",
                    "没价值",
                ],
                "answer": 1,
                "why": "技术名词爆炸，但分层坐标相对稳定。“先定位再判断”是应对信息过载的认知工具。",
            },
            {
                "q": "全栈分成“训练侧(L1-L4)”和“应用侧(L4-L7)”两条河，L4 模型是交汇口。这种划分帮你认清了什么？",
                "opts": [
                    "河流地理",
                    "99% 应用开发者只在 L4 以上工作（不需自己训模型），认清这点能让你把精力放对地方",
                    "训练更重要",
                    "应用更重要",
                ],
                "answer": 1,
                "why": "分清“造模型”和“用模型”两条路，你就知道自己该深耕哪侧、哪些层可以“交给大厂”。坐标系帮你做技术取舍。",
            },
            {
                "q": "把“横切带（评测/可观测/安全）”画成贯穿多层的独立一条，而不是塞进某一层。为什么？",
                "opts": [
                    "画着好看",
                    "这些是“每一层都需要”的横切关注点，独立出来才能表达“它不属于某层、而是贯穿全栈”",
                    "它们不重要",
                    "凑数",
                ],
                "answer": 1,
                "why": "和回调/config 的“横切”思想一致——可观测/安全不是某层专属，而是贯穿性的。画成独立带子是为了表达这种正交性。",
            },
        ],
        "open": [
            "“遇到新名词先问它在第几层”。最近哪个火热的 AI 名词让你困惑过？试着把它放进这张 7 层图里，看看它到底解决哪层的问题。",
            "课里说“应用开发者一辈子只在 L4 以上工作”。你认同吗？什么情况下，一个应用工程师值得往下深入到 L5/L3 甚至 L1？",
        ],
    },
    "23-learning-map.html": {
        "mcq": [
            {
                "q": "课里建议优先下探 L5(推理) 和 L6(检索)，而不是 L3(训练) 或 L1(硬件)。这个优先级的依据是？",
                "opts": [
                    "它们更简单",
                    "投入产出比：L5/L6 紧挨着你已会的应用层、学了立刻能用（解释慢/贵、让 RAG 更准），而 L3/L1 是另一条职业路线",
                    "它们更火",
                    "随便选的",
                ],
                "answer": 1,
                "why": "学习路径应按“与你当前能力的邻接度 + 即时收益”排序。L5/L6 是应用开发者性价比最高的下探方向。",
            },
            {
                "q": "vLLM 的 PagedAttention 把 KV-cache 当“虚拟内存分页”来管。理解这个设计，能让你抓住推理引擎的核心矛盾是？",
                "opts": [
                    "模型太大",
                    "显存的高效利用：把“碎片化的显存”用分页管起来，同一张卡就能扛更多并发——推理优化常是“显存/吞吐”之争",
                    "网络太慢",
                    "CPU 太弱",
                ],
                "answer": 1,
                "why": "借操作系统的成熟思想（分页）解决新问题（KV-cache 碎片），是好设计的共性。理解它，你就抓住了“推理服务”这层的核心矛盾。",
            },
            {
                "q": "推荐主线都是“先用(Ollama/Chroma 起步)→再读核心(vLLM/hnswlib)→要深度再扩展”。这个学习节奏的意图是？",
                "opts": [
                    "拖时间",
                    "先建立直觉再啃原理：能跑起来获得反馈，再深入实现，避免一上来啃硬骨头劝退",
                    "让你多学",
                    "没意图",
                ],
                "answer": 1,
                "why": "“能跑→读核心→工程深度”是符合认知规律的路径：先有体感、再求甚解。这本身就是一种教学设计。",
            },
            {
                "q": "hnswlib 被选为 L6 主攻，理由是“代码小、最适合读懂向量检索到底怎么算”。这种“选小而核心的项目入门”好在哪？",
                "opts": [
                    "省时间",
                    "用最小的代码量看清一个核心算法(HNSW/ANN)的本质，不被工程噪声淹没，学到可迁移的原理",
                    "它最流行",
                    "它最快",
                ],
                "answer": 1,
                "why": "入门读“小而纯”的实现能聚焦核心思想；工程级大库(FAISS/Qdrant)留到要深度时再看。这是“先原理后工程”的选材智慧。",
            },
        ],
        "open": [
            "课里按“与你能力的邻接度 + 即时收益”推荐先学 L5/L6。用同样标准，给你自己当前的技术栈排一个“接下来最该补的相邻一层”。",
            "PagedAttention 借用了操作系统“分页”、HNSW 借用了“跳表/小世界图”。这种“把老领域的成熟思想搬到新问题”的套路，你在别处还见过哪些例子？",
        ],
    },

    # ===== 第四部分 · LangGraph 心智模型 ======================================
    "24-langgraph-mental-model.html": {
        "mcq": [
            {
                "q": "为什么工具型 Agent 用纯 LCEL 链会别扭，而 LangGraph 更合适？",
                "opts": [
                    "因为 LangGraph 只能生成更漂亮的流程图",
                    "因为 Agent 需要在模型、工具和模型之间循环，并把 messages 等状态持续带到下一步",
                    "因为 LCEL 不能调用任何模型",
                    "因为 LangGraph 会自动让模型更聪明",
                ],
                "answer": 1,
                "why": "LCEL 擅长无环数据流；工具 Agent 的核心是状态 + 条件路由 + 回边。LangGraph 把这些隐式 while 逻辑变成显式状态图。",
            },
            {
                "q": "LangGraph 节点返回 <code>{'messages': [AIMessage(...)]}</code> 而不是整份 state，最重要的原因是什么？",
                "opts": [
                    "partial update 让运行时知道该节点写了哪个 key，并交给 reducer/channel 合并",
                    "这样可以避免写 Python 字典",
                    "这样节点就不能被测试",
                    "这样会跳过所有回调",
                ],
                "answer": 0,
                "why": "节点契约是 state -> partial state。返回增量能保持写入目标清晰，让 add_messages 等 reducer 处理合并。",
            },
            {
                "q": "LangChain v1 的 <code>create_agent</code> 与 LangGraph 更准确的关系是？",
                "opts": [
                    "create_agent 完全绕过 LangGraph，只使用字符串拼接",
                    "LangGraph 只负责前端可视化，不参与运行",
                    "二者只能二选一，不能同时出现",
                    "create_agent 是高层便利入口，底层 Agent 循环、状态和持久化能力建立在 LangGraph 上",
                ],
                "answer": 3,
                "why": "LangChain 提供易用 API，LangGraph 提供状态图运行时。高层 Agent 入口常把用户配置组装成可运行的 LangGraph 图。",
            },
        ],
        "open": [
            "选择一条已有 LCEL 链，指出从哪一步开始需要变成图：哪些数据要进入 state？哪些步骤会成为节点？哪条边会回到旧节点？",
            "为工具循环写一个终止策略：除了“没有 tool_calls 就 END”，还需要哪些最大轮数、错误状态或人审分支来防止无限循环？",
        ],
    },
    "28-langgraph-state-schema.html": {
        "mcq": [
            {
                "q": "下列哪项最适合放进 <code>context_schema</code>，而不是普通 state？",
                "opts": [
                    "会被 add_messages 合并的聊天历史",
                    "模型刚生成的最终回答",
                    "本次运行的 user_id、tenant_id、权限范围等环境信息",
                    "工具节点返回的 ToolMessage",
                ],
                "answer": 2,
                "why": "context 是运行环境，state 是会随节点演化并可能 checkpoint 的业务数据。用户、租户、权限通常属于 context。",
            },
            {
                "q": "一个 list 字段希望累积多个节点返回的日志，schema 中最容易漏掉什么？",
                "opts": [
                    "给这个字段声明 reducer，否则默认可能按 LastValue 覆盖",
                    "把所有节点改成同步函数",
                    "删除 output_schema",
                    "把日志写进 context",
                ],
                "answer": 0,
                "why": "list 类型不等于 append 语义。需要用 Annotated 或等价方式声明 reducer，运行时才知道怎样合并多次更新。",
            },
            {
                "q": "节点收到 state 后，推荐的更新方式是什么？",
                "opts": [
                    "原地修改 state，然后返回 None",
                    "把 context 复制进 state 的每个 key",
                    "总是返回整份 state，覆盖所有旧值",
                    "把 state 当只读输入，只返回本节点产生的 partial update",
                ],
                "answer": 3,
                "why": "partial update 能让运行时精确记录写入和调用 reducer；原地修改或整份覆盖都会削弱可追踪性。",
            },
        ],
        "open": [
            "为一个“订单客服 Agent”选择 state keys：messages、order_id、tool_attempts、retrieved_docs、final_answer、needs_human 中哪些需要 reducer？哪些应只做内部私有 state？",
            "你发现某节点直接对 messages 列表执行 append(msg) 后偶发丢历史。请写出调试步骤，并说明如何改成 partial update + reducer。",
        ],
    },
    "29-langgraph-nodes-edges.html": {
        "mcq": [
            {
                "q": "StateGraph 中一个普通业务节点最核心的契约是什么？",
                "opts": [
                    "读取 state，执行一步业务，返回 dict 形式的 partial state",
                    "只能返回字符串",
                    "必须决定整张图的下一跳",
                    "必须直接写数据库作为唯一输出",
                ],
                "answer": 0,
                "why": "节点做状态更新，不负责所有控制流。下一跳通常由普通边或条件边表达。",
            },
            {
                "q": "<code>add_conditional_edges</code> 的路由函数返回值最需要满足什么？",
                "opts": [
                    "必须是模型自然语言解释",
                    "必须是 True 或 False，不能是别的类型",
                    "必须能解析成有效节点名、END，或 path_map 中的键",
                    "必须返回完整 state",
                ],
                "answer": 2,
                "why": "条件边的输出是控制流目的地。返回值和节点名/path_map 不一致，就无法可靠调度下一步。",
            },
            {
                "q": "START 和 END 在图里代表什么？",
                "opts": [
                    "START 是第一个模型节点，END 是最后一个工具节点",
                    "START/END 是虚拟边界：入口和运行完成标记",
                    "START/END 是必须由用户实现的两个函数",
                    "START/END 只用于画图，不影响执行",
                ],
                "answer": 1,
                "why": "START 标出初始输入进入哪条边，END 标出图运行完成；它们不是普通业务节点。",
            },
        ],
        "open": [
            "写一个 <code>route_tools(state)</code> 的设计：它如何检查最后一条消息？返回哪些节点名或 END？如何处理消息为空或 tool_calls 重复？",
            "某图路径是 model -> tools -> model，线上出现无限循环。请列出你会检查的 state key、路由条件、最大轮数和错误分支。",
        ],
    },
    "30-langgraph-reducers-channels.html": {
        "mcq": [
            {
                "q": "没有显式 reducer 的普通 state key，最接近哪种语义？",
                "opts": [
                    "每次都自动 append",
                    "自动按 JSON diff 合并",
                    "LastValue：新值覆盖旧值，适合当前值/最终值",
                    "自动写入外部数据库",
                ],
                "answer": 2,
                "why": "默认覆盖适合 final_answer 等单值字段；需要累积或 fan-in 合并时必须声明 reducer。",
            },
            {
                "q": "<code>add_messages</code> 合并消息列表时，遇到相同 message id 通常意味着什么？",
                "opts": [
                    "按 id 替换旧消息，而不是无条件追加一条重复消息",
                    "抛弃所有消息",
                    "把 id 改成随机数",
                    "停止整张图",
                ],
                "answer": 0,
                "why": "add_messages 的关键是追加新 id、替换旧 id。手动设置重复 id 时要知道自己是在更新。",
            },
            {
                "q": "两个并行分支都写 <code>notes</code>，你希望下游看到两边结果，最合理的做法是？",
                "opts": [
                    "让两个节点都返回整份 state",
                    "给 notes 设计明确 reducer，或让两个分支写不同 key 后再汇总",
                    "把 notes 放进 runtime context",
                    "依赖哪个分支最后完成就用哪个",
                ],
                "answer": 1,
                "why": "并行 fan-in 需要明确合并法律。没有 reducer 时，覆盖或冲突都可能让结果不可解释。",
            },
        ],
        "open": [
            "为这些 key 选择合并语义并说明理由：final_answer、messages、retrieved_docs、risk_scores、audit_events。哪些用 LastValue？哪些需要 reducer？",
            "如果两条 AIMessage 使用同一个 id，add_messages 会发生什么？这对流式修正有何好处？对手写消息 id 有何风险？",
        ],
    },
    "31-langgraph-compile-runtime.html": {
        "mcq": [
            {
                "q": "<code>StateGraph.compile()</code> 和 <code>compiled.invoke()</code> 的关系，哪项正确？",
                "opts": [
                    "compile 负责校验和装配运行时；invoke 才真正执行节点",
                    "compile 会调用模型并返回最终答案",
                    "invoke 只能在 compile 前调用",
                    "二者完全等价，只是名字不同",
                ],
                "answer": 0,
                "why": "compile 把 builder 变成 CompiledStateGraph；运行发生在 invoke/stream/batch。",
            },
            {
                "q": "Runtime context 与 state 的区别是什么？",
                "opts": [
                    "二者没有区别",
                    "context 是运行环境输入；state 是会被节点更新、合并并可能 checkpoint 的业务数据",
                    "state 只能保存 user_id，context 只能保存 messages",
                    "context 会自动通过 add_messages 合并",
                ],
                "answer": 1,
                "why": "Runtime 向节点提供 context、store、stream_writer 等环境能力；只有 state key 的 partial update 才进入图状态合并。",
            },
            {
                "q": "使用 checkpointer 运行会话型图时，为什么常需要在 config 中提供 thread_id？",
                "opts": [
                    "thread_id 用来选择 HTML 模板",
                    "thread_id 会让模型跳过工具调用",
                    "thread_id 会改变 Python 类型检查结果",
                    "thread_id 通常用于定位保存/恢复哪一条会话线程的 checkpoint",
                ],
                "answer": 3,
                "why": "checkpointer 需要知道状态属于哪条线程/会话。缺失或复用错误 thread_id 都可能导致无法恢复或状态串线。",
            },
        ],
        "open": [
            "按时间线写出 build graph -> compile -> invoke -> run nodes -> produce state 每一步的输入、输出和不会发生的事情。",
            "给一个带 checkpointer 的客服图设计 config：thread_id 从哪里来？如何避免不同用户共享 thread_id？恢复时应检查哪些 state？",
        ],
    },

    # ===== 第五部分 · LangGraph 执行引擎 =====================================
    "25-langgraph-pregel-engine.html": {
        "mcq": [
            {
                "q": "Pregel/BSP 超步中的 Plan、Execution、Update 三段，最关键的工程收益是什么？",
                "opts": [
                    "取消 channel 和 reducer，直接修改全局 dict",
                    "保证模型回答一定正确，不再需要调试",
                    "让节点可以在同一超步内立刻读取彼此刚写入的半成品",
                    "把任务选择、并行执行、统一提交分开，让同批任务读稳定快照，结果更确定可复现",
                ],
                "answer": 3,
                "why": "BSP 屏障的核心是可见性控制：本步任务读上一轮已提交状态，写入缓冲后在 Update 阶段统一提交，避免调度顺序造成竞态。",
            },
            {
                "q": "为什么 LangGraph 要把节点写入先放进 buffered writes，而不是节点返回后马上改 channel？",
                "opts": [
                    "因为 Python 不能修改对象",
                    "因为所有写入都必须丢弃",
                    "为了让并行任务互相看不到本步半成品，apply_writes 再按 channel/reducer 规则统一合并",
                    "只是为了让日志更长，没有语义意义",
                ],
                "answer": 2,
                "why": "buffered writes 是确定性和 fan-in 的基础。它把节点执行与状态提交隔开，让合并规则集中在 Update 阶段。",
            },
            {
                "q": "prepare_next_tasks 在 Plan 阶段主要根据什么决定下一批内部可执行任务？",
                "opts": [
                    "channel 版本变化、订阅关系、branch/send 等运行时状态",
                    "源码文件里的函数定义顺序",
                    "节点函数运行耗时的排名",
                    "最终答案是否已经生成中文",
                ],
                "answer": 0,
                "why": "Plan 不是简单拓扑遍历，而是查看哪些 channel 有新可见版本、哪些节点订阅这些变化，以及是否有 Send 触发的 TASKS 通道写入或 branch。内部结果是可执行任务；公开 PregelTask 只是 debug/state 快照视图。",
            },
        ],
        "open": [
            "任选一个 model → tools → model 的图，按 Plan、Execution、Update 写出一个超步的任务选择、节点读取、buffered writes 和下一步可见状态。",
            "解释“本步写、下步见”为什么能减少并行竞态；如果改成节点返回后立即修改共享 state，会出现哪两类调试困难？",
        ],
    },
    "32-langgraph-tasks-channels.html": {
        "mcq": [
            {
                "q": "公开 PregelTask、内部 PregelExecutableTask 与用户定义 node 的关系，哪项最准确？",
                "opts": [
                    "三者完全相同，都是同一个函数对象",
                    "PregelTask 只用于保存最终答案，与 debug/state 无关",
                    "node 只能同步运行，PregelExecutableTask 只能异步运行",
                    "node 是定义；PregelExecutableTask 是某次内部执行实例；公开 PregelTask 是 StateSnapshot/debug 面向观察者的任务快照",
                ],
                "answer": 3,
                "why": "不要把公开 PregelTask 当成 Runner 手里的完整执行对象。公开快照偏向 id/name/path/error/interrupts/state/result；内部 PregelExecutableTask 才携带 input、writes、config、triggers、retry/cache 等执行上下文。",
            },
            {
                "q": "两个并行任务写同一个 channel 时，运行时应如何判断能否合并？",
                "opts": [
                    "看该 channel/reducer 是否定义了多写合并语义；没有语义时应暴露冲突",
                    "永远选择最后完成的任务",
                    "随机保留一个值以提高吞吐",
                    "把两个值转成字符串拼接，不需要 schema",
                ],
                "answer": 0,
                "why": "fan-in 的关键是业务合并规则。列表聚合、消息合并、数值累加可以由 reducer 表达；唯一值多写应失败。",
            },
            {
                "q": "ChannelWrite 的设计价值主要体现在哪里？",
                "opts": [
                    "让节点不需要返回任何内容",
                    "把 partial state、branch、send 等输出归一成标准 writes，方便 debug、checkpoint 和 apply_writes 处理",
                    "强制所有 channel 都只能保存字符串",
                    "绕过 Pregel 的 Update 阶段直接写数据库",
                ],
                "answer": 1,
                "why": "标准化写入让不同节点输出形式进入同一运行时管道，后续才能统一记录来源、合并和持久化。",
            },
        ],
        "open": [
            "设计一个并行检索 fan-out：两个 retriever 分别写什么 channel？如果都写 documents，reducer 应处理顺序、去重和失败中的哪些问题？",
            "某图报错说同一 step 多个任务写 final_answer。请写出排查路径：先看哪些 task，再判断应该加 reducer、拆 key，还是改图结构。",
        ],
    },
    "26-langgraph-persistence-control.html": {
        "mcq": [
            {
                "q": "configurable.thread_id 在 LangGraph 持久化中最核心的作用是什么？",
                "opts": [
                    "决定模型温度",
                    "作为会话/线程索引，让 checkpointer 找到同一条历史的最新或指定 checkpoint",
                    "自动加密所有消息",
                    "替代 state schema 和 reducer",
                ],
                "answer": 1,
                "why": "thread_id 是恢复同一运行历史的关键。没有稳定 thread_id，第二次调用通常会像新会话一样从空状态开始。",
            },
            {
                "q": "Checkpoint 与普通聊天日志的主要区别是什么？",
                "opts": [
                    "Checkpoint 只能保存字符串，聊天日志能保存对象",
                    "Checkpoint 不需要 checkpointer",
                    "Checkpoint 只在程序退出时生成一次",
                    "Checkpoint 保存图在超步边界恢复所需的 channel_values、channel_versions、versions_seen、updated_channels 和 metadata，不只是展示给用户的消息",
                ],
                "answer": 3,
                "why": "checkpoint 是运行状态存档，支撑 resume、get_state、history、interrupt 等能力；聊天日志只是其中可能的一部分。",
            },
            {
                "q": "使用 Pregel.update_state 修补状态时，哪种做法最安全？",
                "opts": [
                    "直接改底层存储里的 JSON，绕过运行时",
                    "不记录操作者和原因，避免日志太多",
                    "通过图的状态更新语义写入增量，并记录基于哪个 checkpoint、谁因为什么修改",
                    "只要能恢复就可以忽略 state schema",
                ],
                "answer": 2,
                "why": "update_state 仍应尊重 channel/reducer 语义，并保留审计信息，否则人审修补会变成新的黑盒。",
            },
        ],
        "open": [
            "为客服对话图设计 checkpoint config：thread_id 从哪个业务对象来？checkpoint_ns 何时需要？如何防止不同用户读到彼此状态？",
            "一次续聊丢失上下文。请按顺序检查 thread_id、checkpointer 生命周期、namespace、get_state 结果和 messages reducer。",
        ],
    },
    "33-langgraph-interrupt-command.html": {
        "mcq": [
            {
                "q": "interrupt 与普通异常最大的语义差别是什么？",
                "opts": [
                    "interrupt 表示受控暂停，预期通过 checkpoint 和 Command.resume 恢复；普通异常通常表示失败",
                    "interrupt 只能在测试里使用",
                    "interrupt 会自动执行所有高风险副作用",
                    "interrupt 不需要 thread_id 或 checkpointer",
                ],
                "answer": 0,
                "why": "GraphInterrupt 是运行时协议的一部分，用来把控制权交给调用方；它不是未处理错误。",
            },
            {
                "q": "Command(resume={...})、Command(update={...})、Command(goto='x') 分别表达什么？",
                "opts": [
                    "三者完全等价，只是字段名不同",
                    "resume 给等待的 interrupt 返回值，update 写状态增量，goto 指定后续控制流去向",
                    "resume 只能删除 checkpoint，update 只能改配置，goto 只能结束图",
                    "它们只影响前端 UI，不影响图运行",
                ],
                "answer": 1,
                "why": "Command 把恢复输入、状态更新和跳转控制放在一个正交原语里，适合人审、handoff 和修补流程。",
            },
            {
                "q": "在退款审批节点中，为什么高风险副作用通常应放在 interrupt 之后？",
                "opts": [
                    "因为 interrupt 之后不能再运行任何节点",
                    "因为审批前执行扣款更容易通过测试",
                    "因为恢复/重试可能重新执行 interrupt 前代码，副作用提前执行会造成重复扣款或重复发信",
                    "因为 Command 不能携带审批备注",
                ],
                "answer": 2,
                "why": "恢复语义要求副作用边界清晰。先暂停审批，通过后再 goto 幂等执行节点，是更安全的设计。",
            },
        ],
        "open": [
            "设计一个退款 approval flow：interrupt payload 包含哪些字段？resume payload 怎样结构化？哪些字段要写入 state 供审计？",
            "如果一个节点在 interrupt 前已经调用了外部发邮件 API，恢复时可能出现什么事故？请提出两种修复：移动副作用或做幂等。",
        ],
    },
    "34-langgraph-time-travel-debug.html": {
        "mcq": [
            {
                "q": "StateSnapshot 调试时为什么不能只看 values？",
                "opts": [
                    "因为还要结合 next、tasks、config、metadata 才能解释控制流、任务状态和写入来源",
                    "因为 values 永远为空",
                    "因为 values 只保存 CSS 样式",
                    "因为 StateSnapshot 不能用于调试",
                ],
                "answer": 0,
                "why": "坏答案可能来自错误路由、失败任务或错误写入来源；只看当前值无法解释状态是怎样变成这样的。",
            },
            {
                "q": "从生产 checkpoint 做时间旅行实验时，哪种方式更安全？",
                "opts": [
                    "直接覆盖主线历史，方便少存数据",
                    "从选定 checkpoint 在新 namespace/thread 中 fork，记录实验修改，再与主线比较",
                    "删除所有 metadata，避免干扰判断",
                    "只改最终 HTML，不看运行历史",
                ],
                "answer": 1,
                "why": "fork 能保护主线审计记录，同时允许对旧状态做受控实验。覆盖历史会破坏复盘能力。",
            },
            {
                "q": "调查坏答案时，最合理的第一步是什么？",
                "opts": [
                    "立刻重写所有 prompt",
                    "随机修改 reducer 直到答案变好",
                    "固定 thread_id 和最终 checkpoint，调用 get_state_history 找出错误第一次出现的 step",
                    "关闭 checkpoint，避免历史太复杂",
                ],
                "answer": 2,
                "why": "先定位错误首次出现的位置，才能判断根因是工具、路由、reducer、状态覆盖还是模型解释。",
            },
        ],
        "open": [
            "一次最终答案把 cancelled 订单说成 shipped。请写出如何用 get_state_history 找到工具结果写入、最终模型回答前后的关键 snapshots。",
            "你要从某个 checkpoint fork 做修复实验：选择 namespace、修改哪个状态、运行哪些后续节点、如何比较主线与分支？",
        ],
    },

}


def render(fname):
    """Return the self-test HTML block for ``fname`` (or '' if none defined)."""
    data = QUIZZES.get(fname)
    if not data:
        return ""
    out = ['<div class="selftest">', "<h2>🧪 自测 · 想一想为什么这么设计</h2>"]
    for i, item in enumerate(data.get("mcq", []), 1):
        shuffled, ans = _shuffle(item["opts"], item["answer"], f"{fname}:{i}")
        opts = "\n".join(f"    <li>{o}</li>" for o in shuffled)
        letter = chr(65 + ans)
        out.append(
            f'<div class="quiz">\n'
            f'  <div class="qn">{i}. {item["q"]}</div>\n'
            f'  <ol class="opts">\n{opts}\n  </ol>\n'
            f'  <details class="accordion">\n'
            f'    <summary>看答案与解析 <span class="hint">点击展开</span></summary>\n'
            f'    <div class="acc-body"><div class="qa"><div class="a">'
            f'<strong>答案：{letter}</strong>。{item.get("why", "")}'
            f"</div></div></div>\n"
            f"  </details>\n"
            f"</div>"
        )
    opens = data.get("open", [])
    if opens:
        lis = "\n".join(f"    <li>{o}</li>" for o in opens)
        out.append(
            '<div class="card spark">\n'
            '  <div class="tag">💭 发散思考（没有标准答案，动手或动脑想想）</div>\n'
            f"  <ul>\n{lis}\n  </ul>\n"
            "</div>"
        )
    out.append("</div>")
    return "\n".join(out)
