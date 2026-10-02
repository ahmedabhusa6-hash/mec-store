import Link from "next/link";

// FIX (UX P2): production had the default English Next.js 404 page
// ("404: This page could not be found.") inside an Arabic RTL product.
export default function NotFound() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center p-6" dir="rtl">
      <div className="max-w-md w-full text-center space-y-5">
        <div className="text-6xl font-mono font-bold text-emerald-500" dir="ltr">404</div>
        <h1 className="text-xl font-bold text-zinc-100">هذه الصفحة غير موجودة</h1>
        <p className="text-sm text-zinc-400 leading-6">
          الرابط الذي فتحته غير صحيح أو أن الصفحة نُقلت. يمكنك العودة للمتجر أو استعراض لوحة الاستخبارات.
        </p>
        <div className="flex gap-2 justify-center">
          <Link
            href="/"
            className="rounded-md bg-emerald-800 hover:bg-emerald-700 text-emerald-50 px-5 py-2.5 text-sm font-bold transition-colors"
          >
            🛒 العودة للمتجر
          </Link>
          <Link
            href="/intel"
            className="rounded-md border border-zinc-700 hover:border-zinc-500 text-zinc-300 px-5 py-2.5 text-sm transition-colors"
          >
            🔬 الاستخبارات
          </Link>
        </div>
      </div>
    </div>
  );
}
