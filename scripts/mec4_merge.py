#!/usr/bin/env python3
"""MEC-4.0 deep-dive: merge research into offers_intelligence.json + update sku_database.md + worklog entry data.
Idempotent: overwrites the mec4_deep_dive key if re-run."""
import json, hashlib, datetime

BASE = '/home/z/my-project'
offers_path = f'{BASE}/download/offers_intelligence.json'
db_path = f'{BASE}/download/sku_database.md'
dd = json.load(open(f'{BASE}/research/deep_dive/deep_dive_compiled.json'))
channel = json.load(open(f'{BASE}/research/deep_dive/prodseller_channel_archive.json'))

offers = json.load(open(offers_path))

run = {
    'run_id': 'MEC4-20260928-DEEPDIVE',
    'trigger': 'طلب المستخدم: شرح متعمق لكل نقطة (ProdSeller API / دولا / التوكن / MENA) + تحديث الموقع',
    'executed_utc': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
    'prodseller_channel_archive': {
        'source': 't.me/s/ProdSellerOfficial (public preview)',
        'messages': len(channel),
        'date_range': '2026-07-06 → 2026-09-27',
        'evidence_class': 'Directly-Observed (advertised prices, dated posts)',
        'saved_file': 'research/deep_dive/prodseller_channel_archive.json'
    },
    'api_documentation': {
        'docs_url': 'https://prodseller.com/api-docs/',
        'base_url': 'https://prodseller.com/v1',
        'auth': 'X-API-Key: psk_...',
        'rate_limit': '300 req / 15 min / IP',
        'endpoints': ['GET /products', 'GET /products/:id', 'GET /balance', 'POST /orders', 'GET /orders', 'GET /orders/:id'],
        'price_fields': 'price (actual charged, account-specific) vs publicPrice (reference)',
        'verified_live': '401 without key confirmed 28/09 — API operational',
        'evidence_class': 'Directly-Observed (public docs + live probe)'
    },
    'fresh_wholesale_observations': dd['point1_prodseller']['price_timeline_2026'],
    'key_discoveries': {
        'prodseller_identity_complete': 'Bot @prodsellerbot · Channel @ProdSellerOfficial · Support @ProdsellerSupport · Admin @sookbit · WhatsApp +33 7 53 43 44 42 · 15K+ users · 500+ API users',
        'three_tier_structure': 'Retail > API (3-8% off) > Bulk (3-10% more off); advertised up to 35% API discount (20/07)',
        'payments': 'USDT BEP20 fully automated (08/07) + Binance Pay + PayPal manual top-up (09/08)',
        'gemini_18m_saga': '$0.43 bulk (11/09) → discontinued worldwide 28/07 at $1.00 peak → returned $0.95 → $0.44 bulk (27/09) — 127% swing proves factory-layer fragility',
        'duolingo_price_war': '$0.59 → $0.45 → $0.37 in 5 days (19-24/09)',
        'adobe_express_collapse': '$0.94 (17/07) → $0.39 (23/09) = -58% in 2 months',
        'free_methods_published': 'Super Grok India 231 INR method published free (12/07) then sold at $2.90 — factory-layer marketing pattern',
        'api_migration': 'API moved from http://51.77.244.194 to https://prodseller.com (12/08) — maturing infrastructure',
        'dolaa_status': '@dolaa handle does not exist on Telegram (checked 28/09); Arabic-wide search found no indexed trace; competitor ecosystem mapped (RAMZ, Yemen Top, Flousk, egatec-center)',
        'mena_data_confirmed': 'Shahid 13-region Turgame ladder (Algeria €9.47/3M vs Qatar €34.42/3M = 3.6x spread) · StarzPlay UAE full ladder · Anghami Egypt €2.60/1M · OSN+ GC ladder'
    },
    'b2b_gate_verdict': 'ProdSeller API = best entry (lightest: TG bot + USDT, no KYC; most transparent: 79 dated public price posts + public API docs; cheapest trial: products from $0.015)',
    'open_items': [
        'فتح حساب ProdSeller فعلي بيد المستخدم (بوت + رصيد USDT) ← يكشف GET /v1/products كاملاً',
        'قائمة أسعار دولا الفعلية (قناة/لقطات) ← تفعيل حاسبة الهوامش فورًا',
        'تدوير توكن Notion (خطوات 6، ملف القرارات §3) — عاجل',
        'قرار توسعة MENA (40-60 SKU كدفعة P4) — جاهز عند الطلب'
    ]
}

