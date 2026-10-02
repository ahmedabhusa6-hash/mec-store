import { db } from "@/lib/db";
import { isAdmin, unauthorized } from "@/lib/admin-auth";
import { guard } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/**
 * NEW (P0 companion, AUDIT-8): supplier costUsd was stripped from the PUBLIC
 * catalog (margin-leak fix). The owner intelligence dashboard (MEC-8 tab)
 * still needs live procurement costs — served here behind the same
 * x-admin-token gate as the other admin endpoints.
 */
export async function GET(req: Request) {
  const limited = guard(req, "admin");
  if (limited) return limited;
  if (!isAdmin(req)) return unauthorized();

  const products = await db.product.findMany({
    where: { active: true },
    include: {
      prices: true,
      chains: { where: { active: true }, include: { supplier: true }, orderBy: { priority: "asc" } },
    },
    orderBy: { name: "asc" },
  });

  return Response.json({
    ok: true,
    products: products.map((p) => ({
      slug: p.slug,
      name: p.name,
      officialUsd: p.officialUsd ?? null,
      chain: p.chains.map((c) => ({
        supplier: c.supplier.code,
        costUsd: c.costUsd,
        stock: c.stock,
      })),
      prices: Object.fromEntries(p.prices.map((g) => [g.region, { price: g.price, currency: g.currency }])),
    })),
  });
}
