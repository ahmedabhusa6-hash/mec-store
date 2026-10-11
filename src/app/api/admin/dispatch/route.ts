import { requireOwner } from "@/lib/auth";
import { guard } from "@/lib/ratelimit";
import { dispatchMonitorRun } from "@/lib/gh";
import { audit } from "@/lib/audit";
import { clientIp } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/** POST: trigger an immediate monitor run (workflow_dispatch). */
export async function POST(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  const limited = guard(req, "dispatch");
  if (limited) return limited;
  try {
    const res = await dispatchMonitorRun(g.owner.email);
    await audit(g.owner.email, "automation.dispatch", {
      entity: "workflow",
      entityId: "price-monitor",
      details: { trigger: "manual", ok: res.ok, status: res.status },
      ip: clientIp(req),
    });
    if (!res.ok) return Response.json({ error: res.message }, { status: 502 });
    return Response.json({ ok: true, message: res.message });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
