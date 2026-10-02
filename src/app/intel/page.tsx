'use client';

import { useEffect, useState } from "react";
import Link from "next/link";
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Overview } from '@/components/intelligence/overview';
import { Skus } from '@/components/intelligence/skus';
import { Entities } from '@/components/intelligence/entities';
import { SupplyAndCoverage } from '@/components/intelligence/supply';
import { ChannelsAndEconomics } from '@/components/intelligence/channels';
import { Batch2 } from '@/components/intelligence/batch2';
import { Batch3 } from '@/components/intelligence/batch3';
import { DeepDive } from '@/components/intelligence/deep-dive';
import { Mec5 } from '@/components/intelligence/mec5';
import { Mec6 } from '@/components/intelligence/mec6';
import { Mec7 } from '@/components/intelligence/mec7';
import { Mec8 } from '@/components/intelligence/mec8';
import { DirectWave } from '@/components/intelligence/direct-wave';
import { ChannelMatrix } from '@/components/intelligence/channel-matrix';
import { Decisions } from '@/components/intelligence/decisions';
import { OpenItems } from '@/components/intelligence/open-items';
import { Audit } from '@/components/intelligence/audit';
import { runData } from '@/lib/data';

export default function Intel() {
  // FIX (P2, AUDIT-5): new Date() in render baked a server timestamp into SSR
  // HTML that mismatched on hydration. Compute once after mount.
  const [lastChecked, setLastChecked] = useState("");
  useEffect(() => {
    setLastChecked(new Date().toISOString().slice(0, 16).replace('T', ' ') + ' UTC');
  }, []);
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-md bg-emerald-950/80 border border-emerald-800 flex items-center justify-center text-emerald-400 text-sm font-bold font-mono">SI</div>
            <div>
              <h1 className="text-sm font-bold leading-5">Supplier Intelligence — مركز استخبارات الأسعار</h1>
              <div className="text-[10px] text-zinc-500 leading-4" dir="ltr">
                Adaptive Supplier Intelligence Research Engine · v4.2 Candidate · {runData.run_metadata.run_id}
              </div>
            </div>
          </div>
          <div className="ms-auto flex flex-wrap items-center gap-1.5 text-[10px]">
            <span className="rounded border border-emerald-800 bg-emerald-950/60 text-emerald-300 px-2 py-0.5">PRICE INTELLIGENCE</span>
            <span className="rounded border border-teal-800 bg-teal-950/60 text-teal-300 px-2 py-0.5">Batch 1+2 / C4</span>
            <span className="rounded border border-cyan-800 bg-cyan-950/60 text-cyan-300 px-2 py-0.5">Direct Wave B3</span>
            <span className="rounded border border-amber-800 bg-amber-950/60 text-amber-300 px-2 py-0.5">400+ SKU Program</span>
            <span className="rounded border border-rose-800 bg-rose-950/60 text-rose-300 px-2 py-0.5">ProdSeller Deep-Dive</span>
            <span className="rounded border border-amber-800 bg-amber-950/60 text-amber-300 px-2 py-0.5">MENA Expansion Ready</span>
            <Link
              href="/"
              className="rounded border border-emerald-700 bg-emerald-950/60 text-emerald-300 px-2 py-0.5 hover:border-emerald-500 transition-colors"
            >
              🛒 المتجر
            </Link>
            <span className="rounded border border-zinc-700 bg-zinc-900 text-zinc-400 px-2 py-0.5">Last Checked: {lastChecked}</span>
          </div>
        </div>
      </header>

      {/* Main — FIX (P2, AUDIT-6): /intel overflowed horizontally on mobile
          (629px content in 390px viewport). Scroll container instead of breaking layout. */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 overflow-x-auto">
        <Tabs defaultValue="mec8" dir="rtl">
          <TabsList className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-1 h-auto bg-zinc-900/70 border border-zinc-800 p-1 mb-6">
            <TabsTrigger value="mec8" className="text-xs py-2 data-[state=active]:bg-amber-950/60 data-[state=active]:text-amber-300 order-first sm:order-none border border-amber-700/60">🏅 أفضل الأسعار المعتمدة</TabsTrigger>
            <TabsTrigger value="mec7" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300 order-first sm:order-none border border-emerald-600/60">🏗️ دراسة المشروع الكاملة</TabsTrigger>
            <TabsTrigger value="mec6" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300 order-first sm:order-none border border-emerald-700/60">🔓 الأسعار الحية API</TabsTrigger>
            <TabsTrigger value="mec5" className="text-xs py-2 data-[state=active]:bg-violet-950/60 data-[state=active]:text-violet-300 order-first sm:order-none border border-violet-900/60">💳 فجوات أسعار API</TabsTrigger>
            <TabsTrigger value="deepdive" className="text-xs py-2 data-[state=active]:bg-rose-950/60 data-[state=active]:text-rose-300 sm:order-none border border-rose-900/60">🔬 البحث المتعمق</TabsTrigger>
            <TabsTrigger value="overview" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">نظرة عامة</TabsTrigger>
            <TabsTrigger value="skus" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">الـSKUs والأسعار (1)</TabsTrigger>
            <TabsTrigger value="batch2" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">الدفعة 2 (173)</TabsTrigger>
            <TabsTrigger value="batch3" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">الدفعة 3 (218) 🏁</TabsTrigger>
            <TabsTrigger value="directwave" className="text-xs py-2 data-[state=active]:bg-cyan-950/60 data-[state=active]:text-cyan-300">الموجة المباشرة 🔬</TabsTrigger>
            <TabsTrigger value="matrix" className="text-xs py-2 data-[state=active]:bg-amber-950/60 data-[state=active]:text-amber-300">مصفوفة 91 قناة + دولا 🧮</TabsTrigger>
            <TabsTrigger value="entities" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">الكيانات والأدوار</TabsTrigger>
            <TabsTrigger value="supply" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">سلسلة التوريد والتغطية</TabsTrigger>
            <TabsTrigger value="channels" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">القنوات §19 والاقتصاديات</TabsTrigger>
            <TabsTrigger value="decisions" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">القرارات D1–D7 🖋️</TabsTrigger>
            <TabsTrigger value="open" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">الفرضيات والعناصر المفتوحة</TabsTrigger>
            <TabsTrigger value="audit" className="text-xs py-2 data-[state=active]:bg-emerald-950/60 data-[state=active]:text-emerald-300">سجل التدقيق</TabsTrigger>
          </TabsList>

          <TabsContent value="mec8"><Mec8 /></TabsContent>
          <TabsContent value="overview"><Overview /></TabsContent>
          <TabsContent value="skus"><Skus /></TabsContent>
          <TabsContent value="batch2"><Batch2 /></TabsContent>
          <TabsContent value="batch3"><Batch3 /></TabsContent>
          <TabsContent value="mec7"><Mec7 /></TabsContent>
          <TabsContent value="mec6"><Mec6 /></TabsContent>
          <TabsContent value="mec5"><Mec5 /></TabsContent>
          <TabsContent value="deepdive"><DeepDive /></TabsContent>
          <TabsContent value="directwave"><DirectWave /></TabsContent>
          <TabsContent value="matrix"><ChannelMatrix /></TabsContent>
          <TabsContent value="entities"><Entities /></TabsContent>
          <TabsContent value="supply"><SupplyAndCoverage /></TabsContent>
          <TabsContent value="channels"><ChannelsAndEconomics /></TabsContent>
          <TabsContent value="decisions"><Decisions /></TabsContent>
          <TabsContent value="open"><OpenItems /></TabsContent>
          <TabsContent value="audit"><Audit /></TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800 bg-zinc-900/50 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="text-[10px] text-zinc-600 leading-5 text-center">
            مجموعة بيانات مزدوجة (Web + Markdown) دلاليًا متطابقة · كل ادعاء مادي مرتبط بحالة تحقق ودليل · لا يُستخدم أبدًا «الأرخص عالميًا» — فقط الصياغة المحدودة بالنطاق
          </div>
          <div className="text-[10px] text-zinc-700 leading-5 text-center mt-1" dir="ltr">
            Discovered ≠ Verified ≠ Supplier ≠ Upstream ≠ Primary Source · Advertised ≠ Transaction · Transaction Verification: Not Performed
          </div>
        </div>
      </footer>
    </div>
  );
}
