#!/usr/bin/env python3
# GDS-1: Generate global query plan (families x regions x languages)
import json, hashlib
from datetime import datetime

# Query families: (family_id, english_template)
FAMILIES = [
    ('wholesale_digital', 'wholesale digital goods supplier {R}'),
    ('giftcard_api', 'gift card wholesale API provider {R}'),
    ('topup_api', 'game top up reseller API {R}'),
    ('voucher_distrib', 'digital voucher distributor {R}'),
    ('b2b_gaming', 'B2B gaming API platform {R}'),
    ('h2h', 'H2H game topup distributor {R}'),
    ('wholesale_keys', 'wholesale game keys distributor {R}'),
    ('reseller_program', 'gift card reseller program {R}'),
    ('digital_distrib', 'digital distribution platform B2B {R}'),
    ('merchant_api', 'merchant digital goods API integration {R}'),
    ('white_label', 'white label digital goods platform {R}'),
    ('prepaid_api', 'prepaid products distributor API {R}'),
    ('aggregator_api', 'gift card aggregator API {R}'),
    ('bulk_supplier', 'bulk digital products supplier {R}'),
    ('sub_reseller', 'subscription reseller platform B2B {R}'),
    ('software_distrib', 'software license distributor reseller {R}'),
    ('esim_api', 'eSIM wholesale API distributor {R}'),
    ('airtime_api', 'airtime top-up API distributor {R}'),
    ('incentive_gifts', 'corporate gift card platform B2B rewards {R}'),
    ('list_discover', 'top digital goods distribution companies list 2026 {R}'),
]

