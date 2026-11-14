"""common.py — 共享的读写与解析：题库 YAML、知识卡 Markdown、引用解析。

所有工具都通过这里读写数据，保证：
  1. YAML 输出格式固定（键顺序、多行文本用 | 块），人工编辑与程序写回的 diff 都干净；
  2. 答案引用（answer_ref）只有一种解析方式；
  3. 校验规则集中在一处（bank.py check 与 CI 共用）。
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "bank"
EXAMS = BANK / "exams"
RAW = BANK / "raw"
KNOW = ROOT / "knowledge"
CARDS = KNOW / "cards"
COMPARE = KNOW / "compare"
REFERENCE = ROOT / "reference"

TYPES = {
    "definition": "名词解释", "fill_blank": "填空题", "single_choice": "单选题", "multi_choice": "多选题",
    "choice": "选择题（单/多选未区分）", "matching": "B型题（配伍）", "true_false": "判断题",
    "short_answer": "简答题", "essay": "问答/论述题", "case": "病例分析题", "experiment_design": "实验设计题",
}
STATUS = {"todo": "待写", "draft-ai": "AI 草稿", "draft": "人工草稿", "reviewed": "已审", "verified": "已核定"}
COMPLETENESS = {
    "full": "题目完整", "stem_with_hint": "题干+回忆者括注", "stem_only": "仅题干（无选项）",
    "topic_only": "仅考点", "image_only": "原文为截图，未转录", "lost": "回忆缺失",
}
EVIDENCE_STATUS = {"待核", "已核"}
KINDS = {"期中", "期末", "缓考", "实验"}

QUESTION_KEYS = ["id", "num", "section", "type", "score", "stem", "sub", "options", "recall", "completeness",
                 "answer", "answer_ref", "analysis", "kp", "evidence", "status", "reviewer", "note"]


# ------------------------------------------------------------------ YAML：固定格式输出
class _Dumper(yaml.SafeDumper):
    pass


def _str(dumper, s: str):
    style = "|" if "\n" in s else None
    if style:
        s = "\n".join(line.rstrip() for line in s.strip("\n").split("\n")) + "\n"
    return dumper.represent_scalar("tag:yaml.org,2002:str", s, style=style)


def _list(dumper, items):
    flow = items and all(isinstance(x, (str, int)) and "\n" not in str(x) for x in items) and sum(len(str(x)) + 2 for x in items) <= 90
    return dumper.represent_sequence("tag:yaml.org,2002:seq", items, flow_style=bool(flow))


_Dumper.add_representer(str, _str)
_Dumper.add_representer(list, _list)


def _clean(obj):
    """去掉空值（None / '' / [] / {}），让文件只留有内容的字段。"""
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items() if v not in (None, "", [], {})}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    return obj


def dump_yaml(obj) -> str:
    return yaml.dump(_clean(obj), Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=1000, indent=2)


def order_question(q: dict) -> dict:
    out = {k: q[k] for k in QUESTION_KEYS if k in q}
    out.update({k: v for k, v in q.items() if k not in out})
    return out


def write_exam(path: Path, data: dict) -> None:
    data = {"exam": data["exam"], "questions": [order_question(q) for q in data["questions"]]}
    head = ("# 本文件是真题库正本，可直接编辑。字段说明见 bank/SCHEMA.md；改完运行 python tools/bank.py check\n"
            "# 程序写回（annotate.py、bank.py fmt）会保持本格式。\n")
    path.write_text(head + dump_yaml(data), encoding="utf-8")


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def exam_files() -> list[Path]:
    return sorted(EXAMS.glob("*.yaml"), key=lambda p: (-int(p.stem[:2]) if p.stem[:2].isdigit() else 0, p.stem))


def load_exams() -> list[dict]:
    out = []
    for f in exam_files():
        d = load_yaml(f) or {}
        d["_file"] = f
        out.append(d)
    return out


# ------------------------------------------------------------------ 知识卡（Markdown + front matter）
def parse_card(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    meta, body = (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, text)
    sections, order, cur, title = {}, [], None, ""
    for line in body.splitlines():
        h1 = re.match(r"^#\s+(.+?)\s*$", line)
        h2 = re.match(r"^##\s+(.+?)\s*$", line)
        if h1 and not title:
            title = h1.group(1)
            continue
        if h2:
            cur = h2.group(1)
            order.append(cur)
            sections[cur] = []
            continue
        if cur:
            sections[cur].append(line)
    sections = {k: "\n".join(v).strip() for k, v in sections.items()}
    return dict(meta=meta, title=title, sections=sections, order=order, body=body.strip(), file=path)


def load_cards() -> dict[str, dict]:
    return {c["meta"]["id"]: c for c in (parse_card(f) for f in sorted(CARDS.glob("*.md")))}


def load_compares() -> dict[str, dict]:
    return {c["meta"]["id"]: c for c in (parse_card(f) for f in sorted(COMPARE.glob("*.md")))}


DEFAULT_SECTIONS = ["标准答案", "评分要点"]


def resolve_ref(ref: str, cards: dict, compares: dict) -> tuple[str, str]:
    """answer_ref 解析：
         first_pass                → 知识卡 first_pass 的【标准答案】【评分要点】（没有这两节则取全文）
         raas#ACEI降压机制          → 知识卡 raas 的该小节
         cmp:heparin_vs_warfarin   → 鉴别卡全文
       返回 (标题, Markdown 正文)；找不到时抛 KeyError。"""
    if ref.startswith("cmp:"):
        c = compares[ref[4:]]
        return c["meta"].get("title", ref), c["body"].split("\n", 1)[1].strip() if c["body"].startswith("# ") else c["body"]
    kid, _, sec = ref.partition("#")
    c = cards[kid]
    if sec:
        if sec not in c["sections"]:
            raise KeyError(f"{kid} 没有小节「{sec}」（现有：{'、'.join(c['order'])}）")
        return f"{c['meta']['title']} · {sec}", c["sections"][sec]
    parts = [s for s in DEFAULT_SECTIONS if s in c["sections"]] or c["order"]
    return c["meta"]["title"], "\n\n".join((f"**{s}**\n\n" if len(parts) > 1 else "") + c["sections"][s] for s in parts)


def full_answer(q: dict, cards: dict, compares: dict) -> str:
    """题目完整答案 = answer（本题特有）+ answer_ref 引用的知识卡内容。"""
    out = []
    if q.get("answer"):
        out.append(str(q["answer"]).strip())
    for r in q.get("answer_ref", []) or []:
        try:
            t, body = resolve_ref(r, cards, compares)
            out.append(f"〔引自知识卡：{t}〕\n{body}")
        except KeyError as e:
            out.append(f"〔引用失效：{r} — {e}〕")
    return "\n\n".join(out)


# ------------------------------------------------------------------ 自动标注：药物
def load_drugs():
    return load_yaml(KNOW / "drugs.yaml") or []


def load_stems():
    return load_yaml(KNOW / "stems.yaml") or []


def drug_patterns(drugs):
    pats = []
    for d in drugs:
        for n in [d["cn"], *d.get("aliases", [])]:
            if re.search(r"[A-Za-z]", n):
                pats.append((d["id"], re.compile(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])", re.I)))
            else:
                pats.append((d["id"], re.compile(re.escape(n))))
        pats.append((d["id"], re.compile(r"(?<![A-Za-z])" + re.escape(d["en"]) + r"(?![A-Za-z])", re.I)))
    return pats


def tag_text(text: str, pats) -> list[str]:
    """命中的 id；与更长匹配重叠的短匹配丢弃（避免“链霉素”同时命中“霉素”类泛称）。"""
    hits = [(m.start(), m.end(), k) for k, p in pats for m in p.finditer(text)]
    keep = [k for s, e, k in hits if not any(k2 != k and s2 < e and s < e2 and (e2 - s2) > (e - s) for s2, e2, k2 in hits)]
    return list(dict.fromkeys(keep))


def question_text(q: dict) -> str:
    opts = q.get("options") or {}
    return " ".join([str(q.get("stem", "")), *map(str, q.get("sub", []) or []), *map(str, opts.values()), str(q.get("recall", ""))])


def stems_for(en: str, stems) -> list[str]:
    words = re.findall(r"[a-z]+", en.lower())
    return [s["id"] for s in stems if any(re.search(s["regex"], w, re.I) for w in words)]
