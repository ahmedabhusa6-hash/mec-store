#!/usr/bin/env python3
# SV-MATRIX-3: Generate comprehensive Arabic RTL negotiation matrix workbook
import json, sys, os
XLSX_SKILL_DIR = "/home/z/my-project/skills/xlsx"
for sub in [XLSX_SKILL_DIR, os.path.join(XLSX_SKILL_DIR, "templates")]:
    if sub not in sys.path: sys.path.insert(0, sub)
import base
from base import *  # design tokens + helpers
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---- Arabic font override (Arial has universal Arabic support in Excel) ----
AR_FONT = 'Arial'
base.FONT_NAME = AR_FONT
FONT_NAME = AR_FONT
HEADER_BOLD = True  # Arial handles bold well

OUT = '/home/z/my-project/research/stackvault_live'
DL = '/home/z/my-project/download'

fams = json.load(open(f'{OUT}/matrix_families.json'))
pdb = json.load(open(f'{OUT}/price_database.json'))
gds = json.load(open('/home/z/my-project/download/gds_qualified_entities.json'))['entities']

wb = Workbook()
wb.properties.creator = "Z.ai"

def rtl(ws):
    ws.sheet_view.rightToLeft = True
    ws.sheet_view.showGridLines = False

def style_range(ws, row, c1, c2, font=None, fill=None, align=None, border=None, numfmt=None):
    for c in range(c1, c2+1):
        cell = ws.cell(row=row, column=c)
        if font: cell.font = font
        if fill: cell.fill = fill
        if align: cell.alignment = align
        if border: cell.border = border
        if numfmt: cell.number_format = numfmt

def make_sheet(ws, title, headers, widths=None, subtitle=None):
    rtl(ws)
    last_col = len(headers) + 1
    ws.merge_cells(start_row=2, start_column=2, end_row=2, end_column=last_col)
    tc = ws.cell(row=2, column=2, value=title)
    tc.font = Font(name=FONT_NAME, size=16, bold=True, color=PRIMARY)
    tc.alignment = Alignment(horizontal='right', vertical='center')
    ws.row_dimensions[1].height = 15
    ws.row_dimensions[2].height = 32
    if subtitle:
        ws.merge_cells(start_row=3, start_column=2, end_row=3, end_column=last_col)
        sc = ws.cell(row=3, column=2, value=subtitle)
        sc.font = Font(name=FONT_NAME, size=9, color=NEUTRAL_600)
        sc.alignment = Alignment(horizontal='right', vertical='center')
        ws.row_dimensions[3].height = 14
    for i, h in enumerate(headers, 2):
        ws.cell(row=4, column=i, value=h)
    style_range(ws, 4, 2, last_col,
                font=Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF"),
                fill=PatternFill('solid', fgColor=PRIMARY),
                align=Alignment(horizontal='center', vertical='center', wrap_text=True),
                border=Border(bottom=Side(style='thin', color=NEUTRAL_200)))
    ws.row_dimensions[4].height = 30
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    ws.column_dimensions['A'].width = 3
    return last_col

def data_row(ws, r, vals, idx, c1, c2, numfmts=None, color_map=None):
    fill = PatternFill('solid', fgColor=NEUTRAL_0 if idx % 2 == 0 else NEUTRAL_100)
    for j, v in enumerate(vals):
        c = ws.cell(row=r, column=c1 + j, value=v)
        c.font = Font(name=FONT_NAME, size=11, color=NEUTRAL_900)
        c.fill = fill
        c.alignment = Alignment(horizontal='right' if isinstance(v, str) else 'left', vertical='center', wrap_text=True)
        if numfmts and numfmts.get(j): c.number_format = numfmts[j]
        if color_map and j in color_map and isinstance(v, (int, float)):
            if v > 0: c.font = Font(name=FONT_NAME, size=11, color=ACCENT_POSITIVE, bold=True)
            elif v < 0: c.font = Font(name=FONT_NAME, size=11, color=ACCENT_NEGATIVE, bold=True)
    ws.row_dimensions[r].height = 24

USD = '$#,##0.00'
PCT = '0.0%'

