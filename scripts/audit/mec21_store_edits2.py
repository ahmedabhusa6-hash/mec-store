# MEC-21 part 2: remaining store.tsx edits (verified current strings)
import sys

PATH = "/home/z/my-project/src/components/store/store.tsx"
src = open(PATH, encoding="utf-8").read()

edits = []

# 1. Empty search state (8-space indent anchor, verified)
edits.append((
    '        {!hasPhone && (\n          <div className="text-[10.5px] text-amber-400',
    '        {q.trim() && filtered.length === 0 && (\n          <div className="text-[11px] text-zinc-400 bg-zinc-950/70 border border-zinc-800 rounded px-3 py-2.5">\n            🔍 لا نتائج — جرّب اسمًا عربيًا (شات جي بي تي، نتفلكس، كانفا) أو إنجليزيًا (ChatGPT، Netflix، Canva)\n          </div>\n        )}\n        {!hasPhone && (\n          <div className="text-[10.5px] text-amber-400'
))

# 2. OOS button -> waitlist CTA + h-11 + feedback line (verified bytes)
edits.append((
    '<Button\n                  className="w-full h-10 text-xs bg-emerald-900 hover:bg-emerald-800 text-emerald-100 disabled:opacity-50"\n                  disabled={!availability.ok}\n                  onClick={() => onBuy(p)}\n                >\n                  {availability.ok ? "🛒 اشترِ الآن — تسليم ≤3 دقائق" : "نفد — فعّل تنبيه التوفير"}\n                </Button>',
    '<Button\n                  className="w-full h-11 text-xs bg-emerald-900 hover:bg-emerald-800 text-emerald-100"\n                  disabled={!availability.ok && wlBusy === p.slug}\n                  onClick={() => (availability.ok ? onBuy(p) : joinWaitlist(p))}\n                >\n                  {availability.ok\n                    ? "🛒 اشترِ الآن — تسليم ≤3 دقائق"\n                    : wlBusy === p.slug ? "⏳ جارٍ تسجيلك…" : "🔔 نفد — انضم لقائمة الانتظار"}\n                </Button>\n                {wlDone[p.slug] && (\n                  <div className="text-[11px] text-amber-300 leading-4">{wlDone[p.slug]}</div>\n                )}'
))

# 3. RTL flow arrows
edits.append((
    'يفحص السلسلة → حارس الهامش → حارس الرصيد الحي → الشراء…',
    'يفحص السلسلة ← حارس الهامش ← حارس الرصيد الحي ← الشراء…'
))

# 4. Internal codename W1 -> customer wording
edits.append((
    'حدود W1: $5–$500',
    'حدود الإيداع: $5–$500'
))

# 5. Admin token input aria-label
edits.append((
    'placeholder="admin token…"',
    'placeholder="admin token…"\n                aria-label="رمز التشغيل (admin token)"'
))

# 6. Deposit amount input aria-label
edits.append((
    '<Input\n              dir="ltr" type="number" min="5" max="500"',
    '<Input\n              dir="ltr" type="number" min="5" max="500" aria-label="مبلغ الإيداع بالدولار"'
))

# 7. StoreGrid call site: pass phone prop (verified bytes)
edits.append((
    '        <StoreGrid\n          data={catalog}\n          region={region}\n          hasPhone={!!phone}\n          onBuy=',
    '        <StoreGrid\n          data={catalog}\n          region={region}\n          hasPhone={!!phone}\n          phone={phone}\n          onBuy='
))

failures = []
for i, (old, new) in enumerate(edits, 1):
    n = src.count(old)
    if n == 0:
        failures.append((i, old[:70].replace("\n", "\\n")))
        continue
    if n > 1:
        failures.append((i, f"AMBIGUOUS x{n}: " + old[:50].replace("\n", "\\n")))
        continue
    src = src.replace(old, new)

if failures:
    print("FAILED REPLACEMENTS:")
    for i, ctx in failures:
        print(f"  #{i}: {ctx}")
    sys.exit(1)

# 8. Wholesale accessibility pass
before_sizes = src.count('text-[10px]') + src.count('text-[10.5px]')
src = src.replace('text-[10px]', 'text-[11px]').replace('text-[10.5px]', 'text-[11px]')
contrast_fixed = src.count('text-zinc-600') + src.count('text-zinc-500')
src = src.replace('text-zinc-600', 'text-zinc-400').replace('text-zinc-500', 'text-zinc-400')

open(PATH, "w", encoding="utf-8").write(src)
print(f"OK: {len(edits)} structural edits applied")
print(f"    micro-text bumped: {before_sizes} instances -> text-[11px]")
print(f"    contrast raised: {contrast_fixed} instances -> text-zinc-400")
