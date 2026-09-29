"""Paper quote lifecycle, transaction rollback and no invented rebate cash."""
import datetime as dt
import json

import pytest

from papertrader.mm_engine import MMEngine
from test_pm_risk import engine


def market_maker(tmp_path):
    e = engine(tmp_path, MMEngine)
    e.cfg['sizing'].update(per_pair_fraction=.06, max_open_markets=1,
                           max_market_loss_fraction=.03, max_open_exposure=.10)
    e.cfg['markets']['assets'] = {'ETH': {'short': 'eth', 'long': 'ethereum'}}
    e.cfg['markets']['windows_minutes'] = [15]
    e.cfg['rebates']['credit_estimates_to_cash'] = False
    e.slugs = lambda *args: ['market']
    e.event = lambda slug: dict(slug='market', title='Test', markets=[dict(
        conditionId='cid', eventStartTime='2026-09-28T14:55:00Z', endDate='2026-09-28T15:10:00Z',
        outcomes=json.dumps(['Up', 'Down']), clobTokenIds=json.dumps(['u','d']))])
    e.book = lambda token: ([(.49 if token=='u' else .51, 100)], [(.48 if token=='u' else .50, 100)])
    e.book_times = {'u': e.now.timestamp(), 'd': e.now.timestamp()}
    e.risk_gate({}, 100)
    return e


def test_quote_batch_rolls_back_if_second_leg_fails(tmp_path, monkeypatch):
    e = market_maker(tmp_path)
    original = e.L.insert_order
    def insert(order):
        if order.ticker.endswith('Down'):
            raise RuntimeError('disk failure')
        return original(order)
    monkeypatch.setattr(e.L, 'insert_order', insert)
    with pytest.raises(RuntimeError):
        e.quote({}, 100)
    assert e.L.db.execute('select count(*) from orders').fetchone()[0] == 0
    assert not e.L.get_state('mm_orders')
    assert not e.L.get_state('mm_reserved')


def test_fill_rollback_retry_and_estimates_never_add_cash(tmp_path, monkeypatch):
    e = market_maker(tmp_path)
    e.quote({}, 100)
    quotes = e.L.get_state('mm_orders')
    reserved = e.L.get_state('mm_reserved')
    e.now += dt.timedelta(minutes=6)
    e.trades = lambda *args: [dict(timestamp=quotes[0]['placed_at']+60, side='SELL', outcome='Up', price=.47, size=100)]
    original = e.L.set_state
    def fail_last(key, value):
        if key == 'mm_orders':
            raise RuntimeError('crash after recording fill')
        original(key, value)
    monkeypatch.setattr(e.L, 'set_state', fail_last)
    with pytest.raises(RuntimeError):
        e.process_orders()
    assert e.L.get_state('cash') == 100
    assert e.L.get_state('mm_reserved') == reserved
    assert e.L.db.execute('select count(*) from fills').fetchone()[0] == 0
    monkeypatch.setattr(e.L, 'set_state', original)
    e.process_orders()
    cost = quotes[0]['shares'] * quotes[0]['price']
    assert e.L.get_state('cash') == pytest.approx(100-cost)
    assert e.L.get_state('mm_reserved') == pytest.approx(0)
    assert e.L.db.execute('select count(*) from dividends').fetchone()[0] == 0
    e.process_orders()
    assert e.L.get_state('cash') == pytest.approx(100-cost)
    assert e.L.db.execute('select count(*) from fills').fetchone()[0] == 1
    assert e.L.verify_chain()[0]


def test_cancellation_keeps_fills_before_cancel_and_ignores_later_trades(tmp_path):
    e = market_maker(tmp_path)
    e.quote({}, 100)
    quotes = e.L.get_state('mm_orders')
    e.now += dt.timedelta(minutes=2)
    e.trades = lambda *args: [dict(timestamp=quotes[0]['placed_at']+seconds, side='SELL',
                                   outcome='Up', price=.47, size=1) for seconds in (60, 180)]
    e.process_orders(cancel=True)
    assert e.L.db.execute('select qty from fills').fetchone()[0] == 1
    assert e.L.get_state('mm_orders') == []
    assert e.L.get_state('mm_reserved') == pytest.approx(0)


def test_missing_tape_keeps_reservation_even_after_an_hour(tmp_path):
    e = market_maker(tmp_path)
    e.quote({}, 100)
    reserved = e.L.get_state('mm_reserved')
    e.now += dt.timedelta(hours=2)
    def unavailable(*args):
        raise RuntimeError('offline')
    e.trades = unavailable
    e.process_orders()
    assert e.L.get_state('mm_reserved') == reserved
    assert len(e.L.get_state('mm_orders')) == 2
    assert e.L.get_state('cash') == 100


def test_settlement_waits_for_unreconciled_quotes_then_pays_once(tmp_path):
    e = market_maker(tmp_path)
    e.quote({}, 100)
    quotes = e.L.get_state('mm_orders')
    # Existing partial inventory on the SAME side as the delayed fill.
    p = dict(slug='market', side='Up', shares=1., cost=.48, token='u', label='ETH 15m 10:55 Up',
             end='2026-09-28T15:10:00Z', entry_time='2026-09-28T14:59:00Z', title='Test', prob=None)
    e.L.set_state('pm_positions', {'market:Up': p})
    e.L.set_state('cash', 99.52)
    e.now += dt.timedelta(minutes=20)
    e.event = lambda slug: dict(markets=[dict(closed=True, outcomes='["Up", "Down"]', outcomePrices='["1", "0"]')])
    e.settle()
    assert e.L.get_state('cash') == 99.52  # pending tape must be reconciled first
    assert e.L.db.execute('select count(*) from fills').fetchone()[0] == 0
    e.trades = lambda *args: [dict(timestamp=quotes[0]['placed_at']+60, side='SELL', outcome='Up', price=.47, size=100)]
    e.process_orders()
    e.settle()
    q = quotes[0]['shares']
    assert e.L.get_state('cash') == pytest.approx(99.52-q*.48+(q+1))
    assert e.L.get_state('pm_positions') == {}
    e.settle()
    assert e.L.db.execute("select count(*) from fills where side='SELL'").fetchone()[0] == 1


def test_cooldown_blocks_new_market_but_allows_risk_reducing_completion(tmp_path,monkeypatch):
    from papertrader import mm_engine
    e=market_maker(tmp_path)
    monkeypatch.setattr(mm_engine,'ledger_cooldown',lambda *args:{'until':'2026-09-28T16:00:00Z'})
    e.quote({},100)
    assert not e.L.get_state('mm_orders')
    pos={'market:Up':dict(slug='market',side='Up',shares=5.,cost=2.4)}
    e.quote(pos,97.6)
    orders=e.L.get_state('mm_orders')
    assert len(orders)==1 and orders[0]['outcome']=='Down' and orders[0]['shares']==5
