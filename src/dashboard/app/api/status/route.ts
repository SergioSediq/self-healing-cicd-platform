import { NextResponse } from "next/server";
import { readFile } from "fs/promises";
import { join } from "path";
import { requireAuth } from "../auth";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const authError = requireAuth(request);
  if (authError) return authError;

  try {
    const filePath = join(process.cwd(), "public", "status.json");
    const data = await readFile(filePath, "utf-8");
    const json = JSON.parse(data);
    return NextResponse.json(json, {
      headers: {
        "Cache-Control": "private, max-age=2, stale-while-revalidate=5",
      },
    });
  } catch {
    return NextResponse.json(
      { status: "idle", error: "Status file not found" },
      { status: 200, headers: { "Cache-Control": "private, max-age=2" } }
    );
  }
}
