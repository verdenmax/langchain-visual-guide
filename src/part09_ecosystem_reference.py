"""C-level Part 9: ecosystem, reference, and glossary lessons."""

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


def _table(headers, rows, klass="t"):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return f'<table class="{klass}"><tr>{head}</tr>{"".join(body)}</table>'


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
    for title, paragraphs in d["sections"]:
        html += _section(title, paragraphs)
    for table in d.get("tables", []):
        html += f"<h2>{table['title']}</h2>" + _p(table["intro"]) + _table(
            table["headers"], table["rows"], table.get("klass", "t")
        )
    html += shell.pitfall_grid(d["pitfalls"])
    html += shell.lab_card(d["lab_title"], d["lab_steps"])
    html += shell.version_note(d["version_note"])
    html += _points(d["points"])
    return html


LESSON_41_CHAT_INTERNALS = _build_lesson(
    {
        "lead": "聊天模型内部的关键，不是某个 provider 的参数名字，而是 LangChain 如何把上层输入先收束成标准消息，再由具体适配器翻译成厂商 payload，最后把厂商响应归一回 <span class='mono'>ChatGeneration</span>、<span class='mono'>AIMessage</span>、usage metadata 与 response metadata。本课从 <span class='mono'>BaseChatModel</span> 往下看 provider adapter：输入转换、payload 构造、网络调用、响应标准化、回调与流式分片如何分层。读完后，你应该能解释为什么业务代码不该直接依赖 OpenAI 或 Anthropic 的原始响应字段，也能在模型行为异常时判断问题发生在输入标准化、provider 请求、响应解析还是消息回填阶段。",
        "analogy": "把聊天模型适配器想成国际快递的转运中心。寄件人可以拿纸箱、文件袋或托盘来，中心先统一贴成内部运单；发往美国、法国、日本的航班有各自报关单和标签，这一层由对应航空公司窗口处理；包裹回来后，转运中心再把不同国家的回执翻译成统一的签收记录。<span class='mono'>BaseChatModel</span> 像转运中心的总流程，<span class='mono'>ChatOpenAI</span>、<span class='mono'>ChatAnthropic</span> 像不同航司窗口，<span class='mono'>ChatGeneration</span> 像统一签收单。用户关心的是包裹有没有送到、花了多少费用、有没有异常，而不是每家航司内部字段叫什么。",
        "map_title": "本课地图：从任意输入到标准聊天结果",
        "map_nodes": [
            ("用户输入", "字符串、PromptValue、BaseMessage 列表等输入先进入统一入口", "before"),
            ("消息标准化", "_convert_input 与 convert_to_messages 把输入变成 BaseMessage 序列", "now"),
            ("Provider payload", "ChatOpenAI、ChatAnthropic 等 wrapper 把标准消息翻译成自家 API 格式", "source"),
            ("响应归一", "原始响应被还原成 AIMessage、ChatGeneration、token usage 与 metadata", "now"),
            ("上层组合", "Runnable、Agent、回调和追踪只看统一结果，不读 provider 私有字段", "after"),
        ],
        "source_intro": "下面的 source map 使用当前可复查的文件与符号名。这里故意不写行号，因为上游实现会移动；但文件和类/函数名能稳定指向阅读入口。重点是分清 core 契约与 partner 适配：core 定义标准消息和生成结果，partner 包负责把这些标准对象翻译到具体厂商。",
        "sources": [
            {"file": "libs/core/langchain_core/language_models/chat_models.py", "symbol": "BaseChatModel", "role": "聊天模型基类，定义 invoke/generate/stream 等共享骨架和子类扩展点", "direction": "上层 Runnable 调用先进入这里，再委派给具体 provider 实现"},
            {"file": "libs/core/langchain_core/language_models/chat_models.py", "symbol": "BaseChatModel._convert_input", "role": "把 str、PromptValue、消息序列统一成 PromptValue/消息输入，隔离调用者输入形态", "direction": "位于 provider 调用前，是所有聊天模型共享的输入入口"},
            {"file": "libs/core/langchain_core/messages/utils.py", "symbol": "convert_to_messages", "role": "把消息类、元组、字典等 message-like 表示转为 BaseMessage 列表", "direction": "供 prompt、chat model、agent loop 共享，避免每个 provider 自己猜输入"},
            {"file": "libs/partners/openai/langchain_openai/chat_models/base.py", "symbol": "ChatOpenAI", "role": "OpenAI 聊天模型适配器，负责 OpenAI 风格 payload、工具 schema 与响应字段处理", "direction": "继承 core 契约，在 provider 边界做翻译"},
            {"file": "libs/partners/anthropic/langchain_anthropic/chat_models.py", "symbol": "ChatAnthropic", "role": "Anthropic 聊天模型适配器，处理 Claude 消息、内容块、工具调用和元数据差异", "direction": "与 ChatOpenAI 并列，说明差异应留在 partner 层"},
            {"file": "libs/core/langchain_core/outputs/chat_generation.py", "symbol": "ChatGeneration", "role": "单个聊天生成结果，封装 message、generation_info 和文本派生字段", "direction": "provider 返回后归一到它，上层再读取 AIMessage 与 metadata"},
        ],
        "flow_title": "调用图：共享骨架与 provider 翻译点",
        "flow_kind": "call_graph",
        "flow_steps": [
            ("model.invoke(input)", "Runnable 入口携带 config、callbacks、tags、metadata", False),
            ("_convert_input", "把 str/PromptValue/message-like 变成标准消息视图", True),
            ("generate_prompt", "共享层处理缓存、回调、批量、stream 分支和错误事件", False),
            ("_generate/_stream", "具体 provider adapter 构造 payload 并调用 SDK 或 HTTP API", True),
            ("ChatResult", "把 raw choices/content blocks/tool calls/usage 归一成 ChatGeneration", True),
            ("AIMessage", "上层看到统一消息、tool_calls、usage_metadata、response_metadata", False),
        ],
        "trace": [
            {"step": "1. input", "input": "用户传入 '查一下订单 42' 或 [HumanMessage(...)]", "action": "BaseChatModel 不直接把字符串交给 provider，而是先走输入转换", "output": "标准化的 BaseMessage 序列"},
            {"step": "2. config/callback", "input": "messages + RunnableConfig", "action": "共享骨架合并 config，触发 chat_model_start，建立 trace 节点", "output": "可观测运行上下文"},
            {"step": "3. payload", "input": "BaseMessage + tools/response_format 等参数", "action": "ChatOpenAI 或 ChatAnthropic 按各自 API 生成 role/content/tool schema/payload", "output": "provider 请求体"},
            {"step": "4. provider response", "input": "raw response、content blocks、token usage、tool calls", "action": "adapter 解析字段、补齐 tool_call id、整理 usage 与 finish reason", "output": "ChatGeneration(message=AIMessage(...))"},
            {"step": "5. return", "input": "ChatResult.generations", "action": "invoke 取第一条 message；stream 则逐块合并 chunk", "output": "业务代码读取统一 AIMessage"},
        ],
        "code_path": "libs/core/langchain_core/language_models/chat_models.py + partner wrappers",
        "code_symbol": "BaseChatModel.invoke/_convert_input/_generate",
        "code": """# 教学版：真实代码还有缓存、回调、stream、batch、错误分支
class BaseChatModel:
    def invoke(self, input, config=None, **kwargs):
        prompt = self._convert_input(input)
        result = self.generate_prompt([prompt], config=config, **kwargs)
        return result.generations[0][0].message

    def _convert_input(self, input):
        if isinstance(input, str):
            return StringPromptValue(text=input)
        if is_message_sequence(input):
            return ChatPromptValue(messages=convert_to_messages(input))
        return input

class ChatOpenAI(BaseChatModel):
    def _generate(self, messages, **kwargs):
        payload = self._create_message_dicts(messages, **kwargs)
        raw = self.client.chat.completions.create(**payload)
        return self._create_chat_result(raw)
""",
        "code_note": "这段伪码只保留契约：BaseChatModel 固化共享调用骨架，_convert_input 负责把输入变成标准中间表示，provider 子类只实现变化点。真实实现会继续处理缓存、回调、异步、流式 chunk、tool calling、结构化输出和 provider 专属参数。",
        "sections": [
            ("为什么先统一成 BaseMessage", [
                "聊天模型的上层调用形态非常宽：有人直接传字符串，有人传 ChatPromptValue，有人传 SystemMessage、HumanMessage、AIMessage、ToolMessage 混合列表，还有人从 prompt 模板或 Agent 状态里传出 message-like 字典。若每个 provider wrapper 都自行解释这些输入，差异会迅速扩散：某个 wrapper 接受二元组，另一个只接受消息对象，第三个把 tool message 当普通文本。统一成 BaseMessage 不是为了形式好看，而是为了把输入语义固定在 core 层。",
                "BaseMessage 是 LangChain 的聊天中间表示。它保留 role、content、name、id、additional_kwargs、response_metadata 等跨 provider 可能有用的信息，同时允许上层链、回调、Agent、LangGraph state 都围绕同一对象工作。等到真正调用 provider 时，adapter 再把 HumanMessage 翻译成 OpenAI 的 role=user 或 Anthropic 的 message block；这个翻译点越靠近 provider，越容易随 SDK 演进而局部调整。",
            ]),
            ("Provider payload 是边界，不是业务模型", [
                "OpenAI、Anthropic 和其他厂商的请求体经常在字段命名、工具 schema、流式事件、内容块结构和安全参数上不同。LangChain partner wrapper 的职责就是承接这些差异：把标准消息变成该厂商接受的 payload，把统一的 tools 参数变成厂商理解的工具声明，把通用 stop、temperature、max tokens 等配置放到正确位置。业务代码若直接拼这些 payload，就等于绕过适配层，把易变细节写进应用核心。",
                "边界还体现在错误与元数据。provider 可能返回 request id、model name、finish reason、safety signal、token usage、cache usage 或若干实验字段。适配器通常会把可通用的信息放进 usage_metadata 或 response_metadata，把无法标准化但仍有调试价值的字段保留在 metadata 中。上层应优先读取标准字段，只有做 provider 特定排障时才下钻原始信息。",
            ]),
            ("ChatGeneration 与 AIMessage 的关系", [
                "很多人只看到 model.invoke 返回 AIMessage，于是忽略了内部还有 ChatResult 与 ChatGeneration。生成结果对象的价值，是把“模型产生的一条候选”与它的附加信息绑在一起。对于 invoke，通常取第一条候选的 message；对于 generate/batch，可能返回多个 prompt、多个候选；对于 stream，则会先得到 chunk，再合并成完整 message。ChatGeneration 让这些场景有统一容器。",
                "AIMessage 则是对话历史要保存的消息。它可以有 content，也可以有 tool_calls；可以携带 usage_metadata，也可以携带 provider response_metadata。Agent loop 最关心的是 tool_calls 是否存在，RAG 与日志最关心的是 content 与 metadata，成本统计最关心 usage。把这些信息放在统一消息里，LangGraph 的 add_messages、callbacks、LangSmith trace 和测试断言就能共享同一套结构。",
            ]),
            ("读源码时如何定位差异", [
                "遇到模型行为异常，先不要直接怪模型。第一步确认输入是否被标准化成你预期的消息序列：系统提示有没有丢，历史消息顺序是否正确，ToolMessage 的 tool_call_id 是否还在。第二步看 provider payload：工具 schema 是否被翻译，参数名是否符合厂商要求，是否把结构化输出和工具调用混在一起。第三步看响应归一：raw response 中是否本来就没有 tool calls，还是 adapter 解析时丢失了。",
                "这个排查顺序能避免把所有问题都推给 prompt。比如模型没有调用工具，可能是 bind_tools 没进 payload；模型调用了工具但 Agent 没执行，可能是 tool_calls 没被标准化进 AIMessage；成本统计缺失，可能是 usage 字段没有映射到 usage_metadata；流式 UI 卡住，可能是 stream chunk 合并和 callback 事件顺序不匹配。每个现象都对应调用链的一段。",
            ]),
            ("流式与非流式只是返回节奏不同", [
                "非流式调用像一次性拿到完整包裹，stream 像快递员一路播报“已揽收、已装车、已到站”。但二者共享的语义应尽量一致：输入仍要标准化，provider payload 仍要构造，回调仍要记录开始和结束，最终仍应能合并成一条 AIMessage。差异在于 adapter 需要把 provider 的 event stream 转成 ChatGenerationChunk 或 AIMessageChunk，并让上层逐块消费。",
                "因此排查 stream 问题时要分清“最终消息正确但中间事件不顺”与“最终归一也错”。前者可能影响 UI 和实时回调，后者会影响 Agent 后续控制流。若 provider 流式事件包含工具调用增量，adapter 还要正确合并 tool call name、args、id；否则模型明明发出了工具请求，最终 AIMessage.tool_calls 却可能不完整。",
            ]),
            ("边界情况：provider 响应并不总是规整的", [
                "把响应归一想象成每次都能拿到干净的 content 加 tool_calls，是低估了 provider 的多样性。真实响应里，content 可能为空而只带 tool_calls，可能由多个内容块（文本块、图片块、引用块、推理块）组成列表，也可能因为安全策略返回拒答或被长度截断。finish reason 在不同 provider 下取值不同：正常结束、达到 max tokens、因工具调用停止、被内容过滤拦截，含义都不一样。适配层要做的，是在这些形态之间挑出上层真正需要的标准字段，而不是假设每次响应都长一个样。",
                "流式让边界情况更明显。工具调用的参数往往分片到达，token usage 常常只在最后一个 chunk 给出，部分 provider 还会把推理过程或缓存信息放进独立事件。如果 adapter 合并 chunk 时没有正确拼接 tool call 的 name、args 和 id，最终 AIMessage.tool_calls 就可能缺字段，导致 Agent 下一步只拿到半个工具请求。排查 stream 问题时，要先分清是中间事件顺序不顺，还是最终合并结果本身就错：前者主要影响实时 UI 和回调，后者会污染后续控制流。",
            ]),
            ("常见误解：标准化不是抹平 provider 能力", [
                "统一成 AIMessage、ChatGeneration 和标准 metadata，统一的是结构形状，不是底层能力。不同 provider 对并行工具调用、严格 JSON schema、系统提示位置、多模态输入、缓存计费的支持并不一致。看到消息里有某个字段，不代表当前模型一定会填它；期望换一个 provider 后行为完全相同，往往会落空。正确心态是：读标准字段是对的，但要把跨 provider 的能力差异当成需要显式验证的变量，而不是默认成立的常量。",
                "结构化输出也常被误解。with_structured_output 在不少实现里其实是借助工具调用或 response_format 完成的，并不是模型内置的魔法；bind_tools 只是把工具声明放进 payload，模型是否真的调用仍由它自己决定。同理，设定 temperature 或 seed 也不能保证逐字可复现。把这些机制当成确定性保证，会让测试和线上行为对不上。理解“统一接口背后仍是各自实现”，才能在 provider 之间迁移时少踩坑。",
            ]),
            ("usage 与 metadata：成本与排障的统一入口", [
                "成本统计最怕每个 provider 各报各的。适配层通常会把输入、输出、总 token 汇总进 usage_metadata，把缓存读写等细分项放到更具体的字段或 metadata。业务侧据此做配额、计费和容量评估，就不必关心某个 provider 把字段叫 prompt_tokens 还是 input_tokens。当 usage 缺失时，往往不是模型没返回，而是 adapter 在某条响应路径（尤其是流式路径）上没有映射，这恰恰是该补契约测试的地方。",
                "response_metadata 则是排障证据带。它适合保留 request id、model name、system fingerprint、finish reason、限流或安全信号等不便标准化、但调试有用的信息。原则仍是分层读取：业务逻辑读标准字段，观测与排障读 metadata，只有写 provider 专属能力时才下钻原始响应。把这三层分清，既能享受跨 provider 的统一，又不至于在需要深挖时无据可查。",
            ]),
            ("把 provider 边界写成可回归测试", [
                "适配层最该被测试，却经常被跳过。契约测试的思路是：用一个可控的假聊天模型或最小真实调用，断言上层拿到的标准字段是否正确，例如 content 是否非空、tool_calls 是否包含预期 name 和 args、usage_metadata 是否汇总了 token。断言对象应该是标准消息，而不是某个 provider 的原始 JSON；后者一旦升级就会让测试无谓地变红，反而掩盖真正的回归。",
                "版本策略是这层测试的延伸。升级 partner 包时，先跑适配层契约测试，再判断是否影响业务链。保持适配层是一条薄缝：provider 字段变化时只改这条缝，不让它扩散到 prompt、Agent 或图节点。同时在 response_metadata 里保留 request id、model name、finish reason 等线索，这样线上出问题时，你能用一次调用的证据快速判断问题落在输入标准化、payload、原始响应还是归一阶段。",
            ]),
            ("设计取舍：为什么要把变化点关进适配层", [
                "软件设计里一个反复出现的原则，是把最常变化的部分与最需要稳定的部分分开。聊天模型领域里，最常变化的就是各家厂商的请求格式、字段命名、工具声明方式和响应结构；最需要稳定的，是上层链路、智能体循环、图状态和测试断言所依赖的那套消息与生成结果。把厂商差异关进适配层，本质上是在易变与稳定之间立一道墙，让墙内的演进不至于震动墙外的业务。",
                "这道墙带来的第一个好处是可替换。当你想从一家厂商切换到另一家，或在同一应用里按成本和能力混用多家时，理想情况是只更换适配层，而上层链路、提示、工具和测试基本不动。如果业务代码到处直接读厂商私有字段，这道墙就被打穿了，切换会演变成全局手术。第二个好处是可测试：墙的接口稳定，你才能用假模型在不联网的情况下断言行为，把不确定的网络与厂商响应隔离在测试之外。",
                "代价当然存在。多一层抽象意味着你要先理解标准消息和厂商载荷两套词汇，调试时也要判断问题落在墙的哪一侧。但这笔成本通常划算，因为厂商演进的频率远高于你重构业务的意愿。记住一个简单的判断标准：每当你想在业务流程里写下某个厂商的专有字段名时，先问自己这是不是应该收进适配层的细节；多数时候答案是肯定的，把它留在墙内，墙外就能保持干净。",
            ]),
            ("把这套分层迁移到自研模型与网关", [
                "这套分层不只适用于商用厂商，也适用于自研模型和模型网关。当你在公司内部署一个推理服务，或在多个模型前架一层网关做路由与限流时，最好仍让它表现得像一个标准聊天模型：对上暴露统一的消息与生成结果，把路由策略、鉴权、配额这些网关细节藏在适配层后面。这样上层链路无需知道请求最终落到哪台机器、哪个版本，灰度和迁移都只在网关层发生。",
                "反过来，如果让业务直接感知网关的内部协议，你会把网关的每一次演进都变成业务的负担。一个好用的模型网关，应该像电源插座：上层只管按标准接口取电，插座背后是火电还是光伏、是本地还是云端，都不该改变取电的方式。把自研服务也纳入同一套适配纪律，整套系统在更换底座时才会平滑，而不是每换一次模型就牵动一片业务代码。",
            ]),
            ("一次最小排障演练", [
                "把本课的分层用一次最小排障演练串起来：假设线上出现模型回答里突然不再带工具调用。第一步先看输入，确认进入模型前的消息序列是否完整，系统提示是否还在，历史是否被截断；第二步看载荷，确认工具是否真的通过绑定进了请求，而不是被谁从参数里漏掉；第三步看原始响应，判断模型到底有没有发出工具调用；第四步看归一，排除适配层在解析时把工具调用丢了的可能。",
                "这套从输入到归一的顺序，最大的价值是避免把所有问题都甩给提示词。同一个症状在不同层有完全不同的修法：载荷漏了工具要补绑定，响应本就没有工具调用要回到提示和模型选择，归一丢了字段要修适配层或补契约测试。每次排障都按这条链走一遍，你会越来越快地把模糊的模型不听话，定位成某一层上可复现、可修复的具体问题。",
            ]),
            ("课堂检查清单：十二个能定位 provider 边界的问题", [
                "一，当前输入在进入 provider 前是否已经变成 BaseMessage 序列。二，SystemMessage 是否仍在第一轮可见位置。三，ToolMessage 是否保留 tool_call_id。四，工具 schema 是在 bind_tools 阶段注入，还是被业务代码手写到 prompt。五，provider payload 中是否出现了预期模型名、温度、停止词和工具声明。六，响应中原始 token usage 是否映射到 usage_metadata。七，response_metadata 是否保留 request id 或 finish reason。八，stream chunk 是否能合并成与 invoke 语义一致的 AIMessage。九，异常是在 shared skeleton 抛出，还是 provider SDK 抛出。十，回调 start/end/error 是否围绕同一个 run。十一，测试是否断言标准消息，而不是断言 provider 私有 JSON。十二，升级 provider 包时是否只影响适配层而不修改业务链。",
            ]),
        ],
        "tables": [
            {"title": "标准字段与 provider 字段的分工", "intro": "下面这张表帮助你判断该读哪个层次的数据。原则是：业务逻辑读标准字段，排障和统计可读 metadata，只有 provider 专属能力才下钻私有字段。", "headers": ["层次", "典型字段", "适合谁读", "风险"], "rows": [
                ["标准消息", "AIMessage.content、tool_calls、usage_metadata", "Agent、链、测试、业务流程", "最稳定，但不覆盖所有厂商细节"],
                ["响应元数据", "response_metadata、finish_reason、model_name、request id", "日志、成本、排障、观测", "字段可能因 provider 或版本变化"],
                ["原始响应", "choices、content blocks、delta events", "适配器作者、深度排障", "最易变，不应扩散到业务核心"],
            ]},
        ],
        "pitfalls": [
            ("ChatOpenAI 返回什么，业务就直接依赖什么", "业务应依赖 AIMessage、ChatGeneration 和标准 metadata；provider 私有字段只在适配层或排障工具中读取。"),
            ("_convert_input 只是把字符串包一下", "它是所有输入形态进入聊天模型前的语义关口，决定消息顺序、类型和后续 provider 翻译是否可靠。"),
            ("Anthropic 和 OpenAI 差异应由上层 if/else 处理", "差异应尽量留在 partner wrapper；上层只看统一消息、工具调用和生成结果。"),
            ("stream 与 invoke 是两套无关逻辑", "它们返回节奏不同，但最终语义应一致；stream chunk 必须能合并成标准 AIMessage。"),
        ],
        "lab_title": "手工追踪一次 provider 适配",
        "lab_steps": [
            "写一个包含 SystemMessage、HumanMessage 和一个工具声明的最小调用，不需要真实请求也可以用 fake model 描述输入。",
            "画出进入 provider 前的 BaseMessage 列表，标出每条消息的 type、content、id 和 tool_call_id。",
            "为 OpenAI 与 Anthropic 各写一份你认为可能的 payload 轮廓，只写 role/content/tools 等关键字段。",
            "假设 provider 返回一次工具调用，写出 raw response 中可能出现的字段，再把它归一成 AIMessage.tool_calls。",
            "最后写两个断言：一个断言标准消息字段，一个断言 metadata 中保留了排障需要的信息。",
        ],
        "version_note": "本课以 LangChain core/partner 分层和 BaseChatModel 适配模式为锚点；provider API、SDK 字段和工具调用格式会演进，实际排障时请以当前安装版本的文件与符号名为准，不把本文示例 payload 当成永久规范。",
        "points": [
            "BaseChatModel 提供共享调用骨架，provider adapter 只应承担厂商差异翻译。",
            "_convert_input 与 convert_to_messages 把宽松输入收束成 BaseMessage 中间表示。",
            "ChatOpenAI、ChatAnthropic 等 partner wrapper 把标准消息翻译为 provider payload，再把响应归一回 ChatGeneration/AIMessage。",
            "业务逻辑优先读取标准字段；provider 私有字段只用于适配或排障。",
            "定位模型问题时按输入标准化、payload、raw response、响应归一、上层控制流逐段排查。",
        ],
    }
)


