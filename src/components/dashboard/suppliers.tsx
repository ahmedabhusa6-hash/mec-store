"use client";

import { useState } from "react";
import { Search, ShieldCheck, CreditCard, PackageCheck } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useApi, Badge, LoadingRows, ErrorState, EmptyState, fmtNum, fmtPrice, timeAgo, KIND_LABELS } from "./kit";

type SupplierRow = {
  channelId: number;
  name: string;
  username: string | null;
  kind: string;
  isPrivate: boolean;
  observations: number;
  products: number;
  firstSeen: string | null;
  lastSeen: string | null;
  avgPriceUsd: number | null;
  signals: { warranty: number; payment: number; minOrder: number; replacement: number };
};

export function SuppliersView() {
  const [q, setQ] = useState("");
  const { data, error, loading } = useApi<{ total: number; rows: SupplierRow[] }>(
    `/api/admin/suppliers${q.trim() ? `?q=${encodeURIComponent(q.trim())}` : ""}`,
    [q]
  );

  const rows = data?.rows ?? [];

  return (
    <div className="space-y-4">
      <div className="relative max-w-md">
        <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="ابحث عن مورّد…"
          className="ps-9 bg-[#0d1421] border-zinc-800 text-zinc-200 placeholder:text-zinc-600 h-10"
        />
      </div>

      {loading && !data ? (
        <LoadingRows rows={6} />
      ) : error && !data ? (
        <ErrorState text={error} />
      ) : rows.length === 0 ? (
        <EmptyState text="لا توجد نتائج" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {rows.map((s) => (
            <div key={s.channelId} className="rounded-xl border border-zinc-800/80 bg-[#0d1421] p-4 hover:border-zinc-700 transition-colors">
              <div className="flex items-start justify-between gap-2 mb-2.5">
                <div className="min-w-0">
                  <div className="text-[13.5px] font-bold text-zinc-100 truncate">{s.name}</div>
                  <div className="text-[10.5px] text-zinc-500 mt-0.5 flex items-center gap-1.5 flex-wrap">
                    <span>{KIND_LABELS[s.kind] ?? s.kind}</span>
                    {s.username ? (
                      <a
                        href={`https://t.me/${s.username}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sky-400 hover:text-sky-300 transition-colors"
                        dir="ltr"
                      >
                        @{s.username}
                      </a>
                    ) : (
                      <Badge tone="violet">خاصة — عبر دعوة</Badge>
                    )}
                  </div>
                </div>
                {s.observations > 500 && <Badge tone="green">نشط جدًا</Badge>}
              </div>

              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="rounded-lg bg-zinc-900/60 border border-zinc-800/60 px-2.5 py-2 text-center">
                  <div className="text-[15px] font-bold text-zinc-100 tabular-nums">{fmtNum(s.observations)}</div>
                  <div className="text-[9.5px] text-zinc-500">رصد</div>
                </div>
                <div className="rounded-lg bg-zinc-900/60 border border-zinc-800/60 px-2.5 py-2 text-center">
                  <div className="text-[15px] font-bold text-zinc-100 tabular-nums">{fmtNum(s.products)}</div>
                  <div className="text-[9.5px] text-zinc-500">منتج</div>
                </div>
                <div className="rounded-lg bg-zinc-900/60 border border-zinc-800/60 px-2.5 py-2 text-center">
                  <div className="text-[15px] font-bold text-zinc-100 tabular-nums" dir="ltr">{s.avgPriceUsd != null ? `$${s.avgPriceUsd}` : "—"}</div>
                  <div className="text-[9.5px] text-zinc-500">متوسط السعر</div>
                </div>
              </div>

              <div className="flex flex-wrap gap-1.5 mb-2.5">
                {s.signals.warranty > 0 && (
                  <Badge tone="green"><ShieldCheck className="w-3 h-3" /> ضمان ×{fmtNum(s.signals.warranty)}</Badge>
                )}
                {s.signals.payment > 0 && (
                  <Badge tone="blue"><CreditCard className="w-3 h-3" /> دفع ×{fmtNum(s.signals.payment)}</Badge>
                )}
                {s.signals.minOrder > 0 && (
                  <Badge tone="gold"><PackageCheck className="w-3 h-3" /> حد أدنى ×{fmtNum(s.signals.minOrder)}</Badge>
                )}
              </div>

              <div className="text-[10px] text-zinc-600 tabular-nums flex justify-between">
                <span>أول رصد: {timeAgo(s.firstSeen)}</span>
                <span>آخر رصد: {timeAgo(s.lastSeen)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
