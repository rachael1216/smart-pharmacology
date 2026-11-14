#!/usr/bin/env python3
"""kb.py — 把你手上的药理学教材 PDF 切成“按章、带页码”的文本，作为 RAG 的 textbook 语料。

教材有版权，本仓库**不包含**教材内容：每位使用者用自己的 PDF 在本机生成，
生成的 reference/textbook/ch_*.md 已被 .gitignore 忽略，不会被提交。

  python tools/kb.py build 药理学第9版.pdf --book "《药理学》第9版（杨宝峰，陈建国 主编，人民卫生出版社，2018）"
  python tools/kb.py build 药理学.pdf --offset 12      # PDF 第 13 页印的是书页 1 时，用 offset 让页码与纸书一致
  python tools/kb.py list                             # 列出各章与页码
  python tools/kb.py show 25                          # 打印第 25 章全文
  python tools/kb.py find 首过消除                     # 全书关键词检索（带页码）

切章规则：行首“第X章 标题”（X 为中文或阿拉伯数字），且出现在该页前 8 行内；
目录页（标题后跟页码点线）会被跳过。扫描版 PDF 无文本层时需先 OCR。
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "reference" / "textbook"
CN = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "百": 100}
HEAD = re.compile(r"^\s*第\s*([一二三四五六七八九十百零\d]+)\s*章\s*(\S[^\n]{0,40}?)\s*$")
TOC_LINE = re.compile(r"(\.{3,}|…{2,}|·{3,})\s*\d+\s*$|\s\d{1,4}\s*$")


def cn2int(s: str) -> int:
    if s.isdigit():
        return int(s)
    total, cur = 0, 0
    for ch in s:
        v = CN[ch]
        if v >= 10:
            total += (cur or 1) * v
            cur = 0
        else:
            cur = v
    return total + cur


def read_pages(pdf: Path) -> list[str]:
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, check=True).stdout
        return out.decode("utf8", "ignore").split("\f")
    try:
        import fitz  # type: ignore
        with fitz.open(pdf) as doc:
            return [p.get_text() for p in doc]
    except ImportError:
        pass
    try:
        from pypdf import PdfReader  # type: ignore
        return [(p.extract_text() or "") for p in PdfReader(str(pdf)).pages]
    except ImportError:
        sys.exit("无法读取 PDF：请安装 poppler（pdftotext）或 pip install pymupdf / pypdf")


def split_chapters(pages: list[str], offset: int = 0) -> list[dict]:
    """pages[i] 为 PDF 第 i+1 页文本；返回 [{num,title,start,end,pages:[(书页,文本)]}]。"""
    starts = []
    for i, text in enumerate(pages):
        lines = [l for l in text.splitlines() if l.strip()][:8]
        for l in lines:
            m = HEAD.match(l)
            if m and not TOC_LINE.search(l):
                n = cn2int(m.group(1))
                if not starts or n > starts[-1][0]:
                    starts.append((n, m.group(2).strip(), i))
                break
    chapters = []
    for j, (n, title, i) in enumerate(starts):
        end = starts[j + 1][2] if j + 1 < len(starts) else len(pages)
        pg = [(k + 1 - offset, pages[k]) for k in range(i, end)]
        chapters.append(dict(num=n, title=title, start=pg[0][0], end=pg[-1][0], pages=pg))
    return chapters


def clean(text: str) -> str:
    text = re.sub(r"[ \t　]{2,}", " ", text)
    text = re.sub(r"(?<=[一-鿿，、；：])\n(?=[一-鿿])", "", text)  # 合并 PDF 折行（“首过消\n除”）
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def cmd_build(pdf: Path, book: str, offset: int):
    pages = read_pages(pdf)
    chs = split_chapters(pages, offset)
    if not chs:
        sys.exit("没有识别到“第X章”标题：请确认 PDF 有文本层（扫描版需先 OCR）。")
    KB_DIR.mkdir(parents=True, exist_ok=True)
    for old in KB_DIR.glob("ch_*.md"):
        old.unlink()
    for c in chs:
        body = "\n\n".join(f"<!-- p.{p} -->\n{clean(t)}" for p, t in c["pages"] if t.strip())
        fm = f"---\nid: ch{c['num']:02d}\nkind: chapter\ntitle: 第{c['num']}章 {c['title']}\npages: {c['start']}-{c['end']}\nbook: {book}\n---\n\n"
        (KB_DIR / f"ch_{c['num']:02d}.md").write_text(fm + body + "\n", encoding="utf-8")
    print(f"✓ {len(chs)} 章 → {KB_DIR.relative_to(ROOT)}/ch_*.md（{book}）")
    print("  下一步：python tools/rag.py build")


def chapters_on_disk():
    out = []
    for f in sorted(KB_DIR.glob("ch_*.md")):
        t = f.read_text(encoding="utf-8")
        meta = dict(re.findall(r"(?m)^(\w+): (.*)$", t.split("---", 2)[1]))
        out.append((f, meta, t.split("---", 2)[2]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("build"); b.add_argument("pdf", type=Path); b.add_argument("--book", default="《药理学》（请用 --book 注明版次）"); b.add_argument("--offset", type=int, default=0, help="PDF 页码 − 书页码")
    sp.add_parser("list")
    s = sp.add_parser("show"); s.add_argument("chapter", type=int)
    f = sp.add_parser("find"); f.add_argument("word")
    a = ap.parse_args()
    if a.cmd == "build":
        return cmd_build(a.pdf, a.book, a.offset)
    chs = chapters_on_disk()
    if not chs:
        sys.exit("尚未建立教材索引：python tools/kb.py build <你的教材.pdf>")
    if a.cmd == "list":
        for _, m, _ in chs:
            print(f"{m['id']}  {m['title']:<30} p.{m['pages']}")
    elif a.cmd == "show":
        for _, m, body in chs:
            if m["id"] == f"ch{a.chapter:02d}":
                print(m["title"], m["pages"], "\n", body)
    elif a.cmd == "find":
        for _, m, body in chs:
            page = "?"
            for line in body.splitlines():
                pm = re.match(r"<!-- p\.(\S+) -->", line)
                if pm:
                    page = pm.group(1)
                elif a.word in line:
                    print(f"{m['title']} p.{page}: {line.strip()[:100]}")


if __name__ == "__main__":
    main()
