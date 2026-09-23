"""Move ledger state between SQLite files (used at runtime) and text dumps in state/ (committed to git).

Text dumps make every change a readable, versioned diff and keep the repository small.
  python -m papertrader.statesync dump      # after a cloud cycle
  python -m papertrader.statesync restore   # before a cloud cycle, or on the Mac to view the latest state
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import sys

from .config import DATA_DIR, LOG_DIR, ROOT, load_experiment

STATE_DIR = ROOT / "state"
MARKER = DATA_DIR / ".restored.json"


def _pairs():
    for b in load_experiment()["books"]:
        db = ROOT / b["ledger"]
        yield b["id"], db, STATE_DIR / (db.stem + ".sql")


def dump() -> list[str]:
    STATE_DIR.mkdir(exist_ok=True)
    changed = []
    for bid, db, sql in _pairs():
        if not db.exists():
            continue
        con = sqlite3.connect(db)
        text = "\n".join(con.iterdump()) + "\n"
        con.close()
        if not sql.exists() or sql.read_text() != text:
            sql.write_text(text)
            changed.append(sql.name)
    hb = DATA_DIR / "heartbeat.json"
    if hb.exists():
        shutil.copy2(hb, STATE_DIR / "heartbeat.json")
    log = LOG_DIR / "cycle.log"
    if log.exists():
        (STATE_DIR / "cycle_log_tail.txt").write_text("\n".join(log.read_text(errors="replace").splitlines()[-300:]) + "\n")
    return changed


def restore(force: bool = False) -> list[str]:
    """Rebuild SQLite ledgers from the dumps (only those that changed since the last restore)."""
    DATA_DIR.mkdir(exist_ok=True)
    seen = json.loads(MARKER.read_text()) if MARKER.exists() else {}
    done = []
    for bid, db, sql in _pairs():
        if not sql.exists():
            continue
        text = sql.read_text()
        sha = hashlib.sha256(text.encode()).hexdigest()
        if not force and seen.get(bid) == sha and db.exists():
            continue
        tmp = db.with_suffix(".restoring")
        tmp.unlink(missing_ok=True)
        con = sqlite3.connect(tmp)
        con.executescript(text)
        con.close()
        os.replace(tmp, db)
        seen[bid] = sha
        done.append(bid)
    hb = STATE_DIR / "heartbeat.json"
    if hb.exists():
        shutil.copy2(hb, DATA_DIR / "heartbeat.json")
    MARKER.write_text(json.dumps(seen))
    return done


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "dump":
        print("dumped:", dump())
    elif cmd == "restore":
        print("restored:", restore(force="--force" in sys.argv))
    else:
        sys.exit("usage: python -m papertrader.statesync dump|restore [--force]")
