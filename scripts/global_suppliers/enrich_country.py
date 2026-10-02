#!/usr/bin/env python3
# GDS-2: Country enrichment — fetch contact/about pages for UNKNOWN-country entities,
# detect phone prefixes + country names. Quota-free. Updates qualified.json in place.
import json, re, sys, concurrent.futures
import requests
import urllib3
urllib3.disable_warnings()

GS = '/home/z/my-project/research/global_suppliers'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

sys.path.insert(0, '/home/z/my-project/scripts/global_suppliers')
from qualify import REGION_BY_COUNTRY

PHONE_COUNTRY = [
    ('+966','Saudi Arabia'),('+971','UAE'),('+972','Israel'),('+973','Bahrain'),('+974','Qatar'),
    ('+975','Bhutan'),('+976','Mongolia'),('+977','Nepal'),('+90','Türkiye'),('+92','Pakistan'),
    ('+93','Afghanistan'),('+94','Sri Lanka'),('+95','Myanmar'),('+98','Iran'),('+212','Morocco'),
    ('+213','Algeria'),('+216','Tunisia'),('+218','Libya'),('+220','Gambia'),('+233','Ghana'),
    ('+234','Nigeria'),('+254','Kenya'),('+255','Tanzania'),('+256','Uganda'),('+257','Burundi'),
    ('+258','Mozambique'),('+260','Zambia'),('+263','Zimbabwe'),('+264','Namibia'),('+27','South Africa'),
    ('+20','Egypt'),('+249','Sudan'),('+251','Ethiopia'),('+250','Rwanda'),('+291','Eritrea'),
    ('+252','Somalia'),('+253','Djibouti'),('+961','Lebanon'),('+962','Jordan'),('+963','Syria'),
    ('+964','Iraq'),('+965','Kuwait'),('+967','Yemen'),('+968','Oman'),('+60','Malaysia'),
    ('+61','Australia'),('+62','Indonesia'),('+63','Philippines'),('+65','Singapore'),('+66','Thailand'),
    ('+84','Vietnam'),('+855','Cambodia'),('+856','Laos'),('+81','Japan'),('+82','South Korea'),
    ('+86','China'),('+886','Taiwan'),('+852','Hong Kong'),('+853','Macau'),('+91','India'),
    ('+880','Bangladesh'),('+7','Russia'),('+380','Ukraine'),('+375','Belarus'),('+373','Moldova'),
    ('+374','Armenia'),('+994','Azerbaijan'),('+995','Georgia'),('+996','Kyrgyzstan'),('+998','Uzbekistan'),
    ('+77','Kazakhstan'),('+48','Poland'),('+40','Romania'),('+359','Bulgaria'),('+420','Czechia'),
    ('+421','Slovakia'),('+36','Hungary'),('+385','Croatia'),('+381','Serbia'),('+386','Slovenia'),
    ('+55','Brazil'),('+52','Mexico'),('+54','Argentina'),('+57','Colombia'),('+56','Chile'),
    ('+51','Peru'),('+593','Ecuador'),('+591','Bolivia'),('+598','Uruguay'),('+509','Haiti'),
    ('+1809','Dominican Republic'),('+1','United States'),('+44','United Kingdom'),('+49','Germany'),
    ('+33','France'),('+34','Spain'),('+39','Italy'),('+31','Netherlands'),('+32','Belgium'),
    ('+41','Switzerland'),('+43','Austria'),('+46','Sweden'),('+47','Norway'),('+45','Denmark'),
    ('+351','Portugal'),('+30','Greece'),('+358','Finland'),
]

