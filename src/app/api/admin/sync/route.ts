import { isAdmin, unauthorized } from "@/lib/admin-auth";
import { guard } from "@/lib/ratelimit";
import { syncFromProdSeller } from "@/lib/engine";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

/**
 * FIX (P0): was fully public — any visitor could trigger a real 25s live sync
 * against ProdSeller (DoS + supplier-API abuse + account-ban risk).
 * Now requires x-admin-token == env ADMIN_TOKEN (fail-closed).
 */
export async function POST(req: Request) {
  const limited = guard(req, "admin");
  if (limited) return limited;
  if (!isAdmin(req)) return unauthorized();

  const result = await syncFromProdSeller();
  return Response.json(result, { status: result.ok ? 200 : 502 });
}

export async function GET() {
  return Response.json({ ok: false, error: "Method Not Allowed — استخدم POST" }, { status: 405 });
}
