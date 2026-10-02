#!/usr/bin/env python3
"""Fix-up harvest: project hub + its child pages (emoji-safe title matching)."""
import os, json, time, re, urllib.request, urllib.error

TOKEN = os.environ.get("NOTION_TOKEN", "")
BASE = "https://api.notion.com/v1"
OUT = "/home/z/my-project/scripts/notion"
PAGES_DIR = os.path.join(OUT, "pages")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D\u2B00-\u2BFF]")

def api(method, path, body=None, retries=4):
    headers = {"Authorization": "Bearer " + TOKEN,
               "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(BASE + path, method=method, headers=headers, data=data)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(min(float(e.headers.get("Retry-After", 2 ** attempt)), 30)); continue
            try: detail = e.read().decode()[:200]
            except Exception: detail = ""
            return {"__error": e.code, "__detail": detail}
        except Exception:
            time.sleep(1.5 ** attempt)
    return {"__error": "max_retries"}

def clean_title(t):
    return EMOJI_RE.sub("", t).strip()

def page_title(page):
    for key, val in page.get("properties", {}).items():
        if val.get("type") == "title":
            return "".join(x.get("plain_text", "") for x in val.get("title", []))
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
        if href and t.strip(): t = "[%s](%s)" % (t, href)
        parts.append(t)
    return "".join(parts)

def block_to_md(block, depth):
    bt = block.get("type", "")
    b = block.get(bt, {}) or {}
    md = ""
    prefix = "  " * depth
    if bt == "paragraph": md = prefix + rich_text_md(b.get("rich_text"))
    elif bt.startswith("heading_"): md = prefix + "#" * int(bt[-1]) + " " + rich_text_md(b.get("rich_text"))
    elif bt == "bulleted_list_item": md = prefix + "- " + rich_text_md(b.get("rich_text"))
    elif bt == "numbered_list_item": md = prefix + "1. " + rich_text_md(b.get("rich_text"))
    elif bt == "to_do":
        md = prefix + "- [%s] %s" % ("x" if b.get("checked") else " ", rich_text_md(b.get("rich_text")))
    elif bt == "toggle": md = prefix + "▶ " + rich_text_md(b.get("rich_text"))
    elif bt == "code":
        md = prefix + "```" + b.get("language", "") + "\n" + rich_text_md(b.get("rich_text")) + "\n" + prefix + "```"
    elif bt == "quote": md = prefix + "> " + rich_text_md(b.get("rich_text"))
    elif bt == "callout": md = prefix + "> 💬 " + rich_text_md(b.get("rich_text"))
    elif bt == "divider": md = prefix + "---"
    elif bt == "child_page": md = prefix + "[[CHILD PAGE: %s | id=%s]]" % (b.get("title", ""), block.get("id", ""))
    elif bt == "child_database": md = prefix + "[[CHILD DATABASE: %s | id=%s]]" % (b.get("title", ""), block.get("id", ""))
    elif bt == "table_row":
        md = prefix + "| " + " | ".join(rich_text_md(c) for c in b.get("cells", [])) + " |"
    elif bt in ("embed", "bookmark", "link_preview"): md = prefix + "[EMBED %s]" % (b.get("url", ""))
    elif bt == "image": md = prefix + "[IMAGE %s]" % rich_text_md(b.get("caption"))
    else:
        rt = b.get("rich_text") if isinstance(b, dict) else None
        md = prefix + ("[%s] %s" % (bt.upper(), rich_text_md(rt) if rt else ""))
    return md

def fetch_blocks(page_id, max_depth=3):
    lines = []
    def walk(bid, depth):
        if depth > max_depth: return
        cursor = None
        while True:
            path = "/blocks/%s/children?page_size=100" % bid
            if cursor: path += "&start_cursor=" + cursor
            r = api("GET", path)
            if "__error" in r:
                lines.append("!! ERROR: %s" % r); return
            for blk in r.get("results", []):
                md = block_to_md(blk, depth)
                if md.strip(): lines.append(md)
                if blk.get("has_children") and blk.get("type") not in ("child_page", "child_database"):
                    walk(blk["id"], depth + 1)
            if not r.get("has_more") or not r.get("next_cursor"): break
            cursor = r["next_cursor"]; time.sleep(0.35)
    walk(page_id, 0)
    return "\n".join(lines)

def save_doc(title, pid, url, body, label):
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in clean_title(title))[:80].strip() or pid[:8]
    fn = os.path.join(PAGES_DIR, safe + ".md")
    with open(fn, "w", encoding="utf-8") as f:
        f.write("# %s\n\n> id=%s | url=%s | label=%s\n\n## Content\n%s\n" % (title, pid, url, label, body))
    print("  + [%s] %s → %s (%d chars)" % (label, clean_title(title)[:60], os.path.basename(fn), len(body)))
    return fn

def main():
    with open(os.path.join(OUT, "raw_search.json"), encoding="utf-8") as f:
        results = json.load(f)
    pages = {p["id"]: p for p in results if p.get("object") == "page" and not p.get("archived")}

    # find hub via Canonical Registry's parent
    hub_id = None
    for pid, p in pages.items():
        if "Canonical Registry" in page_title(p):
            par = p.get("parent", {})
            if par.get("type") == "page_id":
                hub_id = par["page_id"]; break
    print("hub id:", (hub_id or "?")[:13])
    if not hub_id: return

    # hub page itself
    hub = pages.get(hub_id) or api("GET", "/pages/" + hub_id)
    if hub and "__error" not in hub:
        save_doc("HUB — " + page_title(hub), hub_id, hub.get("url", ""), fetch_blocks(hub_id), "HUB")

    # all children of hub
    kids = [(pid, page_title(p)) for pid, p in pages.items()
            if p.get("parent", {}).get("type") == "page_id" and p["parent"]["page_id"] == hub_id]
    print("hub children: %d" % len(kids))
    for pid, t in sorted(kids, key=lambda x: clean_title(x[1])):
        p = pages[pid]
        save_doc(t, pid, p.get("url", ""), fetch_blocks(pid), "HUB-CHILD")

if __name__ == "__main__":
    main()
