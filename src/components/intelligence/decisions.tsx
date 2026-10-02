'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import data from '@/lib/data/decisions-data.json';

const STATUS_STYLE: Record<string, string> = {
  done: 'border-emerald-700 bg-emerald-950/70 text-emerald-300',
  partial: 'border-amber-700 bg-amber-950/70 text-amber-300',
  open: 'border-zinc-600 bg-zinc-900 text-zinc-400',
  signable: 'border-violet-700 bg-violet-950/70 text-violet-300',
};

const STATUS_LABEL: Record<string, string> = {
  done: '✅ محسوم',
  partial: '🟡 جزئي — فعل مستخدمي متبقٍ',
  open: 'مفتوح — بيد المستخدم',
  signable: '🖋️ جاهز للتوقيع — كلمة المستخدم',
};

export function Decisions() {
  const d = data as any;
  return (
    <div className="space-y-6">
      {/* Delegation basis */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">
            حزمة القرارات المفوَّضة — {d.run_id} ({d.date})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded border border-violet-900/40 bg-violet-950/10 p-3">
            <div className="text-[10px] text-violet-400 mb-1">أساس التفويض (نص المستخدم)</div>
            <div className="text-[12px] text-zinc-300 leading-6">{d.delegation_basis}</div>
          </div>
          <div className="text-[10px] text-zinc-500 mb-1">حمايات التفويض المطبقة</div>
          {d.safeguards.map((s: string, i: number) => (
            <div key={i} className="text-[11px] text-zinc-400 leading-6 flex gap-2">
              <span className="text-emerald-600 shrink-0">✓</span>
              <span>{s}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Resolved decisions */}
      {d.decisions.map((dec: any) => (
        <Card key={dec.id} className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline" className="font-mono text-[10px] border-amber-800 bg-amber-950/50 text-amber-300">{dec.id}</Badge>
              <CardTitle className="text-sm text-zinc-100">{dec.topic}</CardTitle>
              <Badge variant="outline" className="text-[10px] border-emerald-700 bg-emerald-950/70 text-emerald-300">{dec.status}</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-2.5">
            <div className="text-[12px] text-zinc-300 leading-6">
              <span className="text-emerald-500 font-bold">الحسم: </span>{dec.resolution}
            </div>
            <div className="text-[11px] text-zinc-500 leading-6">
              <span className="text-zinc-400 font-bold">التبرير: </span>{dec.rationale}
            </div>
            <div className="rounded border border-emerald-900/40 bg-emerald-950/10 p-2.5">
              <div className="text-[10px] text-emerald-500 mb-1">الأثر</div>
              <div className="text-[11px] text-zinc-400 leading-6">{dec.impact}</div>
            </div>
            {dec.executed_now && (
              <div className="rounded border border-teal-900/40 bg-teal-950/10 p-2.5">
                <div className="text-[10px] text-teal-500 mb-1">المُنفَّذ تقنيًا في الجلسة</div>
                {dec.executed_now.map((x: string, i: number) => (
                  <div key={i} className="text-[11px] text-zinc-400 leading-5">• {x}</div>
                ))}
              </div>
            )}
            {dec.user_steps && (
              <div className="rounded border border-amber-900/40 bg-amber-950/10 p-2.5">
                <div className="text-[10px] text-amber-500 mb-1">الخطوات المتبقية بيد المستخدم (5 دقائق)</div>
                {dec.user_steps.map((x: string, i: number) => (
                  <div key={i} className="text-[11px] text-zinc-400 leading-5">{i + 1}. {x}</div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      ))}

      {/* Decisions board */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">لوحة القرارات D1–D7 بعد الحزمة</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2">
            {d.board.map((b: any) => (
              <div key={b.id} className="flex flex-wrap items-center gap-2 rounded border border-zinc-800 bg-zinc-950/40 px-2.5 py-2">
                <Badge variant="outline" className={`text-[10px] whitespace-nowrap ${STATUS_STYLE[b.status] || STATUS_STYLE.open}`}>{b.id}</Badge>
                <span className="text-[12px] text-zinc-200">{b.label}</span>
                <span className="text-[10px] text-zinc-500 leading-5">{STATUS_LABEL[b.status]} — {b.note}</span>
              </div>
            ))}
          </div>
          <div className="text-[10px] text-zinc-600 mt-2 leading-5">
            حق النقض محفوظ على كل حسم: كلمة من المستخدم تُعيد فتح البند بلا كلفة حوكمة.
          </div>
        </CardContent>
      </Card>

      {/* B2B dossier */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">ملف حسابات B2B — أعلى رافعة معلوماتية متبقية</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-[11px] text-zinc-500 leading-6">{d.b2b.why}</div>
          <div className="grid gap-2">
            {d.b2b.priority.map((p: any) => (
              <div key={p.rank} className="rounded border border-zinc-800 bg-zinc-950/40 p-2.5">
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  <Badge variant="outline" className="font-mono text-[10px] border-violet-800 bg-violet-950/50 text-violet-300">#{p.rank}</Badge>
                  <span className="text-[12px] text-zinc-100 font-bold">{p.portal}</span>
                  <span className="text-[10px] text-zinc-500">{p.type}</span>
                </div>
                <div className="text-[11px] text-zinc-400 leading-5"><span className="text-teal-500">يكشف: </span>{p.reveals}</div>
                <div className="text-[11px] text-zinc-400 leading-5"><span className="text-amber-500">الدخول: </span>{p.entry}</div>
                <div className="text-[10px] text-zinc-600 leading-5">{p.evidence}</div>
              </div>
            ))}
          </div>
          <div className="rounded border border-teal-900/40 bg-teal-950/10 p-2.5">
            <div className="text-[10px] text-teal-500 mb-1">بروتوكول الاستخراج بعد فتح أي حساب (20 دقيقة لكل بوابة)</div>
            {d.b2b.protocol.map((x: string, i: number) => (
              <div key={i} className="text-[11px] text-zinc-400 leading-5">{i + 1}. {x}</div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Resume status */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">حالة الاستئناف المؤجل (15 استعلامًا)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="text-[11px] text-zinc-400 leading-6"><span className="text-zinc-500">ترقية السكربت: </span>{d.resume_status.script_upgraded}</div>
          <div className="text-[11px] text-zinc-400 leading-6"><span className="text-zinc-500">المراقب الآلي: </span>{d.resume_status.watcher}</div>
          <div className="text-[11px] text-amber-400/90 leading-6"><span className="text-zinc-500">الحصة الآن: </span>{d.resume_status.quota_state}</div>
        </CardContent>
      </Card>
    </div>
  );
}
