#!/usr/bin/env python3
"""MEC-2.1 G6: Notion sync — Batch 2 (173 P2 SKUs) results commit (2026-09-27).
Commits: (1) Cycle-8 row in Interaction Archive, (2) Batch-2 results child page
under the Governing Reference, (3) dated non-destructive callout on the MEC-2.0
results page.
Guardrails honored: no version promotion, no decision resolution, no history edits,
every addition carries its epistemic label. Token read from scripts (never in outputs)."""
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
LOG_F = open("/home/z/my-project/data/research/mec2b_notion_sync_log.json", "w", encoding="utf-8")

REF_HAKIM = "3e658a07-79e8-81c4-9cdd-d7b74626d61f"       # المرجع الحاكم
MEC2_RESULTS = "3e858a07-79e8-8114-9eaa-e89e40d0ef56"    # نتائج MEC-2.0 page
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
def H3(text): return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": rt(text)}}
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

# ---------------- Step 3: Cycle 8 row ----------------
c8 = {"title": "Cycle 8 — MEC-2.1 Batch 2 Execution (173 P2 SKUs, snippet-evidence run)",
 "actor": "z.ai Runtime (Super Z)",
 "stage": "Runtime Evidence", "cycle": 8, "date": "2026-09-27",
 "status": "Committed",
 "version": "v4.2 Candidate (working) — unchanged",
 "objective": "تنفيذ الدفعة الثانية للكتالوج (173 SKU من أولوية P2 عبر 10 عائلات) بقنوات Notion المحددة حصرًا (التعديل A)، مع بروتوكول الإيقاع المستفاد (5 ثوانٍ + تبريد 15 ثانية) ومراجعة يدوية لضجيج الاستخراج الآلي.",
 "findings": "115/121 استعلامًا ناجحًا (15 مؤجلًا بحصة 477 طويلة النافذة §19). 219 سجل SKU إجمالًا الآن. 31 SKU بعرض معلن مطابق الهوية + 16 مجاورًا + 26 خطًا رسميًا. اكتشافات هيكلية: سوق العلاوة الأرجنتيني (PSN AR فوق الاسمي $67.91/$50) · شحنات رمادية فوق الرسمي (G2A 660UC +166%) · أرضية منتديات V-Bucks ($6.99/2800) · لا فوترة سنوية رسمية لChatGPT Plus · Office 2024 عبر مصدرين مستقلين ($0.56-0.60).",
 "decision": "لا شيء — D1-D7 كلها مفتوحة كما هي (لا ترقية إصدار، لا حسم قرارات).",
 "evidence": "research/action_ledger.json (115 إجراءً بمعرفات RB-001..115 موثقة الحقول §0.1) + findings_index_b2.json (468 نتيجة) + offers_intelligence.json قسم batch2_run + مراجعة يدوية موثقة في scripts/batch2_curation.py. كل الأسعار بمستوى معلن (مقتطف) — القراءة المباشرة مؤجلة.",
 "canonical": "لا شيء — لا ترقية ولا تعديل حوكمة.",
 "next": "إعادة تشغيل الاستعلامات الـ15 المؤجلة (سكربت استئناف موثق) + الدفعة 3 (218 SKU) بجلسة منفصلة بسبب الحصة + حسم D1/D2/D5 (بقاء المستخدم)."}
row8 = {"parent": {"database_id": IA_DB}, "properties": make_row(c8), "children": [P("الحالة المعرفية: أسعار معلنة عبر مقتطفات بحث بتاريخ 2026-09-27 — ليست أسعارًا معاملاتية ولا مشاهدات مباشرة للصفحات. 18 SKU بحالة Rate-Limited موثقة بأمانة. الاستئناف موصوف في sku_database.md القسم هـ.")]}
r8 = api("POST", "/pages", row8)
log("cycle8_row", "__error" not in r8, r8.get("id") or r8)

