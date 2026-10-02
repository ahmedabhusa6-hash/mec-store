# Adaptive Supplier Intelligence — Batch 1 Dataset

> **Engine**: Adaptive Supplier Intelligence Research Engine — v4.1 Candidate
> **Run ID**: SI-BATCH1-20260926 · **Prompt Version**: Adaptive Supplier Intelligence Research Engine — v4.1 Candidate
> **Primary Objective**: PRICE INTELLIGENCE (supplier discovery = mechanism; upstream/legitimacy = supporting dimensions)
> **Program Scope**: 400+ SKU digital products/services catalog — this file documents **Batch 1** (15 SKUs executed, remaining catalog queued)
> **Generated**: 2026-09-26 21:21 UTC

**Governing price formulation** — used exclusively, never "cheapest in the world":

> *"the lowest price discovered and verified within the research scope, at the time of checking, under the specified SKU and offer conditions."*

---

## 1. Run Metadata

| Field | Value |
|---|---|
| Run ID | SI-BATCH1-20260926 |
| Started | 2026-09-26T21:02:52Z |
| Complexity Class | C4 (C4) |
| Actions Executed | 76 / 96 (64 success, 12 failed) |
| Reserve | 24 untouched |
| Transaction Verification | **Not Performed** (all offers — listing-level evidence only) |
| Output Contract | Web Page + Markdown (this file) — semantically identical |

**Core invariants enforced throughout**: Discovered ≠ Verified ≠ Supplier ≠ Upstream Source ≠ Primary Source ≠ Lowest Verified Price · Advertised Price ≠ Transaction Price · Availability ≠ Purchase · Product availability ≠ Resale Authorization · Technical similarity ≠ Business Relationship · Search failure ≠ Non-Existence.

## 2. Scope Lock

**Locked (immutable for the run):**
- Primary objective = Price Intelligence (supplier discovery = mechanism; upstream/legitimacy = supporting dimensions)
- 400+ SKU catalog program scope with internal batching
- Global supplier discovery, no geographic exclusion
- Region-aware SKU matching
- No price ceiling; no fabricated benchmarks
- Multi-scenario volume evaluation (tiers kept separate)
- Governing price formulation (never 'cheapest in the world')

**Proposed Scope Expansions (NOT executed — require user authorization):**

- **Free Fire SKU denomination realignment (520 → market-observable 2200/2420 packs)** — 4 retrieval attempts failed on 520-specific pricing; sellers list different denominations → `NOT executed — requires user authorization`
- **AI-subscription gray-market deep-dive (Etsy Gemini listings, shared-account markets)** — High-value discovery branch surfaced by A002/A023 → `NOT executed — out of Batch 1 budget`

## 3. SKU Records & Price Intelligence (Batch 1)

### SKU-AI-001 — OpenAI ChatGPT Plus

**Family**: AI/SaaS

**SKU Identity** (comparability basis):

```json
{
  "brand": "OpenAI",
  "product": "ChatGPT Plus",
  "plan": "Plus monthly",
  "seats": "1",
  "billing": "monthly",
  "account_type": "individual",
  "region": "Global (service)",
  "locked": true
}
```

**Official Anchor**: 20 USD / month 
- Evidence Level: `Secondary Reported` · Freshness: `Current`
- Evidence: A001 community.openai.com + A023 smartbuy.alibaba.com (Jan 2026: $20/mo monthly, $200/yr annual)

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| OpenAI (official) | 20 | month | Exact Match | Secondary Reported | Current | First-party service terms | N/A | A001/A023 |
| OpenAI (official annual) | 200 | year (=$16.67/mo) | Exact Match (annual billing) | Secondary Reported | Current | First-party | N/A | A023 |
| Gray-market shared/discount accounts | — | — | Non-Comparable (account-sharing ≠ subscription) | Lead | Unknown | Unknown | Suspected unauthorized (community reports: significant discounts typically unofficial — A023 facebook.com) | A023 |

**Price Intelligence**:

- **Lowest verified offer**: $20.00/month official (Secondary Reported)
- **Lowest comparable effective acquisition cost**: $16.67/month equivalent via official annual billing $200/yr (verified legitimate channel)
- **Cheapest advertised marketplace**: None verified — no legitimate below-official offer found
- **Cheapest with documented guarantee**: Official $200/yr annual (first-party terms)
- **Cheapest without documented guarantee**: No verified commercial offer
- **Effective acquisition cost notes**: No mandatory fees beyond subscription price evidenced; taxes Unknown Component: VAT/sales tax not captured

**Coverage**:

- product_first: Verified Findings
- price_first: Searched — No Useful Result (legitimate)
- seller_first: Signal only (rate-limited)
- counter_evidence: Verified Findings

---

### SKU-AI-002 — Google Gemini (Google One AI Pro)

**Family**: AI/SaaS

**SKU Identity** (comparability basis):

```json
{
  "brand": "Google",
  "product": "Gemini (Google One AI Pro)",
  "plan": "AI Pro monthly",
  "seats": "1",
  "billing": "monthly or annual",
  "account_type": "individual",
  "region": "Global (service)",
  "locked": true
}
```

**Official Anchor**: 19.99 USD / month 
- Evidence Level: `Secondary Reported (×2 consistent)` · Freshness: `Current (Aug 2026)`
- Evidence: A002 tech.yahoo.com (Aug 2026) + savingadvice.com ($19.99/mo; annual $199.99/yr)

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| Google (official) | 19.99 | month | Exact Match | Secondary Reported | Current | First-party | N/A | A002 |
| Google (official annual) | 199.99 | year (=$16.67/mo) | Exact Match (annual) | Secondary Reported | Current | First-party | N/A | A002 |
| Etsy seller — 'Gemini AI 18 Month Pro Plan 5TB' | — | — | Possible Match–Review (plan identity unclear, price not captured) | Lead | Unknown | Unknown | Suspected unauthorized — no Google reseller program evidenced | A002 etsy.com |

**Price Intelligence**:

- **Lowest verified offer**: $19.99/month official (Secondary Reported)
- **Lowest comparable effective acquisition cost**: $16.67/month equivalent via annual $199.99/yr
- **Cheapest advertised marketplace**: None verified (Etsy lead unpriced)
- **Cheapest with documented guarantee**: Official annual plan
- **Cheapest without documented guarantee**: None verified
- **Effective acquisition cost notes**: Taxes Unknown Component

**Coverage**:

- product_first: Verified Findings
- price_first: Lead (Etsy)
- seller_first: Not Searched (budget)
- counter_evidence: Not Searched — Batch 2

---

### SKU-SUB-001 — Spotify AB Spotify Premium Individual

**Family**: Digital Subscriptions

**SKU Identity** (comparability basis):

```json
{
  "brand": "Spotify AB",
  "product": "Spotify Premium Individual",
  "plan": "Individual",
  "duration": "1 month (and 12-month comparison)",
  "account_type": "individual",
  "region": "US storefront",
  "locked": true
}
```

**Official Anchor**: 12.99 USD / month 
- Evidence Level: `First-Party Reported (retrieved directly)` · Freshness: `Current`
- Evidence: A072 spotify.com — '$0 for 1 month trial, then $12.99 per month' (US); corroborated ×2 (checkthat.ai Aug 2026, freeyourmusic 2026)

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| Spotify (official) | 12.99 | month | Exact Match | First-Party Reported | Current | First-party | N/A | A072 |
| Eneba (via ozbargain deal post) | 20.86 | 12 months (=$1.74/mo) | Possible Match–Review (region/method ambiguous) | Lead (community deal post, Feb 2025) | Stale | Unknown | Unclear — 87% below official annual; likely region-arbitrage or gray method | A024 ozbargain.com.au |

**Price Intelligence**:

- **Lowest verified offer**: $12.99/month official (First-Party, directly retrieved)
- **Lowest comparable effective acquisition cost**: $12.99/month official (12-month reseller offer NOT comparable — unverified identity/method)
- **Cheapest advertised marketplace**: $20.86/12mo Eneba-signal (Stale + Possible Match–Review — NOT ranked as verified)
- **Cheapest with documented guarantee**: Official $12.99/mo
- **Cheapest without documented guarantee**: None verified this run
- **Effective acquisition cost notes**: Trial offer ($0 first month) is conditional (new-subscriber-only) — not a generalizable price

**Coverage**:

- product_first: Verified Findings (after 3 failed constructions + recovery)
- price_first: Lead
- counter_evidence: Region-arbitrage risk documented
- Notes: Failure Recovery case: A003→A014→A057 failed, A072 succeeded

---

### SKU-SUB-002 — Netflix Netflix Standard (ad-free)

**Family**: Digital Subscriptions

**SKU Identity** (comparability basis):

```json
{
  "brand": "Netflix",
  "product": "Netflix Standard (ad-free)",
  "plan": "Standard",
  "duration": "1 month",
  "region": "US",
  "locked": true
}
```

**Official Anchor**: 19.99 USD / month 
- Evidence Level: `First-Party Reported (retrieved directly)` · Freshness: `Current`
- Evidence: A004 help.netflix.com — Standard with ads $8.99, Standard $19.99, Premium $26.99 (US)

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| Netflix (official) | 19.99 | month (Standard) | Exact Match | First-Party Reported | Current | First-party | N/A | A004 |
| Netflix (official, with ads) | 8.99 | month (Standard with ads) | Strong Comparable (different plan tier — NOT same SKU) | First-Party Reported | Current | First-party | N/A | A004 |

**Price Intelligence**:

- **Lowest verified offer**: $19.99/month for Standard SKU (the $8.99 tier is a DIFFERENT SKU — with ads)
- **Cheapest advertised marketplace**: None found — Netflix gift-card resale channel Retrieval-Limited (A068 rate-limited)
- **Cheapest with documented guarantee**: Official
- **Effective acquisition cost notes**: Plan-tier identity is decisive for comparability (ads vs ad-free)

**Coverage**:

- product_first: Verified Findings
- price_first: Retrieval-Limited
- Notes: Reseller channel unreachable this run

---

### SKU-SUB-003 — NordVPN NordVPN subscription

**Family**: Digital Subscriptions

**SKU Identity** (comparability basis):

```json
{
  "brand": "NordVPN",
  "product": "NordVPN subscription",
  "plan": "Complete (1 year, first term)",
  "duration": "12 months",
  "region": "Global",
  "locked": "Partially — tier ambiguity flagged (Basic/Plus/Complete pricing differs materially)"
}
```

**Official Anchor**: 121.23 USD / first 12 months (Complete plan) 
- Evidence Level: `First-Party Reported (retrieved directly)` · Freshness: `Current`
- Evidence: A005 nordvpn.com — Complete $121.23 first 12mo (75% off $219.48), renews $219.48/yr; security.org: Basic 1yr ≈ $5.49/mo

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| NordVPN (official) | 121.23 | 12 months (Complete) | Exact Match | First-Party Reported | Current | 30-day money-back (security.org) | N/A | A005 |
| K4G (via allkeyshop) | 4.9 | subscription key (plan tier unclear) | Possible Match–Review (tier/duration not confirmed from snippet) | Secondary Reported (comparator) | Current | Unknown | Restricted — NordVPN official statement: no G2A sellers authorized to resell (publisher counter-evidence) | A031 |

**Price Intelligence**:

- **Lowest verified offer**: $121.23/12mo official Complete (First-Party)
- **Cheapest advertised marketplace**: $4.90 at K4G (Advertised via comparator — tier unclear, resale unauthorized per publisher)
- **Cheapest with documented guarantee**: Official (money-back documented)
- **Cheapest without documented guarantee**: $4.90 K4G — held in review state (authorization + identity unconfirmed)
- **Effective acquisition cost notes**: Official renewal at $219.48/yr materially changes 2nd-year cost; K4G key renewal terms Unknown

**Coverage**:

- product_first: Verified Findings
- price_first: Verified Findings
- counter_evidence: Verified Findings (publisher-documented resale restriction)

---

### SKU-GC-001 — Valve/Steam Steam Wallet Gift Card

**Family**: Gift Cards

**SKU Identity** (comparability basis):

```json
{
  "brand": "Valve/Steam",
  "product": "Steam Wallet Gift Card",
  "denomination": "$20 USD",
  "currency": "USD",
  "redemption_region": "US (USD wallet)",
  "locked": true
}
```

**Official Anchor**: 20 USD / card (face value) 
- Evidence Level: `First-Party Retail` · Freshness: `Current`
- Evidence: A006 store.steampowered.com redemption + GameStop $20 retail listing

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| Official retail (GameStop/Amazon/Best Buy) | 20 | $20 card | Exact Match | First-Party Retail | Current | Face-value instrument | N/A | A006 |
| G2A (via gg.deals) | 14.1 | $13 card (US) | Strong Comparable (different denomination, same region) — unit-rate +8.5% ABOVE face | Secondary Reported (aggregator) | Current | Marketplace protection | Unclear | A021 |
| Kinguin | 18.85 | ₴800 UAH card (Ukraine wallet) | Non-Comparable (different currency region — UA accounts only) | First-Party Reported (listing) | Current | Marketplace protection | Unclear | A021 |
| Eneba | — | 10 USD EL SALVADOR region card | Non-Comparable (different region) | First-Party (listing existence) | Current | Unknown | Unknown | A020 |
| Z2U | — | $5-$100 denominations | Strong Comparable (pricing not captured) | Lead | Current | Unknown | Unknown | A049 |

