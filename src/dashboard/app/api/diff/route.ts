import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

/** Compute diff between original and proposed content (simple line-by-line). */
export async function POST(request: Request) {
  try {
    const { original, proposed } = (await request.json()) as {
      original?: string;
      proposed?: string;
    };
    if (!original || !proposed) {
      return NextResponse.json({ error: "original and proposed required" }, { status: 400 });
    }
    const a = (original as string).split("\n");
    const b = (proposed as string).split("\n");
    const diff: { type: "add" | "del" | "ctx"; line: string; num?: number }[] = [];
    let i = 0,
      j = 0;
    while (i < a.length || j < b.length) {
      if (i < a.length && j < b.length && a[i] === b[j]) {
        diff.push({ type: "ctx", line: a[i], num: i + 1 });
        i++;
        j++;
      } else if (j < b.length && (i >= a.length || !a.slice(i).includes(b[j]))) {
        diff.push({ type: "add", line: b[j], num: j + 1 });
        j++;
      } else if (i < a.length) {
        diff.push({ type: "del", line: a[i], num: i + 1 });
        i++;
      } else {
        j++;
      }
    }
    return NextResponse.json({ diff });
  } catch {
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
}
