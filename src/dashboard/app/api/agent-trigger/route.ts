import { NextResponse } from "next/server";
import { requireAuth } from "../auth";
import { spawn } from "child_process";
import { join } from "path";

export const dynamic = "force-dynamic";

/** Trigger agent via CLI. Requires approver role in production. */
export async function POST(request: Request) {
  const authError = requireAuth(request);
  if (authError) return authError;

  try {
    const body = await request.json();
    const logs = (body.logs as string) || "";
    const dryRun = body.dry_run !== false;

    const agentPath = join(process.cwd(), "..", "..", "src", "agent");
    const mainPy = join(agentPath, "main.py");

    return new Promise<NextResponse>((resolve) => {
      const args = ["--provider", "local", "--logs", logs.slice(0, 50000)];
      if (dryRun) args.push("--dry-run");

      const proc = spawn("python", [mainPy, ...args], {
        cwd: agentPath,
        env: { ...process.env, PYTHONPATH: agentPath },
      });

      let stderr = "";
      proc.stderr?.on("data", (d) => (stderr += d.toString()));
      proc.on("close", (code) => {
        if (code === 0) {
          resolve(NextResponse.json({ ok: true, message: "Agent completed (dry-run)" }));
        } else {
          resolve(NextResponse.json({ ok: false, message: stderr || `Exit ${code}` }, { status: 500 }));
        }
      });
      proc.on("error", (e) => {
        resolve(NextResponse.json({ ok: false, message: e.message }, { status: 500 }));
      });
    });
  } catch (e) {
    return NextResponse.json({ ok: false, message: String(e) }, { status: 500 });
  }
}
