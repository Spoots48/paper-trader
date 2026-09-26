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
FEED: dict = {}
_lock = threading.Lock()


def feed() -> dict:
    with _lock:
        return dict(FEED)


def refresh_feed() -> None:
    """Display-only market feed: crypto spot prices and the live 15-minute Bitcoin Up/Down market."""
    import json as _json
    import requests
    H = {"User-Agent": "Mozilla/5.0 (PaperTradingSim viewer)"}
    out = {"at": iso(now_utc())}
    for sym in ("BTC", "ETH", "SOL"):
        try:
            t = requests.get(f"https://api.exchange.coinbase.com/products/{sym}-USD/ticker", headers=H, timeout=8).json()
            out[sym] = {"price": float(t["price"]), "time": t.get("time")}
        except Exception:
            pass
    try:
        now = int(now_utc().timestamp())
        slug = f"btc-updown-15m-{now // 900 * 900}"
        ev = requests.get("https://gamma-api.polymarket.com/events", params={"slug": slug}, headers=H, timeout=8).json()
        if ev:
            m = ev[0]["markets"][0]
            outs, toks = _json.loads(m["outcomes"]), _json.loads(m["clobTokenIds"])
            b = requests.get("https://clob.polymarket.com/book", params={"token_id": toks[outs.index("Up")]}, headers=H, timeout=8).json()
            asks = sorted(((float(x["price"]), float(x["size"])) for x in b.get("asks", [])))[:6]
            bids = sorted(((float(x["price"]), float(x["size"])) for x in b.get("bids", [])), reverse=True)[:6]
            out["pm"] = {"title": ev[0]["title"], "slug": slug, "ends": m.get("endDate"), "start": m.get("eventStartTime"),
                         "asks": asks, "bids": bids}
    except Exception:
        pass
    with _lock:
        FEED.clear()
        FEED.update(out)


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
                out |= {r[0] for r in con.execute("SELECT ticker FROM positions WHERE sleeve != 'predmarket'")}
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


MONTH_BUDGET_MINUTES = 1700  # GitHub Free: 2,000 private-repo minutes/month; extra app-triggered runs stop well before that


def month_minutes_used() -> float | None:
    """Estimate this month's billed Actions minutes from run durations (each job rounds up to a whole minute)."""
    import json as _json
    from . import cloud
    first = now_utc().strftime("%Y-%m-01")
    r = cloud.gh("run", "list", "--workflow", cloud.deployment().get("workflow", "cycle.yml"), "--created", f">={first}",
                 "--limit", "2000", "--json", "createdAt,updatedAt", timeout=30)
    if r.returncode != 0:
        return None
    runs = _json.loads(r.stdout or "[]")
    import math
    tot = 0
    for x in runs:
        a = dt.datetime.fromisoformat(x["createdAt"].replace("Z", "+00:00"))
        b = dt.datetime.fromisoformat(x["updatedAt"].replace("Z", "+00:00"))
        tot += max(1, math.ceil((b - a).total_seconds() / 60))
    return tot


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
        if last is None or now - last > dt.timedelta(minutes=20):
            return "keep the day-trading book current (no cloud run in 20 min)"
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
            try:
                refresh_feed()
            except Exception as e:
                print(f"feed failed: {e}", flush=True)
            time.sleep(15)

    budget = {"used": None, "checked": 0.0}

    def status_loop():
        while True:
            try:
                st = cloud.status(max_age=0)
                why = watchdog_check(st, now_utc())
                # while the app is open, keep results fresh at any hour (within the monthly free-minutes budget)
                if not why and not st.get("running") and st.get("enabled") is not False:
                    if time.time() - budget["checked"] > 1800:
                        budget["used"], budget["checked"] = month_minutes_used(), time.time()
                    last = _last_cloud_start(st)
                    if last and now_utc() - last > dt.timedelta(minutes=20) and (budget["used"] or 0) < MONTH_BUDGET_MINUTES:
                        why = "app is open and the last update is over 20 minutes old"
                if why and time.time() - state["last_dispatch"] > 15 * 60:
                    ok, msg = cloud.trigger()
                    state["last_dispatch"] = time.time()
                    print(f"{iso(now_utc())} watchdog started a cloud run ({why}): {ok} {msg}", flush=True)
            except Exception as e:
                print(f"status failed: {e}", flush=True)
            time.sleep(60)

    threading.Thread(target=fast_loop, daemon=True).start()
    threading.Thread(target=status_loop, daemon=True).start()
