#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PMRF v3.0 — Phase 3 Batch B (v2): CONTENT EXTRACTION — notion_raw/
Actual export structures discovered:
  databases/ : {"database": {id,title,url,properties...}, "rows": [...], "row_query_error": ...}
  pages/     : {"page": {id,title,url,...}, "blocks": [...]}
  text/      : plain markdown (Arabic governing references)
Output: research/pmrf_v3_build/extract_notion.json
"""
import os, json
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ROOT = "/home/z/my-project"
BUILD = os.path.join(ROOT, "research", "pmrf_v3_build")
TZ = timezone(timedelta(hours=3))
RUN_TS = datetime.now(TZ).isoformat(timespec="seconds")

out = {"databases": {}, "pages": {}, "text": {}}
agg = defaultdict(lambda: {"files": 0, "inspected": 0, "bytes": 0})

# --- databases ---
dbdir = os.path.join(ROOT, "notion_raw", "databases")
for fn in sorted(os.listdir(dbdir)):
    fp = os.path.join(dbdir, fn)
    if not os.path.isfile(fp): continue
    sz = os.path.getsize(fp)
    rec = {"size": sz, "inspected": False}
    agg["databases"]["files"] += 1; agg["databases"]["bytes"] += sz
    try:
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        db = data.get("database", {})
        rows = data.get("rows", [])
        rec.update({
            "db_id": db.get("id"),
            "db_title": (db.get("title") or "")[:130],
            "db_url": (db.get("url") or "")[:120],
            "rows_count": len(rows),
            "row_query_error": data.get("row_query_error"),
            "db_properties": list((db.get("properties") or {}).keys())[:30],
            "inspected": True,
        })
        if rows and isinstance(rows[0], dict):
            rec["row_schema"] = list(rows[0].keys())[:25]
            # sample row titles/values
            rec["sample_rows"] = [{k: str(v)[:60] for k, v in list(r.items())[:8]} for r in rows[:5]]
        agg["databases"]["inspected"] += 1
    except Exception as e:
        rec["error"] = str(e)[:120]
    out["databases"][fn] = rec

# --- pages ---
pgdir = os.path.join(ROOT, "notion_raw", "pages")
for fn in sorted(os.listdir(pgdir)):
    fp = os.path.join(pgdir, fn)
    if not os.path.isfile(fp): continue
    sz = os.path.getsize(fp)
    rec = {"size": sz, "inspected": False}
    agg["pages"]["files"] += 1; agg["pages"]["bytes"] += sz
    try:
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        pg = data.get("page", {})
        blocks = data.get("blocks", [])
        rec.update({
            "page_id": pg.get("id"),
            "title": (pg.get("title") or "")[:140],
            "url": (pg.get("url") or "")[:120],
            "blocks_count": len(blocks),
            "created": pg.get("created_time") or pg.get("created"),
            "last_edited": pg.get("last_edited_time") or pg.get("last_edited"),
            "parent": str(pg.get("parent", ""))[:120],
            "properties": list((pg.get("properties") or {}).keys())[:25],
            "inspected": True,
        })
        agg["pages"]["inspected"] += 1
    except Exception as e:
        rec["error"] = str(e)[:120]
    out["pages"][fn] = rec

# --- text (plain markdown) ---
txdir = os.path.join(ROOT, "notion_raw", "text")
for fn in sorted(os.listdir(txdir)):
    fp = os.path.join(txdir, fn)
    if not os.path.isfile(fp): continue
    sz = os.path.getsize(fp)
    rec = {"size": sz, "inspected": False}
    agg["text"]["files"] += 1; agg["text"]["bytes"] += sz
    try:
        with open(fp, encoding="utf-8", errors="replace") as f:
            head = f.read(800)
        lines = head.split("\n")
        rec.update({
            "h1_or_first_line": (lines[0] if lines else "")[:140],
            "first_paragraph": next((l for l in lines[1:] if l.strip()), "")[:180],
            "inspected": True,
        })
        agg["text"]["inspected"] += 1
    except Exception as e:
        rec["error"] = str(e)[:120]
    out["text"][fn] = rec

result = {
    "run": "PMRF v3.0 — Batch B v2: notion_raw/ content extraction (matched real export schema)",
    "generated_at": RUN_TS,
    "per_subdir": {k: dict(v) for k, v in agg.items()},
    **out,
}
with open(os.path.join(BUILD, "extract_notion.json"), "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print(f"RUN {RUN_TS}")
for k, v in agg.items():
    print(f"  {k:12s} files={v['files']:5d} inspected={v['inspected']:5d} {v['bytes']:>10,} B")
print("\n== databases ==")
for fn, rec in out["databases"].items():
    print(f"  {rec.get('db_title','?')[:60]:60s} rows={rec.get('rows_count','?'):>3} err={bool(rec.get('row_query_error'))}")
print("\n== pages: first 20 by title ==")
for i, (fn, rec) in enumerate(sorted(out["pages"].items(), key=lambda x: x[1].get("title") or "")):
    if i >= 20: break
    print(f"  {str(rec.get('title'))[:95]:95s} blocks={rec.get('blocks_count')}")
print("\n== text/ first 10 ==")
for i, (fn, rec) in enumerate(out["text"].items()):
    if i >= 10: break
    print(f"  {rec.get('h1_or_first_line','')[:110]}")
