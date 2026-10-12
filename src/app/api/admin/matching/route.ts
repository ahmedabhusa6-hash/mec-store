import { requireOwner } from "@/lib/auth";
import { sbGet } from "@/lib/supabase";

export const dynamic = "force-dynamic";

type Benchmark = {
  match_key: string; brand: string; product_core: string; tier: string | null;
  duration: string | null; quantity: string | null;
  offers: number; providers: number;
  min_price: number | null; max_price: number | null; avg_price: number | null;
  spread_pct: number | null; cheapest_provider: string | null;
  cheapest_offer: string | null; dearest_provider: string | null;
  last_matched_at: string | null;
};

type Offer = {
  provider_code: string; external_id: string;
  product_name: string; unit_price: number | null; currency: string | null;
  discount_pct: number | null; unit_cost: number | null;
  stock: string | null; status: string | null; fetched_at: string | null;
};

/** GET — cross-provider product benchmarks (Phase-5 matching layer).
 *  ?comparable=1 → only multi-provider priced benchmarks (default: all)
 *  ?q=  free-text filter · ?sort=spread|offers|price · ?key= single benchmark offers */
export async function GET(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const url = new URL(req.url);
    const comparable = url.searchParams.get("comparable") === "1";
    const q = (url.searchParams.get("q") ?? "").trim().toLowerCase();
    const sort = url.searchParams.get("sort") ?? "spread";
    const key = (url.searchParams.get("key") ?? "").trim();

    if (key) {
      const offers = await sbGet<Offer[]>(
        `v_benchmark_offers?match_key=eq.${encodeURIComponent(key)}&select=provider_code,external_id,product_name,unit_price,currency,discount_pct,unit_cost,stock,status,fetched_at&order=unit_price.asc&limit=200`, 30_000);
      return Response.json({ offers });
    }

    let path = `benchmark_products?select=*&limit=500`;
    if (comparable) path += `&providers=gte.2&min_price=not.is.null`;
    const rows = await sbGet<Benchmark[]>(path, 30_000);

    let filtered = rows;
    if (q) {
      filtered = rows.filter((b) =>
        b.match_key.toLowerCase().includes(q) ||
        b.brand.toLowerCase().includes(q) ||
        b.product_core.toLowerCase().includes(q) ||
        (b.cheapest_provider ?? "").toLowerCase().includes(q));
    }

    const cmp: Record<string, (a: Benchmark, b: Benchmark) => number> = {
      spread: (a, b) => (b.spread_pct ?? -1) - (a.spread_pct ?? -1),
      offers: (a, b) => b.offers - a.offers || (b.spread_pct ?? -1) - (a.spread_pct ?? -1),
      price: (a, b) => (a.min_price ?? 1e9) - (b.min_price ?? 1e9),
      recent: (a, b) => (b.last_matched_at ?? "").localeCompare(a.last_matched_at ?? ""),
    };
    filtered = [...filtered].sort(cmp[sort] ?? cmp.spread);

    // summary stats for the header cards
    const stats = {
      benchmarks: rows.length,
      comparable: rows.filter((b) => b.providers >= 2 && b.min_price !== null).length,
      maxSpread: rows.reduce((m, b) => Math.max(m, b.spread_pct ?? 0), 0),
      providersCovered: new Set(rows.flatMap((b) => [b.cheapest_provider, b.dearest_provider].filter(Boolean) as string[])).size,
    };

    return Response.json({ total: filtered.length, stats, rows: filtered.slice(0, 300) });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
