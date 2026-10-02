#!/usr/bin/env python3
# SV-MATRIX-2b: comprehensive family classification — all 357 products
import json, re
from collections import defaultdict

OUT = '/home/z/my-project/research/stackvault_live'
data = json.load(open(f'{OUT}/sv_products_current.json'))
prods = data if isinstance(data, list) else data.get('products', [])

def clean(n):
    n = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u2B50]', '', n).strip()
    return re.sub(r'\s+', ' ', n)

FAMS = [
    ('ChatGPT Plus شهري — مضمون', ['chatgpt plus 1 month full', 'chatgpt plus apple pay 1 month', 'chatgpt plus apple pay 30', 'chatgpt plus gmail 30', 'chatgpt plus 30 days (7 days', 'gpt plus apple 30d', 'renew official chatgpt plus', 'chatgpt plus applepay 1 month', 'chatgpt plus vipp']),
    ('ChatGPT Plus شهري — ضمان قصير/بدون', ['chatgpt plus 1 month (5h', 'chatgpt plus 1 month - 6h', 'chatgpt plus upi domain', 'chatgpt plus 1 month (fast upi', 'chat gpt plus (pay upi)', 'chatgpt plus pay upi', 'chatgpt plus ggpay', 'chatgpt plus gpay', 'chatgpt plus 1 month pay upi', 'gpt plus apple/ggpay 30d no']),
    ('ChatGPT Plus — عروض مجانية/طلاب', ['chatgpt offers plus', 'chatgpt ver students', 'chat gpt has been versioned for students', 'chatgpt free has phone']),
    ('ChatGPT Business/Slots', ['chatgpt business', 'acc chat gpt business', 'slot gpt business', 'shared chatgpt']),
    ('ChatGPT Go/Pro', ['chatgpt go', 'chatgpt pro x5']),
    ('ChatGPT K12 + Codex (سنتان)', ['k12']),
    ('ChatGPT Plus — مستويات طويلة', ['level 4']),
    ('رصيد Codex/Astra (teamsoclo)', ['credit api codex', 'token codex', 'gpt-6-astra']),
    ('رصيد AI — DeepSeek/Cursor/Kiro/MiniMax/ElevenLabs', ['deepseek api', 'api cursor', 'kiro', 'minimax', 'elevenlab']),
    ('رصيد AI فيديو/صوت — Runway/Kling/Seedance/Suno/Gamma', ['runway', 'kling', 'seedance', 'suno', 'gamma', 'domo ai', 'heygen', 'flux 03', 'krea', 'lartai', 'photoroom', 'tryclico', 'dropshot']),
    ('Gemini — 18 شهرًا', ['gemini pro 18', 'gemini 18']),
    ('Gemini — SLOT/GG', ['slot gemini']),
    ('Office 365 Plus سنوي', ['office 365 plus 1 year', 'office 365 plus 12m', 'ms office 365 plus 12m']),
    ('Office/Microsoft — عروض أخرى', ['office 365', 'office 2024', 'microsoft 365', 'ms365', 'admin ms365', 'copilot', 'office admin']),
    ('Windows/برامج — مفاتيح', ['windows 10', 'genuine windows', 'avira', 'hma', 'autodesk', 'autodesk', 'key hma']),
    ('Outlook/Hotmail حسابات', ['outlook', 'hotmail']),
    ('Gmail — حسابات', ['gmail']),
    ('Apple — iCloud/Apple ID', ['apple id', 'icloud']),
    ('CapCut Pro', ['capcut']),
    ('Discord — Boosts/Nitro', ['boost', 'nitro']),
    ('Decor — Discord', ['decor']),
    ('X/Twitter — Premium/حسابات', ['x premium', 'upgrade x', 'account x stock']),
    ('Canva', ['canva']),
    ('Figma', ['figma']),
    ('Adobe', ['adobe']),
    ('Spotify', ['spotify']),
    ('YouTube Premium', ['youtube']),
    ('Amazon Prime', ['amazon prime']),
    ('Apple Music', ['apple music']),
    ('HBO/Streaming أخرى', ['hbo']),
    ('أكواد شركات ناشئة — Framer/Notion/Linear/Manus/Factory', ['framer', 'notion', 'linear business', 'manus', 'factory 12m', 'granola', 'gumloop', 'mobbin', 'posthog', 'resend', 'supercut', 'warp build', 'jam team', 'magic pattern', 'lovable', 'replit', 'grok bot', 'bolt', 'n8n', 'railway', 'gpm']),
    ('تعليم — Coursera/Udemy/JetBrains/Kahoot/Quizlet', ['coursera', 'udemy', 'jetbrain', 'kahoot', 'quizlet', 'memrise', 'skillshare', 'scribd', 'duolingo', 'brain.fm', 'ilovepdf']),
    ('أدوات كتابة — Grammarly/Quillbot', ['grammarly', 'quillbot']),
    ('VPN', ['nord', 'proton', 'vpn', 'surfshark', 'surfark', 'proxyscrape']),
    ('LinkedIn', ['linkedin']),
    ('Zoom', ['zoom']),
    ('TikTok — حسابات بائعين', ['tiktok', 'tiktokvietnam', 'vietnamese tiktok']),
    ('Cloud — AWS/GCP', ['aws', 'gcp', 'google cloud']),
    ('AI أخرى — Perplexity/Claude/Miro/Freepik', ['perplexity', 'claude', 'miro', 'freepik', 'wispr', 'wisper']),
]

