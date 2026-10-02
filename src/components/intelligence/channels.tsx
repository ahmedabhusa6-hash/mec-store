'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import data from '@/lib/data/channels-data.json';

function riskBadge(level: string, label: string) {
  const cls =
    level === 'high'
      ? 'bg-red-950/60 text-red-300 border-red-800'
      : level === 'warn'
      ? 'bg-amber-950/60 text-amber-300 border-amber-800'
      : 'bg-zinc-900 text-zinc-400 border-zinc-700';
  return <span className={`rounded border px-2 py-0.5 text-[10px] font-medium whitespace-nowrap ${cls}`}>{label}</span>;
}

export function ChannelsAndEconomics() {
  const clusters = data.clusters as any[];
  const models = data.sourcing_models as any[];
  const margins = data.margins_ai as any[];
  return (
    <div className="space-y-6">
      {/* Verdict */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">
            §19 — أول تحقق مباشر لسجل القنوات (27/09): 31/31 كيانًا حيًا — إجابة «هل توجد قنوات أفضل؟»
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2 sm:grid-cols-2">
          <div className="rounded border border-emerald-900/60 bg-emerald-950/30 p-3 text-[11px] leading-6">
            <b className="text-emerald-300">للشراء الفردي المشروع:</b> نعم — الفوترة السنوية الرسمية (ChatGPT/Gemini ≈ $16.67/شهر) + منصات المفاتيح الموثقة (Eneba/Kinguin/Driffy) بحماية مشترٍ.
          </div>
          <div className="rounded border border-amber-900/60 bg-amber-950/30 p-3 text-[11px] leading-6">
            <b className="text-amber-300">للوحدة الرمادية الواحدة:</b> لا — هذه القنوات هي نفسها الطبقة الأدنى للجمهور (Gemini 18 شهرًا $0.39–0.59). أي أدنى من كلفة الاقتناء المادية = علامة احتيال لا صفقة.
          </div>
          <div className="rounded border border-emerald-900/60 bg-emerald-950/30 p-3 text-[11px] leading-6">
            <b className="text-emerald-300">للحجم والجملة:</b> نعم — اصعد للمنبع: ProdSeller API ($0.40 Gemini 18m) · GGSel ($9.44 ChatGPT مستقرة) · Turgame/Reloadly/FazerCards (خلف تسجيل B2B).
          </div>
          <div className="rounded border border-red-900/60 bg-red-950/30 p-3 text-[11px] leading-6">
            <b className="text-red-300">تحذير جوهري:</b> رُصد محتوى احتيالي صريح (بطاقات مولدة + CVV عشوائي) في قناة مدرجة (learnwith_Alex) — حُجرت وفق D4 واستُبعدت من أي مقارنة.
          </div>
        </CardContent>
      </Card>

      {/* Clusters table */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">العناقات العشر المرصودة (31 كيانًا → 10 عناقات) + هويات محسومة</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px] min-w-[860px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-start py-1.5 pe-2 font-medium">العناق</th>
                  <th className="text-start py-1.5 pe-2 font-medium">الحجم المرصود</th>
                  <th className="text-start py-1.5 pe-2 font-medium">الدور في السلسلة</th>
                  <th className="text-start py-1.5 pe-2 font-medium">أسعار مرصودة (USD)</th>
                  <th className="text-start py-1.5 pe-2 font-medium">السمعة المستقلة</th>
                  <th className="text-start py-1.5 font-medium">المخاطرة</th>
                </tr>
              </thead>
              <tbody>
                {clusters.map((c, i) => (
                  <tr key={i} className="border-b border-zinc-800/50 align-top">
                    <td className="py-1.5 pe-2 text-zinc-200 font-medium whitespace-nowrap">{c.name}</td>
                    <td className="py-1.5 pe-2 text-zinc-400 whitespace-nowrap">{c.scale}</td>
                    <td className="py-1.5 pe-2 text-zinc-400 max-w-[240px]">{c.role}</td>
                    <td className="py-1.5 pe-2 text-emerald-300 whitespace-nowrap">{c.prices}</td>
                    <td className="py-1.5 pe-2 text-zinc-500 max-w-[180px]">{c.reputation}</td>
                    <td className="py-1.5">{riskBadge(c.riskLevel, c.risk)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 text-[11px] text-zinc-500 leading-6 border-t border-zinc-800 pt-2">
            <b className="text-zinc-300">هويات محسومة [مرصود مباشرة]:</b>
            <ul className="list-disc ps-5 mt-1 space-y-0.5">
              {(data.identity_resolutions as string[]).map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Sourcing models */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">النماذج السبعة للتزويد — كيف يشترون (بالأدلة)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px] min-w-[640px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-start py-1.5 pe-2 font-medium">#</th>
                  <th className="text-start py-1.5 pe-2 font-medium">النموذج</th>
                  <th className="text-start py-1.5 pe-2 font-medium">الدليل</th>
                  <th className="text-start py-1.5 font-medium">الشرعية</th>
                </tr>
              </thead>
              <tbody>
                {models.map((m) => (
                  <tr key={m.n} className={`border-b border-zinc-800/50 ${m.n === 7 ? 'text-red-300' : ''}`}>
                    <td className="py-1.5 pe-2">{m.n}</td>
                    <td className="py-1.5 pe-2 text-zinc-200 max-w-[260px]">{m.model}</td>
                    <td className="py-1.5 pe-2 text-zinc-500 max-w-[280px]">{m.evidence}</td>
                    <td className="py-1.5">{m.legality}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Unit economics + margins */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">كم الهامش؟ — معادلة الوحدة والهوامش المرصودة (الشرط الصارم)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded border border-emerald-900/60 bg-emerald-950/20 p-3 text-[11px] leading-6 text-zinc-300">
            <b className="text-emerald-300">معادلة الوحدة:</b> {data.unit_economics}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px] min-w-[640px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-start py-1.5 pe-2 font-medium">المنتج (AI/الاشتراكات)</th>
                  <th className="text-start py-1.5 pe-2 font-medium">الرسمي</th>
                  <th className="text-start py-1.5 pe-2 font-medium">الأدنى المرصود (رمادي)</th>
                  <th className="text-start py-1.5 pe-2 font-medium">الفجوة</th>
                  <th className="text-start py-1.5 font-medium">الآلية</th>
                </tr>
              </thead>
              <tbody>
                {margins.map((m, i) => (
                  <tr key={i} className="border-b border-zinc-800/50">
                    <td className="py-1.5 pe-2 text-zinc-200">{m.product}</td>
                    <td className="py-1.5 pe-2 text-zinc-500 whitespace-nowrap">{m.official}</td>
                    <td className="py-1.5 pe-2 text-emerald-300 whitespace-nowrap">{m.observed}</td>
                    <td className="py-1.5 pe-2 text-amber-300 whitespace-nowrap">{m.gap}</td>
                    <td className="py-1.5 text-zinc-500 max-w-[220px]">{m.mechanism}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="text-[11px] text-zinc-500 leading-6 border-t border-zinc-800 pt-2">
            <b className="text-zinc-300">كم فائدتهم — ثلاث فئات:</b> المصنع (هامش اسمي هائل لكنه هش — يتبخر بترقيع الطريقة: UPI نجاح 1–2% موثق) · الموزع (هامش طبقة مستقر 10–51% + حجم — الأكثر استدامة) · المتجر (30–100%+ فوق كلفة الاقتناء — الربحية الحقيقية تتحدد بمعدل استبدال الحسابات الميتة، غير معلن).
            <br />
            <b className="text-zinc-300">الخلاصة:</b> لا يهزمون السوق بالكفاءة بل بعدم دفع قيمة المنتج أصلًا — ولذلك أي ترقيع من الناشرين يظهر فورًا كارتفاع أسعار معلن (رُصدت إشارتان حيتان في يوم الرصد نفسه).
          </div>
        </CardContent>
      </Card>

      {/* Notion sync */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">مزامنة Notion</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-2 text-[11px] text-zinc-400">
          <Badge className="bg-emerald-950/60 text-emerald-300 border-emerald-800">أول كتابة ناجحة</Badge>
          <span>{data.notion_sync}</span>
        </CardContent>
      </Card>
    </div>
  );
}
