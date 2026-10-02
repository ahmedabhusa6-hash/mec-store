#!/usr/bin/env python3
"""MEC-2.4 Notion sync — Channel matrix (91) + Dolaa reverse-engineering package (2026-09-27 ~13:40).
Commits: (1) Cycle-11 row in Interaction Archive, (2) MEC-2.4 child page under the
Governing Reference, (3) dated callout on MEC-2.0 results page (economics layer).
Governance: NO version promotion in this sync — v4.2 stays Candidate/Promotion-Ready
even though the user's approval word was received («اعتمد كل شي»): promotion is applied
programmatically only AFTER batch-3 completes (live multi-batch test condition), in the
final wrap-up sync. This page states that honestly."""
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
LOG_F = open("/home/z/my-project/data/research/mec24_notion_sync_log.json", "w", encoding="utf-8")

REF_HAKIM = "3e658a07-79e8-81c4-9cdd-d7b74626d61f"       # المرجع الحاكم
MEC2_RESULTS = "3e858a07-79e8-8114-9eaa-e89e40d0ef56"    # نتائج MEC-2.0 (اقتصاديات التوريد)
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

# ---------------- Step 3: Cycle 11 row ----------------
c11 = {"title": "Cycle 11 — MEC-2.4 Channel Matrix (91) + Dolaa-model Reverse Engineering (quota-free)",
 "actor": "z.ai Runtime (Super Z)",
 "stage": "ChatGPT Analysis", "cycle": 11, "date": "2026-09-27",
 "status": "Committed",
 "version": "v4.2 Candidate — Promotion-Ready (كلمة اعتماد المستخدم استُلمت «اعتمد كل شي» — الترقية تُطبَّق بعد اكتمال الدفعة 3)",
 "objective": "تنفيذ قائمة الانتظار أثناء استمرار حجب الحصة (477 منذ ~02:10 — نافذة طويلة): مصفوفة تقييم القنوات الشاملة (البند 5 من القائمة) + الهندسة العكسية لنموذج دولا (البند 6) + محاولة رصد المتجر مباشرة.",
 "findings": "مصفوفة 91 قناة: 31 كيان سجل §19 مصنفين في 5 طبقات (تصنيع 5 / جملة 5 / تجزئة 16 / ثقة 3 / طرق 2) + 3 مكتشفات (API خلفي StackVault · AiVerseXBot · Gt_Verified) + 57 قناة سوق/رسمية بالعروض. الهندسة العكسية لنموذج دولا: شجرة فرضيات H1-H4 مرجحة بالأدلة (H2 الجملة/API الأقوى: 274 كلفة مرصودة؛ H1 التحكيم الإقليمي قوية: PSN لبنان $9.07، Spotify هندي $0.79/ش) + حاسبة هامش عكسي (ChatGPT: أرضية $2.80 / مستقر $10.67 / رسمي $20 — متجر يبيع $6.67 = هامش 42-58% بطبقة هشة) + قانون الأرضيات (لا كسر بإطراد: هوية مختلفة أو حرق رأس مال أو احتيال) + الحكم المركب: محفظة توريد مركبة إجبارية — لا قناة واحدة تفسّر كتالوجًا عريضًا. محاولة رصد دولا مباشرة: النطاقات المرشحة كلها متوقفة (dolaa.com = parked) — موثق بصدق، النموذج مبني على القرائن.",
 "decision": "لا قرار حوكمي جديد في هذه المزامنة. كلمة الاعتماد («اعتمد كل شي» 27/09) سُجلت كشرط D1 الرابع مستوفى — الترقية الفعلية v4.2→Approved تُطبَّق في مزامنة الإغلاق بعد اكتمال الدفعة 3 (شرط الاختبار الحي متعدد الدفعات).",
 "evidence": "download/channel_matrix.json (91 قناة) + supply_chain_economics.md §11 + sku_database.md قسم MEC-2.4 + supplier_intelligence.html v2.4 (قسم chmatsec تفاعلي) + supplier-intelligence-dolaa-2026-09-27.docx (فحص 0 أخطاء) + Next.js تبويب «مصفوفة 91 قناة + دولا» (tsc نظيف، تشغيل 200).",
 "canonical": "لا ترقية بعد. إضافة معرفية: تصنيف طبقي كامل لمنظومة القنوات المرصودة + أول حاسبة هامش عكسية قابلة للتطبيق على أي متجر تجزئة خليجي فور توفر أسعاره.",
 "next": "مراقبة الحصة (فحوص دورية — 24 فحصًا حتى 13:26 كلها محجوبة) ← عند الفتح: الـ15 المؤجلة ← 143 استعلام الدفعة 3 ← تنقيح ← دمج ← الترقية v4.2→Approved (الشرط الرابع مستوفى بكلمة المستخدم) + الإغلاق الثلاثي D2 + المزامنة النهائية."}

