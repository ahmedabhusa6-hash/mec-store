# MEC-21: byte-precise replacements for store.tsx (bypasses display-layer corruption)
# Each replacement is verified; file written back ONLY if all succeed.
import sys

PATH = "/home/z/my-project/src/components/store/store.tsx"
src = open(PATH, encoding="utf-8").read()

edits = []

# 1. Product type: add aliases
edits.append((
    'type Product = {\n  slug: string; name: string; family: string; sourceTier: string; officialUsd: number | null;\n  chain: Chain[]; prices: Record<string, { price: number; currency: string }>;\n};',
    'type Product = {\n  slug: string; name: string; aliases: string; family: string; sourceTier: string; officialUsd: number | null;\n  chain: Chain[]; prices: Record<string, { price: number; currency: string }>;\n};'
))

# 2. StoreGrid signature + waitlist state + alias-aware filter
edits.append((
    'function StoreGrid({ data, region, hasPhone, onBuy, onRefresh }: {\n  data: CatalogData; region: string; hasPhone: boolean;\n  onBuy: (p: Product) => void; onRefresh: () => void;\n}) {\n  const [family, setFamily] = useState("الكل");\n  const [q, setQ] = useState("");\n  const filtered = data.products.filter(\n    (p) => (family === "الكل" || p.family === family) &&\n      (!q.trim() || p.name.toLowerCase().includes(q.trim().toLowerCase()))\n  );',
    'function StoreGrid({ data, region, hasPhone, phone, onBuy, onRefresh }: {\n  data: CatalogData; region: string; hasPhone: boolean; phone: string | null;\n  onBuy: (p: Product) => void; onRefresh: () => void;\n}) {\n  const [family, setFamily] = useState("الكل");\n  const [q, setQ] = useState("");\n  // FIX (P2, MEC-21-E G12): OOS waitlist join state (was a dead disabled button)\n  const [wlBusy, setWlBusy] = useState<string | null>(null);\n  const [wlDone, setWlDone] = useState<Record<string, string>>({});\n  const joinWaitlist = async (p: Product) => {\n    if (!phone) {\n      setWlDone((m) => ({ ...m, [p.slug]: "⚠️ سجّل رقم جوالك من الأعلى أولًا — سيصلك التنبيه فور التوفر" }));\n      return;\n    }\n    setWlBusy(p.slug);\n    const res = await api("/api/store/waitlist", { phone, slug: p.slug });\n    setWlBusy(null);\n    setWlDone((m) => ({ ...m, [p.slug]: res.ok ? res.note : res.error || "تعذّر التسجيل — أعد المحاولة" }));\n  };\n  // FIX (MEC-21-B): Arabic search — 25/37 names are Latin-only supplier jargon;\n  // Arabic queries («نتفلكس»، «كانفا») previously returned a silent blank grid.\n  const filtered = data.products.filter(\n    (p) => (family === "الكل" || p.family === family) &&\n      (!q.trim() ||\n        p.name.toLowerCase().includes(q.trim().toLowerCase()) ||\n        (p.aliases ?? "").toLowerCase().includes(q.trim().toLowerCase()))\n  );'
))

# 3. Search input: aria-label + bilingual placeholder
edits.append((
    'placeholder="ابحث عن منتج… (ChatGPT، شاهد، Steam…)"',
    'aria-label="البحث في المتجر"\n            placeholder="ابحث عربيًا أو إنجليزيًا… (شات جي بي تي، نتفلكس، ChatGPT…)"'
))

# 4. Empty search state (insert before the hasPhone pricing notice)
edits.append((
    '        {!hasPhone && (\n          <div className="text-[10.5px] text-amber-400',
    '        {q.trim() && filtered.length === 0 && (\n          <div className="text-[11px] text-zinc-400 bg-zinc-950/70 border border-zinc-800 rounded px-3 py-2.5">\n            🔍 لا نتائج — جرّب اسمًا عربيًا (شات جي بي تي، نتفلكس، كانفا) أو إنجليزيًا (ChatGPT، Netflix، Canva)\n          </div>\n        )}\n        {!hasPhone && (\n          <div className="text-[10.5px] text-amber-400'
))

# 5. OOS button -> waitlist CTA + feedback line + h-11 tap target
edits.append((
    '<Button\n                  className="w-full h-10 text-xs bg-emerald-900 hover:bg-emerald-800 text-emerald-100 disabled:opacity-50"\n                  disabled={!availability.ok}\n                  onClick={() => onBuy(p)}\n                >\n                  {availability.ok ? "🛒 اشترِ الآن — تسليم ≤3 دقائق" : "نفد — فعّل تنبيه التوفير"}\n                </Button>',
    '<Button\n                  className="w-full h-11 text-xs bg-emerald-900 hover:bg-emerald-800 text-emerald-100"\n                  disabled={!availability.ok && wlBusy === p.slug}\n                  onClick={() => (availability.ok ? onBuy(p) : joinWaitlist(p))}\n                >\n                  {availability.ok\n                    ? "🛒 اشترِ الآن — تسليم ≤3 دقائق"\n                    : wlBusy === p.slug ? "⏳ جارٍ تسجيلك…" : "🔔 نفد — انضم لقائمة الانتظار"}\n                </Button>\n                {wlDone[p.slug] && (\n                  <div className="text-[11px] text-amber-300 leading-4">{wlDone[p.slug]}</div>\n                )}'
))

# 6. RTL flow arrows (forward progression points LEFT in RTL)
edits.append((
    'يفحص السلسلة → حارس الهامش → حارس الرصيد الحي → الشراء…',
    'يفحص السلسلة ← حارس الهامش ← حارس الرصيد الحي ← الشراء…'
))

# 7. Internal codename W1 -> customer-facing wording
edits.append((
    'حدود W1: $5–$500',
    'حدود الإيداع: $5–$500'
))

# 8. Admin token input aria-label
edits.append((
    'placeholder="admin token…"',
    'placeholder="admin token…"\n                aria-label="رمز التشغيل (admin token)"'
))

# 9. Deposit amount input aria-label
edits.append((
    '<Input\n              dir="ltr" type="number" min="5" max="500"',
    '<Input\n              dir="ltr" type="number" min="5" max="500" aria-label="مبلغ الإيداع بالدولار"'
))

# 10. StoreGrid call site: pass phone prop
edits.append((
    '<StoreGrid\n          data={catalog}\n          region={region}\n          hasPhone={!!phone}',
    '<StoreGrid\n          data={catalog}\n          region={region}\n          hasPhone={!!phone}\n          phone={phone}'
))

failures = []
for i, (old, new) in enumerate(edits, 1):
    n = src.count(old)
    if n == 0:
        failures.append((i, old[:60].replace("\n", "\\n")))
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

# 11. Wholesale accessibility pass (only after all structural edits landed):
# D1: micro-text >= 11px ; D2: zinc-600/zinc-500 text -> zinc-400 (contrast)
before_sizes = src.count('text-[10px]') + src.count('text-[10.5px]')
src = src.replace('text-[10px]', 'text-[11px]').replace('text-[10.5px]', 'text-[11px]')
contrast_fixed = src.count('text-zinc-600') + src.count('text-zinc-500')
src = src.replace('text-zinc-600', 'text-zinc-400').replace('text-zinc-500', 'text-zinc-400')

open(PATH, "w", encoding="utf-8").write(src)
print(f"OK: {len(edits)} structural edits applied")
print(f"    micro-text bumped: {before_sizes} instances -> text-[11px]")
print(f"    contrast raised (zinc-600/500 -> zinc-400): {contrast_fixed} instances")
