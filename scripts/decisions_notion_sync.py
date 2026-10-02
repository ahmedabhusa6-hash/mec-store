#!/usr/bin/env python3
"""MEC-2.2 Notion sync — Decisions package commit (2026-09-27 morning).
Commits: (1) Cycle-9 row in Interaction Archive, (2) Decisions-package child page
under the Governing Reference, (3) dated callout on the Batch-2 results page.
GOVERNANCE NOTE (documented deviation): this sync RECORDS decision resolutions
(D1/D2/D5) as resolved-via-explicit-user-delegation — the user delegated these
in writing ("ما زالت بيدك: D1/D2 (الحوكمة) وD5 ... وحسابات B2B"). No version
promotion (v4.2 remains Candidate; promotion awaits explicit user word only)."""
import json, time, ssl, sys, urllib.request, urllib.error

import os as _os
def _load_token():
    tok = _os.environ.get('NOTION_TOKEN', '')
    if tok:
        return tok
    env_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '.env')
    try:
        for line in open(env_path, encoding='utf-8'):
            if line.strip().startswith('NOTION_TOKEN='):
                return line.strip().split('=', 1)[1].strip().strip(chr(34)).strip(chr(39))
    except FileNotFoundError:
        pass
    raise SystemExit('NOTION_TOKEN missing: set env var or add NOTION_TOKEN=... to .env')
TOKEN = _load_token()
BASE = "https://api.notion.com/v1"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
REPORT = []
LOG_F = open("/home/z/my-project/data/research/mec22_notion_sync_log.json", "w", encoding="utf-8")

REF_HAKIM = "3e658a07-79e8-81c4-9cdd-d7b74626d61f"       # المرجع الحاكم
B2_RESULTS = "3e858a07-79e8-8185-852b-c1f6034be0b9"      # نتائج الدفعة 2 (MEC-2.1) page
IA_DB = "e844ab12-d846-4974-9651-0892464966e5"           # Interaction Archive DB

def log(section, ok, detail):
    line = {"section": section, "ok": ok, "detail": str(detail)[:500]}
    REPORT.append(line)
    print(("[OK] " if ok else "[!!] ") + section + " :: " + str(detail)[:160])