**Price Intelligence**:

- **Lowest verified offer**: $20.00 face value at official retail
- **Cheapest advertised marketplace**: None below face for US-region cards — US wallet codes trade at PREMIUM on gray market (structural finding)
- **Key insight**: US-region Steam codes: gray-market premium +8.5% (region-pricing arbitrage demand). Discounts only exist on non-USD region cards (Non-Comparable SKUs)
- **Cheapest with documented guarantee**: $20 official retail
- **Effective acquisition cost notes**: Gray-market US cards cost MORE than face — no arbitrage value verified

**Coverage**:

- product_first: Verified Findings
- marketplace_first: Verified Findings
- language_ru: Verified Findings (Plati/GGSel context)
- Notes: RU-market Steam top-up operates via codes due to payment restrictions (context)

---

### SKU-GC-002 — Apple App Store & iTunes Gift Card

**Family**: Gift Cards

**SKU Identity** (comparability basis):

```json
{
  "brand": "Apple",
  "product": "App Store & iTunes Gift Card",
  "denomination": "$25 USD",
  "currency": "USD",
  "redemption_region": "US Apple ID",
  "locked": true
}
```

**Official Anchor**: 25 USD / card (face value) 
- Evidence Level: `First-Party Retail` · Freshness: `Current`
- Evidence: A015 amazon.com + bestbuy.com listings at face

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| Amazon / Best Buy (official retail) | 25 | $25 card | Exact Match | First-Party Retail | Current | Face-value instrument | N/A | A015 |
| snoonu (Qatar) | — | $25 US card | Strong Comparable (price not captured) | Lead (listing) | Current | Unknown | Unknown | A015 |
| yallatoys (Qatar) | — | $25 US card | Strong Comparable (price not captured) | Lead | Current | Unknown | Unknown | A051 |
| gml-store | 250 | $250 card at 937.50 SAR (EXACT face at 3.75 SAR/USD) | Strong Comparable (different denomination, same region — unit rate = face) | First-Party Reported | Current | Unknown | Unclear | A051 |
| LikeCard (Bahrain) | — | Apple cards | Strong Comparable (price not captured) | Lead | Current | Unknown | Unknown | A051 |
| vexacard | — | $30 US card | Strong Comparable (price not captured) | Lead | Current | Unknown | Unknown | A036 |
| DIFMARK (via smartcdkeys, EA App card as pattern reference) | 21.92 | EA App $25 card (different brand) | Non-Comparable (different brand) — pattern: 12% below face exists in keyshop segment | Secondary Reported (comparator) | Current | Unknown | Unknown | A022 |

**Price Intelligence**:

- **Lowest verified offer**: $25.00 face value
- **Cheapest advertised marketplace**: None below face verified for Apple $25 US; MENA stores sell at ≈face (gml-store exact-face evidence)
- **Cheapest with documented guarantee**: $25 official retail
- **Effective acquisition cost notes**: Counter-evidence principle (bittopup editorial): 30-50% below face = fraud economics for gift cards

**Coverage**:

- product_first: Verified Findings
- language_ar: Verified Findings (5 MENA sellers)
- counter_evidence: Verified Findings

---

### SKU-GC-003 — Google Google Play Gift Card

**Family**: Gift Cards

**SKU Identity** (comparability basis):

```json
{
  "brand": "Google",
  "product": "Google Play Gift Card",
  "denomination": "$25 USD",
  "redemption_region": "US",
  "locked": true
}
```

**Official Anchor**: **Unknown — Retrieval-Limited** 
- Evidence Level: `Unknown — Retrieval-Limited` · Freshness: `Unknown`
- Evidence: 4 query attempts failed to capture direct listing (A008, A016, A055, A073). Face-value convention NOT committed as fact without evidence.

**Offers**: None captured (honest empty state — see coverage).

**Price Intelligence**:

- **Lowest verified offer**: Unknown — Retrieval-Limited
- **Notes**: Anchor remains open; Batch 2 target. No offers ranked — SKU identity locked but price evidence empty (honest empty state)

**Coverage**:

- product_first: Retrieval-Limited (×4)
- price_first: Not Searched (anchor missing)

---

### SKU-TOP-001 — Tencent/PUBG Mobile PUBG Mobile UC

**Family**: Game Top-up

**SKU Identity** (comparability basis):

```json
{
  "brand": "Tencent/PUBG Mobile",
  "product": "PUBG Mobile UC",
  "denomination": "660 UC (600 + 60 bonus)",
  "delivery": "voucher code or direct top-up",
  "region": "Global (server-dependent)",
  "locked": true
}
```

**Official Anchor**: 9.99 USD / 660 UC pack 
- Evidence Level: `Secondary Reported (official pack pricing)` · Freshness: `Current`
- Evidence: A017 games2usd.com (600+60 UC = $9.99 official pack); A050 cardsouq lists original price $9.99; Eneba listing structure confirms 600+60 denominations

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| Official in-game / Midasbuy | 9.99 | 660 UC | Exact Match | Secondary Reported | Current | Official channel | N/A | A017 |
| Midasbuy (official, advertised 10% off) | 8.99 | 660 UC effective | Exact Match | Advertised | Current | Official after-sales support stated | N/A (official) | A059 |
| bittopup | 8.71 | 660 UC | Strong Comparable | First-Party Reported (listing) | Current (2026) | Unknown | Unclear | A050 |
| Turgame | 10 | 660 UC (454.90 TRY) | Strong Comparable | First-Party Reported (directly observed) | Current — OFFER SOLD OUT at check time | Unknown | Unclear | A037 |
| itemku | 10.07 | 660 UC (from) | Strong Comparable | First-Party Reported | Current (Sep 2026) | Marketplace guarantee advertised | Unclear | A017 |
| cardsouq | 4.99 | 660 UC (600+60) | Possible Match–Review (delivery method unverified; 50% below official) | First-Party Reported (listing) | Current (2026) | Unknown | Unclear | A050 |
| opensooq individuals (JO) | 4.93 | 660 UC (3.50 JOD) | Possible Match–Review | Lead (classifieds) | Current | None (individual) | Unknown | A050 |
| buffbuff | — | 'up to 55% OFF' claimed | Possible Match–Review (claim unverified) | Advertised (self-claimed) | Current | Unknown | Authorization CLAIMED, not verified | A059 |

**Price Intelligence**:

