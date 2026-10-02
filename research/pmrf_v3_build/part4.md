---

## 21. Architecture

### 21.1 معمارية sv-api وStackVault (المفحوصة بالأدلة)
- MongoDB خلف Express: ObjectId بكبسولات زمنية + بصمات جهاز/ProcessID (أدلة G-1: 151 ObjectId مشترك + 8 بصمات خادم Mongo بين cb_ وps_).
- الحوض الكتالوجي الفيتنامي المشترك: canboso/HitMeow منصة شقيقة (111/101 اسمًا و101/111 وصفًا متطابقًا) — الاستبعاد الجماعي الموثق لـ9 منصات في R3/R4/R5/R6 (صفر تطابق مع ProdSeller(26) · laha(15) · AIVerseX(35) · GeminiShop(6) · acczone(4) · DigitalCore(11)).
- البادئات كدلالة توريد: cb_ (حساب جملة على المنصة) · ps_ (منصة نفسها) · mr_ (يدوي) · tgb_ (لوحة canboso) · UUID (DigitalCore) · rsk_ (RichAI) · AK_ (AIXpress) · sk- (بوابة fork).

### 21.2 معمارية متجر mec-store (مفحوصة هذه الجولة)
[Source: extract_scripts_src.json — src/ 80 ملفًا]
- الطبقات: صفحات (5) → مكونات (28) → lib (25) → Prisma (10 جداول) → Supabase → Railway.
- مسارات الـAPI (14): مصفوفة كاملة في §20.3 — منها admin (sync/costs/stats) وwallet (deposit) وorders (restock).
- جداول قاعدة البيانات: Product · Supplier · ChainLink · GeoPrice · Order · Attempt · Wallet · WalletTx · Waitlist · SyncLog [Source: prisma/schema.prisma].

### 21.3 معمارية البوابات
New API خلف Cloudflare (teamsoclo) · Workers (jcc) · Pages (docs) — ثلاث نطاقات فرعية تعمل بلا جذر موقع (AF-2: teamsoclo.site الجذر NXDOMAIN).

---

## 22. Infrastructure

| المكون | البنية | الشاهد |
|---|---|---|
| صندوق OVH الواحد | 51.77.244.194 (Strasbourg) — يستضيف: منصة prodseller.com + باكند StackVault (sv-api) + طُعم decohomz | VERIFIED (v1.4 — vhost) |
| Netlify | واجهة StackVault (stackvaultbot.netlify.app) | موثق |
| OVH عمومًا | أخطاء «Route introuvable» الفرنسية + ساعات CEST 100% — بنية فرنسية | G-1a |
| Railway | استضافة متجر mec-store (وضع sandbox) + lahastore.up.railway.app (HitMeow) 200 | موثق |
| Supabase | Postgres لمتجر المستخدم (pgbouncer=true جذر زمن الاستجابة +790ms — محلول موثق) | MEC-21-D |
| Cloudflare | حماية البوابات + AF (gg.deals خلفه — Retrieval-Limited) | موثق |
| الخوادم المتعددة | AiVerseX (موثق نصيًا) · pool حسابات teamsoclo خلف بوابة | نصي |

---

## 23. Data and Datasets

### 23.1 سجل البيانات الموحد (المصدر الوحيد للحقيقة لبرنامج MEC)
[Source: download/offers_intelligence.json — 267KB]
- البنية: generated · run · fx_basis (USD/EUR/GBP/RUB/TRY/AED) · skus · price_intelligence · mec2_run · batch2_run · b3_direct_run.
- قاعدة D2 المعتمدة: Web + Word + Markdown تُولَّد منه ولا تُحرَّر يدويًا بشكل منفصل.

