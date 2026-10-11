import { requireOwner } from "@/lib/auth";
import { productsAgg, productTrend } from "@/lib/intel";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const url = new URL(req.url);
    const product = url.searchParams.get("trend");
    if (product) {
      return Response.json(await productTrend(product));
    }
    const q = (url.searchParams.get("q") ?? "").trim().toLowerCase();
    const sort = url.searchParams.get("sort") ?? "suppliers";
    let rows = await productsAgg();
    if (q) {
      rows = rows.filter((p) => p.product.toLowerCase().includes(q) || p.bestSupplier.toLowerCase().includes(q));
    }
    const cmp: Record<string, (a: typeof rows[number], b: typeof rows[number]) => number> = {
      suppliers: (a, b) => b.suppliers - a.suppliers || b.observations - a.observations,
      price: (a, b) => a.bestPrice - b.bestPrice,
      observations: (a, b) => b.observations - a.observations,
      recent: (a, b) => (b.lastSeen ?? "").localeCompare(a.lastSeen ?? ""),
    };
    rows = [...rows].sort(cmp[sort] ?? cmp.suppliers);
    return Response.json({ total: rows.length, rows });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
