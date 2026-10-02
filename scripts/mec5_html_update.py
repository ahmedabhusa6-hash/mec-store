#!/usr/bin/env python3
"""MEC-5.0: add API price-gap section to download/supplier_intelligence.html (idempotent)."""
import re, json

P = "/home/z/my-project/download/supplier_intelligence.html"
html = open(P, encoding="utf-8").read()

if "mec5sec" in html:
    print("MEC-5 section already present — nothing to do.")
    raise SystemExit(0)

data = json.load(open("/home/z/my-project/src/lib/data/mec5.json"))
ps = data["prodseller"]; sv = data["stackvault"]

# ---- build verdicts table rows ----
vrows = ""
for v in data["verdicts"]:
    st = {"confirmed": "✅ موثق", "partial": "⚠️ جزئي", "hidden": "🔑 خلف دخول",
          "inquiry": "📜 بالتسعير", "none": "— لا فجوة"}.get(v["status"], v["status"])
    vrows += (f'<tr><td dir="ltr"><b>{v["provider"]}</b></td><td>{v["api"]}</td>'
              f'<td class="price" dir="ltr">{v["gap"]}</td><td>{v["n"]}</td>'
              f'<td style="font-size:.78rem">{v["access"]}</td><td>{st}</td></tr>')

# ---- ProdSeller latest rows ----
prows = ""
for r in ps["latest_per_product"][:14]:
    prows += (f'<tr><td dir="ltr">{r["product"]}</td><td class="price" dir="ltr">{r["public"]}</td>'
              f'<td class="price" style="color:var(--ok)" dir="ltr">{r["api"] if r["api"] is not None else "—"}</td>'
              f'<td class="price" style="color:var(--acc)" dir="ltr">{r["bulk"] if r["bulk"] is not None else "—"}</td>'
              f'<td class="price" dir="ltr">{f"{r[chr(103)+chr(97)+chr(112)]}%" if r.get("gap") is not None else "—"}</td>'
              f'<td class="mut" dir="ltr">{r["date"]}</td></tr>')

# ---- StackVault top rows ----
srows = ""
for r in sv["top_gap"][:10]:
    srows += (f'<tr><td dir="ltr">{r["product"]}</td><td class="price" dir="ltr">{r["price"]}</td>'
              f'<td class="price" style="color:var(--ok)" dir="ltr">{r["cost"]}</td>'
              f'<td class="price" dir="ltr">{r["gap"]}%</td><td class="price" style="color:var(--acc)" dir="ltr">{r["x"]}x</td></tr>')

