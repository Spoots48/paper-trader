"""Historical tests must use the live book's persistent drawdown peak by default."""
import json
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
from papertrader.backtest import run
from papertrader.strategy import EarningsBook


def test_backtest_does_not_restart_risk_after_halt_expires():
    cfg=json.loads((Path(__file__).parents[1]/'config/strategy_v1_primary.json').read_text())
    cfg['risk']['halt_sessions']=2
    idx=pd.bdate_range('2026-01-05',periods=12)
    prices=pd.DataFrame({'SPY':[100,100,100,80,80,80,80,90,100,110,120,130]},index=idx)
    sessions=[x.date() for x in idx]
    data=SimpleNamespace(sessions=sessions,sidx={d:i for i,d in enumerate(sessions)},
        o=prices,h=prices,l=prices,c=prices,c_ffill=prices,div=prices*0,
        ind=SimpleNamespace(c=prices,adv20=prices*0+1e10),
        regime=pd.Series('ON',index=idx),stocks=[],book=EarningsBook([]),
        eligible=lambda t,d:True,add_sessions=lambda d,n:d)
    args=(cfg,data,str(sessions[1]),str(sessions[-1]),'test')
    live=run(*args)
    legacy=run(*args,reset_peak_after_halt=True)
    assert len([f for f in live['fills'] if f.side=='BUY'])==1
    assert len([f for f in legacy['fills'] if f.side=='BUY'])>1
    assert legacy['equity'].iloc[-1]>live['equity'].iloc[-1]
