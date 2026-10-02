#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-1.0 | Phase 5b — Standalone interactive web page (semantic parity with markdown)."""
import json, os

OUT = "/home/z/my-project/download"
intel = json.load(open(OUT + "/offers_intelligence.json", encoding="utf-8"))
cat = json.load(open(OUT + "/catalog_v42.json", encoding="utf-8"))
ents = json.load(open("/home/z/my-project/research/entity_registry.json", encoding="utf-8"))["entities"]
actions = json.load(open("/home/z/my-project/research/action_ledger.json", encoding="utf-8"))

PI = intel["price_intelligence"]
fam_counts = cat["catalog_program"]["families"]
b1 = [s for s in cat["skus"] if s["batch"] == 1]
fam_of = {s["sku_id"]: s["family"] for s in cat["skus"]}
ok_n = len([a for a in actions if a["retrieval_status"]=="OK"])

rows = []
for s in b1:
    sid = s["sku_id"]
    if sid not in PI: continue
    i = PI[sid]
    d = i["cheapest_directly_observed"]; a = i["cheapest_advertised_or_official"]
    rows.append({
        "sku": sid, "family": s["family"],
        "identity": "%s %s — %s — %s" % (s["brand"], s["product"], s["duration_denomination"], s["region"]),
        "direct_usd": d["usd"] if d else None,
        "direct_seller": (d.get("seller","")[:30]) if d else "",
        "direct_note": ((d.get("note") or "")[:80]) if d else "",
        "adv_usd": a["usd"] if a else None,
        "adv_seller": ((a.get("seller","") or a.get("level",""))[:24]) if a else "",
        "state": ("Verified-direct" if d else ("Advertised" if (i["offers_count"]>0 or a) else "Partial")),
    })

