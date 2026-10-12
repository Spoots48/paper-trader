"""Pre-declared screen of published intraday rule families on 60 days of free 5-minute bars (equities).
Every variant is listed in VARIANTS before any result is seen; all are reported, none dropped. Costs: COST per side.
A variant 'passes' only if the day-clustered t-stat is >= 3.0 net of costs AND the net mean is positive in BOTH date halves.
(With ~30 variants, t >= 3 keeps the family-wise false-positive chance low; with ~45 test days this is a screen, not proof.)"""
import json, sys, itertools, numpy as np, pandas as pd, yfinance as yf
cfg = json.load(open("config/strategy_speed_v1.json"))
TICK = sorted(set(cfg["universe"]["tickers"]) | {"QQQ", "IWM", "DIA"})
COST = float(sys.argv[1]) if len(sys.argv) > 1 else 3e-4          # per side, fraction of price
df = yf.download(TICK, period="60d", interval="5m", auto_adjust=False, progress=False, group_by="ticker")
days = {}                                                          # (ticker, date) -> arrays
for t in TICK:
    b = df[t].dropna(); b.index = b.index.tz_convert("America/New_York")
    b = b[(b.index.time >= pd.Timestamp("09:30").time()) & (b.index.time <= pd.Timestamp("15:55").time())]
    for d, g in b.groupby(b.index.date):
        if len(g) >= 76: days[(t, d)] = tuple(g[k].values for k in ("Open", "High", "Low", "Close", "Volume"))
