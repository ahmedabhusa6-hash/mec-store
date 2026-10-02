#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SV-SUPPLY-5: build Notion-importable package (MD pages + CSV database + instructions)."""
import csv, json, os, sys
sys.path.insert(0, "/home/z/my-project/scripts")
from sv_supply5_data import SUPPLIERS, CATALOG, VERIFICATION_SUMMARY, VERIFY_DATE

PKG = "/home/z/my-project/download/مصادر_التوريد_Notion"
os.makedirs(PKG, exist_ok=True)

AR_DATE = "30/09/2026"

def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")

# ============ 1) Dashboard (master page) ============
rows = []
for s in SUPPLIERS:
    ch = next((x for x in s["sources"] if "t.me/" in x["url"] and "Bot" not in x["url"] or "قناة" in x["label"] or "القناة" in x["label"]), s["sources"][0])
    bot = next((x for x in s["sources"] if "Bot" in x["url"] or "بوت" in x["label"] or "البوت" in x["label"]), None)
    rows.append(
        f"| {s['icon']} {s['order']} | **[{s['name']}](<01_ProdSeller.md>)** |"
        .replace("01_ProdSeller.md", f"{s['order']:02d}_{s['key']}.md") +
        f" {md_escape(s['classification'])} | {md_escape(ch['url'])} | {md_escape(bot['url']) if bot else '—'} | {md_escape(s.get('supply_share', '—')[:38])} |"
    )

def _channel_of(s):
    for x in s["sources"]:
        if "القناة" in x["label"]:
            return x["url"]
    for x in s["sources"]:
        if "t.me/" in x["url"] and ("Bot" not in x["url"].split("/")[-1] and "bot" not in x["url"].split("/")[-1]):
            return x["url"]
    return s["sources"][0]["url"]

def _bot_of(s):
    for x in s["sources"]:
        u = x["url"].split("/")[-1]
        if "Bot" in u or "bot" in u or "بوت" in x["label"] or "البوت" in x["label"]:
            return x["url"]
    return "—"

sup_table = "\n".join(
    f"| {s['icon']} {s['order']} | **{s['name']}** | {md_escape(s['classification'])} | "
    f"{md_escape(_channel_of(s))} | {md_escape(_bot_of(s))} |"
    for s in SUPPLIERS)

dashboard = f"""# 📊 مصادر التوريد الموثقة — لوحة القيادة (StackVault)

> **✅ التحقق الحيّ:** {AR_DATE} · **المنهجية:** {VERIFICATION_SUMMARY['method']} · **نطاق الفحص:** {VERIFICATION_SUMMARY['checked']}

هذه اللوحة توثّق مصادر التوريد الدقيقة للموردين السبعة المطلوبين، بروابط مؤكدة حيًا وتاريخ تحقق لكل رابط، وأسعار مؤرخة من قنوات الموردين أنفسهم، ونقاط تفاوض جاهزة للاستخدام. أُنشئت لتحويل قائمة الأسماء (@ProdSellerBot و@HitMeowShop و@storeBatmanBot وProdSeller وTeam Sóc Lọ وEvo Era وAISUBSID وAiVerseX Hub) إلى سبع ملفات موثقة قابلة للتتبع.

## 1 · التحقق من الرابط الرئيسي

| البند | النتيجة (فحص {AR_DATE}) |
| --- | --- |
| **الرابط** | https://stackvault.shop/ |
| **الحالة** | ✅ **حيّ — HTTP 200** |
| **العنوان** | {CATALOG['title']} |
| **البنية التحتية** | {md_escape(CATALOG['server'])} |
| **الكتالوج الحيّ** | **{CATALOG['catalog_n']} منتجًا** ({CATALOG['census']['ps']} عبر ProdSeller ببادئة ps_ = {CATALOG['ps_pct']}% · {CATALOG['census']['mr']} عبر Evo Era ببادئة mr_ = {CATALOG['mr_pct']}% · {CATALOG['in_stock']} منتجًا بمخزون فعلي) |
| **واجهة الكتالوج** | `{CATALOG['catalog_api']}` (تتطلب ترويسة Referer من المتجر) |

## 2 · خريطة سلسلة التوريد المكتشفة

```
[المصنّع المنبع]                     [الموزّع الرئيسي]              [المتجر]
Team Sóc Lọ (فيتنام)  ──صنع حصص AI──▶  ProdSeller (API/بوت)  ──ps_ 91%──▶  StackVault
gpt.teamsoclo.site                     t.me/ProdSellerOfficial            stackvault.shop
                                       ▲
[المصدر اليدوي]                        │ (وسيط يضيف 15–25% على منتجات teamsoclo)
Evo Era ──mr_ 8.7% (أكواد ناشئات + مزارع هندية)───────────────────────────▶ StackVault

[البدائل المُقيَّمة]  HitMeowShop (فيتنام) · AISUBSID (إندونيسيا)
[المرشحان الجديدان]  storeBatmanBot (إندونيسيا — بلا كتالوج علني) · AiVerseX Hub (IST — 22.9K مشترك)
```

## 3 · جدول الموردين السبعة

| # | المورد | التصنيف | القناة الرسمية | بوت البيع |
| --- | --- | --- | --- | --- |
{sup_table}

**تطابق أسماء القائمة الأصلية:** @ProdSellerBot = ProdSeller (بوت المبيعات) · @HitMeowShop = HitMeowShop · @storeBatmanBot = STORE BATMAN (كيان مستقل) · البقية بأسمائها.

## 4 · نتائج التحقق المباشر

- **{VERIFICATION_SUMMARY['live_ok']}** من {VERIFICATION_SUMMARY['checked']}
- **روابط ميتة مؤكدة:** {md_escape(' · '.join(VERIFICATION_SUMMARY['dead']))}
- **تنبيهات أسماء خاطئة:** {md_escape(' · '.join(VERIFICATION_SUMMARY['false_positives']))}

## 5 · الخلاصة التنفيذية

1. **سلسلة توريد فعالة وموثقة:** 91% من الكتالوج يمر عبر ProdSeller (آليًا بالكامل)، و8.7% يدويًا عبر Evo Era — وكلاهما حيّ ومُتحقق منه بتاريخ {AR_DATE}.
2. **اكتشاف البنية العميقة:** ProdSeller نفسه وسيط فوق المصنّع الفيتنامي Team Sóc Lọ — التعاقد المباشر مع المصنع يوفر ~20% على أغلى عائلات المتجر (رصيد AI).
3. **ورقتا ضغط سعريتان جاهزتان:** AISUBSID ($2.50 جملة ChatGPT Plus مقابل $5.72+ تكلفة SV) وAiVerseX (فلاش Gemini $0.39 = تكلفة SV بالضبط).
4. **المرشحان الجديدان:** AiVerseX Hub جاهز للتقييم بعينات فورية (كتالوج وأسعار معلنة)، بينما storeBatmanBot يحتاج استفسارًا مباشرًا من البوت لعدم وجود أي كتالوج علني.

## 6 · كيف تستخدم هذه الحزمة

- كل ملف مرقّم أدناه هو **صفحة مستقلة** تغطي موردًا واحدًا: البطاقة التعريفية، مصادر التوريد المؤكدة، الأسعار المؤرخة، الشروط، نقاط التفاوض، والمخاطر.
- ملف `قاعدة بيانات الموردين.csv` يستورد كـ**قاعدة بيانات Notion** (جدول قابل للفرز والفلترة).
- ملف `تعليمات الاستيراد إلى Notion.md` يشرح خطوتي الاستيراد بالتفصيل.
"""
with open(f"{PKG}/00_لوحة_القيادة_مصادر_التوريد.md", "w", encoding="utf-8") as f:
    f.write(dashboard)

