import { requireOwner } from "@/lib/auth";
import { sbGet, sbPatch } from "@/lib/supabase";
import { audit } from "@/lib/audit";
import { clientIp } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

type ProviderRow = {
  code: string; name: string; kind: string; status: string; domain: string | null;
  docs_url: string | null; sync_interval_min: number;
  last_sync_at: string | null; last_ok_at: string | null; last_error: string | null;
  products: number; last_success_sync: string | null; credentials_env: string[];
};

const ALLOWED_STATUS = new Set([
  "DISCOVERED", "DOCUMENTATION_FOUND", "CREDENTIALS_REQUIRED", "READY_FOR_TEST",
  "READ_ONLY_TEST_PASSED", "SYNC_ACTIVE", "AUTH_FAILED", "RATE_LIMITED",
  "UNSUPPORTED", "BLOCKED", "MAINTENANCE", "RETIRED",
]);

/** GET — provider registry with live status + product counts. */
export async function GET() {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const rows = await sbGet<ProviderRow[]>(
      "v_provider_status?select=*&order=code.asc&limit=100", 30_000);
    return Response.json({ providers: rows });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}

/** PATCH — { code, status?, sync_interval_min?, notes? } (owner-only, audit-logged). */
export async function PATCH(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const body = (await req.json()) as {
      code?: string; status?: string; sync_interval_min?: number; notes?: string;
    };
    const code = (body.code ?? "").trim();
    if (!code) return Response.json({ error: "code مطلوب" }, { status: 400 });

    const patch: Record<string, unknown> = { updated_at: new Date().toISOString() };
    if (body.status != null) {
      if (!ALLOWED_STATUS.has(body.status))
        return Response.json({ error: "حالة غير معروفة" }, { status: 400 });
      patch.status = body.status;
    }
    if (body.sync_interval_min != null) {
      const n = parseInt(String(body.sync_interval_min), 10);
      if (!Number.isFinite(n) || n < 5 || n > 10080)
        return Response.json({ error: "الفاصل خارج النطاق (5–10080 دقيقة)" }, { status: 400 });
      patch.sync_interval_min = n;
    }
    if (body.notes != null) patch.notes = String(body.notes).slice(0, 2000);

    await sbPatch(`providers?code=eq.${encodeURIComponent(code)}`, patch);
    await audit(g.owner.email, "providers.update", {
      entity: "providers", entityId: code,
      details: { status: body.status ?? null, interval: body.sync_interval_min ?? null },
      ip: clientIp(req),
    });
    return Response.json({ ok: true, code });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
