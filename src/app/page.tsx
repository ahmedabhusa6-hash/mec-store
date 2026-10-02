import { Store } from "@/components/store/store";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-md bg-emerald-950/80 border border-emerald-800 flex items-center justify-center text-emerald-400 text-lg font-bold">
              ⚡
            </div>
            <div>
              {/* FIX (P2, AUDIT-5/6): no h1 on the store page — SEO/semantics */}
              <h1 className="text-[15px] font-extrabold text-zinc-50 leading-5">متجر MEC الرقمي</h1>
              <div className="text-[11px] text-zinc-400">
                اشتراكات AI · بث MENA · بطاقات إقليمية — تسليم فوري
              </div>
            </div>
          </div>
          <div className="flex-1" />
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] rounded-full border border-emerald-800 bg-emerald-950/60 text-emerald-300 px-2.5 py-1">
              ⚡ تسليم ≤ 3 دقائق
            </span>
            <span className="text-[11px] rounded-full border border-cyan-800 bg-cyan-950/60 text-cyan-300 px-2.5 py-1">
              🔒 سعر مقفل عند الطلب
            </span>
            <span className="text-[11px] rounded-full border border-amber-800 bg-amber-950/60 text-amber-300 px-2.5 py-1">
              💸 كاش باك 1%
            </span>
            {/* FIX (P2, MEC-21-B): removed public /intel link — owner research panel
                (supplier intelligence) was one click from the customer storefront.
                Owner accesses it by direct URL; robots.txt disallows indexing. */}
          </div>
        </div>
      </header>

      {/* Trust strip */}
      <div className="border-b border-zinc-900 bg-zinc-900/30">
        <div className="max-w-6xl mx-auto px-4 py-2.5 grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] text-zinc-400">
          <div>
            <span className="text-zinc-200 font-bold">شراء مباشر بلا حساب:</span>{" "}
            هويتك رقم جوالك — بلا كلمات مرور
          </div>
          <div>
            <span className="text-zinc-200 font-bold">دفع مرن:</span>{" "}
            USDT TRC-20 · Binance Pay · محفظة داخلية اختيارية
          </div>
          <div>
            <span className="text-zinc-200 font-bold">ضمان:</span>{" "}
            استرداد كامل إذا تعذّر التسليم + اعتذار $1
          </div>
        </div>
      </div>

      {/* Direct download — Pre-Execution Diagnostic Report (2026-10-02) */}
      <section
        dir="rtl"
        aria-label="تحميل تقرير التشخيص ما قبل التنفيذ"
        className="border-b border-emerald-900/50 bg-gradient-to-l from-emerald-950/40 via-zinc-900/40 to-zinc-950"
      >
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="rounded-xl border border-emerald-900/60 bg-zinc-900/50 p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-emerald-950/70 border border-emerald-800 flex items-center justify-center text-2xl shrink-0" aria-hidden="true">
              📄
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-[15px] sm:text-base font-extrabold text-zinc-50 leading-6">
                تقرير التشخيص ما قبل التنفيذ — قاعدة بيانات أرخص موردي ومتاجر المنتجات والخدمات الرقمية
              </h2>
              <p className="text-xs sm:text-[13px] text-zinc-400 mt-1 leading-5">
                تدقيق كامل لبيئة التشغيل والمستودع ومصادر Notion المرجعية ومخاطر سلامة البيانات وجهوزية التنفيذ — 13 قسماً موثقاً.
              </p>
              <div className="flex flex-wrap items-center gap-1.5 mt-2.5 text-[11px]">
                <span className="rounded-full border border-zinc-700 bg-zinc-900 px-2.5 py-1 text-zinc-300">صيغة: Markdown ‏(.md)</span>
                <span className="rounded-full border border-zinc-700 bg-zinc-900 px-2.5 py-1 text-zinc-300">الحجم: ‏50.3 KB</span>
                <span className="rounded-full border border-zinc-700 bg-zinc-900 px-2.5 py-1 text-zinc-300">التاريخ: ‏2026-10-02</span>
                <span className="rounded-full border border-emerald-800 bg-emerald-950/60 text-emerald-300 px-2.5 py-1">بصمة الملف: ‏MD5 46e03c8a…9852</span>
              </div>
            </div>
            <div className="flex flex-col gap-2 shrink-0 sm:items-end">
              <Button asChild className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold shadow-lg shadow-emerald-950/50">
                <a href="/api/download/diagnostic-report" download>
                  ⬇️ تحميل مباشر
                </a>
              </Button>
              <a
                href="/reports/pre-execution-diagnostic-report-2026-10-02.md"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[11px] text-zinc-400 hover:text-emerald-300 transition-colors text-center underline underline-offset-4 decoration-zinc-700"
              >
                أو عرض النص في المتصفح ↗
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Store */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-4">
        <Store />
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800 bg-zinc-900/40">
        <div className="max-w-6xl mx-auto px-4 py-3 space-y-1.5">
          <div className="text-[11px] text-zinc-400">
            MEC — منتجات رقمية بأفضل الأسعار الموثقة · جميع الطلبات مسجلة بسجل شفافية قابل للتتبع · الأسعار تتحدّث مع كل مزامنة للموردين
          </div>
          <div className="text-[11px] text-zinc-400 leading-4">
            💳 الدفع: USDT (TRC-20) · Binance Pay — 🇸🇦 التسعير بالريال لعملاء +966 · 🌐 بالدولار لغيرها — ⏱️ إعادة تدوير رأس المال فورياً — نموذج JIT بلا مخزون
          </div>
          {/* FIX (P1, AUDIT-1 G5): zero legal pages — footer referenced consent
              with no terms/privacy/refund documents. */}
          <div className="flex flex-wrap items-center gap-3 text-[11px] pt-1">
            <Link href="/terms" className="text-zinc-400 hover:text-emerald-300 transition-colors">الشروط والأحكام</Link>
            <span className="text-zinc-700">·</span>
            <Link href="/privacy" className="text-zinc-400 hover:text-emerald-300 transition-colors">سياسة الخصوصية</Link>
            <span className="text-zinc-700">·</span>
            <Link href="/refund" className="text-zinc-400 hover:text-emerald-300 transition-colors">الاستبدال والاسترداد</Link>
            {/* FIX (P2, MEC-21-B): no support channel existed anywhere — highest
                trust-per-line-of-code for KSA/YE. Env-configured; hidden when unset. */}
            {process.env.NEXT_PUBLIC_SUPPORT_URL && (
              <>
                <span className="text-zinc-700">·</span>
                <a
                  href={process.env.NEXT_PUBLIC_SUPPORT_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-emerald-400 hover:text-emerald-300 transition-colors font-bold"
                >
                  💬 الدعم الفني
                </a>
              </>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}
