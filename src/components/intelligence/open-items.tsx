'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { runData } from '@/lib/data';
import { statusBadge } from './shared';

export function OpenItems() {
  const hyps = runData.open_hypotheses as any[];
  const unresolved = runData.unresolved_claims as string[];
  const ex = runData.exclusion_screen as any;
  return (
    <div className="space-y-6">
      {/* Hypotheses */}
      <div className="space-y-3">
        <div className="text-xs text-zinc-500 leading-6 px-1">
          الفرضيات المتنافسة تُدار بالتوازي ولا تُحل إلا بالدليل. الفرضية التي استُنفدت ميزانيتها تبقى Unresolved — لا تُحل بالإهمال (§17).
        </div>
        {hyps.map((h) => (
          <Card key={h.id} className="bg-zinc-900/60 border-zinc-800">
            <CardHeader className="pb-2">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline" className="font-mono text-[10px] border-amber-800 bg-amber-950/50 text-amber-300">{h.id}</Badge>
                <CardTitle className="text-sm text-zinc-100 leading-6" dir="ltr">{h.statement}</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2.5">
              {statusBadge(h.status)}
              <div className="grid sm:grid-cols-2 gap-3">
                <div className="rounded border border-emerald-900/40 bg-emerald-950/10 p-2.5">
                  <div className="text-[10px] text-emerald-500 mb-1">الأدلة الداعمة</div>
                  {h.supporting.map((s: string, i: number) => (
                    <div key={i} className="text-[11px] text-zinc-400 leading-5">• {s}</div>
                  ))}
                </div>
                <div className="rounded border border-rose-900/40 bg-rose-950/10 p-2.5">
                  <div className="text-[10px] text-rose-500 mb-1">الأدلة المعارضة</div>
                  {h.contradicting.map((c: string, i: number) => (
                    <div key={i} className="text-[11px] text-zinc-400 leading-5">• {c}</div>
                  ))}
                </div>
              </div>
              <div className="text-[10px] text-zinc-600 leading-5">
                الإجراءات التالية: {h.next_actions.join(' · ')}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Unresolved claims */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">الادعاءات المادية غير المحلولة ({unresolved.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-1.5">
            {unresolved.map((c, i) => (
              <li key={i} className="text-[11px] text-zinc-400 leading-6 flex gap-2">
                <span className="text-amber-600 shrink-0">◌</span>
                <span dir="ltr">{c}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Exclusion screen */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">شاشة الاستبعاد / النشاط غير المصرح (§10)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-[11px] text-zinc-500 leading-6">
            البروتوكول: Signal → Supporting Evidence → Classification → Action. الإشارة دون دليل كافٍ تبقى حالة مراجعة — ليست اتهامًا أبدًا.
          </div>
          <div className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
            <div className="text-xs text-zinc-300 mb-1">Excluded-Confirmed: <span className="text-emerald-400">لا شيء هذا التشغيل</span></div>
            <div className="text-[10px] text-zinc-600 leading-5">
              لم يُلتقط دليل مباشر على بيانات مسروقة أو تجاوز OTP أو وصول مقصوص — حالة صادقة: الشاشة فُتحت، إشارات سُجلت، لا شيء مؤكد.
            </div>
          </div>
          {ex.excluded_suspected_needs_review.map((s: any, i: number) => (
            <div key={i} className="rounded border border-amber-900/40 bg-amber-950/10 p-3">
              <div className="text-xs text-amber-300 mb-1.5">{s.subject}</div>
              <div className="text-[11px] text-zinc-400 leading-6">الإشارة: {s.signal}</div>
              <div className="text-[11px] text-zinc-500 leading-6">التصنيف: <span className="text-amber-400">{s.classification}</span></div>
              <div className="text-[11px] text-zinc-500 leading-6">الإجراء: {s.action}</div>
            </div>
          ))}
          {ex.not_excluded_with_flags.map((s: any, i: number) => (
            <div key={i} className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
              <div className="text-xs text-zinc-300 mb-1">{s.subject}</div>
              <div className="text-[11px] text-zinc-500 leading-6">⟲ {s.flag}</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
