#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.1 | Batch 2 merge — final records into offers_intelligence.json + catalog coverage ledger.
Applies curated layer (single source) over catalog identities; honest states preserved.
"""
import json, sys, importlib.util

BASE = "/home/z/my-project"
spec = importlib.util.spec_from_file_location("cur", BASE + "/scripts/batch2_curation.py")
cur = importlib.util.module_from_spec(spec); spec.loader.exec_module(cur)
CURATED = cur.CURATED

FX = {"USD": 1.0, "EUR": 1.137, "GBP": 1.3548, "RUB": 0.0126, "TRY": 0.0293,
      "AED": 0.2723, "SAR": 0.2666, "INR": 0.0115, "EGP": 0.0206, "ARS": 0.00104}
def usd(a, c): return round(a * FX.get(c, 1.0), 2)

cat = json.load(open(BASE + "/download/catalog_v42.json", encoding="utf-8"))
offers = json.load(open(BASE + "/download/offers_intelligence.json", encoding="utf-8"))

p2 = [s for s in cat["skus"] if s.get("priority") == "P2"]
missing_cur = [s["sku_id"] for s in p2 if s["sku_id"] not in CURATED]
if missing_cur:
    print("MISSING CURATION for:", missing_cur); sys.exit(1)

new_records, price_intel = {}, {}
counts = {"offers": 0, "official": 0, "lead_only": 0, "rate_limited": 0}
for s in p2:
    sid = s["sku_id"]
    c = CURATED[sid]
    rec = {
        "identity": " | ".join([x for x in [s.get("product"), s.get("plan_edition"),
             s.get("duration_denomination"), s.get("region"), s.get("activation_type")] if x]),
        "batch": 2,
        "evidence_note": "Batch-2 snippet-evidence run (27/09) — direct page verification deferred (remote-function quota exhausted mid-run, §19)",
    }
    if c.get("official") and c["official"].get("price") is not None:
        o = dict(c["official"]); o["usd"] = usd(o["price"], o.get("cur", "USD"))
        rec["official"] = o
        counts["official"] += 1
    elif c.get("official"):
        rec["official_absent_reason"] = c["official"].get("note", "")
    if c.get("offers"):
        rec["offers"] = []
        for of in c["offers"]:
            of = dict(of); of["usd"] = usd(of["price"], of.get("cur", "USD"))
            of.setdefault("freshness", "Unknown (snippet)")
            rec["offers"].append(of)
        valid = [o for o in rec["offers"] if not o.get("identity_flag")]
        best = min(valid, key=lambda x: x["usd"]) if valid else None
        if best:
            price_intel[sid] = {"identity": rec["identity"],
                "cheapest_advertised_batch2": best, "state": "Advertised (snippet) — below Directly-Observed tier"}
        counts["offers"] += 1
    if c.get("rate_limited"):
        rec["ledger_state"] = "Rate-Limited (query deferred — §19 recovery pending)"
        counts["rate_limited"] += 1
    elif not c.get("offers"):
        rec["ledger_state"] = "Searched (snippet) — Lead-only/no valid offer this run"
        counts["lead_only"] += 1
    else:
        rec["ledger_state"] = "Searched (snippet) — advertised candidates documented"
    if c.get("state_note"):
        rec["state_note"] = c["state_note"]
    new_records[sid] = rec

# merge into offers_intelligence
offers["skus"].update(new_records)
offers["batch2_run"] = {
    "run_id": "MEC2-20260927-B2",
    "date": "2026-09-27",
    "scope": "173 P2 SKUs",
    "actions": {"planned": 130, "executed_ok": 115, "failed_rate_limit": 15, "state": "15 queries deferred to retry (§19)"},
    "evidence_level": "Advertised (snippet) for all batch-2 offers — direct page reads deferred",
    "fx_basis": "batch-1 Wise 25/09 for EUR/GBP/RUB/TRY/AED/SAR; INR/EGP/ARS approx 27/09 (lower confidence)",
    "coverage": counts,
    "cheapest_advertised_index": price_intel,
}
json.dump(offers, open(BASE + "/download/offers_intelligence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# update catalog coverage ledger
ledger = cat.get("coverage_ledger", {})
p2_states = {}
for s in p2:
    sid = s["sku_id"]
    r = new_records[sid]
    st = "Rate-Limited" if "Rate-Limited" in r.get("ledger_state", "") else ("Searched-Snippet-Offer" if r.get("offers") else ("Searched-Snippet-LeadOnly" if r.get("official") is None or True else ""))
    p2_states[st] = p2_states.get(st, 0) + 1
    s["ledger_state"] = r.get("ledger_state", "Searched")
    s["batch"] = 2
ledger["batch2"] = {"executed": "2026-09-27", "states": p2_states,
    "note": "Batch 2 executed at snippet-evidence level; direct verification deferred (quota)"}
cat["coverage_ledger"] = ledger
json.dump(cat, open(BASE + "/download/catalog_v42.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("MERGE DONE: %d batch-2 records | with-offers=%d | with-official=%d | lead-only=%d | rate-limited=%d"
      % (len(new_records), counts["offers"], counts["official"], counts["lead_only"], counts["rate_limited"]))
print("Total SKU records in offers_intelligence:", len(offers["skus"]))
print("Catalog P2 states:", p2_states)
