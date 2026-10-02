#!/usr/bin/env python3
# GDS-1: Process raw search results -> candidate entities (dedup vs KNOWN + internal, signal classification)
import json, os, re, sys
from urllib.parse import urlparse
from collections import defaultdict

GS = '/home/z/my-project/research/global_suppliers'

# --- Load known entities ---
K = json.load(open(f'{GS}/known_entities.json'))
K_INDEX = K['match_index']
K_DOMAINS = {r['domain'] for r in K['entities'] if r['domain']}
K_NAMES = set(K_INDEX.keys())

# Skip domains: search engines / news / docs / social / directories that are discovery infrastructure
SKIP_HOSTS = {
    'google.com','youtube.com','facebook.com','instagram.com','twitter.com','x.com','tiktok.com',
    'linkedin.com','reddit.com','quora.com','wikipedia.org','medium.com','github.com','stackoverflow.com',
    'yandex.com','bing.com','duckduckgo.com','yahoo.com','amazon.com','apple.com','play.google.com',
    'apps.apple.com','g2.com','capterra.com','trustpilot.com','sitejabber.com','glassdoor.com',
    'crunchbase.com','bloomberg.com','forbes.com','techcrunch.com','reuters.com','prnewswire.com',
    'businesswire.com','globenewswire.com','digitaljournal.com','menafn.com','albawaba.com',
    'linkedin.co','indeed.com','jobtome.com','glassdoor','upwork.com','fiverr.com','shutterstock.com',
    'pinterest.com','telegram.me','t.me','whatsapp.com','blogspot.com','wordpress.com','substack.com',
    'clutch.co','goodfirms.co','semrush.com','ahrefs.com','moz.com','similarweb.com','builtwith.com',
    'docs.google.com','support.google.com','maps.google.com','support.microsoft.com','learn.microsoft.com',
    'azure.com','aws.amazon.com','cloud.google.com','msn.com','news.google.com','webflow.io','wix.com',
    'squarespace.com','shopify.com','woocommerce.com','npmjs.com','pypi.org','hubspot.com','salesforce.com',
    'marketplace.visualstudio.com','chrome.google.com','addons.mozilla.org','zendesk.com','intercom.com',
    'notion.site','wikipedia.org','wikimedia.org','fandom.com','investopedia.com','techopedia.com',
    'scribd.com','mail-archive.com','lists.jboss.org','archive.org','slideshare.net','researchgate.net',
    'academia.edu','ieee.org','springer.com','sciencedirect.com','semanticscholar.org','papers.ssrn.com',
    'issuu.com','docplayer.net','coursehero.com','chegg.com','studocu.com','scribd',
}