### 23.2 البيانات المجرودة (بحسب جرد هذه الجولة)
| مجموعة البيانات | الحجم/العدد | الشاهد |
|---|---|---|
| research/ كاملة | 79.1MB · 1,049 ملفًا (12 مجلدًا + 79 JSON جذريًا) | discovery.json |
| notion_raw/ | 27.7MB — 31 قاعدة بيانات (825 صفًا معدودة) + 546 صفحة + 546 نصًا | extract_notion.json |
| الكتالوج الموحد | 1,127 سجلًا (11 كيانًا 1,112 + بوابة 15) | sv_master_catalog_consolidated |
| كتالوجات SV المؤرخة | 357 → 345 → 282 → **280** | سلسلة موثقة (§17.2) |
| كتالوج المتجر | 437 SKU في 10 أسر | catalog_v42.json |
| قنوات مصنفة | 91 قناة (مصفوفة MEC-2.4) | channel_matrix.json (57 marketplace) |
| GDS | 230 كيانًا مؤهلًا (من 1,928 مرشحًا: 395 مرفوضة + 1,348 أدلة غير كافية) | gds_qualified_entities |
| سجل القنوات §19 | 31 كيانًا (قائمة المستخدم الحاكمة) | المرجع الحاكم (pre-project) + MEC-2.0 |
| action ledger | 415 إجراء بحثي مؤرخ (RA-001→RA-415) | research/action_ledger.json |
| verified_extractions | 17 استخراجًا متحققًا (RA-122→RA-140) | research/verified_extractions.json |
| بيانات الأدلة الحية | موجات g1 (raw1-6) · g1a (r1-r6) · sv_supply5→9 · b3_* (17) | سلاسل موثقة في worklog |

### 23.3 تكاملات موثقة
API ProdSeller (STALE منذ 29/09 — المفتاح غائب C5) · نقاط New API العامة · Notion (لقطة 26/09 — التوكن غائب AF-5) · قنوات t.me/s/ الثماني (حي حتى شاهد v3.0).

---

## 24. Research Knowledge Base

### 24.1 برامج البحث (مسلسلة بالتنفيذ)
| البرنامج | الموجات/الجولات | الناتج الحاكم |
|---|---|---|
| الموجات التأسيسية (pre-project) | 26 استعلامًا (25/09) — 15 صفحة فُتحت منها 14 بنجاح (الفاشل: GG.deals خلف Cloudflare) | 3 قواعد بيانات عالمية + مرجع حاكم 333KB |
| MEC-1.0/2.x (دفعة 1-3) | 437 SKU · 415 إجراء (RA-001→415) · 3 تشغيلات حية بمعمارية v4.2 | كتالوج مغلق + اقتصاد السلسلة + 12 تناقضًا محلولًا |
| MEC-5 (فجوات API) | Turgame/GamsGo · Kinguin/SEAGM/OffGamers (Hydron Deck 13 صفحة) · Z2U/U7BUY/Reloadly/DingConnect/Bitrefill | فجوات أسعار API موثقة |
| GDS-1/2 | 131 خام → 910 بذور → 230 مؤهلًا | نقطة حفظ 04:20Z (29/09) |
| SV-INTEL→SV-SUPPLY-9 | 9 موجهات | خريطة 5 طبقات + قائمة أسعار البوابة |
| G-1 ( closure) | مسح جنائي + R2 + R3 (12 مجموعة مفاتيح) | حسم معماري/منصيّ/حوضي |
| G-1a (r1→r6) | RDAP/DNS/CT + PlayerUp + websearch + VLM | هوية «SookBit» + الصندوق الواحد |
| SV-MASTER-CATALOG | توحيد 11 كتالوجًا | 1,127 سجلًا + 7 أوراق Excel |
| SV-NEG-CAMPAIGN | تصميم تفاوضي | 8 أطراف · 30 سيناريو · 11 ورقة ضغط |
| PMRF v1.0→v3.0 | 8 إصدارات | هذا الملف (سلسلة كاملة محفوظة) |

### 24.2 أدلة البحث الجوهرية (بالجرد الفعلي)
- g1_rescan_raw1-6 (985KB · 52KB · 14.5KB · 95.9KB · 70.2KB · 136.8KB) — موجات مسح cb_ الكاملة (357 عنوانًا/وصفًا).
- g1_r3_newkeys_raw (427KB) + analysis (37.8KB) + final (S1-S5: تفكيك عائلي 111 وصفًا · مصفوفة حوض 550) — جولة المفاتيح الثانية.
- g1a_r1→r6 (40.6KB · 6.4KB · 9.3KB · 53KB r4 + samebox 3.7KB + objectid 5.3KB · 8.4KB · playerup 809B + websearch 22KB) — سلسلة هوية المشغّل.
- sv_supply5→9 + dated_messages + supplement — تاريخ القنوات المؤرخ.
- b3_* (17 ملفًا: allkeyshop · bittopup · channel_history 44.8KB · direct_observations 55.4KB · k4g · plati ×2 · prefill ×2 · specified_channels · tg_extended · turgame ×5) — مسار B3.
- mec5/ (227 ملفًا: 205 مفحوصة مخططيًا + 8 صورNA + 13 جزئيًا + 1 HTML-mislabeled) — أبحاث فجوات API (agentA/agentB/agentC خام).
- pmrf_v2_build/ (7 أجزاء) — بناء v2.0 التاريخي (HISTORICAL_BUILD_INTERMEDIATE).

