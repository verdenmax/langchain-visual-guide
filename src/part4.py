"""Content for Part 4 (advanced): lesson 14."""

LESSON_14 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
你已经理解了 LangChain 的<strong>用法</strong>和<strong>内部机制</strong>。最后一课给你一套<strong>实战工具箱</strong>：
如何高效读源码、跑测试、调试，以及把改动贡献回去。这会把"理解"变成"能动手"。
</p>

<div class="card analogy">
  <div class="tag">🧭 生活类比</div>
  前面是看地图，这一课是<strong>发驾照</strong>：认识仪表盘（工具链）、学会安全检查（测试）、
  懂得看故障灯（调试），最后按交规上路（贡献规范）。
</div>

<h2>① 工具链：四件套 + make</h2>
<p>第 2 课见过它们，现在配上真实命令。这个仓库用 <span class="inline">uv</span> 管理依赖、<span class="inline">make</span> 封装常用命令：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">libs/core/ （在某个包目录下执行）</span><span class="ln">常用命令</span></div>
<pre><span class="cm"># 安装所有依赖组（首次准备环境）</span>
uv sync --all-groups

<span class="cm"># 跑单元测试（已配置 --disable-socket：禁网络）</span>
make test

<span class="cm"># 代码检查 / 自动格式化</span>
make lint
make format

<span class="cm"># 只跑某个测试文件</span>
uv run --group test pytest tests/unit_tests/test_xxx.py
</pre>
</div>

<table class="t">
  <tr><th>工具</th><th>做什么</th><th>命令入口</th></tr>
  <tr><td class="mono">uv</td><td>装依赖 / 虚拟环境</td><td class="mono">uv sync / uv run</td></tr>
  <tr><td class="mono">pytest</td><td>跑测试</td><td class="mono">make test</td></tr>
  <tr><td class="mono">ruff</td><td>检查 + 格式化</td><td class="mono">make lint / make format</td></tr>
  <tr><td class="mono">mypy</td><td>静态类型检查</td><td class="mono">make lint（含）</td></tr>
</table>

<h2>② 测试结构：镜像源码，单测禁网</h2>
<p>每个包都有自己的 <span class="inline">tests/</span>，结构<strong>镜像源码目录</strong>。两类测试泾渭分明：</p>

<div class="cols">
  <div class="col">
    <h4>🟢 unit_tests（单元测试）</h4>
    <p><strong>不许联网</strong>（<span class="mono">--disable-socket</span>）。用<strong>假模型</strong>替代真实 API，快且稳定。</p>
    <p class="mono">tests/unit_tests/</p>
  </div>
  <div class="col">
    <h4>🔵 integration_tests（集成测试）</h4>
    <p>允许真实网络调用（需 API key），验证与厂商的真实对接。</p>
    <p class="mono">tests/integration_tests/</p>
  </div>
</div>

<div class="card detail">
  <div class="tag">🔬 细节：用"假模型"写单元测试</div>
  既然单测不能联网，怎么测和模型相关的逻辑？用 <span class="mono">core</span> 自带的<strong>假聊天模型</strong>：
  <pre class="code" style="margin:.5rem 0"><span class="kw">from</span> langchain_core.language_models.fake_chat_models <span class="kw">import</span> (
    GenericFakeChatModel,   <span class="cm"># 按预设脚本"假装"回复</span>
    FakeListChatModel,      <span class="cm"># 轮流返回一组固定回复</span>
)
model = GenericFakeChatModel(messages=iter([<span class="st">"你好！"</span>]))
assert model.invoke(<span class="st">"hi"</span>).content == <span class="st">"你好！"</span></pre>
  位置：<span class="mono">core/language_models/fake_chat_models.py</span>。这让你能离线测试链、Agent、解析器等。
</div>

<h2>③ 读源码的正确姿势</h2>
<p>面对几十万行代码别慌。永远<strong>从公开入口往里读</strong>，而不是从底层乱翻：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>从 __init__.py 看导出</h4>
    <p>想知道一个包对外提供啥，先看它的 <span class="mono">__init__.py</span> 的 <span class="mono">__all__</span>。
      比如 <span class="mono">agents/__init__.py</span> 只导出 <span class="mono">create_agent</span> 和 <span class="mono">AgentState</span>。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>顺着 import 往下钻</h4>
    <p>公开函数通常在主力/集成层，真正的抽象在 <span class="mono">core</span>。顺着 import 链走，最终都会到 <span class="mono">langchain_core</span>。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>遇到方法名按名搜索</h4>
    <p>行号会变，但方法名稳定。<span class="mono">grep "def _generate"</span> 比记行号可靠。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>用测试当"活文档"</h4>
    <p>看不懂某个 API？去 <span class="mono">tests/unit_tests/</span> 找它的测试，那里有最小可运行用法。</p></div></div>
</div>

<h2>④ 调试技巧</h2>
<div class="card detail">
  <div class="tag">🔬 细节</div>
  <ul>
    <li><strong>看真实请求</strong>：给 <span class="mono">invoke</span> 传一个打印型回调（<span class="mono">config={"callbacks":[...]}</span>，见第 14 课），
      就能观察生命周期事件。或接入 <strong>LangSmith</strong> 做可视化追踪。</li>
    <li><strong>隔离问题</strong>：用假模型替换真模型，确认 bug 是出在你的链逻辑还是厂商对接。</li>
    <li><strong>最小复现</strong>：把问题缩到 3–5 行能跑的代码，再逐层加回。</li>
  </ul>
</div>

