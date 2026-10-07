"""Test aggressive directional rules on settled Polymarket 15-minute BTC/ETH up/down markets (data from tools/mm_tape_collect.py
and tools/crypto_klines.py). One decision per market per rule, using only data before the decision time. Entry price = the next
taker-BUY print on the chosen outcome within 30 s (a price a buyer actually paid); fee = 7% * p * (1-p) per share.
Output is EV per share with standard errors, split into first/second half of the period. Research only."""
import json
import math
import statistics
import sys
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data" / "mm_tape"
FEE = 0.07


def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def load():
    markets = [json.loads(l) for l in (D / "markets.jsonl").read_text().splitlines() if l]
    markets.sort(key=lambda m: m["start"])
    kl = {s: {int(k): v for k, v in json.loads((D / f"klines_{s}USDT.json").read_text()).items()} for s in ("BTC", "ETH")}
    return markets, kl


def features(m, kl, elapsed):
    k = kl[m["asset"].upper()]
    t = m["start"] + elapsed
    s_open = k.get(m["start"], [None])[0]
    last = (t // 60) * 60 - 60
    if s_open is None or last not in k:
        return None
    s_now = k[last][1]
    closes = [k[x][1] for x in range(last - 3600, last + 1, 60) if x in k]
    if len(closes) < 61:
        return None
    rets = [math.log(closes[i + 1] / closes[i]) for i in range(60)]
    sigma = statistics.pstdev(rets) or 1e-9
    left = max((m["start"] + 900 - t) / 60, 0.5)
    r_open = math.log(s_now / s_open)
    z = r_open / (sigma * math.sqrt(left))
    r5 = math.log(s_now / k[last - 300][1]) if (last - 300) in k else 0.0
    return {"t": t, "z": z, "p_model": phi(z), "r5": r5, "sigma": sigma, "left": left}


def price_state(m, t):
    """Last Up-equivalent price before t (None if no trade yet)."""
    up = None
    for ts, side, out, price, size in m["trades"]:
        if ts >= t:
            break
        up = price if out == "Up" else 1 - price
    return up


def entry(m, t, outcome):
    for ts, side, out, price, size in m["trades"]:
        if t + 2 <= ts <= t + 30 and side == "BUY" and out == outcome:
            return price
    return None


def settle(m, outcome, px):
    fee = FEE * px * (1 - px)
    return (1.0 if m["winner"] == outcome else 0.0) - px - fee


def run(markets, kl, rule, elapsed):
    res = []
    for m in markets:
        f = features(m, kl, elapsed)
        if f is None:
            continue
        up = price_state(m, f["t"])
        if up is None:
            continue
        choice = rule(f, up)
        if choice is None:
            continue
        px = entry(m, f["t"], choice)
        if px is None:
            continue
        res.append({"start": m["start"], "ev": settle(m, choice, px), "win": m["winner"] == choice, "px": px})
    return res


def rules():
    def model(thr):
        def r(f, up):
            pu = f["p_model"]
            eu = pu - (up + 0.01) - FEE * (up + 0.01) * (0.99 - up)
            ed = (1 - pu) - ((1 - up) + 0.01) - FEE * ((1 - up) + 0.01) * (up - 0.01)
            if max(eu, ed) <= thr:
                return None
            return "Up" if eu >= ed else "Down"
        return r

    def mom(k):
        return lambda f, up: ("Up" if f["z"] > k else "Down") if abs(f["z"]) > k else None

    def fade(k):
        return lambda f, up: ("Down" if f["z"] > k else "Up") if abs(f["z"]) > k else None

    def fav(p):
        return lambda f, up: ("Up" if up >= p else "Down") if (up >= p or up <= 1 - p) else None

    def cheap(p):
        return lambda f, up: ("Up" if up <= p else "Down") if (up <= p or up >= 1 - p) else None

    def mom5(k):
        return lambda f, up: ("Up" if f["r5"] > 0 else "Down") if abs(f["r5"]) / (f["sigma"] * math.sqrt(5)) > k else None

    return {
        "model edge>0.00 (any price)": model(0.0), "model edge>0.04": model(0.04), "model edge>0.10": model(0.10),
        "follow open-move |z|>0.5": mom(0.5), "follow open-move |z|>1.0": mom(1.0), "follow open-move |z|>1.5": mom(1.5),
        "fade open-move |z|>1.0": fade(1.0), "fade open-move |z|>1.5": fade(1.5),
        "favorite >=0.80": fav(0.80), "favorite >=0.90": fav(0.90),
        "longshot <=0.15": cheap(0.15), "longshot <=0.25": cheap(0.25),
        "follow 5-min move |z|>1": mom5(1.0), "follow 5-min move |z|>2": mom5(2.0),
    }


def fmt(rs):
    if len(rs) < 20:
        return f"n={len(rs):4d} (too few)"
    ev = [r["ev"] for r in rs]
    se = statistics.pstdev(ev) / math.sqrt(len(ev))
    return f"n={len(rs):4d} win={sum(r['win'] for r in rs) / len(rs):5.1%} avg px={statistics.mean(r['px'] for r in rs):.2f} EV/sh={statistics.mean(ev):+.3f}±{se:.3f}"


def main():
    markets, kl = load()
    cut = markets[len(markets) // 2]["start"]
    print(len(markets), "markets;", "split at", cut)
    for elapsed in (240, 420, 600):
        print(f"\n=== decision at {elapsed // 60} min elapsed (of 15) ===")
        for name, rule in rules().items():
            rs = run(markets, kl, rule, elapsed)
            a = [r for r in rs if r["start"] < cut]
            b = [r for r in rs if r["start"] >= cut]
            print(f"{name:30s} ALL {fmt(rs)} | H1 {fmt(a)[-30:]} | H2 {fmt(b)[-30:]}")


if __name__ == "__main__":
    main()
