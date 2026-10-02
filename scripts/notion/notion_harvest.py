#!/usr/bin/env python3
"""
Notion READ-ONLY content harvest — Supplier Intelligence project.
- Re-runs search, saves RAW results (raw_search.json) with FULL parent IDs
- Builds full-ID tree, isolates project cluster precisely
- Fetches block content (recursive, depth-limited) for project pages
- Queries project databases (Version Registry, Decision Log, Interaction Archive)
- Reads governing reference page + its children + source pages
NO writes to Notion. Token from env only.
"""
import os, json, time, urllib.request, urllib.error

TOKEN = os.environ.get("NOTION_TOKEN", "")
BASE = "https://api.notion.com/v1"
OUT = "/home/z/my-project/scripts/notion"
PAGES_DIR = os.path.join(OUT, "pages")
os.makedirs(PAGES_DIR, exist_ok=True)

def api(method, path, body=None, retries=4):
    headers = {"Authorization": "Bearer " + TOKEN,
               "Notion-Version": "2022-06-28",
               "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(BASE + path, method=method, headers=headers, data=data)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = float(e.headers.get("Retry-After", 2 ** attempt))
                time.sleep(min(wait, 30)); continue
            detail = ""
            try: detail = e.read().decode()[:200]
            except Exception: pass
            return {"__error": e.code, "__detail": detail}
        except Exception:
            time.sleep(1.5 ** attempt)
    return {"__error": "max_retries"}

def search_all():
    results, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor: body["start_cursor"] = cursor
        r = api("POST", "/search", body)
        if "__error" in r: break
        results.extend(r.get("results", []))
        if not r.get("has_more") or not r.get("next_cursor"): break
        cursor = r["next_cursor"]
        time.sleep(0.35)
    return results

def page_title(page):
    for key, val in page.get("properties", {}).items():
        if val.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in val.get("title", []))
    return "(untitled)"

def rich_text_md(rt_list):
    parts = []
    for rt in rt_list or []:
        t = rt.get("plain_text", "")
        href = rt.get("href")
        ann = rt.get("annotations", {})
        if ann.get("bold"): t = "**" + t + "**"
        if ann.get("italic"): t = "*" + t + "*"
        if ann.get("code"): t = "`" + t + "`"
        if href and t.strip():
            t = "[%s](%s)" % (t, href)
        parts.append(t)
    return "".join(parts)

def block_to_md(block, depth):
    bt = block.get("type", "")
    b = block.get(bt, {}) or {}
    md = ""
    prefix = "  " * depth
    if bt == "paragraph":
        md = prefix + rich_text_md(b.get("rich_text"))
    elif bt.startswith("heading_"):
        lvl = int(bt[-1])
        md = prefix + "#" * lvl + " " + rich_text_md(b.get("rich_text"))
    elif bt in ("bulleted_list_item",):
        md = prefix + "- " + rich_text_md(b.get("rich_text"))
    elif bt in ("numbered_list_item",):
        md = prefix + "1. " + rich_text_md(b.get("rich_text"))
    elif bt == "to_do":
        ck = "x" if b.get("checked") else " "
        md = prefix + "- [%s] %s" % (ck, rich_text_md(b.get("rich_text")))
    elif bt == "toggle":
        md = prefix + "▶ " + rich_text_md(b.get("rich_text"))
    elif bt == "code":
        lang = b.get("language", "")
        md = prefix + "```" + lang + "\n" + rich_text_md(b.get("rich_text")) + "\n" + prefix + "```"
    elif bt == "quote":
        md = prefix + "> " + rich_text_md(b.get("rich_text"))
    elif bt == "callout":
        icon = (b.get("icon") or {}).get("emoji", "")
        md = prefix + "> 💬" + icon + " " + rich_text_md(b.get("rich_text"))
    elif bt == "divider":
        md = prefix + "---"
    elif bt == "child_page":
        md = prefix + "[[CHILD PAGE: %s | id=%s]]" % (b.get("title", ""), block.get("id", ""))
    elif bt == "child_database":
        md = prefix + "[[CHILD DATABASE: %s | id=%s]]" % (b.get("title", ""), block.get("id", ""))
    elif bt == "table":
        md = prefix + "[TABLE id=%s]" % block.get("id", "")
    elif bt == "table_row":
        cells = [rich_text_md(c) for c in b.get("cells", [])]
        md = prefix + "| " + " | ".join(cells) + " |"
    elif bt in ("embed", "bookmark", "link_preview"):
        md = prefix + "[EMBED %s]" % (b.get("url", "") or rich_text_md(b.get("caption")))
    elif bt == "image":
        cap = rich_text_md(b.get("caption"))
        url = ""
        for k in ("file", "external"):
            if k in b and b[k]: url = b[k].get("url", ""); break
        md = prefix + "[IMAGE %s %s]" % (cap, url[:120])
    elif bt == "column_list" or bt == "column":
        md = prefix + "[%s]" % bt.upper()
    else:
        rt = b.get("rich_text") if isinstance(b, dict) else None
        md = prefix + ("[%s] %s" % (bt.upper(), rich_text_md(rt) if rt else ""))
    has_children = block.get("has_children", False)
    return md, has_children

