# reference/ — RAG 语料

| 目录 | 内容 | 是否入库 | 如何放入 |
|---|---|---|---|
| `textbook/` | 教材按章切分的文本（带页码标记） | **否**（版权） | `python tools/kb.py build <你的教材.pdf> --book "《药理学》第9版（杨宝峰，陈建国 主编）" --offset <PDF页码−书页码>` |
| `lecture/` | 讲义、PPT 导出的 PDF、课堂笔记（pdf / docx / pptx / md / txt） | 否 | 直接放入 |
| `local/<名称>/` | 其他教材与资料，子目录名即语料标签（如 `local/药理学第10版/`、`local/执医/`） | 否 | 直接放入 |
| `literature/` | 公开文献的书目与要点（可入库） | 是 | 编辑 `references.yaml` |
| `index/` | 检索索引（自动生成） | 否 | `python tools/rag.py build` |

放入资料后：

```bash
python tools/rag.py build                         # 重建索引
python tools/rag.py search 首过消除 --authoritative  # 只查教材/讲义/本地资料
python tools/annotate.py auto --all -k 1          # 为全部题目写入出处候选（待核）
```

扫描版 PDF 没有文本层，需先 OCR（如 `ocrmypdf -l chi_sim in.pdf out.pdf`）。