# ---------------- Step 4: Batch-2 results child page ----------------
children = [
 C("نتائج الدفعة الثانية (MEC-2.1) — 173 SKU من أولوية P2 · تشغيلة MEC2-20260927-B2 · 2026-09-27. مستوى الدليل: معلن (مقتطف بحث) لكل العروض — القراءة المباشرة للصفحات مؤجلة بسبب استنفاد حصة الوظائف البعيدة (خطأ 477 طويل النافذة، §19). هذه صفحة نتائج تشغيلية، لا ترقية إصدار ولا حسم قرارات.", "🆕", "blue_background"),
 H2("1 · حدود التشغيلة (صادقة)"),
 B("121 استعلامًا مخططًا → 115 ناجحًا (صفر إخفاق قبل الحجب) + 15 مؤجلًا بحصة 477 طويلة النافذة (>45 دقيقة رغم التبريد — يُحتمل حصة تراكمية يومية ~230 استعلامًا عبر الجلسات)."),
 B("الإيقاع المطبق: 5 ثوانٍ بين الاستعلامات + تبريد 15 ثانية عند الفشل + استئناف آمن بميزانية زمنية (درس MEC-2.0 مُطبق)."),
 B("18 SKU بحالة Rate-Limited — الاستئناف موثق كسكربت في المخرجات المحلية (sku_database.md §هـ)."),
 H2("2 · ملخص التغطية"),
 B("219 سجل SKU إجمالًا الآن (46 دفعة 1 + 173 دفعة 2)."),
 B("47 SKU بعروض معلنة (31 بهوية مطابقة تمامًا + 16 بهوية مجاورة موسومة) · 26 بخط أساس رسمي موثق · 108 Lead-only (ضجيج مستبعد بمراجعة يدوية) · 18 مؤجلًا."),
 B("ضجيج الاستخراج الآلي استُبعد بمراجعة بشرية (بطاقات المتاجر نفسها Eneba/Kinguin GC تلوت استعلامات Steam/Xbox/Google — مستبعدة وموثقة كنقاط سلوك قنوات)."),
 H2("3 · أهم الاكتشافات السعرية (معلنة 27/09)"),
 B("PSN 20 USD: $19.04 · PSN 25 USD: $23.67 (إينابا، -5%) — أول أسعار PSN أمريكية معلنة تحت الاسمي في المشروع."),
 B("PSN 50 EUR: $50.83–54.18 (cdkeyprices/gg.deals) · Razer Gold 50: $47.00–48.54 · GTA V: $6.79–9.71 (الرسمي انخفض إلى $29.99) · Elden Ring: $46.44 · AC Shadows: $21.48 · Black Myth: $34.28 (Driffle)."),
 B("Windows 10 Pro: £0.75 (~$1.02) · Office 2024 Pro Plus: $0.60 (Keys4us) — يعزز رصد Keyforsteam €0.56 المباشر السابق عبر مصدر مستقل ثانٍ."),
 B("Valorant 2050 VP: $19.49 · Welkin Moon: $4.99 رسمي · M365 Personal سنة: $61.24 · مقعد Spotify Family (بائع TG هندي): ₹119 (~$1.37) — يعزز نموذج استخراج المقاعد العائلية الموثق في MEC-2.0."),
 B("eSIM: أمريكا من $4.00 (Airalo) · السعودية 10GB/7d $24.00 · الإمارات 3GB/30d $7.85 (eSIMCard)."),
 B("SMM (أرضيات لوحات): IG من $0.01–0.09/1000 · TG أعضاء من $0.07 · يوتيوب مشتركون من $0.06 · تيك توك ~$1.50."),
 B("أرقام افتراضية: TG مصر من $1.61 (PvaPins) · WA أمريكي/بريطاني $0.99/شهر (نموذج إيجار ≠ OTP لمرة واحدة)."),
 H2("4 · الاكتشافات الهيكلية"),
 B("سوق العلاوة الأرجنتيني: بطاقات PSN الأرجنتينية تُباع فوق قيمتها الاسمية (بطاقة $50 عند ~$67.91 عبر K4G؛ معدل $1.35/دولار) — البطاقة أداة وصول مراجَح لمتجر أرخص داخليًا. العرض الوحيد تحتها ($34.81 إينابا) كان «نفد» لحظة الرصد."),
 B("«رمادي» ليس مرادف «أرخص»: G2A يبيع 660 PUBG UC بـ$26.61 فوق الرسمي $9.99 (+166%) — تسعير راحة الدفع البديل لا الخصم. مقابل ذلك منتديات رمادية (sythe.org): 2800 V-Bucks بـ$6.99 بلا أي حماية منصة."),
 B("لا توجد فوترة سنوية رسمية لChatGPT Plus (نص help.openai) — كل عرض «Plus 12 شهرًا» في السوق الرمادي بناء غير رسمي بطبيعته (مقاعد/حسابات) وليس خصمًا عن خطة رسمية."),
 B("خطوط رسمية وثّقتها المقتطفات: ChatGPT Go $8 · Claude Max $100/$200 · Midjourney Basic $10 (سنوي $8/ش) / Standard $30 · GitHub Copilot Pro $10 · Disney+ Ads $9.99 · Google One 100GB $1.99 · PS+ Essential 3 أشهر $24.99 / سنة $79.99 · PUBG UC رسمي 325=$4.99/660=$9.99/1800=$24.99."),
 H2("5 · المخرجات المحدثة"),
 B("supplier_intelligence.html v2.1 (جدول تفاعلي للدفعة 2 + 173 صفًا) · sku_database.md (قسم MEC-2.1) · offers_intelligence.json (batch2_run + 219 سجلًا) · catalog_v42.json (دفتر تغطية الدفعة 2) · تطبيق Next.js (تبويب «الدفعة 2 (173)»)."),
 B("سجلات التشغيل: action_ledger.json (RB-001..115) · findings_index_b2.json (468 نتيجة) · batch2_intelligence_draft.json."),
 C("تذكير حوكمي: v4.2 ما زالت مرشح عمل غير معتمد (بوابة Bootstrap D1 مفتوحة) · D1–D7 كلها بيد المستخدم · توصية D5 (تدوير التوكن) ما زالت عاجلة. المزامنة التالية المقترحة: بعد إعادة الاستعلامات الـ15 المؤجلة أو حسم D1/D2.", "🏛️", "gray_background"),
]
page = {"parent": {"page_id": REF_HAKIM},
        "properties": {"title": {"title": rt("نتائج الدفعة 2 — MEC-2.1 (173 SKU من P2، تشغيلة MEC2-20260927-B2)")}},
        "children": children}
pg = api("POST", "/pages", page)
log("batch2_results_page", "__error" not in pg, pg.get("id") or pg)

# ---------------- Step 5: dated callout on MEC-2.0 results page ----------------
cal = {"children": [C("تحديث 2026-09-27 (لاحقًا في اليوم): نُفّذت الدفعة الثانية (MEC-2.1) فوق هذه النتائج — 173 SKU من P2 بمستوى دليل «معلن (مقتطف)»: 219 سجلًا إجمالًا · 31 عرضًا مطابق الهوية + 16 مجاورًا · 26 خطًا رسميًا · 18 SKU مؤجلًا (حصة 477). التفاصيل في صفحة «نتائج الدفعة 2 — MEC-2.1» الشقيقة. لا تغيير حوكمة.", "🔄", "gray_background")]}
cal_r = api("PATCH", "/blocks/" + MEC2_RESULTS + "/children", cal)
log("mec2_page_callout", "__error" not in cal_r, "appended" if "__error" not in cal_r else cal_r)

finalize()
ok_n = len([r for r in REPORT if r["ok"]])
print("SYNC DONE: %d/%d operations OK" % (ok_n, len(REPORT)))
