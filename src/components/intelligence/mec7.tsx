'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import data from '@/lib/data/mec7.json';

const M = ({ v, c = 'text-emerald-400' }: { v: any; c?: string }) => (
  <span className={`font-mono ${c}`} dir="ltr">{v == null ? '—' : `$${Number(v).toFixed(2)}`}</span>
);

const fragStyle: Record<string, string> = {
  stable: 'border-emerald-800 bg-emerald-950/50 text-emerald-300',
  medium: 'border-amber-800 bg-amber-950/50 text-amber-300',
  fragile: 'border-rose-800 bg-rose-950/50 text-rose-300',
};
const fragLabel: Record<string, string> = { stable: 'مستقر', medium: 'متوسط', fragile: 'هش' };

const tierColor: Record<string, string> = {
  'T1 — ابدأ الآن': 'border-emerald-700 bg-emerald-950/60 text-emerald-300',
  'T1.5 — احتياط': 'border-teal-800 bg-teal-950/50 text-teal-300',
  'T2 — توسع': 'border-cyan-800 bg-cyan-950/50 text-cyan-300',
  'T3 — خلف بوابات': 'border-zinc-700 bg-zinc-900 text-zinc-400',
};

const riskP: Record<string, string> = { 'عالٍ': 'text-rose-400', 'متوسط': 'text-amber-400', 'منخفض': 'text-emerald-400', 'منخفض-متوسط': 'text-amber-400' };

