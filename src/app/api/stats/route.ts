import { sbCount, sbGet } from "@/lib/supabase";
import { latestPrices, freshnessBucket } from "@/lib/intel";
import { requireOwner } from "@/lib/auth";

export const dynamic = "force-dynamic";

type RunRaw = {
  id: number; started_at: string | null; finished_at: string | null; runner: string | null;
  channels_scanned: number | null; prices_added: number | null; joins_ok: number | null; errors: string | null;
};

/** PRIVATE per owner master-prompt decision 11 (2026-10-12): owner session required. */
export async function GET() {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const [observations, channels, discoveries, statements, runs, latest] = await Promise.all([
      sbCount("price_observations"),
      sbCount("tg_channels"),
      sbCount("discoveries"),
      sbCount("statements"),
      sbGet<RunRaw[]>("runs?select=id,started_at,finished_at,runner,channels_scanned,prices_added,joins_ok,errors&order=id.desc&limit=1"),
      latestPrices(3000),
    ]);
    const priced = latest.filter((p) => p.price != null);
    const buckets: Record<string, number> = {};
    for (const p of priced) {
      const b = freshnessBucket(p.ageHours);
      buckets[b] = (buckets[b] ?? 0) + 1;
    }
    return Response.json({
      observations,
      channels,
      discoveries,
      statements,
      products: new Set(priced.map((p) => p.product)).size,
      suppliers: new Set(priced.map((p) => p.channelId)).size,
      cadence_minutes: 30,
      freshness: buckets,
      last_run: runs[0] ?? null,
      disclaimer: "الأسعار معلنة من المتاجر ولم تُتحقق بالشراء الفعلي بعد",
    });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
