"""Historical test (research only). Kept separate from the live experiment's ledger.

Uses the exact same `strategy.decide` and `broker.Broker` as the live engine.
Differences from live, all disclosed in the research report:
  * no news confirmation/veto (no reliable free historical news archive),
  * fills only at session opens and stops on daily bars,
  * earnings dates from Yahoo's history.
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import math
from dataclasses import asdict

import numpy as np
import pandas as pd

from .broker import Broker, Portfolio
from .config import HISTORY_DIR, RESEARCH_DIR, load_strategy, load_universe
from .strategy import (DecisionContext, EarningsBook, EarningsEvent, Indicators, catalyst_metrics,
                       catalyst_passes, decide, map_reaction, regime_series)


# ---------------------------------------------------------------------------- data
class HistData:
    def __init__(self, cfg: dict):
        load = lambda n: pd.read_pickle(HISTORY_DIR / f"daily_{n}.pkl")  # noqa: E731
        self.o, self.h, self.l, self.c, self.v = (load(n) for n in ("open", "high", "low", "close", "volume"))
        self.div = load("dividends").fillna(0.0)
        # Sessions = days SPY traded. Drop rows with no SPY close (e.g. an unfinished current day).
        idx = self.c.index[self.c["SPY"].notna()]
        for n in ("o", "h", "l", "c", "v", "div"):
            setattr(self, n, getattr(self, n).loc[idx])
        self.sessions = [d.date() for d in idx]
        self.vix = self.c["^VIX"]
        cols = [c for c in self.c.columns if c != "^VIX"]
        self.ind = Indicators(self.o[cols], self.h[cols], self.l[cols], self.c[cols], self.v[cols], cfg)
        self.c_ffill = self.c[cols].ffill()
        u = load_universe()
        self.stocks = [m["ticker"] for m in u["members"] if m["ticker"] in self.c.columns]
        self.added: dict[str, dt.date] = {}
        for m in u["members"]:
            try:
                self.added[m["ticker"]] = dt.date.fromisoformat(m["date_added"])
            except ValueError:
                pass
        self.regime = regime_series(self.c["SPY"], self.ind.sma200["SPY"], self.vix, cfg)
        ev = pd.read_pickle(HISTORY_DIR / "earnings.pkl")
        events = []
        cutoff = cfg["catalyst"]["announce_hour_cutoff"]
        for r in ev.itertuples():
            mp = map_reaction(r.announce_ts, cutoff, self.sessions)
            if mp is None:
                continue
            events.append(EarningsEvent(r.ticker, r.announce_ts, mp[0], mp[1], pd.notna(r.eps_reported),
                                        r.eps_estimate, r.eps_reported, r.surprise_pct, "yahoo"))
        self.events = events
        self.book = EarningsBook(events)
        self.sidx = {d: i for i, d in enumerate(self.sessions)}

    def add_sessions(self, d: dt.date, n: int) -> dt.date:
        i = self.sidx.get(d)
        if i is None:  # not a known session: move to the next known one
            i = next(k for k, s in enumerate(self.sessions) if s > d) - 1
        j = i + n
        if j < len(self.sessions):
            return self.sessions[j]
        # beyond the data: approximate with weekdays
        extra, cur = j - (len(self.sessions) - 1), self.sessions[-1]
        while extra > 0:
            cur += dt.timedelta(days=1)
            if cur.weekday() < 5:
                extra -= 1
        return cur

    def eligible(self, t: str, d: dt.date) -> bool:
        a = self.added.get(t)
        return a is None or d >= a


# ---------------------------------------------------------------------------- simulation
def run(cfg: dict, data: HistData, start: str, end: str, label: str) -> dict:
    sess = [d for d in data.sessions if dt.date.fromisoformat(start) <= d <= dt.date.fromisoformat(end)]
    broker = Broker(cfg)
    pf = Portfolio(cash=cfg["portfolio"]["starting_cash"])
    R = cfg["risk"]
    pending, fills_all, equity = [], [], {}
    peak, pause_until, halt_until = pf.cash, -1, -1
    costs_paid = 0.0
    counts = {"rejected": 0}
    for i, S in enumerate(sess):
        ts = pd.Timestamp(S)
        prev_ts = pd.Timestamp(data.sessions[data.sidx[S] - 1])
        qty_prev = {t: p.qty for t, p in pf.positions.items()}
        adv_prev = data.ind.adv20.loc[prev_ts]
        need = {o.ticker for o in pending} | set(pf.positions)
        opens = {t: float(data.o.at[ts, t]) for t in need if t in data.o.columns}
        advd = {t: float(adv_prev.get(t, np.nan)) for t in need}
        fills, rej = broker.execute_open(pf, S.isoformat(), pending, opens, advd, S.isoformat() + "T09:30 ET", "daily_open")
        counts["rejected"] += len(rej)
        fills_all += fills
        # intraday stops on the daily bar
        for t in list(pf.positions):
            bar = (S.isoformat(), data.o.at[ts, t], data.h.at[ts, t], data.l.at[ts, t], data.c.at[ts, t])
            f = broker.check_stop(pf, t, [tuple([bar[0]] + [float(x) for x in bar[1:]])], S.isoformat(), "daily_bar", advd.get(t))
            if f:
                fills_all.append(f)
        # dividends for shares held at the prior close
        for t, q in qty_prev.items():
            dv = data.div.at[ts, t] if t in data.div.columns else 0.0
            if dv and dv > 0:
                pf.cash += q * float(dv)
        broker.close_session(pf, {t: float(data.h.at[ts, t]) for t in pf.positions})
        marks = {t: float(data.c_ffill.at[ts, t]) for t in pf.positions}
        eq = pf.equity(marks)
        equity[S] = eq
        # drawdown controls
        peak = max(peak, eq)
        dd = 1 - eq / peak
        halted = i <= halt_until
        if not halted and dd >= R["drawdown_halt"]:
            halt_until, halted = i + R["halt_sessions"], True
            peak = eq  # reset so the halt doesn't re-trigger immediately after it expires
        elif dd >= R["drawdown_pause"]:
            pause_until = max(pause_until, i + R["pause_sessions"])
        risk = {"halted": halted, "paused": i <= pause_until and not halted, "drawdown": dd}
        if i + 1 < len(sess):
            N = sess[i + 1]
            ctx = DecisionContext(cfg=cfg, ind=data.ind, stocks=data.stocks, regime=data.regime.get(ts, "OFF?"),
                                  earnings=data.book, pf=pf, risk=risk,
                                  is_rebalance=(N.isocalendar()[1] != S.isocalendar()[1]) or i == 0,
                                  created_at=S.isoformat() + "T16:00 ET", eligible=data.eligible,
                                  add_sessions=data.add_sessions)
            pending, _ = decide(S, N, ctx)
    costs_paid = sum(f.cost_usd for f in fills_all)
    eq = pd.Series(equity)
    return {"label": label, "equity": eq, "fills": fills_all, "costs": costs_paid, "rejected": counts["rejected"],
            "final_positions": {t: asdict(p) for t, p in pf.positions.items()}}


def spy_buy_hold(cfg: dict, data: HistData, start: str, end: str) -> pd.Series:
    sess = [d for d in data.sessions if dt.date.fromisoformat(start) <= d <= dt.date.fromisoformat(end)]
    c = cfg["costs"]
    px0 = float(data.o.at[pd.Timestamp(sess[0]), "SPY"]) * (1 + (c["etf_bps"] + c["open_auction_extra_bps"]) / 1e4)
    qty = cfg["portfolio"]["starting_cash"] / px0
    cash, out = 0.0, {}
    for S in sess:
        ts = pd.Timestamp(S)
        cash += qty * float(data.div.at[ts, "SPY"] or 0)
        out[S] = cash + qty * float(data.c.at[ts, "SPY"])
    return pd.Series(out)


# ---------------------------------------------------------------------------- metrics
def stats(eq: pd.Series, fills=None) -> dict:
    eq = eq.dropna()
    r = eq.pct_change().dropna()
    yrs = max((eq.index[-1] - eq.index[0]).days / 365.25, 1e-9)
    dd = 1 - eq / eq.cummax()
    out = {
        "start_value": round(float(eq.iloc[0]), 2), "end_value": round(float(eq.iloc[-1]), 2),
        "total_return": float(eq.iloc[-1] / eq.iloc[0] - 1),
        "cagr": float((eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1),
        "ann_vol": float(r.std() * math.sqrt(252)),
        "sharpe_rf0": float(r.mean() / r.std() * math.sqrt(252)) if r.std() > 0 else None,
        "max_drawdown": float(dd.max()),
    }
    if fills is not None:
        sells = [f for f in fills if f.side == "SELL" and f.sleeve != "residual"]
        wins = [f.realized_pnl for f in sells if f.realized_pnl > 0]
        losses = [f.realized_pnl for f in sells if f.realized_pnl <= 0]
        out.update({
            "n_fills": len(fills), "n_stock_round_trips": len(sells),
            "win_rate": len(wins) / len(sells) if sells else None,
            "avg_win_usd": float(np.mean(wins)) if wins else None,
            "avg_loss_usd": float(np.mean(losses)) if losses else None,
            "costs_usd": float(sum(f.cost_usd for f in fills)),
        })
        by = {}
        for f in sells:
            by.setdefault(f.sleeve, []).append(f.realized_pnl)
        out["realized_pnl_by_sleeve"] = {k: round(float(sum(v)), 2) for k, v in by.items()}
        out["exit_reasons"] = pd.Series([f.reason_code for f in sells]).value_counts().to_dict() if sells else {}
    return out


def rolling_windows(eq: pd.Series, bench: pd.Series, days: int = 30) -> dict:
    """Returns over every 30-calendar-day window: how noisy is a single month?"""
    eq, bench = eq.copy(), bench.copy()
    eq.index = pd.to_datetime(eq.index)
    bench.index = pd.to_datetime(bench.index)
    rows = []
    for d0 in eq.index:
        d1 = d0 + pd.Timedelta(days=days)
        if d1 > eq.index[-1]:
            break
        j = eq.index.searchsorted(d1, side="right") - 1
        rs = eq.iloc[j] / eq.loc[d0] - 1
        rb = bench.iloc[j] / bench.loc[d0] - 1
        rows.append((rs, rb))
    a = np.array(rows)
    ex = a[:, 0] - a[:, 1]
    return {
        "n_windows": len(a), "strategy_mean": float(a[:, 0].mean()), "strategy_std": float(a[:, 0].std()),
        "strategy_p05": float(np.percentile(a[:, 0], 5)), "strategy_p95": float(np.percentile(a[:, 0], 95)),
        "spy_mean": float(a[:, 1].mean()), "excess_mean": float(ex.mean()), "excess_std": float(ex.std()),
        "pct_windows_beat_spy": float((ex > 0).mean()), "pct_windows_positive": float((a[:, 0] > 0).mean()),
    }


def event_study(cfg: dict, data: HistData, start: str, end: str) -> dict:
    """Forward returns after qualifying catalyst signals, entering at the next session open."""
    CAT = cfg["catalyst"]
    s0, s1 = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    rows = []
    for ev in data.events:
        D = ev.reaction
        if not (s0 <= D <= s1) or ev.ticker not in data.c.columns or not data.eligible(ev.ticker, D):
            continue
        i = data.sidx.get(D)
        if i is None or i + 21 >= len(data.sessions):
            continue
        m = catalyst_metrics(pd.Timestamp(D), ev.ticker, data.ind)
        ok, _ = catalyst_passes(m, CAT)
        loose = m["valid_bar"] and m["ret"] is not None and m["ret"] >= CAT["min_reaction_return"]
        if not loose:
            continue
        S = pd.Timestamp(data.sessions[i + 1])
        entry, spy_entry = data.o.at[S, ev.ticker], data.o.at[S, "SPY"]
        rec = {"ticker": ev.ticker, "reaction": D, "year": D.year, "passes_all": ok}
        for k in (1, 5, 10, 20):
            e = pd.Timestamp(data.sessions[i + k])
            r = data.c.at[e, ev.ticker] / entry - 1
            rb = data.c.at[e, "SPY"] / spy_entry - 1
            rec[f"r{k}"], rec[f"x{k}"] = r, r - rb
        rows.append(rec)
    df = pd.DataFrame(rows)
    out = {}
    for name, sub in (("all_gaps_ge_threshold", df), ("passes_all_filters", df[df.passes_all] if len(df) else df)):
        if sub.empty:
            out[name] = {"n": 0}
            continue
        d = {"n": int(len(sub))}
        for k in (1, 5, 10, 20):
            x = sub[f"x{k}"].dropna()
            d[f"excess_{k}d_mean"] = float(x.mean())
            d[f"excess_{k}d_median"] = float(x.median())
            d[f"excess_{k}d_tstat"] = float(x.mean() / (x.std() / math.sqrt(len(x)))) if len(x) > 2 else None
            d[f"hit_rate_{k}d"] = float((x > 0).mean())
        d["by_year_excess_20d_mean"] = {int(y): round(float(g["x20"].mean()), 4) for y, g in sub.groupby("year")}
        d["by_year_n"] = {int(y): int(len(g)) for y, g in sub.groupby("year")}
        out[name] = d
    return out


def variant(cfg: dict, **enabled) -> dict:
    c = copy.deepcopy(cfg)
    for k, v in enabled.items():
        c[k]["enabled"] = v
    return c


def main(periods=None, write=True) -> dict:
    cfg = load_strategy()
    data = HistData(cfg)
    periods = periods or {"in_sample": ("2016-01-04", "2021-12-31"), "out_of_sample": ("2022-01-03", "2026-09-21")}
    results = {"generated_note": "Historical simulation; not live results. See research/PREREGISTRATION.md.",
               "config_version": cfg["version"], "periods": {}}
    curves = {}
    for pname, (a, b) in periods.items():
        spy = spy_buy_hold(cfg, data, a, b)
        runs = {
            "full_strategy": run(cfg, data, a, b, "full"),
            "without_catalyst": run(variant(cfg, catalyst=False), data, a, b, "no_catalyst"),
            "without_momentum": run(variant(cfg, momentum=False), data, a, b, "no_momentum"),
            "regime_gated_spy_only": run(variant(cfg, catalyst=False, momentum=False), data, a, b, "spy_regime"),
        }
        pr = {"start": a, "end": b, "spy_buy_hold": stats(spy),
              "cash": {"total_return": 0.0, "cagr": 0.0, "max_drawdown": 0.0}}
        for k, rr in runs.items():
            pr[k] = stats(rr["equity"], rr["fills"])
            pr[k]["rejected_orders"] = rr["rejected"]
        pr["rolling_30d_full_vs_spy"] = rolling_windows(runs["full_strategy"]["equity"], spy)
        pr["catalyst_event_study"] = event_study(cfg, data, a, b)
        results["periods"][pname] = pr
        curves[pname] = {"dates": [d.isoformat() for d in spy.index],
                         "spy": [round(x, 4) for x in spy.values],
                         **{k: [round(x, 4) for x in rr["equity"].reindex(spy.index).values] for k, rr in runs.items()}}
    if write:
        RESEARCH_DIR.mkdir(exist_ok=True)
        (RESEARCH_DIR / "backtest_results.json").write_text(json.dumps(results, indent=1, default=str))
        (RESEARCH_DIR / "backtest_curves.json").write_text(json.dumps(curves))
    return results


if __name__ == "__main__":
    import sys
    r = main()
    print(json.dumps(r, indent=1, default=str)[:20000])
    sys.exit(0)
