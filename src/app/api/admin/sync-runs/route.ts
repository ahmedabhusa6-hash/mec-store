import { requireOwner } from "@/lib/auth";
import { sbGet } from "@/lib/supabase";

export const dynamic = "force-dynamic";

type SyncRunRow = {
  id: number; provider_code: string; started_at: string; finished_at: string | null;
  trigger: string; status: string; items_seen: number | null; items_changed: number | null;
  products_new: number | null; prices_updated: number | null; errors: string | null;
  duration_ms: number | null; meta: Record<string, unknown> | null;
};

/** GET — recent provider sync runs. ?limit= (≤200, default 50) ?code= filter. */
export async function GET(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const url = new URL(req.url);
    const limit = Math.min(parseInt(url.searchParams.get("limit") ?? "50", 10) || 50, 200);
    const code = (url.searchParams.get("code") ?? "").trim();
    let path = `sync_runs?select=*&order=id.desc&limit=${limit}`;
    if (code) path += `&provider_code=eq.${encodeURIComponent(code)}`;
    const rows = await sbGet<SyncRunRow[]>(path, 30_000);
    return Response.json({ runs: rows });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
