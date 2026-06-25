"""C-level Part 2: user-facing LangChain API basics."""

import shell


LESSON_06_MESSAGES = "".join([
r"""
<p class="lead">消息是 LangChain 把“人说的话、模型说的话、工具观察到的结果”统一起来的对话与数据契约。你可以从字符串、字典、二元组或已经构造好的消息对象开始，但进入模型、工具循环和下游 Runnable 之后，稳定的形状应该是 <span class="mono">BaseMessage</span> 家族：<span class="mono">HumanMessage</span> 表达用户输入，<span class="mono">AIMessage</span> 表达模型输出和工具意图，<span class="mono">ToolMessage</span> 表达某次工具调用的执行结果。</p>

<div class="card analogy">
  <div class="tag">📨 生活类比 · 物流面单</div>
  消息像物流面单。包裹里装的东西是 content，寄件人和收件岗位是 role，额外条码是 additional_kwargs，费用和重量记录像 usage_metadata，工具调用编号像面单号。仓库可以临时听懂“帮我寄杯子”这句话，但一旦进入分拣线，就必须贴上标准面单；否则下一站不知道它是用户请求、模型回复，还是某个工具的回执。
</div>

<h2>本课地图：从输入形状到可追踪对话状态</h2>
<p>学习消息系统时，不要先背所有子类，而要先抓住一条主线：输入会被规范化为消息对象；provider adapter 会把消息对象翻译为厂商 payload；模型响应会再被归一化为 <span class="mono">AIMessage</span>；如果它包含 <span class="mono">tool_calls</span>，程序执行工具并追加 <span class="mono">ToolMessage</span>；随后 Runnable、Agent 或图节点继续读取同一份消息状态。</p>
""",
shell.lesson_map("消息系统的五个检查点", [
    ("原始输入", "字符串、PromptValue、BaseMessage 序列都可能出现在用户层", "before"),
    ("规范化", "BaseChatModel._convert_input 先分流；序列元素再由 convert_to_messages 规范化", "now"),
    ("适配器", "provider wrapper 读取 role/content/tool_calls 并生成厂商请求", "source"),
    ("工具回合", "AIMessage.tool_calls 表达意图，ToolMessage 表达执行观察", "now"),
    ("下游状态", "Runnable、Agent、LangGraph 节点共享同一种消息列表", "after"),
]),
r"""
<h2>源码入口：文件 + 符号名</h2>
<p>下面的表只写文件和符号，不写行号。行号会随版本漂移，符号职责更稳定。读源码时先从基类看公共字段，再看具体消息如何补充语义，最后看工具函数如何把各种输入变成这些对象。</p>
""",
shell.source_map([
    {"file": "libs/core/langchain_core/messages/base.py", "symbol": "BaseMessage", "role": "定义 content、additional_kwargs、response_metadata、id、name、type 等公共消息字段。", "direction": "所有具体消息继承它，模型接口围绕它传递数据。"},
    {"file": "libs/core/langchain_core/messages/human.py", "symbol": "HumanMessage", "role": "表示用户或外部人类发出的内容，是最常见的输入消息。", "direction": "由输入转换层创建，传入聊天模型。"},
    {"file": "libs/core/langchain_core/messages/ai.py", "symbol": "AIMessage", "role": "表示模型回复，承载 content、tool_calls、invalid_tool_calls、usage_metadata。", "direction": "由模型包装器返回，下游循环继续消费。"},
    {"file": "libs/core/langchain_core/messages/tool.py", "symbol": "ToolMessage", "role": "表示工具执行结果，并用 tool_call_id 对齐某个 AIMessage 工具请求。", "direction": "由工具执行层追加，再回灌给模型。"},
    {"file": "libs/core/langchain_core/messages/utils.py", "symbol": "convert_to_messages / _convert_to_message", "role": "把 PromptValue 或消息表示序列转换为标准消息列表；序列里的单个 str、二元组、dict、BaseMessage 由 _convert_to_message 处理。", "direction": "BaseChatModel._convert_input 处理序列分支时调用它。"},
    {"file": "libs/core/langchain_core/language_models/chat_models.py", "symbol": "BaseChatModel._convert_input", "role": "把裸字符串先变成 StringPromptValue，把消息序列变成 ChatPromptValue；不是直接把裸 str 交给 convert_to_messages。", "direction": "聊天模型 invoke/stream 前的真实输入分流点。"},
]),
r"""
<h2>主流程：字符串 / 列表 / 字典如何进入工具回合</h2>
<p>消息规范化不是装饰步骤，而是系统边界。真实聊天模型入口会先经过 <span class="mono">BaseChatModel._convert_input</span>：裸字符串变成 <span class="mono">StringPromptValue</span>；<span class="mono">PromptValue</span> 原样保留；消息序列才交给 <span class="mono">convert_to_messages</span>。在序列内部，<span class="mono">(\"system\", \"...\")</span>、dict 或已经构造好的 <span class="mono">BaseMessage</span> 元素再由 <span class="mono">_convert_to_message</span> 逐个转成明确消息对象。规范化之后，provider adapter 才能做确定翻译：role 映射到厂商字段，content 映射到文本或多模态块，tool_calls 映射到函数调用格式，metadata 映射到追踪信息。</p>
""",
shell.call_graph([
    ("str / PromptValue / sequence 输入", "BaseChatModel._convert_input 先按顶层类型分流", True),
    ("StringPromptValue / ChatPromptValue", "裸字符串不直接进 convert_to_messages；序列才会继续转换", True),
    ("sequence items", "convert_to_messages 逐个调用 _convert_to_message", True),
    ("message objects", "序列里的 BaseMessage 元素会被保留，tuple/dict/str 元素被转成消息", True),
    ("provider adapter", "翻译 role、content、tool schema 和额外字段", False),
    ("AIMessage/tool_calls", "模型返回内容或请求工具执行", True),
    ("Runnable / Agent", "下游读取同一消息列表继续编排", True),
]),
r"""
<h2>代码走读：简化版消息规范化</h2>
<p>真实源码里要分清两层：聊天模型的 <span class="mono">_convert_input</span> 负责顶层输入分流，消息工具里的 <span class="mono">convert_to_messages</span> 负责把“消息表示的序列”逐项转换。也就是说，裸 <span class="mono">str</span> 会先成为 <span class="mono">StringPromptValue</span>；单个裸 <span class="mono">BaseMessage</span> 不是 <span class="mono">convert_to_messages</span> 的常规入口；序列中的单个元素才会委托给 <span class="mono">_convert_to_message</span>。下面的伪代码保留这条来源准确的阅读路径。</p>
""",
shell.code_walkthrough(
    "libs/core/langchain_core/language_models/chat_models.py + messages/utils.py",
    "BaseChatModel._convert_input / convert_to_messages",
    '''class BaseChatModel:
    def _convert_input(self, input):
        if isinstance(input, PromptValue):
            return input
        if isinstance(input, str):
            return StringPromptValue(text=input)
        if isinstance(input, Sequence):
            return ChatPromptValue(messages=convert_to_messages(input))
        raise ValueError("Invalid input type")

def convert_to_messages(messages):
    if isinstance(messages, PromptValue):
        return messages.to_messages()
    return [_convert_to_message(item) for item in messages]

def _convert_to_message(item):
    if isinstance(item, BaseMessage):
        return item
    if isinstance(item, str):
        return HumanMessage(content=item)
    if isinstance(item, tuple):
        role, content = item
        return message_from_role(role, content)
    if isinstance(item, dict):
        role = item.get("role") or item.get("type")
        return message_from_role(role, item.get("content"), item)
    raise ValueError("unsupported message representation")''',
    "这是教学伪代码：真实实现还会处理 content blocks、message chunk 和更细的校验；重点是顶层 str 由 _convert_input 包成 StringPromptValue，序列元素才走 _convert_to_message。",
),
r"""
<h2>例子追踪：“查订单 123”的一轮工具调用</h2>
<p>下面的 trace 故意把每个中间对象写出来。关键点是：<span class="mono">AIMessage.tool_calls</span> 只是模型提出的意图，不是工具已经执行；真正的执行结果必须成为 <span class="mono">ToolMessage</span>，并且它的 <span class="mono">tool_call_id</span> 要和原始调用 id 对上。没有这个 id，下一轮模型就不知道哪条观察对应哪次请求。</p>
""",
shell.trace_table([
    {"step": "1 用户输入", "input": "查订单 123", "action": "BaseChatModel._convert_input 先把裸字符串包装成 StringPromptValue，生成时再展开成 HumanMessage。", "output": "StringPromptValue(text='查订单 123') → HumanMessage(content='查订单 123')"},
    {"step": "2 模型判断", "input": "HumanMessage + order_lookup schema", "action": "模型决定调用工具，返回带 tool_calls 列表的 AIMessage。", "output": "AIMessage(tool_calls=[{'id':'call_1','name':'lookup_order','args':{'id':'123'}}])"},
    {"step": "3 程序执行", "input": "call_1 / lookup_order / id=123", "action": "你的代码调用真实订单系统，获得状态。", "output": "订单 123 已发往上海"},
    {"step": "4 工具观察", "input": "执行结果 + call_1", "action": "把结果包装为 ToolMessage，绑定 tool_call_id。", "output": "ToolMessage(content='已发往上海', tool_call_id='call_1')"},
    {"step": "5 最终回复", "input": "HumanMessage + AIMessage + ToolMessage", "action": "模型看到工具观察，生成不再含 tool_calls 的最终回答。", "output": "AIMessage(content='订单 123 已发往上海。')"},
]),
r"""
<h2>字段拆解：role、content 与 metadata 不是一回事</h2>
<p><strong>role / type</strong> 是消息在对话里的身份。它告诉模型和适配器这段内容应被当作系统指令、人类输入、AI 回复还是工具观察。很多 provider 的字段名不同，但 LangChain 在上层保留统一语义。不要把 role 当作业务权限，也不要把系统消息当作绝对安全边界；它只是模型上下文里的优先级提示和结构提示。</p>
<p><strong>content</strong> 是消息主要承载的信息。它可以是普通字符串，也可以是更结构化的内容块，例如文本、图片描述或 provider 支持的多模态片段。C 级排错时要看 content 是否在转换中被拼成了错误字符串，是否把历史消息压成一段难以区分说话人的文本，是否把工具结果误放进 AIMessage.content 而不是 ToolMessage。</p>
<p><strong>additional_kwargs</strong> 是给 provider 差异留出的扩展袋。某些厂商返回的原始字段、函数调用片段或特殊参数可能暂时放在这里。它有用，但不应成为业务主状态。业务代码如果长期依赖某个 provider 特有 additional_kwargs，就等于绕过了统一消息契约，未来切换模型时会出现隐性耦合。</p>
<p><strong>tool_calls</strong> 是 <span class="mono">AIMessage</span> 上最容易误读的字段。它表示“模型请求执行某些工具”，不是“工具结果”。每个 tool call 通常包含 name、args、id 等信息。程序读取它、验证它、执行它、生成 ToolMessage。安全边界在这里：模型提出动作，应用决定是否允许执行。</p>
<p><strong>usage_metadata</strong> 记录 token 数、输入输出用量等观测信息。它适合追踪成本、延迟分析和调试，不适合作为业务状态。例如“本轮用了 1000 token”可以写入日志，但不应该决定订单是否已付款。把观测指标混进领域状态，会让回放、重试和审计变得混乱。</p>
<p><strong>message id</strong> 有助于追踪和去重，但不等于工具调用 id。消息 id 标识一条消息，tool_call_id 标识一次工具请求与一次工具观察之间的对应关系。多工具并行时尤其重要：两个工具都返回“成功”，如果没有 id，模型和 trace 都无法可靠判断哪个成功对应哪个请求。</p>

<h2>为什么 ToolMessage.tool_call_id 是硬边界</h2>
<p>工具回合看似只是把结果追加进历史，实际是一个小型事务：模型发出 call id，执行器按该 id 执行对应工具，观察结果带着同一 id 回来。这个 id 让系统可以处理并行、失败、重试和部分结果。如果漏掉 id，简单 demo 可能仍能工作，因为只有一个工具；生产中一旦模型同时请求天气、库存和价格，结果顺序、错误重试和审计记录都会失去锚点。</p>
<p>另一个常见问题是把工具执行结果直接拼进下一条 HumanMessage，例如“工具返回：……”。这样模型也许能读懂，但框架、tracer 和 provider adapter 都看不到结构化的工具观察。正确做法是保留 ToolMessage，让数据契约告诉系统“这不是用户又说了一句话，而是某个工具调用的结果”。结构一旦丢失，下游就只能靠猜。</p>

<h2>消息列表是对话状态，不是聊天记录文本</h2>
<p>很多应用一开始把 history 存成一段长字符串：“用户：…… AI：……”。这种做法在演示中方便，但会损失角色、工具 id、usage、metadata、内容块类型和消息级追踪。LangChain 的消息列表让历史保持结构化：每一项都有身份、内容和可选元数据。模型适配器可以据此生成最接近 provider 要求的 payload，Agent 循环也能可靠寻找最近一次工具请求。</p>
<p>结构化消息还有利于裁剪上下文。你可以按消息边界删除最老的人机回合，可以保留系统消息和最后一条 ToolMessage，可以对图片块做单独处理。如果历史只是一段字符串，裁剪就容易切断语义，甚至把工具结果和用户输入混成不可区分的文本。</p>

<h2>从源码阅读到业务设计</h2>
<p>读 <span class="mono">BaseMessage</span> 时，重点不是继承语法，而是字段边界：哪些字段是跨 provider 的稳定契约，哪些字段是追踪或扩展，哪些字段只在工具循环中有意义。读 <span class="mono">HumanMessage</span> 和 <span class="mono">AIMessage</span> 时，重点是方向：前者通常进入模型，后者通常从模型出来。读 <span class="mono">ToolMessage</span> 时，重点是它不代表“工具定义”，而代表“工具执行后的观察”。</p>
<p>业务层可以借鉴这套边界。你的领域对象不应该直接等同于消息对象；订单、用户、权限属于业务模型，消息只是把某次对话中的信息送进或送出模型。把业务状态放在数据库或图状态里，把对话证据放在消息列表里，把观测指标放在 metadata / trace 里，三者分清，系统才容易复盘。</p>
<p>调试时建议打印“消息摘要”而不是完整敏感内容：类型、前几十个字符、tool_call_id、tool_calls 名称、usage。这样既能看到结构，又能降低泄露风险。消息是可观测边界，但不是秘密保险箱；真实用户输入、工具结果和系统提示都可能包含敏感信息，日志策略必须谨慎。</p>


<h2>C 级排错清单：消息层先问什么</h2>
<p>当一个对话应用表现异常时，先不要急着改 prompt，也不要马上换模型。第一步应检查消息列表本身：第一条是不是系统消息，用户输入是不是 HumanMessage，模型上一轮回复是不是 AIMessage，工具观察是不是 ToolMessage，顺序是否符合真实发生顺序。很多问题看起来像“模型不听话”，实际是消息身份错了，模型把工具结果当成用户追问，或把用户文本拼进了系统规则。</p>
<p>第二步检查工具调用关系。打印每个 AIMessage 的 tool_calls，列出 id、name、args，再打印每个 ToolMessage 的 tool_call_id。每个工具观察都应该能找到对应请求；每个需要执行的请求都应该有执行记录或明确错误。若同一个 id 出现两次，要判断是重试、重复追加还是状态恢复 bug。若 ToolMessage 没有 id，说明执行层和消息层之间的事务边界已经断开。</p>
<p>第三步检查 metadata 的用途。response_metadata 和 usage_metadata 很适合帮助你知道 provider 返回了什么、token 用了多少、finish_reason 是什么，但它们不是业务事实。不要因为 metadata 里有某个 provider 原始字段，就在业务层长期依赖它；更不要把 token 数、模型名或 run id 当作用户状态。追踪信息应该进入日志、指标和 trace，业务状态应该进入数据库、图状态或领域对象。</p>
<p>第四步检查消息裁剪。上下文过长时，很多应用会删除历史。如果裁剪算法只按字符切字符串，就可能留下半个工具结果或删掉 tool_call 对应的 AIMessage。结构化消息裁剪应按回合处理：系统消息通常保留；成对的 AIMessage tool_calls 与 ToolMessage 尽量一起保留或一起删除；最后一轮用户问题必须保留。否则模型会看到没有来由的工具观察，回答自然混乱。</p>
<p>第五步检查序列化。消息常被存进数据库或队列，再恢复给下一次调用。恢复时要保留 type、content、additional_kwargs、tool_calls、tool_call_id、id 和必要 metadata。若只保存 content，恢复后所有消息都变成普通文本，Agent 轨迹和工具回合就丢了。生产系统应为消息序列化写小测试，确保存取前后消息类型和关键字段一致。</p>
<h2>设计建议：把消息当作边界对象</h2>
<p>在应用架构里，消息对象应位于模型交互边界，而不是到处替代业务对象。订单状态不要长期存成 AIMessage，用户权限不要藏在 HumanMessage，支付结果不要只存在 ToolMessage。消息记录“模型在这次运行中看到了什么和说了什么”，领域对象记录“系统真实状态是什么”。这两层可以互相引用，但不能互相替代。</p>
<p>如果团队多人协作，可以约定消息调试格式：每条消息打印序号、类型、简短内容、tool_calls 名称、tool_call_id、usage 摘要，敏感内容做脱敏。这样产品、后端和模型工程师讨论同一个问题时，不会只盯最终回答，而能看到标准化对话状态。C 级工程能力很大一部分就是把“模型怎么又乱了”改写成“第 4 条 ToolMessage 的 id 没有匹配第 3 条 AIMessage 的请求”。</p>
<p>消息层也影响测试策略。你可以不用真实 provider，直接构造 HumanMessage、AIMessage 和 ToolMessage，测试自己的工具执行器、裁剪器、序列化器和 Agent 路由。只要消息契约稳定，这些测试就不依赖网络和模型随机性。等消息边界测试可靠后，再用少量集成测试验证 provider adapter 是否把真实响应映射到同样结构。</p>
<p>最后记住一个判断：凡是需要模型理解的内容，应以正确消息身份进入上下文；凡是需要程序确定执行的事实，应以结构化字段进入业务状态；凡是需要人排查的证据，应进入 trace。三类数据都可能出现在一次运行里，但责任不同。分清责任，消息系统才不会变成万能垃圾桶。</p>


<h2>课堂复盘：用消息语言描述一次运行</h2>
<p>学完本课后，可以尝试不用“模型回复了”“工具查了”这种模糊说法，而改用消息语言复盘：第 1 条 HumanMessage 承载用户问题；第 2 条 AIMessage 没有最终答案，而是包含一个带 id 的 tool call；执行器读取这个请求并调用业务函数；第 3 条 ToolMessage 用同一 id 记录观察；第 4 条 AIMessage 才是最终自然语言回复。这样的描述把一次运行拆成证据链，任何人都能继续检查。</p>
<p>消息语言还帮助你做代码审查。看到函数接收 <span class="mono">list[dict]</span> 时，问它什么时候转成 BaseMessage；看到函数返回字符串时，问下游是否需要 AIMessage metadata；看到工具结果被拼进 prompt 时，问为什么不是 ToolMessage；看到 usage 被写入业务表时，问它是不是只应进追踪系统。小问题在 demo 中不明显，在多模型、多工具、多轮对话中会迅速放大。</p>
<p>因此，本课不是让你背字段，而是训练一套工程表达：消息是模型上下文的结构化证据，工具 id 是工具事务的连接点，metadata 是观测材料，content 是模型可读主体。只要这几个名词用准，后续学习 prompt、tools、Agent 和 streaming 都会更顺。</p>

<h2>延伸练习：消息契约的最小验收标准</h2>
<p>给消息层写验收标准时，可以要求任何进入模型的输入都先通过一个检查函数：列表不能为空；每项都有明确类型；工具观察必须匹配已有工具请求；系统消息不能由用户文本直接生成；序列化再反序列化后关键字段不丢失。这个检查函数不需要理解业务，只保护消息形状。它像类型系统的补充，让模型调用前的错误更早暴露。</p>
<p>在团队协作中，还可以约定“禁止在业务层拼接历史字符串”。如果确实需要展示聊天记录，可以从消息列表渲染字符串；但存储和调用仍保留结构。渲染是视图，消息是数据。把视图反过来当数据源，是很多多轮对话系统后期难以维护的根源。</p>

<h2>最后检查：把概念落到一次真实调用</h2>
<p>完成本课后，请把概念重新放回一次真实调用中验证：输入从哪里来，经过哪个对象标准化，运行时配置如何传播，输出由谁解释，错误在哪里被看见，哪些信息进入 trace，哪些信息进入业务状态。只要能沿着这条线讲清楚，说明你掌握的不是 API 片段，而是可维护的系统边界。</p>
<p>这也是 C 级课程反复强调的学习方法：每个抽象都要回答“它统一什么、它不负责什么、它失败时看什么证据”。抽象不是为了隐藏一切，而是为了让变化集中、证据清楚、责任可定位。后续课程继续读源码时，请始终用这三个问题检查自己的理解。</p>
<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("dict 和 BaseMessage 对象完全等价，随便混用。", "dict 是输入便利格式；进入模型前应规范化为明确消息对象，避免 role/type/content 缺失或拼错。"),
    ("AIMessage.tool_calls 就是工具执行结果。", "tool_calls 只是模型意图；执行结果必须由你的程序产生并写入 ToolMessage。"),
    ("ToolMessage 不写 tool_call_id 也没关系。", "只有一个工具的 demo 可能侥幸工作；多工具、并行、重试和审计都依赖匹配 id。"),
    ("usage_metadata 可以当业务状态用。", "token 用量是追踪和计费信息，不应决定订单、权限或用户流程。"),
    ("把历史拼成一个字符串更简单也一样。", "字符串历史会丢失角色、工具关系、内容块和消息级追踪，长期维护成本更高。"),
]),
r"""
<h2>小实验：检查一次假工具回合前后的消息列表</h2>
""",
shell.lab_card("手动构造一轮消息状态", [
    "创建 messages = [HumanMessage(content='查订单 123')]，打印每条消息的 type 和 content。",
    "手写一个 AIMessage，令 tool_calls 包含 id='call_1'、name='lookup_order'、args={'id':'123'}。",
    "模拟工具返回，把结果包装为 ToolMessage(content='已发往上海', tool_call_id='call_1')。",
    "再次打印消息列表，确认 AIMessage.tool_calls 和 ToolMessage.tool_call_id 是两条不同消息上的字段。",
    "把 tool_call_id 改错，观察你的检查函数如何发现“工具观察无法匹配请求”。"],),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>消息是 LangChain 的标准对话数据契约，连接用户输入、模型输出、工具观察和下游 Runnable。</li>
    <li><span class="mono">role/content</span> 表达对话身份和主体内容；<span class="mono">additional_kwargs</span> 与 <span class="mono">usage_metadata</span> 更偏扩展和观测。</li>
    <li><span class="mono">AIMessage.tool_calls</span> 是模型请求，<span class="mono">ToolMessage</span> 是程序执行后的观察，二者通过 <span class="mono">tool_call_id</span> 对齐。</li>
    <li>结构化消息列表比聊天记录字符串更适合裁剪、追踪、工具循环和 provider 切换。</li>
  </ul>
</div>
""",
shell.version_note("本课以 LangChain v1 时代的 core 消息契约为锚点：字段名和 provider 细节会演进，但文件 + 符号名所表达的边界——BaseMessage 家族、convert_to_messages、AIMessage.tool_calls 与 ToolMessage.tool_call_id——是阅读新版源码时最稳定的地图。"),
])


