"""Round 4: low-turnover SPY alternatives, next-open execution and cash dividends."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent


def simulate(frame,signals,start,end,cost_scale=1.,halt=True):
    data=frame.loc[start:end]
    cash=100.;qty=0.;pending=0.;peak=100.;halt_until=-1;costs=0.;fills=[];equity=[]
    for i,(date,row) in enumerate(data.iterrows()):
        previous_qty=qty
        opening=cash+qty*row.Open
        current_weight=qty*row.Open/opening
        if abs(current_weight-pending)>.05 or (pending==0 and qty>0):
            target_qty=pending*opening/(row.Open*(1+.0007*cost_scale))
            if target_qty<qty:
                sell=qty-target_qty;px=row.Open*(1-.00073*cost_scale)
                cash+=sell*px;qty-=sell;costs+=sell*(row.Open-px)
                fills.append({'date':str(date.date()),'side':'SELL','shares':sell,'price':px})
            elif target_qty>qty:
                px=row.Open*(1+.0007*cost_scale)
                buy=min(target_qty-qty,cash/px)
                cash-=buy*px;qty+=buy;costs+=buy*(px-row.Open)
                fills.append({'date':str(date.date()),'side':'BUY','shares':buy,'price':px})
        cash+=previous_qty*row.Dividends
        value=cash+qty*row.Close;equity.append(float(value));peak=max(peak,value)
        halted=i<=halt_until
        if halt and not halted and 1-value/peak>=.15:
            halt_until=i+21;halted=True;peak=value
        pending=0. if halted else float(signals.loc[date])
    values=np.array([100.]+equity);rets=values[1:]/values[:-1]-1
    years=max((data.index[-1]-data.index[0]).days/365.25,1/365.25)
    return {'dates':[str(x.date()) for x in data.index],'equity':equity,'fills':fills,'costs':costs,
            'stats':{'return':float(values[-1]/100-1),'cagr':float((values[-1]/100)**(1/years)-1),
                     'drawdown':float((1-values/np.maximum.accumulate(values)).max()),
                     'sharpe':float(rets.mean()/rets.std()*np.sqrt(252)) if rets.std()>0 else None,
                     'orders':len(fills),'costs':costs}}


def signals_for(close,vix):
    from papertrader.strategy import regime_series
    from papertrader.nyse_calendar import next_session

    # Historical exchange sessions provide only the calendar, not future price inputs.
    schedule=close.index
    def following(d):
        i=schedule.searchsorted(pd.Timestamp(d),side="right")
        return schedule[i].date() if i<len(schedule) else next_session(d)
    sma=close.rolling(200).mean()
    cfg={'regime':{'vix_risk_on_below':25,'vix_risk_off_above':30}}
    primary=regime_series(close,sma,vix,cfg,following).eq('ON').astype(float)*.98
    cfg['regime']['use_vix']=False
    pure=regime_series(close,sma,vix,cfg,following).eq('ON').astype(float)*.98
    cfg['regime']['review_frequency']='weekly'
    weekly=regime_series(close,sma,vix,cfg,following).eq('ON').astype(float)*.98
    month_end=[following(d.date()).month!=d.month for d in schedule]
    monthly_close=close[month_end]
    monthly_signal=(monthly_close>monthly_close.shift(12)).astype(float)*.98
    monthly=monthly_signal.reindex(close.index).ffill().fillna(0.)
    return {'primary_regime':primary,'pure_200d':pure,
            'weekly_200d':weekly,'monthly_12m':monthly,'spy_buy_hold':pd.Series(.98,index=close.index)}


def main():
    close=pd.read_pickle(ROOT/'data/history/daily_close.pkl')
    opens=pd.read_pickle(ROOT/'data/history/daily_open.pkl')
    div=pd.read_pickle(ROOT/'data/history/daily_dividends.pkl')
    frame=pd.DataFrame({'Open':opens.SPY,'Close':close.SPY,'Dividends':div.SPY.fillna(0)}).dropna()
    signals=signals_for(frame.Close,close['^VIX'].reindex(frame.index))
    names=['primary_regime','pure_200d','weekly_200d','monthly_12m','spy_buy_hold']
    blocks=[('2016-01-01','2017-12-31'),('2018-01-01','2019-12-31'),('2020-01-01','2021-12-31')]
    dev={}
    for name in names:
        result=simulate(frame,signals[name],'2016-01-01','2021-12-31',halt=name!='spy_buy_hold')
        dev[name]={'full':result['stats'],'blocks':[simulate(frame,signals[name],a,b,halt=name!='spy_buy_hold')['stats'] for a,b in blocks]}
    baseline=dev['primary_regime'];eligible=[]
    for name in names[1:-1]:
        r=dev[name]
        if (r['full']['cagr']>baseline['full']['cagr'] and r['full']['drawdown']<=baseline['full']['drawdown']+.02
            and sum(a['cagr']>b['cagr'] for a,b in zip(r['blocks'],baseline['blocks']))>=2):
            eligible.append(name)
    chosen=max(eligible,key=lambda n:dev[n]['full']['cagr']) if eligible else 'primary_regime'
    # Freeze before touching post-2021 performance of any candidate.
    selection={'round':4,'development':dev,'selected':chosen,'blocks':blocks}
    (OUT/'round_4_selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    final={name:simulate(frame,signals[name],'2022-01-01','2026-09-22',halt=name!='spy_buy_hold')
           for name in dict.fromkeys(['primary_regime',chosen,'spy_buy_hold'])}
    doubled={name:simulate(frame,signals[name],'2022-01-01','2026-09-22',cost_scale=2)['stats'] for name in dict.fromkeys(['primary_regime',chosen])}
    report={**selection,'final_period':['2022-01-01','2026-09-22'],'final':final,'double_costs':doubled,
            'note':'Legacy peak-reset research model: resets the drawdown reference after each halt. This differs materially from live persistent-peak behavior. Use shared_daily.json live_running_peak results for deployment decisions. Overnight exposure is not comparable to the intraday risk budget.'}
    (OUT/'round_4.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ROUND 4',chosen,'development',json.dumps(dev),'final',json.dumps({k:v['stats'] for k,v in final.items()}),flush=True)


if __name__=='__main__':main()
