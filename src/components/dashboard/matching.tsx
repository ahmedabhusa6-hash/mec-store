"use client";

/**
 * MEC — cross-provider product matching & benchmark view (Phase-5, 2026-10-13).
 * Deterministic rule-based matching (providers/matching.py) — no AI/ML on
 * provider data. Every benchmark shows its real offers with full names so the
 * owner can audit the match. Owner-only by design.
 */
import { Fragment, useState } from "react";
import { GitCompareArrows, Search, ChevronDown, ChevronLeft, TrendingDown, Layers, Percent, RefreshCw } from "lucide-react";
import { useApi, Badge, KpiCard, LoadingRows, ErrorState, EmptyState, fmtPrice, timeAgo } from "./kit";

type Benchmark = {
  match_key: string; brand: string; product_core: string; tier: string | null;
  duration: string | null; quantity: string | null;
  offers: number; providers: number;
  min_price: number | null; max_price: number | null; avg_price: number | null;
  spread_pct: number | null; cheapest_provider: string | null;
  cheapest_offer: string | null; dearest_provider: string | null;
  last_matched_at: string | null;
};

type Offer = {
  provider_code: string; external_id: string; product_name: string;
  unit_price: number | null; currency: string | null; discount_pct: number | null;
  unit_cost: number | null; stock: string | null; status: string | null;
  fetched_at: string | null;
};

const PROVIDER_AR: Record<string, string> = {
  stackvault: "StackVault", prodseller: "ProdSeller", acczone: "Acczone",
  aivaulthub: "AIVaultHub", aiversex: "AIVerseX", richai: "RichAI",
  digitalcore: "DigitalCore", aixpress: "AIXpress", reloadly: "Reloadly",
};

function label(b: Benchmark): string {
  const core = b.product_core.replace(/_/g, " ");
  const tier = b.tier && b.tier !== "std" ? ` ${b.tier.replace(/_/g, " ")}` : "";
  return `${core}${tier}`;
}

function OffersList({ matchKey, benchmark }: { matchKey: string; benchmark: Benchmark }) {
  const { data, loading, error } = useApi<{ offers: Offer[] }>(
    `/api/admin/matching?key=${encodeURIComponent(matchKey)}`, [matchKey], 0);
  if (loading) return <div className="py-2 text-center text-[11px] text-slate-500">جارٍ تحميل العروض…</div>;
  if (error) return <div className="py-2 text-center text-[11px] text-rose-400">{error}</div>;
  return (
    <div className="space-y-1.5">
      {(data?.offers ?? []).map((o, i) => (
        <div key={`${o.provider_code}-${o.external_id}-${i}`}
          className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-800/60 bg-slate-950/50 px-3 py-2">
          <div className="flex items-center gap-2">
            <Badge tone={i === 0 ? "green" : "gray"}>
              {PROVIDER_AR[o.provider_code] ?? o.provider_code}
            </Badge>
            <span className="text-[12px] text-slate-300" dir="auto">{o.product_name}</span>
          </div>
          <div className="flex items-center gap-3 text-[11px] text-slate-500">
            {o.discount_pct !== null && <span>خصم {o.discount_pct}%</span>}
            {o.unit_cost !== null && <span>تكلفة {fmtPrice(o.unit_cost)}</span>}
            <span>مخزون: {o.stock ?? "—"}</span>
            <span>{timeAgo(o.fetched_at)}</span>
            <span className="font-medium text-slate-200">{fmtPrice(o.unit_price, o.currency ?? "USD")}</span>
          </div>
        </div>
      ))}
      <div className="pt-1 text-[10px] text-slate-600">
        مفتاح المطابقة: <span className="font-mono" dir="ltr">{matchKey}</span> · آخر مطابقة {timeAgo(benchmark.last_matched_at)} · مطابقة حتمية بالقواعد (بلا AI)
      </div>
    </div>
  );
}

