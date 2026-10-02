'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Badge } from '@/components/ui/badge';
import { skuData } from '@/lib/data';
import { matchBadge, priceEvBadge, statusBadge } from './shared';

export function Skus() {
  const [open, setOpen] = useState<string | null>(skuData.batch1_skus[0]?.sku_id || null);
  return (
    <div className="space-y-3">
      <div className="text-xs text-zinc-500 leading-6 px-1">
        كل SKU وحدة مقارنة مستقلة بهويتها الكاملة. لا تُقارن العروض إلا عبر المطابقة المادية (Exact / Strong Comparable / Possible–Review / Non-Comparable). اضغط أي SKU لفتح سجله الكامل.
      </div>
      {skuData.batch1_skus.map((sku) => {
        const a = sku.official_anchor as any;
        const pi = sku.price_intelligence as any;
        const isOpen = open === sku.sku_id;
        return (
          <Card key={sku.sku_id} className="bg-zinc-900/60 border-zinc-800 overflow-hidden">
            <Collapsible open={isOpen} onOpenChange={(v) => setOpen(v ? sku.sku_id : null)}>
              <CollapsibleTrigger asChild>
                <button className="w-full text-start">
                  <CardHeader className="pb-2 hover:bg-zinc-800/40 transition-colors">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <span className="font-mono text-[10px] text-zinc-500">{sku.sku_id}</span>
                          <Badge variant="outline" className="text-[10px] border-zinc-700 text-zinc-400">{sku.family}</Badge>
                          {a?.price != null ? statusBadge('Verified') : statusBadge('Retrieval-Limited')}
                        </div>
                        <CardTitle className="text-sm sm:text-base text-zinc-100 leading-6">
                          {sku.identity.brand} — {sku.identity.product}
                          <span className="text-zinc-500 font-normal text-xs sm:text-sm">
                            {' '}{sku.identity.plan || sku.identity.denomination || sku.identity.quantity || ''}
                          </span>
                        </CardTitle>
                      </div>
                      <div className="shrink-0 text-end">
                        <div className="text-[10px] text-zinc-500">المرجع الرسمي</div>
                        <div className={`font-mono text-sm ${a?.price != null ? 'text-emerald-400' : 'text-zinc-600'}`} dir="ltr">
                          {a?.price != null ? `${a.price} ${a.currency}` : 'Unknown'}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent className="pt-0 space-y-4">
                  {/* SKU identity */}
                  <div className="rounded-md bg-zinc-950/70 border border-zinc-800 p-3">
                    <div className="text-[11px] text-zinc-500 mb-2">هوية الـSKU (أساس المقارنة)</div>
                    <div className="flex flex-wrap gap-1.5" dir="ltr">
                      {Object.entries(sku.identity as Record<string, unknown>).filter(([k]) => k !== 'locked').map(([k, v]) => (
                        <span key={k} className="text-[10px] font-mono bg-zinc-900 border border-zinc-800 rounded px-1.5 py-0.5 text-zinc-400">
                          {k}: <span className="text-zinc-300">{String(v)}</span>
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Official anchor */}
                  <div className="rounded-md border border-zinc-800 p-3 bg-zinc-950/40">
                    <div className="flex flex-wrap items-center gap-2 mb-1.5">
                      <span className="text-[11px] text-zinc-400 font-medium">المرجع الرسمي (Official Anchor)</span>
                      {statusBadge(String(a?.freshness || 'Unknown'))}
                      {priceEvBadge(String(a?.evidence_level || 'Unknown'))}
                    </div>
                    <div className="text-xs text-zinc-400 leading-6" dir="ltr">{a?.evidence}</div>
                  </div>

                  {/* Offers table */}
                  {sku.offers && sku.offers.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-[11px] min-w-[760px]" dir="ltr">
                        <thead>
                          <tr className="text-zinc-500 border-b border-zinc-800 text-start">
                            <th className="text-start py-2 pe-2 font-medium">Entity</th>
                            <th className="text-start py-2 pe-2 font-medium">Price</th>
                            <th className="text-start py-2 pe-2 font-medium">Match</th>
                            <th className="text-start py-2 pe-2 font-medium">Evidence</th>
                            <th className="text-start py-2 pe-2 font-medium">Freshness</th>
                            <th className="text-start py-2 pe-2 font-medium">Guarantee / Resale</th>
                            <th className="text-start py-2 font-medium">Src</th>
                          </tr>
                        </thead>
                        <tbody>
                          {sku.offers.map((o: any, i: number) => (
                            <tr key={i} className="border-b border-zinc-800/50 align-top">
                              <td className="py-2 pe-2 text-zinc-300 leading-5">
                                {o.entity}
                                {o.flag && <div className="text-[10px] text-rose-400 mt-0.5 leading-4">⚑ {o.flag}</div>}
                              </td>
                              <td className="py-2 pe-2 font-mono text-emerald-300 whitespace-nowrap">
                                {o.price != null ? `${o.price}` : '—'}
                                {o.unit && <div className="text-[9px] text-zinc-500 font-sans leading-4">{o.unit}</div>}
                              </td>
                              <td className="py-2 pe-2">{matchBadge(o.match)}</td>
                              <td className="py-2 pe-2">{priceEvBadge(o.price_evidence)}</td>
                              <td className="py-2 pe-2 text-zinc-400 text-[10px] leading-4">{o.freshness}</td>
                              <td className="py-2 pe-2 text-zinc-500 text-[10px] leading-4">
                                {o.guarantee || 'Unknown'}
                                <span className="text-zinc-700"> / </span>
                                {o.resale || 'Unknown'}
                              </td>
                              <td className="py-2 font-mono text-[9px] text-zinc-600">{o.source}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-xs text-zinc-500 rounded-md border border-zinc-800 p-3">
                      لا عروض مُسجّلة لهذا SKU — حالة فارغة صادقة (الاسترجاع محدود لا يعني عدم الوجود).
                    </div>
                  )}

                  {/* Price intelligence */}
                  <div className="rounded-md bg-amber-950/10 border border-amber-900/40 p-3">
                    <div className="text-[11px] text-amber-400/90 mb-2 font-medium">استخبارات الأسعار (بمستويات الدليل)</div>
                    <div className="grid sm:grid-cols-2 gap-x-6 gap-y-1.5">
                      {Object.entries(pi as Record<string, unknown>).map(([k, v]) => (
                        <div key={k} className="text-[11px] leading-5 text-zinc-400">
                          <span className="text-zinc-500">{k.replace(/_/g, ' ')}: </span>
                          <span dir="ltr" className="inline-block">{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Coverage */}
                  <div className="flex flex-wrap gap-1.5">
                    {Object.entries((sku.coverage || {}) as Record<string, unknown>).map(([k, v]) => (
                      <span key={k} className="text-[10px] rounded border border-zinc-800 bg-zinc-950/60 px-1.5 py-0.5 text-zinc-500">
                        {k}: {String(v).slice(0, 60)}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </CollapsibleContent>
            </Collapsible>
          </Card>
        );
      })}

      {/* Remaining catalog */}
      <Card className="bg-zinc-900/40 border-dashed border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-400">الكتالوج المتبقي — برنامج 400+ SKU (دفعات قادمة)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {skuData.remaining_catalog.status_per_family.map((f, i) => (
              <div key={i} className="rounded border border-zinc-800/60 bg-zinc-950/40 p-2.5">
                <div className="text-[11px] text-zinc-300 leading-5 mb-1">{f.family}</div>
                <div className="text-[10px] text-zinc-600 leading-4">{f.status}</div>
              </div>
            ))}
          </div>
          <div className="text-[10px] text-zinc-600 mt-3 leading-5">
            كل حالة «Not Searched» هي حالة §15 صادقة — لا تعني أبدًا «غير موجود». {skuData.remaining_catalog.expansion_note}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
