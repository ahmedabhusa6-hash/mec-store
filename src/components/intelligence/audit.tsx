'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { runData, actionsData } from '@/lib/data';
import { statusBadge } from './shared';

export function Audit() {
  const au = runData.audit_record as any;
  const failures = runData.failure_recovery_log as any[];
  const [q, setQ] = useState('');
  const actions = (actionsData.actions as any[]).filter(
    (a) => !q || a.query.toLowerCase().includes(q.toLowerCase()) || a.action_id.toLowerCase().includes(q.toLowerCase()) || (a.sku_id || '').toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Audit record */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">سجل التدقيق (§23)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <AuditBlock title="ما الذي تأسس" items={au.what_was_established} color="emerald" />
          <AuditBlock title="ما الذي بقي غير محلول" items={[au.what_remains_unresolved]} color="amber" />
          <AuditBlock title="ما الذي كان غير متاح" items={au.what_was_inaccessible} color="rose" />
          <AuditBlock title="أي الاستنتاجات نجت من التحقق المضاد" items={au.which_conclusions_survived_counter_evidence} color="teal" />
          <AuditBlock title="ما الذي لم يُبحث من مسارات مهمة" items={au.important_routes_not_searched} color="zinc" />
          <AuditBlock title="ما الذي قد يغيّر الاستنتاجات ماديًا" items={au.what_could_materially_change_conclusions} color="amber" />
          <AuditBlock title="قيود الأدوات المؤثرة على الاكتمال" items={au.tool_limitations_affecting_completeness} color="zinc" />
          <div className="rounded border border-zinc-800 bg-zinc-950/50 p-3 text-[11px] text-zinc-400 leading-6">
            <span className="text-zinc-300 font-medium">لماذا توقف البحث: </span>{au.why_research_stopped}
          </div>
          <div className="rounded border border-rose-900/40 bg-rose-950/10 p-3 text-[11px] text-zinc-400 leading-6">
            <span className="text-rose-300 font-medium">Transaction Verification — Not Performed: </span>
            لم تُنفَّذ أي معاملات. كل الأسعار أدلة مستوى قوائم. Advertised ≠ Transaction.
          </div>
        </CardContent>
      </Card>

      {/* Failure recovery */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">سجل الفشل والاسترداد (§19)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[10px] min-w-[720px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-start py-1.5 pe-2 font-medium">Actions</th>
                  <th className="text-start py-1.5 pe-2 font-medium">Subject</th>
                  <th className="text-start py-1.5 pe-2 font-medium">Failure</th>
                  <th className="text-start py-1.5 pe-2 font-medium">Recovery</th>
                  <th className="text-start py-1.5 font-medium">Outcome</th>
                </tr>
              </thead>
              <tbody>
                {failures.map((f, i) => (
                  <tr key={i} className="border-b border-zinc-800/40 align-top">
                    <td className="py-1.5 pe-2 font-mono text-zinc-500" dir="ltr">{f.action}</td>
                    <td className="py-1.5 pe-2 text-zinc-400">{f.sku}</td>
                    <td className="py-1.5 pe-2 text-rose-400/80 leading-4">{f.failure}</td>
                    <td className="py-1.5 pe-2 text-zinc-500 leading-4">{f.recovery}</td>
                    <td className="py-1.5 leading-4">
                      <span className={f.outcome.includes('Recovered') ? 'text-emerald-400' : 'text-amber-400'}>{f.outcome}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="text-[10px] text-zinc-600 leading-5 mt-2">
            الاسترداد لم يكن أبدًا تكرارًا مجردًا: تبديل صياغة الاستعلام أو التوقيت (cooldown) أو القناة — وكل فشل باقٍ مُصنَّف Retrieval-Limited بأمانة.
          </div>
        </CardContent>
      </Card>

      {/* Action log */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <CardTitle className="text-sm text-zinc-300">سجل إجراءات البحث الكامل ({actionsData.total_actions} إجراء — كل واحد مُخفِّض من الميزانية)</CardTitle>
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="ابحث في الاستعلامات / SKU / ID..."
              className="h-8 w-full sm:w-64 text-xs bg-zinc-950 border-zinc-800"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
            <table className="w-full text-[10px] min-w-[820px]">
              <thead className="sticky top-0 bg-zinc-900">
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-start py-1.5 pe-2 font-medium">ID</th>
                  <th className="text-start py-1.5 pe-2 font-medium">Time</th>
                  <th className="text-start py-1.5 pe-2 font-medium">Branch</th>
                  <th className="text-start py-1.5 pe-2 font-medium">SKU</th>
                  <th className="text-start py-1.5 pe-2 font-medium">Family</th>
                  <th className="text-start py-1.5 pe-2 font-medium">Query</th>
                  <th className="text-start py-1.5 font-medium">Retrieval</th>
                </tr>
              </thead>
              <tbody>
                {actions.map((a) => (
                  <tr key={a.action_id} className="border-b border-zinc-800/40 hover:bg-zinc-800/30">
                    <td className="py-1 pe-2 font-mono text-zinc-500">{a.action_id}</td>
                    <td className="py-1 pe-2 font-mono text-zinc-600" dir="ltr">{a.timestamp_utc.slice(11, 19)}</td>
                    <td className="py-1 pe-2 font-mono text-[9px] text-zinc-600" dir="ltr">{a.branch}</td>
                    <td className="py-1 pe-2 font-mono text-[9px] text-zinc-500" dir="ltr">{a.sku_id || '—'}</td>
                    <td className="py-1 pe-2 text-zinc-500 leading-4">{a.discovery_family.split('(')[0].trim()}</td>
                    <td className="py-1 pe-2 text-zinc-400 leading-4" dir="ltr">{a.query}</td>
                    <td className="py-1">
                      <span className={a.retrieval_status === 'Success' ? 'text-emerald-500' : a.retrieval_status === 'Success-Empty' ? 'text-amber-500' : 'text-rose-500'}>
                        {a.retrieval_status} ({a.result_count})
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function AuditBlock({ title, items, color }: { title: string; items: string[]; color: string }) {
  const colors: Record<string, string> = {
    emerald: 'text-emerald-400 border-emerald-900/40',
    amber: 'text-amber-400 border-amber-900/40',
    rose: 'text-rose-400 border-rose-900/40',
    teal: 'text-teal-400 border-teal-900/40',
    zinc: 'text-zinc-400 border-zinc-800',
  };
  return (
    <div className={`rounded border bg-zinc-950/40 p-3 ${colors[color]}`}>
      <div className={`text-xs font-medium mb-1.5 ${colors[color].split(' ')[0]}`}>{title}</div>
      <ul className="space-y-1">
        {items.map((x, i) => (
          <li key={i} className="text-[11px] text-zinc-400 leading-6 flex gap-2">
            <span className="text-zinc-700 shrink-0">▸</span>
            <span dir="auto">{x}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
