import { db } from "@/lib/db";
import { STORE_MODE } from "@/lib/engine";

export const dynamic = "force-dynamic";

/**
 * NEW (P2, AUDIT-8): deep health check for Railway monitoring — verifies the
 * app process AND the database round-trip (the root /api is liveness-only).
 */
export async function GET() {
  const started = Date.now();
  let dbOk = false;
  try {
    await db.$queryRaw`SELECT 1`;
    dbOk = true;
  } catch (e) {
    console.error("[health] db check failed:", e);
  }
  return Response.json(
    {
      ok: dbOk,
      service: "mec-store",
      mode: STORE_MODE,
      db: dbOk,
      latencyMs: Date.now() - started,
      time: new Date().toISOString(),
    },
    { status: dbOk ? 200 : 503 }
  );
}
