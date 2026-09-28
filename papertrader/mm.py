"""Market-maker book: pure quoting and fill-simulation logic (paper only)."""
from __future__ import annotations

import math


def quote_prices(best_bid_up: float | None, best_ask_up: float | None, best_bid_dn: float | None, best_ask_dn: float | None,
                 cfg: dict) -> dict | None:
    """Bid prices for Up and Down, or None if there's no room for a profitable pair."""
    Q = cfg["quoting"]
    values = (best_bid_up, best_ask_up, best_bid_dn, best_ask_dn)
    if any(x is None or not math.isfinite(x) or not 0 < x < 1 for x in values):
        return None
    if best_bid_up >= best_ask_up or best_bid_dn >= best_ask_dn:
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
    vol, through = 0.0, 0.0
    for tr in trades:
        ts = tr["timestamp"]
        if not (order["placed_at"] < ts <= order["expires_at"]):
            continue
        tp, sz = float(tr["price"]), float(tr["size"])
        if tr["outcome"] == o and tr["side"] == "SELL" and tp <= p + 1e-9:
            if tp < p - 1e-9:
                through += sz
            else:
                vol += sz
        elif tr["outcome"] != o and tr["side"] == "BUY" and tp >= 1 - p - 1e-9:
            if tp > 1 - p + 1e-9:
                through += sz
            else:
                vol += sz
    filled = through + max(0.0, vol - order["queue_ahead"])
    return math.floor(min(filled, order["shares"]) * 100) / 100


def plan_quotes(slug: str, prices: dict, positions: dict, orders: list, cash: float,
                equity: float, floor: float, cfg: dict) -> dict[str, float]:
    """Size the whole quote batch before posting either side; never round up to a minimum."""
    from .pm_risk import settlement_floor
    S = cfg['sizing']
    active = {p['slug'] for p in positions.values()} | {o['slug'] for o in orders}
    if slug not in active and len(active) >= S.get('max_open_markets', 1):
        return {}
    owned = {p['side']: p for p in positions.values() if p['slug'] == slug}
    up, down = (owned.get(s, {}).get('shares', 0) for s in ('Up', 'Down'))
    sides = ['Up', 'Down']
    limit = S['per_pair_fraction'] * equity / (prices['Up'] + prices['Down'])
    if abs(up - down) > .005:
        held, missing = ('Up', 'Down') if up > down else ('Down', 'Up')
        if owned[held]['cost'] / owned[held]['shares'] + prices[missing] > cfg['quoting']['max_combined_bid'] + 1e-9:
            return {}
        sides, limit = [missing], min(limit, abs(up - down))
    elif up > 0:
        return {}  # one completed pair batch per market
    reserved = sum(o['price'] * o['shares'] for o in orders)
    invested = sum(p['cost'] for p in positions.values())
    unit = sum(prices[s] for s in sides)
    limit = min(limit, (cash - reserved) / unit,
                (S['max_reserved_fraction'] * equity - reserved) / unit,
                (S.get('max_open_exposure', .10) * equity - invested - reserved) / unit)
    local = {k: p for k, p in positions.items() if p['slug'] == slug}
    local_cost = sum(p['cost'] for p in local.values())

    def admissible(q):
        trial = orders + [dict(slug=slug, outcome=s, shares=q, price=prices[s]) for s in sides]
        worst = settlement_floor(cash, positions, trial)
        market_loss = -settlement_floor(-local_cost, local, [o for o in trial if o['slug'] == slug])
        return worst >= floor - 1e-9 and market_loss <= S.get('max_market_loss_fraction', .03) * equity + 1e-9

    # Monotone: in the worst case only losing quotes fill. Binary search in cents
    # of shares preserves the platform minimum without inflating the risk budget.
    lo, hi = 0, max(0, math.floor(limit * 100))
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if admissible(mid / 100):
            lo = mid
        else:
            hi = mid - 1
    shares = lo / 100
    return {s: shares for s in sides} if shares >= cfg['portfolio']['min_shares'] and admissible(shares) else {}