LESSON_07_CHAT_MODELS = "".join([
r"""
<p class="lead">聊天模型把不同厂商的对话式 API 包装在 <span class="mono">BaseChatModel</span> 后面，让上层用同一套 <span class="mono">invoke</span>、<span class="mono">stream</span>、<span class="mono">batch</span>、异步变体和工具绑定接口工作。你选择 <span class="mono">openai:gpt-5.1</span> 或 <span class="mono">anthropic:claude-sonnet-4-5</span> 时，业务消息和下游解析代码不应该跟着大改；变化应集中在模型构造和 provider wrapper。</p>

<div class="card analogy">
  <div class="tag">☎️ 生活类比 · 多运营商电话交换机</div>
  聊天模型像公司电话交换机。员工只拨统一内线号码，说同一种通话礼仪；交换机根据号码前缀选择移动、电信或海外线路，把内部格式翻译成运营商协议，再把对方回音转成公司熟悉的记录。你不应该在每个业务部门都直接接运营商裸线，否则换线路时整栋楼都要改线。
</div>

<h2>本课地图：模型对象是 Runnable，不是厂商客户端本身</h2>
<p>很多初学者把 <span class="mono">ChatOpenAI</span> 当作 OpenAI SDK 客户端，把 <span class="mono">ChatAnthropic</span> 当作 Anthropic SDK 客户端。更准确的说法是：它们是 LangChain 的聊天模型 wrapper，实现 <span class="mono">BaseChatModel</span> 和 Runnable 协议，内部才调用厂商 SDK。这个区别决定了返回值是 <span class="mono">AIMessage</span>，配置通过 <span class="mono">RunnableConfig</span> 传播，工具绑定通过统一 schema 进入 provider。</p>
""",
shell.lesson_map("聊天模型的稳定路径", [
    ("模型字符串", "用户用 provider:model 或显式类选择底层模型", "before"),
    ("工厂初始化", "init_chat_model 根据前缀查找 partner 包并构造 wrapper", "now"),
    ("统一调用", "BaseChatModel 暴露 invoke/stream/batch/async 等 Runnable 行为", "now"),
    ("厂商请求", "ChatOpenAI、ChatAnthropic 等 wrapper 翻译消息和参数", "source"),
    ("统一输出", "上层拿到 AIMessage、chunks、metadata 和 tool_calls", "after"),
]),
r"""
<h2>源码入口：文件 + 符号名</h2>
<p>读模型源码时建议按“高层入口、抽象基类、配置传播、具体厂商”四层走。不要从某个 provider 的 HTTP payload 一头扎进去，否则容易把通用契约和厂商细节混在一起。</p>
""",
shell.source_map([
    {"file": "libs/langchain_v1/langchain/chat_models/base.py", "symbol": "init_chat_model", "role": "用户友好的模型工厂，解析 provider:model 字符串并实例化对应聊天模型。", "direction": "从应用配置进入 partner wrapper。"},
    {"file": "libs/core/langchain_core/language_models/chat_models.py", "symbol": "BaseChatModel", "role": "聊天模型抽象基类，定义输入转换、invoke、stream、batch、工具绑定和结构化输出等公共行为。", "direction": "具体 provider wrapper 继承并实现底层生成。"},
    {"file": "libs/core/langchain_core/runnables/config.py", "symbol": "RunnableConfig", "role": "携带 tags、metadata、callbacks、run_name、max_concurrency 等运行配置。", "direction": "从上层 Runnable 调用向模型和子调用传播。"},
    {"file": "libs/partners/openai/langchain_openai/chat_models/base.py", "symbol": "ChatOpenAI", "role": "OpenAI 聊天模型 wrapper，负责参数映射、消息转换、工具调用和响应解析。", "direction": "实现 BaseChatModel 并调用 OpenAI SDK。"},
    {"file": "libs/partners/anthropic/langchain_anthropic/chat_models.py", "symbol": "ChatAnthropic", "role": "Anthropic 聊天模型 wrapper，处理 Anthropic 消息格式、流式 chunk 和工具调用差异。", "direction": "实现 BaseChatModel 并调用 Anthropic SDK。"},
]),
r"""
<h2>状态流：从模型字符串到 AIMessage</h2>
<p>下面的状态流展示为什么“换模型只改配置”在理想情况下可行。上层构造消息列表，模型工厂选 wrapper，wrapper 负责把标准消息变成 provider 请求，响应再被包装回 <span class="mono">AIMessage</span>。如果你把 provider 原始响应穿透到业务层，这条稳定路径就会被打破。</p>
""",
shell.state_flow([
    ("模型字符串", "例如 openai:gpt-5.1 或 anthropic:claude-sonnet-4-5，前缀决定 provider，后半段决定模型名。", "provider:model"),
    ("provider 包查找", "init_chat_model 解析前缀，检查可选依赖，找到 ChatOpenAI 或 ChatAnthropic。", "init_chat_model(...)"),
    ("wrapper 初始化", "统一参数和 provider-specific kwargs 被保存到模型对象。", "BaseChatModel subclass"),
    ("消息转换", "invoke 前用 _convert_input 得到 PromptValue；消息序列分支才规范化为 BaseMessage 列表。", "convert input"),
    ("provider 请求", "wrapper 翻译 role/content/tools/config，调用厂商 SDK。", "SDK request"),
    ("AIMessage", "响应被解析为 content、tool_calls、response_metadata、usage_metadata。", "AIMessage"),
]),
r"""
<h2>代码走读：简化版 init_chat_model + invoke</h2>
<p>真实代码会处理更多 provider、可选依赖、声明式配置、回调和缓存。这里保留两条关键路径：构造时把 provider 字符串映射到 wrapper；调用时先把输入转成 <span class="mono">PromptValue</span>，再从 <span class="mono">RunnableConfig</span> 中取 callbacks、tags、metadata、run_name、run_id 传给 <span class="mono">generate_prompt</span>，最后返回标准 <span class="mono">AIMessage</span>。</p>
""",
shell.code_walkthrough(
    "libs/langchain_v1/langchain/chat_models/base.py + libs/core/langchain_core/language_models/chat_models.py",
    "init_chat_model / BaseChatModel.invoke",
    '''def init_chat_model(model, **kwargs):
    provider, model_name = parse_provider(model)
    if provider == "openai":
        return ChatOpenAI(model=model_name, **kwargs)
    if provider == "anthropic":
        return ChatAnthropic(model=model_name, **kwargs)
    raise ValueError("unknown chat model provider")

class BaseChatModel:
    def invoke(self, input, config=None, **kwargs):
        prompt_value = self._convert_input(input)
        config = ensure_config(config)
        result = self.generate_prompt(
            [prompt_value],
            callbacks=config.get("callbacks"),
            tags=config.get("tags"),
            metadata=config.get("metadata"),
            run_name=config.get("run_name"),
            run_id=config.get("run_id"),
            **kwargs,
        )
        return result.generations[0][0].message''',
    "这是教学伪代码：真实 BaseChatModel 还会经过 callback manager、缓存、批量生成、stream 适配和错误处理；这里强调 invoke 传给 generate_prompt 的是 PromptValue 列表和展开后的运行配置。",
),
r"""
<h2>切换 provider 的追踪：业务消息不变</h2>
<p>假设你的客服链只依赖消息和 <span class="mono">AIMessage</span>。当配置从 OpenAI 切到 Anthropic 时，变化应该集中在初始化层；prompt、工具 schema、输出解析器和下游 Runnable 仍面对同一种消息契约。下面的 trace 展示稳定部分和变化部分。</p>
""",
shell.trace_table([
    {"step": "1 初始配置", "input": "openai:gpt-5.1", "action": "init_chat_model 选择 ChatOpenAI。", "output": "model 是 BaseChatModel wrapper"},
    {"step": "2 调用链", "input": "[SystemMessage, HumanMessage]", "action": "业务代码调用 model.invoke(messages)。", "output": "AIMessage(content=..., response_metadata=...)"},
    {"step": "3 切换配置", "input": "anthropic:claude-sonnet-4-5", "action": "同一工厂选择 ChatAnthropic。", "output": "另一个 BaseChatModel wrapper"},
    {"step": "4 下游不变", "input": "相同 messages / parser / Runnable", "action": "调用代码仍读取 AIMessage.content 或 tool_calls。", "output": "业务层无需处理 Anthropic 原始响应"},
    {"step": "5 差异隔离", "input": "provider-specific kwargs", "action": "只在模型构造处处理特殊参数和能力差异。", "output": "爆炸半径被限制在适配层"},
]),
r"""
<h2>invoke、stream、batch 与异步变体</h2>
<p><span class="mono">invoke</span> 是最容易理解的入口：给一个输入，返回一个完整 <span class="mono">AIMessage</span>。输入可以是字符串、消息列表、PromptValue 等，模型会做转换。不要期待返回裸字符串；如果只想要字符串，后面接 <span class="mono">StrOutputParser</span>。保留 AIMessage 的好处是你能读到 tool_calls、usage_metadata、response_metadata 和 id。</p>
<p><span class="mono">stream</span> 返回逐步产生的 chunk，适合 UI 逐字显示、实时日志或早期反馈。它不保证总耗时更短，只是让第一个 token 更早到达。chunk 不是最终消息，通常需要框架或你自己的逻辑合并。对于工具调用、结构化输出和多模态块，流式 chunk 的边界可能比普通文本复杂。</p>
<p><span class="mono">batch</span> 接收多个输入并返回多个结果，重点是批量调用同一个 Runnable。它不是“让模型并行执行工具”的意思；工具并行属于 Agent / tool execution 层。batch 是否真正并发、并发度多少、错误如何返回，受 RunnableConfig 的 <span class="mono">max_concurrency</span> 和具体实现影响。</p>
<p>异步变体如 <span class="mono">ainvoke</span>、<span class="mono">astream</span>、<span class="mono">abatch</span> 让模型调用与 async 应用配合。C 级使用时要注意不要在同步 Web 框架里硬塞事件循环，也不要在 async 服务里调用阻塞同步接口。选择同步还是异步，应由你的运行时决定，而不是由模型名字决定。</p>

<h2>bind_tools：把工具 schema 交给模型，而不是执行工具</h2>
<p><span class="mono">bind_tools</span> 返回一个绑定了工具 schema 的模型 Runnable。它把工具名称、描述、参数结构翻译成 provider 能理解的 tool/function calling 格式，让模型可以在 <span class="mono">AIMessage.tool_calls</span> 中提出请求。但它不执行工具，也不保证模型一定调用工具。执行仍然发生在 Agent 循环、LangGraph 节点或你的业务代码里。</p>
<p>这条边界能避免很多误会。模型 wrapper 的职责是“让 provider 知道有哪些工具可选，并把返回的工具意图解析出来”；工具执行器的职责是“验证参数、检查权限、调用真实代码、生成 ToolMessage”。把这两件事混在一起，会让安全审计和错误处理变得模糊。</p>

<h2>模型 kwargs、retry、fallback 与配置传播</h2>
<p>模型构造参数分两类：通用参数和 provider-specific 参数。通用参数如 temperature、timeout、max_tokens 更容易跨 provider；特殊参数如某厂商的 reasoning、response_format、top_k 或 cache_control 可能只对一个 wrapper 有意义。可移植应用应把特殊参数集中在模型创建处，避免在业务链各处散落。</p>
<p>重试和 fallback 通常通过 Runnable 能力组合，而不是在每个业务函数里手写。你可以把模型包上 retry 策略，或在一个 provider 失败时 fallback 到另一个 provider。但 fallback 不是免费午餐：不同模型支持的工具、上下文长度、结构化输出和安全策略可能不同。可靠 fallback 需要用相同消息契约、相近能力集合和明确的失败条件。</p>
<p><span class="mono">RunnableConfig</span> 承载 tags、metadata、callbacks、run_name、max_concurrency 等运行信息。它不是 prompt 内容，也不是模型参数的垃圾桶。tags 和 metadata 用于追踪与筛选；callbacks 用于观察事件；max_concurrency 影响并发调度。把 config 当成业务输入会导致调用链难以理解。</p>

<h2>模型对象与 provider client 的边界</h2>
<p>如果你需要使用厂商 SDK 的极端新功能，而 wrapper 尚未支持，可以在一小块 adapter 代码里直接调用 SDK。但要知道这会绕过 LangChain 的统一消息、回调、trace、重试和输出类型。更稳的策略是先判断是否能通过 wrapper 的 provider-specific kwargs 暴露；不能时再封装自定义 Runnable，让裸 SDK 只出现在边界层。</p>
<p>反过来，不要为了“更底层可控”在应用各处直接创建 provider client。这样会让 API key、timeout、日志、重试、消息转换和错误处理重复出现。聊天模型 wrapper 的价值，就是把这些胶水收口，并让它们服从 Runnable 组合。</p>

<h2>从 C 级视角调试模型调用</h2>
<p>当模型调用失败时，先定位失败发生在哪一层。构造阶段报错，多半是 provider 前缀、依赖安装、认证或参数名问题；调用前报错，多半是输入消息无法转换；provider 返回错误，可能是模型名、权限、上下文长度或工具 schema 不被支持；返回后下游崩溃，可能是把 AIMessage 当字符串、把 tool_calls 当文本或假设 metadata 字段跨 provider 一致。</p>
<p>调试输出建议包含模型类名、模型名、消息类型摘要、返回消息类型、usage 和 response metadata。不要只打印最终内容，因为最终内容掩盖了最关键的边界信息。一次好的 trace 应能回答：用了哪个 wrapper？输入是什么消息？provider 返回什么结构？上层读取了哪个字段？</p>

<h2>C 级排错清单：模型层先定位哪一段</h2>
<p>聊天模型故障通常分为构造失败、输入失败、provider 失败、解析失败和下游误用。构造失败要看模型字符串、可选依赖、环境变量、provider 前缀和 kwargs；输入失败要看传入的是字符串、PromptValue 还是消息列表，以及是否有无法转换的 dict；provider 失败要看 HTTP 状态、权限、模型名、上下文长度和工具能力；解析失败要看 AIMessage 的真实内容；下游误用则常见于把 AIMessage 当字符串。</p>
<p>如果同一段链在 fake model 下正常、真实 provider 下失败，问题多半在 provider wrapper、认证、参数或模型能力。如果真实 provider 返回正常 AIMessage，但 parser 失败，问题在输出契约或 prompt，而不是模型构造。如果 OpenAI 能调用工具、Anthropic 切换后不能，先确认该 wrapper 是否支持同样工具 schema、参数名是否被翻译、特殊 kwargs 是否仍适用。不要把 provider 能力差异误判为 LangChain 抽象失效。</p>
<p>排查流式问题时也要分层。stream 没有 token 可能是 provider 不支持、模型 wrapper 回退、网络缓冲、callback 阻塞或上游 prompt 还没完成；batch 慢可能是 max_concurrency 太低、provider 限速或你误以为 batch 会并行工具；async 卡住可能是同步函数阻塞事件循环。每个症状都要落到接口语义，而不是笼统说“模型慢”。</p>
<h2>可移植模型配置的设计</h2>
<p>生产项目最好把模型选择集中在一个工厂或配置层。业务链只接收 BaseChatModel 或 Runnable，不直接导入 ChatOpenAI、ChatAnthropic。这样 provider 切换时，你只修改配置层和少量能力适配。若某个业务必须使用 provider 专有参数，应在工厂里明确命名，例如 create_reasoning_model 或 create_fast_chat_model，而不是让每个调用点传一堆神秘 kwargs。</p>
<p>配置层还应记录模型能力：是否支持工具调用、是否支持 JSON schema、最大上下文、是否支持 streaming、是否允许图像输入、成本等级和降级模型。这样 fallback 不是盲目替换字符串，而是从能力相近的候选中选择。C 级工程关注的不是“能不能跑一次”，而是“当主模型失败、限速或升级时，系统如何保持可解释”。</p>
<p>重试策略也要谨慎。网络超时、429 限速和 5xx 可以重试；参数错误、权限错误、上下文过长通常不应原样重试。对流式调用，已经向用户输出部分内容后再重试会造成重复文本，需要 UI 和运行状态配合。对工具调用，重试模型可能生成不同 tool_call_id，执行器要避免重复副作用。模型层的 retry 不是简单装饰器，而是和消息、工具、UI、成本共同设计。</p>
<h2>测试聊天模型边界</h2>
<p>大多数模型层单元测试不应依赖真实 provider。可以使用 fake chat model 固定返回 AIMessage，验证 prompt、parser、工具执行器和下游字段读取。集成测试再少量覆盖真实 wrapper：构造成功、简单 invoke 返回 AIMessage、metadata 可打印、工具 schema 能被接受。这样既控制成本，又能在 provider 变化时快速发现适配问题。</p>
<p>测试还应覆盖“切换模型不改下游”。给同一组消息分别传入两个 fake wrapper，断言下游只读取 AIMessage.content、tool_calls 或标准 metadata，不读取 provider 原始字段。若测试发现业务代码需要 response_metadata 里的私有字段才能工作，说明抽象边界已经泄漏，应把这段逻辑移到 provider adapter 或显式能力分支。</p>
<p>日志方面，建议每次模型调用记录模型类名、模型名、run id、输入消息数量、是否绑定工具、输出类型、finish_reason、token 用量和耗时。不要默认记录完整 prompt；需要排查时再按权限和脱敏策略打开。一个成熟的模型调用层应该既能保护隐私，又能让工程师快速判断失败发生在哪个边界。</p>
<p>最后，把模型 wrapper 看作“可替换但不完全等价”的组件。LangChain 统一调用形状，不抹平所有能力差异。优秀设计会最大化通用路径，最小化专有路径，并把专有路径命名、集中、测试。这样你既能享受抽象带来的迁移能力，也不会对 provider 差异抱有不现实期待。</p>


<h2>课堂复盘：把模型调用写成可替换端口</h2>
<p>一个成熟项目通常不会让业务代码到处写 <span class="mono">ChatOpenAI(...)</span>。更好的形状是：配置层决定 provider 和模型名，基础设施层构造 BaseChatModel，应用层只依赖 Runnable 行为。这样订单客服、知识库问答和总结任务都可以接收“一个聊天模型端口”，而不是硬绑定某个厂商。端口不是为了抽象而抽象，而是为了把认证、参数、重试、fallback 和观测集中管理。</p>
<p>当你审查模型调用代码时，可以问四个问题：第一，下游是否只依赖 AIMessage 的标准字段；第二，provider-specific kwargs 是否集中在构造层；第三，RunnableConfig 的 tags、metadata、callbacks 是否能传到模型；第四，测试是否能用 fake model 替代真实 provider。如果四个问题都能回答，说明模型边界比较健康。</p>
<p>模型切换也要有预期管理。LangChain 统一接口，但不同模型的推理风格、工具支持、上下文长度和结构化输出能力仍可能不同。所谓稳定不是“输出永远一样”，而是“变化发生在明确边界，可观测、可测试、可回滚”。这就是 BaseChatModel 对应用架构的价值。</p>

<h2>延伸练习：为模型工厂写一份能力表</h2>
<p>可以为每个可选模型维护一份小能力表：provider、模型名、是否支持工具、是否支持结构化输出、是否支持 streaming、上下文长度、默认 timeout、成本等级、推荐用途和 fallback 目标。业务代码不直接判断字符串，而是询问能力。这样新增模型时，你会被迫思考它能不能替代当前模型，而不是只看名字是否更强。</p>
<p>能力表还能帮助测试。针对支持工具的模型跑工具 schema 冒烟测试，针对支持 streaming 的模型跑 chunk 合并测试，针对结构化输出模型跑 parser 测试。不同能力对应不同测试，而不是所有模型都跑同一套模糊端到端。模型抽象越统一，能力差异越需要显式记录。</p>
<p>最后，把模型调用成本也纳入设计。usage_metadata 可以进入指标系统，按功能、用户组和模型版本统计。成本异常常常提示 prompt 过长、history 裁剪失败或重试过多。模型 wrapper 给你统一 metadata，应用要把它转化为运维信号，而不是只在调试时看一眼。</p>

<h2>最后检查：把概念落到一次真实调用</h2>
<p>完成本课后，请把概念重新放回一次真实调用中验证：输入从哪里来，经过哪个对象标准化，运行时配置如何传播，输出由谁解释，错误在哪里被看见，哪些信息进入 trace，哪些信息进入业务状态。只要能沿着这条线讲清楚，说明你掌握的不是 API 片段，而是可维护的系统边界。</p>
<p>这也是 C 级课程反复强调的学习方法：每个抽象都要回答“它统一什么、它不负责什么、它失败时看什么证据”。抽象不是为了隐藏一切，而是为了让变化集中、证据清楚、责任可定位。后续课程继续读源码时，请始终用这三个问题检查自己的理解。</p>

<h2>模型层补充提醒</h2>
<p>如果一个模型包装器让你必须在业务层到处判断 provider，说明抽象边界已经变薄。应把差异收回构造层、适配层或能力表，让业务链继续面对消息、Runnable 和 AIMessage。</p>
<p>模型边界越集中，升级越安全，排错越直接。</p>
<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("ChatOpenAI 就是 OpenAI SDK 客户端。", "它是实现 BaseChatModel/Runnable 的 LangChain wrapper，内部才调用厂商 SDK。"),
    ("invoke 返回字符串。", "聊天模型 invoke 返回 AIMessage；要字符串可接 StrOutputParser 或读取 content。"),
    ("batch 等于让模型自动并行调用工具。", "batch 是批量处理多个输入；工具并行属于工具执行或 Agent 编排层。"),
    ("provider-specific kwargs 可以到处传。", "特殊参数应集中在模型初始化边界，否则 provider 切换会污染业务层。"),
    ("fallback 只要换另一个模型名就安全。", "fallback 需要能力、工具 schema、输出契约和错误条件都可兼容。"),
]),
r"""
<h2>小实验：用假模型观察类名与 metadata</h2>
""",
shell.lab_card("确定性模型的模型边界", [
    "使用 FakeListChatModel 或项目已有 deterministic fake model，构造一个固定返回 AIMessage 的模型。",
    "打印 model.__class__.__name__，确认你拿到的是 LangChain 模型 wrapper，而不是 provider 原始 client。",
    "调用 invoke([HumanMessage(content='ping')])，打印 type(result)、result.content、result.response_metadata。",
    "把下游改成读取 result.content，再接 StrOutputParser 对比两种写法的边界差异。",
    "如果有两个 fake/provider wrapper，切换构造处，确认消息输入和下游读取代码保持不变。"],),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">BaseChatModel</span> 把 provider API 包成 Runnable，统一 invoke、stream、batch、async 和 config 传播。</li>
    <li><span class="mono">init_chat_model</span> 是配置入口；<span class="mono">ChatOpenAI</span>、<span class="mono">ChatAnthropic</span> 是具体厂商 wrapper。</li>
    <li>聊天模型返回 <span class="mono">AIMessage</span>，不是裸字符串；工具绑定产生工具意图，不执行真实工具。</li>
    <li>通用能力写在消息和 Runnable 契约上，provider-specific 参数隔离在初始化边界。</li>
  </ul>
</div>
""",
shell.version_note("本课以 LangChain v1 的 init_chat_model、BaseChatModel 和 partner wrapper 分层为锚点。不同版本的模型名、可选依赖和 provider 参数会变化，但“高层工厂 → BaseChatModel → partner wrapper → AIMessage”的阅读路径保持稳定。"),
])


