"use client";

/** MEC — audit trail view (rebuild v4): every sensitive action, immutable. */
import { ScrollText } from "lucide-react";
import { useApi, Badge, SectionCard, LoadingRows, ErrorState, EmptyState, timeAgo } from "./kit";

type AuditRow = {
  id: number; actor: string; action: string; entity: string | null;
  entityId: string | null; details: string | null; ip: string | null; createdAt: string;
};

const ACTION_LABELS: Record<string, string> = {
  "auth.login_ok": "دخول ناجح",
  "auth.login_failed": "دخول فاشل",
  "discoveries.approve": "اعتماد انضمام",
  "discoveries.reject": "رفض انضمام",
  "discoveries.requeue": "إعادة للطابور",
  "discoveries.add_manual": "إضافة مرشحين يدويًا",
  "automation.dispatch": "إطلاق دورة فورية",
  "settings.update": "تعديل إعداد",
  "settings.clear_breakers": "رفع قواطع الأمان",
  "alerts.mark_all_read": "تحديد التنبيهات كمقروءة",
  "tg.join": "انضمام منفَّذ (مراقب)",
  "monitor.breaker": "تفعيل قاطع أمان (مراقب)",
};

export function AuditView() {
  const { data, error, loading } = useApi<AuditRow[]>("/api/admin/audit", [], 60_000);

  if (loading && !data) return <LoadingRows rows={8} />;
  if (error) return <ErrorState text={error} />;
  if (!data || data.length === 0) {
    return (
      <SectionCard>
        <div className="py-10 text-center">
          <ScrollText className="w-8 h-8 text-zinc-700 mx-auto mb-3" />
          <div className="text-[13px] text-zinc-500">سجل التدقيق فارغ — ستظهر هنا كل الإجراءات الحساسة (دخول، موافقات، إعدادات، تشغيل، انضمامات)</div>
        </div>
      </SectionCard>
    );
  }

  return (
    <SectionCard title={`سجل التدقيق — آخر ${data.length} إجراء`}>
      <div className="overflow-x-auto max-h-[560px] overflow-y-auto">
        <table className="w-full text-[11.5px]">
          <thead className="sticky top-0 bg-[#0d1421]">
            <tr className="text-zinc-500">
              <th className="text-start py-2 px-2 font-medium">الوقت</th>
              <th className="text-start py-2 px-2 font-medium">الفاعل</th>
              <th className="text-start py-2 px-2 font-medium">الإجراء</th>
              <th className="text-start py-2 px-2 font-medium">الكيان</th>
              <th className="text-start py-2 px-2 font-medium">التفاصيل</th>
              <th className="text-start py-2 px-2 font-medium">IP</th>
            </tr>
          </thead>
          <tbody>
            {data.map((a) => (
              <tr key={a.id} className="border-t border-zinc-800/60 hover:bg-zinc-900/40">
                <td className="py-2 px-2 text-zinc-400 whitespace-nowrap">{timeAgo(a.createdAt)}</td>
                <td className="py-2 px-2 text-zinc-300 max-w-40 truncate">{a.actor}</td>
                <td className="py-2 px-2"><Badge tone={a.action.includes("failed") ? "red" : a.action.startsWith("discoveries") ? "violet" : "blue"}>{ACTION_LABELS[a.action] ?? a.action}</Badge></td>
                <td className="py-2 px-2 text-zinc-500 font-mono max-w-40 truncate" dir="ltr">{a.entityId ?? a.entity ?? "—"}</td>
                <td className="py-2 px-2 text-zinc-500 max-w-64 truncate" dir="ltr">{a.details?.slice(0, 90) ?? "—"}</td>
                <td className="py-2 px-2 text-zinc-600 font-mono" dir="ltr">{a.ip ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}
