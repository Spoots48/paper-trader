"""Local control panel: a tiny HTTP server (127.0.0.1 only) serving the UI, a JSON API and controls.

The Mac app ("Paper Trader.app") starts this server and shows it in a native window.
`export_static()` also writes dashboard/index.html, a read-only snapshot that opens in any browser.
"""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from .config import DASHBOARD_DIR, LOCK_PATH, LOG_DIR, REPORTS_DIR, ROOT
from .cloud import cloud_viewer, deployment, set_enabled as cloud_set_enabled, sync, trigger as cloud_trigger
from .state import PAUSE_FLAG, full_state

UI_PATH = Path(__file__).parent / "ui" / "index.html"
PORT = int(os.environ.get("PT_PORT", "8765"))
PY = sys.executable


def cycle_running() -> bool:
    try:
        with open(LOCK_PATH, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(f, fcntl.LOCK_UN)
        return False
    except BlockingIOError:
        return True


def export_static() -> Path:
    DASHBOARD_DIR.mkdir(exist_ok=True)
    state = json.dumps(full_state(), default=str).replace("</", "<\\/")
    html = UI_PATH.read_text().replace("/*__STATE__*/", f"window.__STATE__ = {state};")
    out = DASHBOARD_DIR / "index.html"
    tmp = out.with_suffix(".tmp")
    tmp.write_text(html)
    tmp.replace(out)
    return out


def _script(name: str) -> subprocess.CompletedProcess:
    return subprocess.run(["/bin/bash", str(ROOT / "scripts" / name)], capture_output=True, text=True, timeout=60)


class Handler(BaseHTTPRequestHandler):
    server_version = "PaperTrader/1.0"

    def log_message(self, fmt, *args):  # keep the terminal quiet
        pass

    def _send(self, code: int, body: bytes, ctype: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200) -> None:
        self._send(code, json.dumps(obj, default=str).encode())

    def _allowed_post(self) -> bool:
        # Only the local UI may trigger actions: require a custom header (blocked cross-origin without CORS) and a local Origin.
        origin = self.headers.get("Origin")
        ok_origin = origin in (None, f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}")
        return self.headers.get("X-PT") == "1" and ok_origin

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            return self._send(200, UI_PATH.read_bytes(), "text/html; charset=utf-8")
        if u.path == "/api/ping":
            return self._json({"ok": True})
        if u.path == "/api/state":
            st = full_state()
            st["cycle_running"] = bool(st["scheduler"].get("running")) if st["scheduler"].get("mode") == "cloud" else cycle_running()
            return self._json(st)
        if u.path == "/api/log":
            n = int(parse_qs(u.query).get("lines", ["200"])[0])
            p = LOG_DIR / "cycle.log"
            if cloud_viewer():
                p = ROOT / "state" / "cycle_log_tail.txt"
            lines = p.read_text(errors="replace").splitlines()[-n:] if p.exists() else []
            return self._json({"lines": lines, "running": cycle_running()})
        if u.path.startswith("/reports/"):
            name = Path(u.path).name
            p = REPORTS_DIR / name
            if p.parent == REPORTS_DIR and p.exists() and p.suffix in (".html", ".md"):
                ctype = "text/html; charset=utf-8" if p.suffix == ".html" else "text/plain; charset=utf-8"
                return self._send(200, p.read_bytes(), ctype)
        return self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        if not self._allowed_post():
            return self._json({"error": "forbidden"}, 403)
        u = urlparse(self.path)
        if cloud_viewer():
            if u.path == "/api/run":
                ok, msg = cloud_trigger()
                return self._json({"started": ok, "reason": msg or "started in the cloud", "cloud": True})
            if u.path in ("/api/pause", "/api/resume"):
                ok, msg = cloud_set_enabled(u.path == "/api/resume")
                return self._json({"ok": ok, "paused": u.path == "/api/pause", "output": msg})
            if u.path == "/api/sync":
                return self._json(sync())
            if u.path == "/api/open-github":
                subprocess.run(["open", f"https://github.com/{deployment().get('repo')}"])
                return self._json({"ok": True})
        if u.path == "/api/run":
            if cycle_running():
                return self._json({"started": False, "reason": "a cycle is already running"})
            if PAUSE_FLAG.exists():
                return self._json({"started": False, "reason": "paused — resume first"})
            subprocess.Popen([PY, str(ROOT / "run.py"), "cycle", "--trigger", "app"], cwd=str(ROOT),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            return self._json({"started": True})
        if u.path == "/api/pause":
            PAUSE_FLAG.write_text("paused from the app\n")
            return self._json({"paused": True})
        if u.path == "/api/resume":
            PAUSE_FLAG.unlink(missing_ok=True)
            return self._json({"paused": False})
        if u.path == "/api/scheduler/install":
            r = _script("install_scheduler.sh")
            return self._json({"ok": r.returncode == 0, "output": (r.stdout + r.stderr)[-2000:]})
        if u.path == "/api/scheduler/uninstall":
            r = _script("uninstall_scheduler.sh")
            return self._json({"ok": r.returncode == 0, "output": (r.stdout + r.stderr)[-2000:]})
        if u.path == "/api/open-folder":
            subprocess.run(["open", str(ROOT)])
            return self._json({"ok": True})
        if u.path == "/api/export":
            return self._json({"path": str(export_static())})
        return self._json({"error": "not found"}, 404)


def serve(port: int = PORT) -> None:
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    if cloud_viewer():
        def _sync_loop():
            import time
            while True:
                try:
                    sync()
                except Exception as e:  # keep serving the last good state
                    print(f"sync failed: {e}", flush=True)
                time.sleep(180)
        threading.Thread(target=_sync_loop, daemon=True).start()
    print(f"Paper Trader control panel on http://127.0.0.1:{port}", flush=True)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        t.join()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    serve()
