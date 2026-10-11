"use client";

/**
 * MEC — public price explorer UI: product grouping, cheapest highlight,
 * instant search, freshness badges, Arabic RTL.
 */
import { useMemo, useState } from "react";
import { Search, ShieldCheck, Clock, RefreshCw } from "lucide-react";

export type PublicRow = {
  product: string;
  supplier: string;
  username: string | null;
  isPrivate: boolean;
  price: number | null;
  currency: string;
  unit: string | null;
  postedAt: string | null;
  ageHours: number | null;
  freshness: string;
};

const FRESH: Record<string, { label: string; cls: string }> = {
  fresh: { label: "حديث", cls: "bg-emerald-950/60 text-emerald-300 border-emerald-900/70" },
  aging: { label: "يتقادم", cls: "bg-amber-950/60 text-amber-300 border-amber-900/70" },
  stale: { label: "قديم — تحقق قبل الاعتماد", cls: "bg-rose-950/60 text-rose-300 border-rose-900/70" },
  ancient: { label: "متقادم جدًا", cls: "bg-rose-950/60 text-rose-300 border-rose-900/70" },
  unknown: { label: "غير مؤرخ", cls: "bg-zinc-900 text-zinc-400 border-zinc-800" },
};

function timeAgo(iso: string | null): string {
  if (!iso) return "—";
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (m < 60) return `قبل ${m} دقيقة`;
  const h = Math.floor(m / 60);
  if (h < 24) return `قبل ${h} ساعة`;
  const d = Math.floor(h / 24);
  return `قبل ${d} يوم`;
}

