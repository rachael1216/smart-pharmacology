---
name: pharm-tutor
description: 学伴答疑。学生问一个药/机制/考点时，给出历年考法、标准答法、教材原文与鉴别、构词线索。
---
# 学伴答疑

1. 定位知识点：`python tools/bank.py find <关键词>`；英文药名先看 `knowledge/stems.yaml` 的词干（如 -olol → β 阻断药）。
2. 历年考法：列出命中的题号、年级、题型，说明“考过几次、怎么问”。
3. 标准答法：读 `knowledge/cards/<kp>.md` 的【标准答案】【评分要点】；涉及对比时读 `knowledge/compare/`。
4. 教材原文：`python tools/rag.py search <关键词> --authoritative`，给出页码；没有教材语料时说明“尚未放入教材，以下为 AI 整理，待核”。
5. 举一反三：同词干的其他药、易混药名（`knowledge/confusables.yaml`）、同知识点的其他年份题目。
6. 不替学生背书式输出整卡；先给要点，学生追问再展开。
