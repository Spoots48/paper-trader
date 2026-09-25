"""Crypto odds bot v2: pure decision logic (shared by the live engine and the backtest).

Settlement (verified against official outcomes): hourly markets = Binance 1h candle close >= open;
5/15-minute and 4-hour markets = Chainlink 60-second TWAP at the end >= at the start, i.e. effectively
end price vs start price. Both are digital "close vs open" bets.
"""
from __future__ import annotations

import math

from .predmarket import phi, taker_fee_per_share


def fair_prob_digital(s_open: float, s_now: float, minutes_left: float, sigma_per_min: float, shift_frac: float = 0.0) -> float:
    """P(close >= open * (1 + shift_frac)) for a driftless random walk."""
    k = s_open * (1 + shift_frac)
    if minutes_left <= 0:
        return 1.0 if s_now >= k else 0.0
    sd = sigma_per_min * math.sqrt(minutes_left)
    if sd <= 0:
        return 1.0 if s_now >= k else 0.0
    return phi(math.log(s_now / k) / sd)


def sigma_from_closes(closes: list[float], floor: float) -> float:
    rets = [math.log(b / a) for a, b in zip(closes[:-1], closes[1:]) if a > 0 and b > 0]
    if len(rets) < 10:
        return floor
    mu = sum(rets) / len(rets)
    sd = (sum((r - mu) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5
    return max(sd, floor)


def decide_v2(s_open: float, s_now: float, minutes_left: float, sigma: float, elapsed: float,
              asks: dict[str, float], mid_up: float | None, cfg: dict) -> dict:
    """Return {'side','q','ask','unit','edge','reason'} for the best side, or {'skip': reason}."""
    M, E, Mk = cfg["model"], cfg["entry"], cfg["markets"]
    rate = cfg["fees"]["crypto_taker_fee_rate"]
    if not (Mk["min_elapsed_fraction"] <= elapsed <= Mk["max_elapsed_fraction"]):
        return {"skip": f"outside entry timing ({elapsed:.0%} of window elapsed)"}
    if mid_up is None:
        return {"skip": "no market mid price"}
    buf = M["basis_buffer_bps"] / 1e4
    model_up = fair_prob_digital(s_open, s_now, minutes_left, sigma)
    if abs(model_up - mid_up) > M["max_model_market_disagreement"]:
        return {"skip": f"model {model_up:.0%} vs market {mid_up:.0%}: too far apart, treated as model error", "model_up": model_up}
    w = M["market_anchor_weight"]
    q_up = (1 - w) * fair_prob_digital(s_open, s_now, minutes_left, sigma, +buf) + w * mid_up
    q_dn = (1 - w) * (1 - fair_prob_digital(s_open, s_now, minutes_left, sigma, -buf)) + w * (1 - mid_up)
    best = None
    for side, q in (("Up", q_up), ("Down", q_dn)):
        a = asks.get(side)
        if a is None or not (E["min_ask"] <= a <= E["max_ask"]):
            continue
        unit = a + taker_fee_per_share(a, rate)
        edge = q - unit
        if best is None or edge > best["edge"]:
            best = {"side": side, "q": q, "ask": a, "unit": unit, "edge": edge, "model_up": model_up, "mid_up": mid_up}
    if best is None:
        return {"skip": "no side priced between the allowed 30c-75c", "model_up": model_up}
    if best["edge"] < E["min_edge"]:
        return {"skip": f"best edge {best['edge']:+.3f} below {E['min_edge']}", **best}
    return best
