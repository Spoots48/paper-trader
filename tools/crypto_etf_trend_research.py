"""Backtest of the deployable design: hold IBIT/ETHA (crypto ETFs) at 50% each in proportion to how many of the 50/100/200-SESSION
SMAs their signal series is above; rest in SHY. Signals for the long history use BTC-USD/ETH-USD sampled on NYSE session dates; trades
at the next session close after the decision, 7 bp per side. Rebalance daily, weekly or monthly. Research only."""
import math
import numpy as np
import pandas as pd
import yfinance as yf

px = yf.download(["BTC-USD", "ETH-USD", "SPY", "SHY", "IBIT", "ETHA"], start="2017-09-01", auto_adjust=True, progress=False)["Close"]
sess = px["SPY"].dropna().index
sig = px[["BTC-USD", "ETH-USD"]].reindex(sess).ffill()
sess = sig.dropna().index
sig = sig.loc[sess]
shy = px["SHY"].reindex(sess).ffill()
spy = px["SPY"].reindex(sess)
rets = pd.DataFrame({"B": sig["BTC-USD"].pct_change(), "E": sig["ETH-USD"].pct_change(), "S": shy.pct_change()}).fillna(0)
WINS = (50, 100, 200)


def run(freq, cost=0.0007, wins=WINS):
    n = len(sess)
    w = np.array([0.0, 0.0, 1.0])  # B, E, S
    eq = [1.0]
    pending = None
    for i in range(1, n):
        r = float((w * rets.iloc[i].values).sum())
        if pending is not None:
            r -= cost * float(np.abs(pending - w).sum())
            w, pending = pending, None
        eq.append(eq[-1] * (1 + r))
        d = sess[i]
        if i >= max(wins) + 1 and i + 1 < n:
            nxt = sess[i + 1]
            do = freq == "daily" or (freq == "weekly" and nxt.isocalendar()[1] != d.isocalendar()[1]) or (freq == "monthly" and nxt.month != d.month)
            if do:
                tw = []
                for col in ("BTC-USD", "ETH-USD"):
                    s = sig[col].iloc[: i + 1]
                    frac = sum(s.iloc[-1] > s.iloc[-m:].mean() for m in wins) / len(wins)
                    tw.append(0.5 * frac)
                pending = np.array([tw[0], tw[1], 1 - tw[0] - tw[1]])
    return pd.Series(eq, index=sess)


def stats(e, label):
    r = e.pct_change().dropna()
    y = len(r) / 252
    return f"{label:44s} CAGR {e.iloc[-1] ** (1 / y) - 1:7.1%} vol {r.std() * math.sqrt(252):6.1%} Sharpe {r.mean() / r.std() * math.sqrt(252):4.2f} maxDD {(e / e.cummax() - 1).min():7.1%} final x{e.iloc[-1]:.2f}"


mid = pd.Timestamp("2022-01-01")
bh = (0.5 * sig["BTC-USD"] / sig["BTC-USD"].iloc[0] + 0.5 * sig["ETH-USD"] / sig["ETH-USD"].iloc[0])
res = {f: run(f) for f in ("daily", "weekly", "monthly")}
for label, a, b in (("FULL (2018-)", sess[0], sess[-1]), ("2018-2021", sess[0], mid - pd.Timedelta(days=1)), ("2022-2026 (out of sample)", mid, sess[-1])):
    print(f"\n== {label} ==")
    x = bh[(bh.index >= a) & (bh.index <= b)]
    print(stats(x / x.iloc[0], "50/50 BTC+ETH buy & hold (monthly drift)"))
    for f, e in res.items():
        y = e[(e.index >= a) & (e.index <= b)]
        print(stats(y / y.iloc[0], f"crypto trend ensemble, {f} rebalance"))
print("\ncurrent signal weights:", {c: round(0.5 * sum(sig[c].iloc[-1] > sig[c].iloc[-m:].mean() for m in WINS) / 3, 3) for c in ("BTC-USD", "ETH-USD")})
print("IBIT history:", px["IBIT"].dropna().index[0].date(), "ETHA history:", px["ETHA"].dropna().index[0].date(), "last", px["IBIT"].dropna().index[-1].date())
