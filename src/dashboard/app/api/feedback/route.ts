import { NextResponse } from "next/server";
import { appendFile } from "fs/promises";
import { join } from "path";
import { requireAuth } from "../auth";

export const dynamic = "force-dynamic";

/** Collect thumbs up/down feedback on fixes. */
export async function POST(request: Request) {
  const authError = requireAuth(request);
  if (authError) return authError;

  try {
    const body = await request.json();
    const { run_id, feedback, correlation_id, comment } = body as {
      run_id?: string;
      feedback?: "up" | "down";
      correlation_id?: string;
      comment?: string;
    };
    if (!feedback || !["up", "down"].includes(feedback)) {
      return NextResponse.json({ error: "feedback must be 'up' or 'down'" }, { status: 400 });
    }
    const logsDir = process.env.AUDIT_LOG_DIR || join(process.cwd(), "..", "..", "logs");
    const feedbackPath = join(logsDir, "feedback.jsonl");
    const entry = JSON.stringify({
      ts: Date.now() / 1000,
      run_id: run_id ?? "",
      correlation_id: correlation_id ?? "",
      feedback,
      comment: comment ?? "",
    }) + "\n";
    await appendFile(feedbackPath, entry);
    return NextResponse.json({ ok: true });
  } catch (e) {
    return NextResponse.json({ error: "Failed to record feedback" }, { status: 500 });
  }
}
