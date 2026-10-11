"use client";

/**
 * MEC — data quality view (rebuild v4): price freshness distribution, scan
 * coverage, stale prices, channel health, 14-day volume + product trend.
 */
import { useState } from "react";
import { Gauge, RefreshCw } from "lucide-react";
import { useApi, KpiCard, SectionCard, Badge, LoadingRows, ErrorState, EmptyState, timeAgo, fmtNum, fmtPrice, FRESHNESS_LABELS, FRESHNESS_TONES, KIND_LABELS } from "./kit";
import { AreaChart, BarChart } from "./charts";

type Quality = {
  priceFreshness: Record<string, number>;
  scanCoverage: { scannedLast1h: number; scannedLast24h: number; scannedLast72h: number; neverScanned: number; joinedTotal: number };
  staleProducts: { product: string; username: string | null; title: string | null; price: number | null; currency: string; postedAt: string | null; ageHours: number | null }[];
  channelHealth: { tgId: number; username: string | null; title: string | null; kind: string; lastScanned: string | null; observations: number; products: number; scanAgeHours: number | null }[];
  volume14d: { day: string; count: number }[];
  generatedAt: string;
};

type Trend = { day: string; avg: number; min: number; max: number; n: number }[];

export function QualityView() {
  const { data, error, loading, refresh } = useApi<Quality>("/api/admin/quality", [], 120_000);
  const [product, setProduct] = useState("");
  const { data: trend } = useApi<Trend>(
    product ? `/api/admin/products?trend=${encodeURIComponent(product)}` : "/api/admin/quality",
    [product],
  );

  if (loading && !data) return <LoadingRows rows={8} />;
  if (error) return <ErrorState text={error} />;
  if (!data) return <EmptyState text="لا بيانات" />;

  const f = data.priceFreshness;
  const total = Object.values(f).reduce((a, b) => a + b, 0) || 1;
  const cov = data.scanCoverage;

  return (
    <div className="space-y-5">
      <div className="grid gap-3 grid-cols-2 lg:grid-cols-4">
        <KpiCard label="أسعار حديثة ≤24 ساعة" value={`${Math.round((f.fresh / total) * 100)}%`} sub={`${fmtNum(f.fresh)} سعرًا`} tone="emerald" icon={<Gauge className="w-4 h-4" />} />
        <KpiCard label="تغطية المسح ≤ ساعة" value={`${cov.scannedLast1h}/${cov.joinedTotal}`} sub={`${cov.scannedLast24h} خلال 24 ساعة`} tone="sky" />
        <KpiCard label="أسعار قديمة >72 ساعة" value={fmtNum((f.stale ?? 0) + (f.ancient ?? 0))} sub="تُعرض للعامة موسومة بالقدم" tone="rose" />
        <KpiCard label="لم تُمسح قط" value={fmtNum(cov.neverScanned)} sub="قنوات جديدة بانتظار أول دورة" tone={cov.neverScanned > 0 ? "amber" : "emerald"} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <SectionCard title="توزيع انتعاش الأسعار" extra={<button onClick={refresh} className="text-[11px] text-emerald-400 hover:text-emerald-300 flex items-center gap-1"><RefreshCw className="w-3 h-3" /> تحديث</button>}>
          <div className="space-y-2.5">
            {(["fresh", "aging", "stale", "ancient"] as const).map((b) => {
              const n = f[b] ?? 0;
              const pct = Math.round((n / total) * 100);
              const colors: Record<string, string> = { fresh: "bg-emerald-500", aging: "bg-amber-500", stale: "bg-rose-500", ancient: "bg-rose-700" };
              return (
                <div key={b} className="flex items-center gap-3">
                  <Badge tone={FRESHNESS_TONES[b]}>{FRESHNESS_LABELS[b]}</Badge>
                  <div className="flex-1 h-2 rounded-full bg-zinc-800/60 overflow-hidden">
                    <div className={`h-full rounded-full ${colors[b]}`} style={{ width: `${pct}%` }} />
                  </div>
                  <span className="text-[11.5px] tabular-nums text-zinc-400 w-20 text-end">{fmtNum(n)} ({pct}%)</span>
                </div>
              );
            })}
            <div className="text-[10.5px] text-zinc-600 pt-1">العتبات: حديث ≤24 ساعة · يتقادم ≤72 · قديم ≤7 أيام · متقادم جدًا أكثر</div>
          </div>
        </SectionCard>

        <SectionCard title="حجم الرصد (14 يومًا)">
          <AreaChart data={data.volume14d.map((d) => ({ label: d.day.slice(5), value: d.count }))} height={170} />
        </SectionCard>
      </div>

      {/* trend explorer */}
      <SectionCard title="اتجاه سعر منتج">
        <div className="flex gap-2 mb-3">
          <input
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            placeholder="اكتب اسم منتج للبحث عن اتجاهه (مثال: ChatGPT Plus)"
            className="flex-1 rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-2 text-[12px] text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-emerald-800"
          />
        </div>
        {product && trend && trend.length > 0 ? (
          <>
            <AreaChart data={trend.map((t) => ({ label: t.day.slice(5), value: t.avg }))} height={160} />
            <div className="mt-2 text-[11px] text-zinc-500">
              متوسط السعر اليومي — آخر {trend.length} يومًا من رصدها · أدنى {fmtPrice(Math.min(...trend.map((t) => t.min)))} · أعلى {fmtPrice(Math.max(...trend.map((t) => t.max)))}
            </div>
          </>
        ) : product ? (
          <EmptyState text="لا رصد كافٍ لهذا الاسم — جرّب صياغة أخرى" />
        ) : (
          <div className="text-[11.5px] text-zinc-500">اكتب اسم منتج لعرض منحنى متوسط سعره اليومي.</div>
        )}
      </SectionCard>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* stale prices */}
        <SectionCard title="أقدم الأسعار المعروضة (تحتاج تحققًا)">
          {data.staleProducts.length === 0 ? (
            <EmptyState text="لا أسعار متقادمة — ممتاز" />
          ) : (
            <div className="space-y-1.5 max-h-72 overflow-y-auto">
              {data.staleProducts.slice(0, 15).map((p, i) => (
                <div key={i} className="flex items-center gap-2 rounded-lg border border-zinc-800/60 bg-zinc-900/40 px-3 py-2 text-[11px]">
                  <span className="font-medium text-zinc-300 truncate flex-1">{p.product}</span>
                  <span className="text-zinc-500 truncate max-w-24">{p.title || p.username || "خاصة"}</span>
                  <span className="text-zinc-400 tabular-nums">{fmtPrice(p.price, p.currency)}</span>
                  <Badge tone="red">{timeAgo(p.postedAt)}</Badge>
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        {/* channel health */}
        <SectionCard title="صحة المصادر (الأطول دون مسح)">
          {data.channelHealth.length === 0 ? (
            <EmptyState text="لا مصادر" />
          ) : (
            <div className="space-y-1.5 max-h-72 overflow-y-auto">
              {data.channelHealth.slice(0, 15).map((c) => (
                <div key={c.tgId} className="flex items-center gap-2 rounded-lg border border-zinc-800/60 bg-zinc-900/40 px-3 py-2 text-[11px]">
                  <span className="font-medium text-zinc-300 truncate flex-1">{c.title || (c.username ? `@${c.username}` : `#${c.tgId}`)}</span>
                  <Badge tone="gray">{KIND_LABELS[c.kind] ?? c.kind}</Badge>
                  <span className="text-zinc-500 tabular-nums">{fmtNum(c.observations)} رصد</span>
                  <Badge tone={c.scanAgeHours == null ? "red" : c.scanAgeHours <= 1 ? "green" : c.scanAgeHours <= 24 ? "gold" : "red"}>
                    {c.lastScanned ? timeAgo(c.lastScanned) : "أبدًا"}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </SectionCard>
      </div>

      <div className="text-[10.5px] text-zinc-600">حُسبت المؤشرات: {timeAgo(data.generatedAt)} — مباشرة من قاعدة Supabase الحية</div>
    </div>
  );
}
