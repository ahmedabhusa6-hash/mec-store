#!/usr/bin/env python3
"""Explore mystery clusters in the Notion index to locate the suppliers governing DB and project structure."""
import json
from collections import defaultdict

IDX = "/home/z/my-project/scripts/notion/index.json"
with open(IDX, encoding="utf-8") as f:
    index = json.load(f)

all_pages = index["pages"]
all_dbs = index["databases"]

def parent_key(p): return p["parent"].split(":")[1] if ":" in p["parent"] else p["parent"]

print("=== ALL 31 DATABASES ===")
for d in all_dbs:
    print("[DB] %-70s | parent=%s | id=%s" % (d["title"][:70], d["parent"], d["id"][:13]))

print("\n=== WORKSPACE-LEVEL PAGES (22) ===")
for p in all_pages:
    if p["parent"] == "workspace":
        print("[PG] %-70s | id=%s | edited=%s" % (p["title"][:70], p["id"][:13], p["last_edited"]))

# pages of interest by cluster
for cluster in ["230f9103", "14095699", "393c008b", "2d1337a6", "ca158a07", "3e758a07", "2328a57f"]:
    items = [p for p in all_pages if parent_key(p) == cluster]
    print("\n=== CLUSTER %s : %d pages (first 25) ===" % (cluster, len(items)))
    for p in items[:25]:
        print("  * %-80s | id=%s | edited=%s" % (p["title"][:80], p["id"][:13], p["last_edited"]))
    if len(items) > 25:
        print("  ... +%d more" % (len(items) - 25))

# find pages whose title mentions suppliers/mوردين/cheapest
print("\n=== TITLE SEARCH: موردين / suppliers / cheapest / مرجع حاكم ===")
for p in all_pages + all_dbs:
    t = p["title"]
    if any(k in t for k in ["موردين", "upplier", "heapest", "مرجع حاكم", "رخص"]):
        print("  * %-90s | parent=%s | id=%s" % (t[:90], p["parent"], p["id"][:13]))
