"use client";

/**
 * MEC — integrations & provider-sync view (rebuild v4.1, 2026-10-12).
 * Unified supplier registry: API providers (lifecycle states, credentials env
 * NAMES only — values never reach the browser) + the Telegram ecosystem row.
 * Live sync telemetry from sync_runs. Owner-only by design.
 */
import { useState } from "react";
import { Plug, RefreshCw, ExternalLink, Loader2, KeyRound, Clock, CheckCircle2, XCircle, MinusCircle, Settings2 } from "lucide-react";
import { useApi, Badge, SectionCard, LoadingRows, ErrorState, EmptyState, timeAgo } from "./kit";

type Provider = {
  code: string; name: string; kind: string; status: string; domain: string | null;
  docs_url: string | null; sync_interval_min: number;
  last_sync_at: string | null; last_ok_at: string | null; last_error: string | null;
  products: number; last_success_sync: string | null; credentials_env: string[];
};

type SyncRun = {
  id: number; provider_code: string; started_at: string; finished_at: string | null;
  trigger: string; status: string; items_seen: number | null; items_changed: number | null;
  products_new: number | null; prices_updated: number | null; errors: string | null;
  duration_ms: number | null;
};

const STATUS_TONE: Record<string, "green" | "gold" | "rose" | "blue" | "gray"> = {
  SYNC_ACTIVE: "green", READ_ONLY_TEST_PASSED: "green",
  DOCUMENTATION_FOUND: "blue", READY_FOR_TEST: "blue", DISCOVERED: "gray",
  CREDENTIALS_REQUIRED: "gold", AUTH_FAILED: "rose", RATE_LIMITED: "rose",
  UNSUPPORTED: "gray", BLOCKED: "rose", MAINTENANCE: "gold", RETIRED: "gray",
};

const STATUS_AR: Record<string, string> = {
  DISCOVERED: "مكتشف", DOCUMENTATION_FOUND: "الوثائق موثقة", CREDENTIALS_REQUIRED: "يحتاج اعتمادات",
  READY_FOR_TEST: "جاهز للاختبار", READ_ONLY_TEST_PASSED: "اختبار قراءة ناجح", SYNC_ACTIVE: "مزامنة نشطة",
  AUTH_FAILED: "فشل المصادقة", RATE_LIMITED: "محصور معدلًا", UNSUPPORTED: "غير مدعوم",
  BLOCKED: "محجوب", MAINTENANCE: "صيانة", RETIRED: "متقاعد",
};

