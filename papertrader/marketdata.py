"""Market data for the live engine: Yahoo Finance (free, no key) with validation and a local cache.

Data-quality tiers stored per daily bar:
  final=1  official daily bar (finite close, retrieved after the session close)
  final=2  derived from 5-minute bars because the official close was still
           missing at decision time (flagged everywhere it is used)
  final=0  partial / in-progress bar (never used for signals or marks)
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sqlite3
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

from .config import HISTORY_DIR, MARKET_CACHE_PATH
from .nyse_calendar import ET, iso, now_utc, session_close, session_open

SCHEMA = """
CREATE TABLE IF NOT EXISTS daily_bars (
  ticker TEXT NOT NULL, session TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL, volume REAL,
  dividends REAL DEFAULT 0, splits REAL DEFAULT 0, final INTEGER NOT NULL, source TEXT NOT NULL,
  retrieved_at TEXT NOT NULL, PRIMARY KEY (ticker, session)
);
CREATE TABLE IF NOT EXISTS earnings_calendar (
  ticker TEXT NOT NULL, announce_date TEXT NOT NULL, time_code TEXT, announce_ts TEXT NOT NULL,
  source TEXT NOT NULL, eps_forecast TEXT, retrieved_at TEXT NOT NULL, PRIMARY KEY (ticker, announce_date, source)
);
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS fetch_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, what TEXT NOT NULL, ok INTEGER NOT NULL, detail TEXT
);
"""


class DataUnavailable(Exception):
    pass


def _fin(x) -> bool:
    try:
        return x is not None and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


class MarketData:
    def __init__(self, path: Path = MARKET_CACHE_PATH, issue_cb=None):
        self.db = sqlite3.connect(str(path), timeout=30, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.executescript(SCHEMA)
        self.issue = issue_cb or (lambda *a, **k: None)
        self.earnings_failed: list[str] = []

    def kv_get(self, key: str):
        r = self.db.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return r["value"] if r else None

    def kv_set(self, key: str, value: str) -> None:
        self.db.execute("INSERT OR REPLACE INTO kv (key, value) VALUES (?,?)", (key, value))

    def _log(self, what: str, ok: bool, detail: str = "") -> None:
        self.db.execute("INSERT INTO fetch_log (ts, what, ok, detail) VALUES (?,?,?,?)", (iso(now_utc()), what, int(ok), detail[:500]))

    # ---------------------------------------------------------------- seeding & daily updates
    def seed_from_history(self, tickers: list[str] | None = None) -> int:
        """Seed the cache from the research download if present, otherwise download ~15 months from Yahoo."""
        if not (HISTORY_DIR / "download_meta.json").exists():
            st = self.update_daily(tickers or [], now_utc(), period="15mo")
            return st["final"]
        meta = json.loads((HISTORY_DIR / "download_meta.json").read_text())
        retrieved = meta.get("prices_done_at", meta.get("started_at"))
        f = {n: pd.read_pickle(HISTORY_DIR / f"daily_{n}.pkl") for n in ("open", "high", "low", "close", "volume", "dividends", "splits")}
        cutoff = f["close"].index[-320] if len(f["close"]) > 320 else f["close"].index[0]
        rows = []
        for t in f["close"].columns:
            c = f["close"][t].loc[cutoff:]
            for ts, close in c.items():
                if not _fin(close):
                    continue
                rows.append((t, ts.date().isoformat(), float(f["open"].at[ts, t]), float(f["high"].at[ts, t]),
                             float(f["low"].at[ts, t]), float(close), float(f["volume"].at[ts, t] or 0),
                             float(f["dividends"].at[ts, t] or 0), float(f["splits"].at[ts, t] or 0), 1,
                             "yahoo_daily_seed", retrieved))
        self.db.execute("BEGIN")
        self.db.executemany("INSERT OR IGNORE INTO daily_bars VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        self.db.execute("COMMIT")
        return len(rows)

    def _download(self, tickers: list[str], **kw) -> pd.DataFrame | None:
        last = None
        for attempt in range(3):
            try:
                df = yf.download(tickers, group_by="ticker", progress=False, threads=True, auto_adjust=False, **kw)
                if df is not None and not df.empty:
                    return df
                last = "empty response"
            except Exception as e:  # retried with backoff; persistent failures are logged by the caller
                last = f"{type(e).__name__}: {e}"
            time.sleep(3 * (attempt + 1))
        self._log(f"download {kw.get('interval', '1d')} x{len(tickers)}", False, str(last))
        return None

    def update_daily(self, tickers: list[str], now: dt.datetime, period: str = "10d") -> dict:
        """Refresh recent daily bars. Official bars (final=1) are never downgraded."""
        stats = {"requested": len(tickers), "final": 0, "partial": 0, "failed": []}
        retrieved = iso(now)
        today = now.astimezone(ET).date()
        for i in range(0, len(tickers), 100):
            batch = tickers[i:i + 100]
            df = self._download(batch, period=period, interval="1d", actions=True)
            if df is None:
                stats["failed"] += batch
                continue
            rows = []
            for t in batch:
                if t not in df.columns.get_level_values(0):
                    stats["failed"].append(t)
                    continue
                sub = df[t]
                for ts, r in sub.iterrows():
                    d = ts.date()
                    o, h, l, c, v = (r.get(k) for k in ("Open", "High", "Low", "Close", "Volume"))
                    if not _fin(o) and not _fin(c):
                        continue
                    done = d < today or now >= session_close(d) + dt.timedelta(minutes=20)
                    fin = 1 if (done and _fin(c) and _fin(o) and _fin(h) and _fin(l)) else 0
                    rows.append((t, d.isoformat(), *(float(x) if _fin(x) else None for x in (o, h, l, c)),
                                 float(v) if _fin(v) else None, float(r.get("Dividends") or 0),
                                 float(r.get("Stock Splits") or 0), fin, "yahoo_daily", retrieved))
                    stats["final" if fin else "partial"] += 1
            self.db.execute("BEGIN")
            for row in rows:
                # upsert, but never replace an official bar with a partial/derived one
                self.db.execute(
                    "INSERT INTO daily_bars VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(ticker, session) DO UPDATE SET "
                    "open=excluded.open, high=excluded.high, low=excluded.low, close=excluded.close, volume=excluded.volume, "
                    "dividends=excluded.dividends, splits=excluded.splits, final=excluded.final, source=excluded.source, "
                    "retrieved_at=excluded.retrieved_at WHERE daily_bars.final != 1 AND (excluded.final = 1 OR daily_bars.final = 0)",
                    row)
            self.db.execute("COMMIT")
            time.sleep(1)
        self._log(f"update_daily x{len(tickers)}", not stats["failed"], json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in stats.items()}))
        return stats

    def derive_from_intraday(self, tickers: list[str], session: dt.date, now: dt.datetime) -> list[str]:
        """Build a daily bar from 5-minute bars when the official close is still missing (flagged final=2)."""
        need = [t for t in tickers if self.bar_quality(t, session) != 1]
        if not need or now < session_close(session) + dt.timedelta(minutes=5):
            return []
        derived = []
        for i in range(0, len(need), 100):
            batch = need[i:i + 100]
            df = self._download(batch, period="5d", interval="5m", prepost=False)
            if df is None:
                continue
            for t in batch:
                if t not in df.columns.get_level_values(0):
                    continue
                sub = df[t].dropna(subset=["Close"])
                sub = sub[[ts.astimezone(ET).date() == session for ts in sub.index]]
                if len(sub) < 60:  # most of a full session (78 bars) is required
                    continue
                part = self.db.execute("SELECT open, high, low, volume FROM daily_bars WHERE ticker=? AND session=?",
                                       (t, session.isoformat())).fetchone()
                o = part["open"] if part and _fin(part["open"]) else float(sub["Open"].iloc[0])
                h = max(float(sub["High"].max()), part["high"] if part and _fin(part["high"]) else 0)
                l = min(float(sub["Low"].min()), part["low"] if part and _fin(part["low"]) else 1e18)
                v = max(float(sub["Volume"].sum()), part["volume"] if part and _fin(part["volume"]) else 0)
                c = float(sub["Close"].iloc[-1])
                self.db.execute(
                    "INSERT INTO daily_bars VALUES (?,?,?,?,?,?,?,0,0,2,'yahoo_5m_derived',?) ON CONFLICT(ticker, session) "
                    "DO UPDATE SET open=excluded.open, high=excluded.high, low=excluded.low, close=excluded.close, "
                    "volume=excluded.volume, final=2, source=excluded.source, retrieved_at=excluded.retrieved_at "
                    "WHERE daily_bars.final != 1", (t, session.isoformat(), o, h, l, c, v, iso(now)))
                derived.append(t)
        if derived:
            self.issue("INFO", "marketdata", f"official close missing for {session}; derived daily bars from 5m data for {len(derived)} tickers")
        return derived

    # ---------------------------------------------------------------- reads
    def bar(self, ticker: str, session: dt.date) -> dict | None:
        r = self.db.execute("SELECT * FROM daily_bars WHERE ticker=? AND session=?", (ticker, session.isoformat())).fetchone()
        return dict(r) if r else None

    def bar_quality(self, ticker: str, session: dt.date) -> int | None:
        r = self.db.execute("SELECT final FROM daily_bars WHERE ticker=? AND session=?", (ticker, session.isoformat())).fetchone()
        return r["final"] if r else None

    def frames(self, tickers: list[str], through: dt.date, n_sessions: int = 330) -> dict[str, pd.DataFrame]:
        q = ("SELECT ticker, session, open, high, low, close, volume, dividends, splits FROM daily_bars "
             "WHERE final IN (1,2) AND session <= ? AND session >= ?")
        start = (through - dt.timedelta(days=int(n_sessions * 1.5))).isoformat()
        df = pd.read_sql_query(q, self.db, params=(through.isoformat(), start))
        df = df[df.ticker.isin(tickers)]
        df["session"] = pd.to_datetime(df["session"])
        out = {}
        for col in ("open", "high", "low", "close", "volume", "dividends", "splits"):
            out[col] = df.pivot(index="session", columns="ticker", values=col).sort_index().reindex(columns=tickers)
        return out

    def intraday(self, tickers: list[str], session: dt.date, now: dt.datetime) -> dict[str, list[tuple]]:
        """Completed 5-minute bars for `session`: {ticker: [(bar_start_et_iso, o, h, l, c), ...]}."""
        if now < session_open(session) + dt.timedelta(minutes=5):
            return {}
        df = self._download(sorted(set(tickers)), period="5d", interval="5m", prepost=False)
        out: dict[str, list[tuple]] = {}
        if df is None:
            return out
        for t in set(tickers):
            if t not in df.columns.get_level_values(0):
                continue
            sub = df[t].dropna(subset=["Open", "Low"])
            bars = []
            for ts, r in sub.iterrows():
                et = ts.astimezone(ET)
                if et.date() != session or et + dt.timedelta(minutes=5) > now.astimezone(ET):
                    continue  # other day, or bar not finished yet
                bars.append((et.isoformat(), float(r["Open"]), float(r["High"]), float(r["Low"]), float(r["Close"])))
            out[t] = bars
        return out

    def session_opens(self, tickers: list[str], session: dt.date, now: dt.datetime) -> dict[str, tuple[float, str]]:
        """Official session open (from the daily bar). Available shortly after 09:30 ET."""
        if now < session_open(session) + dt.timedelta(minutes=2):
            return {}
        df = self._download(sorted(set(tickers)), period="5d", interval="1d")
        out = {}
        if df is None:
            return out
        for t in set(tickers):
            if t not in df.columns.get_level_values(0):
                continue
            sub = df[t]
            for ts, r in sub.iterrows():
                if ts.date() == session and _fin(r.get("Open")) and float(r["Open"]) > 0:
                    out[t] = (float(r["Open"]), "yahoo_daily_open")
        return out

    # ---------------------------------------------------------------- earnings calendar
    def earnings_for_dates(self, dates: list[dt.date], universe: set[str], now: dt.datetime) -> list[dict]:
        import requests
        ua = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/124.0 Safari/537.36", "Accept": "application/json, text/plain, */*"}
        out = []
        self.earnings_failed = []
        for d in dates:
            rows, err = None, None
            for attempt in range(3):
                try:
                    r = requests.get(f"https://api.nasdaq.com/api/calendar/earnings?date={d.isoformat()}", headers=ua, timeout=20)
                    r.raise_for_status()
                    rows = ((r.json().get("data") or {}).get("rows")) or []
                    break
                except Exception as e:  # retried with backoff; a persistent gap blocks momentum entries
                    err = e
                    time.sleep(2 + 3 * attempt)
            if rows is None:
                self._log(f"nasdaq_earnings {d}", False, str(err))
                self.issue("WARN", "earnings", f"Nasdaq earnings calendar unavailable for {d} after 3 attempts: {err}")
                self.earnings_failed.append(d.isoformat())
                continue
            self._log(f"nasdaq_earnings {d}", True, f"{len(rows)} rows")
            for row in rows:
                t = (row.get("symbol") or "").strip().replace(".", "-")
                if t not in universe:
                    continue
                code = row.get("time") or "time-not-supplied"
                hour = {"time-pre-market": "07:00", "time-after-hours": "16:30"}.get(code)
                if hour is None:
                    hour = self._yahoo_hour(t, d)
                if hour is None:
                    self.issue("WARN", "earnings", f"announcement time unknown for {t} on {d}; event ignored", t)
                    continue
                ev = {"ticker": t, "announce_date": d.isoformat(), "time_code": code, "announce_ts": f"{d.isoformat()} {hour}",
                      "source": "nasdaq", "eps_forecast": row.get("epsForecast"), "retrieved_at": iso(now)}
                self.db.execute("INSERT OR REPLACE INTO earnings_calendar VALUES (?,?,?,?,?,?,?)", tuple(ev.values()))
                out.append(ev)
            time.sleep(0.4)
        return out

    def _yahoo_hour(self, ticker: str, d: dt.date) -> str | None:
        try:
            e = yf.Ticker(ticker).get_earnings_dates(limit=8)
            for ts in e.index:
                et = ts.tz_convert("America/New_York")
                if et.date() == d:
                    return et.strftime("%H:%M")
        except Exception as ex:
            self._log(f"yahoo_earnings {ticker}", False, str(ex))
        return None
