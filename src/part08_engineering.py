"""C-level Part 8: engineering, testing, and capstone."""

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
    html += "<h2>Trace：把一次工程动作摊平成证据链</h2>" + shell.trace_table(d["trace"])
    html += "<h2>简化源码走读：保留契约，不背实现</h2>" + shell.code_walkthrough(
        d["code_path"], d["code_symbol"], d["code"], d["code_note"]
    )
    for title, paragraphs in d["sections"]:
        html += _section(title, paragraphs)
    html += shell.pitfall_grid(d["pitfalls"])
    html += shell.lab_card(d["lab_title"], d["lab_steps"])
    html += shell.version_note(d["version_note"])
    html += _points(d["points"])
    return html


LESSON_37_LOCAL_DEV = _build_lesson(
    {
        "lead": "读源码和贡献不是从克隆仓库后盲目全量测试开始，而是从一个公开 API 的归属开始：先判断它属于 langchain、langchain-core、langgraph 还是本教程生成器，再进入对应包的 pyproject、测试目录和 CI 规则。工程化学习的目标不是记住每个目录，而是建立一条可复查路线：选择 API、找到包边界、用 editable 环境让本地源码参与 import、写或跑一个聚焦测试、用 CI 同款检查证明生成物没有漂移，最后把变更压成小 PR。本课把本地开发、源码调试、包布局和贡献循环合成一条新手可执行的工作流。",
        "analogy": "把本地开发想成修一座大型商场的某个电梯。你不能一进门就拆总配电，也不能只看门口导览图就动手。正确做法是先确认电梯属于哪栋楼、哪家维保、哪张图纸；再把自己的维修工具接到这台电梯的控制柜；只跑这台电梯相关的安全测试；最后把维修记录交给物业验收。LangChain 的包边界就是楼栋，editable install 是把本地控制柜接入运行环境，聚焦测试是安全试运行，PR 是可审计维修单。",
        "map_title": "本课地图：从想改一个 API 到可审计 PR",
        "map_nodes": [
            ("选择入口", "从 docs、示例或报错中确定要研究的 API，例如 create_agent、Runnable 或 @tool", "before"),
            ("定位包边界", "根据 import 路径回到 langchain_v1、core、LangGraph 或本教程 src 目录", "now"),
            ("建立 editable 环境", "让解释器导入本地源码而不是已安装 wheel，使断点和修改立即生效", "now"),
            ("聚焦测试", "先跑最小单测或生成器检查，再扩大到相关包 CI，避免用全量测试掩盖问题", "source"),
            ("小 PR 循环", "提交源码、测试、生成 HTML/PDF 差异和路径说明，让 reviewer 能复现", "after"),
        ],
        "source_intro": "下面的 source map 特意使用当前已验证路径。LangChain 主仓当前没有根目录 pyproject；包级配置在 libs/langchain_v1/pyproject.toml 与 libs/core/pyproject.toml，LangGraph 在独立 langchain-ai/langgraph 仓库的 libs/langgraph/pyproject.toml。本教程自己的工程守卫则在 src/build.py、src/check_* 和 .github/workflows/ci.yml。",
        "sources": [
            {"file": "langchain/libs/langchain_v1/pyproject.toml", "symbol": "[project] / [dependency-groups] / [tool.uv.sources]", "role": "声明 langchain v1 包名、依赖、测试/类型/lint 组和 editable 本地源码来源", "direction": "确定 create_agent 等高层入口属于哪个包以及本地开发依赖如何连线"},
            {"file": "langchain/libs/core/pyproject.toml", "symbol": "langchain-core package", "role": "声明核心协议包，包含 Runnable、消息、工具、回调等稳定契约", "direction": "上层包和 partner 包依赖它，贡献时要特别关注兼容性"},
            {"file": "langgraph/libs/langgraph/pyproject.toml", "symbol": "langgraph package", "role": "声明图运行时包和 langgraph-checkpoint/prebuilt/sdk 等 editable 来源", "direction": "Agent 循环、checkpoint 和图执行相关问题要回到独立 LangGraph 仓库核验"},
            {"file": "src/build.py", "symbol": "build", "role": "本教程把 registry.CONTENT 与 quizzes.render 组合成 lessons 与 index", "direction": "修改课程内容后必须重新生成站点 HTML"},
            {"file": "src/check_html.py", "symbol": "check_lesson / check_stale", "role": "检查结构、导航、陈旧文案、要点卡和类比卡", "direction": "本地和 CI 都用它防止生成 HTML 结构回归"},
            {"file": ".github/workflows/ci.yml", "symbol": "verify job", "role": "重建站点和 print，再跑链接、HTML 与密度检查", "direction": "PR 前本地模拟同款命令，避免提交过期生成物"},
        ],
        "flow_title": "状态流：一次本地源码调试与贡献循环",
        "flow_kind": "state_flow",
        "flow_steps": [
            ("选定 API", "从失败用例或文档疑问出发，写下 import 路径和预期行为。", "api='langchain.agents.create_agent'"),
            ("找包和文件", "用 import 前缀、pyproject 和 source map 判断它落在 langchain_v1、core 还是 langgraph。", "package=langchain_v1"),
            ("接 editable 环境", "用包级 uv/venv/conda 环境把本地 libs 路径作为可编辑来源，确认 python 导入的是工作区文件。", "editable=True"),
            ("跑聚焦测试", "先运行最靠近改动的单测或本教程 check，再扩到相关包的 lint/type/test。", "pytest path::test_name"),
            ("提交 PR", "附上源码锚点、测试输出、生成 HTML 差异和兼容性说明。", "small-reviewed-PR"),
        ],
        "trace": [
            {"step": "1. choose API", "input": "用户报告 create_agent 对某个 middleware 组合行为异常", "action": "记录公开入口、最小复现、期望消息状态", "output": "待查入口 langchain.agents.create_agent"},
            {"step": "2. find package", "input": "import path + source map", "action": "确认高层入口在 langchain/libs/langchain_v1，消息和 Runnable 在 libs/core，图执行在 LangGraph", "output": "文件候选 factory.py、types.py、core messages"},
            {"step": "3. editable env", "input": "包级 pyproject 与 tool.uv.sources", "action": "让本地源码覆盖已安装 wheel，并用 python -c 打印 module.__file__", "output": "导入路径指向工作区 libs/..."},
            {"step": "4. focused test", "input": "最小复现与相关测试文件", "action": "先跑单个失败测试，再跑相关包测试组或本教程 check_*", "output": "红灯证明问题存在，绿灯证明修复有效"},
            {"step": "5. PR", "input": "源码 diff、测试输出、生成 HTML diff", "action": "提交小而完整的变更，说明包边界和兼容性", "output": "reviewer 可复现、CI 可验证"},
        ],
        "code_path": "src/build.py + .github/workflows/ci.yml",
        "code_symbol": "build / verify job",
        "code": """# 教学版：本教程内容改动后的贡献循环
changed = ["src/part08_engineering.py", "src/quizzes.py"]

run("cd src && python build.py")
run("cd src && python build_print.py")
run("cd src && python check_links.py")
run("cd src && python check_html.py")
run("cd src && python check_content_density.py")

assert git_diff("index.html", "lessons/", "print.html").is_committed()
""",
        "code_note": "真实 LangChain 包开发会使用包级 uv/pytest/ruff/mypy；本教程是静态站点，所以贡献循环强调 build、print、链接、结构和密度。共同原则相同：源码改动必须有可复现检查，生成物必须与源码同步。",
        "sections": [
            ("先确认你在改哪个包", [
                "大型 Python monorepo 里最容易犯的错，是把 import 名称、发布包名称和仓库目录混在一起。langchain.agents.create_agent 是用户 API，但它不是 langchain-core 的稳定协议；Runnable、AIMessage、BaseCallbackHandler 属于 langchain-core；checkpoint 和图执行能力来自 LangGraph。贡献前先写下三列：用户 import、源码文件、发布包。三列对齐，后面的测试和 reviewer 说明才不会跑偏。",
                "包边界还决定兼容性承诺。core 的符号被很多包依赖，修改参数、返回类型或异常语义会影响广泛；高层 langchain_v1 可以组合 core 和 langgraph，但也要保护用户 API；本教程 src 目录则是生成器，修改内容后要提交生成的 HTML。不同边界对应不同风险，不应同样处理。",
            ]),
            ("Editable install 的意义不是省安装时间", [
                "editable install 的关键价值是让解释器导入你的工作区源码。没有这一步，你可能在编辑 A 文件，却一直运行环境里旧 wheel 的代码，断点打不到、print 不出现、测试也不会反映修改。确认方式很简单：在 Python 中打印目标模块的 __file__，路径必须指向当前 worktree 或克隆目录，而不是 site-packages 里的压缩发布物。",
                "LangChain 与 LangGraph 的 pyproject 中都有 tool.uv.sources 指向相邻包的本地路径。这个配置说明维护者希望开发时让多个包以源码方式联动：改 core 后 langchain_v1 立即看到，改 prebuilt 或 checkpoint 后 langgraph 测试能覆盖。若这些来源路径和你本地目录不一致，要先修环境，不要急着怀疑业务代码。",
            ]),
            ("聚焦测试比全量测试更适合调试", [
                "全量测试很重要，但不适合第一步。全量失败时你很难知道哪个失败与本次修改有关；全量通过也可能掩盖你没有覆盖具体边界。更好的顺序是：先写或找到一个最小失败测试，只验证一个行为；让它红；修复；让它绿；再跑相邻模块测试；最后跑 CI 同款命令。这个梯度让每个信号都有解释。",
                "本教程的聚焦测试是 build.py、build_print.py、check_links.py、check_html.py、check_content_density.py。内容类改动最常见失败不是 Python 逻辑，而是生成 HTML 没提交、链接断了、课程缺少 source_map 或 CJK 密度不足。先跑这些检查，能在本地发现 CI 会拒绝的 drift。",
            ]),
            ("源码调试从入口往内钻", [
                "调试公开 API 时，不要从最长的内部文件开始。先在调用点确认输入对象，再跳到 public factory 或 base class，看它把输入标准化成什么协议；然后跟到具体实现或图节点；最后用测试验证维护者承诺的行为。这个顺序和课程前面反复强调的 source map 一致：入口、契约、实现、测试。",
                "断点也要按状态边界放。对 Agent 问题，先看 create_agent 收到的 tools、middleware、context_schema；再看模型节点输出的 AIMessage；再看 ToolMessage 是否写回；最后看 structured_response。对静态教程问题，先看 registry.CONTENT 是否映射正确，再看 build 输出，再看检查器解析到的原始 HTML。",
            ]),
            ("PR 应该小到能被 reviewer 复现", [
                "好的 PR 不只是代码少，而是证据完整。标题说明行为，描述列出源码锚点，测试区贴出具体命令和结果，风险区说明公共 API 是否变化，生成物区说明 index、lessons、print 是否同步。reviewer 不应该通过猜测理解你的意图，也不应该重新设计一遍才能判断变更是否安全。",
                "小 PR 还保护贡献者自己。若一次同时改包布局、API 行为、文档和大量快照，任何 CI 失败都难定位。把环境修复、行为修复、文档更新、生成物同步分成可审计步骤，回滚也更容易。工程化贡献的核心不是让改动显得大，而是让因果链短。",
            ]),
            ("本教程的生成物也是源代码责任", [
                "很多静态站点把 HTML 当产物不提交，本仓库相反：index.html、lessons/ 和 print.html 都是需要随 src 同步的发布内容。CI 会重新运行 build，并用 git diff 检查提交的 HTML 是否过期。这意味着改 src/part08_engineering.py 或 src/quizzes.py 后，未重新生成就提交，属于不完整变更。",
                "生成物同步不是形式主义。读者直接打开 index.html 或 GitHub Pages 时看到的是 HTML，不是 Python 源。若源码和 HTML 漂移，reviewer 看源觉得正确，用户却读到旧页面。CI 的 diff gate 把这种风险提前暴露，等价于软件项目里检查编译产物或 API schema 是否随源更新。",
            ]),
            ("常见误解与边界情况：环境问题不是业务问题", [
                "常见误解是“测试没失败，所以源码路径肯定对”。如果你没有确认 module.__file__，测试可能跑的是已安装版本；如果你没有让最小复现先红，测试可能没有覆盖目标行为。另一个误解是“全量 CI 失败一定是我这行代码错了”。在大型仓库里，环境、缓存、依赖约束、生成物漂移都可能导致失败，必须先用聚焦检查缩小范围。",
                "边界情况是跨仓贡献。LangChain 主仓和 LangGraph 独立仓的版本、目录和发布节奏不同；教程里的源码路径也可能随着上游重组而变化。因此本文使用文件 + 符号名而不是行号，并在发现计划路径过期时更新计划。贡献时也要在 PR 描述中写明自己核验的是哪个仓库和哪个时间点。",
            ]),
            ("贡献前自查清单", [
                "第一，公开 API、源码文件、发布包三者是否对齐。第二，环境是否真正 editable，导入路径是否指向工作区。第三，是否有一个聚焦测试或检查证明问题被覆盖。第四，是否跑过与改动同层的检查。第五，生成物是否随源码提交。第六，PR 描述是否能让陌生 reviewer 复现。",
                "这张清单看似琐碎，却能节省大量 review 往返。维护者最怕的不是新手问问题，而是收到无法复现、边界不清、没有测试、生成物过期的改动。把证据链补齐，就是对开源协作的尊重，也是自己学习源码最快的方式。",
            ]),
            ("从本地失败到教学素材", [
                "工程化学习的一个技巧，是把每次失败都转成 source map 的一行。今天因为 check_content_density 失败，就记住它从 registry.CONTENT 读原始 lesson body 而不是读 lessons/*.html；明天因为链接失败，就记住 check_links.py 解析所有相对 href。失败越具体，你的源码地图越可靠。",
                "同样方法也适用于 LangChain。一次 Fake 模型测试失败，可以补充 GenericFakeChatModel 的行为；一次 Agent 工具循环失败，可以补充 AIMessage.tool_calls 和 ToolMessage 的配对规则。读源码不是一次性任务，而是把调试证据持续沉淀成可复查路径。",
            ]),

            ("多包仓库里的调试礼仪", [
                "在多包仓库中工作，还要尊重依赖方向。不要为了让一个高层测试通过，就让 langchain-core 反向导入 langchain_v1 或某个 partner；不要为了省事在 core 里读取环境变量、调用具体 provider SDK 或依赖图运行时。稳定层越干净，边缘包越能独立演进。调试时若发现自己想从底层 import 高层，通常说明修复点选错了，应该把适配逻辑留在上层，或通过协议把需要的信息向下传递。",
                "贡献者还要学会阅读 pyproject 里的依赖组。test、lint、typing、dev 不是装饰字段，而是维护者定义的本地工作模式。某个包只改文档，可能不需要跑所有集成测试；但改公共协议，就至少要跑该包测试和依赖它的高层测试。写 PR 时说明自己为什么选择这些检查，比只写“tests pass”更可审计。",
                "source debugging 也包括理解失败来自构建系统还是运行系统。本教程的失败可能来自 HTML 结构、导航链、密度门槛；LangChain 的失败可能来自 mypy、ruff、pytest、snapshot、依赖约束。先给失败分类，再决定修代码、修测试、修生成物还是修环境。没有分类的调试会在同一堆日志里反复横跳。",
            ]),
            ("贡献记录应留下学习路径", [
                "一份好的贡献记录能让后来者复用你的路线。假设你修了一个 tool schema 问题，PR 描述可以写：公开入口是 @tool，契约在 StructuredTool，失败测试在某个单测，修复影响参数描述生成，不改变工具调用返回类型。这样的记录不只是给 reviewer 看，也会在半年后帮助另一个新手快速进入上下文。",
                "本教程要求 source rows 和版本锚点，也是同一思想。内容不是凭经验写成，而是说明当前核验到哪个仓库、哪个文件、哪个符号。上游路径变化时，计划文档要跟着修正，而不是让读者在旧路径里迷路。工程化写作和工程化代码一样，都要为未来维护成本负责。",
                "最后，贡献循环要保持可逆。每次提交只解决一个清晰问题，生成物和源码一起提交，测试输出可复现，路径修正单独说明。这样即使 reviewer 要求调整，你也能快速定位并修改；如果某个假设错了，也能回滚局部，而不是推倒整个分支。",
            ]),

            ("把源码阅读变成可复制路线", [
                "当你第一次进入一个陌生包，不要急着追所有 import。先建立一张小表：入口函数在哪里，输入输出对象是什么，哪些 base class 或 protocol 定义契约，哪些 tests 展示承诺行为，哪些 CI 命令会保护这些承诺。表格只要五到八行，却能让你从“看见很多文件”变成“知道下一步打开哪个文件”。这也是本课反复强调 source_map 的原因。",
                "路线还要记录没有走的路。例如本次核验发现 LangChain 主仓没有根 pyproject，计划中旧路径就必须标记为过期；发现 LangGraph 在独立仓库，就不能继续写 langchain/libs/langgraph。把这些负面发现写下来，可以防止后来的读者重复踩坑。工程化学习不只是知道正确答案，也包括知道哪些旧答案已经失效。",
                "最后，把每次本地检查结果当成提交资产。一次完整任务应能回答：哪些文件改了，哪些生成物更新了，哪些检查通过了，CJK 密度是多少，quiz 答案分布如何，路径修正是什么。这样的交付报告让维护者马上判断质量，也让未来回溯时有明确证据。",
            ]),

            ("维护者视角下的完整交付", [
                "从维护者视角看，一个贡献是否成熟，关键不是作者花了多少时间，而是变更能否被快速验证。维护者会先看范围是否单一，再看源码锚点是否可信，再看测试是否覆盖行为，再看生成物是否同步，最后看描述是否说明兼容性。若这些信息都齐全，review 可以讨论设计；若缺失，review 只能先要求补证据。",
                "因此新手要把每次任务当成交付练习：先写清楚要改哪一层，过程中保留失败和通过的命令，发现计划路径过期就立即修正文档，结束时报告 CJK 计数、检查结果、答案分布和 commit。这样的习惯会让你在任何大型开源项目中更快获得信任。",
            ]),

            ("最后一公里：报告要能复盘", [
                "完成任务后不要只说已经改好，而要列出文件、检查、计数、路径修正和提交号。报告本身也是工程资产：它告诉接手者哪些假设被验证，哪些生成物已经更新，哪些风险仍需后续任务处理。一个清晰报告能减少维护者重新拉分支检查的成本。",
            ]),

            ("补充复盘", [
                "复盘时还要保存反例：哪些路径原计划可用但当前不存在，哪些检查曾经失败，哪些命令只能在包级目录运行。这些细节会随着仓库演进而变化，写进课程能帮助读者建立版本意识。工程化贡献的最后一步，是让下一位维护者不必重新猜你的调查过程。",
                "为了让密度和质量同时达标，本课把路线、证据、边界、失败模式和交付报告都纳入正文。读者不只知道怎么操作，还知道为什么这些操作能减少风险、缩短排障时间、提高协作可信度。",
            ]),
        ],
        "pitfalls": [
            ("先跑全量测试才专业", "先跑最小相关测试，定位清楚后再扩大到包级和 CI 级检查。"),
            ("编辑源码就等于运行源码", "必须确认 editable 环境和 module.__file__，否则可能运行旧 wheel。"),
            ("行号是最精确引用", "行号随版本漂移；教学和 PR 说明优先使用文件 + 符号名。"),
            ("生成 HTML 是 CI 的事", "本仓库要求提交生成 HTML/PDF 源，CI 只验证没有漂移。"),
        ],
        "lab_title": "定位一个 API 并准备小 PR",
        "lab_steps": [
            "选择一个你想理解的 API，写出 import 路径、源码候选文件和发布包名称。",
            "在本地环境中打印该模块的 __file__，确认它是否来自工作区源码。",
            "找到最靠近该 API 的一个测试或本教程检查命令，只运行这一项并记录输出。",
            "写一段 PR 描述草稿：问题、修改、源码锚点、测试命令、生成物是否同步。",
            "检查草稿里是否还有无法复现的词，例如“应该”“好像”“相关测试都过了”。",
        ],
        "version_note": "路径核验于 2026-06：LangChain 主仓 master 当前无根 pyproject.toml，包配置位于 langchain/libs/langchain_v1/pyproject.toml 与 langchain/libs/core/pyproject.toml；LangGraph 位于独立 langchain-ai/langgraph 仓库的 libs/langgraph/pyproject.toml。本教程 CI 路径以当前仓库 .github/workflows/ci.yml 为准。",
        "points": [
            "从公开 API 到包边界，是源码调试的第一步。",
            "editable install 要用 module.__file__ 验证，不能凭感觉。",
            "聚焦测试先红再绿，再扩大到包级和 CI 级检查。",
            "本教程的 src 与生成 HTML/print 必须同步提交。",
            "PR 的价值在于可复现证据链，而不是一次改很多。",
        ],
    }
)


