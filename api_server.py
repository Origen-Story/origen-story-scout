"""
API server for Origen Story Scout dashboard.
Run alongside the Vite dev server to provide backend functionality.
"""

import subprocess
import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Track running scout process
scout_process = None
scout_output = []
scout_running = False


class APIHandler(BaseHTTPRequestHandler):
    """HTTP handler for scout API endpoints."""

    def log_message(self, format, *args):
        """Suppress default logging, use custom format."""
        print(f"[API] {args[0]}")

    def send_json(self, data, status=200):
        """Send a JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/api/scout/status":
            self.handle_status()
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/api/scout":
            self.handle_scout()
        else:
            self.send_json({"error": "Not found"}, 404)

    def handle_status(self):
        """Return current scout status."""
        global scout_running, scout_output
        self.send_json({
            "running": scout_running,
            "output": scout_output[-50:] if scout_output else []  # Last 50 lines
        })

    def handle_scout(self):
        """Trigger the scouting pipeline."""
        global scout_running, scout_process, scout_output

        if scout_running:
            self.send_json({"error": "Scout already running"}, 409)
            return

        try:
            # Read request body for options
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b'{}'
            options = json.loads(body) if body else {}

            # Start scout in background
            scout_output = []
            scout_running = True

            def run_scout():
                global scout_running, scout_process, scout_output

                cmd = [sys.executable, "-m", "src.main", "run", "--force"]
                if options.get("summarize", True):
                    cmd.append("--summarize")

                try:
                    scout_output.append(f"Starting: {' '.join(cmd)}")
                    scout_process = subprocess.Popen(
                        cmd,
                        cwd=Path(__file__).parent,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )

                    # Stream output
                    for line in scout_process.stdout:
                        line = line.strip()
                        if line:
                            scout_output.append(line)
                            print(f"[Scout] {line}")

                    scout_process.wait()
                    scout_output.append(f"Completed with code: {scout_process.returncode}")

                except Exception as e:
                    scout_output.append(f"Error: {str(e)}")

                finally:
                    scout_running = False
                    scout_process = None

            thread = threading.Thread(target=run_scout, daemon=True)
            thread.start()

            self.send_json({"status": "started", "message": "Scout pipeline started"})

        except Exception as e:
            scout_running = False
            self.send_json({"error": str(e)}, 500)


def main():
    """Start the API server."""
    port = 3001
    server = HTTPServer(("127.0.0.1", port), APIHandler)
    print(f"Scout API server running at http://localhost:{port}")
    print("Endpoints:")
    print("  POST /api/scout - Start scouting")
    print("  GET  /api/scout/status - Check status")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down API server...")
        server.shutdown()


if __name__ == "__main__":
    main()