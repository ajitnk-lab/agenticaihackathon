#!/usr/bin/env python3
"""
Simple HTTP server for dashboard
"""

import http.server
import socketserver
import os

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/dashboard_simple.html'
        return super().do_GET()

os.chdir('/persistent/home/ubuntu/workspace/agenticaihackathon')
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"✅ Dashboard running at: http://localhost:{PORT}")
    print("🔗 Access your security dashboard now!")
    httpd.serve_forever()
