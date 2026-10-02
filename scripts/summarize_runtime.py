#!/usr/bin/env python3
"""Structural summary of local Batch-1 runtime artifacts + Notion source files (read-only)."""
import json, re, os

def head(path, n=40):
    try:
        with open(path, encoding="utf-8") as f:
            return [next(f) for _ in range(n)]
    except Exception as e:
        return ["ERR " + str(e)]

print("=== src/lib/data/run.json ===")
try:
    with open("/home/z/my-project/src/lib/data/run.json", encoding="utf-8") as f:
        run = json.load(f)
    print(json.dumps(run, ensure_ascii=False, indent=1)[:3500])
except Exception as e:
    print("ERR", e)

print("\n=== actions.json summary ===")
try:
    with open("/home/z/my-project/src/lib/data/actions.json", encoding="utf-8") as f:
        acts = json.load(f)
    print("type:", type(acts).__name__, "| count:", len(acts))
    if isinstance(acts, list) and acts:
        print("keys:", list(acts[0].keys()))
        from collections import Counter
        for field in ("status", "retrieval_status", "yield", "wave", "discovery_family"):
            vals = Counter(str(a.get(field, "?")) for a in acts)
            if len(vals) < 25:
                print(f"by {field}:", dict(vals))
except Exception as e:
    print("ERR", e)

print("\n=== entities files counts ===")
for name in ["entities-official", "entities-b2b", "entities-market", "entities-unverified", "skus"]:
    try:
        with open(f"/home/z/my-project/src/lib/data/{name}.json", encoding="utf-8") as f:
            d = json.load(f)
        print(f"{name}: {len(d)} items")
    except Exception as e:
        print(name, "ERR", e)

print("\n=== batch1 dataset md: section headings ===")
try:
    with open("/home/z/my-project/download/supplier-intelligence-batch1-dataset.md", encoding="utf-8") as f:
        txt = f.read()
    lines = txt.splitlines()
    print("total lines:", len(lines), "| chars:", len(txt))
    for ln in lines:
        if ln.startswith("#"):
            print("  ", ln[:110])
except Exception as e:
    print("ERR", e)

print("\n=== Notion source files structure ===")
for fn, label in [
    ("/home/z/my-project/scripts/notion/pages/مصدر _ global_digital_products_database_md.md", "global_digital_products_database.md (198KB)"),
    ("/home/z/my-project/scripts/notion/pages/مصدر _ cheapest_digital_products_suppliers_database_md.md", "cheapest_digital_products_suppliers_database.md (61KB)"),
    ("/home/z/my-project/scripts/notion/pages/مصدر _ global_digital_suppliers_database_md.md", "global_digital_suppliers_database.md (44KB)"),
]:
    try:
        with open(fn, encoding="utf-8") as f:
            txt = f.read()
        lines = txt.splitlines()
        print(f"\n--- {label}: {len(lines)} lines ---")
        hcount = 0
        for ln in lines:
            if ln.startswith("#") and hcount < 45:
                print("  ", ln[:100]); hcount += 1
        # count entity-ish rows
        mentions = {k: len(re.findall(k, txt, re.I)) for k in
                    ["last checked", "SKU", "Cheapest", "guarantee"]}
        print("   keyword counts:", mentions)
        m = re.search(r"(\d{4}-\d{2}-\d{2})", txt)
        print("   first date found:", m.group(1) if m else "?")
    except Exception as e:
        print(label, "ERR", e)

print("\n=== Stack Vault negotiation record: headings only ===")
try:
    with open("/home/z/my-project/scripts/notion/pages/سجل تاريخي _ تفاوض موردي الخدمات الرقمية _ Stack Vault Support.md", encoding="utf-8") as f:
        txt = f.read()
    lines = txt.splitlines()
    print("total lines:", len(lines))
    for ln in lines:
        if ln.startswith("#"):
            print("  ", ln[:100])
except Exception as e:
    print("ERR", e)