LESSON_42_TOOL_INTERNALS = _build_lesson(
    {
        "lead": "工具内部最容易被误解的一点，是“生成 schema”和“执行工具”不是同一件事。<span class='mono'>BaseTool</span> 与 <span class='mono'>args_schema</span> 负责把 Python 函数的输入契约变成可验证对象；<span class='mono'>convert_to_openai_tool</span> 等转换函数负责把这个契约翻译成 provider 可理解的工具说明；模型真正发出 <span class='mono'>tool_calls</span> 后，<span class='mono'>ToolNode</span> 才按名字查找工具、用 Pydantic 校验参数、执行函数并写回 <span class='mono'>ToolMessage</span>。本课把工具的去程 schema、回程执行、错误策略和 provider 兼容边界拆开，帮助你设计可被模型正确调用、可被系统安全执行、可被 trace 审计的工具。",
        "analogy": "把工具系统想成餐厅的点餐与出餐。菜单上的菜名、配料、可选辣度就是 schema，服务员把菜单翻译成顾客能看懂的版本；顾客点菜时填错辣度，前台会先校验，不会让厨房乱做；厨房真正做菜是执行阶段；菜做好后用取餐号送回桌子，这个回执就是 ToolMessage。菜单设计得清楚不代表厨房一定执行成功，厨房执行成功也不代表菜单适合每个平台展示。schema、执行、回执三件事必须分开看。",
        "map_title": "本课地图：工具从 Python 函数到 ToolMessage",
        "map_nodes": [
            ("定义工具", "@tool、StructuredTool 或 BaseTool 声明名称、描述、args_schema", "before"),
            ("生成 schema", "类型注解、docstring、Pydantic 模型生成参数契约", "now"),
            ("Provider 翻译", "convert_to_openai_tool 等把契约变成模型可见工具说明", "source"),
            ("执行工具", "模型返回 tool_calls 后，ToolNode 查找工具、校验 args、调用函数", "now"),
            ("回填观察", "结果或可恢复错误被包装成 ToolMessage，下一轮模型读取", "after"),
        ],
        "source_intro": "下面的文件代表工具链的几个层次：core 的 BaseTool 与 schema 转换是契约层，message 的 ToolMessage 是回执层，LangGraph prebuilt 的 ToolNode 是执行层。读源码时不要把这些层混成一个函数，否则会误判错误发生的位置。",
        "sources": [
            {"file": "libs/core/langchain_core/tools/base.py", "symbol": "BaseTool", "role": "所有工具的基类，定义 name、description、args_schema、invoke/run、错误处理等契约", "direction": "工具对象先作为 Runnable/Tool 暴露给模型和执行节点"},
            {"file": "libs/core/langchain_core/tools/base.py", "symbol": "args_schema", "role": "Pydantic 参数模型或由函数签名推导出的输入 schema", "direction": "用于模型可见 schema 生成，也用于执行前参数校验"},
            {"file": "libs/core/langchain_core/utils/function_calling.py", "symbol": "convert_to_openai_tool", "role": "把 BaseTool、callable、Pydantic 模型或 dict 翻译为 OpenAI 风格工具声明", "direction": "provider payload 去程；不同 provider 可能需要再适配"},
            {"file": "libs/core/langchain_core/messages/tool.py", "symbol": "ToolMessage", "role": "工具执行结果消息，用 tool_call_id 与 AIMessage.tool_calls 配对", "direction": "工具执行回程；下一轮模型读取它作为观察"},
            {"file": "libs/prebuilt/langgraph/prebuilt/tool_node.py", "symbol": "ToolNode", "role": "预置工具执行节点，读取 tool_calls、查找工具、注入状态/上下文、处理结果或错误", "direction": "位于 Agent 的 tools 节点，连接模型请求与工具回执"},
        ],
        "flow_title": "状态流：schema 去程与执行回程",
        "flow_steps": [
            ("Python 工具声明", "开发者写函数、类型注解、docstring，或显式给出 Pydantic args_schema。", "def search_order(order_id: str)"),
            ("schema 生成", "BaseTool 把名称、描述、参数字段、必填项和约束整理成内部 schema。", "args_schema=SearchOrderArgs"),
            ("provider 工具说明", "convert_to_openai_tool 等把内部 schema 翻译成 provider 接受的 JSON schema 轮廓。", "tools=[{type:'function', ...}]"),
            ("模型发起 tool_call", "聊天模型返回 AIMessage.tool_calls，包含 name、args、id；这一步仍只是请求。", "tool_calls=[call_1]"),
            ("ToolNode 执行", "ToolNode 用 name 找工具，用 args_schema 校验参数，调用函数，生成 ToolMessage。", "ToolMessage(tool_call_id='call_1')"),
        ],
        "trace": [
            {"step": "1. authoring", "input": "def refund(order_id: str, reason: str)", "action": "@tool 读取名称、签名、docstring，形成 BaseTool", "output": "工具有 name、description、args_schema"},
            {"step": "2. binding", "input": "BaseTool 列表", "action": "模型适配器调用 schema 转换函数，把工具契约放进 provider payload", "output": "模型看见可调用工具说明"},
            {"step": "3. model request", "input": "用户要求退款 + 工具说明", "action": "模型输出 tool_calls=[{'name':'refund','args':{...},'id':'call_7'}]", "output": "结构化工具请求"},
            {"step": "4. validation", "input": "call_7 args", "action": "ToolNode/BaseTool 用 Pydantic 校验字段、类型、约束", "output": "合法参数或 ValidationError"},
            {"step": "5. observation", "input": "函数返回值或可恢复错误", "action": "包装成 ToolMessage，保留 tool_call_id", "output": "messages 追加工具观察"},
        ],
        "code_path": "libs/core/langchain_core/tools/base.py + libs/prebuilt/langgraph/prebuilt/tool_node.py",
        "code_symbol": "BaseTool.args_schema / ToolNode.invoke",
        "code": """# 教学版：把 schema 生成和工具执行拆开看
class SearchOrderArgs(BaseModel):
    order_id: str

class SearchOrderTool(BaseTool):
    name = "search_order"
    description = "查询订单物流状态"
    args_schema = SearchOrderArgs

# 去程：给模型看的说明，不执行函数
provider_tool = convert_to_openai_tool(SearchOrderTool())

# 回程：模型已经请求调用后，才校验并执行
call = {"name": "search_order", "args": {"order_id": "42"}, "id": "call_1"}
args = SearchOrderArgs.model_validate(call["args"])
result = search_order(**args.model_dump())
message = ToolMessage(content=str(result), tool_call_id="call_1")
""",
        "code_note": "真实 ToolNode 还会处理多个工具调用、并发、状态注入、store 注入、同步/异步、错误策略和返回格式。伪码强调两个边界：schema 转换只是让模型知道工具怎么叫，执行阶段才真正校验参数并产生 ToolMessage。",
        "sections": [
            ("schema 生成不是工具执行", [
                "工具 schema 的去程任务，是把 Python 世界的函数签名、类型注解、Pydantic 字段、docstring 和描述翻译成模型可读说明。它回答的是“模型应该如何构造调用请求”：工具叫什么、适合什么时候用、参数有哪些、每个参数是什么类型、哪些字段必填。这个阶段不应该访问数据库、发请求或产生副作用。若 schema 生成阶段就执行业务逻辑，工具列表绑定一次就可能修改外部状态，这是严重边界错误。",
                "执行阶段则发生在模型已经返回 tool_calls 之后。ToolNode 或调用者读取 name 和 args，找到对应 BaseTool，用 args_schema 做 Pydantic 校验，再执行函数。校验失败、工具抛错、返回值不可序列化、需要人审等问题都属于执行回程。把去程和回程分开，你才能清楚地测试：一个测试验证 schema 是否描述正确，另一个测试验证工具收到合法参数时是否产生正确 ToolMessage。",
            ]),
            ("Pydantic 校验是安全阀，不是文档装饰", [
                "类型注解和 Pydantic 字段常被当作文档，但在工具系统里它们直接参与运行。模型生成的参数是 JSON 风格对象，可能缺字段、类型错、枚举值越界、把自然语言塞进数字字段、把用户可控文本塞进本应由系统注入的 tenant_id。args_schema 的校验能在函数执行前拦住这些错误，避免数据库查询、支付、发邮件等副作用拿到脏参数。",
                "校验错误的处理要按风险分类。搜索无结果、订单号格式错、日期缺失这类可恢复问题，可以转成 ToolMessage 告诉模型“参数不合法，请改用 YYYY-MM-DD”。权限不足、越权 tenant、退款接口失败、内部异常等问题则不应简单回填给模型继续尝试，应该抛给应用层、触发人审或返回安全降级。工具错误不是越温柔越好，而是越符合风险边界越好。",
            ]),
            ("provider schema 兼容性要谨慎", [
                "convert_to_openai_tool 的名字容易让人以为 OpenAI 风格就是所有 provider 的永久标准。更稳妥的理解是：它把 LangChain 工具契约转换为一种常见的 function/tool schema 形态，具体 provider wrapper 仍可能需要根据当前 API 能力、字段限制、strict 支持、JSON schema 子集和工具调用格式做二次处理。不要把某个 provider 接受的全部 JSON schema 特性默认为所有模型都支持。",
                "实际设计工具时，越接近通用 JSON schema 子集越稳：字段名清晰、类型简单、描述明确、嵌套适度、避免复杂联合类型和隐式约束。复杂业务规则应放在执行前校验或工具内部显式报错，而不是全部压进模型不一定遵守的 schema。schema 是给模型的说明书，不是形式化证明；真正的防线仍在 Pydantic、权限检查和业务服务。",
            ]),
            ("ToolMessage 是因果链主键", [
                "ToolMessage 的核心字段不是 content，而是 tool_call_id。一次 AIMessage 可能包含多个 tool_calls，执行顺序可能并行，结果返回顺序也可能不同。如果只按列表位置匹配，任何并发、重试或部分失败都会让模型下一轮读到错配观察。tool_call_id 把“模型请求了什么”和“工具返回了什么”连成因果链，trace、日志、测试和 UI 都应保留它。",
                "ToolMessage 的 content 也要为模型服务。后端返回的内部对象、状态码、缩写字段不一定适合模型继续推理。好的工具观察应明确：事实是什么、是否成功、缺什么信息、是否可重试、下一步限制是什么。对于敏感信息，content 要脱敏；对于大对象，要摘要并保留引用 id；对于不可恢复错误，不要把内部栈追踪回填给模型。",
            ]),
            ("工具设计要区分模型参数与系统参数", [
                "模型适合填写用户问题中出现的业务参数，例如城市、日期、订单号、搜索关键词。模型不适合填写权限边界、tenant_id、用户 id、内部服务 token、审批人、幂等键等系统参数。这些值应通过 Runtime Context、ToolNode 注入或业务服务端补齐，而不是暴露在 provider schema 中让模型猜。把安全参数交给模型，会让提示注入和越权风险大幅增加。",
                "同一个工具也要区分只读和副作用。查天气、查订单、搜索文档一般可以自动执行；退款、发邮件、删除数据、下单等副作用工具需要幂等、权限、人审、限流和审计。ToolNode 能执行工具，但它不知道你的业务风险。工具 schema 应把动作说清楚，执行层应把危险动作关进可验证流程。",
            ]),
            ("边界情况：schema 与执行之间的裂缝", [
                "去程 schema 和回程执行之间，藏着很多容易漏的缝。模型可能忽略 enum 约束、给可选字段塞默认值、把嵌套对象填得松散，甚至虚构 schema 里没有的字段；它也可能返回一个 name 对不上任何已注册工具的 tool_call，或在一条 AIMessage 里同时发起多个工具调用。ToolNode 必须把这些都当正常输入处理：未知工具不能让整轮崩溃，校验失败要变成可读反馈，多调用要逐个执行并各自回填，而不是只处理第一个。",
                "系统参数泄漏是另一类裂缝。tenant_id、user_id、内部 token、审批人、幂等键这类值不该出现在模型可见 schema 里。LangChain/LangGraph 用 InjectedState、InjectedToolArg、InjectedStore 等标注，把这些参数从模型视角隐藏、由运行时注入。如果忘了标注，它们会跟着 args_schema 一起暴露给 provider，模型就可能尝试自己填，带来越权和提示注入风险。此外，同步与异步、并发执行也要区分：无副作用工具可以并行，付款、发邮件这类副作用工具需要幂等和限流，不能图快就并发。",
            ]),
            ("常见误解：description 不重要、try/except 就安全", [
                "工具的 description 和参数描述常被当成可有可无的注释，其实它们直接影响模型是否选这个工具、何时选、参数怎么填。描述含糊会导致模型选错工具或填错字段；多个工具名称或职责相近，会让模型在它们之间摇摆。把“何时该用、何时不该用、每个参数代表什么”写清楚，往往比反复调 prompt 更能稳定工具调用质量。schema 是给模型的说明书，措辞本身就是接口的一部分。",
                "另一个误解是“包一层 try/except 就安全了”。一个吞掉所有异常、再把栈追踪原样回填给模型的工具，既泄漏内部细节，又会诱导模型对不可恢复的操作反复重试。是否把异常转成 ToolMessage，应由风险类别决定：ToolNode 的 handle_tool_errors 控制这一行为，可恢复问题适合回填让模型改正，权限不足、内部 bug、危险副作用失败则应抛给应用层或触发人审。副作用工具还要靠幂等键防止重试造成真实损失，而不是指望模型自觉。",
            ]),
            ("结构化输出、并行调用与回填顺序", [
                "工具有时被用来“塑形输出”，有时被用来“产生副作用”，二者要分清。如果只是想让模型返回结构化对象，with_structured_output 这类结构化响应通常比临时造一个假工具更直接；只有当确实要执行查询、写库、发请求时，才需要一个真正会被执行的工具。把结构化输出和副作用工具混用，会让一次“只想要 JSON”的调用意外触发执行路径，或让本该落库的动作退化成纯文本。",
                "并行与回填顺序是工程化工具的硬骨头。一条 AIMessage 可能带多个 tool_calls，执行可能并行，返回顺序也可能与请求顺序不同；只有用 tool_call_id 把每个 ToolMessage 配回对应请求，模型下一轮才不会读到错配观察。部分失败时要明确：成功的工具照常回填，失败的工具回填可读的失败说明，而不是让整组调用一起报错。流式场景下工具参数还会分片到达，合并不完整就可能执行到残缺参数，这也要靠执行前的 Pydantic 校验兜底。",
            ]),
            ("设计取舍：把昂贵的校验放在执行之前", [
                "工具系统的一个核心取舍，是把校验放在执行之前而不是之后。模型生成的参数本质上是不可信输入：它可能漏字段、类型错、把自然语言塞进数字位、或越过取值范围。如果先执行再发现参数有问题，副作用可能已经发生；先校验再执行，则能在触碰数据库、支付或外部接口之前把脏参数挡在门外。这条边界看似简单，却是工具安全里最便宜也最有效的一道防线。",
                "第二个取舍是反馈给谁。同一个错误，回填给模型还是抛给应用，效果天差地别。日期格式不对、缺少可补的字段，适合转成一句清楚的提示让模型在下一轮自我修正；权限不足、内部异常、危险动作失败，则不该让模型反复试探，而要交给应用层的策略、人工审核或安全降级。把错误按能不能靠对话恢复来分类，是设计工具回程时最该先想清楚的事，也是判断该不该回填的根据。",
                "第三个取舍是谁来填参数。模型擅长填用户问题里出现的业务参数，例如城市、日期、订单号；不擅长也不应该填权限边界、租户标识、内部令牌这类系统参数。把系统参数交给运行时注入、让模型只看见它该看见的字段，既减少出错，也压缩了提示注入的攻击面。工具的优雅，很大程度上来自这条模型参数与系统参数分离的纪律，它让一个工具既好用又难被滥用。",
            ]),
            ("把工具目录当成可治理的资产", [
                "当工具从一两个增长到几十个，工具目录本身就成了需要治理的资产。每个工具的名称是否唯一、描述是否准确、参数是否清晰、权限是否标注、是否有副作用，都会影响模型选择的准确率和系统的安全面。一个杂乱的工具目录，会让模型频繁选错工具、把参数填到错误的字段，也让排障时难以判断问题出在哪一个工具。把工具目录当资产管理，意味着它需要命名规范、评审和定期清理。",
                "治理还包括按场景裁剪可见工具。不是每一轮对话都该让模型看到全部工具：与当前任务无关的工具越多，模型越容易分心或误用。按角色、按步骤、按权限动态地决定这一轮绑定哪些工具，既能提升调用准确率，也能收窄攻击面。工具不是越多越强，而是越合适越稳；目录的克制，往往比工具的数量更能决定智能体的可靠程度。",
            ]),
            ("课堂检查清单：工具链的十二个问题", [
                "一，工具名称是否稳定且不会与其他工具混淆。二，description 是否说明何时该用、何时不该用。三，args_schema 是否覆盖必填字段、类型和约束。四，模型可填参数与系统注入参数是否分离。五，schema 是否避免 provider 不一定支持的复杂结构。六，绑定工具时是否只生成说明而不执行副作用。七，ToolNode 执行前是否经过 Pydantic 校验。八，工具错误是否按可恢复、权限、内部异常、副作用失败分类。九，ToolMessage 是否保留 tool_call_id。十，工具返回内容是否对模型可读且已脱敏。十一，多工具并发是否只用于无副作用或互不依赖工具。十二，测试是否分别覆盖 schema、校验、执行、错误和 ToolMessage 配对。",
            ]),
        ],
        "tables": [
            {"title": "工具错误策略速查", "intro": "不同错误不应都塞回 ToolMessage，也不应都抛异常。下面的表是设计时的风险分层。", "headers": ["错误类型", "例子", "推荐处理", "原因"], "rows": [
                ["参数校验", "日期格式错、缺少 order_id", "可回填 ToolMessage，提示模型修正", "模型有机会在下一轮补齐或改正"],
                ["业务空结果", "订单不存在、搜索无命中", "回填脱敏观察", "这是用户可理解事实，不是系统故障"],
                ["权限问题", "tenant 不匹配、越权退款", "抛给应用层或安全降级", "不应让模型通过重试探索权限边界"],
                ["内部异常", "数据库超时、代码 bug", "记录日志、有限重试、降级", "内部细节不应暴露给模型或用户"],
                ["危险副作用", "付款、删除、发邮件失败", "幂等检查 + 人审或明确失败", "重复执行可能造成真实损失"],
            ]},
        ],
        "pitfalls": [
            ("schema 写得出来，工具就安全", "schema 只帮助模型构造请求；执行前仍要 Pydantic 校验、权限检查、幂等和审计。"),
            ("convert_to_openai_tool 等于所有 provider 的规范", "它是常用翻译形态；不同 provider 的工具协议和 JSON schema 子集可能不同，应以适配器和版本为准。"),
            ("ToolMessage 内容越完整越好", "工具观察要对模型有用且脱敏；内部栈、密钥、超大 JSON 和权限细节不应直接回填。"),
            ("工具错误都应该让模型自己修", "只有可对话恢复的问题适合回填；权限、内部 bug、危险副作用失败应交给应用层策略。"),
        ],
        "lab_title": "为一个退款工具做 schema/执行双测试",
        "lab_steps": [
            "定义 refund_order(order_id: str, reason: str) 的 args_schema，并写出模型可见 description。",
            "把工具转换成 provider schema，检查字段名、必填项和描述是否足够让模型正确填写。",
            "构造一个缺少 reason 的 tool_call，确认 Pydantic 校验失败且不会执行退款函数。",
            "构造一个合法 tool_call，确认返回 ToolMessage 且 tool_call_id 与请求一致。",
            "为权限不足场景写策略：不要把内部权限规则回填给模型，而是返回安全失败或触发人审。",
        ],
        "version_note": "工具调用协议、provider JSON schema 支持范围和 LangGraph ToolNode 的注入/错误选项会随版本演进；本文强调稳定分层：schema 生成、provider 翻译、Pydantic 校验、工具执行、ToolMessage 回填。具体参数名请以当前源码和文档为准。",
        "points": [
            "工具链分去程和回程：schema 让模型知道怎么请求，ToolNode 才真正执行。",
            "BaseTool.args_schema 既生成模型可见契约，也保护执行前参数校验。",
            "convert_to_openai_tool 是 provider schema 翻译入口之一，不代表所有 provider 永远完全一致。",
            "ToolMessage 必须用 tool_call_id 与 AIMessage.tool_calls 配对。",
            "工具错误要按风险分类处理，可恢复问题可回填，权限和危险副作用应由应用层守住。",
        ],
    }
)


