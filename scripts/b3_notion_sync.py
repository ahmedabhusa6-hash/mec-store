#!/usr/bin/env python3
"""MEC-2.3 Notion sync — Direct-observation wave commit (2026-09-27 ~05:30).
Commits: (1) Cycle-10 row in Interaction Archive, (2) Direct-wave child page under
the Governing Reference, (3) dated callouts on MEC-2.0 results page (economics layer).
Governance: no version promotion (v4.2 stays Candidate / Promotion-Ready); batch-3
search execution still pending quota — page states this honestly."""
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
LOG_F = open("/home/z/my-project/data/research/mec23_notion_sync_log.json", "w", encoding="utf-8")

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

# ---------------- Step 3: Cycle 10 row ----------------
c10 = {"title": "Cycle 10 — MEC-2.3 Direct-Observation Wave (StackVault cost exposure + 59 direct offers) + Batch-3 launch infrastructure",
 "actor": "z.ai Runtime (Super Z)",
 "stage": "ChatGPT Analysis", "cycle": 10, "date": "2026-09-27",
 "status": "Committed",
 "version": "v4.2 Candidate — Promotion-Ready (unchanged; awaiting user word only)",
 "objective": "تنفيذ «اكمل ولا تتوقف»: إطلاق الدفعة 3 (218 P3) رغم حجب حصة الوظائف البعيدة (477/429 منذ ~02:10) عبر بناء طبقة رصد HTTP مباشرة مستقلة عن الحصة + تجهيز بنية الدفعة 3 الكاملة للإطلاق الفوري عند التصفيير.",
 "findings": "الاكتشاف المركزي: واجهة StackVault الخلفية (decohomz.com/sv-api/products) تكشف حقل كلفة الشراء لـ274/275 منتجًا — أول رؤية مباشرة لسعر توريد بائع تجزئة في تاريخ المشروع. معادلة التسعير: البيع = الكلفة × 1.2 (هامش وسيط 16.7%). سلّم كلفة ChatGPT Plus كاملًا: $2.80 أساسي ← $10.67 ضمان كامل ← $17.14 تجديد رسمي (فارق 6 أضعاف داخل المنتج الواحد). قياسات انتشار حية: Gemini 18M جملة $0.65 ← تجزئة $0.85 (+31%)، Duolingo جملة $0.37 ← تجزئة $0.85 (+130%)، Office 365 كلفة داخلية $0.21 ≈ جملة ProdSeller $0.17 (تقارب مصدرين). Turgame: 117 منتجًا مسعّرًا مباشرة (بطاقات TL بمعدل موحد $2.048/100TL — معدل FX معلّم للتحقق). 59 عرضًا جديدًا بمستوى «مرصود مباشرة» مدمجة في offers_intelligence.json (118/236 SKU بعروض).",
 "decision": "لا قرار حوكمي جديد — الدفعة 3 أُطلقت بتفويض «اكمل» المسبق (خطة الجلسة المنفصلة كانت أصلاً معتمدة). v4.2 تبقى Candidate/Promotion-Ready.",
 "evidence": "research/b3_direct_observations.json (قنوات §19: 122 رسالة) + research/b3_stackvault_api.json (275 منتجًا بالكلفة) + research/b3_turgame_categories.json (117 منتجًا) + download/offers_intelligence.json قسم b3_direct_run + supply_chain_economics.md §10 + sku_database.md قسم MEC-2.3 + supplier_intelligence.html v2.3 + Next.js تبويب «الموجة المباشرة» (tsc نظيف).",
 "canonical": "لا ترقية. إضافة معرفية: كلفة الشراء الجملية لبائع تجزئة رُصدت مباشرة — ترفع دقة كل جداول الهوامش السابقة من «تقديرية» إلى «قابلة للحساب» (اقسم سعر StackVault على 1.2).",
 "next": "عند تصفير الحصة (المراقب يعمل): الـ15 المؤجلة ← تنقيح ← دمج ← 143 استعلام الدفعة 3 ← تنقيح ← دمج ← التحديث النهائي الثلاثي (D2) + Word برامجي شامل."}

# idempotency guard: skip row creation if Cycle-10 row already committed
_q = {"page_size": 100, "sorts": [{"property": "Cycle", "direction": "descending"}]}
_rows = api("POST", "/databases/" + IA_DB + "/query", _q)
def _rtitle(p):
    for v in p.get("properties", {}).values():
        if v.get("type") == "title" and v.get("title"):
            return "".join(t.get("plain_text", "") for t in v["title"])
    return ""
_existing = [p for p in _rows.get("results", []) if not p.get("archived") and "Cycle 10" in _rtitle(p)]
if _existing:
    log("cycle10_row", True, "already committed (skipped): " + _existing[0].get("id"))
