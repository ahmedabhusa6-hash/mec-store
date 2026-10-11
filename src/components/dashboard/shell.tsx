"use client";

/**
 * MEC Intelligence — owner dashboard shell (rebuild v4, 2026-10-11).
 * 11 views + owner bar (email, unread alerts badge, run-now dispatch, logout).
 */
import { useState } from "react";
import {
  LayoutDashboard, Tags, Boxes, Users, Radio, Radar, Cog, Gauge, Bell, ScrollText, Settings2,
  RefreshCw, LogOut, Play, Loader2,
} from "lucide-react";
import { OverviewView } from "./overview";
import { PricesView } from "./prices";
import { ProductsView } from "./products";
import { SuppliersView } from "./suppliers";
import { ChannelsView } from "./channels";
import { DiscoveriesView } from "./discoveries";
import { AutomationView } from "./automation";
import { QualityView } from "./quality";
import { AlertsView } from "./alerts";
import { AuditView } from "./audit";
import { SettingsView } from "./settings";
import { useApi } from "./kit";

const VIEWS = [
  { key: "overview", label: "نظرة عامة", icon: LayoutDashboard, desc: "مؤشرات حية وحالة الأتمتة" },
  { key: "prices", label: "الأسعار الحية", icon: Tags, desc: "أحدث الأسعار الموثقة لكل مورّد × منتج" },
  { key: "products", label: "المنتجات", icon: Boxes, desc: "كتالوج المنتجات المراقبة وأرخص عروضها" },
  { key: "suppliers", label: "الموردون", icon: Users, desc: "ملفات الموردين وإشاراتهم التجارية" },
  { key: "channels", label: "المصادر", icon: Radio, desc: "جرد القنوات والمجموعات والبوتات" },
  { key: "discoveries", label: "الاكتشافات والموافقات", icon: Radar, desc: "خط أنابيب المصادر الجديدة + اعتماد الانضمامات الخاصة" },
  { key: "automation", label: "الأتمتة", icon: Cog, desc: "دورات المراقبة التلقائية + تشغيل فوري" },
  { key: "quality", label: "جودة البيانات", icon: Gauge, desc: "انتعاش الأسعار وتغطية المسح والقِدم" },
  { key: "alerts", label: "التنبيهات", icon: Bell, desc: "مركز التنبيهات والأحداث الحرجة" },
  { key: "audit", label: "سجل التدقيق", icon: ScrollText, desc: "أثر كل إجراء حساس في المنصة" },
  { key: "settings", label: "الإعدادات والحوكمة", icon: Settings2, desc: "سياسات الانضمام القابلة للضبط + امتثال تلغرام" },
] as const;

type ViewKey = (typeof VIEWS)[number]["key"];

type Me = { authenticated: boolean; email: string; role: string };
type Unread = { unread: number };

