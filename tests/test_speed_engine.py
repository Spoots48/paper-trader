import datetime as dt

import pytest

from papertrader import speed_engine as SE
from papertrader.config import ROOT, UNIVERSE_PATH, load_json, sha256_file
from papertrader.ledger import Ledger
from papertrader.nyse_calendar import ET, session_open

S = dt.date(2026, 10, 7)


class FakeClient:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeMD:
    def __init__(self):
        self.db = __import__("sqlite3").connect(":memory:")
        self.db.row_factory = __import__("sqlite3").Row
        self.db.execute(SE.FIRST_BARS_SCHEMA) if hasattr(SE, "FIRST_BARS_SCHEMA") else None

    def update_daily(self, *a, **k):
        return {"failed": []}

    def bar(self, *a, **k):
        return {"open": 100.0, "close": 100.0}

    def _download(self, *a, **k):
        return None


def _bars(n=390, step=0.0003):
    out, px = {}, 100.0
    t0 = session_open(S)
    for i in range(n):
        o, c = px, px * (1 + step)
        out[(t0 + dt.timedelta(minutes=i)).astimezone(ET).isoformat()] = {"AAA": (o, c * 1.0001, o * 0.9999, c, 1000.0 + (i % 5))}
        px = c
    return out


def _engine(tmp_path, monkeypatch, p=0.9, client=FakeClient, **speed):
    cfg = load_json(ROOT / "config" / "strategy_speed_v1.json")
    cfg["universe"]["tickers"] = ["AAA"]
    cfg["speed"].update(speed)
    exp = {"name": "x", "start_date": "2026-10-07", "end_date": "2026-10-22", "starting_cash": 100.0, "report_days": [7]}
    book = {"id": "speed", "name": "s", "subtitle": "s", "strategy": "config/strategy_speed_v1.json", "ledger": "x", "start_date": "2026-10-07"}
    L = Ledger(tmp_path / "l.sqlite")
    L.freeze(exp, book, cfg["version"], sha256_file(ROOT / "config" / "strategy_speed_v1.json"), sha256_file(UNIVERSE_PATH))
    L.start_run("r", "t")
    now = dt.datetime(2026, 10, 7, 17, 0, tzinfo=ET).astimezone(dt.timezone.utc)
    e = SE.SpeedEngine(L, FakeMD(), cfg, {**exp, "book": "speed"}, now, client_factory=client, root=tmp_path)
    monkeypatch.setattr(e, "_bars_v", lambda s: _bars())
    monkeypatch.setattr(e, "ask_jev", lambda c, t, f, m: p)
    monkeypatch.setattr(e, "_init_benchmark", lambda s: None)
    return e, L


def test_jev_drives_entries_costs_are_charged_and_book_ends_flat(tmp_path, monkeypatch):
    e, L = _engine(tmp_path, monkeypatch)
    e.step()
    fills = [dict(r) for r in L.db.execute("SELECT * FROM fills ORDER BY fill_id")]
    buys = [f for f in fills if f["side"] == "BUY"]
    sells = [f for f in fills if f["side"] == "SELL"]
    assert len(buys) > 20 and len(buys) == len(sells)
    assert all(f["cost_bps"] > 0 for f in fills)
    assert not L.get_state(f"dt:{S}")["positions"] and L.get_state(f"dt:{S}")["closed"]
    assert L.db.execute("SELECT 1 FROM snapshots WHERE session=?", (S.isoformat(),)).fetchone()
    d = L.db.execute("SELECT metrics FROM decisions WHERE action='BUY' LIMIT 1").fetchone()["metrics"]
    assert '"p": 0.9' in d and (tmp_path / SE.LOG).exists()


def test_fill_happens_after_the_decision_bar_plus_delay(tmp_path, monkeypatch):
    e, L = _engine(tmp_path, monkeypatch, entry_delay_bars=1)
    e.step()
    b = dict(L.db.execute("SELECT price_time, reason FROM fills WHERE side='BUY' ORDER BY fill_id LIMIT 1").fetchone())
    decided = b["reason"].split("(decided ")[1].split(")")[0]
    gap = (dt.datetime.fromisoformat(b["price_time"]) - dt.datetime.fromisoformat(decided)).total_seconds() / 60
    assert gap == 2


def test_daily_jev_call_cap_is_respected(tmp_path, monkeypatch):
    e, L = _engine(tmp_path, monkeypatch, max_jev_calls_per_day=7)
    e.step()
    assert L.get_state(f"sp:{S}")["calls"] == 7
    assert len([1 for _ in open(tmp_path / SE.LOG)]) == 7


def test_below_threshold_jev_probability_means_no_trade(tmp_path, monkeypatch):
    e, L = _engine(tmp_path, monkeypatch, p=0.30)
    e.step()
    assert L.db.execute("SELECT COUNT(*) FROM fills").fetchone()[0] == 0


def test_no_jev_means_no_trading_and_no_fallback(tmp_path, monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    e, L = _engine(tmp_path, monkeypatch, client=None)
    out = e.step()
    assert L.db.execute("SELECT COUNT(*) FROM fills").fetchone()[0] == 0 and "Jev unavailable" in out
