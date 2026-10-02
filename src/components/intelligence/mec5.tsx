'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import data from '@/lib/data/mec5.json';

function S({ children }: { children: React.ReactNode }) {
  return <span className="font-mono text-emerald-400" dir="ltr">{children}</span>;
}

const statusStyle: Record<string, string> = {
  confirmed: 'border-emerald-800 bg-emerald-950/50 text-emerald-300',
  partial: 'border-amber-800 bg-amber-950/50 text-amber-300',
  hidden: 'border-cyan-800 bg-cyan-950/50 text-cyan-300',
  inquiry: 'border-zinc-700 bg-zinc-900 text-zinc-300',
  none: 'border-zinc-800 bg-zinc-950 text-zinc-500',
};
const statusLabel: Record<string, string> = {
  confirmed: 'موثق ✅', partial: 'جزئي ⚠️', hidden: 'خلف دخول', inquiry: 'بالتسعير', none: 'لا فجوة',
};

export function Mec5() {
  const d = data as any;
  const ps = d.prodseller;
  const sv = d.stackvault;
  const kg = d.kinguin;
  const tg = d.turgame;
  const rl = d.reloadly;

  return (
    <div className="space-y-6">
      {/* ═══ Run header ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-violet-800 bg-violet-950/50 text-violet-300">MEC-5.0 API-GAP</Badge>
            <CardTitle className="text-sm text-zinc-100">💳 كشف فجوات أسعار API — من يبيع بسعرين مختلفين؟ وبكم بالضبط؟</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center">
            {[
              { n: '12', l: 'مزودًا تم فحصه', c: 'text-violet-300' },
              { n: '4', l: 'بفجوة سعرية API مؤكدة', c: 'text-emerald-400' },
              { n: `${d.headline_stats.prodseller_rows}`, l: 'صف أسعار مزدوجة ProdSeller', c: 'text-rose-300' },
              { n: '274', l: 'منتج StackVault بتكلفة مكشوفة', c: 'text-amber-300' },
              { n: '19.9%', l: 'أعلى فجوة متوسط (StackVault)', c: 'text-cyan-400' },
            ].map((s, i) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className={`text-lg font-bold font-mono ${s.c}`}>{s.n}</div>
                <div className="text-[10px] text-zinc-500 leading-4">{s.l}</div>
              </div>
            ))}
          </div>
          <div className="rounded border border-violet-900/40 bg-violet-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            <b className="text-violet-300">المهمة المنجزة:</b> تحويل «أسعار الجملة المخفية عبر API» من مجهول إلى معلوم موثق. كل الأدلة علنية ومشروعة: أرشيف قناة ProdSeller (79 منشورًا) + صور رسمية من داخل المنصة + وثائق API المنشورة + 274 منتجًا بتكلفة مكشوفة من StackVault + مثال Kinguin الرسمي + 225 صفًا مطابقًا من Turgame. لا رقم واحد بلا مصدر وتاريخ.
          </div>
        </CardContent>
      </Card>

      {/* ═══ 1. Master verdicts ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-emerald-800 bg-emerald-950/50 text-emerald-300">الجدول الحاكم</Badge>
            <CardTitle className="text-sm text-zinc-100">🏆 12 مزودًا — من منهم يقدم فعلًا سعرًا مختلفًا في API؟</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px] border-collapse">
              <thead>
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="p-2 text-right">المزود</th>
                  <th className="p-2 text-right">برنامج API</th>
                  <th className="p-2 text-right">الفجوة المكتشفة</th>
                  <th className="p-2 text-right">حجم الدليل</th>
                  <th className="p-2 text-right">الوصول</th>
                  <th className="p-2 text-right">الحكم</th>
                  <th className="p-2 text-right">الحالة</th>
                </tr>
              </thead>
              <tbody>
                {d.verdicts.map((v: any, i: number) => (
                  <tr key={i} className="border-b border-zinc-800/60 hover:bg-zinc-900/40">
                    <td className="p-2 font-bold text-zinc-100" dir="ltr">{v.provider}</td>
                    <td className="p-2 text-zinc-300">{v.api}</td>
                    <td className="p-2 font-mono text-amber-300" dir="ltr">{v.gap}</td>
                    <td className="p-2 text-zinc-400">{v.n}</td>
                    <td className="p-2 text-zinc-400 text-[10px]">{v.access}</td>
                    <td className="p-2 text-zinc-300">{v.verdict}</td>
                    <td className="p-2">
                      <span className={`rounded border px-1.5 py-0.5 text-[10px] font-mono ${statusStyle[v.status] || statusStyle.none}`}>{statusLabel[v.status] || v.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 rounded border border-emerald-900/40 bg-emerald-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            <b className="text-emerald-300">الإجابة الحاسمة على سؤالك:</b> أربعة فقط من أصل 12 يقدمون فجوة سعرية API حقيقية موثقة: <b>StackVault (19.9%)</b> · <b>ProdSeller (12.0%)</b> · <b>Kinguin (5–10.2% كمية)</b> · <b>Reloadly (2–10% منشور)</b>. Turgame أرضيته العلنية ~1% فقط وخصوماته الحقيقية مخفية. البقية: إما لا فجوة شرائية (Z2U/GamsGo/U7BUY/Bitrefill) أو بالتسعير الاستفساري فقط (SEAGM/OffGamers).
          </div>
        </CardContent>
      </Card>

      {/* ═══ 2. ProdSeller ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-rose-800 bg-rose-950/50 text-rose-300">الأولوية 1</Badge>
            <CardTitle className="text-sm text-zinc-100">🤖 ProdSeller — 38 صفًا مؤرخًا بأسعار مزدوجة/ثلاثية (عام / API / جملة)</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* structural evidence */}
          <div className="rounded border border-rose-900/40 bg-rose-950/10 p-3 space-y-1.5 text-[11px] text-zinc-300 leading-6">
            <div className="text-rose-300 font-bold mb-1">🔬 الأدلة الهيكلية الأربعة (الفجوة مصمَّمة في المنصة نفسها):</div>
            {(Object.entries(ps.structural_evidence) as [string, string][]).map(([k, v]) => (
              <div key={k} className="flex gap-2"><span className="text-zinc-500">▪</span><span>{v}</span></div>
            ))}
          </div>

          {/* gap stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
            {[
              { n: `${ps.summary.api_gap_pct.min}%`, l: 'أدنى فجوة API (ChatGPT K12)' },
              { n: `${ps.summary.api_gap_pct.median}%`, l: 'الوسيط (النمط الغالب)' },
              { n: `${ps.summary.api_gap_pct.avg}%`, l: 'المتوسط' },
              { n: `${ps.summary.api_gap_pct.max}%`, l: 'أقصى فجوة (Office 365 Plus: 0.29→0.17)' },
            ].map((s, i) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className="text-base font-bold font-mono text-rose-300">{s.n}</div>
                <div className="text-[10px] text-zinc-500 leading-4">{s.l}</div>
              </div>
            ))}
          </div>

          {/* latest per product table */}
          <div>
            <div className="text-[12px] font-bold text-zinc-100 mb-2">📋 أحدث سعر لكل منتج (25 منتجًا — الأحدث من الأرشيف يفوز)</div>
            <div className="overflow-x-auto max-h-96 overflow-y-auto rounded border border-zinc-800">
              <table className="w-full text-[11px] border-collapse">
                <thead className="sticky top-0 bg-zinc-900">
                  <tr className="border-b border-zinc-700 text-zinc-400">
                    <th className="p-2 text-right">المنتج</th>
                    <th className="p-2">العام $</th>
                    <th className="p-2">API $</th>
                    <th className="p-2">جملة $</th>
                    <th className="p-2">الفجوة</th>
                    <th className="p-2">التاريخ</th>
                  </tr>
                </thead>
                <tbody>
                  {ps.latest_per_product.map((r: any, i: number) => (
                    <tr key={i} className="border-b border-zinc-800/60 hover:bg-zinc-900/40">
                      <td className="p-2 text-zinc-200" dir="ltr">{r.product}</td>
                      <td className="p-2 text-center font-mono text-zinc-300">{r.public}</td>
                      <td className="p-2 text-center font-mono text-emerald-400">{r.api ?? '—'}</td>
                      <td className="p-2 text-center font-mono text-cyan-300">{r.bulk ?? '—'}</td>
                      <td className="p-2 text-center font-mono text-amber-300">{r.gap != null ? `${r.gap}%` : '—'}</td>
                      <td className="p-2 text-center font-mono text-zinc-500" dir="ltr">{r.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ═══ 3. StackVault ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-amber-800 bg-amber-950/50 text-amber-300">الأولوية 2</Badge>
            <CardTitle className="text-sm text-zinc-100">📦 StackVault — 274 منتجًا بحقل تكلفة مكشوف (price مقابل costPrice)</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center">
            {[
              { n: `${sv.summary.gap_pct.min}%`, l: 'أدنى فجوة' },
              { n: `${sv.summary.gap_pct.median}%`, l: 'الوسيط' },
              { n: `${sv.summary.gap_pct.avg}%`, l: 'المتوسط' },
              { n: `${sv.summary.gap_pct.max}%`, l: 'الأقصى (Apple Music 5M: 2.35←1.00)' },
              { n: '2.35x', l: 'أعلى مضاعف (Apple Music)' },
            ].map((s, i) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className="text-base font-bold font-mono text-amber-300">{s.n}</div>
                <div className="text-[10px] text-zinc-500 leading-4">{s.l}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <div>
              <div className="text-[12px] font-bold text-zinc-100 mb-2">🔺 أعلى 15 فجوة (بيع / تكلفة)</div>
              <div className="overflow-x-auto max-h-80 overflow-y-auto rounded border border-zinc-800">
                <table className="w-full text-[11px] border-collapse">
                  <thead className="sticky top-0 bg-zinc-900">
                    <tr className="border-b border-zinc-700 text-zinc-400">
                      <th className="p-2 text-right">المنتج</th>
                      <th className="p-2">بيع</th>
                      <th className="p-2">تكلفة</th>
                      <th className="p-2">فجوة</th>
                      <th className="p-2">x</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sv.top_gap.map((r: any, i: number) => (
                      <tr key={i} className="border-b border-zinc-800/60 hover:bg-zinc-900/40">
                        <td className="p-2 text-zinc-200 truncate max-w-[220px]" dir="ltr">{r.product}</td>
                        <td className="p-2 text-center font-mono text-zinc-300">{r.price}</td>
                        <td className="p-2 text-center font-mono text-emerald-400">{r.cost}</td>
                        <td className="p-2 text-center font-mono text-amber-300">{r.gap}%</td>
                        <td className="p-2 text-center font-mono text-cyan-300">{r.x}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="space-y-3">
              <div>
                <div className="text-[12px] font-bold text-zinc-100 mb-2">🔻 أدنى 5 فجوة (الأقرب للتكلفة)</div>
                <table className="w-full text-[11px] border-collapse rounded border border-zinc-800">
                  <tbody>
                    {sv.bottom_gap.map((r: any, i: number) => (
                      <tr key={i} className="border-b border-zinc-800/60">
                        <td className="p-2 text-zinc-200 truncate max-w-[200px]" dir="ltr">{r.product}</td>
                        <td className="p-2 text-center font-mono text-zinc-300">{r.price}</td>
                        <td className="p-2 text-center font-mono text-emerald-400">{r.cost}</td>
                        <td className="p-2 text-center font-mono text-amber-300">{r.gap}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="rounded border border-zinc-800 bg-zinc-950/60 p-3">
                <div className="text-[11px] font-bold text-zinc-200 mb-1.5">📊 الفجوة حسب الفئة (274 منتجًا)</div>
                {(Object.entries(sv.summary.by_category) as [string, any][]).map(([cat, s]) => (
                  <div key={cat} className="flex items-center gap-2 mb-1.5">
                    <span className="text-[10px] text-zinc-400 w-32 truncate" dir="ltr">{cat}</span>
                    <div className="flex-1 h-2 bg-zinc-800 rounded overflow-hidden">
                      <div className="h-full bg-amber-500/70" style={{ width: `${Math.min(100, Number(s.avg_gap_pct) * 2)}%` }} />
                    </div>
                    <span className="text-[10px] font-mono text-amber-300 w-24 text-left" dir="ltr">n={s.n} · {s.avg_gap_pct}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ═══ 4. Kinguin + Turgame + Reloadly ═══ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-zinc-100">🎮 Kinguin — طبقات الجملة الكمية (مثال رسمي)</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            <table className="w-full text-[11px] border-collapse">
              <thead><tr className="border-b border-zinc-700 text-zinc-400"><th className="p-1.5">الكمية</th><th className="p-1.5">السعر</th><th className="p-1.5">الخصم</th></tr></thead>
              <tbody>
                {kg.example_tiers.map((t: any, i: number) => (
                  <tr key={i} className="border-b border-zinc-800/60">
                    <td className="p-1.5 text-center font-mono text-zinc-300" dir="ltr">{t.qty}</td>
                    <td className="p-1.5 text-center font-mono text-zinc-200" dir="ltr">${t.price}</td>
                    <td className="p-1.5 text-center font-mono text-emerald-400" dir="ltr">{t.gap}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="text-[10px] text-zinc-500 leading-5">{kg.note}</div>
            <div className="text-[10px] text-zinc-400 leading-5">🔓 الوصول: {kg.access}</div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-zinc-100">🇹🇷 Turgame — بوابة الجملة وأرضية الكتالوج</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-[11px] text-zinc-300 leading-6">
            <div>البوابة: <S>wholesale.turgame.com</S> — 4,739 SKU عبر Store API علني بلا دخول.</div>
            <div>225 منتجًا مطابقًا: أرضية الفجوة <b className="font-mono text-amber-300">{tg.catalog_floor_gap.avg}%</b> متوسط (المدى {tg.catalog_floor_gap.range}).</div>
            <div>الطبقات: {tg.tiers}.</div>
            <div className="text-zinc-400 text-[10px]">{tg.supply_note}</div>
            <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2 space-y-1">
              {tg.sample_rows.map((r: any, i: number) => (
                <div key={i} className="flex justify-between gap-2 text-[10px]">
                  <span className="text-zinc-300" dir="ltr">{r.product}</span>
                  <span className="font-mono text-amber-300" dir="ltr">{r.gap}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-zinc-100">📡 Reloadly — الخصم المنشور لكل علامة</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-[11px] text-zinc-300 leading-6">
            <div>النموذج: {rl.model}.</div>
            <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2 space-y-1">
              {rl.doc_samples.map((s: any, i: number) => (
                <div key={i} className="flex justify-between gap-2 text-[10px]">
                  <span className="text-zinc-300" dir="ltr">{s.brand}</span>
                  <span className="font-mono text-emerald-400" dir="ltr">-{s.discount}%</span>
                </div>
              ))}
            </div>
            <div className="text-zinc-400 text-[10px]">الوصول: {rl.access}.</div>
            <div className="text-[10px] text-zinc-500 leading-5">DingConnect يخفي نفس البنية خلف دخول مجاني · Bitrefill بلا فجوة (revenue share بدلها).</div>
          </CardContent>
        </Card>
      </div>

      {/* ═══ 5. Leaderboard + next moves ═══ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-zinc-100">🏆 لوحة صدارة فجوات API</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {d.leaderboard.map((l: any, i: number) => (
              <div key={i} className="flex items-center gap-2">
                <span className="text-[11px] text-zinc-400 w-5 font-mono">{i + 1}.</span>
                <span className="text-[11px] text-zinc-200 w-28" dir="ltr">{l.provider}</span>
                <div className="flex-1 h-3 bg-zinc-800 rounded overflow-hidden">
                  <div className={`h-full ${l.color === 'rose' ? 'bg-rose-500/70' : l.color === 'amber' ? 'bg-amber-500/70' : l.color === 'emerald' ? 'bg-emerald-500/70' : l.color === 'cyan' ? 'bg-cyan-500/70' : 'bg-zinc-500/70'}`} style={{ width: `${Math.min(100, parseFloat(l.gap) * 5)}%` }} />
                </div>
                <span className="text-[11px] font-mono text-amber-300 w-24 text-left" dir="ltr">{l.gap}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-zinc-100">🎯 الخطوات التالية الجاهزة (بيدك)</CardTitle></CardHeader>
          <CardContent>
            <ol className="space-y-1.5">
              {d.next_moves.map((m: string, i: number) => (
                <li key={i} className="text-[11px] text-zinc-300 leading-6 rounded border border-zinc-800 bg-zinc-950/50 px-3 py-1.5">{m}</li>
              ))}
            </ol>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
