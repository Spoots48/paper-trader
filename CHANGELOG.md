# Change log

Strategy changes are appended here automatically by `run.py log-change`. Past results are never rewritten.

## 2026-09-22 — initial freeze

- Primary book: `config/strategy_v1_primary.json` v1.0.0-primary, sha256 `08c6983d1764dc56…`
- Research book: `config/strategy_v1.json` v1.0.0, sha256 `772a55667e521068…`
- Universe: `config/universe.json`, sha256 `172ba39de91f49af…`
- First decisions made 2026-09-22 21:43 ET for the 2026-09-23 open.

## 2026-09-26T15:38:48Z — daytrade: dt-1.0.0 → dt-2.0.0

Day trader v2: only trade stocks in play that just reported earnings (Nasdaq calendar), and put the stop at the low of the first 5-minute bar instead of 0.10 x ATR. v1 lost all 10 live trades to stops hit by normal noise.

Evidence: Pre-registered 4-variant test (research/PREREGISTRATION.md, research/dt_variants.json): 46 sessions 5-min data -15.5% -> +11.8% (halves -12.9%/-3.0% -> +9.5%/+2.1%); 20 sessions 1-min data -6.7% -> +2.4% (13 trades, 46% won). SPY +2.9% / +0.4%. Small, overlapping samples.

## 2026-09-26 — reporting: daily reports added; valuation fix for unresolved prediction-market bets (no strategy change)

- Daily reports (`papertrader/daily_report.py`): one plain-English recap per New York calendar day, made just after midnight ET, saved as `reports/daily_YYYY-MM-DD.{html,md,json}` and never overwritten. The weekly/final reports (days 7, 14, 21, 28, 30) are unchanged. Days 1–3 were backfilled on 2026-09-26 and are marked as made late.
- Prediction-market end-of-day values: a bet whose market has ended but isn't resolved yet (so it has no price) is now valued at cost instead of $0. This affected one saved value: Market maker 2026-09-25 ($90.07 saved; about $100.07 true). The saved value is left as recorded, and the daily report carries an explanatory note (`config/report_notes.json`).

## 2026-09-28T22:03:00Z — mm: mm-1.0.0 → mm-2.0.0

Market maker v2: size atomic quote pairs by one-sided loss, limit inventory and resting orders, hedge using actual acquisition cost, volume-limit fills, exclude estimated rebates from cash. Current marks, persistent daily stops and protected profit budget; robust delayed settlement.

Evidence: research/revamp_2026_09_28/SUMMARY.md: 62 tests passed; independent review; fixed-variant replay at 1m/5m. Drawdown improved but returns lower; no claim of proven profit.

## 2026-09-28T22:03:00Z — crypto2: pm-2.0.0 → pm-2.1.0

Crypto v2.1: retain probability model, refresh marks before risk, enforce strategy integrity, persist daily loss and profit-protection stops, and cap entries by remaining worst-case settlement budget.

Evidence: research/revamp_2026_09_28/SUMMARY.md: 62 tests passed; independent review; fixed-variant replay at 1m/5m. Drawdown improved but returns lower; no claim of proven profit.

## 2026-09-28T22:03:00Z — daytrade: dt-2.0.0 → dt-3.0.0

Day trader v3: retain earnings-catalyst opening-range rules, size to 0.25% risk per trade including costs within a 1% session stop-loss budget. Tighten drawdown pause/halt to 5%/10%. Tested trailing-stop proposal rejected.

Evidence: research/revamp_2026_09_28/SUMMARY.md: 62 tests passed; independent review; fixed-variant replay at 1m/5m. Drawdown improved but returns lower; no claim of proven profit.
