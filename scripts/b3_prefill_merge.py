#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.5c | Manual curation results (agent-reviewed) + merge into offers_intelligence.json.
Curation of 11 strict candidates from b3_prefill_strict.json:
  9 ACCEPTED (1 exact deferred-answer + 1 exact + 2 strong + 5 adjacent-identity)
  2 REJECTED with documented reasons (identity mismatch / region mismatch).
Updates: offers_intelligence.json (+b3_prefill_run) + catalog coverage ledger states.
"""
import json, os
from datetime import datetime

BASE = "/home/z/my-project"
OI = os.path.join(BASE, "download", "offers_intelligence.json")
CAT = os.path.join(BASE, "download", "catalog_v42.json")

oi = json.load(open(OI, encoding="utf-8"))
cat = json.load(open(CAT, encoding="utf-8"))

# ---------------- curation decisions (manual review, 27/09) ----------------
ACCEPTED = [
    {"sku_id": "SKU-DS043",
     "identity": "Discord Nitro | 12 months | Global | subscription",
     "offer": {"seller": "StackVault (backend API)", "role": "Organized Retail (pass-through)",
               "product": "Discord Nitro 1Y full warranty", "price": 40.23, "cur": "USD", "usd": 40.23,
               "cost_observed": 33.52,
               "evidence": "Directly-Observed (backend API 27/09) — EXACT identity (12m = 1Y)",
               "freshness": "Current (27/09 snapshot)",
               "note": "يجيب الاستعلام المؤجل RB-118 (discord nitro 12 months) — كلفة الجملة $33.52 مرصودة أيضًا"},
     "grade": "exact"},
    {"sku_id": "SKU-GC016",
     "identity": "Xbox Gift Card | 50 TRY | Turkey | code",
     "offer": {"seller": "Turgame", "role": "Retailer (Notion-specified channel)",
               "product": "XBOX Live Gift Card 50 TL TURKEY", "price": 1.02, "cur": "USD", "usd": 1.02,
               "evidence": "Directly-Observed (product page data 27/09) — EXACT (brand+value+region)",
               "freshness": "Current (27/09 snapshot)",
               "note": "يطابق المعدل الموحد الموثق $2.048/100TL (تحقق متقاطع ناجح)"},
     "grade": "exact"},
    {"sku_id": "SKU-AI048",
     "identity": "Grammarly Premium | 1 month | Global | account upgrade",
     "offer": {"seller": "StackVault (backend API)", "role": "Organized Retail",
               "product": "Grammarly AI Pro 1 Month full warranty", "price": 3.21, "cur": "USD", "usd": 3.21,
               "cost_observed": 2.67,
               "evidence": "Directly-Observed (backend API 27/09) — strong identity (Premium→Pro rebrand)",
               "freshness": "Current (27/09 snapshot)",
               "note": "إعادة تسمية المنتج (Premium→Pro) — نفس الهوية"},
     "grade": "strong"},
    {"sku_id": "SKU-SW013",
     "identity": "Adobe CC All Apps | 1 month | Global | account",
     "offer": {"seller": "StackVault (backend API)", "role": "Organized Retail",
               "product": "Adobe Full App Bypass Version 1 Month - full warranty", "price": 6.82, "cur": "USD", "usd": 6.82,
               "cost_observed": 5.68,
               "evidence": "Directly-Observed (backend API 27/09) — strong identity (All Apps = Full App)",
               "freshness": "Current (27/09 snapshot)",
               "note": "طريقة Bypass رمادية — هوية مجاورة بعلَم طريقة"},
     "grade": "strong-flagged"},
    {"sku_id": "SKU-AI030",
     "identity": "Adobe Firefly plan | 1 month | Global | account upgrade",
     "offer": {"seller": "StackVault (backend API)", "role": "Organized Retail",
               "product": "Adobe Full App Bypass Version 1 Month", "price": 6.82, "cur": "USD", "usd": 6.82,
               "cost_observed": 5.68,
               "evidence": "Directly-Observed (backend API 27/09) — ADJACENT identity (Firefly ⊂ All Apps)",
               "freshness": "Current (27/09 snapshot)",
               "note": "عرض لهوية أوسع (الحزمة الكاملة) — أرضية عائلة Adobe لا هوية Firefly نفسها"},
     "grade": "adjacent"},
    {"sku_id": "SKU-SW012",
     "identity": "Adobe Photoshop subscription | 1 month | Global | account",
     "offer": {"seller": "StackVault (backend API)", "role": "Organized Retail",
               "product": "Adobe Full App Bypass Version 1 Month", "price": 6.82, "cur": "USD", "usd": 6.82,
               "cost_observed": 5.68,
               "evidence": "Directly-Observed (backend API 27/09) — ADJACENT identity (Photoshop ⊂ All Apps)",
               "freshness": "Current (27/09 snapshot)",
               "note": "عرض الحزمة الكاملة — أرضية عائلة"},
     "grade": "adjacent"},
    {"sku_id": "SKU-AI047",
     "identity": "Cursor Pro | 1 month | Global | account upgrade",
     "offer": {"seller": "StackVault (backend API)", "role": "Organized Retail",
               "product": "API Cursor Pro 2600 Credits 1 month full warranty", "price": 10.01, "cur": "USD", "usd": 10.01,
               "cost_observed": 8.34,
               "evidence": "Directly-Observed (backend API 27/09) — ADJACENT identity (API credits ≠ subscription)",
               "freshness": "Current (27/09 snapshot)",
               "note": "رصيد API لا اشتراك — هوية مجاورة بعلَم"},
     "grade": "adjacent"},
    {"sku_id": "SKU-DS073",
     "identity": "Microsoft 365 Business Basic | 1 month | Global | tenant/key",
     "offer": {"seller": "StackVault (backend API)", "role": "Organized Retail",
               "product": "Microsoft 365 Admin Premium 1 Month full warranty", "price": 1.72, "cur": "USD", "usd": 1.72,
               "cost_observed": 1.43,
               "evidence": "Directly-Observed (backend API 27/09) — ADJACENT identity (Admin seat ≈ business tenant)",
               "freshness": "Current (27/09 snapshot)",
               "note": "مقعد أدمن — أرضية عائلة MS365 Business"},
     "grade": "adjacent"},
    {"sku_id": "SKU-DS074",
     "identity": "Microsoft 365 Business Standard | 1 month | Global | tenant/key",
     "offer": {"seller": "StackVault (backend API)", "role": "Organized Retail",
               "product": "Microsoft 365 Admin Premium 1 Month full warranty", "price": 1.72, "cur": "USD", "usd": 1.72,
               "cost_observed": 1.43,
               "evidence": "Directly-Observed (backend API 27/09) — ADJACENT identity",
               "freshness": "Current (27/09 snapshot)",
               "note": "مقعد أدمن — أرضية عائلة MS365 Business"},
     "grade": "adjacent"},
]

REJECTED = [
    {"sku_id": "SKU-DS044", "candidate": "Discord Nitro Trial 3 months ($3.89)",
     "reason": "تطابق هوية مزدوج خاطئ: Basic≠Trial و1m≠3m — رفض الضجيج (انضباط الدفعة 2)"},
    {"sku_id": "SKU-GT050", "candidate": "Steam India 250 INR ($2.61)",
     "reason": "عدم تطابق المنطقة: SKU عالمي (Global) والمنتج هندي — والقيمة غير قابلة للتحقق (per-game wallet)"},
]

# ---------------- merge into offers_intelligence ----------------
prefill_run = {
    "run_id": "MEC2-20260927-B3-PREFILL",
    "date": "2026-09-27",
    "method": "تعبئة مسبقة بلا حصة: مطابقة صارمة (علامة+قيمة+منطقة/مدة) بين كتالوجي StackVault-API (275 منتجًا بكلفة) وTurgame (117 منتجًا) وهويات P3 + الـ16 SKU المؤجلة، ثم تنقيح يدوي لكل مرشح (11 مرشحًا: 9 قبول + 2 رفض موثق)",
    "accepted": ACCEPTED,
    "rejected": REJECTED,
    "coverage_effect": "9 عروض Directly-Observed جديدة (2 exact + 2 strong + 5 adjacent) — منها حل الاستعلام المؤجل RB-118 (Nitro 12m = $40.23 بكلفة $33.52)",
    "limitations": [
        "العروض المقبولة بدرجة adjacent ليست هيية SKU نفسها — أرضيات عائلة موسومة بعلَم الهوية",
        "كل الأثمنة لحظة 27/09 (API/صفحات منتجات) — إعلانية لا معاملاتية",
        "كلف costPrice داخلية غير قابلة للتدقيق الخارجي [بحاجة لحساب B2B]",
    ],
}
oi["b3_prefill_run"] = prefill_run

# ---------------- update catalog ledger states ----------------
cov = cat.get("coverage_ledger", {})
for a in ACCEPTED:
    sid = a["sku_id"]
    if sid in cov:
        e = cov[sid]
        if isinstance(e, dict):
            e["ledger_state"] = "Directly-Observed offer (pre-fill) — search still pending for advertised cross-check"
            e["prefill"] = {"grade": a["grade"], "usd": a["offer"]["usd"], "seller": a["offer"]["seller"]}
        else:
            cov[sid] = {"ledger_state": "Directly-Observed offer (pre-fill)"}

json.dump(oi, open(OI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(cat, open(CAT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("OK — merged:")
print("  offers_intelligence.json += b3_prefill_run (9 accepted, 2 rejected documented)")
print("  catalog_v42.json coverage_ledger updated for 9 SKUs")
grades = {}
for a in ACCEPTED:
    grades[a["grade"]] = grades.get(a["grade"], 0) + 1
print("  grades:", grades)
