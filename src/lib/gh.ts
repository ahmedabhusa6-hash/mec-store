/**
 * MEC — GitHub Actions integration (rebuild v4, 2026-10-11).
 * Server-side only. Used for on-demand monitor runs (workflow_dispatch)
 * so the owner can trigger execution from the dashboard ("Run now" /
 * resume automation immediately after approving a private join).
 */
const TOKEN = () => process.env.GH_DISPATCH_TOKEN ?? "";
const REPO = () => process.env.GH_REPO ?? "ahmedabhusa6-hash/mec-store";
const WF = "price-monitor.yml";

export async function dispatchMonitorRun(dispatchedBy?: string): Promise<{ ok: boolean; status: number; message: string }> {
  const token = TOKEN();
  if (!token) return { ok: false, status: 500, message: "GH_DISPATCH_TOKEN غير مضبوط" };
  const r = await fetch(`https://api.github.com/repos/${REPO()}/actions/workflows/${WF}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "mec-console",
    },
    body: JSON.stringify({ ref: "main", inputs: { dispatched_by: dispatchedBy ?? "" } }),
  });
  if (r.status === 204) return { ok: true, status: 204, message: "تم إطلاق دورة المراقب الآن" };
  const text = (await r.text()).slice(0, 200);
  return { ok: false, status: r.status, message: `تعذر الإطلاق (${r.status}): ${text}` };
}

export type GhRun = { id: number; run_number: number; status: string | null; conclusion: string | null; created_at: string; event: string };

export async function recentWorkflowRuns(limit = 5): Promise<GhRun[]> {
  const token = TOKEN();
  if (!token) return [];
  const r = await fetch(`https://api.github.com/repos/${REPO()}/actions/workflows/${WF}/runs?per_page=${limit}`, {
    headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "User-Agent": "mec-console" },
    cache: "no-store",
  });
  if (!r.ok) return [];
  const data = (await r.json()) as { workflow_runs?: GhRun[] };
  return data.workflow_runs ?? [];
}
