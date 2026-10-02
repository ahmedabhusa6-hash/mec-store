import { getCatalog } from "@/lib/engine";
import { guard } from "@/lib/ratelimit";

export const dynamic = "force-dynamic";

/**
 * FIX (P3, MEC-21-D): catalog had no ETag — every poll re-downloaded the
 * full ~13KB payload. A content hash now enables 304 Not Modified responses.
 */
function etagOf(obj: unknown): string {
  const json = JSON.stringify(obj);
  // FNV-1a 32-bit — fast, stable within a single replica's cache lifetime
  let h = 0x811c9dc5;
  for (let i = 0; i < json.length; i++) {
    h ^= json.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return `W/"cat-${(h >>> 0).toString(36)}-${json.length.toString(36)}"`;
}

export async function GET(req: Request) {
  const limited = guard(req, "catalog");
  if (limited) return limited;
  try {
    const catalog = await getCatalog();
    const etag = etagOf(catalog);
    if (req.headers.get("if-none-match") === etag) {
      return new Response(null, {
        status: 304,
        headers: { ETag: etag, "Cache-Control": "public, max-age=30, stale-while-revalidate=30" },
      });
    }
    return Response.json(catalog, {
      headers: {
        ETag: etag,
        "Cache-Control": "public, max-age=30, stale-while-revalidate=30",
      },
    });
  } catch (e) {
    console.error("[catalog] failed:", e);
    return Response.json({ ok: false, error: "تعذّر تحميل الكتالوج — أعد المحاولة" }, { status: 500 });
  }
}
