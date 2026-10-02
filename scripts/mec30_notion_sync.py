#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-3.0 FINAL Notion sync — Cycle 12 + batch-3 results page + promotion callout."""
import json, time, ssl, sys, urllib.request, urllib.error, os

def _load_token():
    tok = os.environ.get('NOTION_TOKEN', '')
    if tok: return tok
    for line in open('/home/z/my-project/.env', encoding='utf-8'):
        if line.strip().startswith('NOTION_TOKEN='):
            return line.strip().split('=', 1)[1].strip().strip('"').strip("'")
    raise SystemExit('NOTION_TOKEN missing')
TOKEN = _load_token()
BASE = "https://api.notion.com/v1"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
REPORT = []

REF_HAKIM = "3e658a07-79e8-81c4-9cdd-d7b74626d61f"
MEC2_RESULTS = "3e858a07-79e8-8114-9eaa-e89e40d0ef56"
IA_DB = "e844ab12-d846-4974-9651-0892464966e5"

def log(s, ok, d):
    REPORT.append({"section": s, "ok": ok, "detail": str(d)[:400]})
    print(("[OK] " if ok else "[!!] ") + s + " :: " + str(d)[:140])

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
            if e.code == 429: time.sleep(min(float(e.headers.get("Retry-After", 2 ** attempt)), 30)); continue
            try: detail = e.read().decode()[:300]
            except Exception: detail = ""
            return {"__error": e.code, "__detail": detail}
        except Exception:
            time.sleep(1.5 ** attempt)
    return {"__error": "max_retries"}

