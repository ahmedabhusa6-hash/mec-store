#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R3 — ANALYSIS & MATCHING (new keys wave):
  P1  PremiKey/canboso catalog: shape, size, ObjectId hexes
  P2  THE DECISIVE TEST: premi hexes ∩ (cb_ ∪ ps_archived) ObjectIds -> same DB?
  P3  name matching premi vs cb_ live (229)
  P4  RichAI/cgpt-active catalog: shape + name matching vs cb_
  P5  DigitalCore buyer vs public catalog diff + tier prices
  P6  AIXpress new key retry on aixpress.shop base (fallback)
  P7  topology: schema fingerprints (canboso v2 / richai / dc / prodseller v1)
Output: research/g1_r3_newkeys_analysis_20261002.json
READ-ONLY."""
import json, re, gzip, time, unicodedata
import urllib.request, urllib.error
from collections import Counter
from datetime import datetime, timezone, timedelta

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
TZ = timezone(timedelta(hours=3))
OUT = "/home/z/my-project/research/g1_r3_newkeys_analysis_20261002.json"
RAW = json.load(open("/home/z/my-project/research/g1_r3_newkeys_raw_20261002.json"))
KEYS = {"aixpress": "AK_CjB0ZEhGDLd7x97ACNYNjDR9wQgDxi7W", "richai": "rsk_87Qn6jtkALbxPc5Y_gmyJT3UwRfbyRgG"}

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
            return r.status, raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try: return e.code, e.read().decode("utf-8", "replace")
        except Exception: return e.code, ""
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:100]}"

def nk(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def body_of(name):
    return next((p["body"] for p in RAW["probes"] if p["name"] == name and p.get("body")), None)

res = {"execution_timestamp": datetime.now(TZ).isoformat(), "tests": {}}

# ---------- load SV corpora ----------
sv_live = json.load(open("/home/z/my-project/research/g1_cb_live_catalog_20261002.json"))["products"]
sv_cb = [p for p in sv_live if str(p["id"]).startswith("cb_")]
sv_ps_live = [p for p in sv_live if str(p["id"]).startswith("ps_")]
sv_mr = [p for p in sv_live if str(p["id"]).startswith("mr_")]
print(f"SV live: {len(sv_live)} (cb_ {len(sv_cb)} · ps_ {len(sv_ps_live)} · mr_ {len(sv_mr)})")

# archived pre-migration catalog (357, with ps_/mr_)
try:
    sv_arch = json.load(open("/home/z/my-project/research/stackvault_live/sv_products_current.json"))
    arch_products = sv_arch.get("products", sv_arch if isinstance(sv_arch, list) else [])
    arch_ps = [p for p in arch_products if str(p.get("id", "")).startswith("ps_")]
    print(f"SV archive (pre-migration): {len(arch_products)} products (ps_ {len(arch_ps)})")
except Exception as e:
    arch_products, arch_ps = [], []
    print("archive load err:", e)

def hexof(pid):  # cb_68f0... -> 68f0...
    s = str(pid)
    return s[3:] if re.fullmatch(r"(cb|ps|mr)_[0-9a-f]{24}", s) else (s if re.fullmatch(r"[0-9a-f]{24}", s) else None)

cb_hexes = {hexof(p["id"]) for p in sv_cb if hexof(p["id"])}
ps_live_hexes = {hexof(p["id"]) for p in sv_ps_live if hexof(p["id"])}
ps_arch_hexes = {hexof(p["id"]) for p in arch_ps if hexof(p["id"])}
all_sv_hexes = cb_hexes | ps_live_hexes | ps_arch_hexes
print(f"hex sets: cb_={len(cb_hexes)} ps_live={len(ps_live_hexes)} ps_arch={len(ps_arch_hexes)} union={len(all_sv_hexes)}")

cb_by_name = {}
for p in sv_cb: cb_by_name.setdefault(nk(p.get("name")), []).append(p)

# ---------- P1/P2/P3: PremiKey ----------
print("\n" + "=" * 60 + "\nP1-P3: PremiKey / canboso.com")
premi_raw = json.loads(body_of("premi_products_X-API-Key"))
premi = premi_raw.get("products") or []
print(f"[P1] premi catalog: {len(premi)} products · top-level keys: {list(premi_raw.keys())}")
if premi:
    print(f"     sample keys: {list(premi[0].keys())}")
    print(f"     sample[0]: {json.dumps(premi[0], ensure_ascii=False)[:340]}")
premi_meta = {k: v for k, v in premi_raw.items() if k != "products"}
premi_hexes = {}
for it in premi:
    h = hexof(it.get("productId") or it.get("id") or "")
    if h: premi_hexes[h] = it

inter_cb = set(premi_hexes) & cb_hexes
inter_ps_live = set(premi_hexes) & ps_live_hexes
inter_ps_arch = set(premi_hexes) & ps_arch_hexes
inter_any = set(premi_hexes) & all_sv_hexes
print(f"\n[P2] *** DECISIVE ObjectId TEST ***")
print(f"     premi hex-24 count: {len(premi_hexes)}/{len(premi)}")
print(f"     ∩ cb_(229)         = {len(inter_cb)}")
print(f"     ∩ ps_live(20)      = {len(inter_ps_live)}")
print(f"     ∩ ps_archived(319) = {len(inter_ps_arch)}")
print(f"     ∩ ANY SV hex       = {len(inter_any)}")
if inter_any:
    print("     MATCHED SAMPLES:")
    for h in list(inter_any)[:10]:
        sv_p = next((p for p in sv_cb + sv_ps_live if hexof(p['id']) == h), None) or \
               next((p for p in arch_ps if hexof(p['id']) == h), None)
        pr = premi_hexes[h]
        print(f"       hex={h} | SV: {(sv_p or {}).get('name','?')[:44]} ${str((sv_p or {}).get('price','?'))[:7]} | premi: {pr.get('name','?')[:44]} ${str(pr.get('price', pr.get('priceFrom','?')))[:7]}")

# name matching (premi price is a NESTED object {amount: x} — extract properly)
def price_of(it):
    p = it.get("price")
    if isinstance(p, dict): return p.get("amount")
    if isinstance(p, (int, float)): return p
    return it.get("priceFrom")

premi_by_name = {}
for it in premi: premi_by_name.setdefault(nk(it.get("name")), []).append(it)
name_inter = set(cb_by_name) & set(premi_by_name)
print(f"\n[P3] name matches premi({len(premi_by_name)} uniq) vs cb_({len(cb_by_name)} uniq) = {len(name_inter)}")
nm_samples = []; price_ratios = []
for k in sorted(name_inter):
    c = cb_by_name[k][0]; p = premi_by_name[k][0]
    pp = price_of(p)
    nm_samples.append({"cb_name": c.get("name"), "cb_price": c.get("price"),
                       "premi_price": pp, "premi_availability": p.get("availability"),
                       "premi_productType": p.get("productType")})
    try:
        if c.get("price") and pp: price_ratios.append(float(c["price"]) / float(pp))
    except Exception: pass
for m in nm_samples[:18]:
    print(f"   ~ {m['cb_name'][:46]:46} cb=${str(m['cb_price'])[:6]:6} premi=${str(m['premi_price'])[:7]:7} avail={str(m['premi_availability'])[:10]}")
if price_ratios:
    price_ratios.sort()
    print(f"\n[P3a] cb_/premi price ratio on {len(price_ratios)} matches: min={price_ratios[0]:.2f} p25={price_ratios[len(price_ratios)//4]:.2f} med={price_ratios[len(price_ratios)//2]:.2f} p75={price_ratios[3*len(price_ratios)//4]:.2f} max={price_ratios[-1]:.2f}")

# P8: LINEAGE TEST — is the canboso overlap cb_-specific or whole-SV-catalog lineage?
arch_ps_names = {nk(p.get("name")) for p in arch_ps if p.get("name")}
premi_arch_inter = arch_ps_names & set(premi_by_name)
cb_matched_names = set(name_inter)
ps_matched_names = set(premi_arch_inter)
print(f"\n[P8] LINEAGE TEST: canboso(348 uniq) ∩ archived-ps_({len(arch_ps_names)} uniq) = {len(premi_arch_inter)}")
print(f"     canboso ∩ cb_ = {len(name_inter)} · of which also in archived ps_: {len(cb_matched_names & arch_ps_names)}")
print(f"     arch-ps_-matched names NOT in cb_: {len(ps_matched_names - cb_matched_names)}")
print(f"     overlap pattern: {'WHOLE-LINEAGE sibling catalogs' if len(premi_arch_inter) >= len(name_inter) else 'cb_-ENRICHED (specific recent link)'}")
res["tests"]["P8"] = {"premi_cap_arch_ps": len(premi_arch_inter), "premi_cap_cb": len(name_inter),
                      "cb_matched_in_arch_ps": len(cb_matched_names & arch_ps_names),
                      "arch_ps_n": len(arch_ps_names),
                      "arch_matched_not_in_cb": len(ps_matched_names - cb_matched_names)}

# P9: description fingerprint comparison on matched pairs
VN_DOMAINS = ["teamsoclo", "bddevlab", "vibi.top", "phh.info.vn", "dongvanfb", "mailtemp", "gpmloginapp", "2fa.live", "lartai", "get-opt"]
fp_stats = {d: {"cb": 0, "premi": 0, "both": 0} for d in VN_DOMAINS}
desc_same = 0; desc_diff_examples = []
for k in name_inter:
    c = cb_by_name[k][0]; p = premi_by_name[k][0]
    cd = (c.get("description") or "").lower(); pd = (p.get("description") or "").lower()
    if cd and pd:
        if cd.strip() == pd.strip(): desc_same += 1
        elif len(desc_diff_examples) < 6: desc_diff_examples.append({"name": c.get("name")[:40], "cb_desc": cd[:130], "premi_desc": pd[:130]})
    for d in VN_DOMAINS:
        inc = d in cd; inp = d in pd
        if inc: fp_stats[d]["cb"] += 1
        if inp: fp_stats[d]["premi"] += 1
        if inc and inp: fp_stats[d]["both"] += 1
print(f"\n[P9] DESC COMPARISON on {len(name_inter)} name-matched pairs: identical={desc_same}")
print("     VN-domain fingerprints (cb_ / premi / both):")
for d, s in fp_stats.items():
    if s["cb"] or s["premi"]: print(f"       {d:12} cb_={s['cb']:3} premi={s['premi']:3} both={s['both']:3}")
for e in desc_diff_examples[:4]:
    print(f"     DIFF ex: {e['name']}")
    print(f"        cb_  : {e['cb_desc'][:100]}")
    print(f"        premi: {e['premi_desc'][:100]}")
res["tests"]["P9"] = {"identical_desc": desc_same, "pairs_compared": len(name_inter), "fp_stats": fp_stats,
                      "desc_diff_examples": desc_diff_examples}

# family coverage
fams = ["grok", "gmail", "facebook", "lovable", "aws", "kling", "lart", "capcut", "perplexity", "claude",
        "chatgpt", "gemini", "netflix", "spotif", "canva", "duolingo", "coursera", "notion", "midjourney"]
premi_text = " || ".join(json.dumps(it, ensure_ascii=False) for it in premi).lower()
cb_text = " || ".join((p.get("name") or "") + " " + (p.get("description") or "") for p in sv_cb).lower()
cov = {f: {"premi": f in premi_text, "cb_": f in cb_text} for f in fams}
print(f"\n[P3b] family coverage (premi / cb_): " + " · ".join(f"{f}:{'Y' if v['premi'] else '-'}{'Y' if v['cb_'] else '-'}" for f, v in cov.items()))

res["tests"]["P1"] = {"n": len(premi), "meta": premi_meta, "id_format": "mongo-hex-24 productId",
                      "fields": list(premi[0].keys()) if premi else []}
res["tests"]["P2"] = {"premi_hex_n": len(premi_hexes), "inter_cb": len(inter_cb), "inter_ps_live": len(inter_ps_live),
                      "inter_ps_arch": len(inter_ps_arch), "inter_any": len(inter_any),
                      "samples": [{"hex": h, "sv_name": (next((p for p in sv_cb + sv_ps_live + arch_ps if hexof(p.get('id','')) == h), {}) or {}).get("name"),
                                   "premi_name": premi_hexes[h].get("name")} for h in list(inter_any)[:12]]}
res["tests"]["P3"] = {"name_matches": len(name_inter), "samples": nm_samples, "family_coverage": cov,
                      "price_ratio": ({"n": len(price_ratios), "min": round(price_ratios[0],3), "p25": round(price_ratios[len(price_ratios)//4],3), "median": round(price_ratios[len(price_ratios)//2],3), "p75": round(price_ratios[3*len(price_ratios)//4],3), "max": round(price_ratios[-1],3)} if price_ratios else None)}

# ---------- P4: RichAI ----------
print("\n" + "=" * 60 + "\nP4: RichAIStore / cgpt-active.pro")
rich_raw = json.loads(body_of("richai_probe_telegram_api_v1_products"))
rich = rich_raw.get("products") or []
print(f"[P4] rich catalog: {len(rich)} products · keys: {list(rich_raw.keys())}")
if rich:
    print(f"     sample keys: {list(rich[0].keys())}")
    print(f"     sample[0]: {json.dumps(rich[0], ensure_ascii=False)[:300]}")
rich_by_name = {}
for it in rich: rich_by_name.setdefault(nk(it.get("name")), []).append(it)
rich_inter = set(cb_by_name) & set(rich_by_name)
print(f"     name matches rich({len(rich_by_name)} uniq) vs cb_({len(cb_by_name)} uniq) = {len(rich_inter)}")
rich_nm = []
for k in sorted(rich_inter)[:20]:
    c = cb_by_name[k][0]; r = rich_by_name[k][0]
    rich_nm.append({"cb_name": c.get("name"), "cb_price": c.get("price"), "rich_name": r.get("name"),
                    "rich_price": r.get("price"), "rich_stock": r.get("stock")})
    print(f"   ~ {c.get('name')[:44]:44} cb=${str(c.get('price'))[:6]:6} rich=${str(r.get('price'))[:7]:7}")
rich_ids = [str(it.get("id")) for it in rich]
rich_hex = sum(1 for i in rich_ids if re.fullmatch(r"[0-9a-f]{24}", i))
rich_text = " || ".join(json.dumps(it, ensure_ascii=False) for it in rich).lower()
rich_cov = {f: (f in rich_text, f in cb_text) for f in fams}
print(f"     id formats: numeric={sum(1 for i in rich_ids if i.isdigit())} mongo-hex={rich_hex} other={len(rich_ids)-sum(1 for i in rich_ids if i.isdigit())-rich_hex}")
print(f"     families (rich/cb_): " + " · ".join(f"{f}:{'Y' if a else '-'}{'Y' if b else '-'}" for f, (a, b) in rich_cov.items()))
res["tests"]["P4"] = {"n": len(rich), "name_matches": len(rich_inter), "samples": rich_nm,
                      "id_format": {"numeric": sum(1 for i in rich_ids if i.isdigit()), "mongo_hex": rich_hex},
                      "family_coverage": {f: {"rich": a, "cb": b} for f, (a, b) in rich_cov.items()}}

# ---------- P5: DigitalCore buyer vs public ----------
print("\n" + "=" * 60 + "\nP5: DigitalCore buyer catalog vs public")
dc_buyer = json.loads(body_of("dc_user_products"))
dc_pub = json.load(open("/home/z/my-project/research/g1_digitalcore_match_20261002.json"))["dc_catalog"]
print(f"[P5] buyer={len(dc_buyer)} public={len(dc_pub)}")
dc_diff = {"same_n": len(dc_buyer) == len(dc_pub)}
bmap = {nk(b.get("name")): b for b in dc_buyer}
name_pairs = []
for p in dc_pub:
    b = bmap.get(nk(p.get("name")))
    if b:
        name_pairs.append({"name": p.get("name"), "public_price": p.get("price"), "public_priceFrom": p.get("priceFrom"),
                           "buyer_price": b.get("price"), "buyer_priceFrom": b.get("priceFrom"),
                           "stock": b.get("stock")})
print(f"     matched by name: {len(name_pairs)}/{len(dc_pub)} (public IDs numeric · buyer IDs slugs — same products)")
for np_ in name_pairs:
    print(f"       {np_['name'][:40]:40} pub=${np_['public_price']}/${np_['public_priceFrom']} buyer=${np_['buyer_price']}/${np_['buyer_priceFrom']} stock={np_['stock']}")
dc_buyer_only = [{"id": str(b.get("id")), "name": b.get("name")} for b in dc_buyer if nk(b.get("name")) not in {nk(p.get("name")) for p in dc_pub}]
print(f"     buyer-only products (not in public): {dc_buyer_only}")
# buyer catalog sample fields
print(f"     buyer item keys: {list(dc_buyer[0].keys()) if dc_buyer else '-'}")
res["tests"]["P5"] = {"buyer_n": len(dc_buyer), "public_n": len(dc_pub), "same_n": dc_diff["same_n"],
                      "name_pairs": name_pairs, "buyer_only": dc_buyer_only,
                      "buyer_fields": list(dc_buyer[0].keys()) if dc_buyer else [],
                      "id_note": "public=numeric · buyer=slug — same 11 products"}

# ---------- P6: AIXpress on aixpress.shop (its OWN deployment!) ----------
print("\n" + "=" * 60 + "\nP6: AIXpress new key — aixpress.shop = separate deployment")
ax_results = {}
ax_products = None
for base in ["https://aixpress.shop", "https://aiversehub.store"]:
    for ep in ["/api/v1/me", "/api/v1/products"]:
        st, body = fetch(base + ep, {"X-API-Key": KEYS["aixpress"]})
        ax_results[f"{base}{ep}"] = {"http": st, "body_head": (body or "")[:140]}
        print(f"     [{st}] {base}{ep}  {(body or '')[:100]}")
        if st == 200 and ep.endswith("products") and body and body.lstrip()[:1] in "[{":
            try: ax_products = json.loads(body)
            except Exception: pass
        time.sleep(0.4)
if ax_products is not None:
    if isinstance(ax_products, dict): ax_products = ax_products.get("products") or ax_products.get("data") or []
    print(f"     AIXpress catalog (aixpress.shop): {len(ax_products)} items")
    if ax_products:
        print(f"     sample: {json.dumps(ax_products[0], ensure_ascii=False)[:240]}")
        # diff vs AIVerseX catalog (aiversehub.store, R2) — same software family?
        _r2 = json.load(open("/home/z/my-project/research/g1_rescan_analysis_20261002.json"))
        aivx = _r2["entity_catalogs"]["aivx_aiversehub"]["items"]
        aivx_names = {nk(i.get("name")) for i in aivx}
        ax_names = {nk(i.get("name")) for i in ax_products}
        both = aivx_names & ax_names
        print(f"     AIXpress({len(ax_names)} uniq) vs AIVerseX({len(aivx_names)} uniq): common={len(both)} · aix-only={len(ax_names-aivx_names)} · aivx-only={len(aivx_names-ax_names)}")
        ax_cb = ax_names & set(cb_by_name)
        print(f"     AIXpress vs cb_ name matches = {len(ax_cb)}")
        ax_results["catalog"] = {"n": len(ax_products), "sample": ax_products[0] if ax_products else None,
                                 "vs_aiversex": {"common": len(both), "aix_only": sorted(ax_names - aivx_names)[:12], "aivx_only": sorted(aivx_names - ax_names)[:12]},
                                 "vs_cb_name_matches": len(ax_cb), "vs_cb_samples": sorted(ax_cb)[:15]}
res["tests"]["P6"] = ax_results

# ---------- P7: topology fingerprints ----------
print("\n" + "=" * 60 + "\nP7: topology fingerprints")
# prodseller v1 items (from R2 analysis) vs premi v2 vs richai vs dc
r2 = json.load(open("/home/z/my-project/research/g1_rescan_analysis_20261002.json"))
ps_items = r2["entity_catalogs"]["prodseller_fresh"]["items"]
topo = {
    "prodseller_v1_psk": {"auth": "psk_ / Bearer?", "id": [str(i.get("id"))[:26] for i in ps_items[:3]],
                          "fields": list(ps_items[0].keys()) if ps_items else []},
    "canboso_v2_tgb": {"auth": "X-API-Key tgb_", "id": [str(i.get("productId")) for i in premi[:3]],
                       "fields": list(premi[0].keys()) if premi else [],
                       "meta_fields": list(premi_raw.keys())},
    "richai_rsk": {"auth": "Bearer rsk_", "id": [str(i.get("id")) + "/" + str(i.get("slug")) for i in rich[:3]],
                   "fields": list(rich[0].keys()) if rich else []},
    "digitalcore_uuid": {"auth": "Api-Key UUID", "id": [str(b.get("id")) for b in dc_buyer[:3]],
                         "fields": list(dc_buyer[0].keys()) if dc_buyer else []},
}
print(json.dumps(topo, ensure_ascii=False, indent=1)[:1800])
res["tests"]["P7"] = topo

with open(OUT, "w") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(f"\nSaved -> {OUT}")
