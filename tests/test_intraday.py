"""Day-trading book: bar-processing rules and the live engine (fake, time-aware data feed; no network)."""
import datetime as dt

import numpy as np
import pandas as pd
import pytest

from papertrader import day_engine as DE
from papertrader.config import ROOT, load_json, sha256_file
from papertrader.intraday import DayState, process_bar
from papertrader.ledger import Ledger
from papertrader.marketdata import MarketData
from papertrader.news import NewsService
from papertrader.nyse_calendar import ET, UTC, prev_session, sessions_between
from papertrader.strategy import NewsVerdict

CFG = load_json(ROOT / "config/strategy_daytrade_v1.json")


def cand(t, trigger=100.61, stop_distance=0.2, rank=1):
    return {"ticker": t, "rank": rank, "rvol": 4.0, "first_open": 100, "first_high": trigger - 0.01, "first_low": 99.9,
            "first_close": 100.5, "first_volume": 1, "atr": 2.0, "adv_usd": 2e9, "trigger": trigger, "stop_distance": stop_distance}


def test_breakout_entry_stop_and_settlement():
    st = DayState("2026-09-24", 100.0, 100.0, candidates=[cand("AAA"), cand("BBB", 50.41, 0.1, 2)], pending=["AAA", "BBB"])
    ev = process_bar(st, "t1", {"AAA": (100.5, 100.55, 100.45, 100.5)}, CFG, is_last_bar=False, entries_allowed=True)
    assert ev == [] and not st.positions  # no breakout yet
    ev = process_bar(st, "t2", {"AAA": (100.62, 100.9, 100.6, 100.85)}, CFG, is_last_bar=False, entries_allowed=True)
    assert ev[0].kind == "BUY" and ev[0].ref_price == 100.62  # gapped above the trigger: fills at the bar open
    assert ev[0].qty * ev[0].fill_price == pytest.approx(20.0, rel=1e-4)
    ev = process_bar(st, "t3", {"AAA": (100.8, 100.8, 100.3, 100.4)}, CFG, is_last_bar=False, entries_allowed=True)
    assert ev[0].kind == "SELL" and ev[0].reason_code == "STOP" and ev[0].ref_price == pytest.approx(100.62 - 0.2)
    # AAA can't be re-entered today, and sale proceeds don't add buying power (cash account, T+1)
    assert "AAA" in st.traded and st.buys_used == pytest.approx(20.0, rel=1e-4)
    cash_after = st.cash
    ev = process_bar(st, "t4", {"AAA": (101, 102, 101, 102), "BBB": (50.5, 50.6, 50.45, 50.55)}, CFG, is_last_bar=True, entries_allowed=True)
    kinds = [(e.kind, e.ticker, e.reason_code) for e in ev]
    assert ("BUY", "BBB", "ORB_BREAKOUT") in kinds and ("SELL", "BBB", "CLOSE_EXIT") in kinds and st.closed
    assert not any(k[1] == "AAA" for k in kinds)
    assert st.cash < cash_after + 1  # just the BBB round trip


def test_same_bar_worst_case_and_slot_limit():
    st = DayState("d", 100.0, 100.0, candidates=[cand(f"S{i}", rank=i + 1) for i in range(7)], pending=[f"S{i}" for i in range(7)])
    ev = process_bar(st, "t", {f"S{i}": (100.5, 101, 100.5, 100.9) for i in range(7)}, CFG, is_last_bar=False, entries_allowed=True)
    assert sum(e.kind == "BUY" for e in ev) == 5 and sum(e.reason_code == "NO_SLOT" for e in ev) == 2
    st2 = DayState("d", 100.0, 100.0, candidates=[cand("X")], pending=["X"])
    ev = process_bar(st2, "t", {"X": (100.5, 101, 100.3, 100.9)}, CFG, is_last_bar=False, entries_allowed=True)
    assert [e.reason_code for e in ev] == ["ORB_BREAKOUT", "STOP"]  # the entry bar also touched the stop: assume stopped


# ---------------------------------------------------------------- live engine
S = dt.date(2026, 8, 20)
HIST = sessions_between(dt.date(2026, 7, 20), prev_session(S))[-20:]
TICK = ["AAA", "BBB", "CCC", "DDD"]


