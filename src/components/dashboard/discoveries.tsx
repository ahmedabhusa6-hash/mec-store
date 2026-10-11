"use client";

/**
 * MEC — discoveries & approvals view (rebuild v4).
 * Private-join candidates land here with their preview metadata; the owner
 * reviews → approves (monitor executes on the auto-dispatched run) or rejects.
 * Manual candidate addition (paste @handles / t.me links) included.
 */
import { useState } from "react";
import { Plus, Check, X, RotateCcw, Loader2, ShieldCheck, Users2 } from "lucide-react";
import { useApi, Badge, SectionCard, LoadingRows, ErrorState, EmptyState, timeAgo, fmtNum, STATUS_LABELS, DISC_STATUS_TONES, KIND_LABELS } from "./kit";

type DiscoveryRow = {
  handle: string; seenIn: number | null; seenAt: string; status: string; kind: string;
  title: string | null; members: number | null; previewAt: string | null;
  source: string; approvedBy: string | null; approvedAt: string | null;
};

type DiscoveriesData = {
  total: number;
  byStatus: Record<string, number>;
  byKind: Record<string, number>;
  recent: DiscoveryRow[];
  awaiting: DiscoveryRow[];
};

export function DiscoveriesView({ onDispatched }: { onDispatched?: () => void }) {
  const { data, error, loading, refresh } = useApi<DiscoveriesData>("/api/admin/discoveries", [], 60_000);
  const [filter, setFilter] = useState<string>("awaiting_approval");
  const [busy, setBusy] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [manual, setManual] = useState("");
  const [adding, setAdding] = useState(false);

  async function act(handle: string, action: "approve" | "reject" | "requeue") {
    setBusy(handle);
    setMsg(null);
    try {
      const r = await fetch("/api/admin/discoveries", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ handle, action }),
      });
      const j = (await r.json()) as { ok?: boolean; dispatched?: { ok: boolean; message: string } | null; error?: string };
      if (!r.ok) throw new Error(j.error ?? "فشل الطلب");
      if (action === "approve" && j.dispatched) {
        setMsg(j.dispatched.ok ? "✓ اعتُمد وأُطلقت دورة تنفيذ فورية" : `اعتُمد لكن تعذر الإطلاق الفوري: ${j.dispatched.message}`);
      } else {
        setMsg(action === "approve" ? "✓ اعتُمد" : action === "reject" ? "✓ رُفض" : "✓ أُعيد للطابور");
      }
      refresh();
      onDispatched?.();
    } catch (e) {
      setMsg(`خطأ: ${String(e instanceof Error ? e.message : e)}`);
    } finally {
      setBusy(null);
      setTimeout(() => setMsg(null), 7000);
    }
  }

  async function addManual() {
    if (!manual.trim()) return;
    setAdding(true);
    setMsg(null);
    try {
      const r = await fetch("/api/admin/discoveries", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: manual }),
      });
      const j = (await r.json()) as { added?: number; error?: string };
      if (!r.ok) throw new Error(j.error ?? "فشل الإضافة");
      setMsg(`✓ أُضيف ${j.added} مرشحًا — سيقيّمه المراقب في أقرب دورة`);
      setManual("");
      refresh();
    } catch (e) {
      setMsg(`خطأ: ${String(e instanceof Error ? e.message : e)}`);
    } finally {
      setAdding(false);
      setTimeout(() => setMsg(null), 7000);
    }
  }

  if (loading && !data) return <LoadingRows rows={8} />;
  if (error) return <ErrorState text={error} />;
  if (!data) return <EmptyState text="لا بيانات" />;

  const rows = filter === "all" ? data.recent : data.recent.filter((d) => d.status === filter);
  const filters = [
    { key: "awaiting_approval", label: `بانتظار موافقتك (${data.awaiting.length})` },
    { key: "approved", label: "معتمد بانتظار التنفيذ" },
    { key: "pending", label: "قيد التقييم التلقائي" },
    { key: "joined", label: "منضم" },
    { key: "all", label: `الكل (${data.total})` },
  ];

  return (
    <div className="space-y-5">
      {msg && <div className="rounded-lg border border-emerald-900/60 bg-emerald-950/30 px-4 py-2.5 text-[12px] text-emerald-300">{msg}</div>}

      {/* approval queue explanation */}
      <SectionCard title="بوابة موافقات الانضمام الخاص">
        <div className="text-[11.5px] text-zinc-400 leading-6">
          القنوات/المجموعات <b className="text-zinc-200">العامة</b> ينضم إليها المراقب تلقائيًا ضمن حدود الانضباط (حد أقصى 3 لكل دورة). أما روابط <b className="text-zinc-200">الدعوة الخاصة</b> فتُعاين قراءةً فقط (العنوان، النوع، عدد الأعضاء، علامات تلغرام الأمنية) ثم تتوقف هنا بانتظار قرارك — الاعتماد يطلق دورة تنفيذ فورية تلقائيًا. لا تُرسل طلبات انضمام للقنوات التي تشترط موافقة مشرف (سياسة مكافحة السبام).
        </div>
      </SectionCard>

      {/* manual add */}
      <SectionCard title="إضافة مرشحين يدويًا" extra={<span className="text-[10.5px] text-zinc-500">سطر لكل عنصر</span>}>
        <div className="flex flex-col gap-2 sm:flex-row">
          <textarea
            value={manual}
            onChange={(e) => setManual(e.target.value)}
            dir="ltr"
            placeholder={"@supplier_channel\nt.me/another_channel\nhttps://t.me/+AbCdEfGh1234"}
            className="flex-1 min-h-20 rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-2 text-[12px] text-zinc-200 font-mono placeholder:text-zinc-600 focus:outline-none focus:border-emerald-800"
          />
          <button
            onClick={addManual}
            disabled={adding || !manual.trim()}
            className="flex items-center justify-center gap-1.5 rounded-lg border border-emerald-800/70 bg-emerald-950/50 px-4 py-2 text-[12px] font-bold text-emerald-300 hover:bg-emerald-900/50 disabled:opacity-50 h-fit"
          >
            {adding ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            إضافة
          </button>
        </div>
      </SectionCard>

      {/* filters */}
      <div className="flex flex-wrap gap-1.5">
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`rounded-lg border px-3 py-1.5 text-[11.5px] font-medium transition-colors ${
              filter === f.key ? "border-emerald-700 bg-emerald-950/60 text-emerald-300" : "border-zinc-800 bg-zinc-900/60 text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* table */}
      <SectionCard>
        {rows.length === 0 ? (
          <EmptyState text={filter === "awaiting_approval" ? "لا طلبات بانتظار الموافقة — كل شيء واضح" : "لا نتائج"} />
        ) : (
          <div className="overflow-x-auto max-h-[520px] overflow-y-auto">
            <table className="w-full text-[11.5px]">
              <thead className="sticky top-0 bg-[#0d1421]">
                <tr className="text-zinc-500 text-start">
                  <th className="text-start py-2 px-2 font-medium">المرشح</th>
                  <th className="text-start py-2 px-2 font-medium">النوع</th>
                  <th className="text-start py-2 px-2 font-medium">الحالة</th>
                  <th className="text-start py-2 px-2 font-medium">المعاينة (خاص)</th>
                  <th className="text-start py-2 px-2 font-medium">المصدر</th>
                  <th className="text-start py-2 px-2 font-medium">أُضيف</th>
                  <th className="text-start py-2 px-2 font-medium">إجراء</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((d) => (
                  <tr key={d.handle} className="border-t border-zinc-800/60 hover:bg-zinc-900/40">
                    <td className="py-2 px-2 font-mono text-zinc-300 max-w-44 truncate" dir="ltr">{d.handle}</td>
                    <td className="py-2 px-2">
                      <Badge tone={d.kind === "invite" ? "violet" : "blue"}>{d.kind === "invite" ? "دعوة خاصة" : "مقبض عام"}</Badge>
                    </td>
                    <td className="py-2 px-2"><Badge tone={DISC_STATUS_TONES[d.status] ?? "gray"}>{STATUS_LABELS[d.status] ?? d.status}</Badge></td>
                    <td className="py-2 px-2">
                      {d.kind === "invite" ? (
                        d.title ? (
                          <span className="flex items-center gap-1.5 text-zinc-400">
                            <Users2 className="w-3 h-3" /> {d.title.slice(0, 30)} · {fmtNum(d.members)} عضو
                          </span>
                        ) : <span className="text-zinc-600">لم تُعاين بعد</span>
                      ) : "—"}
                    </td>
                    <td className="py-2 px-2 text-zinc-500">{d.source === "manual" ? "يدوي" : "تلقائي"}</td>
                    <td className="py-2 px-2 text-zinc-500 whitespace-nowrap">{timeAgo(d.seenAt)}</td>
                    <td className="py-2 px-2">
                      <div className="flex items-center gap-1">
                        {d.status === "awaiting_approval" && (
                          <>
                            <button onClick={() => act(d.handle, "approve")} disabled={busy === d.handle} className="flex items-center gap-1 rounded-md border border-emerald-800/70 bg-emerald-950/50 px-2 py-1 text-[10.5px] font-bold text-emerald-300 hover:bg-emerald-900/50 disabled:opacity-50">
                              {busy === d.handle ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />} اعتمد ونفّذ
                            </button>
                            <button onClick={() => act(d.handle, "reject")} disabled={busy === d.handle} className="flex items-center gap-1 rounded-md border border-rose-900/70 bg-rose-950/40 px-2 py-1 text-[10.5px] text-rose-300 hover:bg-rose-900/40 disabled:opacity-50">
                              <X className="w-3 h-3" /> رفض
                            </button>
                          </>
                        )}
                        {(d.status === "rejected" || d.status === "expired" || d.status === "not_found" || d.status === "disapproved") && d.source === "manual" && (
                          <button onClick={() => act(d.handle, "requeue")} disabled={busy === d.handle} className="flex items-center gap-1 rounded-md border border-zinc-700 bg-zinc-900/60 px-2 py-1 text-[10.5px] text-zinc-300 hover:bg-zinc-800/60 disabled:opacity-50">
                            <RotateCcw className="w-3 h-3" /> أعد للطابور
                          </button>
                        )}
                        {d.status === "approved" && (
                          <span className="flex items-center gap-1 text-[10.5px] text-sky-300"><ShieldCheck className="w-3 h-3" /> سيُنفَّذ في الدورة القادمة</span>
                        )}
                      </div>
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
