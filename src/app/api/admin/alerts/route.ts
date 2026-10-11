import { requireOwner } from "@/lib/auth";
import { alertsData } from "@/lib/intel";
import { sbPatch } from "@/lib/supabase";
import { audit } from "@/lib/audit";

export const dynamic = "force-dynamic";

export async function GET() {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    return Response.json(await alertsData(100));
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}

/** PATCH: mark one ({id}) or all ({all:true}) as read. */
export async function PATCH(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const body = (await req.json()) as { id?: number; all?: boolean };
    const now = new Date().toISOString();
    if (body.all) {
      await sbPatch("alerts?read_at=is.null", { read_at: now });
      await audit(g.owner.email, "alerts.mark_all_read");
      return Response.json({ ok: true, all: true });
    }
    if (body.id == null) return Response.json({ error: "id مطلوب" }, { status: 400 });
    await sbPatch(`alerts?id=eq.${body.id}`, { read_at: now });
    return Response.json({ ok: true, id: body.id });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
