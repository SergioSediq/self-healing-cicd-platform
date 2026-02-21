import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";
import { requireAuth } from "../auth";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const authError = requireAuth(request);
  if (authError) return authError;
  const { searchParams } = new URL(request.url);
  const limit = Math.min(parseInt(searchParams.get("limit") || "50", 10), 200);
  const offset = Math.max(0, parseInt(searchParams.get("offset") || "0", 10));
  const statusFilter = searchParams.get("status");
  const retentionDays = parseInt(searchParams.get("retention_days") || "0", 10);
  const fromDate = searchParams.get("from");
  const toDate = searchParams.get("to");

  try {
    const logsDir = process.env.AUDIT_LOG_DIR || join(process.cwd(), "..", "..", "logs");
    const filePath = join(logsDir, "agent_audit.jsonl");
    const content = await readFile(filePath, "utf-8");
    const lines = content.trim().split("\n").filter(Boolean);
    let entries = lines.map((line: string) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    }).filter(Boolean) as { event?: string; ts?: number }[];

    if (statusFilter) {
      entries = entries.filter((e) => e.event === statusFilter);
    }
    if (retentionDays > 0) {
      const cutoff = Date.now() / 1000 - retentionDays * 86400;
      entries = entries.filter((e) => (e.ts ?? 0) >= cutoff);
    }
    if (fromDate) {
      const fromTs = new Date(fromDate).getTime() / 1000;
      entries = entries.filter((e) => (e.ts ?? 0) >= fromTs);
    }
    if (toDate) {
      const toTs = new Date(toDate).getTime() / 1000;
      entries = entries.filter((e) => (e.ts ?? 0) <= toTs);
    }
    const reversed = [...entries].reverse();
    const sliced = reversed.slice(offset, offset + limit);

    return NextResponse.json({ history: sliced, total: reversed.length });
  } catch {
    return NextResponse.json({ history: [], total: 0 });
  }
}
