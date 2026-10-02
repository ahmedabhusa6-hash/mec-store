#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEC-2.4 | HTML v2.4 update: channel matrix (91 channels) + Dolaa reverse-engineering section.
Inserts new section after b3dirsec, adds interactive matrix table, updates title/footer.
"""
import json, re

BASE = "/home/z/my-project"
HP = f"{BASE}/download/supplier_intelligence.html"
MX = json.load(open(f"{BASE}/download/channel_matrix.json", encoding="utf-8"))

html = open(HP, encoding="utf-8").read()

# ---------- build matrix table rows (31 registry + 3 discovered) ----------
rows = []
for r in MX["matrix_layerA"]:
    anchor = r.get("min_price_anchor_usd")
    anchor_s = f"${anchor:.2f}" if anchor is not None else "—"
    subs = r.get("subscribers", "") or ""
    rows.append({
        "id": r["id"], "type": r["type"], "cluster": r["cluster"].split(" / ")[0],
        "layer": r["layer"], "role": r["role_in_chain"][:60],
        "risk": r["risk_grade"], "anchor": anchor_s, "subs": subs[:30],
        "fit": r["dolaa_fit"], "url": r.get("url", ""),
    })
for d in MX["discovered_entities"]:
    anchor = d.get("min_price_anchor_usd")
    anchor_s = f"${anchor:.3f}" if anchor is not None else "—"
    rows.append({
        "id": d["id"], "type": d["type"], "cluster": "مكتشف",
        "layer": d["layer"], "role": d["role_in_chain"][:60],
        "risk": d["risk_grade"], "anchor": anchor_s, "subs": "-",
        "fit": d["dolaa_fit"], "url": d.get("url", ""),
    })

def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

trs = []
for i, r in enumerate(rows):
    trs.append(
        f'<tr><td class="mut" dir="ltr">{esc(r["id"])}</td>'
        f'<td>{esc(r["type"])}</td>'
        f'<td>{esc(r["layer"])}</td>'
        f'<td class="mut">{esc(r["role"])}</td>'
        f'<td style="font-size:.78rem">{esc(r["risk"][:70])}</td>'
        f'<td class="price">{esc(r["anchor"])}</td>'
        f'<td style="font-size:.78rem">{esc(r["fit"])}</td></tr>'
    )
table_rows = "\n".join(trs)

n_layerA = len(MX["matrix_layerA"])
n_disc = len(MX["discovered_entities"])
n_mkt = len(MX["matrix_layerB_marketplaces"])
sv = MX["stackvault_cost_layer"]

# top marketplace channels (for the summary card)
mkt_top = MX["matrix_layerB_marketplaces"][:12]
mkt_str = " · ".join(f'{esc(m["channel"])} ({m["n_offers"]})' for m in mkt_top)

section = f'''
<h2 id="chmatsec">🧮 مصفوفة تقييم القنوات الشاملة + الهندسة العكسية لنموذج «دولا» (MEC-2.4 — 27/09 ~13:30 UTC)</h2>
<div class="banner" style="border-color:var(--warn)">🧭 <b>هذه المصفوفة تجيب سؤالك المركزي (كم فائدتهم وكيف يشترون ويبيعون) على مستوى كل قناة:</b> 91 قناة مصنفة في طبقات السلسلة (مصنع ← جملة ← تجزئة ← ثقة)، لكل قناة: دورها، درجة خطرها، أرخص مرساة سعرية مرصودة، وملاءمتها كقناة توريد لمتجر على نمط دولا. المصدر الموحد: <span dir="ltr">channel_matrix.json</span> · الوثيقة التحليلية: <span dir="ltr">supply_chain_economics.md §11</span>.</div>
<div class="card">
<div class="grid2">
<div class="ent"><b>📊 حصيلة التصنيف (34 كيانًا رماديًا + 57 قناة سوق/رسمية)</b><br><span class="mut">سجل §19: {n_layerA} كيانًا (كلها حية HTTP 200) + 3 مكتشفات جديدة (API خلفي لـStackVault · AiVerseXBot · Gt_Verified) · طبقة الأسواق والقنوات الرسمية: {n_mkt} قناة ظهرت في العروض الموثقة ({mkt_str} …) · التوزيع الطبقي للسجل: 3 مصنع+تجزئة · 2 مصنع حسابات · 5 جملة · 3 تجزئة منظمة · 6 تجزئة+طرق · 7 تجزئة فردية · 3 طبقة ثقة · 2 بائع طرق · 3 دعم.</span></div>
<div class="ent"><b>🧯 الهندسة العكسية لنموذج دولا — الحكم المركب [استنتاج بأدلة مرصودة]</b><br><span class="mut">المتجر نفسه غير قابل للرصد (النطاقات متوقفة — موثق 27/09) لذا رُكّبت النموذج من الأدلة: <b>لا قناة واحدة تفسّر كتالوجًا عريضًا</b> — البنية الاقتصادية تُجبر المتجر الناجح على محفظة مركبة: <b>عمود فقري جملة/API (H2)</b> للعائلات الرقمية + <b>تحكيم إقليمي (H1)</b> للبطاقات + <b>تقسيم مؤسسي (H4)</b> للتعليمية + تصنيع داخلي (H3) للهوامش القصوى فقط. الدليل البنيوي: StackVault نفسه (275 منتجًا) يظهر موردين متعددين في كلفه الداخلية.</span></div>
</div>
<div class="grid2" style="margin-top:12px">
<div class="ent"><b>🧮 حاسبة الهامش العكسي (مِثل §11.2 — جاهزة للتطبيق على أسعار أي متجر)</b><br><span class="mut">ChatGPT Plus: أرضية توريد <b>$2.80</b> ← «مستقر بضمان» $10.67 ← رسمي $20: متجر يبيع بـ$6.67 هامشه الإجمالي 42–58% (طبقة هشة)؛ يبيع بـ$12 هامشه 11% (طبقة ضمان كامل) — <b>فرق «الرخيص الموثوق» عن «الرخيص الهش» هو طبقة الكلفة لا كفاءة المتجر</b>. مرسيات أخرى: Netflix كلفة ≈$3.33 · Spotify هندي $0.79/شهر · MS365 سنة $0.21 · Office2024 $0.60 · Xbox GPU إقليمي $4–8.4 · PSN أمريكي عبر لبنان $9.07/$10.</span></div>
<div class="ent"><b>🚫 قانون الأرضيات: لماذا لا يُشترى «أرخص من هذا» بإطراد؟</b><br><span class="mut">(1) الجملة الشرعية (Reloadly/DT One) خصمها 1–15% من الاسمي فقط [مستند] · (2) أرضيات المصانع مقيدة بكلفة حدية (UPI ينجح 1–2% — حتى الصانع لا يبيع تحت ~$2.8 بإطراد) · (3) لا كيان واحد في الـ91 يبيع «كل شيء أرخص من الجميع» — الناجون متخصصون بطبقة · (4) من يعرض تحت الأرضيات بإطراد: إما هوية SKU مختلفة (مشاركة لا حساب خاص) أو حرق رأس مال أو احتيال منظم — الأنماط الثلاثة موثقة في السجل.</span></div>
</div>
<h3 style="color:var(--acc);margin:18px 0 8px;font-size:1.02rem">📋 المصفوفة التفاعلية — 34 كيانًا (سجل §19 + المكتشفات) قابلة للفرز والتصفية</h3>
<div style="margin:8px 0 10px;display:flex;gap:8px;flex-wrap:wrap">
<input id="mq" placeholder="🔍 ابحث: كيان / طبقة / دور…" style="flex:1;min-width:220px" oninput="mfilter()">
<select id="mlay" onchange="mfilter()"><option value="">كل الطبقات</option><option value="جملة">جملة</option><option value="مصنع">مصنع</option><option value="تجزئة">تجزئة</option><option value="ثقة">ثقة/ضمان</option><option value="طرق">طرق</option><option value="تكلفة">طبقة تكلفة</option></select>
<span class="mut" style="align-self:center" id="mcount"></span>
</div>
<div style="overflow-x:auto"><table id="mtab"><thead><tr>
<th onclick="msort(0)">الكيان ⇅</th><th onclick="msort(1)">النوع ⇅</th><th onclick="msort(2)">الطبقة ⇅</th><th>الدور في السلسلة</th><th>درجة الخطر</th><th onclick="msort(5)" data-n="1">أرخص مرساة (USD) ⇅</th><th>الملاءمة لنموذج دولا</th>
</tr></thead><tbody id="tbm">
{table_rows}
</tbody></table></div>
<script>
var mrows=[...document.querySelectorAll('#tbm tr')];
function mval(td){{var n=parseFloat(td.textContent.replace(/[^0-9.]/g,''));return isNaN(n)?-1:n;}}
function mfilter(){{var q=document.getElementById('mq').value.trim(),lay=document.getElementById('mlay').value,n=0;
mrows.forEach(function(r){{var t=r.textContent,ok=(!q||t.indexOf(q)>-1)&&(!lay||r.cells[2].textContent.indexOf(lay)>-1);r.style.display=ok?'':'none';if(ok)n++;}});
document.getElementById('mcount').textContent='عرض '+n+' / '+mrows.length;}}
function msort(col){{var asc=msort['c'+col]=!msort['c'+col];var tb=document.getElementById('tbm');
var arr=mrows.slice().sort(function(a,b){{var x=a.cells[col].textContent.trim(),y=b.cells[col].textContent.trim();
var nx=mval(a.cells[col]),ny=mval(b.cells[col]);
if(nx>-1&&ny>-1)return asc?nx-ny:ny-nx;return asc?x.localeCompare(y,'ar'):y.localeCompare(x,'ar');}});
arr.forEach(function(r){{tb.appendChild(r);}});}}
mfilter();
</script>
<div class="ent" style="margin-top:12px"><b>⚠️ حدود المصفوفة (إلزامية):</b><br><span class="mut">كل الأسعار معلنة لا معاملاتية · بوابات الجملة خلف تسجيل دخول (أسعارها الحقيقية تتطلب حساب B2B — البروتوكول جاهز في ملف القرارات) · لا بصمة سمعة مستقلة لأي عنقود · التصنيف الطبقي للكيانات المكتشفة من داخل معاينات قنوات أمها · المتجر محل السؤال (دولا) غير مرصود مباشرة — النموذج مبني على القرائن لا على محاسبته.</span></div>
</div>
'''

# insert before the §19 evaluation section
anchor = '<h2>📡 تقييم سجل القنوات §19 — أول تحقق مباشر في تاريخ المشروع (27/09)</h2>'
assert anchor in html, "anchor not found"
html = html.replace(anchor, section + "\n" + anchor)

# title + footer update
html = html.replace(
    "قاعدة معلومات الموردين — MEC2-20260927-B3 v2.3 (الدفعتان 1+2 + سجل القنوات §19 + اقتصاديات التوريد + حزمة القرارات المفوَّضة)",
    "قاعدة معلومات الموردين — MEC2-20260927 v2.4 (الدفعات 1+2 + مصفوفة 91 قناة + الهندسة العكسية لنموذج دولا + سجل §19 + اقتصاديات التوريد + القرارات)"
)
html = html.replace(
    "MEC-2.3 | Adaptive Supplier Intelligence Research Engine | v4.2 Candidate — Promotion-Ready",
    "MEC-2.4 | Adaptive Supplier Intelligence Research Engine | v4.2 Candidate — Promotion-Ready (كلمة الاعتماد استُلمت 27/09: «اعتمد كل شي» — تُطبَّق بعد اكتمال الدفعة 3)"
)
html = html.replace(
    "المخرجات: Web v2.3 + Word برامجي + Markdown + JSON + Notion مُزامَن (توافق دلالي — معيار D2 الثلاثي)",
    "المخرجات: Web v2.4 + Word برامجي + Markdown + JSON + Notion مُزامَن (توافق دلالي — معيار D2 الثلاثي) | مصادر MEC-2.4: channel_matrix.json (91 قناة) · supply_chain_economics.md §11"
)

open(HP, "w", encoding="utf-8").write(html)

# QA checks
checks = {
    "section-inserted": 'id="chmatsec"' in html,
    "table-populated": html.count('<tr><td class="mut" dir="ltr">') >= 34,
    "filter-script": "function mfilter()" in html,
    "title-v24": "v2.4" in html,
    "dolaa-section": "الهندسة العكسية لنموذج «دولا»" in html,
    "row-count": len(re.findall(r'<tr><td class="mut" dir="ltr">', html)),
}
print("QA:", checks)
assert all(v for k, v in checks.items() if k != "row-count"), "QA failed"
print(f"OK — HTML v2.4 written: {len(html)//1024}KB, matrix rows: {checks['row-count']}")
