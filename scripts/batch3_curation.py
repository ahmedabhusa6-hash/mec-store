#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-3.0 | Batch-3 MANUAL CURATION (agent-reviewed, 2026-09-27 16:30 UTC) + merge.
Reviewed: 21 channel-host candidates + 20 official snippets individually;
other-host candidates rejected as systematic noise per batch-2 lesson (documented).
18 pre-seeded direct offers preserved. Output: offers_intelligence.json += batch3_run.
"""
import json, os

BASE = "/home/z/my-project"
oi = json.load(open(f"{BASE}/download/offers_intelligence.json", encoding="utf-8"))
cat = json.load(open(f"{BASE}/download/catalog_v42.json", encoding="utf-8"))
draft = json.load(open(f"{BASE}/research/batch3_intelligence_draft.json", encoding="utf-8"))["draft"]

# ---------------- CURATION DECISIONS (manual review) ----------------
# channel-host: (sku_id, decision, offer_dict or None, note)
CH_DECISIONS = {
    "SKU-AI035": ("accept", {"seller": "CJS CDKeys", "role": "Marketplace (Notion-specified)",
        "product": "Perplexity AI Pro — annual", "price": 244.86, "cur": "USD", "usd": 244.86,
        "evidence": "Advertised (snippet, 27/09) — channel-host",
        "note": "≈ السعر الرسمي السنوي ($240) — لا خصم فعليًا عبر هذه القناة للهوية السنوية"},
        "قناة معتمدة تبيع الهوية السنوية بسعر يقارب الرسمي"),
    "SKU-GC013": ("reject", None, "سياق gg.deals لفئات أخرى ($119.81 لبطاقات كبيرة) — العرض المباشر من Turgame $5.39 (exact) هو المعتمد"),
    "SKU-GC016": ("accept", {"seller": "SEAGM", "role": "Marketplace",
        "product": "Xbox Live Gift Card (TR) 50 TL", "price": 1.08, "cur": "USD", "usd": 1.08,
        "evidence": "Advertised (snippet, 27/09) — channel-host, EXACT identity",
        "note": "تحقق متقاطع ناجح: Turgame $1.02 مقابل SEAGM $1.08 (فارق 5.8% بين قناتين)"},
        "EXACT — يضاف كعرض معلن لقناة ثانية فوق المباشر"),
    "SKU-GC024": ("reject", None, "السياق لفئة 550/2000 TRY لا 50 TRY — عدم تطابق الفئة"),
    "SKU-GC025": ("reject", None, "السياق لبطاقة 15 EUR لا 35 EUR — عدم تطابق الفئة"),
    "SKU-GC026": ("reject", None, "السياق لبطاقة USD أمريكية لا EUR أوروبية — عدم تطابق العملة/المنطقة"),
    "SKU-GC030": ("reject", None, "السياق لبطاقة 200 EUR لا 10 EUR — عدم تطابق الفئة"),
    "SKU-GT021": ("accept", {"seller": "Eneba", "role": "Marketplace (Notion-specified)",
        "product": "Honkai Star Rail 300 Oneiric Shards + 30 Bonus", "price": 4.99, "cur": "USD", "usd": 4.99,
        "evidence": "Advertised (snippet, 27/09) — channel-host, EXACT identity",
        "note": "بسعر الرسمي تقريبًا (300 شظية = $4.99) — قناة موثقة توفر وصولًا موثوقًا لا خصمًا"},
        "EXACT"),
    "SKU-GT031": ("accept", {"seller": "G2A", "role": "Marketplace (Notion-specified)",
        "product": "Mobile Legends 706 Diamonds GLOBAL", "price": 10.24, "cur": "USD", "usd": 10.24,
        "evidence": "Advertised (snippet, 27/09) — channel-host, EXACT identity; price corrected from extraction noise ($0.99 = عنصر آخر بالصفحة؛ السياق النصي: 10.24 USD)",
        "note": "-9% تحت $11.30 المعلنة بالصفحة"},
        "EXACT مع تصحيح سعري موثق من السياق النصي"),
    "SKU-GT032": ("reject", None, "السياق لهوية 706 شظية (GT031) لا 1050 — عدم تطابق الكمية"),
    "SKU-GT033": ("reject", None, "السياق لفئة 5350 VP (GT034) لا 3650 — عدم تطابق الكمية"),
    "SKU-GT034": ("accept", {"seller": "GG.deals (aggregated keyshops)", "role": "Price comparison",
        "product": "Valorant 5350 Points", "price": 49.40, "cur": "USD", "usd": 49.40,
        "evidence": "Advertised (snippet, 27/09) — channel-host, EXACT",
        "note": "-1.2% تحت الرسمي $49.99"},
        "EXACT"),
    "SKU-GT037": ("reject", None, "$1.00 المستخرج ضجيج (الصفحة تبيع 5250 Robux بـ$55.13) — لا تطابق كمية"),
    "SKU-GT038": ("reject", None, "نفس الضجيج — 10000 Robux تُسعّر ~$95+ لا $1"),
    "SKU-GT040": ("accept", {"seller": "G2A", "role": "Marketplace (Notion-specified)",
        "product": "Genshin Impact 3880 Genesis Crystals (EUROPE)", "price": 64.97, "cur": "USD", "usd": 64.97,
        "evidence": "Advertised (snippet, 27/09) — channel-host, EXACT identity; price corrected from extraction noise ($1.98 = أصغر حزمة بالصفحة)",
        "note": "≈ السعر الرسمي لـ3880 جوهرة — وصول لا خصم"},
        "EXACT مع تصحيح سعري"),
    "SKU-GT041": ("reject", None, "السياق لفئة 3880 (GT040) لا 8080 — عدم تطابق الكمية"),
    "SKU-GT050": ("accept", {"seller": "Eneba", "role": "Marketplace (Notion-specified)",
        "product": "Steam Wallet Gift Card 10 USD", "price": 10.47, "cur": "USD", "usd": 10.47,
        "evidence": "Advertised (snippet, 27/09) — ADJACENT identity (بطاقة Steam ≠ شحن Dota مباشر، لكنه المسار الفعلي للشحن)",
        "note": "+4.7% فوق الاسمي — تأكيد رابع لسوق العلاوة الأمريكي (بعد Steam/Netflix/Spotify)"},
        "ADJACENT"),
    "SKU-GK012": ("accept", {"seller": "GG.deals (aggregated keyshops)", "role": "Price comparison",
        "product": "ARK: Survival Ascended — key", "price": 11.22, "cur": "USD", "usd": 11.22,
        "evidence": "Advertised (snippet, 27/09) — channel-host, EXACT",
        "note": "أدنى سعر موثق بالمقارنة (الرسمي $44.99) — خصم -75%"},
        "EXACT"),
    "SKU-GK015": ("accept", {"seller": "GG.deals (aggregated keyshops)", "role": "Price comparison",
        "product": "PUBG: Battlegrounds — RUSSIA key", "price": 2.99, "cur": "USD", "usd": 2.99,
        "evidence": "Advertised (snippet, 27/09) — EXACT with REGION FLAG",
        "note": "نسخة روسية إقليمية — هوية SKU عالمية قد تسعّر أعلى؛ عُلّم العلم الإقليمي"},
        "EXACT + region flag"),
    "SKU-GK020": ("accept", {"seller": "GG.deals (aggregated keyshops)", "role": "Price comparison",
        "product": "Kingdom Come: Deliverance II — key", "price": 4.99, "cur": "USD", "usd": 4.99,
        "evidence": "Advertised (snippet, 27/09) — channel-host, EXACT",
        "note": "خصم عميق موثق بالمقارنة (الرسمي $49.99) — -90%"},
        "EXACT"),
    "SKU-VN036": ("accept", {"seller": "TollFreeForwarding.com (official provider)", "role": "Official provider",
        "product": "Virtual toll-free number — USA", "price": 4.00, "cur": "USD", "usd": 4.00,
        "evidence": "Advertised (provider's own page, 27/09) — official baseline",
        "note": "سعر المزود الرسمي نفسه — خط أساس لا عرض رمادي"},
        "OFFICIAL baseline"),
}

# official-baseline: (sku_id, decision, baseline or None, note)
OF_DECISIONS = {
    "SKU-AI024": ("accept", {"seller": "Gamma (official)", "usd": 10.0, "note": "نطاق رسمي موثق $10-20/شهر"}, "خط رسمي موثق"),
    "SKU-AI035": ("reject", None, "السياق عن Kinsta (استضافة) لا تسعير Perplexity — ضجيج"),
    "SKU-AI044": ("accept", {"seller": "Gamma (official)", "usd": 10.0, "note": "النطاق الرسمي $10-20 — Max تحديده الدقيق يحتاج قراءة صفحة"}, "خط رسمي (نطاق)"),
    "SKU-AI050": ("reject", None, "السياق من Envato (علامة مختلفة عن Freepik) — عدم تطابق علامة"),
    "SKU-AI051": ("accept", {"seller": "Envato Elements (official)", "usd": 16.5, "note": "$16.50/شهر رسمي"}, "خط رسمي"),
    "SKU-SW010": ("reject", None, "السياق عن أرصدة Azure المرفقة لا سعر المنتج — لا بيانات سعر"),
    "SKU-SW020": ("reject", None, "$24.99 لا يطابق Unity Pro الرسمي (~$2,200/مقعد) — خطأ استخراج"),
    "SKU-SM010": ("downgrade", None, "مصدر Google Sites (دراسة SMM) — ليس رسميًا؛ يبقى lead معلن"),
    "SKU-SM018": ("downgrade", None, "نفس المصدر — downgrade إلى lead"),
    "SKU-SM019": ("downgrade", None, "نفس المصدر — downgrade إلى lead"),
    "SKU-DS023": ("accept", {"seller": "Apple (official)", "usd": 14.99, "note": "Apple TV+ $14.99/شهر بعد تجربة 7 أيام"}, "خط رسمي"),
    "SKU-DS024": ("reject", None, "تعليق مستخدم بمنتدى Deezer ($4.55 قديم 2023) — ليس خطًا رسميًا؛ المعتمد: Turgame $9.61 مباشر"),
    "SKU-DS035": ("reject", None, "مصدر LinkedIn مقال — غير رسمي؛ Trello Premium الرسمي $10/مستخدم"),
    "SKU-DS036": ("reject", None, "مصدر LinkedIn — غير رسمي"),
    "SKU-DS047": ("accept", {"seller": "Spotify (official)", "usd": 18.99, "note": "خط Duo $18.99/شهر (هوية SKU = Duo)"}, "خط رسمي لطبقة Duo"),
    "SKU-DS055": ("accept", {"seller": "LinkedIn (official)", "usd": 39.99, "note": "Premium Career $39.99/شهر أو $239.88/سنة"}, "خط رسمي"),
    "SKU-DS059": ("accept", {"seller": "Skillshare (official)", "usd": 13.99, "note": "$13.99/شهر بفوترة سنوية $167.88"}, "خط رسمي"),
    "SKU-DS066": ("accept", {"seller": "Monday.com (official)", "usd": 9.0, "note": "Standard $9/مستخدم/شهر"}, "خط رسمي"),
    "SKU-DS067": ("reject", None, "السياق من monday.com (علامة مختلفة عن ClickUp) — عدم تطابق علامة"),
    "SKU-DS068": ("reject", None, "السياق من monday.com (علامة مختلفة عن Asana) — عدم تطابق علامة"),
}

# ---------------- apply + build batch3_run ----------------
accepted_channel, accepted_official = {}, {}
for sid, (dec, offer, note) in CH_DECISIONS.items():
    if dec == "accept":
        accepted_channel[sid] = {"offer": offer, "note": note}
for sid, (dec, baseline, note) in OF_DECISIONS.items():
    if dec == "accept":
        accepted_official[sid] = {"baseline": baseline, "note": note}

# count states across 218
states = {"direct_observed_preseeded": 0, "channel_advertised": 0, "official_baseline": 0,
          "advertised_lead_only": 0, "noise_rejected_other_host": 0}
for sid, rec in draft.items():
    if rec.get("has_direct_observed_offers"):
        states["direct_observed_preseeded"] += 1
    elif sid in accepted_channel:
        states["channel_advertised"] += 1
    elif sid in accepted_official:
        states["official_baseline"] += 1
    elif rec.get("n_candidates", 0) > 0:
        states["noise_rejected_other_host"] += 1
    else:
        states["advertised_lead_only"] += 1

batch3_run = {
    "run_id": "MEC2-20260927-B3",
    "date": "2026-09-27",
    "scope": "218 P3 SKUs — 143 search actions (105 OK first window + completion), 562 findings, 218/218 covered",
    "curation": {
        "method": "تنقيح يدوي كامل: مراجعة فردية لكل مرشح قناة معتمدة (21) وكل مقتطف رسمي (20) + رفض منهجي لضجيج المضيفين الآخرين (درس الدفعة 2) مع تصحيحين سعريين موثقين من السياق النصي",
        "channel_accepted": {sid: {"offer": v["offer"], "note": v["note"]} for sid, v in accepted_channel.items()},
        "official_accepted": {sid: {"baseline": v["baseline"], "note": v["note"]} for sid, v in accepted_official.items()},
        "rejections": {
            "channel_host": {sid: note for sid, (d, _, note) in CH_DECISIONS.items() if d == "reject"},
            "official": {sid: note for sid, (d, _, note) in OF_DECISIONS.items() if d in ("reject", "downgrade")},
            "systematic": "كل مرشحين المضيفين الآخرين (مدونات/مراجعات/صفحات غير ذات صلة) رُفضوا كضجيج منهجي — حالة موثقة لا حذف (فشل الاسترجاع ≠ عدم الوجود)",
        },
        "price_corrections": [
            "GT031: $0.99 المستخرج → $10.74→$10.24 من السياق النصي (706 شظية GLOBAL)",
            "GT040: $1.98 المستخرج → $64.97 من السياق النصي (3880 جوهرة EUROPE)",
        ],
    },
    "states_summary": states,
    "key_findings": [
        "التحقق المتقاطع الناجح للبطاقات التركية: Turgame $1.02 مقابل SEAGM $1.08 لبطاقة Xbox 50 TL (فارق 5.8% بين قناتين مستقلتين)",
        "سوق العلاوة الأمريكي تأكد للمرة الرابعة: بطاقة Steam $10 تباع $10.47 (+4.7%) عبر Eneba",
        "خصومات مفاتيح الألعاب الموثقة بالمقارنة: ARK -75% · Kingdom Come II -90% · PUBG RU -70% (بعلم إقليمي)",
        "شحن الألعاب عبر الأسواق ≈ الرسمي (Honkai 300=$4.99 · Valorant 5350=$49.40 -1.2% · ML 706=$10.24 -9%) — قنوات موثوقة للوصول لا للخصم",
        "Perplexity Pro السنوي عبر CJS ≈ الرسمي ($244.86 مقابل $240) — لا خصم للهوية السنوية",
        "خطوط رسمية جديدة موثقة: Apple TV+ $14.99 · LinkedIn Premium $39.99 · Skillshare $13.99/ش · Monday Standard $9 · Spotify Duo $18.99 · Envato $16.50",
    ],
    "limitations": [
        "كل العروض المقبولة من الدفعة 3 بمستوى «معلن (مقتطف)» — قراءات الصفحات المباشرة مؤجلة للحصة (§19)",
        "18 SKU لها عروض مباشرة من موجات MEC-2.5 (أعلى مستوى) — محفوظة وغير مستبدلة",
        "وحدات غير نقدية (UC/VP/Shards/Robux) تحتاج جداول تحويل رسمية للتحقق الكمي الكامل",
    ],
}
oi["batch3_run"] = batch3_run

# ---------------- catalog ledger update: P3 fully searched ----------------
cov = cat.get("coverage_ledger", {})
for sid, rec in draft.items():
    if sid in cov and isinstance(cov[sid], dict):
        if rec.get("has_direct_observed_offers"):
            cov[sid]["ledger_state"] = "Directly-Observed offer(s) + searched (b3 snippet wave)"
        elif sid in accepted_channel:
            cov[sid]["ledger_state"] = "Channel-host advertised offer (curated)"
            cov[sid]["curated_offer"] = {"usd": accepted_channel[sid]["offer"]["usd"],
                                          "seller": accepted_channel[sid]["offer"]["seller"]}
        elif sid in accepted_official:
            cov[sid]["ledger_state"] = "Official baseline documented (curated)"
        else:
            cov[sid]["ledger_state"] = "Searched (b3) — lead-only or noise-rejected (documented)"
# program-level coverage
cat["coverage_ledger"]["_program"] = {
    "P1": "46/46 searched (MEC-1.0, 142 actions)",
    "P2": "173/173 searched (MEC-2.1 + 15 deferred completed 27/09 16:03)",
    "P3": "218/218 searched (MEC-3.0, 143 actions + 18 direct pre-fill offers)",
    "total": "437/437 SKUs at snippet level; 18+15+7+2=42 Directly-Observed offers across waves",
}

json.dump(oi, open(f"{BASE}/download/offers_intelligence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(cat, open(f"{BASE}/download/catalog_v42.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("BATCH-3 CURATION + MERGE COMPLETE")
print("states:", states)
print("channel accepted:", len(accepted_channel), "| official accepted:", len(accepted_official))
print("channel rejected:", len([1 for _, (d, _, _) in CH_DECISIONS.items() if d == "reject"]),
      "| official rejected/downgraded:", len([1 for _, (d, _, _) in OF_DECISIONS.items() if d != "accept"]))