fam_rows, used = [], set()
for fam_name, kws in FAMS:
    items = []
    for i, p in enumerate(prods):
        nl = p['name'].lower()
        if any(k in nl for k in kws) and i not in used:
            items.append(p); used.add(i)
    if not items: continue
    costs = [p['costPrice'] for p in items if p['costPrice']]
    sells = [p['price'] for p in items if p['price']]
    routes = defaultdict(int)
    for p in items:
        routes['ProdSeller' if p['id'].startswith('ps_') else 'Evo_Era'] += 1
    ts = sum(1 for p in items if 'teamsoclo' in (p.get('description') or '').lower())
    fam_rows.append({'family': fam_name, 'n': len(items),
        'sample': clean(items[0]['name'])[:60],
        'cost_min': min(costs) if costs else 0, 'cost_max': max(costs) if costs else 0,
        'sell_min': min(sells) if sells else 0, 'sell_max': max(sells) if sells else 0,
        'routes': dict(routes), 'teamsoclo_n': ts, 'stock': sum(p.get('stock', 0) for p in items),
        'items': [{'name': clean(p['name']), 'sell': p['price'], 'cost': p['costPrice'],
                    'stock': p.get('stock', 0),
                    'route': 'ProdSeller' if p['id'].startswith('ps_') else ('Evo_Era' if p['id'].startswith('mr_') else 'اختبار')} for p in items]})
rest = [p for i, p in enumerate(prods) if i not in used]
if rest:
    costs = [p['costPrice'] for p in rest if p['costPrice']]
    fam_rows.append({'family': 'أخرى — غير مصنفة', 'n': len(rest), 'sample': clean(rest[0]['name'])[:60],
        'cost_min': min(costs) if costs else 0, 'cost_max': max(costs) if costs else 0,
        'sell_min': min(p['price'] for p in rest), 'sell_max': max(p['price'] for p in rest),
        'routes': {'مختلط': len(rest)}, 'teamsoclo_n': 0, 'stock': sum(p.get('stock',0) for p in rest),
        'items': [{'name': clean(p['name']), 'sell': p['price'], 'cost': p['costPrice'], 'stock': p.get('stock',0),
                    'route': 'ProdSeller' if p['id'].startswith('ps_') else ('Evo_Era' if p['id'].startswith('mr_') else 'اختبار')} for p in rest]})

json.dump(fam_rows, open(f'{OUT}/matrix_families.json', 'w'), ensure_ascii=False, indent=1)
print(f'{len(fam_rows)} families | covered {sum(f["n"] for f in fam_rows)}/{len(prods)} | unclassified: {len(rest)}')
for f in fam_rows: print(f"  {f['n']:3d} | {f['family'][:52]:52s} | ${f['cost_min']}-{f['cost_max']}")
