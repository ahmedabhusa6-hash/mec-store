import { db } from "@/lib/db";
import { getOrCreateWallet, credit, creditApologyGuarded, routeOrder, STORE_MODE } from "@/lib/engine";
import { normalizePhone, regionFromPhone, RAILS, genPublicId, round2, sarToUsd, REGIONS } from "@/lib/format";
import { guard } from "@/lib/ratelimit";
import { randomUUID } from "crypto";

export const dynamic = "force-dynamic";

const SANDBOX_TRC20_ADDR = "TMECSandbox000000C7Y";
const LIVE_TRC20_ADDR = process.env.LIVE_TRC20_ADDRESS || "SET-LIVE-TRC20-ADDRESS";

export async function POST(req: Request) {
  const limited = guard(req, "checkout");
  if (limited) return limited;

  let body: { slug?: string; phone?: string; rail?: string };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "طلب غير صالح" }, { status: 400 });
  }

  const slug = typeof body.slug === "string" ? body.slug.slice(0, 120) : "";
  const phone = normalizePhone(body.phone);
  const rail = typeof body.rail === "string" ? body.rail.slice(0, 20) : "";

  if (!slug || !phone) {
    return Response.json(
      { ok: false, error: "بيانات ناقصة: slug + جوال صحيح مطلوبان (+966/+967)" },
      { status: 400 }
    );
  }
  if (!RAILS.includes(rail as any)) {
    return Response.json({ ok: false, error: "وسيلة دفع غير مدعومة" }, { status: 400 });
  }

  // Server-side price lock (client price fields are NEVER trusted — audit verified)
  const product = await db.product.findUnique({
    where: { slug },
    include: { prices: true, chains: { where: { active: true }, include: { supplier: true }, orderBy: { priority: "asc" } } },
  });
  if (!product || !product.active) {
    return Response.json({ ok: false, error: "المنتج غير موجود" }, { status: 404 });
  }

  const region = regionFromPhone(phone);
  const geo = product.prices.find((g) => g.region === region) ?? product.prices.find((g) => g.region === "WW");
  if (!geo) {
    return Response.json({ ok: false, error: "لا يوجد تسعير متاح لهذا المنتج" }, { status: 409 });
  }
  const priceLocked = round2(geo.price);
  const amountUsd = region === "SA" ? sarToUsd(priceLocked) : priceLocked;
  const publicId = genPublicId();

  // ---- Wallet rail: atomic debit + order create, then route immediately ----
  // FIX (P1, AUDIT-3 D2/D3): balance-read → order-create → debit-write was a
  // non-transactional multi-step sequence (double-spend window + crash gap).
  // Now: single $transaction where the debit INSERT is conditional on the
  // live ledger SUM covering the amount (atomic compare-and-insert).
  if (rail === "wallet") {
    let order;
    try {
      order = await db.$transaction(async (tx) => {
        const wallet = await tx.wallet.upsert({ where: { phone }, create: { phone }, update: {} });
        const debited = await tx.$executeRaw`INSERT INTO "WalletTx" ("id", "walletId", "type", "amount", "ref", "note", "createdAt")
          SELECT ${randomUUID()}, ${wallet.id}, 'purchase', ${-amountUsd}, ${`${publicId}-purchase`}, ${`شراء ${product.name}`}, now()
          WHERE (SELECT COALESCE(SUM("amount"), 0) FROM "WalletTx" WHERE "walletId" = ${wallet.id}) >= ${amountUsd}`;
        if (debited === 0) throw new Error("INSUFFICIENT_FUNDS");
        return tx.order.create({
          data: {
            publicId, productId: product.id, phone, region, currency: geo.currency,
            priceLocked, amountUsd, rail, status: "routing",
          },
        });
      });
    } catch (e) {
      if ((e as Error).message === "INSUFFICIENT_FUNDS") {
        return Response.json(
          { ok: false, error: "الرصيد غير كافٍ — اشحن المحفظة أو ادفع بـUSDT مباشرة" },
          { status: 402 }
        );
      }
      console.error("[checkout] wallet transaction failed:", e);
      return Response.json({ ok: false, error: "تعذّر إتمام الطلب — أعد المحاولة" }, { status: 500 });
    }

    let result;
    try {
      result = await routeOrder({
        orderId: order.id, chain: product.chains.map((c) => ({
          supplier: c.supplier.code, name: c.supplier.name, costUsd: c.costUsd, stock: c.stock,
          externalId: c.externalId,
        })), priceUsd: amountUsd, productName: product.name, phone, amountUsd,
      });
    } catch (e) {
      // Router crashed mid-flow → fail-safe: full refund + apology + mark failed
      console.error("[checkout] routeOrder crashed:", e);
      const wallet = await getOrCreateWallet(phone);
      await credit(wallet.id, "refund", amountUsd, `${publicId}-refund`, "استرداد كامل — تعذّر التنفيذ");
      await creditApologyGuarded(wallet.id, phone, 1, `${publicId}-apology`);
      await db.order.update({ where: { id: order.id }, data: { status: "failed", apologyAmount: 1 } });
      return Response.json({ ok: true, publicId, routed: { ok: false, status: "failed", refunded: amountUsd } });
    }

    if (result.status === "delivered") {
      await db.order.update({
        where: { id: order.id },
        data: {
          status: "delivered", winnerCode: result.winner, costUsd: result.costUsd,
          deliveredPayload: result.payload, deliveredAt: new Date(),
          cashbackAmount: result.cashback,
        },
      });
      const wallet = await getOrCreateWallet(phone);
      if (result.cashback > 0) {
        await credit(wallet.id, "cashback", result.cashback, `${publicId}-cashback`, "كاش باك 1%");
      }
      return Response.json({ ok: true, publicId, routed: { ok: true, status: "delivered", winner: result.winner, cashback: result.cashback } });
    }

    // failed → refund + apology (FIX: apology capped once/phone/24h — AUDIT-3 W8)
    const wallet = await getOrCreateWallet(phone);
    await credit(wallet.id, "refund", amountUsd, `${publicId}-refund`, "استرداد كامل — تعذّر التنفيذ");
    const apologized = await creditApologyGuarded(wallet.id, phone, result.apology, `${publicId}-apology`);
    await db.order.update({
      where: { id: order.id },
      data: { status: "failed", apologyAmount: apologized ? result.apology : 0 },
    });
    return Response.json({ ok: true, publicId, routed: { ok: false, status: "failed", refunded: amountUsd, apology: apologized ? result.apology : 0 } });
  }

  // ---- TRC20 / Binance Pay: create pending order + payment instructions ----
  const centsCode = 1 + Math.floor(Math.random() * 98); // unique cents marker
  const payAmount = round2(amountUsd + centsCode / 100);
  const addr = rail === "trc20"
    ? (STORE_MODE === "live" ? LIVE_TRC20_ADDR : SANDBOX_TRC20_ADDR)
    : "BINANCE-PAY-SANDBOX";

  await db.order.create({
    data: {
      publicId, productId: product.id, phone, region, currency: geo.currency,
      priceLocked, amountUsd, rail, status: "pending_payment",
      payAddress: addr, payAmount, paymentRef: `${rail}-${publicId}`,
    },
  });

  return Response.json({
    ok: true,
    publicId,
    payment: {
      rail,
      network: rail === "trc20" ? "TRON (TRC-20)" : "Binance Pay",
      address: addr,
      amount: payAmount,
      centsCode,
      note: "أرسل المبلغ بالضبط — الترميز بالسنتات يميّز طلبك على الشبكة",
      instructions:
        STORE_MODE === "sandbox"
          ? "الوضع التجريبي: اضغط «محاكاة تأكيد الدفع» في صفحة الطلب لإكمال الدورة (نفس مسار الـwebhook الحقيقي)"
          : "أرسل المبلغ ثم انتظر تأكيد الشبكة (بلوك واحد ~1-3 د) — يُطلق الموجّه فورًا تلقائيًا",
    },
  });
}
