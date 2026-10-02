#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PMRF v3.2 -> v3.3 surgical layer (ACZ — Acczone key audit, C13 resolution).
Steps: sanity -> archive v3.2 -> surgical line-based replacements (documented) ->
pre-seal hash -> new §48.3 seal -> final hash -> worklog append (Task ID: ACZ)."""
import hashlib, os, shutil, datetime

PMRF = "/home/z/my-project/download/PROJECT MASTER REFERENCE FILE.md"
ARCH = "/home/z/my-project/download/PMRF_ARCHIVE/PROJECT MASTER REFERENCE FILE_v3.2_2026-10-02.md"
WL = "/home/z/my-project/worklog.md"
TZ = datetime.timezone(datetime.timedelta(hours=3))
TS = datetime.datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+03:00")
AUDIT_TS = "2026-10-02T15:06:50+03:00"  # live audit execution timestamp (acz_audit.py)

def sha(b): return hashlib.sha256(b).hexdigest()
def rb(p): return open(p, "rb").read()

# ---------- 0) sanity: evidence files exist ----------
for p in ["/home/z/my-project/research/acz_audit_raw_20261002.json",
          "/home/z/my-project/research/acz_analysis_20261002.json",
          "/home/z/my-project/download/ACZ_تقرير_تدقيق_مفتاح_Acczone_2026-10-02.md",
          "/home/z/my-project/research/g1_rescan_raw3_20261002.json",
          "/home/z/my-project/research/sv_master_catalog_consolidated_20261002.json"]:
    assert os.path.exists(p), "missing evidence: " + p
print("[sanity] all evidence files present")

# ---------- 1) archive v3.2 ----------
shutil.copy2(PMRF, ARCH)
v32bytes = len(rb(ARCH)); v32sha = sha(rb(ARCH)); v32sha16 = v32sha[:16]
v32lines = len(open(ARCH, encoding="utf-8").read().splitlines())
print("[archive] v3.2 ->", ARCH, "| sha", v32sha16 + "…", "|", v32lines, "lines |", v32bytes, "bytes")

lines = open(PMRF, encoding="utf-8").read().splitlines()
n0 = len(lines)

def rep_line(marker, new_line, tag):
    global lines
    hits = [i for i, l in enumerate(lines) if marker in l]
    assert len(hits) == 1, "[%s] marker hits=%d: %r" % (tag, len(hits), marker[:60])
    lines[hits[0]] = new_line
    print("[ok] %s (line %d)" % (tag, hits[0] + 1))

def ins_after(marker, new_lines, tag):
    global lines
    hits = [i for i, l in enumerate(lines) if marker in l]
    assert len(hits) == 1, "[%s] marker hits=%d" % (tag, len(hits))
    lines[hits[0] + 1:hits[0] + 1] = new_lines
    print("[ok] %s (after line %d, +%d)" % (tag, hits[0] + 1, len(new_lines)))

def ins_before(marker, new_lines, tag):
    global lines
    hits = [i for i, l in enumerate(lines) if marker in l]
    assert len(hits) == 1, "[%s] marker hits=%d" % (tag, len(hits))
    lines[hits[0]:hits[0]] = new_lines
    print("[ok] %s (before line %d, +%d)" % (tag, hits[0] + 1, len(new_lines)))

# ---------- 2) surgical replacements ----------
rep_line("| الإصدار | **v3.2**",
    "| الإصدار | **v3.3** — طبقة ACZ فوق v3.2 (تدقيق مفتاح Acczone + إغلاق C13؛ تحديث جراحي بلا إعادة بناء؛ v3.2 مؤرشف كاملًا بالبصمة) |", "R1-version")
rep_line("| المرجع السابق | PMRF v3.1",
    "| المرجع السابق | PMRF v3.2 — مؤرشف: `download/PMRF_ARCHIVE/PROJECT MASTER REFERENCE FILE_v3.2_2026-10-02.md` (%s سطرًا · %s بايتًا · sha256 أول 16: %s) |" % (f"{v32lines:,}", f"{v32bytes:,}", v32sha16), "R2-prevref")
rep_line("| سلسلة الإصدارات المحفوظة |",
    "| سلسلة الإصدارات المحفوظة | v1.5 (613 سطرًا · sha 486a2502e4ab4a3c) + v2.0 (701 سطرًا · sha e58b326e00375dd9) + v3.0 (1,189 سطرًا · sha 1bfcbaf94f7b2e6d) + v3.1 (1,213 سطرًا · sha 269fd4972bf37b11) + v3.2 (%s سطرًا · sha %s) — كلها في PMRF_ARCHIVE/ |" % (f"{v32lines:,}", v32sha16), "R3-lineage")
rep_line("| Previous Version | PMRF v3.1",
    "| Previous Version | PMRF v3.2 (48 قسمًا · %s سطرًا · sha %s) — مؤرشف كاملًا |" % (f"{v32lines:,}", v32sha16), "R4-prevver")
rep_line("| Current Version | **PMRF v3.2**",
    "| Current Version | **PMRF v3.3** — 48 قسمًا (طبقة ACZ — تحديث جراحي) |", "R5-curver")
ins_after("| **شاهد طبقة v3.2 (C15+G-14)**",
    ["| **شاهد طبقة v3.3 (ACZ)** | " + AUDIT_TS + " — تدقيق Acczone المصادق بالمفتاح المسلَّم (G-13 بند 1): مفتاح صالح (HTTP 200 بحساب كامل) + اختبارا ضبط (مفتاح خاطئ → 400 Invalid · غياب → 400 Missing) + كتالوج 4 خدمات بتحركات حية (استهلاك 116 وحدة/11.3س + قطة Apple Music ‎-66.7%) + سجل تفعيلات فارغ — الأدلة: research/acz_audit_raw_20261002.json + acz_analysis_20261002.json · التقرير: download/ACZ_تقرير_تدقيق_مفتاح_Acczone_2026-10-02.md |"], "R6-witness")
rep_line("| أحدث شاهد بيانات حي |",
    "| أحدث شاهد بيانات حي | research/acz_audit_raw_20261002.json (02/10 15:06:50+03:00 — تدقيق Acczone المصادق) + research/pmrf_v3_live_update_20261002.json (07:39:16+03:00) |", "R7-livewitness")
rep_line("Acczone (عنقود متكامل — المفتاح المبتور G-13)",
    "Acczone (عنقود متكامل — المفتاح سليم وشغال: تدقيق ACZ v3.3)", "R8-layer-d")
rep_line("| المتجر/التجزئة (StackVault · Evo Era · البوتات) |",
    "| المتجر/التجزئة (StackVault · Evo Era · البوتات) | يجمع من الطبقتين ويبيع بضمان متدرج | 30–100%+ فوق كلفة الاقتناء — الربحية تتحدد بمعدل الموت/الاستبدال (غير معلن) · **أوسع موثق: Apple Music 5M من $0.10 (Acczone API) إلى $2.35 (SV خط mr_) = ×23.5 (v3.3)** |", "R9-retail-margin")
rep_line("Gemini 18m $0.40 · جملة $0.39 · Acczone «أكبر مزود»",
    "Gemini 18m $0.40 · جملة $0.39 · Acczone API: 4 SKUs هندية — Apple Music $0.10 · Adobe Express $0.30 · Duolingo Super $0.35 · Gemini $0.69 (تدقيق v3.3؛ ادعاء «أكبر مزود» ذاتي تسويقي لا يسنده اتساع الـAPI)", "R10-scmap")
ins_after("| StackVault (تجزئة) | Go 1M / Plus 1M 3D / Plus full | $3.66 / $8.79 / $11.79-12.02 | **v3.0 / v1.0** |",
    ["| Acczone API 🇮🇳 | رباعية التفعيل الهندي: Apple Music 5M / Adobe Express 12M / Duolingo Super 12M / Gemini 18M | $0.10 / $0.30 / $0.35 / $0.69 | **v3.3 — 02/10 15:07 (شاهد مصادق: أرخص مصدر موثق لثلاثتها)** |"], "R11-anchor-row")
ins_after("- Plus 2HW: ±22% خلال يوم واحد",
    ["- **v3.3 (شاهد Acczone المصادق 02/10):** Apple Music 5M: ‏$0.30→$0.10 (-66.7%) خلال يوم واحد · تدوير خدمة Gemini 18M: ‏$0.40 (09-01)→$0.69 (09-30 = +72.5% مع تغيير مفتاح الخدمة gemini→geminilive) · استهلاك مخزون 116 وحدة خلال 11.3 ساعة (Gemini ‏-62 · Duolingo ‏-50)."], "R12-volatility")
rep_line("| C13 | **جديد v3.0:** مفتاح Acczone مبتور",
    "| C13 | **جديد v3.0 → RESOLVED (v3.3):** «مفتاح Acczone المبتور» — تشخيص خاطئ: المفتاح سليم كامل الصلاحية؛ العلة كانت اسم معامل الاستيثاق في جولة الصباح (?key= وترويسات X-API-Key/Bearer بدل ?apikey= الموثقة → Missing API Key) — بالمعامل الصحيح HTTP 200 فورًا + اختبار ضبط (مفتاح خاطئ → 400 Invalid API Key) · المتبقي من البند الأصلي: مفاتيح AISUBSID/Evo_Era (لم تُسلَّم بعد) | بيانات | **RESOLVED جزئيًا (v3.3)** — التفاصيل: تقرير ACZ §3 |", "R13-c13")
rep_line("| C11 | الأسطح ذات المفاتيح لم تُعاد سبرها",
    "| C11 | الأسطح ذات المفاتيح لم تُعاد سبرها — آخر شاهد R3 (06:40+03) — **استثناء v3.3:** سطح Acczone أُعيد سبره مصادقًا (15:06+03، المفتاح المسلَّم) | منهجي-مقصود | ساري (باستثناء Acczone — v3.3) |", "R14-c11")
rep_line("| **G-13** | **جديد v3.0:** استكمال مدخلات المستخدم المعلقة",
    "| **G-13** | **جديد v3.0:** استكمال مدخلات المستخدم المعلقة | ~~مفتاح Acczone~~ **(سُلِّم 02/10 15:00+03 — v3.3 وشغال: تدقيق كامل)** · مفاتيح AISUBSID/Evo_Era · NOTION_TOKEN **(سُلِّم 02/10 — v3.1)** · رابط نشر المتجر | OPEN (بيد المستخدم) — **2 من 4 متبقية** | تسليمها عند التوفر |", "R15-g13")
ins_after("| **G-14** | مصالحة محتوى دلتا Notion",
    ["| **G-15** | **جديد v3.3:** العلاقة التوريدية Acczone↔خط mr_/Evo_Era — مطابقة قالبية شبه كاملة لوصف Apple Music 5M (ضمان شهر · رابط 5 أشهر · منطقة هندية + VPN · ‏UPI/بطاقة على المشتري · حجز 24س — متطابقة دلاليًا) بين كتالوج Acczone ($0.10) وmr_apple_music_5m في StackVault ($2.35 = ×23.5) | هل Evo_Era يشتري من Acczone أم يشتريان من بركة تفعيل هندية واحدة؟ | OPEN | شراء عينات مقارنة (يتطلب قرار المستخدم — G-7) أو مطابقة أكواد تسليم |"], "R16-g15")
rep_line("2. مفتاح Acczone المبتور (C13/G-13) — بيد المستخدم.",
    "2. ~~مفتاح Acczone المبتور~~ **RESOLVED (v3.3):** المفتاح سليم — العلة كانت اسم معامل الاستيثاق (?apikey= لا ?key=) لا بتْر المفتاح (C13).", "R17-debt2")
rep_line("· أسطح المفاتيح (شاهد R3).",
    "· أسطح المفاتيح (شاهد R3 — ما عدا Acczone: شاهد مصادق v3.3 15:06+03).", "R18-unverified")
rep_line("G-13 (المتبقي: Acczone/AISUBSID/Evo_Era/رابط النشر)",
    "G-13 (المتبقي بعد v3.3: AISUBSID/Evo_Era/رابط النشر — Acczone أُغلق بالتسليم والتدقيق)", "R19-missing")
ins_after("| **v3.2** | **02/10 (يُختم أدناه)**",
    ["| **v3.3** | **02/10 (يُختم أدناه)** | **طبقة ACZ (تحديث جراحي بلا إعادة بناء)** | إغلاق C13 (مفتاح Acczone سليم — العلة اسم معامل) + تدقيق Acczone المصادق الكامل (هوية الحساب الحلقة الثامنة 7334478984 · سجل فارغ · رباعية هندية $0.10–0.69 · هامش ×23.5 أوسع موثق) + G-15 جديدة — بلا تغيير أي حسم معرفي قائم آخر |"], "R20-vhist")
ins_before("## 47.",
    ["### 46.8 تحقق طبقة v3.3 (ACZ — فوق بوابات v3.0/v3.1/v3.2 السابقة)",
     "",
     "- **اكتمال أدلة C13:** المفتاح المسلَّم اختُبر مباشرة (HTTP 200 بحساب كامل) + اختبارا ضبط فاصلان (مفتاح خاطئ → 400 Invalid · غياب → 400 Missing) — الحكم RESOLVED مبني على استجابات حية موثقة في research/acz_audit_raw_20261002.json، وجذر الخلل الصباحي (اسم المعامل ?apikey=) موثق بالتقابل مع نص الوثائق الرسمية المحفوظ خامًا منذ الصباح.",
     "- **اكتمال أدلة التدقيق:** 6 قراءات مصادَقة (docs · openapi · balance · wrong-key · services · history) بحد المعدل المُحترم (2.6ث) + مقارنة زمنية بلقطتين (03:47 و15:06 +03) + مطابقة أسعار وأوصاف ضد الكتالوج الموحد (sv_master_catalog) — كل رقم في طبقة ACZ مسند إلى شاهد ملف.",
     "- **فحص التعارض:** لا تغيير في أي حسم معرفي قائم؛ إثراء فقط (مراسي سعرية جديدة لثلاث عائلات + اكتمال سلسلة الحيازة بالحلقة الثامنة + G-15 جديدة مفتوحة).",
     "- **الخلاصة:** طبقة v3.3 صالحة للختم فوق v3.2 بلا إعادة بناء.",
     ""], "R21-468")
rep_line("«PMRF v3.2 §<القسم>»",
    "- **قاعدة الاستشهاد:** «PMRF v3.3 §<القسم>» هو المرجع الموحد بعد هذا الإصدار (v3.2 مؤرشف بالبصمة كاملة).", "R22-cite")

# ---------- 3) seal ----------
seal_idx = [i for i, l in enumerate(lines) if l.startswith("### 48.3 Release Seal")]
assert len(seal_idx) == 1, "seal marker hits=%d" % len(seal_idx)
pre = lines[:seal_idx[0]]
pre_text = "\n".join(pre) + "\n"
pre_sha = sha(pre_text.encode("utf-8"))
pre_bytes = len(pre_text.encode("utf-8")); pre_lines_n = len(pre)
seal = ["### 48.3 Release Seal", "",
        "| الحقل | القيمة |", "|---|---|",
        "| Filename | PROJECT MASTER REFERENCE FILE.md |",
        "| Release version | **PMRF v3.3** (طبقة ACZ فوق v3.2) |",
        "| Generation timestamp | %s (التحديث الجراحي بعد اكتمال تدقيق Acczone المصادق وإغلاق C13) |" % TS,
        "| Verification timestamp | %s (اكتمال الجولات + اتساق §46.8) |" % TS,
        "| SHA-256 (المحتوى قبل هذا الختم) | `%s` |" % pre_sha,
        "| حجم المحتوى المختوم | %s bytes (%s سطرًا) |" % (f"{pre_bytes:,}", f"{pre_lines_n:,}"),
        "| Canonical status | **CANONICAL PROJECT MASTER REFERENCE** (ميراث قرار v3.0 §46.5 + تحقق طبقات v3.1 §46.6 وv3.2 §46.7 وv3.3 §46.8 — لا تغيير في أي حسم معرفي قائم) |",
        "| الأرشيف المحفوظ | v1.5 (sha 486a2502e4ab4a3c…) + v2.0 (sha e58b326e00375dd9…) + v3.0 (sha 1bfcbaf94f7b2e6d…) + v3.1 (sha 269fd4972bf37b11…) + **v3.2 (sha %s…)** في PMRF_ARCHIVE/ |" % v32sha16,
        "",
        "**قاعدة الختم:** هذا الختم يغطي المحتوى السابق له حصرًا. أي تعديل لاحق يستوجب إصدارًا جديدًا وختمًا جديدًا — لا يُحدَّث هذا الملف موضعيًا بعد الختم."]
final = pre + seal
open(PMRF, "w", encoding="utf-8").write("\n".join(final) + "\n")
final_sha = sha(rb(PMRF)); final_lines = len(final)
print("[seal] pre-seal sha %s… | content %s bytes / %s lines" % (pre_sha[:16], f"{pre_bytes:,}", f"{pre_lines_n:,}"))
print("[done] PMRF v3.3 written | final sha %s… | %s lines (was %s)" % (final_sha[:16], final_lines, n0))

# ---------- 4) worklog append ----------
wl = """
---
Task ID: ACZ
Agent: Main (Super Z)
Task: تسليم المستخدم مفتاح Acczone + رابط الوثائق (G-13 بند 1) — التسليم الثالث للمفاتيح: تدقيق API مصادق قراءة فقط + إغلاق C13 + طبقة PMRF v3.3

