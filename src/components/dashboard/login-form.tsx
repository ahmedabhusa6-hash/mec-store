"use client";

/** MEC — owner login form (single-owner console). */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Lock } from "lucide-react";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const r = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const j = (await r.json()) as { ok?: boolean; error?: string };
      if (!r.ok) throw new Error(j.error ?? "فشل تسجيل الدخول");
      router.push("/dash");
      router.refresh();
    } catch (e) {
      setError(String(e instanceof Error ? e.message : e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div dir="rtl" className="min-h-screen bg-zinc-950 text-zinc-100 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-3 mb-6 justify-center">
          <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-800/80 flex items-center justify-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden>
              <path d="M3 17 L9 11 L13 15 L21 7" stroke="#34d399" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
              <circle cx="21" cy="7" r="2.2" fill="#34d399" />
            </svg>
          </div>
          <div>
            <div className="text-[18px] font-extrabold text-zinc-50">MEC Intelligence</div>
            <div className="text-[11px] text-zinc-500">لوحة تحكم المالك</div>
          </div>
        </div>

        <form onSubmit={submit} className="rounded-2xl border border-zinc-800/80 bg-[#0d1421] p-6 space-y-4">
          <div className="flex items-center gap-2 text-[12px] text-zinc-400">
            <Lock className="w-3.5 h-3.5 text-emerald-500" />
            منطقة خاصة بالمالك — مصادقة مشفرة وجلسة موقعة
          </div>

          <div>
            <label className="block text-[11.5px] text-zinc-400 mb-1.5">البريد الإلكتروني</label>
            <input
              type="email"
              dir="ltr"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-zinc-800 bg-zinc-900/60 px-3.5 py-2.5 text-[13px] text-zinc-100 focus:outline-none focus:border-emerald-800"
            />
          </div>

          <div>
            <label className="block text-[11.5px] text-zinc-400 mb-1.5">كلمة المرور</label>
            <input
              type="password"
              dir="ltr"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-zinc-800 bg-zinc-900/60 px-3.5 py-2.5 text-[13px] text-zinc-100 focus:outline-none focus:border-emerald-800"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-rose-900/60 bg-rose-950/30 px-3.5 py-2.5 text-[11.5px] text-rose-300">{error}</div>
          )}

          <button
            type="submit"
            disabled={busy}
            className="w-full flex items-center justify-center gap-2 rounded-lg border border-emerald-800/70 bg-emerald-950/50 px-4 py-2.5 text-[13.5px] font-bold text-emerald-300 hover:bg-emerald-900/50 disabled:opacity-50"
          >
            {busy && <Loader2 className="w-4 h-4 animate-spin" />}
            دخول
          </button>

          <div className="text-[10.5px] text-zinc-600 text-center leading-5">
            8 محاولات كحد أقصى في الدقيقة · كل محاولة تُسجَّل في سجل التدقيق
          </div>
        </form>

        <div className="mt-4 text-center">
          <a href="/" className="text-[11.5px] text-zinc-600 hover:text-zinc-400">← العودة إلى قاعدة الأسعار العامة</a>
        </div>
      </div>
    </div>
  );
}
