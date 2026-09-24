"""Research only: backtest the day-trading book on Yahoo's ~60 sessions of 5-minute history.

Usage: python -m papertrader.backtest_intraday <data_dir with bars_5m.pkl and daily_6mo.pkl>
Uses exactly the same selection and bar-processing code as the live engine (papertrader/intraday.py).
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .config import RESEARCH_DIR, load_json, ROOT
from .intraday import DayState, process_bar, select_candidates
from .nyse_calendar import ET, session_close


def daily_metrics(daily: pd.DataFrame, tickers: list[str], before: dt.date, cfg: dict) -> dict[str, dict]:
    n = cfg["universe"]["atr_days"]
    out = {}
    for t in tickers:
        if t not in daily.columns.get_level_values(0):
            continue
        d = daily[t].dropna(subset=["Close"])
        d = d[d.index.date < before].tail(30)
        if len(d) < n + 1:
            continue
        pc = d["Close"].shift(1)
        tr = pd.concat([d["High"] - d["Low"], (d["High"] - pc).abs(), (d["Low"] - pc).abs()], axis=1).max(axis=1)
        out[t] = {"atr": float(tr.tail(n).mean()), "avg_vol": float(d["Volume"].tail(cfg["universe"]["avg_volume_days"]).mean()),
                  "adv_usd": float((d["Close"] * d["Volume"]).tail(20).mean()), "prev_close": float(d["Close"].iloc[-1])}
    return out


def run(data_dir: Path, exec_minutes: int = 5) -> dict:
    cfg = load_json(ROOT / "config" / "strategy_daytrade_v1.json")
    bars = pd.read_pickle(data_dir / "bars_5m.pkl")  # selection (opening range, relative volume) always uses 5-minute bars
    daily = pd.read_pickle(data_dir / "daily_6mo.pkl")
    bars["session"] = bars["ts"].dt.date
    bars["bt"] = bars["ts"].dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    sessions = sorted(bars.loc[bars.ticker == "SPY", "session"].unique())
    first = bars[bars["ts"].dt.strftime("%H:%M") == "09:30"].set_index(["session", "ticker"])
    lookback = cfg["selection"]["relative_volume_lookback_sessions"]
    stocks = sorted(set(bars.ticker) - {"SPY"})
    cash, curve, trades, days = cfg["portfolio"]["starting_cash"], {}, [], []
    peak, pause_left, halted = cash, 0, False
    if exec_minutes == 1:  # execution on 1-minute bars (the paper's resolution); only ~30 days exist
        ex = pd.read_pickle(data_dir / "bars_1m.pkl")
        ex["session"] = ex["ts"].dt.date
        ex["bt"] = ex["ts"].dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        by_session = {s: g for s, g in ex.groupby("session")}
    else:
        by_session = {s: g for s, g in bars.groupby("session")}
    for i, S in enumerate(sessions):
        if i < lookback or S not in by_session:
            continue
        hist_sessions = sessions[i - lookback:i]
        fb = {}
        for t in stocks:
            k = (S, t)
            if k in first.index:
                r = first.loc[k]
                fb[t] = (float(r.Open), float(r.High), float(r.Low), float(r.Close), float(r.Volume))
        hist = {}
        for t in fb:
            hist[t] = [float(first.loc[(s, t)].Volume) for s in hist_sessions if (s, t) in first.index]
        dm = daily_metrics(daily, list(fb), S, cfg)
        cands, _ = select_candidates(fb, hist, dm, cfg)
        st = DayState(session=S.isoformat(), cash_at_open=cash, cash=cash, candidates=[c.__dict__ for c in cands],
                      pending=[c.ticker for c in cands])
        g = by_session[S]
        close_t = session_close(S)
        last_start = (close_t - dt.timedelta(minutes=exec_minutes)).strftime("%H:%M")
        entry_cut = (close_t - dt.timedelta(minutes=cfg["entry"]["last_entry_bar_minutes_before_close"])).strftime("%H:%M")
        tick = set(st.pending)
        g = g[g.ticker.isin(tick)]
        allowed = not halted and pause_left == 0
        for bt, gb in g[g["ts"].dt.strftime("%H:%M") >= "09:35"].groupby("bt", sort=True):
            hm = bt[11:16]
            if hm > last_start:
                break
            b = {r.ticker: (float(r.Open), float(r.High), float(r.Low), float(r.Close)) for r in gb.itertuples()}
            ev = process_bar(st, bt, b, cfg, is_last_bar=(hm == last_start), entries_allowed=allowed and hm <= entry_cut)
            trades += [dict(e.__dict__, session=S.isoformat()) for e in ev if e.kind in ("BUY", "SELL")]
        if not st.closed:  # safety: flatten at the last known price
            last = g.groupby("ticker").tail(1).set_index("ticker")
            process_bar(st, f"{S}T{last_start}", {t: tuple(last.loc[t, ["Open", "High", "Low", "Close"]]) for t in st.positions},
                        cfg, is_last_bar=True, entries_allowed=False)
        cash = st.cash
        curve[S] = cash
        pause_left = max(0, pause_left - 1)
        peak = max(peak, cash)
        dd = 1 - cash / peak
        if dd >= cfg["risk"]["drawdown_halt"]:
            halted = True
        elif dd >= cfg["risk"]["drawdown_pause"] and pause_left == 0:
            pause_left = cfg["risk"]["pause_sessions"]
        days.append({"session": S.isoformat(), "candidates": len(cands), "trades": sum(1 for x in trades if x["session"] == S.isoformat() and x["kind"] == "BUY"),
                     "equity": cash})
    eq = pd.Series(curve)
    spy = bars[bars.ticker == "SPY"]
    spy_open = spy[spy.session == eq.index[0]].iloc[0].Open
    spy_close = spy.groupby("session").tail(1).set_index("session").Close
    spy_eq = (spy_close.loc[eq.index] / spy_open) * cfg["portfolio"]["starting_cash"]

    def stats(e: pd.Series, base: float) -> dict:
        r = e.pct_change().fillna(e.iloc[0] / base - 1)
        dd = 1 - e / np.maximum.accumulate(np.maximum(e, base))
        return {"start": str(e.index[0]), "end": str(e.index[-1]), "sessions": len(e), "end_value": round(float(e.iloc[-1]), 2),
                "total_return": float(e.iloc[-1] / base - 1), "max_drawdown": float(dd.max()),
                "daily_mean": float(r.mean()), "daily_std": float(r.std()),
                "sharpe_ann": float(r.mean() / r.std() * math.sqrt(252)) if r.std() > 0 else None,
                "pct_up_days": float((r > 0).mean())}
    sells = [t for t in trades if t["kind"] == "SELL"]
    half = len(eq) // 2
    res = {
        "note": f"Historical simulation, execution on {exec_minutes}-minute Yahoo bars (5-minute: ~60 sessions max; 1-minute: ~20). Not live results. Too short for statistical confidence.",
        "execution_bar_minutes": exec_minutes,
        "config_version": cfg["version"],
        "full": stats(eq, cfg["portfolio"]["starting_cash"]),
        "first_half": stats(eq.iloc[:half], cfg["portfolio"]["starting_cash"]),
        "second_half": stats(eq.iloc[half:], float(eq.iloc[half - 1])),
        "spy_same_period": stats(spy_eq, cfg["portfolio"]["starting_cash"]),
        "trades": {"n_round_trips": len(sells), "win_rate": float(np.mean([t["realized_pnl"] > 0 for t in sells])) if sells else None,
                   "avg_pnl_usd": float(np.mean([t["realized_pnl"] for t in sells])) if sells else None,
                   "exit_reasons": pd.Series([t["reason_code"] for t in sells]).value_counts().to_dict() if sells else {},
                   "avg_trades_per_day": float(np.mean([d["trades"] for d in days])) if days else 0,
                   "costs_usd": float(sum(t["qty"] * abs(t["fill_price"] - t["ref_price"]) for t in trades))},
        "curve": {"dates": [str(d) for d in eq.index], "equity": [round(float(x), 4) for x in eq], "spy": [round(float(x), 4) for x in spy_eq]},
        "days": days,
    }
    return res


if __name__ == "__main__":
    m = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    r = run(Path(sys.argv[1]), m)
    RESEARCH_DIR.mkdir(exist_ok=True)
    (RESEARCH_DIR / f"backtest_daytrade_{m}m.json").write_text(json.dumps(r, indent=1, default=str))
    print(json.dumps({k: v for k, v in r.items() if k not in ("curve", "days")}, indent=1, default=str))
