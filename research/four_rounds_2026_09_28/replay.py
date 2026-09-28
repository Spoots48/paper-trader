"""Reproducible sequential research; existing simulator is the only fill engine.
Run: .venv/bin/python -m research.four_rounds_2026_09_28.replay
"""
import copy
import datetime as dt
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from papertrader.backtest_intraday import daily_metrics
from papertrader.dt_variants import earnings_catalysts
from papertrader.intraday import DayState, process_bar, select_candidates
from papertrader.nyse_calendar import session_close, session_open

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = json.loads((OUT / 'baseline.json').read_text())
CACHE = ROOT / 'data/intraday/four_rounds_prepared.pkl'


def prepare():
    paths = [ROOT / f'data/intraday/{x}' for x in ('bars_5m.pkl','bars_1m.pkl','daily_6mo.pkl')]
    paths += [ROOT/'data/history/earnings.pkl', OUT/'baseline.json']
    signature = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if CACHE.exists():
        with CACHE.open('rb') as f:
            saved = pickle.load(f)
        if saved['signature'] == signature:
            return saved
    bars = pd.read_pickle(paths[0]); daily = pd.read_pickle(paths[2])
    bars['session'] = bars.ts.dt.date
    sessions = sorted(bars.loc[bars.ticker=='SPY', 'session'].unique())
    first = bars[bars.ts.dt.strftime('%H:%M')=='09:30'].set_index(['session','ticker'])
    stocks = sorted(set(bars.ticker)-{'SPY'})
    catalysts = earnings_catalysts(ROOT/'data/history/earnings.pkl', sessions)
    prepared = {}
    for i, day in enumerate(sessions):
        if i < BASE['selection']['relative_volume_lookback_sessions']:
            continue
        fb, hist = {}, {}
        for t in stocks:
            if (day,t) not in first.index:
                continue
            row=first.loc[day,t];fb[t]=tuple(float(row[k]) for k in ('Open','High','Low','Close','Volume'))
            hist[t]=[float(first.loc[s,t].Volume) for s in sessions[i-14:i] if (s,t) in first.index]
        metrics=daily_metrics(daily,list(fb),day,BASE)
        candidates,_=select_candidates(fb,hist,metrics,BASE)
        prepared[day]={'candidates':[vars(c) for c in candidates], 'daily':metrics,
                       'earnings':{t for t,d in catalysts if d==day}, 'bars':{}}
    for minutes, frame in ((5,bars),(1,pd.read_pickle(paths[1]))):
        if 'session' not in frame: frame['session']=frame.ts.dt.date
        for day,g in frame.groupby('session'):
            if day not in prepared:continue
            keep={c['ticker'] for c in prepared[day]['candidates']}
            g=g[g.ticker.isin(keep)]
            grouped=[]
            for ts,b in g.groupby('ts',sort=True):
                if ts.strftime('%H:%M')<'09:35':continue
                grouped.append((ts.isoformat(),{r.ticker:(float(r.Open),float(r.High),float(r.Low),float(r.Close)) for r in b.itertuples()}))
            prepared[day]['bars'][minutes]=grouped
    result={'signature':signature,'sessions':sorted(prepared),'days':prepared}
    with CACHE.open('wb') as f:pickle.dump(result,f)
    return result


