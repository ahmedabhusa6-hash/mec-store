import { requireOwner } from "@/lib/auth";
import { runsData } from "@/lib/intel";
import { recentWorkflowRuns } from "@/lib/gh";

export const dynamic = "force-dynamic";

export async function GET() {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const [runs, workflow] = await Promise.all([runsData(40), recentWorkflowRuns(5)]);
    return Response.json({ runs, workflow });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