def fetch_blocks(page_id, max_depth=3):
    lines = []
    def walk(block_id, depth):
        if depth > max_depth: return
        cursor = None
        while True:
            path = "/blocks/%s/children?page_size=100" % block_id
            if cursor: path += "&start_cursor=" + cursor
            r = api("GET", path)
            if "__error" in r:
                lines.append("  " * depth + "!! ERROR fetching children of %s: %s" % (block_id[:8], r))
                return
            for blk in r.get("results", []):
                md, has_ch = block_to_md(blk, depth)
                if md.strip(): lines.append(md)
                if has_ch and blk.get("type") not in ("child_page", "child_database"):
                    walk(blk["id"], depth + 1)
                elif has_ch and blk.get("type") in ("child_page", "child_database"):
                    pass  # handled separately
            if not r.get("has_more") or not r.get("next_cursor"): break
            cursor = r["next_cursor"]
            time.sleep(0.35)
    walk(page_id, 0)
    return "\n".join(lines)

def props_to_md(page):
    lines = []
    for key, val in page.get("properties", {}).items():
        t = val.get("type", "")
        if t == "title":
            v = rich_text_md(val.get("title"))
        elif t == "rich_text":
            v = rich_text_md(val.get("rich_text"))
        elif t in ("select",):
            v = (val.get("select") or {}).get("name", "")
        elif t == "status":
            v = (val.get("status") or {}).get("name", "")
        elif t == "multi_select":
            v = ", ".join(x.get("name", "") for x in val.get("multi_select", []))
        elif t == "date":
            d = val.get("date") or {}
            v = (d.get("start", "") or "") + (("~" + d["end"]) if d.get("end") else "")
        elif t == "checkbox":
            v = "☑" if val.get("checkbox") else "☐"
        elif t == "url":
            v = val.get("url", "") or ""
        elif t == "number":
            v = str(val.get("number", ""))
        elif t == "people":
            v = ", ".join((p.get("name") or p.get("id", "")[:8]) for p in val.get("people", []))
        elif t == "relation":
            v = "→%d related" % len(val.get("relation", []))
        else:
            v = "(%s)" % t
        if v and v.strip() and v != "(%s)" % t:
            lines.append("- **%s**: %s" % (key, v))
    return "\n".join(lines)

def query_db(db_id, max_rows=200):
    rows, cursor = [], None
    while True:
        body = {"page_size": 100}
        if cursor: body["start_cursor"] = cursor
        r = api("POST", "/databases/%s/query" % db_id, body)
        if "__error" in r: return rows, r
        rows.extend(r.get("results", []))
        if not r.get("has_more") or not r.get("next_cursor") or len(rows) >= max_rows: break
        cursor = r["next_cursor"]
        time.sleep(0.35)
    return rows, None

def get_page(pid):
    return api("GET", "/pages/" + pid)

def save_page_doc(title, page_id, url, body_md, props_md=""):
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:80].strip() or page_id[:8]
    fn = os.path.join(PAGES_DIR, safe + ".md")
    with open(fn, "w", encoding="utf-8") as f:
        f.write("# %s\n\n> id=%s | url=%s\n\n" % (title, page_id, url))
        if props_md: f.write("## Properties\n%s\n\n" % props_md)
        f.write("## Content\n%s\n" % body_md)
    return fn

