"""Temporary skeletons for Part 9: ecosystem and reference pages."""

import shell


def _temp_lesson(title, focus):
    return (
        f'<p class="lead">本课《{title}》将在 M9 Task 2 填充完整内容；'
        f"当前先注册页面入口、导航、索引与质量门，确保第九部分的最终课程序列稳定。</p>"
        '<div class="card analogy"><div class="tag">🧩 临时占位</div>'
        f"把这页先看成书架上的空标签：标签已经贴好，后续会把 {focus} 的图解、源码入口、"
        "边界情况和练习逐步放进来。</div>"
        + shell.lesson_map(
            "M9 占位地图",
            [
                ("已注册", "页面、标题、分区和导航已经进入全站顺序", "before"),
                ("待填充", "正文、图示、源码走读和术语索引会在下一任务完成", "now"),
                ("待验收", "密度门当前应只对这六个临时页面失败", "after"),
            ],
        )
        + "<h2>本课要点</h2>"
        '<div class="card keypoints"><div class="tag">✅ 本课要点</div>'
        "<ul><li>这是第九部分的临时骨架，不包含正式教学内容。</li>"
        "<li>本页故意低于 C-level 密度门，便于 Task 2 用失败清单驱动补全。</li></ul></div>"
        + shell.version_note("M9 Task 1 只注册最终页面集合；请勿在本文件写完整正文。")
    )


LESSON_41_CHAT_INTERNALS = _temp_lesson(
    "ChatModel Provider 内部",
    "ChatModel provider 适配、调用链和响应元数据",
)

LESSON_42_TOOL_INTERNALS = _temp_lesson(
    "Tool Schema 与执行内部",
    "工具 schema 生成、执行封装和 ToolMessage 回填",
)

LESSON_43_ECOSYSTEM_COMPARE = _temp_lesson(
    "LangChain、LangGraph 与多 Agent 生态",
    "LangChain、LangGraph 与多 Agent 框架选型对照",
)

LESSON_44_AI_STACK_PROTOCOLS = _temp_lesson(
    "AI 全栈、MCP 与 A2A",
    "AI 应用栈分层、MCP 工具协议和 A2A 协作协议",
)

LESSON_45_LEARNING_MAP = _temp_lesson(
    "后续学习地图",
    "后续源码阅读、实践项目和生态补课路线",
)

LESSON_46_GLOSSARY = _temp_lesson(
    "术语表与源码索引",
    "全书术语、源码符号和课程跳转索引",
)