- **Lowest verified offer**: $8.99 effective via Midasbuy official 10% discount (Advertised — official channel) OR $8.71 bittopup (First-Party listing) — scoped: lowest directly-listed commercial price = $8.71 (bittopup), within plausible promo band
- **Cheapest advertised**: $4.99 cardsouq — HELD IN REVIEW (50% below official; bittopup's own fraud-economics statement flags 30-50% band as fraudulent for gift cards; UC top-up delivery terms unverified)
- **Cheapest negotiated individual**: ~$4.93 opensooq (non-generalizable, no guarantee)
- **Cheapest with documented guarantee**: Midasbuy official ~$8.99 (official after-sales)
- **Effective acquisition cost notes**: Payment-method fees Unknown Component; TRY-priced offers (Turgame 454.90 TRY) carry FX conversion Unknown Component

**Coverage**:

- product_first: Verified Findings
- price_first: Verified Findings (7 offers)
- language_ar: Verified Findings
- counter_evidence: Verified Findings (fraud-economics + authorization claims)
- Notes: Richest SKU this batch — real price dispersion documented

---

### SKU-TOP-002 — Garena Free Fire Diamonds

**Family**: Game Top-up

**SKU Identity** (comparability basis):

```json
{
  "brand": "Garena",
  "product": "Free Fire Diamonds",
  "denomination": "520 diamonds",
  "delivery": "direct top-up",
  "region": "Global/MENA",
  "locked": true
}
```

**Official Anchor**: **Unknown — Retrieval-Limited** 
- Evidence Level: `Unknown — Retrieval-Limited (×4 attempts: A010, A018, A074)` · Freshness: `Unknown`
- Evidence: Garena official top-up centers confirmed to exist (A054: shop.garena.sg, store.garena.com) but 520-diamond price not captured

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| gameseal | — | 2200 diamonds GLOBAL (different denomination) | Non-Comparable | Lead (listing) | Current | Unknown | Unknown | A054 |
| karteet | — | 2420 diamonds MENA (different denomination) | Non-Comparable | Lead (listing) | Current | Unknown | Unknown | A036 |

**Price Intelligence**:

- **Lowest verified offer**: Unknown — anchor Retrieval-Limited
- **Notes**: Denomination mismatch is the recurring failure mode: sellers list 2200/2420 packs, not 520. SKU identity correct; market denominations differ. Batch 2: query 520-specific or re-scope SKU to observed denominations (requires user authorization per Scope Lock).

**Coverage**:

- product_first: Retrieval-Limited
- price_first: No Comparable Found
- Notes: Proposed adjustment (NOT executed): align SKU denomination to market-observable packs

---

### SKU-SW-001 — Microsoft Windows 11 Pro

**Family**: Software/Licenses

**SKU Identity** (comparability basis):

```json
{
  "brand": "Microsoft",
  "product": "Windows 11 Pro",
  "license": "retail digital license (official anchor); gray-market OEM keys offered by keyshops",
  "duration": "perpetual",
  "activation": "digital key",
  "region": "Global",
  "locked": true
}
```

**Official Anchor**: 199.99 USD / license 
- Evidence Level: `First-Party Reported + Secondary` · Freshness: `Current`
- Evidence: A056 learn.microsoft.com (user-confirmed $199.99) + techradar.com; digitalmaze regular price $199.99 corroborates

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| Microsoft (official) | 199.99 | license | Exact Match | First-Party Reported | Current | First-party | N/A | A056 |
| digitalmaze | 74.99 | license (sale) | Strong Comparable (license type not fully specified) | First-Party Reported | Current | Unknown | Unclear | A056 |
| Kinguin/G2A/CDKeys (typical range) | 25 | OEM key (range $20-30) | Possible Match–Review (OEM vs retail license) | Secondary Reported (guide) | Current | Marketplace protection | Legally gray — 'a key is not a license' (Microsoft position via LTT forum) | A026 |
| Keywrld (via allkeyshop) | 1.1 | €1.03 Windows 11 Pro key | Possible Match–Review (extreme outlier, conditions unknown) | Secondary Reported (comparator) | Current | Unknown | Unclear | A027 |
| techspot deals (pattern reference) | 29.99 | Windows 11 Pro license deal | Strong Comparable (deal site, 2023 — Stale) | Secondary Reported | Stale (Jun 2023) | Unknown | Unknown | A011 |

**Price Intelligence**:

- **Lowest verified offer**: $199.99 official (verified)
- **Cheapest advertised marketplace**: €1.03 Keywrld (comparator, conditions unknown — review state); mainstream gray range $20-30 (steemit guide)
- **Cheapest with documented guarantee**: Official $199.99
- **Cheapest without documented guarantee**: Gray-market keys $20-30 range (license-validity risk documented)
- **Effective acquisition cost notes**: Gray keys: activation-success risk + no Microsoft support = hidden cost dimension (risk ≠ price, kept separate)

**Coverage**:

- product_first: Verified Findings (after 2 failed constructions)
- price_first: Verified Findings
- counter_evidence: Verified Findings (key≠license legal position)

---

### SKU-KEY-001 — Mojang/Microsoft Minecraft: Java & Bedrock Edition

**Family**: Game Keys

**SKU Identity** (comparability basis):

```json
{
  "brand": "Mojang/Microsoft",
  "product": "Minecraft: Java & Bedrock Edition",
  "edition": "Standard (PC, Windows)",
  "platform": "PC",
  "region": "Global",
  "locked": true
}
```

**Official Anchor**: 29.99 USD / key 
- Evidence Level: `First-Party Reported (retrieved directly)` · Freshness: `Current`
- Evidence: A053 microsoft.com official listing ($29.99; Deluxe Collection $39.99); GAMIVO editorial corroborates (Aug 2026)

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| Microsoft (official) | 29.99 | Java & Bedrock PC | Exact Match | First-Party Reported | Current | First-party | N/A | A053 |
| GAMIVO | — | Java & Bedrock (PC) key | Strong Comparable (price not captured) | Lead (listing) | Current | Unknown | Unknown | A012 |
| kiffmarketing (ZA storefront) | 35 | Java Bedrock Standard | Strong Comparable (ABOVE official — gray premium) | Secondary Reported | Unknown | Unknown | Unknown | A012 |

**Price Intelligence**:

- **Lowest verified offer**: $29.99 official
- **Cheapest advertised marketplace**: None below official verified (one reseller ABOVE official at $35)
- **Cheapest with documented guarantee**: Official $29.99
- **Effective acquisition cost notes**: Minecraft gray-market discount not observed this run — official is cheapest verified channel

**Coverage**:

- product_first: Verified Findings
- marketplace_first: Partial (prices thin)
- Notes: Minecraft- specific marketplace queries failed (A028, A052) — constructions recovered via official + editorial

---

### SKU-ESIM-001 — Airalo (reference) / market Regional eSIM data pack — Europe regional

**Family**: eSIM/Telecom

**SKU Identity** (comparability basis):

```json
{
  "brand": "Airalo (reference) / market",
  "product": "Regional eSIM data pack — Europe regional",
  "denomination": "10GB / 30 days",
  "region": "Europe (multi-country regional)",
  "locked": true
}
```

**Official Anchor**: 15.5 USD / 10GB/30 days (Europe regional) 
- Evidence Level: `First-Party Reported (retrieved directly)` · Freshness: `Current`
- Evidence: A013 airalo.com — Europe packages 10GB $15.50-17.00, 5GB $10.50 (Croatia example at $15.50)

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| Airalo (official site) | 15.5 | 10GB/30d Europe regional | Exact Match (reference brand) | First-Party Reported | Current | First-party eSIM terms | N/A | A013 |
| Airalo via esimdb (Portugal country pack) | 11 | 10GB/30d PORTUGAL (single country) | Non-Comparable (different SKU: country vs regional) — documented to prevent false comparison | Secondary Reported (aggregator) | Current (Sep 2026) | Unknown | Unknown | A013 |
| Airalo Eurolink (via abrokenbackpack) | 37 | 10GB/30d Europe | Possible Match–Review (dated info) | Secondary Reported (blog) | Stale (blog guide, likely pre-price-update) | Unknown | Unknown | A013 |

**Price Intelligence**:

- **Lowest verified offer**: $15.50 for Europe regional 10GB/30d (Airalo, First-Party)
- **Key insight**: Region granularity is decisive: Portugal country pack $11 ≠ Europe regional $15.50 — comparing them is a SKU-identity error
- **Cheapest with documented guarantee**: Airalo first-party $15.50
- **Effective acquisition cost notes**: eSIM B2B wholesale layer (DT One etc.) Retrieval-Limited — retail anchor only this run

**Coverage**:

- product_first: Verified Findings
- b2b_upstream: Retrieval-Limited (A046 failed)

---

### SKU-SMM-001 — undefined undefined

**Family**: SMM Services

**SKU Identity** (comparability basis):

```json
{
  "service": "Instagram Followers",
  "quantity": "1,000 followers",
  "quality_terms": "retention/refill quality UNKNOWN — materially affects comparability",
  "platform": "Instagram",
  "locked": "Partially — quality terms undefined (open field)"
}
```

**Official Anchor**: **Unknown — Retrieval-Limited** 
- Evidence Level: `N/A — no official anchor exists (market-defined service)` · Freshness: `N/A`
- Evidence: Meta sells ads, not followers; follower-selling market is platform-ToS-violating by nature (policy risk dimension, separate from price)

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| SMMFollowers | 0.64 | per 1,000 IG followers ($0.6391) | Strong Comparable (quality terms unverified) | Secondary Reported (panel comparator, Sep 2026) | Current | Unknown | Unknown | A043 |
| smmraja | 0.01 | 'under a cent per 1K' reseller rates | Possible Match–Review (quality tier unknown) | Advertised | Current | Unknown | Unknown | A043 |
| smmpwr | 0.0012 | from $0.0012 per 1,000 (460 services) | Possible Match–Review (floor rate, quality unknown, refill guarantee advertised) | First-Party Reported | Current | Refill guarantee advertised (terms unverified) | Unknown | A044 |
| PrimeFollows | — | services listed, price not captured | Strong Comparable (pending price) | Lead | Current | Unknown | Unknown | A042 |

**Price Intelligence**:

- **Lowest verified offer**: None Verified — all offers Advertised/Secondary with unknown quality terms
- **Cheapest advertised**: from $0.0012/1k (smmpwr floor rate) — NOT comparable without quality terms; $0.64/1k (SMMFollowers) as mid-market advertised rate
- **Comparability warning**: Follower quality/retention/refill terms materially alter commercial value — prices across panels are NOT valid comparisons without quality lock (SKU identity incomplete)
- **Policy risk dimension**: Follower-selling violates Instagram platform terms — risk dimension recorded separately from price per spec

**Coverage**:

- seller_first: Partial (2/3 seeds verified)
- price_first: Verified Findings (market rates)

---

### SKU-VN-001 — undefined undefined

**Family**: Virtual Numbers/SMS

**SKU Identity** (comparability basis):

```json
{
  "service": "Virtual number for SMS/OTP verification",
  "country": "US (reference market)",
  "number_type": "non-VoIP real SIM (premium tier)",
  "duration": "single activation window",
  "supported_service": "service-specific (materially affects price)",
  "locked": "Partially — service-specific pricing open"
}
```

**Official Anchor**: **Unknown — Retrieval-Limited** 
- Evidence Level: `N/A — market-defined service` · Freshness: `N/A`
- Evidence: No official anchor; carrier pricing not directly comparable to OTP rental market

**Offers** (each an independent commercial proposition):

| Entity | Price | Unit | Match | Price Evidence | Freshness | Guarantee | Resale | Source |
|---|---|---|---|---|---|---|---|---|
| BlackHatWorld sellers (US non-VoIP) | 0.05 | per number (from $0.05, real US SIMs, OTP) | Strong Comparable (service-specific pricing caveat) | Advertised (marketplace) | Current (Mar 2026) | Unknown | Unknown | A045 |
| 5SIM | — | unlimited SMS per site within 5-30min window | Strong Comparable (price not captured) | Lead | Current (Sep 2026) | Unknown | Unknown | A045 |
| smscode.gg | — | OTP numbers (positions as cheaper 5SIM alternative) | Strong Comparable (price not captured) | Lead | Current | Unknown | Unknown | A045 |

**Price Intelligence**:

- **Lowest verified offer**: None Verified
- **Cheapest advertised**: from $0.05 per US non-VoIP number (marketplace advertised)
- **Comparability warning**: Country + number type (VoIP vs real SIM) + supported service materially change price — full SKU lock required before ranking

**Coverage**:

- price_first: Verified Findings (market signal)

---

## 4. Remaining Catalog (400+ SKU program)

| Family | Status | Planned Coverage |
|---|---|---|
| AI/SaaS (beyond 2 anchor SKUs) | Not Searched — queued Batch 2+ | ChatGPT Pro, Claude, Perplexity, Copilot, API credits, edu/work plans |
| Gift Cards (beyond 3 anchor SKUs) | Not Searched — queued | PSN, Xbox, Nintendo eShop, Razer Gold, Amazon, Visa/MC prepaid, denominations × regions |
| Game Top-up (beyond 2) | Not Searched — queued | Mobile Legends, Genshin, Roblox Robux, Valorant, LOL RP, Free Fire other denominations |
| Game Keys (beyond 1) | Not Searched — queued | AAA titles, Steam/EGS/Xbox/PSN platform matrix, region locks |
| Software/Licenses (beyond 1) | Not Searched — queued | Office suites, antivirus, Adobe, Windows Server, OEM vs retail |
| eSIM/Telecom (beyond 1) | Not Searched — queued | Country/regional/global packs × carriers × validity |
| SMM (beyond 1) | Not Searched — queued | Platform × service type × quantity tiers × quality grades |
| Virtual Numbers/SMS (beyond 1) | Not Searched — queued | Country × service × number type × duration |
| Digital Subscriptions (beyond 3) | Not Searched — queued | YouTube Premium, Disney+, Xbox Game Pass, regional storefronts |

> Every "Not Searched" status is an honest §15 state — it never means "does not exist". Every 'Not Searched' status is an honest §15 state — never 'does not exist'. Budget-limited by design of Batch 1.

## 5. Entities & Role Classification

### 5.1 Publishers / Official Sources (10)

#### ENT-001 — OpenAI

- **Type**: Publisher / Official Source
- **Role**: Primary Source (Publisher) — ChatGPT Plus
- **Status**: Verified-Active
- **Verified via**: A001, A023
- **Independence**: Independent Origin
- **Guarantee**: N/A (first-party sales)
- **Resale**: No authorized reseller program evidenced; community reports (A023, facebook.com) state significant discounts on ChatGPT subscriptions are typically unofficial
- **Evidence**:
  - [A001] community.openai.com — ChatGPT Plus referenced at $20/month (official price discussed on official community forum) (`Secondary Reported`, Freshness: Current (reconfirmed Jan 2026 via A023 smartbuy.alibaba.com: $20/month monthly billing, $200/year annual))
- **Notes**: Official chatgpt.com pricing page not directly retrieved this run — $20/mo anchored via secondary sources only, marked Secondary Reported

#### ENT-002 — Google (Gemini / Google One AI Pro)

- **Type**: Publisher / Official Source
- **Role**: Primary Source (Publisher) — Gemini AI Pro
- **Status**: Verified-Active
- **Verified via**: A002
- **Independence**: Independent Origin
- **Guarantee**: N/A (first-party sales)
- **Resale**: Unknown — reseller signal: Etsy listing 'Gemini AI 18 Month Pro Plan' (A002, etsy.com) = Unverified Lead, unauthorized resale suspected (no Google reseller program evidenced)
- **Evidence**:
  - [A002] tech.yahoo.com — AI Pro costs $19.99/month outside of trial (Aug 2026) (`Secondary Reported (consistent ×2: savingadvice.com — $19.99/mo, $199.99/yr annual)`, Freshness: Current (Aug 2026))
- **Notes**: Etsy reseller lead is a discovery branch for Batch 2 (AI subscription gray market)

#### ENT-003 — Netflix

- **Type**: Publisher / Official Source
- **Role**: Primary Source (Publisher) — Netflix plans
- **Status**: Verified-Active
- **Verified via**: A004
- **Independence**: Independent Origin
- **Guarantee**: N/A (first-party sales)
- **Resale**: Netflix gift cards exist but region-limited; no reseller offer captured this run (A068 rate-limited — Retrieval-Limited)
- **Evidence**:
  - [A004] help.netflix.com — US plans: Standard with ads $8.99/mo, Standard $19.99/mo, Premium $26.99/mo, extra member $7.99-9.99 (`First-Party Reported (official help pages, retrieved directly)`, Freshness: Current (reconfirmed 2026 by checkthat.ai Aug 2026))

#### ENT-004 — Spotify AB

- **Type**: Publisher / Official Source
- **Role**: Primary Source (Publisher) — Spotify Premium
- **Status**: Verified-Active
- **Verified via**: A072
- **Independence**: Independent Origin
- **Guarantee**: N/A (first-party sales)
- **Resale**: 12-month key reseller market exists (A024: ozbargain US$20.86 for 12 months — 87% below official $155.88/yr) — Possible Match–Review, region/method ambiguous, high gray-market risk
- **Evidence**:
  - [A072] spotify.com — Premium Individual: $0 first month (trial), then $12.99/month (US) (`First-Party Reported (official site, retrieved directly)`, Freshness: Current (Aug 2026 corroboration: checkthat.ai — $12.99/mo, +30% since 2023; freeyourmusic.com 2026))
- **Notes**: 3 query attempts failed before direct capture (A003, A014, A057) — Failure Recovery applied, 4th construction succeeded

#### ENT-005 — NordVPN

- **Type**: Publisher / Official Source
- **Role**: Primary Source (Publisher) — NordVPN subscriptions
- **Status**: Verified-Active
- **Verified via**: A005, A031
- **Independence**: Independent Origin
- **Guarantee**: N/A (first-party)
- **Resale**: Restricted — publisher explicitly states no G2A sellers are authorized; marketplace keys (allkeyshop: $4.90 at K4G) carry unauthorized-resale status
- **Evidence**:
  - [A005] nordvpn.com — Complete plan: $121.23 first 12 months (75% off $219.48), renews at $219.48/yr; VAT may apply (`First-Party Reported (official site, retrieved directly)`, Freshness: Current)
  - [A031] nordvpn.com — OFFICIAL WARNING (Dec 2025): 'No G2A seller is authorized to resell NordVPN subscriptions' — publisher-documented resale restriction (`First-Party Reported`, Freshness: Current)
- **Notes**: Plan tiers materially differ (Basic/Plus/Complete) — SKU identity must lock tier; security.org: Basic 1-yr ≈ $5.49/mo

#### ENT-006 — Microsoft / Xbox

- **Type**: Publisher / Official Source
- **Role**: Primary Source (Publisher) — Windows 11 Pro, Minecraft, Xbox
- **Status**: Verified-Active
- **Verified via**: A053, A056, A011
- **Independence**: Independent Origin
- **Guarantee**: N/A (first-party)
- **Resale**: OEM key resale legally gray — Linus Tech Tips forum (A026): 'A key is not a license, as Microsoft has repeatedly clarified'; no authorized reseller program for standalone keys evidenced
- **Evidence**:
  - [A053] microsoft.com — Minecraft: Java & Bedrock Edition for PC = $29.99 (official listing) (`First-Party Reported (retrieved directly)`, Freshness: Current)
  - [A056] learn.microsoft.com + techradar.com — Windows 11 Pro = $199.99 official price (user-confirmed on MS Learn; techradar corroborates) (`First-Party Reported + Secondary`, Freshness: Current)
- **Notes**: Windows 11 Pro anchor failed twice (A011, A019) before capture — Failure Recovery applied

#### ENT-007 — Garena

- **Type**: Publisher / Official Source
- **Role**: Primary Source (Publisher) — Free Fire diamonds
- **Status**: Verified-Active (channels only — pricing not captured)
- **Verified via**: A054
- **Independence**: Independent Origin
- **Guarantee**: N/A
- **Resale**: Third-party top-up sellers exist (gameseal, karteet) — authorization Unknown
- **Evidence**:
  - [A054] shop.garena.sg + store.garena.com — Official Top Up Centers for Free Fire confirmed (SG + US storefronts exist) (`First-Party Reported (channel existence)`, Freshness: Current)
- **Notes**: 520-diamond pack price NOT captured in 4 attempts (A010, A018, A074 + gameseal listing is 2200 denomination — Non-Comparable). SKU price anchor = Unknown (Retrieval-Limited)

#### ENT-008 — Tencent / Midasbuy

- **Type**: Official Top-Up Channel (publisher-authorized)
- **Role**: Official Channel — PUBG Mobile UC
- **Status**: Verified-Active
- **Verified via**: A059
- **Independence**: Independent Origin
- **Guarantee**: Official after-sales support stated (publisher channel)
- **Resale**: N/A (is the official channel)
- **Evidence**:
  - [A059] midasbuy.com + reddit.com/r/PUBGMobile — Midasbuy = official top-up store for PUBG Mobile UC (US store), instant crediting; Reddit community confirms 'official third party uc purchase site'; 10% discount advertised (`First-Party Reported + Community corroboration`, Freshness: Current)
- **Notes**: Advertised 10% discount → effective ≈$8.99 for 660 UC (Advertised level)

#### ENT-009 — Valve / Steam

- **Type**: Platform / Official Source
- **Role**: Primary Source (Platform) — Steam Wallet
- **Status**: Verified-Active
- **Verified via**: A006, A020
- **Independence**: Independent Origin
- **Guarantee**: N/A (wallet codes are value instruments)
- **Resale**: Wallet cards are currency+region-locked (USD cards for US accounts, ₴ UAH cards for UA accounts, etc.) — cross-region cards are Non-Comparable SKUs
- **Evidence**:
  - [A006] store.steampowered.com + gamestop.com — Steam Wallet codes redeemed at face value; $20 card sold at $20 via official/retail channels (GameStop listing) (`First-Party Reported (redemption mechanics) + Retail listing`, Freshness: Current)
- **Notes**: Key structural finding: US-region Steam wallet codes trade ABOVE face on gray market (gg.deals via A021: $13 card at $14.10 G2A, +8.5% premium)

#### ENT-010 — Apple (App Store & iTunes)

- **Type**: Publisher / Official Source
- **Role**: Primary Source (Publisher) — iTunes gift cards
- **Status**: Verified-Active
- **Verified via**: A015
- **Independence**: Independent Origin
- **Guarantee**: N/A
- **Resale**: Cards are region-locked to redemption region (US cards for US Apple ID); MENA sellers resell US cards at ≈face (A051: gml-store $250 card at 937.50 SAR = exact face at 3.75 SAR/USD)
- **Evidence**:
  - [A015] amazon.com + bestbuy.com — Apple $25 App Store & iTunes gift card sold at $25 face value via official US retail (Amazon, Best Buy digital delivery) (`First-Party Retail`, Freshness: Current)

### 5.2 B2B / Upstream API Infrastructure (4)

#### ENT-011 — DT One (dtone.com)

- **Type**: B2B Digital Value Marketplace / API Platform
- **Role**: Upstream Supplier (B2B infrastructure) — mobile top-up, data bundles, gift cards, gaming pins, streaming vouchers
- **Status**: Verified-Active
- **Verified via**: A076
- **Independence**: Independent Origin (dtone.com + globenewswire + prospeo.io — 3 distinct origins)
- **Guarantee**: Unknown (B2B terms not publicly retrieved)
- **Resale**: N/A — is itself an upstream layer; B2B pricing requires account (Retrieval-Limited)
- **Evidence**:
  - [A076] dtone.com — DT One powers PayPal France mobile airtime entry; DT Shop offers mobile top-ups, gift cards, gaming pins, streaming vouchers (`First-Party Reported (retrieved directly)`, Freshness: Current)
  - [A076] globenewswire.com (Mar 2026) — Bitget Wallet integrates DT One for mobile top-ups across 170+ countries, 500+ local operators (`Secondary Reported (press release)`, Freshness: Current (Mar 2026))
- **Relationships**:
  - → PayPal (France): Infrastructure provider (airtime) — `Documented (dtone.com case study)`
  - → Bitget Wallet: Top-up infrastructure provider — `Documented (press release Mar 2026)`
- **Notes**: Deepest evidence-supportable upstream layer this run. Relationship to specific MENA retailers = Unresolved Hypothesis (no direct link evidenced)

#### ENT-012 — Reloadly

- **Type**: B2B Payments / API Platform
- **Role**: Upstream Supplier (B2B infrastructure) — airtime top-ups, data bundles, digital gift cards, utility payments
- **Status**: Verified-Active
- **Verified via**: A040
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: N/A — upstream B2B layer; pricing requires account (Retrieval-Limited)
- **Evidence**:
  - [A040] f6s.com + sourceforge.net + slashdot.org — Developer-first payments platform and API for global airtime top-ups, data bundles, digital gift cards, utility payments; 2,500+ payout options (`Secondary Reported (3 independent directory sources)`, Freshness: Current (Aug 2026 directory))
- **Notes**: Appeared in user seeds TWICE (direct lead + B2B aggregator) — Entity Resolution: single entity, dual role listing in seed records (no split/merge conflict)

#### ENT-013 — Ding / DingConnect

- **Type**: B2B Mobile Top-Up API Platform
- **Role**: Upstream Supplier (B2B infrastructure) — international mobile recharge, gift vouchers, bill payments
- **Status**: Verified-Active
- **Verified via**: A041
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: N/A — upstream B2B layer; pricing requires account (Retrieval-Limited)
- **Evidence**:
  - [A041] dingconnect.com + blog.dingconnect.com — DingConnect = #1 mobile top-up API for businesses; free account, test API keys available via DingConnect+ portal (`First-Party Reported (retrieved directly)`, Freshness: Current)
- **Notes**: Offers self-service test credentials — Batch 2 can attempt authorized B2B price discovery

#### ENT-014 — Al Momaiz Card (المميز كارد)

- **Type**: MENA Digital Store + B2B API (hybrid)
- **Role**: Retailer + potential regional distributor/aggregator (dual-signal)
- **Status**: Verified-Active
- **Verified via**: A035
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unknown
- **Evidence**:
  - [A035] play.google.com — Al-Mamiz Card app: 'leading provider of game, software, and e-card recharge services' (official app listing) (`First-Party Reported (official app store listing)`, Freshness: Current)
  - [A035] almomaizcard.com — Public REST API Reference exists — B2B API capability documented (beyond retail) (`First-Party Reported`, Freshness: Current)
- **Notes**: Seed re-verified: PROMOTED from Unverified Lead → Verified-Active. Dual nature (retail app + public API) suggests aggregator/distributor role — role classification: Seller + API provider; exact upstream position Unresolved

### 5.3 Marketplaces / Sellers / Services (38)

#### ENT-020 — Eneba

- **Type**: Marketplace (keyshop aggregator)
- **Role**: Marketplace
- **Status**: Verified-Active
- **Verified via**: A020, A017, A024
- **Independence**: Independent Origin
- **Guarantee**: Marketplace-level buyer protection exists (terms not fully reviewed) — No Documented Guarantee at offer level
- **Resale**: Terms Available — Permission Unclear (marketplace model; seller-level authorization varies)
- **Evidence**:
  - [A020] eneba.com — Steam Wallet Gift Card 10 USD (EL SALVADOR region) listed — region-specific wallet cards sold (`First-Party Reported (listing)`, Freshness: Current)
  - [A017] eneba.com — PUBG Mobile 600+60 UC Key GLOBAL listed (`First-Party Reported (listing)`, Freshness: Current)
  - [A024] ozbargain.com.au — Eneba cited as seller of discounted Spotify Premium 12-month keys (`Secondary Reported (community)`, Freshness: Feb 2025 — Stale)

#### ENT-021 — Kinguin

- **Type**: Marketplace
- **Role**: Marketplace
- **Status**: Verified-Active
- **Verified via**: A021, A026
- **Independence**: Independent Origin
- **Guarantee**: Marketplace buyer protection exists — No Documented Guarantee at offer level
- **Resale**: Terms Available — Permission Unclear
- **Evidence**:
  - [A021] kinguin.net — Steam Gift Card ₴800 UAH listed at $18.85-19.64 (UAH-currency card for UA accounts, below ~$19.40 USD-equivalent face) (`First-Party Reported (listing)`, Freshness: Current)
  - [A026] steemit.com guide — Windows 11 Pro OEM keys ~$20-30 typical on Kinguin/G2A/CDKeys (`Secondary Reported`, Freshness: Current)
- **Notes**: UAH card = Non-Comparable to USD-region cards (currency-locked SKU)

#### ENT-022 — G2A

- **Type**: Marketplace
- **Role**: Marketplace
- **Status**: Verified-Active
- **Verified via**: A021, A031
- **Independence**: Independent Origin
- **Guarantee**: G2A Shield buyer protection exists — No Documented Guarantee at offer level
- **Resale**: Restricted (at least for NordVPN — publisher-documented unauthorized)
- **Evidence**:
  - [A021] g2a.com — Steam Gift Card 60 USD (EL SALVADOR) listed; gg.deals reports G2A lowest for $13 US card at $14.10 (+8.5% above face) (`First-Party Reported (listing) + Aggregator`, Freshness: Current)
  - [A031] nordvpn.com official warning — NordVPN officially states NO G2A seller is authorized to resell NordVPN subscriptions (`First-Party (publisher counter-evidence)`, Freshness: Current (Dec 2025))
- **Notes**: Publisher counter-evidence captured — feeds Exclusion/Review classification for unauthorized resale offers

#### ENT-023 — GAMIVO

- **Type**: Marketplace
- **Role**: Marketplace
- **Status**: Verified-Active
- **Verified via**: A012, A053
- **Independence**: Independent Origin
- **Guarantee**: SMART subscription buyer protection exists — No Documented Guarantee at offer level
- **Resale**: Terms Available — Permission Unclear
- **Evidence**:
  - [A012] gamivo.com — Minecraft Java & Bedrock Edition (PC) listed on GAMIVO (`First-Party Reported (listing)`, Freshness: Current)
  - [A053] gamivo.com blog (Aug 2026) — GAMIVO editorial confirms Minecraft official price $29.99 / Deluxe $39.99 (`Secondary Reported (marketplace editorial)`, Freshness: Current (Aug 2026))

#### ENT-024 — GGSel (ggsel.net)

- **Type**: Marketplace (RU)
- **Role**: Marketplace
- **Status**: Verified-Active
- **Verified via**: A048, A032
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Terms Available — Permission Unclear
- **Evidence**:
  - [A048] ggsel.net — GGSel marketplace sells digital keys, gifts, top-ups, subscriptions, gift cards (`First-Party Reported (listing)`, Freshness: Current)
  - [A032] dtf.ru (Jun 2026) — GGSel described as marketplace for Steam codes in RU-market Steam top-up guide (`Secondary Reported (independent editorial)`, Freshness: Current (Jun 2026))
- **Notes**: Individual seller seed 'Макс111 on GGSel' — not separately verified this run (remains Unverified Lead)

#### ENT-025 — Plati.market

- **Type**: Marketplace (RU)
- **Role**: Marketplace
- **Status**: Verified-Active
- **Verified via**: A032
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Terms Available — Permission Unclear
- **Evidence**:
  - [A032] plati.market + vc.ru (Jun 2026) — Plati.Market sells Steam top-ups, keys, gift cards from multiple sellers (RU-market payment-workaround context) (`First-Party Reported (listing) + Secondary (vc.ru editorial)`, Freshness: Current (Jun 2026))
- **Notes**: Example observed: Planet Coaster Steam key at 1195.55₽ (Non-Comparable SKU, RU region)

#### ENT-026 — Z2U

- **Type**: Marketplace
- **Role**: Marketplace (gift cards, accounts, top-ups)
- **Status**: Verified-Active
- **Verified via**: A049
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear — account trading violates most publishers' ToS; flagged for review
- **Evidence**:
  - [A049] z2u.com — Z2U sells Steam Wallet Gift Cards ($5-$100) and Steam Wallet Top-Up; also trades ACCOUNTS (3,178 account listings) — account trading = elevated risk signal (`First-Party Reported (listing)`, Freshness: Current)
- **Notes**: RISK SIGNAL: marketplace includes account sales (not just keys) — Needs-Human-Review for any commercial use

#### ENT-027 — K4G

- **Type**: Marketplace
- **Role**: Marketplace
- **Status**: Verified-Active
- **Verified via**: A031
- **Independence**: Shared-Origin risk: single comparator source — Unresolved independence
- **Guarantee**: Unknown
- **Resale**: Restricted (NordVPN publisher warning covers unauthorized resale channels)
- **Evidence**:
  - [A031] allkeyshop.com — NordVPN subscription lowest $4.90 at K4G (via allkeyshop comparator) (`Secondary Reported (comparator)`, Freshness: Current)
- **Notes**: Cheapest NordVPN signal — carries publisher counter-evidence

#### ENT-028 — itemku

- **Type**: Marketplace (SEA/ID)
- **Role**: Marketplace (game top-up)
- **Status**: Verified-Active
- **Verified via**: A017
- **Independence**: Independent Origin
- **Guarantee**: Marketplace transaction guarantee claimed ('100% secure transactions, guaranteed') — Advertised-level guarantee
- **Resale**: Terms Available — Permission Unclear (top-up service model)
- **Evidence**:
  - [A017] itemku.com — PUBG Mobile 660 UC top-up from USD 10.07 (Sept 2026), installment support (`First-Party Reported (listing)`, Freshness: Current (Sep 2026))

#### ENT-029 — Turgame

- **Type**: Digital Store (TR-focused)
- **Role**: Seller / Reseller
- **Status**: Verified-Active (offer observed SOLD OUT)
- **Verified via**: A037, A075
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear — region-locked inventory model (TR-region products)
- **Evidence**:
  - [A037] turgame.com — PUBG 660 UC 10 USD / 454.90 TRY — LISTED AS SOLD OUT at observation time (`First-Party Reported (directly observed listing state)`, Freshness: Current)
  - [A075] instagram.com (turgame official promo) — Turgame actively markets TRY-denominated PSN wallet codes valid ONLY for Turkish-region PSN accounts (`Secondary Reported (official social)`, Freshness: Current)
- **Notes**: Entity Resolution vs 'Definite Play' (seed): NO evidence found linking the two names (A058 failed, A075 indirect) → Unresolved Hypothesis. Availability evidence: 660 UC offer SOLD OUT at check time

#### ENT-030 — bittopup (pubguc.bittopup.com)

- **Type**: Top-Up Store (AR-facing)
- **Role**: Seller / Reseller
- **Status**: Verified-Active
- **Verified via**: A050, A060
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A050] pubguc.bittopup.com — PUBG 660 UC (600+60) = $8.707 ($1.319/100 UC unit display); 1800 UC = $22.22 — below official $9.99 (`First-Party Reported (listing)`, Freshness: Current (2026))
  - [A060] news.bittopup.com (Mar 2026) — bittopup's own editorial: 'discounts of 30-50% below face value are always fraudulent. The economics don't work for legitimate sellers' (on gift cards) (`First-Party (their own fraud-economics statement)`, Freshness: Current (Mar 2026))
