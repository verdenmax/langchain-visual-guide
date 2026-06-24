"""C-level Part 5: LangGraph execution engine."""

import shell


def _p(text):
    return f"<p>{text}</p>"


def _h3(title, text):
    return f"<h3>{title}</h3>" + _p(text)


def _section(title, paragraphs):
    return f"<h2>{title}</h2>" + "".join(_p(p) for p in paragraphs)


def _points(items):
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<div class="card keypoints"><div class="tag">✅ 本课要点</div><ul>{lis}</ul></div>'


def _analogy(text):
    return f'<div class="card analogy"><div class="tag">🧩 生活类比</div>{text}</div>'


LESSON_22_PREGEL = (
    r"""
<p class="lead">LangGraph 的执行引擎不是把节点按边递归调用一遍，而是把编译图降到 Pregel/BSP 风格的超步循环里运行。每个超步分成 Plan、Execution、Update 三段：先根据已经可见的 channel 值决定哪些任务被唤醒，再让这些任务并行读取同一份稳定快照并把写入暂存起来，最后统一把写入应用到 channel，生成下一步可见的状态。本课读懂 <span class="mono">Pregel</span>、<span class="mono">prepare_next_tasks</span>、<span class="mono">PregelRunner</span> 与 <span class="mono">apply_writes</span> 的分工，重点掌握“本步写入，下步可见”为什么是确定性、并行和持久化的共同地基。</p>
"""
    + _analogy("把 LangGraph 的一个超步想成学校里的统一考试。监考老师先根据上一节课的通知名单决定哪些学生进入考场，这就是 Plan；所有学生在同一份试卷上同时答题，不能偷看旁边同学刚写下的答案，这就是 Execution；铃声响后老师统一收卷、批改、登记分数，下一节课才会按新分数分班，这就是 Update。如果学生一边答题一边立刻改变别人的试卷，考场就会变成竞态现场；统一收卷让过程慢半拍，却换来公平、可复查和可重放。")
    + shell.lesson_map(
        "本课地图：Pregel/BSP 怎样支撑 LangGraph 执行",
        [
            ("入口对象", "Pregel 是编译图的运行时骨架，对外表现为 Runnable，对内维护通道、节点和循环", "now"),
            ("Plan", "prepare_next_tasks 按 subscribed channels、pending writes 和版本信息挑出本超步要跑的任务", "now"),
            ("Execution", "PregelRunner 调度任务，任务读取稳定快照，把写入交给缓冲区而不是马上改全局状态", "now"),
            ("Update", "apply_writes 把 buffered writes 合并进 channels，推进版本，供下一超步观察", "source"),
            ("调试", "map_debug_tasks / map_debug_task_results / map_debug_checkpoint 把任务、结果和检查点映射成可读 debug 事件", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>读执行引擎不要先追业务节点，而要先锁定文件 + 符号名：入口对象在哪里，任务如何被计划，写入何时被应用，调试输出从哪里拿数据。行号会随 LangGraph 版本变化，符号和模块边界更适合作为长期锚点。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/pregel/main.py", "symbol": "Pregel", "role": "编译后图的底层运行时，封装 invoke、stream、状态读取、checkpoint、interrupt 等能力", "direction": "用户调用 CompiledStateGraph，最终进入 Pregel 的步骤循环"},
            {"file": "langgraph/pregel/_algo.py", "symbol": "prepare_next_tasks", "role": "Plan 阶段核心，根据哪些 channel 有新版本、哪些节点订阅它们，构造下一批内部 PregelExecutableTask，并在 debug/state 视图中映射为公开 PregelTask 快照", "direction": "每个超步开始时读取当前 checkpoint/channel 版本，输出待运行任务"},
            {"file": "langgraph/pregel/_algo.py", "symbol": "apply_writes", "role": "Update 阶段核心，把任务产生的 writes 按 channel 规则合并并更新版本", "direction": "任务全部结束后统一调用，产生下一步可见状态"},
            {"file": "langgraph/pregel/_runner.py", "symbol": "PregelRunner", "role": "Execution 阶段调度器，负责运行任务、收集写入、处理重试和异常边界", "direction": "接收 plan 出来的任务列表，驱动节点代码执行"},
            {"file": "langgraph/pregel/debug.py", "symbol": "map_debug_tasks / map_debug_task_results / map_debug_checkpoint", "role": "debug stream 映射工具，把 task、task result 与 checkpoint 变化转换成可读事件", "direction": "stream/debug 模式下帮助观察超步内部发生了什么"},
        ]
    )
    + r"""
<h2>状态流：一个超步的三段式</h2>
"""
    + shell.state_flow(
        [
            ("Plan：订阅关系选任务", "运行时查看上一超步已经提交的 channel 版本。某个节点订阅的输入 channel 发生变化，且该节点没有被中断或等待，prepare_next_tasks 就为它创建内部 PregelExecutableTask；对外的 StateSnapshot/debug 事件再把执行结果投影成 PregelTask。", "visible channels: messages@v3 -> task:model"),
            ("Execution：任务读稳定快照", "PregelRunner 让本批任务读取同一份已提交状态。任务可以并行运行，看到的是上一步结果，而不是同批其他任务刚产生的半成品。", "model reads messages@v3, tools reads tool_calls@v1"),
            ("Buffer：写入先进入暂存区", "节点返回 partial state 或 ChannelWrite 后，写入被记录为 task writes。此时 channel 当前值尚未改变，因此并行任务之间不会互相污染。", "writes=[('messages', AIMessage), ('next', 'tools')]"),
            ("Update：统一合并写入", "所有任务结束后 apply_writes 按 channel/reducer 规则合并写入，更新 channel 版本，并把 checkpoint 所需信息整理好。", "messages@v4, next@v2"),
            ("下一步：新版本触发新计划", "下一轮 Plan 才能看到 v4/v2。调试输出把 step n 的 tasks 与 step n+1 的可见状态分开，避免误判。", "prepare_next_tasks(channels@new_versions)"),
        ]
    )
    + r"""
<h2>Trace：一次图步骤如何从订阅到提交</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. step=4 plan", "input": "messages channel 已在 step=3 更新，model 节点订阅 messages", "action": "prepare_next_tasks 发现 model 的触发条件满足，构造 PregelExecutableTask(name='model')", "output": "本批任务=[model]"},
            {"step": "2. run model", "input": "model 读取 messages@v3 和配置", "action": "PregelRunner 调用节点函数，模型决定调用 search_order 工具", "output": "task writes 暂存 messages+=AIMessage(tool_calls=[...])、branch='tools'"},
            {"step": "3. no immediate visibility", "input": "同一超步内仍是 messages@v3", "action": "若还有并行任务，它们看不到 model 刚写的 AIMessage", "output": "避免同批任务因调度先后不同而结果不同"},
            {"step": "4. update phase", "input": "buffered writes from model", "action": "apply_writes 调用 messages channel 的更新逻辑，写入 checkpoint 元数据", "output": "messages@v4、branch@v2 成为下一步可见值"},
            {"step": "5. step=5 plan", "input": "branch='tools' 已提交，tools 节点订阅该分支", "action": "下一轮 Plan 选择 tools 任务", "output": "工具节点在下一超步运行"},
        ]
    )
    + r"""
<h2>简化源码走读：Pregel 主循环</h2>
"""
    + shell.code_walkthrough(
        "langgraph/pregel/main.py",
        "Pregel",
        """while loop_not_done:
    tasks = prepare_next_tasks(checkpoint, channels, versions)
    if not tasks:
        break

    writes = runner.tick(tasks, channel_snapshot=channels)

    apply_writes(checkpoint, channels, writes)
    save_checkpoint_if_configured(checkpoint)
""",
        "教学版只保留 Plan/Execution/Update 的骨架。真实实现还要处理 stream 模式、interrupt、retry、checkpoint 命名空间、任务缓存、debug 输出和配置合并；但核心不变：计划使用已提交状态，执行产生暂存写入，更新阶段统一提交。",
    )
    + _section(
        "为什么一定要延迟写入",
        [
            "LangGraph 允许多个节点在同一超步并行运行。并行的前提不是“大家跑得快”，而是“大家看到的世界一致”。如果 A 节点刚写入 messages，B 节点立刻读到这个半成品，而另一次运行中 B 先执行没有读到它，那么同样输入会因为线程调度不同得到不同结果。BSP 的屏障把这种不确定性切断：同批任务只读上一轮已提交快照，写入统一进入缓冲区，屏障之后才对下一轮可见。",
            "这个规则也解释了为什么 trace 里常出现“节点已经返回了更新，但下一个节点还没马上看到”。这不是 bug，而是运行时故意保留的时间边界。把它理解成数据库事务里的提交点会更自然：事务中途的私有修改不会随便暴露给其他事务，只有提交后才成为公共事实。LangGraph 的公共事实就是 channel 当前值和版本。",
            "确定性带来的第二个收益是 checkpoint。只要每个超步的输入快照、任务列表、写入集合和合并规则明确，运行时就能把某一步存下来，之后从同样的 checkpoint 恢复。若任务之间可以随时读写共享 dict，checkpoint 只能记录一个混乱瞬间，无法说明哪些写入已经被其他任务观察过。延迟写入让存档边界和执行边界对齐。",
        ],
    )
    + _section(
        "Plan 阶段读什么",
        [
            "Plan 阶段不是重新遍历用户写的所有边，也不是简单按拓扑排序跑节点。编译后的图会把节点输入、订阅 channel、触发条件、分支写入和状态 key 映射到底层 Pregel 节点。prepare_next_tasks 关注的是：哪些 channel 从上次该节点运行后变了，哪些 pending sends 或 branch 需要展开，哪些任务因为 interrupt、错误或完成状态不能继续。",
            "这就是为什么学习 LangGraph 时要把“节点订阅什么 channel”放进脑子里。StateGraph 的节点看似只接收一个 state 参数，但编译后会变成读若干 channel 的 PregelNode。某个 channel 有新版本，订阅它的节点才可能被唤醒；没有新版本就不应重复执行，否则图会无意义空转。",
            "Plan 阶段还承担递归上限的守门作用。很多 Agent 图包含 model -> tools -> model 的环，如果模型一直请求工具，图可以无限推进。recursion_limit 在运行时不是限制 Python 递归深度，而是限制超步推进次数：超过上限说明控制流没有按预期收敛，需要停止并暴露错误。",
        ],
    )
    + _section(
        "Execution 阶段如何看节点",
        [
            "执行阶段的任务并不等于用户写的一个函数调用那么简单。这里要区分两个名字：公开/调试视角的 PregelTask 是 StateSnapshot、tasks/debug stream 里给人看的快照，字段偏向 id、name、path、error、interrupts、state、result；内部真正交给 Runner 的是 PregelExecutableTask，它才携带 input、proc、writes、config、triggers、retry_policy、cache_key、timeout 等执行上下文。PregelRunner 负责把这些可执行任务交给对应节点，同时维护写入收集器。节点可以返回 partial state，也可以通过内部 write 原语写 channel；无论形式如何，最后都被归一成“某任务向某 channel 写了某值”。",
            "这里要避免一个常见误解：节点返回后，state 对象不会被就地改成新状态再传给同批其他节点。用户代码里最好也不要依赖原地修改输入 dict。健康的节点像纯函数：读取本步快照，返回自己负责的增量。副作用工具当然可能访问外部世界，但对图状态的贡献仍应通过写入缓冲区表达。",
            "Runner 也是错误边界。节点抛异常、请求 interrupt、触发重试或被取消，都要转成运行时可理解的状态。只有这样 stream/debug/checkpoint 才能用统一方式描述失败发生在哪个 task，而不是只看到一段散乱 Python traceback。",
        ],
    )
    + _section(
        "Update 阶段为什么是 channel 的世界",
        [
            "apply_writes 不是简单 dict.update。不同 state key 背后可能是 LastValue、Topic、BinaryOperatorAggregate 或消息 reducer 等 channel。写入同一个 key 时，运行时必须调用该 channel 的 update/合并逻辑：有的只允许单写，有的会追加列表，有的会按消息 id 替换，有的会把多个并行结果聚合。",
            "这也是上层 reducer 与底层 channel 统一的地方。用户在 schema 上标注 reducer，看起来是在写类型提示；编译后它会影响对应 channel 怎样处理多个写入。理解这一点后，很多错误会变得可解释：并行节点同时写无 reducer 的 key 会冲突，不是运行时小气，而是它不知道两个值该如何合并。",
            "Update 阶段还会推进版本。版本号让 Plan 阶段知道某个节点上次看到的是哪个 channel 版本，也让 checkpoint 可以记录每个 channel 的变化历史。没有版本，图只能知道“现在是什么值”，无法高效判断“谁因为哪个变化应该再跑”。",
        ],
    )
    + _section(
        "调试时如何读 map_debug_* 事件",
        [
            "debug 输出的价值在于把黑盒运行拆成超步。map_debug_tasks 会描述本步任务，map_debug_task_results 会描述任务结果，map_debug_checkpoint 会描述 checkpoint 变化。你应该按 step 阅读：先看本步计划了哪些 tasks，再看每个 task 的输入和输出，再看 writes 如何被应用。不要只看最终 state；最终答案错误时，真正的原因可能是上一步选择了错误节点，也可能是本步多个写入合并方式不对。",
            "当你看到某个节点“晚一步”才响应上一个节点的输出，不要急着怀疑路由函数。先问：这个输出是不是刚在本超步产生？如果是，它本来就只能触发下一超步。LangGraph 的时间模型是离散步，不是连续回调链。用连续调用链的直觉读 Pregel trace，最容易把正常屏障误判为延迟。",
            "另一个调试技巧是记录 channel 版本而不只是值。值一样但版本变了，说明有写入发生；值变了但预期节点没跑，说明订阅或触发关系可能没有连上；同一版本被重复观察，说明图可能在等待 interrupt 或无新任务可计划。版本把“为什么跑/不跑”从猜测变成证据。",
        ],
    )
    + _section(
        "工程复盘：把超步当成调试坐标系",
        [
            "实际排查 LangGraph 问题时，最有用的记录格式不是一大段自然语言日志，而是一张按超步编号展开的表。每一行都写 step、planned tasks、每个 task 的输入摘要、buffered writes、apply_writes 后的 channel 版本。这样做的好处是把“模型为什么没看到工具结果”这类模糊问题，转成“工具结果是在 step=4 才提交，所以 model 要到 step=5 才能读取”的可验证事实。团队协作时，大家也能围绕同一个时间坐标讨论。",
            "如果图里出现循环，超步坐标系更重要。model、tools、model、tools 看起来像重复节点名，但它们分别属于不同 step，读取的 channel 版本也不同。一个工具结果在第二轮被覆盖，和第一轮从未写入，是两种完全不同的问题。只看节点名会把它们混在一起；看 step 与版本能把循环展开成时间线。",
            "超步视角还能帮助设计测试。你不一定要测试 Pregel 内部函数，但可以构造一个小图，让两个节点并行写不同 key，断言下游节点在下一步才看见合并结果；再构造两个节点并行写同一个无 reducer key，断言运行时暴露冲突。这样的测试不是测实现细节，而是锁定用户可观察的执行语义。",
            "很多性能问题也要先从超步读起。如果一个图每次只计划一个很小任务，明明可以并行的检索却被串成多轮，问题可能在依赖关系设计过细；如果一个超步计划了几十个任务但 Update 阶段频繁冲突，问题可能在 channel 合并语义过粗。优化不是盲目加并发，而是看哪些任务真的独立、哪些合并真的明确。",
            "Plan 阶段的错误通常表现为节点没跑或跑太多。节点没跑时，检查它订阅的 channel 是否真的更新、branch 名称是否匹配、条件边是否返回合法目的地。节点跑太多时，检查是否有不必要的 channel 写入让版本持续变化，或者 reducer 每次都产生新值导致订阅者被反复唤醒。Plan 问题不要先改节点业务逻辑，先看触发证据。",
            "Execution 阶段的错误通常表现为任务失败、输入不符合预期或副作用重复。这里要看 task 的输入快照，而不是节点里打印的某个局部变量。输入错说明上游或 mapper 错；输入对输出错才说明节点实现错；输出对但后面状态错，则问题转到 Update。把三阶段分清，能避免把所有锅都甩给模型或工具。",
            "Update 阶段的错误通常表现为字段被覆盖、列表顺序奇怪、消息重复或多写冲突。此时要回到 channel 类型和 reducer。一个 state key 如果承担了多种语义，下游迟早会困惑；一个 reducer 如果没有处理去重、排序或冲突，下游就会吃到不稳定输入。Update 阶段的问题最适合通过缩小 state key 和明确合并策略解决。",
            "版本号是被很多初学者忽略的线索。值不变但版本变化，说明有任务写了等价值，可能造成不必要唤醒；值变化但订阅节点没跑，说明订阅关系或版本记录异常；版本持续推进但业务没有进展，说明图可能在空转。调试输出如果能带上版本，定位效率会明显提高。",
            "在文档和代码注释里，也建议用“本超步可见”和“下一超步可见”这样的词，而不是简单说“更新 state”。前者提醒读者有屏障，后者容易让人误以为同步函数调用一样立即生效。团队统一术语后，很多关于中断、恢复和并行的争论会自然减少。",
            "最后，把 Pregel 理解为工程约束而不是学术名词。你不需要实现一个图计算系统，但要接受它规定的时间模型：选择任务、运行任务、提交写入。只要这个模型站稳，LangGraph 的持久化、调试、时间旅行和人审都能落到同一套语言里。",
        ],
    )
    + r"""
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("Pregel 只是内部实现细节，写业务图不用懂", "不用背源码，但必须懂超步可见性，否则会误判并行、checkpoint 和调试输出。"),
            ("节点返回值会立刻被下一个节点读到", "只有进入下一超步后，apply_writes 已提交的 channel 值才会被新的任务读取。"),
            ("Plan 就是按边的顺序从前往后执行", "Plan 根据 channel 版本、订阅关系、branch/send 和等待状态选择任务，不是简单拓扑遍历。"),
            ("并行越多越好", "并行任务必须有可合并写入和清晰副作用边界，否则会把冲突留到 Update 阶段。"),
        ]
    )
    + _section(
        "实践提示：把引擎规则落到代码评审",
        [
            "评审 LangGraph 图时，可以要求作者说明每条边跨越的是哪个超步，而不是只说“然后会执行某节点”。如果作者无法说明某个节点何时看见上游写入，就说明执行心智还不牢。",
            "还可以要求每个并行区域列出读写 channel。读写表能提前暴露竞态和无 reducer 多写，比上线后从 trace 里挖冲突更便宜。",
            "对循环图，要标明终止条件和 recursion_limit 的业务含义。上限不是修复无限循环的根因，只是最后保险；真正的终止应来自状态满足完成条件。",
            "对需要恢复的图，要说明每个超步提交后是否足以继续。若某个节点把关键上下文藏在局部变量或外部临时文件里，checkpoint 就无法完整恢复。",
            "对调试日志，要避免只打印节点开始和结束。更有用的是打印 step、task、writes 和 channel 版本，这些信息能直接对应 Pregel 三阶段。",
            "当团队成员抱怨“为什么不能立即读到刚写的值”时，可以回到本课的考试类比：不允许偷看同场答卷，是为了保证结果不依赖座位和交卷顺序。",
            "一旦把超步当成基本单位，很多设计会自然变清楚：顺序依赖用下一步表达，并行独立用同一步表达，合并语义用 channel 表达。",
            "因此，懂 Pregel 不是为了炫耀内部知识，而是为了在评审、测试、排障和性能优化时有同一把尺子。",
        ],
    )
    + shell.lab_card(
        "手工模拟一个超步",
        [
            "画三个 channel：messages、tool_calls、answer，并标出每个 channel 当前版本。",
            "假设 model 订阅 messages，tools 订阅 tool_calls，写出 step n 的 prepare_next_tasks 会选谁。",
            "让 model 返回 AIMessage 和 tool_calls，但先不要改 channel；把它们写进 buffered writes。",
            "执行 apply_writes 后再重新计划 step n+1，观察 tools 为什么现在才被选中。",
            "把同一流程改成两个并行节点都写 answer，思考没有 reducer 时 Update 应如何报错。",
        ],
    )
    + shell.version_note("本课按 LangGraph v1 时代的 Pregel 运行时心智模型讲解。具体函数参数、debug 文本和 checkpoint 字段会随版本演进，但 Plan/Execution/Update、channel 版本和 buffered writes 的核心语义是阅读新版源码时最稳定的线索。")
    + _points(
        [
            "Pregel/BSP 把图执行拆成离散超步，屏障让同批任务读取同一份稳定快照。",
            "prepare_next_tasks 属于 Plan，PregelRunner 属于 Execution，apply_writes 属于 Update。",
            "“本步写入，下步可见”牺牲一点即时性，换来确定性、可并行、可 checkpoint 和可重放。",
            "调试 LangGraph 时要按 step、task、write、channel version 阅读，而不是只看最终输出。",
        ]
    )
)