# ================= Sheet 1: الملخص التنفيذي =================
ws = wb.active
ws.title = 'الملخص التنفيذي'
rtl(ws)
ws.column_dimensions['A'].width = 3
ws.merge_cells('B2:J2')
t = ws.cell(row=2, column=2, value='مصفوفة التفاوض الشاملة — StackVault وجميع الموردين والمتاجر')
t.font = Font(name=FONT_NAME, size=18, bold=True, color=PRIMARY)
t.alignment = Alignment(horizontal='right', vertical='center')
ws.row_dimensions[2].height = 36
ws.merge_cells('B3:J3')
st = ws.cell(row=3, column=2, value='مبني على رصد مباشر حيّ بتاريخ 2026-09-29 — كتالوج 357 منتجًا + 6 قنوات موردين + قاعدة 230 كيان موزع رقمي')
st.font = Font(name=FONT_NAME, size=10, color=NEUTRAL_600)
st.alignment = Alignment(horizontal='right', vertical='center')

kpis = [
    ('إجمالي منتجات الكتالوج', 357, 'كتالوج حي من decohomz.com/sv-api'),
    ('حصة ProdSeller (المورد الرئيسي)', '89.3%', '319 منتجًا عبر تكامل API — بادئة ps_'),
    ('المصدر اليدوي Evo_Era', '10.4%', '37 منتجًا — بادئة mr_ — أكواد شركات ناشئة'),
    ('الهامش الوسطي', '25.1%', 'هوامش 15% إلى 154% حسب العائلة'),
    ('فرص وفر مؤكدة', 6, 'موثقة بأدلة من قنوات الموردين أنفسهم'),
    ('أعلى وفر ممكن', '46%', 'ChatGPT Plus عبر AISUBSID جملة $2.90'),
]
r = 5
for i, (label, val, note) in enumerate(kpis):
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
    lc = ws.cell(row=r, column=2, value=label)
    lc.font = Font(name=FONT_NAME, size=12, bold=True, color=PRIMARY)
    lc.alignment = Alignment(horizontal='right', vertical='center')
    lc.fill = PatternFill('solid', fgColor=NEUTRAL_100 if i % 2 else NEUTRAL_0)
    vc = ws.cell(row=r, column=5, value=val)
    vc.font = Font(name=FONT_NAME, size=14, bold=True, color=ACCENT_POSITIVE if isinstance(val, str) and '%' in str(val) or val == 6 else PRIMARY)
    vc.alignment = Alignment(horizontal='center', vertical='center')
    vc.fill = PatternFill('solid', fgColor=NEUTRAL_100 if i % 2 else NEUTRAL_0)
    ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=10)
    nc = ws.cell(row=r, column=6, value=note)
    nc.font = Font(name=FONT_NAME, size=10, color=NEUTRAL_600)
    nc.alignment = Alignment(horizontal='right', vertical='center')
    nc.fill = PatternFill('solid', fgColor=NEUTRAL_100 if i % 2 else NEUTRAL_0)
    ws.row_dimensions[r].height = 26
    r += 1

r += 1
ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=10)
h = ws.cell(row=r, column=2, value='أهم 6 فرص وفر (مرتبة بالأولوية)')
h.font = Font(name=FONT_NAME, size=13, bold=True, color=PRIMARY)
h.alignment = Alignment(horizontal='right', vertical='center')
r += 1
tops = [
    ('1', 'ChatGPT Plus شهري', 'AISUBSID جملة 20+ وحدة @ $2.90', 'حاليًا $5.72+ (مضمون)', 'حتى 46%', '@Aisubsglobalbot'),
    ('2', 'رصيد Codex/Astra (22 منتجًا)', 'التعاقد المباشر مع teamsoclo كموزع', 'هامش ProdSeller المزدوج ~20%', '15-25%', 't.me/teamsoclo'),
    ('3', 'ChatGPT K12 + Codex', 'ProdSeller سعر API المعلن $3.80', 'SV يدفع $4.62', '18%', '@prodsellerbot'),
    ('4', 'Office 365 Plus سنوي', 'ProdSeller سعر الجملة المعلن $0.17', 'SV يدفع $0.21', '19%', '@prodsellerbot'),
    ('5', 'ChatGPT Plus ضمان قصير', 'AISUBSID فردي @ $3.10', 'SV يدفع $3.85', '19%', '@Aisubsglobalbot'),
    ('6', 'Framer Pro 12m', 'Evo_Era فلاش @ $10.50', 'SV يدفع $12.00', '12.5%', 'بوت Evo_Era'),
]
hdr = ['#', 'العائلة', 'البديل الأرخص', 'التكلفة الحالية', 'الوفر', 'قناة التواصل']
for j, hh in enumerate(hdr):
    c = ws.cell(row=r, column=2+j, value=hh)
    c.font = Font(name=FONT_NAME, size=11, bold=True, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor=PRIMARY)
    c.alignment = Alignment(horizontal='center', vertical='center')