export function PublicExplorer({ rows, dbError }: { rows: PublicRow[]; dbError: string | null }) {
  const [q, setQ] = useState("");

  const products = useMemo(() => {
    const byProd = new Map<string, PublicRow[]>();
    for (const r of rows) {
      (byProd.get(r.product) ?? byProd.set(r.product, []).get(r.product)!).push(r);
    }
    const out = [...byProd.entries()].map(([product, arr]) => {
      const sorted = [...arr].sort((a, b) => (a.price ?? 1e9) - (b.price ?? 1e9));
      return {
        product,
        best: sorted[0],
        suppliers: new Set(arr.map((x) => x.supplier)).size,
        latest: arr.reduce<string | null>((acc, x) => (!acc || (x.postedAt && x.postedAt > acc) ? x.postedAt : acc), null),
      };
    });
    out.sort((a, b) => b.suppliers - a.suppliers || (a.best.price ?? 0) - (b.best.price ?? 0));
    return out;
  }, [rows]);

  const filtered = useMemo(() => {
    const v = q.trim().toLowerCase();
    if (!v) return products.slice(0, 250);
    return products
      .filter((p) => p.product.toLowerCase().includes(v) || p.best.supplier.toLowerCase().includes(v))
      .slice(0, 250);
  }, [products, q]);

  const supplierCount = new Set(rows.map((r) => r.supplier)).size;
  const freshCount = rows.filter((r) => r.freshness === "fresh").length;

  return (
    <div dir="rtl" className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      {/* header */}
      <header className="border-b border-zinc-800/70 bg-[#0b111c]">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-emerald-950/80 border border-emerald-800/80 flex items-center justify-center shrink-0">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden>
                <path d="M3 17 L9 11 L13 15 L21 7" stroke="#34d399" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="21" cy="7" r="2.2" fill="#34d399" />
              </svg>
            </div>
            <div>
              <h1 className="text-[22px] font-extrabold text-zinc-50 leading-7">MEC — قاعدة أسعار الموردين الحية</h1>
              <p className="text-[12px] text-zinc-500 mt-0.5">
                قياس آلي مستمر لأسعار المنتجات الرقمية من قنوات ومجموعات الموردين في تلغرام · مسح تفاضلي كل 30 دقيقة
              </p>
            </div>
          </div>

          {/* stats */}
          <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {[
              { n: rows.length.toLocaleString("en-US"), l: "أحدث سعر معروض" },
              { n: products.length.toLocaleString("en-US"), l: "منتجًا مراقبًا" },
              { n: supplierCount.toLocaleString("en-US"), l: "مورّدًا نشطًا" },
              { n: `${rows.length ? Math.round((freshCount / rows.length) * 100) : 0}%`, l: "أسعار حديثة ≤24 ساعة" },
            ].map((s, i) => (
              <div key={i} className="rounded-xl border border-zinc-800/80 bg-[#0d1421] px-3.5 py-3">
                <div className="text-xl font-extrabold tabular-nums text-emerald-400">{s.n}</div>
                <div className="text-[10.5px] text-zinc-500 mt-0.5">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* search */}
      <div className="max-w-5xl w-full mx-auto px-4 pt-5">
        <div className="relative">
          <Search className="absolute start-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="ابحث عن منتج أو مورد… (مثال: Claude، ChatGPT، Gemini، VPN)"
            className="w-full rounded-xl border border-zinc-800 bg-[#0d1421] ps-10 pe-4 py-3 text-[13.5px] text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-emerald-800"
          />
        </div>
      </div>

      {/* table */}
      <main className="max-w-5xl w-full mx-auto px-4 py-4 flex-1">
        {dbError ? (
          <div className="rounded-xl border border-rose-900/60 bg-rose-950/30 p-5 text-center text-[13px] text-rose-300">
            تعذر الاتصال بقاعدة البيانات الحية — أعد المحاولة بعد لحظات ({dbError.slice(0, 120)})
          </div>
        ) : filtered.length === 0 ? (
          <div className="py-14 text-center text-[13px] text-zinc-500">لا نتائج مطابقة لبحثك</div>
        ) : (
          <div className="rounded-xl border border-zinc-800/80 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-[12.5px]">
                <thead>
                  <tr className="bg-[#0b111c] text-zinc-500">
                    <th className="text-start py-3 px-3.5 font-semibold">المنتج</th>
                    <th className="text-start py-3 px-3.5 font-semibold">أرخص مورد</th>
                    <th className="text-start py-3 px-3.5 font-semibold">السعر</th>
                    <th className="text-start py-3 px-3.5 font-semibold">الموردون</th>
                    <th className="text-start py-3 px-3.5 font-semibold">آخر تحديث</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((p, i) => {
                    const fr = FRESH[p.best.freshness] ?? FRESH.unknown;
                    return (
                      <tr key={p.product} className={`border-t border-zinc-800/60 hover:bg-zinc-900/40 ${p.suppliers >= 3 ? "bg-emerald-950/10" : ""}`}>
                        <td className="py-2.5 px-3.5 text-zinc-200 font-medium max-w-64">
                          <div className="truncate" title={p.product}>{p.product}</div>
                          {p.best.unit && <span className="text-[10px] text-zinc-500">{p.best.unit}</span>}
                        </td>
                        <td className="py-2.5 px-3.5 text-amber-300/90 max-w-40">
                          <span className="truncate block" title={p.best.supplier}>
                            {p.best.supplier}{p.best.isPrivate && <span className="text-[9.5px] text-zinc-500 ms-1">(خاصة)</span>}
                          </span>
                        </td>
                        <td className="py-2.5 px-3.5 whitespace-nowrap">
                          <span className="font-extrabold text-emerald-400 tabular-nums">{p.best.price}</span>{" "}
                          <span className="text-[10.5px] text-zinc-500">{p.best.currency === "USDT" ? "USDT" : "$"}</span>
                        </td>
                        <td className="py-2.5 px-3.5 tabular-nums text-zinc-300">{p.suppliers}</td>
                        <td className="py-2.5 px-3.5 whitespace-nowrap">
                          <span className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-medium ${fr.cls}`}>
                            <Clock className="w-2.5 h-2.5" /> {timeAgo(p.latest)}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* footer */}
      <footer className="border-t border-zinc-800/70 bg-[#0b111c] mt-6">
        <div className="max-w-5xl mx-auto px-4 py-4 text-[11px] text-zinc-500 leading-6">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
            <span>الأسعار معلنة من المتاجر ولم تُختبر بالشراء الفعلي بعد · السعر القديم يُعرض موسومًا بحالته ولا يُقدَّم كسعر حالي مؤكد</span>
          </div>
          <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1">
            <RefreshCw className="w-3.5 h-3.5 text-zinc-600" />
            <span>المسح: مراقب تلغرام الآلي (GitHub Actions) كل 30 دقيقة → Supabase → هذه الصفحة · حقائق فقط، لا نصوص رسائل</span>
            <span>·</span>
            <a href="/login" className="text-zinc-600 hover:text-zinc-400">دخول المالك</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