offers['mec4_deep_dive_run'] = run
json.dump(offers, open(offers_path, 'w'), ensure_ascii=False, indent=1)
print('offers_intelligence.json updated: mec4_deep_dive_run key written')
print('total run keys:', [k for k in offers.keys() if k.endswith('_run')])

# ── sku_database.md append ──
section = """
---

## MEC-4.0 — البحث المتعمق: ProdSeller API + دولا + MENA (28/09/2026)

**الزناد:** طلب المستخدم شرحًا متعمقًا لكل نقطة + اعتماد ProdSeller API كخيار أفضل + تحديث الموقع ورفعه.

### 1) ProdSeller API — مشاهد مباشرة جديدة (القناة الرسمية كاملة)

أرشيف القناة الرسمية `t.me/ProdSellerOfficial` استُخرج بالكامل: **79 منشورًا مؤرخًا** (06/07 ← 27/09). الهوية مكتملة: البوت `@prodsellerbot` · الدعم `@ProdsellerSupport` · الأدمن `@sookbit` · واتساب للطوارئ +33 7 53 43 44 42 · الحجم 15K+ مستخدم / 8K+ نشط شهريًا / 500+ مستخدم API.

**وثائق API علنية حية** (`prodseller.com/api-docs/`): Base URL `https://prodseller.com/v1` · مصادقة `X-API-Key: psk_...` · حد 300 طلب/15 دقيقة · نقاط: products / products/:id / balance / POST orders / orders / orders/:id · حقلان للسعر: `price` (المحاسب فعليًا — مخصص للحساب) مقابل `publicPrice` (المرجعي) · خصمان تلقائيان membershipDiscount + bulkDiscount · Idempotency-Key · منتجات تفعيل بالبريد (pending→paid→delivered) · **فُحص حيًا 28/09: 401 بدون مفتاح = الخدمة تعمل**. الدفع: USDT BEP20 مؤتمت (منذ 08/07) + Binance Pay + PayPal يدوي (منذ 09/08).

**أسعار جملة ثلاثية الطبقات طازجة (مختارات — الجدول الكامل 30 صفًا في deep_dive_compiled.json):**

| التاريخ | المنتج | عام $ | API $ | جملة $ |
|---|---|---|---|---|
| 27/09 | Gemini 18M | 0.48 | — | 0.44 |
| 27/09 | CapCut 1M | 1.29 | 1.25 | 1.20 |
| 24/09 | Duolingo Super 12M | 0.37 | 0.36 | 0.34 |
| 23/09 | Adobe Express 12M (Link) | 0.39 | 0.37 | — |
| 20/09 | Office 365 Plus 1Y | 0.29 | 0.17 | 0.17 |
| 20/09 | ChatGPT K12 + Codex | 3.90 | 3.80 | — |
| 19/09 | Gmail Stable | 0.80 | 0.75 | 0.60 |
| 09/09→ | Gemini 18M ساغا | 0.43→1.00→0.44 | +127% تأرجح | |

**قصة Gemini 18M كاملة (دليل هشاشة طبقة المصانع):** $0.43 جملة (11/09 سابقًا 21/07 $0.43) ← **انقطاع عالمي 28/07** («العرض لم يعد متاحًا عالميًا — الكل يبيع $2+») ← عاد بطريقة تفعيل جديدة $1.00 ← $0.80 ← $0.65 ← $0.48/$0.44 (27/09). حرب Duolingo: $0.59←$0.45←$0.37 خلال 5 أيام. انهيار Adobe Express: -58% في شهرين.

**نمط تسويقي مكشوف:** ينشرون «الطرق» مجانًا ثم يبيعون المنتج الجاهز (Super Grok طريقة الهند 231 INR مجانية 12/07 ← المنتج $2.90 يوم 19/09).

**إشارات خطر موثقة:** روابط Gemini تعطلت وأُصلحت (16/09) · أدمن واحد يعالج 200+ رسالة يوميًا (26/07) · «نعيد بناء الثقة» (27/08) · تشغيل مجهول الهوية (أخطاء فرنسية + واتساب فرنسي + لا بيانات شركة) · ضمانات متفاوتة 24 ساعة ← مدى الحياة.

**حكم المقارنة (الشرط الصارم للمستخدم «أفضل من هذا؟»):** نعم — ProdSeller API أفضل من كل البدائل: أخف دخولًا (بوت + USDT، لا KYC — مقابل Reloadly KYC كامل)، أعلى شفافية (79 منشور سعر علني + وثائق API عامة — مقابل Turgame/FazerCards خلف الدخول)، أرخص تجربة (منتجات من $0.015).

### 2) دولا — الفحص المحدث + الحاسبة

`@dolaa` **غير موجود** في تيليجرام (فُحص 28/09). بحث عربي واسع (4 صياغات) بلا أثر مفهرس. **المنظومة المنافسة المكتشفة:** متجر رمز RAMZ · يمن توب · محفظة فلوسك · egatec-center — نفس العائلات في نفس السوق = مراجع مقارنة فورية. **الحاسبة جاهزة** بأرضيات جملة طازجة: ChatGPT Plus (هش) أرضية $2.80 ← بيع $6.67 = 58% · Gemini 18M أرضية $0.44 ← سوق $0.85 = 93% · Office365 أرضية $0.17 = هامش 83-94%. **المطلوب من المستخدم:** رابط القناة أو لقطات الأسعار (10-15 منتجًا تكفي) — الجدول الكامل يُنتج فورًا.

### 3) توكن Notion (D5) — الخطوات الست جاهزة

في ملف القرارات §3: my.integrations.com ← تكامل «موردين» ← Generate new token ← تحديث `.env` ← (اختياري: تقليص الوصول) ← «تحقق من التوكن». 5 دقائق بيد المستخدم — عاجل (R7).

### 4) توسعة MENA — البيانات المؤكدة

سلم Turgame الكامل (مشاهد مباشر 27/09): **شاهد** 3 أشهر: الجزائر €9.47 · مصر €9.52 · ليبيا €10.41 · تونس €10.58 · المغرب €10.94 · فلسطين €11.74 · لبنان €11.76 · الأردن €12.59 **مقابل** عمان €31.20 · البحرين €31.45 · الإمارات €32.48 · الكويت €33.48 · قطر €34.42 = **فارق 3.6x شمال إفريقيا/الخليج** · مصر 12 شهر €33.16 (€2.76/شهر = 80% تحت الرسمي $13.99) · Kinguin $6.77 · GamsGo ~$7 · Zain Iraq 4999 IQD (~$3.80). **StarzPlay** الإمارات: 40/100/195/330 AED = €10.22/25.48/49.68/89.07. **أنغامي**: مصر €2.60 (أرخص) مقابل الأردن/الكويت €5.20. **OSN+**: كويت 3M €33.83 · مغرب 6M/12M €35.82/59.68 + حزمة Epic مع شاهد وDisney+.

**خطة التوسعة:** 40-60 SKU · الأولوية: شاهد ← أنغامي ← StarzPlay ← OSN+ · القرار متاح عند الطلب (دفعة P4 بنفس منهجية الدفعات 1-3).

### ملفات هذا التشغيل
`research/deep_dive/` (prodseller_channel_archive.json · prodseller_api_docs.txt · deep_dive_compiled.json) · `src/lib/data/deep-dive.json` · تبويب «🔬 البحث المتعمق» في الموقع (التبويب 13) · `download/supplier_intelligence.html` §MEC-4.0.
"""

content = open(db_path).read()
if 'MEC-4.0 — البحث المتعمق' not in content:
    content += section
    open(db_path, 'w').write(content)
    print('sku_database.md: MEC-4.0 section appended')
else:
    print('sku_database.md: MEC-4.0 already present (idempotent)')

print('DONE')
