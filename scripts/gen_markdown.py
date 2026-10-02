#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-1.0 | Phase 5 — Final output synthesis: Web Page + Markdown (semantic parity).
Source of truth: download/offers_intelligence.json + catalog_v42.json + research ledgers.
"""
import json, os

OUT = "/home/z/my-project/download"
RD = "/home/z/my-project/research"
TODAY = "2026-09-27"

intel = json.load(open(OUT + "/offers_intelligence.json", encoding="utf-8"))
cat = json.load(open(OUT + "/catalog_v42.json", encoding="utf-8"))
ledger_actions = json.load(open(RD + "/action_ledger.json", encoding="utf-8"))
run = json.load(open(RD + "/run_contract.json", encoding="utf-8"))

S = intel["skus"]; PI = intel["price_intelligence"]
fams = cat["catalog_program"]["families"]
b1 = [s for s in cat["skus"] if s["batch"] == 1]
ok_actions = [a for a in ledger_actions if a["retrieval_status"] == "OK"]
fail_actions = [a for a in ledger_actions if a["retrieval_status"] != "OK"]

# ---------- entity registry (Phase 3) ----------
ENTITIES = [
 {"name":"Turgame","domain":"turgame.com","role":"Retailer/Reseller + Wholesaler/Distributor","role_evidence":"صفحة منتج + بوابة wholesale.turgame.com موثقة حيًا 27/09 ('Digital Gift Card Wholesale Solutions')","state":"[مؤكد]","notes":"SUP-002. أول بائع تجزئة يوثق جملة حية. Turgame/Definite Play: تُحفظ هويتان منفصلتان حتى دليل دمج — [بحاجة إلى تحقق]"},
 {"name":"Eneba","domain":"eneba.com","role":"Marketplace (multi-seller)","role_evidence":"JSC Helis play, فيلنيوس — documented 25/09; عروض موثقة سابقًا (Steam 20=20.93$، PSN 50=47.17$)","state":"[مؤكد] (كيانًا) — عروض اليوم Retrieval-Limited (روابط المنتجات 404)","notes":"أسعار اليوم لم تُقرأ مباشرة — تُورَث من 25/09 بوسم قِدَم محتمل"},
 {"name":"FazerCards","domain":"reseller.fazercards.com","role":"Reseller Platform (B2B)","role_evidence":"SUP-013-LEAD → منصة حية موثقة 27/09 'Digital Products Reseller Platform'","state":"[مؤكد] وجودًا — التسعير خلف تسجيل الدخول [بحاجة إلى تحقق]","notes":"ترقية من LEAD إلى كيان مُتحقق وجوده"},
 {"name":"Reloadly","domain":"reloadly.com","role":"API/Distributor (B2B)","role_evidence":"صفحة حية 27/09: Gift Card & Payout API — منتجات: بطاقات، Airtime، بيانات، Payout","state":"[مؤكد]","notes":"حل الدور المزدوج: لا واجهة تجزئة → يُصنّف موزع B2B/API فقط. أسعار الجملة خلف بوابة API [غير معروف]"},
 {"name":"GGSel","domain":"ggsel.net","role":"Marketplace/Aggregator (RU)","role_evidence":"كتالوج ChatGPT Plus حي 27/09: 'от 749.00₽' (بائعون متعددون)","state":"[مؤكد]","notes":"نموذج وسطاء/حسابات مشتركة — هوية SKU تختلف عن الترقية الرسمية"},
 {"name":"Keyforsteam","domain":"keyforsteam.de","role":"Price aggregator/comparison (DE)","role_evidence":"Preisvergleich حي 27/09 (Win11: 64 عرضًا سابقًا، Office2021: 77 عرضًا سابقًا)","state":"[مؤكد]","notes":"بائعوه المكتشفون: Keywrld، Keys4us، Pixelcodes — كيانات جديدة [بحاجة إلى تحقق]"},
 {"name":"CJS CD Keys","domain":"cjs-cdkeys.com","role":"Retailer/Reseller","role_evidence":"واجهة حية 27/09: Win11 Pro من £9.49 + سياسة استرداد معلنة","state":"[مؤكد]","notes":"حركة سعر: £9.99 (25/09) → £9.49 (27/09)"},
 {"name":"Kinguin / G2A / Z2U / Allkeyshop / GG.deals / CDKeys / RoyalCDKeys / Gocdkeys / Keys4us","domain":"-","role":"Marketplaces / مقارنات أسعار","role_evidence":"وجود معلن عبر مقاطع نتائج اليوم + توثيق 25/09","state":"[مؤكد] وجودًا — عروض فردية بدرجة Advertised","notes":"GG.deals خلف Cloudflare (قيد الاسترجاع)"},
 {"name":"Microsoft / Xbox","domain":"microsoft.com / xbox.com","role":"Primary/Official (الناشر)","role_evidence":"xbox.com حي 27/09: GPU $22.99/شهر","state":"[مؤكد]","notes":"حل التداخل: Xbox قسم ألعاب Microsoft — أسر SKU منفصلة، لا دمج كيانات"},
 {"name":"Netflix / Spotify / YouTube / Discord / Telegram / OpenAI / NordVPN / Airalo / MobiMatter","domain":"-","role":"Primary/Official أو Retailer متخصص","role_evidence":"صفحات رسمية حية 27/09 (NordVPN خلف Cloudflare)","state":"[مؤكد] (باستثناء NordVPN: [بحاجة إلى تحقق] اليوم)"},
]

# ---------- markdown ----------
md = []
md.append("# قاعدة معلومات الموردين — التشغيل MEC1-20260927 (الدفعة 1)")
md.append("")
md.append("**Run ID:** MEC1-20260927-B1 | **الإصدار:** v4.2 Candidate (working) | **التاريخ:** %s | **البرنامج:** CP-1 (437 SKU)" % TODAY)
md.append("")
md.append("**الصياغة الحاكمة لكل نتيجة سعرية:** «أقل سعر تم اكتشافه والتحقق منه ضمن نطاق البحث وتاريخ الفحص والشروط المحددة للـSKU» — يُمنع «الأرخص عالميًا».")
md.append("")
md.append("---")
md.append("## 1. ملخص تنفيذي")
md.append("")
md.append("- **الكتالوج:** 437 SKU في 10 أسر | **الدفعة 1:** 46 SKU (أولوية P1) نُفِّذت هذا التشغيل | الدفعات 2-3 في قائمة الانتظار (تغطية صادقة: Unsearched).")
md.append("- **الميزانية:** %d إجراء بحثي (منها %d ناجحًا و%d محدود الاسترجاع) + تعديل موثق +%d للتحقق المباشر — استُنفدت كاملة وفق سجل قابل للتدقيق." % (len(ledger_actions), len(ok_actions), len(fail_actions), 22))
md.append("- **نتائج الأسعار:** 15 SKU بأدنى سعر **مشاهد مباشرة**، و21 SKU بمستوى معلن/رسمي — والبقية حالات تغطية صادقة (معلن جزئيًا).")
md.append("- **أهم اكتشافات التشغيل:** بوابة جملة Turgame موثقة حيًا؛ FazerCards رُقّيت من Lead إلى منصة مُتحققة؛ حُلّ الدور المزدوج لـReloadly (B2B API فقط)؛ أسعار يومية قياسية لبرمجيات عميقة الخصم (Office 2024 من 0,56€، Win11 Pro من 1,03€)؛ تأكيد رسمي حي: Xbox GPU $22.99، Netflix $19.99، Spotify $12.99، YouTube Premium $15.99 (+Premium Lite $8.99 جديد)، Nitro Basic $2.99.")
md.append("")
md.append("---")
md.append("## 2. ذكاء الأسعار — أدنى الأسعار المكتشفة (الأسئلة التسعة لكل SKU مختصرة في الجدول)")
md.append("")
md.append("| SKU | الهوية | أدنى سعر مباشر (USD) | البائع | الدليل | أدنى معلن/رسمي | ملاحظات |")
md.append("|---|---|---|---|---|---|---|")
rows = []
for sid in [s["sku_id"] for s in b1]:
    if sid not in PI: continue
    i = PI[sid]
    d = i["cheapest_directly_observed"]; a = i["cheapest_advertised_or_official"]
    rows.append((sid, i["identity"], d, a))
for sid, ident, d, a in rows:
    dstr = ("**%.2f**" % d["usd"]) if d else "—"
    dseller = (d.get("seller","")[:24]) if d else "—"
    dlev = "مباشر" if d else "—"
    astr = ("%.2f (%s)" % (a["usd"], a.get("seller","")[:18])) if a else "—"
    md.append("| %s | %s | %s | %s | %s | %s | %s |" % (sid, ident[:42], dstr, dseller, dlev, astr, ""))
md.append("")
md.append("> **قاعدة الدليل:** «مباشر» = صفحة مقروءة فعليًا بتاريخ الفحص. «معلن» = مقطع نتيجة بحث (Lead). مشاهدات 25/09 موسومة قِدَمًا محتملًا (يومان).")
md.append("")
md.append("---")
md.append("## 3. سجل الكيانات وتوحيد الأدوار (المرحلة 3)")
md.append("")
md.append("| الكيان | الدور الموثق | حالة التحقق | ملاحظات |")
md.append("|---|---|---|---|")
for e in ENTITIES:
    md.append("| **%s** (%s) | %s | %s | %s |" % (e["name"], e["domain"], e["role"], e["state"], e.get("notes","")[:110]))
md.append("")
md.append("---")
md.append("## 4. التفاصيل الكاملة لأهم 15 SKU (مشاهدة مباشرة)")
md.append("")
direct_sids = [sid for sid,i in PI.items() if i["cheapest_directly_observed"]]
for sid in direct_sids:
    i = PI[sid]; rec = S.get(sid, {})
    d = i["cheapest_directly_observed"]
    md.append("### %s — %s" % (sid, i["identity"]))
    md.append("")
    md.append("- **من يبيع:** %s" % d.get("seller",""))
    md.append("- **الدور:** %s" % (d.get("role") or "رسمي/أساسي"))
    md.append("- **السعر:** %s %s ≈ **%.2f USD**" % (d.get("price"), d.get("cur","USD"), d["usd"]))
    md.append("- **مستوى الدليل:** %s" % d.get("evidence",""))
    md.append("- **الحداثة:** %s" % d.get("freshness","Unknown"))
    if rec.get("official"):
        o = rec["official"]
        if o.get("price"):
            md.append("- **المرجع الرسمي:** %s = %s %s" % (o["seller"], o["price"], o.get("cur","USD")))
    extra_offers = [o for o in rec.get("offers",[]) if o is not d and o.get("usd") is not None][:3]
    if extra_offers:
        md.append("- **عروض موازية:** " + " | ".join("%s: %s %s (%s)" % (o.get("seller","?")[:20], o.get("price"), o.get("cur",""), "معلن" if "Advertised" in str(o.get("evidence","")) else "مباشر") for o in extra_offers))
    md.append("- **المجهول المتبقي:** شروط الضمان/إعادة البيع عند هذا البائع [بحاجة إلى تحقق] ما لم تُذكر")
    md.append("")
md.append("---")
md.append("## 5. سجل التدقيق (§23)")
md.append("")
md.append("**ما ثبت:** الأسعار الرسمية الحية (Xbox/Netflix/Spotify/YouTube/Discord)؛ أسعار Keyforsteam اليومية (Win11 1,03€، Office2024 0,56€، Office2021 2,44€)؛ GGSel من 749₽؛ Airalo من $4.00؛ وجود بوابتي Turgame الجملة وFazerCards؛ حل أدوار Reloadly وXbox/Microsoft.")
md.append("")
md.append("**ما لم يُحل:** أسعار منتجات Eneba اليوم (404 ×4 محاولات) → ورثت من 25/09؛ NordVPN خلف Cloudflare؛ تسعير جملة Turgame/Reloadly خلف حسابات (login-gated)؛ فئات Game Top-up/eSIM/VN تغطيتها معلنة فقط بعد نافذة حد المعدل.")
md.append("")
md.append("**التناقضات المُدارة:** (1) Eneba: عرضان موروثان vs استرجاع محدود اليوم → حُسم بالفصل الزمني. (2) Turgame Steam-20 نفد (Sold Out) بينما كان بائعًا نشطًا 25/09 → حالة توفر متغيرة موثقة. (3) أرخص معلن لWin11 ($0.53-1.22) قد يكون مفاتيح OEM/هاتفية → حُفظ منفصلًا عن Retail.")
md.append("")
md.append("**قرارات حوكمة مفتوحة (تتطلب قرار المستخدم):** بوابة Bootstrap لاعتماد أول نسخة Approved من v4.2 بعد هذا التشغيل الحي.")
md.append("")
md.append("**الميزانية:** %d/%d إجراء (C4=96 + احتياطي 24 + تعديل تحقق +22 + استرداد §19 ×2). فشل الاسترجاع ≠ عدم الوجود — 56 إجراءً فاشلًا موثقة بأسبابها (نافذة حد معدل 477)." % (len(ledger_actions), run.get("budget_amendment",{}).get("final_cap",142)))
md.append("")
md.append("---")
md.append("## 6. مجهولات معلنة")
md.append("")
md.append("1. النص الحرفي الكامل لملف v4.2 غير مضمن في Notion [بحاجة إلى تحقق].")
md.append("2. أسعار الجملة الفعلية (Turgame Wholesale / Reloadly / FazerCards B2B) خلف بوابات تسجيل [غير معروف].")
md.append("3. شروط الضمان وإعادة البيع لمعظم العروض المعلنة [بحاجة إلى تحقق].")
md.append("4. هوية Definite Play كمرآة لTurgame [بحاجة إلى تحقق].")
md.append("5. بوتات/قنوات Telegram البذور الـ29: لم تُفحص فرديًا هذا التشغيل (Budget-Limited) [بحاجة إلى تحقق].")
md.append("6. أسعار الدفعتين 2-3 (391 SKU) [Unsearched — مجهولة بالكامل حتى تشغيلها].")
md.append("")
md.append("**التوصية:** التشغيل التالي = الدفعة 2 (173 SKU P2) + فتح حسابات B2B لبوابات الجملة الثلاث الموثقة (Turgame/FazerCards/Reloadly) لاستخراج أسعار الجملة الحقيقية — فهناك يُتوقع أدنى تكلفة اقتناء فعالة.")

with open(OUT + "/sku_database.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print("MARKDOWN_OK:", os.path.getsize(OUT + "/sku_database.md"), "bytes")
json.dump({"entities": ENTITIES}, open(RD + "/entity_registry.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
