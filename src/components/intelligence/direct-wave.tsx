'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import data from '@/lib/data/direct-wave.json';

export function DirectWave() {
  const d = data as any;
  return (
    <div className="space-y-6">
      {/* Central discovery */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-cyan-800 bg-cyan-950/50 text-cyan-300">{d.run_id}</Badge>
            <CardTitle className="text-sm text-zinc-100">🔬 الموجة المباشرة — {d.date}</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-[11px] text-zinc-400 leading-6">{d.method}</div>
          <div className="rounded border border-cyan-900/40 bg-cyan-950/10 p-3">
            <div className="text-[10px] text-cyan-400 mb-1">الاكتشاف المركزي</div>
            <div className="text-[12px] text-zinc-200 leading-7">{d.central_discovery.title} — <span dir="ltr" className="font-mono text-cyan-300">{d.central_discovery.endpoint}</span></div>
            <div className="mt-2 grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
              <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className="text-lg font-bold text-emerald-400 font-mono">{d.central_discovery.products}</div>
                <div className="text-[10px] text-zinc-500">منتجًا في الكتالوج</div>
              </div>
              <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className="text-lg font-bold text-emerald-400 font-mono">{d.central_discovery.with_cost}</div>
                <div className="text-[10px] text-zinc-500">بحقل كلفة مكشوف</div>
              </div>
              <div className="rounded border border-emerald-900/50 bg-emerald-950/30 p-2">
                <div className="text-[13px] font-bold text-emerald-300 leading-5">{d.central_discovery.formula}</div>
                <div className="text-[10px] text-zinc-500">معادلة التسعير</div>
              </div>
              <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className="text-lg font-bold text-emerald-400 font-mono">{d.central_discovery.margin_median_pct}%</div>
                <div className="text-[10px] text-zinc-500">هامش وسيط (المدى {d.central_discovery.margin_range})</div>
              </div>
            </div>
            <div className="mt-2 text-[11px] text-zinc-400 leading-6">{d.central_discovery.interpretation}</div>
          </div>
        </CardContent>
      </Card>

      {/* ChatGPT Plus cost ladder */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">🪜 سلّم كلفة ChatGPT Plus حسب الضمان — لأول مرة بالكلفة لا بالأسعار</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-right py-2 px-2">الطبقة</th>
                  <th className="text-right py-2 px-2">كلفة الجملة</th>
                  <th className="text-right py-2 px-2">سعر التجزئة</th>
                  <th className="text-right py-2 px-2">القراءة</th>
                </tr>
              </thead>
              <tbody>
                {d.chatgpt_plus_cost_ladder.map((t: any, i: number) => (
                  <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-900/40">
                    <td className="py-2 px-2 text-zinc-200">{t.tier}</td>
                    <td className="py-2 px-2 font-mono text-amber-300" dir="ltr">${t.cost.toFixed(2)}</td>
                    <td className="py-2 px-2 font-mono text-zinc-300" dir="ltr">${t.retail.toFixed(2)}</td>
                    <td className="py-2 px-2 text-zinc-500">{t.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-2 text-[11px] text-zinc-400 leading-6">
            «نفس المنتج» = <span className="text-amber-300 font-bold">فارق 6 أضعاف كلفة</span> بين طبقاته — إعلان «خصم 85%» يقابله سلّم هشاشة/جودة كامل.
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Solved examples */}
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-100">🧮 أمثلة محلولة [كلفة ← بيع] (StackVault API)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1.5">
              {d.solved_examples.map((e: any, i: number) => (
                <div key={i} className="flex items-center justify-between gap-2 text-[11px] border-b border-zinc-800/50 pb-1.5">
                  <span className="text-zinc-300">{e.product}</span>
                  <span className="font-mono text-zinc-400 shrink-0" dir="ltr">
                    <span className="text-amber-300">${e.cost.toFixed(2)}</span>
                    <span className="text-zinc-600 mx-1">→</span>
                    <span className="text-emerald-400">${e.price.toFixed(2)}</span>
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Live spreads */}
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-100">📈 قياسات حية للانتشار جملة ← تجزئة</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2.5">
              {d.live_spreads.map((s: any, i: number) => (
                <div key={i} className="rounded border border-zinc-800 bg-zinc-950/40 p-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[12px] text-zinc-200">{s.item}</span>
                    <Badge variant="outline" className="font-mono text-[10px] border-emerald-800 bg-emerald-950/60 text-emerald-300">+{s.spread_pct}%</Badge>
                  </div>
                  <div className="mt-1 font-mono text-[10px] text-zinc-500" dir="ltr">
                    ${s.wholesale.toFixed(2)} → ${s.retail ?? s.retail_cost} {s.retail_cost ? '(cost)' : ''}
                  </div>
                  <div className="mt-0.5 text-[10px] text-zinc-500 leading-5">{s.note}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Anchor prices */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">🎯 أثمن مباشرة جديدة (مستوى «مرصود مباشرة»)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-right py-2 px-2">البند</th>
                  <th className="text-right py-2 px-2">الثمن</th>
                  <th className="text-right py-2 px-2">الدليل / السياق</th>
                </tr>
              </thead>
              <tbody>
                {d.anchor_prices.map((a: any, i: number) => (
                  <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-900/40">
                    <td className="py-2 px-2 text-zinc-200">{a.item}</td>
                    <td className="py-2 px-2 font-mono text-emerald-300 whitespace-nowrap" dir="ltr">{a.price}</td>
                    <td className="py-2 px-2 text-zinc-500">{a.evidence}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Batch 3 status + limitations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-100">⚙️ حالة الدفعة 3 (218 P3)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid grid-cols-2 gap-2 text-center mb-2">
              <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className="text-lg font-bold text-cyan-400 font-mono">{d.batch3_status.queries_planned}</div>
                <div className="text-[10px] text-zinc-500">استعلامًا جاهزًا</div>
              </div>
              <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className="text-lg font-bold text-cyan-400 font-mono">218/218</div>
                <div className="text-[10px] text-zinc-500">تغطية SKU (صفر نواقص)</div>
              </div>
            </div>
            <div className="text-[11px] text-zinc-400 leading-6">
              <div><span className="text-amber-400 font-bold">الأولوية عند فتح الحصة: </span>{d.batch3_status.deferred_b2}</div>
              <div><span className="text-emerald-400 font-bold">المراقب: </span>{d.batch3_status.watcher}</div>
              <div><span className="text-zinc-300 font-bold">الحالة: </span>{d.batch3_status.state}</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-100">⚠️ حدود صادقة للموجة</CardTitle>
          </CardHeader>
          <CardContent>
            {d.limitations.map((l: string, i: number) => (
              <div key={i} className="text-[11px] text-zinc-400 leading-6 flex gap-2">
                <span className="text-amber-600 shrink-0">•</span>
                <span>{l}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