LESSON_38_TESTING_DEBUGGING = _build_lesson(
    {
        "lead": "测试 Agent 不是把真实模型、真实网络和真实数据库都接上后祈祷输出稳定，而是把不确定性逐层替换成可控组件：GenericFakeChatModel 提供固定 AIMessage，确定性工具返回固定观察，InMemorySaver 保存线程状态，Runnable 接口让每个节点可单独 invoke，create_agent 把这些零件装成完整循环。这样写出的测试关注结构行为：模型是否请求了正确工具、工具观察是否写回 messages、checkpoint 是否能恢复、回归案例是否锁住曾经失败的 trace，而不是脆弱地断言某一句自然语言完全相同。",
        "analogy": "把 Agent 测试看成消防演习。真正火灾不可控，所以演习不会点燃整栋楼，而是用烟雾机、假警报、固定路线和观察员记录来验证流程：警报是否响、人员是否按路线撤离、门禁是否打开、负责人是否签收。Fake 模型是烟雾机，确定性工具是假警报，trace 断言是观察员记录，回归用例是把上次演习暴露的问题写进下一次检查表。",
        "map_title": "本课地图：确定性 Agent 测试的五个零件",
        "map_nodes": [
            ("Fake 模型", "用 GenericFakeChatModel 或固定消息模型产出预设 AIMessage/tool_calls", "before"),
            ("确定性工具", "工具只依赖测试输入和内存 fixtures，不访问真实网络或随机时间", "now"),
            ("消息断言", "检查 AIMessage、ToolMessage、structured_response 和 messages 长度", "now"),
            ("检查点", "用 InMemorySaver 验证 thread_id 下状态保存、恢复和回放", "source"),
            ("回归 Trace", "把线上失败压缩成最小消息序列，防止同类问题再出现", "after"),
        ],
        "source_intro": "测试课的 source map 选择运行契约和测试替身。GenericFakeChatModel、AIMessage、Runnable、create_agent 在 LangChain 主仓；InMemorySaver 在独立 LangGraph 仓库 checkpoint 包。这些路径帮助你把测试失败定位到模型替身、消息结构、可运行接口、图状态或 Agent 工厂。",
        "sources": [
            {"file": "langchain/libs/core/langchain_core/language_models/fake_chat_models.py", "symbol": "GenericFakeChatModel", "role": "按迭代器返回预设 AIMessage 或字符串，并支持 token callback 测试", "direction": "替代真实聊天模型，让测试输出可复现"},
            {"file": "langchain/libs/core/langchain_core/messages/ai.py", "symbol": "AIMessage", "role": "承载模型内容、tool_calls、usage 和附加字段", "direction": "Fake 模型输出它，Agent 条件边和 ToolNode 读取它"},
            {"file": "langchain/libs/core/langchain_core/runnables/base.py", "symbol": "Runnable", "role": "统一 invoke/ainvoke/stream/batch/config，使组件可单独测试", "direction": "prompt、model、tool wrapper、graph 都遵守该契约"},
            {"file": "langgraph/libs/checkpoint/langgraph/checkpoint/memory/__init__.py", "symbol": "InMemorySaver", "role": "测试和本地调试用的内存 checkpoint 保存器", "direction": "create_agent/graph 运行时按 thread_id 保存和恢复状态"},
            {"file": "langchain/libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "把模型、工具、中间件、checkpointer、response_format 组装成 Agent 图", "direction": "端到端测试入口，同时把内部节点暴露为可追踪运行"},
        ],
        "flow_title": "状态流：用假模型、工具和 checkpointer 跑一次确定性测试",
        "flow_kind": "state_flow",
        "flow_steps": [
            ("准备消息脚本", "Fake 模型第一轮返回带 tool_calls 的 AIMessage，第二轮返回最终 AIMessage。", "messages=iter([call_tool, final])"),
            ("准备工具 fixture", "工具 search_order('A1') 固定返回订单状态，不读真实数据库。", "tool_result='已发货'"),
            ("创建 Agent", "create_agent(model=fake, tools=[tool], checkpointer=InMemorySaver())。", "agent=CompiledStateGraph"),
            ("invoke 并断言 trace", "用 thread_id 运行，检查工具被调用一次、ToolMessage 写回、最终消息不再请求工具。", "assert messages[-1].tool_calls == []"),
            ("复跑回归", "用相同脚本和 thread_id 或新 thread_id 验证状态隔离与曾经失败的边界。", "regression locked"),
        ],
        "trace": [
            {"step": "1. arrange fake", "input": "两个预设 AIMessage：先请求 search_order，后回答用户", "action": "GenericFakeChatModel 从迭代器依次取消息", "output": "模型行为完全可预测"},
            {"step": "2. arrange tool", "input": "内存字典 {'A1': '已发货'}", "action": "@tool 函数只查 fixture，不访问网络、不读当前时间", "output": "ToolMessage 内容固定"},
            {"step": "3. invoke agent", "input": "messages=[HumanMessage('查 A1')] + config.thread_id", "action": "Agent 进入 model -> tools -> model 循环", "output": "状态中出现 AIMessage.tool_calls 与 ToolMessage"},
            {"step": "4. assert state", "input": "result['messages'] 或 state snapshot", "action": "断言工具名、参数、tool_call_id、最终 structured_response", "output": "测试锁住结构，不锁死自然语言措辞"},
            {"step": "5. regression", "input": "曾经失败的消息序列", "action": "加入测试集，确保以后 refactor 不破坏", "output": "同类 bug 被自动捕获"},
        ],
        "code_path": "tests/unit_tests/agents/test_customer_agent.py",
        "code_symbol": "deterministic fake agent test",
        "code": """fake = GenericFakeChatModel(messages=iter([
    AIMessage(content="", tool_calls=[{"name": "search_order", "args": {"order_id": "A1"}, "id": "call_1"}]),
    AIMessage(content="订单 A1 已发货，建议明天关注物流。"),
]))

@tool
def search_order(order_id: str) -> str:
    return {"A1": "已发货"}[order_id]

agent = create_agent(fake, tools=[search_order], checkpointer=InMemorySaver())
result = agent.invoke({"messages": [{"role": "user", "content": "查 A1"}]}, config={"configurable": {"thread_id": "t1"}})
assert result["messages"][-1].tool_calls == []
""",
        "code_note": "教学代码突出测试形状：Fake 模型负责固定动作，工具 fixture 固定观察，checkpointer 固定状态保存位置，断言看消息结构。真实测试还会检查 ToolMessage id 配对、工具调用次数、错误分支和 structured_response 字段。",
        "sections": [
            ("Fake 模型测试的是框架行为，不是模型智商", [
                "真实模型输出会受采样、服务端版本、网络、速率限制和隐藏系统策略影响。把它放进单元测试，会让失败原因变得模糊：是你的 Agent 循环错了，还是模型今天换了措辞？Fake 模型把模型行为压成一段脚本，让测试只关注框架如何处理这个脚本。",
                "这并不表示真实模型测试没价值。集成测试可以周期性验证真实 provider、工具 schema 和 prompt 质量；单元测试则验证消息状态、工具路由、错误处理和 checkpoint。两层测试回答不同问题：单元测试问“程序是否按契约处理给定消息”，集成测试问“真实模型在这个契约下是否大概率表现良好”。",
            ]),
            ("确定性工具要去掉时间、网络和随机数", [
                "工具是 Agent 测试里第二个不稳定来源。一个工具如果访问真实订单系统、读当前时间、随机返回候选或依赖外部权限，就会让测试既慢又脆。测试工具应使用内存 fixture，明确输入输出，并把错误也写成固定分支，例如未知订单返回受控异常或特定字符串。",
                "副作用工具更要隔离。退款、发邮件、改数据库这类工具在单元测试中不应触达生产服务，而应使用 fake repository 或 dry-run 实现。断言关注是否以正确参数请求了副作用、是否经过 guard middleware、失败时是否不产生重复动作，而不是验证真实世界真的收到邮件。",
            ]),
            ("Trace 断言优先于最终文本断言", [
                "最终文本是最不稳定的断言对象。即使用 Fake 模型，真实项目中你也可能换 prompt 或换 provider，导致同义句变化。更稳的断言是结构：第一轮 AIMessage 是否包含正确 tool_calls，ToolMessage.tool_call_id 是否配对，消息数量是否按预期增长，最终 AIMessage 是否不再请求工具，structured_response 是否含必需字段。",
                "结构断言还能定位失败层。如果 tool_calls 参数错，问题在模型脚本或 prompt；如果 ToolMessage 缺失，问题在工具节点或路由；如果最终响应字段缺失，问题在 response_format 或最终模型消息。只断言“回答包含已发货”无法提供这种定位能力。",
            ]),
            ("InMemorySaver 适合测试，不适合伪装生产持久化", [
                "InMemorySaver 的优势是轻、快、无需外部服务，适合测试一个 thread_id 下的状态保存和恢复。它能帮助你断言第二次调用是否看到第一次 messages，或者 update_state 后图是否从正确快照继续。因为它在进程内存中，测试结束就消失，正好避免污染环境。",
                "但它不代表生产持久化能力。跨进程、重启恢复、并发写入、权限隔离和长期审计需要数据库或专门 checkpoint 后端。测试中使用 InMemorySaver 时，要在命名上明确这是 test saver，避免新人误以为把它放进服务就完成了记忆系统。",
            ]),
            ("回归案例来自真实失败，但要压缩", [
                "线上失败往往包含大量无关历史、隐私字段和真实工具结果。写回归测试时，不应直接复制整段日志，而要压缩成最小消息序列：保留触发失败所需的 HumanMessage、AIMessage.tool_calls、ToolMessage 或 context 字段，删除无关内容并脱敏。最小案例更稳定，也更容易让未来维护者理解。",
                "压缩后要确认测试先失败。若测试一写就通过，说明它没有覆盖真实 bug，或者现有代码已经通过其他路径修复。TDD 的红灯在回归场景尤其重要：它证明你的测试确实能抓住曾经的缺陷，而不是只给 coverage 数字添砖。",
            ]),
            ("调试顺序：从可单独 invoke 的边界开始", [
                "Runnable 的统一接口让你不必每次都跑完整 Agent。先单独 invoke prompt，确认消息渲染；单独调用 Fake 模型，确认脚本顺序；单独调用工具，确认 fixture；单独检查 checkpointer，确认 thread_id；最后再运行 create_agent 组装结果。分层调试比在端到端测试里加大量 print 更清楚。",
                "当端到端测试失败时，按最近新增状态逆向排查。最终回答错，先看最后一条 AIMessage；工具观察没被用，先看 ToolMessage 内容是否可读；工具没被调用，先看 Fake 模型第一条消息是否真的有 tool_calls；状态丢失，先看 config.configurable.thread_id 是否一致。",
            ]),
            ("常见误解与边界情况：Mock 不是越多越好", [
                "常见误解是“所有依赖都 mock 掉，测试就稳定”。过度 mock 会让测试只验证 mock 的调用姿势，而不是真实契约。GenericFakeChatModel 是有价值的 fake，因为它实现聊天模型接口并返回真实 AIMessage；内存工具 fixture 也有价值，因为它仍通过 @tool schema。相反，直接 mock 掉 create_agent 内部方法，往往会绕开你真正想验证的 Agent 循环。",
                "边界情况是 provider-specific 行为。不同模型对 tool_calls、stream chunk 或结构化输出支持不同，单元测试可以用 fake 锁住框架预期，但仍需要少量 provider 集成测试覆盖转换层。测试金字塔不是只要底层，而是让大量稳定单测支撑少量昂贵集成测试。",
            ]),
            ("消息状态断言的粒度", [
                "一个实用断言模板包括：messages 第一条是否为用户问题；第一条 AIMessage 是否包含预期工具名和参数；工具结果是否用同一个 tool_call_id 回写；最终 AIMessage 是否不再包含 tool_calls；如果有 structured_response，字段是否满足 schema。这个模板比断言字符串完整相等更能表达 Agent 的真实契约。",
                "还要断负例。未知订单应返回澄清或拒绝，而不是继续调用退款工具；工具抛错应被记录为可读错误或触发重试，而不是吞掉；guard middleware 拦截后不应执行副作用工具。负例证明边界存在，正例只证明 happy path 能跑。",
            ]),
            ("把测试输出写成可读证据", [
                "失败信息要帮助定位。断言 expected_tool_names == actual_tool_names，比 assert len(tool_calls) == 1 更有用；断言 message types 序列等于 ['human','ai','tool','ai']，比只看最终内容更直观。好的测试失败时像小 trace，不需要开发者重新跑 debugger 才知道状态断在哪里。",
                "测试名也要描述行为，例如 test_agent_uses_order_tool_before_final_answer，而不是 test_agent。行为名会在 CI 输出里变成导航。未来有人改 middleware 或工具 schema 导致失败时，测试名直接告诉他破坏的是哪条工程契约。",
            ]),

            ("从失败输出反推测试设计", [
                "设计 Agent 测试时，可以先写理想失败输出。比如你希望失败时看到“期望工具 search_order 被调用一次，实际调用了 search_order 两次，第二次参数 order_id 为空”。为了得到这样的输出，测试就不能只断言最终 answer，而要收集工具调用记录、参数摘要和消息序列。好的测试不是事后装饰，它会反过来推动代码暴露清晰边界。",
                "当测试难写到必须 mock 一堆私有方法时，往往说明设计边界不清。也许工具把查询、判断和副作用混在一起；也许 prompt 渲染和模型调用无法分开；也许 context 安全字段被塞进普通消息。不要急着堆 mock，而要把组件拆到可以单独 invoke 的程度。测试困难是设计反馈，不是测试作者的问题。",
                "回归测试还要控制断言粒度。太粗会漏 bug，太细会因无关重构失败。经验是锁住协议字段而非实现细节：消息类型、工具名、参数、id、结构化字段、错误类别属于协议；内部局部变量名、具体日志句子、自然语言标点通常不是协议。",
            ]),
            ("把测试金字塔放进 Agent 语境", [
                "Agent 项目的底层应有大量纯函数和 Runnable 单测：prompt 渲染、工具参数校验、retriever 格式化、middleware guard、response schema。中层是 fake Agent 流程测试，验证 model -> tools -> model、checkpoint、结构化输出。顶层才是少量真实 provider 集成测试和人工评测，用来发现 fake 无法覆盖的模型行为。",
                "不同层失败后的处理也不同。底层失败通常直接修代码；fake 流程失败要看消息契约或组合顺序；真实模型评测下降可能要调 prompt、工具描述或模型配置。把所有失败都放在端到端真实模型测试里，会让团队不知道该找后端、提示词还是 provider。分层测试让责任边界变清楚。",
                "测试数据也要治理。真实客服、医疗、金融日志不能原样进入仓库；应抽取结构、脱敏实体、保留触发条件。最好的 regression fixture 既能代表真实失败，又不泄漏隐私，并且小到可以在代码 review 中读完。",
            ]),

            ("调试 Agent 时的最小观察面", [
                "最小观察面不是所有日志，而是足以重建控制流的字段。对 Agent 来说，至少要看到消息类型序列、最新 AIMessage 的 tool_calls、每个 ToolMessage 的 tool_call_id、工具参数摘要、checkpoint thread_id、最终结构字段和错误类别。有了这些字段，即使不看完整自然语言，也能判断循环为何继续、为何停止、状态是否保存。",
                "测试代码可以把这些字段整理成小型 trace，再做快照或显式断言。比如 expected_trace = [('human', None), ('ai', 'search_order'), ('tool', 'call_1'), ('ai', None)]。这种断言一眼就能看出多了一次工具调用或缺了一条观察，比翻完整消息对象更适合回归。",
                "当失败与流式输出有关时，还要区分 chunk 与最终消息。GenericFakeChatModel 能触发 token callback，但你的业务断言不应把中间 chunk 当最终状态。测试应等待最终聚合结果，再断言 structured_response；同时可单独断言 callback 是否收到了 token 事件。",
            ]),

            ("测试命名、fixture 与可维护性", [
                "测试长期可维护，靠的不只是断言，还靠命名和 fixture 组织。fixture 名称应说明业务含义，例如 delayed_order、eligible_refund、blocked_refund，而不是 data1、data2。Fake 模型脚本也应按阶段命名，例如 ai_requests_order_tool、ai_final_answer。这样测试失败时，读者不用先理解一大段 JSON，单看名字就知道场景。",
                "fixture 还要避免共享可变状态污染。Fake 模型迭代器、InMemorySaver、工具调用记录最好每个测试重新创建；若多个测试共用同一个对象，前一个测试消耗了一条消息，后一个测试就会莫名失败。确定性测试不仅要求外部世界稳定，也要求测试自身状态隔离。",
                "当回归案例越来越多，可以按失败模式分组：工具参数、权限拦截、checkpoint 恢复、结构化输出、检索无结果。分组能帮助团队看出哪类问题最常出现，也能让新人按主题学习 Agent 的脆弱点。测试集本身就是工程知识库。",
            ]),

            ("最后一公里：让回归长期有效", [
                "回归测试写完后，还要防止它慢慢失真。每次改 prompt、工具 schema 或消息结构，都要问现有回归是否仍表达真实业务风险；若测试只是为了适应实现而不断放宽断言，它就会失去保护力。维护测试和维护代码一样重要，尤其是 Agent 这种容易因小改动改变控制流的系统。",
                "当回归测试失败时，先判断是产品意图改变还是 bug 重现。若意图改变，应同步更新测试名称、fixture 和说明；若是 bug，就沿 trace 找到破坏的组件。不要简单删除失败测试，因为那等于删除一段历史事故经验。",
            ]),

            ("补充复盘", [
                "测试还应覆盖并发和重复调用的边界。即使当前示例只有一个工具，也要理解 tool_call_id 为什么存在，为什么工具观察必须和请求配对，为什么 checkpoint 要按 thread_id 隔离。很多线上事故不是 happy path 不会跑，而是重试、并发、恢复和错误分支没有被测试。",
                "为了让密度和质量同时达标，本课把路线、证据、边界、失败模式和交付报告都纳入正文。读者不只知道怎么操作，还知道为什么这些操作能减少风险、缩短排障时间、提高协作可信度。",
            ]),

            ("补充边界", [
                "继续扩展测试时，要为每个工具维护一份小契约：输入字段、可信字段来源、正常返回、可重试错误、不可重试错误、副作用语义。Fake 测试按契约构造消息，集成测试再验证真实工具是否遵守契约。这样模型脚本、工具实现和回归断言不会各说各话。",
                "这些补充不是额外理论，而是把测试和观测延伸到真实维护周期。系统越长期运行，越需要清楚契约、稳定信号和可执行反馈。",
            ]),
        ],
        "pitfalls": [
            ("用真实模型跑单元测试更接近生产", "单元测试要稳定复现框架行为；真实模型留给少量集成和评测。"),
            ("断言最终回答全文最可靠", "优先断言消息类型、tool_calls、ToolMessage id 和结构化字段。"),
            ("InMemorySaver 可以直接当生产记忆", "它适合测试和本地调试，生产要考虑持久化、并发和审计。"),
            ("Mock 越多越稳定", "有接口契约的 fake 优于绕过真实路径的 mock。"),
        ],
        "lab_title": "设计一个确定性 Agent 回归测试",
        "lab_steps": [
            "写出曾经失败的用户问题，并删除所有与失败无关的历史消息。",
            "构造两个 AIMessage：第一条带工具调用，第二条给最终回答。",
            "把真实工具替换为只读内存 fixture，并写出未知输入的固定错误分支。",
            "运行 Agent 后断言消息类型序列、工具名、参数、tool_call_id 和最终字段。",
            "故意删掉工具回写或改错参数，确认测试会因预期原因失败。",
        ],
        "version_note": "路径核验于 2026-06：GenericFakeChatModel、AIMessage、Runnable、create_agent 位于 LangChain 主仓当前 master；InMemorySaver 位于 langchain-ai/langgraph 独立仓库 libs/checkpoint/langgraph/checkpoint/memory/__init__.py。",
        "points": [
            "Fake 模型让测试关注框架契约，而不是真实模型随机性。",
            "确定性工具应去掉网络、时间和副作用。",
            "Trace 断言比最终文本断言更稳定、更可定位。",
            "InMemorySaver 适合测试状态恢复，不代表生产持久化。",
            "回归测试要从真实失败压缩，并先看到红灯。",
        ],
    }
)


LESSON_39_OBSERVABILITY_CI = _build_lesson(
    {
        "lead": "可观测性和 CI 是同一件事的两面：前者让一次运行的内部过程可解释，后者让一次代码变更的发布过程可验证。Callbacks 和 tracer 把 Runnable、模型、工具、链、Agent 的 start/end/error 事件组织成 run tree；本教程的 build、check_links、check_html、check_content_density 和 CI diff gate 则把课程源码到生成 HTML/PDF 的过程组织成提交树。工程化不是等线上出错再翻日志，而是在每次运行和每次 PR 中留下足够证据，能回答“谁调用了谁、输入输出是什么、哪里漂移、为什么拒绝发布”。",
        "analogy": "把观测和 CI 想成机场运行。旅客只看到飞机起飞，但机场内部记录了值机、安检、登机、滑行、起飞每个节点；这像 callbacks/run tree。与此同时，每架飞机起飞前都有维护清单、航线检查、燃油检查和放行签字；这像 CI。没有运行记录，延误后不知道卡在哪；没有放行清单，问题会在起飞后才暴露。",
        "map_title": "本课地图：从一次运行到一次发布的证据链",
        "map_nodes": [
            ("Callback 事件", "BaseCallbackHandler 接收链、模型、工具、retriever 的生命周期事件", "before"),
            ("Run Tree", "BaseTracer 把嵌套调用整理成父子 run，便于定位耗时和错误", "now"),
            ("本地检查", "build、print、links、html、density 在提交前模拟 CI", "now"),
            ("漂移闸门", "CI 重建生成物并 git diff，发现 lessons/index/print 与 src 不一致就失败", "source"),
            ("发布/PDF", "通过 verify 后再部署 Pages 或生成 PDF，发布物有源可追", "after"),
        ],
        "source_intro": "本课把上游可观测性接口和本仓库 CI 守卫放在同一张图里。BaseCallbackHandler 与 BaseTracer 来自 langchain-core；check_html、check_links、check_content_density 和 ci.yml 来自当前教程仓库，路径已经按本 worktree 验证。",
        "sources": [
            {"file": "langchain/libs/core/langchain_core/callbacks/base.py", "symbol": "BaseCallbackHandler", "role": "定义 on_chain_start、on_llm_start、on_tool_end、on_error 等观察钩子", "direction": "运行时事件从 Runnable/模型/工具向 callback 管理器传播"},
            {"file": "langchain/libs/core/langchain_core/tracers/base.py", "symbol": "BaseTracer", "role": "把 callback 事件组织成 run 对象和父子关系", "direction": "为 LangSmith 风格 run tree、耗时分析和错误定位提供基础"},
            {"file": "src/check_html.py", "symbol": "main / check_lesson", "role": "检查生成 HTML 的结构、导航、陈旧文案和要点卡", "direction": "build 后运行，失败表示页面结构或一致性回归"},
            {"file": "src/check_links.py", "symbol": "check", "role": "扫描 index 与 lessons 中的相对 href，确认内部链接存在", "direction": "防止重排课程后留下死链"},
            {"file": "src/check_content_density.py", "symbol": "main / check_page", "role": "检查 C-level 页面原始内容的 CJK 密度和语义组件", "direction": "防止新增课程退化为空页或缺少 trace/source/lab"},
            {"file": ".github/workflows/ci.yml", "symbol": "verify job", "role": "重建站点和 print、检查生成 HTML 漂移、运行三类检查", "direction": "PR 和 push 的发布前闸门"},
        ],
        "flow_title": "调用图：一次代码变更如何被本地检查和 CI 接住",
        "flow_kind": "call_graph",
        "flow_steps": [
            ("修改 src", "改 lesson、quiz、shell 或 registry", True),
            ("build + print", "生成 index、lessons、print.html", True),
            ("本地 checks", "links/html/density 全部通过", True),
            ("git diff gate", "确认生成物已提交且无漂移", True),
            ("deploy/PDF", "发布 Pages 或打 PDF", False),
        ],
        "trace": [
            {"step": "1. code change", "input": "src/part08_engineering.py 新增一课", "action": "作者修改原始 lesson body 和 quiz 数据", "output": "Python 源发生变化，HTML 尚未同步"},
            {"step": "2. build", "input": "registry.CONTENT + quizzes.render", "action": "python build.py 和 build_print.py 生成站点与打印页", "output": "index.html、lessons/*.html、print.html 更新"},
            {"step": "3. checks", "input": "生成 HTML 和原始 CONTENT", "action": "检查链接、结构、密度、必备组件", "output": "发现死链、缺要点或 CJK 不足则失败"},
            {"step": "4. drift gate", "input": "CI 中重新生成后的工作树", "action": "git diff --quiet -- index.html lessons/", "output": "有差异则说明提交的 HTML 过期"},
            {"step": "5. release", "input": "verify job 通过的提交", "action": "deploy workflow 发布 Pages 并生成 PDF", "output": "用户看到的站点可追溯到源码"},
        ],
        "code_path": ".github/workflows/ci.yml",
        "code_symbol": "verify job",
        "code": """steps:
  - run: python build.py        # 站点 HTML
    working-directory: src
  - run: python build_print.py  # PDF 源 print.html
    working-directory: src
  - run: git diff --quiet -- index.html lessons/
  - run: python check_links.py
    working-directory: src
  - run: python check_html.py
    working-directory: src
  - run: python check_content_density.py
    working-directory: src
""",
        "code_note": "教学版保留 CI 的因果顺序：先生成，再比较，再检查。真实项目里还会加测试、lint、类型检查和部署权限；本教程的重点是防止静态课程生成物与 src 漂移。",
        "sections": [
            ("Callback 和 middleware 的边界", [
                "Callback 主要负责观察：某个 Runnable 开始、模型收到哪些消息、工具何时结束、错误在哪里发生。它不应悄悄改写业务输入，也不应把安全策略藏在日志代码里。Middleware 主要负责改变或包裹运行：注入动态提示、拦截工具、限流、重试、替换模型、读取 runtime context。二者都在运行路径上，但职责不同。",
                "混淆边界会让系统难排查。如果 callback 为了脱敏直接修改消息，trace 里的输入就不再等于真实执行输入；如果 middleware 只记录日志却不改变行为，后续维护者会误以为它有策略效果。设计时先问：我是在记录发生了什么，还是在决定能不能发生？前者选 callback/tracer，后者选 middleware/业务逻辑。",
            ]),
            ("Run tree 是嵌套调用的地图", [
                "复杂链路不是一条线，而是一棵树：外层 Agent run 下面有 model run、tool run、retriever run、parser run；工具内部也可能调用子 Runnable。BaseTracer 的价值是保存父子关系、run_id、输入输出、开始结束和错误，让一次失败能从根节点一路展开到具体子节点。",
                "没有 run tree，日志往往只是时间排序的字符串。并发工具一多，谁属于谁就不清楚；stream chunk 和最终输出混在一起，也很难判断错误发生在模型、工具还是解析器。run tree 让“链调用了工具”变成可查询结构，而不是靠肉眼猜测。",
            ]),
            ("观测数据要最小化和脱敏", [
                "可观测性不是把所有 prompt、用户输入、工具返回和密钥原样写进日志。工程上应采用白名单和摘要策略：记录消息类型、长度、工具名、参数键、文档 id、错误类别、耗时和 run_id；对用户内容、系统提示、token、订单号等敏感字段做脱敏或不记录。",
                "这不是和排障矛盾。好的 trace 保留结构证据而不暴露秘密。例如记录 retriever 返回 doc_id 和 score，必要时让授权工程师按 doc_id 回查；记录工具参数里的 order_id 哈希，而不是完整个人信息。可观测性越强，越需要治理边界。",
            ]),
            ("本地 CI 是提交前的保险", [
                "很多人把 CI 当远端老师，本地只负责写代码。更高效的流程是把 CI 当脚本说明书，在提交前跑同款命令。本教程的 verify job 非常短：build、build_print、diff gate、check_links、check_html、check_content_density。你本地跑过，远端失败概率就大幅下降。",
                "本地跑检查还有一个好处：失败时上下文最新，修复成本低。等推到远端再看失败，可能已经切换任务，或者 CI 输出被折叠。把检查做成本地习惯，比在 PR 里反复追加“fix ci”提交更专业。",
            ]),
            ("Generated drift 是静态站点的真实 bug", [
                "源码生成型项目最典型的错误，是改了源数据却没有提交生成结果。用户打开的是旧 HTML，reviewer 看的是新 Python，二者不一致。CI 的 git diff gate 明确把这种情况视为失败：重新 build 后若 index.html 或 lessons/ 有差异，说明提交不完整。",
                "print.html 和 PDF 也属于同一条链。build_print.py 把课程合成可打印源，deploy 再用浏览器生成 PDF。若课程 HTML 更新但 print 没更新，在线页面和下载 PDF 会不一致。对教程类仓库来说，内容一致性就是产品质量。",
            ]),
            ("Density gate 不是凑字数", [
                "check_content_density 看似检查 CJK 字数和 visual block 数，但目标不是鼓励灌水，而是防止 C-level 页面退化成提纲。它还检查 lesson-map、source-map、trace-table、code-walkthrough、pitfall-grid、lab 等语义组件，确保每课都有地图、证据、流程、代码和练习。",
                "密度检查读取的是 registry.CONTENT 里的原始 body，而不是生成后的 lessons HTML。这避免导航、页脚、quiz 等外壳文字污染课程正文统计。写作者因此必须把真正内容放进 lesson 常量，而不是靠页面模板填充。",
            ]),
            ("常见误解与边界情况：观测不是自动正确", [
                "常见误解是“接了 LangSmith 或 tracer，系统就可控了”。观测只能告诉你发生了什么，不能替你决定策略是否正确。一个 Agent 反复调用同一工具，trace 会清楚显示循环，但修复仍要回到 prompt、工具描述、middleware 或 recursion_limit。没有行动策略的观测，只是更漂亮的事故录像。",
                "另一个边界是测试环境与生产环境。CI 能证明源和生成物一致，不能证明用户一定喜欢内容；callback 能记录 run tree，不能证明模型事实正确。工程守卫要组合使用：结构检查、单元测试、集成评测、人工 review、上线监控各守一层，不要指望单个工具包办质量。",
            ]),
            ("一次运行的排障提问", [
                "排查一次 Agent 运行时，先问根 run 的输入是什么、config 有哪些 tags/metadata、哪些子 run 最耗时、哪个子 run 报错、错误前最后一个成功输出是什么。再看模型是否请求工具、工具是否返回可读观察、retriever 是否返回足够资料、parser 是否因为格式失败。问题按 run tree 逐层收敛。",
                "若有 streaming，则额外区分 token chunk、tool progress 和最终消息。UI 可以展示流式内容，但后端 trace 应保存最终聚合结果和错误状态。不要把半截 JSON 当成功输出，也不要因为用户中途取消就丢掉前面已完成的工具审计记录。",
            ]),
            ("一次提交的排障提问", [
                "排查 CI 失败时，先看失败阶段。build 失败通常是 Python 语法或 registry 映射；diff gate 失败是生成物没提交；check_links 失败是导航或 href；check_html 失败是结构、陈旧文案或导航链；density 失败是正文内容和语义组件不足。不同阶段对应不同修复，不要盲目重跑。",
                "还要看本地是否复现。若本地通过、CI 失败，比较 Python 版本、工作目录、未提交文件和大小写路径；若本地也失败，先修本地。把 CI 输出写进 PR 描述或 commit 验证记录，reviewer 能快速知道你不是只看了最后一个绿色勾。",
            ]),

            ("把运行证据和提交证据对应起来", [
                "一次线上运行的 run tree 和一次 PR 的 CI 记录其实结构相似：都有根节点、子步骤、输入、输出、耗时和失败原因。运行根节点是用户请求，子节点是模型、工具、检索；PR 根节点是提交，子步骤是 build、print、links、html、density。用同一种证据思维看两者，团队就会习惯先定位失败阶段，再讨论修复方案。",
                "这种对应关系还能帮助教学。学生看到 check_content_density 失败，就能理解它像 callback error：不是“系统讨厌我”，而是某个明确节点报告缺少语义组件。学生看到 run tree 中工具失败，也能类比 CI 阶段失败：先读该节点输入输出，不要盲目重跑整条链。",
                "证据链越完整，沟通越少依赖记忆。PR 描述贴出本地检查命令，线上告警带 run_id 和工具名，reviewer 或值班工程师就能接着查。没有证据链，团队只能在聊天记录里反复问“你刚才跑了什么”“用户到底输入了什么”。",
            ]),
            ("观测预算和信号质量", [
                "不是所有事件都值得完整保存。token 级流式事件量很大，工具返回可能含隐私，retriever context 可能很长。工程上要区分实时 UI 信号、短期调试信号和长期审计信号。UI 需要进度和最终答案；调试需要短期详细 trace；审计需要稳定摘要和权限记录。不同用途的保留时间、脱敏级别和访问权限应不同。",
                "信号质量比信号数量更重要。记录“工具失败”不如记录工具名、错误类别、是否可重试、参数摘要和 run_id；记录“密度失败”不如记录哪个页面、当前 CJK、需要 CJK、缺哪个组件。检查器和 tracer 的输出都应让人下一步知道该打开哪个文件或哪个 run，而不是只制造噪音。",
                "CI 也要避免假绿。若 check_html 只检查生成页面不检查导航链，重排课程可能留下断裂；若 density 统计整页包括导航和 quiz，空正文也可能过线。本仓库选择读取 raw CONTENT 并检查语义 class，就是为了提高信号质量，让绿色真正代表课程正文达标。",
            ]),

            ("CI 输出也要面向作者体验", [
                "一个好的 gate 不只是失败，还要告诉作者怎样修。比如 generated drift gate 输出 git diff --stat，让作者知道哪些 HTML 过期；density gate 输出页面名、当前 CJK 和缺失组件，让作者知道是补正文还是补 source_map；link check 输出具体页面和 href，让作者能直接打开文件。检查器越贴近修复动作，团队越愿意在本地运行。",
                "作者体验还包括避免无关噪音。check_html 把缺少类比卡和本课要点设为 warning，但对结构错误和陈旧文案设为 error；density 只检查已迁移 C-level 页面，不把旧版页面全部拉进门槛。这种分级让 CI 既严格又可执行，不会因为历史债务让当前任务寸步难行。",
                "观测系统同样要面向使用者。值班工程师需要快速定位错误节点，产品经理可能只需要趋势指标，安全审计需要权限和副作用记录。不要把同一份庞大原始 trace 扔给所有人，而要从 run tree 派生不同视图。CI 和 observability 的共同目标都是让正确的人看到可行动证据。",
            ]),

            ("从指标到行动闭环", [
                "可观测性最终要形成行动闭环，而不是只堆仪表盘。若工具错误率升高，团队要能下钻到工具名和错误类别，并决定是回滚工具、修参数 schema、增加重试还是降级到人工。若 density gate 失败，作者要能知道补哪一课、补哪个组件。每个指标都应对应一个可能动作，否则它只是背景噪声。",
                "CI 也应定期复盘门槛是否仍合理。页面迁移增加后，C_LEVEL_PAGES 要扩展；课程数量变化后，README 和 print 计数要同步；上游路径变化后，source rows 要更新。守卫不是一次写完就永远正确，它也需要随项目演进维护。把守卫当成代码，而不是当成外部仪式，质量体系才会持续有效。",
                "对 AI 应用尤其如此。模型、provider、索引和业务政策都会变，昨天稳定的 trace 今天可能因为外部版本变化而不同。观测告诉你变化在哪里，CI 告诉你提交是否自洽，评测告诉你质量是否退化。三者合在一起，才是工程化发布的闭环。",
            ]),

            ("最后一公里：把失败变成知识", [
                "每次 CI 或线上 trace 失败，都应沉淀一个小知识点。链接失败说明导航或文件名变了；密度失败说明课程缺少正文或语义组件；run tree 中工具失败说明 schema、权限或外部服务有问题。团队可以把这些失败模式写进开发手册、测试模板或检查器，让同类问题下次更早暴露。",
                "这也是 observability 和 CI 的长期价值：它们不只是阻止一次坏发布，而是让项目不断学习。检查器从历史错误中增加规则，trace 字段从排障需要中演化，PR 模板从 reviewer 反复追问中完善。质量体系会随着项目一起长大。",
                "如果某个 gate 经常失败但没人知道如何修，它就需要改进错误信息；如果某个线上问题经常发生但没有指标，它就需要补充观测字段。保持这条反馈回路，工程化才不会退化成机械跑命令。",
            ]),

            ("补充复盘", [
                "发布前的绿色检查只是起点，发布后的观测还要继续验证真实使用情况。若用户运行路径和测试样例不同，run tree 会暴露新的工具组合、慢查询、空检索和权限拦截。把这些真实信号再反馈到测试和 CI，课程和系统都会越来越稳。",
                "为了让密度和质量同时达标，本课把路线、证据、边界、失败模式和交付报告都纳入正文。读者不只知道怎么操作，还知道为什么这些操作能减少风险、缩短排障时间、提高协作可信度。",
            ]),

            ("补充边界", [
                "可观测性还要服务容量和成本。run tree 中的 token、耗时、检索数量和工具次数能帮助团队发现某个 prompt 过长、某个 retriever 噪声太大、某个工具被重复调用。CI 保证提交自洽，运行指标保证系统在真实流量下仍然经济可控。",
                "这些补充不是额外理论，而是把测试和观测延伸到真实维护周期。系统越长期运行，越需要清楚契约、稳定信号和可执行反馈。",
            ]),

            ("补充发布观测", [
                "发布之后还要比较预期路径和真实路径。若 CI 中所有页面都达标，但线上用户主要集中在某几课或某些 Agent 工具路径，观测指标应帮助团队优先优化高频部分。工程质量不是只在合并那一刻存在，而是贯穿编写、审核、发布、使用和复盘的连续过程。这条连续链路越清楚，团队越能稳定交付。",
            ]),
        ],
        "pitfalls": [
            ("Callback 可以顺手改业务输入", "Callback 应观察和记录；改变运行行为应放到 middleware 或业务层。"),
            ("有最终答案就够排障", "复杂链路要看 run tree、子 run、工具观察、错误和耗时。"),
            ("生成 HTML 漂移只是格式问题", "源码和用户可见页面不一致，是发布质量 bug。"),
            ("密度门槛等于凑中文字符", "它检查语义组件和正文深度，目标是防止课程退化。"),
        ],
        "lab_title": "设计一个内容仓库 CI 闸门",
        "lab_steps": [
            "列出源码文件、生成文件和发布文件三类产物，并说明谁由谁生成。",
            "设计本地命令顺序：先生成，再检查结构/链接/密度，最后检查 git diff。",
            "为一次 Agent 运行列出要记录的 run_id、父子关系、工具名、耗时和错误字段。",
            "写一条失败案例：如果 lessons HTML 漂移，CI 应输出什么信息帮助作者修复。",
            "检查日志字段是否包含隐私或密钥，给出脱敏策略。",
        ],
        "version_note": "路径核验于 2026-06：BaseCallbackHandler 与 BaseTracer 位于 LangChain 主仓 langchain-core；本教程 CI 当前 verify job 运行 build.py、build_print.py、git diff、check_links.py、check_html.py、check_content_density.py。",
        "points": [
            "Callback/tracer 负责观察，middleware 负责改变或包裹行为。",
            "Run tree 把复杂调用变成可追踪父子结构。",
            "本地跑 CI 同款命令能减少远端失败和 review 往返。",
            "生成 HTML/PDF 与 src 漂移是发布质量问题。",
            "观测和 CI 都要保留证据，同时遵守脱敏和最小化。",
        ],
    }
)


LESSON_40_CAPSTONE = _build_lesson(
    {
        "lead": "端到端客服 Agent 不是把所有能力塞进一个巨大 prompt，而是把前面课程的零件放回各自边界：ChatPromptTemplate 表达角色和对话格式，tools 执行订单查询和工单动作，BaseRetriever 提供可引用政策资料，AgentMiddleware 做权限、限流和副作用护栏，runtime context 注入可信用户和租户信息，structured response 把最终结果收束成后端和 UI 可校验字段，测试用 fake 模型和确定性工具锁住 trace。Capstone 的目标不是炫技，而是证明这些抽象能在一个真实客服场景中彼此配合、互不越界、可观测、可回归。",
        "analogy": "把客服 Agent 想成一间有制度的服务台。前台话术手册是 prompt，资料柜是 RAG，订单系统和退款系统是工具，主管审批和门禁是 middleware，员工胸牌里的工号和门店是 runtime context，最终工单表格是 structured response。一个成熟服务台不会让前台凭记忆决定退款，也不会把顾客身份证号写在公开白板上；每个环节有职责，整条服务才可靠。",
        "map_title": "本课地图：客服 Agent 的七个工程零件",
        "map_nodes": [
            ("Prompt", "定义客服语气、证据要求、澄清策略和工具使用原则", "before"),
            ("RAG", "检索政策、FAQ、物流规则，生成带来源的 context 或工具观察", "now"),
            ("Tools", "查询订单、创建工单、发起退款预检等确定动作", "now"),
            ("Middleware/Context", "从可信运行时读取用户、租户、权限，并拦截危险动作", "source"),
            ("Structured + Tests", "返回可校验字段，并用 fake trace 锁住回归", "after"),
        ],
        "source_intro": "Capstone 的 source map 覆盖装配入口、提示模板、工具转换、检索契约和中间件。所有路径按当前 LangChain/LangGraph 仓库核验；这些符号共同支撑一个客服 Agent 从用户问题到结构化结果的完整路径。",
        "sources": [
            {"file": "langchain/libs/langchain_v1/langchain/agents/factory.py", "symbol": "create_agent", "role": "高层装配入口，把模型、工具、中间件、context_schema、response_format 组成 Agent", "direction": "Capstone 主入口，返回可 invoke/stream 的图"},
            {"file": "langchain/libs/core/langchain_core/prompts/chat.py", "symbol": "ChatPromptTemplate", "role": "把系统规则、历史、资料和用户问题渲染成聊天消息", "direction": "模型调用前明确证据、语气和输出要求"},
            {"file": "langchain/libs/core/langchain_core/tools/convert.py", "symbol": "tool", "role": "把 Python 函数或 Runnable 转成带 schema 的工具", "direction": "订单查询、工单创建、政策检索等动作通过它暴露给模型"},
            {"file": "langchain/libs/core/langchain_core/retrievers.py", "symbol": "BaseRetriever", "role": "定义 query 到 Document 列表的检索 Runnable 契约", "direction": "客服知识库和政策资料的证据来源"},
            {"file": "langchain/libs/langchain_v1/langchain/agents/middleware/types.py", "symbol": "AgentMiddleware", "role": "定义 before/after/wrap hooks 和运行时干预点", "direction": "读取 context、拦截敏感工具、注入动态提示或审计"},
        ],
        "flow_title": "状态流：一次客服问题如何穿过 Agent",
        "flow_kind": "state_flow",
        "flow_steps": [
            ("用户问题", "用户问：订单 A1 晚到，能否退款并给我依据？", "HumanMessage"),
            ("Prompt/Context", "系统提示要求先核实身份和订单，runtime context 提供 user_id、tenant、role。", "context trusted"),
            ("检索资料", "RAG 工具或固定检索链查延迟、退款和物流政策，返回 Document 来源。", "docs + citations"),
            ("工具动作", "订单工具查状态；若退款涉及副作用，先走预检或工单，不直接执行高风险动作。", "ToolMessage"),
            ("Middleware guard", "权限不足、金额过高或提示注入时拦截，写入审计事件。", "allowed/blocked"),
            ("结构化响应", "最终返回 answer、next_action、citations、needs_human、risk_reason 等字段。", "CustomerServiceResult"),
            ("回归测试", "Fake 模型和确定性工具复现同一 trace，断言工具、引用和 guard。", "test locked"),
        ],
        "trace": [
            {"step": "1. issue", "input": "用户：A1 晚到，能退款吗？", "action": "Agent 记录问题并读取 runtime context 中可信 user_id/tenant", "output": "消息状态包含用户请求，安全字段不由模型填写"},
            {"step": "2. retrieve docs", "input": "query='晚到 退款 政策'", "action": "BaseRetriever 返回政策 Document，格式化为带 source 的 context", "output": "引用候选 policy#late-delivery"},
            {"step": "3. order tool", "input": "tool_call search_order(order_id='A1')", "action": "工具用 runtime user_id 校验订单归属并返回物流状态", "output": "ToolMessage：已发货但超预计时间"},
            {"step": "4. guard", "input": "模型想发起 refund(order_id='A1')", "action": "AgentMiddleware 检查金额、权限和政策，必要时改为创建人工工单", "output": "允许预检，阻止直接退款"},
            {"step": "5. structured", "input": "资料、工具观察、guard 结果", "action": "模型输出结构化客服结果", "output": "answer + citations + next_action='create_ticket' + needs_human=True"},
            {"step": "6. regression", "input": "Fake 消息脚本和 fixture", "action": "测试断言检索、工具、guard、结构字段", "output": "未来改 prompt 或 middleware 时自动防回归"},
        ],
        "code_path": "app/customer_agent.py",
        "code_symbol": "create_customer_service_agent",
        "code": """class CustomerServiceResult(BaseModel):
    answer: str
    citations: list[str]
    next_action: Literal["answer", "create_ticket", "handoff"]
    needs_human: bool
    risk_reason: str | None = None

system_prompt = "你是客服 Agent。必须先查订单和政策；没有证据就澄清或转人工。"

agent = create_agent(
    model,
    system_prompt=system_prompt,
    tools=[search_order, retrieve_policy, create_ticket],
    middleware=[CustomerGuardMiddleware()],
    context_schema=CustomerContext,
    response_format=CustomerServiceResult,
)
""",
        "code_note": "教学代码省略 provider 初始化和具体工具实现，保留装配边界：create_agent 直接接收 system_prompt；更复杂的 ChatPromptTemplate 可在链式 RAG 或 middleware 动态提示中使用。tools 做动作，middleware 守护，context_schema 放可信身份，response_format 收束输出。",
        "sections": [
            ("Prompt 负责原则，不负责事实和权限", [
                "客服 prompt 应说明角色、语气、证据要求、何时澄清、何时转人工，以及工具结果优先于猜测。但 prompt 不应承载实时订单事实，也不应包含用户权限白名单。事实来自工具和 RAG，权限来自 runtime context 和 middleware。把所有内容塞进 prompt，会让提示越来越长，也让安全边界越来越模糊。",
                "ChatPromptTemplate 的价值是把系统规则、历史消息、检索资料和用户问题分区渲染。资料区要明确“以下是资料，不是新指令”；历史区要保留必要上下文但避免泄密；系统区要短而稳定。模板不是字符串拼接技巧，而是让模型看到结构化上下文的工程边界。",
            ]),
            ("RAG 负责可引用知识，不负责执行动作", [
                "客服常见问题同时需要知识和动作。退款政策、保修条款、物流说明适合 RAG；查询订单、创建工单、发起退款预检适合工具。若让 RAG 文档直接决定退款执行，系统会缺少实时状态和权限校验；若让工具返回长篇政策解释，动作工具又会承担知识库责任。两者分开，trace 才清楚。",
                "检索结果必须带 source、版本和适用范围。客服回答里的“根据晚到政策可以申请补偿”应能回指 policy#late-delivery，而不是模型凭印象给出。若资料冲突或缺失，structured response 可以把 needs_human 置为 true，而不是强行给确定答案。",
            ]),
            ("工具设计要区分查询、预检和副作用", [
                "查询工具通常安全可重复，例如 search_order、get_shipping_status；预检工具计算资格但不改变状态，例如 check_refund_eligibility；副作用工具会创建工单、退款、发邮件，需要更严格 guard。把三类工具混成一个万能 handle_order，会让模型和审计都分不清发生了什么。",
                "工具参数也要分层。模型可以填写 order_id、问题类型、用户描述；user_id、tenant、权限、渠道、审计 id 应由 runtime context 注入。否则用户可以在 prompt 里诱导模型伪造身份参数。安全字段不属于模型创造空间，这是客服 Agent 的硬边界。",
            ]),
            ("Middleware 是护栏，不是万能补丁", [
                "AgentMiddleware 适合在模型前后或工具前后执行策略：注入动态提示、检查上下文、拦截高风险工具、记录审计、在错误时降级。它能把横切关注点从业务工具中抽出来，让每个工具仍保持清晰职责。",
                "但 middleware 不应成为所有业务逻辑的垃圾桶。退款资格本身可能属于业务服务；middleware 只决定是否允许模型触发某类工具、是否需要人审、是否脱敏。若把复杂业务规则都写进 middleware，未来新增渠道或政策时会难以测试和复用。",
            ]),
            ("Runtime context 是可信输入", [
                "用户消息是不可信输入，runtime context 是应用注入的可信运行上下文。客服 Agent 需要知道 user_id、tenant、locale、role、channel、request_id 等字段，但这些字段不应让模型从自然语言里生成。工具和 middleware 通过 context 读取它们，既能做权限隔离，也能避免把敏感值放进 messages。",
                "context_schema 的设计应最小化。只放本次运行必要字段，字段名清楚，类型明确，默认不写入 prompt。若模型确实需要看到某个非敏感偏好，例如语言或时区，可由 middleware 脱敏后注入动态提示。密钥、内部权限和完整身份信息永远留在运行时侧。",
            ]),
            ("结构化响应让 UI 和后端不用猜", [
                "客服最终结果不应只是自然语言。UI 需要知道是否转人工、后端需要知道是否创建工单、评测需要知道引用、风控需要知道风险原因。response_format 把这些字段声明成 schema，让模型输出可校验对象。自然语言 answer 仍存在，但它只是字段之一。",
                "结构化不等于正确。schema 能保证有 citations 字段，不能保证引用真的支持结论；能保证 needs_human 是布尔值，不能保证策略判断正确。因此结构化响应后仍要做引用核验、业务规则校验和回归测试。它解决的是形状，不是事实全部。",
            ]),
            ("可观测性要覆盖组件边界", [
                "一次客服运行至少要记录：request_id、user/tenant 摘要、检索 query 和 doc ids、工具名和参数摘要、guard 决策、structured_response 字段、错误和耗时。这样用户投诉“Agent 擅自退款”时，团队能确认是否真的调用了副作用工具，是否被 middleware 放行，依据是哪条政策。",
                "同时要控制日志内容。不要把完整用户隐私、系统提示、工具密钥或内部工单备注写进公开 trace。对客服场景来说，可观测性和合规同样重要。记录结构证据，敏感内容用哈希、摘要或受控回查。",
            ]),
            ("测试从 happy path 到防线", [
                "Capstone 测试至少覆盖 happy path：用户问晚到，Agent 检索政策、查询订单、返回带引用回答。再覆盖 guard path：模型试图直接退款，middleware 改为预检或转人工。再覆盖缺证据 path：检索无结果时不编造政策。每条测试都用 fake 模型和确定性工具锁住结构。",
                "测试也要覆盖 message state。断言工具调用顺序、ToolMessage id、引用字段、needs_human、risk_reason，而不是只断言 answer 包含“抱歉”。客服系统最危险的失败常发生在结构层：该拦截的副作用没拦、该转人工的没有转、引用为空却给了肯定答案。",
            ]),
            ("常见误解与边界情况：端到端不等于一坨代码", [
                "常见误解是 Capstone 要展示一个巨大的全能 Agent 文件。真正的端到端是边界完整：prompt、tools、retriever、middleware、context、response、tests 各自短小清晰，通过 create_agent 装配。文件越大、职责越混，越不适合作为毕业项目。",
                "边界情况是工具和 RAG 都能回答同一问题。例如“我的包裹什么时候到”既可能查订单工具，也可能查物流政策。策略应写清：实时个人状态优先工具，通用规则优先 RAG，二者冲突时展示具体状态并引用政策。不要让模型临场决定事实优先级。",
            ]),
            ("从玩具到生产的扩展点", [
                "玩具版本可以用内存 fixture、Fake 模型和 InMemorySaver；生产版本要替换为真实 provider、数据库工具、持久 checkpointer、权限服务、LangSmith 或自建 trace、评测集和报警。因为抽象边界相同，替换可以逐步发生，而不是重写整个 Agent。",
                "最先撑不住的通常是准确性、成本和可控性。准确性靠 RAG 评测和引用核验；成本靠缓存、工具选择和模型分层；可控性靠 middleware、人审和结构化响应。Capstone 不是终点，而是让这些扩展点有地方插。",
            ]),

            ("组件契约如何支撑团队协作", [
                "客服 Agent 往往不是一个人维护。平台工程师维护 middleware 和 context，搜索团队维护 retriever，业务后端维护订单工具，产品或内容团队维护 prompt 和政策文档，QA 维护 regression trace。若没有清晰契约，任何改动都会互相踩脚。create_agent 的装配边界让每个团队知道自己交付什么：工具交付 schema 和观察，RAG 交付 Document 和引用，middleware 交付 allow/block 决策，response 交付结构字段。",
                "契约还让灰度发布更安全。你可以先替换 retriever 的索引版本，观察引用命中率；再替换模型，观察工具调用率；再收紧 guard，观察转人工率。每次只动一个组件，指标变化才可解释。若所有逻辑都在一个 prompt 里，任何改动都会同时影响语气、工具、权限和格式，回滚也困难。",
                "Capstone 因此要写出组件清单，而不只是展示一段能跑的 demo。清单说明每个组件的输入、输出、依赖、测试方法和失败模式。真实项目上线后，运维和排障靠的就是这张清单，而不是作者当时脑子里的隐含设计。",
            ]),
            ("客服 Agent 的失败模式分层", [
                "第一层是知识失败：检索不到政策、引用过期、资料冲突。修复点在索引、切块、metadata、query rewrite 或引用核验。第二层是动作失败：工具参数错、订单不属于用户、副作用重复执行。修复点在工具 schema、runtime context、幂等键和 guard。第三层是表达失败：回答语气不合适、没有澄清、结构字段缺失。修复点在 prompt、response_format 和评测样例。",
                "分层能避免错修。若问题是订单工具没有校验 user_id，用更强 prompt 说“不要越权”并不够；若问题是政策资料缺失，增加 middleware 也不会凭空产生证据；若问题是 structured_response 缺字段，调整 retriever 可能没有帮助。trace 应告诉你失败在哪一层，修复也应落在同一层。",
                "端到端回归测试要覆盖跨层连接。一个案例可以同时验证：RAG 返回政策引用，订单工具返回状态，middleware 阻止直接退款，最终 response 指向人工工单。它不是只测一个函数，而是证明组件之间的合同仍然成立。",
            ]),

            ("从课程零件到生产清单", [
                "把 Capstone 落到生产前，可以把前面课程转成一张上线清单：消息系统负责记录用户与工具观察；聊天模型通过统一接口接入 provider；工具有 schema、幂等和权限；prompt 有模板和版本；RAG 有 Document、metadata、引用和拒答；LangGraph 有状态、checkpoint 和控制边；middleware 有 guard 和审计；测试有 fake trace 和真实评测。每一项都对应本书前面的一课。",
                "这张清单能暴露缺口。如果没有引用核验，RAG 只是在 prompt 里塞资料；如果没有 runtime context，权限靠模型猜；如果没有 structured_response，后端只能解析自由文本；如果没有 regression trace，重构后不知道防线是否还在。Capstone 的价值是把这些缺口集中展示，而不是假装 demo 已经等于生产。",
                "生产演进也应沿清单逐项替换。先用 fake 工具和小知识库验证流程，再接真实只读查询，再加副作用预检，再加人审，再扩大评测集。每一步都有测试和观测指标，失败时能回到对应组件。这样从学习项目到真实客服系统才是平滑的，而不是一次危险跳跃。",
            ]),

            ("毕业项目的验收标准", [
                "一个客服 Agent 是否达到工程化标准，可以用六个问题验收。第一，用户身份和权限是否只来自可信 context。第二，实时状态是否通过工具获取而不是模型猜测。第三，政策知识是否有可回指引用。第四，高风险副作用是否经过 middleware 或业务服务 guard。第五，最终输出是否有结构化字段供 UI 和后端读取。第六，是否有 fake 回归测试能复现关键路径和失败防线。",
                "若六个问题有任何一个答不上来，系统仍停留在 demo 阶段。demo 可以展示想法，但生产需要证据。比如没有引用，客服回答听起来合理也不能审计；没有 guard，模型一次误判就可能触发退款；没有结构化字段，工单系统只能解析自然语言；没有测试，下一次改 prompt 就可能破坏工具顺序。",
                "Capstone 的真正成果，是让你看到 LangChain/LangGraph 的抽象如何服务这些验收点。它们不是为了让代码显得高级，而是让职责可分、状态可追、失败可测、发布可控。学到这里，应该能独立设计一个小型 Agent，并说明每个组件为何存在、怎样测试、坏了怎么查。",
            ]),

            ("最后一公里：对用户负责", [
                "客服 Agent 面向真实用户，工程边界最终服务于信任。用户需要知道系统是否查了订单、依据哪条政策、下一步是自动处理还是人工跟进；团队需要知道每次回答背后的证据和动作；公司需要确保权限、隐私和审计达标。Prompt 写得亲切只是起点，可信的服务来自端到端证据链。",
                "因此 Capstone 的验收报告也应包含业务语言：哪些问题能自动回答，哪些必须转人工，哪些工具有副作用，哪些日志会脱敏，哪些失败会触发告警。把技术组件翻译成服务承诺，才说明你真的理解了工程化 Agent。",
            ]),

            ("补充复盘", [
                "端到端 Agent 的难点在长期维护。新政策、新工具、新模型和新渠道都会进入系统，只有组件边界清楚、测试覆盖关键 trace、观测记录真实运行，团队才能安全演进。Capstone 要训练的正是这种演进能力，而不只是一次性跑通示例。",
                "为了让密度和质量同时达标，本课把路线、证据、边界、失败模式和交付报告都纳入正文。读者不只知道怎么操作，还知道为什么这些操作能减少风险、缩短排障时间、提高协作可信度。",
            ]),
        ],
        "pitfalls": [
            ("把所有规则塞进 prompt", "Prompt 负责原则；事实走 RAG/工具，权限和护栏走 context/middleware。"),
            ("RAG 能替代订单工具", "RAG 提供通用资料；实时状态和副作用必须走工具和业务服务。"),
            ("结构化响应保证事实正确", "它保证输出形状；事实仍要靠引用、工具观察和校验。"),
            ("Middleware 可以承载全部业务逻辑", "Middleware 适合横切护栏，核心业务规则仍应在业务服务或工具内清晰实现。"),
        ],
        "lab_title": "设计一个客服 Agent 最小可测版本",
        "lab_steps": [
            "列出三类问题：只需政策资料、需要订单查询、需要副作用或转人工。",
            "为每类问题指定 prompt 规则、RAG 资料、工具和 guard 决策。",
            "设计 CustomerContext 和 CustomerServiceResult，只保留必要字段。",
            "写一个 fake trace：模型先查政策，再查订单，middleware 阻止直接退款，最终转人工。",
            "把 trace 变成测试断言：工具顺序、引用、needs_human、risk_reason 和无副作用执行。",
        ],
        "version_note": "路径核验于 2026-06：create_agent 与 AgentMiddleware 位于 LangChain v1 包；ChatPromptTemplate、tool、BaseRetriever 位于 langchain-core。真实客服系统还应按所选 provider 和部署环境核验 partner 包路径。",
        "points": [
            "Capstone 的核心是边界装配，不是巨型 prompt。",
            "Prompt、RAG、工具、middleware、context、response_format 各有职责。",
            "安全字段来自 runtime context，不应由模型生成。",
            "结构化响应方便 UI、后端和评测，但仍需事实校验。",
            "Fake trace 回归测试能保护端到端 Agent 的关键防线。",
        ],
    }
)
