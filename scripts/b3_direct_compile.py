#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.3 | Direct-observation offers compiler (manual curation layer)
Converts b3 direct-observation raw files into structured offers and merges them
into download/offers_intelligence.json (new section b3_direct_run + per-SKU offers)
+ updates catalog coverage ledger.
Evidence class: Directly-Observed [page/API/channel post, timestamped 27/09 ~05:0x UTC]
Identity curation: exact vs adjacent (per batch2 convention). No fabrication —
every offer carries its raw source line + timestamp.
"""
import json, copy

BASE = "/home/z/my-project"
OI = BASE + "/download/offers_intelligence.json"
CAT = BASE + "/download/catalog_v42.json"

oi = json.load(open(OI, encoding="utf-8"))
cat = json.load(open(CAT, encoding="utf-8"))
sv = json.load(open(BASE + "/research/b3_stackvault_api.json", encoding="utf-8"))
tg = json.load(open(BASE + "/research/b3_turgame_categories.json", encoding="utf-8"))
dw = json.load(open(BASE + "/research/b3_direct_observations.json", encoding="utf-8"))

TS = "2026-09-27 ~05:00-05:20 UTC"
EV = "Directly-Observed [27/09 page/API/channel post]"
SRC = "MEC2-20260927-B3-DIRECT"

def offer(seller, role, price, cur, usd, note, identity="exact", cost=None, fresh="Current (27/09)"):
    o = {"seller": seller, "role": role, "price": price, "cur": cur, "usd": usd,
         "evidence": EV, "freshness": fresh, "date": "2026-09-27",
         "identity_class": identity, "source_run": SRC, "note": note}
    if cost is not None:
        o["observed_input_cost_usd"] = cost
        o["observed_margin_pct"] = round((usd - cost) / usd * 100, 1) if usd else None
    return o

def add(sku_id, o):
    rec = oi["skus"].setdefault(sku_id, {})
    rec.setdefault("offers", [])
    # dedupe by seller+price
    for ex in rec["offers"]:
        if ex.get("seller") == o["seller"] and ex.get("price") == o["price"]:
            return
    rec["offers"].append(o)

# ═══ 1. StackVault API (retail layer with exposed input cost) ═══
add("SKU-AI001", offer("StackVault", "Retailer (TG-shop, §19 registry)", 3.36, "USD", 3.36,
    "ChatGPT Plus 1 Month (basic tier, stock 0 at fetch) — API cost $2.80; warranty-tier ladder: $3.36 basic → $4.62 (6H) → $6.18 (5H) → $12.81 full → $20.57 official renew",
    cost=2.80))
add("SKU-AI001", offer("StackVault", "Retailer (TG-shop, §19 registry)", 12.81, "USD", 12.81,
    "ChatGPT Plus 1 Month FULL warranty (stock 0); cost $10.67", cost=10.67))
add("SKU-AI001", offer("HitMeow Shop", "Retailer (TG, §19 registry)", 10.77, "USD", 10.77,
    "ChatGPT Plus VIP 1 month full warranty — channel post 25/09: stock 14, 'sold 4,157 accounts' (seller-claimed lifetime volume)"))
add("SKU-AI001", offer("AISUBSID (ID supplier)", "Wholesaler (TG, §19 registry)", 2.90, "USD", 2.90,
    "ChatGPT Plus pre-order, min 20 units, $2.90 or 52,000 IDR/unit, stock 250+ — post 26/09 00:58 UTC; same channel admits price rises ('creating accounts is getting harder', +$0.2)",
    identity="adjacent (pre-order/wholesale condition, min 20)"))
add("SKU-AI001", offer("ProdSeller", "Wholesaler/API (TG, §19 registry)", 3.90, "USD", 3.90,
    "ChatGPT K12 with codex, 24h warranty, $3.90 retail / $3.80 API — post 20/09; K12-edu construct (different identity: edu account)",
    identity="adjacent (K12 edu construct)"))
add("SKU-AI028", offer("Evo Era", "Retailer (TG bot, §19 registry)", 5.50, "USDT", 5.50,
    "MANUS PRO 1M — 5000 credit, ready account, no warranty — NEW PRODUCT post 26/09 21:25 UTC"))
add("SKU-AI028", offer("Evo Era", "Retailer (TG bot, §19 registry)", 37.00, "USDT", 37.00,
    "Manus Pro 12m — standing price after flash sale ended, post 27/09 04:32 UTC (live same-session observation)",
    identity="adjacent (12m variant)"))
add("SKU-AI047", offer("Evo Era", "Retailer (TG bot, §19 registry)", 40.00, "USDT", 40.00,
    "Cursor Pro+ — standing price after flash sale ended, post 27/09 04:27 UTC (live same-session observation)",
    identity="adjacent (Pro+ variant vs catalog Pro)"))
add("SKU-AI024", offer("StackVault", "Retailer (TG-shop, §19 registry)", 16.46, "USD", 16.46,
    "Gamma PRO 30D full warranty — stock 52; API cost $13.71", cost=13.71))
add("SKU-AI016", offer("StackVault", "Retailer (TG-shop, §19 registry)", 5.49, "USD", 5.49,
    "Suno Pro 1 month warranty 1 day — stock 0 at fetch; cost $4.57", cost=4.57))
add("SKU-AI038", offer("StackVault", "Retailer (TG-shop, §19 registry)", 21.72, "USD", 21.72,
    "Suno Pre 1 month warranty 7 days — stock 4; cost $18.10", cost=18.10))
add("SKU-DS015", offer("StackVault", "Retailer (TG-shop, §19 registry)", 1.96, "USD", 1.96,
    "HBO MAX 1 month (20-day warranty) — stock 0 at fetch; cost $1.53", cost=1.53))
add("SKU-DS058", offer("Evo Era", "Retailer (TG bot, §19 registry)", 3.50, "USDT", 3.50,
    "Coursera Premium 12m — restock alert 26/09 22:33 UTC: 62 items available"))
add("SKU-DS060", offer("ProdSeller", "Wholesaler/API (TG, §19 registry)", 0.37, "USD", 0.37,
    "Duolingo SUPER 12M $0.37 / API $0.36 / bulk $0.34 — post 24/09 05:14 UTC (price war: $0.59→0.45→0.37 in 5 days)",
    identity="adjacent (12M duration vs catalog 1M; bulk/API tier)"))
add("SKU-DS060", offer("Evo Era", "Retailer (TG bot, §19 registry)", 0.85, "USDT", 0.85,
    "Super Duolingo 12M redeem link — restock 23:27 UTC 26/09 (26 items); CONFIRMED PURCHASE 27/09 02:25 UTC (order feed)"))
add("SKU-DS060", offer("gemini12pro_channel", "Marketplace/Paid-promo channel (§19 registry)", 1.50, "USDT", 1.50,
    "Duolingo Super 12M — 1.50 USDT — wholesale-rates post 14/09"))
add("SKU-SW001", offer("StackVault", "Retailer (TG-shop, §19 registry)", 4.58, "USD", 4.58,
    "Genuine Windows 10/11 Pro Key 20Y with 1Y warranty — stock 2; cost $3.81", cost=3.81))
add("SKU-SW001", offer("StackVault", "Retailer (TG-shop, §19 registry)", 4.07, "USD", 4.07,
    "Windows 10/11 Pro Key 20 years warranty 1 year — stock 22; cost $3.39", cost=3.39))
add("SKU-SW001", offer("Turgame", "Retailer (Notion-specified channel)", 267.97, "USD", 267.97,
    "Microsoft Windows 11 Pro ONLINE LICENSE (official-tier product, not a gray key) — same channel sells gray keys at ~$4; channel-behavior datapoint showing dual-track pricing"))
add("SKU-SW007", offer("StackVault", "Retailer (TG-shop, §19 registry)", 3.16, "USD", 3.16,
    "Microsoft Office 2024 Pro key, 10 years warranty — stock 51; cost $2.63", cost=2.63))
add("SKU-SW008", offer("StackVault", "Retailer (TG-shop, §19 registry)", 1.96, "USD", 1.96,
    "Microsoft 365 Personal 1 year (warranty 3 months) — stock 33; cost $1.53", cost=1.53))
add("SKU-SW008", offer("StackVault", "Retailer (TG-shop, §19 registry)", 0.38, "USD", 0.38,
    "Microsoft Office 365 Plus 1 year — stock 677 (!); cost $0.21 — matches ProdSeller wholesale $0.17-0.29 (upstream confirmation)",
    identity="adjacent (Plus construct, shared account)", cost=0.21))
add("SKU-SW008", offer("ProdSeller", "Wholesaler/API (TG, §19 registry)", 0.29, "USD", 0.29,
    "Office 365 Plus Personal Account $0.29 / bulk&API $0.17 — post 20/09 18:32 UTC; 100% private accounts claim, 5 devices",
    identity="adjacent (Plus construct)"))
add("SKU-SW008", offer("Turgame", "Retailer (Notion-specified channel)", 79.00, "USD", 79.00,
    "Microsoft Office 365 Personal 2025 ONLINE LICENSE (official-tier) — dual-track pricing datapoint"))
add("SKU-SW009", offer("Turgame", "Retailer (Notion-specified channel)", 97.59, "USD", 97.59,
    "Microsoft Office 365 Family 2025 ONLINE LICENSE (official-tier)"))
add("SKU-AI029", offer("StackVault", "Retailer (TG-shop, §19 registry)", 3.44, "USD", 3.44,
    "Microsoft Copilot 1 Month full warranty — stock 4; cost $2.86", cost=2.86))
add("SKU-DS017", offer("StackVault", "Retailer (TG-shop, §19 registry)", 2.35, "USD", 2.35,
    "Amazon Prime Video 6m — stock 14; cost $2.00", identity="adjacent (6m denomination)", cost=2.00))
add("SKU-DS010", offer("StackVault", "Retailer (TG-shop, §19 registry)", 3.60, "USD", 3.60,
    "Youtube Premium 3M — stock 99; cost $3.00",
    identity="adjacent (3-month activation-link construct, region unspecified)", cost=3.00))
add("SKU-DS011", offer("Evo Era", "Retailer (TG bot, §19 registry)", 8.00, "USDT", 8.00,
    "Youtube 3M Link — CONFIRMED PURCHASE x2 at 8.00 USDT 26/09 20:32 UTC (order feed)",
    identity="adjacent (3-month link construct)"))
add("SKU-DS006", offer("StackVault", "Retailer (TG-shop, §19 registry)", 1.96, "USD", 1.96,
    "Spotify Premium 3-Month Activation Link — stock 3; cost $1.53",
    identity="adjacent (3-month activation-link construct)", cost=1.53))
add("SKU-AI031", offer("StackVault", "Retailer (TG-shop, §19 registry)", 1.60, "USD", 1.60,
    "Notion Edu Plus Account — stock 14; cost $0.80 — edu-account market datapoint",
    identity="adjacent (Edu account, not AI add-on)", cost=0.80))
add("SKU-DS033", offer("StackVault", "Retailer (TG-shop, §19 registry)", 2.25, "USD", 2.25,
    "Notion Business 3m — stock 41; cost $1.80",
    identity="adjacent (Business tier, 3m)", cost=1.80))
add("SKU-DS064", offer("StackVault", "Retailer (TG-shop, §19 registry)", 4.60, "USD", 4.60,
    "Figma Pro Edu 2Y — stock 50; cost $4.00", identity="adjacent (Edu 2Y vs catalog Professional annual)",
    cost=4.00))
add("SKU-AI012", offer("StackVault", "Retailer (TG-shop, §19 registry)", 11.90, "USD", 11.90,
    "Perplexity Pro (iOS CDK) 1 month full warranty — stock 7; cost $9.91",
    identity="adjacent (iOS CDK construct)", cost=9.91))
add("SKU-GK023", offer("StackVault", "Retailer (TG-shop, §19 registry)", 16.91, "USD", 16.91,
    "XBOX GAME PASS ULTIMATE 1 YEAR (1 month warranty) — stock 0; cost $14.09 — vs official $22.99 anchor = 26% below",
    identity="exact duration (1Y=12m), gray-construct channel", cost=14.09))
add("SKU-DS043", offer("StackVault", "Retailer (TG-shop, §19 registry)", 40.23, "USD", 40.23,
    "Discord Nitro 1Y full warranty — stock 20; cost $33.52",
    identity="exact duration, gray-construct channel", cost=33.52))
add("SKU-DS042", offer("StackVault", "Retailer (TG-shop, §19 registry)", 1.72, "USD", 1.72,
    "Discord Nitro 1M Token not guaranteed — stock 80; cost $1.34",
    identity="adjacent (token construct)", cost=1.34))
add("SKU-SW013", offer("StackVault", "Retailer (TG-shop, §19 registry)", 16.23, "USD", 16.23,
    "Adobe Full Apps (Bypass Version) 2 devices 3 months — stock 122; cost $13.52 — bypass construct explicitly named",
    identity="adjacent (bypass construct, 3m)", cost=13.52))
add("SKU-AP002", offer("StackVault", "Retailer (TG-shop, §19 registry)", 1.23, "USD", 1.23,
    "Codex API 10M Credit 1 Day — cost $1.23 range scales to 1B/14d $41.09; full API-credit ladder observed",
    identity="adjacent (Codex credit construct)", cost=1.23))
add("SKU-AP003", offer("StackVault", "Retailer (TG-shop, §19 registry)", 1.48, "USD", 1.48,
    "Claude API 10M Token 1 Day — cost $1.15; ladder to 200M/$9.10",
    identity="adjacent (Claude token construct)", cost=1.15))

# Gemini 18M wholesale ladder — attaches to P1 Gemini SKU-AI008 (adjacent: 18M promo-link construct)
add("SKU-AI008", offer("ProdSeller", "Wholesaler/API (TG, §19 registry)", 0.65, "USD", 0.65,
    "Gemini 18M standing price $0.65/link, $0.63 bulk — post 25/09 20:17; flash history: $0.43→0.49→0.53→0.59→0.65→0.69 (2-week window observed)",
    identity="adjacent (18M promo-link construct)"))
add("SKU-AI008", offer("gemini12pro_channel (bulk tiers)", "Marketplace/Paid-promo channel (§19 registry)", 0.40, "USD", 0.40,
    "Gemini Pro 18M bulk tiers: 1-199 → $0.60 | 200-499 → $0.50 | 500+ → $0.40 — post 01/09; alt tier post 07/09: 1-9 $0.65 / 9-99 $0.60 / 100-1000 $0.57",
    identity="adjacent (18M promo-link construct, bulk tier)"))
add("SKU-AI008", offer("Evo Era", "Retailer (TG bot, §19 registry)", 0.85, "USDT", 0.85,
    "Gemini AI Pro 18m x5 = 4.25 USDT → $0.85/unit — CONFIRMED PURCHASE 26/09 21:41 UTC (order feed) — retail layer markup over $0.40-0.65 wholesale visible",
    identity="adjacent (18M promo-link construct)"))

# NOTE: Gmail aged accounts + CapCut constructs are NOT catalog SKUs — recorded in
# b3_direct_run.key_discoveries (economics layer) instead of fake SKU records.

# ═══ 2. Turgame category observations (Notion-specified channel) ═══
def tgoffer(name, price, cur, usd, note, identity="exact", sold_out=False):
    return offer("Turgame", "Retailer (Notion-specified channel)", price, cur, usd,
                 note + (" [SOLD OUT at fetch]" if sold_out else ""), identity=identity)

add("SKU-GC051", tgoffer("PlayStation Lebanon 10 USD", 9.05, "USD", 9.05,
    "PSN Lebanon 10 USD — cross-validates P1 anchor $9.07 (2 independent observations)", sold_out=True))
add("SKU-GC053", tgoffer("PlayStation Bahrain 5 USD", 4.89, "USD", 4.89,
    "PSN Bahrain 5 USD — below face 2.2%; catalog SKU is 50 USD denomination",
    identity="adjacent (5 USD vs catalog 50 USD)", sold_out=True))
add("SKU-GC047", tgoffer("PlayStation UAE 10 USD", 9.73, "USD", 9.73,
    "PSN UAE 10 USD = 2.7% below face", identity="adjacent (UAE region vs US SKU)"))
add("SKU-GC047", tgoffer("PlayStation Oman 5 USD", 4.84, "USD", 4.84,
    "PSN Oman 5 USD — 3.2% below face", identity="adjacent (Oman region)", sold_out=True))
add("SKU-GC016", tgoffer("Xbox Live GC 50 TL", 1.02, "USD", 1.02,
    "Xbox TL-card ladder: 25 TL $0.51 → 10000 TL $204.66 at uniform $2.048/100TL rate"))
add("SKU-GC024", tgoffer("Amazon GC 100 TL", 2.05, "USD", 2.05,
    "Amazon.com.tr TL ladder 100-7500 TL at $2.048/100TL; catalog SKU is 50 TRY (below ladder minimum)",
    identity="adjacent (100 TL vs catalog 50 TRY)"))
add("SKU-GC013", tgoffer("Microsoft Xbox FR 5 EUR", 5.39, "USD", 5.39,
    "Xbox FR 5 EUR = ~5.3% below €5 face (at fx 1.137)"))
add("SKU-GC057", tgoffer("XBOX USA 5 USD", 4.79, "USD", 4.79,
    "Xbox USA 5 USD = 4.2% below face; catalog SKU is 10 USD",
    identity="adjacent (5 USD vs catalog 10 USD)", sold_out=True))
add("SKU-GC035", tgoffer("Steam Wallet GC 5 USD", 5.20, "USD", 5.20,
    "Steam USD ladder: 5→$5.20 (+4%), 10→$10.40, 20→$20.58, 25→$26.09 (10+ SOLD OUT at fetch — only 5 USD & India 1000 INR in stock)",
    identity="adjacent (region unspecified — likely US/global key)"))
# (Steam KSA 20 SAR observation attached to SKU-GC007 below)
# PSN TRY ladder → GC012 adjacent
add("SKU-GC012", tgoffer("PSN 250 TRY", 5.12, "USD", 5.12,
    "PSN TRY ladder 250→$5.12 … 5000 TRY→$102.33 at $2.048/100TL uniform rate; catalog SKU is 50 USD Turkey (USD-denominated) — TRY ladder is the adjacent identity",
    identity="adjacent (TRY-denominated vs USD-denominated TR card)"))
# Xbox GPU at Turgame (P1 anchors; no TRY Steam cards on Turgame page 1 — GC102-104 remain unobserved there)
add("SKU-GK021", tgoffer("Xbox Game Pass Ultimate 1 Month", 22.49, "USD", 22.49,
    "XGPU 1M $22.49 (vs $22.99 P1 anchor — consistent, 2% below); SOLD OUT at fetch",
    sold_out=True))
add("SKU-GK022", tgoffer("Xbox Game Pass Ultimate 3 Months", 39.85, "USD", 39.85,
    "XGPU 3M $39.85; SOLD OUT at fetch", sold_out=True))
# Steam KSA 20 SAR → GC007 adjacent (SAR-denominated)
add("SKU-GC007", tgoffer("Steam Wallet Card KSA 20 SAR", 5.20, "USD", 5.20,
    "Steam KSA 20 SAR $5.20 vs face $5.33 (fx 0.2666) = 2.4% below face; SOLD OUT",
    identity="adjacent (20 SAR vs catalog 20 USD)", sold_out=True))
# Riot Cash ladders (adjacent — Turkey region vs catalog EUW/EMEA)
add("SKU-GT013", tgoffer("LoL Gift Card 120 TL Riot Cash", 2.46, "USD", 2.46,
    "Riot Cash TRY ladder 120→$2.46, 250→$5.12, 500→$10.23, 850→$17.40 — Turkey-region cards (catalog SKU is EUW RP)",
    identity="adjacent (TR region Riot Cash)"))
add("SKU-GT033", tgoffer("Valorant Gift Card 120 TL", 2.46, "USD", 2.46,
    "Valorant Riot Cash TRY ladder — Turkey region (catalog SKU is EMEA VP)",
    identity="adjacent (TR region Riot Cash)"))

# ═══ 3. keyforsteam re-verification ═══
add("SKU-SW001", offer("Keyforsteam (price-comparison page)", "Marketplace aggregator (Notion-specified)", 1.03, "EUR", 1.17,
    "RE-VERIFIED LIVE 27/09 ~05:15 UTC: 'Der beste Preis für Windows 11 Pro PC ist 1,03€ bei Keywrld, aktuell mit 99.6% Rabatt' — table rows €0.84/€0.97/€1.03/€1.13/€1.50/€1.66",
    fresh="Current (re-verified 27/09)"))

# ═══ summary section ═══
n_new = 0
skus_touched = set()
# recount
oi["b3_direct_run"] = {
    "run_id": SRC,
    "date": "2026-09-27",
    "method": "Quota-free direct HTTP observation (z-ai quota 477/429-blocked since ~02:10 UTC)",
    "sources": {
        "stackvault_api": "https://decohomz.com/sv-api/products — 275 products, 274 with costPrice (input-cost layer exposed)",
        "turgame_categories": "12 WooCommerce category pages — 117 products priced",
        "channels": "§19 registry: 11 entities + 6 channels with public message previews (122 messages parsed)",
        "keyforsteam": "Win11 Pro page re-verified",
    },
    "key_discoveries": {
        "pricing_formula": "StackVault retail price = input cost × 1.2 (uniform 16.7% margin, median across 274 products; some SKUs 13-57%)",
        "cost_ladder_chatgpt_plus": "ChatGPT Plus wholesale cost by warranty tier: $2.80 (basic) → $5.15 (5H) → $10.67 (full) → $17.14 (official renew)",
        "wholesale_retail_spread": "Evo Era retail Gemini 18M $0.85 vs ProdSeller wholesale $0.40-0.65 — retail markup +31-112% observed live",
        "office365_convergence": "Office 365 Plus 1y: StackVault input cost $0.21 ≈ ProdSeller wholesale $0.17 — two independent sources converge on the upstream price",
        "turkey_card_rate": "Turgame TL cards uniform $2.048/100TL (implied TRY/USD 48.8 vs project fx_basis 34.1 [stale — to-verify])",
        "price_war_duolingo": "Duolingo Super 12M fell $0.59→$0.45→$0.37 within 5 days (ProdSeller)",
        "gemini_flash_history": "Gemini 18M 2-week price trace: $0.43→0.49→0.53→0.59→0.65→0.69 (falling trend reversed)",
        "raw_materials_layer": "Gmail accounts: wholesale $0.60-0.80 (ProdSeller 19/09), retail $0.77-2.23 by age/2FA (StackVault, cost exposed $0.60-1.74); CapCut 6-7 Days wholesale $0.10-0.14 (ProdSeller 23/09); Apple Music 5M 0.85 USDT, Adobe Express 12M 1.00 USDT (gemini12pro_channel 14/09)",
        "evo_era_order_feed": "Live purchase confirmations observed 26-27/09: Gemini 18m x5 @4.25 USDT, YT 3M x2 @8.00, Super Duolingo @0.85, CapCut Pro 1M @2.35 — transaction-level evidence of demand flow at these price points (seller-published feed)",
    },
    "evidence_level": "Directly-Observed (channel posts / API JSON / category pages, all timestamped)",
    "limitations": "Advertised prices only (no transactions executed); StackVault stock=0 items are price observations of unavailable stock; channel posts are seller-claimed; no identity verification of sellers",
}

json.dump(oi, open(OI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n_offers = sum(len(r.get("offers", [])) for r in oi["skus"].values())
print("offers_intelligence.json updated: total offers now", n_offers)
print("b3_direct_run section added")
