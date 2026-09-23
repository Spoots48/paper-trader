# Paper Trader — 30-day paper-trading experiment

**Paper trading only.** No brokerage account, no credentials, no real orders, no money. Everything runs
locally on this Mac with free data sources. Cost: $0.

- **Window:** 2026-09-23 (Day 1) → 2026-10-22 (Day 30), $100 simulated cash per book
- **Reports:** Day 7 (Sep 29), 14 (Oct 6), 21 (Oct 13), 28 (Oct 20), final Day 30 (Oct 22). Each is
  generated after that day's close and announced with a macOS notification.
- **Benchmarks:** $100 in SPY bought at the first open (same cost model, dividends included), and $100 cash.

## How to use it

Open **Paper Trader** (in `~/Applications`, or search Spotlight). The app shows:

- the portfolio chart against SPY and cash
- holdings with their stops
- every trade and order
- every decision with its reasoning, the data it used, and the news headlines behind it (with publish and retrieval times)
- the weekly reports, the backtest, run logs and integrity checks

There are no buttons to press: runs happen automatically on schedule and the app updates itself.
The ••• menu only has shortcuts (open on GitHub, open the folder, light/dark).

Command line (from this folder):

```
.venv/bin/python run.py status     # summary
.venv/bin/python run.py verify     # audit chain + frozen-strategy hash + cash reconciliation
.venv/bin/python run.py cycle      # one cycle now
```

`dashboard/index.html` is a static read-only snapshot, refreshed after every cycle. It opens in any browser.

## Where it runs: GitHub's cloud (works with the Mac off)

