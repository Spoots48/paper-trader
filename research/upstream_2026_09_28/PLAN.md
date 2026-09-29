# Upstream mechanisms, 28 September 2026

Implement independently in the existing Python simulator; do not install entire bots,
run upstream installers, copy their runtime code, or connect trading credentials.
The simulator uses Python 3.13, pandas 3.0.6, numpy 2.5.3 and requests 2.34.2.

1. Jesse: require a complete, contiguous, closed one-minute volatility window.
   Reject invalid/duplicate candles and nonpositive prices; never quietly substitute
   a volatility floor for missing history. Keep the existing probability model.
2. OctoBot: evaluate snapshot freshness at the decision clock. Require both outcome
   books and the timestamped underlying trade to be recent and mutually consistent;
   log the individual verdicts. Book validation also rejects invalid/crossed levels.
3. Hummingbot: preserve a minimum distance between each bid and its book midpoint,
   quantize down to the configured tick, remain strictly passive, and retain whole-batch
   budget checks and binary inventory completion. Do not import spot inventory targets
   or leverage into binary-outcome markets.
4. Freqtrade: temporary entry lock after two net losing settled markets within four
   hours, lasting one hour from the last known settlement. Aggregate both binary legs;
   exclude incomplete markets. Cooldown survives restart from ledger history and never
   extends merely because the scheduler polls. MM may still complete existing inventory
   under its current pair-profit and worst-case risk caps.
5. Gainium docker-sh: adopt dependency-health gating as meaningful failure exit codes
   for scheduled cycles; engine/report failures must make the cloud run fail while
   preserving state. Run regression tests before cloud trading. Its companion paper
   simulator is inspected for fit; no need for Docker, MongoDB or exchange credentials.

Activate these as explicit versions pm-2.2.0 and mm-2.1.0, with append-only change
records and unchanged cash, existing positions, sizing and drawdown limits. Conservative
freshness/spread/cooldown settings are operational protections, not optimized alpha.
They can reduce trades and returns; make no profitability claim. No changes to stock
entry signals, the retired bot's historical trades, or historical return reports.

Validation: failing regression tests first, then focused and full test suites; synthetic
scenarios for gappy/future data, delayed mixed snapshots, passive tick rounding, whole-market
loss counting, restart/expiry and error reporting; independent code review; read-only
live public-data smoke; cloud cycle and ledger integrity checks after activation.
