"""Diversified trend book (paper only): a published, rule-based risk-control strategy, not a profit promise.

Rule (fixed in advance, see research/review_2026_10_05/TREND_RESEARCH.md): at each month-end, hold 1/N of capital in each of N
asset-class ETFs for every one of the 8-, 10- and 12-month simple moving averages its last close is above (fraction of the three);
everything not allocated is held in short-term Treasuries (cash_asset). Decisions use closes through D and execute at the next open.
Independent implementation of the idea in Faber (2007), "A Quantitative Approach to Tactical Asset Allocation"."""
from __future__ import annotations

import pandas as pd

from .broker import CostModel, Order
from .engine import DERIVE_AFTER, Engine
from .nyse_calendar import ET, iso, next_session, prev_session, session_close, session_open, sessions_between

import datetime as dt

TRADING_DAYS_PER_MONTH = 21


def trend_weights(closes: pd.DataFrame, assets: list[str], months: list[int] | None = None,
                  sessions: list[int] | None = None) -> tuple[dict, dict]:
    """Return ({asset: weight}, {asset: detail}). Windows are given in months (21 sessions each) or directly in sessions.
    Raises if any asset lacks the history for the longest average."""
    if (months is None) == (sessions is None):
        raise ValueError("give exactly one of months or sessions")
    windows = {m: m * TRADING_DAYS_PER_MONTH for m in months} if months is not None else {n: n for n in sessions}
    key = "above_sma_months" if months is not None else "above_sma_sessions"
    need = max(windows.values())
    weights, detail = {}, {}
    for a in assets:
        s = closes[a].dropna()
        if len(s) < need:
            raise ValueError(f"{a}: {len(s)} closes, need {need}")
        last = float(s.iloc[-1])
        votes = {label: last > float(s.iloc[-n:].mean()) for label, n in windows.items()}
        frac = sum(votes.values()) / len(windows)
        detail[a] = {"close": last, key: [m for m, v in votes.items() if v], "weight_fraction": frac}
        if frac > 0:
            weights[a] = frac / len(assets)
    return weights, detail


def is_rebalance_day(T: dt.date, D: dt.date, every: str, first: bool) -> bool:
    """D is the last completed session, T the next one. 'month-end': D closes its month; 'week-end': D closes its ISO week."""
    if first:
        return True
    if every == "week-end":
        return T.isocalendar()[:2] != D.isocalendar()[:2]
    if every == "month-end":
        return T.month != D.month
    raise ValueError(f"unknown rebalance rule {every!r}")


def rebalance_orders(*, equity: float, cash: float, qty: dict, prices: dict, weights: dict, cash_asset: str,
                     buffer: float, min_order: float, band_fraction: float) -> list[dict]:
    """Pure sizing. weights are risk-asset weights; the remainder goes to cash_asset. Returns dicts
    {ticker, side, qty|notional, code} with sells first. Exposure removed is never redistributed beyond the targets."""
    targets = dict(weights)
    targets[cash_asset] = max(0.0, 1.0 - sum(weights.values()))
    band = max(min_order, band_fraction * equity)
    investable = equity * (1.0 - buffer)
    sells, buys = [], []
    for t in sorted(set(targets) | {t for t, q in qty.items() if q > 0}):
        px = prices.get(t)
        if not px or px <= 0:
            continue
        cur = qty.get(t, 0.0) * px
        tgt = targets.get(t, 0.0) * investable
        diff = tgt - cur
        if tgt == 0.0 and cur > 0:
            sells.append({"ticker": t, "side": "SELL", "qty": None, "value": cur, "code": "TREND_EXIT"})
        elif diff < -band:
            sells.append({"ticker": t, "side": "SELL", "qty": -diff / px, "value": -diff, "code": "TREND_TRIM"})
        elif diff > band:
            buys.append({"ticker": t, "side": "BUY", "notional": diff, "value": diff, "code": "TREND_BUY"})
    available = (cash + 0.998 * sum(s["value"] for s in sells) - buffer * equity) * 0.995
    want = sum(b["notional"] for b in buys)
    if buys and want > available:
        scale = max(0.0, available) / want
        for b in buys:
            b["notional"] *= scale
        buys = [b for b in buys if b["notional"] >= min_order]
    return sells + buys


