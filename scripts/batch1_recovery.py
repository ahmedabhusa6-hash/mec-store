#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phase 2 — Batch 1 RECOVERY actions (reserve budget)
Per v4.1 §19: failed retrieval -> switch method/consolidate; not bare repeats.
36 failed queries consolidated into 23 recovery actions from the 25% reserve.
"""
import json, os, subprocess, time

BASE = "/home/z/my-project"
RD = os.path.join(BASE, "research")
AD = os.path.join(RD, "actions")
LEDGER_FILE = os.path.join(RD, "action_ledger.json")
ledger = json.load(open(LEDGER_FILE, encoding="utf-8"))
run = json.load(open(os.path.join(RD, "run_contract.json"), encoding="utf-8"))
used = len(ledger)

REC = [
    # (targets, family, dfam, query)
    (["SKU-GT001","SKU-GT004","SKU-GT008"],"Game Top-up","Price-first","free fire pubg mobile mobile legends diamonds uc top up cheapest price"),
    (["SKU-GT011","SKU-GT014","SKU-GT016"],"Game Top-up","Price-first","valorant points fortnite v-bucks roblox robux cheapest price buy"),
    (["SKU-ES001","SKU-ES003","SKU-ES005"],"eSIM","Price-first","travel esim usa saudi arabia uae data package price comparison"),
    (["SKU-VN001","SKU-VN003","SKU-VN004"],"Virtual Numbers","Price-first","telegram virtual number russia kazakhstan indonesia sms activation price"),
    (["SKU-AP001"],"API Services","Product-first","openai api credits pricing buy prepaid"),
    (["SKU-AP004"],"API Services","Product-first","reloadly api pricing gift cards reseller"),
    (["SKU-GC037","SKU-GC049"],"Gift Cards","B2B/Catalog-oriented","gift card wholesale distributor B2B supplier"),
    (["SKU-GK021","SKU-GK022"],"Game Keys","B2B/Catalog-oriented","game keys wholesale supplier distributor reseller"),
    (["SKU-DS037","SKU-DS042"],"Digital Subscriptions","B2B/Catalog-oriented","digital subscriptions wholesale reseller panel"),
    (["SKU-AP004"],"API Services","Referral-first","reloadly ding dt one gift card api comparison"),
    (["SKU-GC037"],"Gift Cards","Referral-first","turgame wholesale reseller program"),
    (["SKU-GC037"],"Gift Cards","Referral-first","kinguin business B2B wholesale"),
    (["SKU-AI001","SKU-DS002"],"AI/SaaS","Channel-first","plati market chatgpt plus netflix price"),
    (["SKU-AI005","SKU-DS002"],"AI/SaaS","Channel-first","ggsel netflix chatgpt catalog price"),
    (["SKU-DS037","SKU-DS039"],"Digital Subscriptions","Bot-first","telegram premium reseller bot cheap"),
    (["SKU-GC037","SKU-GC062"],"Gift Cards","Bot-first","t.me digital store gift cards sell"),
    (["SKU-GC062"],"Gift Cards","Seller-first","megatec center mega center digital store"),
    (["SKU-GC062"],"Gift Cards","Seller-first","al momaiz card store digital"),
    (["SKU-GC062"],"Gift Cards","Seller-first","fazercards reseller platform"),
    (["SKU-GK021"],"Game Keys","Document-first","xbox game pass ultimate price official store"),
    (["SKU-DS006"],"Digital Subscriptions","Document-first","spotify premium plans official pricing"),
    (["SKU-DS002"],"Digital Subscriptions","Document-first","netflix plans official pricing current"),
    (["SKU-SW001"],"Software/Licenses","Document-first","microsoft windows 11 pro price official"),
]

for idx, (targets, fam, dfam, q) in enumerate(REC):
    if used >= 120:
        print("BUDGET_CAP_REACHED"); break
    aid = "RA-%03d" % (len(ledger) + 1)
    out_file = os.path.join(AD, aid + ".json")
    ok, status, note = True, "OK", ""
    t0 = time.time()
    try:
        r = subprocess.run(["z-ai","function","-n","web_search",
            "-a", json.dumps({"query": q, "num": 6}, ensure_ascii=False), "-o", out_file],
            capture_output=True, text=True, timeout=75)
        if r.returncode != 0: ok, status, note = False, "FAILED", (r.stderr or r.stdout)[:180]
        elif not os.path.exists(out_file) or os.path.getsize(out_file) < 30: ok, status, note = False, "EMPTY", "no file"
    except Exception as e:
        ok, status, note = False, "ERROR", str(e)[:180]
    dur = round(time.time()-t0, 1)
    n = 0
    if ok:
        try:
            d = json.load(open(out_file, encoding="utf-8"))
            n = len(d) if isinstance(d, list) else len(d.get("results", []))
        except Exception: n = 0
    ledger.append({
        "action_id": aid, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "batch": 1, "objective": "Batch1 recovery (consolidated queries)",
        "family": fam, "discovery_family": dfam, "method": "web_search (z-ai CLI)",
        "query": q, "targets": targets, "retrieval_status": status if ok else "Failed",
        "results_count": n, "duration_s": dur, "yield": "pending-classification",
        "budget_debit": 1, "budget_source": "reserve", "note": note,
    })
    print("%s %s n=%d %.1fs | %s" % (aid, status, n, dur, q[:55]))
    json.dump(ledger, open(LEDGER_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(4.0)  # slow pacing to respect rate limits

run["budget_used"] = len(ledger)
json.dump(run, open(os.path.join(RD, "run_contract.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ok_n = len([l for l in ledger if l["retrieval_status"]=="OK"])
print("RECOVERY_DONE: total=%d ok=%d failed=%d budget=%d/120" % (len(ledger), ok_n, len(ledger)-ok_n, len(ledger)))
