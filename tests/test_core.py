"""Unit tests: fill rules, costs, ledger integrity, look-ahead safety, news timestamp handling."""
import datetime as dt
import json
import sqlite3

import numpy as np
import pandas as pd
import pytest

from papertrader.broker import Broker, Order, Portfolio, Position
from papertrader.config import load_strategy
from papertrader.ledger import Ledger
from papertrader.nyse_calendar import add_sessions, is_session, last_completed_session, next_session, UTC
from papertrader.strategy import DecisionContext, EarningsBook, EarningsEvent, Indicators, decide, map_reaction


@pytest.fixture
def cfg():
    return load_strategy()


def order(key, t, side, notional=None, qty=None, prio=50, sleeve="momentum", ep=None):
    return Order(key=key, ticker=t, side=side, order_type="MOO", session="2026-09-23", created_at="2026-09-23T12:00:00Z",
                 sleeve=sleeve, reason_code="TEST", reason="test", notional=notional, qty=qty, priority=prio, entry_params=ep or {})


def test_moo_buy_uses_open_plus_costs(cfg):
    b = Broker(cfg)
    pf = Portfolio(cash=100.0)
    fills, rej = b.execute_open(pf, "2026-09-23", [order("k1", "AAA", "BUY", notional=20)], {"AAA": 50.0}, {"AAA": 2e9}, "t", "test")
    assert not rej and len(fills) == 1
    f = fills[0]
    assert f.ref_price == 50.0
    assert f.fill_price == pytest.approx(50.0 * (1 + (5 + 5) / 1e4))  # 5bp tier + 5bp open auction
    assert pf.cash == pytest.approx(100 - f.qty * f.fill_price)
    assert f.qty * f.fill_price <= 20.0 + 1e-9


def test_sells_fill_before_buys_and_cash_is_checked(cfg):
    b = Broker(cfg)
    pf = Portfolio(cash=0.5, positions={"SPY": Position("SPY", 0.1, 500, "residual", "2026-09-22", 500, high_water=500)})
    orders = [order("buy", "AAA", "BUY", notional=40, prio=20), order("sell", "SPY", "SELL", qty=None, prio=5, sleeve="residual")]
    fills, rej = b.execute_open(pf, "2026-09-23", orders, {"AAA": 10.0, "SPY": 500.0}, {"AAA": 2e9}, "t", "test")
    assert [f.side for f in fills] == ["SELL", "BUY"]
    assert pf.cash >= 0
    assert fills[1].qty * fills[1].fill_price <= 50.5  # limited to available cash, never negative


def test_insufficient_cash_rejects(cfg):
    b = Broker(cfg)
    pf = Portfolio(cash=0.2)
    fills, rej = b.execute_open(pf, "2026-09-23", [order("k", "AAA", "BUY", notional=20)], {"AAA": 10.0}, {}, "t", "test")
    assert not fills and rej and "insufficient cash" in rej[0][1]


def test_stop_gap_fills_at_open_not_stop(cfg):
    b = Broker(cfg)
    pf = Portfolio(cash=0, positions={"AAA": Position("AAA", 1.0, 100, "catalyst", "2026-09-20", 100, initial_stop=92.0, high_water=100)})
    fills, _ = b.execute_open(pf, "2026-09-23", [], {"AAA": 85.0}, {"AAA": 2e9}, "t", "test")
    assert len(fills) == 1 and fills[0].reason_code == "STOP_GAP"
    assert fills[0].ref_price == 85.0  # gap-through: the worse open price, never the stop price


def test_stop_touch_fills_at_stop_with_extra_slippage(cfg):
    b = Broker(cfg)
    pf = Portfolio(cash=0, positions={"AAA": Position("AAA", 1.0, 100, "catalyst", "2026-09-20", 100, initial_stop=92.0, high_water=100)})
    f = b.check_stop(pf, "AAA", [("b1", 95, 96, 94, 95), ("b2", 95, 95.5, 91, 91.5)], "2026-09-23", "test", 2e9)
    assert f.reason_code == "STOP" and f.ref_price == 92.0
    assert f.fill_price == pytest.approx(92.0 * (1 - (5 + 15 + 0.3) / 1e4))
    assert "AAA" not in pf.positions


