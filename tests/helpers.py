"""Testhilfen: Server im Hintergrund, Mini-SMTP-Server, Fake-JARVIS-Gateway."""
import http.cookiejar
import json
import os
import re
import socketserver
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from wochenteller import db, server


class FakeSMTP(socketserver.ThreadingTCPServer):
    """Versteht gerade genug SMTP, um Nachrichten von smtplib anzunehmen."""
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self):
        self.messages = []
        super().__init__(("127.0.0.1", 0), _SMTPHandler)
        threading.Thread(target=self.serve_forever, daemon=True).start()

    @property
    def port(self):
        return self.server_address[1]


class _SMTPHandler(socketserver.StreamRequestHandler):
    def w(self, s):
        self.wfile.write((s + "\r\n").encode())

    def handle(self):
        self.w("220 fake ESMTP")
        rcpt, data_mode, buf = [], False, []
        while True:
            line = self.rfile.readline()
            if not line:
                return
            text = line.decode("utf-8", "replace").rstrip("\r\n")
            if data_mode:
                if text == ".":
                    data_mode = False
                    self.server.messages.append({"to": rcpt, "data": "\n".join(buf)})
                    rcpt, buf = [], []
                    self.w("250 OK")
                else:
                    buf.append(text[1:] if text.startswith("..") else text)
                continue
            cmd = text.upper()
            if cmd.startswith("EHLO") or cmd.startswith("HELO"):
                self.w("250-fake")
                self.w("250 8BITMIME")
            elif cmd.startswith("MAIL FROM"):
                self.w("250 OK")
            elif cmd.startswith("RCPT TO"):
                rcpt.append(text.split(":", 1)[1].strip(" <>"))
                self.w("250 OK")
            elif cmd == "DATA":
                data_mode = True
                self.w("354 go")
            elif cmd == "QUIT":
                self.w("221 bye")
                return
            else:
                self.w("250 OK")


class FakeGateway(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self):
        self.sent = []
        super().__init__(("127.0.0.1", 0), _GWHandler)
        threading.Thread(target=self.serve_forever, daemon=True).start()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server_address[1]}/send"


class _GWHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        self._json({"success": True, "ready": True})

    def do_POST(self):
        if self.headers.get("Origin"):
            return self._json({"success": False, "error": "origin"}, 403)
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.sent.append(body)
        self._json({"success": True, "msgId": "m%d" % len(self.server.sent), "status": "sent"})

    def _json(self, obj, status=200):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class AppServer:
    def __init__(self):
        self.tmp = tempfile.mkdtemp()
        db.init(os.path.join(self.tmp, "t.db"))
        server.SETTINGS.setup_code = "ABCDE-FGHIJ"
        self.httpd = server.make_server("127.0.0.1", 0)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    def client(self):
        return Client(self.base)


class Client:
    def __init__(self, base):
        self.base = base
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.csrf = None

    def req(self, method, path, body=None, csrf=True, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        h = {"Content-Type": "application/json"} if data is not None else {}
        if csrf and self.csrf and method != "GET":
            h["X-CSRF-Token"] = self.csrf
        h.update(headers or {})
        r = urllib.request.Request(self.base + "/api/" + path, data=data, method=method, headers=h)
        try:
            with self.opener.open(r, timeout=30) as resp:
                return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def ok(self, method, path, body=None):
        st, res = self.req(method, path, body)
        assert st == 200, (method, path, st, res)
        return res

    def login(self, username, password):
        st, res = self.req("POST", "login", {"username": username, "password": password})
        if st == 200:
            self.csrf = res["csrf"]
        return st, res


def find_code(text):
    m = re.search(r"\b(\d{6})\b", text)
    return m.group(1) if m else None
