#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D5 TOKEN ROTATION CAPTURE — 2026-10-02
User delivered rotated Notion token (ntn_2379…). PMRF v3.0 D5 = executed by user.
Phases:
  A) Full paginated search inventory (new token)
  B) Delta vs old index notion_raw/00_index.json (2026-09-26T23:48:03+0000)
  C) Accessibility test: 348 indexed-but-unexported pages (gap C14)
  D) Capture content: NEW + CHANGED + NEWLY_ACCESSIBLE (pages, blocks, databases)
  E) Manifest + summary
GET-only discipline (search/query are reads). No writes to Notion.
"""
import json, time, os, urllib.request, urllib.error, datetime, hashlib

TOKEN = "[REDACTED-NOTION-TOKEN]"
BASE = "https://api.notion.com/v1"
HDRS = {"Authorization": "Bearer " + TOKEN, "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
OLD_INDEX = "/home/z/my-project/notion_raw/00_index.json"
OLD_TEXT_DIR = "/home/z/my-project/notion_raw/text"
OUT = "/home/z/my-project/notion_raw_v2_20261002"
STAMP = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).strftime("%Y-%m-%dT%H:%M:%S+03:00")

def api(path, payload=None):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=HDRS, method="POST" if data else "GET")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r), r.status
        except urllib.error.HTTPError as e:
            code = e.code
            body = b""
            try: body = e.read()[:300]
            except Exception: pass
            if code == 429:
                time.sleep(2.0 * (attempt + 1)); continue
            return {"_http_error": code, "_body": body.decode(errors="replace")[:200]}, code
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return {"_error": "timeout"}, 0

def nid(s):  # normalize id
    return s.replace("-", "").lower()

def page_title(p):
    props = p.get("properties", {})
    for key, val in props.items():
        if isinstance(val, dict) and val.get("type") == "title":
            arr = val.get("title", [])
            if arr: return "".join(x.get("plain_text", "") for x in arr)
    return "(untitled)"

def db_title(d):
    return "".join(x.get("plain_text", "") for x in d.get("title", [])) or "(untitled db)"

def block_texts(blocks):
    out = []
    for b in blocks:
        t = b.get("type", "")
        spec = b.get(t, {}) if t else {}
        for key in ("rich_text", "caption", "description"):
            arr = spec.get(key, [])
            if arr and isinstance(arr, list):
                out.append("".join(x.get("plain_text", "") for x in arr))
    return out

def fetch_block_children(block_id, acc, depth=0):
    cursor = None
    while True:
        q = "?page_size=100" + (("&start_cursor=" + cursor) if cursor else "")
        d, st = api("/blocks/" + block_id + "/children" + q)
        if st != 200 or "_http_error" in d or "_error" in d:
            acc.append({"_fetch_error": st, "block": block_id})
            return
        for b in d.get("results", []):
            acc.append({"id": b.get("id"), "type": b.get("type"), "has_children": b.get("has_children"),
                        "text": block_texts([b]), "created": b.get("created_time"), "edited": b.get("last_edited_time")})
            if b.get("has_children") and depth < 6:
                fetch_block_children(b["id"], acc, depth + 1)
        if not d.get("has_more"): return
        cursor = d.get("next_cursor")

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

# ---------- Phase A: full inventory ----------
def phase_a():
    results, cursor, calls = [], None, 0
    while True:
        payload = {"page_size": 100}
        if cursor: payload["start_cursor"] = cursor
        d, st = api("/search", payload)
        calls += 1
        if st != 200 or "_http_error" in d or "_error" in d:
            print("SEARCH-ERROR", st, str(d)[:150]); break
        results += d.get("results", [])
        if not d.get("has_more"): break
        cursor = d.get("next_cursor")
        time.sleep(0.4)
    seen, inv = set(), {"pages": [], "databases": []}
    for r in results:
        i = nid(r.get("id", ""))
        if i in seen: continue
        seen.add(i)
        obj = r.get("object")
        rec = {"id": r.get("id"), "title": page_title(r) if obj == "page" else db_title(r),
               "last_edited": r.get("last_edited_time", ""), "created": r.get("created_time", ""),
               "url": r.get("url", "")}
        inv["pages" if obj == "page" else "databases"].append(rec)
    return inv, calls

# ---------- Phase B: delta vs old index ----------
def phase_b(inv):
    old = json.load(open(OLD_INDEX, encoding="utf-8"))
    old_pages = {nid(p["id"]): p for p in old.get("pages", [])}
    old_dbs = {nid(d["id"]): d for d in old.get("databases", [])}
    old_exported = {fn[:-4] for fn in os.listdir(OLD_TEXT_DIR) if fn.endswith(".txt")}
    delta = {"new_pages": [], "changed_pages": [], "unchanged_pages": 0,
             "new_dbs": [], "changed_dbs": [], "unchanged_dbs": 0, "gone_pages": [], "gone_dbs": []}
    for p in inv["pages"]:
        i = nid(p["id"]); o = old_pages.get(i)
        if o is None:
            delta["new_pages"].append(p); p["_class"] = "NEW"
        elif (p["last_edited"] or "") > (o.get("last_edited", "") or ""):
            delta["changed_pages"].append(p); p["_class"] = "CHANGED"
        else:
            delta["unchanged_pages"] += 1; p["_class"] = "UNCHANGED"
        old_pages.pop(i, None)
    for k, o in old_pages.items():
        delta["gone_pages"].append({"id": o.get("id"), "title": o.get("title"), "last_edited": o.get("last_edited")})
    for drec in inv["databases"]:
        i = nid(drec["id"]); o = old_dbs.get(i)
        if o is None:
            delta["new_dbs"].append(drec); drec["_class"] = "NEW"
        elif (drec["last_edited"] or "") > (o.get("last_edited", "") or ""):
            delta["changed_dbs"].append(drec); drec["_class"] = "CHANGED"
        else:
            delta["unchanged_dbs"] += 1; drec["_class"] = "UNCHANGED"
        old_dbs.pop(i, None)
    for k, o in old_dbs.items():
        delta["gone_dbs"].append({"id": o.get("id"), "title": o.get("title")})
    return delta, old_pages, old_exported

# ---------- Phase C: accessibility of 348 unexported ----------
def phase_c(old_index_pages, old_exported):
    unexported = [p for p in old_index_pages
                  if nid(p["id"]) not in old_exported and "_class" not in p]
    # old index pages list must be re-loaded raw (without _class): handled by caller passing copy
    res = {"total_unexported": len(unexported), "accessible": 0, "inaccessible": 0,
           "detail": []}
    for p in unexported:
        i = nid(p["id"])
        d, st = api("/pages/" + i)
        ok = (st == 200 and "_http_error" not in d and "_error" not in d)
        res["detail"].append({"id": p.get("id"), "title": p.get("title", ""), "last_edited": p.get("last_edited", ""), "http": st, "accessible": ok})
        if ok: res["accessible"] += 1
        else: res["inaccessible"] += 1
        time.sleep(0.3)
    return res, unexported

def main():
    os.makedirs(OUT + "/pages", exist_ok=True)
    os.makedirs(OUT + "/text", exist_ok=True)
    os.makedirs(OUT + "/databases", exist_ok=True)
    state_path = OUT + "/_state.json"
    if os.path.exists(state_path):
        st = json.load(open(state_path, encoding="utf-8"))
        inv = st["inv"]; delta = st["delta"]; acc = st["acc"]
        newly_accessible = st["newly_accessible"]
        calls = st["calls"]
        print("[resume] state loaded: pages", len(inv["pages"]), "| acc", acc["accessible"], "/", acc["total"])
    else:
        print("== PHASE A: full search inventory ==")
        inv, calls = phase_a()
        print("search calls:", calls, "| pages:", len(inv["pages"]), "| dbs:", len(inv["databases"]))
        print("== PHASE B: delta vs 2026-09-26 index ==")
        delta, old_pages_map, old_exported = phase_b(inv)
        print("NEW pages:", len(delta["new_pages"]), "| CHANGED:", len(delta["changed_pages"]),
              "| UNCHANGED:", delta["unchanged_pages"], "| GONE:", len(delta["gone_pages"]))
        print("NEW dbs:", len(delta["new_dbs"]), "| CHANGED dbs:", len(delta["changed_dbs"]),
              "| UNCHANGED dbs:", delta["unchanged_dbs"], "| GONE dbs:", len(delta["gone_dbs"]))
        # ---- Phase C: reload OLD index raw for unexported test ----
        old_raw = json.load(open(OLD_INDEX, encoding="utf-8"))
        old_raw_pages = old_raw.get("pages", [])
        old_exported2 = {fn[:-4] for fn in os.listdir(OLD_TEXT_DIR) if fn.endswith(".txt")}
        unexp = [p for p in old_raw_pages if nid(p["id"]) not in old_exported2]
        print("== PHASE C: accessibility of", len(unexp), "unexported (C14) ==")
        acc = {"total": len(unexp), "accessible": 0, "inaccessible": 0, "detail": []}
        newly_accessible = []
        for p in unexp:
            i = nid(p["id"])
            d, st2 = api("/pages/" + i)
            ok = (st2 == 200 and "_http_error" not in d and "_error" not in d)
            acc["detail"].append({"id": p.get("id"), "title": p.get("title", ""), "last_edited": p.get("last_edited", ""), "http": st2})
            if ok:
                acc["accessible"] += 1
                newly_accessible.append(p)
            else:
                acc["inaccessible"] += 1
            time.sleep(0.25)
        print("accessible:", acc["accessible"], "| inaccessible:", acc["inaccessible"])
        save_json(state_path, {"inv": inv, "delta": delta, "acc": acc,
                               "newly_accessible": newly_accessible, "calls": calls})
    # ---- Phase D: capture NEW + CHANGED + NEWLY_ACCESSIBLE ----
    print("== PHASE D: content capture ==")
    capture_targets = []
    for p in delta["new_pages"] + delta["changed_pages"]:
        capture_targets.append((nid(p["id"]), p["title"], p["_class"], p["last_edited"]))
    for p in newly_accessible:
        capture_targets.append((nid(p["id"]), p.get("title", "(n/a)"), "NEWLY_ACCESSIBLE", p.get("last_edited", "")))
    captured, failed, skipped = 0, 0, 0
    for pid, title, reason, edited in capture_targets:
        if os.path.exists(OUT + "/pages/" + pid + ".json"):
            skipped += 1; continue
        pg, st1 = api("/pages/" + pid)
        if st1 != 200 or "_http_error" in pg:
            failed += 1; continue
        blocks = []
        fetch_block_children(pid, blocks)
        texts = [t for b in blocks for t in (b.get("text") or [])]
        save_json(OUT + "/pages/" + pid + ".json",
                  {"capture_reason": reason, "captured_at": STAMP, "title": title,
                   "last_edited": edited, "page": pg, "block_count": len(blocks), "blocks": blocks})
        with open(OUT + "/text/" + pid + ".txt", "w", encoding="utf-8") as f:
            f.write(title + "\n" + "=" * 40 + "\n" + "\n".join(texts))
        captured += 1
        time.sleep(0.3)
    db_captured = 0
    for drec in delta["new_dbs"] + delta["changed_dbs"]:
        i = nid(drec["id"])
        if os.path.exists(OUT + "/databases/" + i + ".json"):
            skipped += 1; continue
        schema, st1 = api("/databases/" + i)
        if st1 != 200 or "_http_error" in schema:
            failed += 1; continue
        rows, cursor = [], None
        while True:
            q = {"page_size": 100}
            if cursor: q["start_cursor"] = cursor
            d, st2 = api("/databases/" + i + "/query", q)
            if st2 != 200 or "_http_error" in d: break
            rows += d.get("results", [])
            if not d.get("has_more"): break
            cursor = d.get("next_cursor"); time.sleep(0.3)
        save_json(OUT + "/databases/" + i + ".json",
                  {"capture_reason": drec["_class"], "title": drec["title"], "schema": schema, "row_count": len(rows), "rows": rows})
        db_captured += 1
        time.sleep(0.3)
    print("pages captured:", captured, "| dbs captured:", db_captured, "| failed:", failed, "| skipped(done):", skipped)
    # ---- Phase E: manifest ----
    manifest = {
        "generated_at": STAMP, "operation": "D5 token rotation capture",
        "token": {"prefix": TOKEN[:10] + "…", "workspace": "مساحة عمل Ahmed Ahmed",
                  "workspace_id": "c8558a07-79e8-8108-b685-0003b8f22ec9",
                  "owner": "Ahmed Ahmed (tasahom.1998@gmail.com)", "bot": "Z.ai"},
        "old_capture": {"index": OLD_INDEX, "generated_at": "2026-09-26T23:48:03+0000",
                        "pages_indexed": 894, "pages_exported": 546, "databases": 31},
        "inventory": {"pages": len(inv["pages"]), "databases": len(inv["databases"]), "search_calls": calls},
        "delta": {k: (len(v) if isinstance(v, list) else v) for k, v in delta.items()},
        "delta_detail": {"new_pages": delta["new_pages"], "changed_pages": delta["changed_pages"],
                          "new_dbs": delta["new_dbs"], "changed_dbs": delta["changed_dbs"],
                          "gone_pages": delta["gone_pages"], "gone_dbs": delta["gone_dbs"]},
        "c14_accessibility": {"total_unexported": acc["total"], "accessible": acc["accessible"],
                              "inaccessible": acc["inaccessible"], "detail": acc["detail"]},
        "db_classification_note": "old index db entries carry no last_edited field — 'changed_dbs'=all is a comparison artifact; full DB re-pull = fresh snapshot, not verified edit signal",
        "capture": {"pages_captured": captured, "dbs_captured": db_captured, "failed": failed, "skipped_resume": skipped},
    }
    save_json(OUT + "/00_delta_index.json", manifest)
    # console digest for report
    print("\n=== DIGEST ===")
    print("NEW PAGES:")
    for p in delta["new_pages"][:40]: print("  +", p["last_edited"], "|", p["title"][:70])
    print("CHANGED PAGES:")
    for p in delta["changed_pages"][:40]: print("  *", p["last_edited"], "|", p["title"][:70])
    print("NEW DBS:", [d["title"][:50] for d in delta["new_dbs"]])
    print("CHANGED DBS:", [d["title"][:50] for d in delta["changed_dbs"]])
    print("GONE PAGES:", len(delta["gone_pages"]), "->", [g.get("title", "")[:40] for g in delta["gone_pages"][:15]])

if __name__ == "__main__":
    main()