def main():
    if not TOKEN:
        print("NO TOKEN"); return
    results = search_all()
    with open(os.path.join(OUT, "raw_search.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False)
    pages = {p["id"]: p for p in results if p.get("object") == "page" and not p.get("archived")}
    dbs = {d["id"]: d for d in results if d.get("object") == "database" and not d.get("archived")}
    print("raw objects: %d pages, %d dbs" % (len(pages), len(dbs)))

    manifest = []
    def harvest_page(pid, label, read_children_pages=True, note=""):
        p = pages.get(pid) or get_page(pid)
        if p is None or "__error" in p:
            print("  !! cannot fetch page %s (%s)" % (pid[:8], label)); return
        title = page_title(p)
        body = fetch_blocks(pid)
        fn = save_page_doc(title or label, pid, p.get("url", ""), body)
        manifest.append({"label": label, "title": title, "id": pid, "file": fn, "note": note})
        print("  + [%s] %s → %s (%d chars)" % (label, title[:60], os.path.basename(fn), len(body)))
        # collect child pages/dbs found in blocks
        child_pages, child_dbs = [], []
        cursor = None
        while True:
            path = "/blocks/%s/children?page_size=100" % pid
            if cursor: path += "&start_cursor=" + cursor
            r = api("GET", path)
            if "__error" in r: break
            for blk in r.get("results", []):
                if blk.get("type") == "child_page":
                    child_pages.append((blk["id"], blk["child_page"].get("title", "")))
                elif blk.get("type") == "child_database":
                    child_dbs.append((blk["id"], blk["child_database"].get("title", "")))
            if not r.get("has_more") or not r.get("next_cursor"): break
            cursor = r["next_cursor"]; time.sleep(0.35)
        return p, child_pages, child_dbs

    # --- locate targets by title across all pages/dbs
    def find_page_by_title(substr_list, exact=False):
        for pid, p in pages.items():
            t = page_title(p)
            for s in substr_list:
                if (s.lower() in t.lower()) if not exact else (t.strip() == s):
                    return pid, t
        return None, None

    print("\n== A. Governing reference page + children ==")
    gov_id, gov_t = find_page_by_title(["قاعدة بيانات أرخص موردي"])
    gov_children_pages, gov_children_dbs = [], []
    if gov_id:
        p, cps, cdbs = harvest_page(gov_id, "GOVERNING")
        gov_children_pages, gov_children_dbs = cps or [], cdbs or []
        print("   child pages: %d | child dbs: %d" % (len(gov_children_pages), len(gov_children_dbs)))
        for cid, ct in gov_children_dbs:
            print("   - child DB: %s (id=%s)" % (ct, cid[:13]))
        for cid, ct in gov_children_pages[:40]:
            print("   - child page: %s" % ct[:70])

    print("\n== B. Supplier Intelligence cluster (parent = project hub) ==")
    # project hub = parent of 'Prompt Development History'
    hub_id = None
    for pid, p in pages.items():
        if page_title(p).startswith("Prompt Development History"):
            par = p.get("parent", {})
            if par.get("type") == "page_id": hub_id = par["page_id"]
    print("   project hub id:", (hub_id or "?")[:13])
    if hub_id:
        # hub page itself
        hp = pages.get(hub_id) or get_page(hub_id)
        if hp and "__error" not in hp:
            body = fetch_blocks(hub_id)
            fn = save_page_doc("HUB " + page_title(hp), hub_id, hp.get("url", ""), body)
            manifest.append({"label": "HUB", "title": page_title(hp), "id": hub_id, "file": fn, "note": ""})
            print("  + [HUB] %s" % page_title(hp))
        # all children of hub (pages + dbs)
        for pid, p in pages.items():
            par = p.get("parent", {})
            if par.get("type") == "page_id" and par["page_id"] == hub_id:
                harvest_page(pid, "HUB-CHILD")
        for did, d in dbs.items():
            par = d.get("parent", {})
            if par.get("type") == "page_id" and par["page_id"] == hub_id:
                title = "".join(t.get("plain_text", "") for t in d.get("title", []))
                print("   DB under hub: %s (id=%s)" % (title, did[:13]))

    print("\n== C. Project databases: rows + row content ==")
    proj_dbs = {
        "d7aa0988": "Version Registry",
        "2328a57f": "Decision Log",
        "e844ab12": "Interaction Archive",
    }
    for prefix, name in proj_dbs.items():
        did = None
        for k in dbs:
            if k.startswith(prefix): did = k; break
        if not did:
            print("  !! %s not found" % name); continue
        rows, err = query_db(did)
        print("  %s: %d rows" % (name, len(rows)))
        dbdoc = ["# DB: %s (id=%s)" % (name, did), ""]
        for row in rows:
            rt = page_title(row)
            dbdoc.append("\n---\n### ROW: %s (id=%s | edited=%s)\n#### Properties\n%s\n#### Body\n%s" % (
                rt, row["id"][:13], row.get("last_edited_time", ""), props_to_md(row), fetch_blocks(row["id"], max_depth=2)))
        fn = os.path.join(PAGES_DIR, "DB_" + name.replace(" ", "_") + ".md")
        with open(fn, "w", encoding="utf-8") as f:
            f.write("\n".join(dbdoc))
        manifest.append({"label": "DB-" + name, "title": name, "id": did, "file": fn, "rows": len(rows)})
        print("     → %s" % os.path.basename(fn))

    print("\n== D. Reference/source pages ==")
    for label, keys in [
        ("PROMPT-LAB", ["Supplier Intelligence Prompt Lab"]),
        ("LEXICON", ["معجم البحث العميق"]),
        ("OP-SPEC", ["المواصفة التشغيلية"]),
        ("SRC-GLOBAL-DB", ["global_digital_products_database"]),
        ("SRC-CHEAPEST", ["cheapest_digital_products_suppliers_database"]),
        ("SRC-GLOBAL-SUPP", ["global_digital_suppliers_database"]),
        ("SRC-PROGRESS", ["progress.md"]),
        ("HIST-STACKVAULT", ["تفاوض موردي الخدمات الرقمية"]),
    ]:
        pid, t = find_page_by_title(keys)
        if pid:
            harvest_page(pid, label)
        else:
            print("  !! not found: %s" % label)

    print("\n== E. Governing reference children pages content (top 30) ==")
    for cid, ct in gov_children_pages[:30]:
        harvest_page(cid, "GOV-CHILD")

    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("\nDONE. %d docs harvested → %s" % (len(manifest), PAGES_DIR))

if __name__ == "__main__":
    main()
