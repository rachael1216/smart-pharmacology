#!/usr/bin/env python3
"""bank.py — 真题库的校验、统计、查看与可读版生成。

  python tools/bank.py check            # 校验全部数据（CI 同款）；有错误时退出码 1
  python tools/bank.py stats            # 覆盖率：答案、解析、教材出处、审核状态
  python tools/bank.py show 24-pharm-final-019   # 查看一道题（答案引用已展开）
  python tools/bank.py find 首过         # 按题干/知识点搜题
  python tools/bank.py fmt              # 把 bank/exams/*.yaml 规范成统一格式（人工编辑后可跑）
  python tools/bank.py docs             # 重新生成 docs/（GitHub 上直接阅读的试卷与答案解析）
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (COMPLETENESS, EVIDENCE_STATUS, KINDS, KNOW, ROOT, STATUS, TYPES, exam_files, full_answer,  # noqa: E402
                    load_cards, load_compares, load_drugs, load_exams, load_stems, load_yaml, resolve_ref, write_exam)

DOCS = ROOT / "docs"
CARD_STATUS = {"draft-ai", "draft", "reviewed", "verified"}


# ------------------------------------------------------------------ 加载
class Bank:
    def __init__(self):
        self.exams = load_exams()
        self.cards = load_cards()
        self.compares = load_compares()
        self.chapters = {c["id"]: c for c in load_yaml(KNOW / "chapters.yaml")}
        self.drugs = load_drugs()
        self.stems = load_stems()
        self.questions = [dict(q, _exam=e["exam"]) for e in self.exams for q in e.get("questions", [])]
        self.qmap = {q["id"]: q for q in self.questions}

    def kp_questions(self):
        out = collections.defaultdict(list)
        for q in self.questions:
            for k in q.get("kp", []) or []:
                out[k].append(q)
        return out


# ------------------------------------------------------------------ 校验
def check(b: Bank):
    err, warn = [], []
    seen = set()
    for e in b.exams:
        f, ex = e["_file"], e.get("exam", {})
        tag = f.name
        if ex.get("id") != f.stem:
            err.append(f"{tag}: exam.id 应与文件名一致（{f.stem}）")
        if not isinstance(ex.get("cohort"), int):
            err.append(f"{tag}: cohort 应为整数年级，如 2024")
        if ex.get("kind") not in KINDS:
            err.append(f"{tag}: kind 应为 {sorted(KINDS)}")
        if not (ex.get("source") or {}).get("url"):
            err.append(f"{tag}: 缺 source.url")
        nums = set()
        for q in e.get("questions", []):
            qid = q.get("id", "?")
            p = f"{tag} {qid}"
            if qid in seen:
                err.append(f"{p}: 题号重复")
            seen.add(qid)
            if not str(qid).startswith(ex.get("id", "") + "-"):
                err.append(f"{p}: id 应以“{ex.get('id')}-”开头")
            if q.get("num") in nums:
                err.append(f"{p}: num 重复")
            nums.add(q.get("num"))
            if q.get("type") not in TYPES:
                err.append(f"{p}: type 非法 {q.get('type')}")
            if not str(q.get("stem", "")).strip():
                err.append(f"{p}: 缺 stem")
            if q.get("completeness") not in COMPLETENESS:
                err.append(f"{p}: completeness 非法 {q.get('completeness')}")
            st = q.get("status")
            if st not in STATUS:
                err.append(f"{p}: status 非法 {st}")
            if st != "todo" and not (q.get("answer") or q.get("answer_ref")):
                err.append(f"{p}: status={st} 但没有 answer / answer_ref")
            for k in q.get("kp", []) or []:
                if k not in b.cards:
                    err.append(f"{p}: kp 不存在 {k}（knowledge/cards/{k}.md）")
            for r in q.get("answer_ref", []) or []:
                try:
                    resolve_ref(r, b.cards, b.compares)
                except KeyError as x:
                    err.append(f"{p}: answer_ref 无法解析 {r} — {x}")
            opts = q.get("options")
            if opts is not None and (not isinstance(opts, dict) or not all(re.fullmatch(r"[A-Z]", str(k)) for k in opts)):
                err.append(f"{p}: options 应为 A/B/C… 为键的映射")
            for ev in q.get("evidence", []) or []:
                if not isinstance(ev, dict) or not ev.get("src") or not ev.get("loc"):
                    err.append(f"{p}: evidence 每条需有 src 与 loc")
                elif ev.get("status") not in EVIDENCE_STATUS:
                    err.append(f"{p}: evidence.status 应为 {sorted(EVIDENCE_STATUS)}")
            if not q.get("kp") and q.get("completeness") not in ("lost", "image_only"):
                warn.append(f"{p}: 未关联知识点")
            if st in ("reviewed", "verified") and not q.get("evidence"):
                warn.append(f"{p}: 已审但没有教材出处（evidence）")
    for kid, c in b.cards.items():
        m = c["meta"]
        if c["file"].stem != kid:
            err.append(f"cards/{c['file'].name}: id 应与文件名一致")
        if m.get("chapter") not in b.chapters:
            err.append(f"cards/{kid}: chapter 不存在 {m.get('chapter')}")
        if m.get("review_status") not in CARD_STATUS:
            err.append(f"cards/{kid}: review_status 应为 {sorted(CARD_STATUS)}")
        if not c["sections"]:
            err.append(f"cards/{kid}: 至少需要一个“## ”小节")
    for cid, c in b.compares.items():
        for k in c["meta"].get("kp", []):
            if k not in b.cards:
                err.append(f"compare/{cid}: kp 不存在 {k}")
    ids = collections.Counter(d["id"] for d in b.drugs)
    err += [f"drugs.yaml: id 重复 {i}" for i, n in ids.items() if n > 1]
    for d in b.drugs:
        if d.get("kp") not in b.cards:
            err.append(f"drugs.yaml {d['id']}: kp 不存在 {d.get('kp')}")
    for s in b.stems:
        try:
            re.compile(s["regex"])
        except re.error as x:
            err.append(f"stems.yaml {s['id']}: 正则错误 {x}")
    names = {d["cn"] for d in b.drugs}
    for c in load_yaml(KNOW / "confusables.yaml") or []:
        warn += [f"confusables {c['id']}: {n} 不在 drugs.yaml" for n in c["drugs"] if n not in names]
    return err, warn


# ------------------------------------------------------------------ 统计
def coverage(b: Bank):
    qs = [q for q in b.questions if q.get("completeness") not in ("lost",)]
    n = len(qs) or 1
    has_ans = sum(bool(q.get("answer") or q.get("answer_ref")) for q in qs)
    has_ana = sum(bool(q.get("analysis")) for q in qs)
    has_ev = sum(bool(q.get("evidence")) for q in qs)
    st = collections.Counter(q.get("status") for q in qs)
    return dict(total=len(qs), answer=has_ans, analysis=has_ana, evidence=has_ev, status=st, pct=lambda x: f"{x / n:.0%}")


def cmd_stats(b: Bank):
    c = coverage(b)
    print(f"考试 {len(b.exams)} 场 · 题目 {c['total']} 道 · 知识卡 {len(b.cards)} · 鉴别卡 {len(b.compares)} · 药物 {len(b.drugs)} · 词干 {len(b.stems)}")
    print(f"有答案 {c['answer']}（{c['pct'](c['answer'])}） · 有解析 {c['analysis']}（{c['pct'](c['analysis'])}） · 有教材出处 {c['evidence']}（{c['pct'](c['evidence'])}）")
    print("审核状态：" + "  ".join(f"{STATUS.get(k, k)} {v}" for k, v in c["status"].most_common()))
    cs = collections.Counter(c["meta"].get("review_status") for c in b.cards.values())
    print("知识卡状态：" + "  ".join(f"{k} {v}" for k, v in cs.most_common()))


# ------------------------------------------------------------------ 查看
def render_question(q, b: Bank, with_answer=True, link_base="../../") -> str:
    ex = q["_exam"]
    lines = [f"**{q['num']}. {q['stem']}**"]
    for i, s in enumerate(q.get("sub", []) or [], 1):
        lines.append(f"　（{i}）{s}")
    for k, v in (q.get("options") or {}).items():
        lines.append(f"　{k}. {v}")
    if q.get("recall"):
        lines.append(f"\n> 回忆者括注：{q['recall']}")
    if q.get("completeness") not in ("full", None):
        lines.append(f"\n> 题目完整度：{COMPLETENESS.get(q['completeness'])}")
    if with_answer:
        lines.append("")
        lines.append(f"<details><summary>答案与解析 · {STATUS.get(q.get('status'), q.get('status'))}</summary>\n")
        ans = full_answer(q, b.cards, b.compares)
        lines.append("**答案**\n\n" + (ans or "（待写）"))
        if q.get("analysis"):
            lines.append("\n**解析**\n\n" + str(q["analysis"]).strip())
        if q.get("kp"):
            lines.append("\n**知识点**：" + "、".join(f"[{b.cards[k]['meta']['title']}]({link_base}knowledge/cards/{k}.md)" for k in q["kp"] if k in b.cards))
        ev = q.get("evidence") or []
        lines.append("\n**教材出处**：" + ("；".join(f"{e['src']} {e['loc']}（{e['status']}）" for e in ev) if ev else "待检索标注（`python tools/annotate.py suggest " + q["id"] + "`）"))
        if q.get("note"):
            lines.append(f"\n**备注**：{q['note']}")
        lines.append("\n</details>")
    return "\n".join(lines)


def cmd_show(b: Bank, qid: str):
    q = b.qmap.get(qid)
    if not q:
        sys.exit(f"没有题目 {qid}")
    print(f"[{q['_exam']['title']}] {qid}\n")
    print(re.sub(r"</?details>|<summary>.*?</summary>", "", render_question(q, b)))


def cmd_find(b: Bank, words: list[str]):
    for q in b.questions:
        hay = " ".join([q["stem"], *map(str, q.get("sub", []) or []), *[b.cards[k]["meta"]["title"] for k in q.get("kp", []) if k in b.cards]])
        if all(w.lower() in hay.lower() for w in words):
            print(f"{q['id']:<26} {TYPES[q['type']][:4]:<6} {q['stem'][:50]}")


def cmd_fmt(b: Bank):
    for f in exam_files():
        d = load_yaml(f)
        write_exam(f, d)
    print(f"✓ 已规范 {len(exam_files())} 个文件")


# ------------------------------------------------------------------ docs/：GitHub 可读版
def cmd_docs(b: Bank):
    (DOCS / "exams").mkdir(parents=True, exist_ok=True)
    kq = b.kp_questions()
    cov = coverage(b)
    rows = []
    for e in b.exams:
        ex, qs = e["exam"], e.get("questions", [])
        n = len(qs)
        a = sum(bool(q.get("answer") or q.get("answer_ref")) for q in qs)
        ev = sum(bool(q.get("evidence")) for q in qs)
        rv = sum(q.get("status") in ("reviewed", "verified") for q in qs)
        types = "、".join(dict.fromkeys(q["section"] for q in qs))
        rows.append(f"| [{ex['title']}](exams/{ex['id']}.md) | {ex['cohort']} | {ex['major']} | {ex['kind']} | {n} | {types} | {a}/{n} | {ev}/{n} | {rv}/{n} |")
        body = [f"# {ex['title']}", "",
                f"> 来源：[{ex['source']['title']}]({ex['source']['url']})（{ex['source']['published']}，{ex['source']['account']}）· {ex['source']['license']}  ",
                f"> 正本：[`bank/exams/{ex['id']}.yaml`](../../bank/exams/{ex['id']}.yaml) · 原始回忆：[`bank/raw/{ex['id']}.md`](../../bank/raw/{ex['id']}.md)", ""]
        if ex.get("format"):
            body += ["| 题型 | 分值 |", "|---|---|"] + [f"| {s['section']} | {s.get('score', '—')} |" for s in ex["format"]] + [""]
        if ex.get("notes"):
            body += ["**回忆者备注**：" + "；".join(ex["notes"]), ""]
        cur = None
        for q in qs:
            if q.get("section") != cur:
                cur = q.get("section")
                body += [f"## {cur}", ""]
            body += [render_question(dict(q, _exam=ex), b), "", "---", ""]
        body.append(f"*本页由 `python tools/bank.py docs` 生成，请勿手改。*")
        (DOCS / "exams" / f"{ex['id']}.md").write_text("\n".join(body) + "\n", encoding="utf-8")

    by_ch = collections.defaultdict(list)
    for k, c in b.cards.items():
        by_ch[c["meta"]["chapter"]].append(k)
    kp_rows = []
    for k in sorted(b.cards, key=lambda k: (-len({q["_exam"]["id"] for q in kq[k]}), -len(kq[k]))):
        c = b.cards[k]
        exs = {q["_exam"]["id"] for q in kq[k]}
        if not exs:
            continue
        years = sorted({q["_exam"]["cohort"] for q in kq[k]})
        kp_rows.append(f"| [{c['meta']['title']}](../knowledge/cards/{k}.md) | {b.chapters[c['meta']['chapter']]['name']} | {len(exs)} | {len(kq[k])} | {years[0]}–{years[-1]} | {c['meta']['review_status']} |")
    ch_rows = []
    for ch, cinfo in b.chapters.items():
        ks = by_ch.get(ch, [])
        ch_rows.append(f"| {cinfo['name']} | " + "、".join(f"[{b.cards[k]['meta']['title']}](../knowledge/cards/{k}.md)" for k in sorted(ks, key=lambda k: -len(kq[k]))) + " |")
    cmp_rows = [f"- [{c['meta']['title']}](../knowledge/compare/{cid}.md)" for cid, c in b.compares.items()]
    st = cov["status"]
    readme = [
        "# 真题库总览", "",
        f"*由 `python tools/bank.py docs` 生成。* 共 **{len(b.exams)}** 场考试、**{cov['total']}** 道题；"
        f"有答案 {cov['answer']}（{cov['pct'](cov['answer'])}），有解析 {cov['analysis']}（{cov['pct'](cov['analysis'])}），"
        f"有教材出处 {cov['evidence']}（{cov['pct'](cov['evidence'])}）。审核状态：" + "，".join(f"{STATUS.get(k, k)} {v}" for k, v in st.most_common()) + "。", "",
        "## 1 按考试", "",
        "| 考试 | 年级 | 专业 | 类型 | 题数 | 题型 | 有答案 | 有出处 | 已审 |", "|---|---|---|---|---|---|---|---|---|", *rows, "",
        "## 2 知识点考频（按出现的考试场次排序）", "",
        "| 知识点 | 章节 | 考试场次 | 题数 | 年级跨度 | 卡片状态 |", "|---|---|---|---|---|---|", *kp_rows, "",
        "## 3 按章节浏览知识卡", "", "| 章节 | 知识卡（按考频） |", "|---|---|", *ch_rows, "",
        "## 4 鉴别卡", "", *cmp_rows, "",
    ]
    (DOCS / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(f"✓ docs/ 已更新：{len(b.exams)} 份试卷 + 总览")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("stats")
    sub.add_parser("fmt")
    sub.add_parser("docs")
    p = sub.add_parser("show"); p.add_argument("qid")
    p = sub.add_parser("find"); p.add_argument("words", nargs="+")
    a = ap.parse_args()
    b = Bank()
    if a.cmd == "check":
        err, warn = check(b)
        for w in warn:
            print("  !", w)
        for e in err:
            print("  ✗", e)
        print(f"{'✓' if not err else '✗'} 错误 {len(err)} · 警告 {len(warn)} · 考试 {len(b.exams)} · 题目 {len(b.questions)} · 知识卡 {len(b.cards)}")
        sys.exit(1 if err else 0)
    {"stats": cmd_stats, "fmt": cmd_fmt, "docs": cmd_docs}.get(a.cmd, lambda b: None)(b)
    if a.cmd == "show":
        cmd_show(b, a.qid)
    if a.cmd == "find":
        cmd_find(b, a.words)


if __name__ == "__main__":
    main()
