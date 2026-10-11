import { requireOwner } from "@/lib/auth";
import { channelsInventory } from "@/lib/intel";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const url = new URL(req.url);
    const q = (url.searchParams.get("q") ?? "").trim().toLowerCase();
    const kind = (url.searchParams.get("kind") ?? "").trim();
    let rows = await channelsInventory();
    if (kind) rows = rows.filter((c) => c.kind === kind);
    if (q) {
      rows = rows.filter(
        (c) =>
          (c.username ?? "").toLowerCase().includes(q) ||
          (c.title ?? "").toLowerCase().includes(q) ||
          String(c.tgId).includes(q),
      );
    }
    return Response.json({ total: rows.length, rows });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
