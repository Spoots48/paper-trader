# Harsher crypto strategy: what was tested (2026-10-07)

Request: "try a harsher investment strategy on crypto" (win rate 49%, profits only cents). Paper money only. Everything below was tested on
history before anything was deployed; outputs are in this folder.

## 1. Aggressive rules on the 15-minute Polymarket BTC/ETH up/down markets (crypto_aggressive_output.txt)
2,306 settled markets, real taker-buy prices from the public trade tape, fee 7% * p * (1-p), one decision per market using only earlier data,
14 rules x 3 decision times: model edge (any size), follow/fade the move, favorites, longshots, 5-minute momentum.
Result: no rule has a reliable edge. EV per share ranged about -0.075 to +0.03, mostly within one or two standard errors of zero, and signs flip
between the first and second half. Betting the model's pick at any edge wins about 49% at an average price near 0.50 (EV about -2c per $) - the 49%
win rate is simply a fairly priced coin. Sizing up multiplies a small negative expectation; it was NOT deployed.

## 2. Daily trend-following on BTC and ETH, optionally leveraged (crypto_trend_output.txt)
Binance daily candles from 2017-09, SMA 50/100/200, 1x/2x/3x, 10 bp per side, 0.03%/day funding on leveraged notional, liquidation from the day's low.
Unleveraged trend beat buy-and-hold in BOTH 2017-2021 and 2022-2026 for every window (BTC 2022-2026: 22-30%/yr vs 12%; ETH: 8-28% vs -8%) with max drawdown
-32% to -52% vs -67%/-74%. Leverage did not help: 2x added little with -60% to -98% drawdowns; 3x was liquidated on ETH and on BTC SMA100. Leverage rejected.

## 3. Deployable design (crypto_etf_trend_output.txt)
50% IBIT + 50% ETHA, scaled by how many of the 50/100/200-session SMAs each is above, rest in SHY, weekly decisions, 7 bp per side, no leverage.
2018-2026: CAGR 36% vs 29% buy-and-hold, vol 46%, max drawdown -60% vs -88%. 2022-2026 (out of sample): weekly +10.9% vs +1.5%, max drawdown -39% vs -69%.
Signals in the backtest use BTC-USD/ETH-USD sampled on NYSE sessions; the live book uses the ETFs' own closes (IBIT since 2024-01, ETHA since 2024-07).

## Honest reading
The edge out of sample is modest (about +9 points a year over buy-and-hold) and the risk is large. Right now both coins are above all three averages, so the book starts fully invested;
15-day volatility is about +/-9%, so the next two weeks are mostly luck either way. Crypto history is short and was a strong bull market for much of the sample. No profit claim.
