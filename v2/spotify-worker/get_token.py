#!/usr/bin/env python3
"""One-shot helper: gets your Spotify refresh token and saves it to ../token.md (gitignored)."""
import base64, getpass, json, os, threading, urllib.parse, urllib.request, urllib.error, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

REDIRECT = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-recently-played"

client_id = input("Client ID: ").strip()
client_secret = getpass.getpass("Client secret (hidden as you paste): ").strip()

result = {}

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        result["code"] = (q.get("code") or [None])[0]
        result["error"] = (q.get("error") or [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Done! You can close this tab and go back to the terminal.")
        threading.Thread(target=self.server.shutdown, daemon=True).start()
    def log_message(self, *a):
        pass

server = HTTPServer(("127.0.0.1", 8888), H)
url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
    "client_id": client_id, "response_type": "code",
    "redirect_uri": REDIRECT, "scope": SCOPE,
})
print("\nOpening your browser. Click Accept...")
webbrowser.open(url)
server.serve_forever()

if not result.get("code"):
    raise SystemExit(f"No code received. Error: {result.get('error')}")

auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
req = urllib.request.Request(
    "https://accounts.spotify.com/api/token",
    data=urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": result["code"],
        "redirect_uri": REDIRECT,
    }).encode(),
    headers={"Authorization": "Basic " + auth,
             "Content-Type": "application/x-www-form-urlencoded"},
)
try:
    data = json.load(urllib.request.urlopen(req))
except urllib.error.HTTPError as e:
    raise SystemExit("Spotify said: " + e.read().decode())

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "token.md")
with open(path, "w") as f:
    f.write(data["refresh_token"] + "\n")
print("\nSuccess! Refresh token saved to v2/token.md (not shown here, not committed).")
