"""Strategy rules (frozen v1). Pure decision logic shared by backtest and live engine.

Everything here only reads rows at or before the decision date D, so
calling it with full-history frames can't leak future information.
"""
from __future__ import annotations

import bisect
import datetime as dt
import math
from dataclasses import dataclass, field
from typing import Callable

import pandas as pd

from .broker import Order, Portfolio


# ---------------------------------------------------------------------------- indicators
class Indicators:
    """Wide (session x ticker) frames. Rolling windows only look backwards."""

    def __init__(self, o: pd.DataFrame, h: pd.DataFrame, l: pd.DataFrame, c: pd.DataFrame, v: pd.DataFrame,
                 cfg: dict):
        self.o, self.h, self.l, self.c, self.v = o, h, l, c, v
        m = cfg["momentum"]
        cat = cfg["catalyst"]
        self.sma50 = c.rolling(50, min_periods=50).mean()
        self.sma200 = c.rolling(cfg["regime"]["sma_days"], min_periods=cfg["regime"]["sma_days"]).mean()
        self.adv20 = (c * v).rolling(20, min_periods=15).mean()
        self.vol_prev = v.shift(1).rolling(cat["volume_lookback"], min_periods=15).mean()
        self.ret1 = c / c.shift(1) - 1
        rng = (h - l)
        self.clv = (c - l) / rng.where(rng > 0)
        self.mom = c.shift(m["skip_recent_sessions"]) / c.shift(m["lookback_sessions"]) - 1
        self.vol = self.ret1.rolling(m["vol_lookback_sessions"], min_periods=int(m["vol_lookback_sessions"] * 0.8)).std()
        self.mom_score = self.mom / self.vol.where(self.vol > 0)


def valid_bar(o: float, h: float, l: float, c: float, v: float) -> bool:
    vals = (o, h, l, c, v)
    if any(x is None or not math.isfinite(x) for x in vals):
        return False
    if min(o, h, l, c) <= 0 or v <= 0:
        return False
    return h >= max(o, c) * 0.9999 and l <= min(o, c) * 1.0001


# ---------------------------------------------------------------------------- regime
def regime_series(spy_close: pd.Series, spy_sma: pd.Series, vix: pd.Series, cfg: dict,
                  next_trading_session: Callable[[dt.date], dt.date] | None = None) -> pd.Series:
    """Causal close signals; weekly reviews use the exchange schedule, never future prices."""
    from .nyse_calendar import next_session

    r = cfg["regime"]
    frequency = r.get("review_frequency", "daily")
    if frequency not in ("daily", "weekly"):
        raise ValueError(f"Unsupported regime review frequency: {frequency}")
    next_trading_session = next_trading_session or next_session
    use_vix = r.get("use_vix", True)
    out, prev, unknown = {}, "OFF", False
    for d in spy_close.index:
        if frequency == "weekly" and next_trading_session(d.date()).isocalendar()[:2] == d.date().isocalendar()[:2]:
            out[d] = prev + ("?" if unknown else "")
            continue
        c, s, x = spy_close.get(d), spy_sma.get(d), vix.get(d)
        inputs = (c, s, x) if use_vix else (c, s)
        unknown = any(y is None or not math.isfinite(y) for y in inputs)
        if unknown:
            out[d] = prev + "?"  # no new entries until the next valid scheduled review
            continue
        on = c > s and (not use_vix or x < r["vix_risk_off_above" if prev == "ON" else "vix_risk_on_below"])
        prev = "ON" if on else "OFF"
        out[d] = prev
    return pd.Series(out)


# ---------------------------------------------------------------------------- earnings
@dataclass
class EarningsEvent:
    ticker: str
    announce_ts: str  # 'YYYY-MM-DD HH:MM' America/New_York
    reaction: dt.date
    exit_before: dt.date  # last session whose open precedes the announcement
    reported: bool
    eps_estimate: float | None = None
    eps_reported: float | None = None
    surprise_pct: float | None = None
    source: str = ""


