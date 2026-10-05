# virattt/ai-hedge-fund review (2026-10-05)

Source: <https://github.com/virattt/ai-hedge-fund> at [78b779c1](https://github.com/virattt/ai-hedge-fund/tree/78b779c1389e2d1452dc29606d2c4126d859b964), MIT.
Read-only clone, nothing installed or run. Read: README, VISION, ROADMAP, signals/, risk/, event_study/, data/client.py.

## What it is
An educational framework: LLM "investor" agents (Buffett, Munger, Graham, Lynch, Druckenmiller) and one quant model
(post-earnings drift) emit a conviction in [-1, +1]; deterministic code builds weights, hard risk limits clamp them, a simulated
or paper broker fills them, and a hash-chained ledger records each session. It states it is not for real trading and makes no
performance claim; no results are included.

## What works (and is worth borrowing)
* LLMs never touch the trade: they emit a view; sizing, limits and orders are plain code. Matches our Laya rule.
* Risk "clamps are never redistributed": exposure removed by a limit stays in cash. We already size this way.
* Decide at close T, execute at T+1; reconcile broker vs ledger before each session and raise on mismatch. Same spirit as our `verify`.
* LLM failure = abstain (value 0), data failure = fail loudly. Same as how we treat Laya abstentions and data-quality rejects.
* PEAD only trusts the earnings announcement date (8-K), not the later 10-Q filing date, and drops stale/retrospective rows.
* An event-study engine (market-model abnormal returns around earnings). This is the tool our day trader's "earnings catalyst" premise needs: it would
  show whether stocks actually drift after earnings, net of the market, before we trade it.

## What does not (or is unproven)
* No evidence of profit anywhere in the repo; the investor agents are style imitations with no demonstrated edge.
* Daily-close horizon with LLM calls per name; not an intraday or market-making design, so little transfers to our fastest books.
* Needs paid keys: a Financial Datasets key for data plus an LLM provider key. Not free, so not usable under our zero-cost rule.
* Its own roadmap lists the overfitting gate (CPCV/PBO), live trading, the research lab and auto-promotion as not built.
* Backtest and paper modes exist, but "the same code path" does not prove an edge.

## Decision
No code copied, no dependency added. Possible free follow-up, not done: an event study of earnings-day drift using our own free
daily bars and Nasdaq earnings dates, to test the day trader's catalyst filter out of sample.
