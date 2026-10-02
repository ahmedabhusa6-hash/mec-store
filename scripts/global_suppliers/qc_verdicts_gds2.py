#!/usr/bin/env python3
# GDS-2: Append manual QC verdicts (documented reasons) to qc_rejects.json, then rebuild.
import json

GS = '/home/z/my-project/research/global_suppliers'

# (domain, reason) — every reject documented; verdicts from manual page inspection 2026-09-29
VERDICTS = [
    # automation / dev tools / wrong vertical (qualified by incidental signal words)
    ('activepieces.com', 'workflow automation tool — not a goods distributor'),
    ('api.market', 'AI/data API marketplace — wrong vertical (not digital goods)'),
    ('coingate.com', 'crypto payment gateway — money movement, not goods distribution'),
    ('gamblingcommission.gov.uk', 'UK government regulator site — not a business entity in scope'),
    ('hevodata.com', 'data pipeline SaaS — not goods distribution'),
    ('integrately.com', 'app automation SaaS — not goods distribution'),
    ('latenode.com', 'workflow automation SaaS — not goods distribution'),
    ('mcp.composio.dev', 'MCP/dev integration toolkit — not goods distribution'),
    ('raycast.com', 'desktop launcher app — not goods distribution'),
    ('smithery.ai', 'MCP server directory — not goods distribution'),
    ('syncgtm.com', 'GTM/marketing orchestration SaaS — not goods distribution'),
    ('pabbly.com', 'marketing/sales SaaS — not goods distribution'),
    ('vouchermatic.app', 'voucher campaign marketing tool — not goods distribution'),
    ('shi.com', 'enterprise IT reseller; page Cloudflare-blocked, soft categories only, unverifiable'),
    # iGaming / casino software (not digital goods for resale)
    ('softswiss.com', 'iGaming/casino software provider — not digital goods distribution'),
    ('sologe.net', 'iGaming B2B marketplace — not digital goods distribution'),
    ('tecpinion.com', 'casino/sweepstakes software — not digital goods distribution'),
    # SEO/content/ directory artifacts
    ('trakkr.ai', 'AI visibility/SEO platform — Streaming category false positive'),
    ('website.informer.com', 'web stats directory — not a supplier'),
    # physical goods wholesalers
    ('wholesaleclearance.co.uk', 'physical liquidation/bankrupt stock wholesaler — not digital'),
    ('wigmorewholesale.com', 'physical goods wholesaler — not digital'),
    ('gemwholesale.co.uk', 'physical surplus wholesaler — not digital'),
    # marketplace-only (per marketplace rule) / commerce enablement
    ('whop.com', 'digital products marketplace operator — MARKETPLACE_ONLY per rule'),
    ('adivaha.com', 'white-label travel booking platform — wrong vertical (travel)'),
    ('porsa.io', 'commerce storefront SaaS for digital sellers — enablement tool, not distributor'),
    ('spxcommerce.com', 'enterprise e-commerce platform software — not goods distribution'),
]

qc = json.load(open(f'{GS}/entities/qc_rejects.json'))
added = 0
for dom, why in VERDICTS:
    if dom not in qc:
        qc[dom] = why; added += 1
json.dump(qc, open(f'{GS}/entities/qc_rejects.json','w'), ensure_ascii=False, indent=1)
print(f'QC rejects: +{added} added | cumulative: {len(qc)}')
