'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { batch2Data, batch2Stats } from '@/lib/data';

const FAMS = ['Gift Cards', 'Digital Subscriptions', 'AI/SaaS', 'Game Top-up', 'Game Keys', 'Virtual Numbers', 'Software/Licenses', 'SMM Services', 'eSIM', 'API Services'];
const STATES = [
  { k: 'B2-Offer', label: 'عرض معلن' },
  { k: 'B2-OfficialOnly', label: 'خط رسمي فقط' },
  { k: 'B2-LeadOnly', label: 'Lead-only' },
  { k: 'B2-RateLimited', label: 'مؤجل §19' },
];

function stateBadge(cls: string) {
  if (cls === 'B2-Offer') return <Badge variant="outline" className="text-[10px] border-amber-800 bg-amber-950/60 text-amber-300">عرض معلن</Badge>;
  if (cls === 'B2-OfficialOnly') return <Badge variant="outline" className="text-[10px] border-emerald-800 bg-emerald-950/60 text-emerald-300">خط رسمي فقط</Badge>;
  if (cls === 'B2-RateLimited') return <Badge variant="outline" className="text-[10px] border-rose-800 bg-rose-950/60 text-rose-300">مؤجل §19</Badge>;
  return <Badge variant="outline" className="text-[10px] border-zinc-700 bg-zinc-900 text-zinc-400">Lead-only</Badge>;
}

