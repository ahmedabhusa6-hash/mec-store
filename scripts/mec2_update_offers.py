#!/usr/bin/env python3
"""MEC-2.0: append new observed offers to download/offers_intelligence.json (legal data file).
Adds: mec2 section (channels observed prices, mapped to existing SKU ids where identity matches,
plus new raw-material/products SKUs) without altering any pre-existing record."""
import json

F = "/home/z/my-project/download/offers_intelligence.json"
d = json.load(open(F, encoding="utf-8"))

d["mec2_run"] = {
    "run": "MEC2-20260927",
    "scope": "سجل القنوات §19 (31 كيانًا) + متجر StackVault — رصد مباشر 2026-09-27",
    "evidence_files": ["data/research/mec2_channels_raw.json", "data/research/mec2_search_results.json"],
    "disclaimer": "كل الأسعار إعلانية/معروضة بتاريخ 27/09 — التحقق من المعاملات غير منفذ. القنوات رمادية (تنتهك ToS غالبًا) ومصنفة بحسب المخاطرة في channel_evaluation.json — ليست توصيات شراء.",
    "offers": [
        {"sku_map": "SKU-AI001 (ChatGPT Plus — شهر)", "seller": "StackVault", "role": "متجر تجزئة منظم", "usd": 4.99, "evidence": "Directly-Observed (صفحة المتجر 27/09) — «حساب رسمي + ضمان» ادعاء غير متحقق معامليًا", "freshness": "Current"},
        {"sku_map": "SKU-AI001 (ChatGPT Plus — شهر)", "seller": "Evo Era (Telegram)", "role": "تجزئة آلية", "usd": 4.50, "evidence": "Directly-Observed (منشور قناة 27/09) — ضمان ساعتين (2HW)، دفع USDT", "freshness": "Current"},
        {"sku_map": "SKU-AI008 (Gemini AI Pro — شهر مكافئ)", "seller": "ProdSeller (Telegram + API)", "role": "موزع جملة/API", "usd": 0.40, "evidence": "Directly-Observed (منشور قناة 27/09) — منتج «Gemini 18 شهرًا» عبر API؛ فلاش 0.43 · جملة 0.39", "freshness": "Current", "note": "هوية SKU مختلفة عن الاشتراك الرسمي: رابط عرض ترويجي مستغل — فجوة 99.8% عن الرسمي ($359.82/18 شهرًا)"},
        {"sku_map": "SKU-DS002 (Netflix — شهر)", "seller": "StackVault", "role": "متجر تجزئة منظم", "usd": 3.99, "evidence": "Directly-Observed 27/09 — «Netflix Premium حساب خاص»", "freshness": "Current", "note": "هوية SKU مختلفة عن الاشتراك الرسمي (حساب خاص ≠ اشتراك فردي كامل)"},
        {"sku_map": "SKU-DS006 (Spotify Premium — شهر)", "seller": "StackVault", "role": "متجر تجزئة منظم", "usd": 4.49, "evidence": "Directly-Observed 27/09 — «حساب خاص»؛ الكلفة الهندية السنوية المكافئة ≈$0.79/شهر (تحكيم إقليمي)", "freshness": "Current"},
        {"sku_map": "جديد — Canva Pro لوحة 500 مستخدم", "seller": "learnwith_Alex/Bite Store", "role": "بائع طرق ولوحات", "usd": 2.50, "evidence": "Directly-Observed (منشور قناة 27/09) — فلاش سيل (كان 3.99)؛ العناق محجورة D4 (محتوى احتيالي مرصود في القناة)", "freshness": "Current", "quarantine": "D4"},
        {"sku_map": "جديد — Duolingo Super 12 شهرًا", "seller": "ProdSeller", "role": "موزع جملة/API", "usd": 0.55, "evidence": "Directly-Observed 27/09 — رابط 0.59 · API 0.55 · جملة 0.50", "freshness": "Current"},
        {"sku_map": "جديد — Coursera Plus سنة", "seller": "StackVault", "role": "متجر تجزئة منظم", "usd": 29.99, "evidence": "Directly-Observed 27/09", "freshness": "Current"},
        {"sku_map": "جديد — Microsoft 365 سنة/5 أجهزة", "seller": "StackVault", "role": "متجر تجزئة منظم", "usd": 9.99, "evidence": "Directly-Observed 27/09 — بضمان معلن", "freshness": "Current"},
        {"sku_map": "جديد — مادة خام: Gmail مستقر (عمر 2010-201x)", "seller": "ProdSeller", "role": "موزع جملة للمواد الخام", "usd": 0.75, "evidence": "Directly-Observed 27/09 — حساب 0.80 · API 0.75 · جملة 0.60", "freshness": "Current"},
        {"sku_map": "جديد — ChatGPT Plus «Factory 12m»", "seller": "Evo Era", "role": "تجزئة آلية", "usd": 17.00, "evidence": "Directly-Observed 27/09 — فلاش (كان 18.50) بخصم 8%", "freshness": "Current"}
    ],
    "structural_findings": [
        "أول قياس مباشر لفارق جملة→تجزئة داخل السوق الرمادي على منتج متطابق: $0.39 → $0.59 (10–51%)",
        "تدرج الضمان بالسعر موثق: $4.50 (ساعتان) مقابل $8–10 (3 أشهر) — الضمان مكوّن تسعير لا ثابت",
        "إشارتا ندرة حيتان موثقتان نصيًا: ترقيع UPI (نجاح 1–2%) + تقليص عروض Google Pixel (12→6 أشهر)",
        "طبقة API جملة علنية موثقة لأول مرة (ProdSeller: +500 مستخدم API) — منبع أعلى قابل للفحص بحساب"
    ]
}

json.dump(d, open(F, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("offers_intelligence.json updated: mec2_run section appended,", len(d["mec2_run"]["offers"]), "new offers")