dates = sorted({d for _, d in days}); WARM = 15
test_dates = dates[WARM:]; half = test_dates[len(test_dates) // 2]
def hist(t, i, k):  # previous WARM days' value of k(day arrays)
    return [k(days[(t, d)]) for d in dates[max(0, i - WARM):i] if (t, d) in days]
def atr(t, i):
    prev = [(days[(t, d)][1].max() - days[(t, d)][2].min()) for d in dates[max(0, i - 14):i] if (t, d) in days]
    return np.mean(prev) if len(prev) >= 10 else None
def sim(day, e, side, stop=None, tp=None, hold=None):
    """fill at open[e]; exits checked bar by bar (stop first on ambiguous bars); flat at the last bar. returns net fractional return."""
    o, h, l, c, v = day; px = o[e]; last = len(c) - 1 if hold is None else min(len(c) - 1, e + hold - 1)
    for j in range(e, last + 1):
        if side > 0:
            if stop is not None and l[j] <= stop: x = min(stop, o[j]); return side * (x / px - 1) - 2 * COST - 2e-4
            if tp is not None and h[j] >= tp: return side * (tp / px - 1) - 2 * COST
        else:
            if stop is not None and h[j] >= stop: x = max(stop, o[j]); return side * (x / px - 1) - 2 * COST - 2e-4
            if tp is not None and l[j] <= tp: return side * (tp / px - 1) - 2 * COST
    return side * (c[last] / px - 1) - 2 * COST
VARIANTS = []
for n, stopk, filt, sides in itertools.product((1, 3, 6), ("range", "atr10"), ("all", "rvol1.5"), ("both", "long")):
    VARIANTS.append(("ORB", n, stopk, filt, sides))
for z, hold in itertools.product((2.0, 3.0), (6, 12)):
    for kind in ("vwap_revert", "vwap_follow"): VARIANTS.append((kind, z, hold))
for k, hold in itertools.product((3.0, 5.0), (6, 12)):
    for kind in ("spike_follow", "spike_revert"): VARIANTS.append((kind, k, hold))
VARIANTS.append(("first_last", "SPY/QQQ/IWM/DIA"))
res = {v: [] for v in VARIANTS}                                      # variant -> [(date, net)]
for t in TICK:
    for i, d in enumerate(dates):
        if d not in test_dates or (t, d) not in days: continue
        day = days[(t, d)]; o, h, l, c, v = day; A = atr(t, i)
        if A is None: continue
        for var in VARIANTS:
            if var[0] == "ORB":
                _, n, stopk, filt, sides = var
                rv_hist = hist(t, i, lambda x, n=n: x[4][:n].sum())
                if filt != "all" and (len(rv_hist) < 10 or v[:n].sum() < 1.5 * np.mean(rv_hist)): continue
                side = 1 if c[n - 1] > o[0] else -1 if c[n - 1] < o[0] else 0
                if side == 0 or (sides == "long" and side < 0): continue
                hi, lo = h[:n].max(), l[:n].min(); px = o[n]
                stop = (lo if side > 0 else hi) if stopk == "range" else (px - 0.1 * A if side > 0 else px + 0.1 * A)
                if (side > 0 and stop >= px) or (side < 0 and stop <= px): continue
                res[var].append((d, sim(day, n, side, stop=stop)))
            elif var[0] in ("vwap_revert", "vwap_follow"):
                _, z, hold = var; tp_ = (c * v).cumsum() / np.maximum(v.cumsum(), 1)
                dev = (c - tp_); sd = pd.Series(dev).rolling(20).std().values
                for j in range(20, len(c) - hold - 2, 12):               # at most every hour per name/day: no overlapping trades
                    if sd[j] and abs(dev[j]) >= z * sd[j]:
                        side = (-1 if dev[j] > 0 else 1) * (1 if var[0] == "vwap_revert" else -1)
                        res[var].append((d, sim(day, j + 1, side, hold=hold)))
            elif var[0] in ("spike_follow", "spike_revert"):
                _, k, hold = var; ma = pd.Series(v).rolling(20).mean().shift(1).values
                for j in range(20, len(c) - hold - 2, 12):
                    r = c[j] / o[j] - 1
                    if ma[j] and v[j] >= k * ma[j] and abs(r) >= 0.0015:
                        side = (1 if r > 0 else -1) * (1 if var[0] == "spike_follow" else -1)
                        res[var].append((d, sim(day, j + 1, side, hold=hold)))
    # first-half-hour -> last-half-hour (ETFs only), needs previous close
for t in ("SPY", "QQQ", "IWM", "DIA"):
    for i, d in enumerate(dates):
        if d not in test_dates or (t, d) not in days or i == 0 or (t, dates[i - 1]) not in days: continue
        o, h, l, c, v = days[(t, d)]; prev_close = days[(t, dates[i - 1])][3][-1]
        r1 = c[5] / prev_close - 1                                       # prev close -> 10:00
        if abs(r1) < 1e-4: continue
        res[("first_last", "SPY/QQQ/IWM/DIA")].append((d, sim(days[(t, d)], len(c) - 6, 1 if r1 > 0 else -1)))
def stats(rows):
    if len(rows) < 30: return None
    by = {}; [by.setdefault(d, []).append(x) for d, x in rows]
    dm = np.array([np.mean(v) for v in by.values()]); t = dm.mean() / (dm.std(ddof=1) / np.sqrt(len(dm)) + 1e-12)
    a = [x for d, x in rows if d < half]; b = [x for d, x in rows if d >= half]
    return len(rows), np.mean([x for _, x in rows]) * 1e4, t, np.mean(a) * 1e4 if a else float("nan"), np.mean(b) * 1e4 if b else float("nan")
print(f"cost/side={COST*1e4:.1f}bp  test days={len(test_dates)} ({test_dates[0]}..{test_dates[-1]}) split at {half}  variants={len(VARIANTS)}")
print(f"{'variant':58s} {'n':>6s} {'net bp/trade':>12s} {'t(day)':>7s} {'1st half':>9s} {'2nd half':>9s}  pass")
npass = 0
for var in VARIANTS:
    s = stats(res[var])
    if s is None: print(f"{str(var):58s} too few trades ({len(res[var])})"); continue
    ok = s[2] >= 3.0 and s[3] > 0 and s[4] > 0; npass += ok
    print(f"{str(var):58s} {s[0]:6d} {s[1]:12.1f} {s[2]:7.2f} {s[3]:9.1f} {s[4]:9.1f}  {'PASS' if ok else '-'}")
print("variants passing the pre-declared bar:", npass)
