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

---

## Addendum: day-trading book (written 2026-09-23, before its backtest)

The user asked for an aggressive day-trading model. That is a new book, not a change to the two frozen
books, which keep running untouched. Rules: `config/strategy_daytrade_v1.json`, with parameters taken
from Zarattini, Barbon & Aziz (2023) and not tuned. Long only, no leverage, cash-account settlement.

* **Data limit:** Yahoo provides only ~60 sessions of 5-minute history, so the backtest covers about 60
  trading days. That is far too short for statistical confidence, and it will be reported as such.
* **Split:** first half = in-sample, second half = out-of-sample; both are reported. No parameter changes
  based on either.
* **Decision rule:** the book goes live regardless (the user asked for it), but if the backtest loses
  money after costs, the reports and the app will say so plainly.
* **Survivorship:** today's S&P 500 list; over 60 days the effect is small.
* **News veto:** live only, not backtested.

### Day-trading backtest results (appended 2026-09-23)

| Test | Period | Sessions | Book | SPY same days | Trades | Win rate |
|---|---|---|---|---|---|---|
| Pre-registered, 5-minute execution | Jul 21 → Sep 23 | 46 | −15.5% | +2.9% | 142 | 6% |
| Same rules, 1-minute execution | Aug 26 → Sep 23 | 20 | −6.7% | +0.4% | 96 | 11% |

* **5-minute test was not a fair test.** The paper's stop (0.10 × ATR) is smaller than a typical 5-minute
  bar's range. 113 of 142 exits came from the pre-registered worst-case rule: when the entry bar's low
  also reaches the stop, assume the stop was hit. 5-minute bars can't show whether the low came before or
  after the breakout.
* **Deviation (disclosed):** the live book processes 1-minute bars, the resolution the paper used. No
  strategy parameter was changed. The worst-case same-bar rule is kept; it still decided 39 of 96 trades
  at 1 minute.
* **1-minute result:** about +0.8% before costs, −6.7% after 7.5% of modeled costs (spread and slippage on
  ~5 round trips a day on a $100 account). Out-of-sample half: −0.1%. Twenty sessions is statistically
  meaningless; the costs arithmetic is not.
* **Decision (as pre-registered):** the book goes live on 2026-09-24 because the user asked for an
  aggressive day-trading model. The app and reports show these backtest numbers next to the live results.

---

## Addendum: crypto odds bot (prediction markets), 2026-09-25

The user asked for a bot like the viral "Jev" posts: scan many Polymarket markets, compare live prices with
the posted odds, and bet when the gap clears a threshold. Rules (`config/strategy_pm_v1.json`) were
written before this test and were **not** changed after it.

**Calibration test.** 3 days of settled Up/Down windows (BTC/ETH 15-min, five coins 1-hour and 4-hour),
4,126 snapshots. The model was rebuilt at each point using only earlier exchange data:

* Accuracy score (lower = better): **market 0.149, model 0.183**. The market is better calibrated. The
  model is overconfident at the extremes: when it said 90–100% Up, Up happened 85% of the time.
* Replay of the exact entry rule (one bet per market, entry = history price + 1¢, Polymarket crypto taker
  fee): 1,079 bets, 73% won, **−1.1% return on stake**. By window: 15-min +3.3% (n=91), 1-hour −7.7%, 4-hour
  +4.6%. Selecting the positive subsets now would be fitting noise, so nothing is changed.
* **Limitations:** history prices are last trades, not asks, so real fills would be worse. Snapshots are
  every ~10 minutes, so 5-minute markets couldn't be tested. Only 3 days of data.

**Decision:** there's no evidence of an edge. It runs on paper anyway as its own $100 book so the forward
record exists, clearly labeled with these results.

### v1 post-mortem and v2 (appended 2026-09-25, evening)

**v1 live result, day one:** −$32.79 (−33%). 43 bets. Hourly markets lost $63.90 on $175 staked. The 30%
loss limit never fired because it was only checked once a day.

**Root cause (verified against official outcomes):**
* Hourly markets settle on **Binance's 1-hour candle close vs open** (35/35 matches).
* The 5-min, 15-min and 4-hour markets behave like end price vs start price: "end vs start" matched
  96–100% of settled windows, better than "average over the window".
* v1 priced all of them as window averages, which made it overconfident. It then bet against the market
  when they disagreed (e.g. buying at 8.8¢ because the model said 97%).

**What practitioners report** (public write-ups, treated as anecdotes):
* 11,717 trades at a 77% win rate netted $292, and 176 trades at a 92% win rate netted $2. Buying
  favorites needs very high accuracy.
* Settle-source prices (Chainlink/Binance) matter: spot prices can diverge 0.3–0.5%.
* Speed arbitrage is captured by sub-100 ms bots, and makers earn rebates while takers pay fees.
* On-chain studies report ~84% of Polymarket wallets lose money.

