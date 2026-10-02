#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-2.3 | HTML v2.2 -> v2.3: inject B3-DIRECT discoveries section + title/meta/footer updates."""
import re

F = "/home/z/my-project/download/supplier_intelligence.html"
html = open(F, encoding="utf-8").read()
orig_len = len(html)

# 1) title
html = html.replace(
    "<title>قاعدة معلومات الموردين — MEC2-20260927-DEC v2.2 (الدفعتان 1+2 + سجل القنوات §19 + اقتصاديات التوريد + حزمة القرارات المفوَّضة)</title>",
    "<title>قاعدة معلومات الموردين — MEC2-20260927-B3 v2.3 (الدفعتان 1+2 + الموجة المباشرة MEC-2.3: كشف كلفة الشراء + سجل القنوات §19 + اقتصاديات التوريد + حزمة القرارات)</title>")

# 2) meta line
html = html.replace(
    'Run ID: MEC2-20260927-DEC (حزمة القرارات فوق MEC-2.1) | الإصدار: v4.2 Candidate — <b style="color:var(--ok)">جاهزة للترقية (Promotion-Ready) بانتظار كلمة المستخدم</b> | النطاق: الكتالوج CP-1 (46 P1 + 173 P2 منفذة) + سجل القنوات §19 + قرارات D1/D2/D5 + ملف B2B | التاريخ: 2026-09-27 | المصادر: مراجع Notion + السجل §19 + الرصد المباشر + تفويض المستخدم الصريح',
    'Run ID: MEC2-20260927-B3 (الدفعة 3 + الموجة المباشرة فوق MEC-2.2) | الإصدار: v4.2 Candidate — <b style="color:var(--ok)">جاهزة للترقية (Promotion-Ready) بانتظار كلمة المستخدم</b> | النطاق: الكتالوج CP-1 (46 P1 + 173 P2 منفذة + 218 P3 قيد التنفيذ) + سجل القنوات §19 + 59 عرضًا «مرصودًا مباشرة» جديدًا + قرارات D1/D2/D5 + ملف B2B | التاريخ: 2026-09-27 | المصادر: مراجع Notion + السجل §19 + الرصد المباشر (HTTP بلا حصة) + تفويض المستخدم الصريح')

# 3) inject new section before the channels section
NEW_SEC = '''
<h2 id="b3dirsec">🔬 الموجة المباشرة MEC-2.3 — كشف كلفة الشراء الجملية + 59 أثمنًا مرصودة (27/09 ~05:00 UTC)</h2>
<div class="banner" style="border-color:var(--ok)">✅ <b>الاكتشاف المركزي للجلسة:</b> واجهة StackVault الخلفية (<span dir="ltr">decohomz.com/sv-api</span> — مصدر بيانات المتجر نفسه) أعادت الكتالوج الكامل <b>بحقل كلفة الشراء مكشوفًا (274/275 منتجًا)</b> — أول رؤية مباشرة في تاريخ المشروع لسعر التوريد الذي يدفعه بائع تجزئة فعلي. الموجة كلها عبر HTTP خالص (مستقلة عن حصة البحث المحجوبة 477/429 منذ ~02:10).</div>
<div class="card">
<div class="grid2">
<div class="ent"><b>🧮 معادلة التسعير المكتشفة: سعر البيع = الكلفة × 1.2</b><br><span class="mut">هامش موحّد آليًا: الوسيط <b>16.7%</b> (المتوسط 19.9%، المدى 13–57%) عبر الكتالوج كله — StackVault <b>بائع ناقل (pass-through)</b> لا مسعّر سوق: سعره مؤشر نظيف على أسعار الجملة العلوية (اقسم على 1.2). أمثلة محلولة [كلفة ← بيع]: Discord Nitro سنة $33.52←$40.23 · XGPU سنة $14.09←$16.91 · تجديد ChatGPT Plus رسمي $17.14←$20.57 · Office 2024 Pro Key $2.63←$3.16 · Windows Key $3.39←$4.07.</span></div>
<div class="ent"><b>🪜 سلّم كلفة ChatGPT Plus حسب الضمان (لأول مرة بالكلفة لا بالأسعار)</b><br><span class="mut">أساسي <b>$2.80</b> ← ضمان 6 ساعات $3.85 ← 5 ساعات $5.15 ← ضمان كامل <b>$10.67</b> ← تجديد رسمي <b>$17.14</b>. «نفس المنتج» = <b>فارق 6 أضعاف كلفة</b> بين طبقاته — إعلان «خصم 85%» يقابله سلّم جودة/هشاشة كامل، والمشتري يظنه منتجًا واحدًا.</span></div>
</div>
<div class="grid2" style="margin-top:12px">
<div class="ent"><b>📈 قياسات حية للانتشار جملة←تجزئة (نفس الجلسة)</b><br><span class="mut">Gemini 18M: جملة $0.65 ← تجزئة <b>$0.85</b> (مشتريات مؤكدة ×5 في بث الطلبات) = +31% · Duolingo Super 12M: جملة <b>$0.37</b> (حرب أسعار $0.59→0.45→0.37 في 5 أيام) ← تجزئة $0.85 = +130% · Office 365 Plus سنة: كلفة داخلية $0.21 ≈ جملة ProdSeller $0.17 — <b>تقارب مصدرين مستقلين على السعر العلوي</b> · CapCut: $0.14 جملة ← $1.29 كلفة متجر ← $1.60 بيع (سلسلة 3 طبقات مرئية كاملة).</span></div>
<div class="ent"><b>🎯 أثمن مباشرة جديدة (مستوى «مرصود مباشرة» — عيّنة)</b><br><span class="mut">Cursor Pro+ <b>40 USDT</b> (نهاية فلاش 04:27 UTC) · Manus Pro 1M <b>5.50</b> / 12m <b>37.00 USDT</b> · Coursera 12m <b>3.50</b> (62 وحدة) · HBO Max شهر كلفة $1.53←$1.96 · Windows 11 Pro <b>€1.03 أُعيد التحقق مباشرة</b> (جدول €0.84–1.66) · PSN لبنان $9.05 يطابق مرساتنا $9.07 · Turgame: 117 منتجًا — بطاقات TL بمعدل موحد $2.048/100TL، Xbox 50TL=$1.02 · XGPU سنة رمادية $16.91 = تحت الرسمي بـ26%.</span></div>
</div>
<div class="ent"><b>⚙️ حالة الدفعة 3 (218 P3) — التجهيز الكامل:</b><br><span class="mut">143 استعلامًا تغطي 218/218 SKU (تحقق آلي: صفر نواقص) جاهزة في <span dir="ltr">batch3_search.py</span> بمعمارية الاستئناف الذاتي · المراقب مُرقّى للسلسلة الكاملة: الـ15 المؤجلة ← تجميع الدفعة 2 ← 143 استعلام الدفعة 3 ← تجميع ← توقف عند التنقيح اليدوي · سكربتات ما بعد البحث جاهزة تحمي العروض المباشرة الحالية من الكتابة فوقها · الحصيلة الراهنة: 236 سجل SKU، منها 118 بعروض، + قسم <span dir="ltr">b3_direct_run</span> توثيقي في JSON.</span></div>
<div class="ent"><b>⚠️ حدود صادقة للموجة:</b><br><span class="mut">كل الأسعار إعلانية (لا معاملات منفذة) عدا «مشتريات مؤكدة» يبثها البائعون أنفسهم · حقل الكلفة قيمة داخلية غير قابلة للتدقيق الخارجي [بحاجة للتحقق عبر حساب B2B] · المخزون=0 لحظة السحب = نفاد لحظي (رُصدت تعبئات خلال ساعات) · معدل TL الضمني في Turgame (48.8/دولار) يخالف أساس الصرف المعتمد (34.1) — عُلّم [بحاجة للتحقق] ولم تُحسب على أساسه خصومات القيمة الاسمية لبطاقات TL.</span></div>
</div>

'''
marker = '<h2>📡 تقييم سجل القنوات §19 — أول تحقق مباشر في تاريخ المشروع (27/09)</h2>'
assert marker in html, "channels section marker not found"
html = html.replace(marker, NEW_SEC + marker)

