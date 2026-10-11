import { requireOwner } from "@/lib/auth";
import { settingsData, POLICY } from "@/lib/intel";
import { sbPost, sbPatch } from "@/lib/supabase";
import { audit } from "@/lib/audit";
import { clientIp } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/** Whitelisted runtime-tunable settings (read by the monitor at each run start). */
const TUNABLE: Record<string, { type: "int"; min: number; max: number; label: string }> = {
  join_budget: { type: "int", min: 0, max: 20, label: "حد الانضمامات لكل دورة" },
  private_join_cap: { type: "int", min: 0, max: 10, label: "حد الانضمامات الخاصة لكل دورة" },
  join_total_ceiling: { type: "int", min: 50, max: 450, label: "السقف الإجمالي للمصادر" },
  time_budget_s: { type: "int", min: 120, max: 1800, label: "ميزانية المسح (ثانية)" },
  first_scan_cap: { type: "int", min: 100, max: 3000, label: "حد مسح القناة الجديدة" },
  delta_cap: { type: "int", min: 100, max: 2000, label: "حد الرسائل الجديدة بالمسي" },
};

export async function GET() {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const [settings, awaiting] = await Promise.all([
      settingsData(),
      // counts shown on settings page
      Promise.resolve(null),
    ]);
    return Response.json({ policy: POLICY, settings, tunable: TUNABLE });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}

/** PATCH: { key, value } for tunables, or { action: "clear_breaker" }. */
export async function PATCH(req: Request) {
  const g = await requireOwner();
  if ("deny" in g) return g.deny;
  try {
    const body = (await req.json()) as { key?: string; value?: number | string; action?: string };
    const now = new Date().toISOString();

    if (body.action === "clear_breaker") {
      // neutralize any active pause (join_pause_* / scan_pause_*) by backdating it
      const all = await settingsData();
      const targets = all
        .filter((s) => (s.key.startsWith("join_pause") || s.key.startsWith("scan_pause_")) && s.value && new Date(s.value) > new Date())
        .map((s) => s.key);
      for (const k of targets) {
        await sbPatch(`settings?key=eq.${encodeURIComponent(k)}`, { value: "1970-01-01T00:00:00Z", updated_at: now, updated_by: g.owner.email });
      }
      await audit(g.owner.email, "settings.clear_breakers", { details: { cleared: targets }, ip: clientIp(req) });
      return Response.json({ ok: true, cleared: targets });
    }

    const key = body.key ?? "";
    const spec = TUNABLE[key];
    if (!spec) return Response.json({ error: "مفتاح غير قابل للضبط" }, { status: 400 });
    const num = typeof body.value === "number" ? body.value : parseInt(String(body.value), 10);
    if (!Number.isFinite(num) || num < spec.min || num > spec.max) {
      return Response.json({ error: `قيمة خارج النطاق (${spec.min}–${spec.max})` }, { status: 400 });
    }
    // UPSERT (not PATCH-with-filter): the row may not exist yet — a filtered PATCH
    // would silently update 0 rows and report success (live bug found 2026-10-11:
    // owner ceiling change ق5 returned ok but wrote nothing). on_conflict=key +
    // resolution=merge-duplicates creates or updates atomically, same as monitor.py.
    await sbPost(
      `settings?on_conflict=key`,
      { key, value: String(num), updated_at: now, updated_by: g.owner.email },
      "return=minimal,resolution=merge-duplicates",
    );
    await audit(g.owner.email, "settings.update", {
      entity: "settings",
      entityId: key,
      details: { value: num },
      ip: clientIp(req),
    });
    return Response.json({ ok: true, key, value: num });
  } catch (e) {
    return Response.json({ error: String(e).slice(0, 200) }, { status: 500 });
  }
}
