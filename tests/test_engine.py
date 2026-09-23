"""End-to-end simulation of the live engine with a fake, time-aware data feed (no network).

The fake feed only reveals what would have been visible at the simulated time, and reproduces Yahoo's
missing-official-close behaviour. The scenario covers: the first decision, MOO fills, an earnings-gap
buy in the research book, a day with the Mac offline, an intraday stop, a crash in the middle of a
session close-out, duplicate retries, and report generation.
"""
import datetime as dt
import json

import numpy as np
import pandas as pd
import pytest

from papertrader import engine as E
from papertrader import reporting, state
from papertrader.broker import Broker
from papertrader.config import ROOT, load_json, sha256_file
from papertrader.ledger import Ledger
from papertrader.marketdata import MarketData
from papertrader.news import NewsService
from papertrader.nyse_calendar import ET, UTC, prev_session, session_close, session_open, sessions_between
from papertrader.strategy import NewsVerdict

START, END = dt.date(2026, 8, 3), dt.date(2026, 8, 12)
S = sessions_between(START, END)  # 8 sessions
TICKERS = ["SPY", "^VIX", "AAA", "BBB", "CCC"]
EARN_DAY = S[1]  # AAA reports before the open on S2 -> reaction day S2 -> buy at S3 open
PLUNGE_DAY = S[4]  # AAA collapses at 10:30 ET on S5 -> stop


def at(d: dt.date, hh: int, mm: int = 0) -> dt.datetime:
    return dt.datetime.combine(d, dt.time(hh, mm), ET).astimezone(UTC)


# ---------------------------------------------------------------- synthetic "truth"
def build_truth():
    rng = np.random.default_rng(7)
    hist = sessions_between(dt.date(2025, 6, 2), prev_session(START))
    daily = {t: {} for t in TICKERS}
    intr = {t: {} for t in TICKERS}
    base = {"SPY": 500.0, "^VIX": 15.0, "AAA": 50.0, "BBB": 40.0, "CCC": 60.0}
    drift = {"SPY": 0.0006, "^VIX": 0.0, "AAA": -0.0004, "BBB": 0.004, "CCC": 0.0015}
    px = dict(base)
    for d in hist:
        for t in TICKERS:
            o = px[t] * (1 + rng.normal(0, 0.002))
            c = o * (1 + drift[t] + rng.normal(0, 0.006 if t != "^VIX" else 0.02))
            if t == "^VIX":
                c = 15 + rng.normal(0, 0.5)
            daily[t][d] = (o, max(o, c) * 1.004, min(o, c) * 0.996, c, 0.0 if t == "^VIX" else 3e6)
            px[t] = c
    for i, d in enumerate(S):
        for t in TICKERS:
            o = px[t] * (1.0 + (0.08 if (t == "AAA" and d == EARN_DAY) else 0.0))
            bars = []
            p = o
            for k in range(78):
                start = dt.datetime.combine(d, dt.time(9, 30), ET) + dt.timedelta(minutes=5 * k)
                step = drift[t] / 78 + (0.0008 if (t == "AAA" and d == EARN_DAY) else 0)
                if t == "AAA" and d == PLUNGE_DAY and k == 12:  # 10:30 ET: -15%
                    step = -0.15
                if t == "^VIX":
                    step = 0
                bo = p
                p = p * (1 + step)
                bars.append((start, bo, max(bo, p) * 1.0005, min(bo, p) * 0.9995, p, 40000.0 * (3 if (t == "AAA" and d == EARN_DAY) else 1)))
            intr[t][d] = bars
            daily[t][d] = (bars[0][1], max(b[2] for b in bars), min(b[3] for b in bars), bars[-1][4],
                           0.0 if t == "^VIX" else (9e6 if (t == "AAA" and d == EARN_DAY) else 3e6))
            px[t] = bars[-1][4]
    return daily, intr


DAILY, INTR = build_truth()
NOW = {"t": None}


