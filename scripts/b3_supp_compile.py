#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-2.3 | Supplementary compile — deep channel history + plati discovery layer.
Adds timestamped historical price points (evidence class Directly-Observed, with
dates from the posts themselves) to offers_intelligence.json b3_direct_run."""
import json

BASE = "/home/z/my-project"
OI = BASE + "/download/offers_intelligence.json"
oi = json.load(open(OI, encoding="utf-8"))
EV = "Directly-Observed [channel post, timestamped]"
SRC = "MEC2-20260927-B3-DIRECT"

def offer(seller, role, price, cur, usd, note, identity="exact", date="2026-09-26/27"):
    return {"seller": seller, "role": role, "price": price, "cur": cur, "usd": usd,
            "evidence": EV, "freshness": "Post-dated " + date, "date": date[:10],
            "identity_class": identity, "source_run": SRC, "note": note}

def add(sku_id, o):
    rec = oi["skus"].setdefault(sku_id, {})
    rec.setdefault("offers", [])
    for ex in rec["offers"]:
        if ex.get("seller") == o["seller"] and ex.get("price") == o["price"]:
            return
    rec["offers"].append(o)

# ═══ Evo Era live feed (26/09) — purchases confirmed + price drop ═══
add("SKU-AI008", offer("Evo Era", "Retailer (TG bot, §19 registry)", 0.85, "USDT", 0.85,
    "PRICE DROP announcement 26/09: Gemini AI Pro 18m was 1.0 USDT → now 0.85 USDT (-15%); restock 65 items; multiple confirmed purchases (x5 @4.25, x4 @3.40)",
    identity="adjacent (18M promo-link construct)", date="2026-09-26"))
add("SKU-AI001", offer("Evo Era", "Retailer (TG bot, §19 registry)", 5.50, "USDT", 5.50,
    "ChatGPT Plus 2HW ACCOUNT — CONFIRMED PURCHASE 26/09 (order feed). Price ROSE from $4.50 observed in MEC-2.0 probe (~00:53) = +22% within ~24h — volatility datapoint",
    identity="adjacent (2H-warranty construct)", date="2026-09-26"))
add("SKU-AI012", offer("Evo Era", "Retailer (TG bot, §19 registry)", 7.50, "USDT", 7.50,
    "Perplexity Pro 30 Days (Full Warranty) — CONFIRMED PURCHASE 26/09 (order feed); vs StackVault CDK $11.90 — channel spread 37%",
    identity="adjacent (30D account construct)", date="2026-09-26"))
add("SKU-DS008", offer("Evo Era", "Retailer (TG bot, §19 registry)", 0.50, "USDT", 0.50,
    "Canva Pro Team Edu Invite 3Y — CONFIRMED PURCHASE 26/09 = $0.50 for 3-YEAR edu invite — cheapest Canva observation in project history (vs $2.50 500-panel @learnwith_Alex, $6.60 admin @StackVault)",
    identity="adjacent (edu invite 3Y vs Family 12m)", date="2026-09-26"))

# ═══ ProdSeller historical archive (July 2026) — price evolution baseline ═══
add("SKU-DS058", offer("ProdSeller", "Wholesaler/API (TG, §19 registry)", 1.00, "USD", 1.00,
    "Coursera Plus Premium 1Y launch price 24/07: $1.00 regular / $0.84 API-bulk — vs Evo Era retail 3.50 USDT (26/09): +250% supply-chain price evolution OR tier difference — historical baseline documented",
    identity="adjacent (historical datapoint)", date="2026-07-24"))
add("SKU-DS006", offer("ProdSeller", "Wholesaler/API (TG, §19 registry)", 0.95, "USD", 0.95,
    "Spotify Premium 3 Months 23/07: $0.95 regular / $0.85 API — vs StackVault 3M link cost $1.53 (27/09): wholesale rose ~60% in 2 months OR different construct",
    identity="adjacent (3M account vs 1M official)", date="2026-07-23"))
add("SKU-AI001", offer("ProdSeller", "Wholesaler/API (TG, §19 registry)", 0.30, "USD", 0.30,
    "Microsoft Office 365 1Y full warranty 24/07: $0.30 regular / $0.20 API-bulk — matches current StackVault input cost $0.21 and current ProdSeller price $0.17-0.29: STABLE across 2 months (unlike AI subs)",
    identity="adjacent (Office365 account vs ChatGPT — historical archive note)", date="2026-07-24"))

# ═══ Raw materials + API layer (July archive) ═══
oi["b3_direct_run"]["key_discoveries"]["api_discount_claim"] = "ProdSeller API bot advertised 'up to 35% OFF compared to public prices' (20/07) — first direct quantification of the API-discount layer; observed spreads: Gemini $0.55→0.43 bulk, Coursera $1.00→0.84, iLovePDF $0.80→0.70"
oi["b3_direct_run"]["key_discoveries"]["raw_materials_floor"] = "Outlook/Hotmail ready-made accounts from $0.02 (ProdSeller 23/07) — cheapest input cost ever observed in project; aged Gmail $0.60-0.80 remains premium tier vs Outlook floor"
oi["b3_direct_run"]["key_discoveries"]["coursera_price_evolution"] = "Coursera Plus 1Y: $1.00 wholesale launch (24/07) → $3.50 retail (26/09) = +250% through chain/time — largest documented price evolution in the dataset"
oi["b3_direct_run"]["key_discoverings"] = None if False else oi["b3_direct_run"].get("key_discoveries")
oi["b3_direct_run"]["key_discoveries"]["chatgpt_volatility"] = "ChatGPT Plus 2HW at Evo Era: $4.50 (MEC-2.0 probe ~01:00 27/09) → $5.50 (confirmed purchase 26/09 evening feed) — ±22% swing within a day window; gray-market AI subs are the most volatile segment (vs Office365 stable ~2 months)"
oi["b3_direct_run"]["key_discoveries"]["canva_edu_floor"] = "Canva Pro Team Edu Invite 3Y: $0.50 confirmed purchase (Evo Era 26/09) — new project-wide floor for Canva access; edu-invite constructs undercut panel constructs 5-13x"
oi["b3_direct_run"]["key_discoveries"]["legit_topup_tier"] = "gemini12pro_channel (30/06): ChatGPT Plus/Pro top-ups at '20% off official price, full warranty, accessible billing records' (DM @stl...) — a semi-legitimate top-up tier documented alongside the gray constructs ($16 Plus / $80 Pro5x / $320 Pro20x implied)"
oi["b3_direct_run"]["key_discoveries"]["plati_discovery"] = "Plati.market homepage items visible (ChatGPT 6 Astra Plus/Pro, Claude 'Fable-5/Mythos-5', PSN 250-5500 TRY, Apple iTunes US/TRY, XGPU, Spotify, Nintendo US) — item pages behind DDoS-Guard = Retrieval-Limited; market naming shows ChatGPT-6/Astra generation + Claude-5 generation now standard in RU gray market (27/09)"

json.dump(oi, open(OI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n_off = sum(len(r.get("offers", [])) for r in oi["skus"].values())
print("supplementary offers merged. total offers:", n_off)
print("key_discoveries now:", len(oi["b3_direct_run"]["key_discoveries"]))
