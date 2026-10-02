#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phase 0b — Targeted READ-ONLY dump
- Dumps supplier-intelligence relevant content pages (full block trees)
- Queries all databases (read-op) + fetches row-page content where has_children
- Idempotent: skips files already dumped. READ-ONLY: GET + query only.
"""
import json, os, time, sys, urllib.request, urllib.error

import os as _os
def _load_token():
    tok = _os.environ.get('NOTION_TOKEN', '')
    if tok:
        return tok
    env_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '.env')
    try:
        for line in open(env_path, encoding='utf-8'):
            if line.strip().startswith('NOTION_TOKEN='):
                return line.strip().split('=', 1)[1].strip().strip(chr(34)).strip(chr(39))
    except FileNotFoundError:
        pass
    raise SystemExit('NOTION_TOKEN missing: set env var or add NOTION_TOKEN=... to .env')
TOKEN = _load_token()
BASE = "https://api.notion.com/v1"
HDRS = {"Authorization": "Bearer " + TOKEN, "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
RAW = "/home/z/my-project/notion_raw"
PAGES_DIR = os.path.join(RAW, "pages"); TEXT_DIR = os.path.join(RAW, "text"); DB_DIR = os.path.join(RAW, "databases")
for d in (PAGES_DIR, TEXT_DIR, DB_DIR): os.makedirs(d, exist_ok=True)

SLEEP = 0.30

def req(method, path, payload=None, retries=3):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BASE + path, data=data, headers=HDRS, method=method)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:600]
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2 * (attempt + 1)); continue
            return {"_error": e.code, "_body": body, "_path": path}
        except Exception as ex:
            if attempt < retries - 1: time.sleep(2); continue
            return {"_error": "conn", "_body": str(ex), "_path": path}
    return {"_error": "unreachable", "_path": path}

def plain_text(block):
    parts = []; btype = block.get("type", "")
    b = block.get(btype, {}) if isinstance(block.get(btype), dict) else {}
    for key in ("rich_text", "title", "caption", "url", "expression", "code"):
        val = b.get(key)
        if isinstance(val, str) and val: parts.append(val)
        elif isinstance(val, list):
            for rt in val:
                if isinstance(rt, dict):
                    t = rt.get("plain_text", "")
                    if t: parts.append(t)
    if btype == "to_do": parts.insert(0, "[x] " if b.get("checked") else "[ ] ")
    return " ".join(parts).strip()

def get_children(block_id):
    out, cursor = [], None
    while True:
        path = "/blocks/{}/children?page_size=100".format(block_id)
        if cursor: path += "&start_cursor=" + cursor
        res = req("GET", path)
        if "_error" in res: return out, res
        out += res.get("results", [])
        if not res.get("has_more"): break
        cursor = res.get("next_cursor"); time.sleep(SLEEP)
    full = []
    for blk in out:
        full.append(blk)
        if blk.get("has_children"):
            kids, err = get_children(blk["id"])
            for k in kids: k["_depth"] = blk.get("_depth", 0) + 1
            full += kids
            time.sleep(SLEEP)
    return full, None

def render_text(title, blocks):
    lines = ["# " + title]
    for b in blocks:
        t = plain_text(b)
        if t:
            lines.append("  " * b.get("_depth", 0) + t)
    return "\n".join(lines)

def dump_page(page_meta, force=False):
    pid8 = page_meta["id"].replace("-", "")
    jf = os.path.join(PAGES_DIR, pid8 + ".json")
    tf = os.path.join(TEXT_DIR, pid8 + ".txt")
    if not force and os.path.exists(jf) and os.path.getsize(jf) > 10:
        return "skip"
    blocks, err = get_children(page_meta["id"])
    with open(jf, "w", encoding="utf-8") as f:
        json.dump({"page": page_meta, "blocks": blocks}, f, ensure_ascii=False, indent=1)
    with open(tf, "w", encoding="utf-8") as f:
        f.write(render_text(page_meta.get("title", "(untitled)"), blocks))
    return "ok" if err is None else "err:" + str(err.get("_error"))

def db_rows(db_id):
    rows, cursor = [], None
    while True:
        payload = {"page_size": 100}
        if cursor: payload["start_cursor"] = cursor
        res = req("POST", "/databases/{}/query".format(db_id), payload)
        if "_error" in res: return rows, res
        rows += res.get("results", [])
        if not res.get("has_more"): break
        cursor = res.get("next_cursor"); time.sleep(SLEEP)
    return rows, None

def main():
    idx = json.load(open(os.path.join(RAW, "00_index.json")))
    # --- target content pages by title match ---
    WANT_EXACT = [
        "المواصفة التشغيلية — البحث العميق العالمي عن الموردين ومصادرهم",
        "Canonical Registry — Prompt & Evolution",
        "ChatGPT Workspace — Review & Analysis",
        "Central Automation Runtime — سجل التنفيذ والبنية الحالية — 2026-09-26",
        "مرجع حاكم — قاعدة بيانات أرخص موردي ومتاجر المنتجات والخدمات الرقمية",
        "Claude Sonnet 5 Workspace — Research & Drafts",
        "🔁 Operating Protocol — Notion-First ChatGPT ↔ Claude Relay",
        "التسويق العميق",
        "📄 v4.1 Candidate — Exact Prompt Text",
        "🧪 Pre-Claude Repair Audit — v4.0 → v4.1 Candidate",
        "🧠 Knowledge Operating System — Master Hub",
        "مرجع نطاق العمل — Deep Marketing Conversation — 2026-09-26",
        "RSH18 — Claim-Level Evidence Register",
        "RSH2 — Cross-Layer Mechanism Matrix",
        "مرجع هندسة نظام الأتمتة المستمرة 24/7 — قالب قابل لإعادة الاستخدام",
        "RSH-1 — Overlap / Gap Matrix Working Artifact",
        "RSH-1 — Overlap / Gap Matrix — Corrected v2",
        "Operational Reconciliation — 2026-09-26",
        "معجم البحث العميق والمتعدد المسارات — Supplier Discovery Lexicon",
        "سجل تاريخي — تفاوض موردي الخدمات الرقمية | Stack Vault Support",
        "مرجع حاكم — محرك العصف الذهني والتحليل النقدي الصارم",
        "مصدر — cheapest_digital_products_suppliers_database.md",
        "مصدر — global_digital_products_database.md",
        "مصدر — progress.md",
        "مصدر — global_digital_suppliers_database.md",
        "مشروع بيع الخدمات الرقمية عبر Telegram — Payment Architecture & ProdSe",
    ]
    WANT_PREFIX = [
        "🧬 Prompt Development History",
        "🧭 Supplier Intelligence Prompt Lab",
    ]
    targets, seen = [], set()
    for p in idx["pages"]:
        t = p.get("title", "")
        if p["id"] in seen: continue
        if t in WANT_EXACT or any(t.startswith(w) for w in WANT_PREFIX):
            targets.append(p); seen.add(p["id"])
    # untitled workspace pages (2)
    for p in idx["pages"]:
        if not p.get("title") and p["parent"].get("type") == "workspace" and p["id"].startswith("3e758a07"):
            if p["id"] not in seen: targets.append(p); seen.add(p["id"])
    print("TARGET_PAGES:", len(targets))
    for p in targets:
        st = dump_page(p)
        print("PAGE:", st, "|", (p.get("title") or "(untitled)")[:60])
        time.sleep(SLEEP)

    # --- all databases: bulk query + row content if has_children ---
    for d in idx["databases"]:
        did8 = d["id"].replace("-", "")
        rows, err = db_rows(d["id"])
        with open(os.path.join(DB_DIR, did8 + ".json"), "w", encoding="utf-8") as f:
            json.dump({"database": d, "rows": rows, "row_query_error": err}, f, ensure_ascii=False, indent=1)
        nchild = sum(1 for r in rows if r.get("has_children"))
        print("DB:", (d.get("title") or "(untitled)")[:50], "| rows:", len(rows), "| rows_with_content:", nchild)
        # fetch content of row-pages that have blocks (key for supplier/interaction DBs)
        for r in rows:
            if r.get("has_children"):
                rid8 = r["id"].replace("-", "")
                jf = os.path.join(PAGES_DIR, "row_" + rid8 + ".json")
                if os.path.exists(jf) and os.path.getsize(jf) > 10: continue
                blocks, e2 = get_children(r["id"])
                with open(jf, "w", encoding="utf-8") as f:
                    json.dump({"row": {"id": r["id"], "url": r.get("url")}, "blocks": blocks}, f, ensure_ascii=False, indent=1)
                with open(os.path.join(TEXT_DIR, "row_" + rid8 + ".txt"), "w", encoding="utf-8") as f:
                    f.write(render_text("(row)", blocks))
                time.sleep(SLEEP)
    print("TARGETED_DUMP_COMPLETE")

if __name__ == "__main__":
    main()
