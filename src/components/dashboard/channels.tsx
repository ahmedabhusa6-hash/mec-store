"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useApi, Badge, LoadingRows, ErrorState, EmptyState, fmtNum, fmtDate, KIND_LABELS } from "./kit";

type ChannelRow = {
  tgId: number;
  username: string | null;
  title: string | null;
  kind: string;
  relevance: string;
  joined: boolean;
  lastScanned: string | null;
  observations: number;
  products: number;
};

const RELEVANCE_LABELS: Record<string, string> = {
  anchor: "مرجعي",
  relevant: "وثيق الصلة",
  possible: "محتمل",
  new: "جديد",
};

export function ChannelsView() {
  const [q, setQ] = useState("");
  const [kind, setKind] = useState("");
  const { data, error, loading } = useApi<{ total: number; rows: ChannelRow[] }>(
    `/api/admin/channels${kind ? `?kind=${kind}${q.trim() ? `&q=${encodeURIComponent(q.trim())}` : ""}` : q.trim() ? `?q=${encodeURIComponent(q.trim())}` : ""}`,
    [q, kind]
  );

  const rows = data?.rows ?? [];

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="ابحث بالاسم أو المعرّف…"
            className="ps-9 bg-[#0d1421] border-zinc-800 text-zinc-200 placeholder:text-zinc-600 h-10"
          />
        </div>
        <div className="flex gap-2">
          {[
            ["", "الكل"],
            ["channel", "قنوات"],
            ["group", "مجموعات"],
            ["bot", "بوتات"],
          ].map(([k, label]) => (
            <button
              key={k || "all"}
              onClick={() => setKind(k)}
              className={`h-10 px-4 rounded-lg border text-[12px] font-medium transition-colors ${
                kind === k ? "border-emerald-700 bg-emerald-950/60 text-emerald-300" : "border-zinc-800 bg-[#0d1421] text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {label}
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
          <EmptyState text="لا توجد نتائج" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-[12.5px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800/60 bg-zinc-900/50">
                  <th className="text-start font-medium px-4 py-2.5">المصدر</th>
                  <th className="text-start font-medium px-4 py-2.5">النوع</th>
                  <th className="text-start font-medium px-4 py-2.5">الأهمية</th>
                  <th className="text-start font-medium px-4 py-2.5">الحالة</th>
                  <th className="text-start font-medium px-4 py-2.5">رصد</th>
                  <th className="text-start font-medium px-4 py-2.5">منتجات</th>
                  <th className="text-start font-medium px-4 py-2.5">آخر مسح</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((c) => (
                  <tr key={c.tgId} className="border-b border-zinc-900 hover:bg-zinc-900/40 transition-colors">
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-zinc-200 font-medium truncate max-w-[220px]" title={c.title ?? undefined}>
                          {c.title || (c.username ? `@${c.username}` : `#${c.tgId}`)}
                        </span>
                        {c.username ? (
                          <a href={`https://t.me/${c.username}`} target="_blank" rel="noopener noreferrer" className="text-[10.5px] text-sky-400 hover:text-sky-300 shrink-0" dir="ltr">@{c.username}</a>
                        ) : (
                          <Badge tone="violet">خاصة</Badge>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-2.5 text-zinc-400 whitespace-nowrap">{KIND_LABELS[c.kind] ?? c.kind}</td>
                    <td className="px-4 py-2.5 whitespace-nowrap">
                      <Badge tone={c.relevance === "anchor" ? "green" : c.relevance === "relevant" ? "blue" : "gray"}>
                        {RELEVANCE_LABELS[c.relevance] ?? c.relevance}
                      </Badge>
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap">
                      {c.joined ? <Badge tone="green">منضم</Badge> : <Badge tone="gray">غير منضم</Badge>}
                    </td>
                    <td className="px-4 py-2.5 tabular-nums text-zinc-300">{fmtNum(c.observations)}</td>
                    <td className="px-4 py-2.5 tabular-nums text-zinc-300">{fmtNum(c.products)}</td>
                    <td className="px-4 py-2.5 text-zinc-500 tabular-nums text-[11.5px] whitespace-nowrap">{fmtDate(c.lastScanned)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
