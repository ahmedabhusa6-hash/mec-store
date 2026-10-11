import { requireOwner } from "@/lib/auth";
import { auditData } from "@/lib/intel";

export const dynamic = "force-dynamic";

export async function GET() {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    return Response.json(await auditData(200));
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
