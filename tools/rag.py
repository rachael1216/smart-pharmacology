#!/usr/bin/env python3
"""rag.py — 本地检索（RAG 的“R”）：写解析前先查教材原文，答案措辞贴近课本、出处能回到页码。

语料（每个片段带来源标签 corpus 与出处 locator）：
  textbook  reference/textbook/ch_*.md      教材（tools/kb.py 在本机由你的 PDF 生成，不入库）
  lecture   reference/lecture/**            讲义 / PPT 导出的 PDF / 课堂笔记（pdf、docx、md、txt）
  <目录名>   reference/local/<目录>/**         其他教材与资料（如 local/药理学第10版/、local/执医/），只在本机
  card      knowledge/cards/*.md            知识卡（AI 起草，需审核）
  compare   knowledge/compare/*.md          鉴别卡
  bank      bank/exams/*.yaml               历年真题（看“这个点以前怎么考”）

  python tools/rag.py build
  python tools/rag.py search 首过消除 舌下 -k 5
  python tools/rag.py search 氨基糖苷 耳毒性 -c textbook,lecture --full
  python tools/rag.py sources
  python tools/rag.py export -c textbook,lecture     # 导出纯文本，可交给向量检索（如 local-rag-cpp）

算法：中文字二元组 + 英文小写词的 BM25（k1=1.5，b=0.75），纯标准库，结果可复现。
权威度：textbook > lecture > 本地资料 > card/compare（AI 起草）；标注出处时只用前三类。
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CARDS, COMPARE, EXAMS, REFERENCE, ROOT, full_answer, load_cards, load_compares, load_yaml  # noqa: E402

INDEX = REFERENCE / "index" / "rag.json"
TEXTBOOK, LECTURE, LOCAL = REFERENCE / "textbook", REFERENCE / "lecture", REFERENCE / "local"
AUTHORITATIVE = None  # 运行时：除 card / compare / bank 外的全部语料
AI_CORPORA = {"card", "compare", "bank"}
CHUNK = 380

_CJK = re.compile(r"[一-鿿]+")
_LAT = re.compile(r"[A-Za-z][A-Za-z0-9\-]*|\d+(?:\.\d+)?")


def tokens(text: str) -> list[str]:
    out: list[str] = []
    for m in _CJK.finditer(text):
        s = m.group(0)
        out += [s] if len(s) == 1 else [s[i:i + 2] for i in range(len(s) - 1)]
    out += [w.lower() for w in _LAT.findall(text)]
    return out


def split_paragraphs(text: str, size: int = CHUNK) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\d+[．.、])|\n(?=[一二三四五六七八九十]+、)", text) if p.strip()]
    out, buf = [], ""
    for p in paras:
        if len(buf) + len(p) > size and buf:
            out.append(buf)
            buf = ""
        while len(p) > size * 1.6:
            cut = max(p.rfind(c, 0, size) for c in "。；;！？\n")
            cut = cut if cut > size // 2 else size
            out.append((buf + p[:cut + 1]).strip())
            buf, p = "", p[cut + 1:]
        buf = (buf + "\n" + p).strip() if buf else p
    if buf:
        out.append(buf)
    return out


# ------------------------------------------------------------------ 各类语料切片
def chunks_textbook(f: Path):
    t = f.read_text(encoding="utf-8")
    meta = dict(re.findall(r"(?m)^(\w+): (.*)$", t.split("---", 2)[1])) if t.startswith("---") else {}
    body = t.split("---", 2)[2] if t.startswith("---") else t
    for part in re.split(r"(?=<!-- p\.\S+ -->)", body):
        m = re.match(r"<!-- p\.(\S+) -->", part)
        if not m:
            continue
        for piece in split_paragraphs(part[m.end():]):
            yield dict(corpus="textbook", source=meta.get("book", f.stem), chapter=meta.get("id", ""),
                       locator=f"{meta.get('title', f.stem)} p.{m.group(1)}", text=piece)


def chunks_card(f: Path, corpus: str):
    from common import parse_card
    c = parse_card(f)
    if not c["order"]:  # 无“## ”小节（如纯表格的鉴别卡）：整篇切片
        c["order"], c["sections"] = ["全文"], {"全文": re.sub(r"^#\s.*\n", "", c["body"]).strip()}
    for sec in c["order"]:
        for piece in split_paragraphs(c["sections"][sec]):
            yield dict(corpus=corpus, source=c["meta"].get("title", f.stem), chapter=c["meta"].get("chapter", ""),
                       locator=f"{f.relative_to(ROOT)} §{sec}", text=f"{c['meta'].get('title', '')}：{piece}")


def chunks_bank():
    cards, compares = load_cards(), load_compares()
    for f in sorted(EXAMS.glob("*.yaml")):
        d = load_yaml(f)
        for q in d.get("questions", []):
            if q.get("completeness") in ("image_only", "lost"):
                continue
            stem = " ".join([q["stem"], *map(str, q.get("sub", []) or [])])
            ans = full_answer(q, cards, compares)[:300]
            yield dict(corpus="bank", source=d["exam"]["title"], chapter="", locator=q["id"], text=f"{stem}\n{ans}")


def read_pdf(f: Path) -> list[str]:
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True).stdout
        return out.decode("utf8", "ignore").split("\f")
    try:
        import fitz  # type: ignore
        return [pg.get_text() for pg in fitz.open(str(f))]
    except ImportError:
        print(f"! 无法读取 {f.name}：请安装 poppler（pdftotext）或 pip install pymupdf", file=sys.stderr)
        return []


def chunks_file(f: Path, tag: str):
    suf = f.suffix.lower()
    if suf == ".pdf":
        for i, pg in enumerate(read_pdf(f), 1):
            for piece in split_paragraphs(re.sub(r"[ \t]+", " ", pg)):
                yield dict(corpus=tag, source=f.stem, chapter="", locator=f"{f.name} p.{i}", text=piece)
    elif suf == ".docx":
        from docx import Document  # type: ignore
        text = "\n\n".join(p.text for p in Document(str(f)).paragraphs if p.text.strip())
        for piece in split_paragraphs(text):
            yield dict(corpus=tag, source=f.stem, chapter="", locator=f.name, text=piece)
    elif suf == ".pptx":
        from pptx import Presentation  # type: ignore
        for i, s in enumerate(Presentation(str(f)).slides, 1):
            text = "\n".join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)
            for piece in split_paragraphs(text):
                yield dict(corpus=tag, source=f.stem, chapter="", locator=f"{f.name} 第{i}张", text=piece)
    elif suf in (".md", ".txt"):
        for piece in split_paragraphs(f.read_text(encoding="utf-8", errors="ignore")):
            yield dict(corpus=tag, source=f.stem, chapter="", locator=f.name, text=piece)


# ------------------------------------------------------------------ 建库与检索
def build(quiet=False):
    docs: list[dict] = []
    for f in sorted(TEXTBOOK.glob("ch_*.md")):
        docs += list(chunks_textbook(f))
    for base, default in ((LECTURE, "lecture"), (LOCAL, "local")):
        if base.exists():
            for f in sorted(base.rglob("*")):
                if f.is_file() and f.suffix.lower() in (".pdf", ".docx", ".pptx", ".md", ".txt") and f.name.lower() != "readme.md":
                    rel = f.relative_to(base).parts
                    tag = rel[0] if base is LOCAL and len(rel) > 1 else default
                    docs += list(chunks_file(f, tag))
    for f in sorted(CARDS.glob("*.md")):
        docs += list(chunks_card(f, "card"))
    for f in sorted(COMPARE.glob("*.md")):
        docs += list(chunks_card(f, "compare"))
    docs += list(chunks_bank())
    df: Counter = Counter()
    for i, d in enumerate(docs):
        d["id"] = i
        d["tok"] = Counter(tokens(d["text"]))
        d["len"] = sum(d["tok"].values())
        df.update(d["tok"].keys())
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps({"n": len(docs), "avg": sum(d["len"] for d in docs) / max(len(docs), 1), "df": df,
                                 "docs": [{**d, "tok": dict(d["tok"])} for d in docs]}, ensure_ascii=False), encoding="utf-8")
    c = Counter(d["corpus"] for d in docs)
    if not quiet:
        print(f"✓ 索引 {len(docs)} 个片段 → {INDEX.relative_to(ROOT)}")
        for k, v in c.most_common():
            print(f"   {k:<12}{v}")
        if "textbook" not in c:
            print("   （尚无 textbook 语料：python tools/kb.py build <你的药理学教材.pdf>）")
    return c


def load():
    if not INDEX.exists():
        build(quiet=True)
    return json.loads(INDEX.read_text(encoding="utf-8"))


def search(query: str, k: int = 5, corpora: set[str] | None = None, exclude: set[str] | None = None, idx=None):
    idx = idx or load()
    q = Counter(tokens(query))
    n, avg, df = idx["n"], idx["avg"], idx["df"]
    res = []
    for d in idx["docs"]:
        if corpora and d["corpus"] not in corpora:
            continue
        if exclude and d["corpus"] in exclude:
            continue
        s = 0.0
        for t in q:
            f = d["tok"].get(t)
            if f:
                idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                s += idf * f * 2.5 / (f + 1.5 * (0.25 + 0.75 * d["len"] / avg))
        if s > 0:
            res.append((s, d))
    res.sort(key=lambda x: -x[0])
    return res[:k]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("build")
    sp.add_parser("sources")
    e = sp.add_parser("export"); e.add_argument("-c", "--corpus"); e.add_argument("-o", "--out", default=str(REFERENCE / "index" / "corpus.txt"))
    s = sp.add_parser("search")
    s.add_argument("query", nargs="+")
    s.add_argument("-k", type=int, default=5)
    s.add_argument("-c", "--corpus", help="逗号分隔：textbook,lecture,card,compare,bank 或 local 子目录名")
    s.add_argument("--authoritative", action="store_true", help="只检索教材/讲义/本地资料（排除 AI 起草的 card/compare/bank）")
    s.add_argument("--full", action="store_true")
    s.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.cmd == "build":
        build()
        return
    idx = load()
    if a.cmd == "sources":
        for (cp, src), v in sorted(Counter((d["corpus"], d["source"]) for d in idx["docs"]).items()):
            print(f"{cp:<10}{src}  ({v})")
        return
    if a.cmd == "export":
        want = set(a.corpus.split(",")) if a.corpus else None
        lines = [f"[{d['corpus']}] {d['locator']}\n{d['text'].strip()}\n" for d in idx["docs"] if not want or d["corpus"] in want]
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text("\n".join(lines), encoding="utf-8")
        print(f"✓ {a.out}（{len(lines)} 段）")
        return
    res = search(" ".join(a.query), a.k, set(a.corpus.split(",")) if a.corpus else None,
                 AI_CORPORA if a.authoritative else None, idx)
    if a.json:
        print(json.dumps([{"score": round(s, 2), **{k: v for k, v in d.items() if k != "tok"}} for s, d in res], ensure_ascii=False, indent=1))
        return
    if not res:
        print("没有检索到相关片段（换关键词，或先放入教材：python tools/kb.py build <pdf>）。")
    for i, (sc, d) in enumerate(res, 1):
        body = d["text"] if a.full else d["text"].replace("\n", " ")[:200] + ("…" if len(d["text"]) > 200 else "")
        print(f"[{i}] ({d['corpus']}) {d['locator']}  score={sc:.1f}\n    {body}\n")


if __name__ == "__main__":
    main()
