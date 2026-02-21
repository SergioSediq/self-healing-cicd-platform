import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";
import { requireAuth } from "../auth";

export const dynamic = "force-dynamic";

/** Export audit log for compliance (CSV or JSON). */
export async function GET(request: Request) {
  const authError = requireAuth(request);
  if (authError) return authError;

  const { searchParams } = new URL(request.url);
  const format = searchParams.get("format") || "json";

  try {
    const logsDir = process.env.AUDIT_LOG_DIR || join(process.cwd(), "..", "..", "logs");
    const filePath = join(logsDir, "agent_audit.jsonl");
    const content = await readFile(filePath, "utf-8");
    const lines = content.trim().split("\n").filter(Boolean);
    const entries = lines
      .map((line) => {
        try {
          return JSON.parse(line);
        } catch {
          return null;
        }
      })
      .filter(Boolean);

    if (format === "csv") {
      const header = "timestamp,event,run_id,provider,details\n";
      const rows = entries
        .map(
          (e: { ts?: number; event?: string; run_id?: string; provider?: string; details?: object }) =>
            `${e.ts ?? ""},${e.event ?? ""},${e.run_id ?? ""},${e.provider ?? ""},"${JSON.stringify(e.details ?? {}).replace(/"/g, '""')}"`
        )
        .join("\n");
      return new NextResponse(header + rows, {
        headers: {
          "Content-Type": "text/csv",
          "Content-Disposition": "attachment; filename=audit_export.csv",
        },
      });
    }
    return NextResponse.json(entries, {
      headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json({ error: "Audit log not found" }, { status: 404 });
  }
}