section = f'''
<h2 id="mec5sec">💳 كشف فجوات أسعار API — MEC-5.0: من يبيع بسعرين مختلفين؟ وبكم بالضبط؟ (28/09/2026)</h2>
<div class="meta">Run ID: MEC5-20260928-APIGAP | الزناد: توجيه المستخدم «اكشف السعر مهما كان وبكل الطرق... لكل من يقدم أسعارًا مختلفة في API — ابدأ بـ ProdSeller ثم افحص الآخرين» | المنهجية: استنطاق كل المصادر العلنية المشروعة (أرشيف قناة TG + صور رسمية + وثائق API + Store APIs علنية + وثائق منشورة) — 12 مزودًا فُحصوا بثلاثة وكلاء متوازيين + تحليل محلي</div>

<div class="ent"><b>💥 الاكتشاف الحاكم 1 — ProdSeller: الفجوة مصمَّمة داخل المنصة نفسها (أدلة هيكلية ثلاثية):</b><br>
<span class="mut">(أ) <b>لقطة لوحة التحكم الرسمية</b> (منشور #132 بتاريخ 09/09 «Special hidden API pricing — see example image»): نموذج المنتج يحوي حقلين <span dir="ltr">Price (USD) $1.37</span> + <span dir="ltr">API Price (optional) $1.29</span> لمنتج CapCut Pro 1 Month FW — أي أن لكل منتج سعر API مخفيًا يُضبط يدويًا من الإدارة. (ب) <b>صورة رسمية ثلاثية الطبقات</b> (منشور #134 بتاريخ 11/09): FLASH SELL $0.43 ← API PRICE $0.40 ← BULK PRICE $0.39 (Gemini 18M). (ج) <b>وثائق API العلنية</b>: نقطة <span dir="ltr">GET /v1/products</span> تُرجع حقلين: <span dir="ltr">price</span> (ما يُخصم فعليًا من مفتاحك — قد يكون مخصصًا لحسابك) و<span dir="ltr">publicPrice</span> (المعلن للمرجع). البوابة القديمة <span dir="ltr">51.77.244.194</span> تحولت 301 للموقع الجديد (12/08) — لا نسخة مكشوفة. فحص حي بدون مفتاح: 401 «API key manquante» (فرنسية = تعمل وتنتظر مفتاحك فقط).</span></div>

<div class="ent"><b>📊 الإحصاء الحاكم — فجوة API في ProdSeller عبر 38 صفًا مؤرخًا (79 منشورًا مُستنطَقًا):</b><br>
<span class="mut">أدنى فجوة <b>2.6%</b> (ChatGPT K12: $3.90←$3.80) · الوسيط <b>9.1%</b> · المتوسط <b>12.0%</b> · أقصى فجوة <b>41.4%</b> (Office 365 Plus سنة: $0.29←$0.17). فجوة الجملة (الكمية): متوسط 11.1% (أدنى 2.9% ← أقصى 25%). إعلانهم الرسمي «حتى 35% OFF لمستخدمي API» (20/07) مؤكد جزئيًا بهذه الأرقام — الفئة الغالبة 5–10%، والحالات القصوى (Office 365) تتجاوز 35% فعلًا.</span></div>

<div style="overflow-x:auto;margin:14px 0"><table style="min-width:900px"><thead><tr><th>المنتج (أحدث سعر لكل منتج)</th><th>العام $</th><th>API $</th><th>جملة $</th><th>الفجوة</th><th>التاريخ</th></tr></thead><tbody>{prows}</tbody></table></div>
<div class="mut" style="margin-top:-8px">…الجدول الكامل (38 صفًا زمنيًا + 25 منتجًا بالأحدث) في التبويب 14 بالموقع التفاعلي وملف mec5.json.</div>

<div class="ent"><b>💥 الاكتشاف الحاكم 2 — StackVault: 274 منتجًا بحقل التكلفة مكشوفًا علنًا:</b><br>
<span class="mut">واجهة <span dir="ltr">decohomz.com/sv-api/products</span> (خلفية stackvault.shop) كانت تُرجع لكل منتج حقلين: <span dir="ltr">price</span> (البيع) و<span dir="ltr">costPrice</span> (التكلفة الفعلية). النتيجة الإحصائية عبر 274 منتجًا: فجوة متوسط <b>19.9%</b> · وسيط 16.7% · مدى 13%←57.4%. الأعلى: Apple Music 5M بيع $2.35 / تكلفة $1.00 (2.35x!) · Notion Edu Plus $1.60/$0.80 (2x) · Office 365 Plus $0.38/$0.21 (44.7%) · LinkedIn Career 3M $1.15/$0.65 (43.5%). حسب الفئة: Software Keys 21.0% · Digital Services 20.5% · AI Subscriptions 19.1% · Design & Editing 18.9%. <b>ملاحظة نزاهة:</b> الواجهة تتحقق الآن 403 — البيانات المحفوظة (275 منتجًا) هي من الالتقاط المؤرخ 27/09.</span></div>

<div style="overflow-x:auto;margin:14px 0"><table style="min-width:700px"><thead><tr><th>منتج StackVault (أعلى 10 فجوات)</th><th>البيع $</th><th>التكلفة $</th><th>الفجوة</th><th>المضاعف</th></tr></thead><tbody>{srows}</tbody></table></div>

<div class="ent"><b>🎮 Kinguin — طبقات جملة كمية موثقة في الوثائق الرسمية:</b><br>
<span class="mut">وثائق <span dir="ltr">Kinguin-eCommerce-API</span> العامة (GitHub، محدثة 18/09): كل عرض يحمل <span dir="ltr">wholesale.enabled + tiers[]</span>. المثال الرسمي (Counter-Strike: Source): أساسي $5.79 ← 10+ وحدات $5.50 (-5.0%) ← 50+ $5.40 (-6.7%) ← 100+ $5.30 (-8.5%) ← 500+ $5.20 (-10.2%). البوابات حية مؤكدة (401 منظّم). الوصول: Kinguin ID ← طلب موافقة ← X-Api-Key + sandbox ذاتي الخدمة.</span></div>

<div class="ent"><b>🇹🇷 Turgame — أرضية الكتالوج العلني ~1% فقط والخصومات الحقيقية مخفية:</b><br>
<span class="mut">بوابة الجملة <span dir="ltr">wholesale.turgame.com</span> (4,739 SKU عبر Store API علني بلا دخول): مطابقة 225 منتجًا بالاسم مع التجزئة أعطت فجوة متوسط <b>0.91%</b> فقط (مدى 0.48–1.27%) — هذه «أرضية ما قبل الدخول». خصومات الطبقات الحقيقية (Bronze ₺0 / Silver ₺5K / Gold ₺20K / Platinum ₺50K) سرية داخل البوابة. مثال تحت القيمة الاسمية: Google Play TR 500 جملة 491.64 TRY = 98.3% من الاسمية. الوصول: استمارة + KYC ضريبي + اتفاقية موزع v1.0.0. <b>اكتشاف جانبي:</b> رموز Turgame تتدفق من شبكة EZPIN (retailer_item_id: EZPIN-1065) — منبع أعلى قابل للفحص.</span></div>

<div class="ent"><b>📡 Reloadly + DingConnect + Bitrefill — معايير «سعر API» في صناعة الشحن:</b><br>
<span class="mut"><b>Reloadly</b> (الوحيد الذي ينشر الخصم علنًا): حقل <span dir="ltr">discountPercentage</span> لكل منتج + نقطة <span dir="ltr">GET /discounts</span> — عينات الوثائق: 1-800-PetSupplies 7.5% · Apple Music 12M كندا 2% · Afghan Wireless 10%. تسجيل مجاني ذاتي. <b>DingConnect:</b> نفس البنية لكن الأسعار خلف دخول مجاني. <b>Bitrefill:</b> بلا فجوة (تعادل تجزئة) — يعوّضها revenue share. <b>Z2U / GamsGo / U7BUY:</b> لا فجوة شرائية عبر API — Z2U وGamsGo سوقا C2C (البائعون يحددون الأسعار · عمولات 4.9–9.9%) · API الـU7BUY للبائعين فقط (أتمتة عرض وطلبات، عمولة 10%). <b>SEAGM / OffGamers:</b> B2B استفساري فقط — SEAGM يطلب رأس مال $3,000–50,000 وطلبًا أدنى $10,000.</span></div>

<div style="overflow-x:auto;margin:14px 0"><table style="min-width:950px"><thead><tr><th>المزود (12 فُحصت)</th><th>برنامج API</th><th>الفجوة المكتشفة</th><th>حجم الدليل</th><th>الوصول</th><th>الحالة</th></tr></thead><tbody>{vrows}</tbody></table></div>

<div class="banner" style="border-color:var(--acc)">🏆 <b>الإجابة الحاسمة على توجيهك «اعرف جميع الأسعار للذين يقدمون أسعارًا مختلفة في API»:</b> أربعة فقط من أصل 12: <b>StackVault 19.9%</b> (274 منتجًا — الأعلى) · <b>ProdSeller 12.0%</b> (38 صفًا — الأفضل والأسهل دخولًا) · <b>Kinguin 5–10.2%</b> (طبقات كمية رسمية) · <b>Reloadly 2–10%</b> (منشور لكل علامة). Turgame أرضيته ~1% وخصوماته الحقيقية خلف KYC.</div>

<div class="rec">🎯 <b>التوصية التنفيذية المحدّثة (MEC-5.0):</b><br>1) <b>ProdSeller أولًا</b> (كما أمرت): بوت + رصيد USDT رمزي ← مفتاح <span dir="ltr">psk_...</span> ← <span dir="ltr">GET /v1/products</span> = تحويل كل «أسعار API المخفية» إلى رقم حي لكل منتج لحظيًا — الفجوة المتوقعة 5–12% تحت المعلن.<br>2) <b>Kinguin sandbox</b> فورًا (مجاني وذاتي): سحب الكتالوج كاملًا مع <span dir="ltr">wholesale.tiers</span> لكل عرض.<br>3) <b>Reloadly مجاني</b>: نقطة <span dir="ltr">GET /discounts</span> = جدول خصم علني لكل علامة.<br>4) <b>Turgame wholesale</b>: الاستمارة تكشف خصومات Bronze→Platinum (الوعد: تحت 1% العلنية بكثير).</div>
'''

anchor = '<h2>📡 تقييم سجل القنوات §19'
assert anchor in html, "anchor not found!"
html = html.replace(anchor, section + "\n" + anchor, 1)

# title bump v3.1 → v3.2 + footer note
html = html.replace(
    "<title>قاعدة معلومات الموردين — MEC4-20260928 v3.1 (الكتالوج 437/437 + البحث المتعمق: ProdSeller API بالكامل + دولا + MENA + v4.2 APPROVED)</title>",
    "<title>قاعدة معلومات الموردين — MEC5-20260928 v3.2 (فجوات أسعار API: 12 مزودًا + ProdSeller بالكامل + دولا + MENA + v4.2 APPROVED)</title>", 1)
html = html.replace(
    "<footer>MEC-4.0 DEEP-DIVE |",
    "<footer>MEC-5.0 API-GAP (فجوات أسعار API: StackVault 19.9% · ProdSeller 12.0% · Kinguin 5–10.2% · Reloadly 2–10% · Turgame ~1% علني) | MEC-4.0 DEEP-DIVE |", 1)

open(P, "w", encoding="utf-8").write(html)
print("updated:", P, len(html), "chars")
print("section added: mec5sec | verdicts:", len(data["verdicts"]))
