"""Run from repository root: .venv/bin/python -m research.revamp_2026_09_28.replay"""
import copy
import json
from pathlib import Path

import pandas as pd

from papertrader.backtest_intraday import run
from papertrader.dt_variants import earnings_catalysts

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
base = json.loads((OUT / 'daytrade_before.json').read_text())
risk = copy.deepcopy(base)
risk['risk'].update(per_trade_risk=.0025, daily_loss_limit=.01)
trail = copy.deepcopy(risk)
trail['exit'].update(trail_activate_r=2., trail_distance_r=1.)
bars = pd.read_pickle(ROOT / 'data/intraday/bars_5m.pkl')
sessions = sorted({t.date() for t in bars.loc[bars.ticker == 'SPY', 'ts']})
catalyst = earnings_catalysts(ROOT / 'data/history/earnings.pkl', sessions)
results = {}
for minutes in (1, 5):
    for name, cfg in [('baseline', base), ('risk_sized', risk), ('risk_and_trail', trail)]:
        r = run(ROOT / 'data/intraday', minutes, cfg=cfg, catalyst=catalyst)
        results[f'{minutes}m:{name}'] = r
        (OUT / 'replay_results.json').write_text(json.dumps(results, indent=2, default=str))
        print(minutes, name, {k: r[k] for k in ('full','second_half','trades')}, flush=True)