ws.row_dimensions[r].height = 26
r += 1
for i, row in enumerate(tops):
    fill = PatternFill('solid', fgColor=NEUTRAL_0 if i % 2 == 0 else NEUTRAL_100)
    for j, v in enumerate(row):
        c = ws.cell(row=r, column=2+j, value=v)
        c.font = Font(name=FONT_NAME, size=11, color=NEUTRAL_900)
        c.fill = fill
        c.alignment = Alignment(horizontal='center' if j in (0, 4) else 'right', vertical='center', wrap_text=True)
        if j == 4: c.font = Font(name=FONT_NAME, size=11, bold=True, color=ACCENT_POSITIVE)
    ws.row_dimensions[r].height = 24
    r += 1
for i, w in enumerate([5, 24, 30, 26, 10, 18, 12], 2):
    ws.column_dimensions[get_column_letter(i)].width = w
r += 1
ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=10)
f = ws.cell(row=r, column=2, value='ملاحظة: الأسعار المرصودة من قنوات الموردين بتاريخ 2026-09-19 إلى 2026-09-29. لا تشكل عرضًا ملزمًا — استخدمها كنقاط ضغط تفاوضية فقط.')
f.font = Font(name=FONT_NAME, size=9, color=NEUTRAL_600)
f.alignment = Alignment(horizontal='right', vertical='center')
print('Sheet 1 done')

# ================= Sheet 2: مصفوفة التفاوض (الأساسية) =================
ws = wb.create_sheet('مصفوفة التفاوض')
headers = ['العائلة', 'عدد', 'المورد الحالي', 'التكلفة الحالية ($)', 'أفضل بديل / نقطة الضغط',
           'سعر البديل ($)', 'الوفر', 'قناة التواصل', 'ملاحظة تفاوضية']
lc = make_sheet(ws, 'مصفوفة التفاوض — 40 عائلة منتج × المورد × البديل × الوفر', headers,
                widths=[3, 34, 6, 16, 13, 40, 12, 9, 20, 44],
                subtitle='الوفر = (التكلفة الحالية − سعر البديل) ÷ التكلفة الحالية | القيم السالبة تعني أن SV أرخص بالفعل (احتفظ بالمورد)')

