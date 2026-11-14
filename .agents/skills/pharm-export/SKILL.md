---
name: pharm-export
description: 导出。按用途选格式与筛选条件，产出 Word 试卷/答案、Excel、Anki、JSON、SQLite、离线网页。
---
# 导出

| 用途 | 命令 |
|---|---|
| 打印模拟卷（无答案） | `python tools/export.py docx --mode paper --exam 24-pharm-final` |
| 答案解析册（合并） | `python tools/export.py docx --mode key --merge` |
| 只要已审的大题 | `python tools/export.py docx --mode key --type essay,short_answer --status reviewed,verified --merge` |
| Excel 审稿 | `python tools/export.py xlsx` |
| Anki 卡组 | `python tools/export.py anki`（Anki → 导入文件，选“制表符分隔”，第 3 列为标签） |
| 给前端 / 大模型 | `python tools/export.py json` 或 `jsonl` |
| SQL 查询 | `python tools/export.py sqlite`（视图 `v_kp_frequency`、`v_need_evidence`） |
| 离线浏览器 | `python tools/export.py html` |
| 一次全导 | `python tools/export.py all` |

筛选参数：`--exam --cohort --major --kind --type --kp --status --lang`（逗号分隔多选）。产物在 `exports/`（不入库）。
