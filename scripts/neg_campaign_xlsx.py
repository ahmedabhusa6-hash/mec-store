#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SV-NEG-CAMPAIGN — Negotiation opening campaign matrix (xlsx deliverable)
Base:  PMRF v1.4 (2026-10-02) + sv_master_catalog_consolidated (1,112 records)
Out:   download/مصفوفة_حملة_التفاوض_2026-10-02.xlsx
Sheets: الملخص · أطراف_التفاوض · السيناريوهات · الطرق_والقنوات ·
        أوراق_الضغط · خطة_الموجات · النصوص_الجاهزة · المراجعة
"""
import sys, os

XLSX_SKILL_DIR = "/home/z/my-project/skills/xlsx"
for sub in [XLSX_SKILL_DIR, os.path.join(XLSX_SKILL_DIR, "templates")]:
    if sub not in sys.path:
        sys.path.insert(0, sub)
import base
base.FONT_NAME = "Arial"  # Arabic-capable universal font
from base import (PRIMARY, NEUTRAL_600, NEUTRAL_900, NEUTRAL_200, HEADER_BOLD,
                  Font, PatternFill, Alignment, Border, Side)
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

OUT = "/home/z/my-project/download/مصفوفة_حملة_التفاوض_2026-10-02.xlsx"
FONT = "Arial"

# ─────────────────────────── style helpers (RTL) ───────────────────────────
def rtl_sheet(ws):
    ws.sheet_view.rightToLeft = True
    ws.sheet_view.showGridLines = False
    ws.column_dimensions['A'].width = 3
    ws.row_dimensions[1].height = 15

def put_title(ws, title, sub, last_col):
    ws.merge_cells(start_row=2, start_column=2, end_row=2, end_column=last_col)
    c = ws.cell(row=2, column=2, value=title)
    c.font = Font(name=FONT, size=16, bold=HEADER_BOLD, color=PRIMARY)
    c.alignment = Alignment(horizontal='right', vertical='center')
    ws.row_dimensions[2].height = 32
    ws.merge_cells(start_row=3, start_column=2, end_row=3, end_column=last_col)
    s = ws.cell(row=3, column=2, value=sub)
    s.font = Font(name=FONT, size=9, color=NEUTRAL_600)
    s.alignment = Alignment(horizontal='right', vertical='center', wrap_text=True)
    ws.row_dimensions[3].height = 24

def put_headers(ws, headers, row=4):
    for i, h in enumerate(headers, start=2):
        c = ws.cell(row=row, column=i, value=h)
        c.fill = PatternFill('solid', fgColor=PRIMARY)
        c.font = Font(name=FONT, size=11, bold=HEADER_BOLD, color="FFFFFF")
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = Border(bottom=Side(style='thin', color=NEUTRAL_200))
    ws.row_dimensions[row].height = 30

def put_rows(ws, rows, start=5, wrap_cols=None, center_cols=None, num_cols=None,
             fills=None, row_h=None):
    """widths NOT set here — set explicitly per sheet after all tables."""
    wrap_cols = wrap_cols or set()
    center_cols = center_cols or set()
    num_cols = num_cols or set()
    for ri, r in enumerate(rows):
        excel_row = start + ri
        for ci, v in enumerate(r, start=2):
            c = ws.cell(row=excel_row, column=ci, value=v)
            fill = None
            if fills and (ri, ci - 2) in fills:
                fill = fills[(ri, ci - 2)]
            elif ri % 2 == 1:
                fill = NEUTRAL_200 if False else "F7F7F5"
            if fill:
                c.fill = PatternFill('solid', fgColor=fill)
            c.font = Font(name=FONT, size=10, color=NEUTRAL_900)
            if (ci - 2) in num_cols or (ci - 2) in center_cols:
                c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            else:
                c.alignment = Alignment(horizontal='right', vertical='top',
                                        wrap_text=((ci - 2) in wrap_cols))
        ws.row_dimensions[excel_row].height = row_h or 34
    return start + len(rows) - 1

def set_widths(ws, widths):
    for ci, w in enumerate(widths, start=2):
        ws.column_dimensions[get_column_letter(ci)].width = w

def note(ws, row, text, last_col):
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=last_col)
    c = ws.cell(row=row, column=2, value=text)
    c.font = Font(name=FONT, size=9, color=NEUTRAL_600)
    c.alignment = Alignment(horizontal='right', vertical='center', wrap_text=True)
    ws.row_dimensions[row].height = 30

FILL_A = "EAF3FB"; FILL_B = "EFF7EF"; FILL_C = "FBF3E7"; FILL_D = "F5F1F8"; FILL_X = "FBEDEC"

wb = Workbook()
wb.properties.creator = "Z.ai"

# ═══════════════════════ Sheet 1: الملخص ═══════════════════════
ws = wb.active
ws.title = "الملخص"
rtl_sheet(ws)
put_title(ws, "مصفوفة حملة التفاوض الافتتاحية — جميع أطراف سلسلة التوريد",
          "الأساس: PMRF v1.4 (مقبول) + كتالوج موحد 1,112 سجل — كل الأسعار إعلانية موثقة بانتظار التحقق بالمعاملة (G-7)", 5)

kpi = [
    ["8", "أطراف تفاوض فعليون (بعد إزالة التكرار البنيوي)",
     "المستبعدون: stackvault (واجهة المنصة نفسها) · AIXpress (خامل) · Acczone (مفتاح مبتور) · Evo_Era/Pixora/NevaAI (بلا قناة تواصل)"],
    ["4", "موجات متدرجة (W0 تجهيز ← W3 تعاقد منبع)",
     "لا فتح متزامن مع الجميع — التدرج يحمي أوراق الضغط ويمنع تسريب موقفك بين الأطراف المتشابكة"],
    ["5", "طرق تفاوض متعددة لكل طرف حسب قناته الموثقة",
     "رسالة مالك · تذاكر API · استعلام حجمي · شراء اختباري G-7 · شراكة تشغيلية — تصاعد تدريجي بالكلفة والالتزام"],
    ["30", "سيناريو متوقع ومدروس مع رد جاهز وعتبة انسحاب",
     "ورقة السيناريوهات — العمود الفقري التشغيلي؛ الاحتمالات مبنية على السلوك الموثق لكل طرف"],
    ["≤ $300", "سقف ميزانية الافتتاح المقترح (سلّم إيداعات مجزأ)",
     "كل إيداع خلف بوابة موافقة المستخدم (بوابة G-7 للتحقق بالمعاملة)"],
    ["11", "ورقة ضغط سعرية موثقة بالأرقام المرجعية",
     "أرخص سعر موثق لكل عائلة = نقطة ارتكاز الطلب التفاوضي"],
]
put_headers(ws, ["القيمة", "المؤشر", "التفصيل"])
last = put_rows(ws, kpi, wrap_cols={1, 2}, center_cols={0}, row_h=30)

r = last + 2
put_headers(ws, ["الموجة والتوقيت", "الأطراف", "الإجراء الأساسي", "بوابة القرار"], row=r)
waves_short = [
    ["W0 التجهيز — اليوم 0", "— (قرارات داخلية)", "تثبيت التموضع التجاري والهوية + سلّم الميزانية + فحص بوت AISUBSID بعد الهجرة (G-6)", "قرار المستخدم"],
    ["W1 القنوات الموثقة — يوم 1–3", "RichAI · DigitalCore · canboso · AIVerseX", "استعلامات حجمية عبر الحسابات القائمة (بلا إيداع): تذاكر + جداول تدرجات", "موافقة قبل أي إيداع"],
    ["W2 الجائزة الاستراتيجية — يوم 3–7", "ProdSeller / SookBit", "تواصل مباشر (عربي/فرنسي) مسلّح بجداول أسعار W1 كورقة ضغط + طلب الجدول المخفي", "موافقة على النص + الهوية"],
    ["W3 التعاقد المنبع — أسبوع 2+", "teamsoclo · AISUBSID · aivaulthub + جولة ثانية", "حساب موزع مباشر على بوابة AI + جملة Plus + وكالة Gemini", "ميزانية الجملة"],
]
put_rows(ws, waves_short, start=r + 1, wrap_cols={1, 2}, center_cols={0, 3}, row_h=34)
set_widths(ws, [24, 40, 60, 22])  # B..E — يخدم الجدولين معًا
note(ws, r + 6, "قاعدة حاكمة: كل الأسعار في هذه المصفوفة إعلانية مرصودة (رصد سلبي/قراءة API) ولم تُتحقق بمعاملة بعد — لا يُبنى عليها التزام مالي نهائي قبل تنفيذ G-7.", 5)

# ═══════════════════════ Sheet 2: أطراف_التفاوض ═══════════════════════
ws2 = wb.create_sheet("أطراف_التفاوض")
rtl_sheet(ws2)
put_title(ws2, "دليل أطراف التفاوض — بعد إزالة التكرار البنيوي",
          "الطبقة A منصات جملة · B مصانع/بوابات منبع · C لوحات وكالة رسمية · D متاجر متخصصة — القنوات موثقة حيًا 30/09–02/10", 10)
hdr2 = ["الطرف", "الطبقة", "الدور في الشبكة", "قنوات الاتصال الموثقة", "اللغة",
        "ما لدينا", "الموجة", "الهدف التفاوضي", "عتبة الانسحاب"]
put_headers(ws2, hdr2)
parties = [
    ["ProdSeller / SookBit", "A", "منصة الجملة الأم (prodseller.com) — باكند StackVault كامل على صندوقها (إثبات vhost)",
     "t.me/sookbit (الأدمن، ID 5574095571) · واتساب +33 7 53 43 44 42 · t.me/ProdsellerSupport · بوت @ProdSellerBot · قناة @ProdSellerOfficial",
     "عربي / فرنسي / إنجليزي", "مفتاح psk_ (حساب API قائم)", "W2",
     "جدول أسعار API/الجملة المخفي كاملًا + تدرج حجم فوق المعلن + سياسة استبدال مكتوبة",
     "رفض الجدول المكتوب مع اشتراط إيداع بلا شروط = تجميد التعامل"],
    ["canboso / HitMeow (PremiKey)", "A", "منصة شقيقة من الحوض الكتالوجي VN — 349 منتجًا · Binance Pay · usdRate 25,945 VND",
     "t.me/HitmeowSupport (الدعم) · t.me/vahnix (المالك — تفاوض الجملة) · بوتا t.me/PremikeyBot وt.me/Premikey_Bot · قناة @HitMeowShop",
     "إنجليزي (بوت EN رسمي)", "مفتاح tgb_ (رصيد 0)", "W1",
     "جدول تدرجات الكمية + سياسة الاستبدال والضمان + تسوية Binance Pay",
     "لا ضمان استبدال إطلاقًا = اقتصار التعامل على عائلة Deepseek (الأرخص 1.6–1.7×)"],
    ["Team Sóc Lọ (teamsoclo)", "B", "المصنع/البوابة المنبع (لوحة New API) — 15 موديل AI · 85 وصف منتج StackVault يحمل روابطها",
     "قناة t.me/teamsoclo (إعلانات تشغيلية للموزعين) · gpt.teamsoclo.site (البوابة واللوحة) · docs.teamsoclo.site",
     "فيتنامي (يلزم مترجم)", "لا مفتاح — برنامج Reseller معلن", "W3",
     "حساب موزع مباشر يقطع هامش الوسيط 15–25% على عائلات رصيد AI الأغلى (23 منتجًا)",
     "سعر البوابة أعلى من سعر الوسيط المُعاد بيعه (بعد التحقق من تكافؤ الموديلات) = بقاء على ProdSeller"],
    ["DigitalCore", "B", "مورد جملة VN بتوثيق API كامل — 11 منتجًا · تدرجات كمية منشورة",
     "بوت t.me/DCoreStoreBot · قناة التوريد t.me/DGTsupply · digitalcore.top/docs (swagger عام)",
     "إنجليزي", "مفتاح UUID (رصيد 0)", "W1",
     "تدرج كمية فوق المنشور عند 100+ وحدة + اختبار شراء أول موثق",
     "أسعار أعلى من قاع السوق الموثق للعائلة نفسها (Gemini: 0.70–0.80 لديهم مقابل 0.39–0.50 بالسوق)"],
    ["RichAIStore (cgpt-active.pro)", "C", "لوحة وكالة API كاملة v1.0.0 — 12 نقطة نهاية + دورة تذاكر موثقة",
     "بوت t.me/RichAIStoreBot · نظام التذاكر عبر API (مسار موثق) · صفحة تكامل AI-Agent عامة",
     "إنجليزي", "مفتاح rsk_ (Bearer)", "W1",
     "تحسين your_unit_price عند الحجم لعائلة CDK (Google 5TB) + أثر ورقي عبر التذاكر",
     "تجاهل تذكرتين متتاليتين (فاصل 72 ساعة) = خفض الأولوية"],
    ["aivaulthub reseller (@Gemini_Shop_Robot)", "C", "لوحة الوكالة الرسمية لمنصة aivaulthub — عائلة Gemini",
     "بوت t.me/Gemini_Shop_Robot · reseller.aivaulthub.store/api/v1/docs",
     "إنجليزي / عربي", "مفتاح rsk_ (X-API-Key)", "W3",
     "جدول أسعار الوكالة لعائلة Gemini (بداية: Gemini Pro 18M)",
     "سعر وكالة أعلى من فلاش AIVerseX الموثق ($0.39) = يبقى AIVerseX المصدر"],
    ["AIVerseX (AiVerseX Hub)", "D", "أكبر قناة بين الموردين (22,937 مشتركًا) — Gemini وOffice وAdobe · مخزون Gemini معلن 3,804",
     "بوت t.me/AIVerseXBot · قناة t.me/AiVerseXHub (كل الفلاشات تعلن فيها أولًا)",
     "إنجليزي", "مفتاح AK_ (35 منتجًا)", "W1",
     "تثبيت سعر جملة 30 يومًا عند حجم أسبوعي معلن (فلاشه 0.39 = تكلفة SV الحالية)",
     "رفض التثبيت مع الاكتفاء بالفلاشات = شراء انتهازي فقط بلا تعاقد"],
    ["AISUBSID (AISUBS.ID)", "D", "أرخص مصنع Plus موثق في السوق كله (إندونيسي) — جملة 10–50 بـ$2.50",
     "بوت t.me/Aisubsglobalbot · قناة t.me/AISUBSID · المالك t.me/AisubsIDFounder",
     "إنجليزي", "لا مفتاح — بوت عام", "W0 فحص ثم W3",
     "تسعيرة جملة Plus (المرصود 2.50–2.90) + إفصاح طريقة التوريد VIP مقابل UPI (G-8) + حالة ما بعد الهجرة (G-6)",
     "البوت ميت بعد الهجرة أو سعر فردي أعلى من 3.10 = LOW_PRIORITY وإعادة فحص أسبوعي"],
]
fills2 = {(i, 0): FILL_A for i in range(2)}
fills2.update({(2, 0): FILL_B, (3, 0): FILL_B, (4, 0): FILL_C, (5, 0): FILL_C,
               (6, 0): FILL_D, (7, 0): FILL_D})
last2 = put_rows(ws2, parties, wrap_cols={2, 3, 5, 7, 8}, center_cols={1, 4, 6},
                 fills=fills2, row_h=92)
set_widths(ws2, [24, 7, 34, 44, 12, 17, 9, 38, 34])  # B..J

# جدول المستبعدين — الاسم في B والسبب مدمج C..J
r = last2 + 2
ws2.merge_cells(start_row=r, start_column=3, end_row=r, end_column=10)
hdrs = [("الكيان المستبعد", 2), ("سبب الاستبعاد الموثق", 3)]
for h, col in hdrs:
    c = ws2.cell(row=r, column=col, value=h)
    c.fill = PatternFill('solid', fgColor=PRIMARY)
    c.font = Font(name=FONT, size=11, bold=HEADER_BOLD, color="FFFFFF")
    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    c.border = Border(bottom=Side(style='thin', color=NEUTRAL_200))
ws2.row_dimensions[r].height = 28
excluded = [
    ["StackVault (المتجر نفسه)", "ليس موردًا: باكنده يعمل على صندوق منصة ProdSeller نفسه (إثبات vhost بتاريخ 02/10) — التفاوض معه = التفاوض مع واجهة سوكبيت بأسعار تجزئة. علاقة المستخدم به UNRESOLVED في PMRF §22 — لا يُسأل عنه أي طرف"],
    ["AIXpress", "خامل: كتالوج منتجان فقط وكلاهما stock=0 — والمفتاح المجدد يعمل على نشر aixpress.shop الفارغ (وثائق البوت متقادمة)"],
    ["Acczone", "المفتاح المسلّم مبتور (حُذف جزء منه في جلسة سابقة) — 4 منتجات فقط بالكتالوج المؤرشف؛ يحتاج إعادة إرسال المفتاح إن رُغب"],
    ["Evo_Era / Pixora / NevaAI", "بلا مفاتيح أو مسارات تواصل موثقة بعد — تُرصد سلبيًا وتُضاف عند توفر قناة"],
]
for i, (name, why) in enumerate(excluded):
    rr = r + 1 + i
    c1 = ws2.cell(row=rr, column=2, value=name)
    c1.fill = PatternFill('solid', fgColor=FILL_X)
    c1.font = Font(name=FONT, size=10, color=NEUTRAL_900)
    c1.alignment = Alignment(horizontal='right', vertical='top', wrap_text=True)
    ws2.merge_cells(start_row=rr, start_column=3, end_row=rr, end_column=10)
    c2 = ws2.cell(row=rr, column=3, value=why)
    c2.fill = PatternFill('solid', fgColor=FILL_X if i % 2 == 0 else "FFFFFF")
    c2.font = Font(name=FONT, size=10, color=NEUTRAL_900)
    c2.alignment = Alignment(horizontal='right', vertical='top', wrap_text=True)
    ws2.row_dimensions[rr].height = 42
note(ws2, r + 6, "مصدر القنوات: بطاقات الموردين (رصد حي 30/09) + تقارير G1a-R1/R3/R4 (02/10) — كلها فحص سلبي عام GET فقط.", 10)

# ═══════════════════════ Sheet 3: السيناريوهات ═══════════════════════
ws3 = wb.create_sheet("السيناريوهات")
rtl_sheet(ws3)
put_title(ws3, "مصفوفة السيناريوهات المتوقعة والمدروسة",
          "لكل سيناريو: الاحتمال المقدر · الرد المدروس الجاهز · خط الانسحاب — التقديرات مبنية على سلوك موثق لا على تخمين", 7)
hdr3 = ["الطرف", "الرمز", "السيناريو المتوقع", "الاحتمال", "الرد المدروس", "خط الانسحاب / الحد"]
put_headers(ws3, hdr3)
S = []
def sc(party, code, scen, prob, resp, walkaway):
    S.append([party, code, scen, prob, resp, walkaway])

sc("ProdSeller/SookBit", "S-A1", "يرحّب ويرسل قائمة أسعار API المعيارية (سلوك معلن: لمستخدمي API أسعار خاصة)",
   0.45, "اطلب الجدول المكتوب كاملًا، واربطه بالفجوات الموثقة: K12 بـ$3.80 معلن بالقناة (SV يدفع 4.62) · Office جملة $0.17 معلن (SV يدفع 0.21) — مطالبة مباشرة بمطابقة المعلن",
   "الحد: لا تقبل سعرًا أعلى من تكلفة StackVault الموثقة للعائلة نفسها إلا بميزة موثقة مكتوبة")
sc("ProdSeller/SookBit", "S-A2", "يسأل: من أنت؟ كيف وصلت لنا؟",
   0.25, "غطاء جاهز وصادق جزئيًا: عميل API حالي عبر بوت ProdSellerBot + متابع للقناة الرسمية — لا شيء آخر يُذكر",
   "خط أحمر: يُمنع ذكر stackvault أو البنية التحتية أو أي تحليل — كشفها يُفسَّر كتطفل ويحرق العلاقة")
sc("ProdSeller/SookBit", "S-A3", "يعرض متجرًا جاهزًا على منصته (نموذج stackvault: واجهة + باكند مستضاف)",
   0.15, "قيّم العرض كخيار تسريع: اسأل عن التكلفة الشهرية · ملكية بيانات العملاء · قابلية التصدير · الاستقلالية التقنية. لا ترفض فورًا ولا تلتزم",
   "شرط أقصى: لا يقيم باكندك على صندوقه إلا بتصدير كامل للبيانات وإمكانية خروج موثقة")
sc("ProdSeller/SookBit", "S-A4", "اشحن رصيدًا أولًا ثم نتفاوض",
   0.10, "بوابة G-7: إيداع صغير موثق ($30–50) بشرط إيصال/فاتورة — الإيصال نفسه يكشف سكة الدفع وربما الاسم القانوني (يغلق G-1a قانونيًا)",
   "رفض أي إيصال = إيقاف عند حد الاختبار المصغّر")
sc("ProdSeller/SookBit", "S-A5", "تجاهل أو بطء (مشغّل فردي يدير منصة كاملة بساعات عمل CEST)",
   0.05, "متابعة بفاصل 72 ساعة على تيليجرام؛ واتساب الطوارئ (+33 الموسوم «للطوارئ فقط») بعد أسبوع بلا رد على طلب قائم",
   "صمت أسبوعين = خفض الأولوية والاكتفاء بقنوات W1/W3")

sc("canboso/HitMeow", "S-B1", "الأسعار كما بالبوت — اشحن عبر Binance Pay ثم اشترِ",
   0.50, "الحساب قائم أصلًا (مفتاح tgb_ مرتبط بحساب المستخدم): اطلب جدول تدرجات الكمية قبل الشحن، مستشهدًا بنموذج DigitalCore المنشور (تدرجات 3–4 شرائح) كمعيار سوقي",
   "لا تدرجات إطلاقًا = تعامل تجزئة فقط بعائلة Deepseek (الأرخص 1.6–1.7× موثقًا)")
sc("canboso/HitMeow", "S-B2", "طلب تحقق من هوية تيليجرام قبل التفاعل",
   0.20, "استخدم الحساب ذاته المرتبط بالمفتاح أصلًا (7334478984/A7MED) — الاتساق موثق لديهم عبر نقطة /me",
   "طلب توثيق KYC رسمي (هوية/جواز) = انسحاب فوري (سياسة مشتريات ثابتة)")
sc("canboso/HitMeow", "S-B3", "سعر حالي أعلى من لقطة API بتاريخ 02/10",
   0.15, "اقتبس SKU بعينه وسعره المؤرخ من واجهتهم هم (سلوك مشترٍ محترف مشروع تمامًا) واطلب قائمة الرسوم الحالية",
   "فروق جوهرية متكررة >20% بلا إشعار = خطر تشغيلي يُوثَّق ويُرفع وزن ProdSeller")
sc("canboso/HitMeow", "S-B4", "يعرضون وكالة/متجرًا أبيض (منصة كاملة مثل منصة سوكبيت)",
   0.10, "استقبل العرض ووثّقه — ورقة مقارنة مباشرة ضد عرض سوكبيت المحتمل (S-A3): العمولات · التملك · الخروج",
   "التزام واحد فقط: لا عقود حصرية مع أي منصة في مرحلة الافتتاح")
sc("canboso/HitMeow", "S-B5", "لا سياسة استبدال/ضمان واضحة",
   0.05, "اشترط سياسة مكتوبة قبل أول إيداع (نافذة استبدال بالساعات لكل عائلة)",
   "صفر ضمان = عتبة انسحاب للعائلات عالية النفوق (Plus VIP تحديدًا)")

sc("teamsoclo", "S-C1", "القناة توجه للبوابة وبرنامج Reseller (المعلن موجه للمتاجر «các shop»)",
   0.40, "قدّم عبر أدمن القناة/البوابة بإنجليزية مبسطة (نص T8 جاهز) — عرّف نفسك كمشغّل متجر يبحث عن توريد مباشر",
   "لا مسار تطبيق واضح خلال أسبوع = تأجيل وبقاء الوسيط ProdSeller للعائلة")
sc("teamsoclo", "S-C2", "اشتراط رصيد مسبق كبير لتفعيل حساب الموزع",
   0.30, "ابدأ بأصغر رصيد مقبول واختبر 1–2 موديل فقط (عائلة Codex الأصغر) قبل أي التزام",
   "حد أول: $50–100 كحد أقصى لاختبار البوابة (ضمن ميزانية W3)")
sc("teamsoclo", "S-C3", "سعر البوابة المباشر أعلى من سعر ProdSeller المعاد بيعه",
   0.15, "تحقق من تكافؤ الموديلات حرفيًا (gpt-5.6-sol · 6-sol · 6.1-sol · 6-luna) — إن تأكد تفوق الوسيط فالوسيط يملك ترتيبًا خاصًا: وثّق واحتفظ به",
   "تأكيد التفوق = بقاء على ProdSeller للعائلة وإغلاق ملف البوابة مؤقتًا")
sc("teamsoclo", "S-C4", "أعطال خوادم متكررة (موثقة بإعلانات قناتهم نفسها)",
   0.15, "اشترط سياسة استبدال/تمديد مكتوبة قبل أول رصيد — إعلانات الأعطال لديهم تسبق شكوى العملاء (إنذار مبكر استخباراتي مجاني)",
   "رفض أي سياسة استبدال مع تاريخ أعطال موثق = توريد احتياطي فقط")

sc("DigitalCore", "S-D1", "يشتغلون بالجدول المنشور (تدرجات 3–4 شرائح فوق priceFrom)",
   0.50, "اطلب شريحة تدرج إضافية عند 100+ وحدة مستشهدًا بشرائحهم المنشورة نفسها (Coursera تصل 4 شرائح حتى 100+) — طلب طبيعي داخل منطق تسعيرهم",
   "رفض الشريحة الإضافية = الشراء بالشريحة المنشورة وقياس الجودة أولًا")
sc("DigitalCore", "S-D2", "الأسعار نهائية بلا تفاوض (توثيق كامل لكن صلابة)",
   0.20, "اختبار شراء صغير موثق (G-7) ثم إعادة فتح ببيانات نمو فعلية («اشتريت X الشهر الماضي») — التفاوض بالسلوك لا بالكلام",
   "جودة دون المتوسط بالعينة = إسقاط الطرف مهما كان السعر")
sc("DigitalCore", "S-D3", "تفاعل تقني احترافي (swagger عام = فريق منظم)",
   0.30, "استخدم مفردات وثائقهم بدقة في المراسلة (endpoints · priceFrom · tiers) — يرفع جودة الرد وسرعته",
   "—")

sc("RichAIStore", "S-E1", "«your_unit_price هو سعر الوكيل بالفعل»",
   0.40, "افتح تذكرة API موثقة (قناة رسمية لديهم): اطلب تحسين سعر الوحدة عند حجم 100/500 لعائلة CDK الرئيسية — أرفق مقارنة retail_price الموثقة من واجهتهم",
   "لا تحسين مع فروق سوقية كبيرة = توريد احتياطي فقط")
sc("RichAIStore", "S-E2", "بطء الرد (مشغّل فردي خلف لوحة متقنة)",
   0.25, "إيقاع متابعة 72 ساعة — التذاكر تحفظ أثرًا ورقيًا كاملًا (ميزة لا تملكها أي قناة أخرى في الشبكة)",
   "تجاهل تذكرتين متتاليتين = خفض الأولوية")
sc("RichAIStore", "S-E3", "يسألون عن قناة البيع لديك",
   0.35, "جواب موحد: «متجر آلي بتكامل API» — يتطابق مع تسويقهم هم (صفحة تكامل AI-Agent لـCursor/Claude Code) — نقطة تعاطف مؤسسية لا تحتاج تلفيقًا",
   "—")

sc("AIVerseX", "S-F1", "تسعير متقلب قائم على الفلاشات (11–24 ساعة)",
   0.40, "اطلب تثبيت سعر جملة 30 يومًا عند حجم أسبوعي معلن (30–50 وحدة Gemini 18M أسبوعيًا مثلًا) — الفلاش $0.39 الموثق = نقطة الارتكاز",
   "رفض التثبيت = شراء انتهازي موثق بلا اعتماد تشغيلي")
sc("AIVerseX", "S-F2", "تذبذب التوفر (16/35 فقط متوفر بالكتالوج رغم إعلان 3,804 وحدة Gemini)",
   0.20, "اشترط أولوية توفير بعقد صغير مسبق الدفع جزئيًا",
   "نفاد متكرر خلال أسبوعي الاختبار = احتياطي فقط")
sc("AIVerseX", "S-F3", "إلحاح لمعرفة حجم أعمالك الكامل",
   0.05, "أرقام متحفظة قابلة للتصديق: 50–200 وحدة/شهر بداية عبر 4–6 عائلات، قابلة للنمو — لا أرقام ضخمة وهمية",
   "طلب كشوف حسابات أو إثبات حجم رسمي = انسحاب مهذب")
sc("AIVerseX", "S-F4", "بيع عادي عبر البوت بلا تعقيدات ولا تفاوض",
   0.35, "التزم بالشراء الانتهازي للفلاشات حتى تتغير الشروط — وثّق كل عملية كقياس جودة (يغذي G-8)",
   "—")
# يُمنع السؤال المباشر «من أين تجيبون» — G-2 يُحل استدلاليًا عند أول تسليم فعلي (G-7)

sc("AISUBSID", "S-G1", "البوت حي بعد هجرة النطاقات المخصصة (إعلان 02/10)",
   0.50, "استعلام جملة مكتوب: 10–50 وحدة Plus (المرصود $2.50 جملة · $2.80 فلاش يوم واحد) + سؤال الطريقة: VIP أم UPI (G-8: بقاء الحسابات)",
   "سعر جملة أعلى من $2.90 = فقدان ورقة الضغط الأولى ضد ProdSeller")
sc("AISUBSID", "S-G2", "البوت ميت أو المزرعة أوقفت بعد ترقيع UPI المتوقع (تحذير المالك نفسه 27/09)",
   0.30, "سجل LOW_PRIORITY + إعادة فحص أسبوعي — ورقة الضغط على ProdSeller تنتقل لسعر HitMeow K12 ($4.58)",
   "—")
sc("AISUBSID", "S-G3", "يطلبون دفعًا مسبقًا كاملًا لطلب جملة أول",
   0.20, "عينة 5 حسابات أولًا (بروتوكول المصفوفة المعتمد 29/09) ثم الطلب الكبير",
   "رفض العينة = لا طلب كبير (قاعدة معيارية مع المزارع الصغيرة — 309 مشتركين)")

sc("عام (أي طرف)", "S-X1", "يطلب KYC / هوية رسمية / جواز سفر",
   0.05, "رفض مهذب قاطع: «سياسة المشتريات لدينا لا تسمح بمشاركة مستندات هوية مع موردين جدد قبل سجل تعامل»",
   "إصرار = انسحاب نهائي من الطرف")
sc("عام (أي طرف)", "S-X2", "إيداع اختفى بلا تسليم (احتيال)",
   0.05, "أصغر إيداع ممكن دائمًا · وحدة واحدة أولًا · توثيق كامل بالأثر الورقي (تذاكر/رسائل مؤرخة) قبل أي مبلغ معتبر",
   "خسارة أي إيداع اختباري = قائمة سوداء داخلية وإغلاق ملف الطرف")
sc("عام (أي طرف)", "S-X3", "الطرف يكتشف نشاط الاستخبارات (تسريب بين الأطراف المتشابكة)",
   0.05, "كل الأطراف تعرف المستخدم كعميل API لديها فقط — وهذا صحيح وموثق؛ عمق المعرفة البنيوية (vhost/ObjectId) لا يظهر في أي تفاعل تفاوضي",
   "سؤال مباشر عن stackvault أو البنية = إنهاء المحادثة بهدوء وتجميد الطرف 30 يومًا")

fills3 = {}
party_fill = {"ProdSeller/SookBit": FILL_A, "canboso/HitMeow": FILL_A,
              "teamsoclo": FILL_B, "DigitalCore": FILL_B,
              "RichAIStore": FILL_C, "AIVerseX": FILL_D, "AISUBSID": FILL_D,
              "عام (أي طرف)": FILL_X}
for i, row in enumerate(S):
    fills3[(i, 0)] = party_fill.get(row[0], FILL_X)
last3 = put_rows(ws3, S, wrap_cols={2, 4, 5}, center_cols={1, 3}, num_cols={3},
                 fills=fills3, row_h=78)
for i in range(len(S)):
    ws3.cell(row=5 + i, column=5).number_format = '0%'
set_widths(ws3, [20, 8, 42, 9, 58, 42])  # B..G
note(ws3, last3 + 2, "قاعدة الاحتمالات: مجموع احتمالات كل طرف = 100% (فحص حي بورقة المراجعة) — الاحتمالات مبنية على السلوك الموثق (إعلانات القنوات · بنية اللوحات · أنماط الردود) وتُحدَّث بعد كل تفاعل.", 7)

# ═══════════════════════ Sheet 4: الطرق_والقنوات ═══════════════════════
ws4 = wb.create_sheet("الطرق_والقنوات")
rtl_sheet(ws4)
put_title(ws4, "الطرق المتعددة لكل طرف — لا تُفتح كل الطرق مع طرف واحد دفعة واحدة",
          "ابدأ بالقناة الأدنى كلفة والتزامًا واصعد تدريجيًا — كل تصعيد يُوثَّق في السجل", 6)
hdr4 = ["الطريقة", "الوصف", "الأنسب لـ", "الكلفة", "قاعدة الاستخدام"]
put_headers(ws4, hdr4)
methods = [
    ["M1 رسالة المالك/الأدمن المباشرة", "مراسلة صاحب القرار شخصيًا (تيليجرام أو واتساب) برسالة قصيرة احترافية",
     "سوكبيت (@sookbit/واتساب +33) · HitMeow (@vahnix) · AISUBSID (@AisubsIDFounder)", "صفر",
     "رسالة واحدة قصيرة — لا إلحاح قبل 72 ساعة؛ لا تكشف عمق معرفتك بالطرف"],
    ["M2 تذاكر/دعم عبر API", "فتح تذكرة دعم عبر القناة الموثقة (cgpt-active تدعم دورة تذاكر كاملة) أو دعم البوت الرسمي",
     "RichAIStore (تذاكر API) · canboso (@HitmeowSupport) · DigitalCore (@DGTsupply)", "صفر",
     "الميزة: أثر ورقي مؤرخ جاهز للاقتباس — انقل كل اتفاق شفهي إلى تذكرة مكتوبة فورًا"],
    ["M3 الاستعلام الحجمي المكتوب", "طلب تسعيرة لكميات محددة بعائلات وأرقام واضحة (SKU + كمية + هدف سعر)",
     "كل الأطراف — الطريقة الافتتاحية الافتراضية لموجة W1", "صفر",
     "أرقام متحفظة قابلة للتصديق (30–200 وحدة/شهر)؛ اذكر أنك تقارن عدة موردين — حقيقي ويوازن العلاقة"],
    ["M4 الشراء الاختباري (G-7)", "أول معاملة فعلية صغيرة موثقة: إيصال + تسليم + قياس جودة وبقاء",
     "DigitalCore · canboso · AISUBSID (عينة 5 حسابات) ثم ProdSeller (إيداع بفاتورة)", "$10–50 لكل طرف",
     "بوابة المستخدم قبل كل دفعة؛ الإيصال نفسه استخبارات: يكشف سكة الدفع وربما الهوية القانونية (يغلق G-1a)"],
    ["M5 الشراكة التشغيلية/التكامل", "التموضع كمشغّل متجر آلي بتكامل API يبحث عن توريد مستقر طويل الأمد",
     "RichAIStore (يتسوقون تكامل الوكلاء) · سوكبيت (عرض متجر جاهز محتمل) · teamsoclo (برنامج موزعين)", "صفر",
     "يتطلب تثبيت التموضع في W0 — لا يُستخدم قبل استقرار قرار الهوية التجارية"],
]
last4 = put_rows(ws4, methods, wrap_cols={1, 2, 4}, center_cols={3}, row_h=66)
set_widths(ws4, [26, 44, 40, 13, 50])  # B..F

# ═══════════════════════ Sheet 5: أوراق_الضغط ═══════════════════════
ws5 = wb.create_sheet("أوراق_الضغط")
rtl_sheet(ws5)
put_title(ws5, "أوراق الضغط السعرية — كل رقم موثق بمصدره",
          "المرجعية: كتالوج StackVault الموحد (تكلفة 356 منتجًا بالأرشيف) + إعلانات القنوات المؤرخة + قراءات API المباشرة", 7)
hdr5 = ["العائلة", "تكلفة StackVault الموثقة", "القاع البديل الموثق", "نقطة الارتكاز في التفاوض", "المصدر"]
put_headers(ws5, hdr5)
lev = [
    ["ChatGPT Plus (شهر، ضمان كامل)", "$10.67–11.05 (UPI/Apple Pay)", "AISUBSID جملة 10–50: $2.50 · فلاش: $2.80 · HitMeow VIP: $10.77",
     "اطلب من ProdSeller تسعيرًا مفصولًا بالطريقة (UPI مقابل ضمان كامل) — الفارق الموثق يقارب 4×", "أرشيف SV + قناة AISUBSID 27–28/09 + قناة HitMeow 25/09"],
    ["ChatGPT Plus K12 (سنتان)", "$4.62", "API سوكبيت معلن: $3.80 (−18%) · HitMeow: $4.58",
     "مطالبة فورية بمطابقة $3.80 المعلنة رسميًا في قناته — ورقة مكتوبة بيده", "أرشيف SV + قناة ProdSellerOfficial 20/09 + HitMeow 28/09"],
    ["Office 365 Plus (سنة)", "$0.21", "جملة سوكبيت معلنة: $0.17 (−19%) · AIVerseX: $0.29",
     "مطابقة $0.17 المعلنة «جملة» — منشورة بقناته", "أرشيف SV + قناة ProdSellerOfficial 19/09 + AiVerseXHub 26/09"],
    ["Gemini Pro 18 شهرًا", "≈$0.39–0.55 (خط ps_ الحي)", "API سوكبيت: $0.50 · فلاش AIVerseX: $0.39 · AISUBSID: $0.45–0.55 · DigitalCore: $0.70–0.80",
     "اطلب ≤$0.45 مثبتًا 30 يومًا عند حجم أسبوعي — أربع بدائل موثقة تجعل الطلب واقعيًا", "هوامش ps_ الحية + قناتا AiVerseXHub وAISUBSID + تدرجات DigitalCore API"],
    ["رصيد Codex/AI (عبر البوابة)", "هامش وسيط 15–25% فوق المصنع", "بوابة teamsoclo مباشرة: gpt-5.6-sol بـ$6 · gpt-6-astra بـ$60 · gpt-astra بـ$75/150",
     "حساب موزع مباشر على البوابة يقطع الهامش — أغلى عائلات المتجر (23 منتجًا)", "قائمة أسعار البوابة الحية (15 موديلًا) + مصفوفة 29/09"],
    ["Duolingo Super (12 شهرًا)", "$0.15–0.23 (الجديد)", "DigitalCore شرائح: $0.55/0.50/0.45 · API سوكبيت: $0.55",
     "$0.45 عند 25+ وحدة — شريحة منشورة رقميًا لدى DigitalCore", "أرشيف SV + تدرجات DigitalCore API + قناة ProdSellerOfficial 19/09"],
    ["Canva Pro", "$0.60 (سنتان)", "قناة سوكبيت (فلاشات متكررة أقل من 0.60)",
     "راقب فلاشات القناة قبل أي طلبية — لا تلتزم بسعر قائمة", "أرشيف SV + رصد القنوات"],
    ["CapCut Pro (شهر)", "$1.25", "مرجع تاريخي فقط: سوكبيت باع CapCut 1M بـ$0.8 (PlayerUp 09/2025)",
     "سعر المنبع الفعلي أقل من 1.25 بوضوح تاريخيًا — اطلب تسعيرة جملة صريحة", "أرشيف SV + إعلان PlayerUp مفهرس (دليل G-1a/D5)"],
    ["Adobe Express", "$0.50 (خط mr_)", "AIVerseX: $0.40 (كريبتو، −20%)",
     "حوّل العائلة لـAIVerseX أو استخدم سعره ورقة ضغط على مصادر mr_", "AiVerseXHub 26/09 + أرشيف SV"],
    ["Gmail (حسابات مستقرة)", "غير معزولة بالأرشيف", "سوكبيت: $0.80 رابط / $0.75 API / $0.60 جملة (معنون رسميًا)",
     "$0.60 جملة معلن — مطاببة مباشرة", "قناة ProdSellerOfficial 19/09"],
    ["Deepseek API", "أغلى عبر cb_", "canboso أرخص 1.6–1.7× (الاستثناء الموثق الوحيد)",
     "وجّه هذه العائلة تحديدًا لـcanboso أياً كانت نتائج باقي التفاوض", "مقارنة cb_∩canboso (R3/P3a — 111 زوجًا)"],
]
last5 = put_rows(ws5, lev, wrap_cols={1, 2, 3, 4}, row_h=58)
set_widths(ws5, [25, 23, 42, 43, 36])  # B..F
note(ws5, last5 + 2, "قاعدة صارمة: هذه الأسعار إعلانية/قراءة API بتواريخها — التحقق النهائي بمعاملة (G-7). نسبة cb_/canboso الوسيطة 0.912 (p25 0.764 · p75 1.066) مرجع فحص أي «تسعيرة جملة» يدّعيها أي طرف.", 7)

# ═══════════════════════ Sheet 6: خطة_الموجات ═══════════════════════
ws6 = wb.create_sheet("خطة_الموجات")
rtl_sheet(ws6)
put_title(ws6, "خطة الموجات التنفيذية — التدرج بدل الفتح الشامل",
          "كل موجة تنتهي ببوابة قرار للمستخدم قبل التصعيد — لا انتقال تلقائي بين الموجات", 7)
hdr6 = ["الموجة", "التوقيت", "الإجراءات", "الميزانية المقترحة", "مخرج النجاح", "البوابة (قرار المستخدم)"]
put_headers(ws6, hdr6)
plan = [
    ["W0 التجهيز", "اليوم 0", "تثبيت التموضع التجاري والهوية · إقرار سلّم الميزانية · فحص حي لبوت AISUBSID بعد هجرة النطاقات (G-6) · لقطة أسعار حية للعائلات الإحدى عشرة",
     "$0", "قرارات مثبتة + حالة AISUBSID محسومة", "موافقة على التموضع + السقف المالي"],
    ["W1 القنوات الموثقة", "يوم 1–3", "تذكرة RichAI (تحسين your_unit_price) · استعلام تدرجات DigitalCore · استعلام canboso عبر الدعم/المالك · عرض تثبيت سعر لـAIVerseX — كلها M2/M3 بالحسابات القائمة",
     "$0 (اختبارات شراء اختيارية $60–110)", "4 جداول أسعار/سياسات مكتوبة تُقيَّم ضد أوراق الضغط", "موافقة قبل أي إيداع اختباري"],
    ["W2 الجائزة الاستراتيجية", "يوم 3–7", "رسالة مباشرة لسوكبيت (عربي ثم فرنسي عند الحاجة) بصفة عميل API حالي · طلب الجدول المخفي كاملًا · ربط الفجوات المعلنة (K12/Office/Gmail) · استقبال عرض المتجر الجاهز إن طُرح (S-A3) ووثّقه",
     "$30–50 (إيداع اختباري اختياري بفاتورة)", "جدول أسعار مكتوب + إيصال يكشف سكة الدفع (G-1a قانونيًا)", "موافقة على نص الرسالة + الهوية + مبلغ الإيداع"],
    ["W3 التعاقد المنبع", "أسبوع 2+", "تقديم موزع لبوابة teamsoclo (إنجليزية مبسطة/مترجم) · جملة AISUBSID بعد العينة · وكالة aivaulthub (Gemini) · جولة ثانية بالجداول المجمعة مع كل طرف ناجح",
     "$75–125 (رصيد بوابة + عينة جملة)", "عقد منبع واحد مباشر (بوابة أو مزرعة) يعمل فعليًا", "ميزانية الجملة + قرار أولوية العائلات"],
    ["حملة الافتتاح — الإجمالي", "أسبوعان", "المجموع الكلي بكل الاختيارات",
     "≤ $300", "شبكة توريد من 3 أطراف فعالة على الأقل بأسعار ≤ تكلفة StackVault الموثقة", "مراجعة الحملة وقرار التوسع"],
]
last6 = put_rows(ws6, plan, wrap_cols={2, 4, 5}, center_cols={1, 3}, row_h=86)
set_widths(ws6, [21, 9, 60, 19, 38, 30])  # B..G

# ═══════════════════════ Sheet 7: النصوص_الجاهزة ═══════════════════════
ws7 = wb.create_sheet("النصوص_الجاهزة")
rtl_sheet(ws7)
put_title(ws7, "النصوص الافتتاحية الجاهزة للنسخ — بلسان كل طرف",
          "نسخ موجهة: عربي لسوكبيت · إنجليزي لمنصات VN والإندونيسيين — النص الكامل مع المتغيرات في دليل الحملة (docx)", 5)
hdr7 = ["الرمز", "الطرف / القناة", "اللغة", "النص الجاهز (انسخ واستبدل المتغيرات)"]
put_headers(ws7, hdr7)
scripts = [
    ["T1", "سوكبيت — تيليجرام @sookbit أو واتساب +33", "عربي",
     "السلام عليكم، معك أحمد — عميل API عندكم عبر بوت ProdSeller. أجهّز إطلاق متجر اشتراكات رقمية وسأبدأ بحجم شهري ثابت على عائلات ChatGPT وGemini وOffice. شفت بالقناة أسعار API المعلنة (مثل K12 بـ3.80 والـOffice جملة بـ0.17). ممكن الجدول الكامل لأسعار API/الجملة؟ وبحسب الحجم الشهري، ما أفضل تدرج تقدرون تعطونه؟"],
    ["T2", "سوكبيت — واتساب +33 (بديل فرنسي)", "فرنسي",
     "Bonjour, client API de ProdSellerBot ici. Je prépare le lancement d'une boutique d'abonnements numériques avec un volume mensuel fixe (ChatGPT, Gemini, Office). Pourriez-vous m'envoyer la grille tarifaire API/grossiste complète, ainsi que vos paliers selon le volume ? Merci."],
    ["T3", "HitMeow/canboso — الدعم @HitmeowSupport أو المالك @vahnix", "إنجليزي",
     "Hello! I run a PremiKey API account (ready to top up via Binance Pay). I'm launching a subscription store and need volume pricing for: ChatGPT Plus VIP (monthly, warranty), K12 2yr, and Deepseek API credits. Could you share your quantity tier table and replacement policy? Starting around 30-50 units/month, scaling up."],
    ["T4", "DigitalCore — بوت @DCoreStoreBot أو @DGTsupply", "إنجليزي",
     "Hello, I've reviewed your API docs (digitalcore.top/docs) and the published tier pricing. I'm preparing a subscription store launch. Two questions: (1) do you offer a tier above the published bands for 100+ units (e.g., Gemini 18M, Duolingo, Coursera)? (2) what are your replacement terms for a first test order?"],
    ["T5", "RichAIStore — تذكرة عبر API أو بوت @RichAIStoreBot", "إنجليزي",
     "Hi, I'm an API reseller integrating your Reseller API v1.0.0 into an automated store. My monthly volume on CDK products (Google 5TB family) is growing. Could we review my current unit prices against a 100/500-unit tier? Happy to commit to a monthly minimum for better rates."],
    ["T6", "AIVerseX — بوت @AIVerseXBot", "إنجليزي",
     "Hello, I buy Gemini Pro 18M regularly (your flash price is competitive). Instead of catching flashes, I'd like a fixed 30-day wholesale price for a weekly volume of 30-50 units. Do you offer volume contracts? Also interested in Office 365 and Adobe Express at scale."],
    ["T7", "AISUBSID — المالك @AisubsIDFounder", "إنجليزي",
     "Hello, I saw your channel announcement about the domain migration. I'm preparing a bulk purchase of ChatGPT Plus (10-50 units to start, growing monthly). Your bulk price was $2.50 - is it still valid post-migration? Also: are these UPI or VIP method accounts? I test survival rates before committing."],
    ["T8", "teamsoclo — أدمن القناة/البوابة", "إنجليزي مبسط",
     "Hello, I operate a subscription store and buy AI credit products (Codex family) through a reseller. I'm interested in a direct reseller account on your gateway (gpt.teamsoclo.site). Could you share the reseller requirements, the current rate card for the 15 models, and your replacement policy for downtime?"],
    ["T9", "aivaulthub reseller — بوت @Gemini_Shop_Robot", "إنجليزي",
     "Hello, I have a reseller API account and I'm scaling Gemini Pro 18M sales. Could you share your current reseller rate card for the Gemini family, and any volume tiers above the standard reseller price?"],
]
last7 = put_rows(ws7, scripts, wrap_cols={1, 3}, center_cols={0, 2}, row_h=66)
set_widths(ws7, [7, 33, 11, 95])  # B..E
note(ws7, last7 + 2, "متغيرات قبل الإرسال: الأرقام الشهرية (30–200 وحدة) — ثبّتها في W0 ولا تغيّرها بين الأطراف (الاتساق يقي من التناقض). القاعدة الحاكمة: لا ذكر لأي معرفة بنيوية (خوادم/بصمات/علاقة stackvault) في أي نص.", 5)

# ═══════════════════════ Sheet 8: المراجعة ═══════════════════════
ws8 = wb.create_sheet("المراجعة")
ws8.sheet_properties.tabColor = "FFC000"
rtl_sheet(ws8)
put_title(ws8, "المراجعة — فحوص اتساق حية", "تُحدَّث تلقائيًا عند إعادة الحساب — أي فشل يعني خللًا في البناء", 5)
put_headers(ws8, ["الفحص", "المتوقع", "الفعلي (معادلة حية)", "الحالة"])
checks = [
    ["عدد أطراف التفاوض الفعليين", 8, "=COUNTA('أطراف_التفاوض'!B5:B12)", '=IF(C5=D5,"مطابق","فشل")'],
    ["عدد الكيانات المستبعدة", 4, "=COUNTA('أطراف_التفاوض'!B15:B18)", '=IF(C6=D6,"مطابق","فشل")'],
    ["عدد السيناريوهات المدروسة", 30, "=COUNTA('السيناريوهات'!B5:B34)", '=IF(C7=D7,"مطابق","فشل")'],
    ["عدد الطرق", 5, "=COUNTA('الطرق_والقنوات'!B5:B9)", '=IF(C8=D8,"مطابق","فشل")'],
    ["عدد أوراق الضغط", 11, "=COUNTA('أوراق_الضغط'!B5:B15)", '=IF(C9=D9,"مطابق","فشل")'],
    ["عدد صفوف خطة الموجات", 5, "=COUNTA('خطة_الموجات'!B5:B9)", '=IF(C10=D10,"مطابق","فشل")'],
    ["عدد النصوص الجاهزة", 9, "=COUNTA('النصوص_الجاهزة'!B5:B13)", '=IF(C11=D11,"مطابق","فشل")'],
    ["مجموع احتمالات سوكبيت (S-A) = 100%", 1.0, "=SUM('السيناريوهات'!E5:E9)", '=IF(ABS(C12-D12)<0.001,"مطابق","فشل")'],
    ["مجموع احتمالات HitMeow (S-B) = 100%", 1.0, "=SUM('السيناريوهات'!E10:E14)", '=IF(ABS(C13-D13)<0.001,"مطابق","فشل")'],
    ["مجموع احتمالات teamsoclo (S-C) = 100%", 1.0, "=SUM('السيناريوهات'!E15:E18)", '=IF(ABS(C14-D14)<0.001,"مطابق","فشل")'],
    ["مجموع احتمالات DigitalCore (S-D) = 100%", 1.0, "=SUM('السيناريوهات'!E19:E21)", '=IF(ABS(C15-D15)<0.001,"مطابق","فشل")'],
    ["مجموع احتمالات RichAI (S-E) = 100%", 1.0, "=SUM('السيناريوهات'!E22:E24)", '=IF(ABS(C16-D16)<0.001,"مطابق","فشل")'],
    ["مجموع احتمالات AIVerseX (S-F) = 100%", 1.0, "=SUM('السيناريوهات'!E25:E28)", '=IF(ABS(C17-D17)<0.001,"مطابق","فشل")'],
    ["مجموع احتمالات AISUBSID (S-G) = 100%", 1.0, "=SUM('السيناريوهات'!E29:E31)", '=IF(ABS(C18-D18)<0.001,"مطابق","فشل")'],
]
put_rows(ws8, checks, center_cols={1, 2, 3}, row_h=24)
set_widths(ws8, [40, 10, 34, 12])  # B..E
note(ws8, 5 + len(checks) + 1, "الفحوص الحية تُقيَّم عند فتح الملف أو إعادة الحساب — نتائج التحقق الآلي (recalc/audit/scan/validate) مرفقة بتقرير الجولة في worklog.", 5)

wb.save(OUT)
print("XLSX written:", OUT, f"({os.path.getsize(OUT)//1024} KB)")
