"use client";

/**
 * MEC — settings & governance view (rebuild v4): runtime-tunable automation
 * policy (persisted to settings table, read by the monitor at each run start),
 * live circuit breakers, and the documented Telegram ToS compliance layer.
 */
import { useState } from "react";
import { Settings2, ShieldAlert, Save, Loader2, Scale, ExternalLink } from "lucide-react";
import { useApi, Badge, SectionCard, LoadingRows, ErrorState, EmptyState, timeAgo } from "./kit";

type Policy = {
  joinBudgetPerRun: number; privateJoinCapPerRun: number; joinDelaySeconds: string;
  totalJoinCeiling: number; telegramUserLimit: number; safetyMargin: string;
  peerFloodPause: string; floodWaitJoinPause: string; scanPauseOnFloodWait: string;
  adminGatedChats: string; expiredInvites: string; privateJoinPolicy: string; publicJoinPolicy: string;
  dataPolicy: string; cron: string;
  tosSources: { name: string; url: string }[];
};

type SettingRow = { key: string; value: string | null; updated_at: string; updated_by: string | null };
type Tunable = Record<string, { type: string; min: number; max: number; label: string }>;

type SettingsData = { policy: Policy; settings: SettingRow[]; tunable: Tunable };

export function SettingsView() {
  const { data, error, loading, refresh } = useApi<SettingsData>("/api/admin/settings", [], 60_000);
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  if (loading && !data) return <LoadingRows rows={8} />;
  if (error) return <ErrorState text={error} />;
  if (!data) return <EmptyState text="لا بيانات" />;

  const settingMap = new Map(data.settings.map((s) => [s.key, s]));
  const now = new Date();
  const activeBreakers = data.settings.filter(
    (s) => (s.key.startsWith("join_pause") || s.key.startsWith("scan_pause_")) && s.value && new Date(s.value) > now,
  );

  async function save(key: string) {
    const raw = draft[key];
    if (raw == null) return;
    setBusy(key);
    setMsg(null);
    try {
      const r = await fetch("/api/admin/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, value: raw }),
      });
      const j = (await r.json()) as { ok?: boolean; error?: string };
      if (!r.ok) throw new Error(j.error ?? "فشل الحفظ");
      setMsg(`✓ حُفظ ${key} = ${raw} — تسري في الدورة القادمة`);
      setDraft((d) => { const n = { ...d }; delete n[key]; return n; });
      refresh();
    } catch (e) {
      setMsg(`خطأ: ${String(e instanceof Error ? e.message : e)}`);
    } finally {
      setBusy(null);
      setTimeout(() => setMsg(null), 7000);
    }
  }

  async function clearBreakers() {
    setBusy("breakers");
    try {
      const r = await fetch("/api/admin/settings", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "clear_breaker" }),
      });
      const j = (await r.json()) as { cleared?: string[]; error?: string };
      if (!r.ok) throw new Error(j.error ?? "فشل");
      setMsg(`✓ رُفعت ${j.cleared?.length ?? 0} حالة تعليق — تستأنف الأتمتة في الدورة القادمة`);
      refresh();
    } catch (e) {
      setMsg(`خطأ: ${String(e instanceof Error ? e.message : e)}`);
    } finally {
      setBusy(null);
      setTimeout(() => setMsg(null), 7000);
    }
  }

  return (
    <div className="space-y-5">
      {msg && <div className="rounded-lg border border-emerald-900/60 bg-emerald-950/30 px-4 py-2.5 text-[12px] text-emerald-300">{msg}</div>}

      {/* tunables */}
      <SectionCard title="سياسات الأتمتة القابلة للضبط" extra={<span className="text-[10.5px] text-zinc-500">تُقرأ في بداية كل دورة</span>}>
        <div className="grid gap-3 sm:grid-cols-2">
          {Object.entries(data.tunable).map(([key, spec]) => {
            const current = settingMap.get(key)?.value;
            return (
              <div key={key} className="rounded-lg border border-zinc-800/60 bg-zinc-900/40 p-3">
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[12px] font-medium text-zinc-200">{spec.label}</span>
                  {current != null && <Badge tone="blue">مضبوط: {current}</Badge>}
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min={spec.min}
                    max={spec.max}
                    value={draft[key] ?? current ?? ""}
                    onChange={(e) => setDraft((d) => ({ ...d, [key]: e.target.value }))}
                    className="w-24 rounded-md border border-zinc-800 bg-zinc-900 px-2.5 py-1.5 text-[12px] tabular-nums text-zinc-200 focus:outline-none focus:border-emerald-800"
                  />
                  <span className="text-[10.5px] text-zinc-600">النطاق {spec.min}–{spec.max}{current == null ? " · الافتراضي إن تُرك فارغًا" : ""}</span>
                  <div className="flex-1" />
                  <button
                    onClick={() => save(key)}
                    disabled={busy === key || draft[key] == null || draft[key] === (current ?? "")}
                    className="flex items-center gap-1 rounded-md border border-emerald-800/70 bg-emerald-950/50 px-2.5 py-1.5 text-[11px] font-bold text-emerald-300 hover:bg-emerald-900/50 disabled:opacity-40"
                  >
                    {busy === key ? <Loader2 className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />} حفظ
                  </button>
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-3 text-[10.5px] text-zinc-600 leading-5">
          القيم الافتراضية المحافظة: 3 انضمامات/دورة (≤2 خاصة) · سقف إجمالي 250 من حد تلغرام 500 بهامش أمان مضاعف · للوصول إلى هدف ~400 مصدر ارفع السقف تدريجيًا مع مراقبة التنبيهات (قرار يعود للمالك).
        </div>
      </SectionCard>

      {/* circuit breakers */}
      <SectionCard title="قواطع الأمان النشطة">
        {activeBreakers.length === 0 ? (
          <div className="flex items-center gap-2 text-[12px] text-emerald-400">
            <ShieldAlert className="w-4 h-4" /> لا قواطع نشطة — الأتمتة تعمل بانتظام كامل
          </div>
        ) : (
          <div className="space-y-2">
            {activeBreakers.map((b) => (
              <div key={b.key} className="flex items-center gap-2 rounded-lg border border-amber-900/50 bg-amber-950/20 px-3 py-2 text-[11.5px]">
                <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                <span className="font-mono text-zinc-300" dir="ltr">{b.key}</span>
                <span className="text-amber-300">حتى {new Date(b.value!).toLocaleString("en-GB")}</span>
                <span className="text-zinc-600">({timeAgo(b.updated_at)})</span>
              </div>
            ))}
            <button
              onClick={clearBreakers}
              disabled={busy === "breakers"}
              className="flex items-center gap-1.5 rounded-lg border border-amber-800/70 bg-amber-950/40 px-3 py-2 text-[11.5px] font-bold text-amber-300 hover:bg-amber-900/40 disabled:opacity-50"
            >
              {busy === "breakers" ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Settings2 className="w-3.5 h-3.5" />}
              ارفع جميع التعليقات (استئناف فوري)
            </button>
            <div className="text-[10.5px] text-zinc-600 leading-5">
              قواطع الأمان تحمي حساب تلغرام من أنظمة مكافحة السبام (PeerFlood / FloodWait) — لا ترفعها إلا بعد فهم السبب. التعليق يُفرض تلقائيًا ويُرفع تلقائيًا عند انتهاء مدته.
            </div>
          </div>
        )}
      </SectionCard>

      {/* policy doc */}
      <SectionCard title="طبقة الانضباط الموثقة (شروط خدمة تلغرام)">
        <div className="grid gap-2 text-[11.5px]">
          {[
            ["معدل الانضمام", `${data.policy.joinBudgetPerRun} كحد أقصى لكل دورة (≤ ${data.policy.privateJoinCapPerRun} خاصة) بفاصل ${data.policy.joinDelaySeconds}`],
            ["السقف الإجمالي", `${data.policy.totalJoinCeiling} (حد تلغرام ${data.policy.telegramUserLimit} — هامش ${data.policy.safetyMargin})`],
            ["الانضمام الخاص", data.policy.privateJoinPolicy],
            ["الانضمام العام", data.policy.publicJoinPolicy],
            ["قاطع PeerFlood", data.policy.peerFloodPause],
            ["قاطع FloodWait", data.policy.floodWaitJoinPause],
            ["توقف مسح قناة", data.policy.scanPauseOnFloodWait],
            ["القنوات بموافقة مشرف", data.policy.adminGatedChats],
            ["روابط الدعوة المنتهية", data.policy.expiredInvites],
            ["الجدولة", data.policy.cron],
            ["سياسة البيانات", data.policy.dataPolicy],
          ].map(([k, v]) => (
            <div key={k} className="flex flex-wrap items-start gap-2 rounded-lg border border-zinc-800/60 bg-zinc-900/40 px-3 py-2">
              <span className="text-zinc-500 min-w-32">{k}</span>
              <span className="text-zinc-300 flex-1">{v}</span>
            </div>
          ))}
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {data.policy.tosSources.map((s) => (
            <a
              key={s.url}
              href={s.url}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-1.5 text-[11px] text-sky-300 hover:border-sky-900/60"
            >
              <Scale className="w-3.5 h-3.5" /> {s.name} <ExternalLink className="w-3 h-3" />
            </a>
          ))}
        </div>
        <div className="mt-2 text-[10.5px] text-zinc-600">آخر مراجعة رسمية للمصادر: 2026-10-11</div>
      </SectionCard>
    </div>
  );
}
