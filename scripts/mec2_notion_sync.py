#!/usr/bin/env python3
"""MEC-2.0 G4: Notion sync — user-authorized knowledge commit (2026-09-27 session).
Commits: (1) pending Cycle-6 record, (2) Cycle-7 MEC-2.0 record, (3) MEC-2.0 results
child page under the Governing Reference, (4) dated non-destructive sync callouts on
Operating Protocol + Prompt Development History.
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
LOG_F = open("/home/z/my-project/data/research/mec2_notion_sync_log.json", "w", encoding="utf-8")

REF_HAKIM = "3e658a07-79e8-81c4-9cdd-d7b74626d61f"       # المرجع الحاكم (digital products)
OP_PROTOCOL = "3e758a07-79e8-819c-872c-e119effe608e"      # Operating Protocol
PROMPT_HIST = "3e758a07-79e8-8130-9192-e0cb12b48731"      # Prompt Development History
IA_DB = "e844ab12-d846-4974-9651-0892464966e5"            # Interaction Archive DB

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

def P(text, color=None):
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(text)}}
def H2(text):
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rt(text)}}
def H3(text):
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": rt(text)}}
def B(text):
    return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(text)}}
def C(text, icon="📘", color="blue_background"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": rt(text), "icon": {"type": "emoji", "emoji": icon}, "color": color}}
def DIV():
    return {"object": "block", "type": "divider", "divider": {}}

# ---------------- Step 1: identity ----------------
me = api("GET", "/users/me")
log("identity", "__error" not in me, me.get("name") or me)
if "__error" in me:
    print("TOKEN INVALID — aborting all writes."); finalize(); sys.exit(1)

# ---------------- Step 2: Interaction Archive schema ----------------
db = api("GET", "/databases/" + IA_DB)
if "__error" in db:
    log("ia_schema", False, db)
    props = {}
else:
    props = db.get("properties", {})
    log("ia_schema", True, "props: " + ", ".join("%s(%s)" % (k, v.get("type")) for k, v in props.items()))

def make_row(fields):
    """Map semantic fields onto actual DB properties by fuzzy name."""
    out = {}
    used = set()
    def find_prop(*names):
        for n in names:
            for k in props:
                if k.lower().strip() == n.lower() and k not in used:
                    return k
        for n in names:
            for k in props:
                if n.lower() in k.lower() and k not in used:
                    return k
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
            log("row_field_missing:" + key, False, "no prop for " + key); continue
        ptype = props[pk].get("type")
        try:
            if ptype == "title":
                out[pk] = {"title": rt(val)}
            elif ptype == "rich_text":
                out[pk] = {"rich_text": rt(val)}
            elif ptype == "number":
                out[pk] = {"number": int(val)}
            elif ptype == "date":
                out[pk] = {"date": {"start": val}}
            elif ptype in ("select", "status"):
                options = [o.get("name") for o in (props[pk].get(ptype) or {}).get("options", [])]
                m = next((o for o in options if o.lower() == str(val).lower()), None)
                if m: out[pk] = {ptype: {"name": m}}
                else: log("row_select_skip:" + pk, False, "value '%s' not in options %s" % (val, options[:6]))
        except Exception as e:
            log("row_field_error:" + pk, False, e)
        used.add(pk)
    return out

# ---------------- Step 3a: Cycle 6 row (pending package commit) ----------------
c6 = {"title": "Cycle 6 — z.ai Meta-Analysis & Cross-Audit — Batch 1 Results Reconciliation",
 "actor": "z.ai Runtime (Super Z)",
 "stage": "Runtime Evidence + Analysis", "cycle": 6, "date": "2026-09-27",
 "status": "Committed",
 "version": "v4.2 (context) / v4.1 (audited runtime)",
 "objective": "تحليل شامل وتدقيق متقاطع للمحادثة المرجعية مقابل Notion وأدوات تشغيل Batch 1، وسد فجوة الدليل بين نتائج التنفيذ الفعلية وسجلات الدورتين 4–5.",
 "findings": "تأكيد تنفيذ Batch 1 كاملًا (76/96 إجراءً، 15/15 SKU نهائية، 52 كيانًا متحققًا، 52 عرضًا)؛ كشف 12 تناقضًا و11 فجوة و8 مخاطر؛ إجابة مجهولات الدورة 5 الموثقة. (سجل التحليل الكامل: ملف meta-analysis المحلي 2026-09-27)",
 "decision": "D1 بوابة Bootstrap + D2 معيار المخرجات + D5 تدوير التوكن — القرارات السبعة معروضة ولم تُحسم.",
 "evidence": "أدوات التشغيل المحلية (run-contract SI-BATCH1-20260926، budget.json 76/96، skus.json، مجموعة بيانات 1745 سطرًا) + حصاد Notion بقراءة فقط (25 وثيقة + 3 قواعد كاملة الصفوف).",
 "canonical": "لا شيء — لا ترقية ولا تعديل حوكمة.",
 "next": "حسم D1/D2 ثم تخويل الدفعة الثانية تحت v4.2."}
row6 = {"parent": {"database_id": IA_DB}, "properties": make_row(c6), "children": [P("ارتُكبت هذه الحزمة المعلقة (المكوّن 1 من حزمة 2026-09-27) بأثر رجعي عبر جلسة MEC-2.0 بتخويل المستخدم المباشر في رسالة 2026-09-27 (تحديث بنية المعرفة في Notion). الحالة المعرفية: أدلة تشغيل موثقة، لا تتضمن أي ترقية إصدار.")]}
r6 = api("POST", "/pages", row6)
log("cycle6_row", "__error" not in r6, r6.get("id") or r6.get("__detail", r6))
time.sleep(1)

# ---------------- Step 3b: Cycle 7 row (this run) ----------------
c7 = {"title": "Cycle 7 — MEC-2.0 — §19 Channel Registry Verification + Supply-Chain Economics",
 "actor": "z.ai Runtime (Super Z)",
 "stage": "Runtime Research + Knowledge Commit", "cycle": 7, "date": "2026-09-27",
 "status": "Committed",
 "version": "v4.2 (working context)",
 "objective": "تنفيذ ما لم يُنفّذ قط: التحقق المباشر من سجل قنوات Telegram المرجعي (§19، 31 كيانًا) وإجابة الشرط الصارم من المستخدم: كيف يشتري البائعون منخفضًا ويبيعون وكم هوامشهم — مع تحديث الموقع والمشروع بالكامل.",
 "findings": "31/31 كيانًا حيًا (رصد مباشر 27/09): أكبر عناق Gemini GPT الصينية 142,797 مشتركًا؛ Verifier Chat 25,948 (وسيط ضمان 3 أشهر)؛ StackVault متجر حي 248 منتجًا (ChatGPT Plus $4.99، Netflix $3.99، Spotify $4.49، MS365 سنة $9.99). أسعار حية: Gemini AI Pro 18 شهرًا $0.39–0.59 (ProdSeller API $0.40) مقابل $359.82 رسمي؛ ChatGPT Plus $4.50 (ضمان ساعتين)؛ طريقة UPI بنجاح 1–2% لكل 1000 حساب. اكتشافات هوية: رابط الدعوة الخاص = Acczone Store، بوتا PremiKey = HitMeow Shop، VeirfyerSupportbot = Fin Ai Support. رصد محتوى احتيالي صريح (أرقام بطاقات مولدة) في قناة learnwith_Alex — أُبقي في الحجر وفق D4.",
 "decision": "لا حسم لأي قرار — D1–D7 تبقى مفتوحة؛ محتوى الحجر يُحدّث أدلة D4 فقط.",
 "evidence": "رصد مباشر HTTP 200 لـ31/31 كيانًا + 6 معاينات منشورات عامة (t.me/s/) + 26 استعلام بحث (26/26 ناجحًا) + متجر StackVault مباشرة. السجلات: mec2_channels_raw.json + mec2_search_results.json (بيئة z.ai).",
 "canonical": "لا شيء — لا ترقية ولا تعديل حوكمة.",
 "next": "مراجعة صفحة نتائج MEC-2.0 تحت المرجع الحاكم + الموقع المحدّث v2.0 + حسم D1/D2/D5."}
row7 = {"parent": {"database_id": IA_DB}, "properties": make_row(c7), "children": [P("الحالة المعرفية: أسعار مرصودة مباشرة بتاريخ 2026-09-27 (Advertised/Directly-Observed) — ليست أسعارًا معاملاتية؛ التحقق من المعاملات غير منفذ. العلامات التجارية موثقة ككيانات مرصودة لا كتوصيات.")]}
r7 = api("POST", "/pages", row7)
log("cycle7_row", "__error" not in r7, r7.get("id") or r7.get("__detail", r7))
time.sleep(1)

# ---------------- Step 3c: MEC-2.0 results page under المرجع الحاكم ----------------
blocks = [
 C("صفحة نتائج MEC-2.0 — 2026-09-27 · نطاق: التحقق من سجل القنوات §19 + اقتصاديات سلسلة التوريد (الشرط الصارم من المستخدم). التخويل: رسالة المستخدم 2026-09-27. كل معلومة موسومة بحالتها المعرفية: [مرصود مباشرة] / [مستند مصدر خارجي] / [استنتاج] / [افتراض].", "🧭"),
 H2("1 · نتيحة الفحص المباشر لسجل §19 (31 كيانًا)"),
 P("فُحص السجل المرجعي كاملًا بالوصول المباشر بتاريخ 2026-09-27: 31/31 كيانًا حيًا (HTTP 200). هذا يحسم القيد الموثق في الدورات السابقة («لا وصول إلى Telegram») ويحدّث حالة مصدري ProdSeller/StackVault المسجلة 404 في الدورة 5 — الحالة الراهنة: حيّة ومشغّلة. [مرصود مباشرة]"),
 B("عناق Gemini GPT (صينية): قناة 142,797 مشتركًا + دردشة 131,924 عضوًا + بوت Gemini Pixel Helper (استخراج روابط عروض Google One AI Pro) — أكبر تجمع في السجل. [مرصود مباشرة]"),
 B("Verifier Chat: 25,948 عضوًا · بوت وسيط ضمان/إيداع (Escrow) مع ضمان ثلاثة أشهر موثق نصيًا — طبقة الثقة في السوق. [مرصود مباشرة]"),
 B("Acczone: متجر خاص بالدعوة (3,650) + سجل مخزون Logs (8,316) + بوت متجر + بوت فحص روابط Gemini — بنية مزود جملة معلنة («أكبر مزود لجميع المنتجات»). [مرصود مباشرة]"),
 B("هويات محسومة: رابط الدعوة الخاص = متجر Acczone Store؛ بوتا PremiKey يحملان اسم HitMeow Shop (إنجليزي/فيتنامي)؛ VeirfyerSupportbot = Fin Ai Support. [مرصود مباشرة]"),
 B("سمعة مستقلة: لا أثر مراجعات عامة مستقلة لأي عناق (نمط ثقة سوق Telegram: ضمان + سجلات بدل مراجعات). StackVault: تعارض اسم مع منتج SaaS مختلف في متاجر الصفقات — السمعة تعتمد على سجل التفاوض التاريخي المحفوظ. [استنتاج من غياب الدليل]"),
 H2("2 · الأسعار الحية المرصودة (27/09)"),
 B("Gemini AI Pro · 18 شهرًا: تجزئة $0.43–0.59 · API جملة $0.40 · جملة كبيرة $0.39 (ProdSeller) — مقابل $359.82 رسميًا (18×$19.99). [مرصود مباشرة]"),
 B("ChatGPT Plus: حساب بضمان ساعتين $4.50 (Evo Era) · ترقية مستقرة $8–10 (GGSel 749₽=$9.44 موروثة 27/09) · StackVault «رسمي+ضمان» $4.99 — مقابل $20.00 رسميًا. [مرصود مباشرة]"),
 B("StackVault (248 منتجًا): Netflix Premium حساب خاص $3.99 · Spotify Premium $4.49 · Microsoft 365 سنة/5 أجهزة $9.99 · Canva Teams $6.49 · Coursera Plus سنة $29.99. [مرصود مباشرة — إعلانية]"),
 B("مواد خام: Gmail مستقر $0.60–0.80 (عمر 2010–201x) · Duolingo Super سنة $0.50–0.59 · Canva لوحة 500 مستخدم $2.50. [مرصود مباشرة]"),
 H2("3 · اقتصاديات سلسلة التوريد — إجابة الشرط الصارم"),
 P("السلسلة أربع طبقات مرصودة: (1) مواد خام: بريد قديم + تحقق طلابي SheerID (يُشترى عبر Xianyu) + مدفوعات افتراضية UPI/Apple Pay؛ (2) مصانع حسابات: إنشاء جماعي بطريقة UPI بنجاح 1–2% (كل 1000 حساب ≈ 10–20 Plus ناجحة — موثق نصيًا من البائع نفسه) وروابط عروض Pixel/الطلاب لـ Gemini (Google خفّضت العرض 12→6 أشهر مع Pixel 11 → ندرة متزايدة)؛ (3) موزعو جملة/API: ProdSeller API (+500 مستخدم API، +15K مستخدم) يبيع للبائعين الصغار؛ (4) تجزئة Telegram + متاجر مثل StackVault. الطبقة الوسطى للثقة: بوتات الضمان/الوسيط. [مرصود مباشرة + استنتاج]"),
 P("اقتصاديات الوحدة المرصودة: سعر البيع = كلفة اقتناء شبه صفرية (استغلال عروض) + كلفة الفشل (98–99% لطريقة UPI) + احتياطي استبدال/ضمان (ضمان ساعتين مقابل 3 أشهر يحدد السعر: $4.50 مقابل $8–10) + رسوم USDT (~1–2%) + هامش. الهامش بين الجملة والتجزئة المرصود: 10–50% (Gemini: $0.39→$0.59)؛ الهامش مقابل السعر الرسمي: 87–99% لكنه يقوم على منتجات مختلفة هويةً (حساب مشترك/مُنتَج استغلالي ≠ اشتراك كامل). [استنتاج مبني على أسعار مرصودة]"),
 H2("4 · الحجر والأدلة المضادة"),
 B("رُصد محتوى احتيالي صريح في منشورات قناة learnwith_Alex: أرقام بطاقات مولدة مع CVV عشوائي لطرق تحقق — يُصنّف غير قانوني، يُستبعد من أي توصية، ويُبقي في حجر D4 مع خيوط SheerID. [مرصود مباشرة — لا اتهام لأشخاص، تصنيف محتوى]"),
 B("حسابات مشتركة/مُنتَجة تنتهك شروط الناشرين (ToS)؛ مخاطر المشتري: فقدان الوصول، إلغاء جماعي، لا استرداد. التوازي الرسمي الأرخص الموثق: الفوترة السنوية (ChatGPT $200/سنة = $16.67/شهر؛ Gemini $199.99/سنة). [مستند مصادر سابقة + مرساة رسمية]"),
 H2("5 · المخرجات المرجعية"),
 B("موقع ويب محدّث v2.0 بكامل البيانات (تقييم القنوات + اقتصاديات التوريد + قاعدة SKU + التحليل) — بيئة z.ai."),
 B("ملفات: mec2_contract.md · channel_evaluation.json · supply_chain_economics.md · conversation_analysis.md · notion_sync_report — مجلد download/."),
 B("قرارات المستخدم المفتوحة دون تغيير: D1–D7 كما في التقرير التحليلي 2026-09-27."),
 DIV(),
 P("التزمت هذه الصفحة بقواعد الحوكمة: لا ترقية إصدار، لا حسم قرار، لا حذف تاريخ، وكل إضافة موسومة بحالتها المعرفية. المصدر القانوني للبيانات: ملفات JSON المحلية + الرصد المباشر بتاريخ 2026-09-27."),
]
page_payload = {
 "parent": {"page_id": REF_HAKIM},
 "properties": {"title": {"title": rt("نتائج MEC-2.0 — تقييم سجل قنوات §19 واقتصاديات سلسلة التوريد — 2026-09-27")}},
 "children": blocks[:100],
}
rp = api("POST", "/pages", page_payload)
log("mec2_results_page", "__error" not in rp, rp.get("id") or rp.get("__detail", rp))
time.sleep(1)

# ---------------- Step 3d: non-destructive sync callouts ----------------
sync_note_op = C("【مزامنة حالة 2026-09-27 — جلسة MEC-2.0】Current Candidate: v4.2 — Catalog/Batch Architecture Candidate (مقبول من المستخدم 2026-09-27، غير معتمد). v4.1: محفوظ كوقت تشغيل Batch 1 (2026-09-26) ومرجع مقارنة تاريخي. لا يوجد Prompt معتمد. بوابة Bootstrap (D1) ما زالت مفتوحة. الخطوة التالية: اختبار حي متعدد الدفعات (الدفعة الثانية تحت v4.2) + انحدار تنافسي. — ملاحظة: أُضيفت هذه المزامنة أسفل الصفحة بدل استبدال نص القسم الأصلي التزاممًا بقاعدة عدم المساس بالمحتوى التاريخي؛ القسم الأصلي متقادم (يذكر v4.1) والنص البديل المقترح موثق في حزمة التحديثات.", "🔁", "blue_background")
r_op = api("PATCH", "/blocks/%s/children" % OP_PROTOCOL, {"children": [sync_note_op]})
log("op_protocol_sync", "__error" not in r_op, r_op.get("results", [{}])[0].get("id", r_op.get("__detail", r_op)))
time.sleep(1)

sync_note_ph = C("【مزامنة حالة 2026-09-27 — جلسة MEC-2.0】v4.2: مرشح العمل الحالي (مقبول من المستخدم 2026-09-27، غير معتمد). v4.1: محفوظ كوقت تشغيل Batch 1 (2026-09-26). البند المتقادم أعلاه («v4.1: current Candidate») يُقرأ ضمن سياقه التاريخي؛ الحالة الموثقة الراهنة في سجل الإصدارات وسجل Canonical.", "🧬", "blue_background")
r_ph = api("PATCH", "/blocks/%s/children" % PROMPT_HIST, {"children": [sync_note_ph]})
log("prompt_hist_sync", "__error" not in r_ph, r_ph.get("results", [{}])[0].get("id", r_ph.get("__detail", r_ph)))

LOG_F.write(json.dumps(REPORT, ensure_ascii=False, indent=1))
LOG_F.close()
ok_count = sum(1 for r in REPORT if r["ok"])
print("\nSYNC COMPLETE: %d/%d operations OK" % (ok_count, len(REPORT)))