Trading runs on **GitHub Actions** in the private repo
[Spoots48/paper-trader](https://github.com/Spoots48/paper-trader) (`.github/workflows/cycle.yml`). It runs
about 7 times per trading day: after the close (decides the next open, plus two backups), before the open,
just after the open (fills), and midday and late-day checks. Each run:

1. restores the ledgers from `state/*.sql` (text, versioned in git)
2. verifies the audit chain, frozen strategy hashes and cash
3. runs one cycle
4. commits `state/` and any new `reports/` back

- **Cost:** $0. The repo is private (2,000 free minutes a month; this uses about 300). With no payment
  method on file, GitHub blocks usage at the quota instead of charging.
- **Alerts:** GitHub emails you when a run fails. Each weekly report is also posted as a GitHub issue,
  which emails you.
- **Timing caveats:** scheduled runs can be delayed or occasionally dropped by GitHub. Backups are
  scheduled in each key window. A decision window that's entirely missed is logged, never back-filled.
  Standing stop-losses are always applied from the price history on the next run.

**Your Mac is a viewer.** The Paper Trader app pulls the latest state from GitHub every 90 seconds while
it's open. The background job (`com.papertradingsim.cycle`) also syncs every 15 minutes while the Mac is
awake and online, and shows a macOS notification when a new report arrives.

The local copy lives on the internal disk (`~/Library/Application Support/PaperTradingSim/runtime`,
about 25 MB), so the external drive is never needed. `config/deployment.json` sets the mode
(`cloud`/`local`). Only one place trades at a time.

## The two books (both frozen 2026-09-22 before any live trade)

**Primary: regime-gated SPY.** The rules that passed the pre-registered backtest. Hold SPY (98%, 2%
cash buffer) while SPY is above its 200-day average and VIX is below 30 (re-enter below 25). Otherwise
hold cash.

**Research: the original v1 strategy, forward-tested.** Up to 4 stocks at 20% each; leftover cash in SPY.
- *Earnings-gap continuation:* S&P 500 stocks up ≥5% on their earnings reaction day (≥4% more than SPY),
  on ≥2× normal volume, closing in the upper half of the day's range. Buys must be **confirmed** by a
  timestamped earnings headline published before the decision. They're **vetoed** by offerings,
  investigations, restatements, bankruptcy or takeover news, or by net-negative tone. Exits: an 8% stop
  (or the reaction-day low), a 10% trailing stop, and a 20-session time limit.
- *Momentum:* up to 2 of the strongest 6-month (skip last week), volatility-adjusted stocks in confirmed
  uptrends. Rebalanced weekly, never held through earnings, 12% trailing stop. News can only veto.

**Risk controls (both books):** a 10% drawdown pauses new stock entries for 5 sessions. A 15% drawdown
liquidates everything and holds cash for the rest of the experiment. No leverage, shorts or options.
Fractional shares.

### Why it might work, and why it might not

- Post-earnings drift and momentum are two of the most studied return patterns (Bernard & Thomas 1989;
  Jegadeesh & Titman 1993). The news filter tries to avoid known traps: dilution, fraud, and takeover
  targets whose price is pinned to the deal.
- **The backtest does not support them here.** On S&P 500 stocks from 2016–2021 with realistic costs,
  the earnings-gap signal had ~0 excess return and was negative in 2022–2026. The full strategy
  compounded at 3.2%/yr vs SPY's 16.7%. Momentum hurt in-sample but helped out-of-sample. The regime
  filter cut drawdowns (19.5% vs 31.8%) but gave up a lot of return by missing V-shaped rebounds.
  Details: [`research/PREREGISTRATION.md`](research/PREREGISTRATION.md).
- Failure modes: crowded, decaying signals; momentum crashes (e.g. Nov 2020); gap reversals; whipsaws
  around the 200-day average; free data being late or wrong.

## Execution realism

- A decision only uses data available at decision time. Every fill uses a price observed **after** the
  decision:
  - the official open, for orders placed before the open;
  - otherwise, the open of the next 5-minute bar.
- Costs per side:
  - SPY 2 bp; stocks 5 / 10 / 20 bp by liquidity
  - +5 bp at the open, +15 bp on stop fills
  - SEC fee on sells; $0 commission
- Stale, missing or inconsistent data means no trade. Examples:
  - If the Nasdaq earnings calendar fails for a day in the blackout window, momentum entries are skipped.
  - If both news sources fail, research entries are skipped.
- Yahoo often lacks the official close until the next morning. After 30 minutes the daily bar is rebuilt
  from 5-minute data, and it's **flagged** wherever it's used.
- Dividends are credited on the ex-date. Splits adjust positions.

## Integrity

- `fills`, `snapshots`, `decisions`, `news` and the audit `events` are **append-only**; SQLite triggers
  reject edits and deletes.
- Every write is also recorded in a SHA-256 hash chain, checked by `run.py verify`.
- Order and fill keys are unique, so a retried or crashed job can't duplicate a trade. Each session
  close-out is a single transaction.
- Strategy files are hashed at freeze time. If a file changes without a logged change
  (`run.py log-change`, which also appends to `CHANGELOG.md`), new decisions stop.
- Proposed improvements must be tested separately (`run.py backtest` with a new config). They're never
  applied retroactively.

Tests: `.venv/bin/python -m pytest tests -q`. That includes a full offline simulation covering an
offline day, an intraday stop, a mid-transaction crash, retries and report generation.

## Data sources (verified 2026-09-22)

| Source | Used for | Notes |
|---|---|---|
| Yahoo Finance via `yfinance` (free, unofficial, no key) | daily & 5-min prices, ticker news, earnings history | today's official close often missing until the next day, which is handled |
| Nasdaq public API | forward earnings calendar (pre/after-market) | occasional timeouts, retried |
| Google News RSS | second news source, with publish times | |
| Wikipedia | S&P 500 constituents + index-inclusion dates | frozen in `config/universe.json` |
| Not usable | GDELT (1 request / 5 s), Stooq (JavaScript wall), FRED (timeouts) | |

## What one month can tell you

Very little about long-run skill. In the backtest, a single month's return relative to SPY varied by
roughly ±3.5–4.4 percentage points (1 standard deviation). The losing strategy still beat SPY in 34–40%
of 30-day windows. Treat the result as a test of the process, not proof of an edge.

## Files

Live copy (internal disk): `~/Library/Application Support/PaperTradingSim/runtime/`, laid out the same
way. The app's Files menu opens its reports and logs.

`papertrader/` code · `config/` frozen strategies, experiment and universe · `data/` ledgers and market
cache · `reports/` weekly reports · `research/` backtest and pre-registration · `app/` Mac app source
(run `bash app/build_app.sh` from the live copy to rebuild it) · `scripts/` scheduler install/uninstall · `logs/` cycle logs
(launchd logs are in `~/Library/Logs/PaperTradingSim/`).

**To stop everything:** disable the `cycle` workflow on GitHub (Actions tab). Run `bash scripts/uninstall_scheduler.sh`
to remove the Mac's sync job. After Day 30 the cloud job does nothing, so disable it then.

Not investment advice.
