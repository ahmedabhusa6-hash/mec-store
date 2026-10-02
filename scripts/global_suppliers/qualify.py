#!/usr/bin/env python3
# GDS-1: Qualify + commit entities — full schema, dedup, checkpoints, honest states
import json, os, re
from datetime import datetime, timezone

GS = '/home/z/my-project/research/global_suppliers'

# Aggregator/directory/media hosts that must never qualify as entities
JUNK = {
    'justdial.com','f6s.com','slashdot.org','alarabiya.net','apis.io','globalsources.com',
    'made-in-china.com','alibaba.com','faire.com','orderchamp.com','simon-kucher.com',
    'atwix.com','rfp.wiki','aimoo.com','dms.psc.sc.gov','host.acuite.in','infobot.rikers.org',
    'pentabank.sk','b2bmarketplace.corrios.com',
    'sourceforge.net','tradeindia.com','indiamart.com','dir.indiamart.com','ericsson.com',
    'g2.com','capterra.com','producthunt.com','engadget.com','cnet.com','tomshardware.com',
    'crunchbase.com','pitchbook.com','zoominfo.com','trustpilot.com','sitejabber.com',
}

TLD_COUNTRY = {
    '.id':'Indonesia','.in':'India','.sk':'Slovakia','.eg':'Egypt','.tr':'Türkiye','.pl':'Poland',
    '.ro':'Romania','.cz':'Czechia','.ua':'Ukraine','.ru':'Russia','.kz':'Kazakhstan','.uz':'Uzbekistan',
    '.br':'Brazil','.mx':'Mexico','.ar':'Argentina','.co':'Colombia','.cl':'Chile','.pe':'Peru',
    '.my':'Malaysia','.sg':'Singapore','.ph':'Philippines','.th':'Thailand','.vn':'Vietnam',
    '.pk':'Pakistan','.bd':'Bangladesh','.jp':'Japan','.kr':'South Korea','.cn':'China','.hk':'Hong Kong',
    '.tw':'Taiwan','.ng':'Nigeria','.gh':'Ghana','.ke':'Kenya','.za':'South Africa','.tz':'Tanzania',
    '.ug':'Uganda','.rw':'Rwanda','.et':'Ethiopia','.ma':'Morocco','.dz':'Algeria','.tn':'Tunisia',
    '.sa':'Saudi Arabia','.ae':'UAE','.com.sa':'Saudi Arabia','.com.eg':'Egypt','.com.tr':'Türkiye',
    '.com.br':'Brazil','.com.mx':'Mexico','.com.ar':'Argentina','.com.co':'Colombia','.com.pk':'Pakistan',
    '.co.in':'India','.co.id':'Indonesia','.com.my':'Malaysia','.com.sg':'Singapore','.com.ph':'Philippines',
    '.co.za':'South Africa','.co.ke':'Kenya','.co.ng':'Nigeria','.com.ng':'Nigeria','.com.ua':'Ukraine',
    '.co.uk':'United Kingdom','.de':'Germany','.fr':'France','.it':'Italy','.es':'Spain','.nl':'Netherlands',
    '.eu':'European Union','.io':'Global','.app':'Global','.net':'Global','.com':'Global',
}
REGION_BY_COUNTRY = {
    'Saudi Arabia':'MENA','UAE':'MENA','Egypt':'MENA','Morocco':'MENA','Algeria':'MENA','Tunisia':'MENA','Middle East':'MENA',
    'Türkiye':'Türkiye','Turkey':'Türkiye','Indonesia':'SEA','Malaysia':'SEA','Singapore':'SEA','Philippines':'SEA','Thailand':'SEA','Vietnam':'SEA','Cambodia':'SEA',
    'India':'South Asia','Pakistan':'South Asia','Bangladesh':'South Asia','Sri Lanka':'South Asia',
    'China':'East Asia','Japan':'East Asia','South Korea':'East Asia','Hong Kong':'East Asia','Taiwan':'East Asia',
    'Nigeria':'Africa','Ghana':'Africa','Kenya':'Africa','Uganda':'Africa','Tanzania':'Africa','South Africa':'Africa','Ethiopia':'Africa','Rwanda':'Africa',
    'Brazil':'LatAm','Mexico':'LatAm','Argentina':'LatAm','Colombia':'LatAm','Chile':'LatAm','Peru':'LatAm',
    'Poland':'Eastern Europe','Romania':'Eastern Europe','Czechia':'Eastern Europe','Ukraine':'Eastern Europe','Russia':'CIS','Kazakhstan':'CIS','Uzbekistan':'CIS',
    'Germany':'Europe','France':'Europe','Italy':'Europe','Spain':'Europe','Netherlands':'Europe','United Kingdom':'Europe','United States':'North America','USA':'North America','Canada':'North America','Australia':'Oceania',
    'Global':'Global','European Union':'Europe',
}

