"""Causal mechanics for the four-round intraday research challengers."""
import copy
import pytest
from papertrader.config import ROOT, load_json
from papertrader.intraday import DayState, process_bar, select_candidates


def cfg():
    c = copy.deepcopy(load_json(ROOT / 'config/strategy_daytrade_v1.json'))
    return c


def state():
    c = dict(ticker='X', rank=1, rvol=4., first_high=99.99, trigger=100., stop_price=99.,
             first_open=99.5, first_low=99., first_close=99.9, first_volume=1000, atr=2., adv_usd=2e9, stop_distance=1.)
    return DayState('2026-09-01', 100., 100., candidates=[c], pending=['X'])


def step(s, minute, b, c):
    return process_bar(s, f'2026-09-01T09:{minute}:00-04:00', {'X':b}, c, is_last_bar=False, entries_allowed=True)


def test_confirmation_fills_only_after_completed_five_minute_bar():
    s=state(); c=cfg(); c['entry']['confirmation']='close'
    # 09:35–09:40 interval: early spike is not a completed confirmation.
    assert not step(s, '35', (99.8, 100.5, 99.5, 100.3), c)
    assert not step(s, '39', (100.2, 100.6, 100.1, 100.4), c)
    events=step(s, '40', (100.8, 101, 100.5, 100.7), c)
    assert events[0].kind=='BUY' and events[0].ref_price==100.8


def test_failed_confirmation_does_not_enter_on_intrabar_spike():
    s=state(); c=cfg(); c['entry']['confirmation']='close'
    assert not step(s,'39',(99.8,101,99.5,99.9),c)
    assert not step(s,'40',(99.8,100.2,99.5,99.9),c)


def test_pullback_waits_for_later_retest_then_next_open():
    s=state(); c=cfg(); c['entry']['confirmation']='retest'
    assert not step(s,'39',(99.8,100.6,99.5,100.4),c)
    assert not step(s,'44',(100.4,100.8,100.1,100.6),c) # no retest of 100
    assert not step(s,'49',(100.5,100.8,99.9,100.3),c) # confirmed retest
    e=step(s,'50',(100.4,101,100.2,100.8),c)
    assert e[0].kind=='BUY' and e[0].ref_price==100.4


def test_target_is_preplaced_and_stop_wins_ambiguous_bar():
    s=state(); c=cfg(); c['exit']['take_profit_r']=2.
    step(s,'35',(100,100.5,99.5,100.2),c)
    e=step(s,'36',(101,103,100.5,102.5),c)
    assert e[0].reason_code=='PROFIT_TARGET' and e[0].ref_price==102.
    s=state();step(s,'35',(100,100.5,99.5,100.2),c)
    e=step(s,'36',(101,103,98.5,102.5),c)
    assert e[0].reason_code=='STOP'


def test_target_can_fill_on_entry_bar_after_trigger_if_stop_untouched():
    s=state();c=cfg();c['exit']['take_profit_r']=2.
    e=step(s,'35',(99.8,103,99.5,102),c)
    assert [x.reason_code for x in e]==['ORB_BREAKOUT','PROFIT_TARGET']


def test_stagnant_trade_exits_next_bar_not_decision_close():
    s=state();c=cfg();c['exit'].update(stagnation_minutes=5, stagnation_min_r=.5)
    step(s,'35',(100,100.2,99.5,100.1),c)
    e=step(s,'40',(100.1,100.3,99.8,100.2),c)
    assert not e
    e=step(s,'41',(99.8,100.2,99.5,100),c)
    assert e[0].reason_code=='STAGNATION' and e[0].ref_price==99.8


def test_first_hour_cutoff_excludes_bar_that_extends_past_deadline():
    import datetime as dt
    from research.four_rounds_2026_09_28.replay import replay
    day=dt.date(2026,9,1)
    candidate=state().candidates[0]
    tape={'days':{day:{'candidates':[candidate],'daily':{'X':{'prev_close':99}},
        'earnings':{'X'},'bars':{5:[('2026-09-01T10:30:00-04:00',{'X':(99.8,100.5,99.5,100.3)})]}}}}
    c=cfg();c['entry']['max_minutes_after_open']=60
    assert replay(tape,c,[day])['stats']['trades']==0
