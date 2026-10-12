import { latestPrices, freshnessBucket, supplierLabel } from "@/lib/intel";
import { requireOwner } from "@/lib/auth";

export const dynamic = "force-dynamic";

/**
 * Price API — facts only (no raw_text — Content Licensing prudence).
 * PRIVATE per owner master-prompt decision 11 (2026-10-12): the platform is an
 * internal owner tool; anonymous access to supplier/price data is not allowed.
 * Owner session required. ?q= search   ?limit= max rows (≤500)
 */
export async function GET(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const url = new URL(req.url);
    const query = (url.searchParams.get("q") ?? "").trim().toLowerCase();
    const limit = Math.min(parseInt(url.searchParams.get("limit") ?? "300", 10) || 300, 500);
    let rows = await latestPrices(3000);
    rows = rows.filter((p) => p.price != null && p.product && p.product.trim().length >= 2);
    if (query) {
      rows = rows.filter(
        (p) =>
          p.product.toLowerCase().includes(query) ||
          (p.username ?? "").toLowerCase().includes(query) ||
          (p.title ?? "").toLowerCase().includes(query),
      );
    }
    const data = rows.slice(0, limit).map((p) => ({
      channel_id: p.channelId,
      username: p.username,
      title: p.title,
      supplier: supplierLabel(p.username, p.title, p.channelId),
      product: p.product,
      price: p.price,
      currency: p.currency,
      unit: p.unit,
      posted_at: p.postedAt,
      age_hours: p.ageHours,
      freshness: freshnessBucket(p.ageHours),
    }));
    return Response.json(data);
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