TECH_PREFIXES = {'www','docs','doc','blog','app','api','portal','express','developer','dev','shop','store','help','support','partner','partners','business','b2b','wholesale','reseller'}

def root_domain(host):
    parts = [p for p in host.split('.') if p]
    while len(parts) > 2 and parts[0] in TECH_PREFIXES:
        parts = parts[1:]
    # collapse known multi-part public suffixes
    if len(parts) >= 3 and parts[-2] in ('com','co','net','org','gov','edu') and parts[-1] in ('uk','in','id','tr','br','mx','ar','za','ke','ng','ua','my','sg','ph','pk','au','jp'):
        return '.'.join(parts[-3:])
    return '.'.join(parts[-2:]) if len(parts) >= 2 else host

def infer_country(domain, regions_seen, page_text=''):
    for suf, c in sorted(TLD_COUNTRY.items(), key=lambda x: -len(x[0])):
        if domain.endswith(suf):
            if c == 'Global':  # gTLD: no country evidence
                return 'UNKNOWN', 'gTLD (no country evidence)'
            return c, 'domain TLD'
    return 'UNKNOWN', None

def infer_entity_type(rec):
    s = set(rec.get('b2b') or [])
    t = (rec.get('page_title') or '') + ' ' + (rec.get('page_desc') or '')
    if re.search(r'marketplace', t, re.I) and 'API' not in s: return 'Marketplace'
    if 'API' in s and ('Merchant_Infra' in s or 'Automated_Fulfillment' in s): return 'API/Distribution Platform'
    if 'Aggregator' in s: return 'Aggregator Platform'
    if 'White_Label' in s: return 'White-Label Platform'
    if 'Distributor' in s or 'Wholesale' in s: return 'Distributor/Wholesaler'
    if 'Reseller' in s: return 'Reseller Platform'
    return 'Digital Goods Platform'