LESSON_43_ECOSYSTEM_COMPARE = _build_lesson(
    {
        "lead": "横向比较生态时，最危险的写法是给框架贴永久标签：谁“已经过时”、谁“一定更强”、谁“只适合某场景”。这些说法很快会被版本、团队和社区演进打脸。本课采用更稳的比较维度：LangChain/LangGraph 更偏统一组件契约、图状态和可观测运行；AutoGen 风格强调多 actor 对话与消息路由；CrewAI 风格强调角色、任务和团队协作描述；LlamaIndex 风格常从数据连接、索引和 RAG 工作流进入；其他系统可能以 pub/sub、workflow、handoff 或服务网格为中心。比较的目标不是选冠军，而是识别“默认心智模型”与“让什么事情更顺手”。",
        "analogy": "把几个生态想成不同类型的工作场所。LangGraph 像白板上画好的流程车间：每个工位读写共享状态，边决定下一站，质检记录每一步。AutoGen 风格像圆桌会议：多个角色发言、回应、转交，重点是参与者之间的消息。CrewAI 风格像项目经理给团队分角色和任务：研究员、写作者、审阅者按职责协作。LlamaIndex 风格像资料馆：先把资料接入、索引、检索，再组织问答。它们都能做复杂应用，但默认入口不同，入口决定你写代码时最自然的表达方式。",
        "map_title": "本课地图：用默认心智模型比较生态",
        "map_nodes": [
            ("LangChain/LangGraph", "Runnable、工具、消息、StateGraph、Pregel、checkpoint 形成可组合应用栈", "source"),
            ("Actor/对话", "AutoGen 风格常把多个可对话 agent 作为一等对象，关注消息路由与协作", "now"),
            ("角色/任务", "CrewAI 风格常用 crew、role、task、process 描述团队分工", "now"),
            ("数据/RAG", "LlamaIndex 风格常以数据连接、索引、查询引擎和检索工作流切入", "now"),
            ("选型", "按状态可控性、数据重心、团队协作、观测和集成边界决定", "after"),
        ],
        "source_intro": "生态比较的 source map 不追求覆盖每个仓库细节，而是给出本课程已验证的 LangChain/LangGraph 锚点，并用公开概念名描述其他生态的常见心智模型。由于外部框架 API 和维护状态会变化，本文避免对当前热度、活跃度或兼容性做硬断言。",
        "sources": [
            {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable", "role": "LangChain 统一可运行协议，支撑模型、链、工具、检索器和图组合", "direction": "体现 LangChain 的组件契约重心"},
            {"file": "libs/langgraph/langgraph/graph/state.py", "symbol": "StateGraph", "role": "LangGraph 状态图构建器，节点读写共享 state，边定义控制流", "direction": "体现图/状态/边的显式编排重心"},
            {"file": "libs/langgraph/langgraph/pregel/main.py", "symbol": "Pregel", "role": "LangGraph 执行引擎，按超步调度 actors/channels/writes", "direction": "体现可追踪运行时与 checkpoint 能力"},
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "LangChain 高层 Agent 入口，常把模型、工具和 middleware 组装到 LangGraph 循环", "direction": "体现高层易用 API 与底层图运行时的连接"},
            {"file": "外部生态公开概念", "symbol": "AutoGen/CrewAI/LlamaIndex", "role": "分别常以多 agent 对话、角色任务 crew、数据索引/RAG 等概念作为入口", "direction": "用于对照心智模型，不在本课做版本状态判断"},
        ],
        "flow_title": "调用图：同一个研究任务在不同心智模型中的表达",
        "flow_kind": "call_graph",
        "flow_steps": [
            ("问题", "用户要求调研一个技术并生成报告", False),
            ("图/状态", "LangGraph 表达为 research -> draft -> review -> END 的状态图", True),
            ("Actor 对话", "AutoGen 风格表达为 researcher 与 writer 互发消息并由 manager 路由", True),
            ("角色任务", "CrewAI 风格表达为角色、目标、任务和执行过程", True),
            ("数据索引", "LlamaIndex 风格先接入资料、建索引、查询，再交给生成步骤", True),
            ("选型", "根据可控性、数据复杂度、协作形态和团队经验选择", False),
        ],
        "trace": [
            {"step": "1. requirement", "input": "需要对公司知识库做调研并输出可审阅报告", "action": "识别核心难点：数据检索、步骤控制、多角色协作、审计", "output": "选型维度而非框架名单"},
            {"step": "2. LangGraph view", "input": "明确状态字段 documents/draft/review", "action": "节点读写 state，条件边决定是否返工", "output": "强可控 trace 与可 checkpoint 工作流"},
            {"step": "3. actor view", "input": "多个 agent 需要自由讨论", "action": "定义参与者、消息路由、终止规则", "output": "更像会话型协作"},
            {"step": "4. data view", "input": "资料来源多、索引和召回复杂", "action": "优先设计 connector、index、query engine、rerank", "output": "RAG 质量成为主线"},
            {"step": "5. decision", "input": "团队已有栈、观测要求、部署边界", "action": "选择默认最顺手的生态，必要时组合使用", "output": "场景化而非宗教化结论"},
        ],
        "code_path": "生态对照伪码",
        "code_symbol": "graph/state vs actor/message vs data/index",
        "code": """# 同一任务的三种表达，不代表实际 API 完全如此
# 图/状态：显式节点和边
graph.add_node("retrieve", retrieve_docs)
graph.add_node("draft", write_report)
graph.add_node("review", review_report)
graph.add_conditional_edges("review", route_pass_or_rework)

# Actor/对话：参与者之间交换消息
manager.send(researcher, "find evidence")
researcher.reply(writer, evidence)
writer.reply(reviewer, draft)

# 数据/RAG：先组织资料，再回答
index = build_index(load_documents())
ctx = index.query(question)
answer = synthesize(question, ctx)
""",
        "code_note": "伪码只展示心智模型差异，不声称任何外部框架的当前 API 必然如此。真正选型要读当前版本文档、示例、限制、许可证、部署形态和社区实践。",
        "sections": [
            ("比较框架先比较默认抽象", [
                "一个成熟生态通常什么都能做：图框架能做多 Agent，对话框架能做工具调用，RAG 框架能做 workflow，角色框架也能接向量库。如果只问“能不能”，答案往往都是能；真正有意义的是“默认写法让什么变容易”。默认抽象会决定你第一行代码写什么、日志长什么样、错误在哪里暴露、团队如何讨论设计。",
                "LangChain/LangGraph 的默认抽象更接近可组合组件与显式运行时：Runnable 定义组件接口，BaseMessage 统一消息，BaseTool 统一工具，StateGraph 定义状态和边，Pregel 负责执行。它适合把复杂应用拆成可观测步骤，并对状态、重试、checkpoint、人审和工具循环保持控制。代价是你要理解图、state、reducer 和运行配置。",
            ]),
            ("Actor/pubsub 与图状态的差异", [
                "Actor 或 pub/sub 风格更自然地表达“多个自治参与者在通信”。每个 agent 像一个有角色、记忆和工具的 actor，消息在参与者之间传递，管理者或路由规则决定下一位说话者。这种模型适合原型化多角色协作、模拟会议、让不同专家互相质询。它的优势是贴近人类协作直觉，弱点是如果没有严密终止条件、状态摘要和审计结构，对话可能变长、重复或难以回放。",
                "图状态风格则先问：共享 state 有哪些字段，哪些节点能写，哪条边决定下一步，什么时候结束。它不要求每个节点像独立人格，更强调可控流程。多 Agent 在图里可以表现为多个节点或子图，也可以通过 handoff 改变控制权。优势是 trace 和测试清晰，弱点是开放式讨论需要显式建模，否则会显得比对话框架啰嗦。",
            ]),
            ("数据/RAG 重心与编排重心", [
                "LlamaIndex 风格常从数据进入：文档如何接入、如何切分、如何建索引、如何组织查询引擎、如何融合多个数据源、如何评估检索质量。对于知识库问答、文档搜索、结构化资料查询和 RAG 质量优化，数据抽象是第一优先级。编排当然也重要，但如果主要难点是资料来源、索引策略、召回和引用，先选数据/RAG 友好的生态可能更省力。",
                "LangChain 也有 Document、Retriever、VectorStore、RAG 链和工具化检索；差异不在“有没有”，而在默认入口。你可以用 LangChain/LangGraph 编排一个调用 LlamaIndex 查询引擎的节点，也可以在 LlamaIndex 工作流里调用 LangChain 工具。成熟工程经常组合生态，而不是强行让一个框架负责所有层。组合时要明确边界：谁拥有数据索引，谁拥有控制流，谁负责观测和部署。",
            ]),
            ("角色 crew 与 handoff/orchestration", [
                "CrewAI 风格常把角色、目标、背景、任务、过程作为核心语言。它适合教学、原型和团队协作式任务描述：研究员找资料，分析师整理，写作者成稿，审阅者检查。这样的表达降低了多角色任务的上手门槛，也能帮助非工程同学理解系统。但生产化时仍要落到可验证问题：任务如何终止，工具如何授权，输出如何校验，失败如何重试，成本如何观测。",
                "handoff 是很多多 Agent 系统都会遇到的概念：当前 agent 判断自己不适合继续，把任务交给另一个 agent 或子流程。LangGraph 里 handoff 可以表现为 Command、goto、子图或路由边；对话框架里可能表现为 manager 改变发言者；角色框架里可能表现为任务流转。比较 handoff 时不要只看 API 名称，要看它是否保留状态、是否可审计、是否支持人审、是否能防止循环交接。",
            ]),
            ("选型矩阵比排名更可靠", [
                "一个简单矩阵通常比“谁更好”更有用。若你的系统需要严格状态、可回放、checkpoint、人审和测试，图/状态框架权重高。若你的系统需要快速模拟多个专家讨论，actor/对话框架权重高。若资料接入、索引、召回、rerank 是主战场，数据/RAG 框架权重高。若你的团队用角色和任务沟通效率最高，crew 风格可能更顺手。",
                "还要考虑非技术维度：团队已有代码、部署环境、许可证、文档质量、调试工具、社区示例、与现有评测/观测平台的集成。本文避免写当前活跃度或维护状态判断，是因为这些信息变化快，且需要按具体版本核验。工程决策应该把“今天查到的版本证据”写进 ADR 或设计文档，而不是引用泛泛印象。",
            ]),
            ("边界情况：把生态比较写成可复查证据", [
                "生态比较最容易出问题的地方，不是结论本身，而是结论的“保质期”。“某框架已经过时”“某框架一定最好”这类话，往往在你写下它的当天就开始贬值。更稳的做法是把比较当成一次带证据的快照：记录你查证的日期、对照的版本、许可证、部署目标，以及你真正核验过的维护信号（提交活跃度、release 节奏、文档完善度），并把它写进设计决策记录（ADR）。下次复查时，先看快照是否过期，再决定是否更新结论。",
                "另一个边界是“用人气替代匹配度”。star 数、热度榜、社交媒体声量都不是架构依据；真正决定的是它与你主要难点的契合度，加上团队熟悉度和运维成本。一个在演示里很惊艳的框架，可能在你需要严格状态、审计和回放时并不顺手。把“今天看起来很火”与“适合我这个系统”分开，是避免选型后悔的关键。",
            ]),
            ("常见误解：把范式差异当成能力差异", [
                "几乎每个成熟生态都能做工具调用、RAG 和多 Agent，所以“能不能做某件事”几乎不区分框架。真正区分它们的是默认范式：默认抽象让什么变容易、日志和 trace 长什么样、错误在哪里暴露、团队用什么词讨论设计。按功能清单逐项打勾很容易得出“都能做”的平庸结论；按默认范式比较，才能看出哪种写法让你的主要难点最省力。把范式差异误读成能力差异，往往会高估迁移成本或低估隐性复杂度。",
                "组合使用是常态，不是失败。用 LangGraph 编排控制流、在某个节点里调用 LlamaIndex 的查询引擎，或把一个外部 actor 框架包成图节点，都是成熟工程里常见的搭配。真正的陷阱不是“混用框架”，而是“两份状态真相”：同一份对话历史或任务状态被两个框架各自维护，最终对不齐。只要明确谁持有权威状态、谁只是被调用方，混用就既灵活又可控。",
            ]),
            ("组合多个生态时的所有权边界", [
                "组合生态前，先回答三个所有权问题：谁拥有控制流（哪一层决定下一步执行什么），谁拥有数据与索引（哪一层负责文档、向量和检索质量），谁拥有可观测（哪一层串起 trace、成本和错误）。把这三件事分派清楚，组合就有了边界；含糊不清时，往往会出现重复的状态、互相覆盖的重试、以及没人负责的失败。一般建议让一个框架做控制流主干，其它能力以适配器或服务的形式被它调用。",
                "组合系统还需要一条统一的 trace 主线。外部框架的运行 id 要能映射回你的 run id，否则一次跨框架调用会在观测里断成两截，排障时无法对齐。失败归属也要事先约定：外部查询引擎超时算谁的失败、外部 agent 返回低质量结果由谁兜底、降级路径在哪一层触发。把所有权和 trace 想清楚，多生态组合才是加法而不是负担。",
            ]),
            ("一个具体任务的四种落地草图", [
                "设想一个客服工单自动分流并回复的任务。用图与状态的思路，你会先定义状态里有哪些字段：工单内容、分类结果、检索到的知识、草稿回复、是否需要人工。然后把流程拆成分类、检索、起草、审核几个节点，用边决定何时回到起草、何时转人工、何时结束。它的自然之处在于每一步都看得见、可回放、可加检查点；吃力之处在于，如果需求只是随便聊聊，这套显式状态会显得啰嗦。",
                "用多角色对话的思路，你会把分类员、知识专家、写作员设成几个会说话的角色，让它们就一张工单互相提问和补充，由一个协调者决定谁接着发言。这种表达贴近人类客服小组的直觉，适合快速搭出多角色协作的原型；但要让它在生产里收敛，你得额外设计终止条件、状态摘要和审计，否则对话可能越扯越长。角色式团队的写法介于两者之间：先声明角色、目标和任务，再按流程推进，上手快，但同样要把安全和错误恢复补上。",
                "如果这张工单的难点主要在从海量历史工单和文档里找到正确依据，那么数据与检索就是主线：先把资料接入、切分、建索引、设计查询和重排，再谈如何生成回复。这时以数据为入口的思路最省力，编排反而是配角。把四种草图摊开比较，你会发现它们都能做这件事，区别只在默认让什么变容易。真正的选型动作，是挑出你这张工单最痛的那一维，让默认范式与它对齐，而不是先认定某个框架再硬套场景。",
            ]),
            ("把比较结论交给时间检验", [
                "任何生态比较都该带一个复查触发条件，而不是写完就封存。比较的结论依赖当时的版本、团队和需求，这些都会变；与其追求一个永久正确的排名，不如约定什么时候回来重看：当某个框架发布重大版本、当团队主要难点改变、当现有方案在成本或可控性上触顶时，就重新跑一遍同样的比较维度。把结论当成会过期的假设，你才不会被一次旧判断长期绑架。",
                "这也意味着比较的过程比结论更值钱。一份写清了维度、证据和版本的比较记录，即使结论过期，也能在下次快速复用；而一句没有依据的谁更好，即使当时正确，也无法被检验或更新。教学和工程在这里是一致的：留下可复查的推理链，比留下一个漂亮但孤立的结论更有长期价值。",
            ]),
            ("课堂检查清单：生态比较的十二个维度", [
                "一，默认抽象是图、actor、crew、data 还是 workflow。二，状态是显式字段、对话历史还是隐藏在 agent 内。三，工具调用是否有统一 schema 和错误策略。四，RAG 数据层是否是一等能力。五，多 Agent 交接是否保留可审计状态。六，终止条件是结构化字段还是自然语言协商。七，观测能否看到每个节点、消息、工具和成本。八，测试是否能断言中间步骤。九，部署是否支持你的运行环境。十，框架是否允许与现有组件组合。十一，团队是否理解该心智模型。十二，版本和 API 证据是否已经记录。",
            ]),
        ],
        "tables": [
            {"title": "生态心智模型对照表", "intro": "这张表只描述常见默认重心，不评价项目当前活跃度，也不排除某个框架支持其他能力。", "headers": ["风格", "默认入口", "顺手场景", "需要额外警惕"], "rows": [
                ["LangChain/LangGraph", "Runnable、消息、工具、StateGraph、Pregel", "可控 Agent、工作流、工具/RAG 组合、checkpoint", "需要理解 state/reducer/graph 语义"],
                ["AutoGen 风格", "多个可对话 agent、消息路由、manager", "多专家讨论、对话式协作、快速多 Agent 原型", "长对话终止、状态审计和回放要设计清楚"],
                ["CrewAI 风格", "role、goal、task、crew、process", "角色分工清晰的团队任务与演示", "生产安全、工具权限和错误恢复不能只靠角色描述"],
                ["LlamaIndex 风格", "connector、document、index、query engine", "知识库、RAG、数据接入和检索质量优化", "复杂控制流可能需要额外 workflow/graph 设计"],
                ["通用 workflow/pubsub", "事件、队列、任务、服务边界", "已有微服务或异步系统中嵌入 AI", "模型消息和工具 schema 需要自己规范"],
            ]},
        ],
        "pitfalls": [
            ("某框架能做 X，所以它就是 X 场景最佳", "能做不等于默认顺手；比较要看默认抽象、观测、测试和团队理解成本。"),
            ("生态比较必须给出赢家", "成熟选型是场景匹配，不是排名。不同层可以组合使用。"),
            ("用当前热度判断长期架构", "热度和维护状态会变化，应记录具体版本证据，避免不可复查断言。"),
            ("多 Agent 越自治越智能", "自治增加表达力，也增加终止、权限、成本和审计风险。"),
        ],
        "lab_title": "为一个项目做生态选型矩阵",
        "lab_steps": [
            "选一个真实任务，例如客服工单、资料调研、投研报告或内部知识库问答。",
            "写出最重要的三个难点：状态控制、多角色协作、数据/RAG、工具安全、观测或部署。",
            "把 LangGraph、actor 对话、crew 角色、data/RAG 四种风格按 1-5 分打分，并写理由。",
            "说明是否需要组合生态：例如 LangGraph 负责控制流，LlamaIndex 负责索引查询。",
            "记录本次判断依赖的版本和文档入口，避免未来把临时结论当永久事实。",
        ],
        "version_note": "AutoGen、CrewAI、LlamaIndex、LangChain/LangGraph 等生态的 API、维护节奏和能力边界都会变化。本课只比较常见心智模型和架构取舍，不对当前活跃度、性能或未来路线做硬断言；正式选型请核验当时版本。",
        "points": [
            "比较生态要看默认心智模型，而不是只看功能清单。",
            "LangChain/LangGraph 的强项在统一契约、显式状态图、工具/RAG 集成和可观测运行。",
            "Actor、crew、data/RAG 风格各有自然表达场景，也各有终止、状态和安全成本。",
            "多生态可以组合，但要明确谁拥有数据、谁拥有控制流、谁负责观测。",
            "避免不可验证的当前状态断言；选型文档应记录具体版本证据。",
        ],
    }
)