# Regional/local queries: (region, lang, query) — hand-crafted local-language variants
REGIONAL = [
    # MENA / Arabic
    ('MENA','ar','موزع بطاقات رقمية بالجملة API السعودية'),
    ('MENA','ar','منصة توزيع بطاقات شحن وألعاب B2B مصر'),
    ('MENA','ar','تاجر جملة بطاقات رقمية متاجر الامارات'),
    ('MENA','ar','API بطاقات هدايا موزع معتمد الشرق الأوسط'),
    ('MENA','ar','برنامج وكلاء بطاقات الألعاب والاشتراكات الرقمية'),
    # Türkiye
    ('TR','tr','toptan dijital ürün distribütör bayilik'),
    ('TR','tr','oyun para yükleme API toptan satış'),
    ('TR','tr','dijital hediye kartı toptan distribütör B2B'),
    # Indonesia / SEA
    ('ID','id','distributor top up game harga grosir API'),
    ('ID','id',' supplier voucher digital pulsa PPOB grosir'),
    ('SEA','en','game credit distributor API Malaysia Singapore'),
    ('TH','th','ผู้จัดจำหน่ายบัตรเกมราคาส่ง API'),
    ('VN','vi','nha phan phoi the game gia si nap game API'),
    ('PH','en','game credits distributor wholesale supplier Philippines'),
    # South Asia
    ('IN','en','gift card wholesale distributor API India'),
    ('IN','en','game topup B2B distributor reseller India'),
    ('IN','hi','गेम टॉपअप व्होल्सेल डिस्ट्रीब्यूटर भारत'),
    ('PK','en','mobile top up distributor API Pakistan'),
    ('BD','en','digital goods wholesale distributor Bangladesh'),
    # East Asia
    ('JP','ja','デジタルギフトカード 卸販売 API 事業'),
    ('KR','ko','게임 충전소 도매 유통 API'),
    ('CN','en','China digital gift card wholesale distributor export API'),
    ('CN','zh','数字商品批发平台 游戏点卡经销商 API'),
    # Africa
    ('NG','en','airtime top up API distributor Nigeria wholesale'),
    ('KE','en','airtime and data bundle API reseller Kenya'),
    ('GH','en','mobile money airtime API distributor Ghana'),
    ('ZA','en','gift card wholesale distributor South Africa'),
    ('EG','ar','توزيع كروت شحن ومحافظ إلكترونية جملة مصر'),
    ('MA','fr','distributeur cartes cadeaux et recharge grossiste Maroc'),
    # LatAm
    ('BR','pt','distribuidor cartão digital jogos recarga atacado API'),
    ('MX','es','distribuidor tarjetas digitales mayoreo recargas API'),
    ('AR','es','distribuidor tarjetas de regalo digitales mayorista Argentina'),
    ('CO','es','proveedor mayorista tarjetas digitales recargas Colombia'),
    # Eastern Europe / CIS
    ('PL','pl','hurtownik doładowania i karty cyfrowe API'),
    ('RO','ro','distribuitor carduri digitale jocuri en gros'),
    ('CZ','en','game key wholesale distributor Central Europe'),
    ('UA','uk','дистрибютор ігрових карток та поповнення гуртом API'),
    ('RU','ru','дистрибьютор цифровых товаров оптом API H2H'),
    ('KZ','ru','дистрибьютор пополнений игр Казахстан опт'),
    # Central Asia / Caucasus
    ('UZ','ru','пополнение игр дистрибьютор Узбекистан опт API'),
    # GCC extra
    ('GCC','ar','موزع معتمد بطاقات آيتونز وجوجل بلاي بالجملة'),
    ('GCC','ar','متجر جملة اشتراكات رقمية وكلاء السعودية'),
    # Global verticals (EN, no region word)
    ('GLOBAL','en','telco voucher distribution platform API for merchants'),
    ('GLOBAL','en','direct top-up API provider games and subscriptions worldwide'),
    ('GLOBAL','en','digital content distributor for retail networks'),
    ('GLOBAL','en','prepaid pin generator distributor platform B2B'),
    ('GLOBAL','en','OTT subscription distributor reseller API platform'),
    ('GLOBAL','en','in-game currency wholesale API diamonds UC coins'),
    ('GLOBAL','en','gift card trading platform for businesses bulk purchase'),
    ('GLOBAL','en','mobile recharge API aggregator emerging markets'),
    ('GLOBAL','en','digital goods catalog API for loyalty programs'),
    ('GLOBAL','en','white label gift card store platform provider'),
    ('GLOBAL','en','game wallet top up API H2H wholesale providers'),
    ('GLOBAL','en','streaming subscription wholesale provider B2B resellers'),
    ('GLOBAL','en','digital scratch card distributor telecom prepaid'),
    ('GLOBAL','en','B2B marketplace for digital gift cards trading between businesses'),
    ('GLOBAL','en','esim data package API wholesale provider'),
    ('GLOBAL','en','software license reseller cloud marketplace B2B distributor'),
    ('GLOBAL','en','payment aggregator digital goods gift cards API'),
    ('GLOBAL','en','loyalty rewards catalog digital gifts API provider'),
    ('GLOBAL','en','carrier billing digital goods distributor platform'),
    ('GLOBAL','en','kiosk digital goods distributor prepaid terminal supplier'),
]

REGIONS = ['worldwide','in Europe','in Asia','in Middle East','in Africa','in Latin America','in USA','in GCC','in Southeast Asia','in India']

def main():
    queries = []
    seen = set()
    def add(region, lang, family, q):
        qid = hashlib.md5(q.encode()).hexdigest()[:10]
        if qid in seen: return
        seen.add(qid)
        queries.append({'id': qid, 'region': region, 'lang': lang, 'family': family, 'q': q})

    # Layer 1: families x region words (EN)
    for fam, tpl in FAMILIES:
        for r in REGIONS:
            add(r if r != 'worldwide' else 'GLOBAL', 'en', fam, tpl.format(R=r))
    # Layer 2: regional/local-language handcrafted
    for region, lang, q in REGIONAL:
        add(region, lang, 'regional_local', q)

    with open('/home/z/my-project/research/global_suppliers/queries.json','w') as f:
        json.dump({'generated': datetime.now().isoformat(), 'total': len(queries), 'queries': queries}, f, ensure_ascii=False, indent=1)
    print(f"Query plan generated: {len(queries)} queries")
    for r in ['GLOBAL','MENA','GCC','TR','ID','SEA','TH','VN','PH','IN','PK','BD','JP','KR','CN','NG','KE','GH','ZA','EG','MA','BR','MX','AR','CO','PL','RO','CZ','UA','RU','KZ','UZ']:
        n = sum(1 for q in queries if q['region']==r)
        if n: print(f"  {r}: {n}")

if __name__ == '__main__':
    main()
