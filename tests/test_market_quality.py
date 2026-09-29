import datetime as dt
import math
import pytest
from papertrader.market_quality import closed_closes, parse_klines, freshness_checks, parse_book

NOW=dt.datetime(2026,9,28,15,0,30,tzinfo=dt.timezone.utc)
T=int(NOW.timestamp())//60*60
QUALITY={'max_age_seconds':30,'max_skew_seconds':10,'future_tolerance_seconds':5}


def test_volatility_requires_every_closed_minute_and_ignores_forming_candle():
    candles={T-i*60:(100,100+i) for i in range(4)}
    assert closed_closes(candles,NOW,2)==[103,102,101]
    candles[T]=(100,math.nan)
    assert closed_closes(candles,NOW,2)==[103,102,101]
    del candles[T-120]
    with pytest.raises(ValueError,match='missing'):
        closed_closes(candles,NOW,2)


def test_duplicate_kline_and_bad_closed_price_rejected():
    row=[T*1000,'100','101','99','100','10',(T+60)*1000-1]
    with pytest.raises(ValueError,match='duplicate'):
        parse_klines([row,row])
    with pytest.raises(ValueError,match='price'):
        closed_closes({T-60:(100,math.nan),T-120:(100,99)},NOW,1)


def test_mixed_snapshot_ages_are_visible_and_rejected():
    ts=NOW.timestamp()
    checks=freshness_checks({'up':ts-1,'down':ts-20,'underlying':ts-1},NOW,QUALITY)
    assert all(x['ok'] for x in checks if x['name']!='snapshot_skew')
    assert not checks[-1]['ok']
    for bad in (None,ts-31,ts+6,math.nan):
        assert not all(x['ok'] for x in freshness_checks({'book':bad},NOW,QUALITY))
    assert all(x['ok'] for x in freshness_checks({'book':ts-3},NOW,QUALITY))


@pytest.mark.parametrize('price,size',[('nan','5'),('.5','nan'),('.5','-1'),('1.1','4')])
def test_bad_book_levels_rejected(price,size):
    with pytest.raises(ValueError):
        parse_book({'asks':[{'price':price,'size':size}],'bids':[]})


def test_crossed_book_rejected_and_levels_sorted():
    with pytest.raises(ValueError,match='crossed'):
        parse_book({'asks':[{'price':'.4','size':'5'}],'bids':[{'price':'.5','size':'5'}]})
    assert parse_book({'asks':[{'price':'.6','size':'5'},{'price':'.5','size':'8'}],'bids':[]})[0][0]==(.5,8)


def test_fetch_crossing_minute_boundary_cannot_promote_partial_candle(tmp_path):
    from test_pm_risk import engine
    e=engine(tmp_path)
    before=NOW.replace(second=59)
    after=before+dt.timedelta(seconds=3)
    calls=iter([before,after,after])
    e.clock=lambda:next(calls)
    current=int(before.timestamp())//60*60
    rows=[[i*1000,100,101,99,100,10,(i+60)*1000-1] for i in range(current-3660,current+1,60)]
    e.get=lambda url,**kw: rows if url.endswith('/klines') else [{'price':'100','time':after.timestamp()*1000}]
    px=e.prices('BTCUSDT')
    with pytest.raises(ValueError,match='missing'):
        closed_closes(px['candles'],after,60)


def test_engine_rejects_stale_books_and_records_mixed_input_verdicts(tmp_path):
    from test_pm_risk import engine
    e=engine(tmp_path)
    e.get=lambda *a,**kw: {'timestamp':str((e.now.timestamp()-31)*1000),'asks':[{'price':'.5','size':'10'}],'bids':[{'price':'.49','size':'10'}]}
    with pytest.raises(ValueError,match='timestamp'):
        e.book('u')
    e.book_times={'u':e.now.timestamp(),'d':e.now.timestamp()-20}
    assert not e.entry_quality('m',['u','d'])
    row=e.L.db.execute("select action,metrics from decisions where reason_code='INPUT_QUALITY'").fetchone()
    assert row['action']=='SKIP' and 'snapshot_skew' in row['metrics']
