---
name: pharm-entry
description: 录入新考试。把一篇考后回忆整理成 bank/raw/<id>.md（原文）与 bank/exams/<id>.yaml（结构化）。
---
# 录入新考试

1. 定 id：`<年级两位>-<专业代码>-<类型>`，专业代码 lin5 / lin8 / pharm / nurs / dent / prev，类型 midterm / final / makeup / lab；同年同类有两份时加后缀（如 `-c`）。
2. 原文：新建 `bank/raw/<id>.md`，front matter 写 title、url、published、account、license，正文**逐字**粘贴回忆（只删投稿说明等样板）。
3. 结构化：复制 `bank/TEMPLATE.yaml` 为 `bank/exams/<id>.yaml`，填 `exam` 段（含 `format` 分值表与 `notes`），逐题录入：
   - `stem` 只写题干；回忆者括号里的选项/答案线索放 `recall`，能还原成选项的放 `options`；
   - `completeness` 如实填写（full / stem_with_hint / stem_only / topic_only / image_only / lost）；
   - `kp` 先查 `python tools/bank.py find <关键词>` 看往年同类题用的知识卡；
   - 没写答案的题 `status: todo`。
4. `python tools/bank.py fmt && python tools/bank.py check && python tools/bank.py docs`。
5. 再走 `pharm-annotate` 补答案与出处。