class EarningsBook:
    def __init__(self, events: list[EarningsEvent]):
        self.by_reaction: dict[dt.date, list[EarningsEvent]] = {}
        self.reactions: dict[str, list[dt.date]] = {}
        for e in events:
            self.by_reaction.setdefault(e.reaction, []).append(e)
            self.reactions.setdefault(e.ticker, []).append(e.reaction)
        for t in self.reactions:
            self.reactions[t] = sorted(set(self.reactions[t]))

    def reacting_on(self, d: dt.date) -> list[EarningsEvent]:
        return self.by_reaction.get(d, [])

    def reaction_within(self, ticker: str, start: dt.date, end: dt.date) -> dt.date | None:
        lst = self.reactions.get(ticker)
        if not lst:
            return None
        i = bisect.bisect_left(lst, start)
        if i < len(lst) and lst[i] <= end:
            return lst[i]
        return None


def map_reaction(announce_ts: str, cutoff_hour: int, sessions: list[dt.date]) -> tuple[dt.date, dt.date] | None:
    """(reaction session, last session before the announcement) using a sorted session list."""
    d = dt.date.fromisoformat(announce_ts[:10])
    hour = int(announce_ts[11:13])
    if hour < cutoff_hour:
        i = bisect.bisect_left(sessions, d)  # first session >= d
    else:
        i = bisect.bisect_right(sessions, d)  # first session > d
    if i <= 0 or i >= len(sessions):
        return None
    return sessions[i], sessions[i - 1]


# ---------------------------------------------------------------------------- decisions
@dataclass
class NewsVerdict:
    ok: bool
    status: str  # confirmed | no_veto | vetoed | unavailable | unconfirmed | skipped
    reason: str
    news_ids: list = field(default_factory=list)


@dataclass
class Decision:
    ticker: str
    sleeve: str
    action: str  # BUY | SELL | SKIP | HOLD | INFO
    reason_code: str
    reason: str
    metrics: dict = field(default_factory=dict)
    news_ids: list = field(default_factory=list)


@dataclass
class DecisionContext:
    cfg: dict
    ind: Indicators
    stocks: list[str]
    regime: str  # ON | OFF | ON? | OFF?
    earnings: EarningsBook
    pf: Portfolio
    risk: dict  # {'paused': bool, 'halted': bool, 'drawdown': float}
    is_rebalance: bool
    created_at: str
    order_type: str = "MOO"
    eligible: Callable[[str, dt.date], bool] | None = None
    news_check: Callable[[str, str, dict], NewsVerdict] | None = None
    add_sessions: Callable[[dt.date, int], dt.date] | None = None
    earnings_complete: bool = True  # False if any calendar day in the blackout horizon failed to load