# ============ 2) Supplier pages ============
for s in SUPPLIERS:
    src_rows = "\n".join(
        f"| {md_escape(x['label'])} | `{x['url']}` | {md_escape(x['status'])} | {md_escape(x['note'])} |"
        for x in s["sources"])
    price_rows = "\n".join(
        f"| {md_escape(p[0])} | {md_escape(p[1])} | {p[2]} | {md_escape(p[3])} |"
        for p in s["prices"])
    id_rows = "\n".join(f"| {k} | {md_escape(v)} |" for k, v in s["identity"].items())
    bargain = "\n".join(f"- {b}" for b in s["bargain"])

    page = f"""# {s['icon']} {s['name']} — {s['name_ar']}

> **التصنيف:** {s['classification']} · **حالة التحقق:** ✅ روابط مؤكدة حيًا بتاريخ {AR_DATE} · **المنهجية:** فحص سلبي عام (GET فقط)

## الدور في سلسلة توريد StackVault

{s['role']}

## البطاقة التعريفية

| البند | القيمة |
| --- | --- |
{id_rows}

## مصادر التوريد الدقيقة (روابط مؤكدة)

| القناة | الرابط | حالة التحقق | ملاحظات تشغيلية |
| --- | --- | --- | --- |
{src_rows}

**حصة التوريد لـ StackVault:** {s['supply_share']}

## الأسعار الموثقة (مؤرخة من مصادر المورد نفسه)

| المنتج / العرض | السعر | التاريخ | المصدر |
| --- | --- | --- | --- |
{price_rows}

## الشروط وأطر العمل

{s['terms']}

## نقاط التفاوض والفرص

{bargain}

## المخاطر وملاحظات التحقق

{s['risks']}

---

*آخر تحقق حيّ: {AR_DATE} — التوثيق ضمن مشروع استخبارات موردي StackVault.*
"""
    fn = f"{PKG}/{s['order']:02d}_{s['key']}.md"
    with open(fn, "w", encoding="utf-8") as f:
        f.write(page)
    print("page:", fn)

