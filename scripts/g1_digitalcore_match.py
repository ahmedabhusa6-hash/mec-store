#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R2f — THE DECISIVE MATCH: DigitalCore public catalog vs cb_ corpus.
/api/public/products (public, keyless, read-only).
Tests:
  D1 catalog shape + size
  D2 name matching vs cb_ (229) — normalized
  D3 price comparison on matches (cb_ SV retail vs DC wholesale tiers)
  D4 product-family coverage vs cb_ new wave (Lovable/Grok/Gmail/FB/AWS/KLING/LART/Plus 3D)
  D5 distinctive rare-product co-occurrence (Lovable Pro Lite etc.)
  D6 ID format comparison (DC slugs/numeric vs cb_ Mongo hex) -> same panel or different layer?
Output: research/g1_digitalcore_match_20261002.json
"""
import json, re, gzip, unicodedata
import urllib.request, urllib.error
from collections import Counter
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))
OUT = "/home/z/my-project/research/g1_digitalcore_match_20261002.json"

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                try: raw = gzip.decompress(raw)
                except Exception: pass
            return r.status, raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode("utf-8", "replace") if e.fp else "")
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"

def nk(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    t = re.sub(r"[^a-z ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

# ---- fetch DC catalog ----
st, body = fetch("https://digitalcore.top/api/public/products")
print(f"[D1] /api/public/products -> HTTP {st}, len={len(body)}")
dc = None
if st == 200 and body.lstrip()[:1] in "[{":
    try:
        dc = json.loads(body)
    except Exception as e:
        print("  parse err:", e)
if dc is None:
    print("FATAL: no DC catalog"); raise SystemExit(1)
if isinstance(dc, dict):
    dc = dc.get("products") or dc.get("data") or dc.get("items") or []
print(f"  DigitalCore catalog: {len(dc)} products")
print("  sample:", json.dumps(dc[0], ensure_ascii=False)[:220] if dc else "-")

# ---- load cb_ corpus ----
raw1 = json.load(open("/home/z/my-project/research/g1_rescan_raw_20261002.json"))
sv = json.loads(next(f["body"] for f in raw1["fetches"] if f["name"] == "sv_public"))["products"]
sv_cb = [it for it in sv if str(it.get("id", "")).startswith("cb_")]
cb_by_name = {}
for it in sv_cb:
    cb_by_name.setdefault(nk(it.get("name")), []).append(it)

# ---- D2: name matching ----
dc_by_name = {}
for it in dc:
    k = nk(it.get("name"))
    if k: dc_by_name.setdefault(k, []).append(it)
inter = set(cb_by_name) & set(dc_by_name)
print(f"\n[D2] name matches cb_({len(cb_by_name)} uniq) vs DC({len(dc_by_name)} uniq) = {len(inter)}")
matches = []
for k in sorted(inter):
    cbs = cb_by_name[k]; dcs = dc_by_name[k]
    for c in cbs[:1]:
        d = dcs[0]
        tiers = d.get("tiers") or []
        matches.append({
            "name": c.get("name"), "cb_price": c.get("price"),
            "dc_name": d.get("name"), "dc_price": d.get("price"),
            "dc_priceFrom": d.get("priceFrom"), "dc_stock": d.get("stock"),
            "dc_tier_min": tiers[-1].get("price") if tiers else None,
            "cb_id": str(c.get("id"))[:22], "dc_id": d.get("id")})
for m in matches[:40]:
    print(f"   ~ {m['name'][:46]:46} cb=${m['cb_price']:<7} dc=${m['dc_price']} (from ${m['dc_priceFrom']}, stock {m['dc_stock']})")

# ---- D3: price stats on matches ----
ratios = []
for m in matches:
    try:
        if m["cb_price"] and m["dc_price"]:
            ratios.append(float(m["cb_price"]) / float(m["dc_price"]))
    except Exception: pass
if ratios:
    ratios.sort()
    print(f"\n[D3] cb_/DC price ratio on {len(ratios)} matches: min={ratios[0]:.2f} med={ratios[len(ratios)//2]:.2f} max={ratios[-1]:.2f}")

# ---- D4: family coverage of cb_ new wave ----
new_wave = ["lovable", "grok", "gmail", "facebook", "aws", "kling", "lart", "capcut", "chatgpt plus 3d", "deepseek", "minimax", "elevenlab", "gamma", "n8n", "krea", "suno", "kahoot", "coursera", "nordvpn", "gcp"]
dc_text = " || ".join((it.get("name") or "") + " " + str(it.get("id") or "") + " " + str(it.get("desc") or it.get("description") or "") for it in dc).lower()
cb_text = " || ".join((it.get("name") or "") + " " + (it.get("description") or "") for it in sv_cb).lower()
print(f"\n[D4] new-wave family coverage (in DC? / in cb_?):")
cov = {}
for f in new_wave:
    in_dc = f in dc_text; in_cb = f in cb_text
    cov[f] = {"digitalcore": in_dc, "cb_": in_cb}
    print(f"   {f:16} DC={'Y' if in_dc else '-'}  cb_={'Y' if in_cb else '-'}")

# ---- D5: rare-product co-occurrence ----
rare = ["lovable", "coursera", "nordvpn", "kahoot", "n8n", "krea", "suno", "gamma credit", "minimax", "elevenlab"]
rare_cov = {r: {"DC": r in dc_text, "cb_": r in cb_text} for r in rare}
both = [r for r in rare if rare_cov[r]["DC"] and rare_cov[r]["cb_"]]
print(f"\n[D5] rare products in BOTH: {both}")

# ---- D6: ID formats ----
dc_ids = [str(it.get("id")) for it in dc]
slug_n = sum(1 for i in dc_ids if re.fullmatch(r"[a-z0-9_\-]+", i) and "_" in i)
num_n = sum(1 for i in dc_ids if re.fullmatch(r"\d+", i))
hex_n = sum(1 for i in dc_ids if re.fullmatch(r"[0-9a-f]{24}", i))
print(f"\n[D6] DC id formats: slug={slug_n} numeric={num_n} mongo-hex={hex_n} other={len(dc_ids)-slug_n-num_n-hex_n}")
print("     cb_ format = cb_<mongo-hex-24> (panel MongoDB)")
verdict_id = "DIFFERENT ID LAYER (slugs/numeric vs Mongo-hex) -> DC is a storefront/panel front, not the same raw DB exposure" if hex_n == 0 else "mongo-hex present -> possible direct link"

# ---- save ----
res = {"execution_timestamp": datetime.now(TZ).isoformat(),
       "dc_catalog_n": len(dc), "dc_catalog": dc,
       "name_matches": {"n": len(inter), "matches": matches},
       "price_ratio": {"n": len(ratios), "min": ratios[0] if ratios else None,
                       "median": ratios[len(ratios)//2] if ratios else None,
                       "max": ratios[-1] if ratios else None},
       "family_coverage": cov, "rare_cooccurrence": rare_cov,
       "id_format": {"dc": {"slug": slug_n, "numeric": num_n, "mongo_hex": hex_n},
                      "cb": "cb_<mongo-hex-24>", "verdict": verdict_id}}
with open(OUT, "w") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(f"\nSaved -> {OUT}")