LESSON_44_AI_STACK_PROTOCOLS = _build_lesson(
    {
        "lead": "AI 应用不是只有框架一层。一次用户请求可能经过应用 UI、编排框架、工具协议、agent 协作协议、模型 API、推理服务、向量数据库、存储、观测和安全网关。MCP 与 A2A 这类协议的价值，正是在框架 API 与外部系统之间划出边界：MCP 更常被理解为 agent/客户端发现并调用工具、资源、提示等能力的协议；A2A 更常被描述为 agent 与 agent 之间发现、委托、交换任务状态和结果的协作协议；LangChain/LangGraph 这类 framework API 则是在应用进程里组织模型、工具、状态和运行时。本课给出 AI stack 坐标系，比较工具协议、agent-to-agent 协议与框架 API 的边界，并用谨慎版本说明提醒你：协议规范会演进，工程设计要留适配层。",
        "analogy": "把 AI stack 想成一座城市。LangChain/LangGraph 像你公司的调度中心，决定哪个部门先处理、状态表怎么更新、谁审批。MCP 像城市标准插座和服务目录，让调度中心能用统一方式接打印店、档案馆、日历和数据库。A2A 像公司与外包团队之间的任务协作合同，说明如何派单、确认身份、汇报进度和交付结果。模型 API 像电力公司，推理引擎像发电站，向量库像档案馆。不同层可以互相连接，但不能混淆职责。",
        "map_title": "本课地图：AI stack 与协议边界",
        "map_nodes": [
            ("应用/产品", "UI、权限、业务流程、用户体验和最终责任", "before"),
            ("框架 API", "LangChain/LangGraph 组织模型、工具、状态、回调和 Agent 循环", "now"),
            ("工具协议", "MCP 等协议把工具、资源、提示暴露给 agent/客户端发现和调用", "source"),
            ("Agent 协议", "A2A 等协议关注 agent 间任务委托、状态交换和结果交付", "source"),
            ("模型/数据底座", "模型 API、推理引擎、向量数据库、存储、观测和安全横切", "after"),
        ],
        "source_intro": "source map 采用“课程内可核验锚点 + 协议概念边界”的写法。LangChain/LangGraph 的符号可在源码中定位；MCP/A2A 的具体字段会随规范演进，本课只把它们放在工具协议和 agent-to-agent 协议层，不硬编码可能过期的细节。",
        "sources": [
            {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "框架 API：把模型、工具、middleware、response_format 组装成 Agent 运行图", "direction": "应用进程内编排，不等同于跨进程协议"},
            {"file": "libs/langgraph/langgraph/graph/state.py", "symbol": "StateGraph", "role": "框架 API：定义状态、节点、边和编译图", "direction": "用于内部控制流和状态管理"},
            {"file": "libs/core/langchain_core/tools/base.py", "symbol": "BaseTool", "role": "框架工具契约：Python 工具对象、args_schema、执行结果", "direction": "可由框架本地执行，也可桥接到外部工具协议"},
            {"file": "协议层概念", "symbol": "MCP", "role": "工具/上下文协议：常用于把工具、资源、提示等能力标准化暴露给 AI 客户端", "direction": "跨进程/跨产品边界，规格会演进"},
            {"file": "协议层概念", "symbol": "A2A", "role": "agent-to-agent 协作协议：常用于 agent 发现、任务委托、状态同步和结果交付", "direction": "连接多个 agent 系统，而不是替代框架内部 API"},
            {"file": "libs/core/langchain_core/retrievers.py", "symbol": "BaseRetriever", "role": "数据/RAG 框架契约：query -> documents，可桥接向量库、搜索和外部数据服务", "direction": "位于应用编排与数据底座之间"},
        ],
        "flow_title": "状态流：一次跨层 AI 请求",
        "flow_steps": [
            ("产品请求", "用户在业务系统里提出问题，应用层负责认证、租户、审计和展示。", "user/session/tenant"),
            ("框架编排", "create_agent 或 StateGraph 决定先检索、再调用模型、是否需要工具或人审。", "state={messages, docs}"),
            ("工具协议边界", "若工具在外部 MCP server，框架通过适配器发现工具 schema 并发起调用。", "MCP tool call"),
            ("Agent 协议边界", "若任务要交给另一个 agent 系统，A2A 风格协议负责委托、状态和结果。", "task delegation"),
            ("模型/数据底座", "模型 API、推理服务、向量库、对象存储和观测系统完成底层能力。", "answer + trace"),
        ],
        "trace": [
            {"step": "1. app", "input": "用户问：生成上月销售异常分析", "action": "应用验证身份、确定租户和数据权限", "output": "带 context 的请求"},
            {"step": "2. framework", "input": "messages + context", "action": "LangGraph 节点先检索报表，再让模型判断是否需要外部工具", "output": "明确的 state 更新和 trace"},
            {"step": "3. MCP boundary", "input": "需要读取日历或内部文档工具", "action": "MCP 客户端通过协议调用外部工具服务，得到结构化结果", "output": "工具观察被包装回框架消息"},
            {"step": "4. A2A boundary", "input": "需要外部数据团队 agent 补充解释", "action": "通过 agent 协作协议委托任务并接收状态/结果", "output": "外部 agent 的交付物进入 state"},
            {"step": "5. response", "input": "检索证据、工具结果、外部 agent 结果", "action": "框架生成最终回答，观测系统记录成本、延迟和错误", "output": "用户可见报告与审计记录"},
        ],
        "code_path": "框架 API 与协议适配层伪码",
        "code_symbol": "FrameworkToolAdapter / AgentDelegationAdapter",
        "code": """# 教学版：框架内部 API 不直接等于外部协议
class MCPToolAdapter(BaseTool):
    name = "calendar_search"
    args_schema = CalendarArgs

    def _run(self, query: str):
        # 协议细节被适配器包住，框架仍看见 BaseTool
        return mcp_client.call_tool("calendar_search", {"query": query})

class A2ADelegationNode:
    def __call__(self, state):
        task = {"goal": state["goal"], "context": state["summary"]}
        result = a2a_client.delegate("finance_agent", task)
        return {"external_findings": result}

# StateGraph 只关心节点读写 state，不关心协议字段如何演进
""",
        "code_note": "伪码强调适配层：框架内部最好仍使用 BaseTool、StateGraph、Runnable 等稳定契约；MCP/A2A 的 wire format 留在 adapter 中。这样协议升级时主要改 adapter，而不是改业务图。",
        "sections": [
            ("框架 API 与协议不是同一种东西", [
                "框架 API 是你在代码里调用的库接口：create_agent、StateGraph、BaseTool、Runnable、BaseRetriever。它帮助你组织进程内的控制流、对象生命周期、回调、测试和状态。协议是跨边界沟通的约定：不同进程、产品或组织如何发现能力、描述输入输出、传递任务状态、返回错误。把二者混为一谈，会导致设计错位：你可能把协议字段散落在业务节点里，也可能期望外部协议替你管理内部 state。",
                "更稳的做法是保留适配层。对工具协议，写一个 BaseTool 或 ToolNode adapter，把外部工具发现和调用包成框架工具；对 agent 协作协议，写一个图节点或子图，把外部委托包成 state 更新；对模型 API，使用 provider wrapper，把 raw response 归一成 AIMessage。适配层是抗演进缓冲垫，也是测试边界。",
            ]),
            ("MCP：工具和上下文能力的插座", [
                "MCP 常被放在 agent/AI 客户端与外部工具、资源、提示之间。它的关键价值不是让模型更聪明，而是让工具暴露方式更标准：客户端可以发现有哪些工具或资源，知道参数 schema，按协议调用，并以统一方式接收结果或错误。对于桌面 AI、IDE、企业内部工具目录和跨产品集成，这类协议能减少每个工具都写一套私有插件的成本。",
                "但协议不是权限系统的全部，也不是业务校验的替代。MCP server 暴露了工具，不代表任何 agent 都该调用；客户端仍要做用户授权、租户隔离、审计、速率限制、危险动作确认和数据脱敏。框架接入 MCP 时，应把 MCP 工具映射成 BaseTool 或等价对象，再复用课程里讲过的 args_schema、ToolMessage、错误分类和人审策略。",
            ]),
            ("A2A：agent 间协作的任务边界", [
                "A2A 这类 agent-to-agent 协议关注的问题与工具协议不同。工具通常是被调用的能力：输入参数，返回结果；agent 协作更像委托任务：对方可能有自己的模型、工具、状态、策略和执行时间，可能需要报告进度、澄清需求、返回结构化成果或拒绝任务。协议边界要表达身份、能力、任务描述、状态、结果、错误和可能的安全约束。",
                "在 LangGraph 心智模型里，调用另一个 agent 可以被建成一个节点、一个子图或一个 handoff。关键是不要失去可审计状态：委托了什么，给了哪些上下文，对方返回什么，是否可信，是否需要人审，失败后是否重试或转给备用 agent。A2A 不是让所有 agent 随意聊天，而是给跨系统协作提供可治理边界。",
            ]),
            ("AI stack 的层次与横切关注点", [
                "一个实用 AI stack 可以粗分为：产品与业务层、编排框架层、协议/集成层、模型 API 层、推理服务层、数据/检索层、基础设施层。评测、可观测、安全、成本控制和合规不是某一层专属，而是横切每层。比如同一次工具调用，应用层要知道用户是谁，框架层要记录 trace，协议层要记录外部调用，工具层要做权限，模型层要记录 token，数据层要记录文档来源。",
                "分层的好处是定位问题。回答慢，可能是模型推理慢、向量检索慢、外部工具慢、agent 之间等待、或 UI 流式没有及时渲染。回答错，可能是检索召回差、工具权限不足、模型没有读 ToolMessage、外部 agent 返回低质量结果。没有 stack 坐标，你只能笼统说“AI 不稳定”；有坐标后，你能把失败归到具体层并设计证据。",
            ]),
            ("协议演进下的版本策略", [
                "MCP、A2A、provider tool calling 和框架 API 都在演进。课程内容如果写死某个字段“永远如此”，很容易过期。工程上也一样：不要让业务节点直接依赖协议原始字段；不要把 provider 的实验参数扩散到核心 state；不要把外部 agent 的所有返回都当可信事实。把协议字段收口到 adapter，把 adapter 的版本、能力和限制写进测试和文档，升级时才能局部修改。",
                "版本策略还包括降级。外部 MCP server 不可用时，系统能否禁用相关工具并给出可解释提示；A2A 委托超时时，能否转人工或返回部分结果；provider 不支持某个 schema 特性时，能否使用更简单工具描述；推理服务压力大时，能否切换模型或降低并发。这些都不是协议本身自动解决的，而是应用和框架层的责任。",
            ]),
            ("边界情况：协议演进与不兼容时怎么办", [
                "协议会演进，这是设计时就该假设的常态，而不是意外。MCP、A2A、provider tool calling 都可能升级字段、调整能力、引入版本协商。工程上的对策是：固定你采用的规范版本和 SDK 版本，为关键路径写兼容测试，并把“能力发现”当成运行时事实而非编译期常量——对方支持什么，应该问出来或探测出来，而不是写死。当某个能力在新旧版本间不一致时，adapter 是吸收差异的那层，业务图不该感知。",
                "不兼容和不可用必须有降级路径。外部 MCP server 掉线时，系统能否禁用相关工具并给出可解释提示；A2A 委托超时时，能否转人工或返回部分结果；provider 不支持某个 schema 特性时，能否退回更简单的工具描述。这些都不是协议自动解决的，而是应用与框架层的责任。一个常见误解是“协议等于安全”：协议标准化的是连接方式（wire format），不是认证、授权、租户隔离和审计；跨边界进来的数据，默认都应被当成不可信输入处理。",
            ]),
            ("常见误解：MCP/A2A 会替你做治理", [
                "接入 MCP 不等于卸掉治理责任。MCP server 暴露了一批工具，不代表任何 agent 都该调用它们；客户端仍要做用户授权、租户隔离、速率限制、危险动作确认和数据脱敏。正确做法是把 MCP 工具映射成 BaseTool 或等价对象，复用课程里讲过的 args_schema 校验、ToolMessage 回填、错误分类和人审策略。协议帮你省掉的是“每个工具各写一套私有插件”的成本，而不是业务安全那一整套。",
                "A2A 这类 agent 协作协议也一样。被委托 agent 返回的结果不是天然可信的事实：它可能有自己的偏差、过期数据或失败。你需要保留可审计状态——委托了什么、给了哪些上下文、对方返回什么、是否需要人审、失败后是否重试或转给备用 agent。把外部 agent 的交付物直接当权威结论写进核心 state，等于把治理边界让渡给了你无法控制的系统。协议提供的是可治理的协作边界，治理本身仍要你来做。",
            ]),
            ("把 stack 坐标系用于成本、延迟与观测", [
                "分层不只是画图，它是成本与延迟的归因坐标。给每一层定一个延迟预算：应用层、框架编排、协议边界、模型推理、检索数据，各自允许多少毫秒；当总延迟超标时，用 trace 看超支落在哪一层，而不是笼统说“AI 很慢”。成本同理，一次请求的 token、外部工具调用次数、检索请求量应能分别归到对应层，这样优化才有靶子，降级才知道先砍哪里。",
                "跨层观测的关键是相关 id。一次用户请求应携带一个贯穿全栈的 run id：应用层记录用户与租户，框架层记录节点与 state 变化，协议层记录外部调用 id，模型层记录 token 与 finish reason，数据层记录命中的文档来源。只有当这些片段能用同一个 id 串起来，你才能在一张 trace 上回答“慢在哪、错在哪、贵在哪”。没有相关 id，分层就只是漂亮的架构图，帮不上排障。",
            ]),
            ("设计取舍：用一层适配换取协议自由", [
                "AI 栈里协议众多且各自演进，一个务实的设计取舍是用一层适配换取对协议的自由。把外部工具协议、智能体协作协议、模型接口都收进各自的适配器，业务图里只出现稳定的工具对象、状态字段和消息。这样当某个协议升级、替换或临时不可用时，你改的是适配器，而不是整张业务流程。适配层看似多写代码，换来的却是把协议风险从核心隔离出去的长期收益，让业务逻辑不必跟着规范一起抖动。",
                "第二个取舍关乎信任边界。栈越往外，越不该默认可信：外部工具返回的数据、外部智能体交付的结论、第三方服务的状态，都应被当成需要校验、需要审计、可能失败的输入。把它们映射回标准对象的同时，也要带上来源、时间和可信度标记，并为它出错了怎么办预留位置。一个成熟系统的强壮，往往不在于它接了多少协议，而在于每个外部边界都有清楚的校验、降级和审计。",
                "第三个取舍是在哪一层付出可观测成本。给每一层都加追踪、指标和相关标识是有成本的，但缺了它，跨层排障几乎不可能。务实的做法是优先保证那条贯穿全栈的相关标识和关键层的指标，让一次请求在应用、编排、协议、模型、数据之间的足迹能被拼起来。可观测不是免费的，但它是把分层架构图变成可排障系统的那笔必要投入，省不得也拖不得。",
            ]),
            ("协议不是越多越好", [
                "面对琳琅满目的协议和标准，一个容易被忽略的判断是：接入本身就是成本。每多接一个协议，就多一份版本兼容、安全审计、可观测和降级的长期维护。值得接的协议，应该是能明显降低集成成本或打开关键能力的那种，而不是为了赶时髦把所有标准都塞进系统。先问这个协议解决了我哪个真实问题，再决定是否引入，往往比追逐规范清单更省心。",
                "即使决定接入，也建议从一个最小可用的子集开始：先支持你真正用到的能力，把适配层和降级路径打磨稳，再按需扩展。一次性实现协议的全部特性，既拖慢上线，又增加了你可能根本用不到的维护面。协议的价值在于连接，但连接的纪律在于克制；接得少而稳，常常比接得多而脆更接近一个可靠系统。",
            ]),
            ("课堂检查清单：新协议接入前的十二个问题", [
                "一，它连接的是工具、agent、模型、数据还是观测。二，它跨越进程、产品、组织还是只在库内部。三，能力发现和 schema 描述由谁负责。四，身份认证和用户授权在哪里完成。五，错误是协议错误、工具错误、模型错误还是业务错误。六，结果如何映射回 BaseMessage、ToolMessage 或 state。七，协议字段是否被 adapter 收口。八，观测能否串起应用 run 与外部调用 id。九，超时、重试和幂等策略在哪里。十，危险动作是否需要人审。十一，版本升级是否有兼容测试。十二，协议不可用时是否有降级路径。",
            ]),
        ],
        "tables": [
            {"title": "协议边界对照表", "intro": "这张表用边界而非品牌记忆协议。具体字段、端点和能力以当时规范为准。", "headers": ["层次", "解决的问题", "典型对象", "不该承担"], "rows": [
                ["框架 API", "进程内编排、状态、工具对象、回调、测试", "Runnable、StateGraph、BaseTool、create_agent", "跨产品 wire format 的长期兼容承诺"],
                ["工具协议", "工具/资源/提示发现与调用", "MCP tool/resource/prompt 类能力", "内部 Agent 循环和业务权限全部逻辑"],
                ["Agent 协议", "agent 发现、任务委托、状态和结果交换", "A2A 风格任务、进度、交付物", "替代每个 agent 内部框架"],
                ["模型 API", "文本/多模态生成、tool call 输出、token usage", "provider chat/completions/responses", "业务流程、数据权限和长期记忆"],
                ["数据协议/存储", "文档、向量、索引、检索和权限", "VectorStore、Retriever、数据库 API", "模型推理和 agent 协商"],
            ]},
        ],
        "pitfalls": [
            ("接入 MCP 就不用工具 schema 和权限", "MCP 可以标准化工具暴露，但应用仍要做授权、校验、审计、脱敏和危险动作控制。"),
            ("A2A 会替代 LangGraph", "A2A 类协议连接 agent 系统；LangGraph 管理某个系统内部的状态图和运行时，二者层次不同。"),
            ("协议字段可以直接写进业务 state", "应通过 adapter 映射到框架稳定对象，避免规范演进导致业务图大面积修改。"),
            ("AI stack 分层只是画图", "分层用于定位责任、失败、观测和降级路径，是工程排障工具。"),
        ],
        "lab_title": "为一个 MCP 工具和外部 agent 画边界",
        "lab_steps": [
            "选择一个外部日历工具，写出它作为 MCP 工具暴露时的名称、参数、权限和返回摘要。",
            "把这个 MCP 工具映射成 LangChain BaseTool，说明 adapter 保存哪些协议字段、暴露哪些标准字段。",
            "选择一个外部财务 agent，写出通过 A2A 风格委托时的任务输入、状态、超时和交付物。",
            "画出 StateGraph 中两个节点：一个调用工具，一个委托 agent，并写出它们各自更新的 state key。",
            "为 MCP server 不可用、外部 agent 超时、权限不足三种情况写降级策略。",
        ],
        "version_note": "MCP、A2A、provider API 和框架适配层都在快速演进；本文只固定概念边界：工具协议、agent-to-agent 协议、框架 API、模型/数据底座和横切治理。请在项目中记录采用的规范版本、SDK 版本和兼容测试。",
        "points": [
            "框架 API 管内部编排，协议管跨边界沟通，二者不应混淆。",
            "MCP 更适合理解为工具/资源/提示等能力的标准化连接边界。",
            "A2A 更适合理解为 agent 系统之间的任务委托、状态同步和结果交付边界。",
            "协议接入应通过 adapter 映射到 BaseTool、StateGraph、ToolMessage 或 state。",
            "AI stack 分层能帮助定位责任、失败、观测、权限和降级策略。",
        ],
    }
)


