"""Live paper-trading engine. One call = one idempotent cycle; launchd calls it every 15 minutes.

Timing model (all prices used are observed *after* the decision that created an order):
  * Decisions for session T are made once, using daily data through the previous session D.
    Before T's open -> market-on-open (MOO) orders. During T (until 15:30 ET) -> intraday market
    orders filled at the first 5-minute bar that starts after the decision.
  * Stops are standing orders, as at a real broker: they are evaluated against every bar after entry,
    including bars that occurred while the Mac was asleep (processed once it is back online).
  * Everything else (entries, rotations, time exits, regime exits) only happens when the Mac is on
    during a decision window. Missed windows are recorded, never back-filled.
"""
from __future__ import annotations

import datetime as dt
import json
import math

import pandas as pd

from .broker import Broker, Fill, Order, Portfolio
from .config import load_universe
from .ledger import Ledger
from .marketdata import MarketData
from .news import NewsService
from .nyse_calendar import (ET, add_sessions, current_session, iso, last_completed_session, next_session,
                            prev_session, session_close, session_open, sessions_between)
from .strategy import DecisionContext, EarningsBook, EarningsEvent, Indicators, decide, map_reaction, regime_series

VIX = "^VIX"
# If the official daily close is still missing this long after the close, rebuild the bar from 5-minute data.
DERIVE_AFTER = dt.timedelta(minutes=30)
# If no usable bar exists even after the fallback, keep retrying this long before closing with stale marks (flagged).
STALE_AFTER = dt.timedelta(hours=24)


def _ceil5(ts: dt.datetime) -> dt.datetime:
    ts = ts.astimezone(ET).replace(second=0, microsecond=0) + dt.timedelta(minutes=1)
    return ts + dt.timedelta(minutes=(-ts.minute) % 5)


