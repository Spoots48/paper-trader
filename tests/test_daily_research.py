"""Timing and accounting checks for slower SPY alternatives."""
import pandas as pd
import pytest
from research.four_rounds_2026_09_28.daily import simulate


def test_close_signal_cannot_fill_at_same_close_or_open():
    idx=pd.bdate_range('2020-01-01',periods=4)
    frame=pd.DataFrame({'Open':[100,100,120,120], 'Close':[100,110,120,120], 'Dividends':0.},index=idx)
    signals=pd.Series([0,.98,.98,.98],index=idx)
    result=simulate(frame,signals,idx[0],idx[-1],cost_scale=0)
    assert result['equity'][0]==100 and result['equity'][1]==100
    assert result['fills'][0]['date']=='2020-01-03' and result['fills'][0]['price']==120
    assert result['equity'][-1]==pytest.approx(100)


def test_dividends_only_for_previous_close_holder():
    idx=pd.bdate_range('2020-01-01',periods=4)
    frame=pd.DataFrame({'Open':100.,'Close':100.,'Dividends':[0.,1.,1.,0.]},index=idx)
    signals=pd.Series([.98,.98,.98,.98],index=idx)
    result=simulate(frame,signals,idx[0],idx[-1],cost_scale=0)
    assert result['equity'][1]==100  # entered today, not eligible for today's distribution
    assert result['equity'][2]==pytest.approx(100.98)


def test_costs_and_cash_reconcile():
    idx=pd.bdate_range('2020-01-01',periods=4)
    frame=pd.DataFrame({'Open':100.,'Close':100.,'Dividends':0.},index=idx)
    signals=pd.Series([.98,0.,0.,0.],index=idx)
    result=simulate(frame,signals,idx[0],idx[-1])
    assert len(result['fills'])==2
    assert result['equity'][-1]==pytest.approx(100-result['costs'])
