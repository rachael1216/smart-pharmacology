# 真题库数据规范

真题库的正本是 `bank/exams/<考试id>.yaml`，**一场考试一个文件**。`bank/raw/<考试id>.md` 保存考后回忆原文（逐字，不改），两者一一对应。

## 1 考试 id

`<年级两位>-<专业>-<类型>[-后缀]`，例如 `24-pharm-final`、`23-lin5-makeup-c`。

| 专业代码 | 专业 | 类型代码 | kind |
|---|---|---|---|
| lin5 | 临床医学（五年制） | midterm | 期中 |
| lin8 | 临床医学（八年制） | final | 期末 |
| pharm | 药学 | makeup | 缓考 |
| nurs | 护理学 | lab | 实验 |
| dent | 口腔医学 | | |
| prev | 预防医学 | | |

“年级”指考生的入学年级（24 临五 = 2024 级临床五年制），不是考试年份。

## 2 `exam` 段

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✓ | 与文件名一致 |
| `title` | ✓ | 如“2024级 药学 药理学 期末” |
| `cohort` | ✓ | 整数年级，如 2024 |
| `major` | ✓ | 专业全称 |
| `kind` | ✓ | 期中 / 期末 / 缓考 / 实验 |
| `variant` | | 同年同类的区分，如 C（药理学C） |
| `source` | ✓ | `title` `url` `published` `account` `license` |
| `format` | | 题型与分值：`section` `type` `score` `header`（header 为原文表头） |
| `notes` | | 回忆者备注（考试时长、英文比例、复习建议等） |

## 3 题目字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✓ | `<考试id>-<三位序号>`，**一经发布不改**（外部引用靠它） |
| `num` | ✓ | 卷面题号 |
| `section` | ✓ | 所属大题（名词解释、单选题……） |
| `type` | ✓ | 见下表 |
| `stem` | ✓ | 题干（只写题干） |
| `sub` | | 小问列表 |
| `options` | | 选项，`A:` `B:` …；回忆不全时省略 |
| `recall` | | 回忆者括号里的线索（可能是选项，也可能是答案），**不等于标准答案** |
| `completeness` | ✓ | 回忆完整度，见下表 |
| `answer` | | 本题特有的答案（选择题答案、填空、病例判断） |
| `answer_ref` | | 引用知识卡：`kp` / `kp#小节` / `cmp:鉴别卡`，导出时展开 |
| `analysis` | | 解析：考点 → 答题框架 → 易错点 |
| `kp` | ✓* | 关联知识卡 id（`knowledge/cards/<id>.md`）；回忆缺失的题可空 |
| `evidence` | | 教材出处列表，见第 4 节 |
| `status` | ✓ | `todo` / `draft-ai` / `draft` / `reviewed` / `verified` |
| `reviewer` | | 审核人（GitHub 用户名，不写学号姓名） |
| `note` | | 编辑备注 |

`status` 不是 `todo` 时，`answer` 与 `answer_ref` 至少有一个。

**type**：`definition` 名词解释 · `fill_blank` 填空 · `single_choice` 单选 · `multi_choice` 多选 · `choice` 选择（单/多未区分）· `matching` B 型配伍 · `true_false` 判断 · `short_answer` 简答 · `essay` 问答/论述 · `case` 病例分析 · `experiment_design` 实验设计。

**completeness**：`full` 完整 · `stem_with_hint` 题干 + 回忆者括注 · `stem_only` 仅题干无选项 · `topic_only` 仅考点 · `image_only` 原文为截图未转录 · `lost` 回忆缺失。

## 4 `evidence`（教材出处）

```yaml
evidence:
- src: 《药理学》第9版        # 书名或资料名
  loc: 第2章 药物代谢动力学 p.12   # 能翻回去的位置
  quote: 口服药物在通过肠黏膜及肝脏时……   # ≤80 字，仅作定位
  score: 15.3                 # 检索得分（程序写入）
  by: rag                     # rag / rag+人工选择 / 人工
  status: 待核                 # 待核 → 已核
```

出处只能来自教材、讲义、本地资料；知识卡和真题本身不能作为出处。

## 5 答案为什么分 `answer` 和 `answer_ref`

“首过消除”在 13 场考试里出现过。它的标准答案只写一次，放在 `knowledge/cards/first_pass.md`，13 道题都用 `answer_ref: [first_pass]` 引用；改一处，所有年份同步更新。病例判断、选择题答案等本题特有的内容写在 `answer`。导出（`tools/export.py`）与 `docs/` 中两者自动合并展示。

`answer_ref` 的写法：

| 写法 | 展开为 |
|---|---|
| `first_pass` | 知识卡的【标准答案】【评分要点】两节（没有这两节则取全文） |
| `raas#ACEI降压机制` | 知识卡中名为“ACEI降压机制”的小节 |
| `cmp:heparin_vs_warfarin` | 鉴别卡全文 |

## 6 知识卡 `knowledge/cards/<id>.md`

```markdown
---
id: first_pass
title: 首过消除（首过效应）
title_en: first-pass elimination
chapter: ch02                 # knowledge/chapters.yaml
kind: 概念                     # 概念 / 机制 / 药物 / 原则 / 应用 / 实验
match: [首过, first pass]      # 自动关联题目用的关键词（"re:" 开头为正则）
textbook_pages: 待核           # 核对后写“第2章 p.12”
review_status: draft-ai        # draft-ai / draft / reviewed / verified
reviewer: ""
updated: '2026-11-15'
---
# 首过消除（首过效应）
## 标准答案
## 评分要点
## 展开与鉴别
## 英文与构词
```
小节标题可以按内容增减（大题类知识卡常见“作用机制”“临床应用”“不良反应”），但改名时要同步修改引用它的 `answer_ref`——`bank.py check` 会报出失效引用。