def main():
    import sys as _sys
    cands = {c['domain']: c for c in json.load(open(f'{GS}/candidates/candidates.json'))['candidates']}
    verified = {v['domain']: v for v in json.load(open(f'{GS}/candidates/verified_pages.json'))}
    state = json.load(open(f'{GS}/state.json'))
    # KNOWN entities (root-domain level) — prevents harvest-merge leaks (e.g. turgame.com)
    K = json.load(open(f'{GS}/known_entities.json'))
    K_ROOTS = {root_domain(r['domain']) for r in K['entities'] if r.get('domain')}
    # brand-name tokens (from KNOWN names/aliases, length>4) — catches same-brand different-TLD (prodseller.com)
    K_NAME_TOKENS = set()
    for r in K['entities']:
        for nm in ([r.get('name')] or []) + (r.get('aliases') or []):
            nm = (nm or '').lower().strip()
            if len(nm) >= 5 and ' ' not in nm:
                K_NAME_TOKENS.add(nm)
    if '--rebuild' in _sys.argv:
        committed = []
    else:
        try: committed = json.load(open(f'{GS}/entities/qualified.json'))
        except Exception: committed = []

    committed_roots = {}
    for e in committed: committed_roots.setdefault(e['Official_Domain'], e)

    new_qualified, rejected, insufficient = [], [], []
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')

    try: qc_rejects = json.load(open(f'{GS}/entities/qc_rejects.json'))
    except Exception: qc_rejects = {}
    for dom, c in cands.items():
        if dom in qc_rejects or root_domain(dom) in {root_domain(k) for k in qc_rejects}:
            rejected.append({'domain': dom, 'reason': f'QC manual reject: {qc_rejects.get(dom) or "(root match)"}'}); continue
        if dom in JUNK or root_domain(dom) in {root_domain(j) for j in JUNK}:
            rejected.append({'domain': dom, 'reason': 'directory/media/aggregator host'}); continue
        kroot = root_domain(dom)
        if kroot in K_ROOTS:
            rejected.append({'domain': dom, 'reason': f'KNOWN_ENTITY (root {kroot})'}); continue
        # brand-token match on the domain itself (e.g. 'prodseller.com' contains 'prodseller')
        label = dom.split('.')[0].lower()
        if label in K_NAME_TOKENS:
            rejected.append({'domain': dom, 'reason': f'KNOWN_BRAND (token {label})'}); continue
        v = verified.get(dom, {})
        http = v.get('http', 0)
        page_b2b = v.get('page_b2b_signals', [])
        page_cat = v.get('page_cat_signals', [])
        has_b2b = bool(c['b2b_signals'] or page_b2b)
        has_cat = bool(c['category_signals'] or page_cat)

        if not has_b2b or not has_cat:
            insufficient.append({'domain': dom, 'reason': f"missing {'B2B' if not has_b2b else 'digital-category'} evidence"})
            continue
        if http in (0, 404, 410) and not v.get('bot_blocked'):
            insufficient.append({'domain': dom, 'reason': f'domain not reachable (HTTP {http})'})
            continue
        # duplicate vs committed (root-domain level)
        rt = root_domain(dom)
        if rt in committed_roots or any(root_domain(e['Official_Domain']) == rt for e in new_qualified):
            rejected.append({'domain': dom, 'reason': f'DUPLICATE/RELATED of {rt}'}); continue

        # confidence: HIGH = own-page verified signals | MEDIUM = official snippet + alive page
        if http == 200 and page_b2b and page_cat:
            conf = 'HIGH'
        elif http in (200, 403, 406):
            conf = 'MEDIUM'
        else:
            conf = 'LOW'
        if conf == 'LOW':
            insufficient.append({'domain': dom, 'reason': 'weak evidence'}); continue

        country, csource = infer_country(dom, c['regions_seen'])
        b2b_all = sorted(set(c['b2b_signals']) | set(page_b2b))
        cats_all = sorted(set(c['category_signals']) | set(page_cat))
        evidence_official = [{
            'type': 'official page (HTTP 200, direct fetch)' if http==200 else f'official domain (HTTP {http}, bot-blocked)' if v.get('bot_blocked') else 'official-domain search evidence',
            'url': f"https://{dom}/", 'title': v.get('page_title','') or (c['names'][0] if c['names'] else ''),
            'b2b_evidence': b2b_all, 'category_evidence': cats_all, 'ts': now,
        }]
        if not (http == 200 and page_b2b and page_cat):
            evidence_official += [{'type': 'official-domain search result', 'ev': c['evidence'][0]}] if c['evidence'] else []
        independent = [{'type': 'independent search corroboration', 'distinct_queries': c['corroboration_queries']}] if c['corroboration_queries'] > 1 else []

        ent = {
            'Entity_ID': '',  # assigned on commit
            'Canonical_Name': (v.get('page_title') or (c['names'][0] if c['names'] else dom)).split('|')[0].strip()[:60] or dom,
            'Brand_Name': (c['names'][0] if c['names'] else dom)[:60],
            'Official_Domain': root_domain(dom) if dom.split('.')[0] in TECH_PREFIXES and len(dom.split('.')) > 2 else dom,
            'Discovered_Host': dom,
            'Country': country, 'Country_Source': csource,
            'Region': REGION_BY_COUNTRY.get(country, 'UNKNOWN'),
            'Entity_Type': infer_entity_type({'b2b': b2b_all, 'page_title': v.get('page_title',''), 'page_desc': v.get('page_desc','')}),
            'Business_Model': 'B2B' if 'B2B' in b2b_all or 'Merchant_Infra' in b2b_all else ('B2B2C' if 'Reseller' in b2b_all else 'B2B/Wholesale'),
            'Digital_Categories': cats_all,
            'B2B': 'B2B' in b2b_all, 'Wholesale': 'Wholesale' in b2b_all, 'Reseller': 'Reseller' in b2b_all,
            'API': 'API' in b2b_all, 'Webhook': 'Webhook' in b2b_all, 'H2H': 'H2H' in b2b_all,
            'White_Label': 'White_Label' in b2b_all,
            'Automated_Fulfillment': 'Automated_Fulfillment' in b2b_all,
            'Catalog_Breadth': f"{len(cats_all)} categories",
            'Geographic_Coverage': ', '.join(c['regions_seen']) or 'UNKNOWN',
            'Parent_or_Upstream': 'UNKNOWN',
            'Evidence_Official': evidence_official,
            'Evidence_Independent': independent,
            'Last_Checked': now,
            'Qualification_Status': 'QUALIFIED_NEW',
            'Confidence': conf,
            'Notes': f"discovered via {c['corroboration_queries']} distinct queries; page HTTP {http}" + ('; bot-blocked page, signals from search evidence' if v.get('bot_blocked') and not page_b2b else '') + ('; SINGLE-CATEGORY entity (breadth flag)' if len(cats_all) == 1 else ''),
        }
        new_qualified.append(ent)

    # assign IDs (deterministic: sort new batch by domain for stable re-derivation)
    new_qualified.sort(key=lambda e: e['Official_Domain'])
    next_id = max((int(e['Entity_ID'].split('-')[1]) for e in committed), default=0)
    for e in new_qualified:
        next_id += 1
        e['Entity_ID'] = f'GDS-{next_id:04d}'
        committed.append(e)

    json.dump(committed, open(f'{GS}/entities/qualified.json','w'), ensure_ascii=False, indent=1)
    json.dump({'rejected': rejected, 'insufficient': insufficient}, open(f'{GS}/entities/non_qualified.json','w'), ensure_ascii=False, indent=1)

    # state update + checkpoint
    nq = len(committed)
    state['checkpoint'] = {
        'qualified_total': nq,
        'last_checkpoint_at': now,
        'checkpoint_number': nq // 100,
        'note': f'{nq} qualified — checkpoint #{nq//100}' if nq % 100 == 0 else f'{nq} qualified (next checkpoint at {((nq//100)+1)*100})',
    }
    state['counters']['qualified_new'] = nq
    state['counters']['rejected'] = len(rejected)
    state['counters']['insufficient'] = len(insufficient)
    json.dump(state, open(f'{GS}/state.json','w'), ensure_ascii=False, indent=1)

    print(f"COMMITTED: +{len(new_qualified)} QUALIFIED_NEW | total {nq} | rejected {len(rejected)} | insufficient {len(insufficient)}")
    by_conf = {}
    for e in committed: by_conf[e['Confidence']] = by_conf.get(e['Confidence'],0)+1
    print('Confidence:', by_conf)
    by_type = {}
    for e in committed: by_type[e['Entity_Type']] = by_type.get(e['Entity_Type'],0)+1
    print('Types:', by_type)
    print('\nNewest 15:')
    for e in new_qualified[-15:]:
        print(f"  {e['Entity_ID']} {e['Official_Domain'][:36]:38} {e['Entity_Type'][:26]:28} {e['Country'][:18]:20} {e['Confidence']}")

if __name__ == '__main__':
    main()
