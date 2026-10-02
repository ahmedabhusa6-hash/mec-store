#!/usr/bin/env python3
# SV-MATRIX-1: Build consolidated price database from ALL observed suppliers/stores
import json, re
from datetime import datetime, timezone

OUT = '/home/z/my-project/research/stackvault_live'
price_db = {'generated': datetime.now(timezone.utc).isoformat(), 'sources': {}}

# ============ 1. StackVault catalog (current costs = what SV pays now) ============
data = json.load(open(f'{OUT}/sv_products_current.json'))
prods = data if isinstance(data, list) else data.get('products', [])
sv = []
for p in prods:
    route = 'ProdSeller-API' if p['id'].startswith('ps_') else ('يدوي Evo_Era' if p['id'].startswith('mr_') else 'اختبار')
    ts = 'نعم' if 'teamsoclo' in (p.get('description') or '').lower() else ''
    sv.append({'id': p['id'], 'name': p['name'], 'category': p.get('categoryName',''),
               'sell': p.get('price'), 'cost': p.get('costPrice'), 'stock': p.get('stock', 0),
               'route': route, 'teamsoclo': ts})
price_db['sources']['stackvault_catalog'] = sv

# ============ 2. Channel price evidence (all suppliers/stores) ============
ch = json.load(open('/home/z/my-project/research/b3_channel_history.json'))
evidence = []
# ProdSeller announcements
PS_PATTERNS = [
    # (regex, product, tier)
    (r'GEMINI.*?\$([0-9.]+)\s*/?\s*account.*?BULK.*?\$([0-9.]+)', 'Gemini 18 شهرًا', 'wholesale'),
    (r'LINK:\s*\$([0-9.]+).*?API USER:\s*\$([0-9.]+)', 'Gemini 18 شهرًا', 'api'),
    (r'OFFICE 365 PLUS.*?Personal Account:\s*\$([0-9.]+).*?Bulk & API.*?\$([0-9.]+)', 'Office 365 Plus', 'wholesale'),
    (r'Chatgpt K12 with codex.*?Price\s*([0-9.]+)\$.*?([0-9.]+)\$?\s*for api', 'ChatGPT Plus K12 + Codex', 'api'),
]
for m_ in ch.get('ProdSellerOfficial', {}).get('messages', []):
    t = m_.get('text', '')
    d = m_.get('date', '')[:10]
    if 'Gemini' in t and '$' in t:
        for mm in re.finditer(r'(?:\$|Price:\s*)([0-9.]+)', t):
            pass
        # capture raw
        evidence.append({'date': d, 'channel': 'ProdSeller', 'message': t[:250], 'product_hint': t[:60]})
    elif 'OFFICE' in t.upper() and '$' in t:
        evidence.append({'date': d, 'channel': 'ProdSeller', 'message': t[:250], 'product_hint': t[:60]})
    elif 'K12' in t or 'codex' in t.lower():
        evidence.append({'date': d, 'channel': 'ProdSeller', 'message': t[:250], 'product_hint': t[:60]})
    elif '$' in t and len(t) > 20:
        evidence.append({'date': d, 'channel': 'ProdSeller', 'message': t[:250], 'product_hint': t[:60]})

# Evo_Era announcements
for m_ in ch.get('Evo_Era_updates', {}).get('messages', []):
    t = m_.get('text', '')
    d = m_.get('date', '')[:10]
    if any(x in t for x in ['USDT', 'Price', 'PRICE', 'FLASH', 'restocked', 'NEW PRODUCT']):
        evidence.append({'date': d, 'channel': 'Evo_Era', 'message': t[:250], 'product_hint': t[:60]})

# HitMeow
for m_ in ch.get('HitMeowShop', {}).get('messages', []):
    t = m_.get('text', '')
    d = m_.get('date', '')[:10]
    if '$' in t:
        evidence.append({'date': d, 'channel': 'HitMeowShop', 'message': t[:250], 'product_hint': t[:60]})

# AISUBSID
for m_ in ch.get('AISUBSID', {}).get('messages', []):
    t = m_.get('text', '')
    d = m_.get('date', '')[:10]
    if '$' in t or 'IDR' in t:
        evidence.append({'date': d, 'channel': 'AISUBSID', 'message': t[:250], 'product_hint': t[:60]})

