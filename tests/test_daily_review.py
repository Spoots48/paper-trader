import datetime as dt
import sqlite3

from papertrader.daily_review import maybe_generate_review, render, review_book
from papertrader import daily_review as R


def _ledger(path, fills, snaps, issues=()):
    c = sqlite3.connect(path)
    c.executescript("""CREATE TABLE snapshots(session TEXT, equity REAL, spy_bh_equity REAL);
    CREATE TABLE fills(fill_id INTEGER PRIMARY KEY, session TEXT, ticker TEXT, side TEXT, reason_code TEXT, realized_pnl REAL, cost_usd REAL);
    CREATE TABLE decisions(decision_id INTEGER PRIMARY KEY, action TEXT, reason TEXT, created_at TEXT);
    CREATE TABLE data_issues(occurred_at TEXT, severity TEXT, component TEXT, message TEXT);""")
    c.executemany("INSERT INTO snapshots VALUES (?,?,?)", snaps)
    c.executemany("INSERT INTO fills(session,ticker,side,reason_code,realized_pnl,cost_usd) VALUES (?,?,?,?,?,?)", fills)
    c.executemany("INSERT INTO data_issues VALUES (?,?,?,?)", issues)
    c.execute("INSERT INTO decisions(action,reason,created_at) VALUES ('INFO','0 stocks in play selected','2026-10-06T13:40')")
    c.commit()
    c.close()


def test_review_flags_stop_heavy_losing_day_and_gates_changes(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "ROOT", tmp_path)
    fills = [("2026-10-06", t, "SELL", "STOP", -0.2, 0.05) for t in "ABC"]
    _ledger(tmp_path / "l.sqlite", fills, [("2026-10-05", 100.0, 100.0), ("2026-10-06", 99.0, 100.5)])
    r = review_book({"id": "x", "name": "X", "ledger": "l.sqlite"}, dt.date(2026, 10, 6))
    assert round(r["day_pct"], 4) == -0.01 and round(r["spy_pct"], 4) == 0.005
    assert any("stop-outs and no winners" in f for f in r["flags"]) and any("lost" in f for f in r["flags"])
    assert "no rule change is supported yet" in r["gate"]
    assert "No strategy was changed" in render(dt.date(2026, 10, 6), [r])


def test_quiet_day_explains_why_and_missing_ledger_is_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "ROOT", tmp_path)
    _ledger(tmp_path / "l.sqlite", [], [("2026-10-05", 100.0, None), ("2026-10-06", 100.0, None)])
    r = review_book({"id": "x", "name": "X", "ledger": "l.sqlite"}, dt.date(2026, 10, 6))
    assert "No trades today. Why: 0 stocks in play selected" in render(dt.date(2026, 10, 6), [r])
    assert review_book({"id": "y", "name": "Y", "ledger": "nope.sqlite"}, dt.date(2026, 10, 6))["flags"] == ["ledger missing"]


def test_generated_once_after_close_only_on_session_days(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "ROOT", tmp_path)
    _ledger(tmp_path / "l.sqlite", [], [("2026-10-05", 100.0, None), ("2026-10-06", 100.0, None)])
    exp = {"start_date": "2026-09-23", "end_date": "2026-10-22", "books": [{"id": "x", "name": "X", "ledger": "l.sqlite"}]}
    et = R.ET
    before = dt.datetime(2026, 10, 6, 15, 0, tzinfo=et).astimezone(dt.timezone.utc)
    after = dt.datetime(2026, 10, 6, 17, 0, tzinfo=et).astimezone(dt.timezone.utc)
    weekend = dt.datetime(2026, 10, 10, 17, 0, tzinfo=et).astimezone(dt.timezone.utc)
    assert maybe_generate_review(exp, before, tmp_path) is None
    assert maybe_generate_review(exp, weekend, tmp_path) is None
    assert maybe_generate_review(exp, after, tmp_path) == "review_2026-10-06"
    assert maybe_generate_review(exp, after, tmp_path) is None
