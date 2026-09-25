"""Market-maker book: pure quoting and fill-simulation logic (paper only)."""
from __future__ import annotations

import math


def quote_prices(best_bid_up: float | None, best_ask_up: float | None, best_bid_dn: float | None, best_ask_dn: float | None,
                 cfg: dict) -> dict | None:
    """Bid prices for Up and Down, or None if there's no room for a profitable pair."""
    Q = cfg["quoting"]
    if best_bid_up is None or best_bid_dn is None:
        return None
    t = Q["tick"]
    pu, pd = best_bid_up, best_bid_dn
    if pu + pd <= Q["max_combined_bid"] - t + 1e-9:  # room to improve both by a tick
        if best_ask_up is None or pu + t < best_ask_up - 1e-9:
            pu = round(pu + t, 3)
        if best_ask_dn is None or pd + t < best_ask_dn - 1e-9:
            pd = round(pd + t, 3)
    if pu + pd > Q["max_combined_bid"] + 1e-9 or pu <= 0 or pd <= 0:
        return None
    return {"Up": pu, "Down": pd, "improved": {"Up": pu > best_bid_up, "Down": pd > best_bid_dn}}


def simulate_fill(order: dict, trades: list[dict]) -> float:
    """Shares filled for a resting bid, from taker trades after it was placed and before it expired.

    order: {outcome, price, shares, queue_ahead, placed_at, expires_at}
    trades: [{timestamp, side (taker), outcome, price, size}]
    """
    o, p = order["outcome"], order["price"]
    vol, swept = 0.0, False
    for tr in trades:
        ts = tr["timestamp"]
        if not (order["placed_at"] < ts <= order["expires_at"]):
            continue
        tp, sz = float(tr["price"]), float(tr["size"])
        if tr["outcome"] == o and tr["side"] == "SELL" and tp <= p + 1e-9:
            vol += sz
            swept |= tp < p - 1e-9
        elif tr["outcome"] != o and tr["side"] == "BUY" and tp >= 1 - p - 1e-9:
            vol += sz
            swept |= tp > 1 - p + 1e-9
    if swept:
        return order["shares"]
    filled = max(0.0, vol - order["queue_ahead"])
    return math.floor(min(filled, order["shares"]) * 100) / 100