Work Log:
- استُلم المفتاح (بصمة UDEWFT8S…HMcI — 43 محرفًا) + رابط الوثائق api.acczone.xyz
- قُرئت الوثائق الرسمية المحفوظة خامًا (29,298 بايت من جولة الصباح): الاستيثاق ?apikey= كمعامل استعلام وحده — جذر خطأ الجولة الصباحية (?key=/ترويسات → Missing API Key → تشخيص خاطئ «مفتاح مبتور»)
- كُتب ونُفِّذ scripts/acz_audit.py (قراءة فقط · حد معدل محترم 2.6ث): getBalance ‏200 (حساب كامل) + اختبار ضبط مفتاح خاطئ 400 Invalid + getServices ‏200 + getHistory ‏[] (فارغ) + docs/openapi مطابقتان بالبايت — الأدلة: research/acz_audit_raw_20261002.json
- كُتب ونُفِّذ scripts/acz_analyze.py: الهوية (user_id 7334478984/Z555Mm/A7MED = الحلقة الثامنة لسلسلة الحيازة الواحدة · حساب أُنشئ 24/09 23:07 · رصيد $0) · السجل فارغ (صفر تفعيلات) · الكتالوج 4 خدمات (رباعية التفعيل الهندي) بتحركات حية: قطة Apple Music $0.30→$0.10 (-66.7% داخل اليوم) + استهلاك 116 وحدة/11.3س (Gemini ‏-62 · Duolingo ‏-50) + تدوير خدمة Gemini $0.40(09-01)→$0.69(09-30 = +72.5%) — الأدلة: research/acz_analysis_20261002.json
- المطابقة البيئية: Apple Music 5M سلّم كامل (Acczone $0.10 → Gemini Shop لوحة $0.40 → AiVerseX $0.85 → SV تجزئة mr_ $2.35 = ×23.5 أوسع هامش موثق في المشروع) + مطابقة قالبية شبه كاملة لوصف Apple Music بين Acczone وmr_apple_music_5m (SV) → G-15 جديدة (Acczone↔خط mr_/Evo_Era) · Acczone أرخص مصدر موثق لـApple Music/Adobe Express ($0.30)/Duolingo Super ($0.35) وغير تنافسي في Gemini ($0.69 مقابل $0.40 لدى ProdSeller وGemini Shop)
- أُنتج download/ACZ_تقرير_تدقيق_مفتاح_Acczone_2026-10-02.md (11 قسمًا)
- طبقة PMRF v3.3 الجراحية (22 استبدالًا/إدراجًا موثقًا): أرشفة v3.2 (sha %s) → §1/§2 (شاهد ACZ)/§8 طبقة د/§9.3 هامش ×23.5/§10 خريطة التوريد/§13 صف مراسي Acczone/§16.4 تقلب جديد/§28 (C13 RESOLVED + C11 استثناء)/§30 (G-13 → 2 من 4 + G-15 جديدة)/§38.3/§43/§44/§45 جدول الإصدارات/§46.8 جديد/§47/§48 → ختم جديد

Stage Summary:
- المخرجات: PMRF v3.3 (مختوم · CANONICAL مواريث) + تقرير ACZ + دليلان خام/تحليل + سكربتان قابلان لإعادة التشغيل + أرشيف v3.2 كامل بالبصمة
- الإغلاقات: C13 (RESOLVED — المفتاح سليم؛ العلة اسم معامل الاستيثاق لا البتر) · G-13 بند Acczone (مغلق — 2 من 4 متبقية) · C11 (استثناء موثق)
- جديد موثق: رباعية التفعيل الهندي في Acczone بأسعار قاعية لثلاث عائلات · هامش ×23.5 (Apple Music) يتصدر جدول الهوامش · G-15 (علاقة Acczone↔mr_/Evo_Era) · تدوير خدمة Gemini +72.5%
- بقي بيد المستخدم: مفاتيح AISUBSID/Evo_Era · رابط نشر المتجر (G-13)
""" % v32sha16
open(WL, "a", encoding="utf-8").write(wl)
print("[worklog] appended Task ID: ACZ")