def replay(tape,cfg,dates,minutes=5,cost_multiplier=1.):
    cfg=copy.deepcopy(cfg);cfg['execution']['bar_minutes']=minutes
    cfg['costs']={k:v*cost_multiplier if isinstance(v,(int,float)) else v for k,v in cfg['costs'].items()}
    cash=100.;peak=100.;pause=0;halt=False;days=[];trades=[]
    for day in dates:
        source=tape['days'][day]
        if minutes not in source['bars']:continue
        cands=[]
        for c in source['candidates']:
            if cfg['selection'].get('require_earnings_catalyst') and c['ticker'] not in source['earnings']:continue
            if c['rvol'] < cfg['selection']['min_relative_volume']:continue
            if (c['first_close']-c['first_low'])/max(c['first_high']-c['first_low'],1e-9)<cfg['selection'].get('min_close_location',0):continue
            prev=source['daily'][c['ticker']]['prev_close']
            if c['first_open']/prev-1<cfg['selection'].get('min_opening_gap',-float('inf')):continue
            cands.append(copy.deepcopy(c))
        st=DayState(str(day),cash,cash,candidates=cands,pending=[c['ticker'] for c in cands])
        close=session_close(day);last=(close-dt.timedelta(minutes=minutes)).isoformat()
        cutoff=close-dt.timedelta(minutes=cfg['entry']['last_entry_bar_minutes_before_close'])
        early_deadline = None
        if cfg['entry'].get('max_minutes_after_open') is not None:
            early_deadline=session_open(day)+dt.timedelta(minutes=cfg['entry']['max_minutes_after_open'])
        allowed=not halt and pause==0
        selected={c['ticker'] for c in cands}
        last_bars={}
        for ts,all_bars in source['bars'][minutes]:
            now=dt.datetime.fromisoformat(ts)
            if now>dt.datetime.fromisoformat(last):break
            b={t:v for t,v in all_bars.items() if t in selected}
            if not b:continue
            last_bars.update(b)
            events=process_bar(st,ts,b,cfg,is_last_bar=now==dt.datetime.fromisoformat(last),entries_allowed=allowed and now<=cutoff
                               and (early_deadline is None or now+dt.timedelta(minutes=minutes)<=early_deadline))
            trades.extend(dict(vars(e),session=str(day)) for e in events if e.kind in ('BUY','SELL'))
        if st.positions:
            # Match the live fallback, and disclose every use rather than silently dropping exits.
            events=process_bar(st,last,last_bars,cfg,is_last_bar=True,entries_allowed=False)
            trades.extend(dict(vars(e),session=str(day),fallback=True) for e in events)
        days.append({'session':str(day),'equity':st.cash,'return':st.cash/cash-1})
        cash=st.cash;peak=max(peak,cash);pause=max(0,pause-1)
        dd=1-cash/peak
        if dd>=cfg['risk']['drawdown_halt']:halt=True
        elif dd>=cfg['risk']['drawdown_pause'] and pause==0:pause=cfg['risk']['pause_sessions']
    return {'days':days,'trades':trades,'stats':stats(days,trades)}


def stats(days,trades):
    eq=np.array([100.]+[d['equity'] for d in days])
    sells=[t for t in trades if t['kind']=='SELL']
    return {'return':float(eq[-1]/100-1),'drawdown':float((1-eq/np.maximum.accumulate(eq)).max()),
            'trades':len(sells),'win_rate':sum(t['realized_pnl']>0 for t in sells)/len(sells) if sells else None,
            'costs':sum(t['qty']*abs(t['fill_price']-t['ref_price']) for t in trades),
            'fallback_exits':sum(bool(t.get('fallback')) for t in sells)}


def change(cfg,**updates):
    c=copy.deepcopy(cfg)
    for section,values in updates.items():c[section].update(values)
    return c


def round_candidates(number,incumbent):
    if number==1:
        return {'rvol2':change(incumbent,selection={'min_relative_volume':2}),
                'strong_close':change(incumbent,selection={'min_close_location':.75}),
                'gap_volume':change(incumbent,selection={'require_earnings_catalyst':False,'min_relative_volume':2,'min_opening_gap':.02})}
    if number==2:
        return {'early_only':change(incumbent,entry={'max_minutes_after_open':60}),
                'confirmed_breakout':change(incumbent,entry={'confirmation':'close'}),
                'pullback_retest':change(incumbent,entry={'confirmation':'retest'})}
    return {'target_2r':change(incumbent,exit={'take_profit_r':2}),
            'target_3r':change(incumbent,exit={'take_profit_r':3}),
            'stagnation_exit':change(incumbent,exit={'stagnation_minutes':60,'stagnation_min_r':.5})}


