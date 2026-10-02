#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phase 0 — Notion READ-ONLY State Audit
Hard rule: READ-ONLY. Allowed endpoints = search (POST, read-op), blocks retrieve
(GET), databases query (POST, read-op). NO PATCH/PUT/DELETE anywhere.
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
HDRS = {
    "Authorization": "Bearer " + TOKEN,
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
RAW = "/home/z/my-project/notion_raw"
PAGES_DIR = os.path.join(RAW, "pages")
TEXT_DIR = os.path.join(RAW, "text")
DB_DIR = os.path.join(RAW, "databases")
for d in (PAGES_DIR, TEXT_DIR, DB_DIR):
    os.makedirs(d, exist_ok=True)

def req(method, path, payload=None, retries=3):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BASE + path, data=data, headers=HDRS, method=method)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:800]
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2 * (attempt + 1)); continue
            return {"_error": e.code, "_body": body, "_path": path}
        except Exception as ex:
            if attempt < retries - 1:
                time.sleep(2); continue
            return {"_error": "conn", "_body": str(ex), "_path": path}
    return {"_error": "unreachable", "_path": path}

def plain_text(block):
    """Extract plain text from a block's rich text fields."""
    parts = []
    btype = block.get("type", "")
    b = block.get(btype, {}) if isinstance(block.get(btype), dict) else {}
    for key in ("rich_text", "title", "caption", "url", "expression", "code"):
        val = b.get(key)
        if isinstance(val, str) and val:
            parts.append(val)
        elif isinstance(val, list):
            for rt in val:
                if isinstance(rt, dict):
                    t = rt.get("plain_text", "")
                    if t: parts.append(t)
    if b.get("checked") is not None and btype in ("to_do",):
        parts.append("[x] " if b.get("checked") else "[ ] ")
    return " ".join(parts).strip()

def get_children(block_id, depth=0):
    """GET /blocks/{id}/children — paginated, recursive for has_children."""
    out, cursor = [], None
    while True:
        path = "/blocks/{}/children?page_size=100".format(block_id)
        if cursor: path += "&start_cursor=" + cursor
        res = req("GET", path)
        if "_error" in res:
            return out, res
        out += res.get("results", [])
        if not res.get("has_more"): break
        cursor = res.get("next_cursor")
        time.sleep(0.35)
    # recurse into children-of-children (toggles, columns, synced blocks...)
    full = []
    for blk in out:
        full.append(blk)
        if blk.get("has_children"):
            kids, err = get_children(blk["id"], depth + 1)
            if err is None:
                for k in kids:
                    k["_depth"] = depth + 1
                full += kids
            time.sleep(0.3)
    return full, None

def page_title(page):
    props = page.get("properties", {})
    for k, v in props.items():
        if v.get("type") == "title":
            ts = v.get("title", [])
            return "".join(t.get("plain_text", "") for t in ts)
    return "(untitled)"

def render_text(title, blocks):
    lines = ["# " + title]
    for b in blocks:
        t = plain_text(b)
        if t:
            marker = "  " * (b.get("_depth", 0))
            lines.append(marker + ("- " if b.get("type") in ("bulleted_list_item","numbered_list_item","to_do") else "") + t)
    return "\n".join(lines)

def main():
    # 1) enumerate everything the integration can see
    results, cursor, pages, dbs = [], None, [], []
    while True:
        payload = {"page_size": 100}
        if cursor: payload["start_cursor"] = cursor
        res = req("POST", "/search", payload)
        if "_error" in res:
            print("SEARCH_ERROR", json.dumps(res, ensure_ascii=False)[:500]); sys.exit(1)
        batch = res.get("results", [])
        results += batch
        if not res.get("has_more"): break
        cursor = res.get("next_cursor")
        time.sleep(0.35)
    for obj in results:
        if obj.get("object") == "page":
            pages.append(obj)
        elif obj.get("object") == "database":
            dbs.append(obj)
    index = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "counts": {"total": len(results), "pages": len(pages), "databases": len(dbs)},
        "pages": [{"id": p["id"], "title": page_title(p),
                   "last_edited": p.get("last_edited_time", ""),
                   "url": p.get("url", ""), "parent": p.get("parent", {})}
                  for p in pages],
        "databases": [{"id": d["id"],
                       "title": "".join(t.get("plain_text", "") for t in d.get("title", [])),
                       "url": d.get("url", ""), "parent": d.get("parent", {})}
                      for d in dbs],
    }
    with open(os.path.join(RAW, "00_index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print("INDEX: pages={} databases={}".format(len(pages), len(dbs)))

    # 2) dump every page's blocks
    ok, failed = 0, []
    for p in pages:
        blocks, err = get_children(p["id"])
        if err is not None:
            failed.append({"id": p["id"], "title": page_title(p), "err": str(err)[:200]})
        pid = p["id"].replace("-", "")
        with open(os.path.join(PAGES_DIR, pid + ".json"), "w", encoding="utf-8") as f:
            json.dump({"page": {"id": p["id"], "title": page_title(p), "url": p.get("url")},
                       "blocks": blocks}, f, ensure_ascii=False, indent=1)
        with open(os.path.join(TEXT_DIR, pid + ".txt"), "w", encoding="utf-8") as f:
            f.write(render_text(page_title(p), blocks))
        ok += 1
        time.sleep(0.35)
    print("PAGES_DUMPED: ok={} failed={}".format(ok, len(failed)))
    if failed:
        with open(os.path.join(RAW, "00_failed.json"), "w", encoding="utf-8") as f:
            json.dump(failed, f, ensure_ascii=False, indent=2)

    # 3) query databases (read-only)
    for d in dbs:
        did = d["id"].replace("-", "")
        rows, cursor = [], None
        while True:
            payload = {"page_size": 100}
            if cursor: payload["start_cursor"] = cursor
            res = req("POST", "/databases/{}/query".format(d["id"]), payload)
            if "_error" in res:
                rows.append({"_error": res}); break
            rows += res.get("results", [])
            if not res.get("has_more"): break
            cursor = res.get("next_cursor")
            time.sleep(0.35)
        with open(os.path.join(DB_DIR, did + ".json"), "w", encoding="utf-8") as f:
            json.dump({"database": {"id": d["id"],
                                     "title": "".join(t.get("plain_text","") for t in d.get("title",[]))},
                       "rows": rows}, f, ensure_ascii=False, indent=1)
        print("DB_DUMPED: {} rows={}".format(d.get("title", "")[:40] if isinstance(d.get("title"), str) else "", len(rows)))
    print("PHASE0_DUMP_COMPLETE")

if __name__ == "__main__":
    main()
