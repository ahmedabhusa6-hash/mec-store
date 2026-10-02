import { db } from "@/lib/db";
import { normalizePhone } from "@/lib/format";
import { guard } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/**
 * FIX (P1, AUDIT-3/7 — CWE-639): restock/waitlist was triggerable with only a
 * publicId (adds the victim's phone to a waitlist). Now requires the owning
 * phone. FIX (P3, AUDIT-1): waitingAhead off-by-one counted the caller them-
 * selves for fresh entries; FIX: P2002 race (two rapid clicks) returned 500 —
 * now idempotent.
 */
export async function POST(req: Request, ctx: { params: Promise<{ id: string }> }) {
  const limited = guard(req, "generic");
  if (limited) return limited;
  const { id } = await ctx.params;

  const url = new URL(req.url);
  const phone = normalizePhone(url.searchParams.get("phone"));

  const order = await db.order.findUnique({
    where: { publicId: id.slice(0, 40) },
    include: { product: { select: { id: true, name: true } } },
  });
  if (!order || !phone || phone !== order.phone) {
    return Response.json({ ok: false, error: "الطلب غير موجود — تحقق من الرقم والمعرّف" }, { status: 404 });
  }

  let entry;
  try {
    entry = await db.waitlist.create({
      data: { productId: order.product.id, phone: order.phone },
    });
  } catch (e: unknown) {
    // P2002 = unique(productId, phone) → already registered (rapid double-click race)
    if ((e as { code?: string })?.code !== "P2002") throw e;
    const existing = await db.waitlist.findFirst({
      where: { productId: order.product.id, phone: order.phone },
    });
    entry = existing;
  }

  // FIX: exclude the caller's own entry — count strictly EARLIER entries
  const cutoff = entry?.createdAt ?? new Date();
  const waitingAhead = await db.waitlist.count({
    where: { productId: order.product.id, createdAt: { lt: cutoff } },
  });

  return Response.json({ ok: true, waitingAhead });
}
