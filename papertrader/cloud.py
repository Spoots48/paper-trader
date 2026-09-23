"""Cloud mode: the experiment trades on GitHub Actions; this Mac only syncs and views.

config/deployment.json decides the mode. In cloud mode, `run.py cycle` on the Mac performs a sync
(git pull + ledger restore + report notifications) instead of trading, so there is exactly one trader.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time

from .config import CONFIG_DIR, DATA_DIR, REPORTS_DIR, ROOT, load_json
from .nyse_calendar import iso, now_utc

DEPLOY_PATH = CONFIG_DIR / "deployment.json"
SYNC_STATE = DATA_DIR / ".sync.json"
_cache: dict = {}


def deployment() -> dict:
    return load_json(DEPLOY_PATH) if DEPLOY_PATH.exists() else {"mode": "local"}


def in_actions() -> bool:
    return os.environ.get("GITHUB_ACTIONS") == "true"


def cloud_viewer() -> bool:
    return deployment().get("mode") == "cloud" and not in_actions()


def _gh_path() -> str:
    return shutil.which("gh") or next((p for p in ("/opt/homebrew/bin/gh", "/usr/local/bin/gh") if os.path.exists(p)), "gh")


def _run(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "PATH": os.environ.get("PATH", "") + ":/opt/homebrew/bin:/usr/local/bin"}
    return subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout, env=env)


def gh(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return _run([_gh_path(), *args], timeout=timeout)


def sync(notify_new: bool = True) -> dict:
    """Pull the latest cloud state and rebuild local ledgers. Safe to call often."""
    from .statesync import restore
    out = {"at": iso(now_utc())}
    r = _run(["git", "pull", "--ff-only", "--quiet"], timeout=90)
    out["pull_ok"] = r.returncode == 0
    if r.returncode != 0:
        out["error"] = (r.stderr or r.stdout).strip()[-400:]
    try:
        out["restored"] = restore()
    except Exception as e:  # a bad dump must not break the viewer; the previous ledgers stay in place
        out["restore_error"] = f"{type(e).__name__}: {e}"
    prev = json.loads(SYNC_STATE.read_text()) if SYNC_STATE.exists() else {}
    seen = set(prev.get("reports_seen", []))
    current = sorted(p.name for p in REPORTS_DIR.glob("*.json"))
    new = [n for n in current if n not in seen]
    if notify_new and new and prev:  # don't notify for everything on the very first sync
        from .reporting import notify
        for n in new:
            meta = json.loads((REPORTS_DIR / n).read_text())
            h = meta.get("headline") or [[""] * 4]
            notify("Paper Trader", f"Day {meta.get('day')} report ready — {h[0][0]}: {h[0][1]} ({h[0][3].split(' ')[-1]})")
    out["new_reports"] = new
    SYNC_STATE.write_text(json.dumps({**out, "reports_seen": current}))
    return out


def last_sync() -> dict | None:
    try:
        return json.loads(SYNC_STATE.read_text())
    except (OSError, ValueError):
        return None


def status(max_age: float = 60) -> dict:
    """Cloud scheduler status for the UI (cached briefly to avoid hammering the GitHub API)."""
    if _cache.get("t", 0) > time.time() - max_age:
        return _cache["v"]
    d = deployment()
    repo, wf = d.get("repo"), d.get("workflow", "cycle.yml")
    st = {"mode": "cloud", "repo": repo, "url": f"https://github.com/{repo}/actions/workflows/{wf}", "enabled": None, "runs": []}
    r = gh("api", f"repos/{repo}/actions/workflows/{wf}", "--jq", ".state")
    if r.returncode == 0:
        st["enabled"] = r.stdout.strip() == "active"
    else:
        st["error"] = (r.stderr or "").strip()[-300:]
    r = gh("run", "list", "--workflow", wf, "--limit", "15", "--json", "databaseId,status,conclusion,createdAt,updatedAt,event,url")
    if r.returncode == 0:
        st["runs"] = json.loads(r.stdout or "[]")
    st["running"] = any(x.get("status") in ("queued", "in_progress") for x in st["runs"])
    st["last_sync"] = last_sync()
    _cache.update(t=time.time(), v=st)
    return st


def trigger() -> tuple[bool, str]:
    d = deployment()
    r = gh("workflow", "run", d.get("workflow", "cycle.yml"))
    _cache.clear()
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def set_enabled(on: bool) -> tuple[bool, str]:
    d = deployment()
    r = gh("workflow", "enable" if on else "disable", d.get("workflow", "cycle.yml"))
    _cache.clear()
    return r.returncode == 0, (r.stderr or r.stdout).strip()