LESSON_23_TASKS_CHANNELS = (
    r"""
<p class="lead">上一课把 LangGraph 执行看成超步循环，本课进一步拆开超步内部的基本零件：公开的 <span class="mono">PregelTask</span> 是 StateSnapshot/debug 面向观察者的任务快照，内部的 <span class="mono">PregelExecutableTask</span> 才是 Runner 调度的可执行工作；<span class="mono">BaseChannel</span> 是状态在运行时的存储与合并边界，<span class="mono">ChannelWrite</span> 把节点返回值归一成写入，<span class="mono">PregelNode</span> 把用户节点包装成能读 channel、写 channel 的运行时节点。理解 Tasks 与 Channels，才能解释 fan-out 为什么能并行，fan-in 为什么需要 reducer，以及两个任务写同一 key 时到底谁说了算。</p>
"""
    + _analogy("把图运行想成一家报社。每个记者真正拿到的采访单像 PregelExecutableTask，里面有采访对象、截止时间、编辑要求和交稿通道；总编看板上的进度卡像公开 PregelTask，只记录任务编号、记者名、路径、是否出错和最终稿件摘要。不同栏目版面就是 channel，例如头版、财经版、评论版；记者写完稿件不会直接冲进印刷机改版面，而是把稿件交给编辑部的收件箱，这就是 ChannelWrite；同一栏目收到多篇稿件时，编辑规则决定是只放最后一篇、按顺序拼接，还是因为冲突退稿。")
    + shell.lesson_map(
        "本课地图：任务、通道与写入如何协作",
        [
            ("PregelTask", "内部真正调度的是 PregelExecutableTask；公开 PregelTask 主要是 StateSnapshot/debug 面向观察者的任务快照", "now"),
            ("BaseChannel", "每个 state key 编译成 channel，channel 负责保存值、判断可读、应用更新", "now"),
            ("读取", "PregelNode/local_read 让节点看到本超步的稳定 channel 快照", "source"),
            ("写入", "ChannelWrite 把 partial state、branch、send 等输出变成标准化 writes", "now"),
            ("合流", "并行写不同 channel 很自然，写同一 channel 必须有明确 reducer 或冲突策略", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>本课继续用文件 + 符号名定位证据。把 types、channels、read/write 和 algo 连起来看，会发现 LangGraph 的“状态”不是一个普通 dict，而是一组带更新协议的 channel；节点也不是直接被调用，而是被包装成会读写 channel 的 PregelNode。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/types.py", "symbol": "PregelTask / PregelExecutableTask", "role": "PregelTask 是公开/调试快照，含 id、name、path、error、interrupts、state、result；PregelExecutableTask 才携带 input、writes、config、triggers、retry、cache 等执行上下文", "direction": "prepare_next_tasks 构造内部可执行任务，StateSnapshot/debug 再暴露公开任务视图"},
            {"file": "langgraph/channels/base.py", "symbol": "BaseChannel", "role": "所有 channel 的抽象基类，定义值的读取、更新、检查点复制和生命周期", "direction": "State schema/reducer 编译后落到具体 channel 实现"},
            {"file": "langgraph/pregel/_algo.py", "symbol": "local_read", "role": "让任务在执行期读取局部可见的 channel 值，同时尊重本步可见性规则", "direction": "PregelNode 或运行时读 state 时使用"},
            {"file": "langgraph/pregel/_write.py", "symbol": "ChannelWrite", "role": "把节点返回、branch、send、特殊写入统一成 channel write entries", "direction": "节点执行后进入 buffered writes，再由 apply_writes 应用"},
            {"file": "langgraph/pregel/_read.py", "symbol": "PregelNode", "role": "把用户节点包装成可订阅 channel、可读取输入、可产出 writes 的 Pregel 运行时节点", "direction": "编译后的节点对象由 Plan 选择、Runner 调用"},
        ]
    )
    + r"""
<h2>调用图：从用户节点到 channel write</h2>
"""
    + shell.call_graph(
        [
            ("StateGraph node", "用户写的函数：State -> partial State", False),
            ("PregelNode", "编译包装：声明订阅哪些 channel、怎样读输入", True),
            ("PregelExecutableTask", "Plan 阶段生成：本超步要执行的内部任务，之后映射为公开 PregelTask 快照", True),
            ("ChannelWrite", "Execution 后归一：把返回值转成写入条目", True),
            ("BaseChannel.update", "Update 阶段合并：决定 fan-in 的语义", False),
        ]
    )
    + r"""
<h2>Trace：两个并行任务写不同/相同 channel</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. plan fan-out", "input": "question channel 更新，extract_keywords 与 classify_intent 都订阅 question", "action": "prepare_next_tasks 生成两个 PregelExecutableTask", "output": "tasks=[keywords, intent] 可并行"},
            {"step": "2. parallel writes", "input": "两个任务都读取 question@v1", "action": "keywords 写 keywords channel，intent 写 intent channel", "output": "writes=[('keywords', ['退款']), ('intent', 'refund')]"},
            {"step": "3. update different", "input": "写入目标不同", "action": "apply_writes 分别调用两个 channel 的 update", "output": "keywords@v2、intent@v2，无冲突"},
            {"step": "4. same channel fan-in", "input": "retrieve_a 与 retrieve_b 并行写 documents channel", "action": "若 documents 有 list reducer，则两个结果被聚合；若是 LastValue，则多写会冲突", "output": "documents=[docA, docB] 或 InvalidUpdate"},
            {"step": "5. next consumer", "input": "ranker 订阅 keywords、intent、documents", "action": "下一超步读取已合并结果", "output": "ranker 得到完整 fan-in 输入"},
        ]
    )
    + r"""
<h2>简化源码走读：节点读写如何归一</h2>
"""
    + shell.code_walkthrough(
        "langgraph/pregel/_read.py",
        "PregelNode",
        """class PregelNode:
    def run(self, task, channels):
        state = local_read(channels, self.subscriptions)
        result = self.user_func(state)
        return ChannelWrite.from_partial_state(result)

class BaseChannel:
    def update(self, values):
        raise NotImplementedError
""",
        "真实代码更复杂：读输入可能包含 mapper、config、managed values、branch 和 send；写入也会区分普通 channel、特殊控制写入和隐藏元数据。教学版强调同一个事实：节点读的是 channel 快照，返回会被标准化成 writes，合并由 channel 决定。",
    )
    + _section(
        "PregelTask 不是业务节点本身，也不是内部执行对象",
        [
            "用户常说“运行某个节点”，但运行时更准确的单位是任务；同时还要分清公开视图和内部视图。公开的 PregelTask 出现在 StateSnapshot.tasks、checkpoint/debug 输出中，像一张任务快照：它强调 id、name、path，以及失败、interrupt、子图 state、result 等便于观察和恢复的信息。它不是用户节点函数，也不等同于 Runner 手里正在执行的完整对象。",
            "内部可执行对象是 PregelExecutableTask。prepare_next_tasks 会根据 send、订阅变化、路径和配置生成它；它携带 input、proc、writes deque、config、triggers、retry_policy、cache_key、writers、subgraphs、timeout 等上下文。PregelRunner 消费的是这种更丰富的任务对象，才能调用节点、收集写入、应用重试/缓存/超时策略。",
            "区分这两层可以避免调试误判。看到 debug 里的 PregelTask 时，应把它当成对外报告：哪一个 task 在哪个 path 上失败、产生了什么 result 或 interrupt；追执行语义时，则回到 PregelExecutableTask 和 Runner。动态 fan-out 下同一个节点定义可以生成多个内部可执行任务，最终又各自留下对应的公开快照。",
        ],
    )
    + _section(
        "Channel 是状态 key 的执行形态",
        [
            "State schema 让用户觉得自己在声明一个 TypedDict 或 Pydantic 字段；编译后，每个 key 都要落到一个 channel。channel 持有当前值，知道空值是否可读，知道多个 update 应该如何合并，也知道怎样复制到 checkpoint。它既是存储单元，也是并发控制单元。",
            "LastValue channel 适合单写语义，例如最终路由标签、当前草稿、审批结果。聚合类 channel 适合多写语义，例如多个检索器返回 documents、多个工具返回 observations、多个子任务返回局部分析。消息 reducer 适合聊天历史，因为它不仅追加，还要按消息 id 替换。",
            "因此设计 state 时，不要只问字段类型是什么，还要问并行写入时语义是什么。如果将来可能 fan-in，就应在 schema 上给出 reducer；如果业务上只允许一个写入者，就让 LastValue 的冲突暴露错误。沉默覆盖是最危险的默认，因为它会把竞态伪装成正常输出。",
        ],
    )
    + _section(
        "local_read 的边界",
        [
            "local_read 这个名字容易让人误会：它不是给你读任意全局状态的后门，而是在任务执行上下文内读取本步允许看到的 channel 值。它必须尊重 Pregel 可见性：本批任务已经产生但尚未提交的写入，不应突然出现在另一个并行任务的输入里。",
            "在某些内部场景中，运行时需要让任务看到自己的局部写入或特定 managed value，这些属于受控例外。作为业务作者，最稳的心智仍是：节点读进入本超步前已经提交的 state，返回 partial state，等待下一超步被别人读到。这个简化模型能覆盖绝大多数调试问题。",
            "当你发现节点读不到刚刚写的值，先检查它是否在同一超步内。如果是，应该把依赖拆到下一步或通过图边表达。不要用共享可变对象绕过 channel，因为那会破坏 checkpoint 和 replay。",
        ],
    )
    + _section(
        "fan-out 与 fan-in 的设计规则",
        [
            "fan-out 的目标是把一个问题拆成多个独立任务。例如用户问题可以同时进入意图分类、关键词抽取和安全检查；一个检索请求可以发给多个 retriever；一个计划可以分配给多个子 agent。fan-out 健康的前提是这些任务读同一份快照，且不会依赖彼此本步产物。",
            "fan-in 的目标是把多个结果重新合并。合并时必须回答三个问题：结果是否有顺序要求，重复项如何去重，失败的一支是否影响整体。如果这些问题没有答案，简单把所有结果 append 到列表也只是把复杂性推迟到下游节点。好的 reducer 应该承载业务语义，而不是只为了让密度检查或并行执行通过。",
            "写不同 channel 的并行任务通常最安全，因为每个任务拥有自己的输出边界。写同一 channel 时要格外谨慎：如果是消息历史，用 add_messages；如果是数值统计，用加法 reducer；如果是候选文档，用列表聚合后再排序；如果是唯一决策，就不该允许多写，冲突应尽早失败。",
        ],
    )
    + _section(
        "调试冲突写入",
        [
            "InvalidUpdate 或类似冲突错误通常不是运行时坏了，而是 schema 没有表达并行写入语义。调试时先看 trace_table：哪些 task 在同一 step 写了同一个 channel？它们是否本来就应该并行？如果不应该，说明边或触发条件设计错了；如果应该，说明 channel 需要 reducer。",
            "第二步看写入内容是否真的同类。两个检索器都写 documents，可以聚合；一个节点写字符串摘要，另一个节点写文档对象，却都写 answer，就说明 state key 命名太粗。把 key 拆成 draft_answer、retrieved_docs、final_answer，往往比写一个复杂 reducer 更清楚。",
            "第三步看下游消费方式。下游如果只关心最终最佳结果，可以让 fan-in 先聚合候选，再由 ranker 单独写 final_answer。不要让多个上游直接争夺 final_answer；最终决策应该集中在一个可审计节点里。",
        ],
    )
    + _section(
        "工程复盘：用 channel 设计状态边界",
        [
            "设计 LangGraph state 时，最容易犯的错误是先列业务字段，再等冲突发生才补 reducer。更稳的方法是对每个字段回答四个问题：谁会写它，是否可能同一超步多写，多个值的合并是否有业务含义，下游是否依赖顺序。能回答清楚，channel 类型就自然浮现；回答不清楚，就说明字段边界还太粗。",
            "例如 documents 看似只是 List[Document]，但并行检索时它承载了来源、得分、去重和排序语义。如果两个 retriever 都写 documents，简单列表拼接会把来源顺序误当相关性顺序。更好的做法是让每个 retriever 写带 source 和 score 的候选，再由 ranker 节点统一排序并写 ranked_documents。这样 fan-in 的合并和最终决策分开，trace 也更清楚。",
            "再看 final_answer。它通常不应该被多个并行节点同时写，因为最终答案代表一次单一决策。如果多个节点都能写 final_answer，说明你把候选答案和最终答案混在一起了。可以拆成 candidate_answers 列表 channel，再由 judge 或 finalizer 单写 final_answer。冲突错误在这里是朋友，它逼你澄清决策责任。",
            "消息 channel 也需要特别小心。add_messages 的价值不是简单 append，而是按消息 id 替换或追加，适合工具调用与模型响应交织的聊天历史。如果你用普通列表加法替代它，可能在重试、恢复或人工修改时产生重复消息。对话历史是审计材料，合并规则必须比普通列表更严谨。",
            "local_read 的稳定快照语义让任务更像读数据库事务，而不是读共享内存。一个任务不应假设自己能看到另一个同批任务刚写的结果。如果你确实需要顺序依赖，就把两个动作拆到不同超步，用边和 channel 表达依赖。用共享对象偷看半成品会让 replay 和 checkpoint 失去意义。",
            "任务粒度也要服务 channel 设计。一个节点如果同时写十个不相关 channel，下游很难判断哪个变化触发了哪条路径；一个节点如果只做微不足道的字符串清理，又会制造过多 step。合理粒度是一次业务上可命名、可失败、可重试、可观察的动作。它的输出 channel 应该体现这个动作的责任。",
            "fan-out 不是免费午餐。每个分支都可能调用模型、工具或外部服务，产生成本和失败面。并行前要确认分支之间真的独立，且失败策略明确：一个检索器失败是否继续，安全检查失败是否短路，某个子 agent 超时是否保留其他结果。没有失败语义的 fan-out，只是把错误并行放大。",
            "fan-in 则是业务判断的集中地。合并不是把数据堆在一起，而是选择一种解释：并列证据、投票、最高分、最近值、人工优先、模型优先。不同解释应写进 reducer 或后续聚合节点。否则下游模型会收到混杂输入，只能用概率猜测哪条更可信。",
            "调试任务与 channel 时，建议画一张矩阵：行是 tasks，列是 channels，格子标出 read/write。矩阵能立刻暴露两个问题：某任务读取了不该依赖的 channel，或者多个任务写了同一 channel 但没有合并规则。这比在代码里搜索 state key 更直观。",
            "最终要记住，LangGraph 的状态不是共享垃圾桶，而是一组有协议的通信通道。节点之间通过 channel 传递事实，通过 reducer 处理并发，通过 task trace 保留来源。把这三者设计清楚，图会更容易测试、恢复和解释。",
        ],
    )
    + r"""
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("PregelTask 等同于节点函数", "节点是定义；公开 PregelTask 是调试/快照视图，内部 PregelExecutableTask 才是某次运行的可执行实例。"),
            ("State 就是普通 dict", "编译后 state key 由 channel 管理，channel 决定读取、更新、冲突和 checkpoint 行为。"),
            ("并行写同一 key 会自动选择一个", "无 reducer 的多写应失败；有 reducer 才能表达列表追加、消息合并或数值聚合。"),
            ("ChannelWrite 只是语法糖", "它是节点返回值进入 Pregel 写入缓冲区的标准化边界，影响 debug、checkpoint 和合并。"),
        ]
    )
    + _section(
        "实践提示：从小图验证 channel 语义",
        [
            "学习 tasks 与 channels 最快的方法，是写三个只有假数据的小节点，而不是直接调真实模型。一个输入节点写 question，两个并行节点分别写 keywords 和 intent，一个下游节点读取两者。先确认不同 channel 并行写没有冲突。",
            "第二步让两个并行节点都写 documents，并给 documents 加列表 reducer。观察 trace 中两个 task 的写入如何在 Update 阶段合成一个可见值。此时再让下游节点读取 documents，确认它只能在下一超步看到完整列表。",
            "第三步故意让两个节点写 final_answer，且不加 reducer。你应该期待失败，而不是期待框架替你选择一个。这个失败说明状态模型保护了业务唯一性。",
            "第四步把 final_answer 拆成 candidate_answers 和 final_answer。并行节点写候选，judge 节点单写最终答案。这个结构更长一点，却把证据收集和决策责任分开，后续调试更容易。",
            "第五步给每个候选带 source、score 和 task_id。这样下游排序或过滤时不会丢失来源，debug 也能回答某条错误候选来自哪个分支。",
            "第六步把一个分支改成失败，思考 reducer 是否应该保留部分结果、记录错误，还是让整个图失败。fan-in 的失败策略本身就是业务语义。",
            "这些小实验的价值在于把 channel 当成协议测试。你验证的不是 Python 列表能不能 append，而是图在并行、提交、合并、下游读取时是否符合你的业务承诺。",
            "当小图语义稳定后，再把真实模型和工具接进去。否则模型输出的不确定性会掩盖 channel 设计问题，让你误以为是 prompt 不好。",
        ],
    )
    + _section(
        "补充推演：读写矩阵如何指导重构",
        [
            "假设一个图有 planner、retriever_a、retriever_b、summarizer、finalizer 五个节点。把它们放进行列矩阵后，你可能发现 planner 写 plan，两个 retriever 都读 plan 并写 documents，summarizer 读 documents 写 draft，finalizer 读 draft 写 answer。这个结构清楚，因为每个阶段的 channel 责任单一。",
            "如果矩阵显示 retriever_a 也写 answer，summarizer 也写 answer，finalizer 也写 answer，就说明 answer 被滥用。重构时可以让 retriever 写 evidence，summarizer 写 draft_answer，finalizer 单独写 final_answer。字段变多了，但语义更窄，冲突更少。",
            "如果矩阵显示某个节点读所有 channel，通常说明它承担了过多责任。比如 finalizer 同时读原始 question、所有工具结果、审批结果、错误日志和内部评分，也许应该拆出 prepare_context 节点，让 finalizer 只读整理好的上下文。",
            "如果矩阵显示某个 channel 被所有节点写，通常说明它是日志或消息类 channel，需要明确 reducer 和顺序策略。若它不是日志，却被到处写，那就是全局变量味道太重。LangGraph 允许共享状态，但不鼓励无边界共享。",
            "读写矩阵还帮助决定哪些节点可以并行。两个节点读相同输入、写不同输出，通常可以同一超步执行；一个节点读另一个节点的输出，就必须跨超步；两个节点写同一输出，则必须先设计 fan-in。矩阵让这些关系在代码执行前就可见。",
            "因此，Tasks 与 Channels 不是抽象名词，而是重构工具。每当图变复杂，就把节点、task、channel、write 画出来，先修通信结构，再修 prompt 和业务函数。",
        ],
    )
    + _section(
        "最后校验：用读写矩阵验收任务与通道",
        [
            "完成 tasks/channels 设计后，不要只看图能不能跑通，而要把每个节点在一个表里列成 read/write 矩阵：行是 PregelExecutableTask 或节点实例，列是 channel，格子标出读取、写入、reducer 和失败策略。矩阵能直接暴露哪些任务可以并行，哪些必须跨超步，哪些 fan-in 还没有业务语义。",
            "对每个可能多写的 channel，评审时要写出一句可测试的合并承诺。例如 documents 是按来源去重后保留分数，messages 是按 id 替换或追加，candidate_answers 是保留所有候选并交给 judge 排序。若只能说“框架会处理”，就说明 reducer 还没有被业务定义。",
            "对每个公开 PregelTask 快照，调试模板应记录它对应的内部执行上下文线索：task id、name、path、triggers、写入目标和最终 result/error。这样遇到十个并行工具调用时，团队不会只说“工具节点失败”，而能定位是哪一次 send、哪个输入和哪个 channel 写入导致问题。",
            "最后用一个最小 fan-out/fan-in 小图做回归：两个 retriever 并行写 documents，一个 ranker 下一超步读取合并结果，再故意让两个节点写 final_answer 触发冲突。这个练习能证明通道协议、任务粒度和错误边界都被设计清楚，而不是靠模型输出碰巧正确。",
        ],
    )
    + shell.lab_card(
        "设计一个安全 fan-in",
        [
            "定义三个输出：intent、keywords、documents，判断哪些会被单写，哪些可能被多写。",
            "让两个 retriever 并行写 documents，给 documents 设计列表聚合和去重策略。",
            "故意让两个分类器都写 final_intent，解释为什么 LastValue 多写应报错。",
            "增加一个 decide_intent 节点，让它读取两个分类结果后单独写 final_intent。",
            "用 trace 表记录每个 task 写了哪个 channel，并确认下一超步消费者只读提交后的结果。",
        ],
    )
    + shell.version_note("LangGraph 的具体 channel 类名、PregelTask 快照字段和 PregelExecutableTask 执行字段可能随版本微调，但“任务实例化、channel 持有合并语义、写入先标准化再统一提交”的结构非常稳定。读新版源码时优先找 BaseChannel、PregelNode、ChannelWrite 与 prepare/apply 之间的连接。")
    + _points(
        [
            "Task 是运行实例，Node 是定义；动态并行时一个节点可以生成多个任务。",
            "Channel 是 state key 的运行时形态，负责值、版本、合并和 checkpoint。",
            "fan-out 要保证任务互不依赖本步半成品，fan-in 要用 reducer 或明确冲突。",
            "调试并行问题时先列出 step、task、channel、write，再判断是图结构错还是合并规则缺失。",
        ]
    )
)