def evaluate_development(tape,cfg,dates):
    return {k:replay(tape,cfg,ds)['stats'] for k,ds in [('full',dates),('fold1',dates[:15]),('fold2',dates[15:])]}


def eligible(result,base):
    return (result['full']['trades']>=10 and result['full']['return']>0
            and result['full']['drawdown']<=base['full']['drawdown']+.0025
            and all(result[k]['return']>base[k]['return']+1e-10 for k in ('fold1','fold2')))


def main():
    tape=prepare();dates=tape['sessions'];assert len(dates)==46
    previous=json.loads((ROOT/'research/revamp_2026_09_28/replay_results.json').read_text())
    for minutes in (5,1):
        actual=replay(tape,BASE,dates,minutes)['stats']
        expected=previous[f'{minutes}m:risk_sized']
        assert abs(actual['return']-expected['full']['total_return'])<2e-6, (minutes,actual,expected['full'])
        assert actual['trades']==expected['trades']['n_round_trips'], (minutes,actual)
    print('BASELINE PARITY PASSED',flush=True)
    development=dates[:30];final=dates[30:]
    incumbent=copy.deepcopy(BASE);history=[]
    for number in (1,2,3):
        base=evaluate_development(tape,incumbent,development)
        configs=round_candidates(number,incumbent)
        results={name:evaluate_development(tape,c,development) for name,c in configs.items()}
        keep=[name for name,r in results.items() if eligible(r,base)]
        winner=max(keep,key=lambda n:results[n]['full']['return']) if keep else 'incumbent'
        report={'round':number,'incumbent':base,'candidates':results,'selected':winner,'config_before':incumbent}
        if winner!='incumbent':incumbent=configs[winner]
        report['config_after']=incumbent;history.append(report)
        (OUT/f'round_{number}.json').write_text(json.dumps(report,indent=2))
        print('ROUND',number,'selected',winner,'results',json.dumps(results),flush=True)
    (OUT/'intraday_finalist.json').write_text(json.dumps(incumbent,indent=2)+'\n')
    final_results={}
    for minutes in (5,1):
        for cost in (1,2):
            key=f'{minutes}m_{cost}x_costs'
            final_results[key]={name:replay(tape,cfg,final,minutes,cost) for name,cfg in [('baseline',BASE),('finalist',incumbent)]}
    # Moving day-block bootstrap: paired excess returns, fixed seed, 5-day blocks.
    r=final_results['1m_1x_costs'];excess=np.array([d['return'] for d in r['finalist']['days']])-np.array([d['return'] for d in r['baseline']['days']])
    rng=np.random.default_rng(20260928);n=len(excess);means=[]
    for _ in range(5000):
        starts=rng.integers(0,n,size=(n+4)//5)
        sample=np.concatenate([excess[(s+np.arange(5))%n] for s in starts])[:n]
        means.append(float(sample.mean()))
    ci=np.quantile(means,[.025,.975]).tolist()
    checks={key:(v['finalist']['stats']['return']>max(0,v['baseline']['stats']['return']) and v['finalist']['stats']['trades']>=10) for key,v in final_results.items()}
    final_report={'period':[str(final[0]),str(final[-1])],'development':[str(development[0]),str(development[-1])],
                  'results':final_results,'bootstrap_daily_excess_95_interval':ci,'checks':checks,
                  'eligible_for_live':all(checks.values()) and ci[0]>0,'data_hashes':tape['signature']}
    for key,values in final_results.items():
        for name,r in values.items():
            sells=[t['realized_pnl'] for t in r['trades'] if t['kind']=='SELL']
            r['pnl_without_best_trade']=sum(sells)-max(sells,default=0)
    (OUT/'intraday_final_check.json').write_text(json.dumps(final_report,indent=2)+'\n')
    print('FINAL CHECK',checks,'95% interval',ci,'live',final_report['eligible_for_live'],flush=True)


if __name__=='__main__':main()
