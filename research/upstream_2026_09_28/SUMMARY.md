# Summary of the 2026-09-28 revamp

**No profitable strategy has been established.** Everything here is risk-control, data-quality and infrastructure
work on a paper-only experiment ($100 per book, no real money). Unit tests, a synthetic check and news reviews are
not profit evidence. The only valid evidence is forward, out-of-sample results from the frozen versions below,
judged against SPY and cash after costs; there are only days of it so far.

## What changed (activated through `run.py log-change`, append-only, frozen hashes verified)
* crypto2 `pm-2.1.0 -> pm-2.2.0` and mm `mm-2.0.0 -> mm-2.1.0`:
  * closed-candle volatility window and freshness/skew checks (`data_quality`: 30 s max age, 10 s max skew, 5 s future tolerance);
  * ledger-derived cooldown (`protections`: 2 net-losing markets in 240 min -> 60 min pause on new entries);
  * mm bids at least 0.005 below their own book midpoint, rounded down to the tick.
  * Risk budgets, cash, sizing and drawdown limits were not touched. These protections can only reduce trading; they are not optimized alpha and may lower returns.
* Cloud workflow: the full test suite runs before any cycle; if tests, restore or verification fail, no cycle runs and no state is dumped over the ledgers. Failed cycles exit non-zero.
* Day-trading, primary, research and retired crypto v1 books: unchanged strategies and history.

## Tests and verification
* 109 tests pass in the runtime (new: market quality, entry protections, cycle health, Laya worker, midpoint/tick rounding).
* `run.py verify`: audit chain, frozen-strategy hash and cash reconciliation OK on all six ledgers after activation and after the first cloud run.
* Cloud run [36511991233](https://github.com/Spoots48/paper-trader/actions/runs/36511991233) after the push: every step green (tests, restore, verify, cycle, dump, commit). Both changed books reported "no action needed" that cycle, so this shows the deployment works, not that the strategies earn anything.

## Laya (news review, shadow only)
Measured on a small labelled set (48 items) whose thresholds were adjusted after looking at results, so treat these numbers as optimistic:
* Event classification: 27% answered (13/48), all 13 correct; forced answers were 52% right. Only 2 of 12 true adverse events were caught confidently (9 of 12 if forced to answer, at the cost of many false alarms). Not usable as a detector.
* Tone: 35% abstain; 90% right when answered, with 3 confident errors. Real negative-tone flags mostly restated price drops.
* `answer_confidence` is not a profit signal and its calibration on financial news is unverified. Laya reviews the news ledgers in the background (`data/laya/`), never gates, sizes or places orders, and is not in the cloud requirements.

## Storage
Project files, the runtime (`installed/runtime`), app, logs, models, caches and temp files are on `/Volumes/X10 Pro/Paper Trading Sim`. Only OS registration/compatibility links remain internal (`~/Applications/Paper Trader.app` symlink and two Library symlinks). Ledger hashes before the move are in `migration.json`.

## Cloud vs Mac
Trading runs in GitHub Actions on its own schedule and does not need the Mac. The Mac app only pulls, restores and shows results, and dispatches extra runs when open. With the Mac off GitHub may delay or drop scheduled runs, so cadence can be sparser.

## Limitations and open issues
* Cloud run 36476073409 (2026-09-28 19:59Z) failed at the commit step ("Pulling is not possible because you have unmerged files"); its state changes were not committed. Root cause not determined; later runs succeeded.
* The launchd job exits 126 on this Mac: macOS blocks launchd-spawned `/bin/bash` from the external volume until the user grants it access in System Settings. The job is therefore unloaded; the cloud is unaffected.
* Jev, the Opus API and TradingAgents need paid keys only the user can create; not used.

## What evidence would matter
Weeks of forward results per frozen version, net of the modeled costs, beating SPY and cash, with drawdown inside budget and no config changes mid-test. Until then: no claim.
