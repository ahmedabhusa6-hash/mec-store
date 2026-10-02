#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.3 | Batch 3 Research Execution (final P-batch, v4.2 architecture)
Run Contract: MEC2-20260927-B3 | Scope: 218 P3 SKUs (catalog CP-1)
Complexity: C4 | Budget: 138 search actions + 25% reserve | Channels = Notion-specified only (Amendment A)
Rate-limit protocol: 5s pacing + 15s cooldown + 1 retry + 3-fail abort (MEC-2.1/2.2 lessons).
Idempotent resume: only OK actions are skipped; Failed (477) auto-retried; salvage for killed runs.
Every action logged per v4.1 §0.1. Action IDs: RC-xxx.
"""
import json, os, subprocess, time

BASE = "/home/z/my-project"
RD = os.path.join(BASE, "research")
AD = os.path.join(RD, "actions")
os.makedirs(AD, exist_ok=True)

RUN = {
    "run_id": "MEC2-20260927-B3",
    "prompt_version": "v4.2 Candidate (working)",
    "start_time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "batch": 3,
    "scope": "218 P3 SKUs (catalog CP-1, download/catalog_v42.json)",
    "complexity": "C4",
    "budget_total": 138,
    "budget_reserve": 35,
    "budget_used": 0,
    "channels_policy": "Notion-specified references/channels only (Amendment A)",
    "pacing": "5s between queries, 15s cooldown on failure, 1 retry, 3-fail abort",
}
with open(os.path.join(RD, "run_contract_b3.json"), "w", encoding="utf-8") as f:
    json.dump(RUN, f, ensure_ascii=False, indent=1)

# ─── Action definitions: (skus, family, discovery_family, query) ───
A = []
def a(skus, fam, dfam, q):
    A.append({"skus": skus, "family": fam, "discovery_family": dfam, "query": q})

# ═══ AI/SaaS (38 P3) ═══
a(["SKU-AI009"],"AI/SaaS","Product-first","google gemini ultra ai ultra subscription price monthly")
a(["SKU-AI015"],"AI/SaaS","Product-first","poe com subscription price monthly")
a(["SKU-AI016","SKU-AI038"],"AI/SaaS","Product-first","suno pro premier subscription price monthly")
a(["SKU-AI017","SKU-AI039"],"AI/SaaS","Product-first","elevenlabs creator pro plan price monthly")
a(["SKU-AI018","SKU-AI040"],"AI/SaaS","Product-first","runway standard pro plan price monthly")
a(["SKU-AI019","SKU-AI041"],"AI/SaaS","Product-first","ideogram basic plus plan price monthly")
a(["SKU-AI020","SKU-AI042"],"AI/SaaS","Product-first","leonardo ai apprentice artisan plan price")
a(["SKU-AI021","SKU-AI043"],"AI/SaaS","Product-first","krea basic pro plan price monthly")
a(["SKU-AI022"],"AI/SaaS","Product-first","recraft basic subscription price")
a(["SKU-AI023"],"AI/SaaS","Product-first","character ai c.ai plus subscription price")
a(["SKU-AI024","SKU-AI044"],"AI/SaaS","Product-first","gamma app pro max plan price")
a(["SKU-AI025"],"AI/SaaS","Product-first","mistral le chat pro price monthly")
a(["SKU-AI026","SKU-AI045"],"AI/SaaS","Product-first","jasper ai creator business price monthly")
a(["SKU-AI027","SKU-AI055"],"AI/SaaS","Product-first","sider pro team plan price")
a(["SKU-AI028"],"AI/SaaS","Product-first","manus ai subscription price basic plan")
a(["SKU-AI030"],"AI/SaaS","Product-first","adobe firefly standard plan price monthly")
a(["SKU-AI031"],"AI/SaaS","Product-first","notion ai add-on price monthly")
a(["SKU-AI034"],"AI/SaaS","Product-first","claude pro annual plan 12 months price")
a(["SKU-AI035"],"AI/SaaS","Product-first","perplexity pro annual 12 months price")
a(["SKU-AI036","SKU-AI037"],"AI/SaaS","Product-first","midjourney pro mega plan price monthly")
a(["SKU-AI047"],"AI/SaaS","Product-first","cursor pro plan price monthly")
a(["SKU-AI048","SKU-AI049"],"AI/SaaS","Product-first","grammarly premium quillbot premium price monthly")
a(["SKU-AI050","SKU-AI051"],"AI/SaaS","Product-first","freepik premium envato elements subscription price")
a(["SKU-AI052","SKU-AI053"],"AI/SaaS","Product-first","shutterstock standard subscription kittl pro price")
a(["SKU-AI054"],"AI/SaaS","Product-first","framer pro plan price monthly")

# ═══ Gift Cards (43 P3) ═══
a(["SKU-GC005"],"Gift Cards","Marketplace-first","eneba steam gift card 100 EUR price")
a(["SKU-GC006"],"Gift Cards","Price-first","steam wallet gift card 20 USD argentina price")
a(["SKU-GC012"],"Gift Cards","Price-first","playstation network card 50 USD turkey price")
a(["SKU-GC013","SKU-GC014","SKU-GC015"],"Gift Cards","Marketplace-first","cdkeys xbox gift card 5 15 25 EUR price")
a(["SKU-GC016"],"Gift Cards","Price-first","xbox gift card 50 TL turkey price")
a(["SKU-GC017","SKU-GC018"],"Gift Cards","Marketplace-first","eneba google play gift card 10 25 EUR price")
a(["SKU-GC019"],"Gift Cards","Price-first","google play gift card 50 SAR saudi arabia price")
a(["SKU-GC020"],"Gift Cards","Price-first","apple itunes gift card 25 EUR price")
a(["SKU-GC021"],"Gift Cards","Price-first","apple itunes gift card 50 SAR saudi price")
a(["SKU-GC023"],"Gift Cards","Price-first","amazon gift card 25 EUR digital price")
a(["SKU-GC024"],"Gift Cards","Price-first","amazon gift card 50 TRY turkey price")
a(["SKU-GC025"],"Gift Cards","Price-first","nintendo eshop card 35 EUR price")
a(["SKU-GC026"],"Gift Cards","Price-first","razer gold gift card 5 EUR price")
a(["SKU-GC027"],"Gift Cards","Price-first","netflix gift card 25 USD price buy")
a(["SKU-GC028"],"Gift Cards","Price-first","spotify gift card 60 EUR price")
a(["SKU-GC029","SKU-GC030"],"Gift Cards","Marketplace-first","eneba roblox gift card 100 USD 10 EUR price")
a(["SKU-GC033"],"Gift Cards","Price-first","binance gift card crypto voucher buy price")
a(["SKU-GC034"],"Gift Cards","Price-first","prepaid virtual visa mastercard gift card price")
a(["SKU-GC042","SKU-GC044","SKU-GC046"],"Gift Cards","Price-first","steam wallet gift card 10 20 50 USD turkey price")
a(["SKU-GC054","SKU-GC055","SKU-GC056"],"Gift Cards","Price-first","psn playstation card 10 25 50 GBP UK price")
a(["SKU-GC071","SKU-GC073","SKU-GC075","SKU-GC077"],"Gift Cards","Price-first","google play gift card saudi arabia 10 25 50 100 USD price")
a(["SKU-GC079","SKU-GC081","SKU-GC083","SKU-GC085"],"Gift Cards","Price-first","amazon gift card saudi arabia 10 25 50 100 USD price")
a(["SKU-GC086","SKU-GC087","SKU-GC088","SKU-GC089"],"Gift Cards","Price-first","nintendo eshop card 10 20 35 50 USD price")
a(["SKU-GC102","SKU-GC103","SKU-GC104"],"Gift Cards","Price-first","steam gift card 100 250 500 TRY turkey price")

# ═══ Game Top-up (32 P3) ═══
a(["SKU-GT013"],"Game Top-up","Price-first","league of legends 1380 rp price eu west")
a(["SKU-GT048","SKU-GT049"],"Game Top-up","Price-first","league of legends 2800 5000 rp price")
a(["SKU-GT021"],"Game Top-up","Price-first","honkai star rail 300 oneiric shards price")
a(["SKU-GT022","SKU-GT042"],"Game Top-up","Price-first","ea sports fc points 1050 2200 price")
a(["SKU-GT023","SKU-GT043"],"Game Top-up","Price-first","call of duty 1000 2000 cp points price")
a(["SKU-GT024","SKU-GT044","SKU-GT045"],"Game Top-up","Price-first","clash of clans 500 1200 2500 gems price")
a(["SKU-GT025","SKU-GT046","SKU-GT047"],"Game Top-up","Price-first","brawl stars 170 950 2000 gems price")
a(["SKU-GT026"],"Game Top-up","Price-first","honkai impact 3rd 300 crystals price")
a(["SKU-GT027","SKU-GT028"],"Game Top-up","Price-first","free fire 2200 5600 diamonds top up price")
a(["SKU-GT029","SKU-GT030"],"Game Top-up","Price-first","pubg mobile 3850 8100 uc price")
a(["SKU-GT031","SKU-GT032"],"Game Top-up","Price-first","mobile legends 706 1050 diamonds price")
a(["SKU-GT033","SKU-GT034"],"Game Top-up","Price-first","valorant 3650 5350 points price")
a(["SKU-GT036"],"Game Top-up","Price-first","fortnite 13500 v-bucks price")
a(["SKU-GT037","SKU-GT038"],"Game Top-up","Price-first","roblox 4500 10000 robux price")
a(["SKU-GT040","SKU-GT041"],"Game Top-up","Price-first","genshin impact 3880 8080 genesis crystals price")
a(["SKU-GT050"],"Game Top-up","Price-first","dota 2 steam wallet top up price")
a(["SKU-GT051"],"Game Top-up","Price-first","free fire weekly membership booyah pass price")
a(["SKU-GT052"],"Game Top-up","Price-first","pubg mobile royale pass price")
a(["SKU-GT053"],"Game Top-up","Price-first","valorant console 1000 vp price")

# ═══ Game Keys (7 P3) ═══
a(["SKU-GK011"],"Game Keys","Price-first","witcher 3 wild hunt cd key cheapest price")
a(["SKU-GK012"],"Game Keys","Price-first","ark survival ascended cd key price")
a(["SKU-GK013"],"Game Keys","Price-first","rust cd key cheapest price")
a(["SKU-GK015"],"Game Keys","Price-first","pubg battlegrounds cd key price")
a(["SKU-GK016"],"Game Keys","Price-first","civilization 7 cd key price")
a(["SKU-GK020"],"Game Keys","Price-first","kingdom come deliverance 2 cd key price")
a(["SKU-GK027"],"Game Keys","Product-first","nintendo switch online 12 months price")

# ═══ Software/Licenses (10 P3) ═══
a(["SKU-SW010"],"Software/Licenses","Product-first","visual studio professional license price")
a(["SKU-SW012"],"Software/Licenses","Product-first","adobe photoshop single app 1 month price")
a(["SKU-SW013"],"Software/Licenses","Product-first","adobe creative cloud all apps 1 month price")
a(["SKU-SW014"],"Software/Licenses","Price-first","adobe photoshop lifetime key cheap price")
a(["SKU-SW015","SKU-SW016","SKU-SW017","SKU-SW018"],"Software/Licenses","Price-first","adobe illustrator premiere pro after effects lightroom lifetime key price")
a(["SKU-SW019"],"Software/Licenses","Product-first","jetbrains all products pack price")
a(["SKU-SW020"],"Software/Licenses","Product-first","unity pro subscription price monthly")

# ═══ eSIM (15 P3) ═══
a(["SKU-ES008"],"eSIM","Product-first","esim egypt 10gb 30 days price")
a(["SKU-ES009"],"eSIM","Product-first","esim turkey 10gb 30 days price")
a(["SKU-ES011"],"eSIM","Price-first","esim europe 20gb 30 days price")
a(["SKU-ES014"],"eSIM","Product-first","esim japan 10gb 30 days price")
a(["SKU-ES015"],"eSIM","Product-first","esim south korea 10gb price")
a(["SKU-ES016","SKU-ES017"],"eSIM","Product-first","esim thailand malaysia 10gb price")
a(["SKU-ES018","SKU-ES019","SKU-ES020"],"eSIM","Product-first","esim qatar kuwait oman 5gb price")
a(["SKU-ES021","SKU-ES022","SKU-ES023"],"eSIM","Product-first","esim jordan morocco bahrain 5gb price")
a(["SKU-ES024"],"eSIM","Product-first","esim yemen 3gb price")
a(["SKU-ES025"],"eSIM","Product-first","esim iraq 5gb price")

# ═══ SMM Services (23 P3) ═══
a(["SKU-SM002","SKU-SM003"],"SMM Services","Price-first","smm panel instagram 5000 followers 1000 likes price")
a(["SKU-SM005","SKU-SM015"],"SMM Services","Price-first","smm panel tiktok 10000 views 1000 likes price")
a(["SKU-SM007","SKU-SM017"],"SMM Services","Price-first","smm panel youtube 10000 views shorts price")
a(["SKU-SM008","SKU-SM027"],"SMM Services","Price-first","smm panel twitter x followers 1000 retweets price")
a(["SKU-SM010","SKU-SM018","SKU-SM019"],"SMM Services","Price-first","smm panel telegram views reactions premium members price")
a(["SKU-SM011","SKU-SM025"],"SMM Services","Price-first","smm panel facebook page likes followers 1000 price")
a(["SKU-SM012"],"SMM Services","Price-first","smm panel threads followers 1000 price")
a(["SKU-SM013","SKU-SM014"],"SMM Services","Price-first","smm panel instagram views story views 1000 price")
a(["SKU-SM016"],"SMM Services","Price-first","youtube 4000 watch hours monetization smm panel price")
a(["SKU-SM020","SKU-SM021"],"SMM Services","Price-first","smm panel discord members twitch followers 1000 price")
a(["SKU-SM022"],"SMM Services","Price-first","twitch live viewers 100 smm panel price")
a(["SKU-SM023","SKU-SM024"],"SMM Services","Price-first","smm panel spotify plays soundcloud plays 1000 price")
a(["SKU-SM026"],"SMM Services","Price-first","smm panel linkedin followers 1000 price")

# ═══ Virtual Numbers (7 P3) ═══
a(["SKU-VN018"],"Virtual Numbers","Product-first","virtual number 30 day rental russia price")
a(["SKU-VN019"],"Virtual Numbers","Product-first","virtual number long term rental indonesia price")
a(["SKU-VN032"],"Virtual Numbers","Product-first","telegram virtual number turkey price")
a(["SKU-VN033"],"Virtual Numbers","Product-first","telegram virtual number uae price")
a(["SKU-VN034"],"Virtual Numbers","Product-first","virtual number 30 day rental usa price")
a(["SKU-VN035"],"Virtual Numbers","Product-first","virtual number rental kazakhstan price")
a(["SKU-VN036"],"Virtual Numbers","Product-first","toll free virtual number usa monthly price")

# ═══ Digital Subscriptions (38 P3) ═══
a(["SKU-DS018","SKU-DS019","SKU-DS020"],"Digital Subscriptions","Product-first","paramount plus peacock crunchyroll subscription price monthly")
a(["SKU-DS021"],"Digital Subscriptions","Product-first","audible premium plus price monthly")
a(["SKU-DS023"],"Digital Subscriptions","Product-first","apple tv plus price monthly")
a(["SKU-DS024"],"Digital Subscriptions","Product-first","deezer premium price monthly")
a(["SKU-DS027","SKU-DS028"],"Digital Subscriptions","Product-first","dropbox plus mega pro 12 months price")
a(["SKU-DS032","SKU-DS034"],"Digital Subscriptions","Product-first","slack pro zoom pro price monthly")
a(["SKU-DS033","SKU-DS065"],"Digital Subscriptions","Product-first","notion plus price monthly annual")
a(["SKU-DS035","SKU-DS036"],"Digital Subscriptions","Product-first","trello premium jira standard price monthly")
a(["SKU-DS044"],"Digital Subscriptions","Product-first","discord nitro basic 1 month price")
a(["SKU-DS045","SKU-DS046"],"Digital Subscriptions","Product-first","twitch turbo gifted sub price")
a(["SKU-DS047"],"Digital Subscriptions","Product-first","spotify premium duo price monthly")
a(["SKU-DS051","SKU-DS052"],"Digital Subscriptions","Product-first","iqiyi vip youku vip price monthly")
a(["SKU-DS053"],"Digital Subscriptions","Product-first","vimeo plus price monthly")
a(["SKU-DS054"],"Digital Subscriptions","Product-first","soundcloud go plus price monthly")
a(["SKU-DS055"],"Digital Subscriptions","Product-first","linkedin premium career price monthly")
a(["SKU-DS056"],"Digital Subscriptions","Product-first","medium membership price monthly")
a(["SKU-DS057"],"Digital Subscriptions","Product-first","patreon membership tier price")
a(["SKU-DS058"],"Digital Subscriptions","Product-first","coursera plus annual price")
a(["SKU-DS059"],"Digital Subscriptions","Product-first","skillshare premium annual price")
a(["SKU-DS060"],"Digital Subscriptions","Product-first","duolingo super price monthly")
a(["SKU-DS064"],"Digital Subscriptions","Product-first","figma professional annual price")
a(["SKU-DS066","SKU-DS067","SKU-DS068"],"Digital Subscriptions","Product-first","monday.com clickup unlimited asana starter price")
a(["SKU-DS069"],"Digital Subscriptions","Product-first","miro starter price monthly")
a(["SKU-DS070","SKU-DS071"],"Digital Subscriptions","Product-first","google one 2tb icloud 2tb price monthly")
a(["SKU-DS072"],"Digital Subscriptions","Product-first","google workspace individual price monthly")
a(["SKU-DS073","SKU-DS074"],"Digital Subscriptions","Product-first","microsoft 365 business basic standard price")

# ═══ API Services (5 P3) ═══
a(["SKU-AP011"],"API Services","Seller-first","blackhawk network gift card api distributor pricing")
a(["SKU-AP012"],"API Services","Seller-first","incomm payments gift card api reseller")
a(["SKU-AP013"],"API Services","Seller-first","plati market digital goods api reseller")
a(["SKU-AP014"],"API Services","Seller-first","z2u seller api panel program")
a(["SKU-AP015"],"API Services","Seller-first","ggsel seller api panel program")

print("ACTIONS_PLANNED:", len(A))
MAX_SECONDS = int(os.environ.get("MAX_SECONDS", "999999"))
T_START = time.time()
# coverage check
covered = set()
for act in A:
    covered.update(act["skus"])
with open(os.path.join(BASE, "download/catalog_v42.json"), encoding="utf-8") as f:
    cat = json.load(f)
p3 = [s["sku_id"] for s in cat["skus"] if s.get("priority") == "P3"]
missing = [s for s in p3 if s not in covered]
print("P3 total:", len(p3), "| covered by queries:", len([s for s in p3 if s in covered]), "| missing:", missing)

ledger = []
LEDGER_FILE = os.path.join(RD, "action_ledger.json")
if os.path.exists(LEDGER_FILE):
    try:
        ledger = json.load(open(LEDGER_FILE, encoding="utf-8"))
    except Exception:
        ledger = []
done_ids = {l["action_id"] for l in ledger if l.get("retrieval_status") == "OK"}
# only OK actions count as done — Failed entries (477 rate-limit) are re-attempted on resume.

fail_streak = 0
SKIP_IDS = set(x for x in os.environ.get("SKIP_IDS", "").split(",") if x)
for i, act in enumerate(A):
    aid = "RC-%03d" % (i + 1)
    if aid in done_ids or aid in SKIP_IDS:
        continue
    out_file = os.path.join(AD, aid + ".json")
    # salvage: output exists from a killed prior run but ledger missing -> reconstruct entry
    if os.path.exists(out_file) and os.path.getsize(out_file) > 30:
        try:
            d = json.load(open(out_file, encoding="utf-8"))
            n = len(d) if isinstance(d, list) else len(d.get("results", []))
            ledger.append({"action_id": aid, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "batch": 3, "objective": "Batch3 P3 price discovery",
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
        "batch": 3, "objective": "Batch3 P3 price discovery",
        "family": act["family"], "discovery_family": act["discovery_family"],
        "method": "web_search (z-ai CLI)", "query": act["query"],
        "targets": act["skus"], "retrieval_status": status if ok else "Failed",
        "results_count": n_res, "duration_s": dur,
        "yield": "pending-classification", "budget_debit": 1,
        "note": note + ("; retry-ok" if (attempt > 1 and ok) else ""),
    }
    ledger = [l for l in ledger if not (l.get("action_id") == aid and l.get("retrieval_status") != "OK")]
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

# dedupe safeguard (keep last entry per action_id, prefer OK)
seen = {}
for l in ledger:
    aid_ = l.get("action_id")
    if aid_ not in seen or (l.get("retrieval_status") == "OK"):
        seen[aid_] = l
ledger = list(seen.values())
json.dump(ledger, open(LEDGER_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
RUN["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
RUN["budget_used"] = len([l for l in ledger if l.get("batch") == 3 and l["budget_debit"]])
json.dump(RUN, open(os.path.join(RD, "run_contract_b3.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
b3 = [l for l in ledger if l.get("batch") == 3]
ok_n = len([l for l in b3 if l["retrieval_status"] == "OK"])
print("BATCH3_SEARCH_DONE: actions=%d ok=%d failed=%d budget=%d/138" % (len(b3), ok_n, len(b3)-ok_n, RUN["budget_used"]))
