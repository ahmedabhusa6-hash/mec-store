'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useState } from 'react';
import data from '@/lib/data/channel-matrix.json';

export function ChannelMatrix() {
  const d = data as any;
  const [q, setQ] = useState('');
  const [lay, setLay] = useState('');
  const layers = Array.from(new Set((d.channels as any[]).map((c) => c.layer)));

  const filtered = (d.channels as any[]).filter(
    (c) =>
      (!q || JSON.stringify(c).includes(q)) &&
      (!lay || c.layer.includes(lay))
  );

  const anchor = (a: number | null) =>
    a === null ? <span className="text-zinc-600">—</span> : <span className="font-mono text-emerald-400">${a}</span>;

  return (
    <div className="space-y-6">
      {/* Header + totals */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-amber-800 bg-amber-950/50 text-amber-300">MEC-2.4</Badge>
            <CardTitle className="text-sm text-zinc-100">🧮 مصفوفة 91 قناة + الهندسة العكسية لنموذج «دولا»</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
            {[
              { n: d.totals.all, l: 'إجمالي القنوات المصنفة', c: 'text-amber-300' },
              { n: d.totals.registry, l: 'كيان سجل §19 (كلها حية)', c: 'text-emerald-400' },
              { n: d.totals.discovered, l: 'مكتشفات جديدة (API خلفي…)', c: 'text-cyan-400' },
              { n: d.totals.marketplaces, l: 'قناة سوق/رسمية بالعروض', c: 'text-sky-400' },
            ].map((s, i) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className={`text-lg font-bold font-mono ${s.c}`}>{s.n}</div>
                <div className="text-[10px] text-zinc-500">{s.l}</div>
              </div>
            ))}
          </div>
          <div className="rounded border border-amber-900/40 bg-amber-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            <b className="text-amber-300">الحكم المركب:</b> {d.verdict}. معادلة المتجر المنظم المرصودة: <span dir="ltr" className="font-mono text-amber-300">{d.sv_formula.formula}</span> (n={d.sv_formula.n}، وسيط {d.sv_formula.median_markup_pct}%).
          </div>
        </CardContent>
      </Card>

      {/* Hypotheses tree */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">🌳 شجرة فرضيات التزويد — مرجّحة بالأدلة المرصودة</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {(d.hypotheses as any[]).map((h, i) => (
            <div key={i} className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <Badge variant="outline" className="text-[10px] border-emerald-800 bg-emerald-950/40 text-emerald-300">{h.h}</Badge>
                <span className="text-[10px] text-zinc-500">الاستدامة: {h.sustain}</span>
              </div>
              <div className="text-[11px] text-zinc-300 leading-6">
                <b className="text-zinc-100">الآلية:</b> {h.mech} — <b className="text-zinc-100">الدليل:</b> <span className="text-emerald-300/90">{h.evidence}</span> — <b className="text-zinc-100">يغطي:</b> {h.covers}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Margin calculator */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">🧮 حاسبة الهامش العكسي — أرضيات التوريد المرصودة</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-right py-2">المنتج المرسي</th>
                  <th className="text-right py-2">أرضية التوريد</th>
                  <th className="text-right py-2">طبقة «مستقرة»</th>
                  <th className="text-right py-2">الرسمي</th>
                </tr>
              </thead>
              <tbody>
                {(d.margin_calc as any[]).map((m, i) => (
                  <tr key={i} className="border-b border-zinc-900">
                    <td className="py-2 text-zinc-200">{m.product}</td>
                    <td className="py-2 font-mono text-emerald-400" dir="ltr">{m.floor}</td>
                    <td className="py-2 font-mono text-amber-300" dir="ltr">{m.stable}</td>
                    <td className="py-2 font-mono text-zinc-400" dir="ltr">{m.official}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-2 text-[10px] text-zinc-500 leading-5">
            قانون الأرضيات: من يعرض تحت هذه الأرضيات بإطراد = هوية SKU مختلفة (مشاركة لا خاصة) أو حرق رأس مال أو احتيال منظم — الأنماط الثلاثة موثقة في السجل.
          </div>
        </CardContent>
      </Card>

      {/* Interactive matrix */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">📋 المصفوفة التفاعلية — 34 كيانًا رماديًا (سجل §19 + المكتشفات)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="🔍 ابحث: كيان / طبقة / دور…"
              className="flex-1 min-w-48 rounded border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-emerald-800"
            />
            <select
              value={lay}
              onChange={(e) => setLay(e.target.value)}
              className="rounded border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-emerald-800"
            >
              <option value="">كل الطبقات</option>
              {layers.map((l) => (
                <option key={l as string} value={l as string}>{l as string}</option>
              ))}
            </select>
            <span className="text-[10px] text-zinc-500 self-center">عرض {filtered.length} / {d.channels.length}</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-[10.5px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-right py-2">الكيان</th>
                  <th className="text-right py-2">النوع</th>
                  <th className="text-right py-2">الطبقة</th>
                  <th className="text-right py-2">الخطر</th>
                  <th className="text-right py-2">مرساة $</th>
                  <th className="text-right py-2">الملاءمة لنموذج دولا</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((c, i) => (
                  <tr key={i} className="border-b border-zinc-900 hover:bg-zinc-900/40">
                    <td className="py-1.5 font-mono text-cyan-300" dir="ltr">{c.id}</td>
                    <td className="py-1.5 text-zinc-400">{c.type}</td>
                    <td className="py-1.5 text-zinc-300">{c.layer}</td>
                    <td className="py-1.5 text-zinc-500 max-w-40 truncate" title={c.risk}>{c.risk}</td>
                    <td className="py-1.5">{anchor(c.anchor)}</td>
                    <td className="py-1.5 text-zinc-400 max-w-72">{c.fit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="text-[10px] text-zinc-500 leading-5">⚠️ {d.limits}</div>
        </CardContent>
      </Card>
    </div>
  );
}
