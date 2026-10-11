"use client";

/**
 * MEC — overview view (rebuild v4): live KPIs, automation state, approval queue
 * shortcut, freshness summary and recent prices — from /api/admin/overview.
 */
import { Activity, Database, Tags, Users, Radar, Bell, Clock, ShieldAlert, Gauge, Cog } from "lucide-react";
import { useApi, KpiCard, SectionCard, Badge, LoadingRows, ErrorState, EmptyState, timeAgo, fmtNum, fmtPrice, FRESHNESS_LABELS, FRESHNESS_TONES } from "./kit";
import { AreaChart } from "./charts";

type Overview = {
  kpis: {
    observations: number; channels: number; channelKinds: Record<string, number>;
    statements: number; statementsByKind: Record<string, number>;
    discoveries: number; discoveriesByStatus: Record<string, number>; discoveriesByKind: Record<string, number>;
    runs: number; products: number; suppliers: number;
    alertsUnread: number; awaitingApprovals: number; freshPrices24h: number; pricedLatest: number;
  };
  automation: {
    lastRun: { id: number; startedAt: string | null; finishedAt: string | null; runner: string | null; channelsScanned: number | null; pricesAdded: number | null; joinsOk: number | null; durationS: number | null; errors: string | null } | null;
    nextRunUTC: string; cadenceMinutes: number;
    circuitBreakers: { key: string; value: string; updatedAt: string }[];
  };
  volume14d: { day: string; count: number }[];
  recentPrices: { product: string; username: string | null; title: string | null; price: number | null; currency: string; postedAt: string | null; ageHours: number | null }[];
};

