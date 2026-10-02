import { NextRequest, NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import path from 'path'

const REPORT_PATH = path.join(process.cwd(), 'public', 'reports', 'pre-execution-diagnostic-report-2026-10-02.md')
const DOWNLOAD_NAME = 'تقرير_التشخيص_ما_قبل_التنفيذ_2026-10-02.md'

export async function GET(_request: NextRequest) {
  try {
    const fileBuffer = await readFile(REPORT_PATH)
    const encodedName = encodeURIComponent(DOWNLOAD_NAME)

    return new NextResponse(new Uint8Array(fileBuffer), {
      status: 200,
      headers: {
        'Content-Type': 'text/markdown; charset=utf-8',
        'Content-Disposition': `attachment; filename="pre-execution-diagnostic-report-2026-10-02.md"; filename*=UTF-8''${encodedName}`,
        'Content-Length': String(fileBuffer.byteLength),
        'Cache-Control': 'no-store',
      },
    })
  } catch {
    return NextResponse.json({ error: 'Report file not found' }, { status: 404 })
  }
}
