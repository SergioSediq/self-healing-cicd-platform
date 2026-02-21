import { NextResponse } from "next/server";

const RATE_LIMIT = parseInt(process.env.RATE_LIMIT_PER_MINUTE || "60", 10);
const windowMs = 60_000;
const hits = new Map<string, { count: number; resetAt: number }>();

function getClientKey(request: Request): string {
  return request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
}

export function middleware(request: Request) {
  if (process.env.RATE_LIMIT_DISABLED === "1") {
    return NextResponse.next();
  }
  const key = getClientKey(request);
  const now = Date.now();
  const record = hits.get(key);
  if (!record) {
    hits.set(key, { count: 1, resetAt: now + windowMs });
    return NextResponse.next();
  }
  if (now > record.resetAt) {
    hits.set(key, { count: 1, resetAt: now + windowMs });
    return NextResponse.next();
  }
  record.count++;
  if (record.count > RATE_LIMIT) {
    return new NextResponse("Rate limit exceeded", { status: 429 });
  }
  return NextResponse.next();
}

export const config = { matcher: ["/api/:path*"] };