- **Notes**: 13% below official = within plausible promo band (official Midasbuy itself discounts 10%); bittopup's own fraud-economics statement provides context for evaluating deeper discounts

#### ENT-031 — cardsouq (cardsouq.com)

- **Type**: Top-Up / Gift Card Store (AR-facing)
- **Role**: Seller / Reseller
- **Status**: Verified-Active (offer flagged Possible Match–Review)
- **Verified via**: A050
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A050] cardsouq.com — PUBG 600+60 UC: original price $9.99 → CURRENT $4.99 (50% off); also 16200 UC at $50 (`First-Party Reported (listing)`, Freshness: Current (2026))
- **Notes**: LOWEST PUBG price observed — 50% below official. Counter-evidence: bittopup fraud-economics statement (30-50% below face = always fraudulent for gift cards). Delivery method/terms unverified (voucher vs ID-login top-up). Hypothesis H1 open: promo/loss-leader vs different-delivery-terms vs fraudulent. NOT ranked as Cheapest Verified — held in review state

#### ENT-032 — gameseal

- **Type**: Digital Store
- **Role**: Seller / Reseller
- **Status**: Verified-Active
- **Verified via**: A054
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A054] gameseal.com — Free Fire 2200 Diamonds Direct Top-Up GLOBAL listed (price not captured in snippet) (`First-Party Reported (listing existence)`, Freshness: Current)
- **Notes**: Seed re-verified: PROMOTED to Verified-Active. 2200-diamond denomination = Non-Comparable to 520 SKU

