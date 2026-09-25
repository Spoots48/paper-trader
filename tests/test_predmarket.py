"""Prediction-market book: pricing math, fees, order-book walking."""
import pytest

from papertrader.predmarket import fair_prob_up, kelly_budget, taker_fee_per_share, walk_book
from papertrader.config import ROOT, load_json

CFG = load_json(ROOT / "config/strategy_pm_v1.json")


def test_fee_matches_polymarket_docs():
    assert taker_fee_per_share(0.5, 0.07) * 100 == pytest.approx(1.75)  # docs: 100 shares at 50c -> $1.75
    assert taker_fee_per_share(0.97, 0.07) < taker_fee_per_share(0.5, 0.07)


def test_fair_prob_behaves():
    # just started, price at the start level: coin flip
    assert fair_prob_up(100, 100, 100, 0.01, 14.8, 0.001) == pytest.approx(0.5, abs=0.02)
    # far above the start with little time left: near certain; far below: near zero
    assert fair_prob_up(100, 101, 101, 0.9, 1.5, 0.001) > 0.99
    assert fair_prob_up(100, 99, 99, 0.9, 1.5, 0.001) < 0.01
    # it's an average: a late spike above the start can't overturn a window that averaged well below it
    assert fair_prob_up(100, 99.0, 100.5, 0.9, 1.5, 0.0005) < 0.05
    # more volatility -> less certainty
    assert fair_prob_up(100, 100.2, 100.2, 0.5, 30, 0.002) < fair_prob_up(100, 100.2, 100.2, 0.5, 30, 0.0005)


def test_walk_book_stops_when_edge_runs_out():
    asks = [(0.80, 10), (0.85, 10), (0.95, 100)]
    f = walk_book(asks, prob=0.93, budget=100, min_edge=0.05, fee_rate=0.07)
    assert f.levels == 2 and f.shares == pytest.approx(20)  # 0.95 no longer clears a 5c edge
    assert f.cost == pytest.approx(10 * (0.80 + 0.07 * 0.8 * 0.2) + 10 * (0.85 + 0.07 * 0.85 * 0.15))
    assert walk_book(asks, prob=0.83, budget=100, min_edge=0.05, fee_rate=0.07) is None


def test_kelly_sizing_caps():
    assert kelly_budget(0.9, 0.5, 100, CFG, 0) == pytest.approx(10.0)  # capped at 10% per market
    assert kelly_budget(0.9, 0.5, 100, CFG, 55) == pytest.approx(5.0)  # 60% total exposure cap
    assert kelly_budget(0.5, 0.6, 100, CFG, 0) == 0.0
