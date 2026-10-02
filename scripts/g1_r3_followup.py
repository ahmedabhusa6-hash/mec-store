#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R3 — FOLLOW-UP:
  F1  AIXpress full catalog (aixpress.shop, response key = "services") + diff vs AIVerseX + vs cb_
  F2  RichAI openapi.json — full API surface
  F3  canboso.com root HTML anatomy + swagger retry
  F4  DNS/IP hosting topology: canboso · prodseller · aixpress · aiversehub · cgpt-active · digitalcore · stackvault
  F5  PremiKey balance full response + promotions sample (payment rails signals)
READ-ONLY."""
import json, re, gzip, socket, time
import urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))
OUT = "/home/z/my-project/research/g1_r3_followup_20261002.json"
KEYS = {"aixpress": "AK_CjB0ZEhGDLd7x97ACNYNjDR9wQgDxi7W", "richai": "rsk_87Qn6jtkALbxPc5Y_gmyJT3UwRfbyRgG",
        "premikey": "tgb_61210be8d27595ef167d92cbaa26c7d3c970047e87447081"}

def fetch(url, headers=None, timeout=25):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                try: raw = gzip.decompress(raw)
                except Exception: pass
            return r.status, raw.decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        try: return e.code, e.read().decode("utf-8", "replace"), dict(e.headers)
        except Exception: return e.code, "", {}
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:100]}", {}

def nk(t):
    import unicodedata
    t = unicodedata.normalize("NFKC", t or "").lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

out = {"execution_timestamp": datetime.now(TZ).isoformat(), "tests": {}}

# ---------- F1: AIXpress full catalog ----------
print("=== F1: AIXpress catalog (aixpress.shop) ===")
st, body, _ = fetch("https://aixpress.shop/api/v1/products", {"X-API-Key": KEYS["aixpress"]})
ax_items = []
if st == 200:
    j = json.loads(body)
    ax_items = j.get("services") or j.get("products") or j.get("data") or []
    print(f"  keys in response: {list(j.keys())} · services n={len(ax_items)}")
    if ax_items:
        print(f"  sample keys: {list(ax_items[0].keys())}")
        print(f"  sample: {json.dumps(ax_items[0], ensure_ascii=False)[:260]}")
        for it in ax_items[:8]:
            print(f"    - {it.get('name')[:52]:52} ${it.get('price')} stock={it.get('stock')}")
# diff vs AIVerseX (R2) and vs cb_
r2 = json.load(open("/home/z/my-project/research/g1_rescan_analysis_20261002.json"))
aivx = r2["entity_catalogs"]["aivx_aiversehub"]["items"]
aivx_names = {nk(i.get("name")) for i in aivx}
ax_names = {nk(i.get("name")) for i in ax_items}
both = aivx_names & ax_names
sv_live = json.load(open("/home/z/my-project/research/g1_cb_live_catalog_20261002.json"))["products"]
sv_cb = [p for p in sv_live if str(p["id"]).startswith("cb_")]
cb_names = {nk(p.get("name")) for p in sv_cb}
ax_cb = ax_names & cb_names
print(f"  AIXpress({len(ax_names)}) vs AIVerseX({len(aivx_names)}): common={len(both)} aix-only={len(ax_names-aivx_names)} aivx-only={len(aivx_names-ax_names)}")
if ax_names - aivx_names: print(f"    aix-only sample: {sorted(ax_names - aivx_names)[:8]}")
if aivx_names - ax_names: print(f"    aivx-only sample: {sorted(aivx_names - ax_names)[:8]}")
print(f"  AIXpress vs cb_ name matches: {len(ax_cb)}")
out["tests"]["F1"] = {"n": len(ax_items), "sample": ax_items[0] if ax_items else None,
                      "response_key": "services",
                      "vs_aiversex": {"common": len(both), "aix_only": sorted(ax_names - aivx_names)[:20], "aivx_only": sorted(aivx_names - ax_names)[:20]},
                      "vs_cb_matches": len(ax_cb), "vs_cb_samples": sorted(ax_cb)[:12]}

# ---------- F2: RichAI openapi ----------
print("\n=== F2: RichAI openapi.json ===")
st2, body2, _ = fetch("https://cgpt-active.pro/telegram/api/openapi.json")
rich_eps = []
if st2 == 200 and body2.lstrip()[:1] == "{":
    spec = json.loads(body2)
    for path, ops in (spec.get("paths") or {}).items():
        for meth, op in ops.items():
            if isinstance(op, dict):
                rich_eps.append(f"{meth.upper()} {path} :: {(op.get('summary') or op.get('description') or '')[:60]}")
    print(f"  title: {spec.get('info',{}).get('title')} ver: {spec.get('info',{}).get('version')}")
    print(f"  endpoints ({len(rich_eps)}):")
    for e in rich_eps: print(f"    {e[:100]}")
    servers = spec.get("servers") or spec.get("host")
    print(f"  servers: {servers}")
    out["tests"]["F2"] = {"title": spec.get("info",{}).get("title"), "version": spec.get("info",{}).get("version"),
                          "servers": servers, "endpoints": rich_eps}
else:
    print(f"  openapi fetch failed: {st2} {body2[:100]}")
    out["tests"]["F2"] = {"http": st2, "err": body2[:120] if body2 else None}

# ---------- F3: canboso anatomy ----------
print("\n=== F3: canboso.com anatomy ===")
st3, body3, h3 = fetch("https://canboso.com/")
if body3:
    title = re.search(r"<title>(.*?)</title>", body3, re.S)
    metas = re.findall(r'<meta[^>]*(?:name|property)="([^"]+)"[^>]*content="([^"]{0,120})"', body3)
    scripts = re.findall(r'src="([^"]+\.js[^"]*)"', body3)
    print(f"  title: {title.group(1).strip() if title else None}")
    print(f"  metas: {metas[:8]}")
    print(f"  scripts: {scripts[:6]}")
    out["tests"]["F3"] = {"title": title.group(1).strip() if title else None, "metas": metas[:10], "scripts": scripts[:8]}
# swagger retries
for cand in ["/api/swagger/index.html", "/swagger/index.html", "/api/swagger/v2/swagger.json",
             "/api-docs", "/api/v2/swagger.json", "/api/swagger/ui"]:
    s, b, _ = fetch("https://canboso.com" + cand)
    ok = s == 200 and len(b) > 200
    print(f"  [{s}] {cand} len={len(b)}{'  <== FOUND' if ok else ''}")
    if ok and b.lstrip()[:1] in "{[":
        try:
            spec = json.loads(b)
            eps = [f"{m.upper()} {p}" for p, ops in (spec.get('paths') or {}).items() for m in ops]
            out["tests"]["F3"]["swagger"] = {"url": cand, "endpoints": eps[:30]}
            print(f"       SWAGGER SPEC: {len(eps)} endpoints: {eps[:20]}")
            break
        except Exception: pass

# ---------- F4: DNS/IP hosting topology ----------
print("\n=== F4: hosting topology (DNS A records) ===")
domains = ["canboso.com", "prodseller.com", "aixpress.shop", "aiversehub.store", "reseller.aivaulthub.store",
           "cgpt-active.pro", "digitalcore.top", "stackvault.shop", "gpt.teamsoclo.site", "lahastore.up.railway.app"]
ip_map = {}
for d in domains:
    try:
        ips = sorted({ai[4][0] for ai in socket.getaddrinfo(d, 443, socket.AF_INET) if ai})
        ip_map[d] = ips
        print(f"  {d:32} -> {ips}")
    except Exception as e:
        ip_map[d] = f"ERR {type(e).__name__}"
        print(f"  {d:32} -> ERR {type(e).__name__}")
    time.sleep(0.2)
# reverse: shared IPs?
by_ip = {}
for d, ips in ip_map.items():
    if isinstance(ips, list):
        for ip in ips: by_ip.setdefault(ip, []).append(d)
shared = {ip: ds for ip, ds in by_ip.items() if len(ds) > 1}
print(f"\n  SHARED IPs: {shared if shared else 'none (all separate hosts)'}")
out["tests"]["F4"] = {"ip_map": ip_map, "shared_ips": shared}

# ---------- F5: PremiKey balance + promotions ----------
print("\n=== F5: PremiKey wallet/promotions signals ===")
st5, body5, _ = fetch("https://canboso.com/api/v2/telegram-buyer/balance", {"X-API-Key": KEYS["premikey"]})
if st5 == 200:
    bal = json.loads(body5)
    print(f"  balance response: {json.dumps(bal, ensure_ascii=False)[:400]}")
    out["tests"]["F5"] = {"balance": bal}
# a product with promotions
st6, body6, _ = fetch("https://canboso.com/api/v2/telegram-buyer/products", {"X-API-Key": KEYS["premikey"]})
if st6 == 200:
    prods = json.loads(body6).get("products", [])
    withpromo = [p for p in prods if p.get("promotions")]
    print(f"  products with promotions: {len(withpromo)}/{len(prods)}")
    if withpromo:
        print(f"  promo sample: {json.dumps(withpromo[0], ensure_ascii=False)[:400]}")
        out["tests"]["F5"]["promotions_sample"] = withpromo[0]
    # price structure anatomy
    p0 = prods[0]
    out["tests"]["F5"]["price_structure"] = p0.get("price")
    out["tests"]["F5"]["availability_structure"] = p0.get("availability")
    print(f"  price structure: {json.dumps(p0.get('price'), ensure_ascii=False)[:150]}")
    print(f"  availability structure: {json.dumps(p0.get('availability'), ensure_ascii=False)[:150]}")

with open(OUT, "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"\nSaved -> {OUT}")
