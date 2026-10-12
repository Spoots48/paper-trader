# Research pass, 2026-10-12: what the literature and repos say, what was tested, what was adopted

Requested by the user: look at more GitHub repos and strategies, apply them to every book (especially the speed trader), add a memecoin book. This file records what was found and, just as important, what did not survive testing. Nothing here is a profit claim.

## 1. Measured today (our own data)

**Jev's speed-trader probabilities carry no information (so far).** 249 logged calls on 2026-10-12 scored against the next 8 minutes of 1-minute bars: Jev's mean probability 45.5%; the target (+0.30% before -0.25%) was actually hit 7.2% of the time (9.7% over every bar of the same stocks). By bucket: p<0.42 hit 10.4%, 0.42-0.46 8.2%, 0.46-0.50 8.4%, p>=0.50 hit 0 of 45. Correlation of p with the outcome: -0.10. One quiet day, so it is not conclusive, but there is no sign of skill and the probabilities are wildly miscalibrated. The 0.65 entry threshold was never reached (max 0.54), so the book made no trades. The nightly review now scores this automatically (`papertrader/jev_calibration.py`, section in `reports/review_<date>.md`).

**The speed book's mechanical part has no edge either.** 8 sessions of 1-minute bars, 14,000+ simulated entries, same exit rules: candidates chosen by the prefilter lose about 0.070% per trade after assumed costs; random bars lose 0.069%. The prefilter adds nothing. All profit would have to come from Jev.

**41 pre-declared intraday rule variants on 60 days of 5-minute bars, 21 liquid stocks/ETFs, 3 bp per side (`tools/intraday_family_research.py`, output in `intraday_families_output.txt`): 0 passed** the bar (day-clustered t >= 3 net of costs AND positive in both date halves). Families: opening-range breakout (5/15/30 min, opening-range or 10%-ATR stop, all stocks or relative volume >= 1.5, long/short or long-only), VWAP deviation reversion/continuation, volume-spike follow/fade (too few events), first-half-hour -> last-half-hour on ETFs. The published 10%-ATR stop loses the most on this universe (-7 to -22 bp per trade). The best-looking cell, ORB on high-relative-volume names with an opening-range stop, is positive in both halves but with t = 0.3-1.2 on 43-119 trades, and it is the best of 41 tries; that is not evidence.

## 2. Sources and what was taken from them (ideas only; every implementation here is independent)

| Source | Claim / content | Verdict here |
|---|---|---|
| Zarattini, Barbon, Aziz (2024), "A Profitable Day Trading Strategy For The U.S. Equity Market", SSRN 4729284 | ORB on "stocks in play" (high relative volume), Sharpe 2.81 on 7,000+ US stocks 2016-2023, news-driven small caps | Not reproduced on 21 mega-caps; family tested (above). A QuantConnect recreation reports 2.4 with different universe/rules. Universe is the difference; we cannot screen 7,000 stocks for free in real time. |
| Gao, Han, Li, Zhou (2018, J. Financial Economics), "Market intraday momentum" | first half-hour return predicts last half-hour return on SPY 1993-2013 | Tested on 4 ETFs over 44 days: -5.9 bp/trade net, t = -3.8. A 44-day window cannot confirm or refute a 1993-2013 effect, but there is nothing to adopt. |
| quantrocket-codeload/first-last, /trend-day (Apache-2.0) | reference implementations of the above | Read as specifications only; nothing copied. |
| freqtrade/freqtrade-strategies (GPL-3.0, 5.5k stars) | many TA strategies | GPL: nothing copied. Community strategy collections are overwhelmingly curve-fit; none adopted without our own out-of-sample test. |
| Faber (2007) trend, Antonacci dual momentum | slow trend rules | Already live (trend, ctrend books). |
| X (Twitter) API | no free read tier since 2026-02; about $0.005 per post read | Breaks the zero-cost rule. Not used. Bluesky search and Reddit JSON are blocked without credentials (tested). |
| DexScreener, GeckoTerminal, RugCheck public APIs | free pool prices, liquidity, trade counts, trending, rug flags (tested live) | Used by the memecoin book. |
| "Free 2026 Solana sniper bot" repos (several, 80+ stars) | click-to-run bots that ask for a wallet key | **Do not run these.** They match the usual wallet-drainer pattern. Not downloaded, not read beyond the listing. Never put a real wallet or key near any of them. |

## 3. Decisions

1. **No existing strategy was changed.** The rules say a change needs a logged `log-change`, an out-of-sample test and 30+ live trades. Nothing found today meets that, and several things found today argue against the speed book's premise.
2. **Speed book: left frozen, collecting calibration only.** With the 0.65 threshold unreachable it cannot lose money while it collects Jev's calibration data. Pre-registered decision: after the 2026-10-14 close (about 750 scored calls), retire the speed book (stop Jev calls) unless Jev's p >= 0.50 bucket has at least 30 calls and hits at least twice the base rate. Do NOT lower the threshold to force trades: the highest bucket hit 0 of 45.
3. **New `meme` book (meme-1.0.0), starts 2026-10-13.** Forward test only, no historical tape. Honest expectations: few entries (the liquidity/age/rug screen rejects most tokens), and most memecoin strategies lose after real frictions. Fills are deliberately worse than reality would be on average.
4. **Eight sessions remain** (experiment ends 2026-10-22). No new rule can produce meaningful evidence in that time. If the user wants real evidence, the experiment would have to run for months with slow, low-turnover rules (trend books), not days of fast ones.
