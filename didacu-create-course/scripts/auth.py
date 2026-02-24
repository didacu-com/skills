#!/usr/bin/env python3
"""
Didacu CLI auth — localhost callback flow.

1. Starts a temporary local HTTP server
2. Opens browser to didacu.com/cli-auth?port=PORT
3. User logs in (if needed) and clicks "Authorize CLI"
4. Website generates an API key and redirects to http://127.0.0.1:PORT/callback
5. Script captures credentials, saves to ~/.didacu/credentials.json, exits
"""

import http.server
import json
import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

CREDENTIALS_PATH = Path.home() / ".didacu" / "credentials.json"
DIDACU_URL = os.environ.get("DIDACU_WEB_URL", "https://didacu.com")
TIMEOUT_SECONDS = 120

result = {"success": False}


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        params = parse_qs(parsed.query)
        api_key = params.get("key", [None])[0]
        api_url = params.get("api_url", [None])[0]
        error = params.get("error", [None])[0]

        if error:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                f"<html><body><h2>Authentication failed</h2><p>{error}</p>"
                "<p>You can close this tab.</p></body></html>".encode()
            )
            result["success"] = False
            result["error"] = error
            threading.Thread(target=self.server.shutdown).start()
            return

        if not api_key or not api_url:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h2>Missing credentials</h2>"
                b"<p>You can close this tab.</p></body></html>"
            )
            threading.Thread(target=self.server.shutdown).start()
            return

        # Save credentials
        CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
        CREDENTIALS_PATH.write_text(
            json.dumps({"api_key": api_key, "api_url": api_url}, indent=2)
        )
        os.chmod(CREDENTIALS_PATH, 0o600)

        # Success response
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<html><body style='font-family:system-ui;text-align:center;padding:60px'>"
            b"<h2>Authenticated!</h2>"
            b"<p>You can close this tab and return to your terminal.</p>"
            b"</body></html>"
        )

        result["success"] = True
        result["api_key"] = api_key
        result["api_url"] = api_url
        threading.Thread(target=self.server.shutdown).start()

    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def main():
    # Check if already authenticated
    if CREDENTIALS_PATH.exists():
        try:
            creds = json.loads(CREDENTIALS_PATH.read_text())
            if creds.get("api_key") and creds.get("api_url"):
                print(json.dumps({"authenticated": True, **creds}))
                return
        except (json.JSONDecodeError, KeyError):
            pass

    port = find_free_port()
    server = http.server.HTTPServer(("127.0.0.1", port), CallbackHandler)
    server.timeout = TIMEOUT_SECONDS

    auth_url = f"{DIDACU_URL}/cli-auth?callback_port={port}"

    print(f"Opening browser to authenticate...", file=sys.stderr)
    print(f"If the browser doesn't open, visit: {auth_url}", file=sys.stderr)
    webbrowser.open(auth_url)

    # Run with timeout
    timer = threading.Timer(TIMEOUT_SECONDS, server.shutdown)
    timer.start()
    try:
        server.serve_forever()
    finally:
        timer.cancel()

    if result["success"]:
        print(json.dumps({
            "authenticated": True,
            "api_key": result["api_key"],
            "api_url": result["api_url"],
        }))
    else:
        error = result.get("error", "Authentication timed out")
        print(json.dumps({"authenticated": False, "error": error}))
        sys.exit(1)


if __name__ == "__main__":
    main()
