import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";

export const dynamic = "force-dynamic";

export async function GET() {
  const metrics: string[] = [
    "# HELP heal_dashboard_healthy Dashboard health",
    "# TYPE heal_dashboard_healthy gauge",
    "heal_dashboard_healthy 1",
  ];

  try {
    const logsDir = process.env.AUDIT_LOG_DIR || join(process.cwd(), "..", "..", "logs");
    const filePath = join(logsDir, "agent_audit.jsonl");
    const content = await readFile(filePath, "utf-8");
    const lines = content.trim().split("\n").filter(Boolean);
    const fixCount = lines.filter((l) => {
      try {
        return JSON.parse(l).event === "fix_applied";
      } catch {
        return false;
      }
    }).length;
    metrics.push(`# HELP heal_fixes_total Total fixes applied`);
    metrics.push(`# TYPE heal_fixes_total counter`);
    metrics.push(`heal_fixes_total ${fixCount}`);
  } catch {
    metrics.push(`heal_fixes_total 0`);
  }

  return new NextResponse(metrics.join("\n"), {
    headers: { "Content-Type": "text/plain; version=0.0.4; charset=utf-8" },
  });
}
