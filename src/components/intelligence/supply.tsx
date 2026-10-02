'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { runData } from '@/lib/data';
import { statusBadge } from './shared';

export function SupplyAndCoverage() {
  const branches = runData.branch_terminal_states as any[];
  const coverage = runData.coverage_matrix as any[];
  return (
    <div className="space-y-6">
      {/* Supply chain layers */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">سلسلة التوريد — الطبقات والأدلة</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-[11px] text-zinc-500 leading-6">
            تصنيف الأدوار (وليس تسلسلًا إلزاميًا): Seller → Reseller → Wholesaler → Distributor → Aggregator → Upstream Supplier → Primary Source.
            أعمق طبقة علويا يدعمها الدليل هذا التشغيل: <span className="text-violet-300">منصات B2B الرقمية (DT One · Reloadly · DingConnect)</span>.
          </div>
          <div className="grid gap-2">
            <ChainRow layer="Primary Sources (الناشرون)" entities="OpenAI · Google · Netflix · Spotify · NordVPN · Microsoft · Garena · Valve · Apple · Tencent/Midasbuy" status="Verified" />
            <ChainRow layer="Upstream B2B Infrastructure" entities="DT One (تُغذّي PayPal وBitget) · Reloadly · DingConnect" status="Verified" note="التسعير يتطلب حسابًا — Retrieval-Limited" />
            <ChainRow layer="Regional Aggregators / Platforms" entities="LikeCard · bitaqaty · Al Momaiz Card (تملك REST API عامة)" status="Verified (كيان)" note="موقعها الفعلي في السلسلة — Unresolved" />
            <ChainRow layer="Marketplaces" entities="Eneba · Kinguin · G2A · GAMIVO · GGSel · Plati · Z2U · K4G · itemku" status="Verified" />
            <ChainRow layer="Retail Sellers / Services" entities="Turgame · bittopup · cardsouq · gameseal · digitalmaze · متاجر MENA (snoonu/yallatoys/vexacard/karteet/gml) · لوحات SMM · مزودو أرقام" status="Verified" />
            <ChainRow layer="؟ B2B → Retail (سلسلة التزويد الفعلية)" entities="لا يوجد دليل مباشر يربط أي بائع تجزئة بمنصة B2B محددة" status="Unresolved (H3)" note="لا يُستنتج من تشابه الكتالوج أو انخفاض السعر — §7" />
          </div>
          <div className="text-[11px] text-zinc-500 leading-6 border-t border-zinc-800 pt-2">
            <span className="text-amber-400">الثابت المطبق:</span> Upstream ≠ Cheapest — لم يُستنتج أي ارتباط علوي من انخفاض سعر أو تشابه كتالوج أو علامة مشتركة أو لغة مشتركة.
          </div>
        </CardContent>
      </Card>

      {/* Coverage matrix */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">مصفوفة التغطية حسب عائلات الاكتشاف (§15)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {coverage.map((c, i) => (
            <div key={i} className="flex flex-col sm:flex-row sm:items-start gap-1.5 sm:gap-3 border-b border-zinc-800/50 pb-2 last:border-0">
              <div className="sm:w-64 shrink-0 text-xs text-zinc-300 leading-5">{c.discovery_family}</div>
              <div className="shrink-0">{statusBadge(c.status)}</div>
              <div className="flex-1 text-[11px] text-zinc-500 leading-5">{c.detail}</div>
            </div>
          ))}
          <div className="text-[10px] text-zinc-600 leading-5 pt-1">
            الحالات المستخدمة حصريًا: Not Searched · Searched — No Useful Result · Retrieval Failed / Access Unavailable · Budget-Limited · Unresolved · Verified Findings. فشل الاسترجاع لا يُحوَّل أبدًا إلى عدم وجود.
          </div>
        </CardContent>
      </Card>

      {/* Branch terminal states */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">الحالات النهائية للفروع + تشخيص التوقف (§16)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-[11px] min-w-[640px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800">
                  <th className="text-start py-1.5 pe-2 font-medium">Branch</th>
                  <th className="text-start py-1.5 pe-2 font-medium">Terminal State</th>
                  <th className="text-start py-1.5 font-medium">Diagnosis</th>
                </tr>
              </thead>
              <tbody>
                {branches.map((b) => (
                  <tr key={b.branch} className="border-b border-zinc-800/40 align-top">
                    <td className="py-1.5 pe-2 font-mono text-[10px] text-zinc-400">{b.branch}</td>
                    <td className="py-1.5 pe-2">{statusBadge(b.state)}</td>
                    <td className="py-1.5 text-zinc-500 leading-5">{b.diagnosis}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="text-[10px] text-zinc-600 leading-5 pt-2">
            التشخيق الرباعي مطبق قبل إغلاق أي فرع: True Saturation / Retrieval Ceiling / Poor Query Strategy / Insufficient Exploration. لا يُسمى فرع «مُشبعًا» ما دام Retrieval-Limited أو Budget-Limited أو Scope-Excluded.
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function ChainRow({ layer, entities, status, note }: { layer: string; entities: string; status: string; note?: string }) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-950/50 p-3">
      <div className="flex flex-wrap items-center gap-2 mb-1.5">
        <span className="text-xs text-zinc-200 font-medium">{layer}</span>
        <Badge variant="outline" className={`text-[9px] px-1.5 py-0 ${
          status === 'Verified' ? 'border-emerald-800 text-emerald-400'
          : status.includes('Unresolved') ? 'border-amber-800 text-amber-400'
          : 'border-zinc-700 text-zinc-500'
        }`}>{status}</Badge>
      </div>
      <div className="text-[11px] text-zinc-500 leading-6" dir="ltr">{entities}</div>
      {note && <div className="text-[10px] text-zinc-600 mt-1">↳ {note}</div>}
    </div>
  );
}
