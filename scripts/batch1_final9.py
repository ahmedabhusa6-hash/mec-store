#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-1.0 | Final 9 budget actions — highest-materiality gaps (service recovered)."""
import json, os, subprocess, time

RD = "/home/z/my-project/research"
AD = RD + "/actions"
LF = RD + "/action_ledger.json"
ledger = json.load(open(LF, encoding="utf-8"))

REC = [
    (["SKU-GT001","SKU-GT004","SKU-GT008"],"Game Top-up","Price-first","cheapest free fire diamonds pubg uc mobile legends top up store"),
    (["SKU-GT011","SKU-GT014","SKU-GT016"],"Game Top-up","Price-first","valorant vp fortnite v-bucks robux price buy"),
    (["SKU-ES001","SKU-ES003","SKU-ES005"],"eSIM","Price-first","esim data package usa uae saudi price cheapest"),
    (["SKU-VN001","SKU-VN003","SKU-VN004"],"Virtual Numbers","Price-first","buy telegram virtual number sms activation cheapest price"),
    (["SKU-AP001","SKU-AP004"],"API Services","Product-first","openai api credits reloadly api pricing"),
    (["SKU-GC037","SKU-GC049"],"Gift Cards","B2B/Catalog-oriented","gift cards wholesale distributor bulk supplier B2B"),
    (["SKU-DS037","SKU-DS039"],"Digital Subscriptions","Bot-first","telegram premium cheap reseller gift price"),
    (["SKU-GC037","SKU-GC062"],"Gift Cards","Bot-first","telegram store sell gift cards digital products channel"),
    (["SKU-GC037"],"Gift Cards","Referral-first","turgame wholesale program reseller API"),
]
for targets, fam, dfam, q in REC:
    if len(ledger) >= 120: print("BUDGET_CAP_120"); break
    aid = "RA-%03d" % (len(ledger) + 1)
    out_file = os.path.join(AD, aid + ".json")
    ok, status, note = True, "OK", ""
    t0 = time.time()
    try:
        r = subprocess.run(["z-ai","function","-n","web_search",
            "-a", json.dumps({"query": q, "num": 6}, ensure_ascii=False), "-o", out_file],
            capture_output=True, text=True, timeout=75)
        if r.returncode != 0: ok, status, note = False, "FAILED", (r.stderr or r.stdout)[:150]
        elif not os.path.exists(out_file) or os.path.getsize(out_file) < 30: ok, status, note = False, "EMPTY", ""
    except Exception as e:
        ok, status, note = False, "ERROR", str(e)[:150]
    dur = round(time.time()-t0,1); n = 0
    if ok:
        try:
            d = json.load(open(out_file, encoding="utf-8")); n = len(d) if isinstance(d, list) else len(d.get("results",[]))
        except Exception: n = 0
    ledger.append({"action_id": aid, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "batch": 1, "objective": "Batch1 final gaps", "family": fam,
        "discovery_family": dfam, "method": "web_search (z-ai CLI)", "query": q,
        "targets": targets, "retrieval_status": status if ok else "Failed",
        "results_count": n, "duration_s": dur, "yield": "pending-classification",
        "budget_debit": 1, "budget_source": "reserve", "note": note})
    print("%s %s n=%d %.1fs | %s" % (aid, status, n, dur, q[:55]))
    json.dump(ledger, open(LF, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(7.0)
ok_n = len([l for l in ledger if l["retrieval_status"]=="OK"])
print("FINAL_DONE: total=%d ok=%d failed=%d budget=%d/120" % (len(ledger), ok_n, len(ledger)-ok_n, len(ledger)))
