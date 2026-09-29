"""Engine-level regression tests for protection across runs, marks and strategy changes."""
import copy
import datetime as dt

import pytest

from papertrader.config import ROOT, load_json
from papertrader.ledger import Ledger
from papertrader.nyse_calendar import UTC
from papertrader.pm_engine2 import PMEngine2
from papertrader.mm_engine import MMEngine

NOW = dt.datetime(2026, 9, 28, 15, tzinfo=UTC)


def engine(tmp_path, cls=PMEngine2):
    cfg = copy.deepcopy(load_json(ROOT / ('config/strategy_mm_v1.json' if cls is MMEngine else 'config/strategy_pm_v2.json')))
    cfg['risk'].update(daily_loss_limit=.03, drawdown_halt=.10,
                       profit_lock_activation=.02, profit_lock_giveback=.50)
    ledger = Ledger(tmp_path / 'risk.sqlite')
    ledger.freeze(dict(start_date='2026-09-25', end_date='2026-10-22', starting_cash=100, report_days=[]),
                  dict(id='test', strategy='test'), 'test', 'test', 'test')
    return cls(ledger, None, cfg, {}, NOW)


def test_daily_loss_stop_stays_latched_after_recovery_and_restart(tmp_path):
    e = engine(tmp_path)
    assert e.risk_gate({}, 100) is None
    assert 'daily loss' in e.risk_gate({}, 96)
    restarted = PMEngine2(e.L, None, e.cfg, {}, NOW + dt.timedelta(minutes=15))
    assert 'daily loss' in restarted.risk_gate({}, 99)
    restarted.now += dt.timedelta(days=1)
    assert restarted.risk_gate({}, 99) is None


def test_profit_giveback_locks_day_and_survives_restart(tmp_path):
    e = engine(tmp_path)
    e.risk_gate({}, 100)
    assert e.risk_gate({}, 104) is None
    assert 'profit' in e.risk_gate({}, 101.99)
    assert 'profit' in PMEngine2(e.L, None, e.cfg, {}, NOW).risk_gate({}, 104)


@pytest.mark.parametrize('cls', [PMEngine2, MMEngine])
def test_integrity_failure_blocks_new_risk_but_still_settles(tmp_path, cls):
    e = engine(tmp_path, cls)
    e.L.set_state('strategy_integrity_ok', False)
    calls = []
    e.settle = lambda: calls.append('settle')
    e.mark = lambda: True
    e.snapshot = lambda: None
    if cls is MMEngine:
        e.process_orders = lambda **kwargs: None
        e.quote = lambda *args: calls.append('entry')
    else:
        e.scan = lambda *args: calls.append('entry')
    e.step()
    assert calls == ['settle']


@pytest.mark.parametrize('cls', [PMEngine2, MMEngine])
def test_marks_refreshed_before_any_new_risk(tmp_path, cls):
    e = engine(tmp_path, cls)
    e.settle = lambda: None
    e.snapshot = lambda: None
    calls = []
    e.mark = lambda: calls.append('mark') or True
    if cls is MMEngine:
        e.process_orders = lambda **kwargs: None
        e.quote = lambda *args: calls.append('entry')
    else:
        e.scan = lambda *args: calls.append('entry')
    e.step()
    assert calls.index('mark') < calls.index('entry')


@pytest.mark.parametrize('cls', [PMEngine2, MMEngine])
def test_missing_marks_blocks_new_risk(tmp_path, cls):
    e = engine(tmp_path, cls)
    e.settle = lambda: None
    e.snapshot = lambda: None
    e.mark = lambda: False
    calls = []
    if cls is MMEngine:
        e.process_orders = lambda **kwargs: None
        e.quote = lambda *args: calls.append('entry')
    else:
        e.scan = lambda *args: calls.append('entry')
    e.step()
    assert calls == []


def test_settlement_floor_handles_pairs_and_one_sided_fills():
    from papertrader.pm_risk import settlement_floor
    pos = {'u': {'slug': 'x', 'side': 'Up', 'shares': 5, 'cost': 2.5},
           'd': {'slug': 'x', 'side': 'Down', 'shares': 5, 'cost': 2.4}}
    assert settlement_floor(95.1, pos) == pytest.approx(100.1)
    quotes = [{'slug': 'y', 'outcome': 'Up', 'shares': 5, 'price': .48},
              {'slug': 'y', 'outcome': 'Down', 'shares': 5, 'price': .50}]
    assert settlement_floor(95.1, pos, quotes) == pytest.approx(97.6)


def test_empty_book_on_unresolved_market_does_not_invent_zero_loss(tmp_path):
    e = engine(tmp_path)
    e._save_positions = lambda positions: None
    e.L.set_state('pm_positions', {'x': dict(token='u', label='x', slug='x', side='Up', shares=5,
                                            cost=2.5, mark=.01, end='2026-09-28T14:00:00Z')})
    e.book = lambda token: ([], [])
    assert e.mark() is False
    assert 'mark' not in e.L.get_state('pm_positions')['x']


def test_directional_bet_cannot_spend_beyond_remaining_daily_loss_budget(tmp_path, monkeypatch):
    import json
    from papertrader import pm_engine2
    e = engine(tmp_path)
    e.risk_gate({}, 100)
    e.L.set_state('cash', 99)  # one dollar lost before this signal
    e.cfg['markets']['assets'] = {'BTC': {'binance': 'BTCUSDT'}}
    e.cfg['markets']['windows_minutes'] = [60]
    e.cfg['entry']['min_depth_usd'] = 1
    start = NOW - dt.timedelta(minutes=20)
    e.prices = lambda symbol: {'candles': {int(NOW.timestamp())-i*60: (100,100) for i in range(62)},
                                's_now':100, 'tick_time':NOW.timestamp()}
    e.slugs = lambda *args: ['test']
    e.event = lambda slug: dict(slug='test', title='Test', markets=[dict(eventStartTime=start.isoformat(),
        endDate=(NOW+dt.timedelta(minutes=40)).isoformat(), outcomes=json.dumps(['Up','Down']), clobTokenIds=json.dumps(['u','d']))])
    e.book = lambda token: ([(.30, 100)], [(.29, 100)])
    e.book_times = {'u': NOW.timestamp(), 'd': NOW.timestamp()}
    monkeypatch.setattr(pm_engine2, 'decide_v2', lambda *args: dict(side='Up', q=.8, ask=.3, unit=.3147,
                                                               edge=.4853, model_up=.8, mid_up=.8))
    e.scan({}, 99)
    assert e.L.get_state('cash') >= 97  # only $2 of remaining loss capacity
    assert e.L.get_state('cash') < 97.01
    assert len(e.L.get_state('pm_positions')) == 1