# negotiation data keyed by family name prefix
NEG = {
 'ChatGPT Plus شهري — مضمون': ('AISUBSID — جملة 20+ وحدة (مزرعة إندونيسية، اختر عينة أولًا)', 2.90, 5.72, '@Aisubsglobalbot', 'أقوى نقطة ضغط: AISUBSID يوفر حتى 46% — اعرضها على ProdSeller لمطابقة السعر قبل التحويل'),
 'ChatGPT Plus شهري — ضمان قصير/بدون': ('AISUBSID — فردي (131 حسابًا متاحًا)', 3.10, 3.85, '@Aisubsglobalbot', 'نفس طبقة الضمان تقريبًا — وفر 19% مباشرة'),
 'ChatGPT Plus — عروض مجانية/طلاب': ('فاوض مع ProdSeller على سعر حجم للطلبات 10+', None, None, '@prodsellerbot', 'سلع طرق مخصصة لا يوجد لها بديل مرصود — استغل حجم الشراء'),
 'ChatGPT Business/Slots': ('فاوض على قائمة أسعار API (أنت عميل API فعلي)', None, None, '@prodsellerbot', 'ProdSeller يمنح مستخدمي API أسعارًا مخفضة معلنة — اطلب الجدول كاملًا'),
 'ChatGPT Go/Pro': ('HitMeow — ChatGPT Pro 20x بخصم 20% عن الرسمي', None, 65.44, 't.me/HitMeowShop', 'منتج مكافئ للفئة العليا — قابل للمقارنة عند طلبات Pro'),
 'ChatGPT K12 + Codex (سنتان)': ('ProdSeller — سعر API المعلن رسميًا في قناته', 3.80, 4.62, '@prodsellerbot', 'دليل قاطع: القناة أعلنت $3.80 لAPI بتاريخ 20/09 — الفجوة 18% غير مبررة'),
 'ChatGPT Plus — مستويات طويلة': ('لا بديل مرصود — سلع نادرة', None, None, '@prodsellerbot', 'هوامش مرتفعة لكن الندرة تحمي السعر — راقب HitMeow VIP $10.76-11.98'),
 'رصيد Codex/Astra (teamsoclo)': ('teamsoclo مباشرة — برنامج Reseller يقطع الوسيط', None, None, 't.me/teamsoclo', 'الأهم استراتيجيًا: ProdSeller وسيط فوق teamsoclo — التعاقد المباشر يوفر ~20% على 23 منتجًا (أغلى فئات المتجر)'),
 'رصيد AI — DeepSeek/Cursor/Kiro/MiniMax/ElevenLabs': ('HitMeow — Claude Unlimited API يومي 31 موديل', 7.68, None, 't.me/HitMeowShop', 'للعملاء كثيفي الاستخدام: $7.68/يوم بلا حد توكنز أرخص من حزم الرصيد'),
 'رصيد AI فيديو/صوت — Runway/Kling/Seedance/Suno/Gamma': ('فاوض على حزم حجم + راقب عروض AiVerseX', None, None, '@AiVerseXBot', 'سوق متقلب — عروض فلاش متكررة في القنوات، ثبّت سعر إطار شهري'),
 'Gemini — 18 شهرًا': ('لا تغيّر — SV الأرخص في السوق', 0.45, 0.39, '—', 'تكلفة SV $0.39 أرخص من جملة AiVerseX ($0.45) وسعر API لProdSeller ($0.50) — ميزة تنافسية احتفظ بها'),
 'Gemini — SLOT/GG': ('فاوض على حجم', None, None, '@prodsellerbot', 'منتج فريد — لا بديل مرصود'),
 'Office 365 Plus سنوي': ('ProdSeller — سعر Bulk & API المعلن رسميًا', 0.17, 0.21, '@prodsellerbot', 'القناة أعلنت $0.17 بتاريخ 19/09 — الفجوة 19%، أنت مؤهل تلقائيًا كمستخدم API'),
 'Office/Microsoft — عروض أخرى': ('طبّق نفس مبدأ الجملة المعلن على كل عائلة Microsoft', 0.17, 0.96, '@prodsellerbot', 'ابدأ التفاوض من سعر $0.17 المعلن كحد أدنى مرجعي'),
 'Windows/برامج — مفاتيح': ('GDS: CodesWholesale — جملة مفاتيح API معتمد', None, None, 'codeswholesale.com', 'بديل مؤسسي لمفاتيح Windows/Office/Avira — قنوات توزيع رسمية أفضل لضمانات أطول'),
 'Outlook/Hotmail حسابات': ('لا تغيّر — تكلفة شبه معدومة', None, None, '—', '$0.02 للوحدة الموثوقة — أرخص بند في الكتالوج'),
 'Gmail — حسابات': ('فاوض على حزم 100+ وحدة', None, None, '@prodsellerbot', 'متوسط تكلفة معقول — لا بديل مرصود خارج شبكة ProdSeller'),
 'Apple — iCloud/Apple ID': ('لا بديل مرصود', None, None, '@prodsellerbot', 'سلع مخصصة — استقرار أهم من السعر هنا'),
 'CapCut Pro': ('لا تغيّر — SV الأرخص (7 أيام بـ$0.04)', 2.35, 1.25, '—', 'Evo_Era يبيع الشهري بـ$2.35 وتكلفة SV $1.25 — تفوق سعري واضح'),
 'Discord — Boosts/Nitro': ('فاوض على حجم — أعلى فئة مخزون', None, None, '@prodsellerbot', 'Server Boost x2 مخزونه 1139 وحدة — أكبر بند؛ خصم حجم 10% يعني وفرًا ملموسًا'),
 'Decor — Discord': ('لا بديل — عائلة فريدة', None, None, '@prodsellerbot', 'سلع Decor نادرة — تحقق من مصدرها عند أول فرصة تفاوض'),
 'X/Twitter — Premium/حسابات': ('لا بديل مرصود', None, None, '@prodsellerbot', 'حسابات 2009-2022 سلع أثرية — السعر يحدده الندرة'),
 'Canva': ('لا تغيّر — SV أرخص', 0.50, 0.39, '—', 'Evo_Era يبيع دعوة Team Edu 3Y بـ$0.50 وتكلفة SV $0.39'),
 'Figma': ('Evo_Era — نفس المصدر تقريبًا', 4.00, 4.00, 'بوت Evo_Era', 'تعادل سعري — لا ميزة تحويل'),
 'Adobe': ('راقب فلاشات Evo_Era', None, 0.35, 'بوت Evo_Era', 'ProdSeller أعلن Adobe Express بـ$0.85 بيعًا وتكلفة SV $0.50 — ضمن النطاق الطبيعي'),
 'Spotify': ('HitMeow يبيع $2.33 — تكلفة SV $1.53 أرخص', None, None, '—', 'احتفظ بالمورد الحالي'),
 'YouTube Premium': ('لا تغيّر — SV أرخص', 4.00, 2.50, '—', 'Evo_Era يبيع 3M بـ$4.00 وتكلفة SV $2.50 — وفر مريح'),
 'Amazon Prime': ('لا بديل مرصود — مزارع هندية', None, None, '@prodsellerbot', 'عروض UPI هندية — مصدر مستقر حاليًا'),
 'Apple Music': ('لا بديل — مزارع هندية UPI', None, None, '@prodsellerbot', 'نفس طريقة العرض الهندي — الفجوة سعريًا ضيقة'),
 'HBO/Streaming أخرى': ('لا بديل مرصود', None, None, '@prodsellerbot', 'عائلة صغيرة الحجم'),
 'أكواد شركات ناشئة — Framer/Notion/Linear/Manus/Facto': ('Evo_Era — راقب فلاشات الأحد (Framer $10.50)', 10.50, 12.00, 'بوت Evo_Era', 'SV يشتري أصلًا من Evo_Era بطبقة جملة (أرخص 9-57%) — الفلاشات تضيف وفرًا إضافيًا عند التوقيت'),
 'تعليم — Coursera/Udemy/JetBrains/Kahoot/Quizlet': ('لا تغيّر — SV أرخص بكثير', 3.50, 1.50, '—', 'Coursera: Evo_Era يبيع $3.50 وتكلفة SV $1.50 — تفوق 57%'),
 'أدوات كتابة — Grammarly/Quillbot': ('لا بديل — مزارع هندية', None, None, '@prodsellerbot', 'عروض مستهدفة للسوق الهندي — استقرار جيد'),
 'VPN': ('AiVerseX — Nord 3M بـ$2.80 بيعًا', 2.80, None, '@AiVerseXBot', 'قارن بالتكلفة الحالية عند الشراء بالجملة؛ GDS فيه مزودو VPN بديلون'),
 'LinkedIn': ('لا بديل — عروض مستهدفة', None, None, '@prodsellerbot', 'قسائم مستخدمين جدد فقط — لا تنافس سعريًا'),
 'Zoom': ('لا بديل مرصود', None, None, '@prodsellerbot', 'عائلة صغيرة'),
 'TikTok — حسابات بائعين': ('لا بديل — سوق متخصص', None, None, '@prodsellerbot', 'حسابات DE/UK/US/VN مؤسسة — قيمة تاريخية لا سعرية'),
 'Cloud — AWS/GCP': ('عروض ترويجية أصلية — لا بديل', None, None, '@prodsellerbot', 'قسائم $50-100 — تحقق من مصدرها القانوني'),
 'AI أخرى — Perplexity/Claude/Miro/Freepik': ('راقب HitMeow (Claude/Perplexity)', None, None, 't.me/HitMeowShop', 'قناة متخصصة AI — قارن شهريًا'),
 'أخرى — غير مصنفة': ('مراجعة تصنيفية ربع سنوية', None, None, '—', '17 منتجًا متنوعًا — راقب تكاليفها دوريًا'),
}