LESSON_24_CHECKPOINTS = (
    r"""
<p class="lead">LangGraph 的持久化不是“把最终答案保存一下”，而是把图在超步边界上的状态保存成 checkpoint。一个 checkpoint 通常包含 channel values、channel versions、pending sends、已见版本和元数据；checkpointer 负责按 <span class="mono">thread_id</span>、checkpoint namespace 和 checkpoint id 读写这些记录。理解 checkpoint 后，resume、get_state、update_state、人审和时间旅行都会变成同一个问题：我要从哪条线程、哪个命名空间、哪一个已提交超步继续观察或修改状态。</p>
"""
    + _analogy("把 checkpoint 想成游戏存档。玩家不是只在通关后保存结局，而是在每个安全房间保存背包、位置、任务进度和世界状态。thread_id 像玩家账号，namespace 像同一账号下的不同存档槽，checkpoint id 像某次具体保存时间。下一次进入游戏时，只要用同一个账号和存档槽，系统就能从上次安全房间继续；如果账号写错，就像打开了别人的空存档，再强的剧情逻辑也找不到你的装备。")
    + shell.lesson_map(
        "本课地图：从 checkpoint 到 resume",
        [
            ("结构", "Checkpoint 保存 channel values、versions、pending sends 等超步边界状态", "now"),
            ("接口", "BaseCheckpointSaver 定义 put/get/list 等持久化契约", "source"),
            ("内存实现", "InMemorySaver 适合本地实验和测试，不是生产持久层", "now"),
            ("线程", "configurable.thread_id 是恢复同一会话的关键索引", "now"),
            ("控制", "Pregel.get_state/update_state 让外部查看或修补某条线程的状态", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>持久化相关源码要按“数据结构 → 抽象接口 → 具体 saver → 运行时读写状态”的顺序读。仍然使用文件 + 符号名做锚点，因为 checkpoint 字段会迭代，但这些职责边界更稳定。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/checkpoint/base/__init__.py", "symbol": "Checkpoint", "role": "描述一次超步边界的持久化状态，包含 channel_values、channel_versions、versions_seen、pending_sends 等", "direction": "apply_writes 后形成新 checkpoint，saver 持久化"},
            {"file": "langgraph/checkpoint/base/__init__.py", "symbol": "BaseCheckpointSaver", "role": "checkpointer 抽象契约，定义如何按 config 保存、读取、列出 checkpoint", "direction": "Pregel 调用 saver，具体后端实现存储细节"},
            {"file": "langgraph/checkpoint/memory/__init__.py", "symbol": "InMemorySaver", "role": "内存版 saver，适合教程、单进程实验和测试，进程结束数据消失", "direction": "compile(checkpointer=InMemorySaver()) 后被运行时使用"},
            {"file": "langgraph/pregel/main.py", "symbol": "Pregel.get_state", "role": "按 config 读取某条线程最新或指定 checkpoint 的 StateSnapshot", "direction": "外部调试、UI 展示、人审页面查询状态"},
            {"file": "langgraph/pregel/main.py", "symbol": "Pregel.update_state", "role": "在 checkpoint 基础上注入人工更新或修补状态，产生新的可继续运行状态", "direction": "人审、修正工具结果、恢复前调整 state"},
        ]
    )
    + r"""
<h2>状态流：一次带 thread_id 的 invoke</h2>
"""
    + shell.state_flow(
        [
            ("配置线程", "调用 graph.invoke(input, config={'configurable': {'thread_id': 'u-42'}})。thread_id 进入 checkpointer 的索引键。", "configurable.thread_id='u-42'"),
            ("读取旧存档", "运行开始时 saver 按 thread_id 和 namespace 查找最新 checkpoint；第一次调用通常为空。", "checkpoint=None or latest"),
            ("执行超步", "Pregel 按 Plan/Execution/Update 推进，每个提交边界形成新的 channel values 和 versions。", "messages@v1 -> messages@v2"),
            ("写入 checkpoint", "BaseCheckpointSaver.put 保存 checkpoint 和 metadata，记录当前线程的最新状态。", "put(thread_id='u-42', checkpoint_id='...')"),
            ("下次恢复", "下一次用同一个 thread_id 调用，运行时从最新 checkpoint 继续，而不是从空 state 开始。", "resume from latest checkpoint"),
        ]
    )
    + r"""
<h2>Trace：保存后再恢复</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. first invoke", "input": "{'messages': [HumanMessage('我的订单?')]} + thread_id='alice'", "action": "checkpointer 未找到 alice 的存档，初始化 state", "output": "checkpoint-1: messages 含用户问题"},
            {"step": "2. model/tool steps", "input": "checkpoint-1", "action": "模型调用工具、工具写回结果、模型给出答复", "output": "checkpoint-2/3/4 逐步保存 channel values"},
            {"step": "3. process ends", "input": "内存或外部 saver 中已有 alice 最新 checkpoint", "action": "应用进程可结束；持久 saver 仍保留状态", "output": "thread_id='alice' -> checkpoint-4"},
            {"step": "4. second invoke", "input": "{'messages': [HumanMessage('那什么时候到?')]} + same thread_id", "action": "运行时读取 checkpoint-4，把新输入合并到 messages", "output": "模型能看到上次订单上下文"},
            {"step": "5. get_state", "input": "config thread_id='alice'", "action": "Pregel.get_state 返回 StateSnapshot", "output": "UI 可展示 values、next、tasks、metadata"},
        ]
    )
    + r"""
<h2>简化源码走读：checkpointer 契约</h2>
"""
    + shell.code_walkthrough(
        "langgraph/checkpoint/base/__init__.py",
        "BaseCheckpointSaver",
        """class BaseCheckpointSaver:
    def get_tuple(self, config):
        # thread_id + checkpoint_ns + checkpoint_id
        ...

    def put(self, config, checkpoint, metadata, new_versions):
        # persist one committed superstep
        ...

    def list(self, config, before=None, limit=None):
        # history for time travel/debug
        ...
""",
        "教学版突出三个操作：按 config 读最新或指定 checkpoint，提交新 checkpoint，列出历史。真实实现还会处理 serde、pending writes、异步接口、父子 config 和存储后端差异。",
    )
    + _section(
        "checkpoint 保存的不是普通聊天记录",
        [
            "很多人把 LangGraph 持久化理解成“保存 messages 列表”。messages 当然可能在 checkpoint 里，但 checkpoint 的范围更广：每个 channel 的值、每个 channel 的版本、每个节点已经看过哪些版本、还有可能等待发送的任务。它保存的是运行时能恢复图执行所需的最小世界，而不是只给 UI 展示的业务日志。",
            "这就是为什么 checkpoint 能支撑 resume。如果只存最终回答，下次调用只能把历史文字塞回 prompt；如果存完整 channel values 和 versions，运行时知道哪些节点已经执行过、哪些 channel 发生过变化、下一步可以从哪里继续。持久化的是执行状态，不只是对话内容。",
            "checkpoint 也让 get_state 有了精确语义。get_state 返回的 StateSnapshot 不只是 dict values，还可能包含 next tasks、config、metadata、created_at 等信息。调试时你能看到图停在哪里、为什么下一步会去某节点，而不仅是“当前字段长什么样”。",
        ],
    )
    + _section(
        "thread_id 是会话边界",
        [
            "configurable.thread_id 是多数持久化问题的第一现场。它必须来自稳定业务身份，例如用户会话、工单 id、对话 id，而不是随机生成后丢掉。如果每次请求都用新 thread_id，图永远找不到旧 checkpoint；如果多个用户共享同一个 thread_id，状态会串线，后果比普通缓存污染更严重。",
            "生产系统通常把 thread_id 放在后端会话层或业务数据库里，而不是让前端随便传任意字符串。前端可以选择会话，但后端要校验权限：用户 A 不应读取用户 B 的 checkpoint。LangGraph 提供运行时能力，不替你完成租户隔离和鉴权。",
            "命名空间 checkpoint_ns 则适合同一 thread 下的不同用途。例如同一工单可以有 main 运行、实验分支、人工修复分支。namespace 让你不用把所有历史混在一条线上。若不理解 namespace，时间旅行和 fork 很容易覆盖主流程。",
        ],
    )
    + _section(
        "BaseCheckpointSaver 与具体后端",
        [
            "BaseCheckpointSaver 是契约，不是存储产品。它让 Pregel 不关心 checkpoint 最终写到内存、SQLite、Postgres、Redis 还是云服务。运行时只需要按 config put/get/list；序列化、索引、并发控制和清理策略由 saver 实现负责。",
            "InMemorySaver 的价值是教学和测试。它无需外部服务，能让你验证 thread_id、resume、interrupt 和 history 的机制。但进程退出数据就没了，多进程也不共享。把 InMemorySaver 用到生产持久会话，是典型误用。生产环境应选择支持持久介质、并发访问和备份策略的 saver。",
            "选择后端时要看访问模式。聊天机器人常读最新 checkpoint；调试后台常 list history；人审系统可能频繁 update_state；时间旅行会读取指定 checkpoint 并 fork。不同模式对索引和容量要求不同。不要等历史记录堆满后才发现 saver list 很慢。",
        ],
    )
    + _section(
        "update_state 是外部修补，不是随手改内存",
        [
            "Pregel.update_state 允许你在某个 checkpoint 基础上写入新的 state update。它适合人工审核后补充 approved=True，或把错误工具结果修正为可信结果，或在恢复前注入缺失字段。它的关键是仍然通过运行时写入机制产生新状态，而不是绕过 channel 直接改存储。",
            "使用 update_state 时要保留审计意识。谁改了 state，为什么改，基于哪个 checkpoint 改，改完后图从哪里继续，这些都应进入 metadata 或业务日志。否则人审和调试会变成另一个黑盒：你知道状态变了，却不知道哪个人或系统让它变。",
            "还要注意 reducer 语义。向 messages 追加人工消息，和替换某条消息，是两种不同更新；向 LastValue 写 approval，和向列表型 channel 添加一条 reviewer note，也不同。update_state 并不免除你理解 channel 合并规则的责任。",
        ],
    )
    + _section(
        "恢复失败的排查顺序",
        [
            "第一问：第二次调用是否使用了同一个 thread_id、同一个 checkpoint namespace、同一个 checkpointer 实例或同一个持久后端？很多“状态丢失”只是因为第一次用 thread_id=abc，第二次变成 user_abc，或者本地重启后 InMemorySaver 为空。",
            "第二问：输入是不是被设计成覆盖了历史。某些图会把新输入映射到 messages channel 并用 add_messages 合并；如果你把 messages 直接设成新列表且没有正确 reducer，就可能覆盖旧历史。持久化保存了旧状态，不代表你的新输入不会按 schema 把它替换掉。",
            "第三问：get_state 看到的 checkpoint 是否符合预期。如果 saver 里有旧值但运行结果没有用上，问题可能在输入 mapper 或节点读取；如果 saver 里也没有旧值，问题在 checkpoint 写入或 config；如果 checkpoint 有多条 namespace，问题可能是读了错误分支。",
        ],
    )
    + _section(
        "工程复盘：把持久化当成产品能力",
        [
            "在生产系统里，checkpoint 不是框架内部的小优化，而是直接影响产品体验的能力。用户是否能续聊，人工审核是否能回来继续，客服是否能查看历史，调试人员是否能复盘事故，都取决于 checkpoint 是否被正确索引、保存和保护。把它当成“可选缓存”会导致一系列隐蔽问题。",
            "thread_id 的生成策略必须和业务边界一致。聊天应用可以用 conversation_id，工单系统可以用 ticket_id，批处理流程可以用 job_id。不要用用户 id 直接作为所有对话的 thread_id，否则同一用户的多个会话会互相污染；也不要每次请求生成随机 id，否则永远无法恢复。thread_id 是状态隔离线，不是随便的字符串。",
            "checkpoint namespace 适合表达分支，而不是替代 thread_id。比如主线 namespace 保存用户可见会话，debug namespace 保存工程师实验，人审 namespace 保存审批修补。这样同一 thread 下可以有多条相关但不互相覆盖的历史。若把 namespace 用乱，get_state_history 会变得难以解释。",
            "持久化后端还要考虑数据生命周期。对话状态可能包含个人信息、工具结果、业务单号和模型输出，不能无限期保存。团队需要定义保留时间、删除策略、备份策略和导出权限。LangGraph 负责写 checkpoint，不负责替你满足合规要求。",
            "恢复路径也需要测试。很多系统只测试第一次 invoke 成功，却不测试进程重启后第二次 invoke 是否能找到旧 checkpoint。真正的持久化验收应包括：重启应用、换 worker、连续多轮、错误后恢复、人审后恢复、不同用户隔离、namespace 分支读取。少一个场景，线上就可能在那个场景丢状态。",
            "get_state 可以成为运营和客服工具的后端接口，但不能裸露所有 values。某些 state key 可能包含系统提示、内部评分、敏感工具结果或安全策略。展示层应做字段过滤和权限控制。可观察性不等于把内部状态全部公开。",
            "update_state 的产品含义是人工修补。修补能力很有用，也很危险。它能让客服纠正错误订单状态、让审核员补充批准意见、让工程师恢复卡住流程；也可能让未经授权的人篡改历史。每次 update 都应记录操作者、原因、旧 checkpoint、新 checkpoint 和可见影响。",
            "checkpoint metadata 是事故复盘的朋友。不要忽略 step、source、writes、parent 等信息。只有 values 说明不了状态为什么变化；metadata 能告诉你变化来自输入、节点、人工 update 还是 replay 分支。生产 saver 如果丢掉 metadata，会严重削弱调试能力。",
            "InMemorySaver 的问题不只是进程退出丢数据，还包括多 worker 不共享。线上服务一旦横向扩展，请求可能落到不同进程。第一次 invoke 写在 worker A 的内存里，第二次 invoke 落到 worker B 就像没有历史。即使 demo 没问题，架构上也不成立。",
            "最后，持久化是一项端到端能力：config 生成、saver 后端、权限隔离、状态 schema、恢复测试和运维清理缺一不可。LangGraph 给出标准接口，但系统质量取决于你如何把这些接口接到真实业务边界上。",
        ],
    )
    + r"""
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("checkpoint 等于聊天记录", "checkpoint 是图运行状态，包含 channel values、versions、pending 信息和元数据，不只是 messages。"),
            ("传了 checkpointer 就一定能续聊", "还必须稳定传入 configurable.thread_id，并使用可持久保存的 saver。"),
            ("InMemorySaver 可以生产使用", "它适合实验和测试，进程结束即丢失，生产要使用持久后端并做权限隔离。"),
            ("update_state 可以绕过 reducer", "它仍应尊重 channel 更新语义，并记录审计来源。"),
        ]
    )
    + _section(
        "实践提示：持久会话上线清单",
        [
            "上线前先做冷启动恢复测试：启动服务，运行第一轮对话，停止进程，重新启动，再用同一 thread_id 追问。若使用持久 saver，第二轮应能看到第一轮状态；若使用 InMemorySaver，失败是预期结果，不能把它当生产方案。",
            "再做并发隔离测试：两个用户同时使用相似输入，但 thread_id 不同。检查 get_state_history 是否完全隔离，确认用户 A 的消息不会出现在用户 B 的 checkpoint 中。",
            "第三个测试是多会话隔离：同一用户打开两个工单或两个浏览器会话。若 thread_id 只用 user_id，两条会话会串线；正确做法通常是 user_id 加 conversation_id 或后端生成的会话 id。",
            "第四个测试是 namespace 分支：在 debug namespace 中 fork 一次，不应改变 main namespace 的最新状态。UI 展示主线时也不应误读 debug 分支。",
            "第五个测试是 update_state 审计：人工修补后，history 中应能看出修补来源、操作者和原因。若只看到 values 变化而没有 metadata，后续复盘会非常困难。",
            "第六个测试是权限拒绝：尝试用无权限用户读取或恢复别人的 thread_id，后端应拒绝。不要把 thread_id 当成安全凭证，它只是索引。",
            "第七个测试是数据清理：删除或归档某条会话后，get_state 和 history 的行为应符合产品政策。持久化越成功，越需要生命周期管理。",
            "这些检查说明 checkpoint 不只是框架参数，而是应用状态管理的一部分。只有把它纳入产品、后端和运维测试，恢复能力才可靠。",
        ],
    )
    + _section(
        "补充推演：从一次续聊事故反推责任边界",
        [
            "用户第一次问订单，系统正确调用工具并回答；第二次问“那能改地址吗”，系统却说不知道订单。这类事故表面是模型忘记历史，实质往往是 checkpoint 读写边界出错。首先要确认第二次请求是否使用同一 thread_id，而不是只看前端会话还在不在。",
            "如果 thread_id 相同，再看 saver 后端是否同一个。开发环境常把 checkpointer 放在进程内全局变量，重启后自然丢失；生产环境常因为多 worker 或无状态部署，让第二次请求落到没有内存历史的实例。持久后端和共享配置是恢复的基础。",
            "如果 saver 中能看到旧 checkpoint，再看新输入如何进入 graph。某些输入 mapper 会把 messages 设置为新列表，覆盖旧 messages；正确做法通常是让新 HumanMessage 作为增量进入带 reducer 的 messages channel。持久化保存历史，不代表输入合并一定正确。",
            "如果 messages 正确但模型仍然不知道订单，可能是节点只读取了本轮 input 而不是 state['messages']，或 prompt 构造时丢掉了历史。此时问题在节点内部数据流，不在 checkpoint。分层排查能避免盲目换数据库。",
            "如果 get_state_history 中存在多个 namespace，要确认 UI 和 API 使用的是同一个 namespace。debug 分支、人审分支和主线分支混用，会让状态看似丢失，实际只是读了另一条历史线。",
            "最后要把事故写成检查项：稳定 thread_id、持久 saver、正确 namespace、messages reducer、节点读取完整 state、权限隔离。下次续聊失败时，按这张清单走，比重新猜 prompt 更可靠。",
        ],
    )
    + _section(
        "上线校验：把 checkpoint 当成恢复契约",
        [
            "持久化页的最后检查应围绕 thread 归属，而不是围绕 saver 类型。每条业务会话都要能回答：thread_id 从哪个业务对象生成，谁有权限读取，checkpoint_ns 何时分支，checkpoint_id 何时固定到一次审核或复盘。没有这些规则，换成再可靠的数据库也只是把混乱状态保存得更久。",
            "恢复契约还包括输入合并方式。第二次 invoke 不是把旧 checkpoint 和新输入随便拼在一起，而是让新 HumanMessage 或业务事件作为增量进入正确 channel，再由 reducer 合并。测试要覆盖连续多轮、进程重启、多 worker、同用户多会话和错误 thread_id，证明恢复链路在真实部署形态下仍然成立。",
            "人工 update_state 应被当成一次正式状态转移。评审清单里要写操作者、原因、基于哪个 parent checkpoint、写了哪些 channel、是否触发下游节点，以及如何回滚或再审。缺少审计的修补能力会让 checkpoint 从可靠历史变成不可解释的后门。",
            "最后把数据生命周期也纳入契约：哪些 state key 可以长期保存，哪些必须脱敏或定期清理，哪些 debug namespace 只能短期存在。checkpoint 支撑恢复、客服和复盘，但也扩大了数据责任；上线标准必须同时覆盖可用性、隔离性和合规性。",
        ],
    )
    + _section(
        "补充提醒：不要把恢复责任推给模型",
        [
            "模型只能根据节点传给它的上下文回答，不能替运行时找回丢失的 checkpoint。若历史没有被正确保存、读取和合并，再聪明的模型也只能面对残缺输入猜测。排查续聊问题时，先验证持久化链路，再讨论提示词质量。",
            "同样，checkpoint 也不会自动保证业务正确。它保存的是图状态，但状态字段是否合理、thread_id 是否安全、人工修改是否审计，仍然属于应用设计责任。框架提供存档能力，团队负责把存档能力接到可靠流程里。",
        ],
    )
    + shell.lab_card(
        "定位一次丢失上下文",
        [
            "用同一个 checkpointer 连续 invoke 两次，第一次问订单，第二次追问配送时间。",
            "记录两次 config 中的 configurable.thread_id 和 checkpoint_ns，确认完全一致。",
            "在第二次 invoke 前调用 get_state，检查 messages 是否已有第一次历史。",
            "把 thread_id 改成另一个值重跑，观察图为什么像新会话。",
            "把 InMemorySaver 替换为持久 saver 时，列出需要补充的权限、清理和备份策略。",
        ],
    )
    + shell.version_note("本课描述的是 LangGraph checkpoint 的稳定心智模型。不同版本的序列化字段、metadata 键和 saver 后端名称可能调整；遇到差异时，优先追踪 Checkpoint、BaseCheckpointSaver、Pregel.get_state 与 Pregel.update_state 的职责，而不是依赖某个字段顺序。")
    + _points(
        [
            "checkpoint 保存的是超步边界的运行状态，不只是最终输出或聊天日志。",
            "thread_id、checkpoint namespace、checkpoint id 共同决定读写哪条历史线。",
            "BaseCheckpointSaver 隔离运行时与存储后端；InMemorySaver 适合实验，不适合生产持久会话。",
            "get_state 用于观察，update_state 用于受控修补；二者都应带着审计和 channel 语义使用。",
        ]
    )
)


