# What actually works? Strategy research and the trend book (2026-10-05)

## Evidence reviewed (web, 2026-10-05)
* Faber (2007), "A Quantitative Approach to Tactical Asset Allocation": 10-month moving-average timing across five asset classes.
  Original 1972-2005 backtest: Sharpe 0.81, max drawdown 9.5%; a recent out-of-sample update (2006-2025): Sharpe 0.68, CAGR ~6%, max drawdown ~11.7%.
  [Quantpedia](https://quantpedia.com/strategies/asset-class-trend-following), [Concretum](https://concretumgroup.com/global-tactical-asset-allocation/).
* Moskowitz, Ooi, Pedersen (2012) time-series momentum; dual momentum with crash protection reported 10.4% vs 8.2% CAGR for 60/40 (1993-2015).
  [Quantpedia sector momentum](https://quantpedia.com/strategies/sector-momentum-rotational-system), [CXO Advisory](https://www.cxoadvisory.com/technical-trading/dual-momentum-with-multi-market-breadth-crash-protection).
* McLean and Pontiff (2016): published anomalies lose about half their return after publication; post-earnings drift has faded
  ([Columbia](https://business.columbia.edu/sites/default/files-efs/imce-uploads/CEASA/Events%20Page/PEAD_Declined_over_time.pdf)).
* Nothing found supports short-horizon profits at this scale: edges are small, slow and decay.

## Our own test (tools/trend_research.py, output in trend_backtest_output.txt)
Free Yahoo adjusted closes, 2007-2026, monthly decisions executed the next day, 10 bp per side. Rules from the literature, not tuned.
| | CAGR | Vol | Sharpe | Max DD |
|---|---|---|---|---|
| SPY buy & hold | 11.0% | 19.6% | 0.63 | -55.2% |
| 60/40 SPY/IEF | 8.4% | 11.3% | 0.77 | -31.4% |
| SPY 10-month trend | 8.9% | 12.6% | 0.74 | -29.6% |
| Faber 5-asset, 8/10/12-month ensemble (deployed) | 5.3% | 7.8% | 0.70 | -14.5% |
| Dual momentum (12m) | 5.5% | 15.9% | 0.42 | -40.2% |
| Sector momentum top-3 (12m, 10m SMA) | 9.0% | 15.4% | 0.64 | -24.1% |

Ensemble by period: Sharpe 0.57 (2007-2016) and 0.85 (2017-2026); 2008: -4.9% vs SPY -36.2%; 2022: -11.7% vs SPY -18.8%.

## Honest reading
* Nothing here beat buy-and-hold SPY on return in a historic bull market. The trend rules cut drawdowns by 2-4x; that is their value.
* Dual momentum as implemented did not replicate; sector momentum was unstable across halves. Neither was deployed.
* 60/40 had the best Sharpe with no trading; it was not deployed because the trend ensemble is the published, tested method for risk control and it moves to Treasuries in downtrends.
* A book that makes monthly decisions cannot be evaluated in the remaining days of this experiment. It is paper-traded as the evidence-backed core, not as proof of profit.

## What was deployed
New book `trend` (strategy trend-1.0.0, papertrader/trend.py): month-end ensemble of SPY, EFA, IEF, GLD, VNQ with the remainder in SHY, ETF cost line (2 bp + 5 bp open auction).
Dry run on real days 2026-09-24 to 2026-10-02 in a scratch copy: first allocation, month-end evaluation inside the rebalance band, ledger audit OK, reports and state API include the book.
