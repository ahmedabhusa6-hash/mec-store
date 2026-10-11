"use client";

import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useApi, Badge, LoadingRows, ErrorState, EmptyState, fmtNum, fmtPrice, timeAgo } from "./kit";

type ProductRow = {
  product: string;
  bestPrice: number;
  bestSupplier: string;
  bestCurrency: string;
  bestUnit: string | null;
  minPrice: number;
  maxPrice: number;
  suppliers: number;
  observations: number;
  lastSeen: string | null;
};

export function ProductsView() {
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<"suppliers" | "price" | "observations" | "recent">("suppliers");
  const { data, error, loading } = useApi<{ total: number; rows: ProductRow[] }>(
    `/api/admin/products?sort=${sort}${q.trim() ? `&q=${encodeURIComponent(q.trim())}` : ""}`,
    [q, sort]
  );

  const rows = data?.rows ?? [];

  const stats = useMemo(() => {
    if (rows.length === 0) return null;
    const multiSupplier = rows.filter((r) => r.suppliers >= 3).length;
    return { total: rows.length, multiSupplier };
  }, [rows]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="ابحث عن منتج…"
            className="ps-9 bg-[#0d1421] border-zinc-800 text-zinc-200 placeholder:text-zinc-600 h-10"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          {([
            ["suppliers", "الأكثر تنافسًا"],
            ["price", "الأرخص"],
            ["observations", "الأكثر رصدًا"],
            ["recent", "الأحدث"],
          ] as const).map(([k, label]) => (
            <button
              key={k}
              onClick={() => setSort(k)}
              className={`h-10 px-3.5 rounded-lg border text-[12px] font-medium transition-colors ${
                sort === k ? "border-emerald-700 bg-emerald-950/60 text-emerald-300" : "border-zinc-800 bg-[#0d1421] text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {stats && (
        <div className="flex flex-wrap gap-2 text-[11.5px] text-zinc-500">
          <Badge tone="gray">{fmtNum(stats.total)} منتجًا</Badge>
          <Badge tone="green">{fmtNum(stats.multiSupplier)} منتجًا بثلاثة موردين أو أكثر — فرص تفاوض مباشرة</Badge>
        </div>
      )}

      {loading && !data ? (
        <LoadingRows rows={8} />
      ) : error && !data ? (
        <ErrorState text={error} />
      ) : rows.length === 0 ? (
        <EmptyState text="لا توجد منتجات مطابقة" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
          {rows.map((r) => (
            <div
              key={r.product}
              className="rounded-xl border border-zinc-800/80 bg-[#0d1421] p-4 hover:border-zinc-700 transition-colors flex flex-col gap-2"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="text-[13px] font-bold text-zinc-100 leading-5 line-clamp-2" title={r.product}>{r.product}</span>
                {r.suppliers >= 3 && <Badge tone="green">تنافسي</Badge>}
              </div>
              <div className="flex items-baseline justify-between gap-2">
                <div>
                  <span className="text-xl font-extrabold text-emerald-400 tabular-nums" dir="ltr">{fmtPrice(r.bestPrice, r.bestCurrency)}</span>
                  {r.bestUnit && <span className="text-[10.5px] text-zinc-500 ms-1.5">{r.bestUnit}</span>}
                </div>
                <Badge tone="gold">{r.suppliers} موردين</Badge>
              </div>
              <div className="text-[11px] text-zinc-500">أرخص عرض: <span className="text-amber-300/90">{r.bestSupplier}</span></div>
              <div className="flex items-center justify-between gap-2 pt-1.5 border-t border-zinc-800/60 text-[10.5px] text-zinc-500 tabular-nums">
                <span>النطاق: <span dir="ltr">{r.minPrice}–{r.maxPrice}</span></span>
                <span>{fmtNum(r.observations)} رصد · {timeAgo(r.lastSeen)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
