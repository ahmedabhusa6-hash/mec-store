import { requireOwner } from "@/lib/auth";
import { latestPrices, freshnessBucket, supplierLabel } from "@/lib/intel";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const url = new URL(req.url);
    const query = (url.searchParams.get("q") ?? "").trim().toLowerCase();
    const currency = (url.searchParams.get("currency") ?? "").trim().toUpperCase();
    const limit = Math.min(parseInt(url.searchParams.get("limit") ?? "600", 10) || 600, 1000);
    let rows = await latestPrices(3000);
    rows = rows.filter((p) => p.price != null);
    if (query) {
      rows = rows.filter(
        (p) =>
          p.product.toLowerCase().includes(query) ||
          (p.username ?? "").toLowerCase().includes(query) ||
          (p.title ?? "").toLowerCase().includes(query),
      );
    }
    if (currency) {
      rows = rows.filter((p) => p.currency === currency);
    }
    const out = rows.slice(0, limit).map((p) => ({
      channelId: p.channelId,
      username: p.username,
      title: p.title,
      kind: p.kind,
      product: p.product,
      price: p.price,
      currency: p.currency,
      unit: p.unit,
      postedAt: p.postedAt,
      ageHours: p.ageHours,
      freshness: freshnessBucket(p.ageHours),
      supplier: supplierLabel(p.username, p.title, p.channelId),
    }));
    return Response.json({ total: rows.length, rows: out });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
