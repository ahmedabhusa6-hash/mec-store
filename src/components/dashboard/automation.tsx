"use client";

/**
 * MEC — automation view (rebuild v4): run history (with telemetry columns),
 * GitHub workflow runs, dispatch button, discipline status.
 */
import { useState } from "react";
import { Play, Loader2, Clock } from "lucide-react";
import { useApi, Badge, SectionCard, LoadingRows, ErrorState, EmptyState, timeAgo, fmtNum, fmtDuration } from "./kit";

type RunRow = {
  id: number; startedAt: string | null; finishedAt: string | null; runner: string | null; dispatchedBy: string | null;
  channelsScanned: number | null; newMessages: number | null; pricesAdded: number | null;
  newHandles: number | null; invitesFound: number | null; joinsOk: number | null; joinsPrivate: number | null;
  errors: string | null; durationS: number | null;
};

type WorkflowRun = { id: number; run_number: number; status: string | null; conclusion: string | null; created_at: string; event: string };

type RunsData = { runs: RunRow[]; workflow: WorkflowRun[] };

export function AutomationView() {
  const { data, error, loading, refresh } = useApi<RunsData>("/api/admin/runs", [], 60_000);
  const [dispatching, setDispatching] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function runNow() {
    setDispatching(true);
    setMsg(null);
    try {
      const r = await fetch("/api/admin/dispatch", { method: "POST" });
      const j = (await r.json()) as { message?: string; error?: string };
      setMsg(r.ok ? (j.message ?? "تم الإطلاق") : (j.error ?? "فشل"));
      setTimeout(refresh, 8000);
    } catch {
      setMsg("فشل الاتصال");
    } finally {
      setDispatching(false);
      setTimeout(() => setMsg(null), 8000);
    }
  }

  if (loading && !data) return <LoadingRows rows={8} />;
  if (error) return <ErrorState text={error} />;
  if (!data) return <EmptyState text="لا بيانات" />;

  const successRate = data.runs.length
    ? Math.round((data.runs.filter((r) => r.finishedAt).length / data.runs.length) * 100)
    : 0;

  return (
    <div className="space-y-5">
      {msg && <div className="rounded-lg border border-emerald-900/60 bg-emerald-950/30 px-4 py-2.5 text-[12px] text-emerald-300">{msg}</div>}

      <div className="grid gap-3 sm:grid-cols-3">
        <SectionCard title="الجدولة">
          <div className="text-[12px] space-y-1.5">
            <div className="flex justify-between"><span className="text-zinc-500">الدورية</span><span>كل 30 دقيقة (UTC)</span></div>
            <div className="flex justify-between"><span className="text-zinc-500">المشغّل</span><span>GitHub Actions</span></div>
            <div className="flex justify-between"><span className="text-zinc-500">قفل التزامن</span><span>نافذة 25 دقيقة</span></div>
          </div>
        </SectionCard>
        <SectionCard title="معدل الإتمام (آخر 40 دورة)">
          <div className={`text-3xl font-extrabold ${successRate >= 95 ? "text-emerald-400" : "text-amber-400"}`}>{successRate}%</div>
          <div className="text-[11px] text-zinc-500 mt-1">{data.runs.length} دورة مسجلة في قاعدة البيانات</div>
        </SectionCard>
        <SectionCard title="تشغيل فوري">
          <button
            onClick={runNow}
            disabled={dispatching}
            className="w-full flex items-center justify-center gap-2 rounded-lg border border-emerald-800/70 bg-emerald-950/50 px-4 py-3 text-[13px] font-bold text-emerald-300 hover:bg-emerald-900/50 disabled:opacity-50"
          >
            {dispatching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            أطلق دورة مراقبة الآن
          </button>
          <div className="text-[10.5px] text-zinc-500 mt-2 leading-5">يُطلق سير عمل GitHub Actions فورًا (يحترم قفل التزامن — الدورة الجارية تُحمي الجلسة)</div>
        </SectionCard>
      </div>

      {/* workflow runs (github) */}
      {data.workflow.length > 0 && (
        <SectionCard title="أحدث تشغيلات GitHub Actions">
          <div className="space-y-1.5">
            {data.workflow.map((w) => (
              <div key={w.id} className="flex items-center gap-2 rounded-lg border border-zinc-800/60 bg-zinc-900/40 px-3 py-2 text-[11.5px]">
                <span className="text-zinc-500 font-mono">#{w.run_number}</span>
                <Badge tone={w.conclusion === "success" ? "green" : w.status === "completed" ? "red" : "gold"}>
                  {w.status === "completed" ? (w.conclusion === "success" ? "نجحت" : "فشلت") : "جارية"}
                </Badge>
                <span className="text-zinc-500">{w.event === "schedule" ? "مجدولة" : w.event === "workflow_dispatch" ? "تشغيل يدوي (لوحة التحكم)" : w.event}</span>
                <span className="flex-1" />
                <span className="text-zinc-500 flex items-center gap-1"><Clock className="w-3 h-3" /> {timeAgo(w.created_at)}</span>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* run history */}
      <SectionCard title="سجل الدورات (قاعدة البيانات)">
        {data.runs.length === 0 ? (
          <EmptyState text="لا دورات بعد" />
        ) : (
          <div className="overflow-x-auto max-h-[520px] overflow-y-auto">
            <table className="w-full text-[11.5px]">
              <thead className="sticky top-0 bg-[#0d1421]">
                <tr className="text-zinc-500">
                  <th className="text-start py-2 px-2 font-medium">#</th>
                  <th className="text-start py-2 px-2 font-medium">البداية</th>
                  <th className="text-start py-2 px-2 font-medium">المدة</th>
                  <th className="text-start py-2 px-2 font-medium">المشغّل</th>
                  <th className="text-start py-2 px-2 font-medium">قنوات</th>
                  <th className="text-start py-2 px-2 font-medium">رسائل</th>
                  <th className="text-start py-2 px-2 font-medium">أسعار</th>
                  <th className="text-start py-2 px-2 font-medium">مقابض</th>
                  <th className="text-start py-2 px-2 font-medium">دعوات</th>
                  <th className="text-start py-2 px-2 font-medium">انضمام</th>
                  <th className="text-start py-2 px-2 font-medium">أخطاء</th>
                </tr>
              </thead>
              <tbody>
                {data.runs.map((r) => (
                  <tr key={r.id} className="border-t border-zinc-800/60 hover:bg-zinc-900/40">
                    <td className="py-2 px-2 font-mono text-zinc-400">{r.id}</td>
                    <td className="py-2 px-2 text-zinc-400 whitespace-nowrap">{timeAgo(r.startedAt)}</td>
                    <td className="py-2 px-2 text-zinc-400 tabular-nums">{fmtDuration(r.durationS)}</td>
                    <td className="py-2 px-2">
                      <Badge tone={r.runner === "github-actions" ? "blue" : "gray"}>{r.runner ?? "—"}</Badge>
                      {r.dispatchedBy && <span className="ms-1 text-[10px] text-violet-300">(بأمر المالك)</span>}
                    </td>
                    <td className="py-2 px-2 tabular-nums text-zinc-300">{fmtNum(r.channelsScanned)}</td>
                    <td className="py-2 px-2 tabular-nums text-zinc-300">+{fmtNum(r.newMessages)}</td>
                    <td className="py-2 px-2 tabular-nums text-emerald-400 font-bold">+{fmtNum(r.pricesAdded)}</td>
                    <td className="py-2 px-2 tabular-nums text-zinc-400">+{fmtNum(r.newHandles)}</td>
                    <td className="py-2 px-2 tabular-nums text-violet-300">+{fmtNum(r.invitesFound)}</td>
                    <td className="py-2 px-2 tabular-nums text-zinc-300">
                      {fmtNum(r.joinsOk)}{r.joinsPrivate ? ` (${r.joinsPrivate} خاص)` : ""}
                    </td>
                    <td className="py-2 px-2 max-w-52">
                      {r.errors && r.errors !== "[]" ? (
                        <span className="text-amber-400 text-[10.5px] line-clamp-2">{r.errors.slice(0, 140)}</span>
                      ) : <span className="text-emerald-500">سليمة</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>
    </div>
  );
}