#### ENT-033 — digitalmaze

- **Type**: License Store
- **Role**: Seller / Reseller (software licenses)
- **Status**: Verified-Active
- **Verified via**: A056
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear — OEM/gray license resale legally gray per Microsoft position (A026)
- **Evidence**:
  - [A056] digitalmaze.com — Windows 11 Pro License: $74.99 sale (regular $199.99) — 62% below official (`First-Party Reported (listing)`, Freshness: Current)

#### ENT-034 — LikeCard (likecard.com)

- **Type**: MENA Gift Card Platform
- **Role**: Regional Platform / Reseller
- **Status**: Verified-Active
- **Verified via**: A051
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A051] ar-bahrain.likecard.com — Apple gift cards sold (BH storefront) with Apple support redemption guidance (`First-Party Reported (listing)`, Freshness: Current)
- **Notes**: NEW DISCOVERY (not in seed list) — major MENA card platform

#### ENT-035 — bitaqaty (بطاقاتي)

- **Type**: MENA Gift Card Platform
- **Role**: Regional Platform / Reseller
- **Status**: Verified-Active
- **Verified via**: A035
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A035] bitaqaty.com — Sells iTunes, Razer Gold, PlayStation, PUBG top-up, Zain, Mobily cards — instant delivery claimed (`First-Party Reported (listing)`, Freshness: Current)
- **Notes**: NEW DISCOVERY — MENA card aggregator

#### ENT-036 — snoonu

- **Type**: Qatari Digital Store
- **Role**: Seller / Reseller
- **Status**: Verified-Active
- **Verified via**: A015
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear (US-region cards sold in QA market — cross-region resale model)
- **Evidence**:
  - [A015] snoonu.com — Apple iTunes Gift Card 25 USD (USA region) sold in Qatar (`First-Party Reported (listing)`, Freshness: Current)

#### ENT-037 — yallatoys

- **Type**: Qatari Store (digital cards)
- **Role**: Seller / Reseller
- **Status**: Verified-Active
- **Verified via**: A051
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A051] yallatoys.com — Apple iTunes US $25 gift card sold in Qatar with instant delivery (`First-Party Reported (listing)`, Freshness: Current)

#### ENT-038 — gml-store

- **Type**: Digital Store (AR)
- **Role**: Seller / Reseller
- **Status**: Verified-Active
- **Verified via**: A051
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A051] gml-store.com — US iTunes $250 card at 937.50 (SAR) = exact face value at 3.75 SAR/USD (`First-Party Reported (listing)`, Freshness: Current)
- **Notes**: Evidence MENA stores sell US cards AT face — no below-face verified in MENA iTunes segment

#### ENT-039 — vexacard

- **Type**: Digital Store (AR)
- **Role**: Seller / Reseller
- **Status**: Verified-Active
- **Verified via**: A036
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A036] vexacard.com — US App Store/iTunes $30 card sold with digital code delivery (`First-Party Reported (listing)`, Freshness: Current)
- **Notes**: NEW DISCOVERY via language expansion (A036 was FazerCards verification — FazerCards itself not found)

#### ENT-040 — karteet (كرتيت)

- **Type**: Digital Store (AR)
- **Role**: Seller / Reseller
- **Status**: Verified-Active
- **Verified via**: A036
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A036] karteet.com — Free Fire 2420 diamonds MENA top-up listed (`First-Party Reported (listing)`, Freshness: Current)
- **Notes**: 2420-diamond denomination = Non-Comparable to 520 SKU

#### ENT-041 — Midasbuy-adjacent sellers (buffbuff, Epinby)

- **Type**: Top-Up Sellers
- **Role**: Sellers / Resellers (claims of authorization)
- **Status**: Leads (advertised claims, not verified)
- **Verified via**: A059
- **Independence**: N/A
- **Guarantee**: Unknown
- **Resale**: Authorization CLAIMED but not verified against Tencent/Midasbuy — Unclear
- **Evidence**:
  - [A059] buffbuff.com + instagram.com (Epinby) — buffbuff claims 'Officially authorized PUBG UC top-up, up to 55% OFF'; Epinby markets PUBG vouchers on Instagram (`Advertised (self-claimed)`, Freshness: Current)
- **Notes**: 'Up to 55% off' + 'officially authorized' claims are unverified marketing statements — flagged for Batch 2 authorization verification

#### ENT-042 — opensooq individual sellers (JO)

- **Type**: Classifieds individuals
- **Role**: Individual sellers (non-generalizable)
- **Status**: Lead (individual marketplace)
- **Verified via**: A050
- **Independence**: N/A
- **Guarantee**: Unknown
- **Resale**: Unknown
- **Evidence**:
  - [A050] jo.opensooq.com — Individuals offering PUBG 660 UC at 3.50 JOD (~$4.93) in Jordan classifieds (`Lead (classifieds listing)`, Freshness: Current)
- **Notes**: Non-generalizable individual offers — excluded from commercial ranking, retained in research record (Lowest Negotiated Offer category candidate if transaction-verified in future)

#### ENT-043 — Wincdkey

- **Type**: Keyshop (seed)
- **Role**: Seller / Reseller (software keys)
- **Status**: Verified-Active (entity only — prices not captured)
- **Verified via**: A027
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear (gray-market keyshop model)
- **Evidence**:
  - [A027] de.trustpilot.com — WINCDKEY Trustpilot DE profile with 2,722 reviews, positive German review referencing Windows 11 Pro key purchase 'at a top price, received within seconds' (`Secondary Reported (reputation platform)`, Freshness: Current)
- **Notes**: Seed re-verified at ENTITY level; no current price captured for Batch 1 SKUs

#### ENT-044 — Bitcodes

- **Type**: Keyshop (seed)
- **Role**: Seller / Reseller (software keys)
- **Status**: Verified-Active (offer via comparator)
- **Verified via**: A027
- **Independence**: Shared-Origin risk: comparator + coupon site relationship — Unresolved
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A027] gocdkeys.de — Office 2021 PC key from €0.50 at Bitcodes (with coupon gocd76 applied — coupon-conditional price) (`Secondary Reported (comparator)`, Freshness: Current)
- **Notes**: €0.50 Office 2021 = coupon-conditional extreme-low — Possible Match–Review

#### ENT-045 — Keywrld

- **Type**: Keyshop (seed)
- **Role**: Seller / Reseller (software keys)
- **Status**: Verified-Active (offer via comparator)
- **Verified via**: A027
- **Independence**: Shared-Origin risk: single comparator source
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A027] allkeyshop.com — Windows 11 Pro at €1.03 (Keywrld, via allkeyshop comparator) (`Secondary Reported (comparator)`, Freshness: Current)
- **Notes**: €1.03 for $199.99 software = 99.5% below official — extreme outlier, Possible Match–Review (likely coupon/first-purchase condition)

#### ENT-046 — Keys4us

- **Type**: Keyshop (seed)
- **Role**: Seller / Reseller (software keys)
- **Status**: Verified-Active (offers via comparator)
- **Verified via**: A027
- **Independence**: Shared-Origin risk: single comparator source
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A027] allkeyshop.com — Office 2024 Professional Plus (Keys4us) and Office 2021 Pro Plus at €0.46 (via allkeyshop) (`Secondary Reported (comparator)`, Freshness: Current)
- **Notes**: €0.46 Office 2021 Pro Plus — same coupon-conditional pattern as Bitcodes (both via German comparator ecosystem)

#### ENT-047 — Airalo

- **Type**: eSIM Retailer
- **Role**: Retailer (eSIM data packs)
- **Status**: Verified-Active
- **Verified via**: A013
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: N/A (first-party retail)
- **Evidence**:
  - [A013] airalo.com — Europe regional eSIMs: 10GB $15.50-17.00 (30 days); 5GB $10.50; country packs differ (Croatia 10GB $15.50) (`First-Party Reported (retrieved directly)`, Freshness: Current)
- **Notes**: eSIM SKU identity MUST lock region granularity: Europe regional ≠ single country (esimdb: Portugal 10GB $11 with 15% discount — different SKU)

#### ENT-048 — esimdb

- **Type**: eSIM Aggregator/Comparator
- **Role**: Aggregator
- **Status**: Verified-Active
- **Verified via**: A013
- **Independence**: Independent Origin
- **Guarantee**: N/A
- **Resale**: N/A
- **Evidence**:
  - [A013] esimdb.com (Sep 2026) — Airalo Portugal 10GB/30d listed at $11 ($1.10/GB) with 15% discount; 50GB $35 (`Secondary Reported (aggregator)`, Freshness: Current (Sep 2026))