r = 5
for idx, f in enumerate(fams):
    neg = NEG.get(f['family'], ('فاوض على حجم مع المورد الحالي', None, None, '@prodsellerbot', ''))
    cur_cost = f['cost_min'] if f['cost_min'] else None
    alt_price = neg[1]
    anchor = neg[2] if neg[2] else cur_cost
    if alt_price and anchor:
        saving = round((anchor - alt_price) / anchor, 3)
    else:
        saving = None
    route_str = ' + '.join(f"{k} ({v})" for k, v in f['routes'].items())
    cost_str = f"${f['cost_min']:.2f}" + (f" – ${f['cost_max']:.2f}" if f['cost_max'] != f['cost_min'] else "") if f['cost_min'] else '—'
    vals = [f['family'], f['n'], route_str, cost_str, neg[0],
            alt_price if alt_price else '—', saving if saving is not None else '—', neg[3], neg[4]]
    data_row(ws, r, vals, idx, 2, 2+len(headers)-1,
             numfmts={5: USD, 6: PCT}, color_map={6: True})
    r += 1
ws.freeze_panes = 'C5'
print('Sheet 2 done:', r-5, 'rows')

# ================= Sheet 3: كتالوج StackVault الكامل =================
ws = wb.create_sheet('كتالوج StackVault الكامل')
headers = ['المنتج', 'الفئة', 'سعر البيع ($)', 'التكلفة ($)', 'الهامش (%)', 'المخزون', 'مسار التوريد', 'عبر teamsoclo']
make_sheet(ws, 'كتالوج StackVault الكامل — 357 منتجًا (رصد حي 2026-09-29)', headers,
           widths=[3, 52, 15, 12, 11, 11, 9, 16, 12],
           subtitle='المصدر: API العمومي decohomz.com/sv-api/products | الهامش = (البيع − التكلفة) ÷ التكلفة')