LESSON_08_TOOLS = "".join([
r"""
<p class="lead">工具把模型的“我想做某件事”连接到真实代码执行。LangChain 的 Tool 抽象不会让模型直接拥有数据库、网络或文件系统权限；它只是把 Python 函数、参数 schema、名称和描述变成模型可读的能力说明，再把模型返回的 <span class="mono">AIMessage.tool_calls</span> 交给程序执行，最后用 <span class="mono">ToolMessage</span> 把观察结果回灌。</p>

<div class="card analogy">
  <div class="tag">🧰 生活类比 · 前台工单系统</div>
  模型像前台客服，可以填写“查订单”“查天气”“创建退款”这些工单，但不能自己冲进仓库拿货。工具 schema 像工单表格，docstring 像填写说明，type annotations 像字段类型，tool_call_id 像工单号。真正去仓库、查系统、执行退款的是后台程序；回执必须带工单号，前台才能知道哪张工单完成了。
</div>

<h2>本课地图：schema 是承诺，执行是边界</h2>
<p>工具学习最重要的分层是：函数先被转换成工具对象和参数 schema；模型绑定工具后只看到名称、描述和参数结构；模型返回 tool_calls 表示“请求执行”；程序验证与执行；执行结果作为 ToolMessage 回到消息列表。只要记住“schema 不是执行”，很多安全和调试问题都会清楚。</p>
""",
shell.lesson_map("工具调用的五段式", [
    ("Python 函数", "业务代码定义纯函数或受控副作用函数", "before"),
    ("工具 schema", "@tool / BaseTool 提取名称、描述、参数结构", "now"),
    ("绑定模型", "bind_tools 或 create_agent 把 schema 暴露给模型", "now"),
    ("模型意图", "AIMessage.tool_calls 给出 name、args、id", "source"),
    ("执行观察", "程序执行工具并生成 ToolMessage 回灌", "after"),
]),
r"""
<h2>源码入口：文件 + 符号名</h2>
<p>读工具源码时要把“定义工具”“转换 schema”“Agent 执行”“工具消息”分开。下面的入口覆盖了从装饰器到执行回执的主路径，仍然只引用文件 + 符号名，不绑定易漂移的行号。</p>
""",
shell.source_map([
    {"file": "libs/core/langchain_core/tools/convert.py", "symbol": "tool", "role": "把普通函数或 Runnable 转换为 Tool / StructuredTool，并读取名称、docstring 和参数 schema。", "direction": "用户函数进入工具系统的便捷入口。"},
    {"file": "libs/core/langchain_core/tools/base.py", "symbol": "BaseTool", "role": "工具抽象基类，定义 name、description、args_schema、invoke、run、异常处理等行为。", "direction": "具体工具实现和装饰器产物遵守它。"},
    {"file": "libs/core/langchain_core/utils/function_calling.py", "symbol": "convert_to_openai_tool", "role": "把 LangChain 工具或 schema 转为 OpenAI 风格 tool/function calling 描述。", "direction": "provider adapter 生成工具 payload 时使用。"},
    {"file": "libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "把模型、工具和中间件组装成可执行 Agent 循环。", "direction": "高层 API 负责工具请求与执行回灌的编排。"},
    {"file": "libs/core/langchain_core/messages/tool.py", "symbol": "ToolMessage", "role": "承载工具执行结果，并通过 tool_call_id 对齐模型提出的工具请求。", "direction": "工具执行后回到消息状态。"},
]),
r"""
<h2>流程图：函数如何变成工具回合</h2>
""",
shell.call_graph([
    ("function", "带类型标注和 docstring 的 Python 函数", True),
    ("schema", "@tool / BaseTool 生成名称、描述、参数模型", True),
    ("bound model", "bind_tools 把 schema 交给 provider", False),
    ("AIMessage.tool_calls", "模型提出要调用哪个工具和参数", True),
    ("ToolMessage", "执行器运行真实代码并回灌观察", True),
]),
r"""
<h2>代码走读：简化版 @tool 装饰器与 schema 提取</h2>
<p>真实 <span class="mono">@tool</span> 支持更多参数、Runnable、协程、return_direct、response_format 和错误处理。这里保留最核心的机制：名称来自函数名或显式参数，描述来自 docstring，参数来自类型标注或 Pydantic schema，最后包装成实现 BaseTool 行为的对象。</p>
""",
shell.code_walkthrough(
    "libs/core/langchain_core/tools/convert.py",
    "tool",
    '''def tool(fn=None, *, name=None, args_schema=None, description=None):
    def wrap(func):
        tool_name = name or func.__name__
        tool_description = description or inspect.getdoc(func)
        schema = args_schema or create_schema_from_function(func)
        return StructuredTool(
            name=tool_name,
            description=tool_description,
            args_schema=schema,
            func=func,
        )
    return wrap(fn) if fn is not None else wrap

@tool
def lookup_order(order_id: str) -> str:
    """查询订单当前物流状态。order_id 必须是系统订单号。"""
    return read_order_status(order_id)''',
    "这是教学伪代码：真实实现还会校验 docstring、过滤注入参数、支持 async 和更丰富的返回格式。",
),
r"""
<h2>例子追踪：天气 / 订单查询工具调用</h2>
<p>这个 trace 把 id、arguments、执行结果和 ToolMessage 明确分开。模型返回的 arguments 需要校验，不能直接信任；执行结果需要绑定 tool_call_id，不能只把字符串塞进对话。</p>
""",
shell.trace_table([
    {"step": "1 定义工具", "input": "def get_weather(city: str) -> str", "action": "@tool 读取函数名、docstring（示例省略，真实工具必须写）、类型标注。", "output": "BaseTool(name='get_weather', args_schema=...)"},
    {"step": "2 绑定模型", "input": "model.bind_tools([get_weather])", "action": "工具 schema 被转换为 provider 支持的 tool 描述。", "output": "请求 payload 包含工具名称、说明和参数结构"},
    {"step": "3 模型请求", "input": "用户问：杭州明天天气？", "action": "模型返回 tool_calls。", "output": "{'id':'call_weather_1','name':'get_weather','args':{'city':'杭州'}}"},
    {"step": "4 程序执行", "input": "call_weather_1 / city=杭州", "action": "执行器校验参数、调用天气服务、捕获可预期错误。", "output": "多云，22 到 28 度"},
    {"step": "5 回灌观察", "input": "结果 + call_weather_1", "action": "包装 ToolMessage 并追加到 messages。", "output": "ToolMessage(content='多云...', tool_call_id='call_weather_1')"},
]),
r"""
<h2>docstring 是 prompt contract，不是随便写的注释</h2>
<p>工具描述会进入模型上下文，直接影响模型何时调用工具、如何填参数、是否理解边界。一个好 docstring 应该说明工具做什么、什么时候用、参数含义、返回内容和限制。例如“查询订单状态”不如“根据内部订单号查询当前物流状态；不能查询退款进度；order_id 必须是形如 A123 的订单号”。描述越清楚，模型越少猜。</p>
<p>docstring 不是安全控制。即使你写“不要删除数据”，模型仍可能在错误上下文里请求危险参数。安全必须在执行层完成：权限检查、参数白名单、幂等键、人工确认、审计日志、速率限制和回滚策略。工具描述帮助模型选择，执行器负责保护现实世界。</p>

<h2>类型标注、Pydantic args_schema 与参数校验</h2>
<p>类型标注让 LangChain 能推导简单 schema，例如 <span class="mono">city: str</span>、<span class="mono">limit: int</span>。复杂参数更适合显式 Pydantic schema：可以写字段说明、范围限制、枚举、默认值和嵌套结构。schema 越准确，provider 展示给模型的参数表越清楚，执行前的校验也越可靠。</p>
<p>但是 schema 仍然不是业务验证的全部。Pydantic 可以检查 <span class="mono">amount</span> 是数字，却不知道当前用户是否有退款权限；可以检查 <span class="mono">order_id</span> 是字符串，却不知道订单是否属于该用户。工具函数内部或外层执行器仍要检查业务规则。C 级设计会把“结构校验”和“业务授权”分成两层。</p>

<h2>注入状态与 runtime：让工具看到必要上下文</h2>
<p>某些工具需要用户 id、数据库连接、请求上下文或图状态。LangChain / LangGraph 生态里常见做法是通过注入参数、runtime、context 或 middleware 传入，而不是让模型自己填写这些敏感字段。模型可以提供“想查哪个订单”，不应该提供“当前用户是谁”“数据库连接是什么”。这些字段属于系统上下文，应由执行环境注入。</p>
<p>这种设计也防止 prompt injection。用户可能说“把 user_id 改成管理员”，如果 user_id 是模型可填写的普通参数，系统就危险；如果 user_id 来自受信 runtime，模型只能请求“查订单”，执行器会用真实登录用户做权限过滤。工具 schema 要区分模型可控参数和系统注入参数。</p>

<h2>错误表面：让模型知道可恢复错误，让系统记录不可恢复错误</h2>
<p>工具执行会失败：参数缺失、权限不足、外部服务超时、业务对象不存在、返回格式异常。不是所有错误都应该被吞掉。可恢复、可解释的错误可以变成 ToolMessage，让模型告诉用户“没有找到订单”或“需要补充城市”；系统错误则应该记录 trace、触发重试或返回受控失败，而不是让模型编造结果。</p>
<p>广泛捕获 <span class="mono">Exception</span> 并返回“工具失败”会让排错困难，也会训练模型在缺少事实时继续编故事。更好的做法是区分验证错误、权限错误、外部依赖错误和未知错误。每类错误决定是否回灌给模型、是否重试、是否中断、是否报警。</p>

<h2>工具副作用与生产安全</h2>
<p>查询天气和查询订单是低风险工具；退款、发邮件、写数据库、执行 shell 命令是高风险工具。模型提出 tool_call 不应自动意味着执行。高风险工具至少需要权限、确认、幂等、防重复、审计和速率限制。有些动作适合拆成两步：模型先生成计划，系统展示给人确认，人确认后才调用真实副作用工具。</p>
<p>副作用工具还要考虑重试。模型调用或网络层重试可能导致同一个退款请求执行两次，因此工具参数里需要幂等键，执行器需要识别重复 tool_call_id 或业务请求 id。不要把“模型只会调用一次”当作生产假设；流式、中断、恢复和 fallback 都可能让边界更复杂。</p>

<h2>create_agent 与手写执行器的选择</h2>
<p><span class="mono">create_agent</span> 帮你把模型、工具和循环组装起来，适合常见 Agent 场景。它会读取 AIMessage.tool_calls，执行工具，把 ToolMessage 加回状态，并继续调用模型。手写执行器则适合你需要严格控制审批、并行策略、错误分类或业务事务时。两者不是谁高级谁低级，而是控制权不同。</p>
<p>无论使用哪种方式，工具边界不变：模型只产生请求，程序执行真实代码，ToolMessage 回灌观察。理解这条边界后，你可以放心使用高层 Agent，也知道何时下探到 LangGraph 节点或自定义执行器。</p>

<h2>工具名称与参数设计</h2>
<p>工具名称要短、明确、动词化，例如 <span class="mono">lookup_order</span>、<span class="mono">get_weather</span>、<span class="mono">create_refund_draft</span>。不要把多个动作塞进一个工具名，例如 <span class="mono">manage_order</span>，否则模型不知道何时用它，参数 schema 也会变成万能表单。一个工具最好完成一个清晰能力，复杂业务流程交给 Agent 或图编排。</p>
<p>参数也要面向模型理解，而不是面向内部数据库表。让模型填写 <span class="mono">order_id</span>、<span class="mono">city</span>、<span class="mono">date</span> 通常合理；让模型填写 <span class="mono">sql</span>、<span class="mono">internal_user_pk</span>、<span class="mono">raw_payload</span> 就很危险。工具 schema 是模型能触碰的接口，接口越窄，系统越安全。</p>

<h2>C 级排错清单：工具层的五个证据</h2>
<p>工具问题不要只看最终回答，要收集五个证据。第一，工具对象的 name、description、args_schema 是否符合预期；第二，绑定到模型的 schema 是否包含这个工具；第三，AIMessage.tool_calls 是否真的请求了该工具，args 是否通过校验；第四，执行器是否运行了正确函数并记录成功或错误；第五，ToolMessage 是否带着匹配 tool_call_id 回到消息列表。缺任何一环，最终回答都可能偏离事实。</p>
<p>如果模型不调用工具，先看描述是否清楚、工具名是否表达动作、prompt 是否允许或要求使用工具、模型本身是否支持工具调用。不要第一反应在执行函数里加逻辑，因为函数根本没被调用。如果模型调用了错误工具，检查工具之间是否职责重叠，例如 search_order、lookup_order、get_order_info 同时存在会让模型困惑。工具集合越像清晰菜单，模型越容易选择。</p>
<p>如果工具参数错，检查字段描述和类型。<span class="mono">id</span> 这种字段名不如 <span class="mono">order_id</span> 清楚；自由字符串不如枚举；一个万能 query 字段不如几个明确字段。模型不是你的后端同事，它依赖 schema 理解接口。参数设计越贴近用户意图和业务语言，越少需要后处理猜测。</p>
<p>如果工具执行错，检查注入上下文和权限。当前用户、租户、数据库连接、request id、幂等键不应由模型填写。执行器应从受信 runtime 注入这些值，并在工具内部验证资源归属。模型提供的 order_id 只表示“用户提到了哪个订单”，不表示“用户有权查看该订单”。这条边界是生产 Agent 安全的底线。</p>
<h2>工具设计的粒度取舍</h2>
<p>工具太粗会让模型难以判断，太细会让模型需要规划很多步骤。一个好工具通常对应用户可理解的一项能力，并有清晰输入输出。比如 <span class="mono">lookup_order_status</span> 比 <span class="mono">run_sql</span> 安全，比 <span class="mono">lookup_order_city</span>、<span class="mono">lookup_order_time</span>、<span class="mono">lookup_order_carrier</span> 三个碎工具更容易使用。粒度要服务于任务，而不是服务于内部函数拆分。</p>
<p>读写工具应分开。查询类工具可以让模型较自由地请求；写入类工具应更加窄、可审计、可确认。例如不要给模型一个 <span class="mono">update_order</span> 万能工具，而是提供 <span class="mono">create_refund_draft</span>、<span class="mono">send_address_change_request</span> 这类受控动作，并要求人工确认或业务规则通过后才提交。工具名里出现 draft、request、preview 往往比直接 execute 更安全。</p>
<p>工具返回也要设计。返回给模型的内容应足够回答用户，但不要泄露内部字段、密钥、SQL、堆栈或无关个人信息。错误返回要可理解，例如“订单不存在或不属于当前用户”，但内部日志可以保留更详细原因。ToolMessage 是给模型看的观察，不是给工程师的完整日志；工程日志应走 trace 和安全日志。</p>
<h2>工具测试与演练</h2>
<p>每个工具至少应有纯函数或受控环境测试：合法参数返回预期结果，非法参数被拒绝，权限不足不执行，外部服务失败时返回分类错误。工具 schema 也要测试：name、description、必填字段和字段说明是否存在。很多工具 bug 不是函数逻辑错，而是 schema 让模型填错参数。</p>
<p>还可以写“假 tool_call 执行测试”。手动构造 AIMessage.tool_calls，交给执行器，断言它调用正确工具、生成 ToolMessage、保留 tool_call_id、错误时产生可追踪状态。这样不用真实模型也能验证工具执行链。等执行链可靠后，再用真实模型做少量端到端评估：模型是否在正确场景调用工具，参数质量如何，错误时是否追问。</p>
<p>最后建立工具风险分级。低风险查询工具可以自动执行；中风险工具需要权限和速率限制；高风险副作用工具需要确认、幂等和审计；极高风险工具不应暴露给模型。LangChain 提供工具抽象，但风险分级属于你的业务架构。C 级开发者必须能说明每个工具的副作用、权限来源、失败模式和回滚策略。</p>
<p>如果你无法用一句话解释某个工具何时应该被模型调用，说明这个工具还没有准备好进入 Agent。先改名、拆分、补 description、收窄参数，再绑定给模型，比事后调 prompt 更可靠。</p>


<h2>课堂复盘：工具是最小可信执行面</h2>
<p>把工具看成模型能触碰的最小可信执行面。工具名、描述和参数 schema 告诉模型“可以请求什么”；执行器、权限和业务规则决定“是否真的做”。如果工具暴露得过宽，模型一次错误理解就可能影响真实系统；如果工具暴露得过窄，模型需要很多轮才能完成简单任务。好的工具设计是在可用性和安全性之间画清边界。</p>
<p>代码审查时要特别关注副作用。查询工具可以返回事实，写入工具应尽量返回草稿、预览或请求编号，让人或规则确认后再提交。工具函数内部不要信任模型参数，要重新校验用户、租户、资源归属和幂等键。即使工具由 Agent 自动调用，审计日志也应能回答：哪个 run、哪个 tool_call_id、哪个用户、哪个参数、哪个结果。</p>
<p>工具教学里最容易被忽略的是“返回给模型什么”。返回太少，模型无法回答；返回太多，可能泄露内部细节或让上下文膨胀。建议返回面向用户任务的摘要，把详细诊断写入 trace。ToolMessage 是给下一轮模型的观察，不是数据库记录，也不是安全日志。分清这三种输出，工具系统会更稳。</p>

<h2>延伸练习：为每个工具写风险说明</h2>
<p>工具清单旁边应有风险说明：是否读取敏感数据，是否产生副作用，是否依赖外部服务，是否需要用户权限，是否支持幂等，失败时是否能安全重试。这个说明不一定进入模型上下文，但应进入工程文档和代码审查。模型看到的是简洁 description，工程师需要的是完整风险边界。</p>
<p>对于高风险工具，建议把执行拆成计划、预览、确认、提交四步。模型可以生成计划和调用预览工具；系统展示预览；用户或规则确认后，提交工具才执行真实副作用。LangChain 的工具抽象足够灵活，关键在于你不要把所有步骤压成一个“do_anything”工具。工具越窄，越容易审计和恢复。</p>

<h2>最后检查：把概念落到一次真实调用</h2>
<p>完成本课后，请把概念重新放回一次真实调用中验证：输入从哪里来，经过哪个对象标准化，运行时配置如何传播，输出由谁解释，错误在哪里被看见，哪些信息进入 trace，哪些信息进入业务状态。只要能沿着这条线讲清楚，说明你掌握的不是 API 片段，而是可维护的系统边界。</p>
<p>这也是 C 级课程反复强调的学习方法：每个抽象都要回答“它统一什么、它不负责什么、它失败时看什么证据”。抽象不是为了隐藏一切，而是为了让变化集中、证据清楚、责任可定位。后续课程继续读源码时，请始终用这三个问题检查自己的理解。</p>
<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("把 schema 暴露给模型就等于工具已经执行。", "schema 只是能力说明；AIMessage.tool_calls 出现后，程序才决定是否执行。"),
    ("docstring 只是给人看的注释。", "工具描述会进入模型上下文，是模型选择工具和填参数的 prompt contract。"),
    ("模型请求任何副作用都可以直接执行。", "副作用必须经过权限、确认、幂等和审计，模型只能提出请求。"),
    ("ToolMessage 可以省略 tool_call_id。", "工具观察必须对齐具体调用 id，尤其在多工具和并行场景。"),
    ("捕获所有异常并返回空字符串最稳。", "吞错会隐藏系统故障并诱导模型编造结果，应分类处理错误表面。"),
]),
r"""
<h2>小实验：写一个纯工具并观察 schema</h2>
""",
shell.lab_card("检查 @tool 产物", [
    "定义一个无副作用函数 add_tax(price: float, rate: float) -> float，并写清 docstring。",
    "用 @tool 装饰后打印 tool.name、tool.description、tool.args_schema。",
    "故意删除类型标注，比较 schema 信息如何变差。",
    "构造一个假的 AIMessage.tool_calls，手动校验 args 后调用工具函数。",
    "把执行结果包装为 ToolMessage，确认 tool_call_id 与假调用 id 一致。"],),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>工具把函数能力转为模型可读 schema，但真实执行始终由程序控制。</li>
    <li>高质量 docstring、类型标注和 Pydantic args_schema 会显著改善模型调用质量。</li>
    <li>模型可控参数、系统注入状态和业务权限必须分开，不能让 prompt 决定敏感上下文。</li>
    <li><span class="mono">AIMessage.tool_calls</span>、执行器和 <span class="mono">ToolMessage.tool_call_id</span> 构成完整工具回合。</li>
  </ul>
</div>
""",
shell.version_note("本课以 LangChain core tools、function_calling 转换和 v1 create_agent 的边界为锚点。provider 工具格式会变化，但“函数 → schema → tool_calls → 执行 → ToolMessage”的工程契约是阅读新版工具系统的主线。"),
])


LESSON_09_PROMPTS = "".join([
r"""
<p class="lead">Prompt 不是一段随手拼接的字符串，而是结构化消息工厂。<span class="mono">ChatPromptTemplate</span> 负责声明系统消息、人类消息、历史占位、少样本示例和变量；调用时校验变量、合并 partial、格式化内容，最后产出 <span class="mono">ChatPromptValue</span>，再转换为消息列表交给聊天模型。把 prompt 当 Runnable 看，才能把它稳定地接进链、解析器和 Agent。</p>

<div class="card analogy">
  <div class="tag">📝 生活类比 · 表单模板和会议议程</div>
  字符串 prompt 像把会议要求写在便签上，谁先说、历史记录放哪、哪些字段必填都靠人记。ChatPromptTemplate 像正式会议议程和表单：主持人开场、参会人问题、历史发言、示例材料各有位置；开会前检查必填项，固定信息可以提前盖章，真正开会时再填本次问题。
</div>

<h2>本课地图：模板声明到模型消息</h2>
<p>Prompt 的核心价值是保持结构。系统消息放规则，人类消息放本轮问题，历史用 <span class="mono">MessagesPlaceholder</span> 插入消息列表，少样本示例放在合适位置，partial variables 绑定稳定上下文。最终输出不是字符串，而是可转换为消息的 PromptValue。</p>
""",
shell.lesson_map("Prompt 作为消息工厂", [
    ("模板声明", "定义 system/human/history/example 等消息片段", "before"),
    ("变量校验", "确认 role、question、history 等输入齐全且形状正确", "now"),
    ("partial 绑定", "把稳定变量提前固定，减少每次调用参数", "now"),
    ("格式化", "将变量填入模板，保留消息边界", "source"),
    ("交给模型", "ChatPromptValue.to_messages() 成为 BaseMessage 列表", "after"),
]),
r"""
<h2>源码入口：文件 + 符号名</h2>
<p>读 prompt 源码要同时看模板、占位符、PromptValue 和 Runnable。这样你会发现 prompt 并不是模型前面的字符串拼接函数，而是链里第一个可调用组件。</p>
""",
shell.source_map([
    {"file": "libs/core/langchain_core/prompts/chat.py", "symbol": "ChatPromptTemplate", "role": "声明并格式化聊天消息模板，支持 from_messages、partial、invoke 等接口。", "direction": "用户模板进入 Runnable 链。"},
    {"file": "libs/core/langchain_core/prompts/chat.py", "symbol": "MessagesPlaceholder", "role": "在模板中插入已有消息列表，常用于 history、agent_scratchpad 或工具轨迹。", "direction": "把外部消息状态注入 prompt。"},
    {"file": "libs/core/langchain_core/prompt_values.py", "symbol": "ChatPromptValue", "role": "格式化后的聊天 prompt 值，可转换为 BaseMessage 列表或字符串表示。", "direction": "prompt 与模型输入之间的桥。"},
    {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "Runnable", "role": "统一 invoke、batch、stream、config 组合协议，PromptTemplate 也实现它。", "direction": "允许 prompt | model | parser 组合。"},
    {"file": "libs/core/langchain_core/prompts/base.py", "symbol": "BasePromptTemplate", "role": "Prompt 模板公共基类，处理输入变量、partial variables、校验和格式化入口。", "direction": "聊天模板和字符串模板共享基础行为。"},
]),
r"""
<h2>状态流：声明、校验、partial、format、messages</h2>
""",
shell.state_flow([
    ("模板声明", "用 from_messages 写出 system、人类消息和历史占位，变量名成为契约。", "ChatPromptTemplate"),
    ("变量校验", "invoke 时检查必填变量是否存在，placeholder 是否接收消息列表。", "input_variables"),
    ("partial 绑定", "把固定角色、产品名、格式要求提前绑定到模板。", "partial_variables"),
    ("格式化", "把本次 question 填入对应消息，保持 system/human/history 分离。", "format_messages"),
    ("消息输出", "返回 ChatPromptValue，再由模型转换为 BaseMessage 列表。", "ChatPromptValue"),
]),
r"""
<h2>代码走读：简化版 ChatPromptTemplate.invoke</h2>
<p>真实实现支持更多消息表示、模板格式、校验选项和 Runnable config。下面的伪代码突出三件事：先合并 partial 和本次输入；再验证变量；最后逐个消息模板格式化，placeholder 直接展开消息列表。</p>
""",
shell.code_walkthrough(
    "libs/core/langchain_core/prompts/chat.py",
    "ChatPromptTemplate.invoke",
    '''class ChatPromptTemplate(BasePromptTemplate):
    def invoke(self, input, config=None):
        values = merge(self.partial_variables, normalize_input(input))
        self._validate_input(values)
        messages = []
        for part in self.messages:
            if isinstance(part, MessagesPlaceholder):
                messages.extend(values.get(part.variable_name, []))
            else:
                messages.append(part.format(values))
        return ChatPromptValue(messages=messages)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是{role}，回答要简洁。"),
    MessagesPlaceholder("history", optional=True),
    ("human", "{question}"),
])''',
    "这是教学伪代码：真实源码还会处理可选占位符、不同模板引擎、单变量快捷输入和错误信息。",
),
r"""
<h2>例子追踪：role、question 与 history 如何变成消息</h2>
""",
shell.trace_table([
    {"step": "1 声明模板", "input": "system: 你是{role}; history placeholder; human: {question}", "action": "模板记录变量 role、question、history。", "output": "ChatPromptTemplate"},
    {"step": "2 无历史调用", "input": "{role:'客服助手', question:'订单多久到？'}", "action": "optional history 缺省为空，格式化 system 和 human。", "output": "[SystemMessage, HumanMessage]"},
    {"step": "3 有历史调用", "input": "history=[HumanMessage('订单 123'), AIMessage('请稍等')]", "action": "MessagesPlaceholder 展开已有消息，不把历史拼成字符串。", "output": "[SystemMessage, HumanMessage, AIMessage, HumanMessage]"},
    {"step": "4 交给模型", "input": "ChatPromptValue", "action": "模型调用前转换为 messages。", "output": "BaseMessage 列表"},
    {"step": "5 下游稳定", "input": "prompt | model | parser", "action": "prompt 作为 Runnable 输出模型可接受的输入。", "output": "链式组合保持类型边界"},
]),
r"""
<h2>系统、人类、历史分离的意义</h2>
<p>系统消息用于放角色、任务边界、输出约束和安全提醒；人类消息用于放本轮用户问题；历史消息用于保留真实对话上下文。三者分离后，provider adapter 可以按角色翻译，裁剪逻辑可以优先保留系统消息，工具循环可以把 ToolMessage 放在正确位置。混成一个字符串后，模型也许能读懂，但框架无法再可靠处理。</p>
<p>分离也有助于排错。回答跑偏时，你可以检查系统消息是否过长、历史是否污染、本轮 question 是否被错误转义、few-shot 示例是否离用户问题太远。字符串拼接让这些问题都变成“prompt 好像不行”；结构化模板则能定位是哪一段不行。</p>

<h2>partial variables：把稳定上下文提前绑定</h2>
<p>partial 适合固定产品名、角色、格式说明、语言偏好等稳定变量。例如一个客服 prompt 可以提前绑定 <span class="mono">role='耐心的售后客服'</span> 和 <span class="mono">brand='示例商城'</span>，每次调用只传 question 和 history。这样上层链更简单，也减少漏传变量。</p>
<p>但 partial 不应变成隐藏业务状态。用户权限、订单状态、实时库存这类会变化的数据，应来自工具、检索或图状态，而不是在 prompt 构造时永久绑定。否则一次请求的上下文可能污染后续请求，尤其在长生命周期服务中。</p>

<h2>可选 placeholder 与 history 形状</h2>
<p><span class="mono">MessagesPlaceholder(optional=True)</span> 表示没有历史时可以为空。有历史时，它期望的是消息列表，不是一段“用户：...AI：...”字符串。把 history 当字符串传入会丢失角色和工具消息，甚至把旧系统提示伪装成用户内容。C 级检查要确认每个 placeholder 的变量名、是否 optional、传入值类型都符合预期。</p>
<p>Agent 场景中还会看到 scratchpad 或 intermediate steps 的 placeholder。它们本质上也是结构化消息插入点。不要把工具轨迹塞进普通 human 文本；如果轨迹里包含 ToolMessage，就让 placeholder 展开消息对象，让模型和 tracer 看到正确边界。</p>

<h2>few-shot 示例放哪里</h2>
<p>少样本示例可以提升格式稳定性，但位置很重要。放在系统消息里会让规则和例子混杂；放在历史里会让模型误以为示例是真实对话；放在单独的示例消息序列里，通常更清楚。示例应覆盖你希望模型模仿的输入输出模式，而不是堆很多无关问答占满上下文。</p>
<p>示例也要和输出解析器配合。如果后面接 JSON parser，示例输出就必须是合法 JSON；如果后面用工具调用，示例应强调何时调用工具、何时直接回答。prompt 不是孤立文本，它和模型能力、工具 schema、parser 契约一起决定系统行为。</p>

<h2>Prompt 作为 Runnable 的组合价值</h2>
<p>因为 prompt 实现 Runnable，你可以写 <span class="mono">prompt | model | parser</span>。这条链表达了清晰的数据流：输入 dict 进入 prompt，输出消息进入模型，输出 AIMessage 或文本进入 parser。每一段都可以单独 invoke、测试、加 config、批量运行。比起一个巨型函数里拼字符串、调用 SDK、解析结果，Runnable 组合更容易替换和追踪。</p>
<p>这也意味着 prompt 可以被复用和测试。你不必调用真实模型就能验证变量校验、history 插入和消息顺序。很多 prompt bug 在模型调用前就能发现：变量缺失、placeholder 类型错、系统消息被重复插入、few-shot 放错位置。先测试 prompt 输出的消息列表，能省下大量模型调试成本。</p>

<h2>Prompt injection 边界</h2>
<p>系统消息不是魔法防火墙。用户仍可能在 question 或 history 里写“忽略之前规则”。结构化 prompt 能帮助你分清哪部分来自系统、哪部分来自用户，但不能保证模型永远遵守。真正的安全要靠工具权限、输出校验、检索过滤和业务边界。Prompt 层负责表达意图，不负责独自承担所有安全。</p>
<p>一个实用策略是把不可信内容放在明确标记的用户或上下文消息里，避免把用户文本拼进系统规则。比如不要生成 <span class="mono">system=f'你必须遵守：{user_policy}'</span>，而应把用户提供的材料放在 human/context 段落，并在系统消息里说明“以下材料可能不可信”。结构边界越清楚，注入面越小。</p>

<h2>字符串 prompt 与 chat prompt 的取舍</h2>
<p>简单补全文本任务可以使用字符串模板；对话模型、工具调用和多轮历史更适合 chat prompt。判断标准不是“哪种语法更短”，而是你是否需要角色、消息历史、工具观察和 provider 聊天格式。如果需要这些结构，ChatPromptTemplate 的成本很快被收益抵消。</p>
<p>不要把 chat prompt 最终转成字符串再传给聊天模型，除非你明确知道要牺牲结构。很多模型 wrapper 可以接受 PromptValue 或消息列表，保留结构更稳。只有在调试展示或兼容非聊天模型时，字符串表示才是必要折中。</p>

<h2>模板变量命名与维护</h2>
<p>变量名应表达业务语义，例如 <span class="mono">question</span>、<span class="mono">history</span>、<span class="mono">customer_tier</span>，不要使用 <span class="mono">x</span>、<span class="mono">input</span> 混装所有数据。命名清楚后，链的输入 schema 也更清楚，调用者知道要传什么。变量越随意，prompt 越像隐式函数，维护者只能读模板猜契约。</p>
<p>当 prompt 变长时，不要只继续追加系统规则。可以拆出检索上下文、工具说明、输出格式示例、业务策略摘要，分别放在合适消息或上游 Runnable 中。过度膨胀的系统 prompt 会降低可读性，也让模型难以判断哪条规则优先。</p>

<h2>C 级排错清单：Prompt 层如何定位问题</h2>
<p>Prompt 问题首先看格式化后的消息，而不是看模板源码。打印 <span class="mono">prompt.invoke(input).to_messages()</span>，检查消息顺序、类型、变量替换、history 展开和示例位置。很多错误一眼可见：系统消息重复插入，history 作为字符串进入 human 消息，question 为空，partial 绑定了旧用户信息，few-shot 示例被放在本轮问题之后。</p>
<p>其次检查变量契约。模板需要哪些 input_variables，哪些是 optional placeholder，哪些来自 partial，调用者是否都知道。若链的输入叫 <span class="mono">input</span>，模板里叫 <span class="mono">question</span>，上游 mapper 又改成 <span class="mono">query</span>，缺变量错误就会频繁出现。变量名是接口，不是局部随意命名。接口越清楚，链越容易组合。</p>
<p>第三检查上下文来源。检索文档、用户历史、工具观察和业务规则不应都塞进一个 system prompt。检索内容可能不可信，适合单独上下文段；用户历史是消息列表；工具观察是 ToolMessage；稳定业务规则才适合 system。把来源分开后，你才能针对注入、裁剪和过期信息分别处理。</p>
<p>第四检查输出契约。Prompt 要告诉模型输出格式，但真正的约束在 parser 或 structured output。若模型输出格式不稳，不要只在系统消息里继续加“必须必须必须”；应加示例、缩短无关规则、使用 JsonOutputParser 或 with_structured_output，并让解析错误反馈到修复流程。Prompt 是契约说明，不是契约执行器。</p>
<h2>Prompt 版本管理</h2>
<p>生产 prompt 应像代码一样版本化。每次修改系统规则、示例、变量名或输出格式，都可能影响模型行为。建议给关键 prompt 标注名称、版本、适用模型、输出 parser 和评估集。这样线上回答变化时，你能知道是模型升级、prompt 改动、检索变化还是工具 schema 变化。</p>
<p>Prompt 版本不一定需要复杂平台，最小做法是在代码中集中定义模板，配套小型 golden cases。每个 case 包含输入、history、期望消息形状和关键输出性质。修改模板后先跑这些测试，确认没有丢变量、没有把历史拼错、没有破坏 JSON 示例。不要把 prompt 散落在业务函数字符串里，否则查找和回滚都困难。</p>
<p>多语言场景也要明确。中文优先的系统提示、英文工具名、用户混合语言输入可能同时出现。Prompt 应说明回答语言策略，工具 description 也要让模型理解。不要依赖模型自动猜；如果业务要求中文回答，就把语言要求放在稳定位置，并在输出评估里检查。</p>
<h2>长 Prompt 的治理</h2>
<p>当系统 prompt 越写越长时，通常说明多个责任混在一起：角色设定、政策、格式、示例、上下文、拒答规则、工具说明。可以把稳定政策压缩成短规则，把示例移到 few-shot，把动态上下文放到 placeholder，把工具说明交给 tool schema，把输出格式交给 parser。Prompt 越短越不一定越好，但责任越清楚越好。</p>
<p>上下文裁剪也要尊重结构。删除历史时不要删除系统消息；压缩历史时不要把工具 id 和观察关系抹掉；截断检索材料时保留来源和边界。Prompt 层的每一次拼接和裁剪，都会改变模型看到的世界。C 级开发者要能解释“模型这次到底看到了什么”，而不是只说“我们传了上下文”。</p>
<p>Prompt injection 防护应采用多层策略：不可信内容单独标记，系统规则不拼接用户文本，工具执行做权限检查，解析器做输出校验，检索内容保留来源，敏感动作需要确认。结构化模板只是第一层，它让边界可见；真正安全来自每层都不越权。</p>
<h2>Prompt 的可测试性</h2>
<p>不要等真实模型回答后才测试 prompt。先断言格式化后的 messages：第一条是 SystemMessage，history 展开数量正确，最后一条是 HumanMessage，必填变量缺失会报错，optional history 不传时为空。再用 fake model 测链组合，用固定输出测 parser。真实模型评估应关注语义质量，而不是承担基础格式测试。</p>
<p>这种分层测试能让 prompt 迭代更快。模板改动如果导致变量缺失，单元测试立刻失败；模型升级如果导致回答风格变化，评估集再捕捉。把所有问题都留到人工读最终回答，会让 prompt 工程变成玄学。结构化 prompt 的价值之一，就是把玄学部分压缩到真正需要模型判断的地方。</p>
<p>最后，把 prompt 看成 API：它有输入变量、输出形状、版本、适用场景和失败模式。API 需要文档和测试，prompt 也一样。C 级掌握 prompt，不是写更长的咒语，而是把模型上下文设计成可维护、可替换、可验证的组件。</p>


<h2>课堂复盘：Prompt 模板是一份可执行接口文档</h2>
<p>如果把 Prompt 当成接口文档，就会自然关心输入变量、消息顺序、可选字段、输出契约和版本。调用者不应该猜模板里需要什么；模板也不应该偷偷读取全局状态。清晰的 ChatPromptTemplate 会告诉你：我需要 question，我可以接收 history，我已经 partial 绑定 role，我输出 ChatPromptValue。这样的 prompt 才能被组合、测试和替换。</p>
<p>Prompt 维护的难点往往不是写第一版，而是多人长期修改。有人加安全规则，有人加输出格式，有人加业务政策，有人加 few-shot 示例，最后系统消息变成一堵墙。C 级做法是定期拆分责任：稳定规则留在 system，动态材料走 placeholder，格式交给 parser，工具能力写进 tool schema，示例只保留最能说明模式的几条。Prompt 不是垃圾桶。</p>
<p>评估 Prompt 时，不要只看模型最终回答。先看格式化后的消息列表是否符合预期，再看模型是否遵守主要指令，再看 parser 是否通过，最后看业务指标。每层都可单独改进。这样 Prompt 工程就从“调咒语”变成“维护一个结构化、可执行、可观测的模型输入接口”。</p>

<h2>延伸练习：建立 Prompt 变更评审问题</h2>
<p>每次修改 prompt 前，可以问一组固定问题：新增内容属于系统规则、用户上下文、检索材料、示例还是输出格式？是否引入新变量？是否影响 parser？是否让 history 位置改变？是否增加 token 成本？是否扩大 prompt injection 面？这些问题能让 prompt 变更像普通代码变更一样被审查，而不是凭感觉追加句子。</p>
<p>Prompt 还应配合评估样本。样本不需要一开始很多，但要覆盖核心路径：无历史、有历史、有工具观察、用户注入、缺少上下文、需要拒答、需要 JSON 输出。每次模板变化都跑一遍，记录输出差异。这样你会知道改动影响了哪里，而不是等线上用户告诉你模型变得奇怪。</p>

<h2>最后检查：把概念落到一次真实调用</h2>
<p>完成本课后，请把概念重新放回一次真实调用中验证：输入从哪里来，经过哪个对象标准化，运行时配置如何传播，输出由谁解释，错误在哪里被看见，哪些信息进入 trace，哪些信息进入业务状态。只要能沿着这条线讲清楚，说明你掌握的不是 API 片段，而是可维护的系统边界。</p>
<p>这也是 C 级课程反复强调的学习方法：每个抽象都要回答“它统一什么、它不负责什么、它失败时看什么证据”。抽象不是为了隐藏一切，而是为了让变化集中、证据清楚、责任可定位。后续课程继续读源码时，请始终用这三个问题检查自己的理解。</p>
<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("Prompt 就是一段字符串模板。", "ChatPromptTemplate 是结构化消息工厂，输出 ChatPromptValue / messages。"),
    ("历史记录拼成一个字符串最省事。", "history 应保留为消息列表，否则角色、工具观察和裁剪边界会丢失。"),
    ("缺变量时模型会自己补。", "模板应在调用前校验变量，缺失应尽早报错。"),
    ("系统 prompt 越长越安全。", "过长系统消息会掩盖重点；安全还需要工具权限、输出校验和业务边界。"),
    ("防注入只靠在 prompt 里写不要被注入。", "结构化 prompt 只是边界之一，不能替代执行层安全控制。"),
]),
r"""
<h2>小实验：有无 history 的格式化结果对比</h2>
""",
shell.lab_card("观察 ChatPromptValue.to_messages()", [
    "创建包含 system、MessagesPlaceholder('history', optional=True)、human 的 ChatPromptTemplate。",
    "第一次只传 role 和 question，打印 prompt.invoke(...).to_messages() 的类型顺序。",
    "第二次传入 history=[HumanMessage('订单 123'), AIMessage('我来查询')]，再次打印消息顺序。",
    "把 history 改成普通字符串，观察错误或输出差异，并解释为什么消息列表更稳。",
    "把 role 用 partial 预绑定，确认每次调用只需要传 question 和 history。"],),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Prompt 是结构化消息工厂，也是 Runnable；它输出 ChatPromptValue，而不只是字符串。</li>
    <li>system、human、history、few-shot 和工具轨迹应保持消息边界，方便模型适配、裁剪和追踪。</li>
    <li>partial variables 适合稳定上下文，不适合隐藏会变化的业务状态。</li>
    <li>Prompt injection 需要结构边界和执行层安全共同处理，不能只靠一句系统规则。</li>
  </ul>
</div>
""",
shell.version_note("本课以 langchain_core.prompts 的 ChatPromptTemplate、MessagesPlaceholder、ChatPromptValue 和 Runnable 组合为锚点。模板语法会扩展，但“声明变量 → 校验输入 → 格式化消息 → 交给模型”的路径是长期稳定的。"),
])


LESSON_10_OUTPUT_PARSERS = "".join([
r"""
<p class="lead">输出解析器把模型生成的文本或消息变成应用能依赖的数据契约。模型擅长生成，但应用需要稳定类型：字符串、JSON dict、Pydantic 对象、列表或业务命令。<span class="mono">StrOutputParser</span>、<span class="mono">JsonOutputParser</span> 和 <span class="mono">BaseOutputParser</span> 让 <span class="mono">prompt | model | parser</span> 成为清晰链路；解析失败应被看见、验证、修复，而不是被吞掉。</p>

<div class="card analogy">
  <div class="tag">🧾 生活类比 · 海关申报单</div>
  模型输出像旅客口头描述“我带了点东西”，解析器像海关把口头描述填进标准申报单：物品名称、数量、金额、是否需要检查。口头描述可以很流畅，但系统入库必须是字段明确的表。填错了不能假装没事，要退回补充或人工检查。
</div>

<h2>本课地图：从生成文本到应用数据</h2>
<p>解析器的核心任务不是让模型“更聪明”，而是让应用边界更清楚。prompt 说明期望格式，模型生成候选输出，parser 把输出转成类型化结果，验证层检查业务约束，失败时进入修复或重试。没有解析器，应用很容易靠正则和字符串包含判断支撑关键流程，后期会非常脆弱。</p>
""",
shell.lesson_map("解析器的责任边界", [
    ("Prompt", "要求模型输出某种格式或结构", "before"),
    ("Model", "返回 AIMessage 或文本，可能包含格式错误", "now"),
    ("Parser", "把文本 / 消息解析成字符串、dict、对象等契约", "now"),
    ("Validation", "检查类型、必填字段、业务规则和可恢复错误", "source"),
    ("Repair", "失败时重试、修复 prompt、人工介入或中断", "after"),
]),
r"""
<h2>源码入口：文件 + 符号名</h2>
<p>输出解析要同时看普通 parser、JSON parser、抽象基类、模型结构化输出和 RunnableSequence。这样你能区分“parser 在模型之后解析”和“with_structured_output 让模型 wrapper 使用 provider 原生结构化能力”。</p>
""",
shell.source_map([
    {"file": "libs/core/langchain_core/output_parsers/string.py", "symbol": "StrOutputParser", "role": "从模型结果中提取字符串内容，是最简单的模型后处理 parser。", "direction": "常接在聊天模型之后输出纯文本。"},
    {"file": "libs/core/langchain_core/output_parsers/json.py", "symbol": "JsonOutputParser", "role": "解析 JSON 文本为 Python 数据结构，并支持部分流式解析场景。", "direction": "模型文本进入结构化应用数据。"},
    {"file": "libs/core/langchain_core/output_parsers/base.py", "symbol": "BaseOutputParser", "role": "解析器公共基类，定义 parse、parse_result、invoke 等接口。", "direction": "具体 parser 继承并作为 Runnable 使用。"},
    {"file": "libs/core/langchain_core/language_models/chat_models.py", "symbol": "with_structured_output", "role": "聊天模型的结构化输出便捷接口，可结合 schema / provider 能力返回结构化结果。", "direction": "模型 wrapper 层提供 parser 的替代或补充路径。"},
    {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "RunnableSequence", "role": "由 prompt | model | parser 组成的顺序 Runnable，负责把上一步输出传给下一步。", "direction": "解析器进入链式组合。"},
]),
r"""
<h2>流程：prompt → model → parser → typed result → validation / repair</h2>
""",
shell.call_graph([
    ("prompt", "说明输出契约，例如必须返回 JSON", True),
    ("model", "生成 AIMessage 或文本，可能不完全合规", False),
    ("parser", "解析内容，失败时抛出可观察错误", True),
    ("typed result", "dict / str / Pydantic 对象进入应用", True),
    ("validation / repair", "业务校验、重试、修复提示或人工处理", True),
]),
r"""
<h2>代码走读：简化版 parser.invoke 与 JSON 解析</h2>
<p>真实 parser 要处理 Generation、ChatGeneration、partial parsing、异常包装和流式事件。下面的伪代码突出两个边界：先从模型输出中取文本，再由具体 parser 解析；解析失败应该抛出带上下文的异常，而不是返回空 dict。</p>
""",
shell.code_walkthrough(
    "libs/core/langchain_core/output_parsers/base.py",
    "BaseOutputParser / JsonOutputParser",
    '''class BaseOutputParser(Runnable):
    def invoke(self, input, config=None):
        if isinstance(input, BaseMessage):
            text = input.content
        else:
            text = str(input)
        return self.parse(text)

class JsonOutputParser(BaseOutputParser):
    def parse(self, text):
        try:
            return json.loads(extract_json(text))
        except JSONDecodeError as exc:
            raise OutputParserException(
                "model output is not valid JSON",
                llm_output=text,
            ) from exc

chain = prompt | model | JsonOutputParser()''',
    "这是教学伪代码：真实 JsonOutputParser 还支持 markdown JSON 块、partial 解析和更细的异常信息。",
),
r"""
<h2>例子追踪：坏 JSON、验证错误与修复</h2>
""",
shell.trace_table([
    {"step": "1 模型原始输出", "input": "```json {'answer':'是', 'score': 0.9,} ```", "action": "输出看起来像 JSON，但用了单引号和尾逗号。", "output": "raw text"},
    {"step": "2 parser 解析", "input": "raw text", "action": "JsonOutputParser 尝试提取并 json.loads。", "output": "OutputParserException"},
    {"step": "3 修复提示", "input": "错误信息 + 原始输出 + schema", "action": "可选择让模型只修复格式，不重新编造事实。", "output": "{\"answer\":\"是\",\"score\":0.9}"},
    {"step": "4 dict 结果", "input": "合法 JSON 文本", "action": "parser 返回 dict。", "output": "{'answer':'是','score':0.9}"},
    {"step": "5 业务验证", "input": "score=0.9", "action": "验证字段范围、必填字段和业务含义。", "output": "通过或进入人工复核"},
]),
r"""
<h2>Parser 与 structured output 的区别</h2>
<p>普通 parser 通常在模型生成之后运行：模型输出文本或消息，parser 再解析。<span class="mono">with_structured_output</span> 则常常利用模型 wrapper 和 provider 原生能力，把 schema 传给模型，让 provider 尽量按结构返回。两者都服务于数据契约，但失败模式不同。parser 更通用，structured output 可能更稳定却更依赖 provider 支持。</p>
<p>不要把二者看成互斥。你可以优先用 provider 原生结构化输出，再在应用层做 Pydantic 验证；也可以在不支持原生结构化的模型后接 JsonOutputParser。关键是让边界显式：模型被要求输出什么，parser 解析什么，业务验证什么，失败如何处理。</p>

<h2>Pydantic schema：类型契约与业务契约</h2>
<p>Pydantic schema 能表达字段名、类型、描述、默认值和范围，是结构化输出的重要工具。它既能指导模型，也能验证结果。例如客服分类可以要求 <span class="mono">category</span> 是枚举，<span class="mono">confidence</span> 在 0 到 1 之间，<span class="mono">reason</span> 是短字符串。模型输出不符合时，应用应明确失败。</p>
<p>但 schema 不是业务正确性的全部。模型返回 <span class="mono">category='refund'</span> 且格式合法，不代表用户真的有退款资格；返回 <span class="mono">confidence=0.99</span> 不代表事实准确。结构验证保证“像不像一张表”，业务验证保证“这张表能不能用于动作”。两层都需要。</p>

<h2>partial / streaming parse 的价值与限制</h2>
<p>流式输出时，parser 可能尝试 partial parse，让 UI 更早展示部分结构。例如 JSON 对象逐步生成时，可以在字段完整后更新界面。但 partial 结果不是最终契约，不能过早触发副作用。只有最终解析和验证通过后，才应执行写数据库、发邮件或扣款等动作。</p>
<p>partial parse 还会遇到边界问题：字符串尚未闭合、数组尚未结束、模型中途改字段名。UI 可以乐观显示“正在生成”，业务层必须等待稳定结果。把流式体验和业务提交分开，是解析器用于生产的关键。</p>

<h2>失败处理：看见错误，而不是藏起错误</h2>
<p>解析失败是正常工程事件，不是异常羞耻。模型可能输出解释文字、markdown 包裹、尾逗号、缺字段或多字段。好的链路会记录原始输出、parser 名称、schema、错误原因和 run id，然后决定修复、重试、降级或人工处理。坏链路会捕获异常返回 <span class="mono">{}</span>，让下游在更远处以奇怪方式失败。</p>
<p>修复 prompt 也要小心。修复任务应要求“只把以下输出改成合法 JSON，不要改变事实”，并把原始输出和错误放进去。否则模型可能在修复时重新回答问题，导致事实漂移。更可靠的做法是限制修复次数，并在多次失败后中断，而不是无限让模型自我修复。</p>

<h2>正则解析为什么危险</h2>
<p>正则可以提取简单字段，但作为主解析策略很脆。模型多一个空格、换一种引号、先解释后给答案，正则就可能误匹配。尤其在金额、权限、分类、动作命令等关键场景，正则“看起来能用”会制造隐性风险。JSON parser、Pydantic 验证或 provider structured output 更适合作为稳定边界。</p>
<p>这不是说正则永远不能用。它可以作为预处理、日志提取或非关键提示，但不应成为业务契约的唯一守门人。如果你发现正则越来越长，说明输出契约应该升级为结构化 schema。</p>

<h2>Parser 与 tool call 的边界</h2>
<p>工具调用也是结构化输出的一种，但语义不同。tool call 表示模型请求程序执行某个工具；parser 表示程序把模型输出解释为应用数据。不要用 JSON parser 解析一个“请执行退款”的文本后直接退款，除非你已经建立了等价的权限和审计边界。工具调用路径天然带有 tool_call_id、工具 schema 和 ToolMessage 回灌，更适合真实动作。</p>
<p>如果只是分类、摘要、抽取字段，parser 很合适；如果要触发外部系统，工具或图节点更清晰。C 级设计要问：这个结构化结果是“数据”还是“动作请求”？数据可以进入 parser，动作请求通常需要工具边界。</p>

<h2>Schema 不是文档而已</h2>
<p>有些项目把 JSON schema 写在 prompt 里，却不在代码里验证。这样 schema 只是一段愿望，模型一旦偏离，下游仍会接受坏数据。真正的数据契约必须由代码执行：parser 解析，Pydantic 或业务函数验证，失败时阻断。文档能指导模型，验证才能保护应用。</p>
<p>反过来，只验证不提示也不理想。prompt 应清楚告诉模型目标格式，parser 应严格执行，错误处理应反馈可修复信息。提示、解析、验证、修复是一套闭环，不是任意挑一个环节。</p>

<h2>在 RunnableSequence 中定位错误</h2>
<p><span class="mono">prompt | model | parser</span> 失败时，要知道错误来自哪一段。prompt 失败通常是变量缺失；model 失败可能是 provider 错误；parser 失败说明模型返回了不符合契约的内容；验证失败说明结构合法但业务不接受。把所有错误都写成“LLM 调用失败”会浪费排查时间。</p>
<p>RunnableSequence 的好处是每段可以单独 invoke。调试时先运行 prompt 看消息，再用 fake model 给 parser 喂固定坏输出，最后接真实模型。这样你能在不消耗模型调用的情况下复现解析边界，符合可测试的工程习惯。</p>

<h2>C 级排错清单：解析失败时看哪些证据</h2>
<p>解析失败时先保存原始模型输出。没有原始输出，就无法判断是模型没有遵守格式、parser 提取逻辑太窄、prompt 示例误导，还是下游验证过严。原始输出应和 run id、模型名、prompt 版本、parser 名称、schema 版本一起记录。只记录“JSON 解析失败”没有行动价值；记录失败文本和契约，才能改 prompt 或 parser。</p>
<p>第二步区分语法错误、结构错误和业务错误。语法错误是 JSON 不合法；结构错误是合法 JSON 但缺字段或类型错；业务错误是字段都合法但业务不接受，例如金额超过权限。三类错误的处理不同：语法错误可修复格式，结构错误可要求补字段，业务错误通常要拒绝或人工处理。把它们都叫 parse error，会让修复策略混乱。</p>
<p>第三步确认 parser 输入到底是什么。聊天模型返回 AIMessage，StrOutputParser 读取 content；某些 structured output 可能已经返回对象；工具调用结果可能在 tool_calls 而不是 content。如果你把 AIMessage 直接传给 json.loads，或把包含 markdown 解释的 content 当纯 JSON，错误就来自边界误解。每个 parser 都应有明确输入类型预期。</p>
<h2>结构化输出的设计原则</h2>
<p>输出 schema 应尽量小而明确。只要求应用马上需要的字段，不要让模型一次返回十几个“以后可能用”的字段。字段越多，缺失和不一致概率越高，验证和修复成本越大。比如分类任务只需要 category、confidence、reason，就不要再要求 full_analysis、alternative_categories、debug_prompt，除非产品真的使用它们。</p>
<p>字段描述要写给模型看。<span class="mono">score</span> 不如 <span class="mono">confidence: 0 到 1 之间，表示分类置信度</span>；<span class="mono">action</span> 应说明允许枚举和含义。好的 schema 既是解析契约，也是模型生成指南。若字段名来自内部数据库缩写，模型容易误解，parser 即使成功也可能得到语义错误数据。</p>
<p>枚举比自由文本更稳定。若业务只接受 refund、shipping、product、other 四类，就用枚举或明确校验，而不是让模型自由写“物流问题”“快递相关”“运输”。自由文本适合 explanation，不适合作为路由键。路由、权限、动作类型这类字段应尽量封闭。</p>
<h2>修复链的边界</h2>
<p>自动修复不是让模型重新回答问题，而是让它把已有输出改成契约要求的形状。修复 prompt 应包含原始输出、错误原因、schema，并明确“不要添加新事实，不要改变语义，只修复格式”。如果原始输出缺少必要事实，修复不应编造字段，而应失败或请求重试主任务。</p>
<p>修复次数要有限。一次修复失败后，可以再尝试一次；多次失败通常说明 prompt、模型能力或 schema 设计有问题。无限修复会浪费 token，还可能让模型逐步偏离事实。生产链应记录修复次数，并把多次失败的样本纳入评估集。</p>
<p>对于高风险动作，解析成功也不等于可执行。模型返回 <span class="mono">{"action":"refund","amount":100}</span> 只是一个结构化建议；真正退款还需要工具权限、订单状态、人工确认或业务规则。解析器把文本变数据，不把数据变授权。这个边界和工具课的边界是一致的。</p>
<h2>评估解析质量</h2>
<p>解析器质量不能只看成功率，还要看错误是否被正确拒绝。评估集应包含合法输出、坏 JSON、缺字段、字段类型错、枚举越界、模型解释混入 JSON、恶意注入和边界业务值。一个 parser 如果对坏数据过于宽松，短期看成功率高，长期会把错误送入业务层。</p>
<p>还要评估 schema 与 prompt 是否一致。Prompt 要求字段叫 <span class="mono">answer</span>，Pydantic 模型要求 <span class="mono">final_answer</span>，模型会无所适从。示例输出必须和 parser 完全一致，尤其是引号、数组、可选字段和枚举大小写。很多“模型不稳定”其实是契约前后不一致。</p>
<p>最后，把解析器放在 RunnableSequence 中单独测试。给 parser 喂固定字符串，不需要模型；给 prompt 喂输入，不需要 parser；给整条链使用 fake model，不需要网络。这样你能精确知道失败属于哪一层。C 级工程不是迷信端到端，而是在端到端之外建立可定位的小边界。</p>
<p>当解析稳定后，应用代码就可以依赖类型化结果，而不是到处写 if "yes" in text。越早把自然语言收束成数据契约，后面的业务逻辑越普通、越可测、越安全。这就是 output parser 的真正价值。</p>


<h2>课堂复盘：解析器让 AI 输出回到普通软件工程</h2>
<p>没有解析器时，模型输出停留在自然语言世界，业务代码只能用字符串猜测。加上 parser 后，输出变成 dict、对象或明确错误，后续就能使用普通软件工程方法：类型检查、字段校验、单元测试、错误分支、版本迁移和监控。解析器的价值不在于复杂，而在于把不稳定文本尽早收束成可验证边界。</p>
<p>选择解析策略时要看风险。普通展示文本用 StrOutputParser 足够；抽取字段用 JsonOutputParser 或 Pydantic；路由和动作建议使用枚举和严格验证；真实副作用不要只靠 parser，应转入工具或图节点。越接近业务决策，契约越要严格，失败越要显式。宽松解析适合探索，不适合生产关键路径。</p>
<p>解析器还提供评估抓手。你可以统计解析失败率、修复成功率、字段缺失率、业务验证失败率，并按模型、prompt 版本、用户场景分组。这样的指标比“感觉模型不稳定”更可行动。模型输出仍然可能随机，但 parser 把随机性挡在边界外，让应用只接收通过契约的数据。</p>

<h2>延伸练习：把解析结果当作外部输入再验证</h2>
<p>模型生成的数据虽然来自你的系统内部调用，但安全上应按外部输入处理。它可能缺字段、越界、包含注入文本，也可能与业务事实不一致。解析成功只是第一关，后续仍要做业务验证、权限检查和幂等控制。尤其当解析结果会驱动工具或数据库写入时，必须像处理用户提交表单一样严格。</p>
<p>解析器也需要版本意识。Schema 字段改名后，旧 trace、旧缓存、旧评估样本可能仍使用旧格式。可以在结果中加入 schema_version，或在链配置里记录 parser 版本。这样回放和排错时能知道当时使用哪份契约。没有版本，结构化输出一旦演进，历史数据会难以解释。</p>

<h2>最后检查：把概念落到一次真实调用</h2>
<p>完成本课后，请把概念重新放回一次真实调用中验证：输入从哪里来，经过哪个对象标准化，运行时配置如何传播，输出由谁解释，错误在哪里被看见，哪些信息进入 trace，哪些信息进入业务状态。只要能沿着这条线讲清楚，说明你掌握的不是 API 片段，而是可维护的系统边界。</p>
<p>这也是 C 级课程反复强调的学习方法：每个抽象都要回答“它统一什么、它不负责什么、它失败时看什么证据”。抽象不是为了隐藏一切，而是为了让变化集中、证据清楚、责任可定位。后续课程继续读源码时，请始终用这三个问题检查自己的理解。</p>
<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("用几个正则就能稳定解析模型输出。", "正则适合简单辅助，不适合作为关键业务契约；应优先使用 JSON/Pydantic/structured output。"),
    ("模型说是 JSON 就可以直接信任。", "必须由 parser 和验证代码实际解析；格式非法的 JSON 应失败或修复。"),
    ("parser 和 tool call 是一回事。", "parser 解析数据；tool call 请求执行工具，涉及 tool_call_id、权限和 ToolMessage。"),
    ("解析失败时返回空对象更健壮。", "吞掉 parse errors 会让坏数据流向下游，应记录并进入修复、重试或中断。"),
    ("schema 写在 prompt 里就够了。", "schema 必须由代码验证，否则只是模型参考文档。"),
]),
r"""
<h2>小实验：故意破坏 JSON 并观察错误</h2>
""",
shell.lab_card("让 parser 先失败再修复", [
    "准备 JsonOutputParser，并给它输入 \"{'answer': 'ok',}\" 这样的坏 JSON。",
    "确认 parser 抛出解析异常，而不是返回空 dict。",
    "把坏输出改成合法 JSON：{\"answer\":\"ok\"}，确认返回 Python dict。",
    "再加一个 Pydantic 模型，要求 answer 和 confidence 字段，观察缺字段的验证错误。",
    "设计一个修复 prompt，只要求修复 JSON 格式，不允许改变原始事实。"],),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>解析器把模型输出转成应用数据契约，是 prompt 与业务代码之间的类型边界。</li>
    <li>parser、structured output、Pydantic 验证可以组合使用，但失败模式和 provider 依赖不同。</li>
    <li>解析失败必须可观察、可修复或可中断，不能静默吞掉。</li>
    <li>数据解析和动作执行要分开；真实副作用更适合工具 / 图节点边界。</li>
  </ul>
</div>
""",
shell.version_note("本课以 langchain_core.output_parsers、BaseChatModel.with_structured_output 和 RunnableSequence 为锚点。具体 parser 能力会扩展，但“模型输出不等于应用数据，必须解析与验证”的原则长期不变。"),
])


LESSON_11_STREAMING = "".join([
r"""
<p class="lead">Streaming 和 callbacks 让一次运行在发生时就可见。<span class="mono">stream</span> / <span class="mono">astream</span> 让你逐步收到模型 chunk，<span class="mono">astream_events</span> 让你看到链、模型、工具、parser 的事件流，callback handler 和 tracer 则把 run start、token、end、error、tags、metadata、run id 串起来。它们是可观测性边界，不是业务逻辑的隐藏中间件。</p>

<div class="card analogy">
  <div class="tag">🎥 生活类比 · 透明厨房与出餐铃</div>
  普通 invoke 像等服务员端来整盘菜，你只看到最终结果。Streaming 像透明厨房，能看到厨师正在切菜、下锅、装盘；callbacks 像每个工位的出餐铃和记录表，开始、出错、完成都会响。看到过程能提升体验和排错，但你不能因为看见切菜就把半熟食材当成最终菜品。
</div>

<h2>本课地图：从运行开始到结束 / 出错</h2>
<p>流式与回调共同回答一个问题：这次运行现在在哪里？模型是否开始？token 是否到达？工具是否执行？parser 是否失败？run id 是什么？tags 和 metadata 如何关联到用户请求？理解这些事件后，你才能构建实时 UI、日志、LangSmith trace 和可靠错误处理。</p>
""",
shell.lesson_map("运行可观测性的五段", [
    ("run start", "Runnable 或链开始，生成 run id，携带 tags/metadata", "before"),
    ("model start", "聊天模型收到消息，callback 记录输入摘要", "now"),
    ("chunks/events", "token、AIMessageChunk、tool/chain/parser 事件陆续产生", "now"),
    ("end/error", "运行正常结束或错误结束，handler/tracer 收尾", "source"),
    ("UI/trace", "前端渲染、日志、LangSmith 和调试工具消费事件", "after"),
]),
r"""
<h2>源码入口：文件 + 符号名</h2>
<p>读 streaming 与 callbacks 时，要从模型 stream、Runnable events、callback manager、handler 接口和 tracer 五个入口合起来看。单看 stream 只能看到 token；单看 callback 只能看到钩子；合起来才是完整运行可观测性。</p>
""",
shell.source_map([
    {"file": "libs/core/langchain_core/language_models/chat_models.py", "symbol": "BaseChatModel.stream", "role": "聊天模型同步流式入口，返回逐步产生的消息 chunk。", "direction": "模型 wrapper 向上层暴露 token/chunk 流。"},
    {"file": "libs/core/langchain_core/runnables/base.py", "symbol": "astream_events", "role": "Runnable 事件流接口，暴露链、模型、工具等运行事件。", "direction": "上层 UI、日志或调试器消费统一事件。"},
    {"file": "libs/core/langchain_core/callbacks/manager.py", "symbol": "CallbackManager", "role": "管理 callback handlers，分发 start、token、end、error 等事件。", "direction": "运行时把事件广播给观察者。"},
    {"file": "libs/core/langchain_core/callbacks/base.py", "symbol": "BaseCallbackHandler", "role": "用户自定义 callback handler 的基类，定义 on_chat_model_start、on_llm_new_token 等方法。", "direction": "应用实现日志、指标、UI 推送等观察行为。"},
    {"file": "libs/core/langchain_core/tracers/base.py", "symbol": "BaseTracer", "role": "追踪器基类，记录 run 树、时间、输入输出、错误和层级关系。", "direction": "LangSmith 等可观测系统建立 trace。"},
]),
r"""
<h2>状态流：run start → token/chunk → run end/error</h2>
""",
shell.state_flow([
    ("run start", "链或模型开始运行，生成 run_id，读取 tags、metadata、callbacks。", "on_chain_start"),
    ("model start", "聊天模型收到标准消息，callback 可以记录模型名和输入摘要。", "on_chat_model_start"),
    ("token/chunk events", "provider 逐步返回 token 或 AIMessageChunk，stream 产出给调用者。", "on_llm_new_token"),
    ("tool/chain events", "如果链中有工具或子 Runnable，事件树记录每个子运行。", "on_tool_start / on_chain_end"),
    ("run end/error", "成功时收尾并合并最终消息；失败时触发 error 事件并保留证据。", "on_llm_end / on_llm_error"),
]),
r"""
<h2>代码走读：简化版 callback 生命周期</h2>
<p>真实 callback manager 会处理继承 handlers、异步 handlers、run tree、错误传播和 tracing。下面的伪代码保留最常见的四个钩子：模型开始、新 token、模型结束、模型错误。注意 handler 观察事件，不应该偷偷改写核心业务结果。</p>
""",
shell.code_walkthrough(
    "libs/core/langchain_core/callbacks/base.py",
    "BaseCallbackHandler lifecycle",
    '''class PrintingHandler(BaseCallbackHandler):
    def on_chat_model_start(self, serialized, messages, run_id, **kwargs):
        print("model start", run_id, serialized["name"])

    def on_llm_new_token(self, token, run_id, **kwargs):
        print(token, end="", flush=True)

    def on_llm_end(self, response, run_id, **kwargs):
        print("model end", run_id)

    def on_llm_error(self, error, run_id, **kwargs):
        print("model error", run_id, repr(error))

model.invoke(messages, config={"callbacks": [PrintingHandler()]})''',
    "这是教学伪代码：真实回调方法签名会随事件类型携带更多字段，异步场景应使用对应 async 处理。",
),
r"""
<h2>例子追踪：一个流式回答如何产生 chunks 与事件</h2>
""",
shell.trace_table([
    {"step": "1 链开始", "input": "question='解释 Runnable'", "action": "RunnableSequence 生成 run id，发送 chain start 事件。", "output": "on_chain_start / run_id=R1"},
    {"step": "2 模型开始", "input": "格式化后的 messages", "action": "BaseChatModel.stream 调用 provider 流式接口。", "output": "on_chat_model_start / run_id=R2"},
    {"step": "3 chunk 到达", "input": "provider delta='Runnable'", "action": "stream yield AIMessageChunk，同时 callback 收到 token。", "output": "chunk.content='Runnable' / on_llm_new_token"},
    {"step": "4 更多事件", "input": "delta=' 是统一调用协议'", "action": "UI 追加显示，tracer 记录时间顺序。", "output": "多个 chunks 和 events"},
    {"step": "5 收尾", "input": "provider done", "action": "合并最终消息，发送 end；若失败则发送 error。", "output": "final AIMessage / on_llm_end"},
]),
r"""
<h2>stream 与 astream：chunk 不是最终消息</h2>
<p><span class="mono">stream</span> 适合同步代码逐步消费输出；<span class="mono">astream</span> 适合 async WebSocket、SSE 或异步任务。两者都让你更早看到内容，但不保证总耗时更短。网络、provider、工具调用和解析仍决定总时延。流式优化的是“首 token 延迟”和用户感知，不是魔法加速。</p>
<p>chunk 需要合并才能成为最终消息。文本 chunk 可以简单拼接，但工具调用 chunk、结构化输出 chunk、多模态 chunk 可能需要更复杂的合并逻辑。不要在收到第一个 chunk 时就认为模型已经完成，也不要把中间 chunk 写入不可撤销业务状态。UI 可以显示草稿，业务提交要等最终结果和验证。</p>

<h2>astream_events：比 token 更宽的运行事件</h2>
<p>只看 token 不足以调试复杂链。<span class="mono">astream_events</span> 可以暴露链开始、prompt 结束、模型开始、模型 stream、工具开始、工具结束、parser 错误等事件。它适合构建调试面板、实时日志和教学可视化，因为你能看到每个 Runnable 子步骤，而不是只看到模型输出。</p>
<p>事件流也帮助定位卡住位置。如果 UI 长时间没有 token，但事件显示工具正在运行，问题可能是外部 API；如果模型已结束但 parser 报错，问题在输出契约；如果没有 model start，问题可能在 prompt 格式化或上游输入。事件把“慢”拆成可定位阶段。</p>

<h2>callback handlers：观察者，不是业务中间件</h2>
<p>Callback handler 很适合做日志、指标、进度推送、trace 标注和调试打印。它们不适合承载核心业务决策，例如在 <span class="mono">on_llm_new_token</span> 里修改数据库状态，或在 <span class="mono">on_llm_end</span> 里偷偷改变返回值。回调是旁路观察机制，业务逻辑应写在 Runnable、工具或图节点中。</p>
<p>把 callbacks 当 middleware 会制造隐式控制流。阅读链的人看不到 handler 里发生了什么，测试也容易漏掉。生产中应让 handler 幂等、轻量、可失败隔离：日志失败不应让核心回答失败，除非你的合规要求明确规定 trace 写入失败必须中断。</p>

<h2>tags、metadata 与 run IDs</h2>
<p><span class="mono">RunnableConfig</span> 中的 tags 和 metadata 用于给运行打标签，例如 tenant、feature、experiment、request_id。run id 用于关联父子运行和外部日志。良好的标签策略能让 LangSmith 或日志系统按功能、用户组、模型版本筛选 trace。没有标签，线上问题只能靠时间和猜测搜索。</p>
<p>metadata 不是放秘密的地方。它可能进入日志、tracer 或外部可观测平台。不要把 API key、完整用户隐私、原始身份证号放进 metadata。需要关联用户时，使用内部 request id、脱敏 id 或哈希，并遵守你的数据治理规则。</p>

<h2>LangSmith 与 tracer 的角色</h2>
<p><span class="mono">BaseTracer</span> 记录 run 树：哪个链调用了哪个模型，哪个工具失败，耗时多少，输入输出摘要是什么。LangSmith 等平台消费这些 trace，帮助调试、评估和回放。它们不是模型能力的一部分，而是工程可观测性层。没有 trace，Agent 失败时你只能看最终回答；有 trace，你能看见每一步证据。</p>
<p>追踪也要考虑隐私和成本。记录完整 prompt、工具结果和用户输入可能非常有用，也可能泄露敏感信息。生产环境通常需要采样、脱敏、字段过滤和权限控制。C 级设计会把“可观测”和“最小必要数据”一起考虑。</p>

<h2>UI backpressure：显示速度也要被设计</h2>
<p>流式 UI 不只是把 token print 出来。浏览器、终端、WebSocket、SSE 都有缓冲和 backpressure。模型每 20 毫秒来一个 chunk，但前端每个 chunk 都触发重排，可能导致卡顿。实践中常把 chunk 缓冲成小批次刷新，或按句子 / 时间窗口更新。</p>
<p>还要处理用户取消。用户关闭页面或点击停止时，应取消下游 stream、关闭 provider 请求、记录 run canceled 或 error，而不是让后台继续消耗 token。流式体验越好，资源控制越重要。</p>

<h2>错误事件不能忽略</h2>
<p>流式场景中错误可能发生在已经输出一半之后。UI 必须知道这是“完整回答结束”还是“中途失败”。callback 的 <span class="mono">on_llm_error</span>、事件流中的 error、HTTP 连接关闭状态都需要被处理。否则用户可能看到半句话却以为回答完成，业务日志也无法复盘。</p>
<p>工具或 parser 的错误同样重要。模型 token 正常流完，不代表整个链成功；后面的 parser 可能失败，工具可能超时。事件流应覆盖链的每个阶段，最终状态应明确 success、error 或 canceled。生产 UI 应展示可理解的失败提示，而不是永远停在“正在生成”。</p>

<h2>Streaming 与工具调用</h2>
<p>当模型支持工具调用时，流式 chunk 可能逐步给出工具名称和参数片段。不要在参数尚未完整时执行工具。执行器应等待工具调用结构完整、解析和校验通过，再执行真实代码。对于高风险工具，更应等最终消息和审批状态稳定。</p>
<p>如果 Agent 中工具执行时间很长，可以通过 events 告诉 UI“正在查询订单系统”或“正在调用天气服务”。这比让用户只看到空白等待更好，也比伪造模型 token 更诚实。流式可观测性应该反映真实阶段，而不是只追求文字连续。</p>

<h2>从 C 级视角选择接口</h2>
<p>只需要最终回答，使用 invoke；需要逐字显示，使用 stream / astream；需要观察整个链的子步骤，使用 astream_events；需要接入日志或 tracing，使用 callbacks / tracers；需要生产评估和回放，接 LangSmith 或类似系统。接口选择应由观测目标决定。</p>
<p>不要为了“高级”到处打开 streaming。批量后台任务可能更适合 invoke + trace；实时客服 UI 才强烈需要 streaming；调试 Agent 循环时 events 比 token 更有价值。可观测性也有成本，越细粒度越需要数据治理和性能预算。</p>

<h2>C 级排错清单：流式运行卡住时怎么拆</h2>
<p>流式“没有输出”不等于模型没有工作。先看是否收到 run start，再看 prompt 是否完成，再看 chat model start 是否触发，再看 provider 是否返回 chunk，再看 callback 是否阻塞，再看 UI 是否缓冲。若 astream_events 显示工具正在运行，token 空白是正常等待；若连 model start 都没有，问题在上游 prompt 或输入；若 token 到达后 UI 不刷新，问题在前端 backpressure。</p>
<p>流式“输出一半断掉”也要区分 provider 错误、网络断开、用户取消、parser 失败和工具错误。最终状态必须明确 success、error 或 canceled。不要只根据是否收到过 token 判断成功；半句回答加错误事件仍然是失败。UI 应展示“生成中断，可重试”，日志应保留 run id 和已输出片段，业务层不应把半成品当最终结论。</p>
<p>如果 callback 导致变慢，检查 handler 是否做了阻塞 I/O、逐 token 写数据库、同步调用外部服务或打印大量日志。回调应轻量，重工作应入队或批量处理。一个 on_llm_new_token 每个 token 都执行慢操作，会直接拖慢用户看到的速度。可观测性不能反过来压垮被观察对象。</p>
<h2>事件设计与 UI 体验</h2>
<p>好的实时 UI 不只显示 token，还显示阶段：正在理解问题、正在检索、正在调用订单工具、正在生成回答、正在解析结果。token 流适合展示语言生成，events 适合展示任务进度。对于 Agent，工具运行可能占大部分时间，只显示空白会让用户以为系统卡死；展示真实事件能建立信任。</p>
<p>但事件也不能过度暴露内部细节。用户不需要看到完整 prompt、工具参数里的内部 id、数据库错误或堆栈。面向用户的事件应脱敏、翻译成可理解阶段；面向工程师的 trace 可以更详细，但受权限控制。Streaming 和 callbacks 产生很多数据，必须区分用户体验层和调试层。</p>
<p>UI 合并 chunk 时可以按时间窗口或标点刷新，而不是每个 token 都重绘。对 markdown、代码块和 JSON，过早渲染可能造成闪烁或格式错乱。可以在前端保留 raw buffer，周期性渲染安全片段，最终 end 后再做一次完整渲染。流式体验需要产品和工程一起设计，不是简单 for 循环 print。</p>
<h2>run id、metadata 与跨系统关联</h2>
<p>一次用户请求可能穿过前端、后端、LangChain、provider、工具服务和数据库。run id、request id、trace id 的映射要清楚。建议在 RunnableConfig.metadata 中放脱敏 request_id、tenant 或实验组，在应用日志中也记录同一 id。这样线上问题可以从用户反馈跳到 LangSmith trace，再跳到工具服务日志。</p>
<p>metadata 的最小化很重要。为了关联，不需要记录完整邮箱、手机号、身份证或 API key。使用内部不可逆 id 或脱敏值即可。若 trace 平台在第三方环境，还要遵守公司数据策略。可观测性越强，越要尊重数据边界。C 级开发者不仅追求看得见，也要知道哪些不该被看见。</p>
<h2>错误、取消与资源释放</h2>
<p>用户取消生成时，后端应取消 provider 请求或停止消费 stream，释放连接，标记运行取消。若只是前端停止显示、后端继续生成，成本仍在消耗，工具也可能继续执行。对于长工具调用，要考虑取消信号是否能传到工具层；不能取消的工具至少要记录“用户已断开，结果不再发送”。</p>
<p>错误事件也应进入统一收尾路径。无论是 provider error、tool error、parser error 还是 callback error，都要让 run tree 有结束状态。否则 trace 会出现永远 running 的节点，排查时很痛苦。handler 自身失败要特别小心：日志系统短暂不可用不应默认让用户请求失败，除非这是合规强制要求。</p>
<h2>测试 streaming 与 callbacks</h2>
<p>可以用 fake streaming model 产生固定 chunks，测试合并逻辑、UI 事件顺序和取消处理。不要用真实 provider 随机输出测试基础流式框架。callback handler 也可以单独测试：传入假 run id 和 token，断言它写出预期日志或调用队列。事件流测试应覆盖正常结束和错误结束。</p>
<p>对 astream_events，可以记录事件名称序列：prompt_start、prompt_end、chat_model_start、chat_model_stream、chat_model_end、parser_start、parser_end。不同版本名称可能略有变化，但测试思想是检查阶段是否可见。若你的 UI 依赖某些事件名，升级 LangChain 前要跑兼容测试。</p>
<p>最后，明确 streaming 的业务边界：它改善反馈和观测，不改变事实来源，不替代最终解析，不自动处理工具安全。半成品用于显示，最终消息用于回答，验证结果用于业务动作，trace 用于复盘。把这四件事分开，流式系统才既顺滑又可靠。</p>

<h2>课堂复盘：可观测性也是用户 API 的一部分</h2>
<p>Streaming 与 callbacks 看似是内部运行细节，其实直接影响用户体验和生产运维。用户希望知道系统有没有开始、是不是卡住、能不能取消；工程师希望知道慢在哪里、错在哪里、哪个 run 对应哪个日志。把这些需求留到最后补，会发现核心链路没有 run id、没有阶段事件、没有错误收尾，只能靠猜。</p>
<p>设计实时链路时，建议同时定义三层输出：面向用户的进度事件，面向前端的 chunk 数据，面向工程的 trace 事件。三者内容不同、权限不同、保留时间不同。用户事件要简洁脱敏；前端 chunk 要适合增量渲染；工程 trace 要足够定位问题。不要把完整内部事件原样推给用户，也不要只为了用户体验而丢掉工程证据。</p>
<p>最后，流式系统必须尊重最终性。chunk 是草稿，end 是完成，error 是失败，cancel 是用户或系统终止。只有最终状态明确，UI、日志、计费和业务动作才能一致。C 级掌握 streaming，不是会写 for chunk in model.stream，而是能设计一条从运行开始到收尾都可靠的可观测路径。</p>

<h2>延伸练习：定义流式响应的完成协议</h2>
<p>前后端之间最好有明确完成协议，而不是只靠连接关闭。事件可以包含 start、delta、progress、final、error、cancel。final 携带最终文本或最终结构，error 携带可展示错误和内部 run id，cancel 表示用户主动停止。这样前端能区分正常结束、失败和取消，后端也能统一资源释放。</p>
<p>对于需要解析的流式输出，前端看到的文字不一定等于业务最终结果。可以先流式展示模型草稿，等待后端 parser 和验证通过后再发送 final 事件。如果验证失败，UI 应说明“生成内容未通过格式校验”，而不是展示一个看似完成但不能使用的结果。流式体验和最终契约必须同时存在。</p>

<h2>最后检查：把概念落到一次真实调用</h2>
<p>完成本课后，请把概念重新放回一次真实调用中验证：输入从哪里来，经过哪个对象标准化，运行时配置如何传播，输出由谁解释，错误在哪里被看见，哪些信息进入 trace，哪些信息进入业务状态。只要能沿着这条线讲清楚，说明你掌握的不是 API 片段，而是可维护的系统边界。</p>
<p>这也是 C 级课程反复强调的学习方法：每个抽象都要回答“它统一什么、它不负责什么、它失败时看什么证据”。抽象不是为了隐藏一切，而是为了让变化集中、证据清楚、责任可定位。后续课程继续读源码时，请始终用这三个问题检查自己的理解。</p>
<h2>常见误解</h2>
""",
shell.pitfall_grid([
    ("Streaming 会让总生成时间一定更短。", "它主要降低首 token 延迟和改善感知；总耗时仍取决于模型、网络、工具和解析。"),
    ("chunk 就是最终消息。", "chunk 是增量片段，必须合并并等待结束事件后才是稳定结果。"),
    ("callbacks 可以当业务 middleware 用。", "callbacks 是观察者；核心业务逻辑应在 Runnable、工具或图节点中显式表达。"),
    ("日志越全越好，直接记录所有 prompt 和 metadata。", "可观测性必须配合脱敏、采样和权限，避免泄露秘密和用户隐私。"),
    ("只处理正常 end 就够了。", "流式和事件系统必须处理 error、cancel、tool/parser 失败等非成功路径。"),
]),
r"""
<h2>小实验：打印 chunks 和 event names</h2>
""",
shell.lab_card("观察一个小链的运行过程", [
    "构造 prompt | fake streaming chat model | StrOutputParser 这样的小链，避免真实网络依赖。",
    "用 stream 或 astream 打印每个 chunk 的类型和 content，确认它们不是最终完整消息。",
    "用 astream_events 打印 event 名称、name、run_id，观察 prompt、model、parser 的顺序。",
    "添加一个自定义 BaseCallbackHandler，打印 on_chat_model_start、on_llm_new_token、on_llm_end。",
    "故意让 parser 失败，确认 error 事件或异常能被看见并记录。"],),
r"""
<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>stream / astream 暴露模型增量 chunk，astream_events 暴露更完整的 Runnable 运行事件。</li>
    <li>callbacks、CallbackManager 和 tracer 是可观测性机制，应保持旁路、轻量、可审计。</li>
    <li>tags、metadata、run id 让 trace 可关联，但不能记录秘密或未脱敏敏感数据。</li>
    <li>流式 UI 必须处理 backpressure、取消、错误和最终合并，不能把半成品当最终结果。</li>
  </ul>
</div>
""",
shell.version_note("本课以 BaseChatModel.stream、Runnable.astream_events、CallbackManager、BaseCallbackHandler 和 BaseTracer 为锚点。事件字段和平台集成会演进，但“运行开始、增量事件、结束或错误、trace 关联”的可观测性模型稳定适用。"),
])