- **Notes**: Aggregator shows discounted Airalo price below Airalo's own site for country pack

#### ENT-049 — PrimeFollows

- **Type**: SMM Panel (seed)
- **Role**: Service Seller (SMM)
- **Status**: Verified-Active (entity — prices not captured)
- **Verified via**: A042
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: N/A (service)
- **Evidence**:
  - [A042] primefollows.com — Active SMM panel: Instagram, TikTok, YouTube, Facebook, X, Telegram services ('cheapest' self-claimed) (`First-Party Reported (site retrieved)`, Freshness: Current)
- **Notes**: Seed re-verified: PROMOTED to Verified-Active. IG followers 1000 price NOT captured — Batch 2 gap

#### ENT-050 — SMMFollowers

- **Type**: SMM Panel (seed)
- **Role**: Service Seller (SMM)
- **Status**: Verified-Active
- **Verified via**: A043
- **Independence**: Independent Origin
- **Guarantee**: Unknown (retention/refill terms not captured — quality dimension open)
- **Resale**: N/A
- **Evidence**:
  - [A043] comparesmmpanel.com (Sep 2026) — SMMFollowers: 1,181 services; Instagram Followers [Max 500k] $0.6391; Instagram Views $10/300,000 (`Secondary Reported (panel comparator)`, Freshness: Current (Sep 2026))
- **Notes**: IG Followers ≈ $0.64/1000 (advertised panel rate)

#### ENT-051 — SMM market floor (smmraja, smmpwr, usdsmm)

- **Type**: SMM Panels (market)
- **Role**: Service Sellers (SMM)
- **Status**: Verified-Active (market rates)
- **Verified via**: A043, A044
- **Independence**: Independent Origin (multiple panels)
- **Guarantee**: smmpwr: refill guarantee advertised (quality terms unknown)
- **Resale**: N/A
- **Evidence**:
  - [A043] smmraja.com — Instagram followers 'reseller rates starting under a cent per 1K' (`Advertised`, Freshness: Current)
  - [A044] smmpwr.com — 460 Instagram services from $0.0012 to $833.18 per 1000, refill guarantee offered (`First-Party Reported`, Freshness: Current)
- **Notes**: Market floor for IG followers ≈ $0.0012-0.64/1k — quality/retention materially varies and is NOT comparable without quality terms (per SKU identity rule)

#### ENT-052 — 5SIM

- **Type**: Virtual Number Provider
- **Role**: Service Seller (virtual numbers/SMS)
- **Status**: Verified-Active
- **Verified via**: A045
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: N/A
- **Evidence**:
  - [A045] 5sim.net (Sep 2026) — Virtual numbers for SMS/OTP, unlimited SMS within 5-30 min window per purchase (`First-Party Reported`, Freshness: Current (Sep 2026))
- **Notes**: SKU identity for virtual numbers must lock: country + number type (VoIP/non-VoIP) + supported service

#### ENT-053 — SMS verification market (smscode.gg, blackhatworld sellers)

- **Type**: Virtual Number Market
- **Role**: Service Sellers
- **Status**: Verified-Active (market rates)
- **Verified via**: A045
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: N/A
- **Evidence**:
  - [A045] blackhatworld.com (Mar 2026) + smscode.gg — Real US non-VoIP SIM numbers for OTP verification from $0.05; smscode.gg positions as cheaper 5SIM alternative (`Advertised (marketplace)`, Freshness: Current (Mar 2026))
- **Notes**: US non-VoIP = premium tier vs VoIP numbers; from $0.05 per number advertised

#### ENT-054 — Bitrefill

- **Type**: Gift Card / Top-Up Platform (crypto)
- **Role**: Platform / Reseller
- **Status**: Verified-Active
- **Verified via**: A022
- **Independence**: Independent Origin
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A022] bitrefill.com — Sells Eneba gift cards (custom amounts) for Bitcoin/ETH/Lightning in USA (`First-Party Reported (listing)`, Freshness: Current)
- **Notes**: Second-layer resale signal: marketplace gift cards (Eneba) resold via crypto platform

#### ENT-055 — Etsy digital-subscription sellers

- **Type**: Marketplace sellers (handmade platform misuse)
- **Role**: Unverified reseller leads (AI subscriptions)
- **Status**: Lead (Possible Match–Review)
- **Verified via**: A002
- **Independence**: N/A
- **Guarantee**: Unknown
- **Resale**: Almost certainly NOT authorized by Google (no such program exists publicly) — Suspected unauthorized, needs review
- **Evidence**:
  - [A002] etsy.com — 'Gemini AI 18 Month Pro Plan – 5TB Google One' listing appears in search results (price not captured) (`Lead (search result only)`, Freshness: Unknown)
- **Notes**: AI-subscription gray-market branch for Batch 2

#### ENT-056 — DIFMARK (via smartcdkeys)

- **Type**: Keyshop
- **Role**: Seller / Reseller
- **Status**: Lead (via comparator)
- **Verified via**: A022
- **Independence**: Shared-Origin risk: single comparator
- **Guarantee**: Unknown
- **Resale**: Unclear
- **Evidence**:
  - [A022] smartcdkeys.com — EA App $25 gift card lowest $21.92 at DIFMARK (12% below face) (`Secondary Reported (comparator)`, Freshness: Current)
- **Notes**: EA (not Apple) card — but establishes below-face gift card discount pattern in keyshop segment

#### ENT-057 — ozbargain community (deal-sharing)

- **Type**: Community deal forum
- **Role**: Signal source (not a seller)
- **Status**: Verified-Active (as source)
- **Verified via**: A024
- **Independence**: Independent Origin
- **Guarantee**: N/A
- **Resale**: N/A
- **Evidence**:
  - [A024] ozbargain.com.au (Feb 2025) — Community-documented Spotify Premium Individual 12-month key at US$20.86 (~A$33), Eneba mentioned as seller (`Lead (community deal post)`, Freshness: Stale (Feb 2025))
- **Notes**: Deal signal only — 87% below official annual price; region/method ambiguous; high gray-market risk

### 5.4 Unverified Leads — from project seeds (14 groups, retained in Open-Items Ledger)

> Per §0 and seed policy: presence in this list is NOT proof of commercial relationship, current operation, or legitimacy. All entries require re-verification in future batches.

| ID | Name | Seed Layer | Verification Attempts | Status |
|---|---|---|---|---|
| UL-001 | Mega Center | Direct supplier lead | A034 (Failed — no useful result); A065 (Failed — no results) | Unverified Lead — Retrieval-Limited |
| UL-002 | FazerCards | Direct supplier lead | A036 (indirect — no direct hit, but search yielded vexacard/karteet alternatives) | Unverified Lead — Searched, No Direct Result |
| UL-003 | Nexar | Direct supplier lead | A038 (Failed — no useful result) | Unverified Lead — Retrieval-Limited |
| UL-004 | SMM Asia | SMM provider lead | A044 (indirect); A064 (rate-limited); A070 (rate-limited) | Unverified Lead — Retrieval-Limited |
| UL-005 | Turgame = Definite Play? | Candidate entity-merge hypothesis | A058 (Failed — irrelevant results); A075 (indirect — Turgame active, no Definite Play link) | Unresolved Hypothesis (see H2) |
| UL-006 | Макс111 (on GGSel) | Individual seller lead | — | Unverified Lead — Not Searched (budget) |
| UL-007 | CJS CD Keys | Retailer lead | — | Unverified Lead — Not Searched (budget) |
| UL-008 | Royal CD Keys | Retailer lead | — | Unverified Lead — Not Searched (budget) |
| UL-009 | Gamers Outlet | Retailer lead | — | Unverified Lead — Not Searched (budget) |
| UL-010 | HRK | Marketplace lead | — | Unverified Lead — Not Searched (budget) |
| UL-011 | Wyrel | Marketplace lead | — | Unverified Lead — Not Searched (budget) |
| UL-012 | Driffle | Marketplace lead | A027 (indirect — appears in allkeyshop results for Mortal Shell 2 at €45.46) | Partially Verified (marketplace active via comparator) — offer-level Not Verified |
| UL-013 | PremiumCDkeys / Bcdkey / LicenceHouse / Pixelcodes / Soft... | Keyshop leads | — | Unverified Leads — Not Searched (budget) |
| UL-014 | Bot/Channel/Store leads (28 total): Evolution Era Bot, Ga... | Bot/channel/store leads | A047 (adjacent market check — EDU email market confirmed to exist); A066/A071 (shared-account signal check — rate-limited) | Unverified Leads — Not Directly Searchable (no Telegram access this run) |

## 6. Supply Chain / Upstream Tracing

**Role taxonomy** (not a mandatory sequence): Seller → Reseller → Wholesaler → Distributor → Aggregator → Upstream Supplier → Primary Source.

**Deepest evidence-supportable upstream layer this run**: B2B digital-value API infrastructure (DT One, Reloadly, DingConnect).

| Relationship | Type | Status | Evidence |
|---|---|---|---|
| DT One → PayPal (France airtime) | Infrastructure provider | Documented (dtone.com case study) | A076 |
| DT One → Bitget Wallet (top-ups, 170+ countries) | Infrastructure provider | Documented (press release Mar 2026) | A076 |
| B2B platforms → MENA retailers | Suspected supply chain | **Unresolved Hypothesis (H3)** — zero direct evidence | — |
| Turgame ↔ Definite Play | Candidate entity merge | **Unresolved (H2)** — no evidence either direction | A058/A075 |
| Reloadly (dual seed listing) | Entity resolution | Resolved: single entity, dual role records in seeds | A040 |

**Invariant enforced**: Upstream ≠ Cheapest. No upstream link was inferred from lower price, catalogue similarity, shared branding, or common language (§7).

## 7. Coverage Status by Discovery Family

| Discovery Family | Status | Detail |
|---|---|---|
| Product-first (official anchors) | Verified Findings | 9 of 15 SKU anchors locked with evidence; 4 Retrieval-Limited (Google Play ×4, Free Fire ×4, +2 recovered after retries); 2 N/A (SMM/VN have no official anchor by nature) |
| Price-first (offer discovery) | Verified Findings | 40+ offers captured across 9 SKUs with evidence levels |
| Seller-first (seed re-verification) | Partially Verified | Verified: Al Momaiz, Turgame, PrimeFollows, SMMFollowers, gameseal, Wincdkey, Bitcodes, Keywrld, Keys4us. Retrieval-Limited: Mega Center, FazerCards, Nexar, SMM Asia |
| Marketplace-first | Verified Findings | Eneba, Kinguin, G2A, GAMIVO, GGSel, Plati, Z2U, K4G, itemku, Driffle (partial) |
| B2B/Catalog (API-first) | Verified Findings (entity level) | DT One, Reloadly, DingConnect confirmed as upstream API infrastructure; B2B pricing Retrieval-Limited (account required) |
| Language-first (Arabic) | Verified Findings | 5+ MENA sellers discovered/verified: LikeCard, bitaqaty, snoonu, yallatoys, gml-store, vexacard, karteet, bittopup, cardsouq |
| Language-first (Russian) | Verified Findings | Plati.market, GGSel confirmed via RU sources; RU Steam top-up context documented |
| Community-first | Verified Findings | ozbargain (Spotify deal signal), Reddit (Midasbuy confirmation), LTT forum (key≠license), Trustpilot (Wincdkey) |
| Counter-evidence (adversarial) | Verified Findings | 4 material counter-evidence items: NordVPN resale warning, Microsoft key≠license, bittopup fraud-economics, no-authorized-reseller reports |
| Bot/Channel-first (Telegram) | Not Searched — Tool Limitation | No Telegram platform access this run; 28 bot/channel leads remain Unverified |
| Historical-first | Not Searched — Budget-Limited | Queued Batch 2+ |
| Referral-first | Not Searched — Budget-Limited | Queued Batch 2+ |
| Advertisement-first | Not Searched — Budget-Limited | Queued Batch 2+ |
| Domain/Infrastructure-first | Not Searched — Budget-Limited | Queued Batch 2+ |

**Statuses used** (exclusively): Not Searched · Searched — No Useful Result · Retrieval Failed / Access Unavailable · Budget-Limited · Unresolved · Verified Findings. Retrieval failure is never converted into non-existence.

## 8. Branch Terminal States & Stopping Diagnoses

