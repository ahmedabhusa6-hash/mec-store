import { db } from "@/lib/db";
import { getOrCreateWallet, credit, creditApologyGuarded, routeOrder, STORE_MODE } from "@/lib/engine";
import { guard } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/**
 * Payment confirmation (webhook path). In sandbox this is triggered by the
 * "محاكاة تأكيد الدفع" button (same path as the real webhook).
 * Idempotent: repeated confirmations return the current state without re-routing.
 *
 * FIX (P0-live, AUDIT-1/2/3/7 — CWE-306): this endpoint previously verified
 * NOTHING (no signature, no txid check, no STORE_MODE gate) — in live mode
 * anyone with a publicId could self-confirm an unpaid order and trigger a
 * real supplier purchase at the store's expense. Client-initiated
 * confirmation is now restricted to SANDBOX mode; live mode requires a
 * server-verified webhook (W2 scope: on-chain/TRON scan or Binance Pay
 * webhook with signature validation).
 */
export async function POST(req: Request) {
  const limited = guard(req, "confirm");
  if (limited) return limited;

  if (STORE_MODE !== "sandbox") {
    return Response.json(
      { ok: false, error: "التأكيد اليدوي معطّل في الوضع الحي — يتم التحقق من الدفع تلقائيًا على الشبكة" },
      { status: 403 }
    );
  }

  let body: { publicId?: string; txid?: string; ref?: string };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "طلب غير صالح" }, { status: 400 });
  }
  const publicId = typeof body.publicId === "string" ? body.publicId.slice(0, 40) : "";
  const txid = typeof (body.txid ?? body.ref) === "string" ? String(body.txid ?? body.ref).slice(0, 120) : "";
  if (!publicId) {
    return Response.json({ ok: false, error: "publicId مطلوب" }, { status: 400 });
  }

  const order = await db.order.findUnique({
    where: { publicId },
    include: { product: { select: { id: true, name: true } } },
  });
  if (!order) {
    return Response.json({ ok: false, error: "الطلب غير موجود" }, { status: 404 });
  }

  // Idempotency: already confirmed/routed → return state
  if (order.status !== "pending_payment") {
    return Response.json({ ok: true, publicId, status: order.status, idempotent: true });
  }

  // FIX (P1, AUDIT-3 D4 TOCTOU): status-check → update → route was
  // non-atomic; two concurrent confirms could double-route (double real
  // purchase in live). Atomic claim: only ONE request can flip
  // pending_payment → routing; losers get the idempotent state.
  const claimed = await db.order.updateMany({
    where: { id: order.id, status: "pending_payment" },
    data: { status: "routing", paymentRef: txid || order.paymentRef },
  });
  if (claimed.count === 0) {
    const fresh = await db.order.findUnique({ where: { id: order.id } });
    return Response.json({ ok: true, publicId, status: fresh?.status ?? "routing", idempotent: true });
  }

  const chainLinks = await db.chainLink.findMany({
    where: { productId: order.product.id, active: true },
    include: { supplier: true },
    orderBy: { priority: "asc" },
  });

  let result;
  try {
    result = await routeOrder({
      orderId: order.id,
      chain: chainLinks.map((c) => ({
        supplier: c.supplier.code, name: c.supplier.name, costUsd: c.costUsd, stock: c.stock,
        externalId: c.externalId,
      })),
      priceUsd: order.amountUsd,
      productName: order.product.name,
      phone: order.phone,
      amountUsd: order.amountUsd,
    });
  } catch (e) {
    // Router crashed mid-flow → fail-safe: refund + apology + mark failed
    console.error("[confirm] routeOrder crashed:", e);
    const wallet = await getOrCreateWallet(order.phone);
    await credit(wallet.id, "refund", order.amountUsd, `${publicId}-refund`, "استرداد كامل — تعذّر التنفيذ");
    await creditApologyGuarded(wallet.id, order.phone, 1, `${publicId}-apology`);
    await db.order.update({ where: { id: order.id }, data: { status: "failed", apologyAmount: 1 } });
    return Response.json({ ok: true, publicId, routed: { ok: false, status: "failed", refunded: order.amountUsd } });
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
    // Cashback credited to the buyer's wallet (creates wallet if new)
    if (result.cashback > 0) {
      const wallet = await getOrCreateWallet(order.phone);
      await credit(wallet.id, "cashback", result.cashback, `${publicId}-cashback`, "كاش باك 1%");
    }
    return Response.json({ ok: true, publicId, routed: { ok: true, status: "delivered", winner: result.winner, cashback: result.cashback } });
  }

  // failed → refund to wallet + apology (FIX: capped once/phone/24h — AUDIT-3 W8)
  const wallet = await getOrCreateWallet(order.phone);
  await credit(wallet.id, "refund", order.amountUsd, `${publicId}-refund`, "استرداد كامل — تعذّر التنفيذ");
  const apologized = await creditApologyGuarded(wallet.id, order.phone, result.apology, `${publicId}-apology`);
  await db.order.update({
    where: { id: order.id },
    data: { status: "failed", apologyAmount: apologized ? result.apology : 0 },
  });
  return Response.json({ ok: true, publicId, routed: { ok: false, status: "failed", refunded: order.amountUsd, apology: apologized ? result.apology : 0 } });
}