def _f(x) -> float | None:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def decide(D: dt.date, S: dt.date, ctx: DecisionContext) -> tuple[list[Order], list[Decision]]:
    """Orders for session S using information available after the close of D."""
    cfg, ind, pf = ctx.cfg, ctx.ind, ctx.pf
    P, CAT, MOM = cfg["portfolio"], cfg["catalyst"], cfg["momentum"]
    ts = pd.Timestamp(D)
    Ss = S.isoformat()
    otype = ctx.order_type
    orders: list[Order] = []
    decisions: list[Decision] = []
    closes = ind.c.loc[ts]
    residual = P["residual_etf"]

    def px(t: str) -> float | None:
        return _f(closes.get(t))

    marks = {t: (px(t) or p.entry_price) for t, p in pf.positions.items()}
    equity = pf.equity(marks)

    def sell(t: str, code: str, reason: str, sleeve: str, qty: float | None = None, prio: int = 10):
        orders.append(Order(key=f"{Ss}:{sleeve}:{t}:SELL:{code}", ticker=t, side="SELL", order_type=otype,
                            session=Ss, created_at=ctx.created_at, sleeve=sleeve, reason_code=code,
                            reason=reason, qty=qty, priority=prio))
        decisions.append(Decision(t, sleeve, "SELL", code, reason))

    # ---- market-level gates
    if ctx.risk.get("halted"):
        for t, p in pf.positions.items():
            sell(t, "DD_HALT", f"drawdown halt active (drawdown {ctx.risk.get('drawdown', 0):.1%})", p.sleeve)
        decisions.append(Decision("*", "risk", "INFO", "DD_HALT", "drawdown halt: all cash, no buys"))
        return orders, decisions
    if ctx.regime.startswith("OFF"):
        for t, p in pf.positions.items():
            sell(t, "REGIME_OFF", "market regime risk-off (SPY below 200d SMA or VIX high)", p.sleeve)
        decisions.append(Decision("*", "regime", "INFO", "REGIME_OFF",
                                  "risk-off regime: hold cash" + (" (regime inputs missing)" if "?" in ctx.regime else ""),
                                  {"regime": ctx.regime}))
        return orders, decisions
    no_new_entries = ctx.regime.endswith("?")
    if no_new_entries:
        decisions.append(Decision("*", "regime", "INFO", "REGIME_UNKNOWN",
                                  "regime inputs missing for D; keeping positions, no new entries"))

    # ---- exits for single-stock positions
    selling: set[str] = set()
    rank_of: dict[str, int] = {}
    ranked: list[str] = []
    if MOM["enabled"] and ctx.is_rebalance:
        ranked = momentum_ranking(ts, ctx)
        rank_of = {t: i + 1 for i, t in enumerate(ranked)}
    for t, p in pf.singles().items():
        if p.max_hold_until and Ss >= p.max_hold_until:
            sell(t, "TIME_EXIT", f"max holding period reached ({p.max_hold_until})", p.sleeve)
            selling.add(t)
            continue
        if p.sleeve == "momentum":
            if MOM["exit_before_earnings"]:
                r = ctx.earnings.reaction_within(t, S, ctx.add_sessions(S, 1))
                if r is not None:
                    sell(t, "EARNINGS_AVOID", f"earnings reaction expected {r}; momentum positions don't hold through earnings", p.sleeve)
                    selling.add(t)
                    continue
            if ctx.is_rebalance:
                c, s50 = px(t), _f(ind.sma50.loc[ts].get(t))
                rk = rank_of.get(t)
                if rk is None or rk > MOM["exit_rank_buffer"]:
                    sell(t, "MOMENTUM_EXIT", f"momentum rank {rk or 'n/a'} outside top {MOM['exit_rank_buffer']}", p.sleeve)
                    selling.add(t)
                elif c is not None and s50 is not None and c < s50:
                    sell(t, "MOMENTUM_EXIT", f"close {c:.2f} below 50d SMA {s50:.2f}", p.sleeve)
                    selling.add(t)

    singles_after = [t for t in pf.singles() if t not in selling]
    slots = P["max_single_stock_positions"] - len(singles_after)
    n_cat = sum(1 for t in singles_after if pf.positions[t].sleeve == "catalyst")
    n_mom = sum(1 for t in singles_after if pf.positions[t].sleeve == "momentum")
    buys: list[Order] = []
    notional = min(P["target_weight"], P["max_weight_at_entry"]) * equity
    paused = ctx.risk.get("paused", False)
    if paused:
        decisions.append(Decision("*", "risk", "INFO", "DD_PAUSE",
                                  f"drawdown pause active ({ctx.risk.get('drawdown', 0):.1%}); no new stock entries"))

    # ---- catalyst entries (earnings gap continuation)
    if CAT["enabled"] and not paused and not no_new_entries:
        cands = []
        for ev in ctx.earnings.reacting_on(D):
            t = ev.ticker
            if t not in ind.c.columns:
                continue
            m = catalyst_metrics(ts, t, ind)
            m.update({"announce_ts_et": ev.announce_ts, "reaction_session": D.isoformat(),
                      "eps_surprise_pct": _f(ev.surprise_pct), "earnings_source": ev.source})
            ok, why = catalyst_passes(m, CAT)
            if ctx.eligible and not ctx.eligible(t, D):
                ok, why = False, "not in index at that date"
            if not ok:
                if m.get("ret") is not None and m["ret"] > 0.02:  # only log near-misses to keep the ledger readable
                    decisions.append(Decision(t, "catalyst", "SKIP", "CRITERIA", why, m))
                continue
            cands.append((m["excess"], t, m))
        cands.sort(reverse=True)
        for _, t, m in cands:
            if t in pf.positions and t not in selling:
                decisions.append(Decision(t, "catalyst", "SKIP", "ALREADY_HELD", "already held", m))
                continue
            if slots <= 0 or n_cat >= CAT["max_positions"]:
                decisions.append(Decision(t, "catalyst", "SKIP", "NO_SLOT", "all position slots in use", m))
                continue
            nv = None
            if ctx.news_check and CAT["news_required"]:
                nv = ctx.news_check(t, "catalyst", m)
                if not nv.ok:
                    decisions.append(Decision(t, "catalyst", "SKIP", "NEWS_" + nv.status.upper(), nv.reason, m, nv.news_ids))
                    continue
            reason = (f"earnings reaction {m['ret']:+.1%} ({m['excess']:+.1%} vs SPY), volume {m['vol_ratio']:.1f}x, "
                      f"close location {m['clv']:.2f}" + (f"; news: {nv.reason}" if nv else "; news not checked (backtest)"))
            buys.append(Order(key=f"{Ss}:catalyst:{t}:BUY:EARNINGS_GAP", ticker=t, side="BUY", order_type=otype,
                              session=Ss, created_at=ctx.created_at, sleeve="catalyst", reason_code="EARNINGS_GAP",
                              reason=reason, notional=notional, priority=20 + len(buys),
                              entry_params={"stop_max_loss": CAT["stop_max_loss"],
                                            "reaction_low": m["low"] if CAT["stop_use_reaction_low"] else None,
                                            "stop_min_distance": CAT.get("stop_min_distance", 0.03),
                                            "trailing_stop": CAT["trailing_stop"],
                                            "max_hold_until": ctx.add_sessions(S, CAT["max_hold_sessions"]).isoformat()},
                              meta={"metrics": m}))
            decisions.append(Decision(t, "catalyst", "BUY", "EARNINGS_GAP", reason, m, nv.news_ids if nv else []))
            slots -= 1
            n_cat += 1

    # ---- momentum entries (weekly)
    if MOM["enabled"] and ctx.is_rebalance and not paused and not no_new_entries and not ctx.earnings_complete:
        decisions.append(Decision("*", "momentum", "SKIP", "EARNINGS_DATA_MISSING",
                                  "earnings calendar incomplete (data outage), so the earnings blackout can't be checked; no momentum entries"))
    elif MOM["enabled"] and ctx.is_rebalance and not paused and not no_new_entries:
        for t in ranked:
            if n_mom >= MOM["max_positions"] or slots <= 0:
                break
            if t in pf.positions or any(b.ticker == t for b in buys):
                continue
            r = ctx.earnings.reaction_within(t, S, ctx.add_sessions(S, MOM["earnings_blackout_sessions"]))
            m = {"rank": rank_of[t], "mom_score": _f(ind.mom_score.loc[ts].get(t)), "mom_ret": _f(ind.mom.loc[ts].get(t)),
                 "close": px(t), "sma50": _f(ind.sma50.loc[ts].get(t)), "sma200": _f(ind.sma200.loc[ts].get(t)),
                 "adv20": _f(ind.adv20.loc[ts].get(t))}
            if r is not None:
                decisions.append(Decision(t, "momentum", "SKIP", "EARNINGS_BLACKOUT", f"earnings reaction expected {r}", m))
                continue
            nv = None
            if ctx.news_check and MOM["news_veto"]:
                nv = ctx.news_check(t, "momentum", m)
                if not nv.ok:
                    decisions.append(Decision(t, "momentum", "SKIP", "NEWS_" + nv.status.upper(), nv.reason, m, nv.news_ids))
                    continue
            reason = (f"momentum rank #{m['rank']} (6-1 month return {m['mom_ret']:+.1%}, vol-adjusted score {m['mom_score']:.2f}), "
                      f"uptrend: close > 50d > 200d SMA" + (f"; news: {nv.reason}" if nv else ""))
            buys.append(Order(key=f"{Ss}:momentum:{t}:BUY:MOMENTUM", ticker=t, side="BUY", order_type=otype, session=Ss,
                              created_at=ctx.created_at, sleeve="momentum", reason_code="MOMENTUM", reason=reason,
                              notional=notional, priority=40 + len(buys),
                              entry_params={"stop_max_loss": MOM["stop_max_loss"], "trailing_stop": MOM["trailing_stop"]},
                              meta={"metrics": m}))
            decisions.append(Decision(t, "momentum", "BUY", "MOMENTUM", reason, m, nv.news_ids if nv else []))
            slots -= 1
            n_mom += 1

    orders.extend(buys)

    # ---- residual sleeve (SPY)
    spy_px = px(residual)
    if spy_px:
        sell_val = sum(pf.positions[t].qty * (px(t) or pf.positions[t].entry_price) for t in selling)
        buy_val = sum(b.notional or 0 for b in buys)
        singles_val = sum(p.qty * (px(t) or p.entry_price) for t, p in pf.singles().items()) - sell_val + buy_val
        spy_pos = pf.positions.get(residual)
        spy_val = spy_pos.qty * spy_px if spy_pos else 0.0
        cash_after = pf.cash + sell_val * 0.998 - buy_val
        buffer = P["cash_buffer"] * equity
        target = max(0.0, equity * (1 - P["cash_buffer"]) - singles_val)
        band = P["residual_rebalance_band"] * equity
        if cash_after < buffer and spy_pos:
            q = min(spy_pos.qty, (buffer - cash_after) / spy_px * 1.01)
            sell(residual, "FUNDING", f"sell ${q * spy_px:.2f} of {residual} to fund new positions", "residual", qty=q, prio=5)
        elif target - spy_val > band and cash_after - buffer > P["min_order_usd"]:
            orders.append(Order(key=f"{Ss}:residual:{residual}:BUY:RESIDUAL", ticker=residual, side="BUY", order_type=otype,
                                session=Ss, created_at=ctx.created_at, sleeve="residual", reason_code="RESIDUAL",
                                reason=f"park idle cash in {residual} (regime risk-on)", notional=None, priority=90))
            decisions.append(Decision(residual, "residual", "BUY", "RESIDUAL", f"invest idle cash (~${cash_after - buffer:.2f}) in {residual}"))
        elif spy_val - target > band and spy_pos:
            q = min(spy_pos.qty, (spy_val - target) / spy_px)
            sell(residual, "REBALANCE", f"trim {residual} by ${q * spy_px:.2f} to target", "residual", qty=q, prio=5)
    return orders, decisions