| Branch | Terminal State | Diagnosis |
|---|---|---|
| BR-OFFICIAL-ANCHORS | Saturated (with 4 Retrieval-Limited residues) | True Saturation for 9 anchors; Retrieval Ceiling for Google Play/Free Fire despite construction switching ×4 |
| BR-MARKETPLACE-GC | Saturated | Structural finding captured (US codes trade above face); multiple marketplaces covered |
| BR-MARKETPLACE-SUB | Retrieval-Limited | Netflix resale channel rate-limited; Spotify anchor recovered on 4th construction |
| BR-MARKETPLACE-AI | Saturated (run scope) | Counter-evidence captured; gray-market deep-dive deferred as scope expansion |
| BR-MARKETPLACE-SW | Saturated | Official + gray range + extreme outliers + legal counter-evidence captured |
| BR-MARKETPLACE-KEY | Retrieval-Limited | Minecraft marketplace prices thin; official anchor solid |
| BR-MARKETPLACE-TOP | Saturated | Richest branch: 8 offers, price dispersion, official channel discount, review-flagged extreme |
| BR-MARKETPLACE-RU | Saturated | Plati/GGSel verified; RU context documented |
| BR-MENA-SEEDS | Partially Saturated | 2/4 seeds verified; language expansion overcompensated with 5+ new entities |
| BR-MENA-TOPUP | Saturated | Real price dispersion found (official $9.99 → $4.99 review-flagged) |
| BR-TOPUP-SEEDS | Retrieval-Limited (Nexar) | Turgame verified with SOLD OUT availability evidence |
| BR-B2B-API | Saturated (entity) / Retrieval-Limited (pricing) | All 3 platforms verified; pricing requires account access |
| BR-B2B-ESIM | Retrieval-Limited | Single garbage result; retail anchor solid via Airalo |
| BR-SMM-SEEDS | Partially Saturated | Market floor captured; quality-terms comparability gap documented |
| BR-VN-SEEDS | Saturated | Market rates from $0.05 captured; SKU identity requirements defined |
| BR-EXCLUSION-SCREEN | Retrieval-Limited | EDU-email market signal confirmed; shared-account check rate-limited ×2 |
| BR-COUNTER-EVIDENCE | Saturated | 4 material counter-evidence items captured and linked to affected SKUs |
| BR-ENTITY-RESOLUTION | Unresolved | Turgame/Definite Play: no evidence either direction; Reloadly dual-listing resolved (single entity, dual seed records) |

**Four-cause diagnostic enforced**: True Saturation / Retrieval Ceiling / Poor Query Strategy / Insufficient Exploration — differentiated per branch before closure. Retrieval-Limited, Budget-Limited, and Scope-Excluded are never labeled "saturated".

## 9. Open Hypotheses & Unresolved Claims

### H1: cardsouq $4.99 PUBG 660 UC is a genuine promo/loss-leader OR uses different delivery terms OR is fraudulent

- **Status**: Unresolved — Review State (not accusation, not ranking)
- **Supporting evidence**:
  - Listing directly observed at $4.99 (original $9.99 crossed out)
  - Seller operates full gift-card store (not a one-off listing)
- **Contradicting evidence**:
  - 50% below official matches the 30-50% band that bittopup's editorial calls 'always fraudulent' economics for gift cards
  - Delivery method (voucher vs ID-login) unverified
- **Next actions**:
  - Direct page retrieval of cardsouq offer terms
  - Delivery-method verification
  - Reputation sweep

### H2: Turgame and Definite Play are the same entity (user seed lists them as 'Turgame / Definite Play')

- **Status**: Unresolved — Entity Resolution open; no merge/split on insufficient evidence
- **Supporting evidence**:
  - Seed grouping suggests prior association
  - Both operate in TR digital market
- **Contradicting evidence**:
  - No web evidence found linking the names (A058 failed, A075 indirect)
- **Next actions**:
  - WHOIS/domain comparison
  - TR-language search
  - social account cross-check

### H3: MENA retail top-up stores (cardsouq, bittopup, bitaqaty, LikeCard...) source inventory from B2B API platforms (DT One, Reloadly, Ding)

- **Status**: Unresolved Hypothesis — plausible chain, zero direct evidence; do NOT treat upstream as established
- **Supporting evidence**:
  - All three B2B platforms operate at scale in exactly these product categories (top-up, gift cards, gaming pins)
  - MENA stores sell identical global SKU inventory
- **Contradicting evidence**:
  - No direct commercial link evidenced for any specific retailer↔platform pair
- **Next actions**:
  - API-documentation cross-reference
  - retailer tech-stack fingerprinting (lawful)
  - B2B account-based price discovery

### H4: Spotify 12-month keys at ~$20.86 are region-arbitrage products (e.g., TR/IN-family plans converted for resale)

- **Status**: Unresolved — Possible Match–Review maintained
- **Supporting evidence**:
  - 87% below US official annual price is structurally impossible for legitimate US-region resale
  - Known gray-market pattern for subscription keys
- **Contradicting evidence**:
  - Offer is Stale (Feb 2025)
  - Seller/method identity not verified
- **Next actions**:
  - Current-day re-check of Eneba Spotify listings
  - region-of-key verification

**Unresolved material claims**:

- Google Play $25 US anchor price (Retrieval-Limited ×4)
- Free Fire 520-diamond official price (Retrieval-Limited ×4)
- ChatGPT Plus official-page direct price (Secondary Reported only)
- All B2B platform pricing (account-gated)
- All Telegram bot/channel leads (platform access unavailable)
- Mega Center / FazerCards / Nexar / SMM Asia current operational status
- cardsouq delivery terms and offer legitimacy
- PrimeFollows / 5SIM / smscode.gg current price lists
- Eneba Steam Wallet 20 USD US-region current price (rate-limited)

## 10. Exclusion / Unauthorized-Activity Screen

Protocol: Signal → Supporting Evidence → Classification → Action. A signal without sufficient evidence remains a review state, never an accusation.

- **Excluded-Confirmed**: None this run (no direct evidence of stolen credentials, OTP bypass, or cracked access captured — honest state)
- **Excluded-Suspected / Needs-Human-Review**: 2 subject groups quarantined from commercial ranking (see below)
- **Not-Excluded with flags**: 2 (Z2U account listings; individual classifieds sellers)

- **SheerID-adjacent bot leads (SheerID_VIP_Bot, SheerID VN)** — Signal: Names + adjacent market evidence (EDU email accounts sold for student-discount verification, helloskip Sep 2026) → `Not-Excluded but flagged — signal without sufficient evidence remains review state` → Quarantined from commercial ranking pending verification
- **Shared-account AI subscriptions (ChatGPT Plus/Crown AI/Gemini GPT Upgrade bot leads)** — Signal: Community reports discounts on such offers are typically unofficial (A023); account-sharing violates publisher ToS → `Not-Excluded — review state` → Excluded from 'legitimate channel' price rankings; retained as gray-market signals

## 11. Budget Summary & Failure/Recovery Log

| Field | Value |
|---|---|
| Complexity class | C4 |
| Total cap | 96 |
| Actions executed | 76 |
| Failures | 17 (no-results: 3, rate-limited: 11, junk-results: 3) |
| Reserve | 24 untouched |
| Per-branch cap | BR-MARKETPLACE-TOP + BR-OFFICIAL-ANCHORS ≈ 30 actions combined — within 35% cap (33.6) |
| Hypothesis minimum rule | H1-H4 each received ≥2 distinct actions where budget permitted; H2 received 2 (A058, A075); H3 received 3 (A039/A063/A069 + A076); satisfied |

**Failure → Recovery log** (§19 — every failure recovered via construction/method/channel switch or honestly terminalized):

| Actions | Subject | Failure | Recovery | Outcome |
|---|---|---|---|---|
| A003→A014→A057→A072 | Spotify anchor | 3 consecutive garbage-result retrievals | Query-construction switching ×3 → 4th construction succeeded (direct spotify.com capture) | Recovered |
| A011→A019→A056 | Windows anchor | 2 failed constructions | Construction change → captured via learn.microsoft + techradar + digitalmaze | Recovered |
| A009→A017 | PUBG anchor | 1 garbage result | How-much construction → games2usd + itemku + Eneba captured | Recovered |
| A061-A064, A066 → A067-A071 → A072-A076 | multiple | Rate-limit 429 cluster (11 actions) | 60s cooldown (failed) → 180s cooldown + construction change → 5/5 recovered | Partially recovered (6 permanently lost: Eneba US Steam detail, Netflix gift card, SMM Asia, shared-account signal, 2 others) |
| A008→A016→A055→A073 | Google Play anchor | 4 constructions, all garbage | Exhausted reasonable constructions within budget | Terminal: Retrieval-Limited (honest) |
| A010→A018→A074 (+A054 denomination mismatch) | Free Fire anchor | 3 constructions garbage + 1 denomination mismatch | N/A within budget | Terminal: Retrieval-Limited (honest); scope-expansion proposal drafted |

## 12. Research Action Log (complete — 76 actions)

