# MEC-21-B — Marketing, SEO & Growth Strategy Audit (FIRST audit of this domain)
Date: 2026-09-28 · Auditor: MEC-21-B (Team 09) · Mode: evidence-based, GET/HEAD-only on production, browser walkthrough on localhost for funnel (no production form submissions, no source modifications)

Environments: PROD https://mec-store-production.up.railway.app (14 direct GETs + 1 browser page-load) · LOCAL http://localhost:3000 (funnel walkthrough, zero checkout POSTs)
Evidence artifacts: `research/audit/mec21b-prod-hero.png`, `mec21b-local-hero.png`, `mec21b-local-sa-pricing.png`, `mec21b-local-checkout.png`, `mec21b-local-search-arabic-blank.png`, `mec21b-local-grid-restored.png` + VLM hero analysis

---

## 1. Executive Summary

The storefront's **UI Arabic is native-quality and the funnel is genuinely low-friction** (phone-only identity, 1-click checkout, 3 payment rails, price lock, cashback, legal pages linked) — but **the store is invisible and unmeasurable to growth channels**:

- **Sharing is broken for this market**: no `og:image`, no `og:url`, no `og:locale`, no `twitter:image` — WhatsApp/Telegram shares (the #1 discovery channel in KSA/YE) render as a bare text link. VERIFIED.
- **Zero analytics / zero conversion events** — no GA4/Pixel/Plausible/Umami tag anywhere (verified in HTML + network log: zero third-party requests on load). Nothing can be measured or optimized. VERIFIED.
- **No sitemap, no canonical, no JSON-LD, no og:image asset, no favicon.ico/apple-touch-icon/manifest** — and the entire 37-product catalog renders client-side only, so crawlers see a near-empty shell. VERIFIED.
- **Arabic search is broken on an Arabic-first store**: queries نتفلكس / كانفا / شات جي بي تي return a **silent blank grid** (25/37 product names are Latin-only, several in ALL-CAPS supplier jargon like "CAPCUT PRO 1600 CREDITS"). VERIFIED live.
- **Production shows internal/sandbox artifacts**: "🧪 وضع تجريبي" badge, "MEC STORE W1" label, and a public "🔬 الاستخبارات" header link into the internal supplier-intelligence panel (/intel, 48KB of sourcing/cost research) — trust leak + competitive-intelligence leak. VERIFIED.
- **No custom domain** (Railway subdomain `*.up.railway.app`) — blocks serious SEO, ad-platform trust, and WhatsApp Business verification. VERIFIED.

**Verdict:** Content/conversion foundation ≈ 6/10 (VLM 5-second test, corroborated by accessibility snapshot). Growth infrastructure ≈ 1/10. The store can take organic/hand-shared traffic today, but **any paid-traffic spend today would be unmeasurable, untrustworthy-looking, and partially wasted**. Sandbox-mode blockers (payment verification etc.) remain owned by Teams 03/08 (AUDIT-3 G1) — not restated here.

**SEO scorecard: 25 verified items → 10 PASS / 15 FAIL** (table below).

---

## 2. Technical SEO Audit Table (all evidence from live production fetches, 2026-09-28)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | Title tag (Arabic, keyword-relevant) | ✅ PASS | `<title>متجر MEC الرقمي — اشتراكات AI وبث MENA بأسعار موثقة</title>` — Arabic, ~58 chars, includes category keywords |
| 2 | Meta description | ✅ PASS | Present, Arabic, ~155 chars, mentions شاهد/أنغامي/USDT/Binance Pay (layout.tsx:22-23) |
| 3 | `lang="ar" dir="rtl"` | ✅ PASS | `<html lang="ar" dir="rtl">` on all pages |
| 4 | robots.txt exists | ✅ PASS (with gaps) | 200, 160B; allows Googlebot/Bingbot/Twitterbot/facebookexternalhit/* — **but no `Sitemap:` line and no `Disallow: /intel`** (noindex meta covers /intel; robots.txt is defense-in-depth) |
| 5 | /intel noindex | ✅ PASS | `<meta name="robots" content="noindex, nofollow"/>` verified in /intel HTML — internal panel correctly excluded |
| 6 | Legal pages (3) | ✅ PASS | /privacy /terms /refund all 200, ~25KB each, unique Arabic titles, linked in footer |
| 7 | og:title / og:description / og:site_name / og:type | ✅ PASS | All 4 present in head (layout.tsx:39-44) |
| 8 | twitter:card (basic) | ✅ PASS | `summary` + twitter:title + twitter:description present |
| 9 | Favicon (modern) | ✅ PASS (partial) | `/logo.svg` → 200 image/svg+xml, referenced via `icons` metadata; see #17 for legacy gaps |
| 10 | Heading structure h1 | ✅ PASS | Exactly 1 h1 (`متجر MEC الرقمي`, page.tsx:20) in server HTML **and** rendered DOM |
| 11 | Canonical URL | ❌ FAIL | No `<link rel="canonical">` on any page; `metadataBase` absent in layout.tsx (root cause) |
| 12 | og:image | ❌ FAIL | No og:image meta; `/og-image.png` → 404; no image asset in /public (only logo.svg + robots.txt) |
| 13 | og:url | ❌ FAIL | Absent (no metadataBase) |
| 14 | og:locale (ar_SA) | ❌ FAIL | Absent — WhatsApp/Facebook locale hints missing |
| 15 | twitter:image / large card | ❌ FAIL | Card is text-only `summary`, no image |
| 16 | sitemap.xml | ❌ FAIL | `/sitemap.xml` → 404; no sitemap.ts in src/app; no Sitemap line in robots.txt |
| 17 | favicon.ico + apple-touch-icon | ❌ FAIL | Both 404 (Safari/iOS home-screen bookmark + legacy crawlers get nothing; only SVG icon exists) |
| 18 | PWA manifest | ❌ FAIL | `/manifest.json` → 404; no manifest.ts |
| 19 | JSON-LD structured data | ❌ FAIL | Zero `application/ld+json` anywhere — no Organization, no Store, no Product/Offer/ItemList (37 sellable products, zero schema) |
| 20 | Heading hierarchy (h2/h3) | ❌ FAIL | Rendered DOM: h1=1, h2=0, h3=0, h4-h6=0 — flat structure; product names and section titles are styled `<div>`s, not headings |
| 21 | SSR product content | ❌ FAIL | Homepage server HTML contains zero products ("⏳ جارٍ تحميل المتجر…" placeholder); catalog is fetched client-side via /api/store/catalog — non-JS crawlers and link unfurlers see an empty store |
| 22 | Product detail pages | ❌ FAIL | No /products/[slug] routes (src/app: only /, /intel, /privacy, /refund, /terms + api) — no indexable/sharable per-product URLs, no long-tail SEO surface |
| 23 | Analytics tracking | ❌ FAIL | No gtag/GTM/Meta Pixel/Plausible/Umami/Clarity/Hotjar in HTML; network log on load = 100% same-origin requests; zero third-party beacons |
| 24 | Support/contact channel | ❌ FAIL | Zero matches for whatsapp/telegram/mailto/tel/support/تواصل/دعم in served HTML and source UI — no way for a customer to complain about a bad code |
| 25 | Arabic search matching | ❌ FAIL | Live-verified on storefront: queries «نتفلكس», «كانفا», «شات جي بي تي» → 0 results, **silent blank grid, no empty-state message**; search is `p.name` substring only (store.tsx:107-109) and 25/37 names are Latin-only |

**hreflang (ar/en):** N/A — single-locale Arabic site, no EN version exists to alternate with. Not counted as FAIL. If an EN version is added later, hreflang becomes required.

### Product naming evidence (catalog API, 37 products)
- 25/37 AI/SaaS names are Latin-only, several ALL-CAPS supplier feed jargon: `Adobe Express 12M`, `Avira Prime 3 Months`, `CAPCUT PRO 1600 CREDITS`, `Capcut Pro 7D FW`, `Autodesk Admin 3000 invite`, `Gemini Pro 18Months (link)`, `Duolingo 12M new method`. Zero Arabic names in the AI/SaaS family. No product `description` field exists in the catalog payload at all (fields: slug, name, family, sourceTier, officialUsd, chain, prices).
- 12/37 Turgame names are good consumer Arabic: `شاهد VIP مصر — 12 شهرًا`, `أنغامي بلس مصر — 1 شهر`, `Apple iTunes تركيا — 100 TL`.

---

## 3. Content & Positioning

**Hero / 5-second test (browser + VLM-verified, screenshot mec21b-prod-hero.png):**
- What is sold IS visible fast: 3 category labels (اشتراكات AI · بث MENA · بطاقات إقليمية), 37 product cards with prices, filter pills. VLM verdict 6/10: products clear, but the value prop leans on price/speed only; "USDT TRC-20 / Binance Pay" jargon appears above the fold before any trust/social proof; no "official/quality guarantee" badge explains why a $119.88 Adobe Express plan costs 3 ر.س (a skepticism trigger without social proof).
- Trust badges present in header: ⚡ تسليم ≤ 3 دقائق · 🔒 سعر مقفل عند الطلب · 💸 كاش باك 1% — clear, concrete, Arabic-native. GOOD.
- Trust strip: no-account phone identity, refund+apology $1 promise. GOOD.
- Arabic UI copy is human-quality, market-appropriate (Saudi e-commerce register) — NOT machine-translated. GOOD.

**Verified positioning problems:**
1. **Sandbox artifacts on production** (VERIFIED GAP): "🧪 وضع تجريبي" badge and "MEC STORE W1" internal label render on the live store header. Any paying-candidate visitor sees a test-store signal.
2. **"🔬 الاستخبارات" public header link** (VERIFIED GAP, page.tsx:34-37): every visitor is one click from the internal supplier-intelligence panel (/intel — public 200, 48KB: supplier costs, margin research, sourcing decisions D1-D7, "400+ SKU Program"). Trust leak for customers, competitive-intelligence leak for rivals. (Security-owned residual R-INT-1; growth impact documented here.)
3. **Product naming not consumer-Arabic** (VERIFIED GAP): the flagship family (AI/SaaS, 25 products incl. ChatGPT Plus, Canva Pro, CapCut) uses supplier feed names in Latin/ALL-CAPS with insider jargon (FW, invite, link, new method). Not searchable in Arabic, not trust-inspiring, hurts both conversion and SEO.
4. **Search dead-ends** (VERIFIED GAP): Arabic brand queries → silent blank grid; also no empty-state message at all (matches AGENT-1 G16, re-verified live).
5. **No product descriptions** (VERIFIED GAP): catalog schema/payload has no description field — nothing to rank for, nothing to reassure with.

**Pricing display (VERIFIED GOOD with gaps):** geo-pricing works and is visible — after entering +966 phone, checkout shows «🇸🇦 السعودية — ر.س … 3 ر.س ≈ $ 0.80» with price-lock line (screenshot mec21b-local-sa-pricing.png / mec21b-local-checkout.png). Footer explains SA=SAR / others=USD. GAPS: (a) no VAT display/mention anywhere (KSA 15% VAT B2C display expectation — compliance-relevant), (b) prices far below official (officialUsd badges «−N% رسمي» exist and help, but without reviews/social proof the gap reads as "scam?" to newcomers.

**Checkout funnel (walked end-to-end on localhost, zero POSTs):**
- Landing → enter phone (1 field, no password/email) → click buy → checkout panel with locked price + 3 rails → pay. **Funnel length is excellent** — guest checkout by design, phone-only identity, no registration burden. This is a genuine conversion asset.
- Friction points (VERIFIED): Binance Pay rail's own label admits «يتطلب حساب تاجر عند التفعيل الحي» (not live); TRC-20 rail requires leaving the site, sending crypto, waiting ~1 block, returning to confirm (acceptable for crypto-native Yemen buyers, high friction for KSA mainstream); wallet rail requires prior deposit; out-of-stock CTA is a disabled dead-end («نفد — فعّل تنبيه التوفير», cannot join waitlist from catalog — AGENT-1 G12, still visible in snapshot).

**Footer (VERIFIED):** 3 legal links present (الشروط والأحكام / سياسة الخصوصية / الاستبدال والاسترداد) + payment/pricing line. MISSING: support contact, business identity/CR number, social links, Arabic "about" line.

---

## 4. Trust & Conversion

| Signal | Status | Evidence |
|---|---|---|
| Delivery-time promise | ✅ present | «⚡ تسليم ≤ 3 دقائق» header + on every buy button |
| Price lock | ✅ present | «🔒 سعر مقفل عند الطلب» + checkout reiteration |
| Cashback | ✅ present | «💸 كاش باك 1%» + applied in ledger (AUDIT-3/10 verified math) |
| Refund guarantee | ✅ present | Trust strip + legal /refund page |
| Legal pages | ✅ present | 3 pages, Arabic, footer-linked |
| Consistent Arabic RTL | ✅ present | Native-quality copy; dir=rtl correct |
| Social proof (reviews/ratings/customer count) | ❌ missing | Zero review/rating/testimonial elements in UI or API |
| Delivered-orders counter | ❌ missing | Orders data exists in DB (47 orders baseline) but never surfaced |
| Support channel (WhatsApp/Telegram/email) | ❌ missing | Zero contact affordances anywhere |
| Business identity / CR number | ❌ missing | No company info on storefront |
| Sandbox-mode indicators | ❌ leaking | «🧪 وضع تجريبي» + «MEC STORE W1» visible in production header |
| VAT display (KSA) | ❌ missing | No ضريبة/VAT mention on any page or legal doc (rg-verified) |

---

## 5. Growth Channel Readiness

**Analytics & measurement (VERIFIED GAP — blocker):** No analytics of any kind (HTML scan + live network log both empty of third-party calls). No funnel events (view_product / begin_checkout / purchase). Retargeting, A/B testing, LTV/COGS math — all impossible today.

**Shareability (VERIFIED GAP — blocker for the primary channel):** WhatsApp/Telegram are the dominant product-discovery channels in KSA/YE for digital goods. Current share = bare URL + title text (no og:image, no og:locale, no twitter:image, no product-level URLs to share). No in-app share buttons (no navigator.share / wa.me / t.me anywhere in code).

**Market-fit assets that ARE real:** crypto-first rails (USDT TRC-20) genuinely fit Yemen (weak card rails, USDT-common) — positioning is coherent, not a gimmick; Arabic-first RTL native UX; phone-number identity matches local behavior; 1% cashback + apology credit are differentiators worth advertising.

**What blocks paid traffic today (each verified):**
1. STORE_MODE=sandbox with visible «وضع تجريبي» badge → zero buyer trust; real-payment confirm path unverified (Team 03 owns).
2. No analytics → unmeasurable spend.
3. No og:image → ad creatives and organic shares look bare.
4. Railway subdomain → platform-quality score low for ads/SEO; WhatsApp Business verification impossible.
5. No support channel → chargeback/complaint risk on any campaign.
6. No custom domain / no product pages → Google Shopping & SEO long-tail impossible.

---

## 6. Prioritized Growth Backlog (each item maps to a verified gap above)

### P1 — before spending a single riyal on traffic
| # | Action | Verified gap it closes | Expected impact |
|---|---|---|---|
| P1-1 | **Custom domain** (e.g. mec-store.sa / mec.sa) pointed at Railway | Railway subdomain (verified) | Unlocks SEO equity, ad-platform trust, WhatsApp Business; foundational for everything below |
| P1-2 | **Complete head metadata**: `metadataBase`, canonical, og:url, og:locale=ar_SA, twitter:image, **og:image 1200×630** (Arabic-branded, shows product families + «تسليم ≤ 3 دقائق») | Scorecard #11-15 | WhatsApp/Telegram shares become visual ads; CTR on shares/ads up materially (industry-consistent, not invented) |
| P1-3 | **Install analytics + funnel events** (GA4 or privacy-light Plausible/Umami; events: view_product, begin_checkout, select_rail, purchase, deposit) | Scorecard #23 | Everything becomes measurable; retargeting audiences become possible |
| P1-4 | **Arabic consumer naming + aliases for all 37 products** (e.g. «ChatGPT Plus — شات جي بي تي بلس 1 شهر») + description field (1-2 Arabic lines each) + search matches aliases + empty-state «لا نتائج للبحث» | Scorecard #25, §3.3/3.5 | Arabic search converts from 0% to functional; product cards stop looking like a supplier feed |
| P1-5 | **Strip internal artifacts from production**: remove «وضع تجريبي»/«MEC STORE W1» from customer view, unlink /intel from header (or token-gate the page) | §3.1-3.2 | Removes active trust destruction on every visit |
| P1-6 | **Support channel**: WhatsApp or Telegram link in header/footer + order view («تواصل معنا») | Scorecard #24 | Standard trust requirement for KSA/YE digital goods; reduces abandoned carts at first purchase |

### P2 — organic growth infrastructure
| # | Action | Verified gap | Expected impact |
|---|---|---|---|
| P2-1 | **sitemap.ts** (/, /terms, /privacy, /refund) + `Sitemap:` line in robots.txt + `Disallow: /intel` | #16, #4 | Crawl efficiency; correct page set in index |
| P2-2 | **favicon.ico + apple-touch-icon + manifest** (icons already brandable from ⚡ logo) | #17, #18 | Browser tab/iOS home-screen branding; PWA-lite install |
| P2-3 | **JSON-LD**: Organization/WebSite + ItemList of catalog (and later Product/Offer per PDP) | #19 | Rich results eligibility; merchant understanding |
| P2-4 | **Product detail pages /p/[slug]** — SSR, unique title/desc/canonical/OG per product, price + family + description from P1-4 | #22, #21 | Long-tail Arabic SEO («شراء اشتراك شاهد VIP», «ChatGPT Plus بالريال»); per-product shareable links; prerequisite for Google Shopping |
| P2-5 | **SSR initial catalog** (server-render first N products / embedded JSON) | #21 | Non-JS crawlers see inventory; snapshot for unfurlers |
| P2-6 | **Social proof**: delivered-orders counter (data exists), product ratings, testimonials; explain the «−N% رسمي» price gap openly | §4 | Converts skeptics; addresses "too good to be true" reaction |
| P2-7 | **VAT & business identity**: decide VAT display for KSA (15%), add CR/owner info in footer | §4 | Regulatory hygiene before scale |
| P2-8 | **Enable waitlist from catalog** for OOS products (currently dead disabled button) | §3 funnel | Recovers demand signal instead of discarding it |

### P3 — compounding growth
| # | Action | Verified gap | Impact |
|---|---|---|---|
| P3-1 | Share buttons (navigator.share + wa.me) on product/order success | §5 | Turns delivered orders into word-of-mouth (existing 1% cashback is a hook for referral) |
| P3-2 | Referral/coupon program on top of existing cashback ledger | §5 | Cheap CAC channel; infrastructure (WalletTx) already exists |
| P3-3 | EN-language variant + hreflang for expat segment | N/A→future | Optional market expansion |
| P3-4 | Google Merchant Center feed (requires P2-4) | #22 | Shopping ads for gift-card queries |
| P3-5 | Landing pages per category/family (AI subscriptions, streaming, gift cards) with FAQ | #21/22 | Converts SEO traffic better than the single shell page |

---

## 7. Quick Wins This Week (≤5, no new infrastructure)

1. **og:image + og:locale + og:url + canonical + twitter:image + metadataBase** — one commit: layout.tsx metadata + one 1200×630 PNG in /public. (Closes 5 scorecard fails.)
2. **app/sitemap.ts + robots.txt Sitemap line + Disallow: /intel + favicon.ico/apple-touch-icon exports** — static files + 6-line file. (Closes 3 fails.)
3. **Arabic aliases for the top-10 products + search alias matching + «لا نتائج» empty state** — store.tsx + catalog name/alias data; no schema change needed to start. (Closes the worst conversion bug.)
4. **Hide «وضع تجريبي», «MEC STORE W1», and the «🔬 الاستخبارات» link from non-admin production view** — conditional render, no backend change.
5. **Add WhatsApp/Telegram support link in footer + order view** — pure static link (t.me/… or wa.me/…), biggest trust-per-line-of-code in this market.

*(Bonus, near-zero effort: delivered-orders counter «✅ N طلبًا مُسلّمًا» in the trust strip — real number from orders table, not invented social proof.)*

---

## 8. Method & Limitations

- Production checks: curl GETs to /, /robots.txt, /sitemap.xml, /manifest.json, /favicon.ico, /apple-touch-icon.png, /og-image.png, /sitemap_index.xml, /logo.svg, /intel, /privacy, /terms, /refund, /api/store/catalog + one headless browser page-load (network-request log inspected). No form submissions, no POSTs, GET/HEAD only.
- Funnel walkthrough on localhost:3000 (phone +96651110022 registered — read-only GET /api/wallet; zero checkout/deposit POSTs; no DB writes beyond a wallet read. localStorage test phone only).
- VLM used for 5-second hero clarity test (mec21b-prod-hero.png); VLM details (e.g., "32 seconds") overruled by direct DOM evidence wherever they conflicted.
- Search-behavior verification: React-controlled inputs via agent-browser fill; one eval-vs-DOM desync observed during testing (page reloaded to confirm clean state; final counts from fresh reload).
- No source files modified. Only writes: this findings file + worklog append + 6 evidence screenshots.
- Traffic/conversion metrics deliberately not estimated — no analytics exist to source them from (that absence is itself finding #23).
