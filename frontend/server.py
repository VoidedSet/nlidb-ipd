#!/usr/bin/env python3
"""
Simple HTTP server for serving the Querify frontend.
Includes CORS support for API requests.

Usage:
    python server.py          # Runs on http://localhost:8080
    python server.py 3000     # Runs on http://localhost:3000
"""

import http.server
import socketserver
import sys
import os
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Serve index.html for root path
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        return super().do_GET()

    def log_message(self, format, *args):
        """Log server messages in a more readable format."""
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def run_server():
    os.chdir(Path(__file__).parent)
    
    try:
        with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
            print(f"🚀 Querify Frontend Server")
            print(f"📍 Serving at http://localhost:{PORT}")
            print(f"🔗 API Backend: http://localhost:8000")
            print(f"📁 Serving from: {Path.cwd()}")
            print(f"\n⌨️  Press Ctrl+C to stop the server\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Port already in use
            print(f"❌ Port {PORT} is already in use.")
            print(f"💡 Try: python server.py {PORT + 1}")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
