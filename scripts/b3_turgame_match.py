#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.5i | Consolidate 3 Turgame batches (92 categories, ~612 priced products) +
match against P3 catalog (strict: brand + value/currency + region where applicable).
Output: research/b3_turgame_p3_matches.json (candidates for manual curation)
"""
import json, os, re, unicodedata

BASE = "/home/z/my-project"
def L(p): return json.load(open(os.path.join(BASE, p), encoding="utf-8"))

cat = L("download/catalog_v42.json")
batches = [L(f"research/b3_turgame_p3_b{i}.json") for i in (1, 2, 3)]

all_products = []  # {cat, name, price, url}
for b in batches:
    for cname, c in b["categories"].items():
        for p in c.get("products", []):
            if p.get("price"):
                all_products.append({"cat": cname, "name": p["name"], "price": p["price"], "url": p.get("url", "")})

print(f"total priced products: {len(all_products)}")

def norm(s):
    s = unicodedata.normalize("NFKC", str(s or "")).lower()
    return re.sub(r"[^a-z0-9\u0600-\u06FF]+", " ", s).strip()

# brand matcher: catalog brand+product -> product-name tokens
BRANDS = {
    "netflix": ["netflix"], "spotify": ["spotify"], "disney": ["disney"], "hulu": ["hulu"],
    "paramount": ["paramount"], "starzplay": ["starzplay", "starz play"], "osn": ["osn"],
    "crunchyroll": ["crunchyroll"], "tidal": ["tidal"], "deezer": ["deezer"],
    "storytel": ["storytel"], "dazn": ["dazn"], "youtube": ["youtube"], "siriusxm": ["sirius"],
    "britbox": ["britbox"], "shahid": ["shahid", "mbc"], "anghami": ["anghami"],
    "yango": ["yango"], "bilibili": ["bilibili"], "vudu": ["vudu"],
    "microsoft-office": ["office", "microsoft 365", "ms office", "word", "excel", "ms365"],
    "microsoft-windows": ["windows"], "adobe": ["adobe"], "mcafee": ["mcafee"],
    "norton": ["norton"], "bitdefender": ["bitdefender"], "exitlag": ["exitlag"],
    "pubg": ["pubg"], "valorant": ["valorant"], "free-fire": ["free fire"],
    "mobile-legends": ["mobile legends"], "fortnite": ["fortnite"],
    "league-of-legends": ["lol", "league of legends"], "cod": ["call of duty", "cod points", "cp"],
    "bigo": ["bigo"], "roblox": ["roblox", "robux"], "honor-of-kings": ["honor of kings"],
    "candy-crush": ["candy crush"], "tango": ["tango"], "starmaker": ["starmaker"],
    "soulchill": ["soulchill"], "yaahlan": ["yaahlan"], "yalla-ludo": ["yalla ludo"],
    "chamet": ["chamet"], "likee": ["likee"], "imvu": ["imvu"], "rec-room": ["rec room"],
    "jawaker": ["jawaker"], "sugo": ["sugo"], "cherry-credits": ["cherry credit"],
    "karma-koin": ["karma koin"], "xsolla": ["xsolla"], "apex": ["apex"],
    "black-desert": ["black desert"],
    "steam": ["steam"], "playstation": ["playstation", "psn"], "xbox": ["xbox"],
    "google-play": ["google play"], "apple": ["apple", "itunes", "app store"],
    "amazon": ["amazon"], "razer": ["razer"], "battlenet": ["battle net", "battlenet", "blizzard"],
    "epic": ["epic games", "fortnite v bucks" if False else "epic"], "meta": ["meta", "oculus"],
    "tiktok": ["tiktok"], "binance": ["binance"], "flexepin": ["flexepin"],
    "webmoney": ["webmoney"], "huawei": ["huawei"], "gameforge": ["gameforge"],
    "discord": ["discord", "nitro"],
    "airalo": ["airalo"], "alosim": ["alosim"], "esimchoice": ["esim choice", "esimchoice"],
    "surfshark": ["surfshark"],
}

def brand_key(text):
    t = norm(text)
    for k, toks in BRANDS.items():
        if any(tok in t for tok in toks): return k
    return None

# catalog SKU -> brand_key mapping (specific per SKU)
def sku_brand_key(sku):
    return brand_key(sku.get("brand", "") + " " + sku.get("product", ""))

CUR_MAP = {"usd": "USD", "$": "USD", "eur": "EUR", "€": "EUR", "try": "TRY", "tl": "TRY",
           "gbp": "GBP", "sar": "SAR", "aed": "AED", "pln": "PLN", "brl": "BRL",
           "inr": "INR", "qar": "QAR", "egp": "EGP", "cad": "CAD", "cop": "COP",
           "czk": "CZK", "ars": "ARS", "jpy": "JPY", "mad": "MAD"}

def parse_value_cur(text):
    t = norm(text)
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(usd|eur|try|tl|gbp|sar|aed|pln|brl|inr|qar|egp|cad|cop|czk|ars|jpy|mad)", t)
    if not m:
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*(\$|€)", t)
    if m:
        v = float(m.group(1).replace(",", "."))
        return v, CUR_MAP.get(m.group(2), m.group(2).upper())
    return None, None

REGION_TOKENS = {
    "TURKEY": ["turkey", "turkiye", "try", "tl"], "USA": ["usa", "us", "america", "united states"],
    "EU": ["europe", "eu", "germany", "france", "spain", "italy", "poland", "euro"],
    "SAUDI": ["saudi", "ksa", "sar"], "UAE": ["uae", "emirates", "dubai", "aed"],
    "UK": ["uk", "united kingdom", "england", "gbp"], "BRAZIL": ["brazil", "brl"],
    "INDIA": ["india", "inr"], "POLAND": ["poland", "pln"], "COLOMBIA": ["colombia"],
    "MOROCCO": ["morocco", "mad"], "EGYPT": ["egypt", "egp"], "QATAR": ["qatar", "qar"],
    "CANADA": ["canada", "cad"], "ARGENTINA": ["argentina", "ars"], "JAPAN": ["japan", "jpy"],
    "COLOMBIA2": ["colombia", "cop"], "GLOBAL": ["global", "international"],
}

def regions_of(text):
    t = norm(text)
    out = set()
    for reg, toks in REGION_TOKENS.items():
        if reg == "COLOMBIA2": continue
        for tok in toks:
            if re.search(r"\b" + re.escape(tok) + r"\b", t):
                out.add(reg)
                break
    return out

# match P3 SKUs (Gift Cards, Game Top-up, Digital Subscriptions, Software, eSIM, VPNs in DS)
matches = []
p3 = [s for s in cat["skus"] if s.get("priority") == "P3"]
DEFERRED = {"SKU-DS038","SKU-DS040","SKU-DS041","SKU-DS049","SKU-DS050","SKU-DS061","SKU-DS062","SKU-DS063"}
targets = p3 + [s for s in cat["skus"] if s["sku_id"] in DEFERRED]

for sku in targets:
    sid = sku["sku_id"]
    bk = sku_brand_key(sku)
    if not bk: continue
    sku_val, sku_cur = parse_value_cur(str(sku.get("duration_denomination", "")) + " " + str(sku.get("plan_edition", "")))
    sku_reg = str(sku.get("region", ""))
    regmap = {"Turkey": "TURKEY", "EU": "EU", "US": "USA", "Saudi Arabia": "SAUDI",
              "UAE": "UAE", "UK": "UK", "Global": "GLOBAL", "Argentina": "ARGENTINA",
              "Japan": "JAPAN", "India": "INDIA", "Brazil": "BRAZIL", "Morocco": "MOROCCO",
              "Poland": "POLAND", "Egypt": "EGYPT", "Canada": "CANADA", "Colombia": "COLOMBIA"}
    want_reg = regmap.get(sku_reg)
    cands = []
    for p in all_products:
        pk = brand_key(p["name"])
        if pk != bk: continue
        p_val, p_cur = parse_value_cur(p["name"])
        if sku_val is not None and p_val is not None and sku_cur == p_cur:
            if abs(p_val - sku_val) / max(sku_val, 0.01) > 0.25: continue
        p_regs = regions_of(p["name"])
        if want_reg and want_reg != "GLOBAL" and p_regs:
            if want_reg not in p_regs: continue
        # region-less product + region-specific SKU: allowed (single-region store item)
        try:
            pf = float(str(p["price"]).replace(",", "."))
        except Exception:
            continue
        cands.append((pf, p))
    if cands:
        cands.sort(key=lambda x: x[0])
        pf, p = cands[0]
        # grade: exact if value+cur matched or no value in sku identity; adjacent otherwise
        grade = "candidate"
        if sku_val is None:
            grade = "candidate-no-value"
        elif p_val is not None and abs(p_val - sku_val) / max(sku_val, 0.01) <= 0.25:
            grade = "value-matched"
        matches.append({
            "sku_id": sid, "deferred": sid in DEFERRED,
            "identity": f"{sku.get('brand')} | {sku.get('product')} | {sku.get('duration_denomination')} | {sku.get('region')}",
            "family": sku.get("family"),
            "n_candidates": len(cands),
            "best": {"name": p["name"], "price_usd": pf, "turgame_cat": p["cat"], "url": p["url"][:100]},
            "grade": grade,
        })

out = {"run": "MEC-2.5i Turgame P3 matcher", "generated": "2026-09-27",
       "total_products": len(all_products), "matches": matches,
       "counts": {"matched_skus": len(matches),
                  "value_matched": len([m for m in matches if m["grade"] == "value-matched"]),
                  "deferred_matched": len([m for m in matches if m.get("deferred")])}}
json.dump(out, open(os.path.join(BASE, "research", "b3_turgame_p3_matches.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("counts:", out["counts"])
for m in matches:
    d = " [DEF]" if m.get("deferred") else ""
    print(f"{m['sku_id']}{d} {m['grade']:<18} ${m['best']['price_usd']:<7} {m['identity'][:44]} <- {m['best']['name'][:44]}")
