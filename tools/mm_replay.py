"""Offline replay of the market maker's quoting rule against the public taker tape (see tools/mm_tape_collect.py).

Approximations, all stated up front: the live book is unknown historically, so each side's midpoint is taken from the last
trade before the quote time; fills use the same rule as papertrader.mm.simulate_fill with an assumed queue ahead; maker fees
and rebates are ignored (rebates were ~0.4 on 380 live events). This measures adverse selection, not a tradable P&L."""
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from papertrader.mm import simulate_fill

FILE = Path(__file__).resolve().parent.parent / "data" / "mm_tape" / "markets.jsonl"
SHARES = 10.0
LIFETIME = 300


def last_prices(trades, t):
    """Per-outcome last trade price strictly before t, or None."""
    p = {}
    for ts, side, out, price, size in trades:
        if ts >= t:
            break
        p[out] = price
    return p


def mids(trades, t):
    p = last_prices(trades, t)
    if "Up" in p and "Down" in p:
        up = (p["Up"] + (1 - p["Down"])) / 2
    elif "Up" in p:
        up = p["Up"]
    elif "Down" in p:
        up = 1 - p["Down"]
    else:
        return None
    return up, 1 - up


def bids(mid_up, mid_dn, dist=0.005, cap=0.98):
    u = math.floor((mid_up - dist) * 100 + 1e-9) / 100
    d = math.floor((mid_dn - dist) * 100 + 1e-9) / 100
    while u + d > cap + 1e-9:
        if u >= d:
            u = round(u - 0.01, 2)
        else:
            d = round(d - 0.01, 2)
    return u, d


def run_market(m, offset, queue, band=None, dist=0.005):
    tr = [{"timestamp": ts, "side": s, "outcome": o, "price": p, "size": z} for ts, s, o, p, z in m["trades"]]
    t = m["start"] + offset
    mm = mids(m["trades"], t)
    if mm is None:
        return None
    if band is not None and abs(mm[0] - 0.5) > band:
        return None
    u, d = bids(*mm, dist=dist)
    if u < 0.02 or d < 0.02:
        return None
    got = {}
    for out, px in (("Up", u), ("Down", d)):
        o = {"outcome": out, "price": px, "shares": SHARES, "queue_ahead": queue, "placed_at": t, "expires_at": t + LIFETIME}
        got[out] = (simulate_fill(o, tr), px)
    cost = sum(q * px for q, px in got.values())
    n_pair = min(got["Up"][0], got["Down"][0])
    win = m["winner"]
    pay = got[win][0] * 1.0
    legs = sum(1 for q, _ in got.values() if q > 0)
    return {"legs": legs, "cost": cost, "pnl": pay - cost, "start": m["start"], "pair": n_pair > 0}


def summarize(rs, label):
    f = [r for r in rs if r["legs"] > 0]
    if not f:
        print(f"{label:34s} no fills")
        return
    two = [r for r in f if r["legs"] == 2]
    one = [r for r in f if r["legs"] == 1]
    winr = sum(r["pnl"] > 0 for r in one) / len(one) if one else float("nan")
    per = [r["pnl"] for r in f]
    print(f"{label:34s} quotes={len(rs):5d} filled={len(f):4d} pairs={len(two):4d} one-sided={len(one):4d} "
          f"P(win|one)={winr:5.1%} EV/filled={statistics.mean(per):+.3f} (se {statistics.pstdev(per) / math.sqrt(len(per)):.3f}) "
          f"total={sum(per):+.1f} pair-EV={statistics.mean([r['pnl'] for r in two]) if two else float('nan'):+.3f} "
          f"one-EV={statistics.mean([r['pnl'] for r in one]) if one else float('nan'):+.3f}")