<h2>⑤ 贡献规范：提交前必看</h2>
<div class="card warn">
  <div class="tag">⚠️ 提交规范（Conventional Commits）</div>
  <ul>
    <li>PR / commit 标题格式：<span class="mono">type(scope): 描述</span>，<strong>必须带 scope</strong>。
      例：<span class="mono">fix(core): resolve type hinting issue</span>、<span class="mono">feat(openai): add ...</span>。</li>
    <li>描述以小写开头（除非是专有名词/类名）；类/函数/参数名用反引号包裹。</li>
    <li>新功能/修 bug <strong>必须配单元测试</strong>；公共 API 签名<strong>尽量不破坏</strong>，新参数用关键字形式 <span class="mono">*, new_param=...</span>。</li>
    <li>所有 Python 代码<strong>必须有类型注解和返回类型</strong>；文档用 Google 风格 docstring。</li>
  </ul>
</div>

<h2>🔍 深入理解</h2>
<p class="acc-intro" style="color:var(--muted);font-size:.92rem">展开下面的卡片，深入三个实战问题。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么单元测试要禁网（--disable-socket） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 现象</div>
      <div class="a"><span class="mono">make test</span> 跑单测时带了 <span class="mono">--disable-socket</span>，
        任何真实网络请求都会直接失败。所以单测里<strong>不能</strong>真的调 OpenAI。</div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么这么做</div>
      <div class="a">真实 API 调用<strong>慢、要钱、不稳定、结果不确定</strong>，还依赖密钥。
        把网络禁掉能强制单测做到<strong>快速、确定、可离线、免费</strong>——这是优秀单测的基本要求。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 那怎么测模型逻辑</div>
      <div class="a">用<strong>假模型</strong>（<span class="mono">GenericFakeChatModel</span> 等，见本课"假模型"小节）替代真实 API；
        真正验证厂商对接放到 <span class="mono">integration_tests/</span>（需密钥、显式运行）。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 想加一个新厂商集成，从哪下手 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 步骤概览</div>
      <div class="a">
<pre class="code"><span class="cm"># 1) 在 libs/partners/ 新建一个独立包</span>
<span class="cm"># 2) 实现 BaseChatModel 的 _generate（翻译你的厂商 API）</span>
<span class="cm"># 3) 复用 standard-tests 的标准测试套件验证一致性</span>
<span class="kw">from</span> langchain_tests.integration_tests <span class="kw">import</span> ChatModelIntegrationTests</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么有 standard-tests</div>
      <div class="a"><span class="mono">libs/standard-tests/</span> 提供一套<strong>所有厂商共用</strong>的测试，确保每个新集成
        都满足相同的行为契约（如正确返回 AIMessage、支持工具调用）。继承它即可获得一大批现成用例。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 优点</div>
      <div class="a">新集成"填空式"开发：实现接口 + 跑标准测试，质量有保障，且<strong>完全不用改 core</strong>。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">3</span> 提交规范为什么这么严（scope、类型注解、不破坏 API） <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 一个合格提交长什么样</div>
      <div class="a">
<pre class="code">fix(openai): handle empty tool_calls in streaming

- 描述以小写开头，用反引号包裹 `tool_calls`
- 配套单元测试，不破坏公共 API 签名</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">❓ 为什么必要</div>
      <div class="a"><strong>scope</strong> 让人一眼看出改了哪个包（自动生成 changelog）；
        <strong>类型注解</strong>让 mypy 能静态查错、IDE 能补全；
        <strong>不破坏公共 API</strong> 保护成千上万依赖 LangChain 的下游项目不会因升级而崩。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 经验法则</div>
      <div class="a">新增可选参数用关键字形式（<span class="mono">*, new=None</span>）保持向后兼容；
        改动配测试；提交信息让人不看 diff 也能懂"改了什么、为什么"。</div>
    </div>
  </div>
</details>

<h2>全景回顾：你已经走完的地图</h2>
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">第 1 部分</span><span class="name">宏观全景</span></div>
    <div class="ld">是什么 · monorepo 三层 · 一次调用的生命周期</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">第 2 部分</span><span class="name">用户视角</span></div>
    <div class="ld">消息 · 聊天模型 · 工具 · Agent —— 学会"用"</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">第 3 部分</span><span class="name">内部源码</span></div>
    <div class="ld">Runnable · 组合 · 模型调用链 · 工具机制 · Agent 状态图 · 流式与回调</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">第 4 部分</span><span class="name">进阶实战</span></div>
    <div class="ld">读源码 · 测试 · 调试 · 贡献 —— 把理解变成动手</div></div>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>单测禁网 + 假模型</strong>：换来快、确定、可离线、免费的测试——这是优秀测试的底线。</li>
    <li><strong>standard-tests 填空式</strong>加厂商：实现接口 + 跑标准套件，质量自动有保障，且完全不碰 core。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>环境：<span class="mono">uv sync --all-groups</span>；日常：<span class="mono">make test / lint / format</span>。</li>
    <li>单测禁网、用<strong>假模型</strong>；测试目录镜像源码，是最好的"活文档"。</li>
    <li>读源码从 <span class="mono">__init__.py</span> 入口往 <span class="mono">core</span> 钻，按方法名搜索。</li>
    <li>贡献守 Conventional Commits + 类型注解 + 配套测试 + 不破坏公共 API。</li>
    <li>前四部分（宏观→用户→源码→进阶）到此完结。<strong>第五部分</strong>带你把这些零件拼成<strong>你自己的 Agent</strong>。</li>
  </ul>
</div>
"""