LESSON_25_INTERRUPT_COMMAND = (
    r"""
<p class="lead">复杂 Agent 不应该把所有决定都交给模型自动执行。LangGraph 用 <span class="mono">interrupt</span> 暂停图，把需要人工或外部系统确认的信息交还给调用方；调用方再用 <span class="mono">Command</span> 把 resume payload、状态更新和跳转意图送回运行时。interrupt 不是普通异常，Command 也不是随便返回的 dict：前者是受控暂停，后者是“恢复值、更新状态、选择去向”的控制原语。本课用审批流程追踪 node interrupt、caller 返回 <span class="mono">Command(resume={"approved": True, "comment": "ok"})</span>、图继续执行的全过程。</p>
"""
    + _analogy("把 interrupt 想成医院手术室的暂停核对。医生准备进行高风险步骤时，不是把流程崩溃掉，而是按下暂停铃，请家属或主治医生确认；确认单上可能写同意、备注和下一步安排，这张确认单就是 Command。手术团队收到确认单后，从安全的记录点恢复，更新病历，再决定继续原计划、改去观察室，还是终止手术。暂停不是失败，而是把自动流程交给人类判断的一道闸门。")
    + shell.lesson_map(
        "本课地图：中断、恢复与控制命令",
        [
            ("interrupt", "节点内声明需要外部输入，运行时捕获为 GraphInterrupt 并把值返回给调用方", "now"),
            ("GraphInterrupt", "不是业务失败，而是可恢复暂停信号，需要 checkpoint 支撑", "source"),
            ("Command.resume", "调用方把人工输入交回 interrupt 调用点", "now"),
            ("Command.update/goto", "同一个原语还能写状态、改变下一跳，表达人审后的控制流", "now"),
            ("CompiledStateGraph", "高层状态图编译后通过 Pregel.stream/invoke 暴露这些能力", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>interrupt/Command 的源码阅读要把 types、errors、Pregel.stream 和 CompiledStateGraph 连起来。文件 + 符号名能帮助区分“用户节点如何发出暂停”“运行时如何传播暂停”“调用方如何恢复”。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/types.py", "symbol": "interrupt", "role": "节点内部调用的暂停原语，向外暴露需要人工或外部系统提供的值", "direction": "节点执行中触发，运行时把信息交给 stream/invoke 调用者"},
            {"file": "langgraph/types.py", "symbol": "Command", "role": "控制原语，可携带 resume、update、goto 等字段，表达恢复输入、状态更新和跳转", "direction": "调用方或节点返回 Command，Pregel 解释并继续调度"},
            {"file": "langgraph/errors.py", "symbol": "GraphInterrupt", "role": "运行时用于区别受控中断与普通异常的信号", "direction": "interrupt 触发后沿 Pregel 执行边界传播"},
            {"file": "langgraph/pregel/main.py", "symbol": "Pregel.stream", "role": "流式运行入口，能把 interrupt、debug、values、updates 等事件交给调用方", "direction": "调用方观察到暂停事件后决定是否返回 Command"},
            {"file": "langgraph/graph/state.py", "symbol": "CompiledStateGraph", "role": "用户编译后的状态图对象，对外提供 invoke/stream/get_state/update_state 等接口", "direction": "高层图 API 最终复用 Pregel 的中断恢复能力"},
        ]
    )
    + r"""
<h2>状态流：审批节点暂停再恢复</h2>
"""
    + shell.state_flow(
        [
            ("准备高风险动作", "节点发现将要退款、发邮件或执行交易，需要人工确认。它把待审批摘要放进 interrupt payload。", "interrupt({'action': 'refund', 'amount': 500})"),
            ("运行时暂停", "GraphInterrupt 被 Pregel 捕获。因为有 checkpointer，当前线程停在可恢复 checkpoint 上。", "state.next includes approval node"),
            ("调用方展示", "stream 把暂停信息交给 UI/API。人类审核员看到金额、理由、上下文，填写同意和备注。", "UI form -> approved/comment"),
            ("Command 恢复", "调用方用同一 thread_id 继续调用，并传入 Command(resume={'approved': True, 'comment': 'ok'})。", "Command(resume=...)"),
            ("图继续执行", "interrupt 调用点获得 resume 值，节点写入 approval，再 goto 执行实际退款或拒绝分支。", "update approval -> goto execute_refund"),
        ]
    )
    + r"""
<h2>Trace：approval workflow</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. model proposes", "input": "用户要求退款 500 元，risk_score='high'", "action": "route 进入 approval 节点", "output": "next='approval'"},
            {"step": "2. node interrupts", "input": "approval 节点读取 refund_request", "action": "调用 interrupt({'amount': 500, 'reason': 'high risk'})", "output": "GraphInterrupt，stream 返回待审批 payload"},
            {"step": "3. human reviews", "input": "UI 展示 payload 和历史 state", "action": "审核员点击通过并填写 ok", "output": "Command(resume={'approved': True, 'comment': 'ok'})"},
            {"step": "4. resume", "input": "同一 thread_id + Command.resume", "action": "运行时从 checkpoint 恢复，interrupt 返回 resume payload", "output": "approval_result={'approved': True, 'comment': 'ok'}"},
            {"step": "5. continue", "input": "approval_result approved", "action": "节点返回 Command(update={'approval': ...}, goto='execute_refund')", "output": "下一超步执行退款节点"},
        ]
    )
    + r"""
<h2>简化源码走读：interrupt 与 Command</h2>
"""
    + shell.code_walkthrough(
        "langgraph/types.py",
        "interrupt / Command",
        """def approval_node(state):
    decision = interrupt({
        'kind': 'refund_approval',
        'amount': state['amount'],
    })
    if decision['approved']:
        return Command(
            update={'approval': decision},
            goto='execute_refund',
        )
    return Command(update={'approval': decision}, goto='reject')
""",
        "真实恢复依赖 checkpointer 和同一 thread_id。interrupt 第一次运行时暂停；恢复时同一调用点得到 Command.resume 中的值。Command 可以从调用方传入，也可以由节点返回，用统一结构表达更新与跳转。",
    )
    + _section(
        "interrupt 不是普通异常",
        [
            "普通异常表示程序遇到未处理失败，通常要回滚或终止。GraphInterrupt 表示图主动把控制权交还给外部世界，等待一个值后可以继续。二者的处理策略完全不同：异常要修 bug 或走失败分支；interrupt 要保存状态、展示问题、收集输入、用同一线程恢复。",
            "这也是为什么 interrupt 几乎总是和 checkpointer 一起使用。没有 checkpoint，暂停后就没有可靠位置可以恢复。你可以把 interrupt 看成“可恢复异常”，但更准确地说，它是运行时协议：节点发出暂停请求，Pregel 记录停点，调用方返回 Command，运行时把 resume 值送回原调用点。",
            "调试时要区分“节点抛错导致失败”和“节点中断等待人”。如果 UI 把 GraphInterrupt 当成 500 错误，用户会以为系统崩了；如果日志把它当成正常事件，就能展示审批卡片并保持线程等待。",
        ],
    )
    + _section(
        "Command 为什么同时包含 resume、update、goto",
        [
            "人审后的动作通常不只是一段输入。审批通过时，你要把审批结果写入 state，可能跳去 execute 节点；审批拒绝时，要写入拒绝原因，跳去 reject 节点；需要补充信息时，可能回到 ask_user。Command 把这些控制意图放在同一个结构里，避免调用方先 update_state、再手动改边、再 invoke 的多步脆弱流程。",
            "resume 的语义是“把这个值交回正在等待的 interrupt 调用点”。update 的语义是“向图状态写入这些增量”。goto 的语义是“下一步去这个节点或这些节点”。三者正交，可以单独用，也可以组合。理解这个正交性，就能把 human-in-the-loop、agent handoff、修补状态和路由控制看成同一套机制。",
            "不过 Command 不是万能遥控器。goto 必须指向图里合法节点，update 必须符合 state schema，resume 必须匹配等待点需要的数据形状。调用方传入任意 dict 不会自动变成安全业务流程；你仍要做权限校验、payload 校验和审计记录。",
        ],
    )
    + _section(
        "恢复会重新执行什么",
        [
            "interrupt 的一个重要边界是恢复语义。常见心智模型是：恢复后运行时会回到包含 interrupt 的节点，让 interrupt 调用返回 resume 值，然后节点继续计算。由于实现需要重建调用栈，interrupt 之前的代码可能重新执行。具体行为要看版本和节点结构，但工程上应按“interrupt 之前不要做不可重复副作用”来设计。",
            "高风险副作用应放在审批之后。例如不要先扣款再 interrupt 等待确认；应先 interrupt，拿到 approved=True 后再进入 execute_refund 节点扣款。若必须在中断前做外部调用，必须保证幂等，例如使用业务 idempotency key，或把副作用结果写入 checkpoint 后让恢复逻辑检测已执行。",
            "这个规则看似保守，却能避免真实事故。人工审批常发生在退款、发信、删数据、下单、创建工单等副作用前。把 interrupt 放在副作用之前，配合 Command.goto 到执行节点，是最清晰也最安全的结构。",
        ],
    )
    + _section(
        "设计 human-in-the-loop 的数据边界",
        [
            "interrupt payload 应该足够让人做决定，但不应该泄露不必要的敏感信息。审批卡片通常包含动作类型、金额、原因、模型证据、相关消息摘要和可选建议；不应把整份内部 state 原样暴露给前端，尤其是包含密钥、系统提示词或其他用户数据时。",
            "resume payload 应该结构化。不要只传 'yes' 或 'ok'，而应传 {'approved': True, 'comment': 'ok', 'reviewer_id': '...'} 这类可审计字段。节点收到后先校验字段，再写入 approval channel。结构化 payload 让后续节点能清楚地区分通过、拒绝、要求修改和超时。",
            "还要定义超时和取消。如果审核员一直不处理，线程是否保持等待？是否自动拒绝？是否通知用户？这些不是 LangGraph 自动替你决定的业务规则。interrupt 只提供暂停点，产品规则仍要在图结构和外部服务里明确。",
        ],
    )
    + _section(
        "stream 视角下的中断",
        [
            "Pregel.stream 的价值在于调用方可以逐步观察事件，而不是等 invoke 最终返回。中断发生时，stream 可以把 interrupt 信息作为事件交出，UI 立即渲染审批表单；debug 模式还可以显示中断发生在哪个 step、哪个 task、哪个节点。",
            "恢复时仍要使用同一 thread_id。很多失败来自调用方拿到 interrupt 后丢失 config，下一次把 Command 发到新线程。运行时在新线程里找不到等待点，自然无法把 resume 值交回原 interrupt。把 thread_id 和 checkpoint namespace 存在审批任务记录里，是生产系统必须做的事情。",
            "如果一个图可能同时有多个 interrupt，要记录每个 interrupt 的上下文和路径。不要只在前端保存“当前有个审批”。多用户、多标签页、多 agent handoff 场景下，审批事件必须能回到准确线程和准确等待点。",
        ],
    )
    + _section(
        "工程复盘：人审流程的安全边界",
        [
            "human-in-the-loop 的核心不是让人点一个按钮，而是把自动系统的风险边界显式化。哪些动作必须审批，审批人需要哪些证据，审批结果如何影响后续节点，审批记录如何审计，这些问题都应在图和外部系统里有明确答案。interrupt 只负责暂停，不负责替产品定义规则。",
            "审批 payload 要做到足够但最小。足够是指审核员能判断动作是否合理，例如金额、对象、理由、模型证据、工具结果、风险分数；最小是指不暴露与决策无关的内部提示、其他用户信息或密钥。很多安全问题不是模型自动执行造成的，而是人审 UI 泄露了过多 state。",
            "resume payload 要可验证。approved=True 只是一个布尔值，通常不够。更好的结构包括 reviewer_id、approved、comment、reviewed_at、policy_version，必要时还要包含签名或后端生成的审批记录 id。节点收到 resume 后应校验字段，而不是把前端传来的任意对象写进 state。",
            "Command.update 和 Command.goto 让审批结果进入图语义。通过时写 approval 并去 execute，拒绝时写 rejection 并去 notify_user，需要补件时写 request_more_info 并回到 ask_user。不要在调用方外部偷偷执行退款再让图继续，否则 trace 会看不到真正的副作用。",
            "副作用节点应独立且幂等。审批节点只负责收集决定，execute_refund 节点负责调用支付系统，并使用 refund_id 或 operation_id 防重复。这样即使恢复、重试或 worker 崩溃，也能通过外部幂等键避免重复扣款。把审批和执行写在一个节点里，会让恢复边界变得模糊。",
            "超时策略必须提前设计。审批可能几分钟，也可能几天。线程等待期间 checkpoint 要保留多久，用户是否能取消，系统是否提醒审批人，超时后默认拒绝还是升级，这些都不是 interrupt 自动提供的。可以用外部任务队列或调度器在超时后向同一 thread 发送 Command。",
            "多审批人场景要避免竞态。两个人同时打开审批页面，一个通过一个拒绝，哪个生效？可以让后端审批服务先完成乐观锁或状态机判断，再只向 LangGraph 发送一个最终 Command。不要让多个前端直接向同一等待点竞争写 resume。",
            "中断恢复的权限检查不能只靠 thread_id。攻击者如果猜到 thread_id，不应能提交 Command。恢复 API 要验证当前用户是否有权审批该 action、该 checkpoint 是否仍在等待、payload 是否符合当前 policy。LangGraph 是运行时，不是权限系统。",
            "调试人审问题时，先看三个对象：等待时的 StateSnapshot、审批系统保存的 decision record、恢复时传入的 Command。三者应该能互相对应。如果 state 有 approval 但审批系统没有记录，说明有人绕过了流程；如果审批系统有记录但图没继续，说明 Command 没有送回正确线程。",
            "一个成熟的人审图会把自动化和人工判断都纳入 trace。模型提出动作、路由进入审批、人类给出决定、图执行副作用，每一步都有 checkpoint 和 metadata。这样事故发生后，团队能回答谁在什么时候基于什么信息批准了什么，而不是只看到一个最终退款结果。",
        ],
    )
    + r"""
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("interrupt 就是 raise Exception", "它是受控暂停信号，预期由调用方收集输入后恢复。"),
            ("Command(resume=...) 会自动更新 state", "resume 只返回给等待点；要持久记录审批结果，节点或 Command 还需要 update。"),
            ("可以在 interrupt 前执行扣款", "恢复可能重跑前置代码，高风险副作用应放在审批通过后的独立节点，并做幂等。"),
            ("前端随便传 thread_id 就能恢复", "恢复需要同一线程、权限校验和匹配等待点，生产系统必须保存并验证 config。"),
        ]
    )
    + _section(
        "实践提示：审批图的端到端验收",
        [
            "验收审批图时，不要只测 approved=True 的快乐路径。还要测试拒绝、补充信息、审批超时、审批人无权限、重复提交 Command、恢复时 thread_id 错误、执行节点失败等场景。",
            "通过路径应证明三件事：interrupt payload 足够审核，resume payload 被校验并写入 approval，execute 节点只在批准后运行。任何一个条件缺失，都可能让人审流于形式。",
            "拒绝路径应证明副作用没有发生。比如退款审批拒绝后，支付系统不应收到 refund 请求，state 中应记录拒绝原因，用户通知节点应能解释结果。",
            "重复提交场景尤其重要。用户双击按钮、浏览器重试、审批服务超时重发，都可能让同一个决定被发送两次。后端和副作用节点都应使用幂等键。",
            "恢复错线程场景可以暴露 config 管理问题。Command 如果被发到新 thread，运行时找不到等待点；如果被发到别人的 thread，则是严重安全事故。审批任务记录必须保存并校验 thread_id、namespace 和 checkpoint。",
            "审批 UI 还应展示足够上下文，但隐藏敏感内部字段。测试时可以故意在 state 放入不应展示的字段，确认 payload 构造函数不会泄露它。",
            "执行节点失败后，图应有可解释状态：审批已经通过，但副作用执行失败，需要重试或人工处理。不要把执行失败伪装成审批未发生。",
            "这些验收让 interrupt 与 Command 从 API 用法变成可靠流程。人审不是一个按钮，而是一条带权限、审计、幂等和恢复语义的状态机。",
        ],
    )
    + _section(
        "补充推演：Command 让控制流保持可审计",
        [
            "如果没有 Command，审批系统可能会分散成三段：前端调用一个接口保存审批结果，后端再手动改数据库，最后另一个接口触发图继续。三段之间任何一步失败，图状态和业务记录都可能不一致。Command 的价值是把恢复输入、状态更新和下一跳放在同一个运行时事件里。",
            "例如通过审批时，Command.resume 把表单值交回 interrupt，节点校验后返回 Command(update={'approval': decision}, goto='execute_refund')。trace 里能看到审批结果写入，也能看到为什么下一步去执行退款。拒绝时同理写 rejection 并 goto notify_user。",
            "这种可审计性对合规场景很重要。事后复盘时，你可以从 checkpoint 看到模型提出退款，从 interrupt 看到等待人工，从 Command 看到审核员决定，从 execute 节点看到外部退款请求。每一步都有状态证据，而不是散落在多个服务日志里。",
            "Command 也让多 Agent handoff 更朴素。所谓交接给另一个 agent，本质上是更新共享状态并 goto 另一个节点或子图。理解这一点后，就不需要为每种交接发明新机制，只要把交接原因、上下文和目标写清楚。",
            "不过，Command 的集中表达不等于绕过业务校验。恢复 API 仍应确认当前 checkpoint 正在等待审批，审批人有权限，payload 符合 schema，goto 目标合法。运行时负责执行命令，应用负责决定谁可以发命令。",
            "因此，在代码评审中看到 Command 时，应同时问三个问题：resume 值是否可信，update 是否符合审计要求，goto 是否让副作用边界更清晰。能回答这三点，Command 才是安全控制原语。",
        ],
    )
    + _section(
        "上线校验：把人审流做成可恢复状态机",
        [
            "Interrupt/Command 页的最后检查应从状态机开始：哪些节点可能暂停，暂停 payload 暴露哪些字段，等待期间状态里记录什么，Command.resume 的 schema 怎样校验，通过、拒绝、补充信息和超时分别 goto 哪里。只有把这些路径列全，人审才不是一个临时弹窗，而是图中的正式控制流。",
            "高风险副作用必须有独立边界。审批前节点只收集证据并 interrupt；审批通过后的 execute 节点才调用外部系统，并使用业务 idempotency key。测试要覆盖恢复重跑、重复提交 Command、浏览器刷新、worker 重启和外部 API 超时，证明不会因为 LangGraph 重新执行等待点前代码而重复扣款、发信或下单。",
            "权限和审计不能依赖前端自觉。恢复接口要校验 thread_id、namespace、checkpoint 是否处于等待点，审批人是否有权限处理该业务对象，resume/update/goto 是否符合后端允许的转移。Command 是运行时原语，不是授权系统；应用必须在发出 Command 前完成业务校验。",
            "最终验收应能从 history 复盘完整链路：模型或规则为什么请求审批，interrupt 给了审核员哪些上下文，Command 写入了什么决定，副作用节点是否执行成功，失败后如何重试或通知。能复盘，才说明人审流真正可恢复、可审计、可维护。",
        ],
    )
    + shell.lab_card(
        "设计退款审批图",
        [
            "列出 state key：refund_request、risk_score、approval、messages，并决定哪些需要 reducer。",
            "让 route 节点在 risk_score 高时进入 approval，否则直接进入 execute_refund。",
            "approval 节点调用 interrupt，payload 只包含审批必需字段。",
            "调用方返回 Command(resume={'approved': True, 'comment': 'ok'}) 后，节点写 approval 并 goto execute_refund。",
            "把 execute_refund 设计成幂等副作用节点，使用 refund_id 作为 idempotency key。",
        ],
    )
    + shell.version_note("LangGraph 的 interrupt API、Command 字段和 stream 事件格式可能随版本扩展，但“中断是可恢复暂停、Command 是恢复/更新/跳转原语、checkpoint/thread_id 是恢复前提”的心智模型稳定。读新版源码时重点跟踪 types.py、errors.py 与 Pregel.stream 的交界。")
    + _points(
        [
            "interrupt 用来把图暂停在可恢复边界，不应被当成普通失败异常。",
            "Command.resume 把人工输入交回等待点，Command.update/goto 表达状态更新和控制流跳转。",
            "人审流程必须依赖稳定 thread_id/checkpoint，并做好权限、结构化 payload 和审计。",
            "高风险副作用放在 interrupt 之后，并使用幂等键防止恢复或重试造成重复执行。",
        ]
    )
)