def main():
    markets = [json.loads(l) for l in FILE.read_text().splitlines() if l]
    markets.sort(key=lambda m: m["start"])
    print(len(markets), "markets;", len({m["asset"] for m in markets}), "assets")
    cut = markets[len(markets) // 2]["start"]
    for queue in (0.0, 50.0):
        print(f"\n=== assumed queue ahead = {queue:.0f} shares ===")
        for offset in (60, 180, 300):
            for band, name in ((None, "all markets"), (0.10, "balanced only |mid-.5|<=.10")):
                rs = [r for m in markets if (r := run_market(m, offset, queue, band))]
                summarize(rs, f"t+{offset:3d}s {name}")
        rs = [r for m in markets if (r := run_market(m, 180, queue))]
        summarize([r for r in rs if r["start"] < cut], "t+180 all, FIRST half")
        summarize([r for r in rs if r["start"] >= cut], "t+180 all, SECOND half")




def first_fill_study(markets, offset=180, delay=10, band=None):
    """Lookahead-free: at the moment the FIRST bid would fill, what is that leg worth at settlement, and what would buying the
    opposite outcome at the next executable (taker-buy) print after `delay` seconds have paid? Taker fee 7% * p * (1-p)."""
    rows = []
    for m in markets:
        t0 = m["start"] + offset
        mm = mids(m["trades"], t0)
        if mm is None or (band is not None and abs(mm[0] - 0.5) > band):
            continue
        u, d = bids(*mm)
        bid = {"Up": u, "Down": d}
        first = None
        for ts, side, out, price, size in m["trades"]:
            if not (t0 < ts <= t0 + LIFETIME):
                continue
            for o in ("Up", "Down"):
                other = "Down" if o == "Up" else "Up"
                if (out == o and side == "SELL" and price <= bid[o] + 1e-9) or (out == other and side == "BUY" and price >= 1 - bid[o] - 1e-9):
                    first = (ts, o)
                    break
            if first:
                break
        if not first:
            continue
        t1, x = first
        opp = "Down" if x == "Up" else "Up"
        q = next((p for ts, s, o, p, z in m["trades"] if ts >= t1 + delay and o == opp and s == "BUY" and ts <= m["start"] + 840), None)
        win = m["winner"]
        hold = (1.0 if win == x else 0.0) - bid[x]
        row = {"start": m["start"], "x_wins": win == x, "hold": hold, "bid": bid[x]}
        if q is not None:
            fee = 0.07 * q * (1 - q)
            row["opp_ev"] = (1.0 if win == opp else 0.0) - q - fee
            row["opp_price"] = q
        rows.append(row)
    return rows


def report_first_fill(rows, label):
    if not rows:
        print(label, "no events")
        return
    n = len(rows)
    w = sum(r["x_wins"] for r in rows) / n
    h = [r["hold"] for r in rows]
    op = [r["opp_ev"] for r in rows if "opp_ev" in r]
    se = lambda xs: statistics.pstdev(xs) / math.sqrt(len(xs))
    print(f"{label:30s} n={n:4d} P(first-fill leg wins)={w:5.1%} hold EV/sh={statistics.mean(h):+.3f}±{se(h):.3f}"
          + (f" | buy-opposite n={len(op)} EV/sh={statistics.mean(op):+.3f}±{se(op):.3f} avg px {statistics.mean([r['opp_price'] for r in rows if 'opp_price' in r]):.2f}" if op else ""))


def main2():
    markets = [json.loads(l) for l in FILE.read_text().splitlines() if l]
    markets.sort(key=lambda m: m["start"])
    cut = markets[len(markets) // 2]["start"]
    print(len(markets), "markets (first-fill study)")
    for offset in (60, 180, 300):
        for delay in (10, 30):
            rows = first_fill_study(markets, offset, delay)
            report_first_fill(rows, f"t+{offset} delay {delay}s ALL")
            report_first_fill([r for r in rows if r["start"] < cut], f"t+{offset} delay {delay}s 1st half")
            report_first_fill([r for r in rows if r["start"] >= cut], f"t+{offset} delay {delay}s 2nd half")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    (main2 if "--first-fill" in sys.argv else main)()
