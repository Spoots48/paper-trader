"""Prediction-market book: pure pricing, edge and sizing logic for Polymarket crypto 'Up or Down' windows.

The market settles Up if Chainlink's time-weighted average price (TWAP) over the window is >= the price at
the window start. With a fraction e of the window elapsed, realized average A so far, current price S and r
minutes remaining, the final TWAP is e*A + (1-e)*F, where F is the average price over the rest of the window.
For a random walk, the average of the remaining path has standard deviation ~ S * sigma * sqrt(r/3).
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def phi(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def fair_prob_up(s0: float, avg_so_far: float, s_now: float, elapsed_frac: float, minutes_left: float,
                 sigma_per_min: float, threshold_shift: float = 0.0) -> float:
    """P(TWAP over the window >= s0 + threshold_shift)."""
    e = min(max(elapsed_frac, 0.0), 1.0)
    k = s0 + threshold_shift
    if e >= 1.0 or minutes_left <= 0:
        return 1.0 if avg_so_far >= k else 0.0
    k_rest = (k - e * avg_so_far) / (1 - e)  # what the rest of the window must average
    sd = s_now * sigma_per_min * math.sqrt(max(minutes_left, 1e-9) / 3.0)
    if sd <= 0:
        return 1.0 if s_now >= k_rest else 0.0
    return phi((s_now - k_rest) / sd)


def taker_fee_per_share(price: float, rate: float) -> float:
    return rate * price * (1 - price)


@dataclass
class Fill:
    shares: float
    cost: float  # USDC including fees
    avg_price: float  # before fees
    fees: float
    levels: int


def walk_book(asks: list[tuple[float, float]], prob: float, budget: float, min_edge: float, fee_rate: float) -> Fill | None:
    """Buy up to `budget` USDC from ascending asks, only at levels that still clear the edge threshold."""
    shares = cost = fees = notional = 0.0
    levels = 0
    for price, size in sorted(asks):
        unit = price + taker_fee_per_share(price, fee_rate)
        if prob - unit < min_edge or budget - cost < unit:
            break
        take = min(size, (budget - cost) / unit)
        take = math.floor(take * 100) / 100  # shares in hundredths
        if take <= 0:
            break
        shares += take
        cost += take * unit
        fees += take * taker_fee_per_share(price, fee_rate)
        notional += take * price
        levels += 1
    if shares <= 0:
        return None
    return Fill(shares, cost, notional / shares, fees, levels)


def kelly_budget(prob: float, unit_cost: float, equity: float, cfg: dict, open_exposure: float) -> float:
    S = cfg["sizing"]
    if unit_cost >= 1 or prob <= unit_cost:
        return 0.0
    f = S["kelly_fraction"] * (prob - unit_cost) / (1 - unit_cost)
    f = min(f, S["max_per_market"])
    room = max(0.0, S["max_open_exposure"] * equity - open_exposure)
    return max(0.0, min(f * equity, room))


def decide_market(m: dict, px: dict, cfg: dict) -> dict:
    """m: market info with books; px: price context. Returns a decision dict (never places anything itself)."""
    M = cfg["model"]
    buf = px["s0"] * M["basis_buffer_bps"] / 1e4
    args = (px["s0"], px["avg"], px["s_now"], px["elapsed"], px["minutes_left"], px["sigma"])
    p_up_cons = fair_prob_up(*args, threshold_shift=+buf)  # harder for Up
    p_dn_cons = 1 - fair_prob_up(*args, threshold_shift=-buf)  # harder for Down
    p_mid = fair_prob_up(*args)
    cap = M["probability_cap"]
    sides = {"Up": min(p_up_cons, cap), "Down": min(p_dn_cons, cap)}
    rate = cfg["fees"]["crypto_taker_fee_rate"]
    best = None
    for side, q in sides.items():
        asks = m["asks"].get(side) or []
        if not asks:
            continue
        a = min(p for p, _ in asks)
        unit = a + taker_fee_per_share(a, rate)
        edge = q - unit
        cand = {"side": side, "prob": q, "best_ask": a, "unit_cost": unit, "edge": edge}
        if best is None or edge > best["edge"]:
            best = cand
    return {"p_up_model": p_mid, "p_up_conservative": p_up_cons, "p_down_conservative": p_dn_cons, "best": best}
