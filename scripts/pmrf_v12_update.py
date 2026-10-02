#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PMRF v1.1 -> v1.2 surgical update (G-1 RESCAN R2 results).
Per §22 re-acceptance rule: modifies, never replaces. 9 surgical edits."""
import re

P = "/home/z/my-project/download/PROJECT MASTER REFERENCE FILE.md"
s = open(P, encoding="utf-8").read()
orig = s
edits = []

def rep(old, new, tag):
    global s
    if old not in s:
        edits.append(f"FAIL: {tag}")
        return
    if s.count(old) > 1:
        edits.append(f"AMBIGUOUS({s.count(old)}): {tag}")
        return
    s = s.replace(old, new)
    edits.append(f"OK: {tag}")

TS = "2026-10-02T04:55+03:00"

# 1) header version
rep("> **LATEST VERIFIED PROJECT MASTER REFERENCE — الإصدار المرجعي الحاكم للمشروع · PMRF v1.1**",
    "> **LATEST VERIFIED PROJECT MASTER REFERENCE — الإصدار المرجعي الحاكم للمشروع · PMRF v1.2**", "header version")

# 2) version change note
rep("> **v1.1 (2026-10-02T03:25+03:00): حسم معماري لفجوة G-1** — cb_ وصلة على نفس قاعدة بيانات اللوحة الجملية التي تغذي ProdSeller (التفاصيل §14/§18).",
    "> **v1.1 (2026-10-02T03:25+03:00): حسم معماري لفجوة G-1** — cb_ وصلة على نفس قاعدة بيانات اللوحة الجملية التي تغذي ProdSeller (التفاصيل §14/§18).\n"
    f"> **v1.2 ({TS}): حسم منصيّ لـ G-1 + إعادة مسح كاملة** — «اللوحة الجملية المجهولة» = **منصة ProdSeller نفسها** (prodseller.com = ProdsellerAdmin)؛ cb_ = وصلة جملة مباشرة عليها؛ استبعاد 6 كيانات · كشف Team Sóc Lọ · 6 مزودين فيتناميين · 3 كيانات جديدة (§2/§14/§18).", "version note")

# 3) version table row
rep("| الإصدار | **v1.1** — حسم G-1 المعماري (يعدّل v1.0 ولا يستبدله) |",
    "| الإصدار | **v1.2** — حسم G-1 منصيًا + إعادة مسح R2 (يعدّل v1.1 ولا يستبدله) |", "version table")

# 4) v1.2 paragraph after v1.1 paragraph
rep("ProdSeller انحصر بعد التبديل في خط CapCut فقط (20 منتجًا ps_)، وخط Grok الجديد في cb_ ظهر متزامنًا مع إعلان teamsoclo (01/10). المتبقي UNKNOWN: الاسم التجاري للوحة/كيان cb_ (§18 G-1).",
    "ProdSeller انحصر بعد التبديل في خط CapCut فقط (20 منتجًا ps_)، وخط Grok الجديد في cb_ ظهر متزامنًا مع إعلان teamsoclo (01/10). المتبقي UNKNOWN: الاسم التجاري للوحة/كيان cb_ (§18 G-1).\n\n"
    f"**حسم v1.2 (إعادة مسح R2، {TS}):** «اللوحة الجملية» **سُمّيت**: خط CapCut الحي ps_ يطابق كتالوج ProdSeller-API (مفتاح أحمد) **20/20 ObjectId متطابق بالبايت** = قاعدة بيانات prodseller.com هي نفسها قاعدة ps_، وبالتسلسل مع أدلة v1.1 (151 ObjectId مشترك مع cb_) → **اللوحة = منصة ProdSeller نفسها** (الجذر يعرض \"ProdsellerAdmin\" + API ‏/v1 بمفاتيح psk_ · قرابة مخططات requiresEmailActivation↔requiresEmail)، و**cb_ = حساب جملة مباشر مرقّى عليها**. إعادة مسح كاملة بكتالوجات 7 كيانات (مفاتيح مصرّح بها، قراءة فقط): **صفر تطابق مع cb_** — استبعاد جماعي (ProdSeller 26 · laha 15 · AIVerseX 35 · Gemini Shop 6 · acczone 4 · DigitalCore 11). teamsoclo كُشفت = **Team Sóc Lọ** (قناة VN للجملة عبر resellers). كيانات جديدة: DigitalCore/Pixora/NevaAI. هوامش خط ps_ الحية +12%→+154%. المحاسبة: رقم 357 = أرشيف ما قبل الهجرة (319 ps_ + 37 mr_)؛ cb_ الحي = 229. المتبقي: الهوية البشرية لمشغّل المنصة (يتطلب G-7).", "v1.2 paragraph")

# 5) metadata table v1.2 row
rep("| **تحديث v1.1** | Execution = Reference Update = **2026-10-02T03:25+03:00** (مسح G-1 الجنائي) | يعدّل v1.0 وفق قاعدة إعادة الاعتماد §22/§23 |",
    "| **تحديث v1.1** | Execution = Reference Update = **2026-10-02T03:25+03:00** (مسح G-1 الجنائي) | يعدّل v1.0 وفق قاعدة إعادة الاعتماد §22/§23 |\n"
    f"| **تحديث v1.2** | Execution = Reference Update = **{TS}** (إعادة مسح G-1 R2 + كتالوجات 7 كيانات بقراءة مصرّح بها) | يعدّل v1.1 وفق قاعدة إعادة الاعتماد §22/§23 |", "metadata v1.2 row")

# 6) assets row
rep("| `research/g1_cb_live_catalog_20261002.json` + `g1_cb_scan_20261002.json` + `g1_cb_findings_20261002.json` | مسح G-1 الجنائي (v1.1): كتالوج حي خام 282 + تحليل القوالب/طوابع Mongo/البصمات/التعاشق + النتائج الموحدة | — | AVAILABLE (NEW v1.1) |",
    "| `research/g1_cb_live_catalog_20261002.json` + `g1_cb_scan_20261002.json` + `g1_cb_findings_20261002.json` | مسح G-1 الجنائي (v1.1): كتالوج حي خام 282 + تحليل القوالب/طوابع Mongo/البصمات/التعاشق + النتائج الموحدة | — | AVAILABLE (NEW v1.1) |\n"
    "| `research/g1_rescan_raw[1-6]_20261002.json` + `g1_rescan_analysis_20261002.json` + `g1_digitalcore_match_20261002.json` | إعادة مسح R2 (v1.2): 33 قراءة خام (SV حي + 7 كيانات + قناتا g12/Team Sóc Lọ) + التحليل الموحد + مطابقة DigitalCore | — | AVAILABLE (NEW v1.2) |", "assets row")

# 7) cb_ definition (§14) append platform verdict
rep("إذن **cb_ = وصلة/حساب جديد أغنى مخططًا (categoryEmoji · requiresEmail · تصنيفات مهيكلة) على نفس اللوحة الجملية الفيتنامية** التي كان ProdSeller نافذة عليها. 32 منتجًا جديدًا بينها خط Grok ×5 متزامن مع إعلان teamsoclo (01/10) ووصف Codex محدَّث بموديلات 02/10 الأربعة. الاسم التجاري = UNKNOWN (§18 G-1).",
    "إذن **cb_ = وصلة/حساب جديد أغنى مخططًا (categoryEmoji · requiresEmail · تصنيفات مهيكلة) على نفس اللوحة الجملية الفيتنامية** التي كان ProdSeller نافذة عليها. 32 منتجًا جديدًا بينها خط Grok ×5 متزامن مع إعلان teamsoclo (01/10) ووصف Codex محدَّث بموديلات 02/10 الأربعة. **حسم v1.2: اللوحة = منصة ProdSeller نفسها (prodseller.com — ProdsellerAdmin؛ دليل F1: خط CapCut ps_ الحي يطابق ProdSeller-API بـ20/20 ObjectId + استبعاد 6 منصات بديلة بفضاءات معرّفات مختلفة)؛ cb_ = حساب جملة مباشر عليها.** المتقيّد: الهوية البشرية للمشغّل (§18 G-1).", "cb_ definition")

# 8) G-1 gap row
rep("| G-1 | **هوية cb_** | المورد الجديد المسيطر (81%) على كتالوج StackVault | **حُسمت معماريًا في v1.1 (03:25+03)**: نفس قاعدة بيانات اللوحة الجملية الفيتنامية (151/197 ObjectId متطابق + 8 بصمات خادم Mongo مشتركة + تعاشق عدادات 200% = مساران منذ يونيو)؛ cb_ = وصلة/حساب جديد أغنى مخططًا (categoryEmoji · requiresEmail · تصنيفات مهيكلة · بلا costPrice)؛ ProdSeller = نافذة أخرى على نفس اللوحة وبقي ps_ لخط CapCut فقط؛ اقتران تشغيلي وثيق مع teamsoclo (خط Grok متزامن مع إعلان 01/10 + أوصاف Codex محدثة لحظيًا) | حرج → متوسط: البنية مفهومة، المتبقي الاسم التجاري | معماريًا VERIFIED؛ الاسم UNKNOWN | تحديد اسم اللوحة (رصد قنوات VN · فحص API اللوحة عند ظهوره · مطابقة قوائم Gmail/FB/LART مع أسماء لوحات معروفة) · شراء اختباري عند التفعيل | **PARTIALLY_RESOLVED (v1.1)** |",
    "| G-1 | **هوية cb_** | المورد الجديد المسيطر (81%) على كتالوج StackVault | **حُسمت منصيًا في v1.2 (إعادة مسح R2 04:55+03)**: «اللوحة الجملية» = **منصة ProdSeller نفسها** (prodseller.com = ProdsellerAdmin + API /v1 · psk_) — الدليل الحاسم F1: خط CapCut ps_ الحي (20) يطابق كتالوج ProdSeller-API (مفتاح أحمد) **20/20 ObjectId بالبايت**، وبالتسلسل مع 151 ObjectId مشترك مع cb_ (v1.1) → MongoDB واحدة للمنصة/ps_/cb_؛ cb_ = **حساب جملة مباشر مرقّى على المنصة** (مخطط أغنى · بلا costPrice)؛ استبعاد جماعي: 6 كيانات مسوحة بكتالوجاتها = صفر تطابق مع cb_ (ProdSeller 26 · laha 15 · AIVerseX 35 · Gemini Shop 6 · acczone 4 · DigitalCore 11)؛ محاسبة 357: أرشيف ما قبل الهجرة (319 ps_ + 37 mr_) ← 153 هاجرت cb_ + 16 بقيت + 62 شُذّبت + 29 جديدة؛ المنبع الأعلى = Team Sóc Lọ/teamsoclo (بوابة New API) | حرج → **منخفض**: الهوية المنصية محسومة | **RESOLVED (منصةً)** — cb_ = وصلة مباشرة على منصة ProdSeller | المتبقي (G-1a): الهوية البشرية لمشغّل المنصة — شراء اختباري (G-7) أو WHOIS/تحليل تاريخي · تمييز مستأجري المنصة بمفاتيح AISUBSID/HitMeow/Evo_Era عند توفرها | **RESOLVED-PLATFORM (v1.2)** |", "G-1 row")

# 9) changelog row
rep("| **PMRF v1.1** | **2026-10-02T03:25+03:00** | حسم G-1 المعماري (مسح جنائي) | cb_ = وصلة على نفس قاعدة بيانات اللوحة الجملية (151 ObjectId متطابق · 8 بصمات خادم · تعاشق عدادات 200% · مساران منذ يونيو) · ProdSeller = نافذة على اللوحة (بقي لخط CapCut) · اقتران cb_↔teamsoclo (خط Grok متزامن 01/10) · أسعار Grok ×5 · G-1 → PARTIALLY_RESOLVED · ACCEPTED |",
    "| **PMRF v1.1** | **2026-10-02T03:25+03:00** | حسم G-1 المعماري (مسح جنائي) | cb_ = وصلة على نفس قاعدة بيانات اللوحة الجملية (151 ObjectId متطابق · 8 بصمات خادم · تعاشق عدادات 200% · مساران منذ يونيو) · ProdSeller = نافذة على اللوحة (بقي لخط CapCut) · اقتران cb_↔teamsoclo (خط Grok متزامن 01/10) · أسعار Grok ×5 · G-1 → PARTIALLY_RESOLVED · ACCEPTED |\n"
    f"| **PMRF v1.2** | **{TS}** | حسم G-1 منصيًا (إعادة مسح R2 بامر المستخدم + مفاتيح أحمد) | اللوحة = منصة ProdSeller (F1: 20/20 ObjectId · استبعاد 6 كيانات · ProdsellerAdmin) · cb_ = حساب جملة مباشر · G-1 → RESOLVED-PLATFORM · محاسبة 357 كاملة (cb_ الحي = 229) · teamsoclo = Team Sóc Lọ · مزودو VN: bddevlab/vibi/phh/dongvanfb/mailtemp/GPM · كيانات جديدة: DigitalCore/Pixora/NevaAI · هوامش ps_ الحية +12%→+154% · gemini12pro = جدار إعلانات مدفوعة | ", "changelog v1.2 row")

open(P, "w", encoding="utf-8").write(s)
print("EDITS:")
for e in edits: print(" ", e)
print(f"\nsize: {len(orig)} -> {len(s)} bytes | delta: +{len(s)-len(orig)}")
print(f"lines: {orig.count(chr(10))+1} -> {s.count(chr(10))+1}")