# gemini12pro (promos incl AiVerseX)
for m_ in ch.get('gemini12pro_channel', {}).get('messages', []):
    t = m_.get('text', '')
    d = m_.get('date', '')[:10]
    if '$' in t or 'Price' in t:
        evidence.append({'date': d, 'channel': 'AiVerseX/promos', 'message': t[:250], 'product_hint': t[:60]})

price_db['channel_evidence'] = evidence
price_db['n_evidence'] = len(evidence)

# ============ 3. Structured best-known prices (manually verified from evidence) ============
price_db['best_prices'] = {
    'chatgpt_plus_1m': {
        'sv_costs': sorted([p['cost'] for p in sv if 'chatgpt plus 1 month' in p['name'].lower() and p['cost']])[:3],
        'alternatives': [
            {'supplier': 'AISUBSID', 'price': 2.90, 'condition': 'طلب مسبق 20+ وحدة', 'channel': '@Aisubsglobalbot', 'date': '2026-09-26'},
            {'supplier': 'AISUBSID', 'price': 3.10, 'condition': 'فردي (131 حساب متاح)', 'channel': '@Aisubsglobalbot', 'date': '2026-09-24'},
            {'supplier': 'HitMeowShop', 'price': 11.65, 'condition': 'ضمان كامل VIP', 'channel': 't.me/HitMeowShop', 'date': '2026-09-11'},
            {'supplier': 'AiVerseX', 'price': 1.00, 'condition': '"From $1" عرض ترويجي — يرجى التحقق', 'channel': '@AiVerseXBot', 'date': '2026-08-19'},
        ]},
    'k12_codex': {
        'sv_costs': [4.62],
        'alternatives': [
            {'supplier': 'ProdSeller (معلن)', 'price': 3.80, 'condition': 'سعر API المعلن رسميًا — SV يدفع 4.62!', 'channel': '@prodsellerbot', 'date': '2026-09-20'},
            {'supplier': 'HitMeowShop', 'price': 3.85, 'condition': 'K12 Edu سنتان ضمان 24س', 'channel': 't.me/HitMeowShop', 'date': '2026-09-10'},
        ]},
    'office365_plus_1y': {
        'sv_costs': [0.21, 0.70],
        'alternatives': [
            {'supplier': 'ProdSeller (معلن)', 'price': 0.17, 'condition': 'Bulk & API المعلن رسميًا — SV يدفع 0.21', 'channel': '@prodsellerbot', 'date': '2026-09-19'},
        ]},
    'gemini_18m': {
        'sv_costs': [0.39],
        'alternatives': [
            {'supplier': 'AiVerseX', 'price': 0.45, 'condition': 'جملة عبر @Gt_Verified', 'channel': '@AiVerseXBot', 'date': '2026-07-14'},
            {'supplier': 'ProdSeller API', 'price': 0.50, 'condition': 'سعر API', 'channel': '@prodsellerbot', 'date': '2026-09-19'},
            {'supplier': 'AiVerseX فردي', 'price': 0.85, 'condition': 'تجزئة', 'channel': '@AiVerseXBot', 'date': ''},
        ]},
    'codex_credits': {
        'sv_costs': 'via ProdSeller فوق teamsoclo (~20% هامش مزدوج)',
        'alternatives': [
            {'supplier': 'teamsoclo مباشرة', 'price': None, 'condition': 'برنامج Reseller — يقطع هامش ProdSeller (~15-25%)', 'channel': 't.me/teamsoclo', 'date': '2026-09-29'},
            {'supplier': 'HitMeowShop', 'price': 7.68, 'condition': 'Claude Unlimited API يومي (31 موديل) — بديل كثيف الاستخدام', 'channel': 't.me/HitMeowShop', 'date': '2026-09-19'},
        ]},
    'capcut_7d': {
        'sv_costs': [0.04],
        'alternatives': [
            {'supplier': 'AiVerseX', 'price': 0.35, 'condition': 'SV أرخص 9 أضعاف — لا تغيّر', 'channel': '@AiVerseXBot', 'date': '2026-07-31'},
        ]},
    'manus_pro_12m': {
        'sv_costs': [20.00],
        'alternatives': [
            {'supplier': 'Evo_Era', 'price': 33.00, 'condition': 'فلاش (ينتهي ويعود 37) — SV يدفع 20 أصلاً أرخص', 'channel': 'بوت Evo_Era', 'date': '2026-09-26'},
        ]},
    'framer_pro_12m': {
        'sv_costs': [12.00],
        'alternatives': [
            {'supplier': 'Evo_Era', 'price': 10.50, 'condition': 'فلاش — أرخص من تكلفة SV الحالية 12', 'channel': 'بوت Evo_Era', 'date': '2026-09-26'},
        ]},
    'grok_bot_cursor': {
        'sv_costs': [21.00],
        'alternatives': [
            {'supplier': 'Evo_Era', 'price': 35.00, 'condition': 'فلاش (عاد إلى 40)', 'channel': 'بوت Evo_Era', 'date': '2026-09-26'},
        ]},
}