# ============ 3) CSV database ============
csv_path = f"{PKG}/قاعدة بيانات الموردين.csv"
with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["الاسم", "التصنيف", "الدور في سلسلة التوريد", "القناة الرسمية", "بوت البيع",
                "المشرف/التواصل", "الواجهات الأخرى", "المشتركون", "حصة كتالوج SV",
                "أبرز الأسعار الموثقة", "أقوى فرصة", "المخاطر الرئيسية", "حالة التحقق"])
    for s in SUPPLIERS:
        ch_url = _channel_of(s)
        bot_url = _bot_of(s)
        admin = next((x for x in s["sources"] if "المشرف" in x["label"] or "المالك" in x["label"] or "الدعم" in x["label"]), None)
        others = " · ".join(x["url"] for x in s["sources"] if x["url"] not in (ch_url, bot_url, admin["url"] if admin else None, "—") )
        members = next((x["status"].split("—")[-1].strip() for x in s["sources"] if "مشترك" in x["status"]), "—")
        top_price = s["prices"][0] if s["prices"] else ("—",)
        top_bargain = s["bargain"][0] if s["bargain"] else "—"
        w.writerow([s["name"], s["classification"], s["role"][:120], ch_url,
                    bot_url, admin["url"] if admin else "—",
                    others[:100], members, s["supply_share"][:60],
                    f"{top_price[0]}: {top_price[1]} ({top_price[2]})",
                    top_bargain[:140], s["risks"][:140], f"تحقق حيّ {AR_DATE}"])
print("csv:", csv_path)

# ============ 4) Import instructions ============
instructions = f"""# 📥 تعليمات الاستيراد إلى Notion

> هذه الحزمة مبنية بصيغ Notion الأصلية (Markdown للصفحات + CSV لقاعدة البيانات) — الاستيراد يستغرق أقل من دقيقتين.

## الطريقة الأولى — استيراد الصفحات (الأساسية)

1. افتح Notion وانتقل إلى الصفحة الأم التي تريد وضع التوثيق تحتها (يُنصح: **المرجع الحاكم التجاري**).
2. من قائمة الصفحة: **`⋯` ← Import ← Markdown & CSV**".
3. حدد كل ملفات `.md` العشرة داخل هذا المجلد (لوحة القيادة + 7 موردين) وستُستورد كصفحات كاملة بجداولها وتنسيقها.
4. اسحب `00_لوحة_القيادة_مصادر_التوريد` للأعلى لتكون الصفحة الرئيسية، ورتب صفحات الموردين تحتها.

## الطريقة الثانية — قاعدة بيانات الموردين (للفرز والفلترة)

1. في Notion: **`/import` ← CSV**" واختر `قاعدة بيانات الموردين.csv`.
2. ستُنشأ قاعدة بيانات بـ 7 صفوف و13 خاصية (التصنيف، القناة، البوت، الحصة، الأسعار، المخاطر…).
3. حوّل عمود «التصنيف» إلى **Select** والعمود «المشتركون» إلى **Number** إن أردت الفلترة المتقدمة.

## الطريقة الثالثة — المزامنة المباشرة عبر API (اختيارية)

- السكربت `scripts/sv_supply5_notion_sync.py` ينشئ نفس المحتوى مباشرة عبر Notion API (صفحة تحت «المرجع الحاكم» + قيد Cycle 13 في أرشيف التفاعلات).
- **الشرط:** إضافة `NOTION_TOKEN=secret_…` إلى `/home/z/my-project/.env` (التوكن السابق أُزيل مع إعادة بناء البيئة — تدوير D5 كان معلقًا عليك).
- التشغيل: `python3 scripts/sv_supply5_notion_sync.py`

## محتويات الحزمة

| الملف | المحتوى |
| --- | --- |
| `00_لوحة_القيادة_مصادر_التوريد.md` | التحكم الكامل: التحقق من stackvault.shop + خريطة السلسلة + جدول الموردين |
| `01_prodseller.md` | المورد الرئيسي (91% من الكتالوج) |
| `02_teamsoclo.md` | المصنّع الفيتنامي المنبع |
| `03_evoera.md` | المصدر اليدوي (أكواد الناشئات) |
| `04_hitmeow.md` | البديل المنافس (فيتنام) |
| `05_aisubsid.md` | بديل ChatGPT الأرخص (إندونيسيا) |
| `06_storebatman.md` | المرشح الإندونيسي الجديد |
| `07_aiversex.md` | المرشح الأكبر (22,937 مشتركًا) |
| `قاعدة بيانات الموردين.csv` | قاعدة بيانات جاهزة للاستيراد |
| `تعليمات الاستيراد إلى Notion.md` | هذا الملف |

> **تاريخ الحزمة:** {AR_DATE} · جميع الأسعار مؤرخة من قنوات الموردين العامة أنفسهم · المنهجية: OSINT سلبي (GET عام فقط، صفر تفاعل).
"""
with open(f"{PKG}/تعليمات الاستيراد إلى Notion.md", "w", encoding="utf-8") as f:
    f.write(instructions)
print("instructions written")

# manifest
print("\nPackage:", PKG)
for fn in sorted(os.listdir(PKG)):
    print("  -", fn, f"({os.path.getsize(os.path.join(PKG, fn))} bytes)")
