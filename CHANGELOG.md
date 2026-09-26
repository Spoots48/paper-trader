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
