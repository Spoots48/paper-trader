import datetime as dt
from papertrader.entry_protections import market_loss_cooldown

NOW=dt.datetime(2026,9,28,15,tzinfo=dt.timezone.utc)
CFG={'loss_limit':2,'lookback_minutes':240,'cooldown_minutes':60}


def fill(slug,side,pnl,minutes):
    return {'order_key':f'pm:{slug}:{side}:SETTLE','realized_pnl':pnl,
            'recorded_at':(NOW-dt.timedelta(minutes=minutes)).isoformat()}


def test_profitable_pair_is_not_counted_as_a_loss():
    fills=[fill('a','Up',3,20),fill('a','Down',-2.9,20),fill('b','Up',-2,10)]
    assert market_loss_cooldown(fills,set(),NOW,CFG) is None


def test_lock_survives_repeat_calls_and_expires_without_rolling_forward():
    fills=[fill('a','Up',-2,20),fill('b','Up',-2,10)]
    lock=market_loss_cooldown(fills,set(),NOW,CFG)
    assert lock['until']==(NOW+dt.timedelta(minutes=50)).isoformat()
    assert market_loss_cooldown(fills,set(),NOW+dt.timedelta(minutes=49),CFG)==lock
    assert market_loss_cooldown(fills,set(),NOW+dt.timedelta(minutes=50),CFG) is None


def test_lock_does_not_expire_when_old_loss_leaves_lookback():
    fills=[fill('a','Up',-2,245),fill('b','Up',-2,10)]
    assert market_loss_cooldown(fills,set(),NOW,CFG) is not None


def test_incomplete_market_and_future_settlement_do_not_trigger():
    fills=[fill('a','Up',-2,20),fill('b','Up',-2,10)]
    assert market_loss_cooldown(fills,{'a'},NOW,CFG) is None
    assert market_loss_cooldown(fills+[fill('c','Up',-2,-1)],{'a'},NOW,CFG) is None


def test_new_loss_after_expiry_can_start_new_lock():
    fills=[fill('a','Up',-2,120),fill('b','Up',-2,110),fill('c','Up',-2,5)]
    assert market_loss_cooldown(fills,set(),NOW,CFG)['until']==(NOW+dt.timedelta(minutes=55)).isoformat()
