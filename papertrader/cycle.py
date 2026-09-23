"""One scheduled cycle: lock -> pause/online checks -> each book's engine -> reports -> heartbeat -> dashboard."""
from __future__ import annotations

import fcntl
import json
import logging
import logging.handlers
import signal
import socket
import traceback

from .config import LOCK_PATH, LOG_DIR, ROOT, ensure_dirs, load_experiment, load_json, sha256_file
from .engine import Engine
from .ledger import Ledger
from .marketdata import MarketData
from .nyse_calendar import iso, now_utc
from .state import HEARTBEAT, PAUSE_FLAG

log = logging.getLogger("papertrader")


def setup_logging() -> None:
    ensure_dirs()
    if log.handlers:
        return
    h = logging.handlers.RotatingFileHandler(LOG_DIR / "cycle.log", maxBytes=2_000_000, backupCount=5)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    log.addHandler(h)
    log.setLevel(logging.INFO)


def online(timeout: float = 5.0) -> bool:
    for host in ("query1.finance.yahoo.com", "api.nasdaq.com", "www.google.com"):
        try:
            with socket.create_connection((host, 443), timeout=timeout):
                return True
        except OSError:
            continue
    return False


def _heartbeat(status: str, trigger: str, detail) -> None:
    HEARTBEAT.write_text(json.dumps({"at": iso(now_utc()), "status": status, "trigger": trigger, "detail": detail}, default=str))


class _Timeout(Exception):
    pass


def run_cycle(trigger: str = "manual", max_seconds: int = 900) -> dict:
    setup_logging()
    if PAUSE_FLAG.exists():
        log.info("paused by user (data/PAUSED exists); skipping")
        _heartbeat("paused", trigger, "paused by user")
        return {"status": "paused"}
    lock = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log.info("another cycle is running; skipping")
        return {"status": "busy"}
    if not online():
        log.info("offline; skipping (will catch up when back online)")
        _heartbeat("offline", trigger, "no internet connection")
        return {"status": "offline"}

    def _alarm(*_):
        raise _Timeout(f"cycle exceeded {max_seconds}s")
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(max_seconds)
    socket.setdefaulttimeout(30)
    results = {}
    try:
        exp = load_experiment()
        md = MarketData()
        if md.db.execute("SELECT COUNT(*) AS n FROM daily_bars").fetchone()["n"] == 0:
            from .config import load_universe
            n = md.seed_from_history([x['ticker'] for x in load_universe()['members']] + ['SPY', '^VIX'])
            log.info(f"seeded market cache with {n} bars")
        now = now_utc()
        ledgers = {}
        for book in exp["books"]:
            L = Ledger(ROOT / book["ledger"])
            ledgers[book["id"]] = L
            e = L.experiment()
            if not e:
                results[book["id"]] = "not frozen (run: python run.py freeze)"
                continue
            cfg = load_json(ROOT / book["strategy"])
            run_id = f"{now.strftime('%Y%m%dT%H%M%SZ')}-{book['id']}"
            L.start_run(run_id, trigger)
            md.issue = L.issue
            try:
                approved = e["strategy_sha256"]
                ch = L.db.execute("SELECT to_sha256 FROM strategy_changes ORDER BY id DESC LIMIT 1").fetchone()
                if ch:
                    approved = ch["to_sha256"]
                ok = sha256_file(ROOT / book["strategy"]) == approved
                if not ok and L.get_state("strategy_integrity_ok", True):
                    L.issue("CRITICAL", "integrity", f"{book['strategy']} differs from the frozen version; new decisions suspended "
                                                     "until the file is restored or the change is logged with run.py log-change")
                L.set_state("strategy_integrity_ok", ok)
                summary = Engine(L, md, cfg, {**exp, "book": book["id"]}, now).step()
                L.finish_run("OK", summary)
                results[book["id"]] = summary
                log.info(f"[{book['id']}] {summary}")
            except Exception as ex:
                tb = traceback.format_exc()
                log.error(f"[{book['id']}] cycle error: {tb}")
                try:
                    L.db.execute("ROLLBACK")
                except Exception:
                    pass
                L.issue("ERROR", "engine", f"{type(ex).__name__}: {ex}")
                L.finish_run("ERROR", error=tb[-4000:])
                results[book["id"]] = f"ERROR {type(ex).__name__}: {ex}"
        primary = ledgers.get(exp["books"][0]["id"])
        if primary is not None and primary.experiment():
            from .reporting import maybe_generate_reports
            try:
                made = maybe_generate_reports(exp, primary, md, now)
                if made:
                    results["reports"] = made
                    log.info(f"reports generated: {made}")
                    if primary.get_state("experiment_finished"):
                        for L in ledgers.values():
                            L.set_state("experiment_finished", iso(now))
            except Exception:
                log.error("report generation failed: " + traceback.format_exc())
                primary.issue("ERROR", "reporting", traceback.format_exc()[-1500:])
        for L in ledgers.values():
            L.close()
        status = "error" if any(str(v).startswith("ERROR") for v in results.values()) else "ok"
        _heartbeat(status, trigger, results)
    except _Timeout as ex:
        log.error(str(ex))
        _heartbeat("error", trigger, str(ex))
        results["error"] = str(ex)
    finally:
        signal.alarm(0)
        try:
            from .webapp import export_static
            export_static()
        except Exception:
            log.error("static dashboard export failed: " + traceback.format_exc())
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()
    return results
