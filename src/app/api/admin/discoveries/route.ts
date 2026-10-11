import { requireOwner } from "@/lib/auth";
import { discoveriesData } from "@/lib/intel";
import { sbPatch, sbPost } from "@/lib/supabase";
import { audit } from "@/lib/audit";
import { dispatchMonitorRun } from "@/lib/gh";
import { clientIp } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/** GET: discovery pipeline + approval queue. */
export async function GET() {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    return Response.json(await discoveriesData());
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}

/**
 * POST: add candidates manually (owner paste).
 * Body: { input: "@handle | t.me/xxx | https://t.me/+hash | one per line" }
 */
export async function POST(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const body = (await req.json()) as { input?: string };
    const raw = (body.input ?? "").trim();
    if (!raw) return Response.json({ error: "أدخل مقبضًا أو رابطًا" }, { status: 400 });
    const lines = raw.split(/[\n,;]+/).map((l) => l.trim()).filter(Boolean).slice(0, 50);
    const rows: { handle: string; kind: string; status: string; source: string; seen_in: number | null }[] = [];
    for (const line of lines) {
      let h = line;
      let kind = "handle";
      const invite = line.match(/(?:t\.me|telegram\.me)\/(?:joinchat\/|\+)([A-Za-z0-9_\-]{8,80})/i);
      if (invite) {
        h = "+" + invite[1].toLowerCase();
        kind = "invite";
      } else {
        const link = line.match(/(?:t\.me|telegram\.me)\/@?([A-Za-z][A-Za-z0-9_]{2,31})/i);
        h = (link ? link[1] : line.replace(/^@/, "")).toLowerCase();
        if (!/^[a-z][a-z0-9_]{2,31}$/.test(h)) continue;
      }
      rows.push({ handle: h, kind, status: "pending", source: "manual", seen_in: null });
    }
    if (!rows.length) return Response.json({ error: "لم يُتعرف على أي مقبض/رابط صالح" }, { status: 400 });
    await sbPost(
      "discoveries?on_conflict=handle",
      rows,
      "resolution=merge-duplicates,return=minimal",
    );
    await audit(g.owner.email, "discoveries.add_manual", {
      entity: "discoveries",
      details: { added: rows.map((r) => r.handle) },
      ip: clientIp(req),
    });
    return Response.json({ ok: true, added: rows.length });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}

/**
 * PATCH: approve / reject / requeue a candidate.
 * Body: { handle, action: "approve" | "reject" | "requeue", dispatch?: boolean }
 * approve → status=approved (+auto-dispatch monitor run so automation resumes immediately).
 */
export async function PATCH(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const body = (await req.json()) as { handle?: string; action?: string; dispatch?: boolean };
    const handle = (body.handle ?? "").trim();
    const action = body.action ?? "";
    if (!handle || !["approve", "reject", "requeue"].includes(action)) {
      return Response.json({ error: "طلب غير صالح" }, { status: 400 });
    }
    const now = new Date().toISOString();
    const patch =
      action === "approve"
        ? { status: "approved", approved_by: g.owner.email, approved_at: now }
        : action === "reject"
          ? { status: "rejected", approved_by: g.owner.email, approved_at: now }
          : { status: "pending", approved_by: null, approved_at: null };
    await sbPatch(`discoveries?handle=eq.${encodeURIComponent(handle)}`, patch);
    await audit(g.owner.email, `discoveries.${action}`, {
      entity: "discoveries",
      entityId: handle,
      ip: clientIp(req),
    });

    let dispatched: { ok: boolean; message: string } | null = null;
    if (action === "approve" && body.dispatch !== false) {
      dispatched = await dispatchMonitorRun(g.owner.email);
      await audit(g.owner.email, "automation.dispatch", {
        entity: "workflow",
        entityId: "price-monitor",
        details: { trigger: `approve:${handle}`, ok: dispatched.ok },
        ip: clientIp(req),
      });
    }
    return Response.json({ ok: true, action, handle, dispatched });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
