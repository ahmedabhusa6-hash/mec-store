"use client";

// MEC Store — reconstructed 1:1 from the deployed production bundle
// (research/live_capture/store_component_beautified.js) + hardening:
// - Ops panel now sends x-admin-token (admin endpoints are auth-gated)
// - all texts/labels/classes preserved from the live Arabic RTL design

import { useState, useEffect, useCallback, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Chain = { supplier: string; name: string; stock: number | null };
type Product = {
  slug: string; name: string; aliases: string; family: string; sourceTier: string; officialUsd: number | null;
  chain: Chain[]; prices: Record<string, { price: number; currency: string }>;
};
type CatalogData = { ok: boolean; mode: string; families: string[]; lastSyncAt: string | null; products: Product[] };
type PaymentInfo = { rail: string; network: string; address: string; amount: number; centsCode: number; note: string; instructions: string };
type OrderInfo = {
  publicId: string; product: string; family: string; phoneMasked: string; region: string;
  currency: string; priceLocked: number; amountUsd: number; rail: string; status: string; statusAr: string;
  payAddress: string | null; payAmount: number | null; winner: string | null;
  deliveredPayload: string | null; deliveredAt: string | null; cashback: number; apology: number; createdAt: string;
};
type Step = { supplier: string; step: string; stepAr: string; status: string; latencyMs: number | null; message: string | null };
type Tx = { type: string; typeAr: string; amount: number; note: string | null; at: string };
type OrderSummary = { publicId: string; product: string; status: string; statusAr: string; currency: string; priceLocked: number; amountUsd: number; rail: string; createdAt: string };
type AdminStats = {
  mode: string;
  ps: { live: boolean; balanceUsd: number; membership: string; username: string };
  suppliers: { code: string; name: string; kind: string; active: boolean; score: number; failCount: number; circuitOpen: boolean; openUntil: string | null; chainCount: number }[];
  attemptStats: { supplierCode: string; status: string; _count: number }[];
  orders: { total: number; recent: { publicId: string; product: string; phone: string; currency: string; price: number; status: string; winner: string | null }[] };
  syncs: { ok: boolean; matched: number | null; changed: number | null; inStockNow: number | null; balanceUsd: number | null; message: string | null; at: string }[];
  waitlistTotal: number;
};

const REGION_LABELS: Record<string, string> = {
  SA: "🇸🇦 السعودية — ر.س",
  YE: "🇾🇪 اليمن — $",
  WW: "🌍 دولي — $",
};

const TIER_LABELS: Record<string, string> = { ps: "AI/SaaS", turgame: "بث وبطاقات" };

function fmt(price: number, currency: string) {
  return currency === "SAR" ? `${price} ر.س` : `$${price.toFixed(2)}`;
}

/**
 * FIX (P1, AUDIT-5): fetch wrapper previously had no res.ok check, no
 * try/catch, no JSON guard — a network error mid-checkout left the buy
 * button stuck busy forever and the order poll threw unhandled every 2.5s.
 * Now never throws: network/parse failures return {ok:false, error}.
 */
async function api(path: string, body?: unknown, headers?: Record<string, string>): Promise<any> {
  try {
    const res = await fetch(path, body !== undefined
      ? { method: "POST", headers: { "Content-Type": "application/json", ...headers }, body: JSON.stringify(body) }
      : { headers });
    const data = await res.json().catch(() => null);
    if (data === null) return { ok: false, error: "استجابة غير صالحة من الخادم — أعد المحاولة" };
    return data;
  } catch {
    return { ok: false, error: "تعذّر الاتصال — تحقق من الشبكة وأعد المحاولة" };
  }
}

function getAdminToken(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("mec-admin-token") ?? "";
}

// ---------------- Store grid ----------------
function StoreGrid({ data, region, hasPhone, phone, onBuy, onRefresh }: {
  data: CatalogData; region: string; hasPhone: boolean; phone: string | null;
  onBuy: (p: Product) => void; onRefresh: () => void;
}) {
  const [family, setFamily] = useState("الكل");
  const [q, setQ] = useState("");
  // FIX (P2, MEC-21-E G12): OOS waitlist join state (was a dead disabled button)
  const [wlBusy, setWlBusy] = useState<string | null>(null);
  const [wlDone, setWlDone] = useState<Record<string, string>>({});
  const joinWaitlist = async (p: Product) => {
    if (!phone) {
      setWlDone((m) => ({ ...m, [p.slug]: "⚠️ سجّل رقم جوالك من الأعلى أولًا — سيصلك التنبيه فور التوفر" }));
      return;
    }
    setWlBusy(p.slug);
    const res = await api("/api/store/waitlist", { phone, slug: p.slug });
    setWlBusy(null);
    setWlDone((m) => ({ ...m, [p.slug]: res.ok ? res.note : res.error || "تعذّر التسجيل — أعد المحاولة" }));
  };
  // FIX (MEC-21-B): Arabic search — 25/37 names are Latin-only supplier jargon;
  // Arabic queries («نتفلكس»، «كانفا») previously returned a silent blank grid.
  const filtered = data.products.filter(
    (p) => (family === "الكل" || p.family === family) &&
      (!q.trim() ||
        p.name.toLowerCase().includes(q.trim().toLowerCase()) ||
        (p.aliases ?? "").toLowerCase().includes(q.trim().toLowerCase()))
  );

  return (
    <Card className="bg-zinc-900/60 border-zinc-800">
      <CardContent className="p-3 space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <div className="text-sm font-bold text-zinc-100">
            🛒 المتجر — {data.products.length} منتجًا من عالمين
          </div>
          <Button size="sm" variant="ghost" className="text-[11px] text-zinc-400 h-7" onClick={onRefresh}>
            🔄 تحديث المزامنة
          </Button>
        </div>
        <div className="flex flex-wrap gap-1.5 items-center">
          <Input
            dir="rtl"
            aria-label="البحث في المتجر"
            className="flex-1 min-w-40 h-9 text-xs bg-zinc-950 border-zinc-700"
            placeholder="ابحث عربيًا أو إنجليزيًا… (شات جي بي تي، نتفلكس، ChatGPT…)"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          {["الكل", ...data.families].map((f) => (
            <button
              key={f}
              onClick={() => setFamily(f)}
              className={`text-[11px] rounded-full border px-2.5 py-1.5 transition-colors ${
                family === f
                  ? "border-emerald-600 bg-emerald-950/70 text-emerald-300"
                  : "border-zinc-700 bg-zinc-950 text-zinc-400 hover:border-zinc-600"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {filtered.map((p) => {
            const price = p.prices[region] ?? p.prices.WW;
            const inStockChain = p.chain.filter((c) => c.stock !== 0);
            const availability = inStockChain.length === 0
              ? { ok: false, label: "نفد حاليًا" }
              : inStockChain[0].stock == null
                ? { ok: true, label: "متوفر (يُتحقق لحظة الطلب)" }
                : { ok: true, label: `متوفر — ${inStockChain.length} ${inStockChain.length > 1 ? "موردين" : "مورد"}` };
            const discount = p.officialUsd && price?.currency === "USD" && p.officialUsd > 2.5 * price.price
              ? Math.round((1 - price.price / p.officialUsd) * 100)
              : null;
            return (
              <div
                key={p.slug}
                className={`rounded border border-zinc-800 bg-zinc-950/70 p-3 flex flex-col gap-2 ${availability.ok ? "" : "opacity-60"}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="text-[12.5px] font-bold text-zinc-100 leading-5">{p.name}</div>
                  <Badge variant="outline" className="text-[11px] shrink-0 border-zinc-700 bg-zinc-900 text-zinc-400">
                    {TIER_LABELS[p.sourceTier] ?? p.sourceTier}
                  </Badge>
                </div>
                <div className="flex items-center justify-between gap-2">
                  <div className="text-lg font-mono font-bold text-emerald-400" dir="ltr">
                    {fmt(price.price, price.currency)}
                  </div>
                  {discount != null && (
                    <Badge variant="outline" className="text-[11px] bg-rose-950/70 text-rose-300 border border-rose-800">
                      −{discount}% رسمي
                    </Badge>
                  )}
                </div>
                <div className="flex items-center justify-between gap-2">
                  <span className={`text-[11px] ${availability.ok ? "text-emerald-500" : "text-rose-400"}`}>
                    ● {availability.label}
                  </span>
                  <span className="text-[11px] text-zinc-400">
                    {p.chain.length > 1 ? `سلسلة ${p.chain.length} موردين` : "مورد واحد"}
                  </span>
                </div>
                <Button
                  className="w-full h-11 text-xs bg-emerald-900 hover:bg-emerald-800 text-emerald-100"
                  disabled={!availability.ok && wlBusy === p.slug}
                  onClick={() => (availability.ok ? onBuy(p) : joinWaitlist(p))}
                >
                  {availability.ok
                    ? "🛒 اشترِ الآن — تسليم ≤3 دقائق"
                    : wlBusy === p.slug ? "⏳ جارٍ تسجيلك…" : "🔔 نفد — انضم لقائمة الانتظار"}
                </Button>
                {wlDone[p.slug] && (
                  <div className="text-[11px] text-amber-300 leading-4">{wlDone[p.slug]}</div>
                )}
              </div>
            );
          })}
        </div>
        {q.trim() && filtered.length === 0 && (
          <div className="text-[11px] text-zinc-400 bg-zinc-950/70 border border-zinc-800 rounded px-3 py-2.5">
            🔍 لا نتائج — جرّب اسمًا عربيًا (شات جي بي تي، نتفلكس، كانفا) أو إنجليزيًا (ChatGPT، Netflix، Canva)
          </div>
        )}
        {!hasPhone && (
          <div className="text-[11px] text-amber-400 bg-amber-950/30 border border-amber-900/50 rounded px-2.5 py-1.5">
            ⚠️ الأسعار معروضة بالدولار العالمي — سجّل جوالك (+966 / +967) لتحصل على سعر منطقتك
          </div>
        )}
        <div className="text-[11px] text-zinc-400 leading-4">
          الأسعار مقفلة لحظة الشراء · التسليم آلي عبر الموجّه متعدد الموردين · الوضع التجريبي يسلّم إيصالات موسومة (SANDBOX) والوضع الحي يشتري من ProdSeller فورًا
        </div>
      </CardContent>
    </Card>
  );
}

// ---------------- Checkout panel ----------------
const RAILS = [
  { id: "wallet", name: "👛 المحفظة", desc: "خصم فوري + كاش باك 1% + استرداد لحظي — الأسرع" },
  { id: "trc20", name: "💵 USDT TRC-20", desc: "أرسل للعنوان المعروض — تأكيد ببلوك واحد (~1-3 د) — رسوم شبكة ~$1" },
  { id: "binance_pay", name: "🔵 Binance Pay", desc: "تأكيد لحظي 0 رسوم — يتطلب حساب تاجر عند التفعيل الحي" },
];

function CheckoutPanel({ product, phone, region, balance, onDone, onCancel, onNeedWallet }: {
  product: Product; phone: string; region: string; balance: number | null;
  onDone: (publicId: string) => void; onCancel: () => void; onNeedWallet: () => void;
}) {
  const [rail, setRail] = useState("wallet");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [payment, setPayment] = useState<PaymentInfo | null>(null);
  const [publicId, setPublicId] = useState<string | null>(null);

  const price = product.prices[region] ?? product.prices.WW;
  const usd = region === "SA" ? Number((price.price / 3.75).toFixed(2)) : Number(price.price.toFixed(2));
  const canAfford = balance != null && balance >= usd;

  const submit = async () => {
    if (!phone) return setError("سجّل رقم جوالك أولًا");
    setBusy(true); setError(null);
    const res = await api("/api/store/checkout", { slug: product.slug, phone, rail });
    setBusy(false);
    if (res.ok) {
      if (res.payment) { setPayment(res.payment); setPublicId(res.publicId); }
      else onDone(res.publicId);
    } else setError(res.error || "خطأ غير متوقع");
  };

  return (
    <Card className="bg-zinc-900/60 border-emerald-900/50">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-sm font-bold text-zinc-100">🔒 إتمام الشراء — سعر مقفل مضمون</div>
          <Button size="sm" variant="ghost" className="text-xs text-zinc-400 h-8" onClick={onCancel}>
            → رجوع للمتجر
          </Button>
        </div>
        <div className="rounded border border-zinc-800 bg-zinc-950/70 p-3 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[13px] font-bold text-zinc-100">{product.name}</span>
            <Badge variant="outline" className="text-[11px] border-zinc-700 text-zinc-400">{product.family}</Badge>
          </div>
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-zinc-400">{REGION_LABELS[region]}</span>
            <div className="flex items-center gap-2">
              {region === "SA" && (
                <span className="text-zinc-400 text-[11px]" dir="ltr">≈ ${usd.toFixed(2)}</span>
              )}
              <span className="text-xl font-mono font-bold text-emerald-400" dir="ltr">
                {fmt(price.price, price.currency)}
              </span>
            </div>
          </div>
          <div className="text-[11px] text-zinc-400">🔒 هذا السعر مقفول لطلبك — حتى لو تغيرت الأسعار بعده</div>
        </div>

        {payment ? (
          <div className="rounded border border-amber-800/60 bg-amber-950/30 p-3 space-y-2">
            <div className="text-[12px] font-bold text-amber-300">📥 تعليمات الدفع ({payment.network})</div>
            <div className="text-[11px] text-zinc-300 leading-5">
              العنوان: <span className="font-mono text-cyan-300 break-all" dir="ltr">{payment.address}</span>
              <br />
              المبلغ بالضبط:{" "}
              <span className="font-mono text-emerald-300" dir="ltr">${payment.amount.toFixed(2)}</span>
              <span className="text-zinc-400"> (السنتات المميزة تربط التحويل بطلبك)</span>
            </div>
            <div className="text-[11px] text-zinc-400 leading-4">{payment.instructions}</div>
            {publicId && (
              <Button className="w-full h-11 bg-emerald-800 hover:bg-emerald-700 text-emerald-50" onClick={() => onDone(publicId)}>
                ▶️ متابعة إلى صفحة الطلب ← تأكيد الدفع من هناك
              </Button>
            )}
          </div>
        ) : (
          <>
            <div className="space-y-1.5">
              {RAILS.map((r) => {
                const disabledWallet = r.id === "wallet" && !canAfford;
                return (
                  <button
                    key={r.id}
                    onClick={() => !disabledWallet && setRail(r.id)}
                    className={`w-full text-start rounded border px-3 py-2.5 transition-colors ${
                      rail === r.id ? "border-emerald-600 bg-emerald-950/50" : "border-zinc-800 bg-zinc-950/60 hover:border-zinc-700"
                    } ${disabledWallet ? "opacity-50" : ""}`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[12.5px] font-bold text-zinc-100">{r.name}</span>
                      {r.id === "wallet" && (
                        <span className={`text-[11px] font-mono ${canAfford ? "text-emerald-400" : "text-rose-400"}`} dir="ltr">
                          {balance != null ? `$${balance.toFixed(2)}` : "—"} / $ {usd.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-zinc-400 leading-4 mt-0.5">{r.desc}</div>
                  </button>
                );
              })}
            </div>
            {rail === "wallet" && !canAfford && (
              <Button variant="outline" className="w-full h-10 text-xs border-amber-700 text-amber-300" onClick={onNeedWallet}>
                الرصيد غير كافٍ — اشحن المحفظة (إيداع تجريبي فوري في sandbox)
              </Button>
            )}
            {error && (
              <div className="text-[11px] text-rose-400 bg-rose-950/40 border border-rose-900/50 rounded px-2.5 py-1.5">
                {error}
              </div>
            )}
            <Button
              className="w-full h-12 text-sm font-bold bg-emerald-800 hover:bg-emerald-700 text-emerald-50"
              disabled={busy || (rail === "wallet" && !canAfford)}
              onClick={submit}
            >
              {busy ? "⏳ جارٍ الإنشاء…" : rail === "wallet" ? "🚀 ادفع من المحفظة وشراء المورد يبدأ فورًا" : "📝 إنشاء الطلب وتعليمات الدفع"}
            </Button>
          </>
        )}
        <div className="text-[11px] text-zinc-400 leading-4">
          بالضغط أنت توافق على: التسليم آلي عبر سلسلة الموردين (قد يتبدّل المورد تلقائيًا عند النفاد بنفس الجودة) · الفشل الكامل = استرداد لحظي + رصيد اعتذار $1
        </div>
      </CardContent>
    </Card>
  );
}

// ---------------- Order view ----------------
const STEP_ICON: Record<string, string> = { ok: "✅", skip: "⏭️", fail: "❌" };
const STATUS_CLASS: Record<string, string> = {
  pending_payment: "border-amber-700 bg-amber-950/60 text-amber-300",
  paid: "border-cyan-700 bg-cyan-950/60 text-cyan-300",
  routing: "border-violet-700 bg-violet-950/60 text-violet-300",
  delivered: "border-emerald-700 bg-emerald-950/60 text-emerald-300",
  failed: "border-rose-800 bg-rose-950/60 text-rose-300",
};

function OrderView({ publicId, phone, onBack, onWalletRefresh }: {
  publicId: string; phone: string; onBack: () => void; onWalletRefresh: () => void;
}) {
  const [order, setOrder] = useState<OrderInfo | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);
  const [notice, setNotice] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmBusy, setConfirmBusy] = useState(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useCallback(async () => {
    const res = await api(`/api/store/orders/${publicId}?phone=${encodeURIComponent(phone)}`);
    if (res.ok) { setOrder(res.order); setSteps(res.transparency || []); setError(null); }
    else if (res.status === 404 || res.error?.includes("غير موجود")) setError(res.error ?? "الطلب غير موجود");
    return res;
  }, [publicId, phone]);

  useEffect(() => {
    let active = true;
    load();
    timer.current = setInterval(async () => {
      const res = await load();
      if (active && res.ok && !['pending_payment', 'paid', 'routing'].includes(res.order?.status ?? "")) {
        if (timer.current) clearInterval(timer.current);
        onWalletRefresh();
      }
    }, 2500);
    return () => { active = false; if (timer.current) clearInterval(timer.current); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [publicId]);

  const simulateConfirm = async () => {
    if (confirmBusy) return;
    setConfirmBusy(true);
    await api("/api/store/payments/confirm", { publicId, ref: `${order?.rail}-${publicId}` });
    await load();
    setConfirmBusy(false);
  };
  const restock = async () => {
    const res = await api(`/api/store/orders/${publicId}/restock?phone=${encodeURIComponent(phone)}`, {});
    if (res.ok) setNotice(`تم التسجيل ✓ — ${res.waitingAhead} شخصًا قبلك في القائمة، سننبهك عند التوفير`);
  };

  const progress = order ? [
    { key: "pending_payment", label: "بانتظار الدفع", done: order.status !== "pending_payment" },
    { key: "paid", label: "تم الدفع", done: ["routing", "delivered", "failed"].includes(order.status) },
    { key: "routing", label: "الموجّه يشتري", done: ["delivered", "failed"].includes(order.status) },
    { key: "final", label: order.status === "failed" ? "استرداد كامل" : "تم التسليم", done: ["delivered", "failed"].includes(order.status) },
  ] : [];

  return (
    <Card className="bg-zinc-900/60 border-emerald-900/50">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-sm font-bold text-zinc-100">
            📦 الطلب <span className="font-mono text-cyan-300" dir="ltr">{publicId}</span>
          </div>
          <Button size="sm" variant="ghost" className="text-xs text-zinc-400 h-8" onClick={onBack}>
            → رجوع للمتجر
          </Button>
        </div>
        {error && (
          <div className="rounded border border-rose-800/60 bg-rose-950/30 p-3 text-[12px] text-rose-300">
            {error}
          </div>
        )}
        {order && (
          <>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline" className={`text-[11px] ${STATUS_CLASS[order.status]}`}>{order.statusAr}</Badge>
              <span className="text-[11px] text-zinc-400">{order.product}</span>
              <span className="text-[11px] font-mono text-emerald-400" dir="ltr">
                {order.currency === "SAR" ? `${order.priceLocked} ر.س` : `$${order.priceLocked}`}
              </span>
              <span className="text-[11px] text-zinc-400" dir="ltr">{order.phoneMasked}</span>
            </div>
            <div className="flex items-center gap-1">
              {progress.map((s) => (
                <div key={s.key} className="flex-1">
                  <div className={`h-1.5 rounded-full ${s.done ? "bg-emerald-600" : "bg-zinc-800"}`} />
                  <div className={`text-[11px] mt-1 text-center ${s.done ? "text-emerald-400" : "text-zinc-400"}`}>{s.label}</div>
                </div>
              ))}
            </div>
            {order.status === "pending_payment" && order.payAddress && (
              <div className="rounded border border-amber-800/60 bg-amber-950/30 p-3 space-y-2">
                <div className="text-[11px] text-zinc-300 leading-5">
                  أرسل <span className="font-mono text-emerald-300" dir="ltr">${order.payAmount?.toFixed(2)}</span> إلى:
                  <div className="font-mono text-cyan-300 text-[11px] break-all mt-1" dir="ltr">{order.payAddress}</div>
                </div>
                <Button className="w-full h-10 text-xs bg-amber-800 hover:bg-amber-700 text-amber-50" disabled={confirmBusy} onClick={simulateConfirm} aria-label="تأكيد الدفع في الوضع التجريبي">
                  {confirmBusy ? "⏳ جارٍ التأكيد…" : "▶️ تأكيد الدفع (محاكاة sandbox) — يطلق الموجّه فورًا"}
                </Button>
              </div>
            )}
            {order.status === "delivered" && order.deliveredPayload && (
              <div className="rounded border border-emerald-700 bg-emerald-950/40 p-3 space-y-2">
                <div className="text-[12px] font-bold text-emerald-300">
                  🎉 تم التسليم عبر {order.winner === "ps" ? "ProdSeller (شراء آلي)" : order.winner === "sv" ? "StackVault" : order.winner === "turgame" ? "Turgame" : order.winner}
                </div>
                <button
                  onClick={() => {
                    if (order?.deliveredPayload) {
                      navigator.clipboard?.writeText(order.deliveredPayload);
                      setCopied(true);
                      setTimeout(() => setCopied(false), 1800);
                    }
                  }}
                  className="w-full text-start rounded border border-emerald-800 bg-zinc-950 px-3 py-2.5 font-mono text-[12px] text-emerald-200 break-all hover:border-emerald-600"
                  dir="ltr"
                >
                  {order.deliveredPayload}
                </button>
                <div className="text-[11px] text-zinc-400">
                  {copied ? "✓ نُسخ" : "اضغط للنسخ"} · محفوظ في سجل طلبك دائمًا
                </div>
                {order.cashback > 0 && (
                  <div className="text-[11px] text-amber-300">
                    🪙 كاش باك 1% = <span className="font-mono" dir="ltr">${order.cashback.toFixed(2)}</span> أُضيف لمحفظتك
                  </div>
                )}
              </div>
            )}
            {order.status === "failed" && (
              <div className="rounded border border-rose-800 bg-rose-950/40 p-3 space-y-2">
                <div className="text-[12px] font-bold text-rose-300">
                  تعذّر التنفيذ من كل الموردين — المبلغ استُرد كاملًا لمحفظتك
                </div>
                <div className="text-[11px] text-zinc-300 leading-5">
                  💵 استرداد <span className="font-mono text-emerald-300" dir="ltr">${order.amountUsd.toFixed(2)}</span> + 🎁 رصيد اعتذار{" "}
                  <span className="font-mono text-emerald-300" dir="ltr">$1.00</span>
                </div>
                {notice ? (
                  <div className="text-[11px] text-emerald-300">{notice}</div>
                ) : (
                  <Button size="sm" className="h-9 text-[11px] bg-zinc-800 hover:bg-zinc-700 text-zinc-200" onClick={restock}>
                    🔔 أعلمني عند التوفير
                  </Button>
                )}
              </div>
            )}
            {["paid", "routing"].includes(order.status) && (
              <div className="rounded border border-violet-800/60 bg-violet-950/30 p-2.5 text-[11px] text-violet-300 animate-pulse">
                ⚙️ الموجّه يعمل الآن: يفحص السلسلة ← حارس الهامش ← حارس الرصيد الحي ← الشراء… (تلقائي بالكامل)
              </div>
            )}
            <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5">
              <div className="text-[11px] font-bold text-zinc-300 mb-1.5">
                🔍 شفافية الموجّه — ما يحدث خلف الكواليس (حقيقي 100%)
              </div>
              {steps.length === 0 ? (
                <div className="text-[11px] text-zinc-400">لا محاولات بعد…</div>
              ) : (
                <div className="space-y-1 max-h-64 overflow-y-auto">
                  {steps.map((s, i) => (
                    <div key={i} className="flex items-start gap-2 text-[11px] leading-5">
                      <span>{STEP_ICON[s.status] ?? "•"}</span>
                      <div className="flex-1">
                        <span className="text-zinc-300 font-bold">{s.supplier}</span>
                        <span className="text-zinc-400"> — {s.stepAr}</span>
                        {s.latencyMs != null && (
                          <span className="text-zinc-400 font-mono" dir="ltr"> ({s.latencyMs}ms)</span>
                        )}
                        {s.message && <div className="text-zinc-400 text-[11px] leading-4">{s.message}</div>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ---------------- Wallet panel ----------------
const TX_CLASS: Record<string, string> = {
  deposit: "text-emerald-400", purchase: "text-rose-300", refund: "text-emerald-300",
  cashback: "text-amber-300", apology: "text-amber-300",
};

function WalletPanel({ phone, onBalance, onOpenOrder }: { phone: string; onBalance: (b: number) => void; onOpenOrder: (publicId: string) => void }) {
  const [balance, setBalance] = useState(0);
  const [txs, setTxs] = useState<Tx[]>([]);
  const [orders, setOrders] = useState<OrderSummary[]>([]);
  const [amount, setAmount] = useState("25");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const res = await api(`/api/wallet?phone=${encodeURIComponent(phone)}`);
    if (res.ok) { setBalance(res.balance); setTxs(res.txs); onBalance(res.balance); }
    const resOrders = await api(`/api/store/orders?phone=${encodeURIComponent(phone)}`);
    if (resOrders.ok) setOrders(resOrders.orders ?? []);
  }, [phone, onBalance]);

  useEffect(() => { refresh(); }, [refresh]);

  const deposit = async () => {
    const n = Number(amount);
    if (!(n >= 5) || n > 500) return setMsg("الإيداع بين $5 و$500");
    setBusy(true); setMsg(null);
    const res = await api("/api/wallet/deposit", { phone, amountUsd: n });
    setBusy(false);
    setMsg(res.ok ? `✓ ${res.note}` : res.error || "فشل");
    await refresh();
  };

  return (
    <Card className="bg-zinc-900/60 border-amber-900/50">
      <CardContent className="p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="text-sm font-bold text-zinc-100">👛 محفظتك — رصيد شرائي بالدولار</div>
          <div className="text-2xl font-mono font-bold text-emerald-400" dir="ltr">${balance.toFixed(2)}</div>
        </div>
        <div className="rounded border border-amber-900/50 bg-amber-950/20 p-2.5 space-y-2">
          <div className="text-[11px] font-bold text-amber-300">إيداع (USDT TRC-20 / Binance Pay)</div>
          <div className="flex gap-2">
            <Input
              dir="ltr" type="number" min="5" max="500" aria-label="مبلغ الإيداع بالدولار"
              className="flex-1 h-10 font-mono bg-zinc-950 border-zinc-700"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            <Button className="h-10 bg-amber-800 hover:bg-amber-700 text-amber-50" disabled={busy} onClick={deposit}>
              {busy ? "⏳" : "إيداع"}
            </Button>
          </div>
          <div className="flex gap-1.5">
            {[10, 25, 50, 100].map((v) => (
              <button
                key={v}
                onClick={() => setAmount(String(v))}
                className="text-[11px] rounded border border-zinc-700 bg-zinc-950 px-2 py-1 text-zinc-400 hover:border-amber-700"
                dir="ltr"
              >
                ${v}
              </button>
            ))}
          </div>
          <div className="text-[11px] text-zinc-400 leading-4">
            🧪 الوضع التجريبي: إيداع فوري موسوم. في الوضع الحي: عنوان إيداع مخصص + تأكيد on-chain ببلوك واحد. حدود الإيداع: $5–$500. الرصيد للاستخدام الشرائي — استرداد نقدي كامل عند الطلب خلال 24 ساعة.
          </div>
          {msg && <div className="text-[11px] text-emerald-300">{msg}</div>}
        </div>
        <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5">
          <div className="text-[11px] font-bold text-zinc-300 mb-1.5">📦 طلباتك الأخيرة (سجل دائم)</div>
          {orders.length === 0 ? (
            <div className="text-[11px] text-zinc-400">لا طلبات بعد</div>
          ) : (
            <div className="space-y-1 max-h-60 overflow-y-auto">
              {orders.map((o) => (
                <button
                  key={o.publicId}
                  onClick={() => onOpenOrder(o.publicId)}
                  className="w-full flex items-center justify-between gap-2 text-[11px] border-b border-zinc-900 pb-1 hover:border-zinc-700 transition-colors text-start"
                >
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-cyan-300" dir="ltr">{o.publicId}</span>
                    <span className="text-zinc-400">{o.product.slice(0, 24)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-zinc-400" dir="ltr">
                      {o.currency === "SAR" ? `${o.priceLocked} ر.س` : `$${o.amountUsd.toFixed(2)}`}
                    </span>
                    <span className={`font-bold ${ORDER_STATUS_CLASS[o.status] ?? "text-zinc-400"}`}>{o.statusAr}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
        <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5">
          <div className="text-[11px] font-bold text-zinc-300 mb-1.5">📓 سجل الحركات (قيد مزدوج — الرصيد مشتق من السجل)</div>
          {txs.length === 0 ? (
            <div className="text-[11px] text-zinc-400">لا حركات بعد</div>
          ) : (
            <div className="space-y-1 max-h-60 overflow-y-auto">
              {txs.map((t, i) => (
                <div key={i} className="flex items-center justify-between gap-2 text-[11px] border-b border-zinc-900 pb-1">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-[11px] border-zinc-700 text-zinc-400">{t.typeAr}</Badge>
                    <span className="text-zinc-400 text-[11px]">
                      {new Date(t.at).toLocaleString("ar", { hour: "2-digit", minute: "2-digit", month: "numeric", day: "numeric" })}
                    </span>
                  </div>
                  <span className={`font-mono ${TX_CLASS[t.type] ?? "text-zinc-300"}`} dir="ltr">
                    {t.amount > 0 ? "+" : ""}${t.amount.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// ---------------- Ops panel (admin — token-gated) ----------------
const ORDER_STATUS_CLASS: Record<string, string> = {
  delivered: "text-emerald-400", failed: "text-rose-400", pending_payment: "text-amber-400",
  paid: "text-cyan-400", routing: "text-violet-400", refunded: "text-zinc-400",
};

function OpsPanel({ onSyncDone }: { onSyncDone: () => void }) {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [token, setToken] = useState("");
  const [authError, setAuthError] = useState(false);

  useEffect(() => { setToken(getAdminToken()); }, []);

  const load = useCallback(async () => {
    const res = await api("/api/admin/stats", undefined, { "x-admin-token": getAdminToken() });
    if (res.ok) { setStats(res); setAuthError(false); }
    else if (res.error?.includes("غير مصرح")) setAuthError(true);
  }, []);
  useEffect(() => { load(); }, [load]);

  const saveToken = async (t: string) => {
    localStorage.setItem("mec-admin-token", t);
    setToken(t);
    const res = await api("/api/admin/stats", undefined, { "x-admin-token": t });
    if (res.ok) { setStats(res); setAuthError(false); } else setAuthError(true);
  };

  const sync = async () => {
    setBusy(true); setMsg(null);
    const res = await api("/api/admin/sync", {}, { "x-admin-token": getAdminToken() });
    setBusy(false);
    if (res.ok) {
      setMsg(`✓ مزامنة حية: ${res.productsSeen} منتجًا في كتالوج ProdSeller · مطابقة ${res.matched} · تغيّر ${res.changed} · متوفر الآن ${res.inStockNow} · رصيد $${(res.balanceUsd ?? 0).toFixed(2)} (${res.membership}) — ${res.latencyMs}ms`);
      onSyncDone();
      await load();
    } else setMsg(`✗ ${res.error}`);
  };

  return (
    <Card className="bg-zinc-900/60 border-cyan-900/50">
      <CardContent className="p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="text-sm font-bold text-zinc-100">🛠️ لوحة التشغيل — الموجّه والموردون والمزامنة</div>
          <Badge
            variant="outline"
            className={`text-[11px] font-mono ${stats?.mode === "live" ? "border-rose-700 text-rose-300" : "border-amber-700 text-amber-300"}`}
          >
            {stats?.mode === "live" ? "LIVE" : "SANDBOX"}
          </Badge>
        </div>

        {authError && (
          <div className="rounded border border-cyan-900/60 bg-cyan-950/20 p-2.5 space-y-2">
            <div className="text-[11px] font-bold text-cyan-300">🔐 لوحة التشغيل محمية بمفتاح</div>
            <div className="text-[11px] text-zinc-400 leading-4">
              أدخل مفتاح التشغيل (ADMIN_TOKEN) للوصول إلى إحصاءات الموردين والمزامنة الحية. المفتاح يُحفظ محليًا في متصفحك فقط.
            </div>
            <div className="flex gap-2">
              <Input
                dir="ltr" type="password"
                className="flex-1 h-9 font-mono text-xs bg-zinc-950 border-zinc-700"
                placeholder="admin token…"
                aria-label="رمز التشغيل (admin token)"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && saveToken(token)}
              />
              <Button size="sm" className="h-9 bg-cyan-800 hover:bg-cyan-700 text-cyan-50" onClick={() => saveToken(token)}>
                فتح
              </Button>
            </div>
          </div>
        )}

        {stats && !authError && (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5 text-center">
                <div className="text-[11px] text-zinc-400">رصيد ProdSeller (حي)</div>
                <div className="text-lg font-mono font-bold text-emerald-400" dir="ltr">
                  ${(stats.ps.balanceUsd ?? 0).toFixed(2)}
                </div>
                <div className="text-[11px] text-zinc-400">{stats.ps.username} · {stats.ps.membership}</div>
              </div>
              <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5 text-center">
                <div className="text-[11px] text-zinc-400">إجمالي الطلبات</div>
                <div className="text-lg font-mono font-bold text-cyan-300" dir="ltr">{stats.orders.total}</div>
              </div>
              <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5 text-center">
                <div className="text-[11px] text-zinc-400">قائمة «أعلمني»</div>
                <div className="text-lg font-mono font-bold text-amber-300" dir="ltr">{stats.waitlistTotal}</div>
              </div>
              <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5 text-center">
                <div className="text-[11px] text-zinc-400">وضع المتجر</div>
                <div className="text-lg font-bold text-zinc-200">{stats.mode === "live" ? "🔴 حي" : "🧪 تجريبي"}</div>
              </div>
            </div>
            <Button
              className="w-full h-11 text-xs font-bold bg-cyan-900 hover:bg-cyan-800 text-cyan-50"
              disabled={busy}
              onClick={sync}
            >
              {busy ? "⏳ جارٍ السحب الحي من ProdSeller…" : "🔄 مزامنة حية الآن — GET /v1/products + /v1/balance (تحديث الأسعار والمخزون)"}
            </Button>
            {msg && (
              <div className="text-[11px] text-zinc-300 bg-zinc-950/70 border border-zinc-800 rounded px-2.5 py-1.5 leading-5">
                {msg}
              </div>
            )}
            <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5">
              <div className="text-[11px] font-bold text-zinc-300 mb-1.5">🏆 درجات الموردين وقواطع الدائرة</div>
              <div className="overflow-x-auto">
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-zinc-400 border-b border-zinc-800 text-start">
                      <th className="p-1.5">المورد</th>
                      <th className="p-1.5">النوع</th>
                      <th className="p-1.5">درجة</th>
                      <th className="p-1.5">إخفاقات</th>
                      <th className="p-1.5">قاطع الدائرة</th>
                      <th className="p-1.5">منتجات بالسلسلة</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.suppliers.map((s, i) => (
                      <tr key={i} className={`border-b border-zinc-900 ${s.active ? "" : "opacity-50"}`}>
                        <td className="p-1.5 text-zinc-200 font-bold">{s.name}</td>
                        <td className="p-1.5 text-zinc-400">{s.kind}</td>
                        <td className="p-1.5 font-mono text-cyan-300" dir="ltr">{(100 * s.score).toFixed(0)}/100</td>
                        <td className="p-1.5 font-mono text-zinc-400" dir="ltr">{s.failCount}</td>
                        <td className="p-1.5">
                          {s.circuitOpen ? (
                            <span className="text-rose-400 font-bold">مفتوح ⛔</span>
                          ) : (
                            <span className="text-emerald-500">سليم ✓</span>
                          )}
                        </td>
                        <td className="p-1.5 font-mono text-zinc-400" dir="ltr">{s.chainCount}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5">
              <div className="text-[11px] font-bold text-zinc-300 mb-1.5">📋 أحدث الطلبات</div>
              {stats.orders.recent.length === 0 ? (
                <div className="text-[11px] text-zinc-400">لا طلبات بعد — أنشئ طلبًا تجريبيًا من المتجر</div>
              ) : (
                <div className="space-y-1 max-h-56 overflow-y-auto">
                  {stats.orders.recent.map((o, i) => (
                    <div key={i} className="flex flex-wrap items-center justify-between gap-2 text-[11px] border-b border-zinc-900 pb-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-cyan-300" dir="ltr">{o.publicId}</span>
                        <span className="text-zinc-400">{o.product.slice(0, 30)}</span>
                        <span className="text-zinc-400" dir="ltr">{o.phone}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-zinc-400" dir="ltr">
                          {o.currency === "SAR" ? `${o.price} ر.س` : `$${o.price}`}
                        </span>
                        <span className={`font-bold ${ORDER_STATUS_CLASS[o.status] ?? "text-zinc-400"}`}>{o.status}</span>
                        {o.winner && (
                          <Badge variant="outline" className="text-[11px] border-emerald-800 text-emerald-400">{o.winner}</Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="rounded border border-zinc-800 bg-zinc-950/70 p-2.5">
              <div className="text-[11px] font-bold text-zinc-300 mb-1.5">🗂️ سجل المزامنة</div>
              {stats.syncs.length === 0 ? (
                <div className="text-[11px] text-zinc-400">لم تُنفّذ مزامنة بعد — اضغط زر المزامنة الحية</div>
              ) : (
                <div className="space-y-1">
                  {stats.syncs.map((s, i) => (
                    <div key={i} className={`text-[11px] leading-4 ${s.ok ? "text-zinc-400" : "text-rose-400"}`}>
                      {s.ok ? "✓" : "✗"} {s.message} — {new Date(s.at).toLocaleTimeString("ar")}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ---------------- Main Store ----------------
export function Store() {
  const [phone, setPhone] = useState("");
  const [phoneInput, setPhoneInput] = useState("");
  const [view, setView] = useState<"catalog" | "checkout" | "order" | "wallet" | "admin">("catalog");
  const [catalog, setCatalog] = useState<CatalogData | null>(null);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Product | null>(null);
  const [orderPublicId, setOrderPublicId] = useState<string | null>(null);
  const [balance, setBalance] = useState<number | null>(null);
  const [phoneError, setPhoneError] = useState<string | null>(null);

  const digits = phone.replace(/\D/g, "");
  const region = digits.startsWith("966") ? "SA" : digits.startsWith("967") ? "YE" : "WW";

  const loadCatalog = useCallback(async () => {
    setCatalogError(null);
    const res = await api("/api/store/catalog");
    if (res.ok) setCatalog(res);
    else setCatalogError(res.error || "تعذّر تحميل المتجر — أعد المحاولة");
  }, []);

  const loadBalance = useCallback(async () => {
    if (!phone) return setBalance(null);
    const res = await api(`/api/wallet?phone=${encodeURIComponent(phone)}`);
    setBalance(res.ok ? res.balance : null);
  }, [phone]);

  useEffect(() => {
    const saved = localStorage.getItem("mec-phone");
    if (saved) { setPhone(saved); setPhoneInput(saved); }
    loadCatalog();
  }, [loadCatalog]);

  useEffect(() => { if (phone) loadBalance(); }, [phone, loadBalance, view]);

  // FIX (P2, AUDIT-5): client accepted any ≥8 digits but the server enforces
  // ^\+96[67]\d{8,9}$ — users could "register" numbers that always fail at
  // checkout. Client now enforces the exact same rule.
  const register = () => {
    const cleaned = phoneInput.replace(/[^\d+]/g, "");
    if (!/^\+96[67]\d{8,9}$/.test(cleaned)) {
      setPhoneError("أدخل رقم جوال صحيح مع رمز الدولة (مثال: +9665xxxxxxxx أو +9677xxxxxxxx)");
    } else {
      setPhone(cleaned);
      localStorage.setItem("mec-phone", cleaned);
      setPhoneError(null);
      loadBalance();
    }
  };

  return (
    <div className="space-y-4">
      <Card className="bg-zinc-900/60 border-emerald-900/50">
        <CardContent className="p-3 space-y-2.5">
          <div className="flex flex-wrap items-center gap-2 justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="font-mono text-[11px] border-emerald-700 bg-emerald-950/60 text-emerald-300">
                MEC STORE W1
              </Badge>
              <Badge
                variant="outline"
                className={`text-[11px] font-mono ${catalog?.mode === "live" ? "border-rose-700 bg-rose-950/60 text-rose-300" : "border-amber-700 bg-amber-950/60 text-amber-300"}`}
              >
                {catalog?.mode === "live" ? "🔴 وضع حي" : "🧪 وضع تجريبي"}
              </Badge>
              {catalog?.lastSyncAt && (
                <span className="text-[11px] text-zinc-400">
                  آخر مزامنة: {new Date(catalog.lastSyncAt).toLocaleTimeString("ar")}
                </span>
              )}
            </div>
            <div className="flex items-center gap-1.5">
              <Button
                size="sm" variant="outline"
                className={`text-xs h-9 ${view === "wallet" ? "border-amber-600 text-amber-300" : "border-zinc-700 text-zinc-400"}`}
                onClick={() => setView(view === "wallet" ? "catalog" : "wallet")}
              >
                👛 المحفظة {balance != null && <span className="font-mono text-emerald-400" dir="ltr"> ${balance.toFixed(2)}</span>}
              </Button>
              <Button
                size="sm" variant="outline"
                className={`text-xs h-9 ${view === "admin" ? "border-cyan-600 text-cyan-300" : "border-zinc-700 text-zinc-400"}`}
                onClick={() => setView(view === "admin" ? "catalog" : "admin")}
              >
                🛠️ التشغيل
              </Button>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 items-center">
            <Input
              dir="ltr"
              inputMode="tel"
              aria-label="رقم الجوال"
              className="flex-1 min-w-52 font-mono text-sm h-10 bg-zinc-950 border-zinc-700"
              placeholder="+9665xxxxxxxx أو +9677xxxxxxxx"
              value={phoneInput}
              onChange={(e) => setPhoneInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && register()}
            />
            <Button className="h-10 bg-emerald-900 hover:bg-emerald-800 text-emerald-100" onClick={register}>
              تسجيل / تحديث
            </Button>
            {phone && (
              <Badge variant="outline" className="text-[11px] border-cyan-800 bg-cyan-950/60 text-cyan-300 py-1.5 px-2.5">
                {REGION_LABELS[region]}
              </Badge>
            )}
          </div>
          <div className="text-[11px] text-zinc-400 leading-4">
            🆔 هويتك = رقم جوالك (بلا كلمات مرور): يحدد منطقتك السعرية ويربط محفظتك وقائمة تنبيهاتك.
            {!phone && " أدخل جوالك لعرض أسعار منطقتك."}
          </div>
          {phoneError && (
            <div className="text-[11px] text-rose-400 bg-rose-950/40 border border-rose-900/50 rounded px-2.5 py-1.5">
              {phoneError}
            </div>
          )}
        </CardContent>
      </Card>

      {/* FIX (P1, AUDIT-5): catalog tri-state — was a silent blank page on
          fetch failure; now explicit loading / error+retry / empty states. */}
      {view === "catalog" && !catalog && !catalogError && (
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardContent className="p-6 space-y-3">
            <div className="text-[12px] text-zinc-400 animate-pulse">⏳ جارٍ تحميل المتجر…</div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="rounded border border-zinc-800 bg-zinc-950/70 p-3 h-28 animate-pulse" />
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      {view === "catalog" && catalogError && (
        <Card className="bg-zinc-900/60 border-rose-900/50">
          <CardContent className="p-6 space-y-3">
            <div className="text-[12px] text-rose-300">⚠️ {catalogError}</div>
            <Button className="h-10 text-xs bg-emerald-900 hover:bg-emerald-800 text-emerald-100" onClick={loadCatalog} aria-label="إعادة محاولة تحميل المتجر">
              🔄 إعادة المحاولة
            </Button>
          </CardContent>
        </Card>
      )}
      {view === "catalog" && catalog && catalog.products.length === 0 && (
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardContent className="p-6 text-[12px] text-zinc-400">
            لا منتجات متاحة حاليًا — جرّب «تحديث المزامنة» بعد قليل
          </CardContent>
        </Card>
      )}
      {view === "catalog" && catalog && catalog.products.length > 0 && (
        <StoreGrid
          data={catalog}
          region={region}
          hasPhone={!!phone}
          phone={phone}
          onBuy={(p) => { setSelected(p); setView("checkout"); }}
          onRefresh={loadCatalog}
        />
      )}
      {view === "checkout" && selected && (
        <CheckoutPanel
          product={selected}
          phone={phone}
          region={region}
          balance={balance}
          onDone={(id) => { setOrderPublicId(id); setView("order"); loadBalance(); }}
          onCancel={() => setView("catalog")}
          onNeedWallet={() => setView("wallet")}
        />
      )}
      {view === "order" && orderPublicId && (
        <OrderView
          publicId={orderPublicId}
          phone={phone}
          onBack={() => { setView("catalog"); loadCatalog(); }}
          onWalletRefresh={loadBalance}
        />
      )}
      {view === "wallet" && phone && <WalletPanel phone={phone} onBalance={setBalance} onOpenOrder={(id) => { setOrderPublicId(id); setView("order"); }} />}
      {view === "wallet" && !phone && (
        <Card className="bg-zinc-900/60 border-amber-900/50">
          <CardContent className="p-4 text-sm text-zinc-400">
            سجّل رقم جوالك أولًا لفتح المحفظة 👆
          </CardContent>
        </Card>
      )}
      {view === "admin" && <OpsPanel onSyncDone={loadCatalog} />}
    </div>
  );
}
