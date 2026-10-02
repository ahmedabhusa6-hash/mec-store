#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.5 | Quota-free P3 pre-fill: match StackVault API (275, with cost) + Turgame (117)
catalogs against P3 SKUs (218) + 16 deferred SKUs — upgrades evidence to Directly-Observed
WITHOUT consuming search quota. Uses already-fetched JSON only.
Output: research/b3_prefill_matches.json (review candidates for manual curation)
"""
import json, os, re, unicodedata

BASE = "/home/z/my-project"
def L(p): return json.load(open(os.path.join(BASE, p), encoding="utf-8"))

cat = L("download/catalog_v42.json")
sv = L("research/b3_stackvault_api.json")
tg = L("research/b3_turgame_categories.json")
oi = L("download/offers_intelligence.json")

p3 = [s for s in cat["skus"] if s.get("priority") == "P3"]
DEFERRED_SKUS = {"SKU-DS038","SKU-DS040","SKU-DS041","SKU-DS043","SKU-DS049","SKU-DS050",
                 "SKU-DS061","SKU-DS062","SKU-DS063","SKU-AP002","SKU-AP003","SKU-AP007",
                 "SKU-AP008","SKU-AP009","SKU-AP010","SKU-AP005","SKU-AP006","SKU-AP016"}

def norm(s):
    s = unicodedata.normalize("NFKC", str(s or "")).lower()
    return re.sub(r"[^a-z0-9\u0600-\u06FF]+", " ", s).strip()

# ---------------- StackVault products ----------------
sv_prods = [p for p in sv["products"] if p.get("id") != "dummy-free-test"]

# keyword map: (canonical tokens -> list of matching tokens)
BRAND_TOKENS = {
    "netflix": ["netflix"], "spotify": ["spotify"], "chatgpt": ["chatgpt", "gpt plus", "gpt"],
    "claude": ["claude"], "gemini": ["gemini"], "midjourney": ["midjourney"],
    "discord": ["nitro", "discord"], "telegram": ["telegram", "tg premium", "tg "],
    "youtube": ["youtube", "yt premium"], "canva": ["canva"], "coursera": ["coursera"],
    "duolingo": ["duolingo"], "capcut": ["capcut"], "office": ["office", "ms365", "microsoft 365"],
    "windows": ["windows"], "xbox": ["xbox", "game pass"], "playstation": ["psn", "playstation", "ps plus"],
    "steam": ["steam"], "apple": ["apple", "itunes"], "google": ["google play", "google"],
    "amazon": ["amazon"], "adobe": ["adobe"], "nordvpn": ["nordvpn", "nord vpn"],
    "expressvpn": ["expressvpn", "express vpn"], "surfshark": ["surfshark"],
    "cursor": ["cursor"], "perplexity": ["perplexity"], "notion": ["notion"],
    "figma": ["figma"], "grammarly": ["grammarly"], "hbo": ["hbo", "max"],
    "crunchyroll": ["crunchyroll"], "revolut": ["revolut"], "vpn": ["vpn"],
    "prime": ["prime video", "amazon prime"], "disney": ["disney"], "twitch": ["twitch"],
}

def brand_of(text):
    t = norm(text)
    for brand, toks in BRAND_TOKENS.items():
        for tok in toks:
            if tok in t:
                return brand
    return None

# match P3 SKU -> StackVault products by brand + heuristic duration scoring
DUR_TOKENS = {"month": 1, "m": 1, "year": 12, "y": 12, "yr": 12}
def duration_hint(text):
    t = norm(text)
    m = re.search(r"(\d+)\s*(month|year|yr|mo|y\b)", t)
    if m:
        n = int(m.group(1)); unit = m.group(2)
        return n * (12 if unit.startswith(("year", "yr", "y")) else 1)
    if "annual" in t or "yearly" in t: return 12
    return None

matches = []
for sku in p3:
    sid = sku["sku_id"]
    brand = brand_of(sku.get("brand", "") + " " + sku.get("product", ""))
    if not brand: continue
    sku_dur = duration_hint(sku.get("duration_denomination", ""))
    cands = []
    for p in sv_prods:
        ptext = p.get("name", "")
        if brand_of(ptext) != brand: continue
        p_dur = duration_hint(ptext)
        dur_ok = (sku_dur is None) or (p_dur is None) or (p_dur == sku_dur)
        if dur_ok:
            cands.append(p)
    if cands:
        # pick cheapest as candidate + note alternatives count
        with_cost = [c for c in cands if c.get("costPrice")]
        pool = with_cost or cands
        cheapest = min(pool, key=lambda x: x.get("price") or 9999)
        matches.append({
            "sku_id": sid, "identity": f"{sku.get('brand')} | {sku.get('product')} | {sku.get('duration_denomination')} | {sku.get('region')}",
            "family": sku.get("family"),
            "source": "StackVault-API",
            "n_candidates": len(cands),
            "best": {"name": cheapest.get("name", "")[:80], "price": cheapest.get("price"),
                     "cost": cheapest.get("costPrice"), "stock": cheapest.get("stock")},
            "evidence": "Directly-Observed (backend API 27/09) — ADJACENT-IDENTITY CANDIDATE, needs manual curation",
        })

# deferred SKUs (P2) — same matching
deferred_matches = []
for sku in cat["skus"]:
    sid = sku["sku_id"]
    if sid not in DEFERRED_SKUS: continue
    brand = brand_of(sku.get("brand", "") + " " + sku.get("product", ""))
    if not brand: continue
    sku_dur = duration_hint(sku.get("duration_denomination", ""))
    cands = []
    for p in sv_prods:
        if brand_of(p.get("name", "")) != brand: continue
        p_dur = duration_hint(p.get("name", ""))
        if (sku_dur is None) or (p_dur is None) or (p_dur == sku_dur):
            cands.append(p)
    if cands:
        with_cost = [c for c in cands if c.get("costPrice")]
        pool = with_cost or cands
        cheapest = min(pool, key=lambda x: x.get("price") or 9999)
        deferred_matches.append({
            "sku_id": sid, "identity": f"{sku.get('brand')} | {sku.get('product')} | {sku.get('duration_denomination')}",
            "source": "StackVault-API",
            "n_candidates": len(cands),
            "best": {"name": cheapest.get("name", "")[:80], "price": cheapest.get("price"),
                     "cost": cheapest.get("costPrice"), "stock": cheapest.get("stock")},
        })

# Turgame products -> P3 gift-card SKUs
tg_matches = []
tg_all = []
for cname, c in tg.get("categories", {}).items():
    if not isinstance(c, dict): continue
    for p in c.get("products", []):
        p["_cat"] = cname
        tg_all.append(p)

for sku in p3:
    if sku.get("family") not in ("Gift Cards", "Game Top-up"): continue
    sid = sku["sku_id"]
    brand = brand_of(sku.get("brand", "") + " " + sku.get("product", ""))
    if not brand: continue
    # extract nominal value from product/plan
    nominal = None
    m = re.search(r"(\d+(?:\.\d+)?)\s*(USD|EUR|TL|TRY|AED|SAR)?", str(sku.get("plan_edition", "")) + " " + str(sku.get("product", "")))
    if m:
        try: nominal = float(m.group(1))
        except Exception: nominal = None
    cands = []
    for p in tg_all:
        if brand_of(p.get("name", "")) != brand: continue
        pm = re.search(r"(\d+(?:[.,]\d+)?)", p.get("name", ""))
        pv = None
        if pm:
            try: pv = float(pm.group(1).replace(",", "."))
            except Exception: pv = None
        if nominal and pv and abs(pv - nominal) / nominal > 0.35: continue
        cands.append(p)
    if cands:
        def price_f(p):
            try: return float(str(p.get("price", "9999")).replace(",", "."))
            except Exception: return 9999
        cheapest = min(cands, key=price_f)
        tg_matches.append({
            "sku_id": sid, "identity": f"{sku.get('brand')} | {sku.get('product')} | {sku.get('plan_edition')} | {sku.get('region')}",
            "family": sku.get("family"),
            "source": "Turgame-retail",
            "n_candidates": len(cands),
            "best": {"name": cheapest.get("name", "")[:80], "price": cheapest.get("price"),
                     "currency": cheapest.get("currency"), "url": cheapest.get("url", "")[:90]},
            "evidence": "Directly-Observed (product page data 27/09) — ADJACENT-IDENTITY CANDIDATE, needs manual curation",
        })

out = {
    "run": "MEC-2.5 quota-free pre-fill (P3 + deferred vs StackVault/Turgame catalogs)",
    "generated": "2026-09-27",
    "p3_sv_matches": matches,
    "deferred_sv_matches": deferred_matches,
    "p3_tg_matches": tg_matches,
    "counts": {
        "p3_total": len(p3),
        "p3_sv_matched": len(matches),
        "deferred_matched": len(deferred_matches),
        "p3_tg_matched": len(tg_matches),
        "p3_unique_covered": len(set(m["sku_id"] for m in matches) | set(m["sku_id"] for m in tg_matches)),
    },
    "caveat": "كل التطابقات مرشحة بدرجة «هوية مجاورة» — التنقيح اليدوي إلزامي قبل أي دمج (درس الضجيج المنهجي من الدفعة 2)",
}
with open(os.path.join(BASE, "research", "b3_prefill_matches.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("counts:", out["counts"])
print()
print("=== deferred SKUs matched (StackVault) ===")
for m in deferred_matches:
    b = m["best"]
    print(f"{m['sku_id']}: {b['name'][:50]} | price ${b['price']} cost ${b['cost']} | cands={m['n_candidates']}")
print()
print("=== top P3 SV matches (sample 15) ===")
for m in matches[:15]:
    b = m["best"]
    print(f"{m['sku_id']}: {m['identity'][:45]} <- {b['name'][:45]} | ${b['price']}")
