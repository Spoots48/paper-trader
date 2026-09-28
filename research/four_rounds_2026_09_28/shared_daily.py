"""Audit the selected daily candidate using the actual strategy and broker."""
import copy
import json
from pathlib import Path
from papertrader.backtest import HistData,run,stats
from papertrader.strategy import regime_series

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent


def main():
    baseline_path=OUT/'primary_baseline.json'
    baseline=json.loads((baseline_path if baseline_path.exists() else ROOT/'config/strategy_v1_primary.json').read_text())
    candidate=copy.deepcopy(baseline)
    candidate['version']='2.0.0-primary-candidate'
    candidate['strategy_id']='weekly-200-day-spy-candidate'
    candidate['regime'].update(use_vix=False,review_frequency='weekly',
        note='Review SPY versus its 200-session mean at the last scheduled close of the week; execute at the following open. VIX gate disabled.')
    candidate['description']='Research candidate only. Weekly SPY trend; unchanged cash buffer and risk controls.'
    (OUT/'primary_candidate.json').write_text(json.dumps(candidate,indent=2)+'\n')
    (OUT/'primary_baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    data=HistData(baseline)
    reports={}
    for mode,reset in [('legacy_research',True),('live_running_peak',False)]:
        reports[mode]={}
        for period,start,end in [('development','2016-01-01','2021-12-31'),('final','2022-01-01','2026-09-22')]:
            reports[mode][period]={}
            for name,cfg in [('current_primary',baseline),('weekly_candidate',candidate)]:
                data.regime=regime_series(data.c.SPY,data.ind.sma200.SPY,data.vix,cfg,lambda d:data.add_sessions(d,1))
                result=run(cfg,data,start,end,name,reset_peak_after_halt=reset)
                report=stats(result['equity'],result['fills'])
                reports[mode][period][name]=report
                print(mode,period,name,json.dumps(report),flush=True)
    report={'results':reports,'note':'Shared strategy.decide and Broker; live_running_peak matches persistent peak semantics. Daily historical fills still differ from live data timing. No news dependency because both stock sleeves are disabled.'}
    (OUT/'shared_daily.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
