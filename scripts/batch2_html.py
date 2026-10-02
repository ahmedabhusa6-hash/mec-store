#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEC-2.1 | Upgrade supplier_intelligence.html to v2.1 (Batch 2 integration)."""
import json, re

BASE = "/home/z/my-project"
html = open(BASE + "/download/supplier_intelligence.html", encoding="utf-8").read()
offers = json.load(open(BASE + "/download/offers_intelligence.json", encoding="utf-8"))
b2 = {sid: rec for sid, rec in offers["skus"].items() if rec.get("batch") == 2}

# ── build D2 rows ──
rows = []
for sid, rec in b2.items():
    valid_offers = [o for o in rec.get("offers", []) if not o.get("identity_flag")]
    best = min(valid_offers, key=lambda x: x["usd"]) if valid_offers else None
    official = rec.get("official")
    rl = "Rate-Limited" in rec.get("ledger_state", "")
    if best:
        state = "B2-Advertised"
    elif rl:
        state = "B2-RateLimited"
    elif official:
        state = "B2-OfficialOnly"
    else:
        state = "B2-LeadOnly"
    rows.append({
        "sku": sid, "family": rec.get("family", ""), "identity": rec.get("identity", ""),
        "adv_usd": best["usd"] if best else None,
        "adv_seller": (best.get("seller", "")[:38] if best else ""),
        "off_usd": official.get("usd") if official and official.get("price") is not None else None,
        "state": state,
        "note": (best.get("note", "")[:120] if best else (rec.get("state_note", "") or rec.get("official", {}).get("note", ""))[:120]),
    })
rows.sort(key=lambda r: r["sku"])

n_off = len([r for r in rows if r["state"] == "B2-Advertised"])
n_offl = len([r for r in rows if r["state"] == "B2-OfficialOnly"])
n_rl = len([r for r in rows if r["state"] == "B2-RateLimited"])
n_lead = len([r for r in rows if r["state"] == "B2-LeadOnly"])
D2 = json.dumps({"rows": rows}, ensure_ascii=False)

# ── 1. title + meta ──
html = html.replace(
    "<title>قاعدة معلومات الموردين — MEC2-20260927 v2.0 (سجل القنوات §19 + اقتصاديات التوريد)</title>",
    "<title>قاعدة معلومات الموردين — MEC2-20260927-B2 v2.1 (الدفعة 2: 173 SKU + سجل القنوات §19 + اقتصاديات التوريد)</title>")
html = html.replace(
    'Run ID: MEC2-20260927 (تحديث شامل فوق MEC1-B1) | الإصدار: v4.2 Candidate (working) | النطاق: الكتالوج CP-1 + سجل القنوات §19 (مُوثّق حيًا) | التاريخ: 2026-09-27',
    'Run ID: MEC2-20260927-B2 (الدفعة 2 فوق MEC-2.0) | الإصدار: v4.2 Candidate (working) | النطاق: الكتالوج CP-1 (46 P1 + 173 P2 منفذة) + سجل القنوات §19 | التاريخ: 2026-09-27')

# ── 2. stats ──
html = html.replace(
    '<div class="stat"><div class="n">46</div><div class="l">SKU الدفعة 1 (منفذة)</div></div>',
    '<div class="stat"><div class="n">219</div><div class="l">SKU بسجلات ذكاء (46+173)</div></div>')
html = html.replace(
    '<div class="stat"><div class="n">86</div><div class="l">إجراء بحثي ناجح (من 142)</div></div>',
    '<div class="stat"><div class="n">201</div><div class="l">إجراء بحثي ناجح (86+115)</div></div>')
html = html.replace(
    '<div class="stat"><div class="l" style="margin-top:8px">الدفعات 2-3: 391 SKU<br>حالة صادقة: Unsearched</div></div>',
    '<div class="stat"><div class="n" style="color:var(--ok)">47</div><div class="l">SKU الدفعة 2 بعروض معلنة</div></div>\n<div class="stat"><div class="l" style="margin-top:8px">الدفعة 3: 218 SKU<br>حالة صادقة: Unsearched</div></div>')

