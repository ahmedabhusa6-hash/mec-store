'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { entitiesOfficial, entitiesB2B, entitiesMarket, entitiesUnverified, unverifiedNote } from '@/lib/data';
import { statusBadge } from './shared';

type LayerKey = 'official' | 'b2b' | 'market' | 'unverified';

const LAYERS: { key: LayerKey; title: string; desc: string; color: string }[] = [
  { key: 'official', title: 'الناشرون والمصادر الرسمية', desc: 'Primary Sources — مراجع الأسعار الرسمية', color: 'text-emerald-400' },
  { key: 'b2b', title: 'طبقة B2B العلويا (API)', desc: 'Upstream infrastructure — أعمق طبقة موثقة هذا التشغيل', color: 'text-violet-400' },
  { key: 'market', title: 'الأسواق والبائعون والخدمات', desc: 'Marketplaces / Sellers / Services', color: 'text-teal-400' },
  { key: 'unverified', title: 'رصاصات غير متحققة (البذور)', desc: 'Open-Items Ledger — ليست موردين مؤكدين', color: 'text-zinc-500' },
];

export function Entities() {
  const [layer, setLayer] = useState<LayerKey>('official');
  const list = layer === 'official' ? entitiesOfficial : layer === 'b2b' ? entitiesB2B : layer === 'market' ? entitiesMarket : [];
  const unv = entitiesUnverified as any[];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {LAYERS.map((l) => (
          <button
            key={l.key}
            onClick={() => setLayer(l.key)}
            className={`rounded-md border px-3 py-1.5 text-xs transition-colors ${
              layer === l.key
                ? 'border-zinc-600 bg-zinc-800 text-zinc-100'
                : 'border-zinc-800 bg-zinc-950/40 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700'
            }`}
          >
            {l.title}
            <span className="text-[10px] text-zinc-600 ms-1.5">
              ({l.key === 'official' ? entitiesOfficial.length : l.key === 'b2b' ? entitiesB2B.length : l.key === 'market' ? entitiesMarket.length : unv.length})
            </span>
          </button>
        ))}
      </div>

      {layer !== 'unverified' ? (
        <div className="grid gap-3">
          {list.map((e: any) => (
            <Card key={e.id} className="bg-zinc-900/60 border-zinc-800">
              <CardContent className="p-4 space-y-2.5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-[10px] text-zinc-600">{e.id}</span>
                  <span className="text-sm font-semibold text-zinc-100">{e.name}</span>
                  {statusBadge(e.status.split('(')[0].trim())}
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-zinc-500 leading-5">
                  <span>النوع: <span className="text-zinc-400">{e.type}</span></span>
                  <span>الدور: <span className="text-zinc-400">{e.role}</span></span>
                  <span>الاستقلالية: <span className="text-zinc-400">{e.independence || 'N/A'}</span></span>
                </div>
                <div className="grid sm:grid-cols-2 gap-1 text-[11px] leading-5">
                  <div className="text-zinc-500">الضمان: <span className="text-zinc-400">{e.guarantee || 'Unknown'}</span></div>
                  <div className="text-zinc-500">إعادة البيع: <span className="text-zinc-400">{e.resale || 'Unknown'}</span></div>
                </div>
                {e.evidence && (
                  <div className="rounded bg-zinc-950/60 border border-zinc-800/70 p-2.5 space-y-1.5">
                    <div className="text-[10px] text-zinc-600">الأدلة (Action · المصدر · الملاحظة · المستوى · الحداثة):</div>
                    {e.evidence.map((ev: any, i: number) => (
                      <div key={i} className="text-[10px] text-zinc-400 leading-5" dir="ltr">
                        <span className="font-mono text-emerald-600">[{ev.action}]</span>{' '}
                        <span className="text-teal-500">{ev.source}</span> — {ev.observation}
                        <span className="text-zinc-600"> · {ev.evidence_level} · {ev.freshness}</span>
                      </div>
                    ))}
                  </div>
                )}
                {e.relationships && e.relationships.length > 0 && (
                  <div className="text-[10px] text-zinc-500 leading-5">
                    العلاقات: {e.relationships.map((r: any) => (
                      <span key={r.to} className="inline-block me-3">→ {r.to} ({r.type}) <Badge variant="outline" className="text-[9px] px-1 py-0 border-zinc-700 text-zinc-500">{r.status}</Badge></span>
                    ))}
                  </div>
                )}
                {e.notes && <div className="text-[10px] text-zinc-600 leading-5 border-t border-zinc-800/60 pt-2">ملاحظات: {e.notes}</div>}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-zinc-900/40 border-dashed border-zinc-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-400">رصاصات غير متحققة — من بذور المشروع ({unv.length} مجموعات)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-[11px] text-amber-500/80 leading-6 rounded border border-amber-900/40 bg-amber-950/10 p-2.5">{unverifiedNote}</div>
            <div className="overflow-x-auto">
              <table className="w-full text-[10px] min-w-[700px]">
                <thead>
                  <tr className="text-zinc-500 border-b border-zinc-800">
                    <th className="text-start py-1.5 pe-2 font-medium">ID</th>
                    <th className="text-start py-1.5 pe-2 font-medium">Name</th>
                    <th className="text-start py-1.5 pe-2 font-medium">Seed Layer</th>
                    <th className="text-start py-1.5 pe-2 font-medium">Attempts</th>
                    <th className="text-start py-1.5 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {unv.map((e) => (
                    <tr key={e.id} className="border-b border-zinc-800/40 align-top">
                      <td className="py-1.5 pe-2 font-mono text-zinc-600">{e.id}</td>
                      <td className="py-1.5 pe-2 text-zinc-400 leading-4">{e.name}</td>
                      <td className="py-1.5 pe-2 text-zinc-500">{e.seed_layer}</td>
                      <td className="py-1.5 pe-2 text-zinc-600 leading-4" dir="ltr">{(e.verification_attempts || []).join(' · ') || '—'}</td>
                      <td className="py-1.5 text-zinc-500 leading-4">{e.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
