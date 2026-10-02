#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.5f | Embedded-JSON extraction: K4G __NEXT_DATA__ (product feed w/ EUR prices)
+ bittopup NUXT payload (PUBG UC + top-ups). Directly-Observed tier, quota-free.
Output: research/b3_k4g_catalog.json + research/b3_bittopup_catalog.json
"""
import json, os, re, time, urllib.request, gzip

BASE = "/home/z/my-project"

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            d = gzip.decompress(d)
        return d.decode("utf-8", "ignore")

# ---------------- K4G ----------------
html = fetch("https://k4g.com/")
m = re.search(r'<script id="__NEXT_DATA__" type="application/json"[^>]*>(.*?)</script>', html, re.S)
k4g_products = []
k4g_meta = {"http": 200, "bytes": len(html)}
if m:
    try:
        data = json.loads(m.group(1))
        # walk the tree to find product-like objects
        def walk(node, depth=0):
            if depth > 12: return
            if isinstance(node, dict):
                if ("name" in node and "price" in node and isinstance(node.get("price"), (dict, int, float))):
                    k4g_products.append(node)
                for v in node.values(): walk(v, depth + 1)
            elif isinstance(node, list):
                for v in node: walk(v, depth + 1)
        walk(data)
        k4g_meta["next_data_parsed"] = True
    except Exception as e:
        k4g_meta["parse_error"] = str(e)[:120]
else:
    k4g_meta["next_data_found"] = False

# normalize K4G products
def k4g_norm(p):
    name = p.get("name", "")
    price = p.get("price")
    eur = None
    if isinstance(price, dict):
        e = price.get("EUR") or {}
        if isinstance(e, dict): eur = e.get("price")
        elif isinstance(e, (int, float)): eur = e
    elif isinstance(price, (int, float)): eur = price
    return {"name": str(name)[:90], "eur": eur, "id": p.get("id") or p.get("slug", "")}

k4g_normed = [k4g_norm(p) for p in k4g_products]
k4g_priced = [p for p in k4g_normed if p["eur"] is not None]
# dedupe by name
seen = set(); k4g_unique = []
for p in k4g_priced:
    if p["name"] in seen: continue
    seen.add(p["name"]); k4g_unique.append(p)
k4g_unique.sort(key=lambda x: x["eur"])

json.dump({"run": "MEC-2.5f K4G embedded catalog", "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
           "meta": k4g_meta, "n_products": len(k4g_unique), "products": k4g_unique[:400]},
          open(os.path.join(BASE, "research", "b3_k4g_catalog.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"K4G: {len(k4g_products)} product objects -> {len(k4g_unique)} unique priced")
for p in k4g_unique[:12]:
    print(f"   EUR {p['eur']:<8} {p['name'][:70]}")

time.sleep(4)

# ---------------- bittopup ----------------
html2 = fetch("https://bittopup.com/")
# NUXT payload: script window.__NUXT__ = ... (JS object literal, not JSON) — extract via regex patterns
bt_meta = {"http": 200, "bytes": len(html2), "nuxt": "__NUXT__" in html2}
# extract "name":N,"price":M pairs from the payload arrays + string table approach is complex;
# simpler: find quoted names followed by prices in the JS literal
pairs = re.findall(r'"([^"]{2,60})"[^{}]{0,80}?"price":\s*([0-9]+(?:\.[0-9]+)?)', html2)
# also the compact form seen: {"name":40,"price":41},"60 UC",0.942  → indexes into string table
compact = re.findall(r'\{"name":(\d+),"price":(\d+)\}', html2)
bt_items = [{"raw_name": n, "price": float(v)} for n, v in pairs]
bt_meta["n_direct_pairs"] = len(pairs)
bt_meta["n_index_pairs"] = len(compact)

json.dump({"run": "MEC-2.5f bittopup embedded data", "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
           "meta": bt_meta, "items": bt_items[:200], "compact_index_pairs": len(compact)},
          open(os.path.join(BASE, "research", "b3_bittopup_catalog.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\nbittopup: direct pairs={len(pairs)}, index pairs={len(compact)}")
for it in bt_items[:10]:
    print(f"   ${it['price']:<8} {it['raw_name'][:60]}")
