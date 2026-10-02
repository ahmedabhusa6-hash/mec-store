#!/usr/bin/env python3
"""
Notion READ-ONLY index — Supplier Intelligence project.
Enumerates all pages/databases accessible to the integration.
NO writes of any kind. Token comes from env var only.
"""
import os, json, time, urllib.request, urllib.error

TOKEN = os.environ.get("NOTION_TOKEN", "")
BASE = "https://api.notion.com/v1"
OUT_DIR = "/home/z/my-project/scripts/notion"
os.makedirs(OUT_DIR, exist_ok=True)

def api(method, path, body=None, retries=4):
    headers = {
        "Authorization": "Bearer " + TOKEN,
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(BASE + path, method=method, headers=headers, data=data)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = float(e.headers.get("Retry-After", 2 ** attempt))
                time.sleep(min(wait, 30))
                continue
            detail = ""
            try:
                detail = e.read().decode()[:300]
            except Exception:
                pass
            return {"__error": e.code, "__detail": detail}
        except Exception:
            time.sleep(1.5 ** attempt)
    return {"__error": "max_retries"}

def search_all():
    results, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        r = api("POST", "/search", body)
        if "__error" in r:
            return results, r
        results.extend(r.get("results", []))
        if not r.get("has_more") or not r.get("next_cursor"):
            break
        cursor = r["next_cursor"]
        time.sleep(0.35)
    return results, None

def page_title(page):
    props = page.get("properties", {})
    for key, val in props.items():
        if val.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in val.get("title", []))
    return "(untitled)"

def db_title(db):
    return "".join(t.get("plain_text", "") for t in db.get("title", []))

def parent_desc(obj):
    p = obj.get("parent", {})
    t = p.get("type", "")
    if t == "workspace":
        return "workspace"
    if t == "database_id":
        return "db:" + p.get("database_id", "")[:8]
    if t == "page_id":
        return "page:" + p.get("page_id", "")[:8]
    return t or "?"

def main():
    if not TOKEN:
        print("NO TOKEN"); return
    results, err = search_all()
    pages = [o for o in results if o.get("object") == "page" and not o.get("archived")]
    dbs = [o for o in results if o.get("object") == "database" and not o.get("archived")]
    index = {"databases": [], "pages": []}
    for d in dbs:
        index["databases"].append({
            "id": d["id"], "title": db_title(d), "url": d.get("url", ""),
            "parent": parent_desc(d), "last_edited": d.get("last_edited_time", ""),
        })
    for p in pages:
        index["pages"].append({
            "id": p["id"], "title": page_title(p), "url": p.get("url", ""),
            "parent": parent_desc(p), "last_edited": p.get("last_edited_time", ""),
            "created": p.get("created_time", ""),
        })
    index["databases"].sort(key=lambda x: x["title"])
    index["pages"].sort(key=lambda x: (x["parent"], x["title"]))
    with open(os.path.join(OUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print("TOTAL objects:", len(results), "| pages:", len(pages), "| databases:", len(dbs))
    if err:
        print("SEARCH ERROR:", err)
    print("\n=== DATABASES (%d) ===" % len(index["databases"]))
    for d in index["databases"]:
        print("[DB] %s | parent=%s | edited=%s\n     %s" % (d["title"], d["parent"], d["last_edited"], d["url"]))
    print("\n=== TOP-LEVEL PAGES (parent=workspace) ===")
    for p in index["pages"]:
        if p["parent"] == "workspace":
            print("[PG] %s | edited=%s\n     %s" % (p["title"], p["last_edited"], p["url"]))
    print("\n=== DB-ROW / CHILD PAGES (grouped by parent) ===")
    from collections import defaultdict
    groups = defaultdict(list)
    for p in index["pages"]:
        if p["parent"] != "workspace":
            groups[p["parent"]].append(p)
    for parent, items in sorted(groups.items()):
        print("--- parent %s : %d pages" % (parent, len(items)))
        for p in items[:60]:
            print("   * %s (edited %s)" % (p["title"][:90], p["last_edited"]))
        if len(items) > 60:
            print("   ... and %d more" % (len(items) - 60))

if __name__ == "__main__":
    main()
