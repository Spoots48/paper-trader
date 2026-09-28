import copy
import json
from pathlib import Path

import pandas as pd
from papertrader.strategy import regime_series

CFG=json.loads((Path(__file__).parents[1]/'config/strategy_v1_primary.json').read_text())


def weekly(close, sma=None, vix=None):
    cfg=copy.deepcopy(CFG)
    cfg['regime'].update(use_vix=False, review_frequency='weekly')
    return regime_series(close, sma if sma is not None else close*0+100,
                         vix if vix is not None else close*float('nan'),cfg)


def test_weekly_decision_holds_until_friday_and_ignores_vix():
    idx=pd.to_datetime(['2026-09-18','2026-09-21','2026-09-22','2026-09-25'])
    close=pd.Series([110,90,90,90],index=idx)
    assert weekly(close).tolist()==['ON','ON','ON','OFF']


def test_good_friday_uses_thursday_close():
    idx=pd.to_datetime(['2026-03-27','2026-04-01','2026-04-02','2026-04-06'])
    assert weekly(pd.Series([110,90,90,110],index=idx)).tolist()==['ON','ON','OFF','OFF']


def test_weekly_output_does_not_depend_on_later_rows():
    idx=pd.bdate_range('2026-09-14','2026-09-25')
    close=pd.Series([110,90,110,90,110,90,90,90,90,90],index=idx)
    full=weekly(close)
    for n in range(1,len(close)+1):
        pd.testing.assert_series_equal(weekly(close.iloc[:n]),full.iloc[:n])


def test_missing_scheduled_signal_stays_unknown_until_next_review():
    idx=pd.to_datetime(['2026-09-18','2026-09-21','2026-09-25'])
    assert weekly(pd.Series([float('nan'),110,110],index=idx)).tolist()==['OFF?','OFF?','ON']
