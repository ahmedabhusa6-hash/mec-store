#!/usr/bin/env python3
# GDS-1: Apply manual QC verdicts (evidence-based, documented)
import json
GS = '/home/z/my-project/research/global_suppliers'

# Manual verdicts after reviewing suspects + page titles/domains (2026-09-29 run)
REJECT = {
    'a-pay.one':'payments gateway (money movement, not goods distribution)',
    'apmultimedianewsroom.com':'media newsroom content',
    'avanta.info':'B2B commerce platform, no digital-goods evidence',
    'bbusiness.online':'blog/content site',
    'bit2me.com':'crypto exchange',
    'checkthat.ai':'AI tool, not distribution',
    'cloudeagle.ai':'SaaS management tool',
    'conduitdigital.us':'marketing agency',
    'currentasia.com':'marketing agency',
    'digimarconwakefield.co.uk':'marketing conference',
    'digitalagencynetwork.com':'agency network directory',
    'digitalheroesco.com':'dev agency',
    'expressdigitals.com':'web services',
    'gartner.com':'research firm',
    'helloduty.com':'CRM/dialer tool',
    'innoloft.com':'industrial B2B innovation platform',
    'inyad.com':'fintech, insufficient digital-goods evidence',
    'lynon.com':'iGaming casino software (out of scope)',
    'prnewswire.co.uk':'press release distribution',
    'revshare.so':'attribution tool',
    'sdk.finance':'white-label payment platform',
    'toriihq.com':'SaaS management tool',
    'worldradiohistory.com':'content archive',
    'zimpler.com':'payments (A2A)',
}
KEEP_WITH_NOTE = {
    'coingate.com':('Reseller Platform','B2C gift-cards-for-crypto store; crypto payments secondary', 'HIGH'),
    'gifq.com':('API/Distribution Platform','gift-card/prepaid payouts API (Tremendous-class)', 'HIGH'),
    'interswitchgroup.com':('API/Distribution Platform','payments infra + airtime/voucher distribution (Quickteller)', 'MEDIUM'),
    'recharge.com':('Reseller Platform','consumer digital goods store (top-ups+gift cards), global', 'HIGH'),
    'api.market':('Marketplace','API marketplace (digital services/API subscriptions resale)', 'MEDIUM'),
    'vouchermatic.app':('White-Label Platform','voucher management/distribution system', 'HIGH'),
    'shi.com':('Distributor/Wholesaler','enterprise software reseller (bot-blocked page; snippet evidence only)', 'MEDIUM'),
    'runa.io':('API/Distribution Platform','gift card + prepaid payout distribution infrastructure (Tremendous-class)', 'HIGH'),
}
# extra rejects found in manual scan of full list
EXTRA_REJECT = {
    'revenuebase.ai':'B2B leads/data company, not goods distribution',
    'ft.com':'news publisher (bot-blocked, category from noise)',
    'capgemini.com':'IT consulting',
    'databridgemarketresearch.com':'market research firm',
    'eternitylaw.com':'law firm',
    'cdn.prod.website-files.com':'CDN artifact, not an entity',
    'accio.com':'AI sourcing tool',
    'alconost.com':'localization agency',
    'amasty.com':'single-brand plugin vendor/dev company',
    'attackshark.ca':'physical gaming keyboards',
    'bookingkit.com':'booking SaaS for attractions',
    'bizasean.com':'business directory',
    'graphy.com':'creator course platform',
    'indelec.com':'lightning protection (physical)',
    'checkout.com':'payments processor',
    'dlocal.com':'payments infrastructure',
    'stripe.com':'payments processor',
    'finhive.africa':'fintech infrastructure',
    'payonus.com':'payments infrastructure',
    'pxp.io':'payments platform',
    'grafit.agency':'agency',
    'rdegges.com':'personal blog',
    'softanics.com':'software dev vendor (single-brand)',
    'tec-it.com':'barcode software vendor (single-brand)',
}
KEEP_WITH_NOTE.update({
    'armoiri.es':('Distributor/Wholesaler','Indonesian pulsa/PPOB distributor on .es domain (anomaly noted)', 'MEDIUM'),
    'bondplusonline.co.za':('Distributor/Wholesaler','Indonesian pulsa distributor on .co.za domain (anomaly noted)', 'MEDIUM'),
    'cardexpresseg.com':('Distributor/Wholesaler','Egyptian digital gift-card distributor (MENA)', 'HIGH'),
    'cards.salla.com':('White-Label Platform','Salla merchant digital gift-card program (Saudi Arabia)', 'HIGH'),
    'fmpedia.id':('Distributor/Wholesaler','Indonesian topup/voucher distributor (bot-blocked, snippet evidence)', 'MEDIUM'),
    'gamesdrop.io':('Reseller Platform','game top-up + gift card store', 'HIGH'),
    'topupdaddy.com':('Reseller Platform','top-up store (bot-blocked, snippet evidence)', 'MEDIUM'),
})

def main():
    ents = json.load(open(f'{GS}/entities/qualified.json'))
    # persistent cumulative reject registry (survives qualify --rebuild)
    try: persistent = json.load(open(f'{GS}/entities/qc_rejects.json'))
    except Exception: persistent = {}
    all_rejects = {**REJECT, **EXTRA_REJECT}
    for d, r in all_rejects.items(): persistent[d] = r
    json.dump(persistent, open(f'{GS}/entities/qc_rejects.json','w'), ensure_ascii=False, indent=1)
    out, rejected = [], []
    for e in ents:
        d = e['Official_Domain']
        if d in all_rejects or d in EXTRA_REJECT:
            rejected.append({'Entity_ID': e['Entity_ID'], 'domain': d,
                             'reason': all_rejects.get(d) or EXTRA_REJECT.get(d),
                             'action': 'REJECTED (QC false-positive)'})
            continue
        if d in KEEP_WITH_NOTE:
            t, note, conf = KEEP_WITH_NOTE[d]
            e['Entity_Type'] = t; e['Notes'] = (e.get('Notes','') + f"; QC: {note}").strip('; ')
            e['Confidence'] = conf
        out.append(e)
    # renumber IDs sequentially (stable, deterministic)
    for i, e in enumerate(out, 1):
        e['Entity_ID'] = f'GDS-{i:04d}'
    json.dump(out, open(f'{GS}/entities/qualified.json','w'), ensure_ascii=False, indent=1)
    try:
        nq = json.load(open(f'{GS}/entities/non_qualified.json'))
        nq['rejected'] += rejected
    except Exception:
        nq = {'rejected': rejected, 'insufficient': []}
    json.dump(nq, open(f'{GS}/entities/non_qualified.json','w'), ensure_ascii=False, indent=1)
    print(f"QC applied: kept {len(out)} | rejected {len(rejected)}")
    for r in rejected: print(f"  REJECT {r['domain']:32} {r['reason'][:50]}")

if __name__ == '__main__':
    main()
