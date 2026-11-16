#!/usr/bin/env python3
import base64
import binascii
import json
import mimetypes
import os
import re
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

PORT = int(os.environ.get("PORT", "8080"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.realpath(os.path.join(BASE_DIR, "public"))
SUBMISSIONS_DIR = os.path.join(BASE_DIR, "submissions")
MAX_REQUEST_BYTES = 25 * 1024 * 1024
RANGE_PATTERN = re.compile(r"bytes=(\d*)-(\d*)")
FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9_-]+")

os.makedirs(PUBLIC_DIR, exist_ok=True)
os.makedirs(os.path.join(PUBLIC_DIR, "videos"), exist_ok=True)
os.makedirs(SUBMISSIONS_DIR, exist_ok=True)


def get_lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("10.255.255.255", 1))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def safe_filename_component(value, fallback):
    if not isinstance(value, (str, int)):
        return fallback
    component = FILENAME_PATTERN.sub("_", str(value)).strip("_-")
    return component[:80] or fallback


class ShedInspectionHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path != "/api/submit":
            self.send_error(404, "Not Found")
            return

        length_header = self.headers.get("Content-Length")
        if length_header is None:
            self.send_json(411, {"status": "error", "message": "Content-Length is required."})
            return

        try:
            length = int(length_header)
        except ValueError:
            self.send_json(400, {"status": "error", "message": "Invalid Content-Length."})
            return

        if length <= 0:
            self.send_json(400, {"status": "error", "message": "Request body is required."})
            return
        if length > MAX_REQUEST_BYTES:
            self.send_json(413, {"status": "error", "message": "Submission is too large."})
            return

        body = self.rfile.read(length)
        if len(body) != length:
            self.send_json(400, {"status": "error", "message": "Incomplete request body."})
            return

        try:
            data = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"status": "error", "message": "Request body must be valid JSON."})
            return
        if not isinstance(data, dict):
            self.send_json(400, {"status": "error", "message": "JSON object is required."})
            return

        pdf_b64 = data.pop("pdfBase64", None)
        pdf_bytes = None
        if pdf_b64 is not None:
            if not isinstance(pdf_b64, str):
                self.send_json(400, {"status": "error", "message": "pdfBase64 must be a string."})
                return
            try:
                pdf_bytes = base64.b64decode(pdf_b64, validate=True)
            except (binascii.Error, ValueError):
                self.send_json(400, {"status": "error", "message": "pdfBase64 is invalid."})
                return

        loco = safe_filename_component(data.get("locoNo"), "UnknownLoco")
        date = safe_filename_component(data.get("inspDate"), "UnknownDate")
        schedule = safe_filename_component(data.get("schType"), "IA")
        json_filename = f"Inspection_{schedule}_Loco_{loco}_{date}.json"
        pdf_filename = f"Schedule_{schedule}_Loco_{loco}_{date}.pdf"

        try:
            if pdf_bytes is not None:
                with open(os.path.join(SUBMISSIONS_DIR, pdf_filename), "wb") as file:
                    file.write(pdf_bytes)
            with open(os.path.join(SUBMISSIONS_DIR, json_filename), "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
        except OSError as error:
            self.log_error("Could not save submission: %s", error)
            self.send_json(500, {"status": "error", "message": "Unable to save submission."})
            return

        self.send_json(200, {
            "status": "success",
            "json_file": json_filename,
            "pdf_file": pdf_filename if pdf_bytes is not None else None,
        })

    def do_GET(self):
        url_path = unquote(urlparse(self.path).path)
        if url_path in ("", "/"):
            url_path = "/index.html"

        file_path = os.path.realpath(os.path.join(PUBLIC_DIR, url_path.lstrip("/")))
        try:
            is_inside_public = os.path.commonpath((PUBLIC_DIR, file_path)) == PUBLIC_DIR
        except ValueError:
            is_inside_public = False
        if not is_inside_public:
            self.send_error(403, "Forbidden")
            return
        if not os.path.isfile(file_path):
            self.send_error(404, "File Not Found")
            return

        file_size = os.path.getsize(file_path)
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        range_header = self.headers.get("Range")
        start = 0
        end = file_size - 1
        status = 200

        if range_header is not None:
            match = RANGE_PATTERN.fullmatch(range_header.strip())
            if match is None or file_size == 0:
                self.send_range_not_satisfiable(file_size)
                return

            first, last = match.groups()
            if not first and not last:
                self.send_range_not_satisfiable(file_size)
                return
            try:
                if not first:
                    suffix_length = int(last)
                    if suffix_length <= 0:
                        self.send_range_not_satisfiable(file_size)
                        return
                    start = max(file_size - suffix_length, 0)
                else:
                    start = int(first)
                    end = int(last) if last else file_size - 1
                    if start >= file_size or start > end:
                        self.send_range_not_satisfiable(file_size)
                        return
                    end = min(end, file_size - 1)
            except ValueError:
                self.send_range_not_satisfiable(file_size)
                return
            status = 206

        content_length = max(end - start + 1, 0)
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.end_headers()

        with open(file_path, "rb") as file:
            file.seek(start)
            remaining = content_length
            while remaining:
                chunk = file.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)

    def send_range_not_satisfiable(self, file_size):
        self.send_response(416)
        self.send_header("Content-Range", f"bytes */{file_size}")
        self.send_header("Content-Length", "0")
        self.end_headers()


if __name__ == "__main__":
    ip = get_lan_ip()
    print("=" * 60)
    print("  SOUTHERN RAILWAY - ELS / ERODE SECTION-E5B2 SERVER")
    print("=" * 60)
    print(f"  [+] Host Machine IP : http://localhost:{PORT}")
    print(f"  [+] Tablet URL      : http://{ip}:{PORT}")
    print(f"  [+] Submissions Dir : {SUBMISSIONS_DIR}")
    print("=" * 60)
    ThreadingHTTPServer(("0.0.0.0", PORT), ShedInspectionHandler).serve_forever()
