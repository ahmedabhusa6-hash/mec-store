"use client";

/** MEC — alerts center (rebuild v4): severity-tagged alerts, mark read. */
import { Bell, CheckCheck, AlertTriangle, XCircle, Info } from "lucide-react";
import { useApi, Badge, SectionCard, LoadingRows, ErrorState, EmptyState, timeAgo } from "./kit";

type AlertRow = {
  id: number; severity: string; category: string; title: string;
  message: string | null; createdAt: string; readAt: string | null;
};

type AlertsData = { unread: number; alerts: AlertRow[] };

const SEV = {
  critical: { label: "حرج", tone: "red" as const, icon: XCircle },
  warning: { label: "تحذير", tone: "gold" as const, icon: AlertTriangle },
  info: { label: "معلومة", tone: "blue" as const, icon: Info },
};

const CATEGORY_LABELS: Record<string, string> = {
  monitor: "المراقب",
  breaker: "قاطع أمان",
  security: "أمن",
  quality: "جودة بيانات",
  system: "النظام",
};

export function AlertsView({ onRead }: { onRead?: () => void }) {
  const { data, error, loading, refresh } = useApi<AlertsData>("/api/admin/alerts", [], 60_000);

  async function markRead(id?: number) {
    await fetch("/api/admin/alerts", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(id != null ? { id } : { all: true }),
    });
    refresh();
    onRead?.();
  }

  if (loading && !data) return <LoadingRows rows={6} />;
  if (error) return <ErrorState text={error} />;
  if (!data) return <EmptyState text="لا بيانات" />;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-[12.5px] text-zinc-400">
          {data.unread > 0 ? <b className="text-rose-300">{data.unread} تنبيهًا غير مقروء</b> : "كل التنبيهات مقروءة"}
        </div>
        {data.unread > 0 && (
          <button onClick={() => markRead()} className="flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-900/60 px-3 py-1.5 text-[11.5px] text-zinc-300 hover:bg-zinc-800/60">
            <CheckCheck className="w-3.5 h-3.5" /> تحديد الكل كمقروء
          </button>
        )}
      </div>

      {data.alerts.length === 0 ? (
        <SectionCard>
          <div className="py-10 text-center">
            <Bell className="w-8 h-8 text-zinc-700 mx-auto mb-3" />
            <div className="text-[13px] text-zinc-500">لا تنبيهات — النظام يعمل بلا أحداث تستدعي الانتباه</div>
            <div className="text-[11px] text-zinc-600 mt-1.5">تُنشأ التنبيهات تلقائيًا عند: فشل دورة، تفعيل قاطع أمان، محاولات دخول فاشلة، أو توقف مسح مصدر</div>
          </div>
        </SectionCard>
      ) : (
        <div className="space-y-2">
          {data.alerts.map((a) => {
            const sev = SEV[a.severity as keyof typeof SEV] ?? SEV.info;
            const Icon = sev.icon;
            return (
              <div
                key={a.id}
                className={`rounded-xl border p-3.5 flex items-start gap-3 ${
                  a.readAt ? "border-zinc-800/60 bg-zinc-900/30 opacity-70" : "border-zinc-700 bg-[#0d1421]"
                }`}
              >
                <span className={`shrink-0 w-8 h-8 rounded-lg border flex items-center justify-center ${
                  a.severity === "critical" ? "border-rose-900/60 bg-rose-950/40 text-rose-400"
                  : a.severity === "warning" ? "border-amber-900/60 bg-amber-950/40 text-amber-400"
                  : "border-sky-900/60 bg-sky-950/40 text-sky-400"}`}>
                  <Icon className="w-4 h-4" />
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[12.5px] font-bold text-zinc-100">{a.title}</span>
                    <Badge tone={sev.tone}>{sev.label}</Badge>
                    <Badge tone="gray">{CATEGORY_LABELS[a.category] ?? a.category}</Badge>
                  </div>
                  {a.message && <div className="text-[11.5px] text-zinc-400 mt-1 leading-5">{a.message}</div>}
                  <div className="text-[10.5px] text-zinc-600 mt-1">{timeAgo(a.createdAt)}{a.readAt ? " · مقروء" : ""}</div>
                </div>
                {!a.readAt && (
                  <button onClick={() => markRead(a.id)} className="shrink-0 rounded-md border border-zinc-700 px-2 py-1 text-[10.5px] text-zinc-400 hover:text-emerald-300 hover:border-emerald-800">
                    مقروء
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
