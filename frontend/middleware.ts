import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const ADMIN_USER = process.env.ADMIN_USER || "admin";
const ADMIN_PASS = process.env.ADMIN_PASS;

export function middleware(req: NextRequest) {
  if (!req.nextUrl.pathname.startsWith("/admin")) {
    return NextResponse.next();
  }

  if (!ADMIN_PASS) {
    return new NextResponse("Admin password not configured", { status: 500 });
  }

  const authHeader = req.headers.get("authorization");
  const expected = `Basic ${Buffer.from(`${ADMIN_USER}:${ADMIN_PASS}`).toString("base64")}`;

  if (authHeader === expected) {
    return NextResponse.next();
  }

  const res = new NextResponse("Unauthorized", { status: 401 });
  res.headers.set("WWW-Authenticate", 'Basic realm="Admin", charset="UTF-8"');
  return res;
}

export const config = {
  matcher: ["/admin/:path*"],
};
