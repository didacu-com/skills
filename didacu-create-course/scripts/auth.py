#!/usr/bin/env python3
"""
Didacu CLI auth — localhost callback flow.

1. Starts a temporary local HTTP server
2. Opens browser to didacu.com/cli-auth?port=PORT&state=STATE
3. User logs in (if needed) and clicks "Authorize CLI"
4. Website generates an API key and redirects to http://127.0.0.1:PORT/callback
5. Script verifies state, validates api_url, saves credentials securely, exits
"""

import html
import http.server
import json
import os
import re
import secrets
import socket
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

CREDENTIALS_PATH = Path.home() / ".didacu" / "credentials.json"
DIDACU_URL = "https://didacu.com"
ALLOWED_API_URL = re.compile(r"^https://[\w.-]+\.didacu\.com(/.*)?$")
TIMEOUT_SECONDS = 120

result = {"success": False}


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def save_credentials(data):
    """Write credentials file with restrictive permissions from the start."""
    creds_dir = CREDENTIALS_PATH.parent
    creds_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(creds_dir, 0o700)

    content = json.dumps(data, indent=2).encode()
    fd = os.open(CREDENTIALS_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, content)
    finally:
        os.close(fd)


def validate_api_url(url):
    """Ensure api_url is HTTPS on a *.didacu.com domain."""
    return bool(url and ALLOWED_API_URL.match(url))


def html_page(body):
    return (
        f"<html><body style='font-family:system-ui;text-align:center;padding:60px'>"
        f"{body}</body></html>"
    ).encode()


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        params = parse_qs(parsed.query)
        state = params.get("state", [None])[0]
        api_key = params.get("key", [None])[0]
        api_url = params.get("api_url", [None])[0]
        error = params.get("error", [None])[0]

        # Verify state token to prevent CSRF
        if state != self.server.expected_state:
            self.send_response(403)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html_page(
                "<h2>Authentication rejected</h2>"
                "<p>Invalid state token. This request did not originate from your CLI session.</p>"
                "<p>You can close this tab.</p>"
            ))
            threading.Thread(target=self.server.shutdown).start()
            return

        if error:
            safe_error = html.escape(error)
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html_page(
                f"<h2>Authentication failed</h2><p>{safe_error}</p>"
                f"<p>You can close this tab.</p>"
            ))
            result["success"] = False
            result["error"] = error
            threading.Thread(target=self.server.shutdown).start()
            return

        if not api_key or not api_url:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html_page(
                "<h2>Missing credentials</h2>"
                "<p>You can close this tab.</p>"
            ))
            threading.Thread(target=self.server.shutdown).start()
            return

        # Validate api_url against allowlist
        if not validate_api_url(api_url):
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html_page(
                "<h2>Invalid API URL</h2>"
                "<p>The returned API URL is not a recognized didacu domain.</p>"
                "<p>You can close this tab.</p>"
            ))
            threading.Thread(target=self.server.shutdown).start()
            return

        save_credentials({"api_key": api_key, "api_url": api_url})

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html_page(
            "<h2>Authenticated!</h2>"
            "<p>You can close this tab and return to your terminal.</p>"
        ))

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
    state = secrets.token_urlsafe(32)

    server = http.server.HTTPServer(("127.0.0.1", port), CallbackHandler)
    server.expected_state = state
    server.timeout = TIMEOUT_SECONDS

    auth_url = f"{DIDACU_URL}/cli-auth?callback_port={port}&state={state}"

    print("Opening browser to authenticate...", file=sys.stderr)
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
