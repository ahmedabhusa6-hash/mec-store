export const dynamic = "force-dynamic";

export async function GET() {
  return Response.json({
    ok: true,
    service: "mec-intelligence",
    version: "2.2.0",
    time: new Date().toISOString(),
  });
}
