#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-2.1 | Generate Next.js batch-2 data + wire components."""
import json

BASE = "/home/z/my-project"
offers = json.load(open(BASE + "/download/offers_intelligence.json", encoding="utf-8"))
cat = json.load(open(BASE + "/download/catalog_v42.json", encoding="utf-8"))
cat_by_id = {s["sku_id"]: s for s in cat["skus"]}

rows = []
for sid, rec in offers["skus"].items():
    if rec.get("batch") != 2:
        continue
    c = cat_by_id.get(sid, {})
    valid = [o for o in rec.get("offers", []) if not o.get("identity_flag")]
    best = min(valid, key=lambda x: x["usd"]) if valid else None
    official = rec.get("official")
    rl = "Rate-Limited" in rec.get("ledger_state", "")
    rows.append({
        "sku_id": sid.replace("SKU-", "SKU-"),
        "family": rec.get("family", ""),
        "identity": {
            "brand": c.get("brand", ""),
            "product": c.get("product", ""),
            "plan": c.get("plan_edition", ""),
            "denomination": c.get("duration_denomination", ""),
            "region": c.get("region", ""),
        },
        "ledger_state": rec.get("ledger_state", ""),
        "state_class": "B2-Offer" if best else ("B2-RateLimited" if rl else ("B2-OfficialOnly" if official else "B2-LeadOnly")),
        "official_anchor": ({
            "price": official["price"], "currency": official.get("cur", "USD"),
            "evidence": official.get("note", ""), "evidence_level": "Advertised (official-page snippet)"
        } if official and official.get("price") is not None else None),
        "best_advertised": ({
            "entity": best.get("seller", ""), "price": best["price"], "currency": best.get("cur", "USD"),
            "usd": best["usd"], "note": best.get("note", ""), "evidence_level": "Advertised (snippet)"
        } if best else None),
        "all_offers_count": len(rec.get("offers", [])),
        "state_note": rec.get("state_note", "") or "",
    })

out = {
    "run_id": "MEC2-20260927-B2",
    "evidence_level": "Advertised (snippet) — direct page reads deferred (remote-function quota exhausted mid-run, §19)",
    "coverage_note": "115/121 queries OK; 15 deferred (18 SKUs Rate-Limited); auto-extraction noise manually rejected",
    "batch2_skus": rows,
}
json.dump(out, open(BASE + "/src/lib/data/batch2-skus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("batch2-skus.json:", len(rows), "rows")