_q = {"page_size": 100, "sorts": [{"property": "Cycle", "direction": "descending"}]}
_rows = api("POST", "/databases/" + IA_DB + "/query", _q)
def _rtitle(p):
    for v in p.get("properties", {}).values():
        if v.get("type") == "title" and v.get("title"):
            return "".join(t.get("plain_text", "") for t in v["title"])
    return ""
_existing = [p for p in _rows.get("results", []) if not p.get("archived") and "Cycle 11" in _rtitle(p)]
if _existing:
    log("cycle11_row", True, "already committed (skipped): " + _existing[0].get("id"))
else:
    row11 = {"parent": {"database_id": IA_DB}, "properties": make_row(c11),
             "children": [P("الحالة المعرفية: التصنيف الطبقي مبني على رصد مباشر (HTTP 200 + معاينات + API خلفي) بتاريخ 27/09؛ الملاءمة لنموذج دولا = استنتاج تحليلي موسوم. المتجر محل السؤال غير مرصود مباشرة (النطاقات متوقفة) — النموذج قرائني لا محاسبي، والحاسبة جاهزة للتطبيق فور توفر قائمة أسعار المتجر الفعلية.")]}
    r11 = api("POST", "/pages", row11)
    log("cycle11_row", "__error" not in r11, r11.get("id") or r11)

# ---------------- Step 4: MEC-2.4 child page ----------------
children = [
 C("حزمة MEC-2.4 (27/09 ~13:40 UTC): مصفوفة تقييم 91 قناة + الهندسة العكسية لنموذج «دولا» — تنفيذ البندين 5 و6 من قائمة الانتظار أثناء حجب الحصة (HTTP خالص + تجميع أدلة التشغيلات 1-3). إجابة سؤال «كم فائدتهم وكيف يشترون ويبيعون» على مستوى كل قناة.", "🧮", "blue_background"),
 H2("1 · المصفوفة — 91 قناة في 5 طبقات"),
 P("31 كيان سجل §19 (كلها حية HTTP 200) صُنفت: 5 تصنيع (مصانع حسابات + مفاتيح رمادية) · 5 جملة/توزيع (API + رصيد مسبق) · 16 تجزئة (منظمة + آلية + فردية) · 3 ثقة/ضمان (Escrow) · 2 بائعو طرق. + 3 مكتشفات جديدة (الواجهة الخلفية StackVault بحقل الكلفة · بوت طلبات AiVerseXBot · بوت جملة Gt_Verified). + 57 قناة سوق/رسمية ظهرت في العروض الموثقة (Eneba وGGSel وG2A وZ2U وAiralo والقنوات الرسمية…)."),
 P("الدلالة البنيوية: ثلثا المنظومة الرمادية طبقات بيع لا إنتاج — الإنتاج (المصانع) طبقة ضيقة مركزة، والقيمة الاقتصادية تتولد في التوزيع. أرخص مرساة لكل كيان تُظهر سلّم الكلفة: التصنيع من $0.02 (حسابات Outlook بالجملة) · الجملة $0.14-0.65 · التجزئة المنظمة $2.80-12 · الأسواق حول الاسمي (خصم صغير أو علاوة — بطاقات Steam الأمريكية فوق الاسمي +8.5%)."),
 H2("2 · شجرة فرضيات التزويد — مرجّحة بالأدلة"),
 B("H1 التحكيم الإقليمي — دليل قوي [مرصود]: PSN لبنان $9.07/$10 · Spotify هندي $0.79/شهر · Xbox GPU إقليمي $4-8.4 · خصومات TR/AR 38-46%. يغطي: البطاقات + الألعاب + Spotify. استدامة عالية (فروق بنية تعرفة الناشر)."),
 B("H2 الجملة/API — أقوى دليل [مرصود مباشرة]: 274 كلفة داخلية (ChatGPT من $2.80 · Office365 سنة $0.21) + إعلان خصم API حتى 35%. يغطي: كل AI/SaaS + البرمجيات. الاستدامة الأعلى — نموذج الشركة نفسه."),
 B("H3 التصنيع الرمادي — دليل متوسط-قوي: Win11 €1.03 · Office2024 €0.56 (تقارب مصدرين) · SheerID موثقة نصًا · UPI نجاح 1-2%. يغطي: المفاتيح + الحسابات الهشة. استدامة هشة — رُصد الترقيع فعليًا (Pixel 12→6 أشهر)."),
 B("H4 التقسيم المؤسسي — دليل متوسط: Canva 500-لوحة $2.50/مقعد · MS365 $0.21 · Duolingo $0.50. يغطي العائلات التعليمية. استدامة متوسطة."),
 H2("3 · حاسبة الهامش العكسي (مرسيات مرصودة 25-27/09)"),
 B("ChatGPT Plus شهر: أرضية $2.80 / «مستقر بضمان» $10.67 / رسمي $20 — متجر يبيع $6.67 هامشه 42-58% (طبقة هشة)؛ يبيع $12 هامشه 11% (طبقة ضمان كامل): الرخيص الموثوق ضد الرخيص الهش = فرق طبقة كلفة لا كفاءة متجر."),
 B("Netflix شهر: كلفة ≈$3.33 (بيع StackVault $3.99 ÷ 1.2) / رسمي $26.99 · Spotify: $0.79 هندي سنوي / $3.74 مستقر / $12.99 رسمي."),
 B("MS365 سنة: $0.21 كلفة API / $8.33 مستقر / $129.99 رسمي · Office 2024: $0.60 رمادي / $2.63 ضمان 10 سنوات / $249.99 · Xbox GPU: $4 إقليمي / $14.09 سنة API / $22.99 رسمي · PSN $10: $9.07 لبنان."),
 H2("4 · قانون الأرضيات + الحكم المركب"),
 P("لا كسر للأرضيات بإطراد: (1) الجملة الشرعية خصمها 1-15% من الاسمي فقط · (2) أرضيات المصانع مقيدة بكلفة حدية (UPI 1-2%) · (3) لا كيان في الـ91 يبيع كل شيء أرخص من الجميع · (4) من يعرض تحت الأرضيات = هوية SKU مختلفة أو حرق رأس مال أو احتيال — الأنماط الثلاثة موثقة."),
 P("الحكم المركب: المحفظة المركبة إجبارية بنيويًا — عمود جملة/API للعائلات الرقمية + تحكيم إقليمي للبطاقات + تقسيم مؤسسي للتعليمية + تصنيع داخلي للهوامش القصوى فقط. الدليل البنيوي: StackVault نفسه يظهر موردين متعددين في كلفه الداخلية (CapCut: $0.14 جملة ProdSeller لكن كلفته $1.29 = يتزود بطبقة أعلى)."),
 H2("5 · حدود المعرفة (إلزامية)"),
 B("المتجر محل السؤال (دولا) غير مرصود مباشرة — النطاقات المرشحة متوقفة (فُحصت 27/09) — النموذج قرائني، والحاسبة جاهزة للتطبيق فور توفر الأسعار الفعلية."),
 B("كل الأسعار معلنة لا معاملاتية · كلف الـAPI داخلية غير قابلة للتدقيق الخارجي [بحاجة لحساب B2B] · الهوامش إجمالية قبل احتياطي الاستبدال ورسوم المقاصة والاكتساب · السوق سريع الدوران (أرقام لحظة 25-27/09)."),
 H2("6 · المخرجات (معيار D2 الثلاثي)"),
 B("ويب: supplier_intelligence.html v2.4 (قسم مصفوفة تفاعلي 34 صفًا) · Markdown: supply_chain_economics.md §11 + sku_database.md MEC-2.4 · Word: supplier-intelligence-dolaa-2026-09-27.docx (فحص الجودة: 0 أخطاء) · بيانات: channel_matrix.json · تطبيق Next.js: تبويب «مصفوفة 91 قناة + دولا» (10 تبويبات، تشغيل 200)."),
]

