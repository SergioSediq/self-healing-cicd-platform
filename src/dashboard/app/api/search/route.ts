import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";
import { requireAuth } from "../auth";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const authError = requireAuth(request);
  if (authError) return authError;

  const { searchParams } = new URL(request.url);
  const q = (searchParams.get("q") || "").toLowerCase();
  const limit = Math.min(parseInt(searchParams.get("limit") || "20", 10), 100);

  if (!q || q.length < 2) {
    return NextResponse.json({ results: [] });
  }

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
      .filter(Boolean) as { ts?: number; event?: string; run_id?: string; provider?: string; details?: Record<string, unknown> }[];

    const results = entries
      .filter(
        (e) =>
          (e.run_id && (e.run_id as string).toLowerCase().includes(q)) ||
          (e.event && (e.event as string).toLowerCase().includes(q)) ||
          (e.provider && (e.provider as string).toLowerCase().includes(q)) ||
          (e.details && JSON.stringify(e.details).toLowerCase().includes(q))
      )
      .slice(-limit)
      .reverse();

    return NextResponse.json({ results });
  } catch {
    return NextResponse.json({ results: [] });
  }
}