| ID | Time (UTC) | Branch | SKU | Discovery Family | Query | Retrieval | Results |
|---|---|---|---|---|---|---|---|
| A001 | 21:04:06 | BR-OFFICIAL-ANCHORS | SKU-AI-001 | Product-first | OpenAI ChatGPT Plus subscription price $20 per month official site | Success | 2 |
| A002 | 21:04:07 | BR-OFFICIAL-ANCHORS | SKU-AI-002 | Product-first | Google Gemini AI Pro plan monthly price official Google One | Success | 6 |
| A003 | 21:04:09 | BR-OFFICIAL-ANCHORS | SKU-SUB-001 | Product-first | Spotify Premium Individual plan price per month official spotify.com | Success | 3 |
| A004 | 21:04:10 | BR-OFFICIAL-ANCHORS | SKU-SUB-002 | Product-first | Netflix Standard plan price per month official netflix.com 2026 | Success | 8 |
| A005 | 21:04:13 | BR-OFFICIAL-ANCHORS | SKU-SUB-003 | Product-first | NordVPN 1 year plan price official nordvpn.com | Success | 5 |
| A006 | 21:04:14 | BR-OFFICIAL-ANCHORS | SKU-GC-001 | Product-first | Steam Wallet $20 gift card digital code store.steampowered.com | Success | 5 |
| A007 | 21:04:16 | BR-OFFICIAL-ANCHORS | SKU-GC-002 | Product-first | Apple App Store iTunes gift card $25 official apple.com price | Success | 1 |
| A008 | 21:04:18 | BR-OFFICIAL-ANCHORS | SKU-GC-003 | Product-first | Google Play gift card $25 official price play.google.com | Success | 6 |
| A009 | 21:04:19 | BR-OFFICIAL-ANCHORS | SKU-TOP-001 | Product-first | PUBG Mobile 660 UC price USD official in-game purchase | Success | 1 |
| A010 | 21:04:20 | BR-OFFICIAL-ANCHORS | SKU-TOP-002 | Product-first | Free Fire 520 diamonds price USD official Garena | Success | 1 |
| A011 | 21:04:22 | BR-OFFICIAL-ANCHORS | SKU-SW-001 | Product-first | Windows 11 Pro license price official Microsoft Store | Success | 3 |
| A012 | 21:04:23 | BR-OFFICIAL-ANCHORS | SKU-KEY-001 | Product-first | Minecraft Java Bedrock Edition PC price official minecraft.net | Success | 2 |
| A013 | 21:04:25 | BR-OFFICIAL-ANCHORS | SKU-ESIM-001 | Product-first | Airalo eSIM 10GB 30 days Europe price USD | Success | 4 |
| A014 | 21:05:11 | BR-OFFICIAL-ANCHORS | SKU-SUB-001 | Product-first | Spotify Premium Individual subscription cost 11.99 month US price | Success | 1 |
| A015 | 21:05:12 | BR-OFFICIAL-ANCHORS | SKU-GC-002 | Product-first | buy Apple iTunes gift card 25 dollars App Store official | Success | 8 |
| A016 | 21:05:13 | BR-OFFICIAL-ANCHORS | SKU-GC-003 | Product-first | Google Play gift card 25 USD buy online Google Store | Success | 4 |
| A017 | 21:05:15 | BR-OFFICIAL-ANCHORS | SKU-TOP-001 | Product-first | how much does 660 UC cost in PUBG Mobile USD | Success | 4 |
| A018 | 21:05:17 | BR-OFFICIAL-ANCHORS | SKU-TOP-002 | Product-first | Free Fire 520 diamonds pack price how much | Success | 4 |
| A019 | 21:05:17 | BR-OFFICIAL-ANCHORS | SKU-SW-001 | Product-first | Windows 11 Pro license 199 USD Microsoft Store buy download | Success | 6 |
| A020 | 21:05:19 | BR-MARKETPLACE-GC | SKU-GC-001 | Marketplace-first | site:eneba.com steam wallet gift card | Success | 1 |
| A021 | 21:05:20 | BR-MARKETPLACE-GC | SKU-GC-001 | Marketplace-first | G2A Kinguin Steam wallet $20 gift card price buy | Success | 3 |
| A022 | 21:05:21 | BR-MARKETPLACE-GC | SKU-GC-002 | Marketplace-first | Eneba G2A iTunes App Store gift card 25 USD price | Success | 8 |
| A023 | 21:05:24 | BR-MARKETPLACE-AI | SKU-AI-001 | Price-first | buy ChatGPT Plus subscription cheap reseller discount price | Success | 5 |
| A024 | 21:05:25 | BR-MARKETPLACE-SUB | SKU-SUB-001 | Price-first | Spotify Premium 12 months key cheap buy Eneba G2A | Success | 7 |
| A025 | 21:05:27 | BR-MARKETPLACE-SUB | SKU-SUB-002 | Price-first | Netflix gift card subscription reseller buy cheap | Success | 1 |
| A026 | 21:05:28 | BR-MARKETPLACE-SW | SKU-SW-001 | Price-first | Windows 11 Pro key cheap $30 kinguin g2a legal OEM | Success | 5 |
| A027 | 21:05:30 | BR-MARKETPLACE-SW | SKU-SW-001 | Seller-first | Wincdkey Bcdkey Windows 11 Pro Office 2021 key price | Success | 8 |
| A028 | 21:05:31 | BR-MARKETPLACE-KEY | SKU-KEY-001 | Marketplace-first | Minecraft Java Bedrock PC key cheap Eneba Kinguin price | Failed | 0 |
| A029 | 21:05:37 | BR-MARKETPLACE-TOP | SKU-TOP-001 | Price-first | PUBG Mobile UC top up cheap price 660 buy online discount | Success | 1 |
| A030 | 21:05:38 | BR-MARKETPLACE-TOP | SKU-TOP-002 | Price-first | Free Fire diamonds top up cheap 520 buy online discount | Success | 3 |
| A031 | 21:05:40 | BR-MARKETPLACE-SUB | SKU-SUB-003 | Price-first | NordVPN 1 year subscription cheap key reseller buy | Success | 6 |
| A032 | 21:05:41 | BR-MARKETPLACE-RU | SKU-GC-001 | Language/market expansion | plati.market купить Steam подарок кошелек код | Success | 4 |
| A033 | 21:05:43 | BR-MARKETPLACE-AI | SKU-AI-002 | Price-first | Gemini AI Pro subscription cheap reseller 18 month plan buy | Success | 2 |
| A034 | 21:06:06 | BR-MENA-SEEDS | SKU-GC-001 | Seller-first | Mega Center store Saudi Arabia gift cards games digital store | Success | 3 |
| A035 | 21:06:07 | BR-MENA-SEEDS | SKU-GC-002 | Seller-first | المميز كارد Al Momaiz Card متجر بطاقات شحن رقمية | Success | 8 |
| A036 | 21:06:10 | BR-MENA-SEEDS | SKU-GC-001 | Seller-first | FazerCards متجر بطاقات رقمية | Success | 2 |
| A037 | 21:06:12 | BR-TOPUP-SEEDS | SKU-TOP-001 | Seller-first | Turgame PUBG Mobile 660 UC top up price | Success | 2 |
| A038 | 21:06:14 | BR-TOPUP-SEEDS | SKU-TOP-001 | Seller-first | Nexar store digital games top up PUBG UC | Success | 3 |
| A039 | 21:06:15 | BR-B2B-API | SKU-TOP-001 | B2B/Catalog | DT One API top up gift card pricing B2B distributor | Success | 3 |
| A040 | 21:06:17 | BR-B2B-API | SKU-TOP-001 | B2B/Catalog | Reloadly API pricing top up gift cards wholesale | Success | 8 |
| A041 | 21:06:18 | BR-B2B-API | SKU-TOP-001 | B2B/Catalog | Ding Connect top up API pricing resellers | Success | 5 |
| A042 | 21:06:19 | BR-SMM-SEEDS | SKU-SMM-001 | Seller-first | PrimeFollows buy Instagram followers 1000 price | Success | 8 |
| A043 | 21:06:25 | BR-SMM-SEEDS | SKU-SMM-001 | Seller-first | SMMFollowers buy Instagram followers cheap price | Success | 7 |
| A044 | 21:06:26 | BR-SMM-SEEDS | SKU-SMM-001 | Seller-first | SMM Asia panel Instagram followers price | Success | 8 |
| A045 | 21:06:28 | BR-VN-SEEDS | SKU-VN-001 | Price-first | buy virtual number SMS verification online price cheap | Success | 5 |
| A046 | 21:06:29 | BR-B2B-ESIM | SKU-ESIM-001 | B2B/Catalog | eSIM API wholesale B2B provider distributor pricing | Success | 1 |
| A047 | 21:06:30 | BR-EXCLUSION-SCREEN | — | Community/Bot-channel | SheerID student verification discount bots Telegram abuse | Success | 6 |
| A048 | 21:06:31 | BR-MARKETPLACE-RU | SKU-GC-001 | Marketplace-first | GGSel marketplace digital goods gift cards | Success | 3 |
| A049 | 21:06:33 | BR-MARKETPLACE-GC | SKU-GC-001 | Marketplace-first | Z2U gift cards Steam wallet subscription accounts buy | Success | 8 |
| A050 | 21:06:38 | BR-MENA-TOPUP | SKU-TOP-001 | Language-first | شحن شدات ببجي 660 رخيص سعر | Success | 4 |
| A051 | 21:06:41 | BR-MENA-GC | SKU-GC-002 | Language-first | بطاقة ايتونز 25 دولار شراء سعر | Success | 8 |
| A052 | 21:06:43 | BR-MARKETPLACE-KEY | SKU-KEY-001 | Marketplace-first | Minecraft Java Bedrock Edition PC CD key price comparison cheap | Success | 1 |
| A053 | 21:07:50 | BR-OFFICIAL-ANCHORS | SKU-KEY-001 | Product-first | Minecraft Java and Bedrock Edition 29.99 PC Windows price | Success | 3 |
| A054 | 21:07:52 | BR-OFFICIAL-ANCHORS | SKU-TOP-002 | Product-first | Free Fire diamond top up prices list USD Garena official store | Success | 8 |
| A055 | 21:07:55 | BR-OFFICIAL-ANCHORS | SKU-GC-003 | Product-first | Google Play gift card 25 dollar Best Buy Amazon Walmart price | Success | 5 |
| A056 | 21:07:57 | BR-OFFICIAL-ANCHORS | SKU-SW-001 | Product-first | Windows 11 Pro full version price 199.99 buy from Microsoft | Success | 8 |
| A057 | 21:07:59 | BR-OFFICIAL-ANCHORS | SKU-SUB-001 | Product-first | Spotify Premium price increase individual plan monthly how much now | Success | 1 |
| A058 | 21:08:00 | BR-ENTITY-RESOLUTION | — | Domain/Entity-first | Turgame Definite Play same company Turkey game store | Success | 5 |
| A059 | 21:08:01 | BR-COUNTER-EVIDENCE | SKU-TOP-001 | Counter-evidence | cardsouq.com PUBG top up review legit safe | Success | 8 |
| A060 | 21:08:04 | BR-COUNTER-EVIDENCE | SKU-TOP-001 | Counter-evidence | bittopup.com PUBG UC review legit safe | Success | 1 |
| A061 | 21:08:06 | BR-MARKETPLACE-GC | SKU-GC-001 | Marketplace-first | eneba.com Steam Wallet Gift Card 20 USD United States | Failed | 0 |
| A062 | 21:08:06 | BR-MARKETPLACE-SUB | SKU-SUB-002 | Marketplace-first | Netflix gift card buy digital online US price | Failed | 0 |
| A063 | 21:08:06 | BR-B2B-API | SKU-TOP-001 | B2B/Catalog | DTO2 DT One digital content API gift cards games distributor | Failed | 0 |
| A064 | 21:08:06 | BR-SMM-SEEDS | SKU-SMM-001 | Seller-first | smmasia.com SMM panel services price | Failed | 0 |
| A065 | 21:08:06 | BR-MENA-SEEDS | — | Language-first | ميغا سنتر متجر بطاقات شحن رقمية العاب | Failed | 0 |
| A066 | 21:08:06 | BR-EXCLUSION-SCREEN | SKU-AI-001 | Community/Forum-first | cheap ChatGPT Plus account shared subscription buy against terms | Failed | 0 |
| A067 | 21:09:39 | BR-MARKETPLACE-GC | SKU-GC-001 | Marketplace-first | Steam Wallet Gift Card 20 USD United States Eneba price | Failed | 0 |
| A068 | 21:09:39 | BR-MARKETPLACE-SUB | SKU-SUB-002 | Marketplace-first | Netflix gift card digital where to buy US streaming | Failed | 0 |
| A069 | 21:09:39 | BR-B2B-API | SKU-TOP-001 | B2B/Catalog | DT One digital gifts API games publisher distributor brand | Failed | 0 |
| A070 | 21:09:39 | BR-SMM-SEEDS | SKU-SMM-001 | Seller-first | SMM Asia cheap smm panel instagram followers | Failed | 0 |
| A071 | 21:09:39 | BR-EXCLUSION-SCREEN | SKU-AI-001 | Community/Forum-first | buy cheap ChatGPT Plus shared account telegram resale | Failed | 0 |
| A072 | 21:13:05 | BR-OFFICIAL-ANCHORS | SKU-SUB-001 | Product-first | Spotify Premium individual plan monthly price 2026 | Success | 7 |
| A073 | 21:13:06 | BR-OFFICIAL-ANCHORS | SKU-GC-003 | Product-first | Google Play gift card $25 price buy | Success | 2 |
| A074 | 21:13:08 | BR-OFFICIAL-ANCHORS | SKU-TOP-002 | Product-first | Free Fire 520 diamonds $4.99 top up | Success | 4 |
| A075 | 21:13:09 | BR-ENTITY-RESOLUTION | — | Domain/Entity-first | "Definite Play" turgame Turkish digital games platform | Success | 5 |
| A076 | 21:13:10 | BR-B2B-API | SKU-TOP-001 | B2B/Catalog | DT One dtone.com mobile top up gift card API platform | Success | 4 |

## 13. Audit Record (§23)

**What was established**:
- 9 of 15 Batch-1 SKU official anchors locked with graded evidence
- 40+ offers captured across 9 SKUs with per-offer verification dimensions
- Structural market findings: (1) US-region Steam codes trade ABOVE face on gray market; (2) MENA gift-card stores sell US cards at ≈face; (3) PUBG UC shows real price dispersion with an official-channel discount option; (4) software keyshop floor is coupon-conditional €0.46-1.03; (5) B2B upstream layer (DT One/Reloadly/Ding) verified as infrastructure powering retail top-up globally
- 4 publisher/counter-evidence items documented (NordVPN resale restriction, Microsoft key≠license, fraud-economics band, no-authorized-reseller reports)
- 57 entities total: 45 verified-active/lead + 12 unverified-lead groups (from 73 seeds)
- Entity resolution: Reloadly dual-seed-listing resolved; Turgame/Definite Play remains open

**What remains unresolved**: See unresolved_claims (9 items) + open_hypotheses (H1-H4)

**What was inaccessible**:
- Telegram bot/channel verification (platform access unavailable)
- B2B platform pricing (account-gated)
- cardsouq/Eneba offer detail pages (rate-limit window)
- 4 SKU anchors despite construction switching (Google Play, Free Fire)

**What was excluded and why**: Nothing Excluded-Confirmed; 2 subject groups quarantined to review state (SheerID-adjacent leads, shared-account subscriptions) — signals without sufficient evidence remain review states, never accusations

**Which conclusions survived counter-evidence**:
- Official anchors (all counter-checked against at least 2 sources or direct retrieval)
- US Steam code premium finding (3 independent origins: gg.deals, Kinguin listing, G2A listing)
- PUBG official-channel discount legitimacy (Midasbuy = publisher-official, Reddit-corroborated)

**Why research stopped**: Batch 1 operational completeness: all 15 SKU branches reached terminal states (Saturated/Retrieval-Limited), coverage obligations seeded and executed, counter-evidence pass done, remaining budget intentionally reserved for program continuation. Stop is Batch-scoped, not program-scoped.

**Important routes not searched**:
- Telegram channel discovery
- Historical/archive lookups
- Referral-chain tracing
- Advertisement-network discovery
- Infrastructure fingerprinting
- B2B account-based pricing

**What could materially change current conclusions**:
- cardsouq offer verification could move $4.99 from review to verified-lowest (or to excluded)
- Direct retrieval of Eneba US Steam pricing could close the US-code premium gap
- B2B account access would open the true upstream price layer (could restructure MENA retailer relationship graph)
- Telegram access could promote/quarantine 28 bot leads
- Free Fire/Google Play anchor capture would complete Batch-1 SKU set

**Tool limitations affecting completeness**:
- Search-only evidence base (snippet-level) for most offers — §4.1 constraint honestly applied: offers marked Advertised/Secondary where page-level retrieval failed
- Rate-limiting consumed 11 actions (14% of budget)
- Recurring junk-result pattern (scribd 'Zoberetimifid' artifact) polluted ~6 queries
- No transaction capability by design (§5.1 Not Performed)

**Transaction Verification**: Not Performed (all offers) — No purchases, account access, or transaction tests were performed this run. All prices are listing-level evidence (First-Party Reported / Secondary Reported / Advertised / Lead). No offer carries transaction-verified status.

---

*Dataset completeness: 15 SKUs executed / 400+ program scope · 52 verified entities + 14 unverified lead groups · 52 offers · 76 research actions logged · Last Checked: 2026-09-26 21:21 UTC. Continued batches will extend this dataset under the same run contract.*