def test_trailing_stop_rises_with_high_water(cfg):
    p = Position("AAA", 1, 100, "momentum", "2026-09-20", 100, initial_stop=88, trail_pct=0.12, high_water=100)
    assert p.stop_level() == pytest.approx(88)
    p.high_water = 150
    assert p.stop_level() == pytest.approx(132)


def test_calendar():
    assert not is_session(dt.date(2026, 9, 26))  # Saturday
    assert not is_session(dt.date(2026, 11, 26))  # Thanksgiving
    assert next_session(dt.date(2026, 9, 25)) == dt.date(2026, 9, 28)
    assert add_sessions(dt.date(2026, 9, 23), 5) == dt.date(2026, 9, 30)
    # 15:59 ET on 2026-09-23 -> last completed session is the 22nd; 16:00 ET -> the 23rd
    assert last_completed_session(dt.datetime(2026, 9, 23, 19, 59, tzinfo=UTC)) == dt.date(2026, 9, 22)
    assert last_completed_session(dt.datetime(2026, 9, 23, 20, 0, tzinfo=UTC)) == dt.date(2026, 9, 23)


def test_reaction_day_mapping():
    sess = [dt.date(2026, 9, 21), dt.date(2026, 9, 22), dt.date(2026, 9, 23)]
    assert map_reaction("2026-09-22 07:00", 12, sess) == (dt.date(2026, 9, 22), dt.date(2026, 9, 21))  # before open: same day
    assert map_reaction("2026-09-22 16:05", 12, sess) == (dt.date(2026, 9, 23), dt.date(2026, 9, 22))  # after close: next day


# ---------------------------------------------------------------- ledger integrity
def test_ledger_idempotency_and_append_only(tmp_path, cfg):
    L = Ledger(tmp_path / "l.sqlite")
    L.start_run("r1", "test")
    o = order("2026-09-23:momentum:AAA:BUY:MOMENTUM", "AAA", "BUY", notional=20)
    assert L.insert_order(o) is True
    assert L.insert_order(o) is False  # retry cannot duplicate
    b = Broker(cfg)
    pf = Portfolio(cash=100)
    fills, _ = b.execute_open(pf, "2026-09-23", [o], {"AAA": 10.0}, {}, "t", "test")
    assert L.record_fill(fills[0]) is True
    assert L.record_fill(fills[0]) is False  # duplicate fill ignored
    assert L.db.execute("SELECT COUNT(*) c FROM fills").fetchone()["c"] == 1
    with pytest.raises(sqlite3.DatabaseError):
        L.db.execute("UPDATE fills SET fill_price = 1")
    with pytest.raises(sqlite3.DatabaseError):
        L.db.execute("DELETE FROM fills")
    with pytest.raises(sqlite3.DatabaseError):
        L.db.execute("UPDATE orders SET notional = 999 WHERE order_key = ?", (o.key,))
    ok, _ = L.verify_chain()
    assert ok


def test_hash_chain_detects_tampering(tmp_path):
    L = Ledger(tmp_path / "l.sqlite")
    L.event("a", {"x": 1})
    L.event("b", {"x": 2})
    L.db.execute("DROP TRIGGER events_no_update")  # simulate someone bypassing the guard
    L.db.execute("UPDATE events SET payload = '{\"x\": 99}' WHERE seq = 1")
    ok, msg = L.verify_chain()
    assert not ok and "seq 1" in msg


# ---------------------------------------------------------------- no look-ahead
def _synthetic(n=300, seed=1):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2025-06-02", periods=n)
    cols = ["SPY", "AAA", "BBB", "CCC"]
    c = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0.0008, 0.01, (n, len(cols))), axis=0)), index=idx, columns=cols)
    o = c.shift(1).fillna(c.iloc[0]) * (1 + rng.normal(0, 0.002, c.shape))
    h = np.maximum(o, c) * 1.005
    l = np.minimum(o, c) * 0.995
    v = pd.DataFrame(rng.integers(2_000_000, 4_000_000, c.shape), index=idx, columns=cols).astype(float)
    return o, h, l, c, v


