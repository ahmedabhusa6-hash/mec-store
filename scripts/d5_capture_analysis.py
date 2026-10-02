#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D5 capture analysis — classify the 348 NEWLY_ACCESSIBLE + inspect key NEW/CHANGED items"""
import json, os, re

OUT = "/home/z/my-project/notion_raw_v2_20261002"
OLD = "/home/z/my-project/notion_raw"

def load(p):
    return json.load(open(p, encoding="utf-8"))

pages = {}
for fn in os.listdir(OUT + "/pages"):
    d = load(OUT + "/pages/" + fn)
    pages[d["title"] + "|" + fn[:-5]] = d

# ---- 1. classification of 348 NEWLY_ACCESSIBLE ----
cats = {"AUTO-CYCLE (automation)": [], "KOS/كnowledge system": [], "حوكمة/مرجع حاكم": [],
        "محاسبة/Accounting": [], "تسويق/Marketing": [], "موردين/Suppliers": [],
        "شخصي/دراسي/مدونة": [], "أخرى": []}
pat = [
    ("AUTO-CYCLE (automation)", re.compile(r"AUTO-CYCLE|Automation Runtime|Central Automation", re.I)),
    ("KOS/كnowledge system", re.compile(r"KOS|Knowledge|إدارة المعرفة|مرجع نطاق|Prompt Lab|Migration", re.I)),
    ("حوكمة/مرجع حاكم", re.compile(r"مرجع حاكم|Governance|حوكمة|قرار|Protocol|مرجع")),
    ("محاسبة/Accounting", re.compile(r"Accounting|محاسب", re.I)),
    ("تسويق/Marketing", re.compile(r"Marketing|تسويق", re.I)),
    ("موردين/Suppliers", re.compile(r"[Ss]upplier|مورد|توريد|Batch|Batch[123]")),
    ("شخصي/دراسي/مدونة", re.compile(r"مدوّنتي|الواجبات|المقرّرات|ملاحظات الصف|كتاب|Books|أم سارة|PERSONAL", re.I)),
]
na_stats = {"count": 0, "blocks": 0, "chars": 0, "no_blocks": 0}
for key, d in pages.items():
    if d.get("capture_reason") != "NEWLY_ACCESSIBLE":
        continue
    na_stats["count"] += 1
    na_stats["blocks"] += d.get("block_count", 0)
    if d.get("block_count", 0) == 0: na_stats["no_blocks"] += 1
    title = d["title"]
    textfile = OUT + "/text/" + [k for k in os.listdir(OUT + "/text")][0]  # placeholder
    for cat, rx in pat:
        if rx.search(title):
            cats[cat].append(title[:70]); break
    else:
        cats["أخرى"].append(title[:70])
print("=== 348 NEWLY_ACCESSIBLE classification ===")
print("total:", na_stats["count"], "| blocks:", na_stats["blocks"], "| empty(no blocks):", na_stats["no_blocks"])
for c, lst in cats.items():
    print(f"  {c}: {len(lst)}")
    for t in lst[:8]: print("     -", t)

# ---- 2. text volume of the whole capture ----
tot_chars = 0
for fn in os.listdir(OUT + "/text"):
    tot_chars += os.path.getsize(OUT + "/text/" + fn)
print("\n=== capture volume ===")
print("text bytes:", tot_chars, "| pages:", len(pages))

# ---- 3. key NEW items (2026-10-02) full text ----
def show(title_rx, label, maxchars=1800):
    rx = re.compile(title_rx)
    for key, d in pages.items():
        if rx.search(d["title"]) and d.get("capture_reason") in ("NEW", "CHANGED"):
            fn = key.split("|")[1] + ".txt"
            txt = open(OUT + "/text/" + fn, encoding="utf-8").read()
            print("\n" + "=" * 70)
            print(f"[{label}] {d['title']} | reason={d['capture_reason']} | edited={d['last_edited']} | blocks={d.get('block_count')}")
            print(txt[:maxchars])
            break

show(r"هندسة Z\.ai Agent", "NEW-FOUNDATIONAL", 2200)
show(r"Deep Research Findings — Supplier Intelligence — 2026-10-02", "NEW-SUPPLIER", 2200)
show(r"Telegram API Providers — Research", "NEW-SUPPLIER-2", 1500)
show(r"قاعدة بيانات أرخص موردي", "CHANGED-GOVERNING-DB-PAGE", 1500)
show(r"Central Automation Runtime", "CHANGED-RUNTIME", 1200)
show(r"v4\.2 — Catalog/Batch", "CHANGED-ARCH", 1200)

# ---- 4. database row deltas vs old capture ----
print("\n" + "=" * 70)
print("=== DB row counts: new capture vs old (2026-09-26) ===")
old_db = {}
for fn in os.listdir(OLD + "/databases"):
    try:
        d = load(OLD + "/databases/" + fn)
        t = d.get("title") or (d.get("schema", {}).get("title") or [{}])
        if isinstance(t, list): t = "".join(x.get("plain_text", "") for x in t)
        n = d.get("row_count") or len(d.get("rows", [])) or (len(d.get("results", [])) if isinstance(d, dict) else 0)
        old_db[t] = n
    except Exception as e:
        old_db["(err:" + fn[:8] + ")"] = -1
new_db = {}
for fn in os.listdir(OUT + "/databases"):
    d = load(OUT + "/databases/" + fn)
    new_db[d["title"]] = d.get("row_count", 0)
for t, n in sorted(new_db.items()):
    o = old_db.get(t, "?")
    mark = "CHANGED" if (o != "?" and n != o) else ("NEW" if o == "?" else "same")
    print(f"  [{mark}] rows {o} -> {n} | {t[:60]}")

# ---- 5. AUTO-CYCLE range ----
cycles = sorted([d["title"] for k, d in pages.items() if "AUTO-CYCLE" in d["title"]])
print("\n=== AUTO-CYCLE pages captured:", len(cycles), "===")
if cycles:
    print("first:", cycles[0], "| last:", cycles[-1])