---

## 25. Evidence Register

> سجل الأدلة الجوهرية — كل قيد: النوع + القوة + الموصل. مرتبة حسب الطبقة الدلالية (توجيه §12: أدلة أولية > سجلات داخلية > ادعاءات).

| ID | الدليل | النوع | القوة | الموصل |
|---|---|---|---|---|
| E-01 | استجابة sv-api الحية (كتالوج 280 · صفر costPrice) | شاهد مباشر مؤرخ | عالية جدًا | research/pmrf_v3_live_update_20261002.json (07:39:16+03) |
| E-02 | بوابة teamsoclo (15 موديلًا — إصدار a42d372c) | شاهد مباشر مؤرخ | عالية جدًا | نفس الملف + sv_master_gateway_pricing |
| E-03 | معاينات t.me/s/ الثماني (طوابع آخر رسالة) | شاهد مباشر مؤرخ | عالية | pmrf_v3_live_update |
| E-04 | موجات g1_rescan (عناوين/أوصاف cb_ 357) | التقاط خام | عالية جدًا | g1_rescan_raw1-6_20261002.json |
| E-05 | جولة R3 بالمفاتيح (11 مجموعة) | التقاط خام مفاتيح | عالية | g1_r3_newkeys_raw + g1_r3_final (S1-S5) |
| E-06 | أدلة ObjectId المشتركة (151 + 8 بصمات) | تحليل جنائي | عالية جدًا | g1_cb_findings + g1a_r3_objectid_forensics |
| E-07 | سلسلة هوية SookBit (RDAP/DNS/CT + PlayerUp 09/01/2025 + VLM) | تحقيق هوية | عالية | g1a_r1/r2/r5/r6 + g1a_media |
| E-08 | صندوق OVH الواحد 51.77.244.194 (vhost مشترك) | تحليل بنية | عالية | g1a_r4_samebox |
| E-09 | أرشيف costPrice المكشوف (274/275 — 27/09) | التقاط خام تاريخي | عالية جدًا (مغلقة المصدر الآن) | supply_chain_economics §10 + worklog MEC-2.3 |
| E-10 | سجل التفاوض التأسيسي + المرجع الحاكم (25/09) | وثيقة مُدمجة (INGESTED) | عالية (وثيقة مستقلة سابقة للمشروع) | notion_raw/text/3e55…txt + 3e65…txt |
| E-11 | الكتالوج الموحد (1,127) | تجميع مشتق | عالية (مصادر موثقة البنية) | sv_master_catalog_consolidated |
| E-12 | مصفوفة حملة التفاوض (8 أطراف · 30 سيناريو · 14/14 فحصًا) | مخرج تحليلي مدقق | عالية | download/مصفوفة_حملة_التفاوض.xlsx |
| E-13 | اقتصاديات السلسلة (7 نماذج + معادلة الوحدة) | مخرج بحثي (الشرط الصارم) | عالية | supply_chain_economics.md |
| E-14 | قواعد بيانات Notion (31 قاعدة · 825 صفًا) | لقطة ثابتة | متوسطة-عالية (STALE منذ 26/09) | notion_raw/ |
| E-15 | أدلة GDS (230 كيانًا — 204 HIGH) | مسح مؤهل | عالية | gds_qualified_entities + candidates/harvest |
| E-16 | تقارير تدقيق المتجر (10 موجات — MEC-18→21) | تدقيق مستقل | عالية | research/audit/ + download/MEC-20/21 |
| E-17 | أدلة me5 (فجوات API: Hydron Deck 13 صفحة) | التقاط خام + مستندات تجار | متوسطة-عالية | research/mec5/agentB_raw |
| E-18 | ادعاءات القنوات عن نفسها (أعداد مشتركين · «5-8k رابط/يوم» · «1-2% UPI») | SOURCE_CLAIM | منخفضة (غير مستقل الشاهد) | خرائط المستخدم + القنوات |

---

## 26. Source Register

### 26.1 مصادر البيانات الحية (الأولية)
decohomz.com/sv-api/products (الشاهد v3.0) · gpt.teamsoclo.site/api/{status,pricing} · t.me/s/{8 قنوات} · 14 نطاقًا عامًا · أسطح المفاتيح (canboso/tgb_ · DigitalCore/UUID · RichAI/rsk_ · AIXpress/AK_) بشاهد R3 (06:40+03 — C11).