# ── 3. insert Batch-2 section after batch-1 table note ──
B2_SECTION = '''
<h2 id="b2sec">🆕 ذكاء الأسعار — الدفعة 2 (173 SKU من P2 — 27/09، دليل مستوى «معلن»)</h2>
<div class="banner" style="border-color:var(--warn)">⚠️ <b>حدود دليل هذه الدفعة:</b> كل الأسعار أدناه <b>معلنة عبر مقتطفات بحث</b> (القراءة المباشرة للصفحات مؤجلة — استُنفدت حصة الوظائف البعيدة منتصف التشغيلة وفق §19). 15 استعلامًا مؤجلًا (18 SKU بحالة Rate-Limited). ضجيج الاستخراج الآلي استُبعد بمراجعة يدوية — كل صف يحمل ملاحظة هويته.</div>
<div class="controls">
<input id="q2" type="text" placeholder="🔍 ابحث في الدفعة 2: PSN، Windows، eSIM…">
<select id="fam2"><option value="">كل الأسر</option><option value="Gift Cards">Gift Cards</option><option value="Digital Subscriptions">Digital Subscriptions</option><option value="AI/SaaS">AI/SaaS</option><option value="Game Top-up">Game Top-up</option><option value="Virtual Numbers">Virtual Numbers</option><option value="Game Keys">Game Keys</option><option value="SMM Services">SMM Services</option><option value="eSIM">eSIM</option><option value="Software/Licenses">Software/Licenses</option><option value="API Services">API Services</option></select>
<select id="st2"><option value="">كل الحالات</option><option value="B2-Advertised">بعرض معلن (47)</option><option value="B2-OfficialOnly">خط رسمي فقط</option><option value="B2-LeadOnly">Lead-only</option><option value="B2-RateLimited">مؤجل (حد المعدل)</option></select>
<button onclick="resetF2()">إعادة تعيين</button>
</div>
<div class="count" id="cnt2"></div>
<div style="overflow-x:auto"><table id="tbl2">
<thead><tr>
<th data-k2="sku">SKU</th><th data-k2="identity">الهوية التجارية</th><th data-k2="family">الأسرة</th>
<th data-k2="adv_usd" data-n="1">أفضل معلن (USD)</th><th data-k2="adv_seller">البائع</th>
<th data-k2="off_usd" data-n="1">خط رسمي (USD)</th><th data-k2="state">الحالة</th><th data-k2="note">ملاحظة الهوية/الدليل</th>
</tr></thead><tbody id="tb2"></tbody></table></div>
<div class="grid2" style="margin-top:14px">
<div class="ent"><b>🇦🇷 اكتشاف الدفعة 2 الأول — سوق العلاوة الأرجنتيني</b><br><span class="mut">بطاقات PSN الأرجنتينية تُباع <b style="color:var(--err)">فوق</b> قيمتها الاسمية: بطاقة $50 عند ~$67.91 (K4G، معدل $1.35/دولار) — عكس منطق الخصم كليًا. السبب البنيوي: متجر AR أرخص داخليًا فالبطاقة أداة وصول مُراجَح. العرض الوحيد تحتها ($34.81 إينابا) كان «نفد» لحظة الرصد — ندرة العرض تحت الاسمي.</span></div>
<div class="ent"><b>🎮 اكتشاف الدفعة 2 الثاني — «رمادي» ليس مرادف «أرخص»</b><br><span class="mut">G2A يبيع 660 PUBG UC بـ$26.61 أي <b style="color:var(--err)">+166% فوق الرسمي</b> ($9.99) — قناة رمادية تسعّر راحة الدفع البديل لا الخصم. وفي المقابل منتديات رمادية (sythe.org) تعرض 2800 V-Bucks بـ$6.99 (تحت المتاجر بـ~65%) — طبقة أدنى بلا أي حماية منصة. القاعدة: لا افتراض خصم — تحقق لكل قناة×منتج.</span></div>
</div>
<div class="ent"><b>📋 خطوط رسمية وثّقتها الدفعة 2 (مقتطفات رسمية 27/09):</b><br><span class="mut">ChatGPT <b>Go $8</b> · Plus $20 (<b>لا فوترة سنوية رسمية — كل «Plus 12 شهرًا» بناء رمادي بطبيعته</b>) · Pro $200 (وإشارة «From $100» تحتاج تحققًا) · Claude Max $100/$200 · Midjourney Basic $10 (سنوي $8/ش) / Standard $30 · GitHub Copilot Pro $10 · Welkin Moon $4.99 · Disney+ with Ads $9.99 · Google One 100GB $1.99 · Netflix Ads $8.99 (يعزز الدفعة 1) · NordVPN سنة $4.59–5.99/ش · PS+ Essential 3 أشهر $24.99 / سنة $79.99 · PUBG UC رسمي: 325=$4.99 / 660=$9.99 / 1800=$24.99 · Office 2024 عند <b>$0.56–0.60 عبر مصدرين مستقلين</b> (Keyforsteam مباشرة + Keys4us مقتطفًا) — تقارب يرفع الثقة بالأرضية.</span></div>
'''
anchor = '<p class="mut" style="margin-top:10px">«مباشر» = صفحة مقروءة فعليًا بتاريخ الفحص | «معلن» = مقطع نتيجة بحث (Lead) | مشاهدات 25/09 موسومة قِدَمًا محتملًا (يومان). أسعار الجملة خلف بوابات تسجيل الدخول = Unknown.</p>'
html = html.replace(anchor, anchor + B2_SECTION)

