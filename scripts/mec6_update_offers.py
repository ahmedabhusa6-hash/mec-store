#!/usr/bin/env python3
"""Append MEC-6 run to offers_intelligence.json (idempotent)"""
import json
from datetime import datetime, timezone

path = "/home/z/my-project/download/offers_intelligence.json"
d = json.load(open(path, encoding="utf-8"))

run = {
    "run_id": "MEC6-20260928-LIVE",
    "trigger": "مفتاح ProdSeller API وصل من المستخدم → أمر: اكشف كل الأسعار (ProdSeller أولًا ثم الآخرين)",
    "executed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
    "prodseller_live": {
        "key_validated": True,
        "account": "SaraShamari / bronze / balance $0",
        "method": "GET /v1/balance + GET /v1/products (read-only, zero orders)",
        "products_total": 25,
        "in_stock": 19,
        "api_discount_range_pct": [0.0, 27.6],
        "api_discount_median_pct": 9.1,
        "price_range_usd": [0.09, 10.0],
        "top_sellers": [
            {"product": "Gemini Pro 18M (link)", "price": 0.45, "sold": 212259},
            {"product": "CapCut Pro 1M FW", "price": 1.25, "sold": 17282},
            {"product": "MS Office 365 Plus 1yr", "price": 0.21, "sold": 4778},
            {"product": "CapCut Pro 7D FW", "price": 0.13, "sold": 2805},
            {"product": "Duolingo Super 12M", "price": 0.45, "sold": 1589},
        ],
        "notable": [
            "ChatGPT Plus 1M (UPI method) = $2.90 API / $3.40 public — OOS",
            "Netflix غير موجود في الكتالوج الحالي",
            "مثال الوثائق (Netflix $4.99) توضيحي وليس منتجًا فعليًا",
        ],
        "raw_file": "research/prodseller_live/products_raw.json",
        "evidence_class": "Directly-Observed (live API response)",
    },
    "stackvault_live": {
        "url": "https://decohomz.com/sv-api/products",
        "products_total": 322,
        "new_vs_b3_capture": 58,
        "cost_layer_exposed": "costPrice مكشوف لكل منتج",
        "markup_over_cost": {"min": 13.0, "max": 60.7, "median": 16.7},
        "evidence_class": "Directly-Observed (live backend response)",
    },
    "cross_match_verdict": {
        "headline": "12/21 تطابق تام بالسنت بين سعر ProdSeller API وتكلفة StackVault الداخلية",
        "implication": "StackVault يشتري من ProdSeller API — سلسلة التوريد الجملة→تجزئة مثبتة بالسنت لأول مرة",
        "exact_matches": [
            {"product": "CapCut Pro 1M", "ps_api": 1.25, "sv_cost": 1.25, "sv_retail": 1.60},
            {"product": "CapCut Pro 7D", "ps_api": 0.13, "sv_cost": 0.13, "sv_retail": 0.20},
            {"product": "CapCut Pro 6M", "ps_api": 8.50, "sv_cost": 8.50, "sv_retail": 9.99},
            {"product": "CapCut 1600 Credits", "ps_api": 1.60, "sv_cost": 1.60, "sv_retail": 2.05},
            {"product": "Office365 1yr", "ps_api": 0.21, "sv_cost": 0.21, "sv_retail": 0.38},
            {"product": "Gemini Pro 18M", "ps_api": 0.45, "sv_cost": 0.45, "sv_retail": 0.52, "sv_stock": 898},
            {"product": "Canva Admin 500", "ps_api": 4.40, "sv_cost": 4.40, "sv_retail": 5.28},
            {"product": "Gmail fresh", "ps_api": 0.60, "sv_cost": 0.60, "sv_retail": 0.77},
            {"product": "edX 12M", "ps_api": 1.10, "sv_cost": 1.10, "sv_retail": 1.30},
            {"product": "Avira 3M", "ps_api": 0.80, "sv_cost": 0.80, "sv_retail": 0.99},
            {"product": "Miro 100", "ps_api": 8.00, "sv_cost": 8.00, "sv_retail": 9.60},
            {"product": "Framer 1yr", "ps_api": 6.00, "sv_cost": 6.00, "sv_retail": 7.20},
        ],
        "different_identity_note": "حالات DIFF = بناء/ضمان مختلف (ChatGPT Plus UPI $2.90 عند ProdSeller مقابل بناءات أغلى عند SV حتى $12.81 بضمان أطول) — ليست خطأ قياس",
    },
    "other_suppliers_probe": {
        "ggsel": "401 محجوب جغرافيًا (كل المسارات) — Retrieval-Limited؛ رصد سابق: ChatGPT Plus من 749₽",
        "bittopup": "فحص حي: API أمامي داخلي فقط — لا أسعار جملة متفاوتة علنية",
        "k4g": "api.k4g.com = 500 Internal Server Error من بيئتنا",
        "from_mec5_verified": "Turgame (225 صفًا، فجوة 0.8-1%) + Kinguin (5-10.2% كميات، موثق) + Reloadly (2-10% منشور) + Bitrefill/Z2U/U7BUY (لا فجوة شرائية) + SEAGM/OffGamers (استفساري) + DingConnect (خلف دخول مجاني)",
    },
    "wholesale_floor_live": "الأرضية الجملية الحية الآن أرقام فعلية: Gemini 18M=$0.45 · ChatGPT Plus UPI=$2.90 · Office365 1yr=$0.21 · CapCut 1M=$1.25 · Canva Admin500=$4.40 · Duolingo=$0.15 · Adobe Express=$0.35 · Notion=$1.10 · Gmail=$0.60",
    "dolaa_status": "حاسبة الهوامش جاهزة بأرضية حية — بانتظار: رابط قناة دولا / لقطات أسعاره / 10-15 منتجًا بأسعار شرائه",
    "deliverable": "تبويب MEC-6 «الأسعار الحية API» في تطبيق الويب + mec6.json",
}

d["mec6_live_run"] = run
d["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

with open(path, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
print("✓ offers_intelligence.json updated with mec6_live_run")
