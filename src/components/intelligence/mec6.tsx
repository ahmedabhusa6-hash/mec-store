'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import data from '@/lib/data/mec6.json';

function Money({ v, c = 'text-emerald-400' }: { v: any; c?: string }) {
  return <span className={`font-mono ${c}`} dir="ltr">{v == null ? '—' : `$${v}`}</span>;
}

const statusStyle: Record<string, string> = {
  confirmed: 'border-emerald-800 bg-emerald-950/50 text-emerald-300',
  partial: 'border-amber-800 bg-amber-950/50 text-amber-300',
  hidden: 'border-cyan-800 bg-cyan-950/50 text-cyan-300',
  inquiry: 'border-zinc-700 bg-zinc-900 text-zinc-300',
  none: 'border-zinc-800 bg-zinc-950 text-zinc-500',
};
const statusLabel: Record<string, string> = {
  confirmed: 'موثق مباشر ✅', partial: 'جزئي ⚠️', hidden: 'محجوب 🔒', inquiry: 'بالتسعير', none: 'لا فجوة',
};

export function Mec6() {
  const d = data as any;
  const h = d.headline;

  return (
    <div className="space-y-6">
      {/* ═══ Run header ═══ */}
      <Card className="bg-zinc-900/60 border-emerald-900/50">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-emerald-700 bg-emerald-950/60 text-emerald-300">MEC-6.0 LIVE-API</Badge>
            <CardTitle className="text-sm text-zinc-100">🔓 اكتشاف الأسعار الحي — مفتاح ProdSeller API فعّال + سلسلة التوريد مُثبتة بالسنت</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-center">
            {[
              { n: h.ps_products, l: 'منتج ProdSeller بسعر حي', c: 'text-emerald-400' },
              { n: h.ps_instock, l: 'متوفر للشراء الآن', c: 'text-teal-300' },
              { n: h.sv_products, l: 'منتج StackVault حي', c: 'text-amber-300' },
              { n: h.cross_exact, l: 'تطابق تام بالسنت', c: 'text-rose-400' },
              { n: `${h.sv_markup_median_pct}%`, l: 'هامش تجزئة وسيط', c: 'text-cyan-300' },
              { n: h.suppliers_with_api_gap, l: 'مزودين بفجوة API (من 14)', c: 'text-violet-300' },
            ].map((s, i) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className={`text-lg font-bold font-mono ${s.c}`} dir="ltr">{s.n}</div>
                <div className="text-[10px] text-zinc-500 leading-4">{s.l}</div>
              </div>
            ))}
          </div>
          <div className="rounded border border-emerald-900/40 bg-emerald-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            <b className="text-emerald-300">تنفيذ أمر «اكشف السعر مهما كان»:</b> وصل المفتاح من المستخدم → تحقق فوري <span className="font-mono" dir="ltr">GET /v1/balance = 200 OK</span> → سحب كامل الكتالوج الحي (قراءة فقط، صفر طلبات شراء) → سحب حي لـ StackVault (322 منتجًا) → مطابقة منتج-بمنتج كشفت <b>12 تطابقًا تامًا بالسنت</b> بين سعر ProdSeller API والتكلفة الداخلية لـ StackVault — أي أن طبقة التجزئة فوق المصدر الجملة صارت مفسورة بالكامل، وحاسبة هوامش دولا صارت جاهزة بأرقام حية لا تقديرية.
          </div>
        </CardContent>
      </Card>

      {/* ═══ 1. Chain proof — the smoking gun ═══ */}
      <Card className="bg-zinc-900/60 border-rose-900/50">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-rose-800 bg-rose-950/50 text-rose-300">الإثبات الحاسم</Badge>
            <CardTitle className="text-sm text-zinc-100">🔗 سلسلة التوريد مُثبتة: ProdSeller (جملة) ← StackVault (تجزئة) — بالسنت</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded border border-rose-900/40 bg-rose-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            {d.chain_proof.claim}. الدليل: أسعار متطابقة تمامًا بين <span className="font-mono text-rose-300" dir="ltr">price</span> في API لدى ProdSeller وحقل <span className="font-mono text-rose-300" dir="ltr">costPrice</span> المكشوف في باك-إند StackVault. <b className="text-rose-300">الأثر:</b> {d.chain_proof.implication}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-1.5">
            {d.chain_proof.evidence.map((e: string, i: number) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 px-2.5 py-1.5 text-[11px] font-mono text-zinc-300" dir="ltr">{e}</div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* ═══ 2. ProdSeller live catalog ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-emerald-800 bg-emerald-950/50 text-emerald-300">GET /v1/products — 200 OK</Badge>
            <CardTitle className="text-sm text-zinc-100">🤖 كتالوج ProdSeller الحي كاملًا ({h.ps_products} منتجًا) — ما سيُخصم فعليًا من الرصيد</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded border border-zinc-800 bg-zinc-950/60 p-2.5 text-[11px] text-zinc-400 leading-6">
            الحساب: <span className="font-mono text-zinc-200" dir="ltr">@{d.account.username}</span> · شريحة <span className="font-mono text-amber-300" dir="ltr">{d.account.membership}</span> · الرصيد <span className="font-mono text-zinc-300" dir="ltr">${d.account.balance}</span> — {d.account.note}. عمود <span className="font-mono text-emerald-400">API $</span> هو سعر الشحن الفعلي لهذا المفتاح، وعمود <span className="font-mono text-zinc-400">المعلن $</span> للعرض العام المرجعي.
          </div>
          <div className="overflow-x-auto max-h-[28rem] overflow-y-auto rounded border border-zinc-800">
            <table className="w-full text-[11px] border-collapse">
              <thead className="sticky top-0 bg-zinc-900 z-10">
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="p-2 text-right">المنتج</th>
                  <th className="p-2">API $</th>
                  <th className="p-2">المعلن $</th>
                  <th className="p-2">خصم API</th>
                  <th className="p-2">مبيعات</th>
                  <th className="p-2">المخزون</th>
                </tr>
              </thead>
              <tbody>
                {d.prodseller_products.map((r: any, i: number) => (
                  <tr key={i} className={`border-b border-zinc-800/60 hover:bg-zinc-900/40 ${!r.inStock ? 'opacity-45' : ''}`}>
                    <td className="p-2 text-zinc-200" dir="ltr">{r.name}{r.emailActivation && <span className="text-[9px] text-cyan-500 ms-1">[تفعيل بريد]</span>}</td>
                    <td className="p-2 text-center"><Money v={r.price} /></td>
                    <td className="p-2 text-center"><Money v={r.publicPrice} c="text-zinc-500" /></td>
                    <td className="p-2 text-center font-mono text-amber-300" dir="ltr">{r.gap_pct ? `${r.gap_pct}%` : '—'}</td>
                    <td className="p-2 text-center font-mono text-zinc-400" dir="ltr">{r.sold?.toLocaleString?.() ?? r.sold}</td>
                    <td className="p-2 text-center">
                      <span className={`rounded px-1.5 py-0.5 text-[10px] font-mono ${r.inStock ? 'border border-emerald-900 bg-emerald-950/60 text-emerald-400' : 'border border-zinc-800 bg-zinc-950 text-zinc-600'}`}>{r.inStock ? 'متوفر' : 'نافد'}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="text-[10px] text-zinc-500 leading-5">⭐ الأكثر مبيعًا: Gemini Pro 18 شهرًا — <b className="text-zinc-300" dir="ltr">212,259</b> وحدة مباعة عبر المنصة (منتج القناة الأول) · ثانيًا CapCut Pro شهر: 17,282 · ثالثًا Office 365 سنة: 4,778.</div>
        </CardContent>
      </Card>

      {/* ═══ 3. Cross-match table ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-rose-800 bg-rose-950/50 text-rose-300">المطابقة الحاسمة</Badge>
            <CardTitle className="text-sm text-zinc-100">⚖️ ProdSeller API × تكلفة StackVault الداخلية × تجزئته — من هوامش من؟</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded border border-zinc-800">
            <table className="w-full text-[11px] border-collapse">
              <thead className="bg-zinc-900">
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="p-2 text-right">المنتج</th>
                  <th className="p-2">API جملة $</th>
                  <th className="p-2">تكلفة SV $</th>
                  <th className="p-2">تجزئة SV $</th>
                  <th className="p-2">هامش SV</th>
                  <th className="p-2">الحكم</th>
                </tr>
              </thead>
              <tbody>
                {d.cross_match.map((m: any, i: number) => (
                  <tr key={i} className="border-b border-zinc-800/60 hover:bg-zinc-900/40">
                    <td className="p-2 text-zinc-200" dir="ltr">{m.label}</td>
                    <td className="p-2 text-center"><Money v={m.ps_api} /></td>
                    <td className="p-2 text-center"><Money v={m.sv_cost} c="text-amber-300" /></td>
                    <td className="p-2 text-center"><Money v={m.sv_retail} c="text-zinc-300" /></td>
                    <td className="p-2 text-center font-mono text-cyan-300" dir="ltr">{m.markup_pct ? `+${m.markup_pct}%` : '—'}</td>
                    <td className="p-2 text-center">
                      <span className={`rounded px-1.5 py-0.5 text-[10px] font-mono ${m.verdict === 'EXACT' ? 'border border-rose-800 bg-rose-950/60 text-rose-300' : m.verdict === '±2¢' ? 'border border-amber-800 bg-amber-950/60 text-amber-300' : m.verdict === 'CLOSE' ? 'border border-cyan-900 bg-cyan-950/50 text-cyan-400' : 'border border-zinc-800 bg-zinc-950 text-zinc-500'}`}>
                        {m.verdict === 'EXACT' ? 'تطابق تام 🎯' : m.verdict === '±2¢' ? '±2 سنت' : m.verdict === 'CLOSE' ? 'قريب' : 'هوية مختلفة'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 rounded border border-zinc-800 bg-zinc-950/60 p-3 text-[11px] text-zinc-400 leading-6">
            <b className="text-zinc-200">قراءة الجدول:</b> «تطابق تام» = تكلفة StackVault تساوي سعر ProdSeller API بالسنت (نفس المصدر الجملة مؤكد). «هوية مختلفة» = المنتج في المتجرين بناء/ضمان مختلف (مثل ChatGPT Plus: نسخة UPI عند ProdSeller بـ$2.90 مقابل بناءات أغلى بضمان أطول عند StackVault تصل $12.81) — وليس خطأ في القياس.
          </div>
        </CardContent>
      </Card>

      {/* ═══ 4. Wholesale floor — Dolaa calculator ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-amber-800 bg-amber-950/50 text-amber-300">أرضية الجملة الحية</Badge>
            <CardTitle className="text-sm text-zinc-100">🧮 حاسبة هوامش دولا — الأرضية صارت أرقامًا حية (فور وصول أسعاره تُحسب هوامشه فورًا)</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="overflow-x-auto rounded border border-zinc-800">
            <table className="w-full text-[11px] border-collapse">
              <thead className="bg-zinc-900">
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="p-2 text-right">المنتج</th>
                  <th className="p-2">أرضية الجملة $</th>
                  <th className="p-2">تجزئة StackVault $</th>
                  <th className="p-2">نطاق السوق المرصود $</th>
                  <th className="p-2">القيمة الرسمية $</th>
                  <th className="p-2">خصم عن الرسمي</th>
                </tr>
              </thead>
              <tbody>
                {d.wholesale_floor.map((r: any, i: number) => {
                  const disc = r.official_1m_value != null ? (100 - (r.ps_api / r.official_1m_value) * 100) : null;
                  return (
                    <tr key={i} className="border-b border-zinc-800/60 hover:bg-zinc-900/40">
                      <td className="p-2 text-zinc-200">{r.item}</td>
                      <td className="p-2 text-center"><Money v={r.ps_api} /></td>
                      <td className="p-2 text-center"><Money v={r.sv_retail} c="text-amber-300" /></td>
                      <td className="p-2 text-center font-mono text-zinc-400" dir="ltr">{r.observed_market}</td>
                      <td className="p-2 text-center"><Money v={r.official_1m_value} c="text-zinc-500" /></td>
                      <td className="p-2 text-center font-mono text-rose-300" dir="ltr">{disc != null ? `${disc.toFixed(1)}%` : '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="rounded border border-amber-900/40 bg-amber-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            <b className="text-amber-300">ما ينقص لإغلاق ملف دولا نهائيًا:</b> {d.dolaa_status.needs.join(' · ')}. المعادلة جاهزة: <span className="font-mono" dir="ltr">{d.dolaa_status.formula}</span> — بمجرد وصول أي من الثلاثة ننتج جدول هوامش دولا الحقيقية منتجًا-منتجًا خلال دقائق.
          </div>
        </CardContent>
      </Card>

      {/* ═══ 5. Suppliers probe status ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-violet-800 bg-violet-950/50 text-violet-300">فحص الآخرين — مكتمل</Badge>
            <CardTitle className="text-sm text-zinc-100">🗂️ {h.suppliers_probed_total} مزودًا — من يقدم سعرًا مختلفًا في API؟ (الحالة النهائية بعد الفحص الحي)</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded border border-zinc-800">
            <table className="w-full text-[11px] border-collapse">
              <thead className="bg-zinc-900">
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="p-2 text-right">المزود</th>
                  <th className="p-2 text-right">الفجوة المكتشفة</th>
                  <th className="p-2 text-right">الدليل</th>
                  <th className="p-2 text-right">الحكم</th>
                  <th className="p-2">الحالة</th>
                </tr>
              </thead>
              <tbody>
                {d.suppliers.map((s: any, i: number) => (
                  <tr key={i} className="border-b border-zinc-800/60 hover:bg-zinc-900/40">
                    <td className="p-2 font-bold text-zinc-100" dir="ltr">{s.name}</td>
                    <td className="p-2 font-mono text-amber-300" dir="ltr">{s.gap}</td>
                    <td className="p-2 text-zinc-400 text-[10px]">{s.evidence}</td>
                    <td className="p-2 text-zinc-300">{s.verdict}</td>
                    <td className="p-2 text-center">
                      <span className={`rounded border px-1.5 py-0.5 text-[10px] font-mono ${statusStyle[s.status] || statusStyle.none}`}>{statusLabel[s.status] || s.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="rounded border border-emerald-900/40 bg-emerald-950/10 p-3 text-[11px] text-zinc-300 leading-6">
              <b className="text-emerald-300">الخلاصة التنفيذية:</b> خمسة مزودين فقط بفجوة API شرائية حقيقية: <b>ProdSeller</b> (أفضلها: دخول خفيف + شفافية كاملة + خصم API فوري 0–27.6%) · <b>StackVault</b> (طبقة تجزئة فوق ProdSeller — مفيدة كمرآة أسعار لا كمصدر شراء) · <b>Kinguin</b> (5–10.2% كميات، مؤسسي) · <b>Reloadly</b> (2–10% منشور) · <b>Turgame</b> (~1%، بطاقات رسمية). GGSel محجوب جغرافيًا وDingConnect خلف تسجيل مجاني — كلاهما قابل للفتح لاحقًا.
            </div>
            <div className="rounded border border-zinc-800 bg-zinc-950/60 p-3 text-[11px] text-zinc-400 leading-6 space-y-1">
              <div className="text-zinc-200 font-bold mb-1">🔬 تصنيف الأدلة (انضباط المعلومات):</div>
              {(Object.entries(d.evidence_classes) as [string, string][]).map(([k, v]) => (
                <div key={k} className="flex gap-2"><span className="text-emerald-700">▪</span><span><b className="text-zinc-300">{k}</b>: {v}</span></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