sv_prods = pdb['sources']['stackvault_catalog']
r = 5
tot_sell = tot_cost = 0
for idx, p in enumerate(sv_prods):
    margin = round((p['sell'] - p['cost']) / p['cost'], 3) if p['cost'] else None
    vals = [p['name'], p['category'], p['sell'], p['cost'], margin if margin is not None else '—',
            p['stock'], p['route'], p['teamsoclo'] or '—']
    data_row(ws, r, vals, idx, 2, 2+len(headers)-1, numfmts={2: USD, 3: USD, 4: PCT}, color_map={4: True})
    tot_sell += p['sell'] or 0; tot_cost += p['cost'] or 0
    r += 1
# totals row (computed values per skill exception)
ws.cell(row=r, column=2, value=f'الإجمالي — {len(sv_prods)} منتجًا')
ws.cell(row=r, column=4, value=round(tot_sell, 2)).number_format = USD
ws.cell(row=r, column=5, value=round(tot_cost, 2)).number_format = USD
ws.cell(row=r, column=7, value=sum(p['stock'] for p in sv_prods))
style_range(ws, r, 2, 2+len(headers)-1,
            font=Font(name=FONT_NAME, size=11, bold=True, color=PRIMARY),
            fill=PatternFill('solid', fgColor=SECONDARY),
            border=Border(top=Side(style='medium', color=NEUTRAL_200)))
ws.row_dimensions[r].height = 26
ws.freeze_panes = 'C5'
CATALOG_LAST = r
print('Sheet 3 done:', r-5, 'rows')

# ================= Sheet 4: دليل الموردين والمتاجر =================
ws = wb.create_sheet('دليل الموردين والمتاجر')
headers = ['الجهة', 'الدور في السلسلة', 'قنوات التواصل', 'الدفع', 'تقييم المخاطر', 'الحجم/النطاق', 'ملاحظات تعامل']
make_sheet(ws, 'دليل جميع الموردين والمتاجر المرصودة', headers,
           widths=[3, 22, 34, 30, 12, 26, 30, 30],
           subtitle='مرتبة حسب الأهمية في سلسلة توريد StackVault')
DIR_NOTES = {
 'ProdSeller': 'المورد المحوري — 89% من الكتالوج. استخدم أسعاره المعلنة للAPI كنقطة ضغط دائمة',
 'Team Sóc Lọ (teamsoclo)': 'تعاقد مباشر يوفر 15-25% — لكن اختبر الاستقرار أولًا (عمر 3 أسابيع فقط)',
 'Evo Era': 'اشترِ وقت الفلاشات فقط — أسعاره العادية أعلى من طبقة جملتك الحالية',
 'AISUBSID': 'أرخص مصدر ChatGPT Plus — اطلب عينة 5 حسابات قبل الالتزام بالجملة',
 'HitMeowShop': 'جودة أعلى وأسعار أعلى — مناسب لعملاء VIP لا للجملة',
 'AiVerseX Hub': 'عروض ترويجية متقلبة — قارن قبل كل شراء كبير',
 'StackVault': 'المتجر محل التحليل — هامش وسطي 25.1%',
}
r = 5
for idx, d_ in enumerate(pdb['directory']):
    vals = [d_['name'], d_['type'], d_['channel'], d_['payment'], d_['risk'], d_['scale'], DIR_NOTES.get(d_['name'], '')]
    data_row(ws, r, vals, idx, 2, 2+len(headers)-1)
    r += 1