LESSON_45_LEARNING_MAP = _build_lesson(
    {
        "lead": "学完 LangChain、LangGraph、RAG、Agent、测试和生态边界后，下一步不是同时追所有新名词，而是按邻接层补能力。应用开发者最常遇到的瓶颈通常在四个方向：推理服务为什么慢和贵，向量数据库为什么召回不准，评测与可观测如何证明 Agent 没退化，协议与贡献如何让系统接入真实生态。本课给出后续学习地图：从本课程已学锚点出发，分阶段进入 inference engines、vector databases、eval/observability、agent protocols 和 contributing。每一阶段都包含读什么、做什么实验、怎样判断学会，以及什么时候不要深入。",
        "analogy": "把学习路线想成从市中心向外扩展地铁。你已经在 LangChain/LangGraph 这座枢纽站掌握换乘：消息、工具、Runnable、图、RAG、Agent、测试。下一站不该随机坐车，而是按工作需要选择支线：系统慢就去推理引擎线，回答找不到证据就去向量检索线，上线不放心就去评测观测线，要接外部工具和 agent 就去协议线，想理解框架本身就去贡献线。每条线先坐两站建立体感，再决定是否深入终点。",
        "map_title": "本课地图：从应用编排向相邻层扩展",
        "map_nodes": [
            ("已学地基", "Runnable、BaseMessage、BaseChatModel、BaseTool、StateGraph、RAG、AgentMiddleware", "before"),
            ("推理引擎", "理解 KV cache、batching、并发、量化、延迟和吞吐的取舍", "now"),
            ("向量数据库", "理解 embedding、ANN/HNSW、过滤、rerank、召回/精度评估", "now"),
            ("评测观测", "把 trace、数据集、回归、成本、错误分类接成质量闭环", "source"),
            ("协议贡献", "学习 MCP/A2A 边界，阅读源码并贡献小而可验证的改动", "after"),
        ],
        "source_intro": "本课 source rows 指向课程内已经验证的锚点与上游主要符号。学习地图不是让你一次读完所有源码，而是告诉你每条支线从哪个已知概念出发，如何用小实验建立反馈。",
        "sources": [
            {"file": "08-runnable.html", "symbol": "Runnable", "role": "所有组件可组合的应用层协议", "direction": "后续学习任何框架时先问它的可组合契约是什么"},
            {"file": "11-chat-internals.html", "symbol": "BaseChatModel / provider adapter", "role": "模型 API 适配层", "direction": "下探推理引擎前先分清 provider API 与 serving engine"},
            {"file": "37-embeddings-vectorstores.html", "symbol": "Embeddings / VectorStore", "role": "向量化与索引入口", "direction": "进入 ANN、HNSW、过滤、混合检索和向量数据库"},
            {"file": "38-retrievers-rerankers.html", "symbol": "BaseRetriever", "role": "query -> documents 的检索契约", "direction": "学习召回、rerank、压缩和 RAG 评估"},
            {"file": "41-observability-ci.html", "symbol": "callbacks / run tree / CI", "role": "观测、回归和发布守卫", "direction": "进入 eval、dataset、trace、成本和质量门"},
            {"file": "15-contributing.html", "symbol": "build/check loop", "role": "源码调试与贡献流程", "direction": "把学习转成可复查实验和小 PR"},
        ],
        "flow_title": "状态流：四阶段后续学习计划",
        "flow_steps": [
            ("阶段一：复盘地基", "用课程 glossary 检查 Runnable、Message、Tool、StateGraph、Retriever 是否能讲清。", "1-2 天"),
            ("阶段二：相邻层实验", "分别做一个本地模型服务、一个向量库索引、一个 trace/eval 数据集。", "1 周"),
            ("阶段三：源码深读", "选择 vLLM/llama.cpp、hnswlib/Qdrant、LangSmith/OpenTelemetry、MCP/A2A SDK 中最贴近工作的一个。", "2-4 周"),
            ("阶段四：工程化项目", "把推理、检索、Agent、评测、协议适配接进一个端到端小系统。", "1-2 月"),
            ("阶段五：贡献", "修文档、补测试、提交 adapter 或教程示例，留下可复现证据。", "长期"),
        ],
        "trace": [
            {"step": "1. symptom", "input": "Agent 回答慢且费用高", "action": "先用 trace 判断时间花在模型、工具、检索还是外部 agent", "output": "若主要在模型，进入推理引擎支线"},
            {"step": "2. inference", "input": "高延迟/高并发", "action": "学习 KV cache、continuous batching、量化和 serving 配置", "output": "能解释吞吐、延迟、显存的三角关系"},
            {"step": "3. retrieval", "input": "答案缺证据或找错文档", "action": "学习 chunk、embedding、ANN、metadata filter、rerank 和 eval", "output": "能用数据集测召回与精度"},
            {"step": "4. eval", "input": "上线前担心退化", "action": "建立固定问题集、trace 断言、成本门和人工审阅样本", "output": "每次改动有质量信号"},
            {"step": "5. protocol/contrib", "input": "需要接外部工具或理解框架", "action": "写 adapter、读源码、补测试或贡献文档", "output": "学习成果沉淀为可复查资产"},
        ],
        "code_path": "个人学习计划伪码",
        "code_symbol": "choose_next_topic(symptom)",
        "code": """def choose_next_topic(symptom):
    if symptom in ["slow", "expensive", "serving_capacity"]:
        return "inference engines: KV cache, batching, quantization"
    if symptom in ["bad_recall", "missing_citation", "stale_context"]:
        return "vector databases: embeddings, ANN, filters, rerank"
    if symptom in ["regression", "hard_to_debug", "unknown_quality"]:
        return "eval/observability: datasets, traces, metrics"
    if symptom in ["external_tools", "multi_org_agents"]:
        return "agent protocols: MCP, A2A, adapters"
    return "contributing: read source, write focused tests, document evidence"
""",
        "code_note": "学习路线也应像工程系统一样由症状驱动。不要因为某个词热门就立刻深挖，先问它解决你当前哪一层问题，再用小实验验证投入产出比。",
        "sections": [
            ("先复盘应用层地基", [
                "继续学习前，先确认本课程主线已经内化。你应能不用代码解释 Runnable 为什么是协议，BaseMessage 为什么是聊天中间表示，BaseChatModel 如何做 provider adapter，BaseTool 如何拆 schema 和执行，StateGraph 为什么需要 state/reducer/edge，Pregel 为什么按超步执行，create_agent 如何把模型和工具循环组装成图，BaseRetriever 与 VectorStore 如何支撑 RAG，AgentMiddleware 如何在循环边界插入策略。",
                "如果这些概念还需要翻笔记，直接跳到推理引擎或向量库会很吃力。因为下游问题最终还会回到应用层：模型服务再快，也要被 BaseChatModel 适配；向量库再强，也要通过 Retriever 进入 RAG；协议再标准，也要映射成 Tool 或图节点；评测再复杂，也要断言消息、工具和 state。地基不稳，扩展层越多越混乱。",
            ]),
            ("推理引擎：理解慢和贵", [
                "推理层关注的是模型如何被服务出来：请求排队、prefill、decode、KV cache、continuous batching、显存碎片、量化、并发、吞吐、首 token 延迟和总延迟。应用开发者不一定要写 CUDA kernel，但要能解释为什么上下文越长越慢，为什么并发高时 batching 重要，为什么量化能省显存但可能影响质量，为什么同一个模型在不同 serving engine 上表现不同。",
                "推荐路线是先使用一个本地或托管推理服务跑同一组 prompt，记录首 token、总耗时、token 数和并发；再读一篇 serving engine 的架构文章或核心源码导览；最后回到 LangChain provider adapter，观察这些 serving 参数如何通过模型 API 暴露。目标不是成为底层工程师，而是能在应用层做合理容量、成本和降级决策。",
            ]),
            ("向量数据库：理解找得到和找得准", [
                "RAG 的失败常被误怪模型，实际可能是 chunk 切错、embedding 不适合、metadata filter 漏掉权限、ANN 参数召回不足、rerank 排序错误、文档过期或引用没保存。向量数据库学习要围绕“query -> candidate documents -> rerank -> answer”这条链，而不是只背某个产品 API。先理解 embedding 语义，再理解 HNSW/ANN 为什么用近似搜索，最后理解过滤、混合检索和 rerank 如何影响最终上下文。",
                "小实验可以从同一批文档开始：改变 chunk size、overlap、embedding 模型、top_k、metadata filter 和 reranker，记录召回率、精度、引用覆盖和回答质量。不要只看最终答案，要保存每次检索到的 Document id、score、metadata 和片段。这样你能判断问题在检索前、检索中、rerank 后还是生成阶段。",
            ]),
            ("评测与可观测：把感觉变成证据", [
                "Agent 系统上线后，最可怕的不是单次失败，而是你不知道是否退化。评测与可观测要把课程里的 callbacks、run tree、trace_table、fake models 和 CI 连接起来：固定问题集验证核心场景，消息级断言验证工具循环，RAG 数据集验证召回，人工样本验证答案可用性，成本和延迟指标验证工程约束。每次修改 prompt、工具、检索或模型，都应有一组可重复信号。",
                "观测不是只上报日志。一个有用 trace 应能回答：用户输入是什么，模型看到哪些消息，调用了哪些工具，工具参数和结果是什么，检索到了哪些文档，花了多少 token 和时间，错误在哪里发生，最终回答引用了什么证据。没有这些字段，debug 只能靠猜；有这些字段，评测失败可以快速归因。",
            ]),
            ("协议与贡献：从使用者变成维护者", [
                "MCP、A2A、provider tool calling、OpenTelemetry、LangSmith、向量库 SDK 等协议和工具，会不断改变应用边界。学习它们的正确方式不是背字段，而是写 adapter：把外部工具映射成 BaseTool，把外部 agent 映射成 StateGraph 节点，把外部 trace 映射成统一 run id。adapter 写完后补测试，验证协议升级不会污染业务 state。",
                "贡献则是最高质量的学习。你可以从文档错别字、教程示例、类型注解、测试补充、小 bug 修复开始。关键是遵守第八部分的工程循环：定位包边界，建立 editable 环境，写最小失败测试，修复，跑相关检查，提交小 PR。贡献不是为了显得资深，而是把你的理解变成别人也能复查的证据。",
            ]),
            ("阶段化阅读计划", [
                "第一周复习本教程：每天选一个 Part，用 glossary 反查术语，再手画一次 source map。第二周做三个实验：本地模型服务压测、向量库检索评估、Agent trace 回归。第三到四周选一个最贴近工作的方向深读源码：推理层选 serving engine，检索层选小型 ANN 实现或向量库，观测层选 trace/eval 工具，协议层选 MCP/A2A adapter。第五周做端到端项目，把模型、检索、工具、评测和协议接在一起。",
                "每阶段都要有产出：一张图、一组脚本、一份实验记录、一个测试或一篇短文。没有产出的学习很容易变成收藏链接。产出不需要宏大，但必须可复现：别人拿到你的 repo 或笔记，能知道你运行了什么、看到什么、得出什么结论、哪些结论依赖特定版本。",
            ]),
            ("边界情况：学习路线最容易踩的坑", [
                "学习路线最常见的坑，是没有症状就追热点。看到一个新名词就深挖，却说不清它解决你当前哪一层问题，结果是收藏了一堆链接、跑了几个 demo，能力却没沉淀。第二个坑是只读不做：没有可运行的小实验、没有量化指标，学到的东西无法验证，也无法迁移到真实系统。第三个坑是错配投入：把大量时间花在你根本不会维护的底层内核上，反而忽略了离工作更近的相邻层。",
                "还有一个误解是“应用开发者不需要懂推理或检索”。你确实不必写 CUDA kernel 或实现 HNSW，但你需要懂到足以解释成本、延迟、召回和降级的程度：为什么上下文越长越慢、为什么并发高时 batching 重要、为什么 chunk 和 embedding 选择会左右召回、什么时候该量化或换模型。懂得够用，才能在应用层做合理的容量、预算和取舍决策；完全不懂，就只能把问题笼统归给“模型不稳定”。",
            ]),
            ("常见误解：把当前工具版本当成长期事实", [
                "推理引擎、向量库、评测平台的名字和排名变化很快，今天的“最佳实践”可能半年后就换了主角。把某个工具的当前版本当成长期事实去背，性价比很低。更值得学的是可迁移的原理：KV cache 和 batching 解释了几乎所有推理服务的吞吐与延迟取舍，ANN 与近似搜索解释了几乎所有向量库的召回与精度权衡，固定数据集加 trace 断言解释了几乎所有评测框架的质量信号，adapter 解释了几乎所有协议接入的演进策略。原理稳定，产品易变。",
                "落地时建议先用成熟托管服务建立体感，再决定是否深入自建。先把一条链路用现成服务跑通、记录指标，理解它的形状和瓶颈，往往比一上来就读底层源码更高效；只有当托管方案在成本、延迟、合规或可控性上确实不够，再深入实现层。无论用什么，都要把判断依赖的版本和文档入口记下来，避免把一次临时验证当成永久结论。",
            ]),
            ("用 trace 把症状映射到学习方向", [
                "举个具体例子：一个 Agent 既慢又答不准。打开 trace，发现大部分时间花在模型推理上，而答案里缺少应有的引用证据。这一条 trace 同时指向两个方向——慢指向推理引擎支线，缺证据指向向量检索支线。这时不要两条线一起铺，先按影响最大的那条投入：如果用户主要抱怨等待，先去推理层；如果主要抱怨答非所问，先去检索层。症状驱动能让有限的学习时间用在真正的瓶颈上。",
                "每个学习 sprint 都应以一个能反哺真实系统的 artifact 收尾：一段压测脚本、一份检索评估数据集、一组 Agent 消息级回归测试、一个协议 adapter，或一篇说明取舍的短文。没有产出的学习很容易退化成消遣；有可复现产出的学习，才会变成团队能复查、能延续的工程能力。判断一条学习线值不值，最简单的标准就是：四周后，它有没有改变你项目里的某个配置、测试或架构决定。",
            ]),
            ("设计取舍：把学习当成有预算的工程", [
                "把后续学习当成一个有预算的工程项目，方向选择会清晰很多。预算是你的时间和精力，需求是项目当前最痛的瓶颈，验收标准是一个能反哺系统的产出。像排期一样，先挑投入产出比最高的那条线，做出一个最小可验证的成果，再决定要不要追加投入。最怕的是没有预算意识：同时铺开五条线，每条都浅尝辄止，最后哪条都没有形成能用的能力，只剩一堆收藏夹里的链接。",
                "第二个取舍是广度优先还是深度优先。对应用开发者，通常建议先在相邻层都建立够用的体感，能解释推理为什么慢、检索为什么不准、评测为什么必要、协议为什么要适配，再针对当前瓶颈深挖一条。过早深入某个底层实现，容易学到一堆暂时用不上的细节；完全只停在表面，又无法解决真实问题。广度建立坐标，深度解决瓶颈，两者按项目需要交替推进。",
                "第三个取舍是自建还是托管。很多能力都有成熟托管方案，先用托管把链路跑通、把指标量出来，往往比一上来就自建更快形成判断。只有当托管在成本、延迟、合规或可控性上确实不够时，再投入自建。无论选哪条，都要给学习留下可复查的证据：一段脚本、一份数据、一组测试。证据让学习可以被团队复用，也让你在半年后还能想起当时为什么这么决定。",
            ]),
            ("给自己留一条复盘回路", [
                "学习地图最后该补上的一环，是复盘回路。每完成一段学习，回到项目里问三个问题：它解决了我原来的哪个症状，我能不能用一个指标证明改善，这条经验能不能写进团队文档让别人复用。没有复盘，学习容易停在我大概懂了；有复盘，它才会沉淀成我能解释、能验证、能传授的能力。复盘不需要很长，但要诚实地面对投入和产出。",
                "复盘也帮你修正方向。如果一条线学了两周却没改变项目里的任何配置、测试或决定，那很可能是方向选错了，或深度过头了，该及时止损换线。学习不是线性消耗时间，而是不断用真实反馈校准的循环。把症状驱动、最小实验、可复查产出和定期复盘连成回路，你的学习就有了和工程系统一样的自我纠错能力。",
            ]),
            ("课堂检查清单：判断是否该深入某方向", [
                "一，这个方向是否解决你当前项目的真实瓶颈。二，你能否用课程概念连接它与应用层。三，是否有可运行小实验。四，是否能收集量化指标而不只看主观感觉。五，是否能找到源码入口或协议规范。六，是否有测试或数据集验证学习成果。七，是否会引入新的部署和安全成本。八，是否有团队成员能共同维护。九，是否已有成熟托管服务可先用。十，是否需要深入到底层实现，还是只需理解配置。十一，是否记录了版本依赖。十二，学习结束后能否反哺当前系统。",
            ]),
        ],
        "tables": [
            {"title": "后续学习路线表", "intro": "按症状选路线，能防止被技术热点牵着走。", "headers": ["方向", "先学关键词", "小实验", "学会的标志"], "rows": [
                ["推理引擎", "KV cache、batching、量化、吞吐、延迟", "同模型不同并发压测，记录首 token 和总耗时", "能解释慢在哪里、贵在哪里、如何降级"],
                ["向量数据库", "embedding、HNSW/ANN、filter、rerank", "固定问答集比较 chunk/top_k/rerank", "能用召回和引用证据定位 RAG 失败"],
                ["评测观测", "dataset、trace、run tree、regression、cost", "为 Agent 建消息级回归测试和成本门", "每次改动有可复现质量信号"],
                ["Agent 协议", "MCP、A2A、adapter、capability discovery", "把一个外部工具映射为 BaseTool", "协议变化被 adapter 隔离"],
                ["贡献", "editable、focused test、CI、source map", "修一个文档/测试/小 bug", "PR 描述能让陌生人复现"],
            ]},
        ],
        "pitfalls": [
            ("先追最火项目，再找用途", "学习应由症状和相邻层驱动；没有使用场景，很难形成可迁移理解。"),
            ("应用开发者不需要懂推理或检索", "不必写底层内核，但要懂足够多才能解释成本、延迟、召回和降级。"),
            ("评测等上线后再补", "没有基线就无法判断改动是否退化；评测应伴随 prompt、工具和检索演进。"),
            ("贡献必须从大功能开始", "最好的入门贡献往往是小测试、小文档和小修复，关键是证据完整。"),
        ],
        "lab_title": "制定一个四周学习 sprint",
        "lab_steps": [
            "列出当前项目最痛的一个问题：慢、贵、找不准、不可观测、协议集成或源码不熟。",
            "从路线表选择一个方向，写出三条关键词和一个最小实验。",
            "定义实验指标：延迟、召回、答案正确率、trace 完整度、adapter 兼容或 PR 检查。",
            "每周产出一个可复查 artifact：脚本、图、测试、笔记或小 PR。",
            "四周后回到项目，说明这条学习线如何改变架构、配置、测试或文档。",
        ],
        "version_note": "学习地图中的项目和协议会变化，本文不承诺某个工具的当前排名或长期地位。请把它当作层次化方法：从已学应用层出发，按真实症状选择相邻层，用实验和版本证据校验。",
        "points": [
            "后续学习应从真实症状和相邻层出发，而不是追逐名词。",
            "推理引擎解释延迟、吞吐、显存和成本；向量数据库解释召回、过滤和 RAG 质量。",
            "评测与可观测把 Agent 质量从感觉变成可重复证据。",
            "协议学习要落到 adapter；贡献学习要落到小而可验证的 PR。",
            "每个阶段都要产出可复查 artifact，学习才会沉淀为工程能力。",
        ],
    }
)