else:
    row10 = {"parent": {"database_id": IA_DB}, "properties": make_row(c10),
             "children": [P("الحالة المعرفية: كل أرقام هذه الدورة موسومة [مرصود مباشرة] بتاريخ ولقطة — عدا حقل الكلفة فهو قيمة داخلية لنظام البائع غير قابلة للتدقيق الخارجي [بحاجة للتحقق عبر حساب B2B]. الأسعار إعلانية (لا معاملات منفذة) باستثناء مشتريات مؤكدة يبثها البائعون أنفسهم في قنواتهم.")]}
    r10 = api("POST", "/pages", row10)
    log("cycle10_row", "__error" not in r10, r10.get("id") or r10)

# ---------------- Step 4: Direct-wave child page ----------------
children = [
 C("الموجة المباشرة (MEC-2.3) — كشف كلفة الشراء الجملية + 59 عرضًا مرصودًا مباشرة · تشغيلة MEC2-20260927-B3-DIRECT · 2026-09-27 ~05:00 UTC. الطبقة: HTTP خالص مستقلة عن حصة الوظائف البعيدة (محجوبة 477/429 منذ ~02:10). الدفعة 3 (بحث 143 استعلامًا) جاهزة وتُطلق آليًا عند التصفيير — حالتها موثقة أدناه بصدق.", "🔬", "blue_background"),
 H2("1 · الاكتشاف المركزي — واجهة StackVault الخلفية"),
 P("نقطة النهاية decohomz.com/sv-api/products (المصدر الفعلي لبيانات متجر stackvault.shop) أعادت الكتالوج الكامل: 275 منتجًا، منها 274 بحقل costPrice > 0 — أي أن نظام البائع نفسه يكشف سعر التوريد الذي يشتري به. أول رؤية مباشرة من نوعها في تاريخ المشروع: قبلها كانت أسعار الجملة تُستنتج من فرق الأسعار المعلنة بين الطبقات."),
 P("معادلة التسعير المكتشفة: سعر البيع = كلفة الشراء × 1.2 — هامش موحّد آليًا (الوسيط 16.7%، المتوسط 19.9%، المدى 13–57%). الدلالة الهيكلية: StackVault بائع ناقل (pass-through) لا يسعّر بالسوق — سعره مؤشر نظيف على أسعار الجملة العلوية: اقسم أي سعر عنده على 1.2 تحصل على سعر توريده التقريبي."),
 B("أمثلة محلولة [كلفة ← بيع]: Discord Nitro سنة (ضمان كامل) $33.52 ← $40.23 · Xbox Game Pass Ultimate سنة $14.09 ← $16.91 (تحت الرسمي $22.99 بـ26%) · تجديد ChatGPT Plus رسمي $17.14 ← $20.57 · Office 2024 Pro Key (ضمان 10 سنوات) $2.63 ← $3.16 · Windows 10/11 Pro Key $3.39 ← $4.07 · Gamma Pro 30 يوم $13.71 ← $16.46."),
 H2("2 · سلّم كلفة ChatGPT Plus — البنية السرية للتسعير"),
 P("لأول مرة يُرصد سلّم الكلفة الجملية نفسه (لا أسعار البيع): أساسي $2.80 ← ضمان 6 ساعات $3.85 ← 5 ساعات $5.15 ← ضمان كامل $10.67 ← تجديد رسمي على حساب المشتري $17.14. «نفس المنتج» = فارق 6 أضعاف كلفة بين طبقاته — إعلانات «خصم 85%» تقابلها طبقات هشاشة كاملة، والمشتري الذي يظنه منتجًا واحدًا يشتري في الواقع طبقة مختلفة من السلّم."),
 H2("3 · قياسات حية لانتشار الجملة ← التجزئة (نفس الجلسة)"),
 B("Gemini 18M: جملة ProdSeller $0.65 (25/09) ← تجزئة Evo Era $0.85/وحدة مع مشتريات مؤكدة ×5 في بث الطلبات (26/09 21:41 UTC) = +31%."),
 B("Duolingo Super 12M: حرب أسعار جملة موثقة $0.59 (19/09) ← $0.45 (23/09) ← $0.37 (24/09) ← تجزئة Evo Era $0.85 = +130% فوق الجملة لحظة الرصد."),
 B("Office 365 Plus سنة: كلفة StackVault الداخلية $0.21 ≈ جملة ProdSeller المعلنة $0.17 — مصدران مستقلان يتقاربان على السعر العلوي."),
 B("CapCut: $0.14 جملة ProdSeller ← $1.29 كلفة StackVault ← $1.60 بيعه — سلسلة ثلاثية الطبقات مرئية بالكامل."),
 H2("4 · Turgame — 117 منتجًا مسعّرًا مباشرة (قناة محددة في Notion)"),
 B("بطاقات تركية بمعدل موحد $2.048/100TL عبر كل الفئات (Xbox/GooglePlay/Apple/Amazon/PSN): Xbox 50TL=$1.02 · Apple 25TL=$0.51 · Amazon 100TL=$2.05."),
 B("PSN لبنان 10$ = $9.05 — يطابق مرساتنا المستقلة السابقة $9.07 (تحقق متقاطع ناجح عبر مصدرين)."),
 B("بطاقات أمريكية تحت الاسمي: Xbox USA 5$ = $4.79 (-4.2%) · PSN UAE 10$ = $9.73 (-2.7%) · Xbox FR 5€ = $5.39 (-5.3%)."),
 B("تنبيه صادق: المعدل الضمني لبطاقات TL (48.8 TRY/USD) يخالف أساس الصرف المعتمد في المشروع (34.1) — عُلّم [بحاجة للتحقق] ولم تُحسب على أساسه خصومات القيمة الاسمية لبطاقات TL."),
 H2("5 · حالة الدفعة 3 (218 P3) — التجهيز الكامل"),
 P("143 استعلامًا تغطي 218/218 SKU (تحقق آلي: صفر نواقص، صفر دخيل) جاهزة في batch3_search.py بمعمارية الاستئناف الذاتي المجرّبة (idempotent + salvage + ميزانية زمنية + إيقاف عند 3 إخفاقات متتالية). المراقب (quota_watcher.py) مُرقّى للسلسلة الكاملة: الـ15 المؤجلة ← تجميع الدفعة 2 ← 143 استعلام الدفعة 3 ← تجميع ← توقف عند التنقيح اليدوي. سكربتات ما بعد البحث تحمي العروض المباشرة الحالية من الكتابة فوقها."),
 H2("6 · حدود المعرفة (إلزامية)"),
 B("كل الأسعار إعلانية (لا معاملات منفذة) عدا «مشتريات مؤكدة» يبثها البائعون أنفسهم في قنواتهم — دليل بقاء لا تحقق مستقل."),
 B("حقل costPrice قيمة داخلية لنظام البائع — يُفترض أنه سعر التوريد لكنه غير قابل للتدقيق الخارجي [بحاجة للتحقق عبر حساب B2B]."),
 B("المخزون = 0 لحظة السحب = نفاد لحظي لا توقف بيع (رُصدت إعادة تعبئة خلال ساعات)."),
 B("سوق سريع الدوران: كل القياسات لحظة 27/09 ~05:00 UTC — يحتاج مراقبة دورية للاتجاه لا رقمًا ثابتًا."),
]