def rt(t): return [{"text": {"content": t[:1900]}}]
def P(t): return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(t)}}
def H2(t): return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rt(t)}}
def B(t): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(t)}}
def C(t, icon="🏆", color="green_background" if False else "blue_background"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": rt(t), "icon": {"type": "emoji", "emoji": icon}, "color": color}}

# identity
me = api("GET", "/users/me")
log("identity", "__error" not in me, me.get("name") or me)
if "__error" in me: sys.exit(1)

# IA schema
db = api("GET", "/databases/" + IA_DB)
props = db.get("properties", {})

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
        if not pk: continue
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
        except Exception: pass
        used.add(pk)
    return out

# Cycle 12 row
c12 = {"title": "Cycle 12 — MEC-3.0 FINAL: Batch-3 complete (218/218, 143/143 OK) + catalog closure 437/437 + v4.2 → APPROVED",
 "actor": "z.ai Runtime (Super Z)", "stage": "ChatGPT Analysis", "cycle": 12, "date": "2026-09-27",
 "status": "Committed",
 "version": "v4.2 — APPROVED (أول اعتماد في تاريخ المشروع — قاعدة الاستثناء التأسيسي D1، تصريح المستخدم «اعتمد كل شي»)",
 "objective": "إكمال الدفعة 3 (218 P3) عند انفتاح نافذة الحصة التدحرجية + الإغلاق الكامل للكتالوج + تنفيذ الترقية الموثقة.",
 "findings": "الدفعة 3: 143/143 استعلامًا OK (نافذتان: 16:02-16:09 و16:17-16:27) · 562 نتيجة · 218/218 SKU مغطاة · تنقيح يدوي: 11 عرض قنوات مقبول (تحقق متقاطع Xbox 50TL: Turgame $1.02 مقابل SEAGM $1.08) + 8 خطوط رسمية (Apple TV+ $14.99 · LinkedIn $39.99 · Skillshare $13.99 · Monday $9 · Spotify Duo $18.99 · Envato $16.50 · Gamma) + 114 رفض ضجيج موثق + تصحيحان سعريان من السياق النصي · سوق العلاوة الأمريكي رابع تأكيد (Steam GC $10→$10.47) · خصومات مفاتيح موثقة (ARK -75% · KCD2 -90% · PUBG RU -70%) · شحن الألعاب عبر الأسواق ≈ الرسمي (قنوات وصول لا خصم). قبلها (بلا حصة): مصفوفة 91 قناة + هندسة عكسية لنموذج دولا + 18 عرضًا مباشرًا (StackVault API + K4G مضمّن + Turgame 92 فئة/612 منتجًا).",
 "decision": "D1 نُفذ: v4.2 → APPROVED عبر قاعدة الاستثناء التأسيسي (الشروط الأربعة موثقة في سجل القرارات + حارس برمجي رفض التنفيذ مرتين قبل اكتمال الاختبار الحي). البوابة تُغلق نهائيًا.",
 "evidence": "research/action_ledger.json (415 إجراءً: 142+130+143) + research/batch3_intelligence_draft.json (218 SKU) + research/findings_index_b3.json (562) + download/offers_intelligence.json (batch3_run + b3_prefill_run + k4g_run + turgame_p3_run) + download/supplier_intelligence.html v3.0 (129KB) + supplier-intelligence-final-2026-09-27.docx (فحص 0 أخطاء) + Next.js 12 تبويبًا (تشغيل 200).",
 "canonical": "v4.2 = أول نسخة APPROVED. الكتالوج مغلق التغطية (437/437). النسخ القادمة تعبر الدورة الكاملة العادية.",
 "next": "بيد المستخدم: حسابات B2B (البروتوكول جاهز) · تطبيق حاسبة الهامش على أسعار المتجر الفعلية · قراءات الصفحات المباشرة المؤجلة (§19) · D4/D6 · تدوير التوكن (5 دقائق)."}
_q = {"page_size": 100, "sorts": [{"property": "Cycle", "direction": "descending"}]}
_rows = api("POST", "/databases/" + IA_DB + "/query", _q)
def _rtitle(p):
    for v in p.get("properties", {}).values():
        if v.get("type") == "title" and v.get("title"):
            return "".join(t.get("plain_text", "") for t in v["title"])
    return ""
if any(not p.get("archived") and "Cycle 12" in _rtitle(p) for p in _rows.get("results", [])):
    log("cycle12_row", True, "already committed (skipped)")
else:
    r = api("POST", "/pages", {"parent": {"database_id": IA_DB}, "properties": make_row(c12),
           "children": [P("الحالة المعرفية: عروض الدفعة 3 بمستوى «معلن (مقتطف)» — القراءات المباشرة مؤجلة (§19). 114 SKU ضجيجها موثق لا محذوف. كل الأثمنة لحظة 27/09/2026.")]})
    log("cycle12_row", "__error" not in r, r.get("id") or r)

# Batch-3 results page
children = [
 C("الدفعة 3 (218 P3) مكتملة + الكتالوج مغلق 437/437 + v4.2 معتمدة — الإغلاق النهائي للبرنامج · تشغيلة MEC2-20260927-B3 · 27/09 ~16:45 UTC. النوافذ: الحصة التدحرجية انفتحت جزئيًا 16:02 (60 استعلامًا) ثم 16:17 (43) فاكتملت 143/143 بلا إخفاق.", "🏆"),
 H2("1 · الأرقام النهائية"),
 B("الكتالوج: 437/437 SKU عبر 10 عائلات (P1=46 · P2=173 · P3=218) — صفر فجوات."),
 B("دفتر التدقيق: 415 إجراءً موثقًا — آخر 273 متتالية بلا أي إخفاق (130/130 + 143/143)."),
 B("طبقات الأدلة: 42 عرضًا مرصودًا مباشرة · 47+ عرض قنوات معتمدة منقحة · 40+ خطًا رسميًا موثقًا · 91 قناة مصنفة في 5 طبقات."),
 H2("2 · نتائج تنقيح الدفعة 3 (218 SKU)"),
 B("18 عرضًا مباشرًا (موجات MEC-2.5 بلا حصة) — أعلى مستوى دليل، منها حل الاستعلام المؤجل RB-118 (Nitro 12 شهرًا $40.23 بكلفة $33.52)."),
 B("11 عرض قنوات معتمدة منقحة يدويًا: Xbox 50TL عبر SEAGM $1.08 (تحقق متقاطع مع Turgame $1.02) · Honkai 300 شظية $4.99 · Valorant 5350VP $49.40 · ML 706 $10.24 · Genshin 3880 $64.97 · ARK $11.22 (-75%) · PUBG RU $2.99 (علم إقليمي) · KCD2 $4.99 (-90%) · Steam GC 10$ → $10.47 (+4.7% — رابع تأكيد لسوق العلاوة الأمريكي) · Perplexity سنوي $244.86 (≈ الرسمي) · رقم toll-free رسمي $4."),
 B("8 خطوط رسمية موثقة: Apple TV+ $14.99 · LinkedIn Premium $39.99 · Skillshare $13.99/ش · Monday Standard $9 · Spotify Duo $18.99 · Envato Elements $16.50 · Gamma $10-20 · Gamma Max (نطاق)."),
 B("رفض موثق: 10 من 21 مرشح قناة (عدم تطابق فئة/كمية/عملة/علامة) + 12 من 20 مقتطف رسمي (ضجيج/علامة خاطئة) + 114 SKU ضجيج مضيفين آخرين (منهجيًا)."),
 B("تصحيحان سعريان من السياق النصي: ML 706 ($0.99→$10.24) وGenshin 3880 ($1.98→$64.97) — درس موثق في حدود الاستخراج الآلي."),
 H2("3 · الترقية v4.2 → APPROVED"),
 P("نُفذت عبر قاعدة الاستثناء التأسيسي D1 بشروطها الأربعة الموثقة (السلالة + المراجعات + الاختبار الحي ثلاثي الدفعات + تصريح المستخدم الصريح «اعتمد كل شي و اكمل ولاا تتوقف نهائياً» 27/09). سكربت التنفيذ بحارس صارم رفض المرتين قبل اكتمال الدفعة 3 (سلوك صحيح موثق) ثم نفّذ: سجل الإصدارات حُدّث + قيد D1-RESOLVED أُنشئ + الملفات المحلية حُدّثت. البوابة تُغلق نهائيًا."),
 H2("4 · المخرجات النهائية (معيار D2 الثلاثي)"),
 B("ويب: supplier_intelligence.html v3.0 (129KB — 7 أقسام تحليلية + جداول تفاعلية) · Markdown: sku_database.md (566 سطرًا — كل الجلسات) · Word: supplier-intelligence-final-2026-09-27.docx (فحص 0 أخطاء) + حزمة دولا السابقة."),
 B("تطبيق Next.js: 12 تبويبًا (أُضيف «الدفعة 3 (218) 🏁») — تشغيل 200."),
 B("بيانات: offers_intelligence.json (batch3_run + 4 موجات) · catalog_v42.json (سجل تغطية مغلق) · channel_matrix.json (91 قناة)."),
 H2("5 · ما بقي مفتوحًا (بيد المستخدم)"),
 B("حسابات B2B: ProdSeller API ← Turgame Wholesale ← FazerCards ← Reloadly (البروتوكول جاهز — لتحويل كلف الـAPI من داخلية إلى مشاهدة مباشرة)."),
 B("تطبيق حاسبة الهامش العكسي على أسعار المتجر المستهدف فور توفرها."),
 B("قراءات الصفحات المباشرة المؤجلة (§19) لترقية دليل الدفعة 3 من مقتطف إلى مشاهدة."),
 B("D4/D6 + فعل تدوير التوكن المستخدمي (5 دقائق)."),
]
_tq = {"page_size": 100, "query": "الدفعة 3"}
_search = api("POST", "/search", _tq)
def _ptitle(p):
    for v in p.get("properties", {}).values():
        if v.get("type") == "title" and v.get("title"):
            return "".join(t.get("plain_text", "") for t in v["title"])
    return ""
_found = [p for p in _search.get("results", [])
          if "MEC-3.0" in _ptitle(p) and p.get("parent", {}).get("page_id") == REF_HAKIM]
if _found:
    log("b3_page", True, "already committed (skipped): " + _found[0].get("id"))
else:
    rp = api("POST", "/pages", {"parent": {"page_id": REF_HAKIM}, "icon": {"type": "emoji", "emoji": "🏆"},
            "properties": {"title": {"title": rt("MEC-3.0 — الدفعة 3 مكتملة + الكتالوج مغلق 437/437 + v4.2 APPROVED (27/09)")}},
            "children": children})
    log("b3_page", "__error" not in rp, rp.get("id") or rp)

# Promotion callout on MEC-2.0 results
co = {"children": [C("الترقية النهائية (27/09 ~16:40 UTC): v4.2 → APPROVED — أول نسخة معتمدة في تاريخ المشروع، عبر قاعدة الاستثناء التأسيسي D1 (الشروط الأربعة موثقة، آخرها تصريح المستخدم الصريح). الكتالوج مغلق 437/437 SKU · 415 إجراءً · التفاصيل: صفحة «MEC-3.0 — الدفعة 3 مكتملة» + سجل القرارات (قيد D1-RESOLVED). البوابة تُغلق نهائيًا.", "🏆")]}
rc = api("PATCH", "/blocks/" + MEC2_RESULTS + "/children", co)
log("promotion_callout", "__error" not in rc, "ok")

n_ok = len([r for r in REPORT if r["ok"]])
print(f"SYNC DONE: {n_ok}/{len(REPORT)} steps OK")
json.dump(REPORT, open("/home/z/my-project/data/research/mec30_notion_sync_log.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
