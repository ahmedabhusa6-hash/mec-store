'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { stats, runData, skuData } from '@/lib/data';
import { statusBadge } from './shared';

export function Overview() {
  const budget = runData.budget_summary as any;
  return (
    <div className="space-y-6">
      {/* Governing formulation banner */}
      <Card className="border-emerald-900/60 bg-emerald-950/20">
        <CardContent className="p-4 sm:p-5">
          <div className="text-xs text-emerald-400 font-semibold mb-2">الصياغة الحاكمة للأسعار — تُستخدم حصريًا، ولا يُستخدم أبدًا «الأرخص عالميًا»</div>
          <p className="text-sm sm:text-base text-emerald-200 leading-7" dir="ltr">
            &ldquo;the lowest price discovered and verified within the research scope, at the time of checking, under the specified SKU and offer conditions.&rdquo;
          </p>
        </CardContent>
      </Card>

      {/* Stat grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard label="SKUs منفذة (Batch 1)" value={`${stats.skusExecuted}`} sub="من كتالوج 400+ (برنامج)" />
        <StatCard label="مراجع رسمية مقفلة" value={`${stats.anchorsLocked}/15`} sub="بأدلة مُصنّفة" accent="emerald" />
        <StatCard label="كيانات مُتحققة" value={`${stats.entitiesVerified}`} sub={`+ ${stats.entitiesUnverifiedGroups} مجموعات رصاصات غير متحققة`} accent="teal" />
        <StatCard label="عروض مُسجّلة" value={`${stats.offersCaptured}`} sub="كل عرض بشروطه المستقلة" accent="amber" />
        <StatCard label="إجراءات بحث" value={`${stats.actionsExecuted}/96`} sub="C4 · احتياطي 24 سليم" />
        <StatCard label="فرضيات مفتوحة" value={`${stats.hypothesesOpen}`} sub="H1–H4 بحالتها الصادقة" accent="amber" />
      </div>

      {/* Budget + transaction state */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-300">استهلاك ميزانية الأفعال (Action Budget)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <div className="flex justify-between text-xs text-zinc-400 mb-1">
                <span>{budget.actions_executed} / {budget.total_cap} إجراء</span>
                <span>{Math.round((budget.actions_executed / budget.total_cap) * 100)}%</span>
              </div>
              <Progress value={(budget.actions_executed / budget.total_cap) * 100} className="h-2 bg-zinc-800" />
            </div>
            <div className="text-xs text-zinc-500 leading-6">
              نجح: <span className="text-emerald-400 font-mono">64</span> · فشل: <span className="text-rose-400 font-mono">12</span> (429 rate-limit: 11 · لا نتائج: 3) · الاحتياطي <span className="text-amber-400 font-mono">24</span> لم يُمَس · سقف الفرع الواحد ≤35% مُحترم
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-300">حالة التحقق من المعاملات (Transaction Verification)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-lg">⛔</span>
              <div>
                <div className="text-sm font-semibold text-zinc-200">Not Performed — لجميع العروض</div>
                <div className="text-xs text-zinc-500 leading-6">
                  لم تُنفَّذ أي عملية شراء أو اختبار معاملة. كل الأسعار أدلة مستوى قوائم (listing-level) وليست أسعار معاملات. Advertised ≠ Transaction.
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Scope lock */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">قفل النطاق (Scope Lock) — ثوابت التشغيل</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="grid sm:grid-cols-2 gap-x-6 gap-y-2 text-xs text-zinc-400 leading-6">
            {(runData.scope_lock as any).locked.map((l: string, i: number) => (
              <li key={i} className="flex gap-2">
                <span className="text-emerald-500 shrink-0">🔒</span>
                <span>{l}</span>
              </li>
            ))}
          </ul>
          <div className="mt-4 pt-3 border-t border-zinc-800">
            <div className="text-xs text-zinc-500 mb-2">توسيعات نطاق مقترحة — <span className="text-amber-400">لم تُنفَّذ، تتطلب تفويضك</span>:</div>
            {(runData.scope_lock as any).proposed_scope_expansions.map((e: any, i: number) => (
              <div key={i} className="text-xs text-zinc-400 leading-6">• {e.proposal} — <span className="text-zinc-600">{e.reason}</span></div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Price intelligence headline per SKU */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300">خلاصة استخبارات الأسعار — أدنى عرض موثق لكل SKU (صياغة محدودة النطاق)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2.5">
            {skuData.batch1_skus.map((sku) => {
              const pi = sku.price_intelligence as any;
              const lowest = pi.lowest_verified_offer || pi.lowest_comparable_effective_acquisition_cost || 'Unknown';
              const unknown = /unknown|none/i.test(lowest);
              return (
                <div key={sku.sku_id} className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 text-xs border-b border-zinc-800/60 pb-2 last:border-0">
                  <div className="sm:w-56 shrink-0">
                    <span className="font-mono text-[10px] text-zinc-500">{sku.sku_id}</span>
                    <div className="text-zinc-300 font-medium leading-5">{sku.identity.brand} — {sku.identity.product}</div>
                  </div>
                  <div className="flex-1 text-zinc-400 leading-6">
                    {unknown ? (
                      <span className="text-zinc-500">أدنى عرض موثق: Unknown — {pi.notes ? String(pi.notes).slice(0, 90) : ''}</span>
                    ) : (
                      <span>
                        <span className="text-zinc-500">أدنى عرض موثق: </span>
                        <span className="text-emerald-300 font-medium" dir="ltr">{lowest}</span>
                      </span>
                    )}
                  </div>
                  <div className="shrink-0">{statusBadge(sku.official_anchor?.price != null ? 'Verified' : 'Retrieval-Limited')}</div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Core invariants */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardContent className="p-4">
          <div className="text-xs text-zinc-500 mb-2 leading-6">الثوابت الحاكمة المطبقة على كل صف في هذه البيانات:</div>
          <div className="text-[11px] text-zinc-400 leading-7" dir="ltr">
            Discovered ≠ Verified ≠ Supplier ≠ Upstream Source ≠ Primary Source ≠ Lowest Verified Price · Advertised Price ≠ Transaction Price · Availability ≠ Purchase · Product availability ≠ Resale Authorization · Technical similarity ≠ Business Relationship · Search failure ≠ Non-Existence
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({ label, value, sub, accent }: { label: string; value: string; sub?: string; accent?: string }) {
  const color =
    accent === 'emerald' ? 'text-emerald-400'
    : accent === 'teal' ? 'text-teal-400'
    : accent === 'amber' ? 'text-amber-400'
    : 'text-zinc-100';
  return (
    <Card className="bg-zinc-900/60 border-zinc-800">
      <CardContent className="p-3 sm:p-4">
        <div className="text-[10px] sm:text-[11px] text-zinc-500 leading-4 mb-1">{label}</div>
        <div className={`text-xl sm:text-2xl font-bold font-mono ${color}`} dir="ltr">{value}</div>
        {sub && <div className="text-[10px] text-zinc-600 mt-1 leading-4">{sub}</div>}
      </CardContent>
    </Card>
  );
}
