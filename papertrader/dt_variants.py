"""Research only: compare pre-declared day-trading variants on the same data (see research/PREREGISTRATION.md)."""
from __future__ import annotations

import copy
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

from .backtest_intraday import run
from .config import RESEARCH_DIR, ROOT, load_json
from .strategy import map_reaction


def earnings_catalysts(earn_pkl: Path, sessions: list[dt.date]) -> set:
    ev = pd.read_pickle(earn_pkl)
    out = set()
    for r in ev.itertuples():
        mp = map_reaction(r.announce_ts, 12, sessions)
        if mp:
            out.add((r.ticker, mp[0]))
    return out


def main(data_dir: Path, earn_pkl: Path) -> dict:
    base = load_json(ROOT / "config" / "strategy_daytrade_v1.json")
    wide = copy.deepcopy(base)
    wide["exit"]["stop_mode"] = "opening_range_low"
    bars = pd.read_pickle(data_dir / "bars_5m.pkl")
    sessions = sorted({t.date() for t in bars.loc[bars.ticker == "SPY", "ts"]})
    cat = earnings_catalysts(earn_pkl, sessions)
    variants = {"A_baseline": (base, None), "B_earnings_catalyst": (base, cat), "C_wide_stop": (wide, None), "D_catalyst_and_wide_stop": (wide, cat)}
    out = {}
    for minutes in (5, 1):
        for name, (cfg, c) in variants.items():
            r = run(data_dir, minutes, cfg=cfg, catalyst=c)
            t = r["trades"]
            out[f"{minutes}m:{name}"] = {"sessions": r["full"]["sessions"], "total_return": round(r["full"]["total_return"], 4),
                                         "first_half": round(r["first_half"]["total_return"], 4), "second_half": round(r["second_half"]["total_return"], 4),
                                         "max_drawdown": round(r["full"]["max_drawdown"], 4), "trades": t["n_round_trips"],
                                         "win_rate": round(t["win_rate"] or 0, 3), "costs_usd": round(t["costs_usd"], 2),
                                         "exit_reasons": t["exit_reasons"], "spy": round(r["spy_same_period"]["total_return"], 4)}
            print(f"{minutes}m {name:26s} ret {out[f'{minutes}m:{name}']['total_return']:+.2%} (halves {out[f'{minutes}m:{name}']['first_half']:+.2%} / {out[f'{minutes}m:{name}']['second_half']:+.2%}) "
                  f"trades {t['n_round_trips']} win {t['win_rate'] or 0:.0%} costs ${t['costs_usd']:.2f} | SPY {r['spy_same_period']['total_return']:+.2%}", flush=True)
    (RESEARCH_DIR / "dt_variants.json").write_text(json.dumps(out, indent=1, default=str))
    return out


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
