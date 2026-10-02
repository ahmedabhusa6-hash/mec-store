#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.1 | Batch 2 Research Execution (v4.2 architecture continuation)
Run Contract: MEC2-20260927-B2 | Scope: 173 P2 SKUs (catalog CP-1)
Complexity: C4 | Budget: 118 search actions + ~20 direct reads (separate) + 25% reserve
Channels = Notion-specified only (Amendment A): Eneba, Turgame, Kinguin, G2A, CDKeys,
Allkeyshop, GG.deals, Keys4us, Gocdkeys, RoyalCDKeys, CJS, GGSel, Keyforsteam, Z2U,
Plati, Reloadly, Ding, DT One, Mega Center, Al Momaiz, FazerCards, official sources,
Telegram entities + discovery channels.
Rate-limit protocol (MEC-2.0 lesson): 5s pacing + 15s cooldown + single retry -> zero failures.
Every action logged per v4.1 §0.1 (action ID, query, status, yield, debit). Action IDs: RB-xxx.
"""
import json, os, subprocess, time

BASE = "/home/z/my-project"
RD = os.path.join(BASE, "research")
AD = os.path.join(RD, "actions")
os.makedirs(AD, exist_ok=True)

RUN = {
    "run_id": "MEC2-20260927-B2",
    "prompt_version": "v4.2 Candidate (working)",
    "start_time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "batch": 2,
    "scope": "173 P2 SKUs (catalog CP-1, download/catalog_v42.json)",
    "complexity": "C4",
    "budget_total": 121,
    "budget_reserve": 30,
    "budget_used": 0,
    "channels_policy": "Notion-specified references/channels only (Amendment A)",
    "pacing": "5s between queries, 15s cooldown on failure, 1 retry",
}
with open(os.path.join(RD, "run_contract_b2.json"), "w", encoding="utf-8") as f:
    json.dump(RUN, f, ensure_ascii=False, indent=1)

# ─── Action definitions: (skus, family, discovery_family, query) ───
A = []
def a(skus, fam, dfam, q):
    A.append({"skus": skus, "family": fam, "discovery_family": dfam, "query": q})

# ═══ AI/SaaS (11 P2) ═══
a(["SKU-AI002","SKU-AI033"],"AI/SaaS","Product-first","chatgpt plus 12 months subscription price annual")
a(["SKU-AI002","SKU-AI033"],"AI/SaaS","Channel-first","ggsel chatgpt plus 12 months price")
a(["SKU-AI002","SKU-AI007","SKU-AI013"],"AI/SaaS","Channel-first","plati market chatgpt claude midjourney subscription price")
a(["SKU-AI003"],"AI/SaaS","Product-first","chatgpt go plan price monthly cheap")
a(["SKU-AI004"],"AI/SaaS","Product-first","chatgpt pro subscription 200 dollars price")
a(["SKU-AI007"],"AI/SaaS","Product-first","claude max subscription price monthly")
a(["SKU-AI010"],"AI/SaaS","Product-first","supergrok xai subscription price monthly")
a(["SKU-AI011"],"AI/SaaS","Product-first","deepseek api pricing per million tokens")
a(["SKU-AI013","SKU-AI014"],"AI/SaaS","Product-first","midjourney basic standard plan price monthly")
a(["SKU-AI029"],"AI/SaaS","Product-first","microsoft copilot pro price monthly")
a(["SKU-AI046"],"AI/SaaS","Product-first","github copilot pro price monthly")

# ═══ Gift Cards (52 P2) ═══
a(["SKU-GC001","SKU-GC002","SKU-GC003"],"Gift Cards","Marketplace-first","eneba steam gift card 5 10 20 EUR price")
a(["SKU-GC004"],"Gift Cards","Marketplace-first","kinguin steam gift card 50 EUR price")
a(["SKU-GC041","SKU-GC043","SKU-GC045"],"Gift Cards","Marketplace-first","eneba steam gift card EUR USD price comparison")
a(["SKU-GC035","SKU-GC036","SKU-GC038"],"Gift Cards","Marketplace-first","eneba steam gift card 5 10 30 USD price")
a(["SKU-GC040"],"Gift Cards","Marketplace-first","kinguin steam gift card 100 USD price")
a(["SKU-GC007"],"Gift Cards","Product-first","turgame steam wallet gift card 20 USD saudi arabia")
a(["SKU-GC008","SKU-GC048"],"Gift Cards","Marketplace-first","eneba playstation network card 25 20 USD price")
a(["SKU-GC009","SKU-GC010"],"Gift Cards","Marketplace-first","cdkeys playstation network card 25 50 EUR price")
a(["SKU-GC050"],"Gift Cards","Marketplace-first","kinguin psn card 100 USD price")
a(["SKU-GC052"],"Gift Cards","Price-first","playstation network card 50 USD argentina price")
a(["SKU-GC011"],"Gift Cards","Price-first","psn playstation card 50 USD saudi arabia price")
a(["SKU-GC053"],"Gift Cards","Price-first","psn card 50 USD bahrain price buy")
a(["SKU-GC031"],"Gift Cards","Price-first","playstation plus 3 months gift card price us")
a(["SKU-GC032"],"Gift Cards","Price-first","xbox game pass 3 months gift card price")
a(["SKU-GC057","SKU-GC058","SKU-GC059"],"Gift Cards","Marketplace-first","cdkeys xbox gift card 10 15 25 USD price")
a(["SKU-GC060","SKU-GC061"],"Gift Cards","Marketplace-first","cdkeys xbox gift card 50 100 USD price")
a(["SKU-GC066","SKU-GC067","SKU-GC068","SKU-GC069"],"Gift Cards","Marketplace-first","eneba apple gift card itunes 10 25 50 100 USD")
a(["SKU-GC022"],"Gift Cards","Product-first","apple itunes gift card 100 AED UAE price")
a(["SKU-GC070","SKU-GC072"],"Gift Cards","Marketplace-first","eneba google play gift card 10 25 USD price")
a(["SKU-GC074","SKU-GC076"],"Gift Cards","Marketplace-first","cdkeys google play gift card 50 100 USD")
a(["SKU-GC078","SKU-GC080","SKU-GC082","SKU-GC084"],"Gift Cards","Price-first","amazon gift card 25 50 100 USD digital discount")
a(["SKU-GC090","SKU-GC091","SKU-GC092"],"Gift Cards","Marketplace-first","razer gold gift card 5 10 20 USD price")
a(["SKU-GC093","SKU-GC094"],"Gift Cards","Marketplace-first","razer gold 50 100 USD gift card price")
a(["SKU-GC095","SKU-GC096"],"Gift Cards","Price-first","netflix gift card 50 100 USD price buy")
a(["SKU-GC097","SKU-GC098"],"Gift Cards","Price-first","spotify gift card 10 30 USD price")
a(["SKU-GC099","SKU-GC100","SKU-GC101"],"Gift Cards","Marketplace-first","eneba roblox gift card 10 25 50 USD")

# ═══ Game Top-up (15 P2) ═══
a(["SKU-GT002","SKU-GT003"],"Game Top-up","Price-first","free fire 560 1160 diamonds price top up")
a(["SKU-GT005","SKU-GT006","SKU-GT007"],"Game Top-up","Price-first","pubg mobile 325 660 1800 uc price")
a(["SKU-GT009","SKU-GT010"],"Game Top-up","Price-first","mobile legends 172 257 diamonds price")
a(["SKU-GT012"],"Game Top-up","Price-first","valorant 2050 points price cheap")
a(["SKU-GT015","SKU-GT035"],"Game Top-up","Price-first","fortnite 500 2800 v-bucks price")
a(["SKU-GT017","SKU-GT018"],"Game Top-up","Price-first","roblox 800 1700 robux price buy")
a(["SKU-GT019","SKU-GT020"],"Game Top-up","Price-first","genshin impact 300 1980 genesis crystals price")
a(["SKU-GT039"],"Game Top-up","Price-first","genshin impact welkin moon blessing price")
a(["SKU-GT005"],"Game Top-up","Channel-first","z2u pubg mobile uc top up price")
a(["SKU-GT002"],"Game Top-up","Seller-first","free fire diamonds top up cheapest store")

# ═══ Game Keys (18 P2) ═══
a(["SKU-GK001"],"Game Keys","Price-first","ea sports fc 26 cd key cheapest price")
a(["SKU-GK002"],"Game Keys","Price-first","ea sports fc 25 cd key cheapest price")
a(["SKU-GK003"],"Game Keys","Price-first","gta 5 cd key cheapest price")
a(["SKU-GK004"],"Game Keys","Price-first","elden ring cd key cheapest price")
a(["SKU-GK005"],"Game Keys","Price-first","cyberpunk 2077 cd key cheapest price")
a(["SKU-GK006"],"Game Keys","Price-first","hogwarts legacy cd key cheapest price")
a(["SKU-GK007"],"Game Keys","Price-first","baldur's gate 3 cd key cheapest price")
a(["SKU-GK008"],"Game Keys","Price-first","call of duty black ops 6 cd key price")
a(["SKU-GK009"],"Game Keys","Price-first","red dead redemption 2 cd key cheapest price")
a(["SKU-GK010"],"Game Keys","Price-first","starfield cd key cheapest price")
a(["SKU-GK014"],"Game Keys","Price-first","cs2 prime status upgrade key price")
a(["SKU-GK017"],"Game Keys","Price-first","monster hunter wilds cd key price")
a(["SKU-GK018"],"Game Keys","Price-first","assassin's creed shadows cd key price")
a(["SKU-GK019"],"Game Keys","Price-first","black myth wukong cd key price")
a(["SKU-GK023"],"Game Keys","Price-first","xbox game pass ultimate 12 months cheapest price")
a(["SKU-GK024"],"Game Keys","Product-first","pc game pass 1 month price")
a(["SKU-GK025"],"Game Keys","Price-first","playstation plus 3 months essential price")
a(["SKU-GK026"],"Game Keys","Price-first","playstation plus 12 months deluxe extra cheapest")
a(["SKU-GK004","SKU-GK007"],"Game Keys","Marketplace-first","eneba elden ring baldur's gate 3 key price")
a(["SKU-GK006","SKU-GK019"],"Game Keys","Marketplace-first","cdkeys hogwarts legacy black myth wukong price")

# ═══ Software/Licenses (6 P2) ═══
a(["SKU-SW002"],"Software/Licenses","Price-first","windows 11 home key cheapest price")
a(["SKU-SW003"],"Software/Licenses","Price-first","windows 10 pro key cheapest price")
a(["SKU-SW007"],"Software/Licenses","Seller-first","keyforsteam office 2024 pro plus key")
a(["SKU-SW008"],"Software/Licenses","Price-first","microsoft 365 personal 12 months key price")
a(["SKU-SW009"],"Software/Licenses","Price-first","microsoft 365 family 12 months key price")
a(["SKU-SW011"],"Software/Licenses","Price-first","adobe creative cloud all apps 12 months cheapest")
a(["SKU-SW002","SKU-SW007"],"Software/Licenses","Channel-first","ggsel windows office key price rubles")

# ═══ eSIM (7 P2) ═══
a(["SKU-ES002"],"eSIM","Product-first","airalo usa esim 3gb 30 days price")
a(["SKU-ES004"],"eSIM","Product-first","airalo saudi arabia esim 10gb price")
a(["SKU-ES006"],"eSIM","Product-first","airalo uae esim 3gb 30 days price")
a(["SKU-ES007"],"eSIM","Product-first","esim egypt 5gb 30 days price")
a(["SKU-ES010"],"eSIM","Price-first","esim europe 10gb 30 days cheapest price")
a(["SKU-ES012"],"eSIM","Price-first","global esim 1gb 7 days price")
a(["SKU-ES013"],"eSIM","Price-first","global esim 10gb 30 days cheapest")

# ═══ SMM Services (4 P2) ═══
a(["SKU-SM001"],"SMM Services","Price-first","smm panel instagram followers 1000 price")
a(["SKU-SM004"],"SMM Services","Price-first","smm panel tiktok followers 1000 price")
a(["SKU-SM006"],"SMM Services","Price-first","smm panel youtube subscribers 1000 price")
a(["SKU-SM009"],"SMM Services","Price-first","telegram channel members 1000 smm panel price")

# ═══ Virtual Numbers (26 P2) ═══
a(["SKU-VN002"],"Virtual Numbers","Product-first","telegram virtual number ukraine price sms")
a(["SKU-VN005"],"Virtual Numbers","Product-first","telegram virtual number usa price sms activation")
a(["SKU-VN006","SKU-VN007"],"Virtual Numbers","Product-first","telegram virtual number uk germany price")
a(["SKU-VN008"],"Virtual Numbers","Product-first","telegram virtual number egypt price")
a(["SKU-VN009","SKU-VN010","SKU-VN011"],"Virtual Numbers","Product-first","telegram number philippines vietnam india price")
a(["SKU-VN012"],"Virtual Numbers","Product-first","telegram virtual number nigeria price")
a(["SKU-VN013"],"Virtual Numbers","Product-first","whatsapp virtual number russia price")
a(["SKU-VN014","SKU-VN017"],"Virtual Numbers","Product-first","whatsapp virtual number indonesia egypt price")
a(["SKU-VN015","SKU-VN016"],"Virtual Numbers","Product-first","whatsapp virtual number usa uk price")
a(["SKU-VN020"],"Virtual Numbers","Product-first","universal otp virtual number usa price")
a(["SKU-VN021","SKU-VN030"],"Virtual Numbers","Product-first","google gmail virtual number price sms")
a(["SKU-VN022","SKU-VN023","SKU-VN024","SKU-VN025"],"Virtual Numbers","Product-first","instagram facebook discord tiktok virtual number russia price")
a(["SKU-VN026","SKU-VN027","SKU-VN028"],"Virtual Numbers","Product-first","tinder amazon whatsapp business number russia price")
a(["SKU-VN029","SKU-VN031"],"Virtual Numbers","Product-first","whatsapp telegram number indonesia price")
a(["SKU-VN001","SKU-VN003","SKU-VN004","SKU-VN021"],"Virtual Numbers","Price-first","sms-activate 5sim telegram number price comparison")

# ═══ Digital Subscriptions (25 P2) ═══
a(["SKU-DS001"],"Digital Subscriptions","Product-first","netflix standard with ads price usa monthly")
a(["SKU-DS005"],"Digital Subscriptions","Seller-first","netflix private account 1 month buy")
a(["SKU-DS008"],"Digital Subscriptions","Price-first","spotify premium family 12 months price")
a(["SKU-DS009"],"Digital Subscriptions","Price-first","spotify premium 12 months turkey price")
a(["SKU-DS012"],"Digital Subscriptions","Price-first","youtube premium family 12 months price")
a(["SKU-DS048"],"Digital Subscriptions","Price-first","youtube premium india price rupees monthly")
a(["SKU-DS013"],"Digital Subscriptions","Product-first","disney plus basic with ads price usa")
a(["SKU-DS014"],"Digital Subscriptions","Price-first","disney plus premium 12 months cheapest")
a(["SKU-DS015"],"Digital Subscriptions","Product-first","max subscription price usa monthly")
a(["SKU-DS016"],"Digital Subscriptions","Product-first","hulu subscription price usa monthly")
a(["SKU-DS017"],"Digital Subscriptions","Product-first","prime video subscription price usa")
a(["SKU-DS022"],"Digital Subscriptions","Product-first","apple music individual price usa")
a(["SKU-DS029","SKU-DS030"],"Digital Subscriptions","Product-first","icloud plus 50gb 200gb price monthly")
a(["SKU-DS031"],"Digital Subscriptions","Product-first","google one 100gb price monthly")
a(["SKU-DS026"],"Digital Subscriptions","Product-first","nordvpn 1 year plan price")
a(["SKU-DS038"],"Digital Subscriptions","Price-first","telegram premium 3 months price")
a(["SKU-DS040","SKU-DS041"],"Digital Subscriptions","Price-first","telegram stars 100 1000 price buy")
a(["SKU-DS043"],"Digital Subscriptions","Price-first","discord nitro 12 months price")
a(["SKU-DS049","SKU-DS050"],"Digital Subscriptions","Product-first","netflix egypt saudi arabia price monthly")
a(["SKU-DS061"],"Digital Subscriptions","Product-first","expressvpn 12 months plan price")
a(["SKU-DS062"],"Digital Subscriptions","Product-first","surfshark 24 months plan price")
a(["SKU-DS063"],"Digital Subscriptions","Price-first","canva pro annual 12 months cheapest price")

# ═══ API Services (9 P2) ═══
a(["SKU-AP002"],"API Services","Seller-first","openai api credits 500 buy discount reseller")
a(["SKU-AP003"],"API Services","Product-first","anthropic api credits pricing buy")
a(["SKU-AP007"],"API Services","Product-first","gemini api credits pricing 100")
a(["SKU-AP008"],"API Services","Price-first","sms activation api bulk otp price")
a(["SKU-AP009"],"API Services","Price-first","smm panel api reseller price")
a(["SKU-AP010"],"API Services","Price-first","esim distribution api reseller white label price")
a(["SKU-AP005","SKU-AP006"],"API Services","Price-first","ding dt one mobile top-up api reseller pricing")
a(["SKU-AP016"],"API Services","Referral-first","turgame bayi wholesale reseller program price")

print("ACTIONS_PLANNED:", len(A))
MAX_SECONDS = int(os.environ.get("MAX_SECONDS", "999999"))
T_START = time.time()
# coverage check
covered = set()
for act in A:
    covered.update(act["skus"])
import sys
with open(os.path.join(BASE, "download/catalog_v42.json"), encoding="utf-8") as f:
    cat = json.load(f)
p2 = [s["sku_id"] for s in cat["skus"] if s.get("priority") == "P2"]
missing = [s for s in p2 if s not in covered]
print("P2 total:", len(p2), "| covered by queries:", len([s for s in p2 if s in covered]), "| missing:", missing)

ledger = []
LEDGER_FILE = os.path.join(RD, "action_ledger.json")
if os.path.exists(LEDGER_FILE):
    try:
        ledger = json.load(open(LEDGER_FILE, encoding="utf-8"))
    except Exception:
        ledger = []
done_ids = {l["action_id"] for l in ledger if l.get("retrieval_status") == "OK"}
# MEC-2.2 patch: only OK actions count as done — Failed entries (477 rate-limit)
# are re-attempted on resume. Idempotent: OK outputs are never re-queried.

fail_streak = 0
SKIP_IDS = set(x for x in os.environ.get("SKIP_IDS", "").split(",") if x)
for i, act in enumerate(A):
    aid = "RB-%03d" % (i + 1)
    if aid in done_ids or aid in SKIP_IDS:
        continue
    out_file = os.path.join(AD, aid + ".json")
    # salvage: output exists from a killed prior run but ledger missing -> reconstruct entry
    if os.path.exists(out_file) and os.path.getsize(out_file) > 30:
        try:
            d = json.load(open(out_file, encoding="utf-8"))
            n = len(d) if isinstance(d, list) else len(d.get("results", []))
            ledger.append({"action_id": aid, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "batch": 2, "objective": "Batch2 P2 price discovery",
                "family": act["family"], "discovery_family": act["discovery_family"],
                "method": "web_search (z-ai CLI)", "query": act["query"],
                "targets": act["skus"], "retrieval_status": "OK",
                "results_count": n, "duration_s": 0.0,
                "yield": "pending-classification", "budget_debit": 1,
                "note": "salvaged from killed prior run (output file existed)"})
            print("%s SALVAGED n=%d | %s" % (aid, n, act["query"][:58]))
            continue
        except Exception:
            pass  # corrupt file -> re-query
    if time.time() - T_START > MAX_SECONDS:
        print("TIME_BUDGET_REACHED: stopping cleanly at %s" % aid)
        break
    attempt, ok, status, note = 0, True, "OK", ""
    while attempt < 2:
        attempt += 1
        t0 = time.time()
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
            else:
                ok, status, note = True, "OK", ""
                break
        except subprocess.TimeoutExpired:
            ok, status, note = False, "TIMEOUT", "75s"
        except Exception as e:
            ok, status, note = False, "ERROR", str(e)[:200]
        if attempt == 1 and not ok:
            print("  retry after cooldown: %s (%s)" % (aid, status))
            time.sleep(15)
    dur = round(time.time() - t0, 1)
    n_res = 0
    if ok:
        try:
            data = json.load(open(out_file, encoding="utf-8"))
            n_res = len(data) if isinstance(data, list) else len(data.get("results", []))
        except Exception:
            n_res = 0
    fail_streak = 0 if ok else fail_streak + 1
    entry = {
        "action_id": aid, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "batch": 2, "objective": "Batch2 P2 price discovery",
        "family": act["family"], "discovery_family": act["discovery_family"],
        "method": "web_search (z-ai CLI)", "query": act["query"],
        "targets": act["skus"], "retrieval_status": status if ok else "Failed",
        "results_count": n_res, "duration_s": dur,
        "yield": "pending-classification", "budget_debit": 1,
        "note": note + ("; retry-ok" if (attempt > 1 and ok) else ""),
    }
    ledger = [l for l in ledger if not (l.get("action_id") == aid and l.get("retrieval_status") != "OK")]  # MEC-2.2: drop superseded Failed entry
    ledger.append(entry)
    print("%s %s n=%d %.1fs | %s" % (aid, status, n_res, dur, act["query"][:58]))
    if fail_streak >= 3:
        print("ABORT: 3 consecutive failures — rate limit. State saved, resume with re-run.")
        break
    time.sleep(5)
    if time.time() - T_START > MAX_SECONDS:
        print("TIME_BUDGET_REACHED: stopping cleanly after %s" % aid)
        break
    if (i + 1) % 8 == 0:
        json.dump(ledger, open(LEDGER_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# MEC-2.2: dedupe safeguard (keep last entry per action_id, prefer OK)
seen = {}
for l in ledger:
    aid_ = l.get("action_id")
    if aid_ not in seen or (l.get("retrieval_status") == "OK"):
        seen[aid_] = l
ledger = list(seen.values())
json.dump(ledger, open(LEDGER_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
RUN["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
RUN["budget_used"] = len([l for l in ledger if l.get("batch") == 2 and l["budget_debit"]])
json.dump(RUN, open(os.path.join(RD, "run_contract_b2.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
b2 = [l for l in ledger if l.get("batch") == 2]
ok_n = len([l for l in b2 if l["retrieval_status"] == "OK"])
print("BATCH2_SEARCH_DONE: actions=%d ok=%d failed=%d budget=%d/118" % (len(b2), ok_n, len(b2)-ok_n, RUN["budget_used"]))
