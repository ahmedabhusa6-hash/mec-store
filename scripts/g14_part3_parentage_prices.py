#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-14 part 3 — parentage map + key-SKU price reconciliation (25/09 foundational vs project chains)
+ new-lead extraction with context from today's research trio.
Outputs -> research/g14_2026-10-02/
"""
import json, os, glob, collections

NEW = "/home/z/my-project/notion_raw_v2_20261002"
OUT = "/home/z/my-project/research/g14_2026-10-02"

def save(name, obj):
    with open("%s/%s" % (OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

# ---------- 1) parentage map: resolve full parent ids to titles ----------
id2title = {}
pages_data = {}
for fp in glob.glob("%s/pages/*.json" % NEW):
    try:
        j = json.load(open(fp, encoding="utf-8"))
    except Exception:
        continue
    nid = j.get("page", {}).get("id", "").replace("-", "").lower() or fp.split("/")[-1][:-5]
    id2title[nid] = j.get("title", "?")
    pages_data[nid] = j
# old index for titles of non-captured parents
old_idx = json.load(open("/home/z/my-project/notion_raw/00_index.json", encoding="utf-8"))
for p in old_idx.get("pages", []):
    id2title.setdefault(p["id"].replace("-", "").lower(), p.get("title", "?"))
for d in old_idx.get("databases", []):
    id2title.setdefault(d["id"].replace("-", "").lower(), "[DB] " + (d.get("title") or "?"))

parent_map = collections.defaultdict(list)
for nid, j in pages_data.items():
    par = j.get("page", {}).get("parent", {})
    pid = (par.get("page_id") or par.get("database_id") or "").replace("-", "").lower()
    key = id2title.get(pid, pid[:16] if pid else "(no parent / workspace)")
    parent_map[key].append({"title": j.get("title", ""), "reason": j.get("capture_reason", ""),
                             "edited": j.get("last_edited", "")[:10], "blocks": j.get("block_count", 0)})
save("delta_parentage_map.json",
     {k: {"count": len(v), "children": sorted(v, key=lambda x: x["edited"] or "")}
      for k, v in sorted(parent_map.items(), key=lambda kv: -len(kv[1]))})
print("parentage map (top 12):")
for k, v in sorted(parent_map.items(), key=lambda kv: -len(kv[1]))[:12]:
    print("   %-58s %d صفحة" % (k[:58], len(v)))

# ---------- 2) key-SKU price lines in REF_HAKIM by block date ----------
rh = pages_data["3e658a0779e881c49cddd7b74626d61f"]
KEY_SKUS = ["ChatGPT", "Netflix", "Spotify", "Gemini", "Office", "Xbox", "Discord"]
sku_lines = []
for b in rh.get("blocks", []):
    txt = " ".join(b.get("text") or [])
    if not txt: continue
    if any(k.lower() in txt.lower() for k in KEY_SKUS) and any(c in txt for c in "$0123456789"):
        sku_lines.append({"day": (b.get("created") or "")[:10], "type": b.get("type"),
                          "text": txt[:300]})
by_day = collections.Counter(l["day"] for l in sku_lines)
save("ref_hakim_key_sku_price_lines.json",
     {"count": len(sku_lines), "by_created_day": dict(by_day),
      "note": "أسطر الأسعار للأصناف المفتاحية في المرجع الحاكم مصنفة بيوم إنشاء الكتلة — أساس مصالحة G-12",
      "lines": sku_lines})
print("\nkey-SKU price lines:", len(sku_lines), "by day:", dict(by_day))

# ---------- 3) today's research trio: new leads with context ----------
TRIO = {"DR_FINDINGS": "3ed58a0779e88183a21aeb6999ed4924",
        "TG_PROVIDERS": "3ed58a0779e881b3954fe116cd960d77",
        "DR_PROMPT": "3ed58a0779e88116b4b9c4a0eea3e91a"}
import re
handle_re = re.compile(r"(?:t\.me/|@)([A-Za-z0-9_]{3,64})", re.IGNORECASE)
url_re = re.compile(r"(?:https?://)?(?:www\.)?([A-Za-z0-9][A-Za-z0-9-]{1,60}(?:\.(?:com|net|io|org|shop|me|dev|app|xyz|pro|store|site|online|co|ai|gg|to))(?:/[^\s\u0600-\u06FF\"')\]]*)?)", re.IGNORECASE)
KNOWN_BRANDS = ["prodseller", "stackvault", "hitmeow", "acczone", "aisubsid", "evo_era", "teamsoclo",
                "tokensunlimited", "gemini12pro", "eneba", "turgame", "notion", "telegram"]
trio_leads = {}
for key, pid in TRIO.items():
    j = pages_data[pid]
    lines = [" ".join(b.get("text") or []) for b in j.get("blocks", [])]
    leads = {}
    for i, l in enumerate(lines):
        for m in handle_re.finditer(l):
            h = m.group(1)
            if any(kb in h.lower() for kb in KNOWN_BRANDS) or h.lower() in ("telegram", "notion"): continue
            leads.setdefault("@" + h, {"ctx": l[:200]})
        for m in url_re.finditer(l):
            u = m.group(1).lower()
            if any(kb in u for kb in KNOWN_BRANDS): continue
            leads.setdefault(u, {"ctx": l[:200]})
    trio_leads[key] = {"label": j.get("title", ""), "new_leads": leads}
    print("\n%s (%d new leads):" % (key, len(leads)))
    for k, v in list(leads.items())[:25]:
        print("   %-38s | %s" % (k[:38], v["ctx"][:95]))
save("trio_new_leads.json", trio_leads)
