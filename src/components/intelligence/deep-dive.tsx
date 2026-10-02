'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import data from '@/lib/data/deep-dive.json';

function S({ children }: { children: React.ReactNode }) {
  return <span className="font-mono text-emerald-400" dir="ltr">{children}</span>;
}

export function DeepDive() {
  const d = data as any;
  const ps = d.point1_prodseller;
  const dl = d.point2_dolaa;
  const me = d.point3_mena_expansion;

  return (
    <div className="space-y-6">
      {/* ═══ Run header ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-rose-800 bg-rose-950/50 text-rose-300">MEC-4.0 DEEP-DIVE</Badge>
            <CardTitle className="text-sm text-zinc-100">🔬 البحث المتعمق: ProdSeller API + دولا + منصات MENA — شرح كل نقطة</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
            {[
              { n: '79', l: 'منشور سعر مؤرخ من قناة ProdSeller', c: 'text-rose-300' },
              { n: '26+', l: 'منتج بأسعار جملة ثلاثية الطبقات', c: 'text-emerald-400' },
              { n: '4', l: 'بوابات B2B مقارنة بالتفصيل', c: 'text-amber-300' },
              { n: '40-60', l: 'SKU جديدًا جاهزًا للتوسعة MENA', c: 'text-cyan-400' },
            ].map((s, i) => (
              <div key={i} className="rounded border border-zinc-800 bg-zinc-950/60 p-2">
                <div className={`text-lg font-bold font-mono ${s.c}`}>{s.n}</div>
                <div className="text-[10px] text-zinc-500 leading-4">{s.l}</div>
              </div>
            ))}
          </div>
          <div className="rounded border border-rose-900/40 bg-rose-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            <b className="text-rose-300">الإجابة المباشرة على شرطك الصارم «أفضل من هذا؟»:</b> نعم — <b className="text-zinc-100">ProdSeller API</b> هو الأفضل بين كل بوابات B2B المتاحة: أخف دخولًا (بوت تيليجرام + رصيد USDT بلا KYC)، وأعلى شفافية (79 منشور سعر علني + وثائق API منشورة للعموم)، وأرخص تجربة (منتجات من $0.015). كل أسعار الجملة «الداخلية» تتحول فور فتح الحساب إلى «مشاهدة مباشرة» عبر <S>GET /v1/products</S>.
          </div>
        </CardContent>
      </Card>

      {/* ═══════════ النقطة 1: ProdSeller API ═══════════ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-emerald-800 bg-emerald-950/50 text-emerald-300">النقطة 1</Badge>
            <CardTitle className="text-sm text-zinc-100">🤖 ProdSeller API — الطريق الكامل من الصفر إلى مشاهدة أسعار الجملة</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Identity */}
          <div className="rounded border border-emerald-900/40 bg-emerald-950/10 p-3 grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1.5 text-[11px]">
            {(Object.entries(ps.identities) as [string, string][]).map(([k, v]) => (
              <div key={k} className="flex justify-between gap-2 border-b border-zinc-800/50 pb-1">
                <span className="text-zinc-500">{k}</span>
                <span className="font-mono text-emerald-300 text-left" dir="ltr">{v}</span>
              </div>
            ))}
            <div className="flex justify-between gap-2 border-b border-zinc-800/50 pb-1">
              <span className="text-zinc-500">الحجم</span>
              <span className="font-mono text-emerald-300" dir="ltr">{ps.scale.users} users · {ps.scale.monthly_active} MAU · {ps.scale.api_users} API</span>
            </div>
          </div>

          {/* Entry path */}
          <div>
            <div className="text-[12px] font-bold text-zinc-100 mb-2">🚪 مسار الدخول (أخف بوابة في السوق — لا KYC ولا مستندات أعمال)</div>
            <ol className="space-y-1.5">
              {ps.entry_path.map((s: string, i: number) => (
                <li key={i} className="text-[11px] text-zinc-300 leading-6 rounded border border-zinc-800 bg-zinc-950/50 px-3 py-1.5">{s}</li>
              ))}
            </ol>
          </div>

          {/* API structure */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <div className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
              <div className="text-[12px] font-bold text-zinc-100 mb-2">⚙️ بنية الـ API (وثائق علنية حية)</div>
              <ul className="text-[11px] text-zinc-300 leading-6 space-y-1">
                <li>• المصادقة: هيدر <S>X-API-Key: psk_...</S> — يُولَّد من لوحة الإدارة ← API Manager</li>
                <li>• حد الطلبات: <S>300 طلب / 15 دقيقة / IP</S> — تتبَّع عبر هيدرات <S>X-RateLimit-*</S></li>
                <li>• النقاط: <S>/products</S> · <S>/products/:id</S> · <S>/balance</S> · <S>POST /orders</S> · <S>/orders</S> · <S>/orders/:id</S></li>
                <li>• حقلان للسعر: <S>price</S> = ما ستُحاسب عليه فعليًا (قد يكون مخصصًا لحسابك) مقابل <S>publicPrice</S> المرجعي</li>
                <li>• خصمان تلقائيان على الطلب: <S>membershipDiscount</S> + <S>bulkDiscount</S></li>
                <li>• حماية التكرار: هيدر <S>Idempotency-Key</S></li>
                <li>• منتجات تفعيل بالبريد: تتطلب <S>email</S> في الطلب — الحالة <S>pending → paid → delivered</S></li>
                <li>• التاريخ: نقرة قديمة <S>51.77.244.194</S> ← انتقلت إلى HTTPS <S>prodseller.com/v1</S> في 12/08</li>
              </ul>
            </div>
            <div className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
              <div className="text-[12px] font-bold text-zinc-100 mb-2">💳 الدفع + التسعير ثلاثي الطبقات</div>
              <ul className="text-[11px] text-zinc-300 leading-6 space-y-1">
                <li>• <b>USDT BEP20</b>: شحن مؤتمت بالكامل وفوري (معلن 08/07)</li>
                <li>• <b>Binance Pay</b>: متاح · <b>PayPal</b>: شحن يدوي عبر الأدمن (09/08 — لدول بلا كريبتو)</li>
                <li>• الحد الأدنى للإيداع: غير معلن [بحاجة للتحقق] — لكن أرخص منتج <S>$0.015</S> = تجربة برصيد صغير جدًا</li>
                <li className="pt-1">• السلّم: <span className="text-amber-300">سعر البوت العام</span> ← <span className="text-emerald-300">سعر API (خصم 3–8%)</span> ← <span className="text-cyan-300">سعر الجملة Bulk (خصم إضافي 3–10%)</span></li>
                <li>• إعلانهم المرصود: «خصم حتى <b className="text-amber-300">35%</b> عن الأسعار العامة لمستخدمي API» (20/07)</li>
                <li>• مثال حي من وثائقهم نفسها: Netflix 1M — API <S>$4.99</S> مقابل معلن <S>$5.99</S></li>
              </ul>
            </div>
          </div>

          {/* Price timeline */}
          <div>
            <div className="text-[12px] font-bold text-zinc-100 mb-2">📈 الخط الزمني الكامل للأسعار — 79 منشورًا مؤرخًا (يوليو–سبتمبر 2026) · مشاهد مباشرة</div>
            <div className="max-h-96 overflow-y-auto rounded border border-zinc-800">
              <table className="w-full text-[11px]">
                <thead className="sticky top-0 bg-zinc-900 text-zinc-400">
                  <tr className="border-b border-zinc-800">
                    <th className="px-2 py-1.5 text-right font-medium">التاريخ</th>
                    <th className="px-2 py-1.5 text-right font-medium">المنتج</th>
                    <th className="px-2 py-1.5 text-center font-medium">عام $</th>
                    <th className="px-2 py-1.5 text-center font-medium">API $</th>
                    <th className="px-2 py-1.5 text-center font-medium">جملة $</th>
                    <th className="px-2 py-1.5 text-right font-medium hidden sm:table-cell">ملاحظة</th>
                  </tr>
                </thead>
                <tbody>
                  {ps.price_timeline_2026.map((r: any, i: number) => (
                    <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-900/50">
                      <td className="px-2 py-1.5 font-mono text-zinc-500" dir="ltr">{r.date}</td>
                      <td className="px-2 py-1.5 text-zinc-200">{r.product}</td>
                      <td className="px-2 py-1.5 text-center font-mono text-amber-300">{r.retail ?? '—'}</td>
                      <td className="px-2 py-1.5 text-center font-mono text-emerald-400">{r.api ?? '—'}</td>
                      <td className="px-2 py-1.5 text-center font-mono text-cyan-300">{r.bulk ?? '—'}</td>
                      <td className="px-2 py-1.5 text-zinc-500 hidden sm:table-cell">{r.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Volatility */}
          <div>
            <div className="text-[12px] font-bold text-zinc-100 mb-2">⚡ شهادات التقلب — السوق يتغير أمام عينيك</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {ps.volatility_evidence.map((v: any, i: number) => (
                <div key={i} className="rounded border border-amber-900/40 bg-amber-950/10 p-2.5">
                  <div className="text-[11px] font-bold text-amber-300 mb-1">{v.product}</div>
                  <div className="text-[10.5px] text-zinc-300 leading-5">{v.story}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Methods + risks */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <div className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
              <div className="text-[12px] font-bold text-zinc-100 mb-2">🎓 ينشرون «الطرق» مجانًا في القناة — دليل مباشر على نموذج المصانع</div>
              <ul className="text-[11px] text-zinc-300 leading-6 space-y-1">
                {ps.methods_published_free.map((m: string, i: number) => (
                  <li key={i}>• {m}</li>
                ))}
              </ul>
              <div className="text-[10px] text-zinc-500 mt-2 leading-5">النمط: ينشرون الطريقة اليدوية مجانًا → يبيعون المنتج الجاهز لمن لا يريد العناء — نفس بنية طبقة «المصانع» في تحليل سلسلة التوريد.</div>
            </div>
            <div className="rounded border border-red-900/40 bg-red-950/10 p-3">
              <div className="text-[12px] font-bold text-red-300 mb-2">⚠️ إشارات الخطر الموثقة (نزاهة كاملة)</div>
              <ul className="text-[11px] text-zinc-300 leading-6 space-y-1">
                {ps.risk_signals.map((r: string, i: number) => (
                  <li key={i}>• {r}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* B2B comparison */}
          <div>
            <div className="text-[12px] font-bold text-zinc-100 mb-2">⚖️ مقارنة بوابات B2B الأربع — لماذا ProdSeller أولًا؟</div>
            <div className="overflow-x-auto rounded border border-zinc-800">
              <table className="w-full text-[11px]">
                <thead className="bg-zinc-900 text-zinc-400">
                  <tr className="border-b border-zinc-800">
                    <th className="px-2 py-1.5 text-right font-medium">البوابة</th>
                    <th className="px-2 py-1.5 text-right font-medium">الدخول</th>
                    <th className="px-2 py-1.5 text-right font-medium">ظهور الأسعار</th>
                    <th className="px-2 py-1.5 text-right font-medium">الحكم</th>
                  </tr>
                </thead>
                <tbody>
                  {ps.b2b_gate_comparison.map((g: any, i: number) => (
                    <tr key={i} className={`border-b border-zinc-800/50 ${i === 0 ? 'bg-emerald-950/20' : ''}`}>
                      <td className={`px-2 py-1.5 font-bold ${i === 0 ? 'text-emerald-300' : 'text-zinc-200'}`}>{g.gate}{i === 0 ? ' ⭐' : ''}</td>
                      <td className="px-2 py-1.5 text-zinc-300">{g.entry}</td>
                      <td className="px-2 py-1.5 text-zinc-300">{g.pricing_visibility}</td>
                      <td className="px-2 py-1.5 text-zinc-400">{g.verdict}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ═══════════ النقطة 2: دولا + التوكن ═══════════ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-cyan-800 bg-cyan-950/50 text-cyan-300">النقطة 2</Badge>
            <CardTitle className="text-sm text-zinc-100">🎯 دولا: ما نحتاجه منك + الحاسبة الجاهزة + خطوات توكن Notion (5 دقائق)</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <div className="rounded border border-cyan-900/40 bg-cyan-950/10 p-3">
              <div className="text-[12px] font-bold text-cyan-300 mb-2">📩 ماذا نحتاج منك لتفعيل حاسبة هوامش دولا الحقيقية؟</div>
              <ul className="text-[11px] text-zinc-300 leading-6 space-y-1">
                {dl.what_we_need_from_user.map((w: string, i: number) => (
                  <li key={i}>• {w}</li>
                ))}
              </ul>
              <div className="text-[10.5px] text-zinc-500 mt-2 leading-5 border-t border-zinc-800 pt-2">
                <b className="text-zinc-400">نتائج فحص هذا الأسبوع:</b> الحساب <S>@dolaa</S> غير موجود في تيليجرام · بحث عربي واسع (4 صياغات) بلا أثر مفهرس · النطاقات متوقفة كما وُثق 27/09 — المتجر يعمل غالبًا عبر قناة خاصة/مغلق أو باسم مختلف.
              </div>
              <div className="text-[10.5px] text-zinc-400 mt-1.5 leading-5">
                <b>المنظومة المنافسة المكتشفة حوله:</b> متجر رمز RAMZ (نتفلكس/شاهد VIP/OSN/أمازون) · يمن توب للخدمات الرقمية · محفظة فلوسك (كرت نت داخل التطبيق) · egatec-center — كلها تبيع نفس العائلات لنفس السوق = أسعارها مرجع مقارنة فوري.
              </div>
            </div>
            <div className="rounded border border-emerald-900/40 bg-emerald-950/10 p-3">
              <div className="text-[12px] font-bold text-emerald-300 mb-2">🧮 الحاسبة جاهزة — معاينة بأرضيات الجملة الطازجة (من ProdSeller هذا الأسبوع)</div>
              <div className="text-[10.5px] text-zinc-400 mb-2 leading-5">المعادلة: (سعر بيع دولا) − (أدنى كلفة جملة مرصودة) = الهامش الإجمالي. عند وصول قائمته نطبقها على كل منتج فورًا:</div>
              <div className="overflow-x-auto rounded border border-zinc-800">
                <table className="w-full text-[10.5px]">
                  <thead className="bg-zinc-900 text-zinc-400">
                    <tr className="border-b border-zinc-800">
                      <th className="px-2 py-1 text-right font-medium">المنتج</th>
                      <th className="px-2 py-1 text-center font-medium">أرضية الجملة</th>
                      <th className="px-2 py-1 text-center font-medium">سعر السوق</th>
                      <th className="px-2 py-1 text-center font-medium">الهامش</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dl.margin_calculator_ready.example_with_fresh_wholesale.map((r: any, i: number) => (
                      <tr key={i} className="border-b border-zinc-800/50">
                        <td className="px-2 py-1 text-zinc-200">{r.item}</td>
                        <td className="px-2 py-1 text-center font-mono text-cyan-300" dir="ltr">${r.wholesale_floor}</td>
                        <td className="px-2 py-1 text-center font-mono text-zinc-400" dir="ltr">{typeof r.dolaa_estimated_selling === 'number' ? '$' + r.dolaa_estimated_selling : (r.market_range ?? '$' + r.market_retail)}</td>
                        <td className="px-2 py-1 text-center font-mono text-amber-300">{r.gross_margin_pct}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Notion token */}
          <div className="rounded border border-amber-900/40 bg-amber-950/10 p-3">
            <div className="text-[12px] font-bold text-amber-300 mb-2">🔐 D5 — تدوير توكن Notion: 6 خطوات بخطواتها (5 دقائق بيدك — من ملف القرارات §3)</div>
            <ol className="space-y-1">
              {dl.notion_token_d5_steps.map((s: string, i: number) => (
                <li key={i} className="text-[11px] text-zinc-300 leading-6 rounded border border-zinc-800/60 bg-zinc-950/40 px-3 py-1">{s}</li>
              ))}
            </ol>
            <div className="text-[10px] text-zinc-500 mt-2 leading-5">لماذا عاجل: التوكن الحالي له قدرة كتابة على 894 صفحة ووُجد سابقًا كنص صريح — التدوير يُبطل أي قيمة له نهائيًا. بعد التدوير أرسل «تحقق من التوكن» وأمر التحقق جاهز.</div>
          </div>
        </CardContent>
      </Card>

      {/* ═══════════ النقطة 3: MENA ═══════════ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px] border-violet-800 bg-violet-950/50 text-violet-300">النقطة 3</Badge>
            <CardTitle className="text-sm text-zinc-100">🌍 توسعة الكتالوج لمنصات MENA: شاهد · StarzPlay · أنغامي · OSN+</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded border border-violet-900/40 bg-violet-950/10 p-3 text-[11px] text-zinc-300 leading-6">
            <b className="text-violet-300">الحكم:</b> {me.verdict} — القرار متاح عند طلبك ويُنفَّذ كدفعة P4 كاملة المواصفات (نفس منهجية الدفعات 1–3).
          </div>

          {/* Shahid */}
          <div className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-[12px] font-bold text-zinc-100">📺 شاهد VIP (MBC)</span>
              <Badge variant="outline" className="text-[9px] border-emerald-800 bg-emerald-950/40 text-emerald-300">أكبر فروقات إقليمية — الأولوية 1</Badge>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              <div>
                <div className="text-[10.5px] text-zinc-500 mb-1">المرجع الرسمي + الأسواق:</div>
                <ul className="text-[11px] text-zinc-300 leading-6 space-y-0.5">
                  <li>• رسمي عالمي: VIP <S>$13.99</S>/شهر · VIP BigTime <S>$16.99</S> — إطلاق أمريكا <S>$8.99</S>/شهر</li>
                  <li>• مشغّل عراقي (Zain Iraq): 4999 IQD (~<S>$3.80</S>)/شهر عبر الفاتورة</li>
                  <li>• Kinguin: <S>$6.77</S>/شهر · GamsGo: ~<S>$7</S>/شهر (خصم 50–52% عن الرسمي)</li>
                </ul>
                <div className="mt-2 rounded border border-amber-900/40 bg-amber-950/10 p-2 text-[10.5px] text-amber-200 leading-5">
                  💡 {me.shahid.key_insight}
                </div>
              </div>
              <div>
                <div className="text-[10.5px] text-zinc-500 mb-1">سلم Turgame السوقي (3 أشهر، يورو) — مشاهد مباشر 27/09:</div>
                <div className="grid grid-cols-2 gap-1">
                  {[
                    ['الجزائر', me.shahid.turgame_market_eur['3M_algeria']], ['مصر', me.shahid.turgame_market_eur['3M_egypt']],
                    ['ليبيا', me.shahid.turgame_market_eur['3M_libya']], ['تونس', me.shahid.turgame_market_eur['3M_tunisia']],
                    ['المغرب', me.shahid.turgame_market_eur['3M_morocco']], ['فلسطين', me.shahid.turgame_market_eur['3M_palestine']],
                    ['لبنان', me.shahid.turgame_market_eur['3M_lebanon']], ['الأردن', me.shahid.turgame_market_eur['3M_jordan']],
                    ['عمان', me.shahid.turgame_market_eur['3M_oman']], ['البحرين', me.shahid.turgame_market_eur['3M_bahrain']],
                    ['الإمارات', me.shahid.turgame_market_eur['3M_uae']], ['الكويت', me.shahid.turgame_market_eur['3M_kuwait']],
                    ['قطر', me.shahid.turgame_market_eur['3M_qatar']], ['مصر 12 شهر', me.shahid.turgame_market_eur['12M_egypt']],
                  ].map(([c, p], i) => (
                    <div key={i} className={`flex justify-between rounded px-2 py-0.5 text-[10.5px] border ${Number(p) > 20 ? 'border-amber-900/50 bg-amber-950/20' : 'border-zinc-800 bg-zinc-900/40'}`}>
                      <span className="text-zinc-400">{c}</span>
                      <span className="font-mono" dir="ltr">€{p}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* StarzPlay + Anghami + OSN */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
              <div className="text-[12px] font-bold text-zinc-100 mb-1">🎬 StarzPlay (الإمارات)</div>
              <ul className="text-[11px] text-zinc-300 leading-6 space-y-0.5 font-mono" dir="ltr">
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">1M</span><span>40 AED = €10.22</span></li>
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">3M</span><span>100 AED = €25.48</span></li>
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">6M</span><span>195 AED = €49.68</span></li>
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">12M</span><span>330 AED = €89.07</span></li>
              </ul>
              <div className="text-[10.5px] text-zinc-500 mt-2 leading-5">💡 {me.starzplay.key_insight}</div>
            </div>
            <div className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
              <div className="text-[12px] font-bold text-zinc-100 mb-1">🎧 أنغامي Plus</div>
              <ul className="text-[11px] text-zinc-300 leading-6 space-y-0.5 font-mono" dir="ltr">
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">1M Egypt</span><span>€2.60</span></li>
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">1M Jordan</span><span>€5.20</span></li>
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">1M Kuwait</span><span>€5.20</span></li>
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">3M Egypt</span><span>€7.81</span></li>
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">3M Jordan</span><span>€15.61</span></li>
              </ul>
              <div className="text-[10.5px] text-zinc-500 mt-2 leading-5">💡 {me.anghami.key_insight}</div>
            </div>
            <div className="rounded border border-zinc-800 bg-zinc-950/50 p-3">
              <div className="text-[12px] font-bold text-zinc-100 mb-1">📺 OSN+ (بطاقات هدايا)</div>
              <ul className="text-[11px] text-zinc-300 leading-6 space-y-0.5 font-mono" dir="ltr">
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">3M Kuwait GC</span><span>€33.83</span></li>
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">6M Morocco GC</span><span>€35.82</span></li>
                <li className="flex justify-between"><span className="text-zinc-500 font-sans">12M Morocco GC</span><span>€59.68</span></li>
              </ul>
              <div className="text-[10.5px] text-zinc-500 mt-2 leading-5">💡 {me.osn_plus.key_insight}</div>
            </div>
          </div>

          {/* Expansion plan */}
          <div className="rounded border border-emerald-900/40 bg-emerald-950/10 p-3 grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
            <div>
              <div className="text-lg font-bold font-mono text-emerald-300">40–60</div>
              <div className="text-[10px] text-zinc-500 leading-4">SKU جديدًا (شاهد ×13 منطقة ×مدد + البقية)</div>
            </div>
            <div className="sm:border-x border-zinc-800">
              <div className="text-[11px] font-bold text-zinc-200 leading-5 mt-1">الأولوية</div>
              <div className="text-[10.5px] text-zinc-400 leading-5">{me.expansion_plan.priority}</div>
            </div>
            <div>
              <div className="text-[11px] font-bold text-zinc-200 leading-5 mt-1">القرار</div>
              <div className="text-[10.5px] text-zinc-400 leading-5">{me.expansion_plan.decision}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ═══ Evidence classes ═══ */}
      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-100">🔒 تصنيف الأدلة (نظام النزاهة الخماسي)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1.5">
          {[
            ['مشاهد مباشرة', d.evidence_classes.directly_observed, 'border-emerald-800 bg-emerald-950/30 text-emerald-200'],
            ['موثق', d.evidence_classes.documented, 'border-teal-800 bg-teal-950/30 text-teal-200'],
            ['استنتاج مبني على أدلة', d.evidence_classes.inferred, 'border-amber-800 bg-amber-950/30 text-amber-200'],
            ['افتراض يحتاج تحققًا', d.evidence_classes.assumption, 'border-red-900/60 bg-red-950/20 text-red-200'],
          ].map(([t, v, cls], i) => (
            <div key={i} className={`rounded border p-2.5 ${cls}`}>
              <b className="text-[11px]">{t}:</b> <span className="text-[11px] opacity-90">{v}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
