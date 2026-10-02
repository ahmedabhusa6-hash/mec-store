import { db } from "@/lib/db";
import { normalizePhone } from "@/lib/format";
import { guard } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/**
 * NEW (P2, MEC-21-E G12): out-of-stock catalog cards had a DISABLED button
 * ("نفد — فعّل تنبيه التوفير") — the waitlist was unreachable from the
 * catalog (only via an existing order's restock endpoint). This endpoint
 * lets a registered phone join the waitlist directly from an OOS card.
 * Idempotent by the unique([productId, phone]) constraint.
 */
export async function POST(req: Request) {
  const limited = guard(req, "checkout");
  if (limited) return limited;

  let body: { phone?: string; slug?: string };
  try {
    body = await req.json();
  } catch {
    return Response.json({ ok: false, error: "طلب غير صالح" }, { status: 400 });
  }

  const phone = normalizePhone(body.phone ?? "");
  const slug = String(body.slug ?? "").slice(0, 80);
  if (!phone) {
    return Response.json({ ok: false, error: "سجّل رقم جوالك أولًا (+966/+967) ليصلك التنبيه" }, { status: 400 });
  }

  const product = await db.product.findUnique({ where: { slug }, select: { id: true, name: true } });
  if (!product) {
    return Response.json({ ok: false, error: "منتج غير موجود" }, { status: 404 });
  }

  try {
    await db.waitlist.create({ data: { productId: product.id, phone } });
  } catch (e: unknown) {
    // P2002 = already on the waitlist → idempotent success
    if ((e as { code?: string })?.code !== "P2002") throw e;
    const waitingAhead = await db.waitlist.count({
      where: { productId: product.id, createdAt: { lt: new Date() } },
    });
    return Response.json({
      ok: true, already: true, waitingAhead,
      note: `أنت مسجّل مسبقًا في قائمة انتظار «${product.name}» — موقعك تقريبًا ${waitingAhead}`,
    });
  }

  const waitingAhead = await db.waitlist.count({
    where: { productId: product.id, createdAt: { lt: new Date() } },
  });
  return Response.json({
    ok: true, already: false, waitingAhead,
    note: `✓ تم تسجيلك في قائمة انتظار «${product.name}» — سنعلمك فور توفر المخزون`,
  });
}
