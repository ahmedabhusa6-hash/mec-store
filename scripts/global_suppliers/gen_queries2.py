#!/usr/bin/env python3
# GDS-2: Wave-2 query plan — bigger, more vertical, more local-language.
# Merges into queries.json (wave-1 IDs preserved; dedup by qid hash).
import json, hashlib
from datetime import datetime

GS = '/home/z/my-project/research/global_suppliers'

# ---- Layer 1: vertical families x region words (EN) ----
FAMILIES2 = [
    # vertical-numeric (gift cards / topups / keys)
    ('gc_wholesale', 'gift card wholesale distributor {R}'),
    ('gc_supplier', 'gift card supplier for retailers {R}'),
    ('topup_wholesale', 'mobile top up wholesale distributor {R}'),
    ('topup_panel', 'topup reseller panel API {R}'),
    ('gamekey_b2b', 'game key B2B distributor {R}'),
    ('voucher_wholesale', 'prepaid voucher wholesale distributor {R}'),
    ('pin_distributor', 'digital pin distributor wholesale {R}'),
    ('sub_wholesale', 'subscription wholesale distributor {R}'),
    ('ott_distributor', 'OTT streaming subscription distributor {R}'),
    ('esim_wholesale', 'eSIM wholesale distributor platform {R}'),
    ('airtime_wholesale', 'airtime wholesale distributor {R}'),
    ('ingame_wholesale', 'in-game currency wholesale supplier {R}'),
    ('digital_dropship', 'digital goods dropshipping supplier {R}'),
    ('giftcard_trading', 'B2B gift card trading platform {R}'),
    ('gc_api_reseller', 'gift card API reseller platform {R}'),
    ('voucher_api', 'voucher API provider wholesale {R}'),
    ('gaming_distrib', 'gaming distributor wholesale platform {R}'),
    ('prepaid_platform', 'prepaid platform distributor B2B {R}'),
    ('digital_reseller', 'digital products reseller platform {R}'),
    ('wallet_topup', 'wallet top up wholesale API {R}'),
    # brand-specific (high supplier density)
    ('steam_wholesale', 'steam gift card wholesale distributor {R}'),
    ('itunes_wholesale', 'itunes gift card wholesale distributor {R}'),
    ('googleplay_wholesale', 'google play gift card wholesale {R}'),
    ('netflix_reseller', 'netflix subscription reseller wholesale {R}'),
    ('psn_wholesale', 'psn xbox gift card wholesale distributor {R}'),
    ('pubg_supplier', 'pubg uc diamond supplier wholesale {R}'),
    ('freefire_supplier', 'free fire diamond supplier API {R}'),
    ('mobilelegends_supplier', 'mobile legends diamond top up supplier {R}'),
    ('valorant_supplier', 'valorant points top up wholesale {R}'),
    ('roblox_supplier', 'roblox gift card wholesale supplier {R}'),
]

REGIONS2 = [
    'worldwide', 'in UAE', 'in Saudi Arabia', 'in Kuwait', 'in Qatar', 'in Oman', 'in Bahrain',
    'in Jordan', 'in Iraq', 'in Yemen', 'in Lebanon', 'in Egypt', 'in Morocco', 'in Algeria',
    'in Tunisia', 'in Turkey', 'in Indonesia', 'in Malaysia', 'in Vietnam', 'in Thailand',
    'in Philippines', 'in Singapore', 'in Cambodia', 'in Pakistan', 'in Bangladesh', 'in Sri Lanka',
    'in Nepal', 'in Nigeria', 'in Ghana', 'in Kenya', 'in Uganda', 'in Tanzania', 'in South Africa',
    'in Ethiopia', 'in Rwanda', 'in Brazil', 'in Mexico', 'in Argentina', 'in Colombia', 'in Chile',
    'in Peru', 'in Ecuador', 'in Dominican Republic', 'in Poland', 'in Romania', 'in Bulgaria',
    'in Czech Republic', 'in Ukraine', 'in Russia', 'in Kazakhstan', 'in Uzbekistan', 'in Kyrgyzstan',
    'in Georgia', 'in Armenia', 'in Azerbaijan', 'in India', 'in Japan', 'in South Korea', 'in Taiwan',
    'in Hong Kong', 'in USA', 'in UK', 'in Germany', 'in France', 'in Spain', 'in Italy',
    'in Netherlands', 'in Belgium', 'in Sweden', 'in Australia', 'in Canada',
]