class TrendEngine(Engine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # the experiment-wide start date is not this book's: it starts when its own ledger was frozen
        e = self.L.experiment()
        self.start = dt.date.fromisoformat(e["start_date"])
        t = self.cfg["trend"]
        self.assets, self.cash_asset = list(t["assets"]), t["cash_asset"]
        self.months = list(t["sma_months"]) if "sma_months" in t else None
        self.sessions = list(t["sma_sessions"]) if "sma_sessions" in t else None
        self.every = t.get("rebalance_every", "month-end")
        # these are all index ETFs: use the ETF cost line, not the single-stock liquidity tiers
        self.broker.costs = CostModel(self.cfg["costs"], set(self.assets) | {self.cash_asset, self.residual})

    def _universe(self) -> list[str]:
        return sorted(set(self.assets) | {self.cash_asset, self.residual})

    def maybe_decide(self, last_done: dt.date, lcs: dt.date) -> None:
        from .strategy import Decision
        now = self.now
        T = next_session(lcs)
        for s in sessions_between(self.start, min(prev_session(T), self.end)):
            if not self.decided(s):
                self._mark_missed(s, "no decision was made for this session (data unavailable or the cycle did not run in the window)")
        if T > self.end or T < self.start or self.decided(T):
            return
        if last_done < lcs:
            if now >= session_close(T) - dt.timedelta(minutes=30):
                self._mark_missed(T, f"prior session {lcs} data not final before the decision deadline")
            return
        latest = dt.datetime.combine(T, dt.time.fromisoformat(self.cfg["data"]["mkt_order_latest_et"]), ET)
        if now >= latest:
            self._mark_missed(T, "no cycle ran before the 15:30 ET decision deadline")
            return
        D = lcs
        order_type = "MOO" if now < session_open(T) else "MKT"
        universe = self._universe()
        flag = f"refreshed:{D.isoformat()}:trend"
        if not self.md.kv_get(flag):
            depth = self.md.db.execute("SELECT MIN(n) AS n FROM (SELECT COUNT(*) AS n FROM daily_bars WHERE ticker IN (%s) "
                                       "AND final IN (1,2) GROUP BY ticker)" % ",".join("?" * len(universe)), universe).fetchone()["n"]
            have = self.md.db.execute("SELECT COUNT(DISTINCT ticker) AS n FROM daily_bars WHERE ticker IN (%s)" % ",".join("?" * len(universe)),
                                      universe).fetchone()["n"]
            seed_needed = have < len(universe) or (depth or 0) < (max(self.months) * TRADING_DAYS_PER_MONTH if self.months else max(self.sessions)) + 10
            st = self.md.update_daily(universe, now, period="3y" if seed_needed else "10d")
            if st["failed"]:
                self.L.issue("ERROR", "marketdata", f"trend universe refresh failed for {st['failed']}; decision postponed")
                return
            self.md.kv_set(flag, iso(now))
        missing = [t for t in universe if self.md.bar_quality(t, D) not in (1, 2)]
        if missing:
            if now < session_close(D) + DERIVE_AFTER:
                self.note(f"trend decision for {T} waiting: official data for {D} incomplete for {missing}")
                return
            self.md.derive_from_intraday(missing, D, now)
            missing = [t for t in universe if self.md.bar_quality(t, D) not in (1, 2)]
            if missing:
                self.L.issue("ERROR", "marketdata", f"trend data {missing} missing for {D}; decision skipped")
                return
        fr = self.md.frames(universe, D)
        closes = fr["close"]
        spy_days = closes.index[closes[self.residual].notna()]
        closes = closes.loc[spy_days]
        if closes.empty or closes.index[-1].date() != D:
            self.L.issue("ERROR", "marketdata", f"cached frames do not end at {D}; trend decision skipped")
            return
        pf, _ = self.L.load_portfolio(self.cash0)
        px = {t: float(closes[t].iloc[-1]) for t in universe if pd.notna(closes[t].iloc[-1])}
        equity = pf.equity({t: px.get(t, p.entry_price) for t, p in pf.positions.items()})
        first = self.L.db.execute("SELECT 1 FROM decisions WHERE decision_key LIKE 'decide:%' AND reason_code='DECIDED' "
                                  "AND action='INFO' AND metrics LIKE '%\"rebalance\": true%'").fetchone() is None
        due = is_rebalance_day(T, D, self.every, first)
        risk_state = self.L.get_state("risk", {})
        halted = bool(risk_state.get("halt_until") and T.isoformat() <= risk_state["halt_until"])
        self.L.set_state("last_regime", "TREND")
        orders, decisions, rebalance = [], [], due
        detail: dict = {}
        if halted:
            rebalance = True
            for t in pf.positions:
                orders.append(Order(key=f"{T}:trend:{t}:SELL:DD_HALT", ticker=t, side="SELL", order_type=order_type, session=T.isoformat(),
                                    created_at=iso(now), sleeve="residual", reason_code="DD_HALT", reason="drawdown halt active: all cash",
                                    priority=10))
                decisions.append(Decision(t, "trend", "SELL", "DD_HALT", "drawdown halt active: all cash"))
        elif rebalance:
            weights, detail = trend_weights(closes, self.assets, self.months, self.sessions)
            spec = rebalance_orders(equity=equity, cash=pf.cash, qty={t: p.qty for t, p in pf.positions.items()}, prices=px,
                                    weights=weights, cash_asset=self.cash_asset, buffer=self.cfg["portfolio"]["cash_buffer"],
                                    min_order=self.cfg["portfolio"]["min_order_usd"], band_fraction=self.cfg["trend"]["rebalance_band"])
            for s in spec:
                d = detail.get(s["ticker"], {})
                above = d.get("above_sma_months", d.get("above_sma_sessions"))
                unit = "month" if "above_sma_months" in d else "session"
                why = (f"{s['ticker']}: above {above}-{unit} averages" if s["ticker"] in detail
                       else f"{s['ticker']}: unallocated capital held in short-term Treasuries")
                o = Order(key=f"{T}:trend:{s['ticker']}:{s['side']}:{s['code']}", ticker=s["ticker"], side=s["side"], order_type=order_type,
                          session=T.isoformat(), created_at=iso(now), sleeve="residual", reason_code=s["code"],
                          reason=f"{self.every} trend rebalance; {why}", notional=s.get("notional"), qty=s.get("qty"),
                          priority=10 if s["side"] == "SELL" else 50)
                orders.append(o)
                decisions.append(Decision(s["ticker"], "trend", s["side"], s["code"], o.reason, {"value": s["value"], **detail.get(s["ticker"], {})}))
        summary = Decision("*", "system", "INFO", "DECIDED",
                           f"{len(orders)} orders ({order_type}) for {T}; rebalance={rebalance}; trend weights "
                           + (", ".join(f"{k} {v['weight_fraction'] / len(self.assets):.0%}" for k, v in detail.items() if v["weight_fraction"] > 0) or "none")
                           if rebalance else f"{len(orders)} orders ({order_type}) for {T}; rebalance=False ({self.every.replace('-end', 'ly')})",
                           {"rebalance": rebalance, "order_type": order_type, "data_through": D.isoformat(), "detail": detail, "halted": halted})
        with self.L.tx():
            for i, d in enumerate(decisions):
                self.L.insert_decision(f"{T}:{i:03d}:{d.sleeve}:{d.ticker}:{d.reason_code}", D.isoformat(), T.isoformat(), d, iso(now))
            for o in orders:
                self.L.insert_order(o)
            self.L.insert_decision(f"decide:{T}", D.isoformat(), T.isoformat(), summary, iso(now))
        self.note(f"decided for {T}: {len(orders)} orders ({order_type}), rebalance={rebalance}")