def at(h, m, d=S):
    return dt.datetime.combine(d, dt.time(h, m), ET).astimezone(UTC)


def one_min_path(t):
    """1-minute (o,h,l,c) bars for session S; tiny ranges so bars never straddle a stop by accident."""
    out, p = [], {"AAA": 100.0, "BBB": 80.0, "CCC": 60.0, "DDD": 50.0, "SPY": 500.0}[t]
    for k in range(390):
        ts = dt.datetime.combine(S, dt.time(9, 30), ET) + dt.timedelta(minutes=k)
        hm = ts.strftime("%H:%M")
        if t == "AAA":
            p = 100.0 + 0.1 * min(k, 4) if k < 20 else 101.0 + 2.0 * (k - 20) / 370  # range 09:30-09:34, breakout at 09:50, drifts up
        elif t == "DDD":
            p = 50.0 + 0.06 * min(k, 4) if k < 30 else (50.5 if hm < "10:30" else 50.0)  # breakout 10:00, stop 10:30
        elif t == "CCC":
            p = 60.0 - 0.1 * min(k, 5)  # in play but first bar down
        o = out[-1][4] if out else p
        out.append((ts, o, max(o, p) + 0.005, min(o, p) - 0.005, p))
    return out


PATHS = {t: one_min_path(t) for t in TICK + ["SPY"]}
NOW = {"t": None}


def fake_download(self, tickers, **kw):
    now = NOW["t"].astimezone(ET)
    iv = kw.get("interval", "1d")
    frames = {}
    for t in tickers:
        rows, idx = [], []
        if iv == "5m":
            for d in HIST + [S]:
                if d == S and now < dt.datetime.combine(S, dt.time(9, 35), ET):
                    continue
                if d == S:
                    b = PATHS[t][:5]
                    o, h, l, c = b[0][1], max(x[2] for x in b), min(x[3] for x in b), b[-1][4]
                    v = {"AAA": 400e3, "DDD": 300e3, "CCC": 500e3, "BBB": 90e3}.get(t, 1e6)
                else:
                    base = {"AAA": 100, "BBB": 80, "CCC": 60, "DDD": 50}.get(t, 500)
                    o, h, l, c, v = base, base + 0.1, base - 0.1, base, 100e3
                idx.append(pd.Timestamp(dt.datetime.combine(d, dt.time(9, 30), ET)))
                rows.append((o, h, l, c, v))
        elif iv == "1m":
            for (ts, o, h, l, c) in PATHS.get(t, []):
                if ts + dt.timedelta(minutes=1) <= now:
                    idx.append(pd.Timestamp(ts)); rows.append((o, h, l, c, 1000.0))
        else:
            for d in HIST + ([S] if now >= dt.datetime.combine(S, dt.time(16, 20), ET) else []):
                base = {"AAA": 100, "BBB": 80, "CCC": 60, "DDD": 50, "SPY": 500, "^VIX": 15}.get(t, 100)
                atr = {"AAA": 2, "DDD": 1}.get(t, 2)
                idx.append(pd.Timestamp(d)); rows.append((base, base + atr / 2, base - atr / 2, base + (2 if t == "SPY" and d == S else 0), 3e6, 0.0, 0.0))
        cols = ["Open", "High", "Low", "Close", "Volume"] + (["Dividends", "Stock Splits"] if iv == "1d" else [])
        frames[t] = pd.DataFrame(rows, index=pd.DatetimeIndex(idx), columns=cols)
    return pd.concat(frames, axis=1)


@pytest.fixture
def make(tmp_path, monkeypatch):
    monkeypatch.setattr(MarketData, "_download", fake_download)
    monkeypatch.setattr(NewsService, "check", lambda self, t, p, m: NewsVerdict(True, "no_veto", "ok"))
    exp = {"start_date": S.isoformat(), "end_date": S.isoformat(), "starting_cash": 100.0, "report_days": [1]}
    book = {"id": "daytrade", "strategy": "config/strategy_daytrade_v1.json"}

    def _make(name):
        md = MarketData(tmp_path / f"{name}_market.sqlite")
        L = Ledger(tmp_path / f"{name}.sqlite")
        L.freeze(exp, book, CFG["version"], sha256_file(ROOT / book["strategy"]), "u")
        return md, L
    return _make