data_js = json.dumps({"rows": rows, "entities": ents}, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>قاعدة معلومات الموردين — MEC1-20260927 (الدفعة 1)</title>
<style>
:root{--bg:#0d1117;--card:#161b22;--line:#30363d;--txt:#e6edf3;--mut:#8b949e;--acc:#58a6ff;--ok:#3fb950;--warn:#d29922;--err:#f85149}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Tahoma,Arial,sans-serif;background:var(--bg);color:var(--txt);line-height:1.7;padding:24px}
.wrap{max-width:1280px;margin:0 auto}
h1{font-size:1.6rem;color:var(--acc);margin-bottom:6px}
.meta{color:var(--mut);font-size:.9rem;margin-bottom:18px}
.banner{background:linear-gradient(90deg,#1a2332,#161b22);border:1px solid var(--acc);border-radius:10px;padding:12px 16px;margin-bottom:20px;font-size:.95rem}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:22px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;text-align:center}
.stat .n{font-size:1.7rem;font-weight:700;color:var(--acc)}
.stat .l{color:var(--mut);font-size:.82rem}
.controls{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:14px}
input,select,button{background:var(--card);border:1px solid var(--line);color:var(--txt);border-radius:8px;padding:8px 12px;font-size:.9rem;font-family:inherit}
input:focus,select:focus{outline:1px solid var(--acc)}
button{cursor:pointer}
button:hover{border-color:var(--acc)}
table{width:100%;border-collapse:collapse;background:var(--card);border-radius:10px;overflow:hidden;font-size:.86rem}
th{background:#1c2129;padding:10px;border-bottom:2px solid var(--line);cursor:pointer;white-space:nowrap;user-select:none}
th:hover{color:var(--acc)}
td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
tr:hover td{background:#1a2029}
.tag{display:inline-block;padding:2px 9px;border-radius:20px;font-size:.74rem;font-weight:600}
.t-ok{background:#0f2e18;color:var(--ok);border:1px solid var(--ok)}
.t-adv{background:#2e250f;color:var(--warn);border:1px solid var(--warn)}
.t-par{background:#251529;color:#c084fc;border:1px solid #c084fc}
.price{font-weight:700;color:var(--ok);white-space:nowrap}
.mut{color:var(--mut);font-size:.8rem}
h2{color:var(--acc);margin:30px 0 12px;font-size:1.25rem;border-right:4px solid var(--acc);padding-right:10px}
.ent{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin-bottom:10px}
.ent b{color:var(--acc)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:800px){.grid2{grid-template-columns:1fr}}
ul.audit{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 32px}
ul.audit li{margin-bottom:10px}
.unknown{background:#2a1c1c;border:1px solid var(--err);border-radius:10px;padding:16px 30px}
.unknown li{margin-bottom:8px;color:#f0a8a4}
.rec{background:#12261a;border:1px solid var(--ok);border-radius:10px;padding:14px 18px;margin-top:14px}
footer{margin-top:26px;color:var(--mut);font-size:.8rem;text-align:center;border-top:1px solid var(--line);padding-top:14px}
.count{color:var(--mut);font-size:.85rem;margin-bottom:8px}
</style>
</head>
<body><div class="wrap">
<h1>قاعدة معلومات الموردين — Adaptive Supplier Intelligence Research Engine</h1>
<div class="meta">Run ID: MEC1-20260927-B1 | الإصدار: v4.2 Candidate (working) | البرنامج: CP-1 | التاريخ: 2026-09-27 | القنوات: المراجع المحددة في Notion حصرًا</div>
<div class="banner">⚖️ <b>الصياغة الحاكمة:</b> «أقل سعر تم اكتشافه والتحقق منه ضمن نطاق البحث وتاريخ الفحص والشروط المحددة للـSKU» — يُمنع لفظ «الأرخص عالميًا». مكتشف ≠ موثّق ≠ مورد ≠ منبع ≠ أدنى سعر موثّق.</div>

<div class="stats">
<div class="stat"><div class="n">437</div><div class="l">SKU في الكتالوج (10 أسر)</div></div>
<div class="stat"><div class="n">46</div><div class="l">SKU الدفعة 1 (منفذة)</div></div>
<div class="stat"><div class="n">__OK__</div><div class="l">إجراء بحثي ناجح (من __TOT__)</div></div>
<div class="stat"><div class="n">__ND__</div><div class="l">SKU بأدنى سعر مشاهد مباشرة</div></div>
<div class="stat"><div class="n">__NE__</div><div class="l">كيان موثق الدور</div></div>
<div class="stat"><div class="l" style="margin-top:8px">الدفعات 2-3: 391 SKU<br>حالة صادقة: Unsearched</div></div>
</div>

<h2>📊 ذكاء الأسعار — الدفعة 1 (قابل للفرز والتصفية)</h2>
<div class="controls">
<input id="q" type="text" placeholder="🔍 ابحث: Steam، Netflix، Windows…">
<select id="fam"><option value="">كل الأسر</option>__FAMS__</select>
<select id="st"><option value="">كل حالات الدليل</option><option value="Verified-direct">مُشاهد مباشرة</option><option value="Advertised">معلن/رسمي</option><option value="Partial">جزئي</option></select>
<button onclick="resetF()">إعادة تعيين</button>
</div>
<div class="count" id="cnt"></div>
<div style="overflow-x:auto"><table id="tbl">
<thead><tr>
<th data-k="sku">SKU</th><th data-k="identity">الهوية التجارية</th><th data-k="family">الأسرة</th>
<th data-k="direct_usd" data-n="1">أدنى سعر مباشر (USD)</th><th data-k="direct_seller">البائع (مباشر)</th>
<th data-k="adv_usd" data-n="1">أدنى معلن/رسمي (USD)</th><th data-k="adv_seller">البائع (معلن)</th>
<th data-k="state">حالة الدليل</th><th data-k="direct_note">ملاحظة</th>
</tr></thead><tbody id="tb"></tbody></table></div>
<p class="mut" style="margin-top:10px">«مباشر» = صفحة مقروءة فعليًا بتاريخ الفحص | «معلن» = مقطع نتيجة بحث (Lead) | مشاهدات 25/09 موسومة قِدَمًا محتملًا (يومان). أسعار الجملة خلف بوابات تسجيل الدخول = Unknown.</p>

<h2>🏛️ سجل الكيانات وتوحيد الأدوار (Entity Resolution)</h2>
__ENTS__

<h2>🧾 سجل التدقيق (Audit Record §23)</h2>
<div class="grid2">
<ul class="audit">
<li><b style="color:var(--ok)">ما ثبت (مباشر حي 27/09):</b> Xbox GPU $22.99 رسميًا، Netflix Standard $19.99 / with-ads $8.99، Spotify $12.99، YouTube Premium $15.99 + Premium Lite $8.99 (اكتشاف جديد)، Discord Nitro Basic $2.99، Keyforsteam: Win11 Pro من 1,03€ وOffice 2024 من 0,56€ وOffice 2021 من 2,44€، GGSel ChatGPT Plus من 749₽، Airalo من $4.00، بوابة Turgame الجملة، منصة FazerCards، Reloadly كـAPI/موزع.</li>
<li><b style="color:var(--warn)">ما لم يُحل (Retrieval-Limited):</b> صفحات منتجات Eneba (404 ×4 — ورثنا أسعار 25/09)، NordVPN (Cloudflare)، تسعير جملة Turgame/Reloadly/FazerCards (خلف حسابات).</li>
<li><b>التناقضات المُدارة:</b> Turgame Steam-20 صار Sold Out (كان نشطًا 25/09) — توفر ديناميكي موثق. أرخص معلن لWin11 ($0.53-1.22) مفاتيح غالبًا OEM/هاتفية — حُفظ منفصلًا عن Retail.</li>
<li><b>الميزانية:</b> 142/142 (C4=96 + احتياطي 24 + تعديل تحقق +22 موثق + استرداد §19 ×2). فشل الاسترجاع ≠ عدم الوجود.</li>
</ul>
<div class="unknown">
<b>⚠️ مجهولات معلنة (Unknowns):</b>
<li>النص الحرفي لملف v4.2 خارج Notion [بحاجة إلى تحقق]</li>
<li>أسعار الجملة الحقيقية للبوابات الثلاث [غير معروف — خلف تسجيل]</li>
<li>الضمان/إعادة البيع لمعظم العروض المعلنة [بحاجة إلى تحقق]</li>
<li>هوية Definite Play كمرآة لTurgame [بحاجة إلى تحقق]</li>
<li>بوتات Telegram الـ29 البذور [Budget-Limited — لم تُفحص فرديًا]</li>
<li>الدفعتان 2-3 (391 SKU) [Unsearched]</li>
</div>
</div>
<div class="rec">🎯 <b>التوصية (الخطوة التالية):</b> تشغيل الدفعة 2 (173 SKU) + فتح حسابات B2B على Turgame Wholesale وFazerCards وReloadly لاستخراج أسعار الجملة الفعلية — هناك يُتوقع أدنى تكلفة اقتناء فعالة، وهي الهدف الرئيسي للمشروع. قرار حوكمة مفتوح للمستخدم: بوابة Bootstrap لاعتماد v4.2 كأول نسخة Approved بعد اجتياز هذا التشغيل الحي.</div>

<footer>MEC-1.0 | Adaptive Supplier Intelligence Research Engine | v4.2 Candidate (working) | كل ادعاء يحمل دليله وحالة تحققه | المخرجات: Web Page + Markdown + JSON (توافق دلالي تام)</footer>
</div>
<script>
const D = __DATA__;
let sortK = 'direct_usd', sortAsc = true;
const tb = document.getElementById('tb'), cnt = document.getElementById('cnt');
function fmtRow(r){
  const stTag = r.state==='Verified-direct' ? '<span class="tag t-ok">مُشاهد مباشرة</span>' : r.state==='Advertised' ? '<span class="tag t-adv">معلن/رسمي</span>' : '<span class="tag t-par">جزئي</span>';
  return `<tr><td><b>${r.sku}</b></td><td>${r.identity}</td><td class="mut">${r.family}</td>`+
    `<td>${r.direct_usd!=null?'<span class="price">'+r.direct_usd.toFixed(2)+'</span>':'—'}</td><td>${r.direct_seller||'—'}</td>`+
    `<td>${r.adv_usd!=null?r.adv_usd.toFixed(2):'—'}</td><td class="mut">${r.adv_seller||'—'}</td>`+
    `<td>${stTag}</td><td class="mut">${r.direct_note||''}</td></tr>`;
}
function render(){
  const q = document.getElementById('q').value.toLowerCase();
  const fam = document.getElementById('fam').value;
  const st = document.getElementById('st').value;
  let rows = D.rows.filter(r =>
    (!q || (r.identity+' '+r.sku+' '+r.family+' '+r.direct_seller).toLowerCase().includes(q)) &&
    (!fam || r.family===fam) && (!st || r.state===st));
  rows.sort((a,b)=>{
    let va=a[sortK], vb=b[sortK];
    if(va==null) return 1; if(vb==null) return -1;
    if(typeof va==='number') return sortAsc?va-vb:vb-va;
    return sortAsc?String(va).localeCompare(String(vb)):String(vb).localeCompare(String(va));
  });
  tb.innerHTML = rows.map(fmtRow).join('');
  cnt.textContent = `عرض ${rows.length} من ${D.rows.length} SKU`;
}
document.querySelectorAll('th').forEach(th=>th.addEventListener('click',()=>{
  const k = th.dataset.k;
  if(sortK===k) sortAsc=!sortAsc; else {sortK=k; sortAsc = th.dataset.n==='1';}
  render();
}));
['q','fam','st'].forEach(id=>document.getElementById(id).addEventListener('input',render));
function resetF(){document.getElementById('q').value='';document.getElementById('fam').value='';document.getElementById('st').value='';render();}
render();
</script>
</body></html>"""

fams_opts = "".join('<option value="%s">%s (%d)</option>' % (f, f, fam_counts[f]) for f in sorted(fam_counts, key=fam_counts.get, reverse=True))
ents_html = "".join(
    '<div class="ent"><b>%s</b> <span class="mut">(%s)</span> — الدور: <b>%s</b><br><span class="tag %s">%s</span><br><span class="mut">%s</span></div>' % (
        e["name"], e["domain"], e["role"],
        "t-ok" if e["state"].startswith("[مؤكد]") and "بحاجة" not in e["state"] else "t-adv", e["state"], e.get("notes",""))
    for e in ents)

nd = len([1 for r in rows if r["direct_usd"] is not None])
html = html.replace("__FAMS__", fams_opts).replace("__ENTS__", ents_html)
html = html.replace("__OK__", str(ok_n)).replace("__TOT__", str(len(actions)))
html = html.replace("__ND__", str(nd)).replace("__NE__", str(len(ents)))
html = html.replace("__DATA__", data_js)

with open(OUT + "/supplier_intelligence.html", "w", encoding="utf-8") as f:
    f.write(html)
print("HTML_OK:", os.path.getsize(OUT + "/supplier_intelligence.html"), "bytes | rows:", len(rows), "| direct:", nd)
