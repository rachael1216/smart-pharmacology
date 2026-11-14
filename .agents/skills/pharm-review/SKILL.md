---
name: pharm-review
description: 审核。把 AI 草稿逐条核对到 reviewed / verified，并记录审核人。
---
# 审核

状态：`todo` 待写 → `draft-ai` AI 草稿 → `draft` 人工草稿 → `reviewed` 同伴审过 → `verified` 对照教材页码或老师确认。

## 题目
1. `python tools/bank.py show <题号>`，对照教材核对答案、解析与出处。
2. 出处逐条打开页码核对，无误后 `python tools/annotate.py verify <题号>`。
3. 题目 `status` 改为 `reviewed`（有已核出处且老师/教材确认可改 `verified`），`reviewer` 填审核人（GitHub 用户名即可，不写学号）。

## 知识卡
1. 打开 `knowledge/cards/<kp>.md`，核对每个小节；`python tools/annotate.py card <kp> --write` 写入页码候选并人工确认。
2. front matter：`review_status: reviewed`、`reviewer: <用户名>`、`textbook_pages: 第X章 p.xx`（去掉“待核”）、`updated`。

## 优先级
按 `docs/README.md` 第 2 节“知识点考频”从上往下审——考频越高越先审。
