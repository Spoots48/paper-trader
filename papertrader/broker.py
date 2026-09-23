"""Simulated broker: portfolio state, cost model, and fill rules.

Shared by the backtest and the live engine so both use identical execution
logic. Fill rules (every fill uses a price that became available *after* the
order was created):

* MOO (market-on-open): official session open, plus open-auction slippage.
* MKT (intraday, live only): open of the first 5-minute bar that starts at or
  after the order time.
* Stops (standing, evaluated bar by bar after entry): if a bar opens at or
  below the stop, fill at that bar's open (gap-through); otherwise if its low
  touches the stop, fill at the stop. Extra slippage is applied to stop fills.

Costs are applied as an adverse price adjustment: buys fill above the
reference price, sells below it.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field


@dataclass
class Position:
    ticker: str
    qty: float
    avg_cost: float
    sleeve: str  # catalyst | momentum | residual
    entry_session: str
    entry_price: float
    initial_stop: float | None = None
    trail_pct: float | None = None
    high_water: float = 0.0
    max_hold_until: str | None = None
    meta: dict = field(default_factory=dict)

    def stop_level(self) -> float | None:
        lv = self.initial_stop or 0.0
        if self.trail_pct and self.high_water > 0:
            lv = max(lv, self.high_water * (1 - self.trail_pct))
        return lv if lv > 0 else None


@dataclass
class Order:
    key: str
    ticker: str
    side: str  # BUY | SELL
    order_type: str  # MOO | MKT
    session: str  # target session YYYY-MM-DD
    created_at: str  # UTC ISO timestamp of the decision
    sleeve: str
    reason_code: str
    reason: str
    notional: float | None = None  # BUY: dollars to invest; None = residual cash
    qty: float | None = None  # SELL: shares; None = entire position
    priority: int = 50  # lower fills first within the same side
    entry_params: dict = field(default_factory=dict)  # stop settings for new positions
    meta: dict = field(default_factory=dict)


@dataclass
class Fill:
    order_key: str
    ticker: str
    side: str
    qty: float
    ref_price: float
    fill_price: float
    cost_bps: float
    cost_usd: float
    session: str
    price_time: str  # timestamp of the bar/price used (ET ISO or session tag)
    price_source: str
    sleeve: str
    reason_code: str
    reason: str
    realized_pnl: float | None = None


@dataclass
class Portfolio:
    cash: float
    positions: dict[str, Position] = field(default_factory=dict)

    def equity(self, prices: dict[str, float]) -> float:
        return self.cash + sum(p.qty * prices.get(t, p.entry_price) for t, p in self.positions.items())

    def singles(self) -> dict[str, Position]:
        return {t: p for t, p in self.positions.items() if p.sleeve != "residual"}


class CostModel:
    def __init__(self, cfg: dict, etfs: set[str]):
        self.c = cfg
        self.etfs = etfs

    def bps(self, ticker: str, adv_usd: float | None, side: str, at_open: bool, is_stop: bool) -> float:
        c = self.c
        if ticker in self.etfs:
            b = c["etf_bps"]
        elif adv_usd is not None and adv_usd >= 1e9:
            b = c["stock_bps_adv_ge_1b"]
        elif adv_usd is not None and adv_usd >= 2e8:
            b = c["stock_bps_adv_ge_200m"]
        else:
            b = c["stock_bps_other"]
        if at_open:
            b += c["open_auction_extra_bps"]
        if is_stop:
            b += c["stop_fill_extra_bps"]
        if side == "SELL":
            b += c["sec_fee_bps_on_sells"]
        return b


def _round_qty(q: float, decimals: int) -> float:
    f = 10 ** decimals
    return math.floor(q * f) / f


def _apply_cost(ref: float, side: str, bps: float) -> float:
    return ref * (1 + bps / 1e4) if side == "BUY" else ref * (1 - bps / 1e4)


class Broker:
    """Applies orders and stops to a Portfolio. Returns Fill records; never places real orders."""

    def __init__(self, strategy_cfg: dict):
        self.cfg = strategy_cfg
        p = strategy_cfg["portfolio"]
        self.residual = p["residual_etf"]
        self.costs = CostModel(strategy_cfg["costs"], {self.residual})
        self.min_order = p["min_order_usd"]
        self.decimals = p["fractional_decimals"]
        self.cash_buffer = p["cash_buffer"]

    # -- primitive fills ------------------------------------------------------------
    def _sell(self, pf: Portfolio, ticker: str, qty: float | None, ref: float, session: str, price_time: str,
              source: str, adv: float | None, at_open: bool, is_stop: bool, key: str, reason_code: str,
              reason: str) -> Fill | None:
        pos = pf.positions.get(ticker)
        if pos is None or pos.qty <= 0:
            return None
        q = pos.qty if qty is None else min(qty, pos.qty)
        bps = self.costs.bps(ticker, adv, "SELL", at_open, is_stop)
        px = _apply_cost(ref, "SELL", bps)
        proceeds = q * px
        pnl = (px - pos.avg_cost) * q
        pf.cash += proceeds
        pos.qty = _round_qty(pos.qty - q, self.decimals) if qty is not None else 0.0
        if pos.qty * ref < 0.01:
            del pf.positions[ticker]
        return Fill(key, ticker, "SELL", q, ref, px, bps, q * (ref - px), session, price_time, source,
                    pos.sleeve, reason_code, reason, realized_pnl=pnl)

    def _buy(self, pf: Portfolio, order: Order, ref: float, session: str, price_time: str, source: str,
             adv: float | None, at_open: bool, equity_now: float) -> tuple[Fill | None, str | None]:
        if order.notional is None:  # residual sleeve: all cash above the buffer
            budget = pf.cash - self.cash_buffer * equity_now
        else:
            budget = min(order.notional, pf.cash)
        if budget < self.min_order:
            return None, f"insufficient cash (available ${pf.cash:.2f}, budget ${budget:.2f})"
        bps = self.costs.bps(order.ticker, adv, "BUY", at_open, False)
        px = _apply_cost(ref, "BUY", bps)
        q = _round_qty(budget / px, self.decimals)
        if q <= 0:
            return None, "quantity rounds to zero"
        pf.cash -= q * px
        ep = order.entry_params
        pos = pf.positions.get(order.ticker)
        if pos is None:
            stop = None
            if ep.get("stop_max_loss"):
                stop = px * (1 - ep["stop_max_loss"])
                rl = ep.get("reaction_low")
                if rl and rl <= px * (1 - ep.get("stop_min_distance", 0.03)):
                    stop = max(stop, rl)
            pf.positions[order.ticker] = Position(
                ticker=order.ticker, qty=q, avg_cost=px, sleeve=order.sleeve, entry_session=session,
                entry_price=px, initial_stop=stop, trail_pct=ep.get("trailing_stop"), high_water=px,
                max_hold_until=ep.get("max_hold_until"), meta=dict(order.meta))
        else:  # add to existing (only the residual ETF does this)
            tot = pos.qty + q
            pos.avg_cost = (pos.avg_cost * pos.qty + px * q) / tot
            pos.qty = tot
        return Fill(order.key, order.ticker, "BUY", q, ref, px, bps, q * (px - ref), session, price_time,
                    source, order.sleeve, order.reason_code, order.reason), None

    # -- session steps --------------------------------------------------------------
    def execute_open(self, pf: Portfolio, session: str, orders: list[Order], opens: dict[str, float],
                     adv: dict[str, float], price_time: str, source: str
                     ) -> tuple[list[Fill], list[tuple[Order, str]]]:
        """Fill MOO orders at the session open. Sells first, then open-gap stops, then buys."""
        fills: list[Fill] = []
        rejected: list[tuple[Order, str]] = []
        moo = [o for o in orders if o.order_type == "MOO" and o.session == session]
        selling = set()
        for o in sorted([o for o in moo if o.side == "SELL"], key=lambda o: o.priority):
            ref = opens.get(o.ticker)
            if ref is None or not math.isfinite(ref) or ref <= 0:
                rejected.append((o, "no valid open price"))
                continue
            f = self._sell(pf, o.ticker, o.qty, ref, session, price_time, source, adv.get(o.ticker), True,
                           False, o.key, o.reason_code, o.reason)
            if f:
                fills.append(f)
                selling.add(o.ticker)
            else:
                rejected.append((o, "no position to sell"))
        # stops that gap through at the open
        for t, pos in list(pf.positions.items()):
            if t in selling:
                continue
            stop = pos.stop_level()
            ref = opens.get(t)
            if stop and ref and math.isfinite(ref) and ref <= stop:
                f = self._sell(pf, t, None, ref, session, price_time, source, adv.get(t), True, True,
                               f"stop:{t}:{pos.entry_session}", "STOP_GAP",
                               f"opened at {ref:.2f}, at/below stop {stop:.2f}")
                if f:
                    fills.append(f)
        marks = dict(opens)
        for o in sorted([o for o in moo if o.side == "BUY"], key=lambda o: o.priority):
            ref = opens.get(o.ticker)
            if ref is None or not math.isfinite(ref) or ref <= 0:
                rejected.append((o, "no valid open price"))
                continue
            f, why = self._buy(pf, o, ref, session, price_time, source, adv.get(o.ticker), True,
                               pf.equity(marks))
            if f:
                fills.append(f)
            else:
                rejected.append((o, why or "rejected"))
        return fills, rejected

    def execute_market(self, pf: Portfolio, order: Order, ref: float, price_time: str, source: str,
                       adv: float | None, marks: dict[str, float]) -> tuple[Fill | None, str | None]:
        """Intraday market order at a price observed after the order time (live engine only)."""
        if order.side == "SELL":
            f = self._sell(pf, order.ticker, order.qty, ref, order.session, price_time, source, adv, False,
                           False, order.key, order.reason_code, order.reason)
            return f, (None if f else "no position to sell")
        return self._buy(pf, order, ref, order.session, price_time, source, adv, False, pf.equity(marks))

    def check_stop(self, pf: Portfolio, ticker: str, bars: list[tuple[str, float, float, float, float]],
                   session: str, source: str, adv: float | None) -> Fill | None:
        """bars: chronological (bar_time, open, high, low, close), all strictly after entry/last check."""
        pos = pf.positions.get(ticker)
        if pos is None:
            return None
        stop = pos.stop_level()
        if not stop:
            return None
        for (bt, o, h, lo, c) in bars:
            if any(not math.isfinite(x) for x in (o, lo)):
                continue
            if o <= stop:
                return self._sell(pf, ticker, None, o, session, bt, source, adv, False, True,
                                  f"stop:{ticker}:{pos.entry_session}", "STOP_GAP",
                                  f"bar opened at {o:.2f}, below stop {stop:.2f}")
            if lo <= stop:
                return self._sell(pf, ticker, None, stop, session, bt, source, adv, False, True,
                                  f"stop:{ticker}:{pos.entry_session}", "STOP",
                                  f"low {lo:.2f} touched stop {stop:.2f}")
        return None

    def close_session(self, pf: Portfolio, highs: dict[str, float]) -> None:
        """After the session: raise high-water marks so trailing stops apply from the next bar."""
        for t, pos in pf.positions.items():
            h = highs.get(t)
            if h and math.isfinite(h):
                pos.high_water = max(pos.high_water, h)


def session_str(d: dt.date) -> str:
    return d.isoformat()