_tq = {"page_size": 100, "query": "مصفوفة"}
_search = api("POST", "/search", _tq)
def _ptitle(p):
    for v in p.get("properties", {}).values():
        if v.get("type") == "title" and v.get("title"):
            return "".join(t.get("plain_text", "") for t in v["title"])
    return ""
_found = [p for p in _search.get("results", [])
          if "MEC-2.4" in _ptitle(p) and "مصفوفة" in _ptitle(p)
          and p.get("parent", {}).get("page_id") == REF_HAKIM]
if _found:
    log("mec24_page", True, "already committed (skipped): " + _found[0].get("id"))
else:
    page = {"parent": {"page_id": REF_HAKIM}, "icon": {"type": "emoji", "emoji": "🧮"},
            "properties": {"title": {"title": rt("MEC-2.4 — مصفوفة 91 قناة + الهندسة العكسية لنموذج دولا (27/09)")}},
            "children": children}
    rp = api("POST", "/pages", page)
    log("mec24_page", "__error" not in rp, rp.get("id") or rp)

# ---------------- Step 5: dated callout on MEC-2.0 results ----------------
co = {"children": [C("تحديث MEC-2.4 (27/09 ~13:40 UTC): أُضيفت طبقة تحليلية فوق اقتصاديات التوريد — مصفوفة 91 قناة مصنفة في 5 طبقات تشغيلية + الهندسة العكسية لنموذج متجر على نمط دولا (شجرة فرضيات H1-H4 مرجحة بالأدلة + حاسبة الهامش العكسي + قانون الأرضيات). الخلاصة التطبيقية للقسم أدناه: كل جداول الهوامش تبقى صالحة، وتُقرأ الآن مع تصنيف القناة-التي-تخدم-كل-طبقة. التفاصيل: صفحة «MEC-2.4 — مصفوفة 91 قناة» + supply_chain_economics.md §11.", "🧮", "blue_background")]}
rc = api("PATCH", "/blocks/" + MEC2_RESULTS + "/children", co)
log("mec2_results_callout", "__error" not in rc, rc.get("results", [{}])[0].get("id") if rc.get("results") else rc)

finalize()
n_ok = len([r for r in REPORT if r["ok"]])
print("SYNC DONE: %d/%d steps OK" % (n_ok, len(REPORT)))
