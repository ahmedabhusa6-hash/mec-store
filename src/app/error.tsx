"use client";

// NEW (P2, AUDIT-5): no error.tsx existed — an unhandled render error meant a
// white screen with zero guidance. Arabic-first error boundary with retry.
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center px-4" dir="rtl">
      <div className="max-w-md w-full rounded border border-rose-900/60 bg-zinc-900/60 p-6 space-y-4">
        <div className="text-2xl">⚠️</div>
        <h2 className="text-base font-bold text-rose-300">حدث خطأ غير متوقع</h2>
        <p className="text-[12.5px] text-zinc-400 leading-6">
          تعذّر عرض هذه الصفحة حاليًا. ليس هناك أي تأثير على أموالك أو طلباتك — كل العمليات المالية مسجّلة في سجل قابل للتدقيق.
        </p>
        <div className="flex gap-2">
          <button
            onClick={reset}
            className="h-10 px-4 rounded bg-emerald-900 hover:bg-emerald-800 text-emerald-100 text-xs font-bold transition-colors"
          >
            🔄 إعادة المحاولة
          </button>
          <a
            href="/"
            className="h-10 px-4 rounded border border-zinc-700 hover:border-zinc-500 text-zinc-300 text-xs leading-10 transition-colors"
          >
            العودة للمتجر
          </a>
        </div>
        {error.digest && (
          <div className="text-[10.5px] text-zinc-600 font-mono" dir="ltr">ref: {error.digest}</div>
        )}
      </div>
    </div>
  );
}
