/** MEC — audit trail helper (owner console actions). Server-side only. */
import { sbPost } from "./supabase";

export async function audit(
  actor: string,
  action: string,
  opts: { entity?: string; entityId?: string | number; details?: unknown; ip?: string | null } = {},
): Promise<void> {
  try {
    await sbPost("audit_log", {
      actor,
      action,
      entity: opts.entity ?? null,
      entity_id: opts.entityId != null ? String(opts.entityId) : null,
      details: opts.details ?? null,
      ip: opts.ip ?? null,
    });
  } catch {
    // audit failure must never break the main action
  }
}

export async function raiseAlert(
  severity: "info" | "warning" | "critical",
  category: string,
  title: string,
  message?: string,
  entity?: string,
  entityId?: string | number,
): Promise<void> {
  try {
    await sbPost("alerts", {
      severity,
      category,
      title,
      message: message ?? null,
      entity: entity ?? null,
      entity_id: entityId != null ? String(entityId) : null,
    });
  } catch {
    // alert failure must never break the main action
  }
}
