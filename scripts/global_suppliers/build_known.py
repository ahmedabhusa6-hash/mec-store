#!/usr/bin/env python3
# GDS-1: Compile KNOWN_ENTITIES from all project sources (exclusion list for global discovery)
import json, re, os

BASE = '/home/z/my-project'
known = {}  # key: lowercase name or domain -> record

def add(name, domain=None, aliases=None, source='', layer='ENTITY'):
    if not name: return
    name = str(name).strip()
    if len(name) < 2: return
    dom = (domain or '').lower().strip().replace('https://','').replace('http://','').split('/')[0].strip()
    if dom in ('-','',' ','—'): dom = ''
    key = name.lower()
    if key in known:
        # merge: keep domain if existing lacks it; prefer ENTITY layer over BRAND
        rec = known[key]
        if dom and not rec['domain']: rec['domain'] = dom
        if layer == 'ENTITY' and rec['layer'] == 'BRAND': rec['layer'] = 'ENTITY'
        rec['aliases'] = list({a.lower().strip() for a in (rec.get('aliases',[]) + (aliases or [])) if a and a.strip()})
        return
    known[key] = {
        'name': name, 'domain': dom,
        'aliases': [a.lower().strip() for a in (aliases or []) if a and a.strip()],
        'source': source, 'layer': layer,
    }

# --- 1. entity_registry.json (verified research entities) ---
d = json.load(open(f'{BASE}/research/entity_registry.json'))
for e in d.get('entities', []):
    n = e.get('name','')
    dom = e.get('domain','')
    # multi-name entries like "Kinguin / G2A / Z2U ..." and "Netflix / Spotify / ..."
    parts = [p.strip() for p in re.split(r'[/,]', n) if p.strip()]
    if len(parts) > 1 and not dom:
        for p in parts:  # brand clusters
            add(p, None, source='entity_registry(brands)', layer='BRAND')
    else:
        add(n, dom, source='entity_registry')

# --- 2. Manual seed: entities documented across worklog/research runs ---
manual_entities = [
    # (name, domain, aliases, source)
    ('ProdSeller','prodseller.io',['prodseller','ps seller'],'store supplier + mec research'),
    ('Turgame','turgame.com',['turgame','definite play'],'SUP-002'),
    ('FazerCards','fazercards.com',['fazer cards','fazercards'],'SUP entity'),
    ('Reloadly','reloadly.com',[],'SUP entity'),
    ('Eneba','eneba.com',[],'marketplace known'),
    ('GGSel','ggsel.net',['ggsel','gg sel'],'wholesale portal'),
    ('Keyforsteam','keyforsteam.de',[],'verified retailer'),
    ('CJS CD Keys','cjs-cdkeys.com',['cjs cdkeys'],'verified retailer'),
    ('Kinguin','kinguin.net',[],'marketplace known'),
    ('G2A','g2a.com',['g2a pay'],'marketplace known'),
    ('Z2U','z2u.com',[],'marketplace known (mec5)'),
    ('U7Buy','u7buy.com',[],'mec5 research'),
    ('OffGamers','offgamers.com',['off gamers'],'mec5 research'),
    ('SEA Gamer Mall','seagm.com',['seagm','sea gamer'],'mec5 research'),
    ('GamsGo','gamsgo.com',['gamsgo'],'mec5 research'),
    ('AllKeyShop','allkeyshop.com',['allkeyshop'],'price comparison known'),
    ('GG.deals','gg.deals',[],'price comparison known'),
    ('CDKeys','cdkeys.com',['cd keys'],'retailer known'),
    ('RoyalCDKeys','royalcdkeys.com',[],'retailer known'),
    ('GoCDKeys','gocdkeys.com',[],'retailer known'),
    ('Keys4us','keys4us.com',[],'retailer known'),
    ('Driffy','driffy.com',[],'marketplace known'),
    ('K4G','k4g.com',['k4g'],'b2b/b2c marketplace (b3 research)'),
    ('Plati.market','plati.market',['plati','plati market'],'ru marketplace (b3)'),
    ('Digiseller','digiseller.com',['digi seller','digiseller'],'ru platform (b3)'),
    ('BitTopup','bittopup.com',['bit topup'],'b3 research'),
    ('StackVault','stackvault.shop',['stack vault'],'mec2 channel entity'),
    ('Acczone','acczone.store',['acczone store','awz'],'mec2 channel entity'),
    ('HitMeow','hitmeow.com',['premikey','premikey bots','hitmeow shop'],'mec2 channel entity'),
    ('Neva AI','neva-ai.com',['nevakeystore','neva'],'mec2 channel entity'),
    ('Fin Ai Support','finai.support',['veriyfersupportbot','fin ai'],'mec2 channel entity'),
    ('Gamisell','gamisell.com',['gamisell'],'mec2 channel entity'),
    ('Evolution Era','evolutionera.io',['evo era'],'mec2 channel entity'),
    ('insightXpro','insightxpro.com',['insightxpro'],'mec2 channel entity'),
    ('AISUBS.ID','aisubs.id',[],'mec2 channel entity'),
    ('Verifier','verifier.support',['verifierbot','verifier group'],'mec2 channel entity'),
    ('Gemini12Pro','gemini12pro.com',['gemini12pro'],'mec2 channel entity'),
    ('Bite Store','bitestore.io',['learnwith_alex','bite store'],'mec2 channel entity'),
    ('MobiMatter','mobimatter.com',[],'esim b2b (registry)'),
    ('Airalo','airalo.com',[],'esim brand + partner'),
    ('NordVPN','nordvpn.com',[],'brand known'),
    ('SheerID','sheerid.com',[],'verification service known'),
    ('Binance Pay','binance.com',['binance pay'],'payment rail known'),
]
for n,dom,al,src in manual_entities:
    add(n, dom, al, src)

# --- 3. catalog brands (226) as BRAND layer for name-collision awareness ---
try:
    cat = json.load(open(f'{BASE}/download/catalog_v42.json'))
    for s in cat.get('skus', []):
        b = s.get('brand') or s.get('brand_name')
        if b: add(b, None, source='catalog_v42', layer='BRAND')
except Exception as ex:
    print('catalog warn:', ex)

# --- 4. offers_intelligence entity mentions (official baselines etc.) ---
try:
    oi = json.load(open(f'{BASE}/download/offers_intelligence.json'))
    def walk(o):
        if isinstance(o, dict):
            for k,v in o.items():
                if k in ('entity','platform','store','source_entity') and isinstance(v,str) and 2 < len(v) < 60:
                    add(v, None, source='offers_intelligence', layer='ENTITY')
                walk(v)
        elif isinstance(o, list):
            for x in o[:5000]: walk(x)
    walk(oi)
except Exception as ex:
    print('offers warn:', ex)

# index for fast matching
index = {}
for k, rec in known.items():
    keys = [k] + rec['aliases'] + ([rec['domain']] if rec['domain'] else [])
    for key in keys:
        if key: index.setdefault(key, rec)

out = {
    'generated': __import__('datetime').datetime.now().isoformat(),
    'total_records': len(known),
    'entities': [r for r in known.values() if r['layer']=='ENTITY'],
    'brands': [r['name'] for r in known.values() if r['layer']=='BRAND'],
    'match_index': index,
}
with open(f'{BASE}/research/global_suppliers/known_entities.json','w') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

ents = [r for r in known.values() if r['layer']=='ENTITY']
print(f"KNOWN_ENTITIES compiled: {len(ents)} entities + {len(out['brands'])} brands | match keys: {len(index)}")
print(f"Saved: research/global_suppliers/known_entities.json")