B2B_SIGNALS = {
    'api':'API', 'rest api':'API', 'api integration':'API', 'api provider':'API', 'api platform':'API',
    'webhook':'Webhook', 'h2h':'H2H', 's2s':'S2S', 'white label':'White_Label', 'white-label':'White_Label',
    'wholesale':'Wholesale', 'wholesaler':'Wholesale', 'bulk':'Wholesale', 'b2b':'B2B', 'b2b2c':'B2B',
    'distributor':'Distributor', 'distribution':'Distributor', 'distributeur':'Distributor', 'distribuidor':'Distributor',
    'distribución':'Distributor', 'дистрибьютор':'Distributor',
    'reseller':'Reseller', 'resellers':'Reseller', 'revendedor':'Reseller', 'partnership':'Reseller',
    'partner program':'Reseller', 'partner api':'Reseller', 'affiliate program':'Reseller',
    'fulfillment':'Automated_Fulfillment', 'automated delivery':'Automated_Fulfillment', 'instant delivery':'Automated_Fulfillment',
    'dealer':'Reseller', 'bayilik':'Reseller', 'agents':'Reseller', 'agency':'Reseller',
    'merchant':'Merchant_Infra', 'for business':'B2B', 'for businesses':'B2B', 'enterprise':'B2B',
    'trade platform':'B2B', 'trading platform':'B2B', 'portal':'Reseller',
    'grosir':'Wholesale', 'en gros':'Wholesale', 'en-gros':'Wholesale', 'mayoreo':'Wholesale', 'mayorista':'Wholesale',
    'atacado':'Wholesale', 'hurtownik':'Wholesale', 'opět':'Wholesale', 'гуртом':'Wholesale', 'опт':'Wholesale',
    'toptan':'Wholesale', 'جملة':'Wholesale', 'بالجملة':'Wholesale', 'وكلاء':'Reseller',
    'aggregator':'Aggregator', 'super aggregator':'Aggregator',
}
CATEGORY_SIGNALS = {
    'gift card':'Gift_Cards', 'gift cards':'Gift_Cards', 'giftcard':'Gift_Cards', 'gift cards':'Gift_Cards',
    'carte cadeau':'Gift_Cards', 'tarjetas de regalo':'Gift_Cards', 'بطاقات هدايا':'Gift_Cards', 'كروت هدايا':'Gift_Cards',
    'hediye kart':'Gift_Cards', 'gaming voucher':'Gift_Cards', 'game card':'Gift_Cards',
    'game key':'Game_Keys', 'game keys':'Game_Keys', 'cd key':'Game_Keys', 'cdkeys':'Game_Keys',
    'game code':'Game_Keys', 'top-up':'Topups', 'top up':'Topups', 'topup':'Topups', 'top-ups':'Topups',
    'recarga':'Topups', 'recargas':'Topups', 'recharge':'Topups', 'recarga de jogos':'Topups',
    'yükleme':'Topups', 'doładowanie':'Topups', 'пополнен':'Topups', 'nap game':'Topups', 'nạp game':'Topups',
    '充值':'Topups', 'top up game':'Topups', 'in-game':'InGame_Currency', 'game credit':'InGame_Currency',
    'game credits':'InGame_Currency', 'diamonds':'InGame_Currency', 'uc':'InGame_Currency', 'v-bucks':'InGame_Currency',
    'subscription':'Subscriptions', 'subscriptions':'Subscriptions', 'subscrição':'Subscriptions',
    'suscripción':'Subscriptions', 'اشتراكات':'Subscriptions', 'اشتراك':'Subscriptions',
    'esim':'eSIM', 'e-sim':'eSIM', 'airtime':'Airtime', 'recharge api':'Airtime', 'mobile recharge':'Airtime',
    'voucher':'Vouchers', 'vouchers':'Vouchers', 'voucher digital':'Vouchers', 'pin':'Pins',
    'prepaid':'Prepaid', '_prepaid':'Prepaid', 'cartão virtual':'Prepaid', 'streaming':'Streaming',
    'software license':'Software_Licenses', 'licensing':'Software_Licenses', 'saas':'SaaS_Products',
    'digital goods':'Digital_Goods_General', 'digital products':'Digital_Goods_General',
    'digital content':'Digital_Goods_General', 'produk digital':'Digital_Goods_General',
    'dijital ürün':'Digital_Goods_General', 'منتجات رقمية':'Digital_Goods_General', 'بطاقات رقمية':'Digital_Goods_General',
    'كروت شحن':'Topups', 'digital gift':'Gift_Cards', 'gaming':'Gaming_General', 'gamer':'Gaming_General',
    'ott':'Streaming', 'mobility':'Mobile_Services', 'wallet':'Wallets',
}

def host_of(url):
    try:
        h = urlparse(url).hostname or ''
        return h.lower().replace('www.','')
    except: return ''

def norm_name(title):
    t = re.sub(r'\s*[\|\-–—:·»«]\s*.*$', '', title or '')  # cut after first separator
    t = re.sub(r'\(.*?\)', '', t)
    return t.strip()[:70]

def find_signals(text):
    tl = ' ' + (text or '').lower() + ' '
    b2b, cats = set(), set()
    for sig, label in B2B_SIGNALS.items():
        if (' ' + sig + ' ') in tl or tl.strip().startswith(sig):
            b2b.add(label)
    for sig, label in CATEGORY_SIGNALS.items():
        if (' ' + sig + ' ') in tl or tl.strip().startswith(sig):
            cats.add(label)
    return b2b, cats

