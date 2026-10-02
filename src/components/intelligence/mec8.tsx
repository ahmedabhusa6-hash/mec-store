"use client";

// MEC-8.0 BEST-PRICE — سجل أفضل الأسعار المعتمدة
// Families verdict + trust ladder: static (extracted from deployed intel page).
// Adoption table: computed LIVE from /api/admin/costs (x-admin-token gated —
// FIX: public catalog no longer exposes supplier costUsd, so the owner
// dashboard reads costs from the gated admin endpoint instead).

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type CatalogProduct = {
  slug: string; name: string; family: string; officialUsd: number | null;
  chain: { supplier: string; costUsd: number; stock: number | null }[];
  prices: Record<string, { price: number; currency: string }>;
};

const FAMILIES = [
  { family: "اشتراكات AI/SaaS (Gemini/ChatGPT/Office365/CapCut/Canva...)", winner: "ProdSeller API", best: "25 SKU حية $0.09–$10 — مفتاحك جاهز الآن", why: "أثبتت المطابقة أنه طبقة التوريد نفسها التي تشتري منها المتاجر (12 تطابق بالسنت)", alt: "StackVault retail (+13–61%) — نفس المصدر بسعر أعلى" },
  { family: "خدمات رقمية خارج كتالوج PS (YouTube/LinkedIn/Adobe/Grammarly)", winner: "StackVault retail (الآن) → طلب إضافتها لدى ProdSeller", best: "$0.64–$11.44 (7 عائلات مرجعية)", why: "PS لا يعرضها حاليًا؛ SV أرخص مصدر متاح فورًا بلا تسجيل", alt: "GGSel (VPN روسي) — أسعار أدنى معلنة لكن محجوبة" },
  { family: "بث MENA (شاهد/أنغامي/StarzPlay/OSN+)", winner: "Turgame", best: "شاهد مصر 12 شهرًا $33.16 (−80% عن الرسمي)", why: "السلم الإقليمي الكامل موثق — مصر/شمال إفريقيا أرخص بـ3.6× من الخليج لنفس الخدمة", alt: "Kinguin ($6.77–7.00 لشاهد 1M) / GamsGo" },
  { family: "بطاقات عالمية $ (iTunes/Google Play/Steam US)", winner: "Reloadly (شرطي W2) — الآن Turgame", best: "Reloadly: تحت الاسمي 2–10% · Turgame الآن: فوق الاسمية ~4–11%", why: "Reloadly الوحيد الموثق الذي يبيع تحت القيمة الاسمية — لكن خلف حساب مجاني", alt: "Turgame (شراء فوري) — الخيار العملي في W1" },
  { family: "بطاقات إقليمية (TL/TRY/SAR)", winner: "Turgame", best: "Steam KSA 20SAR بـ$5.20 (تحت الاسمي!) · TL سلم كامل", why: "بطاقة سعودية تحت اسميها = تحكيم مباشر لسوقك الأساسي + سوق تركيا الأرخص", alt: "BitTopUp (بلا فجوة سعرية موثقة)" },
  { family: "مفاتيح ألعاب PC", winner: "Kinguin API (شرطي W2)", best: "خصم كميات 5–10.2% (10/50/100/500+)", why: "الجملة الكمية الرسمية الوحيدة الموثقة للمفاتيح", alt: "AllKeyShop أدنى سوق (Witcher 3 من $4.82) — تجزئة" },
  { family: "شحن ألعاب/top-ups", winner: "Turgame", best: "21 منتجًا بالدولار — واجهة مباشرة", why: "كتالوج حي بلا بوابة؛ البدائل بلا فجوة موثقة", alt: "BitTopUp / Z2U / U7BUY" },
  { family: "برمجيات/مفاتيح Office+Windows", winner: "ProdSeller (Office365 سنة $0.21)", best: "أرخص سعر موثق في السجل كله", why: "$0.21 حي ومخزون 4,778 وحدة مباعة — لا يقاربه أي مصدر", alt: "Plati رمادي (Office2024 $0.60 دائم مقابل الاشتراك)" },
];

const LADDER = [
  "السعر القابل للاعتماد = الأرخص بين المصادر التي يمكن الدفع لها فعليًا اليوم (وصول + مخزون)",
  "طبقة الدليل: موثق مباشر (API/صفحة حية) > موثق (وثائق رسمية) > معلن (يُعتمد كمرجع لا كشراء)",
  "المصدر المحجوب (GGSel 401) لا يُعتمد سعره للشراء — يُعرض كأرضية مرجعية فقط",
  "طبقة كلفة StackVault الداخلية ليست سعر شراء لنا — نحن نشتري بسعر تجزئته",
  "لكل صف: مصدر أساسي + بديل جاهز — قاعدة عدم الاعتماد على مورد واحد",
];

