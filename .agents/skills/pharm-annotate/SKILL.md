---
name: pharm-annotate
description: 解析标注。为一道题（或一批题）写答案、解析，并挂上可回到页码的教材出处。
---
# 解析标注

## 单题流程
1. `python tools/bank.py show <题号>`：读题干、现有答案、引用的知识卡、已有出处。
2. **先检索再写**：`python tools/annotate.py suggest <题号>`（只查教材、讲义、本地资料）；
   需要更多上下文时 `python tools/rag.py search <关键词> --authoritative --full`。
3. 决定答案放在哪里：
   - 多年反复出现的概念或机制（名解、经典大题）→ 写进或修订 `knowledge/cards/<kp>.md` 的对应小节，题目里用 `answer_ref` 引用；
   - 本题特有的内容（选择题选项、填空、病例里的具体判断）→ 写在题目的 `answer`。
4. 写 `analysis`（解析）：考点 → 答题框架（得分点顺序）→ 易错点。不复述答案。
5. 挂出处：`python tools/annotate.py add <题号> --pick <序号>`，或 `--src/--loc/--quote` 手填。出处 `status` 一律先写“待核”。
6. `python tools/bank.py check`，零错误再提交。

## 批量
`python tools/annotate.py auto --exam <考试id> -k 1 --min-score 8` 只写入候选（待核），必须逐条人工核对后 `annotate.py verify <题号>`。

## 硬规则
- 依据只来自教材、讲义、本地资料；知识卡与真题是 AI/同学整理，**不能当出处**。
- 找不到依据：答案可以先写，但不加 evidence，并在 `note` 写“教材依据待查”。
- 引文 `quote` ≤ 80 字，只作定位；答案与解析用自己的话写。
- 不改 `bank/raw/`（原始回忆）；修订只改 `bank/exams/*.yaml`。
- AI 写的内容保持 `status: draft-ai`；只有人审过才能改 `reviewed`。
