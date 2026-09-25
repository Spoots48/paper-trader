"""Crypto odds bot v2: each fix for v1's losses has a test."""
import pytest

from papertrader.config import ROOT, load_json
from papertrader.pm2 import decide_v2, fair_prob_digital

CFG = load_json(ROOT / "config/strategy_pm_v2.json")


def test_digital_close_vs_open_math():
    assert fair_prob_digital(100, 100, 30, 0.001) == pytest.approx(0.5)
    # same move, more time left -> less certain (v1 used averaging math and was far too sure)
    assert fair_prob_digital(100, 100.3, 50, 0.001) < fair_prob_digital(100, 100.3, 5, 0.001)
    assert fair_prob_digital(100, 99.7, 5, 0.001) == pytest.approx(1 - fair_prob_digital(100, 100.3, 5, 0.001), abs=0.01)


def test_big_disagreement_with_market_is_treated_as_model_error():
    # v1 bought at 8.8c because its model said 97%; v2 refuses
    d = decide_v2(100, 100.5, 3, 0.0006, 0.5, {"Up": 0.10, "Down": 0.91}, 0.09, CFG)
    assert "skip" in d and "model error" in d["skip"]


def test_no_chasing_favorites_above_75c():
    d = decide_v2(100, 100.15, 20, 0.0006, 0.5, {"Up": 0.82, "Down": 0.19}, 0.81, CFG)
    assert "skip" in d


def test_entry_timing_window():
    assert "timing" in decide_v2(100, 100, 50, 0.0006, 0.05, {"Up": 0.5, "Down": 0.5}, 0.5, CFG)["skip"]
    assert "timing" in decide_v2(100, 100, 5, 0.0006, 0.9, {"Up": 0.5, "Down": 0.5}, 0.5, CFG)["skip"]


def test_trades_when_anchored_edge_clears_fees():
    # market lags a real move: model ~83% Up, market mid 64% -> anchored ~71% vs 65c + fee
    d = decide_v2(100, 100.45, 60, 0.0006, 0.4, {"Up": 0.65, "Down": 0.37}, 0.64, CFG)
    assert d.get("side") == "Up" and d["edge"] >= CFG["entry"]["min_edge"]
    assert 0.64 < d["q"] < d["model_up"]  # pulled toward the market, not the raw model
