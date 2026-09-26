import datetime as dt

import pytest

from papertrader import daily_report as DR
from papertrader.nyse_calendar import ET

EXP = {"start_date": "2026-09-23", "end_date": "2026-10-22", "starting_cash": 100.0, "books": [
    {"id": "daytrade", "name": "Day trading", "strategy": "config/strategy_daytrade_v1.json", "start_date": "2026-09-24"},
    {"id": "mm", "name": "Market maker", "strategy": "config/strategy_mm_v1.json", "start_date": "2026-09-25"}]}


def fill(fid, side, t, when, pnl=None, code="X"):
    return {"fill_id": fid, "side": side, "ticker": t, "fill_price": 1.0, "price_time": when, "session": when[:10],
            "realized_pnl": pnl, "reason_code": code}


def fake_state(book, exp, n_decisions=1):
    if book["id"] == "daytrade":
        return {"frozen": True, "issues": [], "snapshots": [{"session": "2026-09-24", "equity": 99.0}, {"session": "2026-09-25", "equity": 101.0}],
                "fills": [fill(1, "BUY", "AAA", "2026-09-25T09:40:00-04:00", code="ORB_BREAKOUT"),
                          fill(2, "SELL", "AAA", "2026-09-25T15:59:00-04:00", 2.0, "CLOSE_EXIT")]}
    # processed (session) on the 26th, but it happened on the evening of the 25th in New York
    return {"frozen": True, "issues": [], "snapshots": [{"session": "2026-09-25", "equity": 100.5}],
            "fills": [dict(fill(3, "BUY", "ETH Up", "2026-09-25T21:34:00-04:00"), session="2026-09-26")]}


def test_daily_report(tmp_path, monkeypatch):
    monkeypatch.setattr(DR, "book_state", fake_state)
    now = dt.datetime(2026, 9, 26, 0, 50, tzinfo=ET)
    made = DR.maybe_generate_daily(EXP, now, tmp_path)
    assert made == ["daily_2026-09-23", "daily_2026-09-24", "daily_2026-09-25"]
    r = DR.daily_list(tmp_path)[0]
    assert r["date"] == "2026-09-25" and r["day"] == 3
    rows = {x["id"]: x for x in r["rows"]}
    assert rows["daytrade"]["change"] == pytest.approx(2.0) and rows["daytrade"]["wins"] == 1 and rows["daytrade"]["trades"] == 2
    assert rows["mm"]["change"] == pytest.approx(0.5) and rows["mm"]["trades"] == 1  # grouped by when it happened
    assert r["total_before"] == pytest.approx(199.0) and r["total_end"] == pytest.approx(201.5)
    md = (tmp_path / "daily_2026-09-25.md").read_text()
    assert "BUY AAA" in md and "broke above" in md
    assert DR.maybe_generate_daily(EXP, now, tmp_path) == []  # never regenerated or overwritten
    with pytest.raises(FileExistsError):
        DR.generate(EXP, dt.date(2026, 9, 25), now, tmp_path)


def test_daily_report_waits_for_end_of_day_values(tmp_path, monkeypatch):
    monkeypatch.setattr(DR, "book_state", lambda b, e, n_decisions=1: {"frozen": True, "issues": [], "fills": [], "snapshots": []})
    assert DR.maybe_generate_daily(EXP, dt.datetime(2026, 9, 26, 1, 0, tzinfo=ET), tmp_path) == ["daily_2026-09-23", "daily_2026-09-24"]
    # by noon the next day it goes ahead and says what is missing
    assert DR.maybe_generate_daily(EXP, dt.datetime(2026, 9, 26, 12, 30, tzinfo=ET), tmp_path) == ["daily_2026-09-25"]
    assert "Market maker" in DR.daily_list(tmp_path)[0]["missing"]