# ── 4. audit record additions ──
html = html.replace(
    '<li><b>الميزانية (MEC-2.0):</b> 26 استعلام بحث + 41 طلب رصد مباشر (31 كيان + 9 معاينات + متجر) بإيقاع مُدار → <b style="color:var(--ok)">صفر إخفاق</b> (مقابل 14% في تشغيلة سابقة) — درس إدارة المعدل مُطبّق وموثّق.</li>',
    '<li><b>الميزانية (MEC-2.0):</b> 26 استعلام بحث + 41 طلب رصد مباشر (31 كيان + 9 معاينات + متجر) بإيقاع مُدار → <b style="color:var(--ok)">صفر إخفاق</b> (مقابل 14% في تشغيلة سابقة) — درس إدارة المعدل مُطبّق وموثّق.</li>\n<li><b>الميزانية (MEC-2.1 / الدفعة 2):</b> 121 استعلامًا مخططًا → 115 ناجحًا + 15 مؤجلًا (حصة 477 طويلة النافذة &gt;45 دقيقة رغم التبريد — يُحتمل حصة تراكمية يومية ~230 استعلامًا عبر الجلسات). الإيقاع 5 ث + تبريد 15 ث + استئناف آمن بميزانية زمنية. الاستئناف موصوف في sku_database.md §هـ.</li>')
html = html.replace(
    '<li>الدفعتان 2-3 (391 SKU) [Unsearched]</li>',
    '<li>الدفعة 3 (218 SKU P3) [Unsearched] · الدفعة 2: نفذت بمستوى مقتطفات — القراءة المباشرة لأفضل 47 مرشحًا مؤجلة</li>')

# ── 5. footer ──
html = html.replace(
    'المخرجات: Web v2.0 + Markdown + JSON + Notion مُزامَن (توافق دلالي) | سجل الأدلة: mec2_channels_raw.json · mec2_search_results.json',
    'المخرجات: Web v2.1 + Markdown + JSON + Notion مُزامَن (توافق دلالي) | سجل الأدلة: mec2_channels_raw.json · mec2_search_results.json · findings_index_b2.json · batch2_intelligence_draft.json')

# ── 6. append D2 data + logic before </script> ──
JS2 = '''
const D2 = ''' + D2 + ''';
let sortK2 = 'adv_usd', sortAsc2 = true;
const tb2 = document.getElementById('tb2'), cnt2 = document.getElementById('cnt2');
function fmtRow2(r){
  const stTag = r.state==='B2-Advertised' ? '<span class="tag t-adv">عرض معلن</span>' :
    r.state==='B2-OfficialOnly' ? '<span class="tag t-ok">خط رسمي فقط</span>' :
    r.state==='B2-RateLimited' ? '<span class="tag" style="background:#2a1c1c;color:var(--err);border:1px solid var(--err)">مؤجل §19</span>' :
    '<span class="tag t-par">Lead-only</span>';
  return `<tr><td><b>${r.sku}</b></td><td>${r.identity}</td><td class="mut">${r.family}</td>`+
    `<td>${r.adv_usd!=null?'<span class="price">'+r.adv_usd.toFixed(2)+'</span>':'—'}</td><td class="mut">${r.adv_seller||'—'}</td>`+
    `<td>${r.off_usd!=null?r.off_usd.toFixed(2):'—'}</td>`+
    `<td>${stTag}</td><td class="mut">${r.note||''}</td></tr>`;
}
function render2(){
  const q = document.getElementById('q2').value.toLowerCase();
  const fam = document.getElementById('fam2').value;
  const st = document.getElementById('st2').value;
  let rows = D2.rows.filter(r =>
    (!q || (r.identity+' '+r.sku+' '+r.family+' '+r.adv_seller+' '+r.note).toLowerCase().includes(q)) &&
    (!fam || r.family===fam) && (!st || r.state===st));
  rows.sort((a,b)=>{
    let va=a[sortK2], vb=b[sortK2];
    if(va==null) return 1; if(vb==null) return -1;
    if(typeof va==='number') return sortAsc2?va-vb:vb-va;
    return sortAsc2?String(va).localeCompare(String(vb)):String(vb).localeCompare(String(va));
  });
  tb2.innerHTML = rows.map(fmtRow2).join('');
  cnt2.textContent = `عرض ${rows.length} من ${D2.rows.length} SKU (الدفعة 2)`;
}
document.querySelectorAll('[data-k2]').forEach(th=>th.addEventListener('click',()=>{
  const k = th.dataset.k2;
  if(sortK2===k) sortAsc2=!sortAsc2; else {sortK2=k; sortAsc2 = th.dataset.n==='1';}
  render2();
}));
['q2','fam2','st2'].forEach(id=>document.getElementById(id).addEventListener('input',render2));
function resetF2(){document.getElementById('q2').value='';document.getElementById('fam2').value='';document.getElementById('st2').value='';render2();}
render2();
'''
html = html.replace('</script>', JS2 + '</script>')

open(BASE + "/download/supplier_intelligence.html", "w", encoding="utf-8").write(html)
print("HTML v2.1 written: %d bytes | D2 rows: %d (offers=%d official-only=%d lead=%d rate-limited=%d)"
      % (len(html), len(rows), n_off, n_offl, n_lead, n_rl))
