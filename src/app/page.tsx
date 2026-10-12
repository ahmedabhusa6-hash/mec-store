import { latestPrices, freshnessBucket, supplierLabel } from "@/lib/intel";
import { PublicExplorer } from "@/components/dashboard/public-explorer";
import { getOwner } from "@/lib/auth";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

/**
 * MEC price explorer — PRIVATE per owner master-prompt decision 11 (2026-10-12):
 * internal owner tool; no anonymous disclosure of supplier/price data.
 * Server-rendered from the LIVE latest_prices view; freshness is surfaced so a
 * stale price is never presented as a confirmed current price.
 */
export default async function Home() {
  const owner = await getOwner();
  if (!owner) redirect("/login");

  let rows: Awaited<ReturnType<typeof latestPrices>> = [];
  let dbError: string | null = null;
  try {
    rows = (await latestPrices(3000)).filter((p) => p.price != null && p.product && p.product.trim().length >= 2);
  } catch (e) {
    dbError = String(e instanceof Error ? e.message : e);
  }

  const priced = rows.map((p) => ({
    product: p.product,
    supplier: supplierLabel(p.username, p.title, p.channelId),
    username: p.username,
    isPrivate: !p.username,
    price: p.price,
    currency: p.currency,
    unit: p.unit,
    postedAt: p.postedAt,
    ageHours: p.ageHours,
    freshness: freshnessBucket(p.ageHours),
  }));

  return <PublicExplorer rows={priced} dbError={dbError} />;
}
