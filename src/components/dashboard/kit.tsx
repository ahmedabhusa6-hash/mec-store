"use client";

/**
 * MEC Intelligence — shared UI kit: fetch hook, KPI cards, badges, formatters.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";

// ─── data fetching ────────────────────────────────────────────────────
export function useApi<T>(url: string, deps: unknown[] = [], intervalMs?: number) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [tick, setTick] = useState(0);
  const mounted = useRef(true);

  const refresh = useCallback(() => setTick((t) => t + 1), []);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(url)
      .then(async (r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return (await r.json()) as T;
      })
      .then((d) => {
        if (!cancelled && mounted.current) {
          setData(d);
          setError(null);
        }
      })
      .catch((e) => {
        if (!cancelled && mounted.current) setError(String(e.message ?? e));
      })
      .finally(() => {
        if (!cancelled && mounted.current) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [url, tick, ...deps]);

  useEffect(() => {
    if (!intervalMs) return;
    const id = setInterval(() => setTick((t) => t + 1), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  return { data, error, loading, refresh };
}

// ─── formatters ───────────────────────────────────────────────────────
export const nf = new Intl.NumberFormat("en-US");

export function fmtNum(v: number | null | undefined): string {
  return v == null ? "—" : nf.format(v);
}

export function fmtPrice(v: number | null | undefined, currency = "USD"): string {
  if (v == null) return "—";
  return `${nf.format(v)} ${currency === "USDT" ? "USDT" : "$"}`;
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short" }) + " " + d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

export function fmtDay(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-GB", { day: "2-digit", month: "2-digit" });
}

export function timeAgo(iso: string | null | undefined): string {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "الآن";
  if (m < 60) return `قبل ${m} دقيقة`;
  const h = Math.floor(m / 60);
  if (h < 24) return `قبل ${h} ساعة`;
  const d = Math.floor(h / 24);
  if (d < 30) return `قبل ${d} يوم`;
  return `قبل ${Math.floor(d / 30)} شهر`;
}

export function fmtDuration(sec: number | null): string {
  if (sec == null) return "—";
  if (sec < 60) return `${sec} ث`;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  if (m < 60) return `${m}د ${s ? s + "ث" : ""}`.trim();
  return `${Math.floor(m / 60)}س ${m % 60}د`;
}

// ─── primitives ───────────────────────────────────────────────────────
export function KpiCard({
  label, value, sub, tone = "emerald", icon,
}: {
  label: string; value: string | number; sub?: string;
  tone?: "emerald" | "amber" | "sky" | "rose" | "violet"; icon?: React.ReactNode;
}) {
  const tones: Record<string, string> = {
    emerald: "text-emerald-400 border-emerald-900/60 bg-emerald-950/30",
    amber: "text-amber-400 border-amber-900/60 bg-amber-950/30",
    sky: "text-sky-400 border-sky-900/60 bg-sky-950/30",
    rose: "text-rose-400 border-rose-900/60 bg-rose-950/30",
    violet: "text-violet-400 border-violet-900/60 bg-violet-950/30",
  };
  return (
    <div className="rounded-xl border border-zinc-800/80 bg-[#0d1421] p-4 flex flex-col gap-1 hover:border-zinc-700 transition-colors">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11.5px] text-zinc-400 font-medium leading-4">{label}</span>
        {icon && <span className={`shrink-0 w-7 h-7 rounded-lg border flex items-center justify-center ${tones[tone]}`}>{icon}</span>}
      </div>
      <span className="text-2xl font-extrabold tabular-nums text-zinc-50 leading-7">{typeof value === "number" ? fmtNum(value) : value}</span>
      {sub && <span className="text-[11px] text-zinc-500 leading-4">{sub}</span>}
    </div>
  );
}

export function SectionCard({
  title, extra, children, className = "",
}: {
  title?: string; extra?: React.ReactNode; children: React.ReactNode; className?: string;
}) {
  return (
    <section className={`rounded-xl border border-zinc-800/80 bg-[#0d1421] ${className}`}>
      {title && (
        <header className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 border-b border-zinc-800/60">
          <h3 className="text-[13px] font-bold text-zinc-200">{title}</h3>
          {extra}
        </header>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}

const badgeStyles: Record<string, string> = {
  green: "bg-emerald-950/60 text-emerald-300 border-emerald-900/70",
  gold: "bg-amber-950/60 text-amber-300 border-amber-900/70",
  blue: "bg-sky-950/60 text-sky-300 border-sky-900/70",
  gray: "bg-zinc-900 text-zinc-400 border-zinc-800",
  red: "bg-rose-950/60 text-rose-300 border-rose-900/70",
  violet: "bg-violet-950/60 text-violet-300 border-violet-900/70",
};

export function Badge({ children, tone = "gray" }: { children: React.ReactNode; tone?: keyof typeof badgeStyles }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10.5px] font-medium whitespace-nowrap ${badgeStyles[tone]}`}>
      {children}
    </span>
  );
}

export function EmptyState({ text }: { text: string }) {
  return (
    <div className="py-12 text-center text-[13px] text-zinc-500">{text}</div>
  );
}

export function ErrorState({ text }: { text: string }) {
  return (
    <div className="py-10 text-center text-[13px] text-rose-400">تعذر التحميل: {text}</div>
  );
}

export function LoadingRows({ rows = 6 }: { rows?: number }) {
  return (
    <div className="space-y-2.5">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-10 w-full bg-zinc-900" />
      ))}
    </div>
  );
}

export const KIND_LABELS: Record<string, string> = {
  channel: "قناة",
  group: "مجموعة",
  bot: "بوت",
};

export const STATUS_LABELS: Record<string, string> = {
  pending: "قيد التقييم",
  joined: "منضم",
  rejected: "مرفوض",
  not_found: "غير موجود",
  expired: "منتهي",
  request_needed: "يتطلب موافقة مشرف",
  request_sent: "طلب مُرسل",
  awaiting_approval: "بانتظار موافقتك",
  approved: "معتمد — سيُنفَّذ",
  disapproved: "مرفوض من المالك",
};

export const DISC_STATUS_TONES: Record<string, keyof typeof badgeStyles> = {
  pending: "gold",
  joined: "green",
  rejected: "red",
  not_found: "gray",
  expired: "gray",
  request_needed: "violet",
  request_sent: "blue",
  awaiting_approval: "violet",
  approved: "blue",
  disapproved: "red",
};

export const FRESHNESS_LABELS: Record<string, string> = {
  fresh: "حديث",
  aging: "يتقادم",
  stale: "قديم",
  ancient: "متقادم جدًا",
  unknown: "غير مؤرخ",
};

export const FRESHNESS_TONES: Record<string, keyof typeof badgeStyles> = {
  fresh: "green",
  aging: "gold",
  stale: "red",
  ancient: "red",
  unknown: "gray",
};

export const STMT_LABELS: Record<string, string> = {
  warranty: "ضمان",
  payment: "دفع",
  payment_terms: "شروط دفع",
  min_order: "حد أدنى للطلب",
  replacement: "استبدال",
};
