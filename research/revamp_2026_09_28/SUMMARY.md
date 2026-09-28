# Strategy revamp — 2026-09-28

## What the ledger actually showed

At 21:37 UTC, the retired original crypto bot had realized a $25.78 loss. The
day trader had realized a $1.18 loss on 10 round trips. The replacement directional
crypto bot had taken no trades. The market maker had $101.60, of which $0.42
was estimated rebates; its six completed pairs made about $0.20 each, while
unpaired results were -$2.47, +$3.83 and -$1.41. Those wins are directional
exposure, not evidence of consistent spread earnings. Primary and Research held
stock positions and were modestly below their starting values.

## Changes adopted

- Day trader v3 keeps the earnings catalyst and opening-range-low stop. Each entry
  fits a 0.25% modeled loss budget including costs; realized session losses plus
  remaining stop exposure must fit 1%. Opening gaps can exceed a stop budget.
- Market maker v2 uses one active market and budgets both legs together, assuming
  only the losing side might fill. Market loss is capped at 3% when quoting;
  inventory plus orders at 10% of equity. A completion quote must be profitable
  at the actual cost paid for its existing partner. Fills never exceed observed
  qualifying tape volume. Estimated rebates remain informational, excluded from cash.
- Directional crypto v2.1 keeps its probability model but reduces the exposure
  ceiling to 6% and budgets entries against the worst terminal outcome of open bets.
- Both active crypto engines refresh position marks before allowing new risk and
  honor frozen-strategy integrity. Daily losses trip a persistent 3% entry stop;
  10% lifetime drawdown halts the book. After a +2% daily peak, the entry budget
  preserves half the peak gain. Existing liabilities are not erased or instantly sold.
- Quote creation and fill processing are transactional. Missing trade tape keeps
  funds reserved; unresolved quotes defer settlement so delayed fills pay exactly once.
- No ledger resets, retroactive fills or edits to historical performance.

## Historical stock comparison

The entry signal is identical across variants, including the earnings filter.
One predeclared sizing policy and one trailing policy were compared; no parameter
search. The 1-minute and 5-minute windows overlap and were already inspected for
v2; neither is a fresh out-of-sample test. This is risk evidence, not proof of edge.

| Bars | Variant | Sessions | Return | Max closing drawdown | Second-half return |
|---|---|---:|---:|---:|---:|
| 1m | baseline | 20 | 2.38% | 1.46% | 0.34% |
| 1m | risk_sized | 20 | 0.58% | 0.50% | 0.10% |
| 1m | risk_and_trail | 20 | 0.29% | 0.50% | 0.10% |
| 5m | baseline | 46 | 11.78% | 1.76% | 2.06% |
| 5m | risk_sized | 46 | 3.05% | 0.50% | 0.29% |
| 5m | risk_and_trail | 46 | 2.78% | 0.65% | 0.00% |

The sizing policy deliberately traded away return for lower exposure. The optional
2R-activation/1R-distance trailing stop worsened the 1-minute result and was
rejected for deployment. Its implementation remains disabled in the active config
so the research replay is reproducible. The stock drawdown pause/halt thresholds
were tightened to 5%/10%; neither would have triggered in the sizing replay.

Crypto quote and execution changes cannot be honestly backtested from the saved
last-trade prices: historical full books and queue states were not recorded.
They were verified with deterministic scenarios, not assigned invented returns.

## Validation and reproduction

- Regression tests cover stale/missing marks, frozen integrity, daily-stop restart,
  profit giveback, partial inventory hedges, quote/fill crash rollback, cancellation,
  missing tape, volume caps, delayed settlement, risk sizing, and no same-bar lookahead.
- Independent code review found a delayed-hedge settlement collision. It was fixed
  and a failing-before/passing-after reproduction added.
- Full suite: **62 passed**, `.venv/bin/python -m pytest tests -q`.
- Historical replay: `.venv/bin/python -m research.revamp_2026_09_28.replay`.
  Requires the existing local `data/intraday` and `data/history/earnings.pkl`.
- Full numerical evidence is in `replay_results.json`; proposals and baseline
  configurations are kept alongside this report. `PLAN.md` records selection criteria.

## External checks

The existing taker-fee formula matches [Polymarket's fee documentation](https://docs.polymarket.com/trading/fees).
Rebate distributions depend on the program and participation; the simulator cannot
verify an allocation to a nonexistent paper wallet, so it no longer credits the
estimate ([maker rebates](https://docs.polymarket.com/programs/maker-rebates)).
Stop prices are not guaranteed execution prices, particularly during gaps or
volatility ([FINRA](https://www.finra.org/investors/insights/stop-orders-factors-consider-during-volatile-markets)).
