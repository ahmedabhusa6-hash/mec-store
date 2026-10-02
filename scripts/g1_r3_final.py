#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G-1 RESCAN R3 — FINAL COMPILE (summary stats for PMRF + report):
  S1  family breakdown of the 111 cb_∩canboso name matches
  S2  canboso ∩ ps_live (CapCut line) — does the pool include the live ps_ line?
  S3  price-ratio outliers (min 0.09 / max 1.71) identification
  S4  pool model numbers: pool = cb_ ∪ ps_arch ∪ canboso coverage matrix
  S5  final verdict table for all 4 probed entities
Output: research/g1_r3_final_20261002.json"""
import json, re, unicodedata
from collections import Counter
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=3))
OUT = "/home/z/my-project/research/g1_r3_final_20261002.json"

def nk(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

raw = json.load(open("/home/z/my-project/research/g1_r3_newkeys_raw_20261002.json"))
premi = json.loads(next(p["body"] for p in raw["probes"] if p["name"] == "premi_products_X-API-Key"))["products"]
def price_of(it):
    p = it.get("price")
    if isinstance(p, dict): return p.get("amount")
    return p if isinstance(p, (int, float)) else None

sv_live = json.load(open("/home/z/my-project/research/g1_cb_live_catalog_20261002.json"))["products"]
sv_cb = [p for p in sv_live if str(p["id"]).startswith("cb_")]
sv_ps = [p for p in sv_live if str(p["id"]).startswith("ps_")]
arch = json.load(open("/home/z/my-project/research/stackvault_live/sv_products_current.json"))
arch_products = arch.get("products", arch if isinstance(arch, list) else [])
arch_ps = [p for p in arch_products if str(p.get("id", "")).startswith("ps_")]

premi_names = {nk(p.get("name")) for p in premi}
cb_names = {nk(p.get("name")) for p in sv_cb}
ps_live_names = {nk(p.get("name")) for p in sv_ps}
arch_names = {nk(p.get("name")) for p in arch_ps}

inter_cb = premi_names & cb_names
inter_ps_live = premi_names & ps_live_names
inter_arch = premi_names & arch_names

# S1: family breakdown of cb_∩canboso
FAM = [("discord decor", "decor discord"), ("discord", "discord"), ("cursor", "cursor"), ("perplexity", "perplexity"),
       ("claude", "claude"), ("chatgpt/plus", "chatgpt"), ("gemini", "gemini"), ("gmail", "gmail"),
       ("apple id", "apple id"), ("adobe", "adobe"), ("netflix", "netflix"), ("youtube", "youtube"),
       ("spotify", "spotif"), ("canva", "canva"), ("capcut", "capcut"), ("vpn", "vpn"), ("ms365/office", "ms365"),
       ("midjourney", "midjourney"), ("api credits", "api"), ("k12/edu", "k12")]
cb_match_products = [p for p in sv_cb if nk(p.get("name")) in inter_cb]
fam_counter = Counter()
assigned = set()
for label, pat in FAM:
    for p in cb_match_products:
        k = nk(p.get("name"))
        if k in assigned: continue
        if pat in k:
            fam_counter[label] += 1; assigned.add(k)
fam_counter["other"] = len(cb_match_products) - len(assigned)
print("S1 — family breakdown of 111 cb_∩canboso matched products:")
for fam, n in fam_counter.most_common():
    print(f"    {fam:16} {n}")

# S2: ps_live (CapCut) ∩ canboso
print(f"\nS2 — canboso ∩ ps_LIVE({len(ps_live_names)}) = {len(inter_ps_live)}")
ps_live_in_premi = [p.get("name") for p in sv_ps if nk(p.get("name")) in premi_names]
print(f"    ps_ live names found in canboso: {ps_live_in_premi[:8]}")
# price compare on those
pc = []
for p in sv_ps:
    k = nk(p.get("name"))
    pm = next((x for x in premi if nk(x.get("name")) == k), None)
    if pm and p.get("price") and price_of(pm):
        pc.append({"name": p.get("name"), "ps_price": p.get("price"), "premi_price": price_of(pm),
                   "ratio": round(float(p["price"]) / float(price_of(pm)), 3)})
for x in pc: print(f"    {x['name'][:40]:40} ps_=${x['ps_price']} premi=${x['premi_price']} ratio={x['ratio']}")

# S3: outliers from P3a
pairs = []
for p in sv_cb:
    k = nk(p.get("name"))
    if k in inter_cb:
        pm = next((x for x in premi if nk(x.get("name")) == k), None)
        if pm and p.get("price") and price_of(pm):
            pairs.append((float(p["price"]) / float(price_of(pm)), p.get("name"), p.get("price"), price_of(pm)))
pairs.sort()
print(f"\nS3 — price-ratio outliers (cb_/canboso):")
for r, n, cp, pp in pairs[:5]: print(f"    LOW  {r:.3f}  {n[:48]} cb_=${cp} premi=${pp}")
for r, n, cp, pp in pairs[-5:]: print(f"    HIGH {r:.3f}  {n[:48]} cb_=${cp} premi=${pp}")

# S4: pool coverage matrix
pool = cb_names | arch_names | ps_live_names | premi_names
print(f"\nS4 — CATALOG-POOL MATRIX (unique normalized names):")
print(f"    pool size (union) = {len(pool)}")
print(f"    canboso {len(premi_names)} | cb_ {len(cb_names)} | ps_arch {len(arch_names)} | ps_live {len(ps_live_names)}")
print(f"    canboso∩cb_={len(inter_cb)} · canboso∩ps_arch={len(inter_arch)} · canboso∩ps_live={len(inter_ps_live)}")
print(f"    cb_∩ps_arch (R2 known: migration) = {len(cb_names & arch_names)}")
print(f"    in ALL THREE (canboso+cb_+arch) = {len(inter_cb & arch_names & premi_names)}")
cb_only = cb_names - premi_names - arch_names
print(f"    cb_-ONLY (neither canboso nor archived ps_): {len(cb_only)}")
print(f"      samples: {sorted(cb_only)[:12]}")

# S5: verdict table
print(f"\nS5 — VERDICTS (R3):")
verdicts = {
    "premikey_canboso": {
        "entity": "PremiKey @PremiKeyBot (HitMeow 🇻🇳 cluster — @vahnix)",
        "platform": "canboso.com — 'Quản Lý Bán Hàng' (VN admin panel) · Vite/React · Binance Pay rails · usdRate 25,945 VND",
        "api": "GET /api/v2/telegram-buyer/{products,balance,purchase} · X-API-Key tgb_ · v2 generation",
        "catalog": f"{len(premi)} products / {len(premi_names)} uniq · productId = Mongo hex-24 (separate DB)",
        "vs_cb_": f"names {len(inter_cb)}/228 · descriptions identical 101/111 · VN-domain fingerprints shared (vibi/phh/dongvanfb/gpmloginapp/2fa.live/lartai/get-opt)",
        "objectid_overlap": "0/349 vs cb_∪ps_ — DIFFERENT MongoDB (not the ProdSeller platform DB)",
        "price_direction": f"cb_/canboso median 0.91 (p25 0.76, p75 1.07) — cb_ CHEAPER → canboso NOT the visible upstream",
        "verdict": "SIBLING PANEL — same VN catalog pool, separate platform/DB. HitMeow's own storefront platform. NOT cb_ identity (excluded as DB), but confirms shared pool architecture"
    },
    "richai_cgptactive": {
        "entity": "RichAIStore @RichAIStoreBot (IN wholesale cluster)",
        "platform": "cgpt-active.pro (Cloudflare) · Reseller API v1.0.0 · 12 endpoints (full order lifecycle + ticketing) · Bearer rsk_ · retail_price vs your_unit_price margin model · AI-Agent integration page (Cursor/Claude Code prompts)",
        "catalog": "25 products (CDK-focused: Perplexity PRO 12M ...) · numeric IDs + slugs",
        "vs_cb_": "0 name matches · family overlap partial (grok/gmail/lovable/capcut/perplexity/claude/duolingo)",
        "verdict": "EXCLUDED as cb_ identity — new fully-documented CDK reseller platform (registered as new entity)"
    },
    "aixpress_regenerated": {
        "entity": "AIXpress @AIXpress_Bot (IN cluster)",
        "platform": "aixpress.shop = OWN deployment (IP 188.166.90.19 SHARED with aiversehub.store/AIVerseX — same DO box) · bot docs' base URL (aiversehub.store) is STALE — key valid only on aixpress.shop",
        "catalog": "2 products only (Gemini Pro 18M $0.65 · gemini pro 18m(2) $0.45) · both stock=0 · balance $0",
        "identity_note": "/me reveals chat_id 7334478984 'A7MED' — the key owner = Ahmed (same TG account across canboso/LahaStore shop ID)",
        "verdict": "EXCLUDED — dormant/minimal deployment, zero stock, zero overlap with cb_ (and with AIVerseX's 35-product catalog)"
    },
    "digitalcore_confirmed": {
        "entity": "DigitalCore @DCoreStoreBot (digitalcore.top)",
        "platform": "buyer API /api/user/{me,products,product} · Api-Key UUID · balance $0 / 0 orders",
        "catalog": "11/11 same products as public · buyer price = qty-1 tier (Gemini 18M $0.80 → $0.70 at 50+) · slug IDs",
        "verdict": "EXCLUDED as cb_ (0 matches, R2) — buyer tier pricing documented (tier ladder +12-47% over priceFrom)"
    }
}
for k, v in verdicts.items():
    print(f"\n  [{k}]")
    for kk, vv in v.items(): print(f"    {kk}: {str(vv)[:150]}")

out = {"execution_timestamp": datetime.now(TZ).isoformat(),
       "S1_family_breakdown": dict(fam_counter),
       "S2_ps_live_capcut": {"n": len(inter_ps_live), "pairs": pc},
       "S3_outliers": {"low": [{"ratio": r, "name": n, "cb": c, "premi": p} for r, n, c, p in pairs[:5]],
                       "high": [{"ratio": r, "name": n, "cb": c, "premi": p} for r, n, c, p in pairs[-5:]]},
       "S4_pool_matrix": {"pool_size": len(pool), "canboso": len(premi_names), "cb": len(cb_names),
                          "ps_arch": len(arch_names), "ps_live": len(ps_live_names),
                          "canboso_cap_cb": len(inter_cb), "canboso_cap_arch": len(inter_arch),
                          "canboso_cap_ps_live": len(inter_ps_live), "cb_cap_arch": len(cb_names & arch_names),
                          "in_all_three": len(inter_cb & arch_names & premi_names),
                          "cb_only_n": len(cb_only), "cb_only_samples": sorted(cb_only)[:15]},
       "S5_verdicts": verdicts}
with open(OUT, "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"\nSaved -> {OUT}")
