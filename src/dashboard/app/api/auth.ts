/** API auth with RBAC: viewer (read-only) vs approver (can trigger actions). */
export type Role = "viewer" | "approver" | null;

export function requireAuth(request: Request): Response | null {
  const viewerKey = process.env.DASHBOARD_VIEWER_KEY || process.env.DASHBOARD_API_KEY;
  const approverKey = process.env.DASHBOARD_APPROVER_KEY;
  if (!viewerKey && !approverKey) return null;

  const auth = request.headers.get("authorization");
  if (!auth || !auth.startsWith("Bearer ")) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }
  const token = auth.slice(7);
  if (approverKey && token === approverKey) return null; // approver allowed
  if (viewerKey && token === viewerKey) return null;     // viewer allowed
  return new Response(JSON.stringify({ error: "Forbidden" }), {
    status: 403,
    headers: { "Content-Type": "application/json" },
  });
}

export function getRole(request: Request): Role {
  const approverKey = process.env.DASHBOARD_APPROVER_KEY;
  const viewerKey = process.env.DASHBOARD_VIEWER_KEY || process.env.DASHBOARD_API_KEY;
  const auth = request.headers.get("authorization");
  if (!auth?.startsWith("Bearer ")) return null;
  const token = auth.slice(7);
  if (approverKey && token === approverKey) return "approver";
  if (viewerKey && token === viewerKey) return "viewer";
  return null;
}