**v2 (`config/strategy_pm_v2.json`), rules written before its test:**
* Close-vs-open math, with Binance data.
* Estimate anchored halfway to the market's odds; skip when model and market differ by more than 20 points.
* Buy only between 30¢ and 75¢, at 10–70% of the window.
* BTC/ETH only; 3% stakes; one bet per settlement time and direction.
* Loss limits checked every run: 20% drawdown halt, 6% daily limit.

**v2 replay, 6 days (Sep 19–25), 1,506 settled BTC/ETH markets: 0 qualifying bets.** Diagnostics on one
day (280 decision points):
* Model minus market: median −2 points; 80% of points within ±10.
* Best edge after fee and a 1¢ spread: −0.5¢.

At the resolution this system can observe (runs every 20–60 minutes), the market leaves no edge after
fees. v2 runs on paper so any genuine opportunity is recorded; expect it to bet rarely or never. v1 is
retired: no new bets, open bets settle, record unchanged.

---

## Addendum: market maker (2026-09-25)

The user asked to add the market-making approach, which is where public reports say the steady profits in
these markets go. Rules: `config/strategy_mm_v1.json`.

* **Quotes:** bids on both Up and Down of live BTC/ETH 15-minute and 1-hour markets, costing at most 98¢
  per pair. Each joins the best bid, or improves it by 1¢ when there's room. Quotes last 5 minutes, only
  in the first half of a window.
* **Sizing:** equal shares on both sides, about 10% of equity per pair. If only one side filled, only the
  missing side is quoted afterwards.
* **Fills:** simulated from Polymarket's public taker-trade tape, respecting the queue ahead of the order
  at placement (a real exchange's time priority). Complementary trades count; a trade through the price
  fills the whole order. Fills are at the limit price, no fee.
* **Rebates:** 20% of the taker fee, as an estimate.
* **Risk:** the 20% drawdown and 6% daily loss limits are checked every run.
* **No backtest:** historical order books aren't available, so there's no honest way to reconstruct past
  quotes. It's a forward paper test only.

**Pre-launch dry run (throwaway ledger), which exposed a design flaw fixed before freezing.** The first
draft sized each side at the same dollar amount, which buys unequal share counts (7.04 Up at 71¢ vs 18.51
Down at 27¢). Only matched shares form a riskless pair, so sizing now uses equal shares. In the same dry
run, 2 of 6 quotes filled (one ETH pair); the BTC quotes and the hourly ones were behind 39–802 queued
shares and didn't fill.

**Expected risks:**
* Adverse selection: one side fills when the price is moving against it.
* Queue position: our paper orders can't know about cancellations ahead of them, so fills may be
  understated or overstated.
* Quotes are only live for about 5 minutes per cloud run, so fill opportunities are limited.

---

## Addendum: day-trader improvement test (written 2026-09-26, before results)

**Live evidence:** 10 trades, 10 losses, all stopped out within minutes (Sep 24–25). The 0.10×ATR stop is
tighter than normal intraday noise.

**Variants (declared before running):**
* **A** Current frozen rules.
* **B** Earnings catalyst: only stocks in play whose earnings reaction day is today (reported after
  yesterday's close or before today's open). Timing comes from the earnings calendar, so there's no
  look-ahead.
* **C** Wider stop: at the low of the first 5-minute bar (standard opening-range practice) instead of
  0.10×ATR.
* **D** B + C.

**Data:** 5-minute execution (46 sessions) and 1-minute execution (20 sessions), same cost model.

**Adoption rule:** a variant replaces A only if it beats A on total return in **both** data sets **and** in
both halves of the 46-session set. If several qualify, the one with the higher 1-minute return wins. If
none qualify, A stays. Historical news with intraday timestamps isn't freely available (Google News history
has dates only), so news and social filters beyond the earnings calendar can't be tested this way. They'd
be collected forward (StockTwits sentiment is free and live) and evaluated later.

### Day-trader variant results (appended after running)

| | 5-min, 46 sessions | halves | 1-min, 20 sessions | trades (1-min) | win rate (1-min) |
|---|---|---|---|---|---|
| A current | −15.5% | −12.9% / −3.0% | −6.7% | 96 | 11% |
| B earnings catalyst | −8.7% | −6.9% / −2.0% | −2.0% | 13 | 0% |
| C wide stop | +2.6% | +10.5% / −7.2% | −2.6% | 96 | 34% |
| **D both** | **+11.8%** | **+9.5% / +2.1%** | **+2.4%** | 13 | 46% |
| SPY same days | +2.9% | | +0.4% | | |

* **Result:** B and D pass the adoption rule; C fails the second half. **D is adopted** (higher 1-minute
  return), effective 2026-09-28, via `run.py log-change`, so the day-one history is kept.
* **Caveats:** the 1-minute sample has only 13 trades, and the two periods overlap. D only trades on days
  with earnings reports, so expect idle days until earnings season (mid-October).
