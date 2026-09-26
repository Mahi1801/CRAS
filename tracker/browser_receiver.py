from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from threading import Lock

class BrowserState:
    def __init__(self):
        self.lock = Lock()
        self.data = None

    def update(self, data):
        with self.lock:
            self.data = data

    def get(self):
        with self.lock:
            return self.data

browser_state = BrowserState()

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/browser":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                browser_state.update(data)
                self.send_response(200)
            except:
                self.send_response(400)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return  # silence

def start_browser_server(port=8765):
    server = HTTPServer(("127.0.0.1", port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server