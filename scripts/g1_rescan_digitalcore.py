#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R2e — DigitalCore probe (the 30/09 'direct supplier for resellers' entity):
  - digitalcore.top root + /docs (public, passive)
  - discover API base/products/pricing endpoints from docs
  - fetch public catalog if available -> compare with cb_
READ-ONLY passive GETs on public pages only."""
import json, re, time, gzip
import urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))

def fetch(name, url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"})
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
        try: rec["body"] = e.read().decode("utf-8", "replace")
        except Exception: rec["body"] = None
        rec["http"] = e.code; rec["err"] = "HTTPError"; rec["len"] = len(rec["body"] or "")
    except Exception as e:
        rec["err"] = f"{type(e).__name__}: {str(e)[:100]}"
    return rec

out = {"execution_timestamp": datetime.now(TZ).isoformat(), "probes": []}
def do(name, url):
    rec = fetch(name, url)
    out["probes"].append(rec)
    b = (rec.get("body") or "")[:90].replace("\n", " ")
    print(f"  [{rec['http']}] {name:24} len={rec['len']:>7}  {b}")
    time.sleep(0.6)
    return rec

print("=== DigitalCore probes ===")
r_root = do("dc_root", "https://digitalcore.top/")
r_docs = do("dc_docs", "https://digitalcore.top/docs")

# extract API hints from docs/root
for rec in (r_root, r_docs):
    body = rec.get("body") or ""
    if not body: continue
    urls = sorted(set(re.findall(r'https?://[a-zA-Z0-9\.\-]+(?:/[a-zA-Z0-9\.\-/]*)?', body)))
    apiish = [u for u in urls if any(k in u.lower() for k in ['api', 'docs', 'v1', 'pricing', 'product', 'spec', 'openapi', 'json'])]
    paths = sorted(set(re.findall(r'[\'"`](/(?:api|v1|docs)[a-zA-Z0-9_\-/\.]*)[\'"`]', body)))
    print(f"  [{rec['name']}] api-ish urls: {apiish[:12]}")
    print(f"  [{rec['name']}] api paths: {paths[:15]}")

# common public endpoints
for name, url in [
    ("dc_openapi", "https://digitalcore.top/openapi.json"),
    ("dc_api_pricing", "https://digitalcore.top/api/pricing"),
    ("dc_api_products", "https://digitalcore.top/api/products"),
    ("dc_api_v1_products", "https://digitalcore.top/api/v1/products"),
    ("dc_docs_json", "https://digitalcore.top/docs-json"),
    ("dc_api_docs", "https://api.digitalcore.top/"),
]:
    do(name, url)

with open("/home/z/my-project/research/g1_rescan_raw5_20261002.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("Saved -> research/g1_rescan_raw5_20261002.json")
