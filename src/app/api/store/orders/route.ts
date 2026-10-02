import { db } from "@/lib/db";
import { STATUS_AR, normalizePhone } from "@/lib/format";
import { guard } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/**
 * NEW (P2, AUDIT-1 G12): the store UI promises "محفوظ في سجل طلبك دائمًا"
 * but there was no way to retrieve past orders (publicId-only). This endpoint
 * returns the buyer's recent orders by phone — fulfilling the promise.
 * Owner-scoped by phone (same identity model as the wallet).
 */
export async function GET(req: Request) {
  const limited = guard(req, "wallet_read");
  if (limited) return limited;

  const url = new URL(req.url);
  const phone = normalizePhone(url.searchParams.get("phone"));
  if (!phone) {
    return Response.json({ ok: false, error: "جوال صحيح مطلوب (+966/+967)" }, { status: 400 });
  }

  const orders = await db.order.findMany({
    where: { phone },
    include: { product: { select: { name: true } } },
    orderBy: { createdAt: "desc" },
    take: 10,
  });

  return Response.json({
    ok: true,
    orders: orders.map((o) => ({
      publicId: o.publicId,
      product: o.product.name,
      status: o.status,
      statusAr: STATUS_AR[o.status] ?? o.status,
      currency: o.currency,
      priceLocked: o.priceLocked,
      amountUsd: o.amountUsd,
      rail: o.rail,
      createdAt: o.createdAt.toISOString(),
    })),
  });
}