export function Dashboard() {
  const [view, setView] = useState<ViewKey>("overview");
  const [dispatching, setDispatching] = useState(false);
  const [dispatchMsg, setDispatchMsg] = useState<string | null>(null);
  const current = VIEWS.find((v) => v.key === view)!;
  const { data: me } = useApi<Me>("/api/auth/me", [], 300_000);
  const { data: unreadData, refresh: refreshUnread } = useApi<Unread>("/api/admin/alerts", [], 60_000);
  const unread = unreadData?.unread ?? 0;

  async function runNow() {
    setDispatching(true);
    setDispatchMsg(null);
    try {
      const r = await fetch("/api/admin/dispatch", { method: "POST" });
      const j = (await r.json()) as { message?: string; error?: string };
      setDispatchMsg(r.ok ? (j.message ?? "تم الإطلاق") : (j.error ?? "فشل الإطلاق"));
    } catch (e) {
      setDispatchMsg("فشل الاتصال");
    } finally {
      setDispatching(false);
      setTimeout(() => setDispatchMsg(null), 6000);
    }
  }

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" });
    window.location.href = "/login";
  }

  return (
    <div dir="rtl" className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      {/* owner bar */}
      <div className="sticky top-0 z-50 bg-[#0b111c]/95 backdrop-blur border-b border-zinc-800">
        <div className="flex items-center gap-3 px-4 py-2.5">
          <Logo />
          <div className="flex-1" />
          {dispatchMsg && <span className="text-[11px] text-emerald-300">{dispatchMsg}</span>}
          <button
            onClick={runNow}
            disabled={dispatching}
            className="flex items-center gap-1.5 rounded-lg border border-emerald-800/70 bg-emerald-950/50 px-3 py-1.5 text-[11.5px] font-bold text-emerald-300 hover:bg-emerald-900/50 disabled:opacity-50 transition-colors"
          >
            {dispatching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            شغّل دورة الآن
          </button>
          <button
            onClick={() => { setView("alerts"); }}
            className="relative flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-1.5 text-[11.5px] text-zinc-300 hover:bg-zinc-800/60 transition-colors"
          >
            <Bell className="w-3.5 h-3.5" />
            التنبيهات
            {unread > 0 && (
              <span className="absolute -top-1.5 -start-1.5 min-w-4 h-4 px-1 rounded-full bg-rose-500 text-white text-[9.5px] font-bold flex items-center justify-center">
                {unread > 99 ? "99+" : unread}
              </span>
            )}
          </button>
          <span className="hidden sm:flex items-center gap-1.5 text-[11px] text-zinc-500">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            {me?.email ?? "…"}
          </span>
          <button
            onClick={logout}
            className="flex items-center gap-1.5 rounded-lg border border-zinc-800 bg-zinc-900/60 px-2.5 py-1.5 text-[11.5px] text-zinc-400 hover:text-rose-300 hover:border-rose-900/60 transition-colors"
            title="تسجيل الخروج"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
        {/* mobile nav */}
        <nav className="lg:hidden flex gap-1.5 overflow-x-auto px-3 pb-2.5 [scrollbar-width:none]">
          {VIEWS.map((v) => (
            <button
              key={v.key}
              onClick={() => setView(v.key)}
              className={`shrink-0 px-3 py-1.5 rounded-lg border text-[11.5px] font-medium transition-colors ${
                view === v.key ? "border-emerald-700 bg-emerald-950/60 text-emerald-300" : "border-zinc-800 bg-zinc-900/60 text-zinc-400"
              }`}
            >
              {v.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="flex flex-1">
        {/* sidebar (desktop) */}
        <aside className="hidden lg:flex flex-col w-64 shrink-0 border-e border-zinc-800/80 bg-[#0b111c] sticky top-0 h-screen pt-4">
          <nav className="flex-1 overflow-y-auto p-3 space-y-1 [scrollbar-width:thin]">
            {VIEWS.map((v) => {
              const Icon = v.icon;
              const active = view === v.key;
              return (
                <button
                  key={v.key}
                  onClick={() => setView(v.key)}
                  className={`w-full flex items-center gap-3 rounded-lg px-3 py-2.5 text-start transition-colors ${
                    active
                      ? "bg-emerald-950/50 text-emerald-300 border border-emerald-900/60"
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 border border-transparent"
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span className="text-[12.5px] font-medium flex-1">{v.label}</span>
                  {v.key === "alerts" && unread > 0 && (
                    <span className="min-w-4 h-4 px-1 rounded-full bg-rose-500 text-white text-[9.5px] font-bold flex items-center justify-center">
                      {unread > 99 ? "99+" : unread}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
          <div className="p-4 border-t border-zinc-800/60 text-[10px] text-zinc-600 leading-5">
            مراقب تلغرام كل 30 دقيقة (GitHub Actions) + تشغيل فوري عند الطلب → Supabase الحية → هذا الداشبورد
          </div>
        </aside>

        {/* main */}
        <main className="flex-1 min-w-0">
          <header className="hidden lg:flex items-center justify-between gap-4 px-6 py-4 border-b border-zinc-800/60">
            <div>
              <h2 className="text-[17px] font-extrabold text-zinc-50">{current.label}</h2>
              <p className="text-[12px] text-zinc-500 mt-0.5">{current.desc}</p>
            </div>
            <div className="flex items-center gap-3 text-[11px] text-zinc-500">
              <span className="flex items-center gap-1.5 text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> بيانات حية من Supabase
              </span>
              <span className="text-zinc-700">|</span>
              <span className="flex items-center gap-1">
                <RefreshCw className="w-3.5 h-3.5" /> تحديث تلقائي كل 60 ثانية
              </span>
            </div>
          </header>

          <div className="p-4 lg:p-6 max-w-[1500px]" key={view}>
            {view === "overview" && <OverviewView onNavigate={(k) => setView(k as ViewKey)} />}
            {view === "prices" && <PricesView />}
            {view === "products" && <ProductsView />}
            {view === "suppliers" && <SuppliersView />}
            {view === "channels" && <ChannelsView />}
            {view === "discoveries" && <DiscoveriesView onDispatched={refreshUnread} />}
            {view === "automation" && <AutomationView />}
            {view === "quality" && <QualityView />}
            {view === "alerts" && <AlertsView onRead={refreshUnread} />}
            {view === "audit" && <AuditView />}
            {view === "settings" && <SettingsView />}
          </div>

          <footer className="mt-auto border-t border-zinc-800/60 px-6 py-4 text-[10.5px] text-zinc-600 leading-5">
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
              <span className="text-zinc-500 font-medium">MEC — منصة استخبارات أسعار الموردين</span>
              <span>·</span>
              <span>الأسعار معلنة من المتاجر ولم تُختبر بالشراء الفعلي</span>
              <span>·</span>
              <span>حقائق فقط — نصوص الرسائل الخام محفوظة في قاعدة المالك الخاصة</span>
              <span>·</span>
              <span>الامتثال: شروط خدمة تلغرام (مراجعة 2026-10-11)</span>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}

function Logo() {
  return (
    <div className="flex items-center gap-2.5">
      <div className="w-9 h-9 rounded-lg bg-emerald-950/80 border border-emerald-800/80 flex items-center justify-center">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path d="M3 17 L9 11 L13 15 L21 7" stroke="#34d399" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="21" cy="7" r="2.2" fill="#34d399" />
        </svg>
      </div>
      <div>
        <div className="text-[14px] font-extrabold text-zinc-50 leading-4">MEC Intelligence</div>
        <div className="text-[10px] text-zinc-500 mt-0.5">استخبارات أسعار الموردين — تلغرام</div>
      </div>
    </div>
  );
}
