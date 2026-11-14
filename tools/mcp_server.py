#!/usr/bin/env python3
"""smart-pharmacology MCP 服务（stdio，仅依赖标准库 + PyYAML）。

  Tools     搜题、看题、教材检索、出处候选、导出、校验
  Prompts   总菜单 + .agents/skills 下的各 skill
  Resources 数据规范、AGENTS.md、各 skill 原文

接入 Claude Code：claude mcp add smart-pharm -- python3 /绝对路径/tools/mcp_server.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".agents" / "skills"
PROTOCOL, VERSION = "2024-11-05", "0.1.0"


def run(script: str, args: list[str], timeout: int = 300) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools" / script), *map(str, args)], cwd=ROOT,
                       capture_output=True, text=True, timeout=timeout, encoding="utf8", errors="replace")
    return p.returncode, (p.stdout + (("\n" + p.stderr) if p.stderr.strip() else "")).strip()


def skill_names():
    return sorted(d.name for d in SKILLS.iterdir() if (d / "SKILL.md").exists()) if SKILLS.exists() else []


def skill_text(name):
    f = SKILLS / name / "SKILL.md"
    if not f.exists():
        raise ValueError(f"没有这个 skill：{name}。可用：{', '.join(skill_names())}")
    return f.read_text(encoding="utf8")


def skill_desc(name):
    m = re.search(r"(?m)^description:\s*(.+)$", skill_text(name))
    return m.group(1).strip() if m else name


S = {"type": "string"}


def obj(props, req=None):
    return {"type": "object", "properties": props, "required": req or []}


def t_export(a):
    args = [a.get("fmt", "json")]
    for k in ("mode", "exam", "cohort", "major", "kind", "type", "kp", "status", "lang"):
        if a.get(k):
            args += [f"--{k}", str(a[k])]
    return run("export.py", args, 600)


TOOLS = {
    "pharm_menu": ("展示功能菜单（新会话先调用）。", obj({}), lambda a: (0, (SKILLS / "pharm-menu" / "menu.md").read_text(encoding="utf8"))),
    "pharm_skill": ("读取一个 skill 的完整步骤；不给 name 则列出全部。", obj({"name": S}),
                    lambda a: (0, skill_text(a["name"]) if a.get("name") else "\n".join(f"- {n}：{skill_desc(n)}" for n in skill_names()))),
    "bank_find": ("按关键词搜历年真题（题干、小问、知识点标题），返回题号列表。", obj({"words": {"type": "string", "description": "空格分隔的关键词"}}, ["words"]),
                  lambda a: run("bank.py", ["find", *a["words"].split()])),
    "bank_show": ("查看一道题：题干、答案（知识卡引用已展开）、解析、知识点、教材出处。", obj({"qid": S}, ["qid"]), lambda a: run("bank.py", ["show", a["qid"]])),
    "bank_stats": ("题库覆盖率：答案、解析、出处、审核状态。", obj({}), lambda a: run("bank.py", ["stats"])),
    "bank_check": ("校验全部数据（编辑后必跑）。", obj({}), lambda a: run("bank.py", ["check"])),
    "rag_search": ("检索教材/讲义/本地资料/知识卡/真题（BM25，返回片段与页码）。authoritative=true 时只查教材、讲义与本地资料。",
                   obj({"query": S, "k": {"type": "integer"}, "corpus": S, "authoritative": {"type": "boolean"}, "full": {"type": "boolean"}}, ["query"]),
                   lambda a: run("rag.py", ["search", *a["query"].split(), "-k", str(a.get("k", 5))] + (["-c", a["corpus"]] if a.get("corpus") else [])
                                 + (["--authoritative"] if a.get("authoritative") else []) + (["--full"] if a.get("full") else []))),
    "annotate_suggest": ("为一道题检索教材出处候选（只查教材/讲义/本地资料）。", obj({"qid": S, "k": {"type": "integer"}}, ["qid"]),
                         lambda a: run("annotate.py", ["suggest", a["qid"], "-k", str(a.get("k", 5))])),
    "annotate_add": ("把出处写入题目 evidence（status 待核）。pick 为 suggest 结果序号；或给 src/loc/quote 手填。",
                     obj({"qid": S, "pick": {"type": "array", "items": {"type": "integer"}}, "src": S, "loc": S, "quote": S}, ["qid"]),
                     lambda a: run("annotate.py", ["add", a["qid"], *(["--pick", *map(str, a["pick"])] if a.get("pick") else
                                                                      ["--src", a.get("src", ""), "--loc", a.get("loc", ""), "--quote", a.get("quote", "")])])),
    "export": ("导出题库：fmt=json/jsonl/csv/xlsx/sqlite/md/docx/anki/html；可按 exam/cohort/major/kind/type/kp/status/lang 筛选；md/docx 的 mode=paper|key。",
               obj({"fmt": S, "mode": S, "exam": S, "cohort": S, "major": S, "kind": S, "type": S, "kp": S, "status": S, "lang": S}, ["fmt"]), t_export),
}

RESOURCES = {
    "pharm://schema": ("真题库字段规范", ROOT / "bank" / "SCHEMA.md"),
    "pharm://agents": ("协作规则", ROOT / "AGENTS.md"),
    "pharm://overview": ("真题库总览", ROOT / "docs" / "README.md"),
}


def reply(i, result=None, error=None):
    m = {"jsonrpc": "2.0", "id": i, **({"error": error} if error else {"result": result})}
    sys.stdout.write(json.dumps(m, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(m):
    method, i, p = m.get("method"), m.get("id"), m.get("params") or {}
    if i is None:
        return
    try:
        if method == "initialize":
            reply(i, {"protocolVersion": p.get("protocolVersion", PROTOCOL), "capabilities": {"tools": {}, "prompts": {}, "resources": {}},
                      "serverInfo": {"name": "smart-pharm", "version": VERSION},
                      "instructions": "复旦（上医）药理学真题库与学伴。答题与写解析前先 rag_search（authoritative=true）取教材原文与页码；没有教材依据时标注“待核”。"})
        elif method == "ping":
            reply(i, {})
        elif method == "tools/list":
            reply(i, {"tools": [{"name": n, "description": d, "inputSchema": s} for n, (d, s, _) in TOOLS.items()]})
        elif method == "tools/call":
            name, args = p.get("name"), p.get("arguments") or {}
            if name not in TOOLS:
                return reply(i, error={"code": -32602, "message": f"未知工具 {name}"})
            try:
                rc, out = TOOLS[name][2](args)
                reply(i, {"content": [{"type": "text", "text": out or "(无输出)"}], "isError": rc != 0})
            except Exception as e:  # noqa: BLE001
                reply(i, {"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}], "isError": True})
        elif method == "prompts/list":
            reply(i, {"prompts": [{"name": n, "description": skill_desc(n)} for n in skill_names()]})
        elif method == "prompts/get":
            reply(i, {"description": p.get("name"), "messages": [{"role": "user", "content": {"type": "text", "text": skill_text(p.get("name"))}}]})
        elif method == "resources/list":
            rs = [{"uri": u, "name": n, "mimeType": "text/markdown"} for u, (n, _) in RESOURCES.items()]
            rs += [{"uri": f"pharm://skill/{n}", "name": n, "mimeType": "text/markdown"} for n in skill_names()]
            reply(i, {"resources": rs})
        elif method == "resources/read":
            uri = p.get("uri", "")
            text = RESOURCES[uri][1].read_text(encoding="utf8") if uri in RESOURCES else skill_text(uri.rsplit("/", 1)[1]) if uri.startswith("pharm://skill/") else None
            if text is None:
                return reply(i, error={"code": -32602, "message": f"未知资源 {uri}"})
            reply(i, {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": text}]})
        else:
            reply(i, error={"code": -32601, "message": f"未实现 {method}"})
    except Exception as e:  # noqa: BLE001
        reply(i, error={"code": -32603, "message": f"{type(e).__name__}: {e}"})


def main():
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    for line in sys.stdin:
        if line.strip():
            try:
                handle(json.loads(line))
            except json.JSONDecodeError:
                reply(None, error={"code": -32700, "message": "parse error"})


if __name__ == "__main__":
    main()
