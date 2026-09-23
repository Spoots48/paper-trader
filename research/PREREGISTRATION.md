# Pre-registration: historical test plan

Written **2026-09-22, before any backtest was run** on this universe. Parameters
live in `config/strategy_v1.json`. I picked them from published research and
round-number conventions, not by tuning them on this data.

## Hypotheses

1. **Post-earnings drift (catalyst sleeve).** Large S&P 500 stocks that gap up
   ≥5% on earnings (≥4% more than SPY that day), trade at least 2× their normal
   volume and close in the upper half of the day's range keep outperforming
   over the next ~20 sessions.
   Literature: Bernard & Thomas (1989); Chan, Jegadeesh & Lakonishok (1996);
   Brandt et al. (2008) on earnings-announcement returns. Counter-evidence:
   Martineau (2021) finds classic PEAD has mostly disappeared in large caps.
   *Prior: weak-to-moderate, possibly zero after costs.*
2. **Momentum (momentum sleeve).** Stocks with the best 6-month returns
   (skipping the last week), measured relative to their own volatility and
   confined to established uptrends, beat the index.
   Literature: Jegadeesh & Titman (1993); Barroso & Santa-Clara (2015) on
   volatility-scaled momentum. Known failure mode: momentum crashes after
   sharp market reversals.
3. **Regime filter.** Holding cash while SPY is below its 200-day average or
   VIX is above 30 cuts drawdowns at the cost of whipsaw losses.
   Literature: Faber (2007); Moskowitz, Ooi & Pedersen (2012).

## Periods

* Warm-up: 2015 (indicator history only; no trading)
* **In-sample (IS): 2016-01-04 → 2021-12-31**
* **Out-of-sample (OOS): 2022-01-03 → 2026-09-21**

## Decision rules (fixed before looking at results)

* A sleeve is **kept** only if adding it to the other components improves
  in-sample CAGR net of costs *and* doesn't worsen in-sample max drawdown by
  more than 5 percentage points.
* No parameter is changed based on backtest results. If a sleeve fails, it is
  disabled (`enabled: false`), and the change is recorded here with its
  numbers. I won't tune it until it passes.
* OOS is run exactly once with the final frozen config. Its result is
  reported whatever it shows. If OOS is bad, the live experiment still runs
  (the point is an honest test), and the report says so.
* Sensitivity grids (thresholds ±) may be run *for disclosure only*. They
  can't be used to pick parameters.

## Known limitations (stated in advance)

* **Survivorship bias:** the universe is today's S&P 500. Mitigation: a stock
  is eligible only after its "date added" to the index. Residual bias: stocks
  that were removed (bankruptcies, acquisitions, demotions) are missing.
* **News is not backtested.** No free, timestamped historical news archive
  was found that could be reached reliably. GDELT is rate-limited to 1
  request / 5 s; Stooq and FRED were unreachable from this machine. Nothing is
  fabricated: the backtest trades every qualifying price/earnings event, and
  the live system adds a news confirmation/veto whose effect is unknown.
* **Earnings timing:** Yahoo's historical announcement times are used to
  assign the reaction day. Scheduled dates are treated as known 5 sessions
  ahead, which is usually true but not always.
* **Costs:** modeled as a fixed adverse price adjustment per side (see
  config). Real fractional-share execution quality varies by broker.
* **Dividends:** credited in cash on the ex-date for positions held at the
  prior close, for both the strategy and the SPY benchmark.

---

## Results and decisions (appended 2026-09-22, after the backtest ran)

Raw output: `research/backtest_results.json` (curves in `backtest_curves.json`).
$100 start, costs included, dividends credited.

### In-sample 2016-01-04 → 2021-12-31

| Variant | Total | CAGR | Max DD | Sharpe (rf=0) |
|---|---|---|---|---|
| SPY buy & hold | +151.9% | +16.7% | 31.8% | 0.99 |
| Regime-gated SPY only | +62.7% | +8.5% | 19.5% | 0.81 |
| + momentum (no catalyst) | +54.0% | +7.5% | 18.7% | 0.64 |
| + catalyst (no momentum) | +33.7% | +5.0% | 27.0% | 0.47 |
| Full v1 (both sleeves) | +20.8% | +3.2% | 29.1% | 0.30 |

Catalyst event study (entry at next open, excess vs SPY): signals passing
all filters n=678, 20-day excess −0.04% (t = −0.14). The unfiltered "gap ≥5%"
set did better in-sample (+0.63%, t = 2.70), but the close-location and
volume filters removed that edge.

### Decision under the pre-registered rule

* **Catalyst sleeve: FAILS** (adding it lowers IS CAGR 7.5% → 3.2% and raises
  max DD 18.7% → 29.1%). Disabled in the primary book.
* **Momentum sleeve: FAILS** (adding it to regime-gated SPY lowers IS CAGR
  8.5% → 7.5%; adding it to the catalyst variant lowers CAGR 5.0% → 3.2%).
  Disabled in the primary book.
* **Regime filter and drawdown limits:** no keep/drop rule was pre-registered
  for these. They stay as the defined risk controls. Disclosure: they cost a
  lot of return in-sample (8.5% vs 16.7% CAGR) in exchange for a smaller
  drawdown (19.5% vs 31.8%), mostly by missing V-shaped rebounds such as
  mid-2020, when VIX stayed above the 25 re-entry level.

### Procedural disclosure

The backtest script computed in-sample and out-of-sample results in the same
run. So the OOS numbers were visible before the sleeve decision, which bends
the "OOS runs once, after freezing" rule. The decision above follows the
in-sample rule exactly and was **not** changed after seeing OOS, even though
OOS favored momentum:

### Out-of-sample 2022-01-03 → 2026-09-21 (reported regardless of outcome)

| Variant | Total | CAGR | Max DD | Sharpe |
|---|---|---|---|---|
| SPY buy & hold | +68.8% | +11.7% | 24.4% | 0.74 |
| Regime-gated SPY only (= primary book) | +34.8% | +6.5% | 22.9% | 0.65 |
| + momentum (no catalyst) | +72.5% | +12.3% | 25.5% | 0.82 |
| + catalyst (no momentum) | −7.2% | −1.6% | 25.9% | −0.07 |
| Full v1 (= research book) | +10.8% | +2.2% | 27.9% | 0.23 |

Catalyst event study OOS: n=894, 5-day excess −0.31% (t = −2.22), 20-day
−0.15% (t = −0.62).

### What runs live

1. **Primary book** = `config/strategy_v1_primary.json`: v1 with both sleeves
   disabled (regime-gated SPY plus drawdown limits).
2. **Research book** = `config/strategy_v1.json`: the unmodified pre-registered
   v1, including the live news confirmation/veto that could not be
   backtested. It runs forward on its own $100 so the month produces
   evidence about the news-confirmed signals without presenting them as the
   main result.

Both files are hashed at freeze time. Neither may change during the 30 days
except through a logged change (`python run.py log-change`).

### What one month can and cannot show

Across 1,490 rolling 30-day windows in-sample, the full v1 strategy's excess
return vs SPY had a standard deviation of 3.5 percentage points. The v1
strategy beat SPY in 34% of windows in-sample and 40% out-of-sample while
underperforming over the full periods. A single month's result, good or bad,
is well inside the noise.
