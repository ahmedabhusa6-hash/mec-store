#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.5j | Turgame P3 wave — FINAL manual curation (agent-reviewed) + merge.
From 612 priced products across 92 categories:
  7 ACCEPTED offers (4 exact + 1 strong + 2 adjacent)
  All other candidates rejected with documented reasons (identity/region/brand mismatch,
  unverifiable non-monetary units).
  Rich market signals documented (not SKU offers).
"""
import json, os

BASE = "/home/z/my-project"
oi = json.load(open(f"{BASE}/download/offers_intelligence.json", encoding="utf-8"))
cat = json.load(open(f"{BASE}/download/catalog_v42.json", encoding="utf-8"))

ACCEPTED = [
    {"sku_id": "SKU-DS044", "grade": "exact",
     "identity": "Discord Nitro Basic | 1 month | Global | gift code",
     "offer": {"seller": "Turgame", "role": "Retailer (Notion-specified channel)",
               "product": "Discord Nitro Basic - 1 Month Subscription", "price": 4.76, "cur": "USD", "usd": 4.76,
               "evidence": "Directly-Observed (product page data 27/09) — EXACT identity",
               "freshness": "Current (27/09 snapshot)",
               "note": "فوق الرسمي ($2.99) بـ+59% — علاوة مسار البطاقة: المنتج الرقمي عبر بطاقة الهدية أغلى من الشراء المباشر بالبطاقة الدولية (علاوة وصول لا خصم)"}},
    {"sku_id": "SKU-GC013", "grade": "exact",
     "identity": "Xbox Gift Card | 5 EUR | EU | code",
     "offer": {"seller": "Turgame", "role": "Retailer (Notion-specified channel)",
               "product": "Microsoft Xbox FR 5 EUR", "price": 5.39, "cur": "USD", "usd": 5.39,
               "evidence": "Directly-Observed (product page 27/09) — EXACT (brand+value+currency, FR⊂EU)",
               "freshness": "Current (27/09 snapshot)",
               "note": "+7.8% فوق القيمة الاسمية — البطاقات الأوروبية أيضًا تعامل بعلاوة عبر هذه القناة"}},
    {"sku_id": "SKU-GC103", "grade": "exact",
     "identity": "PSN Card (TRY) | 250 TRY | Turkey | code",
     "offer": {"seller": "Turgame", "role": "Retailer (Notion-specified channel)",
               "product": "Sony PlayStation Store Gift Card 250 TRY TURKEY", "price": 5.12, "cur": "USD", "usd": 5.12,
               "evidence": "Directly-Observed (product page 27/09) — EXACT",
               "freshness": "Current (27/09 snapshot)",
               "note": "المعدل الموحد $2.048/100TRY — تأكد عبر 10 فئات PSN TRY (250→5000)"}},
    {"sku_id": "SKU-GC104", "grade": "exact",
     "identity": "PSN Card (TRY) | 500 TRY | Turkey | code",
     "offer": {"seller": "Turgame", "role": "Retailer (Notion-specified channel)",
               "product": "Sony PlayStation Store Gift Card 500 TRY TURKEY", "price": 10.23, "cur": "USD", "usd": 10.23,
               "evidence": "Directly-Observed (product page 27/09) — EXACT",
               "freshness": "Current (27/09 snapshot)", "note": "نفس المعدل الموحد"}},
    {"sku_id": "SKU-DS024", "grade": "strong",
     "identity": "Deezer subscription | 1 month | US",
     "offer": {"seller": "Turgame", "role": "Retailer (Notion-specified channel)",
               "product": "Deezer Premium 10.99 USD", "price": 9.61, "cur": "USD", "usd": 9.61,
               "evidence": "Directly-Observed (product page 27/09) — strong identity (بطاقة اشتراك شهري بالدولار)",
               "freshness": "Current (27/09 snapshot)",
               "note": "-12.6% تحت القيمة الرسمية ($10.99) — أول مرساة Deezer في المشروع"}},
    {"sku_id": "SKU-DS047", "grade": "adjacent",
     "identity": "Spotify Premium | 1 month | US",
     "offer": {"seller": "Turgame", "role": "Retailer (Notion-specified channel)",
               "product": "Spotify Gift Card - 10 USD", "price": 11.08, "cur": "USD", "usd": 11.08,
               "evidence": "Directly-Observed (product page 27/09) — ADJACENT (بطاقة هدية لا اشتراك مباشر)",
               "freshness": "Current (27/09 snapshot)",
               "note": "+10.8% فوق الاسمي — تأكيد ثالث لسوق العلاوة الأمريكي (بعد Steam +8.5% وNetflix)"}},
    {"sku_id": "SKU-DS062", "grade": "adjacent", "deferred_query": "RB-121 (جزئي)",
     "identity": "Surfshark subscription | 24 months | Global",
     "offer": {"seller": "Turgame", "role": "Retailer (Notion-specified channel)",
               "product": "Surfshark One 49.08 USD", "price": 35.35, "cur": "USD", "usd": 35.35,
               "evidence": "Directly-Observed (product page 27/09) — ADJACENT (حزمة One أعلى من VPN المجرد؛ المدة غير مصرّحة بالاسم)",
               "freshness": "Current (27/09 snapshot)",
               "note": "-28% تحت قيمة الحزمة المعلنة — يجيب جزئيًا الاستعلام المؤجل RB-121: مسار سوق (لا رسمي) لـSurfshark عند $35.35/24 شهرًا تقريبًا"}},
]

SIGNALS = [
    "معدل PSN TRY الموحد $2.048/100TRY تأكد عبر 10 فئات (250→5000 TRY) — أقوى دليل على التسعير الصيري للبطاقات التركية",
    "PSN لبنان 10USD = $9.05 — التأكيد الثالث المستقل لمرساة $9.07 (تشغيلة 25/09 + MEC-2.3 + الآن)",
    "بطاقات PSN خليجية تحت الاسمي: عمان 5USD=$4.84 (-3.2%) · البحرين $4.89 · الإمارات 10USD=$9.73 (-2.7%)",
    "بطاقات Airalo للمحفظة عند -1% تحت الاسمي (4 فئات) — تختلف هويةً عن باقات البيانات (مرساة P1 $4.00 باقة فعلية)",
    "سلّم StarzPlay UAE كاملًا: 1M $10.22 · 3M $25.48 · 6M $49.68 · 12M $89.07 (330 AED)",
    "سلّم Shahid 3M عبر 8 دول: $9.47 (الجزائر) → $12.59 (الأردن) — أول خريطة تسعير إقليمية لمنصة خليجية",
    "Anghami Plus 1M مصر $2.60 — أرخص اشتراك موسيقي خليجي-إقليمي مرصود",
    "Bilibili Premium 30 يوم: تايلاند $1.89 · الفلبين $1.39 · ماليزيا $2.24 — التحكيم الآسيوي داخل منتج واحد",
    "Turgame البرمجيات بسعر التجزئة الكامل: Win11 Pro $267.97 مقابل €1.03 رمادي (فارق ~260×) — القناة ليست مصدر برمجيات رمادية؛ قيمتها في البطاقات والاشتراكات الإقليمية",
    "Hulu JP: 1M $7.31 · 3M $21.90 · 6M $43.78 — مسار ياباني موثق",
    "YouTube TV بطاقات عند +4% فوق الاسمي ($5→$5.19 … $100→$103.99)",
    "منصات MENA بلا SKUs في الكتالوج (StarzPlay/Shahid/Anghami/OSN+/Yango/Storytel/Bilibili/iQIYI Youku…) — مرشحة لتوسيع الكتالوج مستقبلًا",
]

REJECTED_SUMMARY = [
    "كل مطابقات candidate-no-value (وحدات غير نقدية: RP/diamonds/UC/CP/Robux) — غير قابلة للتحقق بدون جدول تحويل رسمي",
    "بطاقات بقيمة مطابقة وعلامة مختلفة (FORTNITE≠Steam، IMVU≠Xbox، Meta≠Apple…)",
    "عدم تطابق منطقة/عملة (Spotify Colombia≠US، Crunchyroll 3M UK≠1M US)",
    "بطاقة Paramount $100 ≠ اشتراك شهر (هوية مختلفة)",
    "Office 365 Personal ≠ Business Basic/Standard (طبقة خطة مختلفة)",
]

turgame_p3_run = {
    "run_id": "MEC2-20260927-TG-P3",
    "date": "2026-09-27",
    "method": "موجة Turgame P3: 92 فئة ذات صلة استُخرجت (612 منتجًا مسعّرًا، صفر أخطاء، إيقاع 3 ثوانٍ) من قناة محددة في Notion — ثم تنقيح يدوي كامل بمطابقة صارمة (علامة+قيمة+عملة+منطقة)",
    "accepted": ACCEPTED,
    "market_signals": SIGNALS,
    "rejected": REJECTED_SUMMARY,
    "coverage_effect": "7 عروض Directly-Observed جديدة (4 exact + 1 strong + 2 adjacent) — منها إجابة جزئية للاستعلام المؤجل RB-121 (Surfshark) وإجابة كاملة لهوية Nitro Basic",
    "limitations": ["كل الأثمنة لحظة 27/09", "إعلانية لا معاملاتية", "فئات بدون أسعار معروضة (roblox معظمها، prepaid-visa، software) موثقة Retrieval-Limited", "بطاقات MENA الغنية بلا SKUs مقابلة في الكتالوج الحالي"],
}
oi["turgame_p3_run"] = turgame_p3_run

cov = cat.get("coverage_ledger", {})
for a in ACCEPTED:
    sid = a["sku_id"]
    if sid in cov and isinstance(cov[sid], dict):
        cov[sid]["turgame_prefill"] = {"grade": a["grade"], "usd": a["offer"]["usd"]}
        if a.get("deferred_query"):
            cov[sid]["deferred_partial_answer"] = a["deferred_query"]

json.dump(oi, open(f"{BASE}/download/offers_intelligence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(cat, open(f"{BASE}/download/catalog_v42.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK — turgame_p3_run merged: 7 offers, 12 signals, ledger updated")