# 4) economics section: add discovery banner at its top
eco_marker = '<h2>🏭 اقتصاديات سلسلة التوريد — كيف يشترون ويبيعون وكم الهامش (الشرط الصارم)</h2>'
eco_banner = eco_marker + '\n<div class="banner" style="border-color:var(--ok)">🆕 <b>تحديث كمي حاسم (MEC-2.3):</b> كلفة الشراء الجملية لبائع تجزئة رُصدت مباشرة من داخل نظامه — المعادلة «بيع = كلفة × 1.2» وسلّم كلفة ChatGPT Plus كاملًا وتقارب مصدرين على سعر الجملة العلوي. التفاصيل المحلولة في <span dir="ltr">supply_chain_economics.md</span> §10 — وأدناه أقسام الاقتصاديات كما وُثّقت في MEC-2.0 مع إضافة القسم 10.</div>'
if eco_marker in html:
    html = html.replace(eco_marker, eco_banner)

# 5) footer
html = html.replace(
    "<footer>MEC-2.2 | Adaptive Supplier Intelligence Research Engine | v4.2 Candidate — Promotion-Ready | كل ادعاء يحمل دليله وحالة تحققه وتاريخ رصده | المخرجات: Web v2.2 + Word برامجي + Markdown + JSON + Notion مُزامَن (توافق دلالي — معيار D2 الثلاثي) | سجل الأدلة: mec2_channels_raw.json · mec2_search_results.json · findings_index_b2.json · batch2_intelligence_draft.json · decisions_d1_d2_d5_b2b.md</footer>",
    "<footer>MEC-2.3 | Adaptive Supplier Intelligence Research Engine | v4.2 Candidate — Promotion-Ready | كل ادعاء يحمل دليله وحالة تحققه وتاريخ رصده | المخرجات: Web v2.3 + Word برامجي + Markdown + JSON + Notion مُزامَن (توافق دلالي — معيار D2 الثلاثي) | سجل الأدلة: mec2_channels_raw.json · mec2_search_results.json · findings_index_b2.json · batch2_intelligence_draft.json · b3_direct_observations.json · b3_stackvault_api.json · b3_turgame_categories.json · decisions_d1_d2_d5_b2b.md · supply_chain_economics.md §10</footer>")

open(F, "w", encoding="utf-8").write(html)
print("HTML v2.3 written: %d -> %d bytes (+%d)" % (orig_len, len(html), len(html) - orig_len))
# structural QA
checks = {
    "title_v23": "MEC2-20260927-B3 v2.3" in html,
    "b3dirsec": 'id="b3dirsec"' in html,
    "formula_banner": "بيع = كلفة × 1.2" in html,
    "cost_ladder": "$10.67" in html and "$2.80" in html,
    "eco_banner": "تحديث كمي حاسي".replace("حاسي","حاسم") in html or "تحديث كمي حاسم" in html,
    "footer_v23": "Web v2.3" in html,
    "b2_table_preserved": 'id="tb2"' in html,
    "b1_table_preserved": "tbl1" in html or 'id="tbl"' in html,
}
for k, v in checks.items():
    print(("PASS" if v else "FAIL"), k)
print("QA: %d/%d" % (sum(checks.values()), len(checks)))
