#!/usr/bin/env python3
# StackVault report charts (Arabic labels via reshaper+bidi, Morandi-consistent palette)
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

OUT = '/home/z/my-project/research/stackvault_live'

# palette (doc accent family: deep cyan/teal like DM-1)
C_MAIN = '#1B6B7A'
C_ACC = '#37DCF2'
C_SEC = '#5B6B7D'
C_MUT = ['#1B6B7A', '#2E8FA0', '#5FB3C0', '#8FCCD5', '#B8DDE3', '#D0E8EC', '#E4F2F4']

# ── Chart 1: category distribution ──
cats = {"Digital Services": 173, "AI Subscriptions": 103, "Design & Editing": 58,
        "Software Keys": 15, "Learning": 4, "Streaming": 3, "Bulk Emails": 1}
ar_cats = {"Digital Services": "خدمات رقمية", "AI Subscriptions": "اشتراكات ذكاء اصطناعي",
           "Design & Editing": "تصميم وتحرير", "Software Keys": "مفاتيح برمجيات",
           "Learning": "تعليم", "Streaming": "بث", "Bulk Emails": "بريد جماعي"}
names = [ar_cats[k] for k in cats]
vals = list(cats.values())
fig, ax = plt.subplots(figsize=(8.6, 4.4), constrained_layout=True)
bars = ax.barh(range(len(names))[::-1], vals, color=[C_MAIN if v >= 50 else '#5FB3C0' if v >= 10 else '#B8DDE3' for v in vals], height=0.62)
ax.set_yticks(range(len(names))[::-1])
ax.set_yticklabels([ar(n) for n in names], fontsize=11)
ax.set_xlabel(ar('عدد المنتجات (من أصل 357)'), fontsize=10, color=C_SEC)
ax.set_title(ar('توزيع كتالوج StackVault حسب الفئة — 29/09/2026'), fontsize=13, color='#162235', pad=12)
for i, v in enumerate(vals):
    ax.text(v + 2.5, (len(names)-1-i), str(v), va='center', fontsize=10, color=C_SEC)
ax.spines[['top', 'right']].set_visible(False)
ax.set_xlim(0, 200)
fig.savefig(f'{OUT}/chart_categories.png', dpi=200)
plt.close(fig)

# ── Chart 2: margin distribution ──
d = json.load(open(f'{OUT}/sv_products_current.json'))
prods = d if isinstance(d, list) else d.get('products', [])
margins = []
for p in prods:
    if p.get('price') and p.get('costPrice') and p['price'] > 0:
        margins.append((p['price'] - p['costPrice']) / p['price'] * 100)
fig, ax = plt.subplots(figsize=(8.6, 4.2), constrained_layout=True)
bins = [10, 15, 20, 25, 30, 35, 40, 45, 50, 65]
n, b, patches = ax.hist(margins, bins=bins, color=C_MAIN, edgecolor='white', linewidth=1.2)
ax.set_xlabel(ar('نسبة هامش الربح ٪ (سعر البيع − سعر التكلفة) ÷ سعر البيع'), fontsize=10, color=C_SEC)
ax.set_ylabel(ar('عدد المنتجات'), fontsize=10, color=C_SEC)
ax.set_title(ar(f'توزيع هوامش الربح المعلنة في الواجهة العامة — متوسط {sum(margins)/len(margins):.1f}٪ (n={len(margins)})'), fontsize=12.5, color='#162235', pad=12)
for i, cnt in enumerate(n):
    if cnt > 0:
        ax.text((b[i]+b[i+1])/2, cnt + 2, str(int(cnt)), ha='center', fontsize=9.5, color=C_SEC)
ax.spines[['top', 'right']].set_visible(False)
fig.savefig(f'{OUT}/chart_margins.png', dpi=200)
plt.close(fig)

# ── Chart 3: supply chain composition (ps_ vs mr_) ──
fig, ax = plt.subplots(figsize=(7.6, 3.6), constrained_layout=True)
labels = [ar('معرّفات ps_ (بصمة ProdSeller)'), ar('معرّفات mr_ (مصدر ثانوي)'), ar('منتج اختبار')]
sizes = [319, 37, 1]
colors = [C_MAIN, '#5FB3C0', '#D9E2E6']
w, _, autotexts = ax.pie(sizes, colors=colors, autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
                          startangle=90, pctdistance=0.75,
                          wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2))
for t in autotexts:
    t.set_color('white'); t.set_fontsize(11); t.set_fontweight('bold')
ax.legend([ar(f'ps_ — {319} منتجًا (89.4٪)'), ar(f'mr_ — {37} منتجًا (10.4٪)'), ar('اختبار مجاني — 1')],
          loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=10, frameon=False)
ax.set_title(ar('تركيب الكتالوج حسب بصمة معرّف المصدر'), fontsize=12.5, color='#162235', pad=10)
fig.savefig(f'{OUT}/chart_ids.png', dpi=200)
plt.close(fig)
print('charts done:', f'{OUT}/chart_categories.png', f'{OUT}/chart_margins.png', f'{OUT}/chart_ids.png')
