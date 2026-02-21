"""Simple health server for the agent (run as separate process or --serve)."""
import http.server
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/health", "/ready"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            ok = bool(os.getenv("GOOGLE_API_KEY"))
            self.wfile.write(json.dumps({
                "status": "ok" if ok else "degraded",
                "ready": ok,
            }).encode())
        elif self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            # Placeholder Prometheus metrics
            self.wfile.write(b"# HELP heal_agent_healthy Agent health\n# TYPE heal_agent_healthy gauge\nheal_agent_healthy 1\n")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    port = int(os.getenv("HEALTH_PORT", "8080"))
    with http.server.HTTPServer(("0.0.0.0", port), HealthHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
