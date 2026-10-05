"""Honest backtest of published, rule-based ETF strategies on free Yahoo history (total-return adjusted closes).

Rules are taken from the literature as published and are NOT tuned here: monthly decisions on the last trading day,
executed at the NEXT trading day's close (no lookahead), 10 bp per side on traded notional. Output is for deciding what
to paper trade; it is not a forecast. Usage: python tools/trend_research.py"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

CACHE = Path(__file__).resolve().parent.parent / "data" / "etf_closes.csv"
TICKERS = ["SPY", "EFA", "EEM", "IEF", "TLT", "AGG", "GLD", "DBC", "VNQ", "SHY",
           "XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB"]
COST = 0.0010


def load():
    if CACHE.exists():
        return pd.read_csv(CACHE, index_col=0, parse_dates=True)
    raw = yf.download(TICKERS, start="2003-01-01", auto_adjust=True, progress=False)["Close"]
    raw = raw.dropna(how="all")
    raw.to_csv(CACHE)
    return raw


def month_ends(idx):
    s = pd.Series(idx, index=idx)
    return list(s.groupby([idx.year, idx.month]).last().values)


def backtest(px, weights_fn, start, warmup_days=260):
    """weights_fn(prices up to and including decision day) -> dict ticker->weight (sum<=1, rest cash=SHY)."""
    rets = px.pct_change().fillna(0.0)
    idx = px.index
    mes = [d for d in month_ends(idx) if d >= start]
    w = pd.Series(0.0, index=px.columns)
    w["SHY"] = 1.0
    eq, prev_eq = [], 1.0
    pending = None
    series, turn = [], 0.0
    me_set = set(mes)
    for i, d in enumerate(idx):
        if d < start:
            continue
        r = float((w * rets.loc[d]).sum())
        if pending is not None:
            # trade at today's close: pay cost on traded notional, new weights apply from tomorrow
            nw = pending
            t = float((nw - w).abs().sum())
            r -= COST * t
            turn += t
            w = nw
            pending = None
        prev_eq *= 1 + r
        series.append((d, prev_eq))
        if d in me_set and i >= warmup_days:
            tw = pd.Series(0.0, index=px.columns)
            for k, v in weights_fn(px.iloc[: i + 1]).items():
                tw[k] = v
            tw["SHY"] = max(0.0, 1.0 - tw.drop("SHY").sum())
            pending = tw
    eq = pd.Series(dict(series))
    return eq, turn / max(len(eq) / 252, 1e-9)


def stats(eq, label, turnover=None):
    r = eq.pct_change().dropna()
    yrs = len(r) / 252
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    vol = r.std() * math.sqrt(252)
    dd = (eq / eq.cummax() - 1).min()
    sharpe = r.mean() / r.std() * math.sqrt(252) if r.std() > 0 else float("nan")
    t = f" turnover/yr {turnover:4.1f}x" if turnover is not None else ""
    return f"{label:40s} CAGR {cagr:6.1%} vol {vol:5.1%} Sharpe {sharpe:4.2f} maxDD {dd:6.1%}{t}"


def ret_months(p, m):
    return p.iloc[-1] / p.iloc[-1 - m * 21] - 1


def sma_months(p, m):
    return p.iloc[-m * 21:].mean()


def faber(assets, m=10):
    def f(p):
        up = [a for a in assets if p[a].iloc[-1] > sma_months(p[a], m)]
        return {a: 1 / len(assets) for a in up}
    return f


def dual_momentum(lookback=12):
    def f(p):
        spy, efa, cash = ret_months(p["SPY"], lookback), ret_months(p["EFA"], lookback), ret_months(p["SHY"], lookback)
        if spy > cash:
            return {"SPY": 1.0} if spy >= efa else {"EFA": 1.0}
        return {"IEF": 1.0}
    return f


def sector_momentum(n=3, lookback=6, trend=10):
    secs = ["XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB"]

    def f(p):
        ranked = sorted(secs, key=lambda s: ret_months(p[s], lookback), reverse=True)[:n]
        return {s: 1 / n for s in ranked if p[s].iloc[-1] > sma_months(p[s], trend)}
    return f


def spy_trend(m=10):
    return lambda p: {"SPY": 1.0} if p["SPY"].iloc[-1] > sma_months(p["SPY"], m) else {}


def buy_hold(ticker):
    return lambda p: {ticker: 1.0}


def sixty_forty(p):
    return {"SPY": 0.6, "IEF": 0.4}


def main():
    px = load()
    start_all = pd.Timestamp("2007-03-01")
    px = px[[c for c in TICKERS if c in px.columns]].ffill()
    first_ok = px.dropna().index[0]
    print("data", px.index[0].date(), "->", px.index[-1].date(), "| all-asset history from", first_ok.date())
    start = max(start_all, first_ok + pd.Timedelta(days=380))
    mid = pd.Timestamp("2017-01-01")
    five = ["SPY", "EFA", "IEF", "GLD", "VNQ"]
    strategies = {
        "SPY buy & hold": buy_hold("SPY"),
        "60/40 SPY/IEF": sixty_forty,
        "Faber 5-asset 10m SMA (SPY EFA IEF GLD VNQ)": faber(five, 10),
        "Faber 5-asset 8m SMA": faber(five, 8),
        "Faber 5-asset 12m SMA": faber(five, 12),
        "SPY 10m SMA trend": spy_trend(10),
        "Dual momentum 12m (SPY/EFA/IEF)": dual_momentum(12),
        "Dual momentum 9m": dual_momentum(9),
        "Sector momentum top3/6m + 10m SMA": sector_momentum(3, 6, 10),
        "Sector momentum top3/12m + 10m SMA": sector_momentum(3, 12, 10),
    }
    results = {}
    for name, fn in strategies.items():
        eq, to = backtest(px, fn, start)
        results[name] = (eq, to)
    for label, a, b in (("FULL", start, px.index[-1]), ("FIRST HALF (to 2016)", start, mid - pd.Timedelta(days=1)),
                        ("SECOND HALF (2017+)", mid, px.index[-1])):
        print(f"\n== {label} ==")
        for name, (eq, to) in results.items():
            e = eq[(eq.index >= a) & (eq.index <= b)]
            if len(e) < 100:
                continue
            e = e / e.iloc[0]
            print(stats(e, name, to if label == "FULL" else None))


if __name__ == "__main__" and "--ensemble" not in sys.argv:
    main()


def faber_ensemble(assets, months=(8, 10, 12)):
    def f(p):
        w = {}
        for a in assets:
            frac = sum(p[a].iloc[-1] > sma_months(p[a], m) for m in months) / len(months)
            if frac > 0:
                w[a] = frac / len(assets)
        return w
    return f


def main_ensemble():
    px = load()
    px = px[[c for c in TICKERS if c in px.columns]].ffill()
    start = max(pd.Timestamp("2007-03-01"), px.dropna().index[0] + pd.Timedelta(days=380))
    mid = pd.Timestamp("2017-01-01")
    five = ["SPY", "EFA", "IEF", "GLD", "VNQ"]
    cands = {"SPY buy & hold": buy_hold("SPY"), "60/40 SPY/IEF": sixty_forty,
             "Faber ensemble 8/10/12m (5 assets)": faber_ensemble(five)}
    res = {n: backtest(px, fn, start) for n, fn in cands.items()}
    for label, a, b in (("FULL", start, px.index[-1]), ("FIRST HALF (to 2016)", start, mid - pd.Timedelta(days=1)),
                        ("SECOND HALF (2017+)", mid, px.index[-1]), ("2022 only", pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
                        ("2008 only", pd.Timestamp("2008-01-01"), pd.Timestamp("2008-12-31"))):
        print(f"\n== {label} ==")
        for n, (eq, to) in res.items():
            e = eq[(eq.index >= a) & (eq.index <= b)]
            if len(e) > 100:
                print(stats(e / e.iloc[0], n, to if label == "FULL" else None))
    cur = faber_ensemble(five)(px)
    print("\ncurrent target weights (as of", px.index[-1].date(), "):", {k: round(v, 3) for k, v in cur.items()}, "cash", round(1 - sum(cur.values()), 3))


if __name__ == "__main__" and "--ensemble" in sys.argv:
    main_ensemble()
