import { requireOwner } from "@/lib/auth";
import { suppliersAgg, channelsInventory } from "@/lib/intel";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const url = new URL(req.url);
    if (url.searchParams.get("view") === "channels") {
      return Response.json(await channelsInventory());
    }
    const q = (url.searchParams.get("q") ?? "").trim().toLowerCase();
    let rows = await suppliersAgg();
    if (q) {
      rows = rows.filter(
        (s) => s.name.toLowerCase().includes(q) || (s.username ?? "").toLowerCase().includes(q),
      );
    }
    return Response.json({ total: rows.length, rows });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