COUNTRY_WORDS = {
 'saudi arabia':'Saudi Arabia','united arab emirates':'UAE','dubai':'UAE','abu dhabi':'UAE',
 'kuwait':'Kuwait','qatar':'Qatar','bahrain':'Bahrain','oman':'Oman','jordan':'Jordan',
 'lebanon':'Lebanon','iraq':'Iraq','yemen':'Yemen','egypt':'Egypt','morocco':'Morocco',
 'casablanca':'Morocco','algiers':'Algeria','algeria':'Algeria','tunisia':'Tunisia','libya':'Libya',
 'istanbul':'Türkiye','turkey':'Türkiye','türkiye':'Türkiye','ankara':'Türkiye','indonesia':'Indonesia',
 'jakarta':'Indonesia','malaysia':'Malaysia','kuala lumpur':'Malaysia','singapore':'Singapore',
 'philippines':'Philippines','manila':'Philippines','thailand':'Thailand','bangkok':'Thailand',
 'vietnam':'Vietnam','vietnam':'Vietnam','ho chi minh':'Vietnam','hanoi':'Vietnam','cambodia':'Cambodia',
 'phnom penh':'Cambodia','india':'India','mumbai':'India','delhi':'India','bangalore':'India',
 'pakistan':'Pakistan','karachi':'Pakistan','lahore':'Pakistan','bangladesh':'Bangladesh','dhaka':'Bangladesh',
 'sri lanka':'Sri Lanka','colombo':'Sri Lanka','nepal':'Nepal','nigeria':'Nigeria','lagos':'Nigeria',
 'ghana':'Ghana','accra':'Ghana','kenya':'Kenya','nairobi':'Kenya','uganda':'Uganda','kampala':'Uganda',
 'tanzania':'Tanzania','dar es salaam':'Tanzania','south africa':'South Africa','johannesburg':'South Africa',
 'cape town':'South Africa','ethiopia':'Ethiopia','addis ababa':'Ethiopia','rwanda':'Rwanda','kigali':'Rwanda',
 'brazil':'Brazil','são paulo':'Brazil','sao paulo':'Brazil','bogotá':'Colombia','bogota':'Colombia',
 'colombia':'Colombia','mexico':'Mexico','méxico':'Mexico','argentina':'Argentina','buenos aires':'Argentina',
 'chile':'Chile','santiago':'Chile','peru':'Peru','lima':'Peru','ecuador':'Ecuador','poland':'Poland',
 'warsaw':'Poland','romania':'Romania','bucharest':'Romania','bulgaria':'Bulgaria','sofia':'Bulgaria',
 'czech':'Czechia','prague':'Czechia','ukraine':'Ukraine','kyiv':'Ukraine','kiev':'Ukraine',
 'russia':'Russia','moscow':'Russia','kazakhstan':'Kazakhstan','almaty':'Kazakhstan','uzbekistan':'Uzbekistan',
 'tashkent':'Uzbekistan','kyrgyzstan':'Kyrgyzstan','bishkek':'Kyrgyzstan','georgia':'Georgia','tbilisi':'Georgia',
 'armenia':'Armenia','yerevan':'Armenia','azerbaijan':'Azerbaijan','baku':'Azerbaijan','japan':'Japan',
 'tokyo':'Japan','osaka':'Japan','south korea':'South Korea','seoul':'South Korea','china':'China',
 'shanghai':'China','beijing':'China','hong kong':'Hong Kong','taiwan':'Taiwan','taipei':'Taiwan',
 'united states':'United States','usa':'United States','new york':'United States','california':'United States',
 'texas':'United States','florida':'United States','united kingdom':'United Kingdom','london':'United Kingdom',
 'germany':'Germany','berlin':'Germany','france':'France','paris':'France','spain':'Spain','madrid':'Spain',
 'italy':'Italy','milan':'Italy','rome':'Italy','netherlands':'Netherlands','amsterdam':'Netherlands',
 'belgium':'Belgium','canada':'Canada','toronto':'Canada','australia':'Australia','sydney':'Australia',
}

def curl(url, timeout=9):
    try:
        r = requests.get(url, headers={'User-Agent': UA}, timeout=(4, timeout), allow_redirects=True, verify=False)
        if r.status_code == 200: return r.text or ''
    except Exception: pass
    return ''

def textify(html):
    t = re.sub(r'<script[^>]*>.*?</script>', ' ', html[:300000], flags=re.S|re.I)
    t = re.sub(r'<style[^>]*>.*?</style>', ' ', t, flags=re.S|re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', t)[:15000]

def detect_country(dom):
    """Return (country, source) best-effort from contact/about/home pages."""
    votes = {}
    for path in ('/contact', '/contact-us', '/about', '/about-us', '/'):
        html = curl(f'https://{dom}{path}')
        if not html: continue
        text = textify(html).lower()
        for pref, c in PHONE_COUNTRY:
            if pref + ' ' in text or pref + '\u00a0' in text or re.search(re.escape(pref) + r'[\s\-()]*[2-9]', text):
                votes[c] = votes.get(c, 0) + 3; break  # one prefix per page is enough
        for w, c in COUNTRY_WORDS.items():
            if w in text:
                votes[c] = votes.get(c, 0) + 1
        if votes: break  # first page with evidence wins
    if not votes: return None, None
    best = max(votes.items(), key=lambda x: x[1])
    if best[1] >= 2: return best[0], 'contact/about page (phone/address evidence)'
    return None, None

def main():
    ents = json.load(open(f'{GS}/entities/qualified.json'))
    targets = [e for e in ents if e.get('Country') in ('UNKNOWN', None, '')]
    print(f'Enriching country for {len(targets)}/{len(ents)} UNKNOWN-country entities...')
    PROG = f'{GS}/candidates/country_enrich.json'
    try: cache = json.load(open(PROG))
    except Exception: cache = {}
    targets = [e for e in targets if e['Official_Domain'] not in cache]
    print(f'after cache-skip: {len(targets)}')

    def work(e): return e['Official_Domain'], detect_country(e['Official_Domain'])
    n = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        for dom, (country, source) in ex.map(work, targets):
            n += 1
            cache[dom] = {'country': country, 'source': source}
            if n % 25 == 0:
                print(f'  {n}/{len(targets)}')
                json.dump(cache, open(PROG,'w'))
    json.dump(cache, open(PROG,'w'))

    # apply to entities
    enriched = 0
    for e in ents:
        c = cache.get(e['Official_Domain'])
        if c and c.get('country') and e.get('Country') in ('UNKNOWN', None, ''):
            e['Country'] = c['country']; e['Country_Source'] = c['source']
            e['Region'] = REGION_BY_COUNTRY.get(c['country'], 'UNKNOWN')
            enriched += 1
    json.dump(ents, open(f'{GS}/entities/qualified.json','w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(f'\nENRICHED: +{enriched} countries assigned')
    print('Region distribution now:', dict(Counter(e['Region'] for e in ents)))

if __name__ == '__main__':
    main()
