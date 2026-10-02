#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PMRF v3.1 -> v3.2 surgical layer (C15 write test + G-14 Notion delta reconciliation).
Steps: sanity -> archive v3.1 -> surgical line-based replacements (documented) ->
pre-seal hash -> new §48.3 seal -> final hash -> worklog append (Task ID: C15-G14)."""
import hashlib, os, shutil, datetime

PMRF = "/home/z/my-project/download/PROJECT MASTER REFERENCE FILE.md"
ARCH = "/home/z/my-project/download/PMRF_ARCHIVE/PROJECT MASTER REFERENCE FILE_v3.1_2026-10-02.md"
WL = "/home/z/my-project/worklog.md"
TZ = datetime.timezone(datetime.timedelta(hours=3))
TS = datetime.datetime.now(TZ).strftime("%Y-%m-%dT%H:%M:%S+03:00")

def sha(b): return hashlib.sha256(b).hexdigest()
def rb(p): return open(p, "rb").read()

# ---------- 0) sanity: evidence files exist ----------
for p in ["/home/z/my-project/research/c15_write_test_2026-10-02.json",
          "/home/z/my-project/research/c15_write_test_2026-10-02_run2.json",
          "/home/z/my-project/download/G14_تقرير_مصالحة_دلتا_Notion_2026-10-02.md",
          "/home/z/my-project/research/g14_2026-10-02/ref_hakim_blocks_edited_since_2709.json",
          "/home/z/my-project/research/g14_2026-10-02/ref_hakim_price_anchor_blocks.json"]:
    assert os.path.exists(p), "missing evidence: " + p
print("[sanity] all evidence files present")

# ---------- 1) archive v3.1 ----------
shutil.copy2(PMRF, ARCH)
v31bytes = len(rb(ARCH)); v31sha = sha(rb(ARCH)); v31sha16 = v31sha[:16]
v31lines = len(open(ARCH, encoding="utf-8").read().splitlines())
print("[archive] v3.1 ->", ARCH, "| sha", v31sha16 + "…", "|", v31lines, "lines |", v31bytes, "bytes")

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
rep_line("| الإصدار | **v3.1**",
    "| الإصدار | **v3.2** — طبقة C15+G-14 فوق v3.1 (تحديث جراحي بلا إعادة بناء؛ v3.1 مؤرشف كاملًا بالبصمة) |", "R1-version")
rep_line("| المرجع السابق | PMRF v3.0",
    "| المرجع السابق | PMRF v3.1 — مؤرشف: `download/PMRF_ARCHIVE/PROJECT MASTER REFERENCE FILE_v3.1_2026-10-02.md` (%s سطرًا · %s بايتًا · sha256 أول 16: %s) |" % (f"{v31lines:,}", f"{v31bytes:,}", v31sha16), "R2-prevref")
rep_line("| سلسلة الإصدارات المحفوظة |",
    "| سلسلة الإصدارات المحفوظة | v1.5 (613 سطرًا · sha 486a2502e4ab4a3c) + v2.0 (701 سطرًا · sha e58b326e00375dd9) + v3.0 (1,189 سطرًا · sha 1bfcbaf94f7b2e6d) + v3.1 (%s سطرًا · sha %s) — كلها في PMRF_ARCHIVE/ |" % (f"{v31lines:,}", v31sha16), "R3-lineage")
rep_line("| Previous Version | PMRF v3.0",
    "| Previous Version | PMRF v3.1 (48 قسمًا · %s سطرًا · sha %s) — مؤرشف كاملًا |" % (f"{v31lines:,}", v31sha16), "R4-prevver")
rep_line("| Current Version | **PMRF v3.1**",
    "| Current Version | **PMRF v3.2** — 48 قسمًا (طبقة C15+G-14 — تحديث جراحي) |", "R5-curver")
ins_after("شاهد طبقة v3.1 (تدوير D5)",
    ["| **شاهد طبقة v3.2 (C15+G-14)** | %s — اختبار كتابة WRITE_FULL (جولتان موثقتان · أدلة research/c15_write_test_2026-10-02*.json) + فحص G-14 التفصيلي (ثلاثية بحوث موردي 02/10 + مرجع حاكم 3,243 كتلة بعزل طوابع الكتل) — التقرير: download/G14_تقرير_مصالحة_دلتا_Notion_2026-10-02.md |" % TS], "R6-witness")
rep_line("| C15 | **جديد v3.1:**",
    "| C15 | قدرة كتابة التوكن الجديد → **RESOLVED (v3.2): WRITE_FULL** — مثبتة باختبار فعلي بتعليمات المستخدم الصريحة: إنشاء صفحة + إلحاق كتل (PATCH /blocks/{id}/children) + تحديث كتلة + تحديث خصائص + أرشفة، كلها HTTP 200 بتحقق قراءة عكسي (جولتان؛ ج1 عيب منهجي POST/PATCH وُثق وصُحح). الأثر المتبقي موثق: صفحتا اختبار في سلة المحذوفات + طابع تحرير المرجع الحاكم 27/09T16:33Z→02/10T09:57Z بلا أي تغيير محتوى | بيانات/أمنية | **RESOLVED (v3.2)** |", "R7-c15")
rep_line("| R7 |",
    "| R7 | توكن Notion بقدرة كتابة — التدوير بيد المستخدم | أمنية | موثق | **التدوير نُفِّذ (v3.1) + قدرة كتابة التوكن الجديد مثبتة كاملة WRITE_FULL (C15 — v3.2)** — انضباطية المفتاح الحساس سارية للتوكن الجديد |", "R8-r7")
rep_line("| **G-12** |",
    "| **G-12** | مصالحة بيانات الأسعار بين الطبقة التأسيسية (25/09) ونتائج المشروع → **ANSWERED (v3.2 عبر G-14):** طوابع الكتل تحسم الاتجاه — مراسي الأسعار الرسمية (ChatGPT $20 · Spotify $12.99 · Netflix $8.99/$19.99) وسلة الأسواق (Eneba/Turgame) كتلٌ 25/09 تسبق سلاسل المشروع (26-27/09)؛ سلّم الكلفة 2.80/10.67/17.14 ومعادلة ×1.2 كتلٌ 27/09 تدفقت من المشروع إلى Notion؛ القيم متسقة (5/6 مراسي عينة مثبتة في قاعدة SKU) — صفر تعارض | **ANSWERED (v3.2)** | متبقٍ اختياري: مقارنة سلة SKU بندًا-بندًا |", "R9-g12")
rep_line("| **G-14** |",
    "| **G-14** | مصالحة محتوى دلتا Notion مع طبقات المعرفة القائمة → **ANSWERED (v3.2):** فحص تفصيلي كامل — ثلاثية 02/10 (05:32+03) طبقة تخطيط DECLARED لمحرك Provider Intelligence فوق ~300 بوت مورد؛ مزودوها الأربعة (PremiKeyBot/canboso · DCoreStoreBot/digitalcore.top · AIXpress/aixpress.shop · RichAIStoreBot/cgpt-active.pro) كيانات معروفة فحصها G-1 R3 بعد 68 دقيقة بأدلة OBSERVED؛ المرجع الحاكم 3,243 كتلة = 2,528 (25/09) + 554 (26/09) + 161 (27/09 = طبقة مزامنة MEC) وصفر تحرير بعدها؛ مفارقة زمنية واحدة موثقة (aiversehub.store متقادمة مقابل aixpress.shop في R3) — **صفر تعارض معرفي** | **ANSWERED (v3.2)** | التفاصيل: §34.2c + تقرير G-14 |", "R10-g14")
rep_line("6. هل تتطابق أسعار الطبقة التأسيسية",
    "6. هل تتطابق أسعار الطبقة التأسيسية (25/09) مع سلاسل المشروع أم تسبقها كخط أساس؟ (G-12) — **ANSWERED (v3.2):** تسبقها كخط أساس (طوابع الكتل) والقيم متسقة عند نقاط التماس المفحوصة.", "R11-q6")
rep_line("8. هل يمتلك التوكن الجديد قدرة كتابة؟",
    "8. هل يمتلك التوكن الجديد قدرة كتابة؟ (C15) — **ANSWERED (v3.2): WRITE_FULL** (اختبار فعلي موثق بجولتين + تنظيف كامل).", "R12-q8")

ins_before("### 34.3 ",
    ["### 34.2c طبقة v3.2 — مصالحة دلتا Notion التفصيلية (C15 + G-14)",
     "",
     "- **C15 (اختبار كتابة التوكن المدوّر):** WRITE_FULL — إنشاء + إلحاق + تحديث كتلة + تحديث خصائص + أرشفة، كلها HTTP 200 بتحقق قراءة عكسي. أدلة: research/c15_write_test_2026-10-02.json (ج1 — عيب منهجي POST بدل PATCH وُثق وصُحح) + _run2.json (ج2 كاملة). الأثر المتبقي: صفحتا اختبار في سلة المحذوفات + قفز طابع تحرير المرجع الحاكم 2026-09-27T16:33Z → 2026-10-02T09:57Z (ميتاداتا فقط، بلا تغيير محتوى).",
     "- **G-14 (بحوث موردي 02/10):** الثلاثية (127+401+147 كتلة · حررت 05:32+03) = بحث «Provider Intelligence Engine»: لا مشروع واحد يجمع الطبقات (FINDING) · وحدة التنفيذ = Credential+Endpoint+Adapter لا البوت (INFERENCE) · توصية البناء لا Fork (RECOMMENDATION) · نموذج أدلة DECLARED/OBSERVED متطابق مع §45.8. المزودون الأربعة كلهم كيانات G-1 R3 (06:40+03): canboso=منصة HitMeow (349 منتجًا · v2/tgb_) · digitalcore.top=API مشترٍ مؤكد · aixpress: المفتاح 401 على aiversehub.store و200 على aixpress.shop (وثائق البوت متقادمة؛ النطاقان يتشاركان IP 188.166.90.19 بنشرين مختلفين) · cgpt-active.pro=RichAI Reseller API v1.0.0 (12 نقطة نهاية — أنضج تصميم في المنظومة). سياق جديد: ~300 بوت مورد لدى المستخدم + ملاحظة أمنية داخلية بحجب مفاتيح API.",
     "- **المرجع الحاكم (3,243 كتلة):** 2,528 كتلة 25/09 (البحث التأسيسي) + 554 كتلة 26/09 + 161 كتلة 27/09 (طبقة مزامنة MEC: 6 صفحات نتائج ابنة + كالاوتات + فحص §19 المباشر 31/31 + الأسعار الحية 27/09 + اقتصاديات السلسلة + الحجر والأدلة المضادة). صفر تحرير بعد 27/09 — الاستقرار الهيكلي مؤكد بالطوابع.",
     "- **امتداد G-12 (حسم):** الاتجاه الزمني «أسس 25/09 ثم سلاسل 26-27/09» + اتساق قيمي 5/6 (20.93 · 47.17 · 9.07 · 12.99 · 19.99 مثبتة في قاعدة SKU؛ السادس 20.61 عرض نافد غيابه متسق) + اتجاه التدفق ثنائي المسار موثق (مراس رسمية Notion→مشروع · نتائج رمادية مشروع→Notion).",
     "- **الكشف الكامل:** download/G14_تقرير_مصالحة_دلتا_Notion_2026-10-02.md + research/g14_2026-10-02/ (بنية المرجع الحاكم · كتل 27/09 · مراسي الأسعار ببطوابعها · أبوّة الدلتا · الكيانات · الأسعار · النصوص الكاملة).",
     ""], "R13-342c")

ins_after("| **v3.1** | **02/10 (يُختم أدناه)**",
    ["| **v3.2** | **02/10 (يُختم أدناه)** | **طبقة C15+G-14 (تحديث جراحي بلا إعادة بناء)** | إغلاق C15 (WRITE_FULL) + حسم G-14 (صفر تعارض معرفي) + حسم G-12 (اتجاه الزمن + اتساق القيم) + تحديث R7 — بلا تغيير أي حسم معرفي قائم آخر |"], "R14-v43")
rep_line("1. **348 صفحة Notion غير المُصدَّرة (C14) — RESOLVED (v3.1):**",
    "1. **عائلة C14/C15 (Notion غير المُصدَّرة + قدرة كتابة التوكن) — RESOLVED بالكامل (v3.1+v3.2):** C14 أُغلقت (348/348) · G-14 المصالحة التفصيلية ANSWERED (v3.2) · C15 WRITE_FULL (v3.2). الحد البنيوي المتبقي: لا مقارنة صفوف مباشرة من ملفات القواعد القديمة (C15/C16 الأصلية) — موثق كقيد دائم.", "R15-l45")
rep_line("**ما هو مجهول (UNKNOWN بنيويًا):**",
    "**ما هو مجهول (UNKNOWN بنيويًا):** الاسم القانوني للمشغّل (G-7) · أسعار الجملة خلف بوابات التسجيل · أسعار المعاملات الفعلية (لم تُنفَّذ معاملة). — **(v3.1)** محتوى 348 صفحة Notion أصبح معروفًا؛ **(v3.2)** قدرة كتابة التوكن أصبحت معلومة (WRITE_FULL).", "R16-unknown")
rep_line("**ما هو ناقص (يحتاج بحثًا مستقبلًا):**",
    "**ما هو ناقص (يحتاج بحثًا مستقبلًا):** G-2 (منبع AiVerseX — أُغني سياقيًا بطبقة API في v3.2 بلا حسم) · G-6 (بقاء AISUBSID بعد التحول) · G-7 (التحقق بالمعاملة) · G-8 (قياس البقاء) · G-11 (استقرار الكتالوج — يحتاج شهودًا متباعدة) · G-13 (المتبقي: Acczone/AISUBSID/Evo_Era/رابط النشر) · استئناف GDS الـ770 المتبقية (محجوب بالحصة) · ~~G-12~~ **(ANSWERED v3.2)** · ~~G-14~~ **(ANSWERED v3.2)** · ~~اختبار قدرة كتابة التوكن~~ **(RESOLVED v3.2 — WRITE_FULL).**", "R17-todo")

ins_before("## 47.",
    ["### 46.7 تحقق طبقة v3.2 (C15 + G-14 — فوق بوابات v3.0/v3.1 السابقة)",
     "",
     "- **اكتمال أدلة C15:** جولتا اختبار كاملتان موثقتان (11 خطوة API لكل جولة) — الحكم WRITE_FULL مبني على استجابات HTTP 200 حية لا على استدلال؛ الأثر المتبقي مفحص وموثق (صفحتا اختبار في سلة المحذوفات + قفز طابع تحرير المرجع الحاكم).",
     "- **اكتمال أدلة G-14:** 6 صفحات محورية مقروءة كاملة النص (3,243 + 2,608 + 407 + 401 + 147 + 127 كتلة) · عزل التغيير بطوابع الكتل لا بفرق النصوص · مقاطعة ضد 3 سجلات (§19 + 10 كيانات + 230 GDS) + تقرير G-1 R3 + قاعدة SKU — كل ادعاء في §34.2c مسند إلى شاهد ملف.",
     "- **فحص التعارض:** صفر تعارض معرفي جديد؛ مفارقة زمنية واحدة (aiversehub→aixpress) مصنفة ترتيب شهود لا تعارضًا؛ لا تغيير في أي حسم معرفي قائم.",
     "- **الخلاصة:** طبقة v3.2 صالحة للختم فوق v3.1 بلا إعادة بناء.",
     ""], "R18-467")
rep_line("«PMRF v3.1 §<القسم>»",
    "- **قاعدة الاستشهاد:** «PMRF v3.2 §<القسم>» هو المرجع الموحد بعد هذا الإصدار (v3.1 مؤرشف بالبصمة كاملة).", "R19-cite")

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
        "| Release version | **PMRF v3.2** (طبقة C15+G-14 فوق v3.1) |",
        "| Generation timestamp | %s (التحديث الجراحي بعد اكتمال اختبار C15 وفحص G-14) |" % TS,
        "| Verification timestamp | %s (اكتمال الجولتين + اتساق §46.7) |" % TS,
        "| SHA-256 (المحتوى قبل هذا الختم) | `%s` |" % pre_sha,
        "| حجم المحتوى المختوم | %s bytes (%s سطرًا) |" % (f"{pre_bytes:,}", f"{pre_lines_n:,}"),
        "| Canonical status | **CANONICAL PROJECT MASTER REFERENCE** (ميراث قرار v3.0 §46.5 + تحقق طبقات v3.1 §46.6 وv3.2 §46.7 — لا تغيير في أي حسم معرفي قائم) |",
        "| الأرشيف المحفوظ | v1.5 (sha 486a2502e4ab4a3c…) + v2.0 (sha e58b326e00375dd9…) + v3.0 (sha 1bfcbaf94f7b2e6d…) + **v3.1 (sha %s…)** في PMRF_ARCHIVE/ |" % v31sha16,
        "",
        "**قاعدة الختم:** هذا الختم يغطي المحتوى السابق له حصرًا. أي تعديل لاحق يستوجب إصدارًا جديدًا وختمًا جديدًا — لا يُحدَّث هذا الملف موضعيًا بعد الختم."]
final = pre + seal
open(PMRF, "w", encoding="utf-8").write("\n".join(final) + "\n")
final_sha = sha(rb(PMRF)); final_lines = len(final)
print("[seal] pre-seal sha %s… | content %s bytes / %s lines" % (pre_sha[:16], f"{pre_bytes:,}", f"{pre_lines_n:,}"))
print("[done] PMRF v3.2 written | final sha %s… | %s lines (was %s)" % (final_sha[:16], final_lines, n0))

# ---------- 4) worklog append ----------
wl = """
---
Task ID: C15-G14
Agent: Main (Super Z)
Task: تعليمات المستخدم الصريحة — (1) اختبار قدرة كتابة التوكن الجديد C15 · (2) G-14 فحص تفصيلي لدلتا Notion (بحوث موردي 02/10 + المرجع الحاكم 3,243 كتلة) امتداد G-12

