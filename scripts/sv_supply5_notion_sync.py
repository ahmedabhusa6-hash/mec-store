#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-5 Notion sync — يوثّق مصادر التوريد السبعة مباشرة في Notion عبر API.

المتطلبات: NOTION_TOKEN في متغير البيئة أو في /home/z/my-project/.env
الاستيراد:  python3 scripts/sv_supply5_notion_sync.py
الأعراف:    أعراف المشروع نفسها (حارس خامل scan-based · لا تعديل تاريخ · لا ترقية إصدارات ·
            Cycle 13 في أرشيف التفاعلات · صفحة نتائج تحت المرجع الحاكم · كالوت مؤرخ على MEC-2.0)."""
import json, os, ssl, sys, time, urllib.request, urllib.error

sys.path.insert(0, "/home/z/my-project/scripts")
from sv_supply5_data import SUPPLIERS, CATALOG, VERIFICATION_SUMMARY

# ---------- config ----------
REF_HAKIM = "3e658a07-79e8-81c4-9cdd-d7b74626d61f"   # المرجع الحاكم (الأصل)
MEC2_RESULTS = "3e858a07-79e8-8114-9eaa-e89e40d0ef56"  # صفحة نتائج MEC-2.0 (الكالوت المؤرخ)
IA_DB = "e844ab12-d846-4974-9651-0892464966e5"          # قاعدة أرشيف التفاعلات
AR_DATE = "30/09/2026"
LOG_PATH = "/home/z/my-project/research/sv_supply5_notion_sync_log.json"

def _load_token():
    tok = os.environ.get("NOTION_TOKEN", "")
    if tok:
        return tok
    env_path = "/home/z/my-project/.env"
    if os.path.exists(env_path):
        for line in open(env_path, encoding="utf-8"):
            if line.strip().startswith("NOTION_TOKEN="):
                return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    print("❌ لا يوجد NOTION_TOKEN — أضف السطر التالي إلى /home/z/my-project/.env ثم أعد التشغيل:")
    print('   NOTION_TOKEN=secret_توكنك_هنا')
    print("   (التوكن السابق أُزيل مع إعادة بناء البيئة — تدوير D5 معلّق على المستخدم)")
    return None

TOKEN = _load_token()
if not TOKEN:
    sys.exit(1)

BASE = "https://api.notion.com/v1"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
REPORT = []

def log(section, ok, detail):
    REPORT.append({"section": section, "ok": bool(ok), "detail": str(detail)[:400]})
    print(("[OK] " if ok else "[!!] ") + section + " :: " + str(detail)[:150])

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
        except Exception:
            time.sleep(1.5 ** attempt)
    return {"__error": "max_retries"}

# ---------- block builders ----------
def rt(t): return [{"text": {"content": str(t)[:1900]}}]
def P(t): return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rt(t)}}
def H2(t): return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": rt(t)}}
def B(t): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rt(t)}}
def C(t, icon="📦", color="blue_background"):
    return {"object": "block", "type": "callout", "callout": {"rich_text": rt(t), "icon": {"type": "emoji", "emoji": icon}, "color": color}}
def TBL(header, rows):
    cells = [[{"text": {"content": str(c)[:380]}} for c in header]]
    cells += [[{"text": {"content": str(c)[:380]}} for c in r] for r in rows]
    return {"object": "block", "type": "table", "table": {
        "table_width": len(header), "has_column_header": True, "has_row_header": False,
        "children": [{"object": "block", "type": "table_row", "table_row": {"cells": row}} for row in cells]}}

def append_children(page_id, blocks, note):
    """Append blocks in chunks of 100 (API limit)."""
    for i in range(0, len(blocks), 100):
        r = api("PATCH", f"/blocks/{page_id}/children", {"children": blocks[i:i+100]})
        if "__error" in r:
            log(note, False, r); return False
    log(note, True, f"{len(blocks)} blocks"); return True

def page_title(p):
    for v in p.get("properties", {}).values():
        if v.get("type") == "title" and v.get("title"):
            return "".join(t.get("plain_text", "") for t in v["title"])
    return ""

def find_child_page(parent_id, title_kw):
    """Scan-based exact guard (per b3_notion_sync incident lesson)."""
    q = {"page_size": 100, "query": title_kw}
    res = api("POST", "/search", q)
    for p in res.get("results", []):
        if p.get("archived"): continue
        if p.get("parent", {}).get("page_id") == parent_id and title_kw in page_title(p):
            return p
    return None

# ---------- 1) identity ----------
me = api("GET", "/users/me")
log("identity", "__error" not in me, me.get("name") or me)
if "__error" in me:
    sys.exit(1)

# ---------- 2) Cycle 13 row ----------
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
        except Exception:
            pass
        used.add(pk)
    return out

c13 = {
 "title": "Cycle 13 — SV-SUPPLY-5: توثيق مصادر التوريد السبعة (تحقق حيّ) + مورّدان جديدان + حزمة Notion",
 "actor": "z.ai Runtime (Super Z)", "stage": "ChatGPT Analysis", "cycle": 13, "date": "2026-09-30",
 "status": "Committed",
 "version": "v4.2 — APPROVED (دورة كاملة عادية بعد الاعتماد — بلا ترقية)",
 "objective": "استخراج مصادر التوريد بدقة لكل مورد طلبه المستخدم (7 كيانات فريدة) + التحقق الحيّ من stackvault.shop وجميع الروابط + التوثيق في Notion.",
 "findings": "تحقق حيّ 30/09: 24 رابطًا حيًا من 27 هدفًا + 8 أهداف تعمق · stackvault.shop حيّ (Netlify، كتالوج 345 منتجًا: ps_ 314 = 91%، mr_ 30 = 8.7%) · ProdSellerOfficial الآن 5,023 مشتركًا (كان 681 في 27/09) وprodseller.io ميت · teamsoclo: القناة 159 مشتركًا + 3 نطاقات فرعية حية والجذر NXDOMAIN · Evo_Era يبيع Gemini 18m بـ$0.85 (SV يشتري بـ$0.39) · HitMeow: Plus VIP $10.77 (باع 4,157) وK12 $4.58 · AISUBSID: جملة ChatGPT Plus $2.50 (28/09) وGemini $0.45-0.55 · جديد: storeBatmanBot = عنقود إندونيسي (بوت + قناة 52 مشتركًا بلا كتالوج علني + مالك @Chulopapirel + قناة إثباتات @proofbatman) · جديد: AiVerseX Hub = 22,937 مشتركًا (الأكبر) — Gemini فلاش $0.39 = تكلفة SV، Office 365 بـ$0.29، Adobe Express $0.40، مخزون Gemini 3,804 وحدة.",
 "decision": "لا قرار إصدار — دورة توثيق. توصية تنفيذية: عينة من AiVerseX (منافس Gemini/Adobe مباشر) + ورقة ضغط AISUBSID على ProdSeller (فجوة 56%) + استفسار مباشر من storeBatmanBot (لا كتالوج علني).",
 "evidence": "research/sv_supply5_live_check.json (27 هدفًا) + sv_supply5_deepdive.json + sv_supply5_storebatman.json + sv_supply5_dated_messages.json + sv_products_20260930.json (345) + download/مصادر_التوريد_Notion/ (10 ملفات: لوحة قيادة + 7 موردين + CSV + تعليمات).",
 "canonical": "مصادر التوريد السبعة موثقة بروابط مؤكدة حيًا وأسعار مؤرخة — المرجع التشغيلي الجديد لمفاوضات SV.",
 "next": "بيد المستخدم: استيراد الحزمة إلى Notion (أو تزويدي بـ NOTION_TOKEN للمزامنة المباشرة — التوكن القديم أُزيل مع إعادة بناء البيئة) · استفسار مباشر من storeBatmanBot · عينة AiVerseX · تدوير D5.",
}
_q = {"page_size": 100, "sorts": [{"property": "Cycle", "direction": "descending"}]}
_rows = api("POST", "/databases/" + IA_DB + "/query", _q)
if any(not p.get("archived") and "Cycle 13" in page_title(p) for p in _rows.get("results", [])):
    log("cycle13_row", True, "already committed (skipped)")
else:
    r = api("POST", "/pages", {"parent": {"database_id": IA_DB}, "properties": make_row(c13),
           "children": [P("الحالة المعرفية: كل الأسعار «معلنة (قناة عامة)» بتواريخها · التحقيق سلبي صرف (GET عام فقط) · الكتالوج 345 منتجًا لحظة 30/09.")]})
    log("cycle13_row", "__error" not in r, r.get("id") or r)

# ---------- 3) main results page under المرجع الحاكم ----------
MAIN_TITLE = "SV-SUPPLY-5 — مصادر التوريد الموثقة: 7 موردين (تحقق حيّ 30/09)"
main_children = [
 C(f"توثيق مصادر التوريد للموردين السبعة المطلوبين، بروابط مؤكدة حيًا بتاريخ {AR_DATE} وأسعار مؤرخة من قنوات الموردين أنفسهم · المنهجية: OSINT سلبي صرف (GET عام فقط، صفر تفاعل) · النطاق: {VERIFICATION_SUMMARY['checked']}.", "📊"),
 H2("1 · التحقق من الرابط الرئيسي (stackvault.shop)"),
 TBL(["البند", "النتيجة"], [
   ["الرابط", "https://stackvault.shop/"],
   ["الحالة", "✅ حيّ — HTTP 200"],
   ["العنوان", CATALOG["title"]],
   ["البنية التحتية", CATALOG["server"]],
   ["الكتالوج الحيّ", f"{CATALOG['catalog_n']} منتجًا ({CATALOG['census']['ps']} ps_ عبر ProdSeller = {CATALOG['ps_pct']}% · {CATALOG['census']['mr']} mr_ عبر Evo Era = {CATALOG['mr_pct']}% · {CATALOG['in_stock']} بمخزون)"],
   ["واجهة الكتالوج", CATALOG["catalog_api"]],
 ]),
 H2("2 · خريطة سلسلة التوريد"),
 P("Team Sóc Lọ (مصنّع فيتنامي — gpt.teamsoclo.site) ──صنع حصص AI──▶ ProdSeller (موزع API — t.me/ProdSellerOfficial) ──ps_ 91%──▶ StackVault (stackvault.shop)"),
 P("Evo Era ──mr_ 8.7% (أكواد ناشئات + مزارع هندية، تسليم يدوي)──▶ StackVault · ProdSeller وسيط فوق teamsoclo (تحميل 15–25% على أغلى العائلات)."),
 P("البدائل المُقيَّمة: HitMeowShop (فيتنام) · AISUBSID (إندونيسيا) — المرشحان الجديدان: storeBatmanBot (إندونيسيا) · AiVerseX Hub (22,937 مشتركًا)."),
 H2("3 · جدول الموردين"),
 TBL(["#", "المورد", "التصنيف", "القناة", "البوت"], [
   [str(s["order"]), s["name"], s["classification"],
    next((x["url"] for x in s["sources"] if "القناة" in x["label"]), s["sources"][0]["url"]),
    next((x["url"] for x in s["sources"] if "Bot" in x["url"].split("/")[-1] or "bot" in x["url"].split("/")[-1]), "—")]
   for s in SUPPLIERS]),
 H2("4 · نتائج التحقق المباشر"),
 B(f"{VERIFICATION_SUMMARY['live_ok']} — " + " · ".join(VERIFICATION_SUMMARY["dead"])),
 B("تنبيهات أسماء خاطئة: " + " · ".join(VERIFICATION_SUMMARY["false_positives"])),
 H2("5 · الخلاصة التنفيذية"),
 B("ورقتا ضغط جاهزتان: AISUBSID (ChatGPT Plus جملة $2.50 مقابل تكلفة SV $5.72+ = وفر حتى 56%) · AiVerseX (فلاش Gemini $0.39 = تكلفة SV بالضبط — أي فلاش أقل يعني إعادة تسعير فورية)."),
 B("الفرصة الاستراتيجية: التعاقد المباشر مع teamsoclo كموزع يقطع وسيط ProdSeller (~20% على 23 منتج رصيد AI)."),
 B("المرشحان: AiVerseX جاهز لعينة فورية · storeBatmanBot يحتاج استفسارًا مباشرًا من البوت (بلا كتالوج علني)."),
 P("التفاصيل الكاملة لكل مورد في الصفحات الفرعية السبع أدناه + حزمة الملفات القابلة للاستيراد: download/مصادر_التوريد_Notion/ (لوحة قيادة + 7 صفحات + قاعدة بيانات CSV + تعليمات)."),
]

existing_main = find_child_page(REF_HAKIM, "SV-SUPPLY-5")
if existing_main:
    log("main_page", True, f"already committed (skipped): {existing_main['id']}")
    main_id = existing_main["id"]
else:
    rp = api("POST", "/pages", {"parent": {"page_id": REF_HAKIM},
            "icon": {"type": "emoji", "emoji": "📊"},
            "properties": {"title": {"title": rt(MAIN_TITLE)}},
            "children": main_children[:100]})
    log("main_page", "__error" not in rp, rp.get("id") or rp)
    if "__error" in rp: sys.exit(1)
    main_id = rp.get("id")
    if len(main_children) > 100:
        append_children(main_id, main_children[100:], "main_page_overflow")

# ---------- 4) seven supplier sub-pages ----------
for s in SUPPLIERS:
    title = f"{s['order']:02d} · {s['name']} — {s['name_ar']}"
    existing = find_child_page(main_id, title[:40])
    if existing:
        log(f"page_{s['key']}", True, "already committed (skipped)"); continue
    blocks = [
        C(f"التصنيف: {s['classification']} · تحقق حيّ {AR_DATE} · المنهجية: GET عام فقط", s["icon"]),
        H2("الدور في سلسلة توريد StackVault"), P(s["role"]),
        H2("البطاقة التعريفية"),
        TBL(["البند", "القيمة"], [[k, v] for k, v in s["identity"].items()]),
        H2("مصادر التوريد الدقيقة (روابط مؤكدة)"),
        TBL(["القناة", "الرابط", "حالة التحقق", "ملاحظات"],
            [[x["label"], x["url"], x["status"], x["note"]] for x in s["sources"]]),
        P(f"حصة التوريد لـ StackVault: {s['supply_share']}"),
        H2("الأسعار الموثقة (مؤرخة)"),
        TBL(["المنتج/العرض", "السعر", "التاريخ", "المصدر"], [list(p) for p in s["prices"]]),
        H2("الشروط وأطر العمل"), P(s["terms"]),
        H2("نقاط التفاوض والفرص"),
    ] + [B(b) for b in s["bargain"]] + [
        H2("المخاطر وملاحظات التحقق"), P(s["risks"]),
    ]
    r = api("POST", "/pages", {"parent": {"page_id": main_id},
            "icon": {"type": "emoji", "emoji": s["icon"]},
            "properties": {"title": {"title": rt(title)}},
            "children": blocks[:100]})
    log(f"page_{s['key']}", "__error" not in r, r.get("id") or r)
    if "__error" not in r and len(blocks) > 100:
        append_children(r["id"], blocks[100:], f"page_{s['key']}_overflow")
    time.sleep(0.5)

# ---------- 5) dated callout on MEC-2.0 results ----------
co_text = (f"تحديث {AR_DATE} — SV-SUPPLY-5: توثيق مصادر التوريد السبعة (ProdSeller · teamsoclo · Evo Era · HitMeowShop · AISUBSID · storeBatmanBot · AiVerseX Hub) "
           "بتحقق حيّ 24/27 رابطًا + أسعار مؤرخة + مورّدان جديدان (AiVerseX Hub 22.9K مشتركًا، فلاش Gemini $0.39 = تكلفة SV) — "
           "التفاصيل: صفحة «SV-SUPPLY-5 — مصادر التوريد الموثقة» + Cycle 13 في أرشيف التفاعلات.")
me_children = api("GET", f"/blocks/{MEC2_RESULTS}/children", None) if False else api("GET", f"/blocks/{MEC2_RESULTS}/children")
already = any("SV-SUPPLY-5" in json.dumps(b.get("callout", {}), ensure_ascii=False) for b in me_children.get("results", []))
if already:
    log("mec2_callout", True, "already committed (skipped)")
else:
    rc = api("PATCH", f"/blocks/{MEC2_RESULTS}/children", {"children": [C(co_text, "📊")]})
    log("mec2_callout", "__error" not in rc, "ok")

# ---------- summary ----------
n_ok = len([r for r in REPORT if r["ok"]])
json.dump(REPORT, open(LOG_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nSYNC DONE: {n_ok}/{len(REPORT)} steps OK — log: {LOG_PATH}")