LESSON_26_TIME_TRAVEL = (
    r"""
<p class="lead">当一个 LangGraph 应用给出坏答案时，最弱的调试方式是只看最终文本。时间旅行调试要求你把运行历史当成一串 <span class="mono">StateSnapshot</span>：每个 snapshot 记录某个 checkpoint 的 values、next、tasks、metadata 和 config。通过 <span class="mono">get_state_history</span> 你可以倒看每一步，通过指定 checkpoint replay 可以复现旧路径，通过 <span class="mono">bulk_update_state</span> 或新的 namespace 可以从某个 checkpoint fork 出实验分支。本课追踪一次“坏答案调查”：检查历史，选中问题 checkpoint，用改过的输入重放或分叉，确认错误来自模型、工具、路由还是状态合并。</p>
"""
    + _analogy("把时间旅行调试想成看足球比赛录像。只看比分 1:2，你不知道输在哪里；逐帧看回放，才能发现第 63 分钟后卫传错、第 64 分钟门将站位太靠前、第 65 分钟丢球。StateSnapshot 就是一帧比赛画面，metadata 是时间和裁判记录，checkpoint 是可以从那一帧重新开球的位置。你不能改变已经发生的正式比赛，但可以在训练场从第 63 分钟重放，换一种传球策略，验证问题是否真的在那里。")
    + shell.lesson_map(
        "本课地图：历史、回放与分叉",
        [
            ("StateSnapshot", "对某个 checkpoint 的可读视图，包含 values、next、tasks、config、metadata", "now"),
            ("History", "get_state_history 按线程列出过去 checkpoint，支持倒查执行轨迹", "source"),
            ("Replay", "用指定 checkpoint_id 作为 config，从旧状态重放后续路径", "now"),
            ("Fork", "在旧 checkpoint 基础上 update 或 bulk_update_state，进入新 namespace 做实验", "now"),
            ("Debug", "map_debug_tasks 把任务事件映射成可读调试信息，帮助定位坏步骤", "after"),
        ],
    )
    + r"""
<h2>源码入口：文件 + 符号名</h2>
<p>时间旅行相关源码要把类型、历史接口、批量状态更新、checkpoint metadata 和 debug task 映射放在一张图里。文件 + 符号名比行号更抗版本漂移，也更适合建立调试工作流。</p>
"""
    + shell.source_map(
        [
            {"file": "langgraph/types.py", "symbol": "StateSnapshot", "role": "运行状态的快照视图，通常包含 values、next、tasks、config、metadata、created_at 等", "direction": "get_state/get_state_history 返回给外部调试或 UI"},
            {"file": "langgraph/pregel/main.py", "symbol": "Pregel.get_state_history", "role": "列出某条 thread/namespace 的 checkpoint 历史，用于回看每一步状态", "direction": "调试器、审计页面、时间旅行 UI 调用"},
            {"file": "langgraph/pregel/main.py", "symbol": "Pregel.bulk_update_state", "role": "按一组 superstep 更新批量构造或修补状态历史，适合回放实验和离线导入", "direction": "在 checkpoint 基础上写入受控更新"},
            {"file": "langgraph/checkpoint/base/__init__.py", "symbol": "CheckpointMetadata", "role": "记录 checkpoint 来源、step、writes、parents 等元信息，帮助解释状态从哪里来", "direction": "saver 存储，history/snapshot 展示"},
            {"file": "langgraph/pregel/debug.py", "symbol": "map_debug_tasks", "role": "把内部 task 执行信息转换成 debug stream 可读事件", "direction": "debug stream 展示任务、输入、输出和错误"},
        ]
    )
    + r"""
<h2>状态流：坏答案调查</h2>
"""
    + shell.state_flow(
        [
            ("发现坏答案", "用户说最终回答引用了错误订单状态。先不要改 prompt，先固定 thread_id 和最终 checkpoint。", "thread_id='case-9'"),
            ("列出历史", "调用 get_state_history，倒序查看每个 StateSnapshot 的 values、next、tasks 和 metadata。", "snapshots=[step5, step4, step3...]"),
            ("定位可疑步", "发现 step=3 工具返回 status='cancelled'，但 step=4 model 回答成 shipped。", "checkpoint_id='step3'"),
            ("重放或分叉", "从 step=3 checkpoint replay，或在新 namespace 中把工具结果改成更完整结构后继续。", "checkpoint_ns='debug-run-1'"),
            ("比较结果", "对比主线与分叉的 writes、next 和最终 answer，判断错误来自工具数据、路由还是模型解释。", "diff snapshots"),
        ]
    )
    + r"""
<h2>Trace：从历史中找坏步骤</h2>
"""
    + shell.trace_table(
        [
            {"step": "1. final snapshot", "input": "answer='订单已发货' 但用户实际已取消", "action": "记录 thread_id、checkpoint_id、模型版本和输入", "output": "可复现实验起点"},
            {"step": "2. history scan", "input": "get_state_history(config)", "action": "查看每个 snapshot 的 values['messages']、next、tasks、metadata.writes", "output": "发现工具消息写入 status='cancelled'"},
            {"step": "3. pick checkpoint", "input": "checkpoint before final model", "action": "选择工具结果已写入、最终模型尚未回答的 checkpoint", "output": "最佳 replay 起点"},
            {"step": "4. fork", "input": "同一 checkpoint + 新 namespace", "action": "bulk/update state 增加 normalized_status='cancelled' 或替换提示输入", "output": "debug 分支，不覆盖主线"},
            {"step": "5. compare", "input": "主线与分支 snapshots", "action": "比较 route、writes、answer", "output": "确认错误是模型没正确解释工具结果，而非工具返回错误"},
        ]
    )
    + r"""
<h2>简化源码走读：历史与快照</h2>
"""
    + shell.code_walkthrough(
        "langgraph/pregel/main.py",
        "Pregel.get_state_history",
        """def debug_bad_answer(graph, config):
    history = list(graph.get_state_history(config))
    for snapshot in history:
        print(snapshot.config, snapshot.next, snapshot.metadata)

    fork_config = history[2].config
    graph.update_state(fork_config, {'normalized_status': 'cancelled'})
    return graph.invoke(Command(goto='final_model'), fork_config)
""",
        "示例代码省略了真实 API 的细节，强调工作流：列出历史，选择 checkpoint，在受控配置或 namespace 中更新状态，再继续运行并比较结果。不要在生产主线随意覆盖历史。",
    )
    + _section(
        "StateSnapshot 应该怎么看",
        [
            "StateSnapshot 不是另一个名字的 state dict。values 告诉你这个 checkpoint 下各 channel 的可见值；next 告诉你如果继续运行，可能调度哪些节点；tasks 告诉你当前或上一步任务状态；config 里通常带 checkpoint_id/thread_id/namespace；metadata 告诉你这个 checkpoint 是怎样产生的。调试时要把这些字段合起来读。",
            "只看 values 容易遗漏控制流问题。比如 messages 没错，但 next 指向了错误节点，说明路由函数或 branch write 有问题；values 和 next 都对，但 tasks 里某个工具报错被 fallback 吞掉，说明错误处理路径有问题；values 最终错误，则要沿 metadata.writes 追踪是哪个 task 写坏了它。",
            "好的调试记录会为每个 snapshot 写一句解释：这一步之前世界是什么，本步哪个 task 写了什么，下一步为什么去那里。这样团队讨论就不再围绕“模型好像乱说”，而是围绕可验证状态转移。",
        ],
    )
    + _section(
        "history 与 replay 的边界",
        [
            "get_state_history 让你回看过去，但回看不等于改变过去。历史 checkpoint 应被当成审计记录，尤其在生产系统中不要随意覆盖。需要实验时，应选择旧 checkpoint 作为起点，在新的 namespace、thread 或明确 debug 分支中继续。这样主线记录保持完整，实验结果也能被比较。",
            "replay 的目标可以不同。若你想验证确定性，就从同一 checkpoint 用同一输入和同一模型设置重跑，看是否得到相同 writes。若你想验证修复，就从同一 checkpoint 改 prompt、改工具结果或改路由规则，观察坏答案是否消失。两种实验不要混在一起，否则无法判断变化来自随机性还是修复。",
            "LLM 的非确定性是现实边界。即使 checkpoint 完全一致，模型温度、provider 版本或工具外部状态变化也可能让 replay 不完全相同。因此关键生产路径应尽量记录模型参数、工具响应摘要和外部请求 id，让回放有足够证据。",
        ],
    )
    + _section(
        "fork from checkpoint 的安全做法",
        [
            "从旧 checkpoint 分叉时，先决定分叉目的：调试、人工修补、A/B 实验还是用户主动回滚。不同目的需要不同 namespace 和权限。调试分支不应影响用户可见主线；人工修补可能要产生新的正式 checkpoint；A/B 实验要记录实验标签。",
            "bulk_update_state 适合批量构造或修补一串状态更新，但也更危险。它能让你快速重建历史或导入离线步骤，同时也可能制造一条没有真实任务执行证据的历史。使用时要在 metadata 中标明来源，例如 operator、reason、import_batch_id。",
            "如果只是一次人工修改，update_state 往往更清晰；如果要把外部系统的一批事件导入为图历史，bulk_update_state 更合适。选择标准不是 API 哪个更强，而是哪一个能最诚实地表达状态来源。",
        ],
    )
    + _section(
        "用 debug task 定位节点级问题",
        [
            "map_debug_tasks 这类调试映射函数的意义是把内部任务结构翻译成人能读的事件。你不必记住每个内部字段，但要知道 debug stream 能回答：哪个 task 被计划，输入是什么，输出写了哪些 channel，是否异常或中断。",
            "坏答案调查通常按三层缩小范围。第一层看输入与最终输出：问题是什么，答案错在哪里。第二层看 state history：错误字段从哪个 checkpoint 开始出现。第三层看 debug tasks：是哪个节点/任务写入了错误字段，还是哪个路由把正确字段送到了错误节点。",
            "一旦定位到任务，不要马上改 prompt。先判断该任务读到的输入是否正确。如果输入错，修上游 state 或 reducer；如果输入对但输出错，才考虑 prompt、模型、工具或节点逻辑。很多所谓“模型幻觉”其实是上游工具结果丢字段或消息合并顺序错误。",
        ],
    )
    + _section(
        "一次完整调查报告模板",
        [
            "报告开头写清楚 thread_id、主线 checkpoint_id、用户可见坏答案和预期答案。接着列出关键 snapshots：输入进入、工具调用、工具结果写入、最终模型回答。每个 snapshot 标明 step、next、关键 values 和 metadata.writes。最后给出定位结论：错误来自工具、路由、reducer、prompt 还是外部数据。",
            "然后写分叉实验。说明从哪个 checkpoint fork，在哪个 namespace，修改了什么输入或状态，运行了哪些节点，结果如何变化。如果修复后答案正确，要解释为什么这能证明根因；如果没有变化，要记录排除的假设。调试是一组可复查实验，不是一次灵感猜测。",
            "最后写修复建议和回归验证。比如增加工具结果 schema 校验、给 documents channel 加去重 reducer、调整 final_model prompt 强制引用 tool status、或在 route 中处理 cancelled 状态。修复后应保留最小可复现 thread 或测试用例，防止同类坏答案再次出现。",
        ],
    )
    + _section(
        "工程复盘：把调试变成可复现实验",
        [
            "坏答案调试最忌讳边改边猜。看到模型说错，立刻改 prompt，也许能让这一次输出变好，却无法证明根因。时间旅行提供的是实验方法：固定一条历史，找到错误第一次出现的 checkpoint，只改变一个变量，重放后比较结果。这样每次修改都有证据，而不是凭感觉调参。",
            "第一份证据是输入证据。记录用户原始输入、运行 config、thread_id、checkpoint namespace、模型参数和工具环境。如果这些信息不固定，后面所有 replay 都可能变成另一场实验。尤其是外部工具会随时间变化，最好保存工具响应摘要或请求 id，方便区分框架问题和外部数据变化。",
            "第二份证据是状态证据。get_state_history 给出 snapshots，但你需要挑关键帧：输入进入后、路由前、工具返回后、最终模型前、最终回答后。每一帧都写出关键 values 和 next。这样就能判断错误是从工具结果开始，还是工具结果正确但模型解释错。",
            "第三份证据是写入来源。metadata.writes 或 debug tasks 能告诉你哪个 task 写了错误字段。字段错并不等于写字段的节点错；也可能是它读到的输入已经错。沿着 writes 往上游追，直到找到第一个从正确变错误的边界，这才是根因候选。",
            "fork 实验要一次只改一个因素。若同时改 prompt、工具结果和 reducer，答案变好也无法解释原因。可以先从同一 checkpoint 重放原配置，验证是否稳定复现；再只改工具结果结构；再只改 final prompt；再只改路由条件。每个分支都记录 namespace 和修改说明。",
            "比较结果时不要只看最终文本。还要比较中间 snapshots：路由是否改变，documents 是否排序不同，approval 是否出现，final_model 输入是否包含关键字段。有时候最终答案都正确，但中间路径更脆弱；有时候最终答案仍错，却已经排除了工具层问题。",
            "时间旅行也能帮助写回归测试。把最小坏历史抽象成一个小图或固定 snapshots，断言修复后某个 checkpoint 之后的路由、写入或最终 answer 符合预期。测试不一定要重放真实生产数据，但要覆盖导致事故的状态转移。",
            "不要把生产历史当成随意编辑的草稿。审计系统需要知道真实发生过什么，即使它是错误的。修复应该产生新的 checkpoint 或分支，保留原始错误路径。覆盖历史也许让界面干净，却会让事故复盘失去证据。",
            "团队协作时，建议把调试结论写成假设表：假设 A 是工具返回错，证据是什么，实验如何排除；假设 B 是模型解释错，证据是什么，修复如何验证。StateSnapshot 和 checkpoint id 是表里的引用，而不是口头描述。这样评审者能复查每个结论。",
            "最终，时间旅行调试的价值不只是找到一次 bug，而是训练团队用状态转移思考 Agent。坏答案不是神秘事件，而是一串可观察、可分叉、可比较的步骤。只要保存足够历史并按实验方法分析，复杂图也能像普通程序一样被定位和修复。",
        ],
    )
    + r"""
<h2>常见误解与边界情况</h2>
"""
    + shell.pitfall_grid(
        [
            ("时间旅行就是把历史改掉", "历史用于审计；实验应从 checkpoint 分叉到新 namespace 或明确产生新 checkpoint。"),
            ("StateSnapshot 只看 values", "还要看 next、tasks、config、metadata，才能解释控制流和写入来源。"),
            ("replay 一定逐 token 相同", "LLM/provider/外部工具可能非确定；要记录参数和外部响应，并区分确定性验证与修复实验。"),
            ("坏答案一定是 prompt 问题", "先沿 history 找到错误首次出现的 step，可能是工具、reducer、路由或状态覆盖导致。"),
        ]
    )
    + _section(
        "实践提示：调试报告如何写得可复查",
        [
            "一份好的时间旅行报告开头要列出固定坐标：thread_id、checkpoint_ns、最终 checkpoint_id、模型配置、用户原始输入和错误现象。没有这些坐标，别人无法复现实验。",
            "报告主体应列关键 snapshots，而不是贴完整历史。通常选择输入后、工具前、工具后、最终模型前、最终输出后五类快照。每个快照写 values 摘要、next、关键 writes 和判断。",
            "然后列根因假设。比如工具返回错、工具返回对但消息合并错、路由跳错节点、final prompt 忽略了 cancelled 字段、模型随机性导致解释错。每个假设都要对应证据或实验。",
            "分叉实验要说明只改变了什么。例如只把 status 字段从自然语言改成枚举，或只改 final_model prompt，或只改 documents reducer。一次改多个因素会让结论不可解释。",
            "比较结果时要用表格列主线与分支的同一 step：输入、writes、next、answer。这样评审者能看到变化从哪里开始，而不是只相信“改完好了”。",
            "如果 replay 不能稳定复现，也要记录。非确定性本身就是结论，可能需要降低 temperature、缓存工具响应、固定 provider 版本或改用更确定的解析节点。",
            "修复建议应落到图结构或测试：添加 schema 校验、拆分 channel、修改 reducer、调整 route、增加人审、修改 prompt。只说“优化模型回答”太模糊，不能防回归。",
            "最后把最小复现纳入回归检查。未来有人改图时，测试应能捕捉同类状态转移错误。时间旅行的终点不是一份报告，而是一条可自动验证的经验。",
        ],
    )
    + _section(
        "补充推演：选择正确的回放起点",
        [
            "时间旅行实验最重要的选择，是从哪个 checkpoint 开始。起点太早，会重复太多无关步骤，外部工具和模型随机性增加；起点太晚，错误已经写入最终状态，无法观察它是怎样产生的。理想起点通常在可疑写入之前一两步。",
            "调查 cancelled 被说成 shipped 时，如果工具结果本身就是 shipped，回放起点应选工具调用前，重点检查工具输入和外部数据；如果工具结果是 cancelled，但最终模型说 shipped，起点应选工具结果已写入、final_model 尚未运行的 checkpoint，重点检查 prompt 和模型解释。",
            "如果怀疑 reducer 覆盖了字段，起点应选并行写入发生前。重放时观察 apply_writes 后 channel 值如何变化。如果两个任务分别写 cancelled 和 shipped，而 LastValue 只保留一个，就说明合并语义错误。",
            "如果怀疑路由错误，起点应选路由节点运行前。比较主线和分支的 next 字段，能看出是条件函数判断错，还是上游状态给了它错误信号。不要只看最终答案，因为错误路由可能之后被模型掩盖。",
            "如果怀疑人工 update 引入问题，起点应选 update_state 前一个 checkpoint，并检查 metadata 中的操作者和原因。人工修补也是状态转移，必须像节点写入一样被审计。",
            "选择起点的原则是让实验最小化：包含产生错误所需的全部上下文，排除已经确定无关的早期步骤。这样的回放更快、更稳定，也更容易说服评审者。",
        ],
    )
    + _section(
        "复盘校验：让时间旅行结论可复现",
        [
            "时间旅行调试的交付物不应只是“我 fork 后好了”，而应是一份可复现结论。开头固定列 thread_id、checkpoint_ns、起点 checkpoint_id、模型和工具版本、原始输入、错误输出、选择该起点的理由。坐标越精确，别人越能判断实验是否真的隔离了变量。",
            "报告正文要按状态转移写证据：错误前一个 snapshot 的 values/next/tasks，错误写入发生时的 metadata.writes，错误后下游节点读到了什么。若只贴最终 answer，就无法区分是工具错、reducer 覆盖、路由误判、prompt 忽略字段，还是模型非确定性解释错。",
            "Fork 实验一次只改一个因素，并写清改动位置：某个 channel 值、某条 reducer、某个 route 条件或某段 prompt。比较主线和分支时，用同一 step 的 writes、next、关键 values 和最终输出对齐。这样评审者能看到修复从哪一步改变了状态，而不是只相信分支结果更好。",
            "最后把复盘收束为回归项。若根因是状态 schema，应新增 reducer/冲突测试；若根因是路由，应新增条件函数样例；若根因是 prompt 忽略字段，应固定输入 snapshot 做评估。时间旅行的价值在于把一次事故变成可自动检查的状态转移知识。",
        ],
    )
    + shell.lab_card(
        "做一次坏答案时间旅行",
        [
            "选一条带 thread_id 的错误运行，保存最终 checkpoint_id 和用户反馈。",
            "调用 get_state_history，挑出工具结果写入前后、最终模型前后的三个 snapshots。",
            "写出每个 snapshot 的 values、next、metadata.writes，并标记错误第一次出现的位置。",
            "从错误前一个 checkpoint fork 到 debug namespace，修改一个变量后继续运行。",
            "比较主线和分支输出，写出根因假设、排除项和修复建议。",
        ],
    )
    + shell.version_note("时间旅行调试依赖 checkpoint 后端保存足够历史。LangGraph 版本可能改变 StateSnapshot 字段名、metadata 细节或 bulk_update_state 参数；但历史列表、指定 checkpoint 读取、分叉实验和 debug task 映射这四个概念是稳定的调试骨架。")
    + _points(
        [
            "StateSnapshot 是 checkpoint 的可读视图，调试时要同时看 values、next、tasks、config 和 metadata。",
            "get_state_history 把最终坏答案拆回一串状态转移，帮助定位错误第一次出现的 step。",
            "replay 用来复现，fork 用来实验；不要随意覆盖生产主线历史。",
            "坏答案调查应先追状态和写入来源，再决定是否修改 prompt、工具、reducer 或路由。",
        ]
    )
)
