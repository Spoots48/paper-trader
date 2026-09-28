import copy

import pytest

from papertrader.config import ROOT, load_json
from papertrader.intraday import DayState, process_bar


def config():
    cfg = copy.deepcopy(load_json(ROOT / 'config/strategy_daytrade_v1.json'))
    cfg['risk'].update(per_trade_risk=.0025, daily_loss_limit=.01)
    cfg['exit'].update(trail_activate_r=2., trail_distance_r=1.)
    return cfg


def state():
    c = dict(ticker='X', rank=1, rvol=4, first_high=100, trigger=100, adv_usd=2e9,
             atr=10, stop_distance=10, stop_price=90)
    return DayState('d', 100., 100., candidates=[c], pending=['X'])


def bar(st, values, cfg=None):
    return process_bar(st, 't', {'X': values}, cfg or config(), is_last_bar=False, entries_allowed=True)


def test_size_includes_stop_distance_and_both_sides_of_costs():
    st = state()
    ev = bar(st, (100, 101, 99, 100))
    buy = ev[0]
    sell = bar(st, (100, 101, 89, 90))[0]
    assert buy.kind == 'BUY' and sell.kind == 'SELL'
    assert -.25 - 1e-8 <= sell.realized_pnl < -.249
    assert st.cash == pytest.approx(99.75, abs=.0001)


def test_no_entry_when_remaining_daily_budget_cannot_fund_minimum():
    st = state()
    st.cash = 99.05  # realized loss earlier in session
    assert not any(e.kind == 'BUY' for e in bar(st, (100, 101, 99, 100)))


def test_trailing_stop_uses_completed_close_and_only_next_bar():
    st = state()
    c = st.candidates[0]
    c['stop_price'], c['stop_distance'] = 99, 1
    bar(st, (100, 100.5, 99.5, 100))
    # Close arms trail at 102; low was 100.5, but it cannot hit a stop
    # which did not exist until after this bar completed.
    ev = bar(st, (100.5, 103.5, 100.5, 103))
    assert not ev and st.positions['X']['stop'] == pytest.approx(102)
    ev = bar(st, (101.5, 102, 101, 101.5))
    assert ev[0].kind == 'SELL' and ev[0].ref_price == 101.5
    assert ev[0].realized_pnl > 0  # gap fills at actual open, never the nicer stop


def test_trailing_stop_does_not_tighten_on_unrealized_intrabar_spike():
    st = state()
    st.candidates[0]['stop_price'] = 99
    bar(st, (100, 103, 99.5, 100))
    assert st.positions['X']['stop'] == 99