def fake_download(self, tickers, **kw):
    now = NOW["t"]
    today = now.astimezone(ET).date()
    interval = kw.get("interval", "1d")
    frames = {}
    for t in tickers:
        if t not in DAILY:
            continue
        if interval == "1d":
            sess = [d for d in sorted(DAILY[t]) if d <= today][-10:]
            rows, idx = [], []
            for d in sess:
                o, h, l, c, v = DAILY[t][d]
                if now < session_open(d):
                    continue
                if now < session_close(d):  # in progress: partial bar
                    bars = [b for b in INTR[t].get(d, []) if b[0] + dt.timedelta(minutes=5) <= now.astimezone(ET)]
                    if not bars:
                        rows.append((o, o, o, o, 0.0, 0.0, 0.0))
                    else:
                        rows.append((o, max(b[2] for b in bars), min(b[3] for b in bars), bars[-1][4], v * len(bars) / 78, 0.0, 0.0))
                else:
                    # Yahoo quirk: the official close stays missing until 09:00 ET the next day
                    missing = t != "^VIX" and now < dt.datetime.combine(d + dt.timedelta(days=1), dt.time(9, 0), ET)
                    rows.append((o, h, l, np.nan if missing else c, v * 0.6 if missing else v, 0.0, 0.0))
                idx.append(pd.Timestamp(d))
            df = pd.DataFrame(rows, index=pd.DatetimeIndex(idx), columns=["Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"])
        else:
            rows, idx = [], []
            for d in [x for x in sorted(INTR[t]) if x <= today][-5:]:
                for b in INTR[t][d]:
                    if b[0] <= now.astimezone(ET):
                        idx.append(pd.Timestamp(b[0]))
                        rows.append(b[1:])
            df = pd.DataFrame(rows, index=pd.DatetimeIndex(idx), columns=["Open", "High", "Low", "Close", "Volume"])
        frames[t] = df
    if not frames:
        return None
    return pd.concat(frames, axis=1)


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(MarketData, "_download", fake_download)
    monkeypatch.setattr(MarketData, "earnings_for_dates", lambda self, dates, uni, now: [
        {"ticker": "AAA", "announce_date": EARN_DAY.isoformat(), "time_code": "time-pre-market",
         "announce_ts": f"{EARN_DAY.isoformat()} 07:00", "source": "nasdaq", "eps_forecast": "$1", "retrieved_at": "x"}] if EARN_DAY in dates else [])
    monkeypatch.setattr(NewsService, "check", lambda self, t, purpose, m: NewsVerdict(True, "confirmed" if purpose == "catalyst" else "no_veto", "test news ok"))
    monkeypatch.setattr(reporting, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(state, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(reporting, "notify", lambda *a: None)
    md = MarketData(tmp_path / "market.sqlite")
    rows = []
    for t in TICKERS:
        for d, (o, h, l, c, v) in DAILY[t].items():
            if d < START:
                rows.append((t, d.isoformat(), o, h, l, c, v, 0, 0, 1, "seed", "x"))
    md.db.executemany("INSERT INTO daily_bars VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    exp = {"start_date": START.isoformat(), "end_date": END.isoformat(), "starting_cash": 100.0, "report_days": [3, 10],
           "books": [{"id": "primary", "name": "Primary", "subtitle": "p", "strategy": str(ROOT / "config/strategy_v1_primary.json"), "ledger": str(tmp_path / "primary.sqlite")},
                     {"id": "research", "name": "Research", "subtitle": "r", "strategy": str(ROOT / "config/strategy_v1.json"), "ledger": str(tmp_path / "research.sqlite")}]}
    ledgers = {}
    for b in exp["books"]:
        L = Ledger(tmp_path / f"{b['id']}.sqlite")
        L.freeze(exp, b, load_json(b["strategy"])["version"], sha256_file(ROOT / b["strategy"]), "u")
        ledgers[b["id"]] = L
    return {"md": md, "exp": exp, "L": ledgers}


def cycle(env, when, crash=None):
    NOW["t"] = when
    out = {}
    for b in env["exp"]["books"]:
        L = env["L"][b["id"]]
        cfg = load_json(b["strategy"])
        L.start_run(f"{when.isoformat()}-{b['id']}-{np.random.rand()}", "test")
        eng = E.Engine(L, env["md"], cfg, env["exp"], when)
        eng.stocks = ["AAA", "BBB", "CCC"]
        eng.names = {"AAA": "Alpha Co", "BBB": "Beta Co", "CCC": "Gamma Co"}
        try:
            if crash and crash[0] == b["id"]:
                crash[1](eng)
            out[b["id"]] = eng.step()
            L.finish_run("OK", out[b["id"]])
        except RuntimeError as e:
            L.finish_run("ERROR", error=str(e))
            out[b["id"]] = f"ERROR {e}"
    reporting.maybe_generate_reports(env["exp"], env["L"]["primary"], env["md"], when)
    return out


def counts(L):
    return {k: L.db.execute(f"SELECT COUNT(*) c FROM {k}").fetchone()["c"] for k in ("orders", "fills", "decisions", "snapshots")}


def test_full_live_simulation(env):
    Lp, Lr = env["L"]["primary"], env["L"]["research"]
    # evening before the start: official close missing -> derived from 5m after 16:30 ET -> MOO orders for S1
    out = cycle(env, at(prev_session(START), 20, 0))
    assert "decided for 2026-08-03" in out["primary"], out
    o = Lp.open_orders()
    assert [x.ticker for x in o] == ["SPY"] and o[0].order_type == "MOO"
    assert {x.ticker for x in Lr.open_orders() if x.sleeve == "momentum"}  # momentum picks exist
    before = counts(Lr)
    cycle(env, at(prev_session(START), 20, 5))  # retry: nothing new
    assert counts(Lr) == before

    # S1 during the session: MOO fills at the official open
    cycle(env, at(S[0], 10, 0))
    f = Lp.db.execute("SELECT * FROM fills").fetchone()
    assert f["ticker"] == "SPY" and f["ref_price"] == pytest.approx(DAILY["SPY"][S[0]][0])
    assert f["price_time"].startswith("2026-08-03T09:30")
    # S1 after close -> close-out + decision for S2; S2 -> S3 with the earnings-gap buy
    cycle(env, at(S[0], 17, 0))
    cycle(env, at(S[1], 11, 0))
    cycle(env, at(S[1], 17, 0))
    buys = [x for x in Lr.open_orders() if x.ticker == "AAA"]
    assert buys and buys[0].side == "BUY" and buys[0].sleeve == "catalyst" and buys[0].session == S[2].isoformat()
    dec = Lr.db.execute("SELECT * FROM decisions WHERE ticker='AAA' AND action='BUY'").fetchone()
    assert dec["data_through"] == EARN_DAY.isoformat() and json.loads(dec["metrics"])["ret"] > 0.05
    cycle(env, at(S[2], 9, 45))
    aaa = Lr.db.execute("SELECT * FROM fills WHERE ticker='AAA'").fetchone()
    assert aaa["ref_price"] == pytest.approx(DAILY["AAA"][S[2]][0])  # the S3 open, after the decision
    cycle(env, at(S[2], 16, 45))  # close S3 + decide S4 (MOO)

    # S4: Mac offline all day. S5 08:00 ET: S4 is closed out from daily data; decision for S4 is logged as missed.
    out = cycle(env, at(S[4], 8, 0))
    assert Lp.db.execute("SELECT 1 FROM snapshots WHERE session=?", (S[3].isoformat(),)).fetchone()
    missed = Lr.db.execute("SELECT * FROM decisions WHERE decision_key=?", (f"missed:{S[3]}",)).fetchone()
    assert missed is None  # S4's decision was made on S3's evening, so nothing was missed
    assert Lr.db.execute("SELECT 1 FROM decisions WHERE decision_key=?", (f"decide:{S[4]}",)).fetchone()

    # S5 11:00 ET: AAA collapsed at 10:30 -> stop fills from 5m bars, after entry, at/below the stop
    cycle(env, at(S[4], 11, 0))
    st = Lr.db.execute("SELECT * FROM fills WHERE ticker='AAA' AND side='SELL'").fetchone()
    assert st is not None and st["reason_code"] in ("STOP", "STOP_GAP")
    assert st["price_time"] >= "2026-08-07T10:30"
    assert st["fill_price"] < aaa["fill_price"]

    # crash in the middle of closing out S5 -> full rollback, then a clean retry
    def crash(eng):
        orig = eng.broker.close_session

        def boom(*a, **k):
            raise RuntimeError("injected crash")
        eng.broker.close_session = boom
    before = counts(Lr)
    out = cycle(env, at(S[4], 17, 0), crash=("research", crash))
    assert out["research"].startswith("ERROR")
    assert counts(Lr) == before  # nothing half-written
    assert Lr.get_state("last_closed_session") == S[3].isoformat()
    cycle(env, at(S[4], 17, 5))
    assert Lr.get_state("last_closed_session") == S[4].isoformat()

    # Mac asleep for S6 and S7 entirely, comes back after S8 closes
    cycle(env, at(S[7], 18, 0))
    missed = [r["session"] for r in Lp.db.execute("SELECT session FROM decisions WHERE decision_key LIKE 'missed:%'")]
    assert missed == [S[6].isoformat(), S[7].isoformat()]  # S6's decision was made on S5's evening
    for L in (Lp, Lr):
        snaps = [r["session"] for r in L.db.execute("SELECT session FROM snapshots ORDER BY session")]
        assert snaps == [d.isoformat() for d in S]
        ok, msg = L.verify_chain()
        assert ok, msg
        # every non-stop fill uses a price observed after its order was created
        for r in L.db.execute("SELECT f.price_time, o.created_at, o.order_type FROM fills f JOIN orders o USING(order_key) WHERE o.order_type != 'STOP'"):
            px_time = dt.datetime.fromisoformat(r["price_time"][:25])
            assert px_time > dt.datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")), r
        # cash reconciles with fills + dividends
        b = L.db.execute("SELECT COALESCE(SUM(CASE WHEN side='BUY' THEN -qty*fill_price ELSE qty*fill_price END),0) s FROM fills").fetchone()["s"]
        assert L.get_state("cash") == pytest.approx(100 + b)
        assert L.db.execute("SELECT COUNT(*) c FROM fills").fetchone()["c"] == L.db.execute("SELECT COUNT(DISTINCT order_key) c FROM fills").fetchone()["c"]
    # the SPY benchmark bought at S1's official open
    bench = Lp.get_state("benchmark")
    assert bench["entry_price"] == pytest.approx(DAILY["SPY"][S[0]][0] * 1.0007)
    # reports: day 3 (as of S3) and day 10 (final, as of S8)
    reps = [r["report_key"] for r in Lp.db.execute("SELECT report_key FROM reports ORDER BY report_key")]
    assert reps == ["day03", "day10"]
    assert Lp.get_state("experiment_finished")
    md_text = (reporting.REPORTS_DIR / f"day03_{S[2].isoformat()}.md").read_text()
    assert "SPY buy & hold" in md_text and "Cash (do nothing)" in md_text and "Execution assumptions" in md_text
    # after the end date: no new orders
    n = counts(Lr)["orders"]
    cycle(env, at(END + dt.timedelta(days=3), 12, 0))
    assert counts(Lr)["orders"] == n
