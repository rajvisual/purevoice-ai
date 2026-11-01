#!/usr/bin/env python3
"""
PureVoice AI - Audio & Video Noise Reduction Web Server
======================================================
Zero-dependency Python HTTP Server with audio & video processing pipeline,
range request streaming for video/audio seek, and REST endpoints.
"""

import os
import sys
import json
import mimetypes
import shutil
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from email.message import EmailMessage

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from denoiser_engine import PureVoiceDenoiser

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

denoiser_instance = PureVoiceDenoiser()

class InstaDenoiserHandler(BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Range")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.serve_file(os.path.join(FRONTEND_DIR, "index.html"), "text/html; charset=utf-8")
            return

        # Serve static assets
        if path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            file_path = os.path.join(FRONTEND_DIR, "static", rel_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
                self.serve_file(file_path, mime)
                return
            else:
                self.send_error(404, "Static file not found")
                return

        # Serve output files (audio / video with Range support)
        if path.startswith("/outputs/"):
            filename = os.path.basename(urllib.parse.unquote(path))
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
                self.serve_media_with_range(file_path, mime)
                return
            else:
                self.send_error(404, "Output file not found")
                return

        if path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "PureVoice AI"}).encode("utf-8"))
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/process":
            self.handle_process()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_process(self):
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            self.send_json_response({"error": "Expected multipart/form-data"}, status=400)
            return

        # Parse multipart form data
        boundary = content_type.split("boundary=")[-1].strip()
        if not boundary:
            self.send_json_response({"error": "Missing boundary in multipart/form-data"}, status=400)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        # Parse the multipart boundary chunks
        boundary_bytes = ("--" + boundary).encode("utf-8")
        parts = raw_body.split(boundary_bytes)

        uploaded_filename = None
        file_bytes = None
        preset = "instagram"
        reduction_level = 18

        for part in parts:
            if not part or part == b"--\r\n" or part == b"--":
                continue
            
            # Split headers and content
            header_end = part.find(b"\r\n\r\n")
            if header_end == -1:
                continue
            
            headers_raw = part[:header_end].decode("utf-8", errors="ignore")
            content = part[header_end + 4:]
            if content.endswith(b"\r\n"):
                content = content[:-2]

            if 'name="file"' in headers_raw:
                # Extract filename
                for line in headers_raw.split("\r\n"):
                    if "Content-Disposition" in line:
                        for item in line.split(";"):
                            item = item.strip()
                            if item.startswith("filename="):
                                uploaded_filename = item.split("=", 1)[1].strip('"\'')
                file_bytes = content

            elif 'name="preset"' in headers_raw:
                preset = content.decode("utf-8", errors="ignore").strip()
            elif 'name="reduction_level"' in headers_raw:
                try:
                    reduction_level = int(content.decode("utf-8", errors="ignore").strip())
                except ValueError:
                    reduction_level = 18

        if not uploaded_filename or not file_bytes:
            self.send_json_response({"error": "No file uploaded or file empty"}, status=400)
            return

        safe_filename = os.path.basename(uploaded_filename)
        input_save_path = os.path.join(UPLOAD_DIR, safe_filename)
        with open(input_save_path, "wb") as f:
            f.write(file_bytes)

        try:
            result = denoiser_instance.process_file(
                input_path=input_save_path,
                output_dir=OUTPUT_DIR,
                preset=preset,
                reduction_level=reduction_level
            )
            self.send_json_response(result)
        except Exception as e:
            self.send_json_response({"error": f"Audio processing failed: {str(e)}"}, status=500)

    def send_json_response(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, file_path: str, content_type: str):
        if not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return
        
        with open(file_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(content)

    def serve_media_with_range(self, file_path: str, content_type: str):
        """Supports HTTP 206 Partial Content for video/audio seeking in browser"""
        file_size = os.path.getsize(file_path)
        range_header = self.headers.get("Range")

        if not range_header:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_cors_headers()
            self.end_headers()
            with open(file_path, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
            return

        # Parse range header: e.g. bytes=0-1024 or bytes=1024-
        try:
            byte_range = range_header.replace("bytes=", "").split("-")
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if byte_range[1] else file_size - 1
            if end >= file_size:
                end = file_size - 1
            length = end - start + 1

            self.send_response(206)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.send_cors_headers()
            self.end_headers()

            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = length
                chunk_size = 64 * 1024
                while remaining > 0:
                    read_len = min(remaining, chunk_size)
                    chunk = f.read(read_len)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except Exception:
            pass

def run(host: str = "0.0.0.0", port: int = 8000):
    server_address = (host, port)
    httpd = HTTPServer(server_address, InstaDenoiserHandler)
    print(f"================================================================")
    print(f"  PureVoice AI - Audio & Video Noise Reducer running!")
    print(f"  Access URL: http://localhost:{port} (bound to {host})")
    print(f"================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    env_port = os.environ.get("PORT")
    port = int(env_port) if env_port else 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(host="0.0.0.0", port=port)
