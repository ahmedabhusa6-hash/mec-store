#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R3 — NEW KEYS PROBE WAVE (user delivery #2, 02/10):
  A. PremiKey (@PremiKeyBot — HitMeow/VN cluster): canboso.com swagger + /api/v2/telegram-buyer/products (key tgb_)
  B. DigitalCore (@DCoreStoreBot): digitalcore.top buyer API /api/user/* (key UUID) — docs already discovered endpoints (Api-Key)
  C. AIXpress (@AIXpress_Bot — IN cluster): aiversehub.store /api/v1/* with REGENERATED key (old was 401)
  D. RichAIStore (@RichAIStoreBot — IN cluster): cgpt-active.pro/telegram/api/docs + integration page + products (Bearer rsk_)
READ-ONLY: GET requests only. NO purchase POSTs. User-authorized keys.
Output: research/g1_r3_newkeys_raw_20261002.json
"""
import json, re, time, gzip
import urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))
OUT = "/home/z/my-project/research/g1_r3_newkeys_raw_20261002.json"

KEYS = {
    "premikey": "tgb_61210be8d27595ef167d92cbaa26c7d3c970047e87447081",
    "digitalcore": "36a343bb-04eb-41c5-8a44-cf7832ef4a44",
    "aixpress": "AK_CjB0ZEhGDLd7x97ACNYNjDR9wQgDxi7W",
    "richai": "rsk_87Qn6jtkALbxPc5Y_gmyJT3UwRfbyRgG",
}

def fetch(name, url, headers=None, timeout=25):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    rec = {"name": name, "url": url, "http": None, "err": None, "len": 0, "body": None, "hdrs": None,
           "ts": datetime.now(TZ).isoformat()[:19]}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                try: raw = gzip.decompress(raw)
                except Exception: pass
            rec["body"] = raw.decode("utf-8", "replace"); rec["http"] = r.status; rec["len"] = len(rec["body"])
            rec["hdrs"] = dict(list(r.headers.items())[:14])
    except urllib.error.HTTPError as e:
        try: rec["body"] = e.read().decode("utf-8", "replace")
        except Exception: rec["body"] = None
        rec["http"] = e.code; rec["err"] = "HTTPError"; rec["len"] = len(rec["body"] or "")
        rec["hdrs"] = dict(list(e.headers.items())[:14]) if e.headers else None
    except Exception as e:
        rec["err"] = f"{type(e).__name__}: {str(e)[:120]}"
    return rec

out = {"execution_timestamp": datetime.now(TZ).isoformat(),
       "scope": "G-1 R3 new-keys probe (read-only GETs, no purchases)",
       "probes": []}

def do(name, url, headers=None, quiet=False):
    rec = fetch(name, url, headers)
    out["probes"].append(rec)
    b = (rec.get("body") or "")[:100].replace("\n", " ")
    if not quiet:
        print(f"  [{rec['http']}] {name:34} len={rec['len']:>7}  {b[:88]}")
    time.sleep(0.5)
    return rec

def try_json(rec):
    if rec.get("http") == 200 and rec.get("body") and rec["body"].lstrip()[:1] in "[{":
        try: return json.loads(rec["body"])
        except Exception: return None
    return None

# ============================================================
print("=== A. PremiKey / canboso.com (HitMeow VN cluster) ===")
r_root = do("canboso_root", "https://canboso.com/")
r_swagger_html = do("canboso_swagger_html", "https://canboso.com/api/swagger")

# extract swagger JSON url from the HTML
swagger_json_url = None
for rec in (r_swagger_html, r_root):
    body = rec.get("body") or ""
    m = (re.search(r'url:\s*["\x27]([^"\x27]+swagger[^"\x27]*\.json[^"\x27]*)["\x27]', body)
         or re.search(r'["\x27](/[^"\x27]*swagger[^"\x27]*\.json[^"\x27]*)["\x27]', body)
         or re.search(r'configUrl\s*=\s*["\x27]([^"\x27]+)["\x27]', body))
    if m:
        swagger_json_url = m.group(1)
        if swagger_json_url.startswith("/"):
            swagger_json_url = "https://canboso.com" + swagger_json_url
        break
print(f"  [A] swagger JSON url extracted: {swagger_json_url}")

canboso_spec = None
if swagger_json_url:
    r_swj = do("canboso_swagger_json", swagger_json_url)
    canboso_spec = try_json(r_swj)

# fallback common swagger json paths
if canboso_spec is None:
    for cand in ["/api/swagger/v1/swagger.json", "/swagger/v1/swagger.json", "/api/swagger.json",
                 "/api/docs/swagger.json", "/api/swagger/docs/v1"]:
        r_c = do(f"canboso_swjson_{cand.replace('/','_')[:30]}", "https://canboso.com" + cand, quiet=True)
        canboso_spec = try_json(r_c)
        if canboso_spec is not None:
            swagger_json_url = r_c["url"]; break

# enumerate endpoints from spec
premi_endpoints = []
if canboso_spec:
    for path, ops in (canboso_spec.get("paths") or {}).items():
        for meth, op in ops.items():
            if isinstance(op, dict):
                premi_endpoints.append({"method": meth.upper(), "path": path, "op": op.get("operationId", ""),
                                        "summary": (op.get("summary") or op.get("description") or "")[:80]})
    sec = canboso_spec.get("securityDefinitions") or canboso_spec.get("components", {}).get("securitySchemes")
    print(f"  [A] SPEC: title={canboso_spec.get('info',{}).get('title')} ver={canboso_spec.get('info',{}).get('version')} "
          f"paths={len(premi_endpoints)} security={json.dumps(sec)[:200]}")
    for e in premi_endpoints[:25]:
        print(f"      {e['method']:5} {e['path']:55} {e['summary'][:45]}")

# products with auth scheme discovery (READ-ONLY GET)
auth_schemes = [
    ("X-API-Key", {"X-API-Key": KEYS["premikey"]}),
    ("Bearer",    {"Authorization": "Bearer " + KEYS["premikey"]}),
    ("Api-Key",   {"Api-Key": KEYS["premikey"]}),
    ("apikey-hdr",{"apikey": KEYS["premikey"]}),
    ("query",     None),  # via url param
]
premi_products = None
premi_working_auth = None
for scheme, hdrs in auth_schemes:
    url = "https://canboso.com/api/v2/telegram-buyer/products"
    if scheme == "query":
        url += "?api_key=" + KEYS["premikey"]
    r_p = do(f"premi_products_{scheme}", url, hdrs, quiet=(scheme != "X-API-Key"))
    premi_products = try_json(r_p)
    if premi_products is not None:
        premi_working_auth = scheme
        print(f"  [A] PRODUCTS OK via {scheme} -> {json.dumps(premi_products, ensure_ascii=False)[:180]}")
        break
    if r_p.get("http") not in (401, 403, 404, None):
        # non-auth error: stop trying
        break
if premi_products is None:
    print("  [A] products: no auth scheme worked (or endpoint blocked)")

# me/balance endpoints (read-only) — from spec if available
for ep in ["/api/v2/telegram-buyer/me", "/api/v2/telegram-buyer/wallet", "/api/v2/telegram-buyer/balance"]:
    if canboso_spec and not any(e["path"] == ep for e in premi_endpoints):
        continue
    if premi_working_auth:
        hdrs = dict(auth_schemes[[s[0] for s in auth_schemes].index(premi_working_auth)][1] or {})
        do(f"premi{ep.replace('/','_')[:34]}", "https://canboso.com" + ep, hdrs or None)

# ============================================================
print("\n=== B. DigitalCore / digitalcore.top buyer API (Api-Key per docs) ===")
dc_auth_variants = [
    ("ApiKey",  {"Api-Key": KEYS["digitalcore"]}),
    ("Bearer",  {"Authorization": "Bearer " + KEYS["digitalcore"]}),
    ("XAPIKey", {"X-API-Key": KEYS["digitalcore"]}),
]
dc_products = None; dc_me = None; dc_auth = None
for scheme, hdrs in dc_auth_variants:
    r_me = do(f"dc_user_me_{scheme}", "https://digitalcore.top/api/user/me", hdrs, quiet=(scheme != "ApiKey"))
    if r_me.get("http") == 200:
        dc_auth = scheme
        dc_me = try_json(r_me) or r_me.get("body", "")[:400]
        print(f"  [B] /api/user/me OK via {scheme}: {json.dumps(dc_me, ensure_ascii=False)[:200] if not isinstance(dc_me,str) else dc_me}")
        break
if dc_auth:
    hdrs = dict(dc_auth_variants[[s[0] for s in dc_auth_variants].index(dc_auth)][1])
    r_pr = do("dc_user_products", "https://digitalcore.top/api/user/products", hdrs)
    dc_products = try_json(r_pr)
    if dc_products is not None:
        n = len(dc_products) if isinstance(dc_products, list) else len(dc_products.get("products") or dc_products.get("data") or [])
        print(f"  [B] buyer catalog fetched: {n} items")
else:
    print("  [B] /api/user/me: no auth scheme returned 200")

# ============================================================
print("\n=== C. AIXpress regenerated key / aiversehub.store ===")
r_ax_me = do("aix_me_newkey", "https://aiversehub.store/api/v1/me", {"X-API-Key": KEYS["aixpress"]})
ax_me = try_json(r_ax_me)
if ax_me is not None:
    print(f"  [C] KEY VALID: {json.dumps(ax_me, ensure_ascii=False)[:200]}")
r_ax_pr = do("aix_products_newkey", "https://aiversehub.store/api/v1/products", {"X-API-Key": KEYS["aixpress"]})
ax_products = try_json(r_ax_pr)
if ax_products is not None:
    n = len(ax_products) if isinstance(ax_products, list) else len(ax_products.get("products") or ax_products.get("data") or [])
    print(f"  [C] AIXpress catalog: {n} items")

# ============================================================
print("\n=== D. RichAIStore / cgpt-active.pro (Bearer rsk_) ===")
r_rich_docs = do("richai_docs", "https://cgpt-active.pro/telegram/api/docs")
r_rich_int = do("richai_integration", "https://cgpt-active.pro/telegram/api/integration")
r_rich_root = do("cgptactive_root", "https://cgpt-active.pro/")

# extract endpoint hints from docs html
rich_hints = []
for rec in (r_rich_docs, r_rich_int):
    body = rec.get("body") or ""
    for m in re.findall(r'/telegram/api/[a-zA-Z0-9_\-/{}\.]*|/api/v\d/[a-zA-Z0-9_\-/{}\.]*', body):
        if m not in rich_hints: rich_hints.append(m)
    # also look for curl examples
    for m in re.findall(r'curl[^<\n]{10,150}', body):
        rich_hints.append("CURL: " + m[:140])
print(f"  [D] endpoint hints ({len(rich_hints)}):")
for h in rich_hints[:25]: print("      ", h[:130])

# try common products paths with Bearer
rich_products = None
cands = [p if p.startswith("http") else "https://cgpt-active.pro" + p for p in [
    "/telegram/api/v1/products", "/telegram/api/products", "/api/v1/products",
    "/telegram/api/v1/me", "/telegram/api/me"]]
seen = set()
for url in cands:
    if url in seen: continue
    seen.add(url)
    r_r = do(f"richai_probe{url.split('.pro')[1][:28].replace('/','_')}", url,
             {"Authorization": "Bearer " + KEYS["richai"]})
    j = try_json(r_r)
    if j is not None:
        rich_products = (url, j)
        print(f"  [D] OK {url} -> {json.dumps(j, ensure_ascii=False)[:170]}")
        break

out["keys_used"] = {k: (v[:8] + "..." + v[-4:]) for k, v in KEYS.items()}
out["discovery"] = {
    "premikey_swagger_json_url": swagger_json_url,
    "premikey_endpoints": premi_endpoints,
    "premikey_working_auth": premi_working_auth,
    "digitalcore_working_auth": dc_auth,
    "richai_endpoint_hints": rich_hints,
    "richai_products_url": rich_products[0] if rich_products else None,
}
with open(OUT, "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"\nSaved -> {OUT}  ({len(out['probes'])} probes)")
