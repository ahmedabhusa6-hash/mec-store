import { db } from "@/lib/db";
import { STATUS_AR, maskPhone, SUPPLIER_NAMES, STEP_AR, normalizePhone } from "@/lib/format";
import { guard } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/**
 * FIX (P1, AUDIT-3 W6 / AUDIT-7 — CWE-639): order detail (incl. the delivered
 * product payload = the goods) was readable with ONLY the publicId — no owner
 * proof. publicIds are 2^40 random (non-CSPRNG) and also leak via wallet
 * transaction refs. Now the requesting phone must match the order's phone.
 */
export async function GET(req: Request, ctx: { params: Promise<{ id: string }> }) {
  const limited = guard(req, "generic");
  if (limited) return limited;
  const { id } = await ctx.params;

  const url = new URL(req.url);
  const phone = normalizePhone(url.searchParams.get("phone"));

  const order = await db.order.findUnique({
    where: { publicId: id.slice(0, 40) },
    include: {
      product: { select: { name: true, family: true } },
      attempts: { orderBy: { createdAt: "asc" } },
    },
  });
  if (!order || !phone || phone !== order.phone) {
    // Do not reveal existence: same error for not-found and not-owner
    return Response.json({ ok: false, error: "الطلب غير موجود — تحقق من الرقم والمعرّف" }, { status: 404 });
  }

  return Response.json({
    ok: true,
    order: {
      publicId: order.publicId,
      product: order.product.name,
      family: order.product.family,
      phoneMasked: maskPhone(order.phone),
      region: order.region,
      currency: order.currency,
      priceLocked: order.priceLocked,
      amountUsd: order.amountUsd,
      rail: order.rail,
      status: order.status,
      statusAr: STATUS_AR[order.status] ?? order.status,
      payAddress: order.payAddress,
      payAmount: order.payAmount,
      winner: order.winnerCode,
      deliveredPayload: order.deliveredPayload,
      deliveredAt: order.deliveredAt?.toISOString() ?? null,
      cashback: order.cashbackAmount,
      apology: order.apologyAmount,
      createdAt: order.createdAt.toISOString(),
    },
    // FIX (P0, AUDIT-8): supplier costUsd per step leaked to the public —
    // transparency now shows status/latency/message only (costs stay internal).
    transparency: order.attempts.map((a) => ({
      supplier: SUPPLIER_NAMES[a.supplierCode] ?? a.supplierCode,
      step: a.step,
      stepAr: STEP_AR[a.step] ?? a.step,
      status: a.status,
      latencyMs: a.latencyMs,
      message: a.message,
      at: a.createdAt.toISOString(),
    })),
  });
}