export function OverviewView({ onNavigate }: { onNavigate?: (key: string) => void }) {
  const { data, error, loading, refresh } = useApi<Overview>("/api/admin/overview", [], 120_000);
  if (loading && !data) return <LoadingRows rows={8} />;
  if (error) return <ErrorState text={error} />;
  if (!data) return <EmptyState text="لا توجد بيانات" />;

  const k = data.kpis;
  const freshPct = k.pricedLatest ? Math.round((k.freshPrices24h / k.pricedLatest) * 100) : 0;

  return (
    <div className="space-y-5">
      {/* urgent row */}
      {(k.awaitingApprovals > 0 || k.alertsUnread > 0 || data.automation.circuitBreakers.length > 0) && (
        <div className="grid gap-3 sm:grid-cols-3">
          {k.awaitingApprovals > 0 && (
            <button onClick={() => onNavigate?.("discoveries")} className="rounded-xl border border-violet-900/70 bg-violet-950/30 p-4 text-start hover:bg-violet-950/50 transition-colors">
              <div className="flex items-center gap-2 text-violet-300 text-[12px] font-bold"><Radar className="w-4 h-4" /> {k.awaitingApprovals} انضمام خاص بانتظار موافقتك</div>
              <div className="text-[11px] text-zinc-500 mt-1">اضغط للمراجعة والاعتماد — يُنفَّذ تلقائيًا فور الاعتماد</div>
            </button>
          )}
          {k.alertsUnread > 0 && (
            <button onClick={() => onNavigate?.("alerts")} className="rounded-xl border border-rose-900/70 bg-rose-950/30 p-4 text-start hover:bg-rose-950/50 transition-colors">
              <div className="flex items-center gap-2 text-rose-300 text-[12px] font-bold"><Bell className="w-4 h-4" /> {k.alertsUnread} تنبيهًا غير مقروء</div>
              <div className="text-[11px] text-zinc-500 mt-1">راجع مركز التنبيهات</div>
            </button>
          )}
          {data.automation.circuitBreakers.length > 0 && (
            <button onClick={() => onNavigate?.("settings")} className="rounded-xl border border-amber-900/70 bg-amber-950/30 p-4 text-start hover:bg-amber-950/50 transition-colors">
              <div className="flex items-center gap-2 text-amber-300 text-[12px] font-bold"><ShieldAlert className="w-4 h-4" /> {data.automation.circuitBreakers.length} قاطع أمان نشط</div>
              <div className="text-[11px] text-zinc-500 mt-1">حماية الحساب من أنظمة مكافحة السبام — يمكن تعليقها من الإعدادات</div>
            </button>
          )}
        </div>
      )}

      {/* KPI grid */}
      <div className="grid gap-3 grid-cols-2 lg:grid-cols-4">
        <KpiCard label="رصد سعر متراكم" value={k.observations} sub={`${fmtNum(k.products)} منتجًا عبر ${fmtNum(k.suppliers)} مورّدًا`} tone="emerald" icon={<Tags className="w-4 h-4" />} />
        <KpiCard label="مصادر تحت المراقبة" value={k.channels} sub={`${k.channelKinds.channel ?? 0} قناة · ${k.channelKinds.group ?? 0} مجموعة · ${k.channelKinds.bot ?? 0} بوت`} tone="sky" icon={<Users className="w-4 h-4" />} />
        <KpiCard label="انتعاش الأسعار ≤24 ساعة" value={`${freshPct}%`} sub={`${fmtNum(k.freshPrices24h)} من ${fmtNum(k.pricedLatest)} سعرًا حديثًا`} tone={freshPct >= 60 ? "emerald" : freshPct >= 30 ? "amber" : "rose"} icon={<Gauge className="w-4 h-4" />} />
        <KpiCard label="دورات الأتمتة" value={k.runs} sub={`كل ${data.automation.cadenceMinutes} دقيقة + تشغيل فوري`} tone="violet" icon={<Cog className="w-4 h-4" />} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {/* automation state */}
        <SectionCard title="حالة الأتمتة" extra={<button onClick={refresh} className="text-[11px] text-emerald-400 hover:text-emerald-300">تحديث</button>}>
          {data.automation.lastRun ? (
            <div className="space-y-2.5 text-[12px]">
              <div className="flex justify-between"><span className="text-zinc-500">آخر دورة</span><span>#{data.automation.lastRun.id} · {data.automation.lastRun.runner}</span></div>
              <div className="flex justify-between"><span className="text-zinc-500">انتهت</span><span>{timeAgo(data.automation.lastRun.finishedAt)}</span></div>
              <div className="flex justify-between"><span className="text-zinc-500">قنوات ممسوحة / أسعار مضافة</span><span>{fmtNum(data.automation.lastRun.channelsScanned)} / +{fmtNum(data.automation.lastRun.pricesAdded)}</span></div>
              <div className="flex justify-between"><span className="text-zinc-500">انضمامات</span><span>{fmtNum(data.automation.lastRun.joinsOk)}</span></div>
              <div className="flex justify-between"><span className="text-zinc-500">المدة</span><span>{data.automation.lastRun.durationS ?? "—"} ثانية</span></div>
              <div className="flex justify-between"><span className="text-zinc-500">الدورة المجدولة القادمة</span><span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {timeAgo(data.automation.nextRunUTC).replace("قبل", "بعد")}</span></div>
              {data.automation.lastRun.errors && data.automation.lastRun.errors !== "[]" && (
                <div className="rounded-lg border border-amber-900/50 bg-amber-950/20 p-2 text-[11px] text-amber-300 leading-5">
                  أخطاء آخر دورة: {data.automation.lastRun.errors.slice(0, 220)}
                </div>
              )}
            </div>
          ) : (
            <EmptyState text="لا دورات بعد" />
          )}
        </SectionCard>

        {/* volume */}
        <SectionCard title="حجم الرصد اليومي (14 يومًا)">
          {data.volume14d.length > 0 ? (
            <AreaChart data={data.volume14d.map((d) => ({ label: d.day.slice(5), value: d.count }))} height={150} />
          ) : (
            <EmptyState text="لا بيانات" />
          )}
        </SectionCard>
      </div>

      {/* recent prices */}
      <SectionCard title="أحدث الأسعار الملتقطة">
        {data.recentPrices.length === 0 ? (
          <EmptyState text="لا أسعار بعد" />
        ) : (
          <div className="space-y-1.5">
            {data.recentPrices.map((p, i) => (
              <div key={i} className="flex items-center gap-2 rounded-lg border border-zinc-800/60 bg-zinc-900/40 px-3 py-2 text-[11.5px]">
                <Activity className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="font-medium text-zinc-200 truncate flex-1">{p.product}</span>
                <span className="text-zinc-500 truncate max-w-28">{p.title || (p.username ? `@${p.username}` : "خاصة")}</span>
                <span className="text-emerald-400 font-bold tabular-nums whitespace-nowrap">{fmtPrice(p.price, p.currency)}</span>
                <Badge tone={FRESHNESS_TONES[p.ageHours != null && p.ageHours <= 24 ? "fresh" : p.ageHours != null && p.ageHours <= 72 ? "aging" : "stale"] ?? "gray"}>
                  {timeAgo(p.postedAt)}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </SectionCard>

      {/* discoveries summary */}
      <SectionCard title="خط أنابيب الاكتشاف" extra={<button onClick={() => onNavigate?.("discoveries")} className="text-[11px] text-emerald-400 hover:text-emerald-300">إدارة الاكتشافات</button>}>
        <div className="flex flex-wrap gap-2">
          {Object.entries(k.discoveriesByStatus).map(([s, n]) => (
            <Badge key={s} tone="gray">{s}: {fmtNum(n)}</Badge>
          ))}
        </div>
        <div className="mt-3 text-[11px] text-zinc-500 leading-5">
          إشارات تجارية متراكمة: {fmtNum(k.statements)} (ضمان {fmtNum(k.statementsByKind.warranty ?? 0)} · دفع {fmtNum(k.statementsByKind.payment ?? 0)} · حد أدنى {fmtNum(k.statementsByKind.min_order ?? 0)})
        </div>
      </SectionCard>

      <div className="text-[10.5px] text-zinc-600 flex items-center gap-1.5">
        <Database className="w-3 h-3" /> المصدر: Supabase الحية (عرض latest_prices) — تحديث تلقائي كل دقيقتين
      </div>
    </div>
  );
}
