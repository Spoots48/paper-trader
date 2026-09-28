# Four improvement rounds, fixed before new results — 2026-09-28

Objective: seek higher net return, rather than simply increasing the amount at risk.
All experiments are paper research. Intraday risk stays at v3's 0.25% per trade,
1% session budget, 20% position ceiling. No leverage, shorts, options or balance resets.

Data: saved June–September 2026 intraday bars; archived 2015–2026 daily bars.
These datasets have been examined previously. The final chronological check is
reserved from THIS selection procedure; it is not a new independent holdout.

Rounds (each challenger uses the incumbent carried from the preceding round):
1. Selection: (a) earnings plus >=2x opening relative volume; (b) earnings plus
   opening close in top quarter of range; (c) broaden beyond earnings only when
   opening relative volume >=2x and opening gap >=2% above prior close.
2. Entries: (a) expiry 60 minutes after open; (b) a completed FIVE-minute close
   above trigger, enter next bar open; (c) that confirmation followed by a pullback
   to the old range high that closes back above it, enter next bar open. Entry
   confirmations use 5-minute bars at both execution resolutions. No signal/fill
   on the same bar, no favorable same-bar sequencing.
3. Exits: (a) preplaced 2R profit target; (b) preplaced 3R target; (c) cancel weak
   trades after 60 minutes if close has not reached +0.5R, exit next bar open.
   Stops have priority when both stop and target are touched. R is initial stop distance.
4. Slower alternatives: compare the original primary strategy against a pure
   200-day SPY trend filter (remove VIX gate), weekly SPY trend decisions,
   and monthly 12-month absolute momentum. Same next-open fills, 98% allocation,
   dividend credit, 7bp entry/7.3bp exit; same 15% drawdown/21-session research halt.
   Separately report plain 98% SPY buy-and-hold. This is a different overnight risk
   profile and cannot be presented as like-for-like with intraday risk.

Selection for rounds 1–3: first 30 of 46 five-minute sessions, split into two
15-session development folds. Promote an incumbent only when both folds exceed
its net return, total net return is positive, at least 10 round trips are present,
and full development drawdown is no more than incumbent +0.25 percentage points.
No parameter grid or threshold revisions after results. Otherwise retain incumbent.
Run rounds sequentially and save every failure, not just the best result.

Final intraday check: final 16 five-minute sessions; same dates at one-minute
execution; doubled costs; best trade removed; day-block bootstrap of excess
returns. An actual main-book change additionally requires >0 net return and
improvement over v3 at both resolutions on those dates, improvement at doubled
costs, >=10 final-period trades, and positive lower 95% block-bootstrap bound.
Otherwise keep it research-only (no silently relaxed threshold).

Round 4 selection: 2016–2021 development, then freeze the chosen candidate and
check 2022–2026 once. Require higher CAGR, no more than +2 percentage points
max drawdown, and excess improvement in at least two of three two-year development
blocks. Compare the unselected candidates only in development. No automatic main
book deployment of a research-only implementation without live-parity tests.

Validation: regression tests for all new mechanics, baseline parity against the
previous replay, full pytest suite, independent code review. Persist a report
per round, full results, source/data hashes and the final decision. Publish the
research artifacts to the existing project without falsifying historical returns.
