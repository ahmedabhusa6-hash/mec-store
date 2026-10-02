import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    ok: true,
    service: "mec-store",
    mode: process.env.STORE_MODE || "sandbox",
    time: new Date().toISOString(),
  });
}
