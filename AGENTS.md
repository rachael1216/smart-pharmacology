# AGENTS.md

本仓库是复旦（上医）药理学的历年真题库与学伴系统：真题 → 答案与解析 → 知识卡 → 教材出处（本地 RAG）→ 多格式导出。AI 助手在其中担任**整理者与学伴**，不是出题人或阅卷人。

## 入口
- 新会话先展示菜单：MCP 工具 `pharm_menu`，或读 `.agents/skills/pharm-menu/menu.md`。
- Skill：`pharm-tutor`（答疑）`pharm-annotate`（解析标注）`pharm-entry`（录入）`pharm-review`（审核）`pharm-export`（导出）。

## 工作规则
- **先检索再写**：写或改答案、解析前，先 `python tools/rag.py search <关键词> --authoritative`（或 `annotate.py suggest <题号>`）取教材原文与页码。
- **出处只来自教材、讲义、本地资料**。知识卡、鉴别卡、真题是整理物，不能当出处。没有依据时不加 evidence，并在 `note` 写“教材依据待查”。
- **状态如实**：AI 写的内容为 `draft-ai`；出处一律先写 `待核`。只有人审过才能改 `reviewed`、`已核`。
- **原文不动**：`bank/raw/` 是考后回忆原文，不修改；修订只改 `bank/exams/*.yaml`。题目 `id` 发布后不改。
- **一处写一次**：反复出现的概念答案写在知识卡，题目用 `answer_ref` 引用；本题特有内容写 `answer`。
- 引文 ≤ 80 字只作定位，答案用自己的话写；不把教材原文、讲义提交进仓库。
- 仓库里不写学生姓名与学号；`reviewer` 用 GitHub 用户名。
- 每次修改后：`python tools/bank.py check`（零错误）→ `python tools/bank.py docs`（更新可读版）。

## 开发
- 测试：`python -m unittest discover tests`
- 改动工具后同步更新对应 skill、`tools/mcp_server.py` 工具说明与 README。
