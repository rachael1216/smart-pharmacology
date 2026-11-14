#!/usr/bin/env python3
"""export.py — 把真题库导出成任意需要的格式（输出到 exports/，该目录不入库）。

  python tools/export.py json                 # 完整数据（答案引用已展开）→ exports/pharm-bank.json
  python tools/export.py jsonl                # 一行一题，便于喂给大模型 / 向量库
  python tools/export.py csv                  # 一行一题的表格（Excel 可直接打开，UTF-8 BOM）
  python tools/export.py xlsx                 # 多工作表：题目 / 知识点考频 / 药物 / 构词法 / 易混药名
  python tools/export.py sqlite               # 关系库：exam / question / kp / question_kp / evidence / drug / stem
  python tools/export.py md --mode paper      # 试卷版（无答案），每场考试一个 .md
  python tools/export.py md --mode key        # 答案解析版
  python tools/export.py docx --mode key      # Word（需 pandoc）
  python tools/export.py anki                 # Anki 导入用 TSV（正面题干，背面答案+解析，带标签）
  python tools/export.py html                 # 单文件离线题库浏览器

筛选（任意格式通用）：
  --exam 24-pharm-final  --cohort 2024  --major 临床医学（五年制）  --kind 期末
  --type definition,essay  --kp first_pass,raas  --status reviewed,verified  --lang en
示例：只导出“已审”的心血管大题做 Word：
  python tools/export.py docx --mode key --type essay,short_answer --status reviewed,verified
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bank import Bank, render_question  # noqa: E402
from common import COMPLETENESS, ROOT, STATUS, TYPES, drug_patterns, full_answer, question_text, stems_for, tag_text  # noqa: E402

OUT = ROOT / "exports"


# ------------------------------------------------------------------ 统一的“展开后”记录
def records(b: Bank, a) -> list[dict]:
    pats = drug_patterns(b.drugs)
    dmap = {d["id"]: d for d in b.drugs}
    out = []
    for q in b.questions:
        ex = q["_exam"]
        if a.exam and ex["id"] not in a.exam.split(","):
            continue
        if a.cohort and str(ex["cohort"]) not in a.cohort.split(","):
            continue
        if a.major and ex["major"] not in a.major.split(","):
            continue
        if a.kind and ex["kind"] not in a.kind.split(","):
            continue
        if a.type and q["type"] not in a.type.split(","):
            continue
        if a.status and q.get("status") not in a.status.split(","):
            continue
        if a.kp and not set(a.kp.split(",")) & set(q.get("kp", []) or []):
            continue
        text = question_text(q)
        lang = "en" if re.search(r"[A-Za-z]{4,}", q["stem"]) else "zh"
        if a.lang and lang != a.lang:
            continue
        drugs = tag_text(text, pats)
        out.append(dict(
            id=q["id"], exam=ex["id"], exam_title=ex["title"], cohort=ex["cohort"], major=ex["major"], kind=ex["kind"],
            num=q["num"], section=q.get("section"), type=q["type"], type_cn=TYPES[q["type"]],
            stem=q["stem"], sub=q.get("sub", []) or [], options=q.get("options") or {}, recall=q.get("recall"),
            completeness=q["completeness"], answer=full_answer(q, b.cards, b.compares), answer_short=q.get("answer"),
            answer_ref=q.get("answer_ref", []) or [], analysis=q.get("analysis"), kp=q.get("kp", []) or [],
            kp_titles=[b.cards[k]["meta"]["title"] for k in q.get("kp", []) or [] if k in b.cards],
            drugs=[dict(id=d, cn=dmap[d]["cn"], en=dmap[d]["en"], stems=stems_for(dmap[d]["en"], b.stems)) for d in drugs],
            evidence=q.get("evidence", []) or [], status=q.get("status"), lang=lang, source_url=ex["source"]["url"],
            _q=q, _ex=ex))
    return out


def strip(r: dict) -> dict:
    return {k: v for k, v in r.items() if not k.startswith("_")}


def name(a, base: str, ext: str) -> Path:
    OUT.mkdir(exist_ok=True)
    tag = "-".join(x for x in [a.exam, a.cohort, a.type, a.kp, a.status] if x).replace(",", "+")
    return OUT / f"{base}{('-' + tag) if tag else ''}.{ext}"


# ------------------------------------------------------------------ 各格式
def ex_json(b, rs, a):
    p = name(a, "pharm-bank", "json")
    data = dict(meta=dict(exported=date.today().isoformat(), count=len(rs), status_levels=STATUS, types=TYPES),
                questions=[strip(r) for r in rs],
                knowledge=[dict(id=k, **{x: c["meta"].get(x) for x in ("title", "title_en", "chapter", "review_status", "textbook_pages")},
                                sections=c["sections"]) for k, c in b.cards.items()],
                compare=[dict(id=k, title=c["meta"]["title"], markdown=c["body"]) for k, c in b.compares.items()],
                drugs=b.drugs, stems=b.stems)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def ex_jsonl(b, rs, a):
    p = name(a, "pharm-bank", "jsonl")
    with p.open("w", encoding="utf-8") as f:
        for r in rs:
            f.write(json.dumps(strip(r), ensure_ascii=False) + "\n")
    return p


FLAT = ["id", "cohort", "major", "kind", "num", "type_cn", "stem", "sub", "options", "recall", "completeness",
        "answer", "analysis", "kp_titles", "drugs", "evidence", "status", "source_url"]


def flat(r):
    return [("\n".join(r[c]) if c in ("sub", "kp_titles") else
             "\n".join(f"{k}. {v}" for k, v in r[c].items()) if c == "options" else
             "、".join(f"{d['cn']}({d['en']})" for d in r[c]) if c == "drugs" else
             "\n".join(f"{e['src']} {e['loc']}（{e['status']}）" for e in r[c]) if c == "evidence" else r[c]) for c in FLAT]


def ex_csv(b, rs, a):
    p = name(a, "pharm-bank", "csv")
    with p.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(FLAT)
        w.writerows(flat(r) for r in rs)
    return p


def ex_xlsx(b, rs, a):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook()

    def sheet(ws, header, rows, widths):
        ws.append(header)
        for r in rows:
            ws.append(r)
        for i, w in enumerate(widths):
            ws.column_dimensions[chr(65 + i)].width = w
        for c in ws[1]:
            c.font, c.fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F4E79")
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes, ws.auto_filter.ref = "A2", ws.dimensions

    ws = wb.active
    ws.title = "题目"
    sheet(ws, FLAT, [flat(r) for r in rs], [24, 7, 14, 6, 5, 10, 40, 30, 24, 20, 12, 60, 40, 24, 24, 30, 9, 20])
    kq = defaultdict(set)
    for r in rs:
        for k in r["kp"]:
            kq[k].add(r["exam"])
    sheet(wb.create_sheet("知识点考频"), ["id", "知识点", "英文", "章节", "考试场次", "卡片状态", "教材页码"],
          [[k, c["meta"]["title"], c["meta"].get("title_en"), b.chapters[c["meta"]["chapter"]]["name"], len(kq[k]),
            c["meta"]["review_status"], c["meta"].get("textbook_pages")] for k, c in sorted(b.cards.items(), key=lambda x: -len(kq[x[0]]))],
          [22, 28, 28, 24, 9, 10, 24])
    sheet(wb.create_sheet("药物"), ["id", "中文", "英文", "类别", "知识卡", "别名", "词干"],
          [[d["id"], d["cn"], d["en"], d["cls"], d["kp"], "、".join(d.get("aliases", [])), "、".join(stems_for(d["en"], b.stems))] for d in b.drugs],
          [22, 14, 24, 28, 20, 20, 20])
    ex_by_stem = defaultdict(list)
    for d in b.drugs:
        for s in stems_for(d["en"], b.stems):
            ex_by_stem[s].append(f"{d['cn']} {d['en']}")
    sheet(wb.create_sheet("构词法"), ["词干", "位置", "中文译字", "类别", "机制", "易错提醒", "例药"],
          [[s["stem"], s["position"], s["cn"], s["cls"], s["mechanism"], s["pitfalls"], "；".join(ex_by_stem[s["id"]])] for s in b.stems],
          [16, 8, 12, 26, 32, 50, 50])
    from common import KNOW, load_yaml
    sheet(wb.create_sheet("易混药名"), ["组", "药物", "鉴别"],
          [[c["id"], " / ".join(c["drugs"]), c["tip"]] for c in load_yaml(KNOW / "confusables.yaml")], [8, 30, 90])
    p = name(a, "pharm-bank", "xlsx")
    wb.save(p)
    return p


def ex_sqlite(b, rs, a):
    p = name(a, "pharm-bank", "sqlite")
    if p.exists():
        p.unlink()
    con = sqlite3.connect(p)
    c = con.cursor()
    c.executescript("""
    CREATE TABLE exam(id TEXT PRIMARY KEY, title TEXT, cohort INT, major TEXT, kind TEXT, source_url TEXT);
    CREATE TABLE question(id TEXT PRIMARY KEY, exam_id TEXT REFERENCES exam(id), num INT, section TEXT, type TEXT, stem TEXT,
        sub TEXT, options TEXT, recall TEXT, completeness TEXT, answer TEXT, analysis TEXT, status TEXT, lang TEXT);
    CREATE TABLE kp(id TEXT PRIMARY KEY, title TEXT, title_en TEXT, chapter TEXT, review_status TEXT, textbook_pages TEXT, markdown TEXT);
    CREATE TABLE question_kp(question_id TEXT, kp_id TEXT, PRIMARY KEY(question_id, kp_id));
    CREATE TABLE evidence(question_id TEXT, src TEXT, loc TEXT, quote TEXT, status TEXT, by TEXT);
    CREATE TABLE drug(id TEXT PRIMARY KEY, cn TEXT, en TEXT, cls TEXT, kp_id TEXT, stems TEXT);
    CREATE TABLE question_drug(question_id TEXT, drug_id TEXT);
    CREATE TABLE stem(id TEXT PRIMARY KEY, stem TEXT, position TEXT, regex TEXT, cn TEXT, cls TEXT, mechanism TEXT, pitfalls TEXT);
    """)
    J = lambda x: json.dumps(x, ensure_ascii=False)  # noqa: E731
    for e in {r["exam"]: r["_ex"] for r in rs}.values():
        c.execute("INSERT INTO exam VALUES(?,?,?,?,?,?)", (e["id"], e["title"], e["cohort"], e["major"], e["kind"], e["source"]["url"]))
    for r in rs:
        c.execute("INSERT INTO question VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (r["id"], r["exam"], r["num"], r["section"], r["type"], r["stem"],
                  J(r["sub"]), J(r["options"]), r["recall"], r["completeness"], r["answer"], r["analysis"], r["status"], r["lang"]))
        c.executemany("INSERT INTO question_kp VALUES(?,?)", [(r["id"], k) for k in r["kp"]])
        c.executemany("INSERT INTO evidence VALUES(?,?,?,?,?,?)", [(r["id"], e["src"], e["loc"], e.get("quote"), e["status"], e.get("by")) for e in r["evidence"]])
        c.executemany("INSERT INTO question_drug VALUES(?,?)", [(r["id"], d["id"]) for d in r["drugs"]])
    for k, cd in b.cards.items():
        m = cd["meta"]
        c.execute("INSERT INTO kp VALUES(?,?,?,?,?,?,?)", (k, m["title"], m.get("title_en"), m["chapter"], m["review_status"], m.get("textbook_pages"), cd["body"]))
    for d in b.drugs:
        c.execute("INSERT INTO drug VALUES(?,?,?,?,?,?)", (d["id"], d["cn"], d["en"], d["cls"], d["kp"], J(stems_for(d["en"], b.stems))))
    for s in b.stems:
        c.execute("INSERT INTO stem VALUES(?,?,?,?,?,?,?,?)", (s["id"], s["stem"], s["position"], s["regex"], s["cn"], s["cls"], s["mechanism"], s["pitfalls"]))
    c.executescript("""
    CREATE VIEW v_kp_frequency AS SELECT kp.id, kp.title, COUNT(DISTINCT q.exam_id) AS exams, COUNT(*) AS questions
      FROM question_kp qk JOIN kp ON kp.id = qk.kp_id JOIN question q ON q.id = qk.question_id GROUP BY kp.id ORDER BY exams DESC, questions DESC;
    CREATE VIEW v_need_evidence AS SELECT q.id, q.stem FROM question q WHERE NOT EXISTS (SELECT 1 FROM evidence e WHERE e.question_id = q.id);
    """)
    con.commit()
    con.close()
    return p


def md_exam(b, rs_exam, mode) -> str:
    ex = rs_exam[0]["_ex"]
    head = [f"# {ex['title']}{'（答案解析版）' if mode == 'key' else ''}", "",
            f"> 来源：{ex['source']['title']}（{ex['source']['published']}，{ex['source']['account']}）", ""]
    body, cur = [], None
    for r in rs_exam:
        if r["section"] != cur:
            cur = r["section"]
            body += [f"## {cur}", ""]
        txt = render_question(r["_q"] | {"_exam": ex}, b, with_answer=(mode == "key"))
        txt = re.sub(r"</?details>|<summary>.*?</summary>\n?", "", txt)
        txt = re.sub(r"\]\((\.\./)+knowledge/", "](https://github.com/rachael1216/smart-pharmacology/blob/main/knowledge/", txt)
        body += [txt, ""]
    return "\n".join(head + body)


def ex_md(b, rs, a, to_docx=False):
    by = defaultdict(list)
    for r in rs:
        by[r["exam"]].append(r)
    d = name(a, f"md-{a.mode}", "d")
    d = d.with_suffix("")
    d.mkdir(parents=True, exist_ok=True)
    files = []
    for eid, rr in by.items():
        f = d / f"{eid}{'-key' if a.mode == 'key' else ''}.md"
        f.write_text(md_exam(b, rr, a.mode), encoding="utf-8")
        files.append(f)
    if a.merge:
        m = d / f"合集{'-答案解析' if a.mode == 'key' else '-试卷'}.md"
        m.write_text("\n\n\\newpage\n\n".join(f.read_text(encoding="utf-8") for f in files), encoding="utf-8")
        files = [m]
    if to_docx:
        if not shutil.which("pandoc"):
            sys.exit("docx 需要 pandoc：brew install pandoc / winget install JohnMacFarlane.Pandoc")
        outs = []
        for f in files:
            o = f.with_suffix(".docx")
            subprocess.run(["pandoc", str(f), "-o", str(o)], check=True)
            outs.append(o)
        return d if len(outs) > 1 else outs[0]
    return d if len(files) > 1 else files[0]


def ex_anki(b, rs, a):
    p = name(a, "pharm-anki", "txt")
    with p.open("w", encoding="utf-8") as f:
        f.write("#separator:tab\n#html:true\n#tags column:3\n")
        for r in rs:
            if r["completeness"] in ("image_only", "lost") or not r["answer"]:
                continue
            front = r["stem"] + "".join(f"<br>（{i}）{s}" for i, s in enumerate(r["sub"], 1)) + "".join(f"<br>{k}. {v}" for k, v in r["options"].items())
            back = r["answer"].replace("\n", "<br>") + (("<hr>" + str(r["analysis"]).replace("\n", "<br>")) if r["analysis"] else "")
            tags = " ".join([f"年级::{r['cohort']}", f"题型::{r['type_cn']}", *[f"知识点::{t}" for t in r["kp_titles"]]]).replace("（", "_").replace("）", "")
            f.write("\t".join(x.replace("\t", " ") for x in [front, back, tags]) + "\n")
    return p


def ex_html(b, rs, a):
    tpl = (ROOT / "tools" / "viewer.html").read_text(encoding="utf-8")
    data = dict(questions=[strip(r) for r in rs], cards={k: dict(title=c["meta"]["title"], chapter=c["meta"]["chapter"], status=c["meta"]["review_status"],
                body=c["body"]) for k, c in b.cards.items()}, compares={k: dict(title=c["meta"]["title"], body=c["body"]) for k, c in b.compares.items()},
                chapters=b.chapters, stems=b.stems, drugs=b.drugs, exported=date.today().isoformat())
    p = name(a, "pharm-bank", "html")
    p.write_text(tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")), encoding="utf-8")
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fmt", choices=["json", "jsonl", "csv", "xlsx", "sqlite", "md", "docx", "anki", "html", "all"])
    ap.add_argument("--mode", choices=["paper", "key"], default="key", help="md/docx：paper 试卷版（无答案）/ key 答案解析版")
    ap.add_argument("--merge", action="store_true", help="md/docx：合并为一个文件")
    for f in ("exam", "cohort", "major", "kind", "type", "kp", "status", "lang"):
        ap.add_argument(f"--{f}")
    a = ap.parse_args()
    b = Bank()
    rs = records(b, a)
    if not rs:
        sys.exit("筛选后没有题目。")
    fns = dict(json=ex_json, jsonl=ex_jsonl, csv=ex_csv, xlsx=ex_xlsx, sqlite=ex_sqlite, anki=ex_anki, html=ex_html,
               md=lambda b, rs, a: ex_md(b, rs, a), docx=lambda b, rs, a: ex_md(b, rs, a, to_docx=True))
    for fmt in (["json", "jsonl", "csv", "xlsx", "sqlite", "anki", "html"] if a.fmt == "all" else [a.fmt]):
        p = fns[fmt](b, rs, a)
        print(f"✓ {fmt:<6} {len(rs)} 题 → {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