def test_decisions_do_not_depend_on_future_data(cfg):
    o, h, l, c, v = _synthetic()
    D = c.index[-40].date()
    S = (c.index[-39]).date()
    events = [EarningsEvent("AAA", f"{D} 07:00", D, c.index[-41].date(), True)]

    def run(frames):
        ind = Indicators(*frames, cfg)
        ctx = DecisionContext(cfg=cfg, ind=ind, stocks=["AAA", "BBB", "CCC"], regime="ON", earnings=EarningsBook(events),
                              pf=Portfolio(cash=100), risk={}, is_rebalance=True, created_at="x",
                              add_sessions=lambda d, k: (pd.Timestamp(d) + pd.offsets.BDay(k)).date())
        orders, decs = decide(D, S, ctx)
        return [(x.key, round(x.notional or 0, 8)) for x in orders], [(d.ticker, d.action, d.reason_code) for d in decs]

    full = run((o, h, l, c, v))
    cut = run(tuple(x.loc[:pd.Timestamp(D)] for x in (o, h, l, c, v)))
    # scramble everything after D: decisions must not change
    scr = []
    for x in (o, h, l, c, v):
        y = x.copy()
        y.loc[y.index > pd.Timestamp(D)] *= 3.0
        scr.append(y)
    assert full == cut == run(tuple(scr))


def test_news_after_decision_time_is_ignored(monkeypatch, tmp_path, cfg):
    from papertrader import news as N
    L = Ledger(tmp_path / "l.sqlite")
    decision = dt.datetime(2026, 9, 23, 13, 0, tzinfo=UTC)
    items = [
        {"ticker": "AAA", "source": "yahoo", "provider": "X", "title": "Acme beats estimates and raises guidance", "summary": "",
         "url": "u1", "published_at": "2026-09-23T14:00:00Z", "retrieved_at": "2026-09-23T14:05:00Z"},  # AFTER decision
    ]
    monkeypatch.setattr(N, "fetch_yahoo", lambda t: [dict(i) for i in items])
    monkeypatch.setattr(N, "fetch_google", lambda t, n: [])
    svc = N.NewsService(L, {"AAA": "Acme Corp"}, cfg, decision)
    v = svc.check("AAA", "catalyst", {"reaction_session": "2026-09-22"})
    assert not v.ok and v.status == "unconfirmed"
    items[0]["published_at"] = "2026-09-23T12:30:00Z"  # now before the decision
    svc2 = N.NewsService(L, {"AAA": "Acme Corp"}, cfg, decision)
    v2 = svc2.check("AAA", "catalyst", {"reaction_session": "2026-09-22"})
    assert v2.ok and v2.status == "confirmed"


def test_news_hard_negative_vetoes(monkeypatch, tmp_path, cfg):
    from papertrader import news as N
    L = Ledger(tmp_path / "l.sqlite")
    decision = dt.datetime(2026, 9, 23, 13, 0, tzinfo=UTC)
    items = [{"ticker": "AAA", "source": "google_news", "provider": "Y", "title": "Acme beats estimates", "url": "a",
              "published_at": "2026-09-22T21:00:00Z", "retrieved_at": "2026-09-23T12:59:00Z"},
             {"ticker": "AAA", "source": "google_news", "provider": "Z", "title": "Acme announces $2 billion public offering", "url": "b",
              "published_at": "2026-09-22T22:00:00Z", "retrieved_at": "2026-09-23T12:59:00Z"}]
    monkeypatch.setattr(N, "fetch_yahoo", lambda t: [])
    monkeypatch.setattr(N, "fetch_google", lambda t, n: [dict(i) for i in items])
    v = N.NewsService(L, {"AAA": "Acme Corp"}, cfg, decision).check("AAA", "catalyst", {"reaction_session": "2026-09-23"})
    assert not v.ok and v.status == "vetoed" and "offering" in v.reason


def test_news_outage_skips_trade(monkeypatch, tmp_path, cfg):
    from papertrader import news as N
    L = Ledger(tmp_path / "l.sqlite")

    def boom(*a, **k):
        raise ConnectionError("down")
    monkeypatch.setattr(N, "fetch_yahoo", boom)
    monkeypatch.setattr(N, "fetch_google", boom)
    monkeypatch.setattr(N.time, "sleep", lambda s: None)
    v = N.NewsService(L, {"AAA": "Acme"}, cfg, dt.datetime(2026, 9, 23, 13, tzinfo=UTC)).check("AAA", "momentum", {})
    assert not v.ok and v.status == "unavailable"