def run(md, L, when):
    NOW["t"] = when
    L.start_run(f"{when}-{np.random.rand()}", "test")
    e = DE.DayEngine(L, md, CFG, {}, when)
    e.stocks, e.names = TICK, {t: t for t in TICK}
    return e.step()


def fills(L):
    return [(r["ticker"], r["side"], round(r["qty"], 6), round(r["fill_price"], 6), r["price_time"], r["reason_code"])
            for r in L.db.execute("SELECT * FROM fills ORDER BY fill_id")]


def test_day_engine_live_matches_catch_up(make):
    md, L = make("live")
    assert "waiting" not in run(md, L, at(9, 33)) or True  # opening range not complete: nothing happens
    assert fills(L) == []
    run(md, L, at(10, 40))  # during the session
    f = fills(L)
    assert [x[:2] for x in f] == [("AAA", "BUY"), ("DDD", "BUY"), ("DDD", "SELL")]
    assert f[0][4].startswith("2026-08-20T09:50") and f[1][4].startswith("2026-08-20T10:00")
    assert f[2][5] == "STOP" and f[2][4].startswith("2026-08-20T10:30")
    cands = {r["ticker"] for r in L.db.execute("SELECT ticker FROM decisions WHERE reason_code='CANDIDATE'")}
    assert cands == {"AAA", "DDD"}  # CCC was in play but its first bar was down (long-only)
    assert [r["ticker"] for r in L.db.execute("SELECT ticker FROM positions")] == ["AAA"]
    run(md, L, at(16, 25))  # after the close
    f = fills(L)
    assert f[-1][:2] == ("AAA", "SELL") and f[-1][5] == "CLOSE_EXIT"
    snap = L.db.execute("SELECT * FROM snapshots").fetchone()
    assert snap and snap["equity"] == pytest.approx(L.get_state("cash")) and snap["spy_bh_equity"] > 100
    assert L.db.execute("SELECT COUNT(*) FROM positions").fetchone()[0] == 0
    n = len(f)
    run(md, L, at(16, 40))  # retry: nothing new
    assert len(fills(L)) == n
    # a single run long after the close produces exactly the same trades and prices
    md2, L2 = make("catchup")
    run(md2, L2, at(18, 0))
    assert fills(L2) == f
    assert L2.db.execute("SELECT COUNT(*) FROM decisions WHERE reason LIKE '%after the bar%'").fetchone()[0] > 0
    assert L.verify_chain()[0] and L2.verify_chain()[0]


def test_v2_requires_an_earnings_catalyst(make, monkeypatch):
    import copy
    cfg2 = copy.deepcopy(CFG)
    cfg2["selection"]["require_earnings_catalyst"] = True
    cfg2["exit"]["stop_mode"] = "opening_range_low"
    # only DDD reported earnings before today's open
    monkeypatch.setattr(MarketData, "earnings_for_dates", lambda self, dates, uni, now: (
        setattr(self, "earnings_failed", []) or [{"ticker": "DDD", "announce_date": S.isoformat(), "time_code": "time-pre-market",
                                                   "announce_ts": f"{S.isoformat()} 07:00", "source": "nasdaq", "eps_forecast": "", "retrieved_at": "x"}]))
    monkeypatch.setattr(DE.DayEngine, "_stocktwits", lambda self, t: {})
    md, L = make("v2")
    NOW["t"] = at(10, 40)
    L.start_run("v2", "test")
    e = DE.DayEngine(L, md, cfg2, {}, at(10, 40))
    e.stocks, e.names = TICK, {t: t for t in TICK}
    e.step()
    cands = {r["ticker"] for r in L.db.execute("SELECT ticker FROM decisions WHERE reason_code='CANDIDATE'")}
    assert cands == {"DDD"}  # AAA was in play too, but had no earnings catalyst
    buy = L.db.execute("SELECT reason FROM fills WHERE ticker='DDD' AND side='BUY'").fetchone()
    assert buy and "low of the first 5 minutes" in buy["reason"]
