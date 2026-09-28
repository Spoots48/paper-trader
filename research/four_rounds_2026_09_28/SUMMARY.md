# Four strategy research rounds — 28 September 2026

**Decision: no new strategy passed the evidence required for activation.** The existing
risk-controlled configurations remain active. This work found and fixed an optimistic
backtest assumption; it did not establish a profitable replacement. Historical simulated
returns below are not returns earned in the running paper books.

## Rounds 1–3: intraday alternatives

Development: 30 sessions, 21 July–31 August 2026, split into two 15-session folds.
The current risk-sized strategy returned **+3.321%**, maximum closing drawdown **0.452%**,
57 completed trades after modeled transaction costs. All candidates used the same
0.25% per-trade modeled risk and 1% session risk budget. Selection rules were written
in [PLAN.md](PLAN.md) before the search; no thresholds were relaxed afterward.

| Round | Approaches tested | Development net return | Decision |
|---|---|---:|---|
| 1: trade selection | Opening relative volume >=2x; strong opening close; non-earnings gap plus volume | +3.321%; +2.190%; +1.643% | Volume rule made no difference. Other variants did not improve both folds. |
| 2: entry timing | First hour only; completed five-minute breakout; later pullback/retest | +3.321%; +0.905%; −0.024% | No improvement in both folds. |
| 3: exits | 2R target; 3R target; exit weak trades after 60 minutes | +2.623%; +3.120%; +2.263% | No improvement in both folds. The weak-trade exit also increased drawdown. |

The final chronological check, 1–23 September, returned **−0.260% across seven trades**
at both one-minute and five-minute execution. Doubled costs returned **−0.344%**.
Removing the best trade left a **−$0.487** sum of closed-trade P&L per $100 initial
capital. These results do not validate the current strategy as profitable either.
Since no challenger survived development, the final candidate equals the incumbent:
the excess-return bootstrap interval is [0, 0], not evidence of an edge. Seven final
trades also fall below the predeclared minimum of ten.

Confirmed entries use a completed five-minute signal and a later bar's opening price.
Retests must occur after the breakout interval. Stagnation exits execute at the next
bar open. Stops take priority if both a stop and target are touched. The first-hour
experiment excludes any execution bar ending after the deadline. No fallback exits
were needed in these final replays. The first-hour limit is a research-wrapper policy;
it is not enabled or implemented as an active DayEngine configuration.

## Round 4: trade less often

Tested pure 200-session SPY trend, weekly trend review, and monthly 12-month absolute
momentum against the current SPY/VIX regime. The development selection (2016–2021)
chose weekly trend review. It improved all three two-year development blocks under the
**legacy research model**, which resets its drawdown reference after a halt.

| 2022–22 September 2026 check | Current primary | Weekly trend candidate |
|---|---:|---:|
| Legacy reconstructed model: total return | +34.89% | +41.29% |
| Shared strategy/broker, legacy peak reset: total return | +34.80% | +41.20% |
| **Shared strategy/broker, live persistent peak: total return** | **−15.59%** | **−15.86%** |

The first row is **not a live-parity result**. The running primary book preserves its
original equity peak; after a large drawdown, halt expiry does not erase that loss.
The legacy backtest reset the peak, permitting later re-entry. The weekly candidate's
apparent positive outcome did not survive that correction, and was rejected.

For context, a 98% SPY buy-and-hold benchmark returned **+66.79%** with **24.21%** maximum
drawdown in the reconstructed final-period model. The weekly candidate did not beat
that benchmark's return even under the more favorable legacy assumptions. Daily
strategies have overnight exposure and much larger drawdowns than the intraday book;
these are not comparable risk budgets. Drawdown halts are evaluated at closing prices
and filled later, so a 15% trigger is not a guarantee that losses stop at exactly 15%.

The code now defaults to the live persistent-peak rule in `backtest.run`. Explicit
`reset_peak_after_halt=True` exists only to reproduce and audit the older research
behavior. Older saved reports remain historical artifacts and were not rewritten;
their results require this qualification.

## What changed and what remains uncertain

- Added reproducible candidate comparisons, immutable baseline snapshots, cost stress
  checks, timing/accounting regression tests, and an explicit production-rule audit.
- Added optional causal research policies in the shared intraday simulator and a
  weekly regime policy. All new strategy options are disabled in active configurations.
- Fixed the backtest's default halt accounting. This changes future historical
  evaluations, not the running ledger's accounting or its risk limits.
- Independent review found an entry-deadline bug; it was fixed, regression-tested,
  and all three intraday rounds were rerun. Outcomes did not change.
- No live balances, fills, historical strategy records, or active configurations were
  reset or replaced. The candidate JSON is research-only.

The archived data has been studied before. The final dates were reserved from this
specific search, but are **not a fresh independent holdout**. Intraday coverage is short,
models omit real execution uncertainty, and daily testing uses historical data rather
than the exact live data arrival sequence. No candidate has demonstrated future profits.
Further strategy selection needs new forward observations; repeatedly tuning this same
sample would weaken the evidence.

Validation: **77 tests passed**, baseline intraday replay parity passed, and an
independent code review found no remaining blockers after the deadline correction.

## Reproduce and inspect

From the project root with the archived market data present:

```sh
.venv/bin/python -m research.four_rounds_2026_09_28.replay
.venv/bin/python -m research.four_rounds_2026_09_28.daily
.venv/bin/python -m research.four_rounds_2026_09_28.shared_daily
.venv/bin/python -m pytest -q
```

Each round's JSON retains the losing candidates. `intraday_final_check.json` contains
fills, daily equity, costs and the final gates. `round_4.json` explicitly labels the
legacy peak-reset model; `shared_daily.json` contains the relevant persistent-peak
audit. `manifest.json` hashes source, baseline configurations and input data.

Research background: [Concretum's published research](https://concretumgroup.com/papers/)
provided context for opening-range experiments; [AQR's time-series momentum paper](https://www.aqr.com/insights/research/journal-article/time-series-momentum)
provided context for slower trend rules. These publications do not validate this
implementation. [Bailey et al., Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)
motivates retaining failures and avoiding repeated selection on the same observations.