_PART_ROWS = []
for idx, (fname, title, part) in enumerate(shell.PAGES, 1):
    _PART_ROWS.append((part, fname, title, idx))


def _glossary_lesson():
    grouped = []
    seen_parts = []
    for part, _fname, _title, _idx in _PART_ROWS:
        if part not in seen_parts:
            seen_parts.append(part)
    for part in seen_parts:
        rows = [r for r in _PART_ROWS if r[0] == part]
        grouped.append(
            f"<h2>{part}：页面与核心术语</h2>"
            + _table(
                ["课序", "页面", "标题", "建议复习词"],
                [
                    [
                        str(idx),
                        f'<a href="{fname}">{fname}</a>',
                        title,
                        _terms_for_page(fname),
                    ]
                    for _part, fname, title, idx in rows
                ],
                "t",
            )
        )
    lead = "术语表不是背单词页，而是全书的概念索引、源码索引和复习路线。C-level 版本按 Parts 1-9 重写：每一行都使用当前 shell.PAGES 中的页面文件名和标题，避免旧课号；每个术语都指向它在课程中的上下文；最后附上源码锚点表，帮助你从概念跳到 Runnable、BaseMessage、BaseChatModel、BaseTool、StateGraph、Pregel、create_agent、BaseRetriever、VectorStore、AgentMiddleware 等关键符号。使用方法很简单：遇到陌生词先在本页定位，再跳回对应课复习图、trace 和源码入口。"
    html = (
        f'<p class="lead">{lead}</p>'
        + _analogy("把术语表想成一本城市黄页加地铁图。黄页告诉你每个机构叫什么、负责什么；地铁图告诉你它在哪一站、和哪些线路相连；源码锚点像门牌号，让你真正走到办公室门口。只背术语定义，就像只记公司名字不知道地址；只看源码不看概念，就像拿着门牌号却不知道部门职责。本页把名字、路线、职责和源码入口放在一起。")
        + shell.lesson_map(
            "本课地图：从查词到读源码",
            [
                ("按 Part 查", "先按课程九个部分找到概念所在章节", "before"),
                ("按术语查", "用浏览器搜索 Runnable、ToolMessage、HNSW、MCP 等关键词", "now"),
                ("按源码查", "用源码锚点表定位主要符号所在文件", "source"),
                ("按关系复习", "看相邻概念：消息-工具-Agent、Retriever-VectorStore-RAG", "now"),
                ("按项目应用", "把术语翻译成你项目里的对象、边界和测试", "after"),
            ],
        )
        + "<h2>源码入口：主要符号锚点</h2>"
        + _p("下表是本页最重要的 source map。路径按当前课程核验到的上游源码组织；如果上游移动文件，请优先搜索符号名并更新自己的笔记。")
        + shell.source_map(
            [
                {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable", "role": "统一可运行协议，定义 invoke/stream/batch/config 等组合契约", "direction": "模型、链、检索器、图都可按此组合"},
                {"file": "libs/core/langchain_core/messages/base.py", "symbol": "BaseMessage", "role": "聊天消息基类，承载 role/type/content/id/metadata 等标准字段", "direction": "prompt、chat model、Agent state 和 trace 共享"},
                {"file": "libs/core/langchain_core/language_models/chat_models.py", "symbol": "BaseChatModel", "role": "聊天模型基类，定义输入转换、generate/stream 调用骨架", "direction": "provider adapter 继承并实现具体调用"},
                {"file": "libs/core/langchain_core/tools/base.py", "symbol": "BaseTool", "role": "工具基类，定义 name、description、args_schema、invoke/run 与错误策略", "direction": "模型工具说明和 ToolNode 执行都围绕它"},
                {"file": "libs/langgraph/langgraph/graph/state.py", "symbol": "StateGraph", "role": "状态图构建器，节点读写共享 state，边决定控制流", "direction": "LangGraph 和 create_agent 的核心编排抽象"},
                {"file": "libs/langgraph/langgraph/pregel/main.py", "symbol": "Pregel", "role": "图执行引擎，按超步调度 actors、channels 和 writes", "direction": "CompiledStateGraph 的运行时基础"},
                {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "高层 Agent 工厂，组装模型、工具、middleware 和图循环", "direction": "用户入口连接 LangChain API 与 LangGraph 运行时"},
                {"file": "libs/core/langchain_core/retrievers.py", "symbol": "BaseRetriever", "role": "检索契约，输入 query 返回 Document 列表", "direction": "RAG 链、压缩、rerank 和工具化检索的边界"},
                {"file": "libs/core/langchain_core/vectorstores/base.py", "symbol": "VectorStore", "role": "向量库接口，负责文本/向量写入和相似度搜索", "direction": "连接 embedding、索引和 Retriever"},
                {"file": "libs/langchain_v1/langchain/agents/middleware/types.py", "symbol": "AgentMiddleware", "role": "Agent 中间件基类，在模型、工具和响应边界插入策略", "direction": "动态提示、模型包装、工具包装和结构化响应治理"},
            ]
        )
        + "<h2>状态流：一次查词复习如何变成源码阅读</h2>"
        + shell.state_flow(
            [
                ("遇到术语", "读到 BaseRetriever、ToolMessage 或 MCP，不先猜含义。", "keyword='BaseRetriever'"),
                ("定位课程", "在本页按 Part 或浏览器搜索找到对应页面与相邻概念。", "38-retrievers-rerankers.html"),
                ("回看图解", "打开该课的 lesson_map、trace_table、pitfall_grid，先恢复心智模型。", "concept -> flow"),
                ("打开源码", "用 source anchor 的文件 + 符号名进入上游源码或本课程 source map。", "class BaseRetriever"),
                ("落到项目", "写下你项目里哪个类、工具、节点或测试对应这个概念。", "local mapping"),
            ]
        )
        + "<h2>Trace：从一个陌生词到可测试理解</h2>"
        + shell.trace_table(
            [
                {"step": "1. search", "input": "术语 AgentMiddleware", "action": "在本页搜索并查看 Part 6 与 source anchor", "output": "知道它属于 Agent 内部和中间件"},
                {"step": "2. lesson", "input": "18-custom-middleware.html", "action": "回看 middleware 生命周期、wrap_model_call、wrap_tool_call", "output": "理解插入点和风险"},
                {"step": "3. source", "input": "middleware/types.py :: AgentMiddleware", "action": "阅读基类方法和泛型 state/context/response", "output": "知道如何实现自定义策略"},
                {"step": "4. project", "input": "本地客服 Agent", "action": "把动态系统提示和工具审计映射成 middleware", "output": "形成设计草图"},
                {"step": "5. test", "input": "设计草图", "action": "写 fake model + deterministic tool 的消息级测试", "output": "概念变成可验证行为"},
            ]
        )
        + "<h2>简化源码走读：术语表本身如何保持不过期</h2>"
        + shell.code_walkthrough(
            "src/part09_ecosystem_reference.py",
            "_glossary_lesson / shell.PAGES",
            """# 教学版：页面索引来自唯一导航源，避免旧课号漂移
for idx, (fname, title, part) in enumerate(shell.PAGES, 1):
    glossary.add_row(part=part, file=fname, title=title, terms=terms_for(fname))

source_anchors = [
    ("Runnable", "libs/core/langchain_core/runnables/base.py"),
    ("StateGraph", "libs/langgraph/langgraph/graph/state.py"),
]
""",
            "本页的页面/标题表由 shell.PAGES 生成，因此会跟当前导航保持一致。术语说明仍需人工维护，因为概念关系不是文件名能自动推断的。",
        )
        + "".join(grouped)
        + _section("核心概念分组索引", [
            "LangChain 核心：Runnable 是组合协议，LCEL 是表达组合的语法，RunnableConfig 让 callbacks、tags、metadata 穿过调用链，BaseMessage 让聊天历史有统一形状，BaseChatModel 把输入标准化并委派给 provider adapter，ChatGeneration 保存候选生成，Output Parser 与 structured output 把文本约束成结构化对象。复习顺序建议是：先看一次调用全链路，再看消息、聊天模型、Runnable 和 parser。",
            "工具与 Agent：BaseTool、args_schema、convert_to_openai_tool、AIMessage.tool_calls、ToolMessage、ToolNode、create_agent、AgentMiddleware、Runtime Context、recursion_limit 构成工具型 Agent 的主线。请求和结果靠 tool_call_id 配对，schema 生成和工具执行要分开，middleware 负责在模型和工具边界插入策略。复习时不要只看最终回答，要看消息序列和 trace。",
            "LangGraph：StateGraph、Node、Edge、conditional edge、reducer、channel、Pregel、Checkpoint、interrupt、Command、Send、StateSnapshot 构成有状态图运行时。重点关系是：节点返回 partial state，reducer/channel 合并更新，Pregel 按超步执行，checkpoint 让状态可恢复，Command 和 interrupt 让控制权可被人或路由改变。",
            "RAG 与记忆：Document、metadata、TextSplitter、Embeddings、VectorStore、BaseRetriever、rerank、compression、conversation state、long-term memory 组成证据链。RAG 失败要沿 query、chunk、embedding、ANN、filter、rerank、prompt stuffing、answer citation 排查。记忆不是无限聊天历史，而是把短期 state、摘要、长期事实和权限边界分层。",
            "工程与生态：fake model、deterministic tool、trace assertion、callbacks、LangSmith/run tree、CI、PDF、MCP、A2A、inference engine、vector database、eval/observability、contributing 让课程从 demo 走向工程。术语表最后几部分提醒你，框架只是应用层坐标的一部分，协议、推理、检索和评测都需要独立学习。",
        ])
        + _table(
            ["主题", "关键术语", "如何自测"],
            [
                ["调用与组合", "Runnable、invoke、stream、batch、LCEL、RunnableConfig", "能画出输入、config、回调和输出如何穿过一条链"],
                ["消息与模型", "BaseMessage、HumanMessage、AIMessage、ToolMessage、BaseChatModel、ChatGeneration", "能解释 provider payload 与标准消息的边界"],
                ["工具", "BaseTool、args_schema、convert_to_openai_tool、ToolNode、tool_call_id", "能把 schema 生成、参数校验、执行和回填分开测试"],
                ["图", "StateGraph、reducer、channel、Pregel、checkpoint、interrupt、Command", "能说明 state 如何在节点和超步之间变化"],
                ["RAG", "Document、Embeddings、VectorStore、BaseRetriever、rerank、memory", "能用检索结果而非最终回答定位问题"],
                ["工程", "fake model、trace、callbacks、CI、observability、capstone", "能为一次变更提供可复现检查"],
                ["生态", "MCP、A2A、AutoGen、CrewAI、LlamaIndex、inference engine", "能按层次和默认心智模型比较，而不写不可证断言"],
            ],
            "t",
        )
        + _section("按学习阶段重排术语：从入门到工程", [
            "术语表不必从字母或课号顺序读，按掌握阶段重排往往更有效。入门阶段先吃透最小词汇：Runnable 是组件可组合的协议，BaseMessage 是聊天的中间表示，invoke/stream/batch 是统一调用方式，RunnableConfig 让回调和元数据穿过调用链。这组词是读懂后面任何一课的门票；它们没立稳，越往后越像在背孤立名词。",
            "进阶阶段补上工具、Agent 与图的词汇，并且重点记关系而不是定义。BaseTool 与 args_schema 负责 schema，AIMessage.tool_calls 与 ToolMessage 靠 tool_call_id 配对，StateGraph 的节点返回 partial state、由 reducer 合并、被 Pregel 按超步执行、用 checkpoint 持久化。这一层的考点几乎都是“谁和谁如何连起来”，所以复习时要画箭头，而不是抄释义。",
            "工程阶段的词汇面向上线与协作：fake model、deterministic tool、trace 断言、callbacks、run tree、CI、PDF 让质量可复现；MCP、A2A、inference engine、vector database、eval/observability、contributing 把视野从框架扩展到整个栈。到这一层，术语表的作用更像索引：你不再逐条背，而是遇到问题时用它快速跳回对应课程、源码锚点和本地项目映射。",
        ])
        + _section("边界情况与常见误解：让术语表不腐烂", [
            "术语表会随课程和源码演进而过期，这是它最大的边界。本页刻意只用 shell.PAGES 里的当前文件名和标题，就是为了避免旧课号漂移；当你做笔记时也应跟随这个约定，用链接和符号名而不是“第几课”。一个常见误解是术语表写一次就一劳永逸，实际上每次课程新增页面、重排顺序或上游移动文件，它都需要重新生成并核对。",
            "源码锚点的边界在于：行号最容易随上游修改漂移，所以本页用“文件 + 符号名”而不是行号。当上游重命名符号或移动文件时，正确做法是按符号名搜索、确认语义未变，再更新自己的笔记，而不是死记某个路径。把锚点当成“可复查的入口”而非“永久坐标”，术语表才不会在一次上游重构后整页失效。",
            "最根本的常见误解，是把术语表当成背单词页。一个术语如果脱离了它的相邻关系（消息—工具—Agent、Retriever—VectorStore—RAG、StateGraph—Pregel—Checkpoint）和源码入口，就只学了一半。健康的用法是定期审计：随机抽几个词，检查它是否还指向有效页面、源码符号是否仍存在、你能否用它解释一段真实代码。审计不过关的词，就是下一轮要重读的课。",
        ])
        + _section("从术语到源码到测试：三条复查路径", [
            "以 ToolMessage 为例走一条完整路径：先在本页定位到它属于工具与 Agent 主线，跳回 06-tools.html 与 12-tool-internals.html 恢复“schema 生成与执行分离”的心智模型，再用源码锚点进入 messages/tool.py 阅读它如何用 tool_call_id 与 AIMessage.tool_calls 配对，最后在本地写一个测试：构造一次多工具并行调用，断言每个 ToolMessage 都配回了正确的请求。术语于是从一个名字，变成一段可验证的行为。",
            "再走 BaseRetriever 这条路径：本页指向 RAG 与记忆分组，跳回 38-retrievers-rerankers.html 理解 query 到 documents 的契约与 rerank 的位置，进入 retrievers.py 看它的最小接口，然后用一个固定问答集测召回：记录检索到的 Document id、score、metadata 和片段，比较改 chunk、top_k、reranker 前后的变化。这样你复习的不只是定义，而是“如何用证据判断检索好坏”。",
            "第三条以 StateGraph 的 reducer 为例：本页指向 LangGraph 分组，跳回 30-langgraph-reducers-channels.html 理解节点为何返回 partial state、reducer 如何合并，进入 graph/state.py 对照 add_messages 等内置 reducer，最后写一个测试模拟两个节点并行写同一个 key，断言合并结果符合预期。三条路径的共同套路都是：术语定位、课程复盘、源码入口、本地测试，缺一环，理解就停在表面。",
        ])
        + _section("把术语表当成排障的起点", [
            "术语表最被低估的用法，是当成排障的起点而不是终点。线上出问题时，先别急着翻代码，而是用一句话描述症状，再到术语表里判断它属于哪一组概念：是消息与模型、工具与智能体、图与状态、检索与记忆，还是工程与生态。把症状归到概念组，等于先缩小了搜索范围，再顺着该组的页面和源码锚点往下查，效率比漫无目的地翻日志高得多。",
            "举个例子：用户反映智能体偶尔不调用工具。在术语表里，这显然落在工具与智能体组。顺着它跳回相关课程，你会重新想起几个可能的断点：工具是否在绑定阶段进了载荷、模型是否真的发出了工具调用、调用是否被正确归一进了消息、执行节点是否按名字找到了工具。每一个断点都对应一个源码锚点和一个可写的测试。术语表在这里的作用，是把一句模糊抱怨翻译成一串可核验的假设。",
            "这种用法也解释了为什么术语表要和源码锚点、课程链接绑在一起，而不只是给出定义。定义只告诉你它是什么，锚点和链接才告诉你它在哪、和谁相连、怎么验证。把术语表当排障起点用几次，你会发现自己记住的不再是孤立的词，而是一张从症状到概念、再到源码和测试的地图，这正是 C-level 术语表想要培养的能力。",
        ])
        + _section("术语之间的关系网比单词更重要", [
            "比起单个术语的定义，它们之间的关系网更值得记住，因为真实问题几乎都发生在关系上。第一条主链是消息到工具到智能体：模型把意图表达成带工具调用的消息，执行节点按名字找到工具、校验参数并执行，结果以带 tool_call_id 的工具消息回填，模型读着观察决定下一步。理解这条链，你才能判断一次工具调用是在表达、执行还是回填环节出了问题。",
            "第二条主链是检索证据链：原始文档经过切分得到片段，片段经过嵌入变成向量写入向量库，检索器按查询召回候选，重排调整顺序，最终被拼进提示并在回答里留下引用。检索增强出问题时，几乎总能定位到这条链的某一环，例如切错、嵌入不合适、过滤漏权限、召回不足、重排乱序或引用丢失。把这条链记牢，排障就有了一条固定的巡查路线，而不必每次从零猜起。",
            "第三条主链是状态运行链：节点返回局部状态，归并器与通道合并更新，执行引擎按超步推进，检查点让状态可持久化与恢复，命令与中断让控制权能被路由或人改变。这三条主链分别对应工具、检索和图三大主题；术语表的深层价值，就是帮你随时把一个陌生词挂回它所在的链条，从而看清它在整个系统里的位置，而不是把它当成一个孤立名词死记硬背。",
        ])
        + _section("术语表如何随课程一起演进", [
            "术语表是活的文档，它必须随课程和源码一起演进，否则很快就会变成误导。本页的页面与标题来自统一的导航源，所以新增或重排课程时，这部分会自动跟上；但术语说明、相邻关系和源码锚点仍需要人工维护，因为这些信息无法只从文件名推断。每次大改课程后，正确的动作是重新生成本页，再逐组核对术语是否仍然准确、链接是否仍然有效。",
            "维护时要特别警惕三类残留：指向已被重命名页面的旧链接、引用了已不存在符号的源码锚点、以及偷偷溜回来的旧课号。它们都会让读者跳到错误的地方，或对照到过期的实现。一个简单的自检办法，是随机抽查若干术语，沿着它的链接和锚点走一遍，看是否还能到达正确的课程段落和源码符号；走不通的，就是下一次维护要修的条目。",
            "把术语表的维护本身也当成一种学习。每次核对，你都在重新走一遍课程的概念地图，确认自己对每条主链的理解仍然成立。久而久之，这种定期巡查会让你对整个体系的边界越来越清晰：哪些概念稳定、哪些随版本漂移、哪些需要重新解释。术语表于是不只是给别人的索引，也是你自己保持知识不过期的一面镜子。",
        ])
        + _section("用三个问题自测一个术语", [
            "想检验自己是否真的掌握一个术语，可以问三个问题：它属于哪一条主链，它的上一环和下一环分别是谁，它在源码里对应哪个符号。能顺畅回答，说明你记住的是关系和入口，而不是一句孤立定义；卡在某一问，正好指出该回去复习的方向。比起反复默写释义，这种基于关系的自测更接近真实排障时需要的能力。",
            "第二种自测是反向的：随便给出一个项目里的真实对象，比如某个本地工具类、某个检索函数、某个图节点，试着把它映射回术语表里的标准概念和源码锚点。能映射，说明术语已经和你的代码长在一起；映射不上，往往意味着这块代码还停留在照抄阶段。术语表的终点，从来不是背下多少词，而是能在自己的系统和课程的概念之间自由地来回翻译。",
        ])
        + shell.pitfall_grid(
            [
                ("术语表只用来背定义", "它应当作为跳转索引、源码索引和项目映射工具。"),
                ("课号永远不变", "本页使用当前文件名和标题，避免引用旧课号；写笔记也优先用链接和符号名。"),
                ("源码锚点等于行号", "行号最易漂移；文件 + 符号名更适合长期复查。"),
                ("概念孤立记忆", "要记关系：Message-Tool-Agent，Retriever-VectorStore-RAG，StateGraph-Pregel-Checkpoint。"),
            ]
        )
        + shell.lab_card(
            "用术语表复盘一个本地项目",
            [
                "选择你项目里的一个 AI 功能，列出它用到的消息、模型、工具、检索、图或协议术语。",
                "在本页找到每个术语对应课程和源码锚点，补齐你不确定的概念。",
                "画一张本地 source map：项目文件、LangChain/LangGraph 符号、外部协议或服务。",
                "挑一个最薄弱术语写测试，例如 ToolMessage 配对、Retriever 返回文档或 middleware 修改请求。",
                "把复盘结果写进项目文档，使用文件名和符号名而不是旧课号。",
            ],
        )
        + shell.version_note("术语表的页面标题来自当前 shell.PAGES；上游源码路径和协议名称会演进。未来更新课程时，应先重新生成本页并核对 source anchor 表，避免旧课号、旧标题或旧路径残留。")
        + _points([
            "本页是按 Parts 1-9 组织的概念、页面和源码索引。",
            "页面链接和标题来自当前导航，避免旧 lesson number 漂移。",
            "主要源码锚点覆盖 Runnable、BaseMessage、BaseChatModel、BaseTool、StateGraph、Pregel、create_agent、BaseRetriever、VectorStore、AgentMiddleware。",
            "查术语时要同时看概念定义、相邻关系、课程链接和源码入口。",
            "术语学习的终点是能映射到本地项目并写出可验证测试。",
        ])
    )
    return html


def _terms_for_page(fname):
    terms = {
        "01-what-is-langchain.html": "LangChain、LangGraph、编排层、生态边界",
        "02-monorepo.html": "langchain-core、partner 包、依赖方向、包边界",
        "03-lifecycle.html": "invoke、RunnableConfig、callback、provider payload",
        "04-source-reading-map.html": "Public API、protocol、implementation、tests/examples",
        "05-learning-path.html": "concept、trace、source、experiment、glossary",
        "04-messages.html": "BaseMessage、HumanMessage、AIMessage、ToolMessage、tool_calls",
        "05-chat-models.html": "init_chat_model、BaseChatModel、provider wrapper、stream",
        "06-tools.html": "@tool、BaseTool、args_schema、bind_tools、ToolMessage",
        "16-prompts.html": "ChatPromptTemplate、MessagesPlaceholder、PromptValue、partial",
        "10-output-parsers.html": "StrOutputParser、JsonOutputParser、schema validation、repair loop",
        "14-streaming-callbacks.html": "stream、astream_events、callbacks、run tree",
        "08-runnable.html": "Runnable、invoke、stream、batch、RunnableSerializable",
        "09-runnable-compose.html": "LCEL、RunnableSequence、管道、输入输出契约",
        "12-runnable-parallel-branch.html": "RunnableParallel、RunnableBranch、assign、passthrough",
        "13-runnable-config-callbacks.html": "RunnableConfig、ensure_config、tags、metadata",
        "15-runnable-retry-fallback.html": "with_retry、with_fallbacks、RunnableWithFallbacks",
        "24-langgraph-mental-model.html": "StateGraph、有状态图、节点、边、循环",
        "28-langgraph-state-schema.html": "TypedDict、Pydantic state、context_schema、partial state",
        "29-langgraph-nodes-edges.html": "add_node、add_edge、conditional edge、START/END",
        "30-langgraph-reducers-channels.html": "reducer、add_messages、LastValue、Topic、Aggregate",
        "31-langgraph-compile-runtime.html": "compile、CompiledStateGraph、Runtime、context",
        "25-langgraph-pregel-engine.html": "Pregel、superstep、Plan、Execution、Update",
        "32-langgraph-tasks-channels.html": "PregelTask、channels、writes、fan-in/fan-out",
        "26-langgraph-persistence-control.html": "Checkpoint、checkpointer、thread_id、resume",
        "33-langgraph-interrupt-command.html": "interrupt、Command、human-in-the-loop、goto/update",
        "34-langgraph-time-travel-debug.html": "StateSnapshot、get_state_history、replay、debug",
        "07-agents-intro.html": "model node、tools node、tool_calls、loop termination",
        "13-agent-internals.html": "create_agent、ToolNode、StateGraph、tools_condition",
        "18-custom-middleware.html": "AgentMiddleware、before_model、wrap_model_call、wrap_tool_call",
        "19-runtime-context.html": "Runtime、context_schema、response_format、structured_response",
        "35-agent-control-errors.html": "recursion_limit、tool errors、retry、fallback",
        "17-rag.html": "query、retrieve、stuff、map-rerank、answer",
        "36-documents-splitters.html": "Document、metadata、Loader、TextSplitter、chunk overlap",
        "37-embeddings-vectorstores.html": "Embeddings、VectorStore、similarity search、indexing",
        "38-retrievers-rerankers.html": "BaseRetriever、compression、rerank、recall/precision",
        "39-memory-conversation-state.html": "chat history、summary memory、long-term memory、state",
        "15-contributing.html": "editable install、source debugging、focused test、PR",
        "40-testing-debugging.html": "fake model、deterministic tool、trace assertion、regression",
        "41-observability-ci.html": "callbacks、LangSmith、CI、PDF、deploy",
        "20-capstone.html": "客服 Agent、prompts、tools、RAG、middleware、tests",
        "11-chat-internals.html": "BaseChatModel、_convert_input、ChatOpenAI、ChatAnthropic、ChatGeneration",
        "12-tool-internals.html": "BaseTool、args_schema、convert_to_openai_tool、ToolNode、ToolMessage",
        "21-langchain-vs-autogen.html": "AutoGen、CrewAI、LlamaIndex、graph/state、actor/pubsub、handoff",
        "22-ai-stack.html": "AI stack、MCP、A2A、framework API、tool protocol",
        "23-learning-map.html": "inference engine、vector database、eval/observability、contributing",
        "27-glossary.html": "concept index、source anchors、where to read next",
    }
    return terms.get(fname, "课程术语、源码锚点、复习路线")


LESSON_46_GLOSSARY = _glossary_lesson()
