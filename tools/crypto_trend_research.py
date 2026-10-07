"""Daily trend-following on BTC and ETH, optionally leveraged, on Binance daily history (public). Rules are standard and NOT tuned:
long when close > N-day SMA (N in 50, 100, 200) else cash; leverage L in 1, 2, 3 (daily rebalanced). Costs: 10 bp per side on position
change; perp-style funding 0.03%/day on leveraged notional while long; liquidation if the day's low is below entry-of-day close by
(1/L - 0.5%). Signal on day t close, position held over day t+1 (no lookahead)."""
import json, math, sys, time
from pathlib import Path
import requests
import numpy as np
import pandas as pd

C = Path(__file__).resolve().parent.parent / "data" / "crypto_daily.json"


def fetch(sym):
    out, t = [], int(pd.Timestamp("2017-09-01").timestamp() * 1000)
    while True:
        r = requests.get("https://data-api.binance.vision/api/v3/klines", params={"symbol": sym, "interval": "1d", "startTime": t, "limit": 1000}, timeout=30)
        k = r.json()
        if not k: break
        out += [[row[0], float(row[1]), float(row[2]), float(row[3]), float(row[4])] for row in k]
        t = k[-1][0] + 86400000
        if len(k) < 1000: break
    return out


def load():
    if not C.exists():
        C.write_text(json.dumps({s: fetch(s) for s in ("BTCUSDT", "ETHUSDT")}))
    d = json.loads(C.read_text())
    return {s: pd.DataFrame(v, columns=["t", "o", "h", "l", "c"]).assign(date=lambda x: pd.to_datetime(x.t, unit="ms")).set_index("date") for s, v in d.items()}


def backtest(df, n, lev, cost=0.0010, funding=0.0003):
    c, lo = df.c.values, df.l.values
    sma = pd.Series(c).rolling(n).mean().values
    eq, pos, out = 1.0, 0.0, []
    liq = 0
    for i in range(len(c)):
        if i >= n and i + 1 < len(c):
            sig = 1.0 if c[i] > sma[i] else 0.0
        else:
            sig = 0.0
        new = sig * lev
        # held over day i+1 with exposure `new` set at close i
        if i + 1 < len(c):
            eq *= 1 - cost * abs(new - pos)
            pos = new
            if pos > 0:
                r = c[i + 1] / c[i] - 1
                worst = lo[i + 1] / c[i] - 1
                if lev > 1 and worst <= -(1 / lev - 0.005):
                    eq *= 0.0
                    liq += 1
                    pos = 0.0
                else:
                    eq *= 1 + pos * r - funding * pos * (lev > 1)
        out.append(eq)
    return pd.Series(out, index=df.index), liq


def stats(eq, label):
    r = eq.pct_change().dropna()
    yrs = len(r) / 365
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1.0
    dd = (eq / eq.cummax() - 1).min()
    sh = r.mean() / r.std() * math.sqrt(365) if r.std() > 0 else float("nan")
    return f"{label:34s} final x{eq.iloc[-1]:7.2f}  CAGR {cagr:7.1%}  Sharpe {sh:4.2f}  maxDD {dd:7.1%}"


def main():
    data = load()
    mid = pd.Timestamp("2022-01-01")
    for sym, df in data.items():
        print(f"\n######## {sym}  {df.index[0].date()} -> {df.index[-1].date()}")
        bh = (df.c / df.c.iloc[0])
        for label, a, b in (("FULL", df.index[0], df.index[-1]), ("2017-2021", df.index[0], mid - pd.Timedelta(days=1)), ("2022-2026", mid, df.index[-1])):
            print(f"== {label} ==")
            sub = bh[(bh.index >= a) & (bh.index <= b)]
            print(stats(sub / sub.iloc[0], "buy & hold 1x"))
            for n in (50, 100, 200):
                for lev in (1, 2, 3):
                    eq, liq = backtest(df, n, lev)
                    e = eq[(eq.index >= a) & (eq.index <= b)]
                    print(stats(e / e.iloc[0], f"trend SMA{n} {lev}x") + (f"  liquidations {liq}" if lev > 1 and label == "FULL" else ""))


if __name__ == "__main__":
    main()
