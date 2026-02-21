import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const checks: Record<string, boolean> = {
    dashboard: true,
  };
  if (process.env.CHECK_GITHUB === "1") {
    try {
      const r = await fetch("https://api.github.com", { signal: AbortSignal.timeout(3000) });
      checks.github = r.ok;
    } catch {
      checks.github = false;
    }
  }
  const ok = Object.values(checks).every(Boolean);
  return NextResponse.json({
    status: ok ? "ok" : "degraded",
    ready: true,
    checks,
  });
}