# ---- Layer 2: local-language queries (hand-crafted, high supplier density) ----
REGIONAL2 = [
    # Arabic — more countries & verticals
    ('MENA','ar','موزع كروت شحن وألعاب بالجملة الامارات'),
    ('MENA','ar','موزع بطاقات جوجل بلاي وآيتونز بالجملة السعودية'),
    ('MENA','ar','توكيل بطاقات رقمية معتمد الكويت'),
    ('MENA','ar','موزع بطاقات شحن ببجي و فري فاير قطر'),
    ('MENA','ar','جملة اشتراكات نتفلكس وشاهد العراق'),
    ('MENA','ar','موزع بطاقات رقمية عمان مسقط'),
    ('MENA','ar','تاجر جملة بطاقات هدايا البحرين'),
    ('MENA','ar','موزع بطاقات شحن الأردن عمان'),
    ('MENA','ar','أرخص موزع بطاقات رقمية اليمن صنعاء'),
    ('MENA','ar','برنامج تجار بطاقات الشحن الرقمية لبنان'),
    ('MENA','ar','موزع معتمد بطاقات شحن موبايلي الاتصالات'),
    ('MENA','ar','منصة بيع بطاقات رقمية للأعضاء مصر API'),
    ('MENA','ar','موزع سماعات وبطاقات شحن جملة ليبيا'),
    ('MENA','ar','موزع بطاقات شحن سوداني جملة'),
    # Turkish
    ('TR','tr','oyun para yükleme bayilik toptan panel'),
    ('TR','tr','hediye kartı toptan satış bayilik programı'),
    ('TR','tr','dijital ürün toptan distribütör API entegrasyon'),
    ('TR','tr','epin toptan dağıtım platformu bayilik'),
    ('TR','tr','mobil ödeme dijital ürün toptan tedarikçi'),
    # Indonesian (huge topup market)
    ('ID','id','distributor pulsa h2h harga master'),
    ('ID','id','server pulsa murah untuk agen PPOB'),
    ('ID','id','distributor voucher game harga distributor API'),
    ('ID','id','agen resmi top up game diamond murah'),
    ('ID','id','supplier token listrik dan pulsa h2h'),
    ('ID','id','distributor produk digital untuk webtopup'),
    ('ID','id','jasa pembuatan website topup game harga distributor'),
    ('ID','id','distributor google play gift card indonesia'),
    # Vietnamese
    ('VN','vi','đại lý phân phối thẻ game giá gốc'),
    ('VN','vi','nap game tự động API giá sỉ'),
    ('VN','vi','nhà phân phối thẻ cào điện thoại giá sỉ'),
    ('VN','vi','trang web bán thẻ game giá đại lý'),
    # Thai
    ('TH','th','ผู้แทนจำหน่ายบัตรเติมเกมราคาส่ง API'),
    ('TH','th','รับขายบัตรเติมเงินสตีมราคาส่ง'),
    # Malay / SG
    ('MY','en','game credit supplier wholesale Malaysia reseller'),
    ('MY','ms','pengedar top up game murah harga borong'),
    ('PH','en','loading business supplier wholesale Philippines'),
    ('PH','en','game credits reseller panel Philippines'),
    # South Asia
    ('IN','en','recharge API provider wholesale India distributor'),
    ('IN','en','game diamond distributor reseller India B2B'),
    ('IN','hi','गेम टॉपअप सप्लायर डिस्ट्रीब्यूटर थोक'),
    ('PK','en','easyload jazz card wholesale distributor Pakistan'),
    ('PK','ur','گیم ٹاپ اپ ڈسٹریبیوٹر تھوک پاکستان'),
    ('BD','bn','গেম টপ আপ ডিস্ট্রিবিউটর পাইকারি বাংলাদেশ'),
    ('BD','en','mobile recharge wholesale distributor Bangladesh'),
    ('LK','en','mobile reload wholesale distributor Sri Lanka'),
    ('NP','en','mobile top up distributor API Nepal'),
    # East Asia
    ('JP','ja','ゲーム課金 代行 卸 API 事業'),
    ('JP','ja','ギフトカード 卸売 代理店 募集'),
    ('KR','ko','게임 충전소 솔루션 도매 유통'),
    ('KR','ko','기프트카드 총판 도매 공급'),
    ('CN','zh','游戏点卡批发平台 代理加盟 API'),
    ('CN','zh','数字礼品卡批发 供货商 平台'),
    ('TW','zh','遊戲點數經銷 批發 代理'),
    ('HK','zh','遊戲點卡 批發 分銷商'),
    # Africa
    ('NG','en','data and airtime reseller platform Nigeria API'),
    ('NG','en','bulk SMS and data platform Nigeria reseller'),
    ('KE','en','airtime data reseller API Kenya wholesale'),
    ('GH','en','telecom airtime reseller Ghana API'),
    ('UG','en','airtime reseller platform Uganda'),
    ('TZ','en','airtime and bundles reseller Tanzania'),
    ('ZA','en','voucher and prepaid distributor South Africa'),
    ('ET','en','telecom airtime distributor Ethiopia API'),
    ('MA','fr','distributeur recharge télécom Maroc grossiste'),
    ('DZ','ar','موزع بطاقات شحن جيزي وموبيليس الجزائر'),
    ('TN','ar','موزع بطاقات شحن أوريدو تونس جملة'),
    ('CI','fr','distributeur crédit téléphone Côte d Ivoire'),
    ('SN','fr','distributeur crédit téléphonique Sénégal grossiste'),
    # LatAm
    ('BR','pt','distribuidor gift card atacado plataforma B2B'),
    ('BR','pt','fornecedor recarga games atacado API'),
    ('BR','pt','revenda recarga digital painel API'),
    ('MX','es','distribuidor tarjetas de regalo al mayoreo México'),
    ('MX','es','proveedor recargas PVS API mayorista'),
    ('AR','es','mayorista tarjetas de regalo digitales Argentina'),
    ('CO','es','distribuidor recargas y tarjetas digitales Colombia'),
    ('CL','es','distribuidor tarjetas de regalo Chile mayoreo'),
    ('PE','es','distribuidor tarjetas digitales Perú recargas'),
    ('EC','es','distribuidor recargas Ecuador tarjetas digitales'),
    ('DO','es','distribuidor recargas República Dominicana'),
    ('GT','es','distribuidor tarjetas de regalo Guatemala'),
    # Europe / CIS
    ('PL','pl','dystrybutor doładowań i kart cyfrowych hurt'),
    ('PL','en','game key wholesale distributor Poland'),
    ('RO','ro','distribuitor reincarcari si carduri digitale en gros'),
    ('RO','en','gift card wholesale distributor Romania'),
    ('BG','bg','дистрибутор цифрови карти и зареждания едро'),
    ('CZ','cs','distributor dobití a digitálních karet velkoobchod'),
    ('UA','uk','дистриб' + 'ютор ігрових карток та поповнення гуртом API'),
    ('UA','en','game topup wholesale distributor Ukraine'),
    ('RU','ru','дистрибьютор игровых карт пополнение опт API'),
    ('RU','ru','платформа цифровых товаров опт партнерская программа'),
    ('KZ','ru','дистрибьютор пополнений игр Казахстан опт API'),
    ('UZ','ru','пополнение игр дистрибьютор Узбекистан API опт'),
    ('UZ','uz','o‘yin to‘ldirish distribyutori ulgur'),
    ('KG','ru','пополнение игр Киргизия дистрибьютор опт'),
    ('AM','hy','խաղի լիցքավորման դիստրիբյուտոր մեծածախ'),
    ('AM','ru','пополнение игр Армения дистрибьютор опт'),
    ('AZ','ru','пополнение игр Азербайджан дистрибьютор опт API'),
    ('GE','ru','пополнение игр Грузия дистрибьютор опт'),
    ('BY','ru','дистрибьютор цифровых товаров Беларусь опт'),
    ('MD','ru','пополнение игр Молдова дистрибьютор опт'),
    # Europe West
    ('DE','de','Großhändler digitale Güter Geschenkkarten B2B'),
    ('DE','en','gift card wholesale distributor Germany DACH'),
    ('FR','fr','distributeur cartes cadeaux digitales grossiste'),
    ('FR','en','gift card B2B distributor France'),
    ('ES','es','mayorista tarjetas regalo digitales España'),
    ('IT','it','distributore gift card digitali all ingrosso'),
    ('NL','en','gift card wholesale distributor Netherlands Benelux'),
    ('SE','en','gift card distributor Nordics wholesale'),
    ('UK','en','gift card wholesale distributor UK trade platform'),
    ('GR','el','χονδρέμπορος ψηφιακών καρτών και充值'),  # note: mixed; kept for diversity probe
    ('RS','en','game key distributor Balkans wholesale'),
    ('HR','en','digital goods distributor Croatia wholesale'),
    ('LT','en','game key wholesale distributor Baltics'),
    # North America / Oceania
    ('US','en','gift card wholesale distributor USA B2B trade'),
    ('US','en','prepaid wireless topup distributor wholesale USA'),
    ('CA','en','gift card wholesale distributor Canada'),
    ('AU','en','gift card wholesale distributor Australia'),
    # Central Asia / MENA extra
    ('IQ','ar','موزع بطاقات شحن آسياسيل وزين العراق'),
    ('YE','ar','موزع بطاقات شحن يمن موبايل جملة'),
    ('SY','ar','موزع بطاقات شحن سيرياتيل موبيل جملة'),
    ('LB','ar','موزع بطاقات شحن الفا ألفا جملة لبنان'),
    ('JO','ar','موزع بطاقات شحن أورنج وزين الأردن'),
    ('LY','ar','موزع بطاقات شحن الليثام والمدارى ليبيا'),
    ('SD','ar','موزع بطاقات شحن زين سوداني'),
    ('PS','ar','موزع بطاقات شحن جوال وجوالي فلسطين'),
    ('MR','ar','موزع بطاقات شحن موريتانيا جملة'),
    ('DJ','ar','موزع بطاقات شحن جيبوتي'),
    ('SO','en','airtime reseller distributor Somalia'),
    ('GLOBAL','en','digital gift card wholesale API for developers'),
    ('GLOBAL','en','game topup API provider list resellers'),
    ('GLOBAL','en','prepaid content distribution platform telco'),
    ('GLOBAL','en','gift card trade desk B2B platform'),
    ('GLOBAL','en','digital goods supply platform for kiosks'),
    ('GLOBAL','en','loyalty program gift card fulfillment API'),
    ('GLOBAL','en','telco recharge hub API wholesale'),
    ('GLOBAL','en','white label topup wallet platform solution'),
    ('GLOBAL','en','esim connectivity reseller API platform'),
    ('GLOBAL','en','cross border digital goods distributor'),
]