Work Log:
- كُتب ونُفِّذ scripts/c15_write_test.py (جولتان): ج1 12:57:15+03 (عيب منهجي: POST بدل PATCH لنقطة الإلحاق → 400 — وُثق وصُحح) · ج2 12:57:51+03 كاملة: إنشاء صفحة تحت REF_HAKIM + إلحاق كتلة + تحديث كتلة + تحديث أيقونة + تحقق قراءة عكسي + أرشفة — كل الخطوات HTTP 200
- الحكم: WRITE_FULL — الأدلة: research/c15_write_test_2026-10-02.json + _run2.json (11 خطوة API لكل جولة)
- الأثر المتبقي الموثق: صفحتا اختبار في سلة المحذوفات (in_trash=true) + طابع تحرير المرجع الحاكم 2026-09-27T16:33Z → 2026-10-02T09:57Z (ميتاداتا فقط)
- كُتب ونُفِّذت سكربتات G-14 الثلاثة (g14_delta_reconcile.py · g14_part2_timestamps.py · g14_part3_parentage_prices.py): 6 صفحات محورية كاملة النص (3,243+2,608+407+401+147+127 كتلة) + عزل بطوابع الكتل + مقاطعة (§19 + سجل 10 + GDS 230 + G-1 R3 + قاعدة SKU)
- النتائج الحاكمة: المرجع الحاكم = 2,528 كتلة 25/09 + 554 كتلة 26/09 + 161 كتلة 27/09 (طبقة مزامنة MEC: 6 صفحات نتائج ابنة) + صفر تحرير بعدها · ثلاثية 02/10 (05:32+03) = طبقة تخطيط DECLARED لمحرك Provider Intelligence فوق ~300 بوت مورد · المزودون الأربعة كيانات G-1 R3 (06:40+03، بعدها بـ68 دقيقة): canboso=منصة HitMeow · digitalcore.top · aixpress/aiversehub (مفارقة زمنية موثقة: Base URL متقادم) · cgpt-active.pro=RichAI · مراسي الأسعار 2.80/10.67/17.14/×1.2 كلها كتل 27/09 (تدفق مشروع→Notion) · قيم السلة التأسيسية متسقة 5/6 مع قاعدة SKU
- أُنتج download/G14_تقرير_مصالحة_دلتا_Notion_2026-10-02.md + research/g14_2026-10-02/ (9 مخرجات تحليل)
- طبقة PMRF v3.2 الجراحية (19 استبدالًا/إدراجًا موثقًا): أرشفة v3.1 (sha %s) → §1/§2/§28(C15 RESOLVED)/§29(R7)/§30(G-12+G-14 ANSWERED)/§31/§34.2c جديد/§43/§45/§46.7 جديد/§47/§48 → ختم جديد

Stage Summary:
- المخرجات: PMRF v3.2 (مختوم · CANONICAL مواريث) + تقرير G-14 + أدلة C15 (جولتان) + 9 مخرجات تحليل + أرشيف v3.1 كامل بالبصمة
- الإغلاقات: C15 (RESOLVED — WRITE_FULL) · G-14 (ANSWERED — صفر تعارض معرفي) · G-12 (ANSWERED — اتجاه الزمن + اتساق القيم) · R7 محدث
- جديد موثق: سياق ~300 بوت مورد · مفارقة زمنية aiversehub/aixpress (ترتيب شهود لا تعارض) · C4/G-2 أُغنيا سياقيًا بلا حسم
- بقي بيد المستخدم: مفاتيح Acczone/AISUBSID/Evo_Era · رابط نشر المتجر (G-13)
""" % v31sha16
open(WL, "a", encoding="utf-8").write(wl)
print("[worklog] appended Task ID: C15-G14")
