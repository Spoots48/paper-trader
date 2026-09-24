"""Background work for the Mac app while it's open (display only; never writes to the ledgers).

  * every 15 s: pull the latest cloud state from GitHub, and fetch current prices for held positions
  * every 60 s: refresh the cloud run status (never blocks the UI)
  * watchdog: if GitHub skipped a key scheduled run (after the open / after the close), start it now
"""
from __future__ import annotations

import datetime as dt
import threading
import time

from .nyse_calendar import ET, is_session, iso, now_utc, session_close, session_open

QUOTES: dict[str, tuple[float, str]] = {}
_lock = threading.Lock()


def quotes() -> dict[str, tuple[float, str]]:
    with _lock:
        return dict(QUOTES)


def held_tickers() -> list[str]:
    import sqlite3
    from .config import ROOT, load_experiment
    out = {"SPY"}
    for b in load_experiment()["books"]:
        p = ROOT / b["ledger"]
        if p.exists():
            con = sqlite3.connect(p)
            try:
                out |= {r[0] for r in con.execute("SELECT ticker FROM positions")}
            finally:
                con.close()
    return sorted(out)


def refresh_quotes() -> None:
    import yfinance as yf
    tickers = held_tickers()
    df = yf.download(tickers, period="1d", interval="1m", prepost=False, progress=False, group_by="ticker", auto_adjust=False)
    if df is None or df.empty:
        return
    got = {}
    for t in tickers:
        if t not in df.columns.get_level_values(0):
            continue
        s = df[t]["Close"].dropna()
        if len(s):
            got[t] = (float(s.iloc[-1]), s.index[-1].astimezone(ET).isoformat())
    with _lock:
        QUOTES.update(got)


def _last_cloud_start(st: dict) -> dt.datetime | None:
    starts = [dt.datetime.fromisoformat(r["createdAt"].replace("Z", "+00:00")) for r in st.get("runs") or [] if r.get("createdAt")]
    return max(starts) if starts else None


def watchdog_check(st: dict, now: dt.datetime) -> str | None:
    """Return a reason to start a cloud run now, or None. Key windows: after the open, after the close."""
    if st.get("enabled") is False or st.get("running") or not st.get("runs"):
        return None
    d = now.astimezone(ET).date()
    if not is_session(d):
        return None
    last = _last_cloud_start(st)
    windows = [
        (session_open(d) + dt.timedelta(minutes=12), session_open(d) + dt.timedelta(hours=5), "record the open"),
        (session_close(d) + dt.timedelta(minutes=35), session_close(d) + dt.timedelta(hours=7), "close out the day and decide the next open"),
    ]
    for start, end, why in windows:
        if start <= now <= end and (last is None or last < start):
            return why
    if session_open(d) + dt.timedelta(minutes=6) <= now <= session_close(d) + dt.timedelta(minutes=10):
        if last is None or now - last > dt.timedelta(minutes=45):
            return "keep the day-trading book current (no cloud run in 45 min)"
    return None


def start_background() -> None:
    from . import cloud
    state = {"last_dispatch": 0.0}

    def fast_loop():
        while True:
            try:
                cloud.sync()
            except Exception as e:  # keep showing the last good state
                print(f"sync failed: {e}", flush=True)
            try:
                refresh_quotes()
            except Exception as e:
                print(f"quotes failed: {e}", flush=True)
            time.sleep(15)

    def status_loop():
        while True:
            try:
                st = cloud.status(max_age=0)
                why = watchdog_check(st, now_utc())
                if why and time.time() - state["last_dispatch"] > 20 * 60:
                    ok, msg = cloud.trigger()
                    state["last_dispatch"] = time.time()
                    print(f"{iso(now_utc())} watchdog started a cloud run ({why}): {ok} {msg}", flush=True)
            except Exception as e:
                print(f"status failed: {e}", flush=True)
            time.sleep(60)

    threading.Thread(target=fast_loop, daemon=True).start()
    threading.Thread(target=status_loop, daemon=True).start()