def api(method, path, body=None, retries=3):
    headers = {"Authorization": "Bearer " + TOKEN, "Notion-Version": "2022-06-28",
               "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(BASE + path, method=method, headers=headers, data=data)
            with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(min(float(e.headers.get("Retry-After", 2 ** attempt)), 30)); continue
            try: detail = e.read().decode()[:300]
            except Exception: detail = ""
            return {"__error": e.code, "__detail": detail}
        except Exception as e:
            time.sleep(1.5 ** attempt)
    return {"__error": "max_retries"}

def rt(text): return [{"text": {"content": text[:1900]}}]
def P(text): return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}
def H2(text): return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rt(text)}}
def B(text): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(text)}}
def C(text, icon="📘", color="blue_background"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": rt(text), "icon": {"type": "emoji", "emoji": icon}, "color": color}}
def DIV(): return {"object": "block", "type": "divider", "divider": {}}

def finalize():
    LOG_F.write(json.dumps(REPORT, ensure_ascii=False, indent=1)); LOG_F.close()

# ---------------- Step 1: identity ----------------
me = api("GET", "/users/me")
log("identity", "__error" not in me, me.get("name") or me)
if "__error" in me:
    print("TOKEN INVALID — aborting all writes."); finalize(); sys.exit(1)

# ---------------- Step 2: IA schema ----------------
db = api("GET", "/databases/" + IA_DB)
props = db.get("properties", {}) if "__error" not in db else {}
log("ia_schema", "__error" not in db, "props: " + ", ".join(props.keys()))

def make_row(fields):
    out, used = {}, set()
    def find_prop(*names):
        for n in names:
            for k in props:
                if k.lower().strip() == n.lower() and k not in used: return k
        for n in names:
            for k in props:
                if n.lower() in k.lower() and k not in used: return k
        return None
    for key, val in fields.items():
        candidates = {"title": ("record", "name", "title"), "actor": ("actor",),
                      "stage": ("stage",), "cycle": ("cycle",), "date": ("date",),
                      "status": ("status",), "version": ("version",),
                      "objective": ("objective",), "findings": ("findings", "changes"),
                      "decision": ("decision",), "evidence": ("evidence", "sources"),
                      "canonical": ("canonical",), "next": ("next", "action")}[key]
        pk = find_prop(*candidates)
        if not pk:
            log("row_field_missing:" + key, False, "no prop"); continue
        ptype = props[pk].get("type")
        try:
            if ptype == "title": out[pk] = {"title": rt(val)}
            elif ptype == "rich_text": out[pk] = {"rich_text": rt(val)}
            elif ptype == "number": out[pk] = {"number": int(val)}
            elif ptype == "date": out[pk] = {"date": {"start": val}}
            elif ptype in ("select", "status"):
                options = [o.get("name") for o in (props[pk].get(ptype) or {}).get("options", [])]
                m = next((o for o in options if o.lower() == str(val).lower()), None)
                if m: out[pk] = {ptype: {"name": m}}
                else: log("row_select_skip:" + pk, False, "'%s' not in %s" % (val, options[:6]))
        except Exception as e:
            log("row_field_error:" + pk, False, e)
        used.add(pk)
    return out

# ---------------- Step 3: Cycle 9 row ----------------
c9 = {"title": "Cycle 9 — MEC-2.2 Decisions Package (delegated D1/D2/D5 + B2B dossier + D2 first Word execution)",
 "actor": "z.ai Runtime (Super Z)",
 "stage": "Runtime Evidence", "cycle": 9, "date": "2026-09-27",
 "status": "Committed",
 "version": "v4.2 Candidate — Promotion-Ready (3/4 bootstrap conditions met; awaiting user word only)",
 "objective": "تنفيذ حزمة القرارات المفوَّضة من المستخدم صراحةً (D1 بوابة الاعتماد الأولي، D2 معيار المخرجات، D5 تدوير التوكن) + إدارة ملف حسابات B2B + متابعة استئناف الاستعلامات الـ15 المؤجلة عند تصفير الحصة.",
 "findings": "D1 حُسم: اعتُمدت قاعدة الاستثناء التأسيسي (بوابة Bootstrap مفتوحة لأول مرة — كانت معطلة بنيويًا). v4.2 = Promotion-Ready (السلالة + المراجعات + 3 تشغيلات حية مستوفاة؛ الشرط الرابع كلمة المستخدم). D2 حُسم: المعيار الثلاثي (ويب+Word+Markdown) بتوليد آلي من المصدر الموحد — التنفيذ الأول صدر (Word برامجي 28KB اجتاز الفحص بلا أخطاء). D5 حُسم قرارًا (تدوير فوري) + نُفذ الجانب التقني: التوكن أُزيل من السكربتات الخمسة ونُقل إلى .env المستثنى من git وحُوّلت السكربتات لمتغير بيئة باختبار حي ناجح — الفعل المتبقي 5 دقائق بيد المستخدم. ملف B2B: ترتيب أولوي معتمد (ProdSeller API ← Turgame Wholesale ← FazerCards ← Reloadly) + بروتوكول استخراج جاهز (12 مرساة P1، تصنيف «مشاهد مباشرة»، حساب الفوارق تلقائيًا). مراقب حصة آلي يعمل (الحصة ما زالت محجوبة — نافذة طويلة).",
 "decision": "ثلاثة حسومات بتفويض صريح موثق (D1/D2/D5) مع حق نقض كامل. لا ترقية إصدار — v4.2 تبقى Candidate حتى كلمة المستخدم. D4/D6 يبقيان مفتوحين.",
 "evidence": "download/decisions_d1_d2_d5_b2b.md (الحزمة الكاملة) + supplier-intelligence-program-2026-09-27.docx (أول Word برامجي — postcheck 0 أخطاء) + supplier_intelligence.html v2.2 (100KB) + sku_database.md قسم MEC-2.2 + scripts/quota_watcher.py (سجل research/quota_watcher.log) + فحص rg = صفر توكنات في السكربتات.",
 "canonical": "لا ترقية. تغيير حوكمي واحد موثق: اعتماد قاعدة Bootstrap (D1-أ) — تصبح نافذة فورًا؛ أول تطبيق لها ينتظر تصريح المستخدم حصرًا.",
 "next": "كلمة المستخدم في ترقية v4.2 (جاهزة) + تدوير التوكن (5 دقائق بخطوات جاهزة) + فتح حساب B2B الأول (ProdSeller) + عند تصفير الحصة: استئناف الـ15 تلقائيًا ثم الدفعة 3 بجلسة منفصلة."}
row9 = {"parent": {"database_id": IA_DB}, "properties": make_row(c9),
        "children": [P("الحالة المعرفية: حسومات حوكمية مبنية على تفويض مستخدم صريح (نص التفويض موثق حرفيًا في وثيقة القرارات) — ليست حسومات بالوكالة الصامتة. كل حسم قابل للنقض بكلمة من المستخدم بلا كلفة حوكمة. مخرجات الحزمة اجتازت فحص الجودة (Word: 0 أخطاء؛ HTML: 6/6 فحوصات بنيوية؛ Next.js: tsc نظيف لمجلد src).")]}
r9 = api("POST", "/pages", row9)
log("cycle9_row", "__error" not in r9, r9.get("id") or r9)

# ---------------- Step 4: Decisions package child page ----------------
children = [
 C("حزمة القرارات المفوَّضة (MEC-2.2) — D1/D2/D5 + ملف حسابات B2B · تشغيلة MEC2-20260927-DEC · 2026-09-27. الأساس: تفويض المستخدم الصريح الحرفي. هذه الصفحة تسجل الحسومات بنسبتها إلى التفويض (لا إلى المستخدم) — حق النقض محفوظ بالكامل. لا ترقية إصدار هنا.", "⚖️", "purple_background"),
 H2("1 · الحسم D1 — بوابة الاعتماد الأولي (Bootstrap)"),
 P("اعتُمد الخيار (أ): قاعدة الاستثناء التأسيسي. النص المعتمد: يجوز ترقية أول نسخة Candidate إلى Approved إذا اجتمعت أربعة شروط — (1) انتماؤها لآخر سلالة مُتحقق منها في سجل النسخ، (2) اجتياز المراجعات التقنية الموثقة، (3) اجتياز اختبار حي متعدد الدفعات مسجل في Runtime Evidence، (4) تصريح مستخدم صريح لا يقبل الوكالة. بعد أول ترقية تُغلق البوابة نهائيًا وتعود قاعدة الباب القياسي حصرًا."),
 P("التبرير: الخيار البديل معطل بنيويًا (القاعدة القياسية تتطلب سلفًا معتمدًا ولا سلف معتمد موجود — استحالة اعتماد أبدي، توتر حوكيمي موثق). قاعدة تنتج تعطيلًا أبديًا ليست حوكمة بل جمودًا؛ وكل إطار ثقة ناضج يملك مسارًا تأسيسيًا (كتلة التكوين، جذر الثقة). الشروط الأربعة المقيدة تمنع الانزلاق."),
 P("الأثر على v4.2: الشروط (1) و(2) و(3) مستوفاة توثيقيًا — السلالة v4.0←v4.1←v4.2 كاملة التوثيق، والمراجعات (تدقيق الفجوات السبع + معمارية v4.2 المغلقة لها + تدقيق الحالة)، والاختبار الحي (ثلاث تشغيلات بمعمارية v4.2: الدفعة 1 = 46 SKU/142 إجراء، الدفعة 2 = 173 SKU/130 استعلامًا، تحقق القنوات = 31/31). الشرط (4) — التصريح الصريح — بيد المستخدم حصرًا بحكم نص القاعدة نفسها."),
 C("النتيجة: v4.2 = Promotion-Ready — بانتظار كلمة المستخدم فقط. كلمة واحدة («اعتمد v4.2») تُفعّل أول ترقية في تاريخ المشروع عبر البوابة المفتوحة الآن. لا يجوز لأي وكيل تنفيذها بالنيابة.", "🖋️", "green_background"),
 H2("2 · الحسم D2 — معيار مخرجات البرنامج"),
 P("اعتُمد الخيار (أ): المعيار الثلاثي (صفحة ويب تفاعلية + Markdown + Word). المصدر الوحيد للحقيقة = قاعدة البيانات الموحدة (offers_intelligence.json + الكتالوج) — الصيغ الثلاث تُولَّد منه ولا تُحرَّر يدويًا بشكل منفصل. إيقاع التوليد: عند اكتمال كل دفعة + عند كل حزمة قرارات حوكمية."),
 P("التبرير: يحسم أعمق تناقض موثق (المرجع الحاكم يشترط ثلاثة مخرجات وعقود التشغيل أُغلقت على اثنين دون تعديل موثق — تناقض مصنف حرجة) لصالح المرجع الأعلى سلطة دون تحريره. سلوك المستخدم الفعلي يدعم الثلاثة (طلب Word واستخدمه). التوليد من المصدر الموحد يجعل الكلفة إجراءً آليًا ويصفر الانحراف الدلالي."),
 P("التنفيذ الأول (صدر مع الحزمة نفسها): ملف Word برامجي شامل (supplier-intelligence-program-2026-09-27.docx — 28KB، فهرس تفاعلي، اجتاز فحص الجودة بلا أخطاء) + تحديث الويب v2.2 والـMarkdown في الحزمة نفسها."),
 H2("3 · الحسم D5 — تدوير توكن Notion"),
 P("اعتُمد التدوير الفوري (لا خيار تأجيلي): التوكن أثبت قدرة كتابة فعلية (أول كتابات ناجحة في MEC-2.0)، ووجوده نصًا صريحًا في ملفات مخزنة يرفع درجة الخطر إلى الأعلى (R7)."),
 B("المُنفَّذ تقنيًا في الجلسة (قبل التدوير — تقليل سطح التعرض فورًا): إزالة نص التوكن من السكربتات الخمسة جميعها (فحص rg = صفر تطابقات)."),
 B("نقل التوكن إلى ملف .env المستثنى من نظام الإصدارات (سطر .env* في .gitignore)."),
 B("تحويل السكربتات الخمسة إلى قراءة متغير بيئة NOTION_TOKEN عبر دالة تحميل موحدة."),
 B("اختبار حي ناجح عبر المسار الجديد (استجابة API 200 — تكامل «موردين»)."),
 B("المتبقي بيد المستخدم (5 دقائق): توليد سر جديد من إعدادات التكامل ← تحديث سطر NOTION_TOKEN في .env ← إبطال القديم ← (موصى به) تقييد نطاق وصول التكامل لصفحات المشروع فقط."),
 P("ملاحظة أمنية صادقة: النص القديم موجود في تاريخ git المحلي (3 التزامات) لكن المستودع محلي بلا أي remote — التعرض محصور في هذه البيئة، والتدوير يبطل أي قيمة لهذا النص نهائيًا بغض النظر عن التاريخ."),
 H2("4 · ملف حسابات B2B (إدارة مفوَّضة — الفتح بيد المستخدم)"),
 P("أكبر مجهول معلن في المشروع: أسعار الجملة الفعلية (Unknown بنيويًا — خلف بوابات تسجيل). فتح حساب واحد يحوّل طبقة كاملة من «غير معروف» إلى «مشاهد مباشرة» — أعلى عائد معلوماتي متبقٍ في البرنامج."),
 B("الأولوية 1 — ProdSeller API (بوت Telegram): أخف دخولًا (رصيد USDT مبدئي)؛ مصدر أول قياس جملة→تجزئة موثق (10-51%)."),
 B("الأولوية 2 — Turgame Wholesale: بوابة جملة موثقة حية (بطاقات PSN/Steam/Xbox/Google Play بعملات متعددة)."),
 B("الأولوية 3 — FazerCards: منصة موزعين — أخف بوابة ويب دخولًا."),
 B("الأولوية 4 — Reloadly: API مؤسسي — أثقل دخولًا (KYC أعمال + حد أدنى إيداع)."),
 B("بروتوكول الاستخراج جاهز: أول 12 SKU = مراسي P1 المؤكدة؛ كل سعر داخل بوابة جملة = مشاهد مباشرة بتاريخ ولقطة؛ الفوارق تُحسب وتُدمج في جداول الهوامش تلقائيًا. حد نزاهة: لا شراء لأغراض الاستطلاع."),
 H2("5 · حالة الاستئناف المؤجل (15 استعلامًا)"),
 P("سكربت الاستئناف رُقّي (الفاشل يُعاد تلقائيًا + إزالة التكرارات — الاستئناف ذاتي بالكامل) + مراقب حصة آلي يعمل بقِطَع زمنية يفتح خط الأنابيب عند تصفير الحصة (بحث ← تجميع ← ذكاء) ويتوقف عند التنقيح اليدوي. الحصة ما زالت محجوبة منذ ~02:10 — نافذة طويلة تُحتمل حصة يومية تراكمية."),
 DIV(),
 P("لوحة القرارات بعد الحزمة: D1 ✅ محسوم بتفويض · D2 ✅ محسوم بتفويض · D3 ✅ مدمج بالدفعة 2 · D4 مفتوح (أدلة MEC-2.0 مضافة) · D5 🟡 قرار حاسم + فعل مستخدمي متبقٍ (5 دقائق) · D6 مفتوح · D7 ✅ منفذ · ترقية v4.2: جاهزة للتوقيع بيد المستخدم حصرًا · الدفعة 3: جلسة منفصلة."),
]
page = {"parent": {"page_id": REF_HAKIM},
        "icon": {"type": "emoji", "emoji": "⚖️"},
        "properties": {"title": {"title": rt("نتائج MEC-2.2 — حزمة القرارات المفوَّضة (D1/D2/D5) وملف B2B وجاهزية الترقية")}},
        "children": children}
rp = api("POST", "/pages", page)
log("decisions_page", "__error" not in rp, rp.get("id") or rp)

# ---------------- Step 5: dated callout on Batch-2 results page ----------------
callout = C("تحديث MEC-2.2 (صباح 2026-09-27): الاستئناف المؤجل (15 استعلامًا) ما زال معلقًا على تصفير الحصة — سكربت الاستئناف رُقّي ليصبح ذاتيًا بالكامل (إعادة محاولة الفاشل + إزالة التكرارات) ومراقب حصة آلي يعمل الآن (scripts/quota_watcher.py) ويفتح خط الأنابيب تلقائيًا عند التصفيير. حزمة القرارات المفوَّضة (D1/D2/D5 + B2B) صدرت وموثقة في صفحة نتائج MEC-2.2 الشقيقة تحت المرجع الحاكم.", "🔄", "gray_background")
rc = api("PATCH", "/blocks/" + B2_RESULTS + "/children", {"children": [callout]})
log("b2_callout", "__error" not in rc, "appended" if "__error" not in rc else rc)

finalize()
print("SYNC COMPLETE — report: data/research/mec22_notion_sync_log.json")