ws.freeze_panes = 'C5'
print('Sheet 4 done:', r-5, 'rows')

# ================= Sheet 5: أدلة الأسعار المرصودة =================
ws = wb.create_sheet('أدلة الأسعار المرصودة')
headers = ['التاريخ', 'القناة/المورد', 'المنتج (مقتطف)', 'النص الكامل للإعلان']
make_sheet(ws, 'سجل الأدلة السعرية — من قنوات الموردين أنفسهم', headers,
           widths=[3, 12, 16, 26, 90],
           subtitle='كل صف = إعلان موثق قابل للاقتباس في التفاوض | الفترة 2026-06-25 إلى 2026-09-29')
ev = pdb['channel_evidence']
r = 5
for idx, e in enumerate(ev):
    vals = [e['date'], e['channel'], e['product_hint'].strip() or '—', e['message']]
    data_row(ws, r, vals, idx, 2, 2+len(headers)-1)
    r += 1
ws.freeze_panes = 'C5'
EVID_LAST = r - 1
print('Sheet 5 done:', r-5, 'rows')

# ================= Sheet 6: مصادر GDS البديلة =================
ws = wb.create_sheet('مصادر GDS البديلة')
headers = ['المعرف', 'الاسم', 'النطاق', 'الدولة', 'API', 'جملة', 'B2B', 'الفئات الرقمية']
make_sheet(ws, 'مصادر توريد بديلة من قاعدة GDS — 230 كيانًا مؤهلًا (مفلترة حسب الصلة)', headers,
           widths=[3, 11, 38, 26, 12, 8, 8, 8, 40],
           subtitle='الفلترة: كيانات ذات فئات Subscriptions/SaaS/Software/Prepaid/Vouchers وقادرة على API أو الجملة — لتنويع مصادر البرامج والمفاتيح والبطاقات')
rel = []
for e in gds:
    cats = str(e.get('Digital_Categories', ''))
    if any(x in cats for x in ['Subscriptions', 'SaaS', 'Software', 'Prepaid', 'Vouchers']):
        if e.get('API') or e.get('Wholesale') or e.get('B2B'):
            rel.append(e)
r = 5
for idx, e in enumerate(rel):
    vals = [e['Entity_ID'], e['Canonical_Name'][:40], e['Official_Domain'], e.get('Country', '—'),
            'نعم' if e.get('API') else '—', 'نعم' if e.get('Wholesale') else '—',
            'نعم' if e.get('B2B') else '—', str(e.get('Digital_Categories', ''))[:70]]
    data_row(ws, r, vals, idx, 2, 2+len(headers)-1)
    r += 1
GDS_LAST = r - 1
ws.freeze_panes = 'C5'
print('Sheet 6 done:', r-5, 'rows')

# ================= Sheet 7: خطة التفاوض =================
ws = wb.create_sheet('خطة التفاوض')
headers = ['الأولوية', 'الإجراء', 'الجهة المستهدفة', 'نقطة الضغط', 'الوفر المتوقع', 'الإطار الزمني', 'مؤشر النجاح']
make_sheet(ws, 'خطة التفاوض التنفيذية — مرتبة بالأولوية والأثر', headers,
           widths=[3, 10, 42, 22, 40, 14, 12, 26])
