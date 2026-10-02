import { db } from "@/lib/db";
import { isAdmin, unauthorized } from "@/lib/admin-auth";
import { guard } from "@/lib/ratelimit";
import { STORE_MODE } from "@/lib/engine";
import { psBalance } from "@/lib/prodseller";

export const dynamic = "force-dynamic";

/**
 * FIX (P0): was fully public — leaked supplier account username/membership,
 * circuit-breaker state, and order counters to anonymous visitors.
 * Now requires x-admin-token == env ADMIN_TOKEN (fail-closed).
 */
export async function GET(req: Request) {
  const limited = guard(req, "admin");
  if (limited) return limited;
  if (!isAdmin(req)) return unauthorized();

  const [suppliers, ordersTotal, recentOrders, syncs, waitlistTotal, psBal] = await Promise.all([
    db.supplier.findMany({ orderBy: { createdAt: "asc" } }),
    db.order.count(),
    db.order.findMany({
      orderBy: { createdAt: "desc" },
      take: 12,
      select: { publicId: true, status: true, currency: true, priceLocked: true, winnerCode: true, phone: true, product: { select: { name: true } } },
    }),
    db.syncLog.findMany({ orderBy: { createdAt: "desc" }, take: 8 }),
    db.waitlist.count(),
    psBalance(),
  ]);

  const chainCounts = await db.chainLink.groupBy({
    by: ["supplierId"],
    where: { active: true },
    _count: { _all: true },
  });
  const chainMap = new Map(chainCounts.map((c) => [c.supplierId, c._count._all]));

  const attemptStats = await db.attempt.groupBy({
    by: ["supplierCode", "status"],
    _count: { _all: true },
  });

  return Response.json({
    ok: true,
    mode: STORE_MODE,
    ps: {
      live: !!psBal,
      balanceUsd: typeof psBal?.balance === "number" ? psBal.balance : 0,
      membership: psBal?.membership ?? "—",
      username: psBal?.username ?? "—",
    },
    suppliers: suppliers.map((s) => ({
      code: s.code, name: s.name, kind: s.kind, active: s.active,
      score: s.score, failCount: s.failCount,
      circuitOpen: s.openUntil ? s.openUntil.getTime() > Date.now() : false,
      openUntil: s.openUntil?.toISOString() ?? null,
      chainCount: chainMap.get(s.id) ?? 0,
    })),
    attemptStats: attemptStats.map((a) => ({
      supplierCode: a.supplierCode, status: a.status, _count: a._count._all,
    })),
    orders: {
      total: ordersTotal,
      recent: recentOrders.map((o) => ({
        publicId: o.publicId, product: o.product.name, phone: o.phone,
        currency: o.currency, price: o.priceLocked, status: o.status, winner: o.winnerCode,
      })),
    },
    syncs: syncs.map((s) => ({
      ok: s.ok, matched: s.matched, changed: s.changed, inStockNow: s.inStockNow,
      balanceUsd: s.balanceUsd, message: s.message, at: s.createdAt.toISOString(),
    })),
    waitlistTotal,
  });
}
