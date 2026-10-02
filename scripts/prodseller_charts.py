#!/usr/bin/env python3
# ProdSeller package charts (Arabic labels via reshaper+bidi, indigo palette matching docx)
import json
import matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/freefont/FreeSerif.ttf')
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'FreeSerif']
plt.rcParams['axes.unicode_minus'] = False

def ar(text):
    return get_display(arabic_reshaper.reshape(text))

OUT = '/home/z/my-project/research/prodseller_live'

# indigo palette (doc identity)
C_MAIN = '#3E3878'
C_ACC = '#9D8CFF'
C_SEC = '#5B6B7D'
C_MUT = ['#3E3878', '#554E96', '#6F66B0', '#8B82C4', '#A9A2D8', '#C9C4EA', '#E4E1F5']

# ── Chart 1: top products by units sold (sales velocity) ──
d = json.load(open(f'{OUT}/products_fresh.json'))['products']
top = sorted(d, key=lambda p: -p.get('sold', 0))[:10]
names = [p['name'][:28] for p in top][::-1]
vals = [p.get('sold', 0) for p in top][::-1]
fig, ax = plt.subplots(figsize=(8.6, 4.8), constrained_layout=True)
colors = [C_MAIN if v >= 4000 else '#6F66B0' if v >= 300 else '#A9A2D8' for v in vals]
ax.barh(range(len(names)), vals, color=colors, height=0.62)
ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=9.5)
ax.set_xlabel(ar('الوحدات المبيعة عبر المتجر (عدّاد API الرسمي — 29/09/2026)'), fontsize=10, color=C_SEC)
ax.set_title(ar('أعلى 10 منتجات مبيعًا لدى Prodseller — مؤشر سرعة الدوران'), fontsize=13, color='#1E1B33', pad=12)
for i, v in enumerate(vals):
    ax.text(v + 2500, i, f'{v:,}', va='center', fontsize=9.5, color=C_SEC)
ax.spines[['top', 'right']].set_visible(False)
ax.set_xlim(0, 245000)
fig.savefig(f'{OUT}/chart_sold.png', dpi=200)
plt.close(fig)

# ── Chart 2: Gemini 18M price timeline (published channel prices Jul–Sep) ──
timeline = [
    ('21/07', 0.55), ('23/07', 0.50), ('25/07', 0.46), ('28/07', 1.00),
    ('29/07', 0.80), ('30/07', 0.75), ('31/07', 0.59), ('01/08', 0.46),
    ('04/08', 0.45), ('16/08', 0.44), ('11/09', 0.43), ('19/09', 0.49),
    ('20/09', 0.49), ('25/09', 0.69), ('27/09', 0.48), ('29/09', 0.89),
]
xs = list(range(len(timeline)))
ys = [t[1] for t in timeline]
labels = [t[0] for t in timeline]
fig, ax = plt.subplots(figsize=(9.0, 4.2), constrained_layout=True)
ax.plot(xs, ys, color=C_MAIN, linewidth=2.2, marker='o', markersize=5, markerfacecolor=C_ACC, markeredgecolor=C_MAIN)
ax.fill_between(xs, ys, 0.40, color=C_ACC, alpha=0.12)
ax.axhline(0.41, color='#2E8B57', linestyle='--', linewidth=1.2)
ax.text(0.2, 0.425, ar('الأرضية التاريخية 0.41$ (01/08)'), fontsize=9, color='#2E8B57')
ax.axhline(0.89, color='#B04040', linestyle='--', linewidth=1.2)
ax.text(0.2, 0.915, ar('السعر الحي 29/09: 0.89$'), fontsize=9, color='#B04040')
ax.set_xticks(xs)
ax.set_xticklabels(labels, fontsize=9, rotation=45)
ax.set_ylabel(ar('السعر المعلن للرابط ($)'), fontsize=10, color=C_SEC)
ax.set_title(ar('تقلب سعر Gemini Pro 18 شهرًا كما أعلنته قناة Prodseller (يوليو–سبتمبر 2026)'), fontsize=12.5, color='#1E1B33', pad=12)
ax.spines[['top', 'right']].set_visible(False)
ax.set_ylim(0.35, 1.08)
ax.grid(axis='y', alpha=0.25)
fig.savefig(f'{OUT}/chart_gemini_timeline.png', dpi=200)
plt.close(fig)

# ── Chart 3: API discount vs public price per product ──
disc = []
for p in d:
    fin, pub = p.get('finalPrice'), p.get('publicPrice')
    if fin and pub and pub > fin:
        disc.append((p['name'][:24], (1 - fin / pub) * 100))
disc.sort(key=lambda x: -x[1])
disc = disc[:12]
names3 = [x[0] for x in disc][::-1]
vals3 = [x[1] for x in disc][::-1]
fig, ax = plt.subplots(figsize=(8.6, 4.8), constrained_layout=True)
colors3 = [C_MAIN if v >= 15 else '#6F66B0' if v >= 8 else '#A9A2D8' for v in vals3]
ax.barh(range(len(names3)), vals3, color=colors3, height=0.62)
ax.set_yticks(range(len(names3)))
ax.set_yticklabels(names3, fontsize=9.5)
ax.set_xlabel(ar('خصم سعر API عن السعر العام المعلن (٪) — عضوية Bronze'), fontsize=10, color=C_SEC)
ax.set_title(ar('أين يحقق حساب API أكبر خصم — أعلى 12 منتجًا (29/09/2026)'), fontsize=12.5, color='#1E1B33', pad=12)
for i, v in enumerate(vals3):
    ax.text(v + 0.4, i, f'{v:.0f}%', va='center', fontsize=9.5, color=C_SEC)
ax.spines[['top', 'right']].set_visible(False)
ax.set_xlim(0, 32)
fig.savefig(f'{OUT}/chart_discount.png', dpi=200)
plt.close(fig)

print('charts saved: chart_sold.png, chart_gemini_timeline.png, chart_discount.png')