export function Batch2() {
  const [q, setQ] = useState('');
  const [fam, setFam] = useState('');
  const [st, setSt] = useState('');
  const rows = useMemo(() => {
    const ql = q.toLowerCase();
    return batch2Data.batch2_skus.filter((s: any) => {
      const hay = `${s.sku_id} ${s.identity.brand} ${s.identity.product} ${s.identity.region} ${s.best_advertised?.entity || ''} ${s.state_note}`.toLowerCase();
      return (!ql || hay.includes(ql)) && (!fam || s.family === fam) && (!st || s.state_class === st);
    });
  }, [q, fam, st]);

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-amber-900/60 bg-amber-950/30 p-3 text-xs text-amber-200/90 leading-6">
        تشغيلة MEC2-20260927-B2 · 121 استعلامًا مخططًا → 115 ناجحًا + 15 مؤجلًا (حصة 477 طويلة النافذة — §19).
        مستوى دليل كل العروض: <b>معلن (مقتطف بحث)</b> — القراءة المباشرة للصفحات مؤجلة. ضجيج الاستخراج الآلي استُبعد بمراجعة يدوية.
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        <Card className="bg-zinc-900/60 border-zinc-800"><CardContent className="p-3 text-center"><div className="text-xl font-bold text-emerald-400">{batch2Stats.skusTotal}</div><div className="text-[10px] text-zinc-500">SKU منفذ (P2)</div></CardContent></Card>
        <Card className="bg-zinc-900/60 border-zinc-800"><CardContent className="p-3 text-center"><div className="text-xl font-bold text-amber-400">{batch2Stats.withOffers}</div><div className="text-[10px] text-zinc-500">بعرض مطابق الهوية</div></CardContent></Card>
        <Card className="bg-zinc-900/60 border-zinc-800"><CardContent className="p-3 text-center"><div className="text-xl font-bold text-emerald-400">{batch2Stats.officialBaselines}</div><div className="text-[10px] text-zinc-500">خط رسمي موثق</div></CardContent></Card>
        <Card className="bg-zinc-900/60 border-zinc-800"><CardContent className="p-3 text-center"><div className="text-xl font-bold text-zinc-400">{batch2Stats.leadOnly}</div><div className="text-[10px] text-zinc-500">Lead-only</div></CardContent></Card>
        <Card className="bg-zinc-900/60 border-zinc-800"><CardContent className="p-3 text-center"><div className="text-xl font-bold text-rose-400">{batch2Stats.rateLimited}</div><div className="text-[10px] text-zinc-500">مؤجل (حد المعدل)</div></CardContent></Card>
      </div>

      <div className="flex flex-wrap gap-2 items-center">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="🔍 ابحث: PSN، Windows، eSIM…" className="bg-zinc-900 border border-zinc-800 rounded-md px-3 py-1.5 text-xs w-56" />
        <select value={fam} onChange={(e) => setFam(e.target.value)} className="bg-zinc-900 border border-zinc-800 rounded-md px-3 py-1.5 text-xs">
          <option value="">كل الأسر</option>
          {FAMS.map((f) => <option key={f} value={f}>{f}</option>)}
        </select>
        <select value={st} onChange={(e) => setSt(e.target.value)} className="bg-zinc-900 border border-zinc-800 rounded-md px-3 py-1.5 text-xs">
          <option value="">كل الحالات</option>
          {STATES.map((s) => <option key={s.k} value={s.k}>{s.label}</option>)}
        </select>
        <span className="text-[10px] text-zinc-500">{rows.length} / {batch2Data.batch2_skus.length}</span>
      </div>

      <div className="overflow-x-auto rounded-md border border-zinc-800">
        <table className="w-full text-[11px] min-w-[900px]">
          <thead>
            <tr className="text-zinc-500 bg-zinc-900/80 border-b border-zinc-800">
              <th className="text-start py-2 px-2 font-medium">SKU</th>
              <th className="text-start py-2 px-2 font-medium">المنتج</th>
              <th className="text-start py-2 px-2 font-medium">الأسرة</th>
              <th className="text-start py-2 px-2 font-medium">أفضل معلن</th>
              <th className="text-start py-2 px-2 font-medium">البائع</th>
              <th className="text-start py-2 px-2 font-medium">خط رسمي</th>
              <th className="text-start py-2 px-2 font-medium">الحالة</th>
              <th className="text-start py-2 px-2 font-medium">ملاحظة</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((s: any) => (
              <tr key={s.sku_id} className="border-b border-zinc-800/50 hover:bg-zinc-800/30 align-top">
                <td className="py-2 px-2 font-mono text-[10px] text-zinc-500">{s.sku_id}</td>
                <td className="py-2 px-2 text-zinc-300 leading-5">
                  <span className="text-zinc-100">{s.identity.brand}</span> — {s.identity.product}
                  {s.identity.denomination ? <span className="text-zinc-500"> · {s.identity.denomination}</span> : null}
                  <span className="text-zinc-500"> · {s.identity.region}</span>
                </td>
                <td className="py-2 px-2 text-zinc-500">{s.family}</td>
                <td className="py-2 px-2 font-mono" dir="ltr">
                  {s.best_advertised ? <span className="text-emerald-400">${s.best_advertised.usd.toFixed(2)}</span> : '—'}
                </td>
                <td className="py-2 px-2 text-zinc-400">{s.best_advertised?.entity || '—'}</td>
                <td className="py-2 px-2 font-mono" dir="ltr">
                  {s.official_anchor?.price != null ? <span className="text-zinc-300">${s.official_anchor.price}</span> : '—'}
                </td>
                <td className="py-2 px-2">{stateBadge(s.state_class)}</td>
                <td className="py-2 px-2 text-zinc-500 max-w-[280px] leading-5">{s.best_advertised?.note || s.state_note || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-1"><CardTitle className="text-sm">اكتشافات الدفعة 2 الهيكلية</CardTitle></CardHeader>
        <CardContent className="text-xs text-zinc-400 leading-7 space-y-1">
          <div>🇦🇷 <b className="text-zinc-200">سوق العلاوة الأرجنتيني:</b> بطاقات PSN الأرجنتينية تُباع فوق قيمتها الاسمية (بطاقة $50 عند ~$67.91) — العرض الوحيد تحتها ($34.81) كان «نفد» لحظة الرصد.</div>
          <div>🎮 <b className="text-zinc-200">«رمادي» ≠ «أرخص»:</b> G2A يبيع 660 PUBG UC بـ$26.61 فوق الرسمي $9.99 بـ166% — في مقابل منتديات رمادية (sythe.org) بـ2800 V-Bucks عند $6.99 بلا أي حماية.</div>
          <div>📜 <b className="text-zinc-200">Office 2024 عبر مصدرين مستقلين:</b> Keyforsteam €0.56 (رصد مباشر سابق) + Keys4us $0.60 (مقتطف اليوم) — تقارب يرفع الثقة بالأرضية.</div>
          <div>🚫 <b className="text-zinc-200">لا فوترة سنوية رسمية لChatGPT Plus</b> (نص help.openai) — كل عرض «Plus 12 شهرًا» بناء سوق رمادي بطبيعته.</div>
        </CardContent>
      </Card>
    </div>
  );
}