export function Mec7() {
  const d = data as any;
  const ma = d.meta_analysis;

  return (
    <div className="space-y-6">
      {/* ═══ Header ═══ */}
      <Card className="bg-zinc-900/60 border-emerald-900/50">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-emerald-700 bg-emerald-950/60 text-emerald-300">MEC-7.0 BLUEPRINT</Badge>
            <CardTitle className="text-sm text-zinc-100">🏗️ دراسة المشروع الكاملة — من أين أشتري؟ بكم أبيع؟ وكيف أُطلق؟</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-center">
            {[
              { n: '25', l: 'SKU مسعّر بقرار موثق', c: 'text-emerald-400' },
              { n: '$0.57', l: 'متوسط هامش صافٍ/وحدة (عند السعر المقترح)', c: 'text-rose-400' },
              { n: '6', l: 'مصادر توريد مرتبة', c: 'text-cyan-300' },
              { n: '4', l: 'مراحل إطلاق ببوابات', c: 'text-violet-300' },
              { n: '10', l: 'مخاطر مصنفة + تخفيف', c: 'text-amber-300' },
              { n: '$30', l: 'أدنى رأس مال للبداية', c: 'text-teal-300' },
            ].map((s, i) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className={`text-lg font-bold font-mono ${s.c}`} dir="ltr">{s.n}</div>
                <div className="text-[10px] text-zinc-500 leading-4">{s.l}</div>
              </div>
            ))}
          </div>
          <div className="rounded border border-emerald-900/40 bg-emerald-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            <b className="text-emerald-300">التخصص السيادي:</b> {ma.sovereign_discipline}
            <br /><b className="text-emerald-300">القالب التشغيلي:</b> {ma.operational_template}
          </div>
        </CardContent>
      </Card>

      {/* ═══ 1. Critical deconstruction ═══ */}
      <Card className="bg-zinc-900/60 border-rose-900/50">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-rose-800 bg-rose-950/50 text-rose-300">تفكيك صارم</Badge>
            <CardTitle className="text-sm text-zinc-100">⚔️ عيوب النص الأصلي العشرة — لماذا هي أخطاء وما البديل</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded border border-zinc-800">
            <table className="w-full text-[11px] border-collapse">
              <thead className="bg-zinc-900">
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="p-2 text-right w-24">الاقتباس</th>
                  <th className="p-2 text-right">العيب</th>
                  <th className="p-2 text-right">لماذا خطأ</th>
                  <th className="p-2 text-right">البديل الصحيح</th>
                </tr>
              </thead>
              <tbody>
                {ma.flaws.map((f: any, i: number) => (
                  <tr key={i} className="border-b border-zinc-800/60 hover:bg-zinc-900/40">
                    <td className="p-2 font-bold text-rose-300">{f.q}</td>
                    <td className="p-2 text-zinc-200">{f.flaw}</td>
                    <td className="p-2 text-zinc-400">{f.why}</td>
                    <td className="p-2 text-emerald-300">{f.fix}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 rounded border border-emerald-900/40 bg-emerald-950/10 p-3 text-[11px] text-zinc-300 leading-7">
            <div className="text-emerald-300 font-bold mb-1">✍️ النص بعد إعادة الصياغة — التوجيه المحكم:</div>
            {ma.rewritten_directive}
          </div>
        </CardContent>
      </Card>

      {/* ═══ 2. Business model ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-violet-800 bg-violet-950/50 text-violet-300">القرار 1</Badge>
            <CardTitle className="text-sm text-zinc-100">🧭 نموذج العمل — ثلاث مراحل تطورية لا ثلاثة خيارات متنافسة</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {d.business_model.options.map((o: any) => (
              <div key={o.id} className={`rounded border p-3 ${o.id === 'A' ? 'border-emerald-800 bg-emerald-950/20' : 'border-zinc-800 bg-zinc-950/60'}`}>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="font-mono font-bold text-zinc-100">{o.id}</span>
                  <span className="text-[12px] font-bold text-zinc-100">{o.name}</span>
                </div>
                <div className="text-[11px] text-zinc-400 leading-6">{o.desc}</div>
                <div className={`mt-2 text-[10px] rounded px-2 py-1 inline-block ${o.id === 'A' ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-900' : 'bg-zinc-900 text-zinc-400 border border-zinc-800'}`}>{o.verdict}</div>
              </div>
            ))}
          </div>
          <div className="rounded border border-amber-900/40 bg-amber-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            <b className="text-amber-300">دولاب الموازنة:</b> {d.business_model.flywheel}
          </div>
        </CardContent>
      </Card>

      {/* ═══ 3. Sourcing matrix ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-cyan-800 bg-cyan-950/50 text-cyan-300">القرار 2 — من أين أشتري</Badge>
            <CardTitle className="text-sm text-zinc-100">🚚 مصفوفة التوريد — مرتبة بالجاهزية والتكلفة</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded border border-zinc-800">
            <table className="w-full text-[11px] border-collapse">
              <thead className="bg-zinc-900">
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="p-2 text-right">الطبقة</th>
                  <th className="p-2 text-right">المزود</th>
                  <th className="p-2 text-right">ماذا يوفر</th>
                  <th className="p-2 text-right">أساس التكلفة</th>
                  <th className="p-2 text-right">الدخول</th>
                  <th className="p-2">الدليل</th>
                </tr>
              </thead>
              <tbody>
                {d.sourcing_matrix.map((s: any, i: number) => (
                  <tr key={i} className="border-b border-zinc-800/60 hover:bg-zinc-900/40">
                    <td className="p-2"><span className={`rounded border px-1.5 py-0.5 text-[10px] ${tierColor[s.tier] || ''}`}>{s.tier}</span></td>
                    <td className="p-2 font-bold text-zinc-100" dir="ltr">{s.name}</td>
                    <td className="p-2 text-zinc-300">{s.what}</td>
                    <td className="p-2 text-zinc-400" dir="ltr">{s.cost_basis}</td>
                    <td className="p-2 text-zinc-300">{s.entry}</td>
                    <td className="p-2 text-[10px] text-zinc-500">{s.evidence}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* ═══ 4. PRICING TABLE — the centerpiece ═══ */}
      <Card className="bg-zinc-900/60 border-emerald-900/50">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-emerald-800 bg-emerald-950/50 text-emerald-300">القرار 3 — بكم أبيع</Badge>
            <CardTitle className="text-sm text-zinc-100">💰 جدول التسعير الكامل (25 SKU) — التكلفة الحية × السعر المقترح × الهامش الصافي</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="overflow-x-auto max-h-[34rem] overflow-y-auto rounded border border-zinc-800">
            <table className="w-full text-[11px] border-collapse">
              <thead className="sticky top-0 bg-zinc-900 z-10">
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="p-2 text-right">المنتج</th>
                  <th className="p-2">تكلفة API $</th>
                  <th className="p-2">سعر البيع $</th>
                  <th className="p-2">هامش صافٍ</th>
                  <th className="p-2">النطاق المنافس $</th>
                  <th className="p-2">الهشاشة</th>
                  <th className="p-2">المخزون</th>
                </tr>
              </thead>
              <tbody>
                {d.pricing.map((r: any, i: number) => (
                  <tr key={i} className={`border-b border-zinc-800/60 hover:bg-zinc-900/40 ${!r.in_stock ? 'opacity-45' : ''}`}>
                    <td className="p-2 text-zinc-200" dir="ltr">
                      {r.name}
                      {r.sold > 10000 && <span className="ms-1 text-[9px] text-amber-500">★</span>}
                    </td>
                    <td className="p-2 text-center"><M v={r.cost} c="text-zinc-400" /></td>
                    <td className="p-2 text-center"><M v={r.rec} /></td>
                    <td className="p-2 text-center font-mono text-cyan-300" dir="ltr">${r.net.toFixed(2)} · {r.net_pct}%</td>
                    <td className="p-2 text-center font-mono text-zinc-500 text-[10px]" dir="ltr">{r.market}</td>
                    <td className="p-2 text-center"><span className={`rounded border px-1.5 py-0.5 text-[10px] ${fragStyle[r.fragility]}`}>{fragLabel[r.fragility]}</span></td>
                    <td className="p-2 text-center">
                      <span className={`rounded px-1.5 py-0.5 text-[10px] font-mono ${r.in_stock ? 'border border-emerald-900 bg-emerald-950/60 text-emerald-400' : 'border border-zinc-800 bg-zinc-950 text-zinc-600'}`}>{r.in_stock ? 'متوفر' : 'نافد'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="text-[10px] text-zinc-500 leading-5">★ = الأكثر مبيعًا عبر المنصة (Gemini: 212,259 وحدة · CapCut 1M: 17,282 · Office365: 4,778) · الهامش الصافي = السعر − التكلفة − رسوم دفع 1.5% − مخصص ضمان (مستقر 3% / متوسط 8% / هش 15%) · الأعمدة الرمادية = نافد عند ProdSeller يوم 28/09 — يُعرض «أعلمني عند التوفر»</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="rounded border border-zinc-800 bg-zinc-950/60 p-3">
              <div className="text-[12px] font-bold text-zinc-100 mb-2">📐 سياسة التسعير (قواعد صلبة)</div>
              <ul className="space-y-1.5">
                {d.pricing_policy.map((p: string, i: number) => (
                  <li key={i} className="text-[11px] text-zinc-300 leading-6 flex gap-2"><span className="text-emerald-700">▪</span><span>{p}</span></li>
                ))}
              </ul>
            </div>
            <div className="rounded border border-zinc-800 bg-zinc-950/60 p-3">
              <div className="text-[12px] font-bold text-zinc-100 mb-2">🧮 اقتصاديات الوحدة — ثلاث عائلات معمولة</div>
              <table className="w-full text-[11px] border-collapse">
                <thead>
                  <tr className="text-zinc-500 border-b border-zinc-800">
                    <th className="p-1.5 text-right">العائلة</th><th className="p-1.5">سعر</th><th className="p-1.5">تكلفة</th><th className="p-1.5">ضمان</th><th className="p-1.5">صافٍ</th>
                  </tr>
                </thead>
                <tbody>
                  {d.unit_economics.worked.map((w: any, i: number) => (
                    <tr key={i} className="border-b border-zinc-800/60">
                      <td className="p-1.5 text-zinc-300">{w.item}</td>
                      <td className="p-1.5 text-center font-mono text-zinc-300" dir="ltr">${w.price}</td>
                      <td className="p-1.5 text-center font-mono text-zinc-500" dir="ltr">${w.cost}</td>
                      <td className="p-1.5 text-center font-mono text-rose-300" dir="ltr">${w.prov}</td>
                      <td className="p-1.5 text-center font-mono text-emerald-400" dir="ltr">${w.net} ({w.pct}%)</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="mt-2 text-[10px] text-zinc-500 leading-5">المعادلة: {d.unit_economics.equation}. {d.unit_economics.blended_assumption}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ═══ 5. Payments + Tech ═══ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-zinc-100">💳 استقبال أموال العملاء — المصفوفة</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {d.payment_rails.map((r: any, i: number) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-2.5">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="text-[12px] font-bold text-zinc-100">{r.rail}</span>
                  <span className="font-mono text-[11px] text-amber-300" dir="ltr">{r.fee}</span>
                </div>
                <div className="text-[11px] text-zinc-400 leading-5">{r.pros} · {r.cons}</div>
                <div className="text-[10px] text-emerald-400 mt-1">{r.verdict}</div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-zinc-100">⚙️ البنية التقنية — النواة جاهزة أصلًا</CardTitle></CardHeader>
          <CardContent className="space-y-2.5">
            <div className="rounded border border-emerald-900/40 bg-emerald-950/10 p-2.5 text-[11px] text-zinc-300 leading-6">{d.tech_stack.foundation}</div>
            <ul className="space-y-1.5">
              {d.tech_stack.add.map((a: string, i: number) => (
                <li key={i} className="text-[11px] text-zinc-300 leading-6 flex gap-2 rounded border border-zinc-800 bg-zinc-950/50 px-2.5 py-1.5"><span className="text-cyan-700">▪</span><span>{a}</span></li>
              ))}
            </ul>
            <div className="grid grid-cols-2 gap-2 text-center">
              <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className="text-sm font-bold font-mono text-cyan-300" dir="ltr">{d.tech_stack.timeline}</div>
                <div className="text-[10px] text-zinc-500">الجدول الزمني (دوام جزئي)</div>
              </div>
              <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className="text-[10px] text-zinc-500 leading-4">{d.tech_stack.app_verdict}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ═══ 6. Roadmap ═══ */}
      <Card className="bg-zinc-900/60 border-violet-900/50">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-violet-800 bg-violet-950/50 text-violet-300">خارطة الطريق</Badge>
            <CardTitle className="text-sm text-zinc-100">🗺️ الإطلاق رباعي المراحل — كل مرحلة برأس مال وبوابة قرار رقمية</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
            {d.roadmap.map((p: any, i: number) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[12px] font-bold text-violet-300">{p.phase}</span>
                  <span className="font-mono text-[10px] text-zinc-500" dir="ltr">{p.when}</span>
                </div>
                <div className="rounded border border-emerald-900/40 bg-emerald-950/20 px-2 py-1 text-center font-mono text-[12px] text-emerald-300" dir="ltr">{p.capital}</div>
                <div className="text-[11px] text-zinc-300 leading-6">{p.actions}</div>
                <div className="rounded border border-amber-900/40 bg-amber-950/10 p-2 text-[10px] text-amber-200 leading-5"><b>بوابة القرار:</b> {p.gate}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ═══ 7. Scenarios ═══ */}
      <Card className="bg-zinc-900/60 border-amber-900/50">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-amber-800 bg-amber-950/50 text-amber-300">توقعات — بافتراضات معلنة</Badge>
            <CardTitle className="text-sm text-zinc-100">📊 السيناريوهات المالية الثلاثة</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded border border-amber-900/40 bg-amber-950/10 p-2.5 text-[10px] text-amber-200 leading-5">{d.scenarios_note} · {d.break_even}</div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {d.scenarios.map((s: any) => (
              <div key={s.id} className="rounded border border-zinc-800 bg-zinc-950/60 p-3 text-center space-y-1.5">
                <div className="text-[12px] font-bold text-zinc-100">{s.name} <span className="font-mono text-zinc-500" dir="ltr">({s.id})</span></div>
                <div className="font-mono text-lg text-amber-300" dir="ltr">${s.net_mo}<span className="text-[10px] text-zinc-500">/شهر صافٍ</span></div>
                <div className="text-[10px] text-zinc-400 leading-5" dir="ltr">رأس مال عائم: ${s.float_usd} · {s.units_mo.toLocaleString()} وحدة/شهر</div>
                <div className="text-[10px] text-emerald-400 leading-5">{s.verdict}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ═══ 8. Risks ═══ */}
      <Card className="bg-zinc-900/60 border-rose-900/50">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-rose-800 bg-rose-950/50 text-rose-300">سجل المخاطر</Badge>
            <CardTitle className="text-sm text-zinc-100">🛡️ 10 مخاطر مصنفة (احتمال × أثر × تخفيف)</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded border border-zinc-800">
            <table className="w-full text-[11px] border-collapse">
              <thead className="bg-zinc-900">
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="p-2 text-right">الخطر</th><th className="p-2">الاحتمال</th><th className="p-2">الأثر</th><th className="p-2 text-right">التخفيف</th>
                </tr>
              </thead>
              <tbody>
                {d.risk_register.map((r: any, i: number) => (
                  <tr key={i} className="border-b border-zinc-800/60 hover:bg-zinc-900/40">
                    <td className="p-2 text-zinc-200">{r.risk}</td>
                    <td className={`p-2 text-center font-mono ${riskP[r.p] || 'text-zinc-400'}`}>{r.p}</td>
                    <td className={`p-2 text-center font-mono ${riskP[r.i] || 'text-zinc-400'}`}>{r.i}</td>
                    <td className="p-2 text-zinc-400">{r.mitigation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* ═══ 9. Decision points + evidence ═══ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-zinc-900/60 border-cyan-900/50">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-zinc-100">🎯 ثلاث نقاط قرار تنتظر كلمتك (لا تُطمس — تُعلن)</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {d.decision_points.map((dp: any) => (
              <div key={dp.id} className="rounded border border-zinc-800 bg-zinc-950/60 p-2.5">
                <div className="text-[12px] font-bold text-cyan-300 mb-1">{dp.id}. {dp.q}</div>
                <div className="text-[11px] text-zinc-400 leading-6">الأثر: {dp.impact}</div>
                <div className="text-[11px] text-emerald-400 leading-6">المسار الافتراضي الآمن: {dp.default}</div>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2"><CardTitle className="text-xs text-zinc-100">🔬 انضباط الأدلة — كل رقم في هذه الدراسة يعود لأحد هذه الصناديق</CardTitle></CardHeader>
          <CardContent className="space-y-1.5">
            {(Object.entries(d.evidence_discipline) as [string, string][]).map(([k, v]) => (
              <div key={k} className="text-[11px] text-zinc-300 leading-6 flex gap-2 rounded border border-zinc-800 bg-zinc-950/50 px-2.5 py-1.5">
                <span className="text-emerald-700">▪</span>
                <span><b className="text-zinc-100">{k}:</b> {v}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