export function IntegrationsView() {
  const { data, error, loading, refresh } = useApi<{ providers: Provider[] }>("/api/admin/providers", [], 30_000);
  const syncQ = useApi<{ runs: SyncRun[] }>("/api/admin/sync-runs?limit=15", [], 30_000);
  const [busy, setBusy] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  if (loading && !data) return <LoadingRows rows={6} />;
  if (error) return <ErrorState text={error} />;
  if (!data) return <EmptyState text="لا بيانات" />;

  const providers = data.providers ?? [];
  const apiProviders = providers.filter((p) => p.kind === "api");
  const tgRow = providers.find((p) => p.kind === "telegram");

  async function patch(code: string, payload: Record<string, unknown>) {
    setBusy(code);
    setMsg(null);
    try {
      const r = await fetch("/api/admin/providers", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, ...payload }),
      });
      const j = (await r.json()) as { ok?: boolean; error?: string };
      if (!r.ok) throw new Error(j.error ?? "فشل");
      setMsg(`✓ حُدِّث ${code}`);
      refresh();
    } catch (e) {
      setMsg(`خطأ: ${String(e instanceof Error ? e.message : e)}`);
    } finally {
      setBusy(null);
      setTimeout(() => setMsg(null), 6000);
    }
  }

  return (
    <div className="space-y-5">
      {msg && <div className="rounded-lg border border-emerald-900/60 bg-emerald-950/30 px-4 py-2.5 text-[12px] text-emerald-300">{msg}</div>}

      {/* policy banner */}
      <div className="rounded-lg border border-zinc-800 bg-zinc-900/40 px-4 py-3 text-[11.5px] leading-6 text-zinc-400">
        <b className="text-zinc-200">نموذج المزامنة المزدوج:</b> مزودو <b className="text-sky-300">API</b> يُقرؤون مباشرة عبر واجهاتهم الرسمية (قراءة فقط — أي طلب شراء يتطلب موافقة المالك)،
        ومنظومة <b className="text-emerald-300">تلغرام</b> تُزامن عبر المراقب (نتيجة موثقة: لا توجد واجهات API رسمية في نطاق اشتراكات AI — كل الموردين الحاليين قنوات تلغرام).
        الحالة لا تُرفع إلى «مزامنة نشطة» إلا بنجاح فعلي مُسجَّل.
      </div>

      {/* API providers */}
      <SectionCard title="مزودو الواجهات (API)" extra={<span className="text-[10.5px] text-zinc-500">{apiProviders.length} مسجلًا</span>}>
        <div className="space-y-2">
          {apiProviders.map((p) => (
            <div key={p.code} className="rounded-lg border border-zinc-800/60 bg-zinc-900/40 p-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-[12px] font-bold text-zinc-100" dir="ltr">{p.code}</span>
                <span className="text-[12px] text-zinc-300">{p.name}</span>
                <Badge tone={STATUS_TONE[p.status] ?? "gray"}>{STATUS_AR[p.status] ?? p.status}</Badge>
                <span className="text-[10.5px] text-zinc-600">{p.domain}</span>
                <div className="flex-1" />
                {p.docs_url && (
                  <a href={p.docs_url} target="_blank" rel="noreferrer"
                     className="flex items-center gap-1 text-[10.5px] text-sky-300 hover:text-sky-200">
                    الوثائق <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
              <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-zinc-500">
                <span className="flex items-center gap-1"><KeyRound className="w-3 h-3" /> اعتمادات: {p.credentials_env.length ? p.credentials_env.join(" ، ") : "—"}</span>
                <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> كل {p.sync_interval_min} د</span>
                <span>منتجات مسجلة: {p.products}</span>
                <span>آخر مزامنة: {p.last_sync_at ? timeAgo(p.last_sync_at) : "—"}</span>
                <span>آخر نجاح: {p.last_ok_at ? timeAgo(p.last_ok_at) : "—"}</span>
              </div>
              {p.last_error && (
                <div className="mt-2 rounded-md border border-rose-900/50 bg-rose-950/20 px-2.5 py-1.5 text-[10.5px] text-rose-300" dir="ltr">
                  {p.last_error.slice(0, 220)}
                </div>
              )}
              <div className="mt-2 flex flex-wrap gap-2">
                {p.status === "CREDENTIALS_REQUIRED" && (
                  <button onClick={() => patch(p.code, { status: "READY_FOR_TEST" })}
                          disabled={busy === p.code}
                          className="flex items-center gap-1 rounded-md border border-sky-800/70 bg-sky-950/40 px-2.5 py-1.5 text-[11px] font-bold text-sky-300 hover:bg-sky-900/40 disabled:opacity-40">
                    {busy === p.code ? <Loader2 className="w-3 h-3 animate-spin" /> : <Settings2 className="w-3 h-3" />} علّمت الاعتمادات كمتوفرة (جاهز للاختبار)
                  </button>
                )}
                {(p.status === "SYNC_ACTIVE" || p.status === "AUTH_FAILED" || p.status === "RATE_LIMITED") && (
                  <button onClick={() => patch(p.code, { status: "MAINTENANCE" })}
                          disabled={busy === p.code}
                          className="rounded-md border border-amber-800/70 bg-amber-950/40 px-2.5 py-1.5 text-[11px] font-bold text-amber-300 hover:bg-amber-900/40 disabled:opacity-40">
                    أوقف للصيانة
                  </button>
                )}
                {(p.status === "MAINTENANCE" || p.status === "RETIRED" || p.status === "BLOCKED") && (
                  <button onClick={() => patch(p.code, { status: "DOCUMENTATION_FOUND" })}
                          disabled={busy === p.code}
                          className="rounded-md border border-emerald-800/70 bg-emerald-950/40 px-2.5 py-1.5 text-[11px] font-bold text-emerald-300 hover:bg-emerald-900/40 disabled:opacity-40">
                    أعد التفعيل
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-3 text-[10.5px] leading-5 text-zinc-600">
          قيم الاعتمادات تُقرأ من متغيرات البيئة في بيئة التنفيذ فقط (أسماء المتغيرات أعلاه) — لا تصل القيم أبدًا إلى المتصفح أو السجلات.
          لتفعيل Reloadly: أنشئ حسابًا لديهم، ثم ضع RELOADLY_CLIENT_ID و RELOADLY_CLIENT_SECRET في أسرار GitHub Actions، ثم اضغط «جاهز للاختبار».
        </div>
      </SectionCard>

      {/* Telegram ecosystem row */}
      {tgRow && (
        <SectionCard title="منظومة تلغرام (المزامنة القائمة فعليًا)">
          <div className="flex flex-wrap items-center gap-2 text-[12px]">
            <Badge tone="green">مزامنة نشطة — المراقب هو المحرك</Badge>
            <span className="text-zinc-300">{tgRow.name}</span>
            <span className="text-[11px] text-zinc-500">فاصل الدورة: {tgRow.sync_interval_min} دقيقة</span>
            <span className="text-[11px] text-zinc-500">آخر نجاح: {tgRow.last_ok_at ? timeAgo(tgRow.last_ok_at) : "—"}</span>
          </div>
          <div className="mt-2 text-[11px] leading-6 text-zinc-500">
            نتيجة موثقة 2026-10-12: لا يوجد مورد واحد في نطاق اشتراكات AI يقدم واجهة API رسمية؛
            المزامنة في هذا النطاق تتم حصرًا عبر مراقب تلغرام (قراءة منضبطة + قواطع أمان + موافقات الانضمام الخاص).
          </div>
        </SectionCard>
      )}

      {/* sync telemetry */}
      <SectionCard title="سجل المزامنة (آخر 15)" extra={
        <button onClick={() => { refresh(); syncQ.refresh(); }}
                className="flex items-center gap-1 text-[11px] text-sky-300 hover:text-sky-200">
          <RefreshCw className="w-3 h-3" /> تحديث
        </button>}>
        {syncQ.loading && !syncQ.data ? <LoadingRows rows={4} /> : (
          (syncQ.data?.runs?.length ?? 0) === 0 ? (
            <div className="flex items-center gap-2 text-[12px] text-zinc-500">
              <MinusCircle className="w-4 h-4" /> لا سجلات بعد — أول دورة مراقبة ستسجلها تلقائيًا
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-[11px]">
                <thead>
                  <tr className="text-zinc-500 border-b border-zinc-800">
                    <th className="text-right py-2 pr-2">#</th>
                    <th className="text-right py-2">المزود</th>
                    <th className="text-right py-2">الحالة</th>
                    <th className="text-right py-2">المشغّل</th>
                    <th className="text-right py-2">عناصر</th>
                    <th className="text-right py-2">جديد</th>
                    <th className="text-right py-2">أسعار متغيرة</th>
                    <th className="text-right py-2">المدة</th>
                    <th className="text-right py-2 pl-2">الوقت</th>
                  </tr>
                </thead>
                <tbody>
                  {syncQ.data!.runs.map((r) => (
                    <tr key={r.id} className="border-b border-zinc-900 text-zinc-300">
                      <td className="py-2 pr-2 font-mono" dir="ltr">{r.id}</td>
                      <td className="py-2 font-mono" dir="ltr">{r.provider_code}</td>
                      <td className="py-2">
                        {r.status === "success" ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 inline" /> :
                         r.status === "failed" ? <XCircle className="w-3.5 h-3.5 text-rose-400 inline" /> :
                         <MinusCircle className="w-3.5 h-3.5 text-zinc-500 inline" />}
                        <span className="mr-1 text-[10.5px] text-zinc-500">
                          {r.status === "success" ? "نجحت" : r.status === "failed" ? "فشلت" : r.status === "skipped" ? "تخطت" : r.status}
                        </span>
                      </td>
                      <td className="py-2 text-zinc-500">{r.trigger === "manual" ? "يدوي" : "مجدول"}</td>
                      <td className="py-2 tabular-nums" dir="ltr">{r.items_seen ?? "—"}</td>
                      <td className="py-2 tabular-nums" dir="ltr">{r.products_new ?? "—"}</td>
                      <td className="py-2 tabular-nums" dir="ltr">{r.prices_updated ?? "—"}</td>
                      <td className="py-2 tabular-nums text-zinc-500" dir="ltr">{r.duration_ms ? `${(r.duration_ms / 1000).toFixed(1)}s` : "—"}</td>
                      <td className="py-2 pl-2 text-zinc-500">{r.started_at ? timeAgo(r.started_at) : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {syncQ.data!.runs.some((r) => r.errors) && (
                <div className="mt-2 space-y-1">
                  {syncQ.data!.runs.filter((r) => r.errors).slice(0, 3).map((r) => (
                    <div key={r.id} className="rounded-md border border-rose-900/40 bg-rose-950/10 px-2.5 py-1.5 text-[10.5px] text-rose-300" dir="ltr">
                      {r.provider_code}: {r.errors?.slice(0, 180)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        )}
      </SectionCard>
    </div>
  );
}
