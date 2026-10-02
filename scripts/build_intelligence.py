#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phases 3-4 — Master offers ledger + price intelligence.
Merges: (1) direct observations 27/09 (RA-122..142), (2) advertised snippets 27/09,
(3) prior-run direct observations 25/09 (documented in Notion authority page).
Every offer carries: evidence level, freshness, seller, role, source, date.
Roles per six-layer taxonomy. Prices in native currency + USD-normalized (rate basis).
"""
import json, re, os

RD = "/home/z/my-project/research"
OUT = "/home/z/my-project/download"
TODAY = "2026-09-27"
PRIOR = "2026-09-25"

# FX basis: prior-run documented rates (Wise 25/09: 1 EUR=1.137 USD; GBP≈1.3548; RUB≈0.0126)
FX = {"USD": 1.0, "EUR": 1.137, "GBP": 1.3548, "RUB": 0.0126, "TRY": 0.0293, "AED": 0.2723, "SAR": 0.2666}

def usd(amount, cur):
    return round(amount * FX.get(cur, 1.0), 2)

# ─── Helper: advertised snippet prices from today's searches (evidence=Advertised) ───
fi = json.load(open(RD + "/findings_index.json", encoding="utf-8"))
def snippet_prices(sku, must_words=None, exclude_hosts=None):
    out = []
    for f in fi["findings"]:
        if sku not in f["targets"]: continue
        if exclude_hosts and any(h in f["host"] for h in exclude_hosts): continue
        text = f["title"] + " " + f["snippet"]
        if must_words and not all(w.lower() in text.lower() for w in must_words): continue
        for m in re.finditer(r'(\$|€|£|₽)\s?([0-9]{1,5}(?:[.,][0-9]{1,2})?)', text):
            cur = {"$":"USD","€":"EUR","£":"GBP","₽":"RUB"}[m.group(1)]
            amt = float(m.group(2).replace(",", "."))
            if amt <= 0 or amt > 2000: continue
            out.append({"seller_host": f["host"], "price": amt, "cur": cur, "usd": usd(amt, cur),
                        "context": (f["snippet"][:160]), "url": f["url"], "date": f.get("date","")})
    # dedupe by host+price
    seen, ded = set(), []
    for o in out:
        k = (o["seller_host"], o["price"])
        if k in seen: continue
        seen.add(k); ded.append(o)
    return sorted(ded, key=lambda x: x["usd"])

# ─── Build per-SKU intelligence ───
S = {}  # sku -> record
def sku(sku_id, base):
    S[sku_id] = base

# ===== AI/SaaS =====
sku("SKU-AI001", {  # ChatGPT Plus 1mo
    "identity": "ChatGPT Plus | 1 month | Global | account upgrade",
    "official": {"seller": "OpenAI", "price": 20.0, "cur": "USD", "evidence": "direct (prior-run 25/09) + official page retrieved 27/09 (JS-rendered price; $20 confirmed via multiple snippets)", "date": PRIOR},
    "offers": [
        {"seller": "GGSel marketplace (via YouTube promo snippet)", "role": "Marketplace sellers", "price": 2.43, "cur": "USD", "usd": 2.43, "evidence": "Advertised (snippet)", "freshness": "Unknown", "note": "promotional video snippet — lead only, terms unverified"},
        {"seller": "GGSel (RU marketplace)", "role": "Marketplace/Aggregator", "price": 749.0, "cur": "RUB", "usd": 9.44, "evidence": "Directly Observed (page title live 27/09)", "freshness": "Current", "note": "'Цены от 749.00₽' — multiple seller offers from 749₽ (e.g. 1688₽ 24/7 offer); intermediated/shared-account model likely — SKU identity differs (shared seat, see SKU-AI005)"},
    ],
})
sku("SKU-AI005", {  # ChatGPT Plus shared
    "identity": "ChatGPT Plus shared account | 1 month | Global | credentials",
    "offers": [
        {"seller": "Z2U marketplace", "role": "Marketplace (account resellers)", "price": 4.72, "cur": "USD", "usd": 4.72, "evidence": "Advertised (snippet)", "freshness": "Unknown", "note": "Z2U listing lead documented 25/09 and seen again 27/09"},
        {"seller": "GGSel sellers", "role": "Marketplace/Aggregator", "price": 749.0, "cur": "RUB", "usd": 9.44, "evidence": "Directly Observed (live 27/09)", "freshness": "Current", "note": "cheapest GGSel ChatGPT Plus offers are shared/intermediated — match class: Possible Match (account model)"},
    ],
})
sku("SKU-AI006", {  # Claude Pro
    "identity": "Claude Pro | 1 month | Global",
    "official": {"seller": "Anthropic", "price": 20.0, "cur": "USD", "evidence": "Advertised (multiple snippets $20; official page not directly retrieved)", "date": TODAY},
    "offers": snippet_prices("SKU-AI006")[:4],
})
sku("SKU-AI008", {  # Gemini Pro
    "identity": "Gemini AI Pro | 1 month | Global",
    "official": {"seller": "Google", "price": 19.99, "cur": "USD", "evidence": "Advertised (snippet $19.99)", "date": TODAY},
    "offers": [
        {"seller": "G2A", "role": "Marketplace", "price": 7.99, "cur": "USD", "usd": 7.99, "evidence": "Advertised (snippet: Gemini Pro 12 months account $7.99 — account model, duration differs)", "freshness": "Unknown", "note": "match class: Possible Match — 12-month account vs 1-month upgrade"},
    ] + snippet_prices("SKU-AI008", exclude_hosts=["g2a.com"])[:3],
})
sku("SKU-AI012", {"identity": "Perplexity Pro | 1 month", "official": {"seller": "Perplexity", "price": 20.0, "cur": "USD", "evidence": "Advertised (snippet)", "date": TODAY}, "offers": snippet_prices("SKU-AI012")[:3]})
sku("SKU-AI032", {"identity": "Canva Pro | 1 month", "official": {"seller": "Canva", "price": 15.0, "cur": "USD", "evidence": "Advertised (snippet ~$15/mo annual basis)", "date": TODAY}, "offers": snippet_prices("SKU-AI032")[:3]})

# ===== Gift Cards =====
sku("SKU-GC037", {  # Steam 20 US
    "identity": "Steam Wallet Gift Card 20 USD | US | code",
    "offers": [
        {"seller": "Eneba", "role": "Marketplace", "price": 20.93, "cur": "USD", "usd": 20.93, "evidence": "Directly Observed (prior-run 25/09)", "freshness": "Stale-risk (2d)", "note": "prior-run verified retail cheapest"},
        {"seller": "Turgame", "role": "Retailer/Reseller + verified Wholesaler", "price": None, "cur": "USD", "usd": None, "evidence": "Directly Observed (27/09): product page live = SOLD OUT", "freshness": "Current", "note": "availability state: Sold Out at 27/09 — price unavailable"},
        {"seller": "Kinguin", "role": "Marketplace", "price": None, "cur": "USD", "evidence": "Advertised (homepage snippets; product-level price not retrieved)", "freshness": "Unknown", "note": "Kinguin marketplace sells Steam wallet codes; exact offer prices not directly retrieved this run"},
        {"seller": "Turgame Wholesale (wholesale.turgame.com)", "role": "Wholesaler/Distributor — DIRECTLY VERIFIED live 27/09", "price": None, "cur": "USD", "evidence": "Directly Observed (portal title 'Digital Gift Card Wholesale Solutions')", "freshness": "Current", "note": "upstream wholesale channel exists; account-gated pricing (login required) — wholesale price Unknown"},
    ],
})
sku("SKU-GC039", {"identity": "Steam Wallet 50 USD | US", "offers": snippet_prices("SKU-GC039")[:4] or [{"seller": "Eneba (prior-run)", "role": "Marketplace", "price": None, "evidence": "prior-run: Steam 20=20.93$; 50$ not separately verified", "freshness": "Unknown"}]})
sku("SKU-GC047", {"identity": "PSN 10 USD | US", "offers": [
    {"seller": "Eneba (via search snippet: psn 10 usd usa)", "role": "Marketplace", "price": None, "evidence": "product URL found (eneba.com/us/psn-...10-usd...); page price not directly retrieved (Eneba URL 404 on other patterns)", "freshness": "Unknown"},
]})
sku("SKU-GC049", {  # PSN 50 US
    "identity": "PSN 50 USD | US",
    "offers": [
        {"seller": "Eneba", "role": "Marketplace", "price": 47.17, "cur": "USD", "usd": 47.17, "evidence": "Directly Observed (prior-run 25/09)", "freshness": "Stale-risk (2d)", "note": "5.66% below nominal — prior-run verified"},
        {"seller": "G2A", "role": "Marketplace", "price": None, "evidence": "Advertised presence", "freshness": "Unknown"},
    ],
})
sku("SKU-GC051", {"identity": "PSN 10 USD | Lebanon", "offers": [{"seller": "Turgame", "role": "Retailer/Reseller", "price": 9.07, "cur": "USD", "usd": 9.07, "evidence": "Directly Observed (prior-run 25/09)", "freshness": "Stale-risk (2d)", "note": "9.3% below nominal — deepest discount in prior run"}]})
for sid, denom in [("SKU-GC062","50 AED"),("SKU-GC063","100 AED"),("SKU-GC064","200 AED"),("SKU-GC065","500 AED")]:
    sku(sid, {"identity": "Apple Gift Card %s | UAE" % denom,
        "offers": [
            {"seller": "FazerCards (reseller.fazercards.com)", "role": "Reseller Platform — SUP-013 LEAD VERIFIED live 27/09", "price": None, "cur": "AED", "evidence": "Directly Observed (platform live; per-denomination prices behind login/catalog navigation)", "freshness": "Current", "note": "platform verified; specific AED-denomination offers need catalog navigation (B2B reseller model)"},
        ] + snippet_prices(sid)[:2],
        "prior_run_note": "SKU-001 prior run: no qualifying offer within scope/date for Apple UAE — category remains under-covered"})

# ===== Game Top-up (snippet-level) =====
for sid in ["SKU-GT001","SKU-GT004","SKU-GT008","SKU-GT011","SKU-GT014","SKU-GT016"]:
    sp = snippet_prices(sid)
    sku(sid, {"identity": sid, "offers": sp[:4] if sp else [], "coverage_state": "Advertised-level only (Retrieval-Limited during rate-limit window; recovered partially)"})

# ===== Game Keys =====
sku("SKU-GK021", {"identity": "Xbox Game Pass Ultimate 1 month",
    "official": {"seller": "Microsoft Xbox", "price": 22.99, "cur": "USD", "evidence": "Directly Observed (xbox.com live 27/09)", "freshness": "Current", "note": "official $22.99/month confirmed on page"},
    "offers": snippet_prices("SKU-GK021")[:3]})
sku("SKU-GK022", {"identity": "Xbox Game Pass Ultimate 3 months",
    "offers": [
        {"seller": "G2A (category page)", "role": "Marketplace", "price": 13.99, "cur": "USD", "usd": 13.99, "evidence": "Advertised (snippet: GPU offers $14.99/$13.99/$22.99)", "freshness": "Unknown", "note": "lowest listed offer in G2A category snippet — likely 1-month equivalent or partial; match class: Possible Match"},
        {"seller": "GG.deals (subscription tracker)", "role": "Price comparison", "price": 13.75, "cur": "USD", "usd": 13.75, "evidence": "Advertised (snippet: $46.19/$13.75 for 3-month)", "freshness": "Unknown", "note": "gg.deals subscription page snippet; Cloudflare blocked direct read on 25/09"},
    ] + snippet_prices("SKU-GK022", exclude_hosts=["g2a.com","gg.deals"])[:2]})

# ===== Software =====
sku("SKU-SW001", {  # Win11 Pro
    "identity": "Windows 11 Pro license | retail key | Global",
    "offers": [
        {"seller": "Keyforsteam daily best — seller 'Keywrld'", "role": "Marketplace seller", "price": 1.03, "cur": "EUR", "usd": 1.17, "evidence": "Directly Observed (keyforsteam.de homepage live 27/09)", "freshness": "Current", "note": "daily-best listing; edition/OEM-vs-retail semantics to verify — deep-discount market"},
        {"seller": "Allkeyshop comparison", "role": "Price comparison", "price": 1.22, "cur": "USD", "usd": 1.22, "evidence": "Advertised (snippet)", "freshness": "Unknown"},
        {"seller": "CJS CD Keys", "role": "Retailer/Reseller", "price": 9.49, "cur": "GBP", "usd": 12.85, "evidence": "Directly Observed (cjs-cdkeys.com live 27/09: 'Key from £9.49')", "freshness": "Current", "note": "prior-run £9.99 → 27/09 £9.49 (price moved); CJS publishes money-back guarantee policy"},
        {"seller": "GGSel (RU)", "role": "Marketplace/Aggregator", "price": 977.47, "cur": "RUB", "usd": 12.32, "evidence": "Directly Observed (prior-run 25/09)", "freshness": "Stale-risk (2d)"},
    ],
    "official": {"seller": "Microsoft", "price": 199.0, "cur": "USD", "evidence": "Advertised (MSRP reference documented 25/09)", "date": PRIOR},
})
sku("SKU-SW004", {  # Office 2021
    "identity": "Office 2021 Pro Plus | key",
    "offers": [
        {"seller": "Keyforsteam Preisvergleich — seller 'Pixelcodes' (phone activation)", "role": "Marketplace seller", "price": 2.44, "cur": "EUR", "usd": 2.77, "evidence": "Directly Observed (keyforsteam.de live 27/09: from 2,44€ / 2,60€ offers)", "freshness": "Current", "note": "phone-activation keys — SKU-SW005 identity; retail variant offers higher"},
        {"seller": "Allkeyshop", "role": "Price comparison", "price": 0.53, "cur": "USD", "usd": 0.53, "evidence": "Advertised (snippet)", "freshness": "Unknown", "note": "allkeyshop snippet $0.53 — likely activation-method variant; verify before comparison"},
        {"seller": "CJS CD Keys", "role": "Retailer/Reseller", "price": None, "evidence": "Directly Observed (storefront live; Office pricing visible in bundles)", "freshness": "Current"},
        {"seller": "RoyalCDKeys", "role": "Retailer/Reseller", "price": 4.59, "cur": "EUR", "usd": 5.22, "evidence": "Advertised (snippet €4,59)", "freshness": "Unknown"},
    ],
})
sku("SKU-SW005", {"identity": "Office 2021 Pro Plus | phone-activation key", "offers": [
    {"seller": "Keyforsteam sellers (Pixelcodes et al.)", "role": "Marketplace sellers", "price": 2.44, "cur": "EUR", "usd": 2.77, "evidence": "Directly Observed (live 27/09: TELEFON AKTIVIERUNG offers from 2,44€)", "freshness": "Current"}]})
sku("SKU-SW006", {"identity": "Office 2024 Pro Plus | key", "offers": [
    {"seller": "Keyforsteam daily best — seller 'Keys4us'", "role": "Marketplace seller", "price": 0.56, "cur": "EUR", "usd": 0.64, "evidence": "Directly Observed (keyforsteam.de homepage live 27/09)", "freshness": "Current", "note": "consistent with prior-run 0.59€ lead (25/09) — deep-discount market segment"},
]})

# ===== eSIM =====
sku("SKU-ES001", {"identity": "eSIM USA 1GB/7d", "offers": [
    {"seller": "Airalo", "role": "eSIM retailer", "price": 4.0, "cur": "USD", "usd": 4.0, "evidence": "Directly Observed (airalo.com live 27/09: US from $4.00)", "freshness": "Current", "note": "US 1GB package ~$4.00 baseline (pack size on page to confirm)"}] + snippet_prices("SKU-ES001", exclude_hosts=["airalo.com"])[:2]})
sku("SKU-ES003", {"identity": "eSIM Saudi 5GB/30d", "offers": [
    {"seller": "Airalo (Saudi packages)", "role": "eSIM retailer", "price": None, "evidence": "Directly Observed (store live; SA package price to extract from catalog)", "freshness": "Current"},
    {"seller": "MobiMatter", "role": "eSIM reseller", "price": 12.99, "cur": "USD", "usd": 12.99, "evidence": "Advertised (snippet $12.99/21.99 ranges)", "freshness": "Unknown"}]})
sku("SKU-ES005", {"identity": "eSIM UAE 1GB/7d", "offers": [
    {"seller": "Airalo (UAE packages)", "role": "eSIM retailer", "price": None, "evidence": "Directly Observed (store live; UAE from ~$4.50 pattern seen in snippets)", "freshness": "Current"}] + snippet_prices("SKU-ES005", exclude_hosts=["airalo.com"])[:2]})

# ===== Virtual Numbers =====
for sid in ["SKU-VN001","SKU-VN003","SKU-VN004"]:
    sp = snippet_prices(sid)
    base = {"SKU-VN001": ("Russia", 0.20), "SKU-VN003": ("Kazakhstan", None), "SKU-VN004": ("Indonesia", None)}[sid]
    offers = []
    if base[1] is not None:
        offers.append({"seller": "SMS-activation providers (smscode.gg / nexsms.net)", "role": "OTP service providers", "price": base[1], "cur": "USD", "usd": base[1], "evidence": "Advertised (snippet $0.20-$0.60 per number)", "freshness": "Unknown", "note": "per-number OTP pricing; $0.006 rates seen = per-SMS bulk API rates"})
    offers += sp[:2]
    sku(sid, {"identity": "Telegram virtual number | %s | one-time" % base[0], "offers": offers, "coverage_state": "Advertised-level (market range $0.10-$0.60/number)"})

# ===== Digital Subscriptions =====
sku("SKU-DS002", {"identity": "Netflix Standard 1mo US",
    "official": {"seller": "Netflix", "price": 19.99, "cur": "USD", "evidence": "Directly Observed (help.netflix.com live 27/09: Standard $19.99, with-ads $8.99)", "freshness": "Current"},
    "offers": [{"seller": "Z2U (shared/private accounts)", "role": "Marketplace (account resellers)", "price": 1.87, "cur": "USD", "usd": 1.87, "evidence": "Advertised (snippet)", "freshness": "Unknown", "note": "account model — different SKU identity (shared account)"}] + snippet_prices("SKU-DS002", exclude_hosts=["z2u.com"])[:2]})
sku("SKU-DS003", {"identity": "Netflix Premium 1mo US", "official": {"seller": "Netflix", "price": None, "evidence": "page live 27/09; Premium tier present, exact figure in page (approx $24.99-29.99 range per snippets)", "freshness": "Current"}, "offers": snippet_prices("SKU-DS003")[:2]})
sku("SKU-DS004", {"identity": "Netflix Standard 12mo (TR/ARG region-priced)", "offers": snippet_prices("SKU-DS004")[:3], "note": "region-priced paths documented (Techmusea lead 25/09); formal region-migration SKUs not directly priced this run"})
sku("SKU-DS006", {"identity": "Spotify Premium Individual 1mo US",
    "official": {"seller": "Spotify", "price": 12.99, "cur": "USD", "evidence": "Directly Observed (spotify.com live 27/09: $12.99/mo after $0 first month)", "freshness": "Current"},
    "offers": snippet_prices("SKU-DS006")[:3]})
sku("SKU-DS007", {"identity": "Spotify Individual 12mo US", "offers": [
    {"seller": "Ozbargain-documented reseller threads", "role": "Resellers (forum-documented)", "price": 20.86, "cur": "USD", "usd": 20.86, "evidence": "Advertised (prior-run thread: 12mo US$20.86)", "freshness": "Stale-risk", "note": "marketplace/region-mix paths"}]})
sku("SKU-DS010", {"identity": "YouTube Premium Individual 1mo US",
    "official": {"seller": "Google/YouTube", "price": 15.99, "cur": "USD", "evidence": "Directly Observed (youtube.com/premium live 27/09: $15.99/mo; NEW: Premium Lite $8.99/mo)", "freshness": "Current"},
    "offers": snippet_prices("SKU-DS010")[:2]})
sku("SKU-DS011", {"identity": "YouTube Premium 12mo TR/ARG", "offers": [
    {"seller": "Region-priced paths (Techmusea-documented TR/IN/ARG)", "role": "Resellers", "price": 4.50, "cur": "USD", "usd": 4.50, "evidence": "Advertised (prior-run thread: TR ~$4.50/mo)", "freshness": "Stale-risk", "note": "requires account region conditions — not generalizable"}]})
sku("SKU-DS025", {"identity": "NordVPN Plus 2-year",
    "official": {"seller": "NordVPN", "price": None, "evidence": "Cloudflare-blocked 27/09 (Just a moment); prior-run direct 25/09 verified official pricing page + 30-day guarantee", "freshness": "Stale-risk (2d)"},
    "offers": [{"seller": "Allkeyshop (NordVPN key comparison)", "role": "Price comparison", "price": 4.88, "cur": "USD", "usd": 4.88, "evidence": "Advertised (snippet)", "freshness": "Unknown"}] + snippet_prices("SKU-DS025", exclude_hosts=["allkeyshop.com"])[:2]})
sku("SKU-DS037", {"identity": "Telegram Premium 1mo",
    "official": {"seller": "Telegram (in-app)", "price": 3.99, "cur": "USD", "evidence": "Advertised (snippet ~$3.99/mo; official blog page retrieved, price in-app)", "freshness": "Unknown"},
    "offers": snippet_prices("SKU-DS037")[:4]})
sku("SKU-DS039", {"identity": "Telegram Premium 12mo", "offers": snippet_prices("SKU-DS039")[:4],
    "note": "reseller gift market documented (bots/channels); fragment-documented 12mo gifts significantly below official aggregate"})
sku("SKU-DS042", {"identity": "Discord Nitro 1mo",
    "official": {"seller": "Discord", "price": 9.99, "cur": "USD", "evidence": "Directly Observed (discord.com/nitro live 27/09: Nitro Basic $2.99; full Nitro $9.99 standard)", "freshness": "Current"},
    "offers": [{"seller": "GG.deals", "role": "Price comparison", "price": 8.18, "cur": "USD", "usd": 8.18, "evidence": "Advertised (snippet)", "freshness": "Unknown"}] + snippet_prices("SKU-DS042")[:2]})

# ===== API =====
sku("SKU-AP001", {"identity": "OpenAI API credits $100", "official": {"seller": "OpenAI", "price": 100.0, "cur": "USD", "evidence": "Advertised (prepaid credits at face; help.openai.com $5/$10 gift tiers seen)", "freshness": "Unknown"}, "offers": snippet_prices("SKU-AP001")[:2]})
sku("SKU-AP004", {"identity": "Reloadly API (gift cards/payouts)",
    "offers": [{"seller": "Reloadly", "role": "API/Distributor — DIRECTLY VERIFIED live 27/09", "price": None, "cur": "USD", "evidence": "Directly Observed (reloadly.com: 'Gift Card & Payout API Platform' — products: Digital Gift Cards, Airtime, Data Bundles, Payout)", "freshness": "Current", "note": "reseller/API pricing behind 'Get API Keys' (account-gated) — wholesale spread Unknown without account"}],
    "role_resolution": "Reloadly dual-role resolved: (1) API/Distributor layer [VERIFIED live]; (2) direct retail channel — no retail storefront found → consolidated as B2B API/Distributor only"})

# ═══════════ PRICE INTELLIGENCE COMPUTATION ═══════════
intel = {}
for sid, rec in S.items():
    all_offers = []
    if rec.get("official"): 
        o = rec["official"]
        if o.get("price"):
            all_offers.append({"seller": o["seller"], "role": "Official/Primary", "price": o["price"], "cur": o.get("cur","USD"), "usd": usd(o["price"], o.get("cur","USD")), "evidence": o["evidence"], "level": "Official"})
    for o in rec.get("offers", []):
        if o.get("usd") is not None:
            all_offers.append(o)
    direct = [o for o in all_offers if "Directly Observed" in str(o.get("evidence",""))]
    adv = [o for o in all_offers if "Advertised" in str(o.get("evidence","")) or o.get("level") == "Official"]
    cheapest_direct = min(direct, key=lambda x: x["usd"]) if direct else None
    cheapest_adv = min(adv, key=lambda x: x["usd"]) if adv else None
    intel[sid] = {
        "identity": rec.get("identity", sid),
        "cheapest_directly_observed": cheapest_direct,
        "cheapest_advertised_or_official": cheapest_adv,
        "governing_formulation": "أقل سعر تم اكتشافه والتحقق منه ضمن نطاق البحث وتاريخ الفحص",
        "offers_count": len(all_offers),
    }

# coverage ledger update
cat = json.load(open(OUT + "/catalog_v42.json", encoding="utf-8"))
ledger_cov = cat["coverage_ledger"]
for sid in ledger_cov:
    if sid in S:
        has_direct = any("Directly Observed" in str(o.get("evidence","")) for o in S[sid].get("offers",[]))
        ledger_cov[sid]["state"] = "Verified (direct offer)" if has_direct else ("Partially Researched (advertised-level)" if S[sid].get("offers") else "Partially Researched")
        ledger_cov[sid]["last_checked"] = TODAY
cat["coverage_ledger"] = ledger_cov
json.dump(cat, open(OUT + "/catalog_v42.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

json.dump({"generated": TODAY, "run": "MEC1-20260927-B1", "fx_basis": FX,
           "skus": S, "price_intelligence": intel},
          open(OUT + "/offers_intelligence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

n_direct = sum(1 for sid,i in intel.items() if i["cheapest_directly_observed"])
n_adv = sum(1 for sid,i in intel.items() if i["cheapest_advertised_or_official"])
print("SKU_RECORDS: %d | with direct-observed cheapest: %d | with advertised/official: %d" % (len(S), n_direct, n_adv))
print("\n=== TOP FINDINGS (cheapest directly observed) ===")
rows = [(sid, i["cheapest_directly_observed"]) for sid,i in intel.items() if i["cheapest_directly_observed"]]
for sid, o in sorted(rows, key=lambda x: x[1]["usd"]):
    print("%-11s %8.2f USD | %-28s | %s" % (sid, o["usd"], o.get("seller","")[:28], str(o.get("evidence",""))[:40]))