_tq = {"page_size": 100, "query": "كشف كلفة الشراء"}
_search = api("POST", "/search", _tq)
def _ptitle(p):
    for v in p.get("properties", {}).values():
        if v.get("type") == "title" and v.get("title"):
            return "".join(t.get("plain_text", "") for t in v["title"])
    return ""
_found = [p for p in _search.get("results", [])
          if "MEC-2.3" in _ptitle(p) and "الموجة المباشرة" in _ptitle(p)
          and p.get("parent", {}).get("page_id") == REF_HAKIM]
if _found:
    log("direct_wave_page", True, "already committed (skipped): " + _found[0].get("id"))
else:
    page = {"parent": {"page_id": REF_HAKIM}, "icon": {"type": "emoji", "emoji": "🔬"},
            "properties": {"title": {"title": rt("MEC-2.3 — الموجة المباشرة: كشف كلفة الشراء + 59 عرضًا مرصودًا (27/09)")}},
            "children": children}
    rp = api("POST", "/pages", page)
    log("direct_wave_page", "__error" not in rp, rp.get("id") or rp)

# ---------------- Step 5: dated callout on MEC-2.0 results (economics) ----------------
co = {"children": [C("تحديث MEC-2.3 (27/09 ~05:00 UTC): طبقة الاقتصاديات أدناه حصلت على أول تدقيق كمي مباشر — واجهة StackVault الخلفية تكشف كلفة الشراء (274 منتجًا): معادلة البيع = الكلفة × 1.2، وسلّم كلفة ChatGPT Plus كاملًا ($2.80 ← $10.67 ← $17.14). التفاصيل المحلولة: صفحة «MEC-2.3 — الموجة المباشرة» + supply_chain_economics.md §10. أرقام القسم الأصلي أدناه تبقى صحيحة كأساس MEC-2.0 وتُقرأ الآن مع الطبقة الكمية الجديدة.", "🔬", "blue_background")]}
rc = api("PATCH", "/blocks/" + MEC2_RESULTS + "/children", co)
log("mec2_results_callout", "__error" not in rc, rc.get("results", [{}])[0].get("id") if rc.get("results") else rc)

finalize()
n_ok = len([r for r in REPORT if r["ok"]])
print("SYNC DONE: %d/%d steps OK" % (n_ok, len(REPORT)))