def test_momentum_entries_blocked_when_earnings_calendar_incomplete(cfg):
    o, h, l, c, v = _synthetic()
    D, S = c.index[-2].date(), c.index[-1].date()
    base = dict(cfg=cfg, ind=Indicators(o, h, l, c, v, cfg), stocks=["AAA", "BBB", "CCC"], regime="ON", earnings=EarningsBook([]),
                pf=Portfolio(cash=100), risk={}, is_rebalance=True, created_at="x",
                add_sessions=lambda d, k: (pd.Timestamp(d) + pd.offsets.BDay(k)).date())
    ok_orders, _ = decide(D, S, DecisionContext(**base))
    bad_orders, decs = decide(D, S, DecisionContext(**base, earnings_complete=False))
    assert not [x for x in bad_orders if x.sleeve == "momentum"]
    assert any(d.reason_code == "EARNINGS_DATA_MISSING" for d in decs)


def test_state_dump_restore_round_trip(tmp_path, monkeypatch, cfg):
    """Ledgers survive the text round trip used for cloud storage: same rows, same hash chain, guards intact."""
    from papertrader import statesync
    L = Ledger(tmp_path / "data" / "ledger_primary.sqlite")
    L.start_run("r", "t")
    L.freeze({"start_date": "2026-09-23", "end_date": "2026-10-22", "starting_cash": 100, "report_days": [7]},
             {"id": "primary", "strategy": "x"}, "v", "sha", "u")
    o = order("k1", "AAA", "BUY", notional=20)
    L.insert_order(o)
    fills, _ = Broker(cfg).execute_open(Portfolio(cash=100), "2026-09-23", [o], {"AAA": 10.0}, {}, "t", "test")
    L.record_fill(fills[0])
    L.close()
    monkeypatch.setattr(statesync, "ROOT", tmp_path)
    monkeypatch.setattr(statesync, "STATE_DIR", tmp_path / "state")
    monkeypatch.setattr(statesync, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(statesync, "MARKER", tmp_path / "data" / ".restored.json")
    monkeypatch.setattr(statesync, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(statesync, "load_experiment", lambda: {"books": [{"id": "primary", "ledger": "data/ledger_primary.sqlite"}]})
    assert statesync.dump() == ["ledger_primary.sql"]
    before = sqlite3.connect(tmp_path / "data" / "ledger_primary.sqlite")
    rows = {t: before.execute(f"SELECT * FROM {t}").fetchall() for t in ("fills", "orders", "events", "experiment")}
    before.close()
    (tmp_path / "data" / "ledger_primary.sqlite").unlink()
    assert statesync.restore() == ["primary"]
    L2 = Ledger(tmp_path / "data" / "ledger_primary.sqlite")
    assert {t: [tuple(r) for r in L2.db.execute(f"SELECT * FROM {t}").fetchall()] for t in rows} == rows
    assert L2.verify_chain()[0]
    with pytest.raises(sqlite3.DatabaseError):
        L2.db.execute("DELETE FROM fills")
    assert statesync.restore() == []  # unchanged dump -> nothing to do


def test_watchdog_starts_missed_key_runs():
    from papertrader.live import watchdog_check
    from papertrader.nyse_calendar import ET
    d = dt.date(2026, 9, 23)
    at = lambda h, m: dt.datetime.combine(d, dt.time(h, m), ET)  # noqa: E731
    run = lambda h, m: {"createdAt": at(h, m).astimezone(UTC).isoformat().replace("+00:00", "Z"), "status": "completed"}  # noqa: E731
    st = {"enabled": True, "running": False, "runs": [run(2, 0)]}
    assert watchdog_check(st, at(9, 20)) is None                   # before the open window
    assert watchdog_check(st, at(10, 0)) == "record the open"      # the 09:43 run never came
    st["runs"].append(run(9, 50))
    assert watchdog_check(st, at(10, 0)) is None                   # it did run
    assert watchdog_check(st, at(10, 30)) is not None               # 40 min without a run during the session
    assert watchdog_check(st, at(17, 30)) == "close out the day and decide the next open"
    assert watchdog_check({**st, "running": True}, at(17, 30)) is None
    assert watchdog_check({**st, "enabled": False}, at(17, 30)) is None
    assert watchdog_check(st, dt.datetime(2026, 9, 26, 17, 30, tzinfo=ET)) is None  # Saturday