export function MatchingView() {
  const [comparable, setComparable] = useState(true);
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("spread");
  const query = `/api/admin/matching?comparable=${comparable ? 1 : 0}` +
    (q ? `&q=${encodeURIComponent(q)}` : "") + `&sort=${sort}`;
  const { data, error, loading, refresh } = useApi<{
    total: number;
    stats: { benchmarks: number; comparable: number; maxSpread: number; providersCovered: number };
    rows: Benchmark[];
  }>(query, [comparable, q, sort], 60_000);

  const [openKey, setOpenKey] = useState<string | null>(null);

  if (loading && !data) return <LoadingRows rows={8} />;
  if (error) return <ErrorState text={error} />;
  if (!data) return <EmptyState text="لا بيانات مطابقة بعد" />;

  const s = data.stats;

  return (
    <div className="space-y-5">
      {/* header stats */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <KpiCard icon={<Layers className="w-4 h-4" />} label="معايير موحدة" value={String(s.benchmarks)} sub="مفاتيح مطابقة حتمية" />
        <KpiCard icon={<GitCompareArrows className="w-4 h-4" />} tone="sky" label="قابلة للمقارنة" value={String(s.comparable)} sub="منتج يعرضه موردان فأكثر" />
        <KpiCard icon={<Percent className="w-4 h-4" />} tone="amber" label="أعلى فاصل سعري" value={`${s.maxSpread.toFixed(0)}%`} sub="بين أرخص وأغلى عرض" />
        <KpiCard icon={<TrendingDown className="w-4 h-4" />} tone="emerald" label="مزودون في المقارنات" value={String(s.providersCovered)} sub="ظاهرون كأرخص/أغلى" />
      </div>

      {/* controls */}
      <div className="flex flex-wrap items-center gap-2">
        <button
          onClick={() => setComparable((v) => !v)}
          className={`rounded-lg border px-3 py-1.5 text-[12px] transition-colors ${comparable
            ? "border-emerald-800/60 bg-emerald-950/40 text-emerald-300"
            : "border-slate-800 bg-slate-900/60 text-slate-400 hover:text-slate-200"}`}
        >
          {comparable ? "✓ متعدد الموردين فقط" : "كل المعايير"}
        </button>
        <div className="relative">
          <Search className="absolute right-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="ابحث: gemini، adobe، مزود…"
            className="w-56 rounded-lg border border-slate-800 bg-slate-900/60 py-1.5 pr-8 pl-3 text-[12px] text-slate-200 placeholder:text-slate-600 focus:border-slate-600 focus:outline-none"
          />
        </div>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="rounded-lg border border-slate-800 bg-slate-900/60 px-2.5 py-1.5 text-[12px] text-slate-300 focus:outline-none"
        >
          <option value="spread">ترتيب: الفاصل السعري</option>
          <option value="offers">ترتيب: عدد العروض</option>
          <option value="price">ترتيب: أرخص سعر</option>
          <option value="recent">ترتيب: الأحدث مطابقة</option>
        </select>
        <button onClick={refresh} className="rounded-lg border border-slate-800 bg-slate-900/60 p-1.5 text-slate-400 hover:text-slate-200" title="تحديث">
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
        </button>
        <span className="text-[11px] text-slate-500">{data.total} نتيجة</span>
      </div>

      {/* benchmarks table */}
      <div className="overflow-hidden rounded-xl border border-slate-800/70">
        <table className="w-full text-right text-[12px]">
          <thead className="bg-slate-900/80 text-slate-400">
            <tr>
              <th className="px-3 py-2.5 font-medium">المنتج الموحد</th>
              <th className="px-3 py-2.5 font-medium">المدة</th>
              <th className="px-3 py-2.5 font-medium">مزودون</th>
              <th className="px-3 py-2.5 font-medium">أرخص</th>
              <th className="px-3 py-2.5 font-medium">أغلى</th>
              <th className="px-3 py-2.5 font-medium">الفاصل</th>
              <th className="px-3 py-2.5 font-medium">أرخص مزود</th>
              <th className="px-3 py-2.5 font-medium"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
            {data.rows.map((b) => {
              const open = openKey === b.match_key;
              return (
                <Fragment key={b.match_key}>
                  <tr className="hover:bg-slate-900/40">
                    <td className="px-3 py-2.5">
                      <div className="font-medium text-slate-200">{label(b)}</div>
                      <div className="font-mono text-[10px] text-slate-600" dir="ltr">{b.brand}{b.quantity ? ` · ${b.quantity}` : ""}</div>
                    </td>
                    <td className="px-3 py-2.5">
                      {b.duration ? <Badge tone="blue">{b.duration}</Badge> : <span className="text-slate-600">—</span>}
                    </td>
                    <td className="px-3 py-2.5 text-slate-300">{b.providers}<span className="text-slate-600"> / {b.offers} عرضًا</span></td>
                    <td className="px-3 py-2.5 font-medium text-emerald-400">{fmtPrice(b.min_price)}</td>
                    <td className="px-3 py-2.5 text-slate-300">{fmtPrice(b.max_price)}</td>
                    <td className="px-3 py-2.5">
                      {b.spread_pct !== null ? (
                        <Badge tone={b.spread_pct >= 200 ? "rose" : b.spread_pct >= 50 ? "gold" : "gray"}>
                          +{b.spread_pct.toFixed(0)}%
                        </Badge>
                      ) : <span className="text-slate-600">—</span>}
                    </td>
                    <td className="px-3 py-2.5 text-slate-300">{PROVIDER_AR[b.cheapest_provider ?? ""] ?? b.cheapest_provider ?? "—"}</td>
                    <td className="px-3 py-2.5">
                      <button
                        onClick={() => setOpenKey(open ? null : b.match_key)}
                        className="rounded p-1 text-slate-500 hover:bg-slate-800 hover:text-slate-200"
                        title={open ? "إخفاء العروض" : "عرض كل العروض"}
                      >
                        {open ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronLeft className="h-3.5 w-3.5" />}
                      </button>
                    </td>
                  </tr>
                  {open && (
                    <tr className="bg-slate-900/30">
                      <td colSpan={8} className="px-4 py-3">
                        <OffersList matchKey={b.match_key} benchmark={b} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
        {data.rows.length === 0 && (
          <div className="py-10 text-center text-[12px] text-slate-500">لا نتائج مطابقة للبحث</div>
        )}
      </div>
    </div>
  );
}
