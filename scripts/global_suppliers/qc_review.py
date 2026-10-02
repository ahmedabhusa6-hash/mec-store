#!/usr/bin/env python3
# GDS-1: QC review — surface suspect entities for manual verdict (false-positive patterns)
import json, re, sys
GS = '/home/z/my-project/research/global_suppliers'

CORE_CATS = {'Gift_Cards','Game_Keys','Topups','eSIM','Airtime','Vouchers','Prepaid','InGame_Currency','Streaming','Digital_Goods_General','Wallets','Mobile_Services','Gaming_General'}
SOFT_CATS = {'Subscriptions','SaaS_Products','Software_Licenses','Pins'}

SUSPECT_PATTERNS = [
    (r'radio|archive|history|library|museum|genealogy', 'content archive/media (non-commerce)'),
    (r'payment|payin|payout|acquir|issuing|banking|neobank|card issuing', 'fintech/payments (money movement, not goods distribution)'),
    (r'\bsaas (management|platform|procurement|spend)|saas discovery|license management|it asset', 'SaaS-management tool (not a goods distributor)'),
    (r'marketing|seo agency|advertis|affiliate network|crm|helpdesk|email marketing', 'marketing/agency tool'),
    (r'medical|pharma|clinic|dental|lab equipment|surgical', 'physical medical goods'),
    (r'logistics|freight|shipping|cargo|3pl', 'logistics services'),
    (r'\bcourse\b|academy|elearning|training|certification', 'education provider'),
    (r'hosting|cloud vps|dedicated server|domain registrar|ssl certificate', 'web infrastructure'),
    (r'recruit|hr platform|hiring|payroll', 'HR/recruitment'),
    (r'furniture|apparel|textile|machinery|spare parts|electronics manufacturer', 'physical goods'),
    (r'news|weekly|daily|times\b|magazine|press release|newswire|journal(?!.*card)', 'news/media outlet'),
    (r'\bjobs?\b|careers|vacanc|hiring board', 'job board'),
    (r'expo|conference|summit|trade show|webinar series', 'event/trade show'),
    (r'price tracker|compare (prices|top.?up)|price comparison|deals? tracker', 'price comparison / tracker (discovery source)'),
    (r'smm (panel|service)|social media (panel|marketing service)|instagram (followers|likes)', 'SMM panel (social media metrics)'),
    (r'vpn|proxy service|private browsing', 'VPN/proxy service'),
    (r'chargeback|fraud prevention|risk scor', 'chargeback/fraud SaaS'),
    (r'accounting|invoice software|bookkeeping|erp\b|payroll software', 'business ops software'),
    (r'video (generator|summarizer|hosting)|image generator|ai writer|content writer', 'AI content tool'),
    (r'project management|work platform|workflow automation|task manage', 'productivity/work SaaS'),
]

def main():
    ents = json.load(open(f'{GS}/entities/qualified.json'))
    suspects = []
    for e in ents:
        blob = f"{e['Canonical_Name']} {e.get('Brand_Name','')} {e['Official_Domain']} {' '.join(e['Digital_Categories'])} " + \
               ' '.join(str(x.get('title','')) for x in e.get('Evidence_Official',[])[:2]).lower()
        reasons = []
        for pat, why in SUSPECT_PATTERNS:
            if re.search(pat, blob, re.I): reasons.append(why)
        core = [c for c in e['Digital_Categories'] if c in CORE_CATS]
        soft_only = (not core) and bool([c for c in e['Digital_Categories'] if c in SOFT_CATS])
        if soft_only: reasons.append('soft categories only (subscriptions/software words can be incidental)')
        if reasons:
            suspects.append({'Entity_ID': e['Entity_ID'], 'domain': e['Official_Domain'],
                             'title': e['Canonical_Name'][:60], 'conf': e['Confidence'],
                             'cats': e['Digital_Categories'], 'reasons': sorted(set(reasons))})
    print(f"Suspects: {len(suspects)} / {len(ents)}")
    for s in suspects:
        print(f"  {s['Entity_ID']} {s['domain'][:36]:38} {s['title'][:40]:42} {s['conf'][:6]:7} {s['reasons'][0][:46]}")
    json.dump(suspects, open(f'{GS}/entities/qc_suspects.json','w'), ensure_ascii=False, indent=1)
    print(f"\nSaved -> entities/qc_suspects.json ({len(suspects)})")

if __name__ == '__main__':
    main()