function computeMargin(cost: number, sell: number): number {
  const fee = sell * 0.015;
  const provision = sell * 0.08; // متوسط مخصص الضمان حسب فئة الهشاشة
  return Math.round(((sell - cost - fee - provision) / sell) * 1000) / 10;
}

export function Mec8() {
  const [products, setProducts] = useState<CatalogProduct[] | null>(null);
  const [mode, setMode] = useState<string>("");
  const [needsToken, setNeedsToken] = useState(false);

  useEffect(() => {
    const token = typeof window !== "undefined" ? (localStorage.getItem("mec-admin-token") ?? "") : "";
    fetch("/api/admin/costs", { headers: { "x-admin-token": token } })
      .then((r) => { if (r.status === 401) { setNeedsToken(true); return null; } return r.json(); })
      .then((d) => {
        if (d?.ok) { setProducts(d.products); setMode("live"); }
      })
      .catch(() => setProducts([]));
  }, []);

  // Adoption table from gated admin costs: ps-sourced products, in-stock first.
  // FIX (P3, AUDIT-6 console error): guard undefined cost/sell before toFixed.
  const adoption = (products ?? [])
    .filter((p) => p.chain.some((c) => c.supplier === "ps" && typeof c.costUsd === "number"))
    .map((p) => {
      const ps = p.chain.find((c) => c.supplier === "ps")!;
      const sell = p.prices.YE?.price ?? p.prices.WW?.price ?? 0;
      const alt = p.chain.find((c) => c.supplier === "sv");
      return {
        name: p.name,
        cost: ps.costUsd ?? 0,
        stock: ps.stock,
        sell,
        margin: sell > 0 ? computeMargin(ps.costUsd ?? 0, sell) : 0,
        alt: alt && typeof alt.costUsd === "number" ? `StackVault retail $${alt.costUsd.toFixed(2)}${alt.stock != null ? ` (مخزون ${alt.stock})` : ""}` : "—",
        official: p.officialUsd,
      };
    })
    .sort((a, b) => Number(b.stock === 0) - Number(a.stock === 0) || b.margin - a.margin);

  const cheapest = adoption.length ? adoption.reduce((m, p) => (p.cost < m.cost ? p : m), adoption[0]) : null;
  const inStock = adoption.filter((p) => p.stock !== 0).length;

  return (
    <div className="space-y-4">
      <Card className="bg-zinc-900/60 border-emerald-900/50">
        <CardContent className="p-4 space-y-3">
          <div className="text-sm font-bold text-zinc-100">
            🏅 سجل أفضل الأسعار المعتمدة — أفضل سعر لكل خدمة/منتج رقمي من أي مصدر (ليس ProdSeller فقط)
          </div>
          <div className="flex flex-wrap gap-2 text-[10.5px]">
            <Badge variant="outline" className="border-emerald-800 bg-emerald-950/60 text-emerald-300">
              صف اعتماد فوري (اليوم): {inStock} متوفر + {adoption.length - inStock} نفد
            </Badge>
            {mode && (
              <Badge variant="outline" className="border-zinc-700 text-zinc-400">
                متصل بأسعار التوريد الحية ({mode})
              </Badge>
            )}
          </div>
          {needsToken && (
            <div className="text-[10.5px] text-amber-300 bg-amber-950/30 border border-amber-900/50 rounded px-2.5 py-1.5">
              🔐 جدول التبني الحي يتطلب مفتاح التشغيل — أدخله في «🛠️ التشغيل» بالمتجر ثم عد لهذه الصفحة (أسعار التوريد لم تعد علنية حمايةً للهوامش)
            </div>
          )}
          {cheapest && (
            <div className="rounded border border-emerald-800/60 bg-emerald-950/30 p-3 space-y-1.5">
              <div className="text-[11px] font-bold text-emerald-300">🏆 أرخص سعر في السجل كله:</div>
              <div className="text-xl font-mono font-bold text-emerald-400" dir="ltr">${cheapest.cost.toFixed(2)}</div>
              <div className="text-[11px] text-zinc-300">{cheapest.name} (حي، 4,778 مبيعة)</div>
              <div className="text-[10.5px] text-amber-300">
                🇸🇦 تحت الاسمي: Steam KSA 20SAR بـ$5.20 (الاسمي $5.45) — تحكيم مباشر لسوقك
              </div>
              <div className="text-[10.5px] text-cyan-300">
                🎁 W2: Reloadly يبيع البطاقات العالمية تحت الاسمي 2–10% (حساب مجاني)
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardContent className="p-4 space-y-2">
          <div className="text-[12px] font-bold text-zinc-200">📐 سلم الاعتماد — متى يُعتمد السعر؟</div>
          {LADDER.map((r, i) => (
            <div key={i} className="text-[10.5px] text-zinc-400 leading-5">
              <span className="text-emerald-400 font-bold">{i + 1})</span> {r}
            </div>
          ))}
          <div className="text-[9.5px] text-zinc-600 mt-1">
            تصحيح: أسعار Turgame بعملة USD (وسم currency=USD في 110 صفحة مسحوبة) — وسم «يورو» في MEC-4 كان تحفظًا خاطئًا يُصحح هنا
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardContent className="p-4 space-y-2">
          <div className="text-[12px] font-bold text-zinc-200">🥇 حسم العائلات الثماني — من يفوز بكل عائلة ولماذا</div>
          <div className="overflow-x-auto">
            <table className="w-full text-[10.5px]">
              <thead>
                <tr className="text-zinc-500 border-b border-zinc-800 text-right">
                  <th className="p-1.5">العائلة</th>
                  <th className="p-1.5">المصدر الرابح</th>
                  <th className="p-1.5">أفضل سعر</th>
                  <th className="p-1.5">لماذا</th>
                  <th className="p-1.5">البديل الجاهز</th>
                </tr>
              </thead>
              <tbody>
                {FAMILIES.map((f, i) => (
                  <tr key={i} className="border-b border-zinc-900 align-top">
                    <td className="p-1.5 text-zinc-200 font-bold">{f.family}</td>
                    <td className="p-1.5 text-emerald-300">{f.winner}</td>
                    <td className="p-1.5 text-zinc-300 font-mono" dir="rtl">{f.best}</td>
                    <td className="p-1.5 text-zinc-400 leading-4">{f.why}</td>
                    <td className="p-1.5 text-zinc-500">{f.alt}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/60 border-emerald-900/50">
        <CardContent className="p-4 space-y-2">
          <div className="text-[12px] font-bold text-zinc-200">
            ✅ اعتمد الآن — العمود الفقري: ProdSeller API · مفتاحك جاهز — USDT فوري بلا KYC
          </div>
          <div className="text-[9.5px] text-zinc-500">
            الجدول محسوب لحظيًا من كتالوج المتجر الحي (التكلفة = سعر API · البيع = سعر المتجر YE · الهامش بعد رسوم 1.5% + مخصص ضمان 8%)
          </div>
          {!products ? (
            <div className="text-[10.5px] text-zinc-600">جارٍ التحميل من الكتالوج الحي…</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-[10.5px]">
                <thead>
                  <tr className="text-zinc-500 border-b border-zinc-800 text-right">
                    <th className="p-1.5">المنتج</th>
                    <th className="p-1.5">أفضل سعر (تكلفة API)</th>
                    <th className="p-1.5">المخزون</th>
                    <th className="p-1.5">بيع المتجر (YE)</th>
                    <th className="p-1.5">صافي الهامش</th>
                    <th className="p-1.5">البديل الجاهز</th>
                    <th className="p-1.5">الرسمي</th>
                  </tr>
                </thead>
                <tbody>
                  {adoption.map((p, i) => (
                    <tr key={i} className={`border-b border-zinc-900 ${p.stock === 0 ? "opacity-50" : ""}`}>
                      <td className="p-1.5 text-zinc-200 font-bold">{p.name}</td>
                      <td className="p-1.5 font-mono text-cyan-300" dir="ltr">${p.cost.toFixed(2)}</td>
                      <td className="p-1.5">
                        <span className={p.stock === 0 ? "text-rose-400" : "text-emerald-400"}>
                          ● {p.stock === 0 ? "نفد" : p.stock == null ? "يُتحقق" : "متوفر"}
                        </span>
                      </td>
                      <td className="p-1.5 font-mono text-emerald-400" dir="ltr">${p.sell.toFixed(2)}</td>
                      <td className="p-1.5 font-mono text-amber-300" dir="ltr">{p.margin}%</td>
                      <td className="p-1.5 text-zinc-500">{p.alt}</td>
                      <td className="p-1.5 font-mono text-zinc-600" dir="ltr">{p.official ? `$${p.official.toFixed(2)}` : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
