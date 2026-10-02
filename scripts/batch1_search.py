#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phase 2 — Batch 1 Research Execution (v4.2 architecture)
Run Contract: MEC1-20260927-B1 | C4 = 96 Research Actions + 25% reserve (24)
Channels = Notion-specified only (Amendment A): Eneba, Turgame, Kinguin, G2A,
CDKeys, Allkeyshop, GG.deals, Keys4us, Gocdkeys, RoyalCDKeys, CJS, GGSel,
Keyforsteam, Z2U, Plati, Reloadly, Ding, DT One, Mega Center, Al Momaiz,
FazerCards, official sources, Telegram entities + discovery channels.
Every action logged per v4.1 §0.1 (action ID, query, status, yield, debit).
"""
import json, os, subprocess, time, sys

BASE = "/home/z/my-project"
RD = os.path.join(BASE, "research")
AD = os.path.join(RD, "actions")
os.makedirs(AD, exist_ok=True)

# ─── Run Contract ───
RUN = {
    "run_id": "MEC1-20260927-B1",
    "prompt_version": "v4.2 Candidate (working)",
    "start_time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "batch": 1,
    "scope": "46 P1 SKUs (catalog CP-1, download/catalog_v42.json)",
    "complexity": "C4",
    "budget_total": 96,
    "budget_reserve": 24,
    "budget_used": 0,
    "channels_policy": "Notion-specified references/channels only (Amendment A)",
}
with open(os.path.join(RD, "run_contract.json"), "w", encoding="utf-8") as f:
    json.dump(RUN, f, ensure_ascii=False, indent=1)

# ─── Action definitions: (action_id, skus, family, discovery_family, query) ───
A = []
def a(skus, fam, dfam, q):
    A.append({"skus": skus, "family": fam, "discovery_family": dfam, "query": q})

# — Gift Cards (12 P1) —
a(["SKU-GC037","SKU-GC039"],"Gift Cards","Marketplace-first","eneba steam gift card 20 USD price")
a(["SKU-GC037"],"Gift Cards","Product-first","turgame steam wallet gift card 20 USD price")
a(["SKU-GC039"],"Gift Cards","Marketplace-first","kinguin steam gift card 50 USD price")
a(["SKU-GC037"],"Gift Cards","Marketplace-first","g2a steam wallet gift card 20 USD price")
a(["SKU-GC037"],"Gift Cards","Marketplace-first","cdkeys steam wallet gift card price")
a(["SKU-GC047","SKU-GC049"],"Gift Cards","Product-first","eneba playstation network card 50 USD price")
a(["SKU-GC049"],"Gift Cards","Price-first","playstation network card 50 USD cheapest price comparison")
a(["SKU-GC051"],"Gift Cards","Product-first","turgame psn playstation card 10 USD lebanon price")
a(["SKU-GC047"],"Gift Cards","Price-first","psn card 10 USD united states cheapest")
a(["SKU-GC062","SKU-GC063","SKU-GC064","SKU-GC065"],"Gift Cards","Product-first","apple itunes gift card UAE 100 AED price")
a(["SKU-GC062"],"Gift Cards","Product-first","apple gift card 50 AED dubai buy online")
a(["SKU-GC062","SKU-GC063"],"Gift Cards","Price-first","itunes gift card UAE cheapest price reseller")
a(["SKU-GC037","SKU-GC049"],"Gift Cards","Price-first","gg.deals steam gift card price comparison")
# — AI/SaaS (6 P1) —
a(["SKU-AI001"],"AI/SaaS","Product-first","chatgpt plus subscription price official 20 dollars")
a(["SKU-AI001"],"AI/SaaS","Seller-first","chatgpt plus cheap reseller price buy")
a(["SKU-AI005"],"AI/SaaS","Channel-first","ggsel chatgpt plus price")
a(["SKU-AI005"],"AI/SaaS","Channel-first","z2u chatgpt plus account price")
a(["SKU-AI006"],"AI/SaaS","Product-first","claude pro subscription price official")
a(["SKU-AI006"],"AI/SaaS","Seller-first","claude pro cheap reseller buy")
a(["SKU-AI008"],"AI/SaaS","Product-first","gemini advanced google AI pro subscription price")
a(["SKU-AI008"],"AI/SaaS","Seller-first","gemini pro cheap reseller subscription")
a(["SKU-AI012"],"AI/SaaS","Product-first","perplexity pro subscription price")
a(["SKU-AI032"],"AI/SaaS","Product-first","canva pro subscription price official")
a(["SKU-AI032"],"AI/SaaS","Seller-first","canva pro cheap reseller invite")
# — Digital Subscriptions (10 P1) —
a(["SKU-DS002"],"Digital Subscriptions","Product-first","netflix standard plan price usa 2026")
a(["SKU-DS003"],"Digital Subscriptions","Product-first","netflix premium plan price usa")
a(["SKU-DS004"],"Digital Subscriptions","Price-first","netflix 12 months subscription cheap turkey argentina")
a(["SKU-DS002"],"Digital Subscriptions","Seller-first","netflix subscription cheap reseller shared account")
a(["SKU-DS006"],"Digital Subscriptions","Product-first","spotify premium individual price usa")
a(["SKU-DS007"],"Digital Subscriptions","Price-first","spotify premium 12 months cheap deal")
a(["SKU-DS010"],"Digital Subscriptions","Product-first","youtube premium individual price usa")
a(["SKU-DS011"],"Digital Subscriptions","Price-first","youtube premium 12 months cheap turkey")
a(["SKU-DS025"],"Digital Subscriptions","Product-first","nordvpn 2 year plan price official")
a(["SKU-DS025"],"Digital Subscriptions","Seller-first","nordvpn cheapest deal reseller key")
a(["SKU-DS037"],"Digital Subscriptions","Product-first","telegram premium 1 month price official")
a(["SKU-DS039"],"Digital Subscriptions","Price-first","telegram premium 12 months cheap reseller gift")
a(["SKU-DS037","SKU-DS039"],"Digital Subscriptions","Seller-first","telegram premium gift cheap buy stars")
a(["SKU-DS042"],"Digital Subscriptions","Product-first","discord nitro 1 month price official")
a(["SKU-DS042"],"Digital Subscriptions","Seller-first","discord nitro cheap reseller gift code")
# — Software (4 P1) —
a(["SKU-SW001"],"Software/Licenses","Price-first","windows 11 pro key cheapest price comparison")
a(["SKU-SW001"],"Software/Licenses","Seller-first","cjs cd keys windows 11 professional price")
a(["SKU-SW001"],"Software/Licenses","Seller-first","keyforsteam windows 11 pro key preis")
a(["SKU-SW001"],"Software/Licenses","Channel-first","ggsel windows 11 pro price rubles")
a(["SKU-SW004","SKU-SW005"],"Software/Licenses","Price-first","office 2021 pro plus key cheapest price")
a(["SKU-SW006"],"Software/Licenses","Price-first","office 2024 pro plus key cheapest price")
a(["SKU-SW004"],"Software/Licenses","Seller-first","royalcdkeys office 2021 pro plus price")
a(["SKU-SW004"],"Software/Licenses","Seller-first","gocdkeys office 2021 price")
# — Game Keys (2 P1) —
a(["SKU-GK021"],"Game Keys","Product-first","xbox game pass ultimate 1 month price official")
a(["SKU-GK022"],"Game Keys","Price-first","xbox game pass ultimate 3 months cheapest price")
a(["SKU-GK021"],"Game Keys","Marketplace-first","eneba xbox game pass ultimate price")
a(["SKU-GK022"],"Game Keys","Marketplace-first","cdkeys xbox game pass ultimate 3 month")
# — Game Top-up (7 P1) —
a(["SKU-GT001"],"Game Top-up","Price-first","free fire 110 diamonds price cheapest top up")
a(["SKU-GT001"],"Game Top-up","Seller-first","free fire diamonds top up cheap store")
a(["SKU-GT004"],"Game Top-up","Price-first","pubg mobile 60 uc price cheapest")
a(["SKU-GT004"],"Game Top-up","Seller-first","pubg mobile uc top up cheap site")
a(["SKU-GT008"],"Game Top-up","Price-first","mobile legends 86 diamonds price")
a(["SKU-GT011"],"Game Top-up","Price-first","valorant 1000 points price buy cheap")
a(["SKU-GT014"],"Game Top-up","Price-first","fortnite 1000 v-bucks price cheapest")
a(["SKU-GT016"],"Game Top-up","Price-first","roblox 400 robux price buy cheap")
# — eSIM (3 P1) —
a(["SKU-ES001"],"eSIM","Product-first","travel esim usa 1gb 7 days price")
a(["SKU-ES003"],"eSIM","Product-first","esim saudi arabia 5gb 30 days price")
a(["SKU-ES005"],"eSIM","Product-first","esim uae 1gb 7 days price cheapest")
a(["SKU-ES001","SKU-ES003","SKU-ES005"],"eSIM","Price-first","cheapest travel esim data packages comparison")
# — Virtual Numbers (3 P1) —
a(["SKU-VN001"],"Virtual Numbers","Product-first","telegram virtual number russia price sms activation")
a(["SKU-VN003"],"Virtual Numbers","Product-first","telegram virtual number kazakhstan price")
a(["SKU-VN004"],"Virtual Numbers","Product-first","telegram virtual number indonesia price")
a(["SKU-VN001","SKU-VN003","SKU-VN004"],"Virtual Numbers","Price-first","sms activation service cheapest telegram number")
# — API Services (2 P1) —
a(["SKU-AP001"],"API Services","Product-first","openai api credits buy 100 dollars")
a(["SKU-AP004"],"API Services","Product-first","reloadly gift card api pricing reseller")
# — Upstream/Wholesale discovery (lexicon: Role+Commercial+Access terms) —
a(["SKU-GC037","SKU-GC049"],"Gift Cards","B2B/Catalog-oriented","gift card wholesale distributor B2B supplier API")
a(["SKU-GK021","SKU-GK022"],"Game Keys","B2B/Catalog-oriented","game keys wholesale distributor supplier reseller")
a(["SKU-DS037","SKU-DS042"],"Digital Subscriptions","B2B/Catalog-oriented","digital subscriptions wholesale reseller panel")
a(["SKU-AP004"],"API Services","Referral-first","reloadly vs ding vs dt one gift card api reseller comparison")
a(["SKU-GC037"],"Gift Cards","Referral-first","turgame wholesale program reseller")
a(["SKU-GC037"],"Gift Cards","Referral-first","kinguin business B2B wholesale")
a(["SKU-AI001","SKU-DS002"],"AI/SaaS","Channel-first","plati.market chatgpt plus netflix subscription price")
a(["SKU-AI005"],"AI/SaaS","Channel-first","ggsel netflix chatgpt catalog price rubles")
# — Telegram entities (Notion seeds — Discovery Leads verification) —
a(["SKU-DS037"],"Digital Subscriptions","Bot-first","telegram premium reseller bot channel cheap")
a(["SKU-GC037"],"Gift Cards","Bot-first","site:t.me steam gift card sell price")
a(["SKU-DS002"],"Digital Subscriptions","Channel-first","site:t.me netflix subscription sell")
a(["SKU-AI001"],"AI/SaaS","Channel-first","site:t.me chatgpt plus subscription")
# — Seed LEAD verification (SUP-011/012/013) —
a(["SKU-GC062"],"Gift Cards","Seller-first","mega center megatec-center digital products store")
a(["SKU-GC062"],"Gift Cards","Seller-first","al momaiz card almomaizcard digital store")
a(["SKU-GC062"],"Gift Cards","Seller-first","fazercards reseller platform gift cards price")
# — Official baselines (price reference points) —
a(["SKU-GK021"],"Game Keys","Document-first","xbox game pass ultimate official price 22.99")
a(["SKU-DS006"],"Digital Subscriptions","Document-first","spotify premium official pricing page")
a(["SKU-DS002"],"Digital Subscriptions","Document-first","netflix official plans pricing page")
a(["SKU-SW001"],"Software/Licenses","Document-first","windows 11 pro official price microsoft")

print("ACTIONS_PLANNED:", len(A))
ledger = []
# resume support: load existing ledger + skip completed actions
LEDGER_FILE = os.path.join(RD, "action_ledger.json")
if os.path.exists(LEDGER_FILE):
    try:
        ledger = json.load(open(LEDGER_FILE, encoding="utf-8"))
    except Exception:
        ledger = []
done_ids = {l["action_id"] for l in ledger}
for i, act in enumerate(A):
    aid = "RA-%03d" % (i + 1)
    if aid in done_ids:
        continue
    t0 = time.time()
    out_file = os.path.join(AD, aid + ".json")
    ok, status, note = True, "OK", ""
    try:
        r = subprocess.run(
            ["z-ai", "function", "-n", "web_search",
             "-a", json.dumps({"query": act["query"], "num": 6}, ensure_ascii=False),
             "-o", out_file],
            capture_output=True, text=True, timeout=75)
        if r.returncode != 0:
            ok, status, note = False, "FAILED", (r.stderr or r.stdout)[:200]
        elif not os.path.exists(out_file) or os.path.getsize(out_file) < 30:
            ok, status, note = False, "EMPTY", "no output file"
    except subprocess.TimeoutExpired:
        ok, status, note = False, "TIMEOUT", "75s"
    except Exception as e:
        ok, status, note = False, "ERROR", str(e)[:200]
    dur = round(time.time() - t0, 1)
    n_res = 0
    if ok:
        try:
            data = json.load(open(out_file, encoding="utf-8"))
            n_res = len(data) if isinstance(data, list) else len(data.get("results", []))
        except Exception:
            n_res = 0
    entry = {
        "action_id": aid, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "batch": 1, "objective": "Batch1 P1 price discovery",
        "family": act["family"], "discovery_family": act["discovery_family"],
        "method": "web_search (z-ai CLI)", "query": act["query"],
        "targets": act["skus"], "retrieval_status": status if ok else "Failed",
        "results_count": n_res, "duration_s": dur,
        "yield": "pending-classification", "budget_debit": 1,
        "note": note,
    }
    ledger.append(entry)
    RUN["budget_used"] = len([l for l in ledger if l["budget_debit"]])
    print("%s %s n=%d %.1fs | %s" % (aid, status, n_res, dur, act["query"][:60]))
    time.sleep(0.4)
    # checkpoint every 12 actions
    if (i + 1) % 12 == 0:
        json.dump(ledger, open(os.path.join(RD, "action_ledger.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

json.dump(ledger, open(os.path.join(RD, "action_ledger.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
RUN["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
json.dump(RUN, open(os.path.join(RD, "run_contract.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ok_n = len([l for l in ledger if l["retrieval_status"] == "OK"])
print("BATCH1_SEARCH_DONE: actions=%d ok=%d failed=%d budget_used=%d/96" % (len(ledger), ok_n, len(ledger)-ok_n, RUN["budget_used"]))
