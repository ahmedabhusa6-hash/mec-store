#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-1 RESCAN R2 — full cb_ re-scan + entity catalog collection (read-only).
Context: user reports cb_ complete = 357 (prior scan 03:17+03 captured 229/282).
New: API keys provided by Ahmed (2026-10-02 ~03:21-03:32) for:
  ver_pixel_bot/lahastore, AIVerseX, Gemini_Shop/aivaulthub, AIXpress, ProdSeller,
  Mike_E_0/acczone, stackvault (svr_).
Passive probes: gemini12pro links (channel/user/bot) + decohomz.com root.
STRICTLY READ-ONLY: GET endpoints only. NO orders, NO balance mutation.
Output: research/g1_rescan_raw_20261002.json
"""
import json, re, time, gzip, ssl
import urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))  # Asia/Aden
OUT = "/home/z/my-project/research/g1_rescan_raw_20261002.json"

KEYS = {
    "sv":   "svr_151cbd48e3ff20550a3f3b0f46f3799e413df805eab6698c",
    "laha": "[REDACTED-PRODSELLER-KEY]",
    "aivx": "AK_5Up6V45AJz1TecHklp2ldnp1RaS8NowX",
    "aixp": "AK_w3elZvNBdF8QNQs5ynTrkD1bW6hVAh3e9",
    "gshop":"rsk_rFG1syRRcBMofqHpJ0a6CPYDcsAXTkp2huJ8U0dujOI",
    "ps":   "[REDACTED-PRODSELLER-KEY]",
    "acz":  "[REDACTED-ACZ-KEY]",
}
def mask(k): return k[:8] + "..." + k[-4:]

def fetch(name, url, headers=None, timeout=22):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    rec = {"name": name, "url": url, "http": None, "err": None,
           "ctype": None, "len": 0, "body": None, "ts": datetime.now(TZ).isoformat()[:19]}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                try: raw = gzip.decompress(raw)
                except Exception: pass
            txt = raw.decode("utf-8", "replace")
            rec["http"] = r.status; rec["ctype"] = r.headers.get("Content-Type", "")
            rec["len"] = len(txt); rec["body"] = txt
    except urllib.error.HTTPError as e:
        try:
            raw = e.read()
            if e.headers.get("Content-Encoding") == "gzip":
                try: raw = gzip.decompress(raw)
                except Exception: pass
            rec["body"] = raw.decode("utf-8", "replace")
        except Exception:
            rec["body"] = None
        rec["http"] = e.code; rec["err"] = "HTTPError"; rec["len"] = len(rec["body"] or "")
    except Exception as e:
        rec["http"] = None; rec["err"] = f"{type(e).__name__}: {str(e)[:120]}"
    return rec

def jparse(rec):
    """try parse body as json -> (ok, data)"""
    if not rec.get("body"): return False, None
    s = rec["body"].lstrip()
    if s[:1] not in "[{": return False, None
    try: return True, json.loads(rec["body"])
    except Exception: return False, None

H_JSON = {"Accept": "application/json"}

results = {"execution_timestamp": datetime.now(TZ).isoformat(),
           "task": "G-1 RESCAN R2 (user-reported cb_ complete=357)",
           "keys_used_masked": {k: mask(v) for k, v in KEYS.items()},
           "reads_only": True, "fetches": []}

def do(name, url, headers=None):
    rec = fetch(name, url, headers)
    results["fetches"].append(rec)
    b = (rec.get("body") or "")[:80].replace("\n", " ")
    print(f"  [{rec['http'] if rec['http'] is not None else 'ERR'}] {name:22} len={rec['len']:>8}  {b}")
    time.sleep(0.6)
    return rec

print("=== PHASE 1: stackvault live catalog (re-scan, pagination + auth probes) ===")
r1 = do("sv_public", "https://decohomz.com/sv-api/products", H_JSON)
r2 = do("sv_public_limit", "https://decohomz.com/sv-api/products?limit=2000&offset=0", H_JSON)
r3 = do("sv_bearer", "https://decohomz.com/sv-api/products",
        {"Authorization": "Bearer " + KEYS["sv"], **H_JSON})
do("sv_me", "https://decohomz.com/sv-api/me",
   {"Authorization": "Bearer " + KEYS["sv"], **H_JSON})
do("sv_shop_v1_products", "https://stackvault.shop/api/v1/products",
   {"Authorization": "Bearer " + KEYS["sv"], **H_JSON})
do("sv_shop_svapi", "https://stackvault.shop/sv-api/products",
   {"Authorization": "Bearer " + KEYS["sv"], **H_JSON})

print("=== PHASE 2: entity catalogs via provided keys (READ-ONLY) ===")
# ProdSeller (base URL from research/deep_dive/prodseller_api_docs.txt)
do("ps_products", "https://prodseller.com/v1/products",
   {"X-API-Key": KEYS["ps"], **H_JSON})
do("ps_balance", "https://prodseller.com/v1/balance",
   {"X-API-Key": KEYS["ps"], **H_JSON})

# laha / ver_pixel_bot
do("laha_docs", "https://lahastore.up.railway.app/api/v1/docs")
r_laha_o = do("laha_openapi", "https://lahastore.up.railway.app/api/v1/openapi.json", H_JSON)
do("laha_products_xak", "https://lahastore.up.railway.app/api/v1/products",
   {"X-API-Key": KEYS["laha"], **H_JSON})
do("laha_products_bearer", "https://lahastore.up.railway.app/api/v1/products",
   {"Authorization": "Bearer " + KEYS["laha"], **H_JSON})

# aiversehub platform: AIVerseX + AIXpress (same base URL, two shops/keys)
do("aivx_products", "https://aiversehub.store/api/v1/products",
   {"X-API-Key": KEYS["aivx"], **H_JSON})
do("aivx_me", "https://aiversehub.store/api/v1/me",
   {"X-API-Key": KEYS["aivx"], **H_JSON})
do("aixp_products", "https://aiversehub.store/api/v1/products",
   {"X-API-Key": KEYS["aixp"], **H_JSON})
do("aixp_me", "https://aiversehub.store/api/v1/me",
   {"X-API-Key": KEYS["aixp"], **H_JSON})

# Gemini Shop / aivaulthub reseller
do("gshop_products", "https://reseller.aivaulthub.store/api/v1/products",
   {"X-API-Key": KEYS["gshop"], **H_JSON})
do("gshop_me", "https://reseller.aivaulthub.store/api/v1/me",
   {"X-API-Key": KEYS["gshop"], **H_JSON})

# acczone / Mike_E_0 — discover first
r_acz_root = do("acz_root", "https://api.acczone.xyz/", H_JSON)
do("acz_docs", "https://api.acczone.xyz/docs")
do("acz_openapi", "https://api.acczone.xyz/openapi.json", H_JSON)
do("acz_products_v1_bearer", "https://api.acczone.xyz/api/v1/products",
   {"Authorization": "Bearer " + KEYS["acz"], **H_JSON})
do("acz_products_v1_xak", "https://api.acczone.xyz/api/v1/products",
   {"X-API-Key": KEYS["acz"], **H_JSON})

print("=== PHASE 3: passive probes (gemini12pro + infra) ===")
do("g12_channel", "https://t.me/s/gemini12pro_channel")
do("g12_user", "https://t.me/gemini12pro")
do("g12_bot", "https://t.me/gemini12pro_bot")
do("decohomz_root", "https://decohomz.com/")

# ---------- compact summary ----------
print("\n=== SUMMARY ===")
def get_products(rec):
    ok, j = jparse(rec)
    if not ok: return None
    if isinstance(j, list): return j
    if isinstance(j, dict):
        for k in ("products", "data", "items", "result"):
            v = j.get(k)
            if isinstance(v, list): return v
            if isinstance(v, dict) and isinstance(v.get("products"), list): return v["products"]
    return None

sv = get_products(r1) or get_products(r2) or get_products(r3)
if sv is not None:
    from collections import Counter
    pref = Counter(str(it.get("id") or it.get("_id") or "").split("_")[0] for it in sv)
    print(f"SV LIVE TOTAL = {len(sv)} | prefixes = {dict(pref)}")
else:
    print("SV LIVE: FAILED to parse products")

for nm, rec in [("ps_products", None), ("laha_products_xak", None), ("laha_products_bearer", None),
                ("aivx_products", None), ("aixp_products", None), ("gshop_products", None),
                ("acz_products_v1_bearer", None), ("acz_products_v1_xak", None)]:
    rec = next((f for f in results["fetches"] if f["name"] == nm), None)
    if not rec: continue
    prods = get_products(rec)
    if prods is not None:
        print(f"{nm}: OK n={len(prods)} | sample={json.dumps(prods[0], ensure_ascii=False)[:180] if prods else '-'}")
    else:
        print(f"{nm}: http={rec['http']} no-product-list | body[:120]={(rec.get('body') or '')[:120]!r}")

# gemini12pro channel: last post time
g12 = next((f for f in results["fetches"] if f["name"] == "g12_channel"), None)
if g12 and g12.get("body"):
    times = re.findall(r'datetime="([\d\-T:+]+)"', g12["body"])
    print(f"g12_channel: http={g12['http']} posts_seen={len(times)} last_datetime={times[-1] if times else None}")

with open(OUT, "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print(f"\nSaved -> {OUT}  ({len(results['fetches'])} fetch records)")