# ============ 4. Suppliers & stores directory ============
price_db['directory'] = [
    {'name': 'ProdSeller', 'type': 'موزع جملة + API (المورد الرئيسي 89%)', 'channel': 't.me/ProdSellerOfficial + @prodsellerbot',
     'admin': '@sookbit', 'payment': 'USDT', 'risk': 'متوسط — ادعاءات حجم غير قابلة للتحقق، نموذج API مستقر نسبيًا',
     'scale': '15K+ مستخدم، 8K+ نشط شهريًا، 500+ مستخدم API (مزعوم)'},
    {'name': 'Team Sóc Lọ (teamsoclo)', 'type': 'مصنع رصيد AI فيتنامي (عبر ProdSeller حاليًا)', 'channel': 't.me/teamsoclo + gpt.teamsoclo.site',
     'admin': 'عبر Reseller فقط', 'payment': 'غير معلن', 'risk': 'عالٍ — عمر 3 أسابيع، مجهول الهوية، قيود OpenAI نشطة',
     'scale': 'قناة 154 مشتركًا — B2B للمتاجر'},
    {'name': 'Evo Era', 'type': 'بائع تجزئة آلي (المصدر اليدوي mr_)', 'channel': 't.me/Evo_Era_updates + بوت',
     'admin': 'غير معلن', 'payment': 'USDT', 'risk': 'متوسط-عالٍ — ضمانات قصيرة، أسعار فلاش متقلبة',
     'scale': 'قناة 2,319 مشتركًا، إشعارات مشتريات حية'},
    {'name': 'AISUBSID', 'type': 'مزرعة حسابات ChatGPT (إندونيسيا)', 'channel': '@Aisubsglobalbot',
     'admin': 'قناة AISUBSID', 'payment': 'USDT/IDR', 'risk': 'متوسط — حجم كبير 131+ حساب، أسعار صاعدة',
     'scale': 'astock 250+ حساب، جملة 20+'},
    {'name': 'HitMeowShop', 'type': 'بائع حسابات ChatGPT مميزة + Claude API', 'channel': 't.me/HitMeowShop',
     'admin': 'غير معلن', 'payment': 'غير معلن', 'risk': 'متوسط — سجل مبيعات موثق (3,792 حساب)',
     'scale': 'VIP + K12 + Claude Unlimited API'},
    {'name': 'AiVerseX Hub', 'type': 'متجر عروض متنوع (Gemini/CapCut/VPN)', 'channel': '@AiVerseXBot + aiversehub.store',
     'admin': '@Gt_Verified للجملة', 'payment': 'غير معلن', 'risk': 'متوسط — عروض ترويجية مدفوعة عبر قنوات أخرى',
     'scale': 'Gemini 3804 وحدة متاحة'},
    {'name': 'StackVault', 'type': 'المتجر محل التحليل', 'channel': 'stackvault.shop + t.me/stackvault_bot',
     'admin': 'غير معلن', 'payment': 'غير معلن', 'risk': '—',
     'scale': '354 منتجًا، هامش متوسط 25%'},
]

json.dump(price_db, open(f'{OUT}/price_database.json', 'w'), ensure_ascii=False, indent=1)
print(f"price_database.json: {len(sv)} SV products, {len(evidence)} evidence rows, {len(price_db['directory'])} directory entries")
# Quick validation of key facts
assert any(p['route'] == 'يدوي Evo_Era' for p in sv), 'mr_ route missing'
print('OK')
