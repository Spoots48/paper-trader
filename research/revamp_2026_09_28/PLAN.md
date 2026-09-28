# Capital preservation revamp — 2026-09-28

The user requested a serious strategy revamp after repeated losses and rapid giveback.
This is a paper-only experiment; preserve every historical fill and snapshot.

Observed ledger at 2026-09-28 21:37 UTC: original crypto -$25.78 (retired),
day trader -$1.18, crypto v2 zero trades, market maker +$1.60 including $0.42
of estimated rebates. Six paired market-maker outcomes earned about $0.20 each;
one unpaired loss cost $2.47, another $1.41, one unpaired win made $3.83.
The record does not establish a profitable edge.

Implementation order and acceptance:
1. Reproduce and fix stale pre-risk valuation, missing integrity gates, non-latching daily limits.
2. Market maker: batch both quotes atomically, reserve inventory plus resting quotes,
   size to worst-case one-sided fills, only one active market, evaluate hedge cost
   against the actual old inventory, count observed tape volume, no estimated rebate cash.
3. Day trader: keep the existing earnings selection. Test a single risk-sizing proposal
   (0.25% per trade, 1% session loss budget, including entry and stop costs), and
   one optional trailing proposal (activate after 2 initial stop distances, trail 1 distance
   from completed closes, effective next bar). Compare baseline, sizing alone and
   sizing plus trail on the existing 1m and 5m data; no parameter search.
   Adopt sizing for a smaller loss budget; adopt trail only if it does not worsen
   full-period or second-half return on either resolution. These are previously
   inspected samples, not fresh out-of-sample evidence.
4. Regression tests, full suite, independent review; logged version changes and cloud
   verification before declaring active. No balance resets or rewriting past reports.

Risk parameters for prediction markets: 10% lifetime drawdown, 3% daily loss limit,
profit protection armed at +2% in a day and stopped after 50% giveback. Entry budgets
must preserve that floor even if all unpaired bets lose. Existing liabilities can
already exceed a newly raised floor; stops suppress new risk and cannot guarantee
an exit price or reverse a loss. Markets with minimum size exceeding the budget are skipped.

Validation: `.venv/bin/python -m pytest tests -q`. No new dependencies.
