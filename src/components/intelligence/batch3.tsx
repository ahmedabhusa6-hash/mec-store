'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import data from '@/lib/data/batch3-data.json';

export function Batch3() {
  const d = data as any;
  return (
    <div className="space-y-6">
      <Card className="bg-zinc-900/60 border-emerald-900/50">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-emerald-800 bg-emerald-950/50 text-emerald-300">MEC-3.0 FINAL</Badge>
            <CardTitle className="text-sm text-zinc-100">🎯 الدفعة 3 (218 P3) + اكتمال الكتالوج 437/437 + الترقية التاريخية</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded border border-emerald-900/50 bg-emerald-950/20 p-3 text-[11px] text-emerald-200 leading-6">
            🏆 <b>v4.2 = Approved</b> — أول نسخة معتمدة في تاريخ المشروع. قاعدة الاستثناء التأسيسي D1: السلالة + المراجعات + الاختبار الحي ثلاثي الدفعات (46/142 · 173/130 · 218/143 إجراءً) + تصريح المستخدم الصريح «اعتمد كل شي». البوابة تُغلق نهائيًا.
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center">
            {[
              { n: '437/437', l: 'SKU مغطاة (كل الكتالوج)', c: 'text-emerald-300' },
              { n: '415', l: 'إجراءً موثقًا', c: 'text-sky-300' },
              { n: '42', l: 'عرضًا مرصودًا مباشرة', c: 'text-amber-300' },
              { n: '91', l: 'قناة مصنفة (5 طبقات)', c: 'text-cyan-300' },
              { n: '143/143', l: 'نجاح الدفعة 3 بلا إخفاق', c: 'text-emerald-400' },
            ].map((s, i) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className={`text-base font-bold font-mono ${s.c}`}>{s.n}</div>
                <div className="text-[9px] text-zinc-500">{s.l}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">📊 توزيع حالات الـ218 SKU بعد التنقيح اليدوي</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center">
            {Object.entries(d.states).map(([k, v]: [string, any]) => (
              <div key={k} className="rounded border border-zinc-800 bg-zinc-950/50 p-2">
                <div className="text-lg font-bold text-zinc-200 font-mono">{v}</div>
                <div className="text-[9px] text-zinc-500 leading-4">
                  {k === 'direct_observed_preseeded' ? 'عروض مباشرة (موجات MEC-2.5)' :
                   k === 'channel_advertised' ? 'عروض قنوات معتمدة منقحة' :
                   k === 'official_baseline' ? 'خطوط رسمية موثقة' :
                   k === 'advertised_lead_only' ? 'Lead فقط' : 'ضجيج موثق (لا محذوف)'}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3 space-y-1.5">
            {(d.key_findings as string[]).map((f, i) => (
              <div key={i} className="text-[10.5px] text-zinc-400 leading-5 border-r-2 border-emerald-900/60 pr-2">
                {f}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">✅ عروض القنوات المعتمدة المنقّحة (11)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[10.5px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-right py-2">SKU</th><th className="text-right py-2">البائع</th>
                  <th className="text-right py-2">المنتج</th><th className="text-right py-2">USD</th>
                  <th className="text-right py-2">ملاحظة</th>
                </tr>
              </thead>
              <tbody>
                {(d.channel_offers as any[]).map((o, i) => (
                  <tr key={i} className="border-b border-zinc-900 hover:bg-zinc-900/40">
                    <td className="py-1.5 font-mono text-cyan-300" dir="ltr">{o.sku}</td>
                    <td className="py-1.5 text-zinc-300">{o.seller}</td>
                    <td className="py-1.5 text-zinc-400 max-w-52 truncate" title={o.product}>{o.product}</td>
                    <td className="py-1.5 font-mono text-emerald-400">${o.usd}</td>
                    <td className="py-1.5 text-zinc-500 max-w-56">{o.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">🏛️ الخطوط الرسمية الموثقة (8)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[10.5px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-right py-2">SKU</th><th className="text-right py-2">المصدر</th>
                  <th className="text-right py-2">USD</th><th className="text-right py-2">ملاحظة</th>
                </tr>
              </thead>
              <tbody>
                {(d.official_baselines as any[]).map((o, i) => (
                  <tr key={i} className="border-b border-zinc-900 hover:bg-zinc-900/40">
                    <td className="py-1.5 font-mono text-cyan-300" dir="ltr">{o.sku}</td>
                    <td className="py-1.5 text-zinc-300">{o.seller}</td>
                    <td className="py-1.5 font-mono text-amber-300">${o.usd}</td>
                    <td className="py-1.5 text-zinc-500">{o.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 text-[10px] text-zinc-500 leading-5">
            ⚠️ {(d.limitations as string[]).join(' · ')}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
