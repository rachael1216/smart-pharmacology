#!/usr/bin/env python3
"""annotate.py — 解析标注：给每道题、每张知识卡挂上“教材出处”。

原则（与 AGENTS.md 一致）：答案与解析的依据只能来自教材、讲义或本地资料，
AI 起草的知识卡不算出处。程序给出候选，人核对后把 status 从“待核”改成“已核”。

  python tools/annotate.py suggest 24-pharm-final-019        # 为一道题检索候选出处（只查教材/讲义/本地资料）
  python tools/annotate.py add 24-pharm-final-019 --src 药理学第9版 --loc "第2章 p.12" --quote "……"
  python tools/annotate.py auto --exam 24-pharm-final -k 1   # 批量：给尚无出处的题写入首条候选（待核）
  python tools/annotate.py auto --all --min-score 10
  python tools/annotate.py verify 24-pharm-final-019         # 人工核对后标记“已核”
  python tools/annotate.py card first_pass --write           # 为知识卡写入 textbook_pages 候选

写回文件时保持 bank/exams/*.yaml 的统一格式（tools/common.py:write_exam）。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CARDS, exam_files, load_cards, load_yaml, write_exam  # noqa: E402
import rag  # noqa: E402

QUOTE_MAX = 80


def query_for(q: dict, cards: dict) -> str:
    parts = [str(q.get("stem", "")), *map(str, q.get("sub", []) or [])]
    for k in q.get("kp", []) or []:
        c = cards.get(k)
        if c:
            parts.append(c["meta"]["title"])
            parts += [m for m in c["meta"].get("match", []) if not str(m).startswith("re:")][:4]
    text = " ".join(parts)
    return re.sub(r"[（）()？?，,。：:；;、\-—_]+", " ", text)


def hits_for(q: dict, cards: dict, k: int, idx):
    return rag.search(query_for(q, cards), k, exclude=rag.AI_CORPORA, idx=idx)


def to_evidence(score: float, d: dict, by: str = "rag") -> dict:
    quote = re.sub(r"\s+", "", d["text"])[:QUOTE_MAX]
    return dict(src=d["source"], loc=d["locator"], quote=quote, score=round(score, 1), by=by, status="待核")


def find_question(qid: str):
    for f in exam_files():
        d = load_yaml(f)
        for q in d["questions"]:
            if q["id"] == qid:
                return f, d, q
    sys.exit(f"没有题目 {qid}")


def cmd_suggest(qid: str, k: int):
    f, d, q = find_question(qid)
    cards = load_cards()
    idx = rag.load()
    print(f"{qid}：{q['stem']}\n检索式：{query_for(q, cards)}\n")
    res = hits_for(q, cards, k, idx)
    if not res:
        print("没有教材/讲义候选。请先放入教材（python tools/kb.py build <pdf>）和讲义（reference/lecture/），再 python tools/rag.py build。")
    for i, (s, dd) in enumerate(res, 1):
        print(f"[{i}] {dd['source']} · {dd['locator']}  score={s:.1f}\n    {dd['text'].replace(chr(10), ' ')[:220]}\n")
    if res:
        print(f"写入：python tools/annotate.py add {qid} --pick 1   （或 --src/--loc/--quote 手填）")


def cmd_add(qid: str, src, loc, quote, pick, k):
    f, d, q = find_question(qid)
    if pick:
        res = hits_for(q, load_cards(), max(pick), rag.load())
        new = [to_evidence(*res[i - 1], by="rag+人工选择") for i in pick if i <= len(res)]
    else:
        if not (src and loc):
            sys.exit("需要 --pick N，或 --src 与 --loc")
        new = [dict(src=src, loc=loc, quote=(quote or "")[:QUOTE_MAX], by="人工", status="待核")]
    ev = q.setdefault("evidence", [])
    for e in new:
        if not any(x.get("loc") == e["loc"] for x in ev):
            ev.append(e)
    write_exam(f, d)
    print(f"✓ {qid} 现有出处 {len(ev)} 条（均需人工核对后 verify）")


def cmd_auto(exam: str | None, all_: bool, k: int, min_score: float, overwrite: bool):
    cards, idx = load_cards(), rag.load()
    if not any(d["corpus"] not in rag.AI_CORPORA for d in idx["docs"]):
        sys.exit("索引中没有教材/讲义语料，无法标注出处。先 python tools/kb.py build <教材.pdf> 并 python tools/rag.py build。")
    n_q = n_e = 0
    for f in exam_files():
        if not all_ and f.stem != exam:
            continue
        d = load_yaml(f)
        changed = False
        for q in d["questions"]:
            if q.get("completeness") in ("image_only", "lost") or (q.get("evidence") and not overwrite):
                continue
            res = [(s, dd) for s, dd in hits_for(q, cards, k, idx) if s >= min_score]
            if res:
                q["evidence"] = [to_evidence(s, dd) for s, dd in res]
                n_q += 1
                n_e += len(res)
                changed = True
        if changed:
            write_exam(f, d)
    print(f"✓ 为 {n_q} 道题写入 {n_e} 条候选出处（status: 待核）。请逐条核对：python tools/bank.py show <题号>")


def cmd_verify(qid: str):
    f, d, q = find_question(qid)
    for e in q.get("evidence", []) or []:
        e["status"] = "已核"
    write_exam(f, d)
    print(f"✓ {qid} 的 {len(q.get('evidence', []))} 条出处已标记为已核")


def cmd_card(kid: str, k: int, write: bool):
    cards = load_cards()
    if kid not in cards:
        sys.exit(f"没有知识卡 {kid}")
    c = cards[kid]
    query = " ".join([c["meta"]["title"], *[m for m in c["meta"].get("match", []) if not str(m).startswith("re:")]])
    res = rag.search(query, k, exclude=rag.AI_CORPORA)
    for i, (s, dd) in enumerate(res, 1):
        print(f"[{i}] {dd['locator']}  score={s:.1f}  {dd['text'].replace(chr(10), ' ')[:120]}")
    if write and res:
        pages = "；".join(dict.fromkeys(dd["locator"] for _, dd in res)) + "（待核）"
        f = CARDS / f"{kid}.md"
        t = f.read_text(encoding="utf-8")
        t = re.sub(r"(?m)^textbook_pages:.*$", f"textbook_pages: {pages}", t, count=1)
        f.write_text(t, encoding="utf-8")
        print(f"✓ 已写入 {f.name}: textbook_pages: {pages}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("suggest"); s.add_argument("qid"); s.add_argument("-k", type=int, default=5)
    s = sp.add_parser("add"); s.add_argument("qid"); s.add_argument("--src"); s.add_argument("--loc"); s.add_argument("--quote")
    s.add_argument("--pick", type=int, nargs="+", help="选用 suggest 结果的序号"); s.add_argument("-k", type=int, default=5)
    s = sp.add_parser("auto"); s.add_argument("--exam"); s.add_argument("--all", action="store_true"); s.add_argument("-k", type=int, default=1)
    s.add_argument("--min-score", type=float, default=8.0); s.add_argument("--overwrite", action="store_true")
    s = sp.add_parser("verify"); s.add_argument("qid")
    s = sp.add_parser("card"); s.add_argument("kp"); s.add_argument("-k", type=int, default=3); s.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if a.cmd == "suggest":
        cmd_suggest(a.qid, a.k)
    elif a.cmd == "add":
        cmd_add(a.qid, a.src, a.loc, a.quote, a.pick, a.k)
    elif a.cmd == "auto":
        if not (a.exam or a.all):
            sys.exit("需要 --exam <考试id> 或 --all")
        cmd_auto(a.exam, a.all, a.k, a.min_score, a.overwrite)
    elif a.cmd == "verify":
        cmd_verify(a.qid)
    elif a.cmd == "card":
        cmd_card(a.kp, a.k, a.write)


if __name__ == "__main__":
    main()