def catalyst_metrics(ts: pd.Timestamp, t: str, ind: Indicators) -> dict:
    g = lambda fr: _f(fr.loc[ts].get(t))  # noqa: E731
    o, h, lo, c, v = g(ind.o), g(ind.h), g(ind.l), g(ind.c), g(ind.v)
    ret, spy_ret = g(ind.ret1), _f(ind.ret1.loc[ts].get("SPY"))
    vp = g(ind.vol_prev)
    return {
        "open": o, "high": h, "low": lo, "close": c, "volume": v,
        "valid_bar": valid_bar(o, h, lo, c, v),
        "ret": ret, "spy_ret": spy_ret,
        "excess": (ret - spy_ret) if ret is not None and spy_ret is not None else None,
        "clv": g(ind.clv), "vol_ratio": (v / vp) if v and vp else None, "adv20": g(ind.adv20),
    }


def catalyst_passes(m: dict, CAT: dict) -> tuple[bool, str]:
    if not m["valid_bar"]:
        return False, "invalid or missing bar for reaction day"
    for k in ("ret", "excess", "clv", "vol_ratio", "adv20"):
        if m.get(k) is None:
            return False, f"missing {k}"
    if m["ret"] < CAT["min_reaction_return"]:
        return False, f"reaction {m['ret']:+.1%} < {CAT['min_reaction_return']:.0%}"
    if m["excess"] < CAT["min_excess_vs_spy"]:
        return False, f"excess vs SPY {m['excess']:+.1%} < {CAT['min_excess_vs_spy']:.0%}"
    if m["clv"] < CAT["min_close_location"]:
        return False, f"faded: close location {m['clv']:.2f} < {CAT['min_close_location']}"
    if m["vol_ratio"] < CAT["min_volume_ratio"]:
        return False, f"volume {m['vol_ratio']:.1f}x < {CAT['min_volume_ratio']}x"
    if m["close"] < CAT["min_price"]:
        return False, "price below minimum"
    if m["adv20"] < CAT["min_adv_usd"]:
        return False, "insufficient liquidity"
    return True, "passes"


def momentum_ranking(ts: pd.Timestamp, ctx: DecisionContext) -> list[str]:
    ind, MOM = ctx.ind, ctx.cfg["momentum"]
    cols = [t for t in ctx.stocks if t in ind.c.columns]
    c = ind.c.loc[ts, cols]
    score = ind.mom_score.loc[ts, cols]
    mask = score.notna() & (c >= MOM["min_price"]) & (ind.adv20.loc[ts, cols] >= MOM["min_adv_usd"])
    if MOM["require_close_above_sma50"]:
        mask &= c > ind.sma50.loc[ts, cols]
    if MOM["require_sma50_above_sma200"]:
        mask &= ind.sma50.loc[ts, cols] > ind.sma200.loc[ts, cols]
    # the bar for D itself must be valid
    mask &= ind.v.loc[ts, cols] > 0
    if ctx.eligible:
        D = ts.date()
        mask &= pd.Series({t: ctx.eligible(t, D) for t in cols})
    return list(score[mask].sort_values(ascending=False).index)
