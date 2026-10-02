#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-3.0 | Next.js batch-3 tab data + component wiring."""
import json, os

BASE = "/home/z/my-project"
oi = json.load(open(f"{BASE}/download/offers_intelligence.json", encoding="utf-8"))
b3 = oi["batch3_run"]

ch = [{"sku": sid, "seller": v["offer"]["seller"], "product": v["offer"]["product"],
       "usd": v["offer"]["usd"], "note": v["note"]} for sid, v in b3["curation"]["channel_accepted"].items()]
of = [{"sku": sid, "seller": v["baseline"]["seller"], "usd": v["baseline"]["usd"],
       "note": v["baseline"]["note"]} for sid, v in b3["curation"]["official_accepted"].items()]

out = {
    "run": "الدفعة 3 (218 P3) — الإغلاق النهائي",
    "date": "2026-09-27",
    "promotion": "v4.2 → Approved — أول نسخة معتمدة في تاريخ المشروع (قاعدة D1، تصريح المستخدم «اعتمد كل شي»)",
    "totals": {"catalog": "437/437 SKU", "actions": 415, "direct_offers": 42, "channels": 91},
    "states": b3["states_summary"],
    "key_findings": b3["key_findings"],
    "channel_offers": ch,
    "official_baselines": of,
    "price_corrections": b3["curation"]["price_corrections"],
    "limitations": b3["limitations"],
}
with open(f"{BASE}/src/lib/data/batch3-data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("batch3-data.json:", len(ch), "channel offers,", len(of), "official baselines")
