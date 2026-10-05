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