def main():
    with open(f'{GS}/queries.json') as f:
        plan = json.load(f)
    existing_ids = {q['id'] for q in plan['queries']}
    seen = set(existing_ids)
    queries = plan['queries']
    wave_of = {q['id']: q.get('wave', 1) for q in queries}
    for q in queries: q.setdefault('wave', 1)

    def add(region, lang, family, q, wave):
        qid = hashlib.md5(q.encode()).hexdigest()[:10]
        if qid in seen: return 0
        seen.add(qid)
        queries.append({'id': qid, 'region': region, 'lang': lang, 'family': family, 'q': q, 'wave': wave})
        return 1

    added = 0
    for fam, tpl in FAMILIES2:
        for r in REGIONS2:
            added += add(r if r != 'worldwide' else 'GLOBAL', 'en', fam, tpl.format(R=r), 2)
    for region, lang, q in REGIONAL2:
        added += add(region, lang, 'regional_local2', q, 2)

    plan['total'] = len(queries)
    plan['generated'] = datetime.now().isoformat()
    plan['waves'] = {'wave1': sum(1 for q in queries if q.get('wave',1)==1), 'wave2': sum(1 for q in queries if q.get('wave',2)==2)}
    with open(f'{GS}/queries.json','w') as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    print(f"Wave-2 added {added} new queries | total plan: {len(queries)}")
    print(f"  wave1: {plan['waves']['wave1']} | wave2: {plan['waves']['wave2']}")

if __name__ == '__main__':
    main()
