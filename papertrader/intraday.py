"""Day-trading book: 'stocks in play' 5-minute opening-range breakout (long only, flat by the close).

Pure logic shared by the backtest and the live engine. It is processed strictly bar by bar: when a
bar is processed, only that bar and earlier bars are known, so no decision can use later prices.

Timeline for one session:
  09:35 ET  first 5-minute bar complete -> pick candidates (heavy relative volume, first bar up)
            and place buy-stop orders at the first bar's high
  each bar  1) stops on open positions  2) breakout entries  3) same-bar stop check for new entries
  last bar  everything still open is sold at that bar's close
Cash account: purchases during a session are limited to the cash available at the open (T+1 settlement).
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field


@dataclass
class Candidate:
    ticker: str
    rank: int
    rvol: float
    first_open: float
    first_high: float
    first_low: float
    first_close: float
    first_volume: float
    atr: float
    adv_usd: float
    trigger: float
    stop_distance: float


@dataclass
class DayPosition:
    ticker: str
    qty: float
    entry_price: float  # after costs
    entry_ref: float
    stop: float
    entry_time: str


@dataclass
class DayEvent:
    kind: str  # BUY | SELL
    ticker: str
    qty: float
    ref_price: float
    fill_price: float
    cost_bps: float
    bar_time: str
    reason_code: str
    reason: str
    realized_pnl: float | None = None


@dataclass
class DayState:
    session: str
    cash_at_open: float
    cash: float
    buys_used: float = 0.0
    candidates: list[dict] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)  # tickers with a live buy-stop
    positions: dict[str, dict] = field(default_factory=dict)
    traded: list[str] = field(default_factory=list)  # one entry per ticker per day
    processed_through: str | None = None  # bar start time (ET ISO) of the last processed bar
    closed: bool = False

    def to_json(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_json(d: dict) -> "DayState":
        return DayState(**d)


# ---------------------------------------------------------------------------- selection
def select_candidates(first_bars: dict[str, tuple], hist_first_vol: dict[str, list[float]], daily: dict[str, dict],
                      cfg: dict) -> tuple[list[Candidate], list[tuple[str, str]]]:
    """first_bars: {t: (o, h, l, c, v)} for today's 09:30 bar. hist_first_vol: previous sessions' first-bar volumes.
    daily: {t: {'atr': .., 'avg_vol': .., 'adv_usd': .., 'prev_close': ..}} from completed daily bars before today."""
    U, SEL, ENT, EX = cfg["universe"], cfg["selection"], cfg["entry"], cfg["exit"]
    rows, skipped = [], []
    for t, (o, h, l, c, v) in first_bars.items():
        dd = daily.get(t)
        hist = [x for x in hist_first_vol.get(t, []) if x and x > 0]
        if not dd or any(x is None or not math.isfinite(x) for x in (o, h, l, c, v)) or v <= 0:
            continue
        if len(hist) < max(5, SEL["relative_volume_lookback_sessions"] // 2):
            continue
        if c < U["min_price"] or dd["avg_vol"] < U["min_avg_daily_volume_shares"] or dd["atr"] < U["min_atr_usd"]:
            continue
        rvol = v / (sum(hist[-SEL["relative_volume_lookback_sessions"]:]) / len(hist[-SEL["relative_volume_lookback_sessions"]:]))
        rows.append((rvol, t, (o, h, l, c, v), dd))
    rows.sort(reverse=True)
    out = []
    for rank, (rvol, t, (o, h, l, c, v), dd) in enumerate(rows[:SEL["top_n_by_relative_volume"]], start=1):
        if rvol < SEL["min_relative_volume"]:
            skipped.append((t, f"relative volume {rvol:.2f}x below {SEL['min_relative_volume']}x"))
            continue
        if SEL["require_first_bar_up"] and not c > o:
            skipped.append((t, f"first bar down ({o:.2f} → {c:.2f}); long-only book"))
            continue
        out.append(Candidate(ticker=t, rank=rank, rvol=rvol, first_open=o, first_high=h, first_low=l, first_close=c,
                             first_volume=v, atr=dd["atr"], adv_usd=dd["adv_usd"], trigger=h + ENT["trigger_offset_usd"],
                             stop_distance=EX["stop_atr_fraction"] * dd["atr"]))
    return out, skipped


# ---------------------------------------------------------------------------- costs
def cost_bps(cfg: dict, adv_usd: float, kind: str) -> float:
    c = cfg["costs"]
    b = c["stock_bps_adv_ge_1b"] if adv_usd >= 1e9 else c["stock_bps_adv_ge_200m"] if adv_usd >= 2e8 else c["stock_bps_other"]
    b += {"entry": c["entry_stop_extra_bps"], "stop": c["stop_exit_extra_bps"], "close": c["close_exit_extra_bps"]}[kind]
    if kind != "entry":
        b += c["sec_fee_bps_on_sells"]
    return b


def _floor(q: float, d: int) -> float:
    f = 10 ** d
    return math.floor(q * f) / f


# ---------------------------------------------------------------------------- bar processing
def process_bar(st: DayState, bar_time: str, bars: dict[str, tuple], cfg: dict, *, is_last_bar: bool,
                entries_allowed: bool, news_ok=None) -> list[DayEvent]:
    """Advance the session by one completed 5-minute bar. bars: {t: (o, h, l, c)} for this bar only."""
    P = cfg["portfolio"]
    cands = {c["ticker"]: c for c in st.candidates}
    events: list[DayEvent] = []

    def sell(t: str, ref: float, kind: str, code: str, why: str):
        p = st.positions.pop(t)
        c = cands[t]
        bps = cost_bps(cfg, c["adv_usd"], kind)
        px = ref * (1 - bps / 1e4)
        st.cash += p["qty"] * px  # proceeds: not reusable for buys today (T+1)
        events.append(DayEvent("SELL", t, p["qty"], ref, px, bps, bar_time, code, why, (px - p["entry_price"]) * p["qty"]))

    # 1) stops on positions held from earlier bars
    for t in list(st.positions):
        b = bars.get(t)
        if not b:
            continue
        o, h, l, c = b
        stop = st.positions[t]["stop"]
        if o <= stop:
            sell(t, o, "stop", "STOP_GAP", f"bar opened {o:.2f} below stop {stop:.2f}")
        elif l <= stop:
            sell(t, stop, "stop", "STOP", f"low {l:.2f} hit stop {stop:.2f}")
    # 2) breakout entries, higher relative volume first
    if entries_allowed:
        for t in sorted(st.pending, key=lambda x: cands[x]["rank"]):
            b = bars.get(t)
            if not b or t in st.positions or t in st.traded:
                continue
            o, h, l, c = b
            cand = cands[t]
            if h < cand["trigger"]:
                continue
            st.pending.remove(t)
            if len(st.positions) >= P["max_positions"]:
                events.append(DayEvent("SKIP", t, 0, 0, 0, 0, bar_time, "NO_SLOT", "breakout, but all position slots in use"))
                continue
            if news_ok is not None:
                ok, why = news_ok(t, bar_time)
                if not ok:
                    events.append(DayEvent("SKIP", t, 0, 0, 0, 0, bar_time, "NEWS_VETO", why))
                    continue
            ref = max(cand["trigger"], o)  # a buy stop fills at the trigger, or at the open if the bar gapped above it
            bps = cost_bps(cfg, cand["adv_usd"], "entry")
            px = ref * (1 + bps / 1e4)
            budget = min(P["position_weight"] * st.cash_at_open, st.cash_at_open - st.buys_used, st.cash)
            if budget < P["min_order_usd"]:
                events.append(DayEvent("SKIP", t, 0, 0, 0, 0, bar_time, "NO_CASH", "today's settled cash already used (cash account)"))
                continue
            q = _floor(budget / px, P["fractional_decimals"])
            st.cash -= q * px
            st.buys_used += q * px
            stop = ref - cand["stop_distance"]
            st.positions[t] = asdict(DayPosition(t, q, px, ref, stop, bar_time))
            st.traded.append(t)
            events.append(DayEvent("BUY", t, q, ref, px, bps, bar_time, "ORB_BREAKOUT",
                                   f"broke above first 5-min high {cand['first_high']:.2f} (rel. volume {cand['rvol']:.1f}x, "
                                   f"rank {cand['rank']}); stop {stop:.2f} = entry − 0.10×ATR ({cand['atr']:.2f})"))
            # 3) worst case inside the entry bar: if its low also reached the stop, assume we were stopped
            if l <= stop:
                sell(t, stop, "stop", "STOP", f"entry bar low {l:.2f} also reached stop {stop:.2f} (worst-case assumption)")
    # 4) end of session: flat by the close
    if is_last_bar:
        for t in list(st.positions):
            b = bars.get(t)
            ref = b[3] if b else st.positions[t]["entry_ref"]
            sell(t, ref, "close", "CLOSE_EXIT", "day trade: sold at the close")
        st.pending.clear()
        st.closed = True
    if not entries_allowed:
        st.pending.clear()
    st.processed_through = bar_time
    return events
