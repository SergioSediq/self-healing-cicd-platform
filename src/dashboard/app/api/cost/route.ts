import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";
import { requireAuth } from "../auth";

export const dynamic = "force-dynamic";

/** Cost dashboard: token usage over time. */
export async function GET(request: Request) {
  const authError = requireAuth(request);
  if (authError) return authError;

  const { searchParams } = new URL(request.url);
  const days = parseInt(searchParams.get("days") || "7", 10);

  try {
    const logsDir = process.env.AUDIT_LOG_DIR || join(process.cwd(), "..", "..", "logs");
    const tokenPath = join(logsDir, "token_usage.jsonl");
    const content = await readFile(tokenPath, "utf-8").catch(() => "");
    const lines = content.trim().split("\n").filter(Boolean);
    const cutoff = Date.now() / 1000 - days * 86400;
    const entries = lines
      .map((line) => {
        try {
          return JSON.parse(line);
        } catch {
          return null;
        }
      })
      .filter(Boolean) as { run_id?: string; model?: string; input_tokens?: number; output_tokens?: number; total?: number }[];

    const totalTokens = entries.reduce((s, e) => s + (e.total ?? 0), 0);
    const byModel = entries.reduce((acc, e) => {
      const m = e.model ?? "unknown";
      acc[m] = (acc[m] ?? 0) + (e.total ?? 0);
      return acc;
    }, {} as Record<string, number>);

    return NextResponse.json({
      total_tokens: totalTokens,
      by_model: byModel,
      runs: entries.length,
      days,
    });
  } catch {
    return NextResponse.json({ total_tokens: 0, by_model: {}, runs: 0, days });
  }
}
