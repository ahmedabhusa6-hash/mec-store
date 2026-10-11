"use client";

import { useMemo, useState } from "react";
import { Search, ArrowUpDown } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useApi, Badge, LoadingRows, ErrorState, EmptyState, fmtDate, fmtPrice, KIND_LABELS } from "./kit";

type PriceRow = {
  channelId: number | null; username: string | null; title: string | null; kind: string;
  product: string; price: number | null; currency: string; unit: string | null; postedAt: string | null;
  supplier: string;
};

type PricesData = { total: number; rows: PriceRow[] };

type SortKey = "date" | "price" | "product" | "supplier";

export function PricesView() {
  const [q, setQ] = useState("");
  const [currency, setCurrency] = useState("");
  const [sort, setSort] = useState<SortKey>("date");
  const [desc, setDesc] = useState(true);

  const url = useMemo(() => {
    const p = new URLSearchParams();
    if (q.trim()) p.set("q", q.trim());
    if (currency) p.set("currency", currency);
    p.set("limit", "600");
    return `/api/admin/prices?${p.toString()}`;
  }, [q, currency]);

  const { data, error, loading } = useApi<PricesData>(url, [q, currency]);

  const rows = useMemo(() => {
    if (!data) return [];
    const r = [...data.rows];
    r.sort((a, b) => {
      let cmp = 0;
      if (sort === "date") cmp = (a.postedAt ?? "").localeCompare(b.postedAt ?? "");
      else if (sort === "price") cmp = (a.price ?? 1e9) - (b.price ?? 1e9);
      else if (sort === "product") cmp = a.product.localeCompare(b.product);
      else cmp = a.supplier.localeCompare(b.supplier);
      return desc ? -cmp : cmp;
    });
    return r;
  }, [data, sort, desc]);

  const toggleSort = (k: SortKey) => {
    if (sort === k) setDesc(!desc);
    else {
      setSort(k);
      setDesc(true);
    }
  };

  const cheapestByProduct = useMemo(() => {
    const m = new Map<string, number>();
    for (const r of rows) {
      if (r.price == null) continue;
      const cur = m.get(r.product);
      if (cur == null || r.price < cur) m.set(r.product, r.price);
    }
    return m;
  }, [rows]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="ابحث عن منتج أو مورد… (Claude، ChatGPT، Gemini، VPN…)"
            className="ps-9 bg-[#0d1421] border-zinc-800 text-zinc-200 placeholder:text-zinc-600 h-10"
          />
        </div>
        <div className="flex gap-2">
          {["", "USD", "USDT"].map((c) => (
            <button
              key={c || "all"}
              onClick={() => setCurrency(c)}
              className={`h-10 px-4 rounded-lg border text-[12px] font-medium transition-colors ${
                currency === c ? "border-emerald-700 bg-emerald-950/60 text-emerald-300" : "border-zinc-800 bg-[#0d1421] text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {c || "الكل"}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-zinc-800/80 bg-[#0d1421] overflow-hidden">
        {loading && !data ? (
          <div className="p-4"><LoadingRows rows={8} /></div>
        ) : error && !data ? (
          <ErrorState text={error} />
        ) : rows.length === 0 ? (
          <EmptyState text="لا توجد نتائج مطابقة" />
        ) : (
          <>
            <div className="px-4 py-2.5 border-b border-zinc-800/60 text-[11.5px] text-zinc-500">
              {rows.length.toLocaleString("en-US")} صف — أحدث سعر موثق لكل (مورّد × منتج)
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-[12.5px]">
                <thead>
                  <tr className="text-zinc-500 border-b border-zinc-800/60 bg-zinc-900/50">
                    {([
                      ["product", "المنتج"],
                      ["supplier", "المورّد"],
                      ["price", "السعر"],
                      ["date", "آخر نشر"],
                    ] as [SortKey, string][]).map(([k, label]) => (
                      <th key={k} className="text-start font-medium px-4 py-2.5 cursor-pointer hover:text-zinc-300 select-none whitespace-nowrap" onClick={() => toggleSort(k)}>
                        <span className="inline-flex items-center gap-1">{label}{sort === k && <ArrowUpDown className="w-3 h-3" />}</span>
                      </th>
                    ))}
                    <th className="text-start font-medium px-4 py-2.5">الوحدة</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r, i) => {
                    const isCheapest = r.price != null && cheapestByProduct.get(r.product) === r.price;
                    return (
                      <tr key={i} className={`border-b border-zinc-900 hover:bg-zinc-900/40 transition-colors ${isCheapest ? "bg-emerald-950/20" : ""}`}>
                        <td className="px-4 py-2.5 max-w-[280px]">
                          <span className="text-zinc-200 block truncate" title={r.product}>{r.product}</span>
                          {isCheapest && <Badge tone="green">أرخص عرض</Badge>}
                        </td>
                        <td className="px-4 py-2.5 whitespace-nowrap">
                          <span className="text-amber-300/90">{r.supplier}</span>
                          {!r.username && r.title && <Badge tone="violet">خاصة</Badge>}
                          <span className="block text-[10px] text-zinc-600">{KIND_LABELS[r.kind] ?? r.kind}</span>
                        </td>
                        <td className="px-4 py-2.5 whitespace-nowrap">
                          <span className="font-bold text-emerald-400 tabular-nums" dir="ltr">{fmtPrice(r.price, r.currency)}</span>
                        </td>
                        <td className="px-4 py-2.5 whitespace-nowrap text-zinc-500 tabular-nums text-[11.5px]">{fmtDate(r.postedAt)}</td>
                        <td className="px-4 py-2.5">
                          {r.unit ? <Badge tone="gray">{r.unit}</Badge> : <span className="text-zinc-600">—</span>}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