### 26.2 مصادر ما قبل المشروع (طبقة تأسيسية — INGESTED)
[Source: notion_raw/text/ — مفحوصة هذه الجولة]
- المرجع الحاكم — قاعدة بيانات أرخص الموردين (333KB · 25/09) — **المصدر الأصلي لقائمة القنوات §19 (31 كيانًا) وقنوات التحقيق اللاحقة (@stackvault_support · @ProdSellerBot...)**.
- مصدر — global_digital_products_database.md (122KB · v1.0 · 25/09).
- مصدر — cheapest_digital_products_suppliers_database.md (33KB · 26 استعلامًا · 4 عملاء استرشاديين: Mega Center · Al Momaiz Card · FazerCards · Turgame).
- مصدر — global_digital_suppliers_database.md (33KB).
- سجل تاريخي — تفاوض موردي الخدمات الرقمية | Stack Vault Support (55KB · 25/09).
- Supplier Intelligence Prompt Lab — ChatGPT × Claude (37KB) + v4.0/v4.1 (46KB).
- Central Automation Runtime (137KB · 26/09) + تدقيق نظام الأتمتة 24/7 (27KB) + مرجع هندسة الأتمتة (33KB).
- 🧠 KOS Master Hub (92KB) + التسويق العميق (48KB) + معجم البحث العميق (22KB).

### 26.3 الملفات المرجعية (ثانوية — قابلة للتتبع)
worklog.md (1,224 سطرًا · 61 معرف مهمة) · research/pmrf_v3_{discovery,extract_*} (ملفات هذه الجولة) · sv_master_catalog_consolidated · مصفوفة/دليل حملة التفاوض · سلاسل g1/g1a/b3/sv_supply · global_suppliers · audit/ (تدقيق المتجر) · download/ (52 مخرجًا) · PMRF_ARCHIVE (v1.5 + v2.0).

---

## 27. Decision Ledger

| ID | القرار | الحالة | الشاهد | ملاحظات النفاذ |
|---|---|---|---|---|
| D1 | بوابة الاعتماد الأولي (Bootstrap) — قاعدة الاستثناء التأسيسي | محسوم بتفويض (MEC-2.2) | decisions_d1_d2_d5_b2b.md | حق النقض محفوظ للمستخدم |
| D2 | المعيار الثلاثي للمخرجات (Web+Word+MD من مصدر واحد) | محسوم بتفويض — ساري | نفس الملف | |
| D3 | إعادة توطين Free Fire | مُدمج تنفيذيًا (MEC-2.1) | worklog | |
| D4 | مجموعتا الحجر (SheerID/الحسابات المشتركة) | مفتوح — بيد المستخدم | أدلة مرقّاة | |
| D5 | تدوير توكن Notion | محسوم قرارًا — **الفعل بيد المستخدم (لم يُنفّذ)** | C5/AF-5 | الرجوع للمستخدم |
| D6 | مهمة المراقبة الأسبوعية | مفتوح — بيد المستخدم | — | |
| D7 | تخويل الدفعة 2 | نُفذ (MEC-2.1) | أمر «اكمل» | |
| B2B | الترتيب الأولوي: ProdSeller → Turgame → FazerCards → Reloadly | معتمد تنفيذيًا | decisions file | |
| v4.2 | ترقية معمارية الكتالوج/الدفعات إلى APPROVED | نُفذت (MEC-3.0 — أول اعتماد تاريخي) | worklog MEC-3.0 | بعد تصريح المستخدم |
| MEC-7 | رأس مال S1/$100 · سوق اليمن أولًا · أسعار Dolaa | قرارات افتراضية قائمة | mec7 | قابلة للاستبدال |
| D-NEG | حملة تفاوض متدرجة W0→W3 (لا فتح شامل متزامن) | معتمد تشغيليًا — **كل البوابات بيد المستخدم** | مصفوفة_حملة_التفاوض.xlsx | حماية ورقة المعرفة السعرية 1,127 |
| D-v2 | تنفيذ ذاتي كامل + تحديث حي + مصالحة v1.5 | نُفذ (جولة v2.0) | توجيه MASTER AGENT PROMPT | |
| D-v2b | عدم إعادة سبر الأسطح ذات المفاتيح (شاهد R3) | قرار منهجي موثق | C11 | |
| **D-v3** | **تنفيذ جنائي 42-قسمًا + بنية 48 + توثيق طبقة ما قبل المشروع + تحديث حي ثالث** | نُفذ (هذه الجولة) | توجيه MASTER AGENT PROMPT الموسع | لا تغيير في أي حسم معرفي قائم |
