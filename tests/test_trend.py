import numpy as np
import pandas as pd
import pytest

from papertrader.trend import rebalance_orders, trend_weights

ASSETS = ["A", "B"]


def _closes(a_end, b_end, n=300):
    idx = pd.date_range("2025-01-01", periods=n, freq="B")
    return pd.DataFrame({"A": np.linspace(100, a_end, n), "B": np.linspace(100, b_end, n)}, index=idx)


def test_uptrend_gets_full_weight_downtrend_none():
    w, d = trend_weights(_closes(150, 60), ASSETS, [8, 10, 12])
    assert w == {"A": 0.5} and d["B"]["above_sma_months"] == [] and d["A"]["weight_fraction"] == 1.0


def test_partial_vote_gives_one_third_weight():
    # 132 days at 200, 147 days at 100, last 21 days at 110: above the 8-month average (~101) but below the 10- and 12-month ones
    idx = pd.date_range("2025-01-01", periods=300, freq="B")
    vals = [200.0] * 132 + [100.0] * 147 + [110.0] * 21
    c = pd.DataFrame({"A": vals, "B": vals}, index=idx)
    w, d = trend_weights(c, ASSETS, [8, 10, 12])
    assert d["A"]["above_sma_months"] == [8] and w["A"] == pytest.approx(0.5 / 3)


def test_short_history_raises_instead_of_guessing():
    with pytest.raises(ValueError):
        trend_weights(_closes(150, 150, n=100), ASSETS, [8, 10, 12])


def _kw(**o):
    base = dict(equity=100.0, cash=100.0, qty={}, prices={"A": 10.0, "SHY": 80.0}, weights={"A": 0.5}, cash_asset="SHY",
                buffer=0.01, min_order=1.0, band_fraction=0.03)
    base.update(o)
    return rebalance_orders(**base)


def test_first_rebalance_buys_targets_and_parks_rest_in_cash_asset():
    o = {x["ticker"]: x for x in _kw()}
    assert o["A"]["side"] == "BUY" and o["SHY"]["side"] == "BUY"
    assert o["A"]["notional"] == pytest.approx(0.5 * 99.0, rel=0.02)
    assert sum(x["notional"] for x in o.values()) <= 99.0


def test_exit_sells_whole_position_and_funds_cash_asset():
    o = _kw(cash=1.0, qty={"A": 5.0}, weights={})
    sells = [x for x in o if x["side"] == "SELL"]
    assert sells and sells[0]["ticker"] == "A" and sells[0]["qty"] is None
    assert o[0]["side"] == "SELL"
    assert sum(x["notional"] for x in o if x["side"] == "BUY") <= (1.0 + 0.998 * 50.0 - 1.0) * 0.995 + 1e-9


def test_inside_band_no_trades():
    assert _kw(cash=1.0, qty={"A": 4.95, "SHY": 0.62}, prices={"A": 10.0, "SHY": 80.0}, equity=100.0) == []


def test_never_spends_more_than_available():
    o = _kw(equity=100.0, cash=10.0, qty={"A": 9.0}, weights={"A": 0.2})
    assert sum(x.get("notional", 0) for x in o if x["side"] == "BUY") <= 10.0 + 0.998 * sum(x["value"] for x in o if x["side"] == "SELL")


def test_engine_uses_its_own_ledgers_start_date_not_the_experiments(tmp_path):
    import datetime as dt

    from papertrader.config import UNIVERSE_PATH, load_json, sha256_file, ROOT
    from papertrader.ledger import Ledger
    from papertrader.trend import TrendEngine

    cfg_path = ROOT / "config" / "strategy_trend_v1.json"
    cfg = load_json(cfg_path)
    exp = {"name": "x", "start_date": "2026-09-23", "end_date": "2026-10-22", "starting_cash": 100.0, "report_days": [7]}
    book = {"id": "trend", "name": "t", "subtitle": "s", "strategy": "config/strategy_trend_v1.json", "ledger": "x", "start_date": "2026-10-05"}
    L = Ledger(tmp_path / "l.sqlite")
    L.freeze({**exp, "start_date": "2026-10-05"}, book, cfg["version"], sha256_file(cfg_path), sha256_file(UNIVERSE_PATH))
    eng = TrendEngine(L, None, cfg, {**exp, "book": "trend"}, dt.datetime(2026, 10, 5, 8, tzinfo=dt.timezone.utc))
    assert eng.start == dt.date(2026, 10, 5)


def test_session_windows_and_exactly_one_unit():
    idx = pd.date_range("2025-01-01", periods=260, freq="B")
    c = pd.DataFrame({"A": np.linspace(100, 160, 260), "B": np.linspace(160, 100, 260)}, index=idx)
    w, d = trend_weights(c, ASSETS, sessions=[50, 100, 200])
    assert w == {"A": 0.5} and d["A"]["above_sma_sessions"] == [50, 100, 200] and d["B"]["above_sma_sessions"] == []
    with pytest.raises(ValueError):
        trend_weights(c, ASSETS)
    with pytest.raises(ValueError):
        trend_weights(c, ASSETS, months=[8], sessions=[50])
    with pytest.raises(ValueError):
        trend_weights(c.iloc[:150], ASSETS, sessions=[50, 100, 200])


def test_rebalance_schedule_weekly_monthly_and_first():
    import datetime as dt

    from papertrader.trend import is_rebalance_day
    fri, mon = dt.date(2026, 10, 2), dt.date(2026, 10, 5)
    wed, thu = dt.date(2026, 10, 7), dt.date(2026, 10, 8)
    assert is_rebalance_day(mon, fri, "week-end", False)
    assert not is_rebalance_day(thu, wed, "week-end", False)
    assert is_rebalance_day(dt.date(2026, 10, 1), dt.date(2026, 9, 30), "month-end", False)
    assert not is_rebalance_day(thu, wed, "month-end", False)
    assert is_rebalance_day(thu, wed, "week-end", True)
    with pytest.raises(ValueError):
        is_rebalance_day(thu, wed, "daily", False)
