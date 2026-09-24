"""Live engine for the day-trading book (book_type = intraday).

Each cloud run advances today's session through every *completed* 1-minute bar it hasn't processed yet,
strictly in time order, using papertrader.intraday. A trade is priced at the bar where it happened and
only uses earlier bars. If a run is late, the bars are processed afterwards in the same causal way,
and each decision records how long after its bar it was processed.
"""
from __future__ import annotations

import datetime as dt
import json
import math

import pandas as pd

from .broker import Fill, Order, Portfolio, Position
from .config import load_universe
from .intraday import DayState, process_bar, select_candidates
from .ledger import Ledger
from .marketdata import MarketData
from .news import NewsService
from .nyse_calendar import (ET, add_sessions, iso, is_session, last_completed_session, next_session, prev_session,
                            session_close, session_open, sessions_between)
from .strategy import Decision

FIRST_BARS_SCHEMA = """CREATE TABLE IF NOT EXISTS first_bars (
  ticker TEXT NOT NULL, session TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL, volume REAL,
  retrieved_at TEXT NOT NULL, PRIMARY KEY (ticker, session))"""


class DayEngine:
    def __init__(self, ledger: Ledger, md: MarketData, cfg: dict, exp: dict, now: dt.datetime):
        self.L, self.md, self.cfg, self.now = ledger, md, cfg, now
        e = ledger.experiment()
        self.start = dt.date.fromisoformat(e["start_date"])
        self.end = dt.date.fromisoformat(e["end_date"])
        self.cash0 = e["starting_cash"]
        u = load_universe()
        self.stocks = [m["ticker"] for m in u["members"]]
        self.names = {m["ticker"]: m["name"] for m in u["members"]}
        self.exec_min = cfg.get("execution", {}).get("bar_minutes", 1)
        self.log: list[str] = []
        md.db.execute(FIRST_BARS_SCHEMA)

    def note(self, m: str) -> None:
        self.log.append(m)

    # ------------------------------------------------------------------ main
    def step(self) -> str:
        if self.L.get_state("experiment_finished"):
            return "experiment finished; nothing to do"
        today = self.now.astimezone(ET).date()
        last = min(today, self.end)
        for S in sessions_between(self.start, last):
            st_json = self.L.get_state(f"dt:{S}")
            if st_json and st_json.get("closed") and self.L.db.execute("SELECT 1 FROM snapshots WHERE session=?", (S.isoformat(),)).fetchone():
                continue
            if self.now < session_open(S) + dt.timedelta(minutes=6):
                break  # the opening range isn't complete yet
            st = DayState.from_json(st_json) if st_json else self.select(S)
            if st is None:
                self.note(f"{S}: waiting for opening-range data")
                break
            self.advance(S, st)
            if not st.closed:
                break  # session still in progress (or data not complete yet)
        return "; ".join(self.log) or "no action needed"

    # ------------------------------------------------------------------ 09:35 selection
    def _ensure_first_bars(self, S: dt.date) -> None:
        need = [prev_session(S)]
        for _ in range(self.cfg["selection"]["relative_volume_lookback_sessions"] - 1):
            need.append(prev_session(need[-1]))
        have = {r[0] for r in self.md.db.execute("SELECT DISTINCT session FROM first_bars WHERE session >= ?", (min(need).isoformat(),))}
        period = "1mo" if any(d.isoformat() not in have for d in need) else "5d"
        tickers = self.stocks
        rows = []
        for i in range(0, len(tickers), 100):
            df = self.md._download(tickers[i:i + 100], period=period, interval="5m", prepost=False)
            if df is None:
                continue
            for t in tickers[i:i + 100]:
                if t not in df.columns.get_level_values(0):
                    continue
                sub = df[t].dropna(subset=["Close"])
                for ts, r in sub.iterrows():
                    et = ts.astimezone(ET)
                    if et.strftime("%H:%M") == "09:30" and et + dt.timedelta(minutes=5) <= self.now.astimezone(ET):
                        rows.append((t, et.date().isoformat(), float(r["Open"]), float(r["High"]), float(r["Low"]),
                                     float(r["Close"]), float(r["Volume"]), iso(self.now)))
        self.md.db.execute("BEGIN")
        self.md.db.executemany("INSERT OR REPLACE INTO first_bars VALUES (?,?,?,?,?,?,?,?)", rows)
        self.md.db.execute("COMMIT")

    def _daily_metrics(self, S: dt.date) -> dict[str, dict]:
        n = self.cfg["universe"]["atr_days"]
        q = ("SELECT ticker, session, high, low, close, volume FROM daily_bars WHERE final IN (1,2) AND session < ? AND session >= ?")
        df = pd.read_sql_query(q, self.md.db, params=(S.isoformat(), (S - dt.timedelta(days=60)).isoformat()))
        out = {}
        for t, g in df.groupby("ticker"):
            g = g.sort_values("session").tail(30)
            if len(g) < n + 1:
                continue
            pc = g["close"].shift(1)
            tr = pd.concat([g["high"] - g["low"], (g["high"] - pc).abs(), (g["low"] - pc).abs()], axis=1).max(axis=1)
            out[t] = {"atr": float(tr.tail(n).mean()), "avg_vol": float(g["volume"].tail(self.cfg["universe"]["avg_volume_days"]).mean()),
                      "adv_usd": float((g["close"] * g["volume"]).tail(20).mean()), "prev_close": float(g["close"].iloc[-1])}
        return out

    def select(self, S: dt.date) -> DayState | None:
        D = prev_session(S)
        flag = f"refreshed:{D.isoformat()}:universe"
        if not self.md.kv_get(flag):
            st = self.md.update_daily(self.stocks + ["SPY", "^VIX"], self.now)
            if len(st["failed"]) > 50:
                self.L.issue("ERROR", "marketdata", f"daily refresh failed for {len(st['failed'])} tickers; day-trade selection postponed")
                return None
            self.md.kv_set(flag, iso(self.now))
        self._ensure_first_bars(S)
        rows = self.md.db.execute("SELECT * FROM first_bars WHERE session >= ?", ((S - dt.timedelta(days=40)).isoformat(),)).fetchall()
        first_today, hist = {}, {}
        for r in rows:
            if r["session"] == S.isoformat():
                first_today[r["ticker"]] = (r["open"], r["high"], r["low"], r["close"], r["volume"])
            elif r["session"] < S.isoformat():
                hist.setdefault(r["ticker"], []).append((r["session"], r["volume"]))
        if len(first_today) < 0.6 * len(self.stocks):
            return None  # today's opening bars not available yet (or data outage): try again next run
        hist = {t: [v for _, v in sorted(x)][-self.cfg["selection"]["relative_volume_lookback_sessions"]:] for t, x in hist.items()}
        cands, skipped = select_candidates(first_today, hist, self._daily_metrics(S), self.cfg)
        risk = self.L.get_state("risk", {"peak": self.cash0})
        halted = bool(risk.get("halt_until") and S.isoformat() <= risk["halt_until"])
        paused = bool(risk.get("pause_until") and S.isoformat() <= risk["pause_until"])
        cash = self.L.get_state("cash", self.cash0)
        st = DayState(session=S.isoformat(), cash_at_open=cash, cash=cash, candidates=[c.__dict__ for c in cands],
                      pending=[] if (halted or paused) else [c.ticker for c in cands])
        asof = (session_open(S) + dt.timedelta(minutes=5)).isoformat()
        with self.L.tx():
            self._init_benchmark(S)
            for c in cands:
                self.L.insert_decision(f"{S}:dt:cand:{c.ticker}", asof, S.isoformat(), Decision(
                    c.ticker, "daytrade", "INFO", "CANDIDATE",
                    f"stock in play: first 5-min volume {c.rvol:.1f}x normal (rank {c.rank}), first bar up "
                    f"{c.first_open:.2f}→{c.first_close:.2f}; buy stop at {c.trigger:.2f}", c.__dict__), iso(self.now))
                if not (halted or paused):
                    self.L.insert_order(Order(key=f"{S}:daytrade:{c.ticker}:BUY:ORB", ticker=c.ticker, side="BUY", order_type="STOP_ENTRY",
                                              session=S.isoformat(), created_at=asof, sleeve="daytrade", reason_code="ORB_BREAKOUT",
                                              reason=f"buy stop {c.trigger:.2f} (first 5-min high + $0.01)", notional=None,
                                              meta={"processed_at": iso(self.now), "trigger": c.trigger}))
            for t, why in skipped[:10]:
                self.L.insert_decision(f"{S}:dt:skip:{t}", asof, S.isoformat(), Decision(t, "daytrade", "SKIP", "CRITERIA", why), iso(self.now))
            gate = " (drawdown halt: no trading)" if halted else " (drawdown pause: no new trades)" if paused else ""
            self.L.insert_decision(f"{S}:dt:selected", asof, S.isoformat(), Decision(
                "*", "daytrade", "INFO", "DAY_SELECTION",
                f"{len(cands)} stocks in play selected at 09:35 ET from {len(first_today)} with opening data; buying power ${cash:.2f}{gate}",
                {"candidates": [c.ticker for c in cands], "processed_at": iso(self.now)}), iso(self.now))
            self.L.set_state(f"dt:{S}", st.to_json())
        self.note(f"{S}: {len(cands)} candidates ({', '.join(c.ticker for c in cands[:8])}{'…' if len(cands) > 8 else ''})")
        return st

    def _init_benchmark(self, S: dt.date) -> None:
        if self.L.get_state("benchmark") or S != self.start:
            return
        self.md.update_daily(["SPY"], self.now)
        b = self.md.bar("SPY", S)
        o = b.get("open") if b else None
        if not o:  # fall back to the first 1-minute bar's open
            spy = self._bars(S, ["SPY"])
            o = spy[min(spy)]["SPY"][0] if spy else None
        if not o:
            return
        px = o * (1 + (2 + 5) / 1e4)
        self.L.set_state("benchmark", {"ticker": "SPY", "qty": self.cash0 / px, "entry_price": px, "entry_session": S.isoformat(),
                                       "div_cash": 0.0, "note": "SPY bought at this book's first official open"})

    # ------------------------------------------------------------------ bar-by-bar
    def _bars(self, S: dt.date, tickers: list[str]) -> dict[str, dict[str, tuple]]:
        """{bar_time_iso: {ticker: (o,h,l,c)}} for completed execution bars of session S."""
        if not tickers:
            return {}
        df = self.md._download(sorted(set(tickers)), start=S.isoformat(), end=(S + dt.timedelta(days=1)).isoformat(),
                               interval=f"{self.exec_min}m", prepost=False)
        out: dict[str, dict[str, tuple]] = {}
        if df is None:
            return out
        now_et = self.now.astimezone(ET)
        for t in set(tickers):
            if t not in df.columns.get_level_values(0):
                continue
            for ts, r in df[t].dropna(subset=["Open", "Low"]).iterrows():
                et = ts.astimezone(ET)
                if et.date() != S or et + dt.timedelta(minutes=self.exec_min) > now_et:
                    continue
                out.setdefault(et.isoformat(), {})[t] = (float(r["Open"]), float(r["High"]), float(r["Low"]), float(r["Close"]))
        return out

    def advance(self, S: dt.date, st: DayState) -> None:
        if not self.L.get_state("benchmark"):
            with self.L.tx():
                self._init_benchmark(S)
        tick = [c["ticker"] for c in st.candidates]
        if not tick:
            if self.now >= session_close(S) + dt.timedelta(minutes=5):
                st.closed = True
                with self.L.tx():
                    self.L.set_state(f"dt:{S}", st.to_json())
                    self._snapshot(S, st)
            return
        bars = self._bars(S, tick)
        close_t = session_close(S)
        last_start = (close_t - dt.timedelta(minutes=self.exec_min)).isoformat()
        entry_cut = (close_t - dt.timedelta(minutes=self.cfg["entry"]["last_entry_bar_minutes_before_close"])).isoformat()
        start_t = (session_open(S) + dt.timedelta(minutes=5)).isoformat()
        news = NewsService(self.L, self.names, {"momentum": {"news_lookback_hours": self.cfg["news"]["lookback_hours"]}}, self.now)
        cands = {c["ticker"]: c for c in st.candidates}

        def news_ok(t: str, bar_time: str):
            news.decision_time = dt.datetime.fromisoformat(bar_time).astimezone(dt.timezone.utc)
            v = news.check(t, "momentum", {})
            return v.ok, v.reason

        events_all = []
        times = sorted(bt for bt in bars if bt >= start_t and (st.processed_through is None or bt > st.processed_through))
        data_complete = bool(times) and times[-1] >= last_start
        for bt in times:
            ev = process_bar(st, bt, bars[bt], self.cfg, is_last_bar=(bt >= last_start), entries_allowed=bt <= entry_cut,
                             news_ok=news_ok)
            events_all += [(bt, e) for e in ev]
            if st.closed:
                break
        # the session is over but the final bar never arrived (data gap): flatten at the last known prices
        if not st.closed and self.now >= close_t + dt.timedelta(minutes=30) and not data_complete:
            lastpx = {}
            for bt in sorted(bars):
                for t, b in bars[bt].items():
                    lastpx[t] = b
            ev = process_bar(st, last_start, {t: lastpx[t] for t in st.positions if t in lastpx}, self.cfg,
                             is_last_bar=True, entries_allowed=False)
            events_all += [(last_start, e) for e in ev]
            self.L.issue("WARN", "marketdata", f"{S}: final 1-minute bars missing; positions closed at last available prices")
        lag_note = ""
        if times:
            lag = (self.now - dt.datetime.fromisoformat(times[-1])).total_seconds() / 60
            if lag > 15:
                lag_note = f" (processed {int(lag)} min after the bar: cloud run was late)"
        with self.L.tx():
            for bt, e in events_all:
                if e.kind == "SKIP":
                    self.L.insert_decision(f"{S}:dt:{e.reason_code}:{e.ticker}", bt, S.isoformat(),
                                           Decision(e.ticker, "daytrade", "SKIP", e.reason_code, e.reason), iso(self.now))
                    if e.reason_code in ("NO_SLOT", "NO_CASH", "NEWS_VETO"):
                        self.L.set_order_status(f"{S}:daytrade:{e.ticker}:BUY:ORB", "CANCELLED", e.reason)
                    continue
                key = f"{S}:daytrade:{e.ticker}:BUY:ORB" if e.kind == "BUY" else f"{S}:daytrade:{e.ticker}:SELL:{e.reason_code}"
                f = Fill(key, e.ticker, e.kind, e.qty, e.ref_price, e.fill_price, e.cost_bps, e.qty * abs(e.fill_price - e.ref_price),
                         S.isoformat(), bt, f"yahoo_{self.exec_min}m_bar", "daytrade", e.reason_code, e.reason + lag_note, e.realized_pnl)
                if e.kind == "SELL":
                    self.L.ensure_order_row(key, f, bt)
                if self.L.record_fill(f):
                    self.L.set_order_status(key, "FILLED", f"{e.kind} {e.qty:.6f} {e.ticker} @ {e.fill_price:.4f}")
                    self.L.insert_decision(f"{S}:dt:{e.kind}:{e.ticker}:{e.reason_code}", bt, S.isoformat(),
                                           Decision(e.ticker, "daytrade", e.kind, e.reason_code, e.reason + lag_note,
                                                    {k: cands[e.ticker].get(k) for k in ("rvol", "rank", "trigger", "atr", "first_high")}),
                                           iso(self.now))
                    self.note(f"{e.kind} {e.ticker} @ {e.fill_price:.2f} ({e.reason_code})")
            if st.closed:
                for o in self.L.open_orders():
                    if o.session == S.isoformat():
                        self.L.set_order_status(o.key, "EXPIRED", "no breakout before the entry cutoff")
            self.L.set_state("cash", st.cash)
            self._save_positions(st, S)
            self.L.set_state(f"dt:{S}", st.to_json())
            self.L.set_state("live_marks", {"as_of": iso(self.now), "marks": {
                t: (bars[max(bars)][t][3], max(bars)) for t in st.positions if bars and t in bars[max(bars)]}})
            if st.closed:
                self._snapshot(S, st)

    def _save_positions(self, st: DayState, S: dt.date) -> None:
        self.L.db.execute("DELETE FROM positions")
        for t, p in st.positions.items():
            self.L.db.execute(
                "INSERT INTO positions (ticker, qty, avg_cost, sleeve, entry_session, entry_price, initial_stop, trail_pct, high_water, "
                "max_hold_until, stop_checked_through, meta) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (t, p["qty"], p["entry_price"], "daytrade", S.isoformat(), p["entry_price"], p["stop"], None, p["entry_ref"],
                 S.isoformat(), st.processed_through, json.dumps({"entry_time": p["entry_time"]})))

    def _snapshot(self, S: dt.date, st: DayState) -> None:
        equity = st.cash
        bench = self.L.get_state("benchmark")
        spy_bh = None
        if bench:
            self.md.update_daily(["SPY"], self.now)
            b = self.md.bar("SPY", S)
            if b and b.get("close"):
                spy_bh = bench["qty"] * b["close"] + bench.get("div_cash", 0.0)
            else:
                spy = self._bars(S, ["SPY"])
                if spy:
                    spy_bh = bench["qty"] * spy[max(spy)]["SPY"][3] + bench.get("div_cash", 0.0)
        risk = self.L.get_state("risk", {"peak": self.cash0})
        risk["peak"] = max(risk.get("peak", self.cash0), equity)
        dd = 1 - equity / risk["peak"]
        R = self.cfg["risk"]
        if dd >= R["drawdown_halt"] and not risk.get("halt_until"):
            risk["halt_until"] = self.end.isoformat()
            self.L.issue("CRITICAL", "risk", f"day-trading drawdown {dd:.1%} ≥ {R['drawdown_halt']:.0%}: book halted for the rest of the experiment")
        elif dd >= R["drawdown_pause"]:
            risk["pause_until"] = add_sessions(S, R["pause_sessions"]).isoformat()
            self.L.issue("WARN", "risk", f"day-trading drawdown {dd:.1%}: no new trades until after {risk['pause_until']}")
        risk["drawdown"] = dd
        self.L.set_state("risk", risk)
        n_trades = self.L.db.execute("SELECT COUNT(*) FROM fills WHERE session=? AND side='BUY'", (S.isoformat(),)).fetchone()[0]
        self.L.insert_snapshot({
            "session": S.isoformat(), "created_at": iso(self.now), "run_id": self.L.run_id, "equity": equity, "cash": st.cash,
            "positions_value": 0.0, "spy_bh_equity": spy_bh, "cash_bh_equity": self.cash0, "peak": risk["peak"], "drawdown": dd,
            "regime": f"{n_trades} trades", "risk_state": json.dumps(risk), "marks": json.dumps({"marks": {}, "flags": {}}),
            "holdings": json.dumps({})})
        self.note(f"closed {S}: equity ${equity:.2f} ({n_trades} trades)")