class Engine:
    def __init__(self, ledger: Ledger, md: MarketData, cfg: dict, exp: dict, now: dt.datetime):
        self.L, self.md, self.cfg, self.exp, self.now = ledger, md, cfg, exp, now
        self.broker = Broker(cfg)
        self.start = dt.date.fromisoformat(exp["start_date"])
        self.end = dt.date.fromisoformat(exp["end_date"])
        u = load_universe()
        self.stocks = [m["ticker"] for m in u["members"]]
        self.names = {m["ticker"]: m["name"] for m in u["members"]}
        self.residual = cfg["portfolio"]["residual_etf"]
        self.cash0 = exp["starting_cash"]
        self.log: list[str] = []

    # ------------------------------------------------------------------ helpers
    def note(self, msg: str) -> None:
        self.log.append(msg)

    def last_done(self) -> dt.date:
        s = self.L.get_state("last_closed_session")
        return dt.date.fromisoformat(s) if s else prev_session(self.start)

    def _persist_fills(self, fills: list[Fill], created_at: str) -> None:
        for f in fills:
            if f.order_key.startswith("stop:"):
                self.L.ensure_order_row(f.order_key, f, created_at)
            if self.L.record_fill(f):
                self.L.set_order_status(f.order_key, "FILLED", f"{f.side} {f.qty:.6f} {f.ticker} @ {f.fill_price:.4f}")
                self.note(f"FILL {f.side} {f.ticker} {f.qty:.4f} @ {f.fill_price:.2f} ({f.reason_code})")

    def _adv(self, tickers, D: dt.date) -> dict[str, float]:
        out = {}
        for t in tickers:
            rows = self.md.db.execute("SELECT close*volume AS dv FROM daily_bars WHERE ticker=? AND session<=? AND final IN (1,2) "
                                      "ORDER BY session DESC LIMIT 20", (t, D.isoformat())).fetchall()
            vals = [r["dv"] for r in rows if r["dv"] is not None]
            out[t] = sum(vals) / len(vals) if vals else float("nan")
        return out

    # ------------------------------------------------------------------ main
    def step(self) -> str:
        now = self.now
        if self.L.get_state("experiment_finished"):
            return "experiment finished; nothing to do"
        exp_changed = self.L.get_state("strategy_integrity_ok", True) is False
        pf, checked = self.L.load_portfolio(self.cash0)
        last_done = self.last_done()
        lcs = last_completed_session(now)
        to_close = [s for s in sessions_between(next_session(last_done), min(lcs, self.end)) if s >= self.start]
        if to_close:
            need = sorted(set(pf.positions) | {o.ticker for o in self.L.open_orders()} | {self.residual, VIX})
            self.md.update_daily(need, now)
        for S in to_close:
            if not self.close_session(S, pf, checked):
                self.note(f"waiting for final data for {S}")
                break
            last_done = S
        cur = current_session(now)
        if cur and self.start <= cur <= self.end and last_done == prev_session(cur):
            self.intraday(cur, pf, checked)
        if not exp_changed:
            self.maybe_decide(last_done, lcs)
        else:
            self.note("strategy file integrity check failed: decisions suspended")
        return "; ".join(self.log) or "no action needed"

    # ------------------------------------------------------------------ session close-out
    def close_session(self, S: dt.date, pf: Portfolio, checked: dict) -> bool:
        now = self.now
        Ss = S.isoformat()
        orders = [o for o in self.L.open_orders() if o.session == Ss]
        need = sorted(set(pf.positions) | {o.ticker for o in orders} | {self.residual})
        missing = [t for t in need if self.md.bar_quality(t, S) != 1]
        if missing:
            if now < session_close(S) + DERIVE_AFTER:
                return False  # give the official daily bar a chance to arrive first
            self.md.derive_from_intraday(missing, S, now)
        bars = {t: self.md.bar(t, S) for t in need}
        usable = {t: b for t, b in bars.items() if b and b["final"] in (1, 2) and b["close"]}
        if len(usable) < len(need) and now < session_close(S) + STALE_AFTER:
            return False  # retry on a later cycle rather than lock in a stale snapshot
        for t in need:
            if t not in usable:
                self.L.issue("ERROR", "marketdata", f"no usable daily bar for {S} after fallback; positions carried at last mark", t)
        intr_need = sorted(set(pf.positions) | {o.ticker for o in orders})
        intr = self.md.intraday(intr_need, S, now) if intr_need and (now.date() - S).days <= 6 else {}
        adv = self._adv(need, prev_session(S))
        created = iso(now)
        with self.L.tx():
            self._apply_splits(S, pf, usable)
            prev_qty = {t: p.qty for t, p in pf.positions.items()}
            # 1) the open (if it wasn't processed live)
            if not self.L.get_state(f"open_done:{Ss}"):
                opens = {t: b["open"] for t, b in usable.items() if b["open"]}
                self._init_benchmark(S, opens)
                fills, rej = self.broker.execute_open(pf, Ss, orders, opens, adv, f"{Ss}T09:30:00-04:00 (official open)", "yahoo_daily_open")
                self._persist_fills(fills, created)
                for o, why in rej:
                    self.L.set_order_status(o.key, "REJECTED", why)
                for f in fills:
                    if f.side == "BUY":
                        checked.pop(f.ticker, None)
                self.L.set_state(f"open_done:{Ss}", True)
            # 2) intraday market orders still open for S
            for o in sorted([o for o in self.L.open_orders() if o.session == Ss and o.order_type == "MKT"],
                            key=lambda o: (o.side != "SELL", o.priority)):
                self._fill_mkt(o, pf, intr.get(o.ticker, []), usable.get(o.ticker), adv, created, checked)
            # 3) standing stops for the rest of the session
            for t in list(pf.positions):
                self._stops_for_session(t, S, pf, checked, intr.get(t), usable.get(t), adv.get(t), created)
            # 4) dividends (ex-date S) for shares held at the previous close
            for t, q in prev_qty.items():
                b = usable.get(t)
                if b and (b.get("dividends") or 0) > 0:
                    amt = q * b["dividends"]
                    cur = self.L.db.execute("INSERT OR IGNORE INTO dividends VALUES (?,?,?,?,?,?)",
                                            (t, Ss, b["dividends"], q, amt, created))
                    if cur.rowcount:
                        pf.cash += amt
                        self.L.event("dividend", {"ticker": t, "ex_date": Ss, "amount": amt})
            # 5) high-water marks for trailing stops
            highs = {}
            for t, p in pf.positions.items():
                et = p.meta.get("entry_time")
                if p.entry_session == Ss and et and intr.get(t):
                    hs = [b[2] for b in intr[t] if b[0] >= et]
                    highs[t] = max(hs) if hs else p.entry_price
                elif usable.get(t):
                    highs[t] = usable[t]["high"]
            self.broker.close_session(pf, highs)
            for t in pf.positions:
                checked[t] = session_close(S).isoformat()
            # 6) orders for S that could not be filled expire
            for o in self.L.open_orders():
                if o.session <= Ss:
                    self.L.set_order_status(o.key, "EXPIRED", "not filled during its session (missing price data)")
            # 7) end-of-day snapshot and risk state
            self._snapshot(S, pf, usable, created)
            self.L.save_portfolio(pf, checked)
            self.L.set_state("last_closed_session", Ss)
        self.note(f"closed {Ss}")
        if S >= self.end:
            self.note("experiment end date reached")
        return True

    def _apply_splits(self, S: dt.date, pf: Portfolio, usable: dict) -> None:
        for t, p in pf.positions.items():
            b = usable.get(t)
            r = (b or {}).get("splits") or 0
            if r and r > 0 and r != 1:
                p.qty *= r
                for attr in ("avg_cost", "entry_price", "high_water"):
                    setattr(p, attr, getattr(p, attr) / r)
                if p.initial_stop:
                    p.initial_stop /= r
                self.L.issue("INFO", "corporate_action", f"split {r}:1 on {S}; position adjusted", t)
                self.L.event("split", {"ticker": t, "session": S.isoformat(), "ratio": r})

    def _init_benchmark(self, S: dt.date, opens: dict) -> None:
        if self.L.get_state("benchmark") or S != self.start:
            return
        o = opens.get("SPY")
        if not o:
            return
        c = self.cfg["costs"]
        px = o * (1 + (c["etf_bps"] + c["open_auction_extra_bps"]) / 1e4)
        self.L.set_state("benchmark", {"ticker": "SPY", "qty": self.cash0 / px, "entry_price": px, "entry_session": S.isoformat(),
                                       "div_cash": 0.0, "note": "SPY bought at the first session's official open with the same cost model"})
        self.L.event("benchmark_init", {"qty": self.cash0 / px, "entry_price": px})

    def _fill_mkt(self, o: Order, pf: Portfolio, bars: list, daily: dict | None, adv: dict, created: str, checked: dict) -> bool:
        t0 = _ceil5(dt.datetime.fromisoformat(o.created_at.replace("Z", "+00:00"))).isoformat()
        nxt = [b for b in bars if b[0] >= t0]
        if nxt:
            ref, ptime, src = nxt[0][1], nxt[0][0], "yahoo_5m_bar_open"
        elif daily and daily.get("close") and self.now >= session_close(dt.date.fromisoformat(o.session)):
            ref, ptime, src = daily["close"], f"{o.session}T16:00:00-04:00 (close; 5m bars unavailable)", "yahoo_daily_close_fallback"
        else:
            return False
        marks = {t: ref for t in pf.positions}
        f, why = self.broker.execute_market(pf, o, ref, ptime, src, adv.get(o.ticker), marks)
        if f:
            if f.side == "BUY" and f.ticker in pf.positions:
                pf.positions[f.ticker].meta["entry_time"] = ptime
                checked.pop(f.ticker, None)
            self._persist_fills([f], created)
            return True
        self.L.set_order_status(o.key, "REJECTED", why or "rejected")
        return False

    def _stops_for_session(self, t: str, S: dt.date, pf: Portfolio, checked: dict, bars5: list | None,
                           daily: dict | None, adv: float | None, created: str) -> None:
        p = pf.positions.get(t)
        if p is None or not p.stop_level():
            return
        chk = checked.get(t)
        if chk and chk[:10] != S.isoformat():
            chk = None
        et = p.meta.get("entry_time") if p.entry_session == S.isoformat() else None
        if bars5 and len(bars5) >= 70:
            bars = [b for b in bars5 if (chk is None or b[0] > chk) and (et is None or b[0] >= et)]
            f = self.broker.check_stop(pf, t, bars, S.isoformat(), "yahoo_5m", adv)
        elif daily:
            stop = p.stop_level()
            if chk is None and et is None:
                bar = (f"{S.isoformat()} (daily bar)", daily["open"], daily["high"], daily["low"], daily["close"])
            else:  # the earlier part of the day was already checked on 5m bars without a trigger
                bar = (f"{S.isoformat()} (rest of day, daily bar)", max(daily["high"], stop * 1.0001), daily["high"], daily["low"], daily["close"])
            f = self.broker.check_stop(pf, t, [bar], S.isoformat(), "yahoo_daily_bar", adv)
        else:
            return
        if f:
            self._persist_fills([f], created)
            checked.pop(t, None)

    def _snapshot(self, S: dt.date, pf: Portfolio, usable: dict, created: str) -> None:
        marks, flags = {}, {}
        for t, p in pf.positions.items():
            b = usable.get(t)
            if b:
                marks[t] = b["close"]
                if b["final"] == 2:
                    flags[t] = "derived_from_5m"
            else:
                r = self.md.db.execute("SELECT close FROM daily_bars WHERE ticker=? AND session<? AND final IN (1,2) "
                                       "ORDER BY session DESC LIMIT 1", (t, S.isoformat())).fetchone()
                marks[t] = r["close"] if r else p.entry_price
                flags[t] = "stale_carried_forward"
        pos_val = sum(p.qty * marks[t] for t, p in pf.positions.items())
        equity = pf.cash + pos_val
        bench = self.L.get_state("benchmark")
        spy_bh = None
        if bench and usable.get("SPY"):
            b = usable["SPY"]
            if (b.get("dividends") or 0) > 0 and S.isoformat() > bench["entry_session"]:
                bench["div_cash"] += bench["qty"] * b["dividends"]
                self.L.set_state("benchmark", bench)
            spy_bh = bench["qty"] * b["close"] + bench["div_cash"]
        risk = self.L.get_state("risk", {"peak": self.cash0, "pause_until": None, "halt_until": None})
        risk["peak"] = max(risk["peak"], equity)
        dd = 1 - equity / risk["peak"]
        R = self.cfg["risk"]
        halted = risk.get("halt_until") and S.isoformat() <= risk["halt_until"]
        if not halted and dd >= R["drawdown_halt"]:
            risk["halt_until"] = add_sessions(S, R["halt_sessions"]).isoformat()
            risk["halt_triggered"] = {"session": S.isoformat(), "drawdown": dd}
            self.L.issue("CRITICAL", "risk", f"drawdown {dd:.1%} >= halt threshold; liquidating and halting until {risk['halt_until']}")
        elif dd >= R["drawdown_pause"]:
            pu = add_sessions(S, R["pause_sessions"]).isoformat()
            risk["pause_until"] = max(risk.get("pause_until") or "", pu)
            self.L.issue("WARN", "risk", f"drawdown {dd:.1%} >= pause threshold; no new stock entries until {risk['pause_until']}")
        risk["drawdown"] = dd
        self.L.set_state("risk", risk)
        holdings = {t: {"qty": p.qty, "avg_cost": p.avg_cost, "sleeve": p.sleeve, "stop": p.stop_level(),
                        "entry_session": p.entry_session, "max_hold_until": p.max_hold_until} for t, p in pf.positions.items()}
        self.L.insert_snapshot({
            "session": S.isoformat(), "created_at": created, "run_id": self.L.run_id, "equity": equity, "cash": pf.cash,
            "positions_value": pos_val, "spy_bh_equity": spy_bh, "cash_bh_equity": self.cash0, "peak": risk["peak"],
            "drawdown": dd, "regime": self.L.get_state("last_regime"), "risk_state": json.dumps(risk),
            "marks": json.dumps({"marks": marks, "flags": flags}), "holdings": json.dumps(holdings)})

    # ------------------------------------------------------------------ live session
    def intraday(self, S: dt.date, pf: Portfolio, checked: dict) -> None:
        now = self.now
        Ss = S.isoformat()
        orders = [o for o in self.L.open_orders() if o.session == Ss]
        created = iso(now)
        moo = [o for o in orders if o.order_type == "MOO"]
        opens = {}
        if not self.L.get_state(f"open_done:{Ss}"):
            need = sorted({o.ticker for o in moo} | set(pf.positions) | ({"SPY"} if S == self.start else set()))
            got = self.md.session_opens(need, S, now) if need else {}
            opens = {t: v[0] for t, v in got.items()}
            if need and not all(t in opens for t in need):
                self.note(f"waiting for official opens ({len(opens)}/{len(need)})")
                opens = None
        tick = sorted(set(pf.positions) | {o.ticker for o in orders if o.order_type == "MKT"})
        if opens:
            tick = sorted(set(tick) | {o.ticker for o in moo if o.side == "BUY"})
        intr = self.md.intraday(tick, S, now) if tick else {}
        adv = self._adv(set(tick) | {o.ticker for o in orders}, prev_session(S))
        with self.L.tx():
            if opens is not None and not self.L.get_state(f"open_done:{Ss}"):
                self._init_benchmark(S, opens)
                fills, rej = self.broker.execute_open(pf, Ss, orders, opens, adv, f"{Ss}T09:30:00-04:00 (official open)", "yahoo_daily_open")
                self._persist_fills(fills, created)
                for o, why in rej:
                    self.L.set_order_status(o.key, "REJECTED", why)
                for f in fills:
                    if f.side == "BUY":
                        checked.pop(f.ticker, None)
                self.L.set_state(f"open_done:{Ss}", True)
            if self.L.get_state(f"open_done:{Ss}"):
                for o in sorted([o for o in self.L.open_orders() if o.session == Ss and o.order_type == "MKT"],
                                key=lambda o: (o.side != "SELL", o.priority)):
                    self._fill_mkt(o, pf, intr.get(o.ticker, []), None, adv, created, checked)
                for t in list(pf.positions):
                    bars = intr.get(t) or []
                    p = pf.positions[t]
                    chk = checked.get(t)
                    if chk and chk[:10] != Ss:
                        chk = None
                    et = p.meta.get("entry_time") if p.entry_session == Ss else None
                    new = [b for b in bars if (chk is None or b[0] > chk) and (et is None or b[0] >= et)]
                    if not new:
                        continue
                    f = self.broker.check_stop(pf, t, new, Ss, "yahoo_5m", adv.get(t))
                    if f:
                        self._persist_fills([f], created)
                        checked.pop(t, None)
                    else:
                        checked[t] = new[-1][0]
            live = {t: (intr[t][-1][4], intr[t][-1][0]) for t in intr if intr[t]}
            self.L.set_state("live_marks", {"as_of": created, "marks": live})
            self.L.save_portfolio(pf, checked)

    # ------------------------------------------------------------------ decisions
    def decided(self, T: dt.date) -> bool:
        return self.L.db.execute("SELECT 1 FROM decisions WHERE decision_key=? OR decision_key=?",
                                 (f"decide:{T}", f"missed:{T}")).fetchone() is not None

    def _mark_missed(self, T: dt.date, why: str) -> None:
        from .strategy import Decision
        with self.L.tx():
            self.L.insert_decision(f"missed:{T}", "-", T.isoformat(), Decision("*", "system", "INFO", "MISSED_WINDOW", why), iso(self.now))
        self.note(f"missed decision window for {T}")

    def maybe_decide(self, last_done: dt.date, lcs: dt.date) -> None:
        now = self.now
        T = next_session(lcs)
        # record decision windows that passed while the Mac was off/asleep
        for s in sessions_between(self.start, min(prev_session(T), self.end)):
            if not self.decided(s):
                self._mark_missed(s, "no decision was made for this session (Mac off, asleep, offline, or data unavailable)")
        if T > self.end or T < self.start or self.decided(T):
            return
        if last_done < lcs:
            if current_session(now) == T and now >= session_close(T) - dt.timedelta(minutes=30):
                self._mark_missed(T, f"prior session {lcs} data not final before the decision deadline")
            return
        latest = dt.datetime.combine(T, dt.time.fromisoformat(self.cfg["data"]["mkt_order_latest_et"]), ET)
        if now >= latest:
            self._mark_missed(T, "Mac was not online before the 15:30 ET decision deadline")
            return
        D = lcs
        order_type = "MOO" if now < session_open(T) else "MKT"
        uses_stocks = self.cfg["catalyst"]["enabled"] or self.cfg["momentum"]["enabled"]
        stocks = self.stocks if uses_stocks else []
        universe = stocks + [self.residual, VIX]
        # refresh once per data date; shared across books through the market cache
        flag = f"refreshed:{D.isoformat()}:{'universe' if uses_stocks else 'core'}"
        if not self.md.kv_get(flag):
            st = self.md.update_daily(universe, now)
            if len(st["failed"]) > 50:
                self.L.issue("ERROR", "marketdata", f"universe refresh failed for {len(st['failed'])} tickers; decision postponed")
                return
            self.md.kv_set(flag, iso(now))
        core_missing = [t for t in (self.residual, VIX) if self.md.bar_quality(t, D) not in (1, 2)]
        stock_missing = [t for t in stocks if self.md.bar_quality(t, D) not in (1, 2)]
        if core_missing or stock_missing:
            if now < session_close(D) + DERIVE_AFTER:
                self.note(f"decision for {T} waiting: official data for {D} incomplete ({len(stock_missing)} stocks, core {core_missing})")
                return
            self.md.derive_from_intraday(core_missing + stock_missing, D, now)
            stock_missing = [t for t in stocks if self.md.bar_quality(t, D) not in (1, 2)]
            core_missing = [t for t in (self.residual, VIX) if self.md.bar_quality(t, D) not in (1, 2)]
            if core_missing:
                self.L.issue("ERROR", "marketdata", f"core data {core_missing} missing for {D}; no new entries this session")
        fr = self.md.frames(universe, D)
        # sessions = days SPY traded (VIX can print on market holidays; those rows would break rolling windows)
        spy_days = fr["close"].index[fr["close"]["SPY"].notna()]
        fr = {k: v.loc[spy_days] for k, v in fr.items()}
        if fr["close"].empty or fr["close"].index[-1].date() != D:
            self.L.issue("ERROR", "marketdata", f"cached frames do not end at {D}; decision skipped")
            return
        stocks_cols = [t for t in universe if t != VIX]
        ind = Indicators(*(fr[k][stocks_cols] for k in ("open", "high", "low", "close", "volume")), self.cfg)
        reg = regime_series(fr["close"]["SPY"], ind.sma200["SPY"], fr["close"][VIX], self.cfg)
        regime = reg.iloc[-1] if not core_missing else reg.iloc[-1].rstrip("?") + "?"
        self.L.set_state("last_regime", regime)
        # earnings calendar around D (reaction day) and the momentum blackout horizon
        horizon = add_sessions(T, self.cfg["momentum"]["earnings_blackout_sessions"] + 2)
        days = [prev_session(D) + dt.timedelta(days=i) for i in range((horizon - prev_session(D)).days + 1)]
        cal = self.md.earnings_for_dates(days, set(self.stocks), now) if uses_stocks else []
        sess = sessions_between(D - dt.timedelta(days=40), T + dt.timedelta(days=60))
        events = []
        for e in cal:
            mp = map_reaction(e["announce_ts"], self.cfg["catalyst"]["announce_hour_cutoff"], sess)
            if mp:
                events.append(EarningsEvent(e["ticker"], e["announce_ts"], mp[0], mp[1], True, source=f"nasdaq ({e['time_code']})"))
        book = EarningsBook(events)
        risk_state = self.L.get_state("risk", {"peak": self.cash0})
        risk = {"drawdown": risk_state.get("drawdown", 0.0),
                "halted": bool(risk_state.get("halt_until") and T.isoformat() <= risk_state["halt_until"]),
                "paused": bool(risk_state.get("pause_until") and T.isoformat() <= risk_state["pause_until"])}
        pf, _ = self.L.load_portfolio(self.cash0)
        first = self.L.db.execute("SELECT 1 FROM decisions WHERE decision_key LIKE 'decide:%'").fetchone() is None
        news = NewsService(self.L, self.names, self.cfg, now)
        ctx = DecisionContext(cfg=self.cfg, ind=ind, stocks=stocks, regime=regime, earnings=book, pf=pf, risk=risk,
                              is_rebalance=first or T.isocalendar()[1] != D.isocalendar()[1], created_at=iso(now),
                              order_type=order_type, news_check=news.check, add_sessions=add_sessions,
                              earnings_complete=not (uses_stocks and self.md.earnings_failed))
        orders, decisions = decide(D, T, ctx)
        spy_c, spy_s = float(fr["close"]["SPY"].iloc[-1]), float(ind.sma200["SPY"].iloc[-1])
        vix_c = float(fr["close"][VIX].iloc[-1]) if math.isfinite(fr["close"][VIX].iloc[-1]) else None
        from .strategy import Decision
        summary = Decision("*", "system", "INFO", "DECIDED",
                           f"{len(orders)} orders ({order_type}) for {T}; regime {regime}; SPY {spy_c:.2f} vs 200d {spy_s:.2f}; "
                           f"VIX {vix_c}; {len(book.reacting_on(D))} earnings reactions on {D}; rebalance={ctx.is_rebalance}",
                           {"regime": regime, "spy_close": spy_c, "spy_sma200": spy_s, "vix": vix_c, "order_type": order_type,
                            "data_through": D.isoformat(), "stock_bars_missing": len(stock_missing), "risk": risk,
                            "earnings_events_loaded": len(events),
                            "earnings_dates_failed": list(self.md.earnings_failed) if uses_stocks else []})
        with self.L.tx():
            for i, d in enumerate(decisions):
                self.L.insert_decision(f"{T}:{i:03d}:{d.sleeve}:{d.ticker}:{d.reason_code}", D.isoformat(), T.isoformat(), d, iso(now))
            for o in orders:
                self.L.insert_order(o)
            self.L.insert_decision(f"decide:{T}", D.isoformat(), T.isoformat(), summary, iso(now))
        self.note(f"decided for {T}: {len(orders)} orders ({order_type}), regime {regime}")
