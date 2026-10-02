#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phase 2 — Direct verification reads (page_reader)
Budget amendment record (v4.1 §13, justified): cap 120 -> 140.
Reason: §4.1 Evidence Integrity — material P1 price claims require directly
retrieved source content over search snippets (cumulative program accounting
per v4.2 catalog architecture). Targets = Notion-specified channels (Amend. A)
+ documented URLs from the 2026-09-25 prior run.
"""
import json, os, subprocess, time

RD = "/home/z/my-project/research"
PG = RD + "/pages"
os.makedirs(PG, exist_ok=True)
LF = RD + "/action_ledger.json"
ledger = json.load(open(LF, encoding="utf-8"))

PAGES = [
    # (url, targets, note)
    ("https://www.eneba.com/steam-gift-card-20-usd-steam-key-united-states", ["SKU-GC037"], "prior-run documented URL pattern"),
    ("https://wholesale.turgame.com", ["SKU-GC037","SKU-GC049"], "Turgame WHOLESALE — upstream/role verification (dual value)"),
    ("https://www.turgame.com/steam-wallet-gift-card-20-usd", ["SKU-GC037"], "prior-run documented channel"),
    ("https://www.eneba.com/playstation-network-card-50-usd-psn-key-united-states", ["SKU-GC049"], "prior-run documented URL pattern"),
    ("https://reseller.fazercards.com/en", ["SKU-GC062"], "SUP-013 LEAD verification + Apple GC UAE channel"),
    ("https://openai.com/chatgpt/pricing/", ["SKU-AI001"], "official baseline"),
    ("https://ggsel.net/catalog/chatgpt-plus", ["SKU-AI005"], "cheapest documented lead 749 RUB (prior run)"),
    ("https://www.spotify.com/premium/", ["SKU-DS006"], "official baseline"),
    ("https://help.netflix.com/en/node/24926", ["SKU-DS002"], "official baseline documented 25/09"),
    ("https://www.youtube.com/premium", ["SKU-DS010"], "official baseline"),
    ("https://telegram.org/blog/telegram-premium", ["SKU-DS037"], "Telegram Premium official"),
    ("https://discord.com/nitro", ["SKU-DS042"], "official baseline"),
    ("https://www.cjs-cdkeys.com/", ["SKU-SW001"], "CJS documented 25/09: Win11 Pro 9.99 GBP"),
    ("https://www.keyforsteam.de/windows-11-pro-key-kaufen-preisvergleich/", ["SKU-SW001"], "prior-run documented (51 offers)"),
    ("https://www.keyforsteam.de/microsoft-office-2021-pro-plus-cd-key-kaufen-preisvergleich/", ["SKU-SW004"], "prior-run documented (77 offers)"),
    ("https://www.keyforsteam.de/", ["SKU-SW006"], "Office 2024 0.59 EUR lead documented 25/09"),
    ("https://www.xbox.com/en-US/xbox-game-pass/compare", ["SKU-GK021","SKU-GK022"], "official baseline 22.99 USD documented"),
    ("https://www.nordvpn.com/pricing/", ["SKU-DS025"], "official baseline documented 25/09"),
    ("https://www.reloadly.com/", ["SKU-AP004"], "API/Distributor role + pricing"),
    ("https://www.airalo.com/", ["SKU-ES003","SKU-ES005"], "eSIM channel candidate"),
]

for url, targets, note in PAGES:
    aid = "RA-%03d" % (len(ledger) + 1)
    out_file = os.path.join(PG, aid + ".json")
    ok, status, err = True, "OK", ""
    t0 = time.time()
    try:
        r = subprocess.run(["z-ai","function","-n","page_reader",
            "-a", json.dumps({"url": url}), "-o", out_file],
            capture_output=True, text=True, timeout=90)
        if r.returncode != 0: ok, status, err = False, "FAILED", (r.stderr or r.stdout)[:150]
        elif not os.path.exists(out_file) or os.path.getsize(out_file) < 30: ok, status, err = False, "EMPTY", ""
    except Exception as e:
        ok, status, err = False, "ERROR", str(e)[:150]
    dur = round(time.time()-t0, 1)
    size = os.path.getsize(out_file) if os.path.exists(out_file) else 0
    ledger.append({"action_id": aid, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "batch": 1, "objective": "Direct verification (evidence integrity §4.1)",
        "family": "verification", "discovery_family": "Document-first",
        "method": "page_reader (z-ai CLI)", "query": url, "targets": targets,
        "retrieval_status": status if ok else "Failed", "results_count": 1 if ok else 0,
        "duration_s": dur, "yield": "pending-classification", "budget_debit": 1,
        "budget_source": "verification-subbudget (+20, justified per §13/§4.1)",
        "note": note + (" | " + err if err else "")})
    print("%s %s %6dB %.1fs | %s" % (aid, status, size, dur, url[:70]))
    json.dump(ledger, open(LF, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(3.0)

ok_n = len([l for l in ledger if l["retrieval_status"]=="OK"])
print("VERIFY_DONE: total=%d ok=%d failed=%d" % (len(ledger), ok_n, len(ledger)-ok_n))
# update run contract with amendment
rc = json.load(open(RD + "/run_contract.json", encoding="utf-8"))
rc["budget_amendment"] = {"original_cap": 120, "new_cap": 140,
    "reason": "§4.1 evidence integrity: material P1 price claims require direct source retrieval; cumulative catalog accounting per v4.2",
    "amended_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
rc["budget_used"] = len(ledger)
json.dump(rc, open(RD + "/run_contract.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
