#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1 RESCAN R2b — gap-fill fetches:
  1) AIXpress real base URL (aixpress.shop — key was invalid on aiversehub.store)
  2) acczone endpoint discovery (root/docs HTML analysis + common paths)
  3) laha docs HTML spec-URL discovery (if other endpoints exist)
READ-ONLY GET only.
Output: research/g1_rescan_raw2_20261002.json
"""
import json, re, time, gzip
import urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))
OUT = "/home/z/my-project/research/g1_rescan_raw2_20261002.json"
KEYS = {
    "aixp": "AK_w3elZvNBdF8QNQs5ynTrkD1bW6hVAh3e9",
    "acz":  "[REDACTED-ACZ-KEY]",
}
H_JSON = {"Accept": "application/json"}

def fetch(name, url, headers=None, timeout=22):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    rec = {"name": name, "url": url, "http": None, "err": None, "len": 0, "body": None,
           "ts": datetime.now(TZ).isoformat()[:19]}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                try: raw = gzip.decompress(raw)
                except Exception: pass
            rec["body"] = raw.decode("utf-8", "replace"); rec["http"] = r.status; rec["len"] = len(rec["body"])
    except urllib.error.HTTPError as e:
        try:
            raw = e.read()
            rec["body"] = raw.decode("utf-8", "replace")
        except Exception: rec["body"] = None
        rec["http"] = e.code; rec["err"] = "HTTPError"; rec["len"] = len(rec["body"] or "")
    except Exception as e:
        rec["err"] = f"{type(e).__name__}: {str(e)[:120]}"
    return rec

results = {"execution_timestamp": datetime.now(TZ).isoformat(), "fetches": []}
def do(name, url, headers=None):
    rec = fetch(name, url, headers)
    results["fetches"].append(rec)
    b = (rec.get("body") or "")[:70].replace("\n", " ")
    print(f"  [{rec['http'] if rec['http'] is not None else 'ERR'}] {name:26} len={rec['len']:>8}  {b}")
    time.sleep(0.5)
    return rec

# ---- 1) analyze saved acczone root/docs HTML locally for endpoint hints ----
print("=== analyzing saved acczone HTML ===")
raw1 = json.load(open("/home/z/my-project/research/g1_rescan_raw_20261002.json"))
acz_root = next((f["body"] for f in raw1["fetches"] if f["name"] == "acz_root"), "") or ""
acz_docs = next((f["body"] for f in raw1["fetches"] if f["name"] == "acz_docs"), "") or ""
acz_openapi = next((f["body"] for f in raw1["fetches"] if f["name"] == "acz_openapi"), "") or ""
api_refs = sorted(set(re.findall(r'[\'"`](/[a-zA-Z0-9_\-/]{2,40})[\'"`]', acz_root + acz_docs)))
print("  path-like refs in acczone HTML:", api_refs[:40])
spec_urls = sorted(set(re.findall(r'(?:url|spec|src|href)\s*[:=]\s*[\'"`]?([^\'"`\s>]+(?:openapi|swagger|spec)[^\'"`\s>]*)', acz_root + acz_docs, re.I)))
print("  spec-url refs:", spec_urls[:10])
title = re.search(r"<title>(.*?)</title>", acz_root, re.S)
print("  acz_root title:", title.group(1).strip()[:120] if title else None)
try:
    op = json.loads(acz_openapi)
    print("  openapi paths:", list(op.get("paths", {}).keys()))
except Exception as e:
    print("  openapi parse:", e)

# ---- 2) AIXpress real base ----
print("=== AIXpress on aixpress.shop ===")
do("aixp_shop_products", "https://aixpress.shop/api/v1/products", {"X-API-Key": KEYS["aixp"], **H_JSON})
do("aixp_shop_me", "https://aixpress.shop/api/v1/me", {"X-API-Key": KEYS["aixp"], **H_JSON})
do("aixp_shop_docs", "https://aixpress.shop/docs")

# ---- 3) acczone candidate paths ----
print("=== acczone path probes ===")
for path in ["/api/products", "/products", "/v1/products", "/api/v1/me", "/me", "/api/me",
             "/api/v1/catalog", "/api/catalog", "/user", "/api/v1/user"]:
    do("acz" + path.replace("/", "_"), "https://api.acczone.xyz" + path,
       {"Authorization": "Bearer " + KEYS["acz"], **H_JSON})

with open(OUT, "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print(f"\nSaved -> {OUT}")