def main():
    candidates = {}   # domain -> record
    dup_known, marketplace_only, discovery_sources, filtered_physical = [], [], [], []
    raws = sorted(os.listdir(f'{GS}/raw'))
    for rf in raws:
        if not rf.endswith('.json'): continue
        d = json.load(open(f'{GS}/raw/{rf}'))
        for r in d.get('results', []):
            host = r.get('host') or host_of(r.get('url',''))
            if not host or host in SKIP_HOSTS: continue
            if any(host.endswith('.'+s) for s in SKIP_HOSTS): continue
            title, snip = r.get('name',''), r.get('snippet','')
            text = f"{title} {snip}"
            b2b, cats = find_signals(text)
            # discovery sources: comparison/news/affiliate lists — still harvested for links, not qualified
            if re.search(r'(best |top )?\d+\s+(best|top)?\s*(gift card|digital|gaming|top.?up).*(sites|platforms|companies|providers)', text, re.I):
                discovery_sources.append({'host': host, 'title': title[:80], 'from_query': d['query']})
                # do NOT skip — list articles' own domains can still be qualified if they run APIs
            # PAGE-FIRST strategy: keep ALL non-junk domains as candidates; page verification decides
            # known entity?
            base = host
            kn = K_DOMAINS.intersection({base}) or {k for k in K_NAMES if k in text.lower()}
            dom_known = next((kdom for kdom in K_DOMAINS if base == kdom or base.endswith('.'+kdom)), None)
            name_known = None
            for kname in K_NAMES:
                if kname and kname in text.lower() and len(kname) > 3:
                    rec = K_INDEX[kname]
                    if rec['layer'] == 'ENTITY': name_known = kname; break
            if dom_known or name_known:
                dup_known.append({'host': host, 'matched': dom_known or name_known, 'from_query': d['query']})
                continue
            rec = candidates.setdefault(host, {
                'domain': host,
                'names': set(),
                'b2b_signals': set(),
                'category_signals': set(),
                'evidence': [],      # (query, url, title, snippet, official_domain_or_not)
                'query_regions': set(),
                'corroboration': set(),  # distinct query ids
            })
            rec['names'].add(norm_name(title))
            rec['b2b_signals'] |= b2b
            rec['category_signals'] |= cats
            rec['query_regions'].add(d['region'])
            rec['corroboration'].add(d['qid'])
            rec['evidence'].append({
                'query': d['query'], 'url': r.get('url',''), 'title': title[:120],
                'snippet': snip[:250], 'in_results_of_own_domain': True
            })

    # finalize
    out = []
    for host, rec in candidates.items():
        official_ev = [e for e in rec['evidence'] if host_of(e['url']) == host or (e['url'] and host in e['url'])]
        out.append({
            'domain': host,
            'names': sorted(n for n in rec['names'] if n)[:4],
            'b2b_signals': sorted(rec['b2b_signals']),
            'category_signals': sorted(rec['category_signals']),
            'n_evidence': len(rec['evidence']),
            'n_official_evidence': len(official_ev),
            'corroboration_queries': len(rec['corroboration']),
            'regions_seen': sorted(rec['query_regions']),
            'evidence': rec['evidence'][:6],
        })

    # --- merge harvest domains (quota-free discovery channel) ---
    try:
        hv = json.load(open(f'{GS}/candidates/harvest.json'))['domains']
        existing_hosts = {c['domain'] for c in out}
        for h in hv:
            if h['host'] in existing_hosts: continue
            b2b, cats = find_signals(f"{h.get('anchor','')} {h['host']}")
            out.append({
                'domain': h['host'],
                'names': [h.get('anchor','')[:60]] if h.get('anchor') else [],
                'b2b_signals': sorted(b2b),
                'category_signals': sorted(cats),
                'n_evidence': h.get('corroboration', 1),
                'n_official_evidence': 0,
                'corroboration_queries': h.get('corroboration', 1),
                'regions_seen': [],
                'evidence': [{'query': f"harvest:{h.get('origin','listicle')}", 'url': h.get('sources',[{}])[0] if h.get('sources') else '', 'title': h.get('anchor','')[:120], 'snippet': (h.get('ctx','') or '')[:250], 'in_results_of_own_domain': False}],
                'origin': h.get('origin', 'listicle'),
            })
    except Exception as ex:
        print('harvest merge warn:', ex)

    out.sort(key=lambda x: (-min(x['n_official_evidence'],3), -x['corroboration_queries'], -x['n_evidence']))

    json.dump({
        'generated': __import__('datetime').datetime.now().isoformat(),
        'raw_files': len(raws),
        'candidates': out,
        'dup_known': dup_known,
        'filtered_physical_n': len(filtered_physical),
        'discovery_sources': discovery_sources[:80],
        'stats': {
            'unique_candidate_domains': len(out),
            'with_official_evidence': sum(1 for x in out if x['n_official_evidence'] > 0),
            'with_b2b_and_category': sum(1 for x in out if x['b2b_signals'] and x['category_signals']),
            'multi_query_corroborated': sum(1 for x in out if x['corroboration_queries'] > 1),
            'dup_known_hits': len(dup_known),
        }
    }, open(f'{GS}/candidates/candidates.json','w'), ensure_ascii=False, indent=1)

    st = json.load(open(f'{GS}/candidates/candidates.json'))
    print('STATS:', json.dumps(st['stats'], ensure_ascii=False))
    print('\nTop 25 candidates:')
    for c in out[:25]:
        print(f"  {c['domain'][:40]:42} b2b={','.join(c['b2b_signals'])[:28]:30} cats={len(c['category_signals'])} offEv={c['n_official_evidence']} corr={c['corroboration_queries']}")

if __name__ == '__main__':
    main()
