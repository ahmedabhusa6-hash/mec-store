#!/usr/bin/env python3
"""Probe the structure of all pulled catalog files to build the consolidation map."""
import json, os

R = "/home/z/my-project/research"

FILES = {
    "sv_live_282": f"{R}/g1_cb_live_catalog_20261002.json",
    "entities_raw7": f"{R}/g1_rescan_raw_20261002.json",
    "newkeys_raw": f"{R}/g1_r3_newkeys_raw_20261002.json",
    "sv_archive_357": f"{R}/stackvault_live/sv_products_current.json",
    "prodseller_fresh": f"{R}/prodseller_live/products_fresh.json",
    "gateway_pricing": f"{R}/sv_master_gateway_pricing_20261002.json",
    "rescan_raw2": f"{R}/g1_rescan_raw2_20261002.json",
    "rescan_raw4": f"{R}/g1_rescan_raw4_20261002.json",
    "rescan_raw5": f"{R}/g1_rescan_raw5_20261002.json",
    "rescan_raw6": f"{R}/g1_rescan_raw6_20261002.json",
    "rescan_raw3": f"{R}/g1_rescan_raw3_20261002.json",
    "r3_followup": f"{R}/g1_r3_followup_20261002.json",
}

def probe(name, path):
    if not os.path.exists(path):
        print(f"### {name}: MISSING")
        return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    print(f"### {name} ({os.path.basename(path)}, {os.path.getsize(path)//1024}KB)")
    def walk(d, depth=0, prefix=""):
        if depth > 2:
            return
        if isinstance(d, dict):
            for k, v in list(d.items())[:25]:
                t = type(v).__name__
                if isinstance(v, list):
                    print(f"{'  '*depth}{k}: list[{len(v)}]", end="")
                    if v and isinstance(v[0], dict):
                        print(f" keys={list(v[0].keys())[:14]}")
                    else:
                        print(f" sample={str(v[:2])[:80]}")
                elif isinstance(v, dict):
                    print(f"{'  '*depth}{k}: dict keys={list(v.keys())[:14]}")
                    walk(v, depth+1)
                else:
                    print(f"{'  '*depth}{k}: {t} = {str(v)[:70]}")
        elif isinstance(d, list):
            print(f"{'  '*depth}list[{len(d)}]")
            if d and isinstance(d[0], dict):
                print(f"{'  '*depth}item keys={list(d[0].keys())[:16]}")
                print(f"{'  '*depth}sample={str(d[0])[:220]}")
    walk(data)
    print()

for name, path in FILES.items():
    try:
        probe(name, path)
    except Exception as e:
        print(f"### {name}: ERROR {e}\n")