plan = [
 ('1 — فوري', 'المطالبة بسعر API المعلن: K12 بـ$3.80 وOffice بـ$0.17', 'ProdSeller (@prodsellerbot)',
  'إعلانات قناته الرسمية بتاريخ 19-20/09 (مذكورة في ورقة الأدلة)', '18-19% على العائلتين', 'هذا الأسبوع',
  'تحديث الأسعار في API خلال 48 ساعة'),
 ('2 — فوري', 'فتح خط Reseller مباشر مع teamsoclo لرصيد Codex/Astra (23 منتجًا)', 'Team Sóc Lọ (t.me/teamsoclo)',
  'أنت تبيع حجمًا شهريًا من أغلى فئاتهم — والبديل تحويل الطلب لمزود آخر', '15-25% على $115 كحد أقصى للوحدة', 'أسبوعان',
  'عرض سعر مكتوب منهم + فترة تجريبية'),
 ('3 — هذا الأسبوع', 'طلب عرض جملة 20+ ChatGPT Plus من AISUBSID @$2.90 + عينة جودة 5 حسابات', 'AISUBSID (@Aisubsglobalbot)',
  'سعرهم المعلن للجملة أقل 46% من تكلفة SV الحالية للمضمون', 'حتى 46% على أكبر عائلة مبيعًا', 'أسبوعان',
  'اجتياز العينة للاختبار بدون شكاوى'),
 ('4 — أسبوعي', 'مراقبة فلاشات Evo_Era و الشراء عند الفلاش فقط (مثل Framer $10.50)', 'Evo Era (البوت)',
  'توقيت الفلاشات مسائي نهاية الأسبوع غالبًا', '8-25% وقت الشراء', 'مستمر',
  'لوغ شراء شهري يوثق الوفر'),
 ('5 — شهري', 'تدقيق مصادر GDS البديلة لمفاتيح البرامج (CodesWholesale وغيرها)', 'GDS (codeswholesale.com وغيره)',
  'قنوات API رسمية تعطي ضمانات أطول لنفس المنتجات', 'تنويع + حماية من انقطاع ProdSeller', 'شهر',
  'مصدر ثانٍ فعّال لعائلة Windows/Office'),
 ('6 — استراتيجي', 'تقليل الاعتماد على مورد واحد (89% من الكتالوج) — هدف: ألا يتجاوز 70%', 'الإدارة الداخلية',
  'أي انقطاع لدى ProdSeller يعطل المتجر بالكامل', 'استمرارية الأعمال', 'ربع سنة',
  'خريطة توريد بموردين لكل عائلة رئيسية'),
]
r = 5
for idx, row in enumerate(plan):
    data_row(ws, r, list(row), idx, 2, 2+len(headers)-1)
    r += 1
print('Sheet 7 done:', r-5, 'rows')

# ================= Sheet 8: Review (فحوص التحقق) =================
ws = wb.create_sheet('Review')
ws.sheet_properties.tabColor = 'FFC000'
rtl(ws)
headers = ['الفحص', 'المتوقع', 'الفعلي', 'الحالة']
make_sheet(ws, 'ورقة التحقق — فحوص اتساق داخلية', headers, widths=[3, 40, 16, 16, 14])
checks = [
 ('عدد منتجات الكتالوج', 357, f"=COUNTA('كتالوج StackVault الكامل'!B5:B{CATALOG_LAST-1})"),
 ('عدد عائلات المصفوفة', len(fams), f"=COUNTA('مصفوفة التفاوض'!B5:B{4+len(fams)})"),
 ('صفوف الأدلة السعرية', len(ev), f"=COUNTA('أدلة الأسعار المرصودة'!B5:B{EVID_LAST})"),
 ('صفوف مصادر GDS', len(rel), f"=COUNTA('مصادر GDS البديلة'!B5:B{GDS_LAST})"),
 ('عدد جهات الدليل', len(pdb['directory']), f"=COUNTA('دليل الموردين والمتاجر'!B5:B{4+len(pdb['directory'])})"),
]
r = 5
for idx, (name, exp, actual_formula) in enumerate(checks):
    ws.cell(row=r, column=2, value=name)
    ws.cell(row=r, column=3, value=exp)
    ws.cell(row=r, column=4, value=actual_formula)
    ws.cell(row=r, column=5, value=f'=IF(C{r}=D{r},"✓ PASS","✗ FAIL")')
    data_row(ws, r, [name, exp, actual_formula, f'=IF(C{r}=D{r},"✓ PASS","✗ FAIL")'], idx, 2, 5)
    r += 1
print('Sheet 8 done')

OUTFILE = f'{DL}/مصفوفة_التفاوض_الشاملة_StackVault_2026-09-29.xlsx'
wb.save(OUTFILE)
print('SAVED:', OUTFILE)
