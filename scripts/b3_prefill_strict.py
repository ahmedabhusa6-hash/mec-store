#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.5b | STRICT quota-free pre-fill matcher (v2 — post noise-lesson).
Rules:
  StackVault (AI/Subscriptions/Software): brand-strict + score(duration match, type match,
    warranty) - penalty(token/decor/badge/clone/admin-noise). Min score gate.
  Turgame (Gift Cards): brand-strict + EXACT nominal value+currency + region compatibility.
Output: research/b3_prefill_strict.json — shortlist for MANUAL curation (no auto-merge).
"""
import json, os, re, unicodedata

BASE = "/home/z/my-project"
def L(p): return json.load(open(os.path.join(BASE, p), encoding="utf-8"))

cat = L("download/catalog_v42.json")
sv = L("research/b3_stackvault_api.json")
tg = L("research/b3_turgame_categories.json")

p3 = [s for s in cat["skus"] if s.get("priority") == "P3"]
DEFERRED_SKUS = {"SKU-DS038","SKU-DS040","SKU-DS041","SKU-DS043","SKU-DS049","SKU-DS050",
                 "SKU-DS061","SKU-DS062","SKU-DS063","SKU-AP002","SKU-AP003","SKU-AP007",
                 "SKU-AP008","SKU-AP009","SKU-AP010","SKU-AP005","SKU-AP006","SKU-AP016"}

def norm(s):
    s = unicodedata.normalize("NFKC", str(s or "")).lower()
    return re.sub(r"[^a-z0-9\u0600-\u06FF]+", " ", s).strip()

BRAND_TOKENS = {
    "netflix": ["netflix"], "spotify": ["spotify"], "openai": ["chatgpt", "gpt plus", "openai"],
    "anthropic": ["claude"], "google": ["gemini", "google one", "google ai"],
    "midjourney": ["midjourney"], "discord": ["discord nitro", "nitro"],
    "telegram": ["telegram", "tg premium"], "youtube": ["youtube", "yt premium"],
    "canva": ["canva"], "coursera": ["coursera"], "duolingo": ["duolingo"],
    "capcut": ["capcut"], "microsoft": ["office", "ms365", "microsoft 365", "word", "excel"],
    "windows": ["windows"], "xbox": ["xbox", "game pass"], "sony": ["psn", "playstation", "ps plus"],
    "valve": ["steam"], "apple": ["apple", "itunes"], "googleplay": ["google play"],
    "amazon": ["amazon"], "adobe": ["adobe"], "nord": ["nordvpn", "nord vpn"],
    "expressvpn": ["express vpn", "expressvpn"], "surfshark": ["surfshark"],
    "cursor": ["cursor"], "perplexity": ["perplexity"], "notion": ["notion"],
    "grammarly": ["grammarly"], "hbo": ["hbo"], "disney": ["disney"],
    "crunchyroll": ["crunchyroll"], "grammarly2": ["grammarly"], "revolut": ["revolut"],
    "prime": ["prime video"], "twitch": ["twitch"], "figma": ["figma"],
}
NOISE_TOKENS = ["token", "decor", "badge", "clone", "contact admin", "gift decor", "cheaper than the original"]
SUB_TYPE_TOKENS = ["full warranty", "upgrade", "premium", "pro ", "subscription", "month", "year", "1m", "3m", "6m", "1y"]

def brand_of(*texts):
    t = norm(" ".join(texts))
    for brand, toks in BRAND_TOKENS.items():
        for tok in toks:
            if tok in t:
                return brand
    return None

def months_of(text):
    t = norm(text)
    m = re.search(r"(\d+)\s*(month|months|mo\b)", t)
    if m: return int(m.group(1))
    m = re.search(r"(\d+)\s*(year|years|yr|y\b|annual)", t)
    if m: return int(m.group(1)) * 12
    m = re.search(r"(\d+)\s*(day|days|d\b|week|weeks|hour|hours)", t)
    if m: return -1  # sub-month durations: different family
    if "annual" in t or "yearly" in t: return 12
    return None

# ---------------- StackVault strict matcher ----------------
sv_prods = [p for p in sv["products"] if p.get("id") != "dummy-free-test"]

def sv_score(sku, p):
    """Score a StackVault product against a subscription SKU. None = reject."""
    name = norm(p.get("name", ""))
    if any(nz in name for nz in NOISE_TOKENS): return None
    sku_m = months_of(str(sku.get("duration_denomination", "")))
    p_m = months_of(p.get("name", ""))
    if p_m == -1 and sku_m and sku_m >= 1: return None  # days/weeks vs months — different identity
    score = 0
    if sku_m and p_m:
        if sku_m == p_m: score += 5
        elif (sku_m >= 10) == (p_m >= 10): score += 2  # same duration family
        else: return None
    if "full warranty" in name: score += 2
    if any(st in name for st in ["premium", "pro"]): score += 1
    # API-credit products vs subscription SKUs = adjacent identity (allowed, flagged)
    is_api = "api" in name or "credit" in name
    if is_api: score -= 2
    return score

sv_matches = []
for sku in p3 + [s for s in cat["skus"] if s["sku_id"] in DEFERRED_SKUS]:
    if sku.get("family") in ("Gift Cards", "Game Top-up", "eSIM"): continue  # not StackVault territory
    brand = brand_of(sku.get("brand", ""), sku.get("product", ""))
    if not brand: continue
    best, best_score, cands = None, -99, 0
    for p in sv_prods:
        if brand_of(p.get("name", "")) != brand: continue
        sc = sv_score(sku, p)
        if sc is None: continue
        cands += 1
        # tie-break: cheaper
        key = (sc, -(p.get("price") or 9999))
        if best is None or key > (best_score, -(best.get("price") or 9999)):
            best, best_score = p, sc
    if best and best_score >= 4:
        sv_matches.append({
            "sku_id": sku["sku_id"], "deferred": sku["sku_id"] in DEFERRED_SKUS,
            "identity": f"{sku.get('brand')} | {sku.get('product')} | {sku.get('duration_denomination')} | {sku.get('region')}",
            "family": sku.get("family"),
            "best": {"name": best.get("name", ""), "price": best.get("price"), "cost": best.get("costPrice"), "stock": best.get("stock")},
            "score": best_score, "n_candidates": cands,
            "state": "adjacent-identity candidate — manual review required",
        })

# ---------------- Turgame strict matcher ----------------
CUR_MAP = {"try": "TRY", "tl": "TRY", "usd": "USD", "$": "USD", "eur": "EUR", "€": "EUR",
           "aed": "AED", "sar": "SAR", "inr": "INR", "₹": "INR", "gbp": "GBP", "£": "GBP",
           "qar": "QAR", "omr": "OMR", "bhd": "BHD", "kwd": "KWD", "egp": "EGP", "jpy": "JPY"}
REGION_MAP = {"turkey": "TURKEY", "usa": "USA", "us": "USA", "india": "INDIA", "oman": "OMAN",
              "uae": "UAE", "lebanon": "LEBANON", "europe": "EU", "eu": "EU", "germany": "EU",
              "france": "EU", "saudi": "SAUDI", "uk": "UK", "united kingdom": "UK",
              "qatar": "QATAR", "qa": "QATAR", "bahrain": "BAHRAIN", "egypt": "EGYPT",
              "japan": "JAPAN", "argentina": "ARGENTINA", "canada": "CANADA", "australia": "AUSTRALIA"}

def parse_value(text):
    t = norm(text)
    m = re.search(r"(\d+(?:\.\d+)?)\s*(try|tl|usd|eur|aed|sar|inr|gbp|qar|omr|bhd|kwd|egp|jpy)", t)
    if not m:
        m = re.search(r"(\d+(?:\.\d+)?)\s*(\$|€|₹|£)", t)
    if m:
        return float(m.group(1)), CUR_MAP.get(m.group(2), m.group(2).upper())
    return None, None

def parse_region(text):
    t = norm(text)
    for k, v in REGION_MAP.items():
        if re.search(r"\b" + k + r"\b", t): return v
    return None

tg_all = []
for cname, c in tg.get("categories", {}).items():
    if not isinstance(c, dict): continue
    for p in c.get("products", []):
        tg_all.append(p)

tg_matches = []
for sku in p3:
    if sku.get("family") not in ("Gift Cards", "Game Top-up"): continue
    sid = sku["sku_id"]
    brand = brand_of(sku.get("brand", ""), sku.get("product", ""))
    if not brand: continue
    sku_val, sku_cur = parse_value(str(sku.get("duration_denomination", "")))
    sku_region = str(sku.get("region", ""))
    cands = []
    for p in tg_all:
        pname = p.get("name", "")
        if brand_of(pname) != brand: continue
        p_val, p_cur = parse_value(pname)
        # REJECT when either side unparseable: no verified value match = not a match
        if sku_val is not None and (p_val is None or p_cur is None): continue
        if sku_val is not None and p_val is not None:
            if abs(p_val - sku_val) > 0.01 or (sku_cur and p_cur and sku_cur != p_cur): continue
        # unparseable price = unusable offer
        try:
            _pv = float(str(p.get("price", "")).replace(",", "."))
        except Exception:
            continue
        p_reg = parse_region(pname)
        if sku_region and sku_region not in ("Global", "Any"):
            regmap = {"Turkey": "TURKEY", "EU": "EU", "US": "USA", "Saudi Arabia": "SAUDI",
                      "UAE": "UAE", "UK": "UK", "Argentina": "ARGENTINA", "Japan": "JAPAN"}
            want = regmap.get(sku_region, sku_region.upper())
            if p_reg is None or p_reg != want: continue
        cands.append(p)
    if cands:
        def price_f(p):
            try: return float(str(p.get("price", "9999")).replace(",", "."))
            except Exception: return 9999
        cheapest = min(cands, key=price_f)
        tg_matches.append({
            "sku_id": sid,
            "identity": f"{sku.get('brand')} | {sku.get('product')} | {sku.get('duration_denomination')} | {sku.get('region')}",
            "family": sku.get("family"),
            "best": {"name": cheapest.get("name", ""), "price": cheapest.get("price"),
                     "currency": cheapest.get("currency"), "url": cheapest.get("url", "")},
            "n_candidates": len(cands),
            "state": "candidate — manual review required",
        })

out = {
    "run": "MEC-2.5b strict pre-fill matcher",
    "generated": "2026-09-27",
    "sv_matches": sv_matches,
    "tg_matches": tg_matches,
    "counts": {
        "sv_matched": len(sv_matches),
        "sv_deferred": len([m for m in sv_matches if m.get("deferred")]),
        "tg_matched": len(tg_matches),
    },
    "caveat": "قائمة مرشحين للتنقيح اليدوي فقط — لا دمج آلي",
}
with open(os.path.join(BASE, "research", "b3_prefill_strict.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("counts:", out["counts"])
print("\n=== SV matches (strict, score>=4) ===")
for m in sv_matches:
    b = m["best"]
    d = " [DEFERRED]" if m.get("deferred") else ""
    print(f"{m['sku_id']}{d} (s={m['score']}): {m['identity'][:42]:<44} <- {b['name'][:52]:<54} ${b['price']}")
print("\n=== TG matches (strict value+region) ===")
for m in tg_matches:
    b = m["best"]
    print(f"{m['sku_id']}: {m['identity'][:48]:<50} <- {b['name'][:52]:<54} {b['price']} {b.get('currency','')}")
