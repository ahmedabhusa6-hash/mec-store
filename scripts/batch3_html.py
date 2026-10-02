#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-3.0 final | HTML v3.0: batch-3 section + promotion banner + final stats."""
import json

BASE = "/home/z/my-project"
HP = f"{BASE}/download/supplier_intelligence.html"
oi = json.load(open(f"{BASE}/download/offers_intelligence.json", encoding="utf-8"))

b3 = oi["batch3_run"]
st = b3["states_summary"]
ch_acc = b3["curation"]["channel_accepted"]
of_acc = b3["curation"]["official_accepted"]

rows = []
for sid, v in ch_acc.items():
    o = v["offer"]
    rows.append(f'<tr><td class="mut" dir="ltr">{sid}</td><td>{o["seller"]}</td>'
                f'<td class="mut">{o["product"][:52]}</td><td class="price">${o["usd"]}</td>'
                f'<td style="font-size:.78rem">{v["note"][:70]}</td></tr>')
ch_rows = "\n".join(rows)

rows = []
for sid, v in of_acc.items():
    b = v["baseline"]
    rows.append(f'<tr><td class="mut" dir="ltr">{sid}</td><td>{b["seller"]}</td>'
                f'<td class="price">${b["usd"]}</td><td style="font-size:.78rem">{b["note"][:80]}</td></tr>')
of_rows = "\n".join(rows)

section = f'''
<h2 id="b3sec">🎯 الدفعة 3 (218 P3) + اكتمال الكتالوج 437/437 + ترقية v4.2 → Approved (MEC-3.0 — 27/09 ~16:40 UTC)</h2>
<div class="banner" style="border-color:var(--ok)">🏆 <b>لحظة تاريخية للمشروع:</b> الكتالوج كامل لأول مرة — <b>437/437 SKU مغطاة</b> (P1: 46/142 إجراءً · P2: 173/130 · P3: 218/143) · الدفتر: <b>415 إجراءً موثقًا بلا إخفاق متبقٍ</b> (143/143 + 130/130 في النوافذ الأخيرة) · <b>v4.2 = أول نسخة Approved في تاريخ المشروع</b> (قاعدة الاستثناء التأسيسي D1: السلالة + المراجعات + الاختبار الحي ثلاثي الدفعات + تصريح المستخدم الصريح «اعتمد كل شي» — البوابة تُغلق نهائيًا).</div>
<div class="card">
<div class="grid2">
<div class="ent"><b>📊 حصيلة الدفعة 3 (بعد التنقيح اليدوي الكامل)</b><br><span class="mut">143 استعلامًا (143/143 OK) · 562 نتيجة · 218/218 SKU مغطاة · <b>18 عرضًا مباشرًا</b> (موجات MEC-2.5 بلا حصة: StackVault-API + K4G المضمّن + Turgame 92 فئة) · <b>10 عروض قنوات معتمدة</b> منقحة يدويًا · <b>7 خطوط رسمية</b> موثقة · 69 lead-only · 114 رفض ضجيج موثق (درس الدفعة 2 مطبق). تصحيحان سعريان من السياق النصي (GT031: $10.24 · GT040: $64.97).</span></div>
<div class="ent"><b>🔬 اكتشافات الدفعة 3 الحاكمة</b><br><span class="mut">(1) تحقق متقاطع ناجح للبطاقات التركية: Turgame $1.02 مقابل SEAGM $1.08 (Xbox 50 TL — فارق 5.8% بين قناتين) · (2) سوق العلاوة الأمريكي رابع تأكيد: بطاقة Steam $10 تباع $10.47 (+4.7%) · (3) خصومات مفاتيح موثقة: ARK -75% · Kingdom Come II -90% · PUBG RU -70% (بعلم إقليمي) · (4) شحن الألعاب عبر الأسواق ≈ الرسمي — قنوات وصول لا خصم · (5) Perplexity السنوي عبر CJS ≈ الرسمي ($244.86/$240).</span></div>
</div>
<h3 style="color:var(--acc);margin:16px 0 8px;font-size:1.02rem">✅ عروض القنوات المعتمدة المنقّحة (10)</h3>
<div style="overflow-x:auto"><table><thead><tr><th>SKU</th><th>البائع</th><th>المنتج</th><th>USD</th><th>ملاحظة التنقيح</th></tr></thead><tbody>{ch_rows}</tbody></table></div>
<h3 style="color:var(--acc);margin:16px 0 8px;font-size:1.02rem">🏛️ الخطوط الرسمية الموثقة (7)</h3>
<div style="overflow-x:auto"><table><thead><tr><th>SKU</th><th>المصدر</th><th>USD</th><th>ملاحظة</th></tr></thead><tbody>{of_rows}</tbody></table></div>
<div class="ent" style="margin-top:12px"><b>📦 الحصيلة الإجمالية للكتالوج الكامل (الدفعات 1-3 + الموجات المباشرة):</b><br><span class="mut">42 عرضًا بمستوى «مرصود مباشرة» (أعلى مستوى دليل) · 47+ عروض قنوات معتمدة معلنة · 40+ خطًا رسميًا موثقًا · مصفوفة 91 قناة مصنفة · هندسة عكسية كاملة لنموذج دولا (شجرة فرضيات + حاسبة هوامش + قانون أرضيات) · اقتصاديات سلسلة التوريد بمعادلة موثقة (بيع = كلفة × 1.2) · كل ادعاء يحمل دليله وحالة تحققه وتاريخه.</span></div>
<div class="ent"><b>⚠️ حدود الدفعة 3 (إلزامية):</b><br><span class="mut">عروض الدفعة 3 بمستوى «معلن (مقتطف)» — القراءات المباشرة مؤجلة (§19) · وحدات غير نقدية (UC/VP/Shards/Robux) تحتاج جداول تحويل رسمية · 114 SKU ضُجيجها موثق لا محذوف (فشل الاسترجاع ≠ عدم الوجود) · كل الأثمنة لحظة 27/09/2026.</span></div>
</div>
'''

anchor = '<h2>📡 تقييم سجل القنوات §19 — أول تحقق مباشر في تاريخ المشروع (27/09)</h2>'
assert anchor in open(HP, encoding="utf-8").read(), "anchor missing"
html = open(HP, encoding="utf-8").read()
html = html.replace(anchor, section + "\n" + anchor)
html = html.replace(
    "قاعدة معلومات الموردين — MEC2-20260927 v2.4 (الدفعات 1+2 + مصفوفة 91 قناة + الهندسة العكسية لنموذج دولا + سجل §19 + اقتصاديات التوريد + القرارات)",
    "قاعدة معلومات الموردين — MEC2-20260927 v3.0 (الكتالوج الكامل 437/437: الدفعات 1+2+3 + مصفوفة 91 قناة + الهندسة العكسية لدولا + v4.2 APPROVED)")
html = html.replace(
    "MEC-2.4 | Adaptive Supplier Intelligence Research Engine | v4.2 **APPROVED** (ترقية 27/09 — قاعدة الاستثناء D1)",
    "MEC-3.0 FINAL | Adaptive Supplier Intelligence Research Engine | v4.2 **APPROVED** (أول اعتماد في تاريخ المشروع — 27/09) | 437/437 SKU · 415 إجراءً · 91 قناة مصنفة")

open(HP, "w", encoding="utf-8").write(html)
checks = {"b3sec": 'id="b3sec"' in html, "promotion-banner": "أول نسخة Approved" in html,
          "v30": "v3.0" in html, "ch-table": len(ch_rows) > 0}
print("QA:", checks)
assert all(checks.values())
print(f"OK — HTML v3.0: {len(html)//1024}KB")
